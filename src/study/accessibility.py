"""Matched E/W from one pinned destination universe and directed pedestrian graph."""
from __future__ import annotations
from collections import Counter,defaultdict
import gc
import json
import math
import networkx as nx
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import LineString,Point,Polygon,box
from shapely.ops import transform,polygonize,unary_union

from src.ingestion.common import PROJECT_ROOT
from src.pipeline.osm_taxonomy import categories,normalize_name,NAME_DEDUP_METRES,WIKIDATA_DEDUP_METRES
from src.pipeline.build_bus_euclidean_accessibility import selection_rule,consolidate
from src.spatial.walking_network import walking_directions
from src.spatial.walking_routing import station_distance_labels,grouped_opportunities
from src.study.sources import verify_source
from src.study.specification import load_design
from src.study.geography import metric_transform


def selected_sources():
    primary=json.loads((PROJECT_ROOT/'config/study/osm_source_attempts.json').read_text())
    fragments=json.loads((PROJECT_ROOT/'config/study/osm_recovery_attempts.json').read_text())
    recovered=json.loads((PROJECT_ROOT/'config/study/osm_capacity_recovery.json').read_text())
    completion=PROJECT_ROOT/'config/study/osm_destination_completion.json'
    final=json.loads(completion.read_text()) if completion.exists() else []
    def valid(record):
        if record['http_status']!=200:return False
        document=json.loads(verify_source(record).read_text())
        return bool(document.get('elements')) and not document.get('remark')
    selected={}
    for city,roles in primary.items():
        selected[city]={}
        for role,attempts in roles.items():
            successful=[r for r in attempts if valid(r)]
            if successful:
                selected[city][role]=[successful[0]]
                continue
            tiles={r['geographic_extent']['tile']:r for r in fragments[city][role] if valid(r)}
            tiles.update({r['geographic_extent']['tile']:r for r in recovered[city][role] if valid(r)})
            if city=='stockholm' and role=='osm_destinations':
                tiles.update({r['geographic_extent']['tile']:r for r in final if valid(r)})
            if set(tiles)!={0,1,2,3}:raise ValueError('BLOCKED incomplete common OSM extent: '+city+'/'+role)
            selected[city][role]=[tiles[i] for i in range(4)]
    timestamp=load_design()[0]['accessibility']['preferred_osm_timestamp']
    if any(r['snapshot']!=timestamp for roles in selected.values() for records in roles.values() for r in records):raise ValueError('Mixed OSM observation times')
    return selected


def elements(records):
    """Identical element versions across tile overlaps; no silent conflict winner."""
    seen={}
    for record in records:
        document=json.loads(verify_source(record).read_text())
        if 'remark' in document or not document.get('elements'):raise ValueError('Partial/empty OSM extraction')
        for element in document['elements']:
            key=(element['type'],element['id'])
            if element.get('timestamp','')>record['snapshot']:raise ValueError('OSM version newer than requested snapshot')
            if key in seen:
                if seen[key]!=element:raise ValueError('Conflicting tiled OSM element version/geometry')
            else:seen[key]=element
    return list(seen.values())


def complete_geometry(city,document):
    pin=PROJECT_ROOT/'config/study/destination_geometry_sources.json'
    if not pin.exists():raise ValueError('Required destination member-geometry acquisition is pending')
    records=json.loads(pin.read_text())[city]
    geo={(e['type'],e['id']):e for e in elements(records)}
    result=[]
    for e in document:
        selected=bool(categories(e.get('tags',{})) or selection_rule(e.get('tags',{})))
        if e['type']!='node' and selected:
            g=geo.get((e['type'],e['id']))
            if g is None:raise ValueError('Destination geometry/source object missing')
            if any(g.get(k)!=e.get(k) for k in ('timestamp','version','tags')):raise ValueError('Geometry response conflicts with frozen destination identity/tags')
            result.append({**e,**g})
        else:result.append(e)
    return result


