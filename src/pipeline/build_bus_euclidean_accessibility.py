"""Core bus destinations: frozen taxonomy, physical-stop consolidation and distance."""
from __future__ import annotations
import json
from collections import defaultdict
import osmium
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import LineString,Polygon
from sqlalchemy import text
from src.db.connection import get_engine
from src.ingestion.common import sha256_file
from src.pipeline.acquire_osm import existing_archive,PBF_NAME
from src.pipeline.osm_taxonomy import normalize_name
from src.pipeline.storage import export
VERSION='bus_destinations_v3'

def selection_rule(tags):
    if tags.get('highway')=='bus_stop':return 'highway=bus_stop'
    if tags.get('public_transport') in {'platform','stop_position'} and tags.get('bus')=='yes':
        return 'public_transport='+tags['public_transport']+';bus=yes'
    return None

def representation(tags):
    return 'stop_position' if tags.get('public_transport')=='stop_position' else 'platform'

class BusHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__();self.rows=[];self.missing_way_locations=0;self.stop_areas=defaultdict(list)
        self.project=Transformer.from_crs(4326,25832,always_xy=True)
        self.inverse=Transformer.from_crs(25832,4326,always_xy=True)
    def node(self,node):
        tags={t.k:t.v for t in node.tags};rule=selection_rule(tags)
        if rule:
            if not node.location.valid(): raise RuntimeError('Bus node has no location')
            self.rows.append(dict(key=f'node/{node.id}',type='node',id=int(node.id),rule=rule,tags=tags,
                lon=node.location.lon,lat=node.location.lat,position_method='osm_node'))
    def way(self,way):
        tags={t.k:t.v for t in way.tags};rule=selection_rule(tags)
        if not rule:return
        xy=[self.project.transform(n.location.lon,n.location.lat) for n in way.nodes if n.location.valid()]
        if len(xy)!=len(way.nodes) or len(xy)<2:self.missing_way_locations+=1;return
        shape=Polygon(xy) if xy[0]==xy[-1] and len(xy)>=4 else LineString(xy)
        if not shape.is_valid:raise RuntimeError('Invalid bus platform geometry')
        point=shape.representative_point() if shape.geom_type=='Polygon' else shape.interpolate(.5,normalized=True)
        lon,lat=self.inverse.transform(point.x,point.y)
        self.rows.append(dict(key=f'way/{way.id}',type='way',id=int(way.id),rule=rule,tags=tags,
            lon=lon,lat=lat,position_method='projected_point_on_surface' if shape.geom_type=='Polygon' else 'projected_line_midpoint'))
    def relation(self,rel):
        tags={t.k:t.v for t in rel.tags}
        if tags.get('public_transport')=='stop_area':
            for member in rel.members:
                kind={'n':'node','w':'way','r':'relation'}.get(member.type)
                if kind:self.stop_areas[f'{kind}/{member.ref}'].append(int(rel.id))

def consolidate(stops):
    """No unnamed proximity merges except effectively coincident representations.

    Same representation merges require <=3 m and matching name/ref (unnamed <=.5 m).
    Stop-position/platform pairs require a shared stop_area/ref/name, <=25 m,
    and mutual nearest identity-compatible partners. This preserves opposite
    carriageways and avoids merging every member of a multi-platform stop_area.
    """
    rows=stops.to_dict('records');xy=stops[['x','y']].to_numpy(float);parent=list(range(len(rows)));reasons={}
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def identity(a,b):
        ta,tb=rows[a]['tags'],rows[b]['tags']
        for key in ['ref','local_ref']:
            if ta.get(key) and tb.get(key) and ta[key]!=tb[key]:return None
        if set(rows[a].get('stop_areas',[])) & set(rows[b].get('stop_areas',[])):return 'shared_stop_area'
        if ta.get('ref') and ta.get('ref')==tb.get('ref'):return 'shared_ref'
        na,nb=normalize_name(ta.get('name')),normalize_name(tb.get('name'))
        if na and na==nb:return 'same_name'
        return None
    pairs=sorted(cKDTree(xy).query_pairs(25)) if len(rows)>1 else []
    cross=defaultdict(list)
    for a,b in pairs:
        distance=float(np.linalg.norm(xy[a]-xy[b]));match=identity(a,b)
        same=representation(rows[a]['tags'])==representation(rows[b]['tags'])
        unnamed=not rows[a]['tags'].get('name') and not rows[b]['tags'].get('name')
        conflicting_ref=any(rows[a]['tags'].get(k) and rows[b]['tags'].get(k) and rows[a]['tags'][k]!=rows[b]['tags'][k] for k in ['ref','local_ref'])
        if conflicting_ref:continue
        if same and ((distance<=3 and match) or (distance<=.5 and unnamed)):
            parent[root(b)]=root(a);reasons[(a,b)]='coincident_'+(match or 'unnamed')
        elif not same and match:
            cross[a].append((distance,rows[b]['bus_stop_key'],b,match));cross[b].append((distance,rows[a]['bus_stop_key'],a,match))
    nearest={i:min(options) for i,options in cross.items()}
    for a,item in sorted(nearest.items()):
        _,_,b,match=item
        if a<b and nearest.get(b,(None,None,None))[2]==a:
            parent[root(b)]=root(a);reasons[(a,b)]='mutual_nearest_platform_stop_position_'+match
    groups=defaultdict(list)
    for i in range(len(rows)):groups[root(i)].append(i)
    result=[]
    for members in groups.values():
        representative=min(members,key=lambda i:(representation(rows[i]['tags'])=='stop_position',rows[i]['type']!='node',rows[i]['bus_stop_key']))
        key=rows[representative]['bus_stop_key']
        why=';'.join(sorted({v for (a,b),v in reasons.items() if a in members and b in members})) or 'canonical_singleton'
        for i in members:result.append({**rows[i],'canonical_key':key,'dedup_reason':why})
    return sorted(result,key=lambda row:row['bus_stop_key'])

