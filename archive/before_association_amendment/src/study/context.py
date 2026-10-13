"""Fresh source-native density and consistent OSM civic-anchor distances."""
from __future__ import annotations

import csv
import io
import json
import math
from collections import defaultdict
from shapely.geometry import Point,shape
from shapely.ops import transform
import pandas as pd
from sqlalchemy import text

from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.ingestion.download_copenhagen_statbank import decode_csv
from src.pipeline.protocol import canonical_hash
from src.v4.context import jsonstat_cells
from src.v4.geography import oslo_areas
from src.study.geography import metric_transform
from src.study.sources import verify_source
from src.study.specification import load_design


def aggregate_density(units):
    """Only already qualified whole units; missingness is never filled."""
    if not units or any(not u.get('whole_unit_verified',False) for u in units):
        raise ValueError('Validated whole-unit aggregation required; no split-unit allocation')
    if any(u['population'] is None or u['area_km2'] is None for u in units):
        return None
    if any(u['population']<0 or u['area_km2']<=0 for u in units):
        raise ValueError('Invalid source population/area')
    return sum(u['population'] for u in units)/sum(u['area_km2'] for u in units)


def density_record(group,native_id,population,area,period,area_definition,sources):
    density=aggregate_density([{'population':population,'area_km2':area,'whole_unit_verified':True}])
    if density is None or density<=0:
        raise ValueError('Required density unavailable/nonpositive; no invented substitute')
    return {'group':group,'native_id':native_id,'population':population,'area_km2':area,
            'population_density':density,'log_population_density':math.log(density),
            'reference_period':period,'area_definition':area_definition,'sources':sources}


def copenhagen_density(conn,config):
    policy=json.loads((PROJECT_ROOT/'config/v4/geography_A03_20261011.json').read_text())['cities']['copenhagen_frederiksberg']
    pin=policy['districts'];document=json.loads(verify_source(pin).read_text())
    population_path=PROJECT_ROOT/'data/raw/copenhagen_statbank/2026-09-29/tables/KKBEF1.csv'
    if sha256_file(population_path)!='953f29d57f9d62fecc747a68830f97cc6acb54ff8e364c0b180c48503bb26009':
        raise ValueError('Preserved Copenhagen population source changed')
    pop=decode_csv(population_path.read_bytes())
    if len(pop)!=1 or pop[0][:4]!=['Marital status total','Age total','Sex total','2026Q3'] or len(pop[0])!=14:
        raise ValueError('Population selectors/period/schema differ')
    sources={'districts':pin,'population':{'path':population_path.relative_to(PROJECT_ROOT).as_posix(),'sha256':sha256_file(population_path)}}
    project=metric_transform(config['metric_crs']);result=[]
    for f in document['features']:
        code=int(f['properties']['bydel_nr']);group=f['properties']['navn']
        if group not in set(config['operational_mapping'].values()):raise ValueError('Official density/provider unit label mismatch')
        result.append(density_record(group,str(1000+code),int(pop[0][3+code]),transform(project,shape(f['geometry'])).area/1e6,
                                     '2026Q3 (2026-07-01; one day after listing batch)',
                                     'Gross native official district polygon; water/statistical-vintage caveats retained',sources))
    national=PROJECT_ROOT/'data/raw/municipality_statbank/2026-09-29/tables/FOLK1A.csv'
    if sha256_file(national)!='62af775af77d0cdfd82a50f497c3ffd8c1ec18e57ca7c7821b2a51c815b5caa8':raise ValueError('Preserved Frederiksberg population changed')
    rows=list(csv.DictReader(io.StringIO(national.read_text(encoding='utf-8-sig')),delimiter=';'))
    selected=[r for r in rows if r['OMRÅDE'].split(' ')[0]=='147']
    if len(selected)!=1 or tuple(selected[0][k].split(' ')[0] for k in ('KØN','ALDER','CIVILSTAND','TID'))!=('TOT','IALT','TOT','2026K3'):
        raise ValueError('Frederiksberg source selection differs')
    old=config['historical_listing_selection']
    geo=conn.scalar(text('SELECT ST_AsGeoJSON(geom,15) FROM v4_spatial.study_boundaries WHERE version=:version AND run_id=:run '
                         "AND city=:city AND snapshot='2026-06-30' AND source_area_id='0147'"),
                    {'version':old['source_version'],'run':old['run_id'],'city':old['city']})
    area=transform(project,shape(json.loads(geo))).area/1e6
    result.append(density_record('Frederiksberg','147',int(selected[0]['INDHOLD']),area,'2026Q3',
                                 'Gross accepted source municipal polygon; source-compatible transport at15 decimal places',
                                 {'population':{'path':national.relative_to(PROJECT_ROOT).as_posix(),'sha256':sha256_file(national)},
                                  'geometry_manifest':old['manifest_sha256']}))
    return result