def pedestrian_graph(document,metric_crs):
    project=Transformer.from_crs(4326,metric_crs,always_xy=True)
    coordinates={};segments=[];counts=Counter()
    for element in document:
        if element['type']!='way':raise ValueError('Network extraction must contain highway ways')
        forward,reverse=walking_directions(element.get('tags',{}))
        if not (forward or reverse):counts['excluded_ways']+=1;continue
        nodes=element['nodes'];geometry=element.get('geometry',[])
        if len(nodes)!=len(geometry) or any(p is None for p in geometry):raise ValueError('Missing highway-node geometry; incomplete graph')
        for node,p in zip(nodes,geometry,strict=True):
            value=(p['lon'],p['lat'])
            if node in coordinates and coordinates[node]!=value:raise ValueError('Conflicting coordinate for same topological OSM node')
            coordinates[node]=value
        segments.extend((u,v,forward,reverse) for u,v in zip(nodes,nodes[1:]) if u!=v)
        counts['included_ways']+=1
    if not segments:raise ValueError('No permitted pedestrian graph')
    ids=list(coordinates);lon,lat=zip(*(coordinates[k] for k in ids));x,y=project.transform(lon,lat)
    metric=dict(zip(ids,zip(x,y),strict=True));graph=nx.DiGraph();graph.add_nodes_from(ids)
    for u,v,forward,reverse in segments:
        length=math.dist(metric[u],metric[v])
        if length<.01:counts['zero_length_segments']+=1;continue
        if forward:graph.add_edge(u,v,length_m=length)
        if reverse:graph.add_edge(v,u,length_m=length)
    sizes=sorted((len(c) for c in nx.weakly_connected_components(graph)),reverse=True)
    return graph,metric,{'metric_crs':metric_crs,'nodes':len(graph),'arcs':graph.number_of_edges(),'weak_components':len(sizes),
                         'largest_component_nodes':sizes[0],**dict(counts)}


def destination_point(element,project):
    kind=element['type']
    if kind=='node':return transform(project,Point(element['lon'],element['lat'])),'osm_node'
    geometry=element.get('geometry')
    if kind=='way' and geometry:
        xy=[project(p['lon'],p['lat']) for p in geometry if p is not None]
        if len(xy)!=len(geometry) or len(xy)<2:raise ValueError('Missing destination way-node geometry')
        geom=Polygon(xy) if xy[0]==xy[-1] and len(xy)>=4 else LineString(xy)
        if not geom.is_valid:raise ValueError('Invalid destination geometry; no repair')
        return (geom.representative_point(),'projected_point_on_surface') if geom.geom_type=='Polygon' else (geom.interpolate(.5,normalized=True),'projected_line_midpoint')
    if kind=='relation' and element.get('tags',{}).get('type')=='multipolygon':
        lines=defaultdict(list)
        for m in element.get('members',[]):
            if m.get('type')!='way':continue
            coordinates=m.get('geometry',[])
            if len(coordinates)<2 or any(p is None for p in coordinates):raise ValueError('Incomplete multipolygon destination geometry')
            lines[m.get('role') or 'outer'].append(LineString([project(p['lon'],p['lat']) for p in coordinates]))
        outer=unary_union(list(polygonize(unary_union(lines['outer']))))
        inner=unary_union(list(polygonize(unary_union(lines['inner'])))) if lines['inner'] else None
        geom=outer.difference(inner) if inner is not None else outer
        if geom.is_empty or not geom.is_valid:raise ValueError('Invalid/incomplete multipolygon destination')
        return geom.representative_point(),'projected_point_on_surface'
    # Nonpolygon relation metadata supplies only an OSM object centre. This
    # common pre-fit representation is recorded separately from polygon points.
    if element.get('center'):
        p=element['center'];return Point(*project(p['lon'],p['lat'])),'osm_nonpolygon_relation_center'
    raise ValueError('Required destination has no source-supported point')


def destinations(document,metric_crs):
    project=Transformer.from_crs(4326,metric_crs,always_xy=True).transform
    inverse=Transformer.from_crs(metric_crs,4326,always_xy=True).transform
    candidates=[];bus=[];stop_areas=defaultdict(list)
    for element in document:
        tags=element.get('tags',{})
        if element['type']=='relation' and tags.get('public_transport')=='stop_area':
            for member in element.get('members',[]):stop_areas[f"{member['type']}/{member['ref']}"].append(element['id'])
        selected=categories(tags);rule=selection_rule(tags)
        if not selected and not rule:continue
        point,method=destination_point(element,project)
        key=f"{element['type']}/{element['id']}"
        common={'key':key,'type':element['type'],'id':element['id'],'tags':tags,'x':point.x,'y':point.y,'position_method':method}
        candidates.extend({**common,'category':c,'candidate_key':c+':'+key} for c in selected)
        if rule:bus.append({**common,'bus_stop_key':key,'rule':rule})
    candidates.sort(key=lambda r:(r['category'],{'node':0,'way':1,'relation':2}[r['type']],r['id']))
    canonical=[];by_identity=defaultdict(list)
    for r in candidates:
        name=normalize_name(r['tags'].get('name'));wikidata=r['tags'].get('wikidata')
        possible={o['candidate_key']:o for token in [('name',name),('wikidata',wikidata)] if token[1]
                  for o in by_identity[(r['category'],*token)]}
        matches=[]
        for o in possible.values():
            distance=math.hypot(r['x']-o['x'],r['y']-o['y'])
            same_name=name and name==normalize_name(o['tags'].get('name')) and distance<=NAME_DEDUP_METRES[r['category']]
            same_wikidata=wikidata and wikidata==o['tags'].get('wikidata') and distance<=WIKIDATA_DEDUP_METRES[r['category']]
            if same_name or same_wikidata:matches.append(o)
        if matches:continue
        canonical.append({**r,'destination_key':r['candidate_key']})
        if name:by_identity[(r['category'],'name',name)].append(r)
        if wikidata:by_identity[(r['category'],'wikidata',wikidata)].append(r)
    for r in bus:r['stop_areas']=stop_areas[r['bus_stop_key']]
    if not bus:raise ValueError('Bus universe empty')
    consolidated=consolidate(pd.DataFrame(bus))
    canonical.extend({**r,'category':'bus','destination_key':'bus:'+r['canonical_key']} for r in consolidated if r['bus_stop_key']==r['canonical_key'])
    counts=Counter(r['category'] for r in canonical)
    if set(counts)!={'station','bus','food_social','cultural_tourist'}:raise ValueError('Required matched destination category empty')
    return canonical,{'raw_selected_candidates':len(candidates),'raw_bus':len(bus),'canonical_counts':dict(counts),
                       'position_methods':dict(Counter(r['position_method'] for r in canonical)),'metric_crs':metric_crs}