def run():
    archive=existing_archive()
    if archive is None:raise RuntimeError('Frozen OSM city extract required')
    pbf=archive/PBF_NAME;meta=json.loads((archive/'acquisition_metadata.json').read_text())
    digest=sha256_file(pbf)
    if digest!=meta['files'][PBF_NAME]['sha256']:raise RuntimeError('Frozen OSM hash mismatch')
    handler=BusHandler();handler.apply_file(str(pbf),locations=True)
    if not handler.rows or handler.missing_way_locations:raise RuntimeError('Bus extraction incomplete')
    stops=pd.DataFrame(handler.rows).rename(columns={'key':'bus_stop_key'})
    stops['stop_areas']=[handler.stop_areas[key] for key in stops.bus_stop_key]
    project=Transformer.from_crs(4326,25832,always_xy=True)
    stops['x'],stops['y']=project.transform(stops.lon.to_numpy(),stops.lat.to_numpy())
    rows=consolidate(stops);engine=get_engine()
    try:
        with engine.begin() as conn:
            source=conn.scalar(text('SELECT source_file_id FROM meta.source_files WHERE file_hash_sha256=:hash'),{'hash':digest})
            if source is None:raise RuntimeError('Bus PBF source must first be registered')
            if conn.scalar(text('SELECT count(*) FROM v3_spatial.bus_stops')):raise RuntimeError('V3 bus destinations already built; refusing replacement')
            conn.execute(text('INSERT INTO v3_spatial.bus_stops(bus_stop_key,source_file_id,taxonomy_version,osm_object_type,osm_id,selection_rule,tags,canonical_key,dedup_reason,geom,geom_25832) '
                'VALUES(:bus_stop_key,:source,:version,:type,:id,:rule,CAST(:tags AS jsonb),:canonical_key,:dedup_reason,'
                'ST_SetSRID(ST_MakePoint(:lon,:lat),4326),ST_SetSRID(ST_MakePoint(:x,:y),25832))'),
                [{**r,'source':source,'version':VERSION,'tags':json.dumps({**r['tags'],'_stop_area_ids':r['stop_areas'],'_position_method':r['position_method']})} for r in rows])
            conn.execute(text('INSERT INTO v3_features.bus_accessibility(snapshot_date,listing_id,source_file_id,taxonomy_version,nearest_bus_euclidean_key,nearest_bus_euclidean_m,euclidean_coverage_complete) '
                'SELECT l.snapshot_date,l.listing_id,:source,:version,b.bus_stop_key,b.distance_m,b.distance_m<e.source_edge_distance_m '
                'FROM v3_clean.airbnb_listings l JOIN v3_features.euclidean_accessibility e USING(snapshot_date,listing_id) '
                'LEFT JOIN LATERAL(SELECT bus_stop_key,ST_Distance(geom_25832,l.geom_25832) AS distance_m FROM v3_spatial.canonical_bus_stops '
                'ORDER BY geom_25832 <-> l.geom_25832,bus_stop_key LIMIT 1)b ON l.valid_coordinates'),{'source':source,'version':VERSION})
        export('accessibility','bus_deduplication.csv',pd.DataFrame([{k:r[k] for k in ['bus_stop_key','canonical_key','dedup_reason','rule','position_method']} for r in rows]))
        return {'version':VERSION,'source_sha256':digest,'raw_bus_objects':len(rows),'canonical_bus_stops':sum(r['bus_stop_key']==r['canonical_key'] for r in rows),'crs_epsg':25832}
    finally:engine.dispose()
if __name__=='__main__':print(json.dumps(run(),indent=2))