def oslo_density(config):
    context=json.loads((PROJECT_ROOT/'config/v4/context_A04_20261011.json').read_text())['cities']['oslo']
    entries={s['record']['source_id']:s for s in context['sources']}
    data=entries['a04_20261011_population_data'];schema=entries['a04_20261011_population_schema']
    for entry in (data,schema):
        r=entry['record'];verify_source({'path':r['local_location'],'sha256':r['sha256']})
        verify_source(entry['receipt'])
    r=data['record'];meta=schema['record']
    if r['selection']['schema_sha256']!=meta['sha256']:raise ValueError('Population metadata source mismatch')
    document=json.loads((PROJECT_ROOT/r['local_location']).read_text())
    metadata=json.loads((PROJECT_ROOT/meta['local_location']).read_text())
    cells=jsonstat_cells(document,metadata,r);values=defaultdict(list)
    for c in cells:
        if c['unit']!='Antall personer':raise ValueError('Wrong population units')
        values[c['keys']['bosted']].append(c['value'])
    if len(values)!=19 or any(len(v)!=106 or None in v for v in values.values()):raise ValueError('Incomplete native age/population support')
    geography=json.loads((PROJECT_ROOT/'config/v4/geography_A03_20261011.json').read_text())['cities']['oslo']
    areas=oslo_areas(json.loads(verify_source(geography['boroughs']).read_text()),geography['native_codes'])
    project=metric_transform(config['metric_crs']);result=[]
    for a in areas:
        native='301'+a['native_id'];population=sum(values[native])
        result.append(density_record(a['name'],native,population,transform(project,a['geom']).area/1e6,'2026-01-01',
                                     'Gross native official17-unit polygons; distinct from provider fold polygons; no total/unlocated redistribution',
                                     {'population_sha256':r['sha256'],'metadata_sha256':meta['sha256'],'geometry':geography['boroughs'],
                                      'reuse_terms':'City-service explicit reuse licence not stated; raw statistics/geometries kept private'}))
    return result


STOCKHOLM_CODES={1:'Järva',4:'Hässelby-Vällingby',6:'Bromma',8:'Kungsholmen',9:'Norra innerstaden',12:'Södermalm',
                 14:'Enskede-Årsta-Vantör',15:'Skarpnäck',18:'Farsta',22:'Hägersten-Älvsjö',24:'Skärholmen'}


def stockholm_density():
    sources=json.loads((PROJECT_ROOT/'config/study/stockholm_population_sources.json').read_text())
    population=pd.read_excel(verify_source(sources['population']),header=None)
    area=pd.read_excel(verify_source(sources['area']),header=None)
    return parse_stockholm_density(population,area,sources)