def measurements(graph,metric,destination_rows,listing_rows,bbox,metric_crs):
    project=metric_transform(metric_crs);ids=np.asarray(list(metric),dtype=np.int64)
    nodes=np.array([metric[int(k)] for k in ids]);tree=cKDTree(nodes)
    snaps=[]
    for row in destination_rows:
        distance,i=tree.query([row['x'],row['y']]);snaps.append({**row,'snapped_node_id':int(ids[i]),'snap_distance_m':float(distance)})
    listing_snaps=[]
    for row in listing_rows:
        x,y=project(row['longitude'],row['latitude']);distance,i=tree.query([x,y])
        listing_snaps.append({'listing_id':row['listing_id'],'x':x,'y':y,'snapped_node_id':int(ids[i]),'snap_distance_m':float(distance)})
    matched={c:[r for r in snaps if r['category']==c] for c in ('station','bus','food_social','cultural_tourist')}
    labels={c:station_distance_labels(graph,matched[c]) for c in ('station','bus')}
    opportunities,qa=grouped_opportunities(graph,listing_snaps,matched['food_social']+matched['cultural_tourist'])
    euclidean={c:cKDTree([[r['x'],r['y']] for r in rows]) for c,rows in matched.items()}
    south,west,north,east=bbox
    domain=transform(project,box(west,south,east,north).segmentize(.002))
    output=[];per_minute=5000/60;counts=Counter()
    for r in listing_snaps:
        row={'listing_id':r['listing_id'],'snap_distance_m':r['snap_distance_m'],'metric_crs':metric_crs}
        edge=domain.boundary.distance(Point(r['x'],r['y']));row['source_edge_distance_m']=edge
        for category,target in [('station','nearest_station'),('bus','nearest_bus')]:
            straight=float(euclidean[category].query([r['x'],r['y']])[0]);path=labels[category][0].get(r['snapped_node_id'])
            length=None if path is None else path+r['snap_distance_m']
            row[target+'_euclidean_km']=straight/1000
            row[target+'_walking_minutes']=None if length is None else length/per_minute
            row[target+'_coverage_complete']=length is not None and length<edge and straight<edge
            counts[category+'_routing_failures']+=length is None
        for category,prefix in [('food_social','food'),('cultural_tourist','culture')]:
            for minutes,radius in zip((10,15,20),(833,1250,1667),strict=True):
                count=len(euclidean[category].query_ball_point([r['x'],r['y']],radius))
                value=opportunities[r['listing_id']][(category,per_minute*minutes)]
                row[prefix+f'_e_{minutes}']=count;row[prefix+f'_w_{minutes}']=value
                if minutes==10:
                    row['log1p_'+prefix+'_e']=math.log1p(count);row['log1p_'+prefix+'_w']=math.log1p(value)
            counts[prefix+'_true_zero_network_10']+=row[prefix+'_w_10']==0
        row['opportunity_coverage_complete']=edge>1667
        row['common_support']=row['opportunity_coverage_complete'] and row['nearest_station_coverage_complete'] and row['nearest_bus_coverage_complete']
        counts['common_support']+=row['common_support'];counts['snap_over_100m']+=r['snap_distance_m']>100;counts['snap_over_250m']+=r['snap_distance_m']>250
        output.append(row)
    return output,{'counts':dict(counts),**qa,'metric_crs':metric_crs,'same_destination_universe':True,
                   'connector_rule':'Both endpoints; directed pedestrian edges; no unreachable-to-zero conversion'}
