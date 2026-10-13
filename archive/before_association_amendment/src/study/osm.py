"""Common historical OSM extraction, with exact query and transport receipts."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import json
from urllib.parse import urlencode
from shapely.geometry import box
from shapely.ops import transform
from pyproj import Transformer

from src.ingestion.common import PROJECT_ROOT
from src.pipeline.osm_taxonomy import query_text
from src.study.sources import acquire, get_engine, historical_inputs, write_once
from src.study.specification import CITIES, load_design
from src.study.geography import metric_transform

ENDPOINTS = ('https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter')


def queries(bbox, timestamp):
    south,west,north,east=bbox
    bounds=','.join(f'{v:.7f}' for v in bbox)
    header=f'[out:json][timeout:300][date:"{timestamp}"];'
    network=header+f'way["highway"]({bounds});out meta geom;'
    destination=query_text(bbox)
    destination=destination[destination.index('\n')+1:]
    # Preserve inherited eligible taxonomy and bus rules; extra retrieved memorial
    # objects remain excluded by the inherited category selector.
    bus=(f'nwr["highway"="bus_stop"]({bounds});'
         f'nwr["public_transport"~"^(platform|stop_position)$"]["bus"="yes"]({bounds});'
         f'relation["public_transport"="stop_area"]({bounds});')
    destination=header+destination.replace(');\nout center tags;',bus+');\nout meta geom;')
    return {'osm_network':network,'osm_destinations':destination}


def extract_city(city, bbox, timestamp):
    attempts={}
    for role,query in queries(bbox,timestamp).items():
        attempts[role]=[]
        for endpoint in ENDPOINTS:
            record=acquire(endpoint,city=city,role=role,extent={'bbox_south_west_north_east':bbox},
                           crs='EPSG:4326',licence='ODbL; © OpenStreetMap contributors',snapshot=timestamp,
                           body=urlencode({'data':query}).encode(),timeout=360)
            attempts[role].append(record)
            valid=False
            if record['http_status']==200:
                try:
                    document=json.loads((PROJECT_ROOT/record['path']).read_text())
                    elements=document['elements']
                    valid=(isinstance(elements,list) and bool(elements) and not document.get('remark')
                           and all(e.get('timestamp','')<=timestamp for e in elements))
                except (ValueError,KeyError):
                    pass
            print(city,role,record['http_status'],'validated nonempty' if valid else 'failed/unqualified',flush=True)
            if valid:
                break
    return attempts


def acquire_matched_sources():
    target=PROJECT_ROOT/'config/study/osm_source_attempts.json'
    if target.exists():
        raise ValueError('Acquisition selection already exists; preserve failures and use a separately identified recovery')
    design,cities=load_design()
    boxes={}
    engine=get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                _,mask,_=historical_inputs(conn,city)
                metric=transform(metric_transform(cities[city]['metric_crs']),mask).buffer(design['accessibility']['extraction_buffer_m'])
                geographic=transform(Transformer.from_crs(cities[city]['metric_crs'],4326,always_xy=True).transform,metric)
                west,south,east,north=geographic.bounds
                boxes[city]=[south,west,north,east]
    finally:
        engine.dispose()
    # Public endpoints share per-client capacity; serialize large city extracts.
    with ThreadPoolExecutor(max_workers=1) as executor:
        jobs={city:executor.submit(extract_city,city,boxes[city],design['accessibility']['preferred_osm_timestamp']) for city in CITIES}
        result={city:job.result() for city,job in jobs.items()}
    write_once(target,(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode())
    return result


def recover_fragments():
    """Recover failed roles without changing the date, taxonomy or full extent."""
    prior=json.loads((PROJECT_ROOT/'config/study/osm_source_attempts.json').read_text())
    design,_=load_design();result={}
    for city,roles in prior.items():
        result[city]={}
        for role,attempts in roles.items():
            if any(r['http_status']==200 for r in attempts):
                continue
            south,west,north,east=attempts[0]['geographic_extent']['bbox_south_west_north_east']
            midlat,midlon=(south+north)/2,(west+east)/2
            tiles=[[south,west,midlat,midlon],[south,midlon,midlat,east],
                   [midlat,west,north,midlon],[midlat,midlon,north,east]]
            result[city][role]=[]
            for i,tile in enumerate(tiles):
                query=queries(tile,design['accessibility']['preferred_osm_timestamp'])[role]
                record=acquire(ENDPOINTS[0],city=city,role=role+'_fragment',
                               extent={'tile':i,'bbox_south_west_north_east':tile,'full_extent':[south,west,north,east]},
                               crs='EPSG:4326',licence='ODbL; © OpenStreetMap contributors',
                               snapshot=design['accessibility']['preferred_osm_timestamp'],
                               body=urlencode({'data':query}).encode(),timeout=360)
                result[city][role].append(record)
                print(city,role,'tile',i,record['http_status'],record['failure'],flush=True)
                # Save each recovery attempt before continuing; interruption never
                # loses already acquired immutable source evidence.
                target=PROJECT_ROOT/'data/metadata/osm_recovery'/city/(role+f'_tile_{i}.json')
                write_once(target,(json.dumps(record,indent=2,ensure_ascii=False)+'\n').encode())
    write_once(PROJECT_ROOT/'config/study/osm_recovery_attempts.json',(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode())
    return result