def parse_stockholm_density(population,area,sources):
    if (str(population.iloc[0,0]).strip()!='Folkmängd efter ålder 2025-12-31'
            or not str(area.iloc[0,0]).startswith('Areal och befolkningstäthet') or '2024-12-31' not in str(area.iloc[0,0])
            or population.iloc[2,9]!='Samtliga' or list(area.iloc[3,2:5])!=['Land','Vatten','Totalt']):
        raise ValueError('Official spreadsheet years/units/schema changed')
    result=[]
    for code,group in STOCKHOLM_CODES.items():
        selected=area.loc[area[0].eq(code)]
        if len(selected)!=1:raise ValueError('Official NYKO2 native unit missing/duplicated')
        row=selected.iloc[0]
        if str(row[1]).replace(' - ','-').strip()!=group:raise ValueError('Official area/provider crosswalk name differs')
        matches=population.iloc[3:23].loc[population.iloc[3:23,0].astype(str).str.strip().eq(group)]
        if len(matches)!=1:raise ValueError('Official population/provider crosswalk missing/duplicated')
        p=matches.iloc[0]
        if sum(p.iloc[1:9].astype(int))!=int(p.iloc[9]):raise ValueError('Source age sum differs from native total')
        if int(row[2])+int(row[3])!=int(row[4]):raise ValueError('Native land+water differs from total area')
        result.append(density_record(group,str(code),int(p.iloc[9]),float(row[4])/100.,'2025-12-31 population /2024-12-31 area table',
                                     'Gross official borough land+water hectares /100; rounded published source areas, historical2003/1997 derivation; source-labelled11-unit correspondence, no exact provider/current boundary identity',
                                     {'population':sources['population'],'area':sources['area']}))
    return result


def build_context(conn,city,rows,assignments,mask):
    _,cities=load_design();config=cities[city]
    density=copenhagen_density(conn,config) if city=='copenhagen' else oslo_density(config) if city=='oslo' else stockholm_density()
    by_group={d['group']:d for d in density}
    if len(by_group)!=config['operational_count'] or set(by_group)!=set(config['operational_mapping'].values()):raise ValueError('Density crosswalk does not cover every operational unit')
    anchor=json.loads((PROJECT_ROOT/'config/study/civic_anchors.json').read_text())[city]
    verify_source(anchor['source'])
    point=Point(anchor['coordinates']['lon'],anchor['coordinates']['lat'])
    if not mask.covers(point):raise ValueError('Frozen public civic point outside accepted city mask')
    project=metric_transform(config['metric_crs']);metric_anchor=transform(project,point)
    context=[]
    for row,assigned in zip(rows,assignments,strict=True):
        if row['listing_id']!=assigned['listing_id']:raise ValueError('Context join order/key mismatch')
        group=assigned['operational_group'];native=by_group.get(group)
        unique=assigned['assignment_status']=='unique'
        location=transform(project,Point(row['longitude'],row['latitude'])) if row['longitude'] is not None else None
        context.append({'listing_id':row['listing_id'],'operational_group':group,'native_density_id':native['native_id'] if native and unique else None,
                        'log_population_density':native['log_population_density'] if native and unique else None,
                        'distance_centre_euclidean_km':location.distance(metric_anchor)/1000 if location is not None and unique else None,
                        'metric_x':location.x if location is not None else None,'metric_y':location.y if location is not None else None})
    missing=sum(r['eligible_positive'] and (c['log_population_density'] is None or c['distance_centre_euclidean_km'] is None) for r,c in zip(assignments,context,strict=True))
    summary={'city':city,'status':'QUALIFIED_SOURCE_NATIVE_CONTEXT_WITH_RECORDED_LIMITS' if missing==0 else 'BLOCKED',
             'eligible_context_missing_n':missing,'density_units':density,'civic_anchor':anchor,'metric_crs':config['metric_crs'],
             'density_assignment':'Explicit published native unit/name crosswalk to operational grouping; native matching denominator, not provider polygon denominator; polygon footprints differ as geography QA records',
             'income_required':False,'historical_density_reused':False,'blockers':[] if missing==0 else ['Eligible listings lack required source-native context']}
    return summary,context
