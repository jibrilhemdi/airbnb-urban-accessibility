"""Qualified surrounding geography for maps, isolated from frozen analytical data."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json
import hashlib
from pathlib import Path
import geopandas as gpd
import requests
from pyproj import Transformer
from shapely.geometry import shape,mapping,Point
from shapely.ops import transform,unary_union
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT as ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once,verify_source
from src.study.specification import CITIES,load_design
from src.reporting.thesis_sources import verify_catalog,chosen

SELECTOR=ROOT/'config/reporting/map_context.json'
MIGRATION=ROOT/'sql/cartography/001_map_context.sql'
API='https://ws.geonorge.no/kommuneinfo/v1/'


def download(url,path,extent):
    response=requests.get(url,timeout=45);response.raise_for_status()
    body=response.content
    record={'path':str(path.relative_to(ROOT)),'source_url':url,'final_url':response.url,
            'acquired_at_utc':datetime.now(timezone.utc).isoformat(),'geographic_extent':extent,
            'source_crs':'EPSG:4326 requested explicitly for area geometry',
            'reference_period':'API current at retrieval; display context, not June analytical geography',
            'licence':'CC BY 4.0, Kartverket','sha256':hashlib.sha256(body).hexdigest(),
            'size_bytes':len(body),'role':'presentation_context_only','http_status':response.status_code}
    write_once(path,body);write_once(Path(str(path)+'.receipt.json'),(json.dumps(record,indent=2)+'\n').encode())
    return json.loads(body),record


def native_to_geographic(geom,crs):
    if geom.is_empty or not geom.is_valid:raise ValueError('Invalid cartographic source geometry; no repair')
    return transform(Transformer.from_crs(crs,'EPSG:4326',always_xy=True).transform,geom)


def prepare():
    if SELECTOR.exists():raise ValueError('Cartographic selector already frozen; verify rather than reacquire')
    verify_catalog();_,cities=load_design();sources=[];features=[];study=get_engine()
    try:
        with study.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            geography,refs=chosen(conn,'geography_selection','geography')
            contexts,_=chosen(conn,'context_selection','context')
            masks={c:shape(json.loads(conn.scalar(text("SELECT ST_AsGeoJSON(geom,17) FROM study.geometries WHERE run_id=:run AND geometry_key='mask'"),{'run':next(r['run_id'] for r in refs if r['city']==c)}))) for c in CITIES}
        def add_source(record):
            path=ROOT/record['path']
            if sha256_file(path)!=record['sha256']:raise ValueError('Cartographic source checksum changed')
            identity=canonical_hash(record);sources.append({'source_id':identity,'metadata':record});return identity
        def add(city,key,geom,source,**props):
            if geom.is_empty or not geom.is_valid:raise ValueError('Invalid map geometry: '+key)
            features.append({'city':city,'feature_key':key,'role':'civic_reference' if geom.geom_type=='Point' else 'surrounding_municipality',
                             'source_id':source,'properties':props,'geometry':mapping(geom)})
        def nearby(city,geom,crs):
            project=Transformer.from_crs('EPSG:4326',crs,always_xy=True).transform
            area=transform(project,masks[city]);candidate=transform(project,geom)
            return candidate.distance(area)<=3500
        path=ROOT/'data/raw/official_map_context/2026-09-29/capital_region_municipalities.geojson'
        metadata=json.loads((path.parent/'acquisition_metadata.json').read_text())['files'][path.name]
        dk=add_source({**metadata,'path':str(path.relative_to(ROOT)),'licence':'CC BY 4.0, DAGI/DAWA',
                       'reference_period':'Current at 29 September 2026 acquisition','role':'presentation_context_only'})
        for feature in json.loads(path.read_text())['features']:
            props=feature['properties'];geom=shape(feature['geometry']);code=props['kode']
            if code not in {'0101','0147'} and nearby('copenhagen',geom,cities['copenhagen']['metric_crs']):
                add('copenhagen','municipality:'+code,geom,dk,municipality_code=code,name=props.get('navn'),source_crs='EPSG:4326')
        directory=ROOT/'data/raw/cartographic_context/oslo'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        neighbours,receipt=download(API+'kommuner/0301/nabokommuner',directory/'neighbours.json','Official municipality neighbours of Oslo')
        neighbour_id=add_source(receipt)
        def fetch(row):
            code=row['kommunenummer']
            document,record=download(API+'kommuner/'+code+'/omrade?utkoordsys=4326',directory/(code+'.json'),row['kommunenavn']+' municipality, Oslo surroundings')
            geom=shape(document['omrade']);declared=document['omrade'].get('crs',{}).get('properties',{}).get('name','EPSG:4326')
            return row,native_to_geographic(geom,declared),record
        with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,neighbours))
        for row,geom,record in results:
            sid=add_source(record)
            if nearby('oslo',geom,cities['oslo']['metric_crs']):add('oslo','municipality:'+row['kommunenummer'],geom,sid,
                name=row['kommunenavn'],municipality_code=row['kommunenummer'],source_crs='EPSG:4326',neighbour_list_source_id=neighbour_id)
        path=ROOT/'data/raw/v4/research_design_v4/stockholm/2026-06-30/scb_regso_2025_20261011_geopackage/regso_2025.gpkg'
        receipt=json.loads(Path(str(path)+'.receipt.json').read_text())
        se=add_source({**receipt,'path':str(path.relative_to(ROOT)),'source_crs':'EPSG:3006, verified GeoPackage declaration',
                       'derivation':'Full RegSO union by original kommunkod; surrounding municipalities only','role':'presentation_context_only',
                       'documentation_url':'https://www.scb.se/en/services/open-data-api/open-geodata/open-data-for-regso--regional-statistical-areas/'})
        project=Transformer.from_crs('EPSG:4326','EPSG:3006',always_xy=True).transform
        extent=transform(project,masks['stockholm']).buffer(3500).bounds
        nearby_rows=gpd.read_file(path,layer='RegSO_2025',bbox=extent)
        codes=sorted(set(nearby_rows.kommunkod)-{'0180'})
        where='kommunkod IN ('+','.join("'"+code+"'" for code in codes)+')'
        rows=gpd.read_file(path,layer='RegSO_2025',where=where)
        if rows.crs.to_epsg()!=3006:raise ValueError('Unexpected RegSO CRS')
        for code,part in rows.groupby('kommunkod'):
            if not part.geometry.is_valid.all():raise ValueError('Invalid RegSO geometry; no repair')
            geom=native_to_geographic(unary_union(part.geometry.to_list()),'EPSG:3006')
            if nearby('stockholm',geom,cities['stockholm']['metric_crs']):add('stockholm','municipality:'+code,geom,se,
                municipality_code=code,source_crs='EPSG:3006',derivation='Full municipality union of source RegSO polygons')
        from src.db.connection import get_engine as legacy_engine
        legacy=legacy_engine()
        try:
            with legacy.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                row=conn.execute(text("SELECT description,source_url,source_accessed_on,source_crs_text,ST_AsGeoJSON(geom_4326,17) AS geometry FROM v3_spatial.reference_points WHERE reference_id='city_hall_square'")).mappings().one()
                square=shape(json.loads(row['geometry']))
                evidence={'database':'thesis_accessibility','table':'v3_spatial.reference_points','key':'city_hall_square',
                          'source_url':row['source_url'],'acquired_at_utc':str(row['source_accessed_on']),
                          'source_crs':row['source_crs_text'],'geographic_extent':'Public Copenhagen City Hall Square point',
                          'point_sha256':canonical_hash(json.loads(row['geometry'])),'role':'cartographic_reference_only',
                          'frozen_analytical_civic_point_replaced':False}
        finally:legacy.dispose()
        square_id=canonical_hash(evidence);sources.append({'source_id':square_id,'metadata':evidence})
        add('copenhagen','civic_reference',square,square_id,name='City Hall Square',point_kind='square',source_crs='EPSG:4326')
        for city in ['oslo','stockholm']:
            anchor=contexts[city]['civic_anchor'];verify_source(anchor['source']);sid=add_source(anchor['source'])
            point=Point(anchor['coordinates']['lon'],anchor['coordinates']['lat'])
            add(city,'civic_reference',point,sid,name='City Hall',point_kind='town_hall',source_crs='EPSG:4326',
                frozen_context_selector='config/study/context_selection.json',osm_type=anchor['osm_type'],osm_id=anchor['osm_id'])
        if any(not any(f['city']==c and f['role']=='surrounding_municipality' for f in features) for c in CITIES):raise ValueError('Missing surrounding geography')
        with study.begin() as conn:
            conn.exec_driver_sql('SELECT pg_advisory_xact_lock(2026101302)')
            if conn.scalar(text("SELECT to_regclass('cartography.features') IS NOT NULL")):raise ValueError('Cartographic schema exists; refuse replacement')
            conn.exec_driver_sql(MIGRATION.read_text())
            conn.execute(text('INSERT INTO cartography.schema_migrations VALUES (:name,:digest)'),{'name':MIGRATION.name,'digest':sha256_file(MIGRATION)})
            for source in {r['source_id']:r for r in sources}.values():
                conn.execute(text('INSERT INTO cartography.sources VALUES (:id,CAST(:metadata AS jsonb))'),{'id':source['source_id'],'metadata':json.dumps(source['metadata'])})
            for row in features:
                conn.execute(text('INSERT INTO cartography.features VALUES (:city,:key,:role,:source,CAST(:props AS jsonb),ST_SetSRID(ST_GeomFromGeoJSON(:geom),4326))'),
                             {'city':row['city'],'key':row['feature_key'],'role':row['role'],'source':row['source_id'],'props':json.dumps(row['properties']), 'geom':json.dumps(row['geometry'])})
            actual=sql_records(conn)
            source_rows=[dict(r) for r in conn.execute(text('SELECT source_id,metadata FROM cartography.sources ORDER BY source_id')).mappings()]
        result={'purpose':'Presentation context only; no sample/feature/fold/model changes','feature_sha256':canonical_hash(actual),
                'source_sha256':canonical_hash(source_rows),'sources':source_rows,'geometry_crs':'EPSG:4326',
                'metric_crs':{c:cities[c]['metric_crs'] for c in CITIES},'migration_sha256':sha256_file(MIGRATION),
                'neighbourhood_geography':'Unchanged frozen study.geometries group polygons',
                'context_count':{c:sum(r['city']==c and r['role']=='surrounding_municipality' for r in actual) for c in CITIES},
                'civic_reference_count':3,'models_refitted':False,'new_sources':'Oslo surrounding municipalities only, current-at-acquisition map context'}
        write_once(SELECTOR,(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode());return result
    finally:study.dispose()


def sql_records(conn):
    return [dict(row) for row in conn.execute(text('SELECT city,feature_key,role,source_id,properties,ST_AsGeoJSON(geom,17)::jsonb AS geometry FROM cartography.features ORDER BY city,feature_key')).mappings()]


def load_layers(conn):
    selected=json.loads(SELECTOR.read_text());rows=sql_records(conn)
    sources=[dict(r) for r in conn.execute(text('SELECT source_id,metadata FROM cartography.sources ORDER BY source_id')).mappings()]
    if canonical_hash(rows)!=selected['feature_sha256'] or canonical_hash(sources)!=selected['source_sha256']:raise ValueError('Frozen cartographic context changed')
    if sha256_file(MIGRATION)!=selected['migration_sha256']:raise ValueError('Cartographic migration changed')
    for row in sources:
        record=row['metadata']
        if record.get('path') and sha256_file(ROOT/record['path'])!=record['sha256']:raise ValueError('Cartographic raw bytes changed')
    layers={c:[] for c in CITIES}
    for row in rows:layers[row['city']].append({**row,'geometry':shape(row['geometry'])})
    return layers,{'path':'config/reporting/map_context.json','sha256':sha256_file(SELECTOR),'artifact':'Public surrounding municipalities and verified civic reference points','spatial_crs':'EPSG:4326'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prepare',action='store_true',required=True)
    parser.parse_args();result=prepare();print(json.dumps({k:v for k,v in result.items() if k!='sources'},indent=2))
