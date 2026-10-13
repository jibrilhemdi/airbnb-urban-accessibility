"""A04 native context qualification; no routing, sample freeze or estimation.

Source validation does not authorize spatial joins to unqualified geography.
The dedicated V4 database stores this checkpoint independently of model runs.
"""
from __future__ import annotations
import argparse
from collections import Counter
from decimal import Decimal
import itertools
import json
import math
from pathlib import Path
from pyproj import CRS, Transformer
from shapely.geometry import Point
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.provenance.cities import CITIES, VERSION
from src.provenance.geography import selected_evidence, verify_evidence
from src.provenance.identity import Paths, Scope, freeze_sources
from src.provenance.listings import acquire
from src.provenance.persistence import SCOPE_SQL, get_engine, register_manifest, verify_database
from src.provenance.source_reuse import reuse_listing_source, read_listing_audit
from src.provenance.specification import DEFINITION_VERSION

DEFINITION = 'v4_context_A04_20261011'
POLICY = PROJECT_ROOT / 'archive/previous_analysis/config/context_A04_20261011.json'
SELECTION = PROJECT_ROOT / 'archive/previous_analysis/config/context_reuse_accessibility_only.json'


def load_policy():
    p = json.loads(POLICY.read_text())
    if p['definition_version'] != DEFINITION or p['design_id'] != DEFINITION_VERSION:
        raise ValueError('Context definition mismatch')
    if p['income_mode'] != 'QUALIFIED_INCOME_PRIMARY_WITH_MATCHED_NO_INCOME_SENSITIVITY':
        raise ValueError('Unapproved primary income-mode change')
    return p


def jsonstat_cells(document, metadata, receipt):
    """Validate requested native categories and units before decoding Cartesian cells."""
    if document.get('class') != 'dataset' or document.get('version') != '2.0':
        raise ValueError('Expected JSON-stat2 dataset')
    dimensions = document['id']; sizes = document['size']
    if len(set(dimensions)) != len(dimensions) or len(sizes) != len(dimensions):
        raise ValueError('Duplicate/malformed dimensions')
    selectors = receipt['selection']['selected_codes']
    variables = {v['code']:v for v in metadata['variables']}
    if set(selectors) != set(variables) or set(dimensions) != set(selectors) | {'ContentsCode'}:
        raise ValueError('Unexpected statistical schema')
    codes = []
    for dim, size in zip(dimensions, sizes, strict=True):
        category = document['dimension'][dim]['category']
        index = category['index']
        ordered = list(index) if isinstance(index, list) else sorted(index, key=index.get)
        if (len(ordered) != size or len(set(ordered)) != size
                or (isinstance(index,dict) and set(index.values())!=set(range(size)))):
            raise ValueError('Duplicate/incomplete native keys')
        if dim in selectors:
            if set(ordered) != set(selectors[dim]) or not set(ordered) <= set(variables[dim]['values']):
                raise ValueError('Returned years/geography/selection differs from frozen request')
            labels = dict(zip(variables[dim]['values'], variables[dim]['valueTexts'], strict=True))
            if any(category['label'][c] != labels[c] for c in ordered):
                raise ValueError('Native labels differ from source schema')
        elif ordered != ['EliminatedValue']:
            raise ValueError('Unexpected implicit statistical measure')
        codes.append(ordered)
    values = document['value']; n = math.prod(sizes)
    if isinstance(values, list) and len(values) != n:
        raise ValueError('Incomplete values vector')
    units = document['dimension']['ContentsCode']['category'].get('unit', {})
    rows = []
    for i, coordinates in enumerate(itertools.product(*codes)):
        keys = dict(zip(dimensions, coordinates, strict=True))
        value = values[i] if isinstance(values, list) else values.get(str(i))
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value)):
            raise ValueError('Invalid statistical value')
        unit = units.get(keys['ContentsCode'], {}).get('base')
        if not unit:
            raise ValueError('Missing native unit')
        rows.append({'keys': keys, 'value': value, 'unit': unit})
    return rows


def gross_density(population, area_m2, metric_crs):
    crs = CRS.from_user_input(metric_crs)
    if not crs.is_projected or any(a.unit_conversion_factor != 1 for a in crs.axis_info):
        raise ValueError('Gross area requires recorded projected metre CRS')
    if population is None or area_m2 is None:
        return None
    if not math.isfinite(population) or not math.isfinite(area_m2) or population <= 0 or area_m2 <= 0:
        raise ValueError('Invalid population/gross area; no filling')
    return math.log(population / (area_m2 / 1_000_000))


def join_context(assignments, areas):
    """Retain every audit row; strict many-to-one, NULLs/ambiguity never guessed."""
    lookup = {}
    for r in areas:
        if r['area_id'] in lookup:
            raise ValueError('Duplicate context area ID; would multiply rows')
        lookup[r['area_id']] = r
    seen = set(); joined = []
    for r in assignments:
        if r['listing_id'] in seen:
            raise ValueError('Duplicate listing key')
        seen.add(r['listing_id'])
        area = lookup.get(r['area_id']) if r.get('status') == 'unique' and r.get('inside_boundary') is True else None
        joined.append({'listing_id':r['listing_id'], 'area_id':None if area is None else area['area_id'],
                       'log_population_density':None if area is None else area['log_population_density'],
                       'income_100k_dkk':None if area is None else area['income_100k_dkk']})
    return joined


def anchor_point(policy, records):
    anchor = policy['anchor']
    if anchor is None:
        return None
    lon, lat = anchor['coordinates']
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        raise ValueError('Invalid public anchor coordinate')
    if 'stedsnummer' in anchor:
        r = records['a04_20261011_anchor_ssr']; j = json.loads((PROJECT_ROOT/r['local_location']).read_text())
        matches = [n for n in j['navn'] if n['stedsnummer']==anchor['stedsnummer']
                   and n['navneobjekttype']=='Rådhus' and n['stedstatus']=='aktiv'
                   and n['skrivemåte']=='Rådhuset' and n['skrivemåtestatus']=='godkjent og prioritert'
                   and any(k['kommunenummer']=='0301' for k in n['kommuner'])]
        if len(matches)!=1 or [matches[0]['representasjonspunkt']['øst'],matches[0]['representasjonspunkt']['nord']] != anchor['coordinates']:
            raise ValueError('Official public civic point identity/coordinates mismatch')
        api = json.loads((PROJECT_ROOT/records['a04_20261011_anchor_openapi']['local_location']).read_text())
        parameter = next(p for p in api['paths']['/navn']['get']['parameters'] if p['name']=='utkoordsys')
        if parameter['schema']['default'] != 4258 or anchor['source_crs'] != 'EPSG:4258':
            raise ValueError('Official point source CRS mismatch')
    for item in anchor.get('evidence', []):verify_evidence(PROJECT_ROOT,item)
    point = Point(*Transformer.from_crs(anchor['source_crs'],4326,always_xy=True).transform(lon,lat))
    return point


def native_statistics(city, paths, records):
    result = []; diagnostics = {}
    for kind in ('population','income'):
        data = records['a04_20261011_'+kind+'_data']; schema = records['a04_20261011_'+kind+'_schema']
        if data['selection']['schema_sha256'] != schema['sha256']:
            raise ValueError('Statistical metadata dependency mismatch')
        document = json.loads((paths.root/data['local_location']).read_text())
        metadata = json.loads((paths.root/schema['local_location']).read_text())
        cells = jsonstat_cells(document, metadata, data)
        expected_unit = {'population':'Antall personer','income':'kroner'} if city=='oslo' else {'population':'antal','income':None}
        if any(c['unit']!=expected_unit[kind] for c in cells) and expected_unit[kind] is not None:
            raise ValueError('Unexpected native statistics unit')
        if city=='oslo' and kind=='population':
            grouped = {}
            for c in cells:grouped.setdefault(c['keys']['bosted'],[]).append(c['value'])
            # All 106 single-year ages (last 105+) were explicitly selected; never sum municipal totals with boroughs.
            if len(grouped)!=19 or any(len(v)!=106 for v in grouped.values()):
                raise ValueError('Missing age coverage')
            cells = [{'keys':{'bosted':code},'value':None if None in vals else sum(vals),'unit':'persons'} for code,vals in grouped.items()]
        for c in cells:
            keys = c['keys']; native = keys['bosted' if kind=='population' else 'Geografi'] if city=='oslo' else keys['Region']
            stat = ('population' if kind=='population' else 'mean_equivalised_after_tax_income') if city=='oslo' else {'000007Y7':'population','000008AA':'mean_equivalised_disposable_income','000008AB':'median_equivalised_disposable_income','000008A5':'income_eligible_persons'}[keys['ContentsCode']]
            if city=='stockholm' and (not native.startswith('0180R') or not native.endswith('_RegSO2025')):
                raise ValueError('Wrong municipality/native RegSO vintage')
            unit = c['unit']
            if city=='stockholm' and unit != ('tusentals kronor' if 'income' in stat and stat!='income_eligible_persons' else 'antal'):
                raise ValueError('Income/count unit confusion')
            if c['value'] is not None and c['value']<0:raise ValueError('Negative context value')
            result.append({'source_id':data['source_id'],'native_id':native,'measure':stat,'value':c['value'],
                           'unit':unit,'currency':'NOK' if kind=='income' and city=='oslo' else 'SEK' if 'income' in stat and stat!='income_eligible_persons' else None,
                           'reference_period':data['reference_period'],'geography':'Oslo BEF001 statistical borough/native total/address-unlocated' if city=='oslo' and kind=='population' else 'Oslo INN003 borough/combined88/native total' if city=='oslo' else 'RegSO2025 native statistics; NOT validation geography',
                           'source_sha256':data['sha256'],'record':{'source_metadata_sha256':schema['sha256'],'request_sha256':data['request_sha256'],
                           'source_updated':document.get('updated'),'statistical_note':document.get('note'),'native_keys':keys,'source_validation':'VALIDATED_NATIVE_SOURCE_ONLY','spatial_join':'NOT_JOINED'}})
        observed = [c['value'] for c in cells if c['value'] is not None]
        diagnostics[kind] = {'native_cells':len(cells),'missing_cells':len(cells)-len(observed),
                             'distinct_observed_values':len(set(observed)),'source_updated':document.get('updated')}
    if city=='stockholm':
        # Exact source ID match is QA, not permission for listing joins or RegSO folds.
        import geopandas as gpd
        candidates = list((PROJECT_ROOT/'data/raw/v4/research_design_v4/stockholm/2026-06-30/scb_regso_2025_20261011_geopackage').glob('*.gpkg'))
        if len(candidates)!=1:raise ValueError('Preserved RegSO source unavailable')
        # Source pin is verified by selected_evidence before entering this function.
        frame = gpd.read_file(candidates[0]); ids=set(frame.loc[frame.kommunkod=='0180','regsokod'])
        statsids={r['native_id'].removesuffix('_RegSO2025') for r in result}
        if len(ids)!=127 or ids!=statsids:raise ValueError('Native statistics/municipal mask component IDs differ')
        diagnostics['native_id_mask_match']={'count':127,'status':'EXACT_NATIVE_ID_MATCH_ONLY_NOT_ANALYSIS_APPROVAL'}
    return result, diagnostics


def copenhagen_context():
    """Read approved V3 SQL, independently check source-derived numbers; no V3 writes."""
    from src.db.connection import get_engine as v3_engine
    from src.pipeline.qualified_income import validate, verify_sql, source_rows
    from src.pipeline.protocol import DESIGN
    from src.ingestion.download_copenhagen_statbank import decode_csv
    import csv, io
    validate(DESIGN)
    income = {r['analysis_area']:r for r in source_rows()}
    city_path=PROJECT_ROOT/'data/raw/copenhagen_statbank/2026-09-29/tables/KKBEF1.csv'
    city_meta=json.loads((city_path.parent.parent/'metadata/KKBEF1.json').read_text())
    codes=city_meta['selected_codes']
    if codes!={'var1':[str(i) for i in range(1001,1011)],'var2':['TOT'],'var3':['TOT'],'var4':['TOT'],'var5':['2026K3']}:
        raise ValueError('Inherited population selector changed')
    row=decode_csv(city_path.read_bytes())
    if len(row)!=1 or row[0][:4]!=['Marital status total','Age total','Sex total','2026Q3'] or len(row[0])!=14:
        raise ValueError('Inherited district population schema changed')
    populations={'cph_'+str(i+1).zfill(2):int(v) for i,v in enumerate(row[0][4:])}
    national=PROJECT_ROOT/'data/raw/municipality_statbank/2026-09-29/tables/FOLK1A.csv'
    raw=list(csv.DictReader(io.StringIO(national.read_text(encoding='utf-8-sig')),delimiter=';'))
    frb=[r for r in raw if r['OMRÅDE'].split(' ')[0]=='147']
    if (len(frb)!=1 or tuple(frb[0][key].split(' ')[0] for key in ('KØN','ALDER','CIVILSTAND','TID'))
            !=('TOT','IALT','TOT','2026K3')):raise ValueError('Ambiguous/changed Frederiksberg population selection')
    populations['frederiksberg_0147']=int(frb[0]['INDHOLD'])
    engine=v3_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY');verify_sql(conn)
            areas=[dict(r) for r in conn.execute(text('SELECT a.analysis_area AS area_id,a.population_count,a.population_period,a.area_km2,a.log_population_density,a.income_100k_dkk,a.crs_epsg,ST_Area(g.geom_25832) AS native_area_m2 FROM v3_features.area_context a JOIN v3_spatial.analysis_areas g ON a.analysis_area=g.area_id ORDER BY a.analysis_area')).mappings()]
            anchor=conn.execute(text("SELECT ST_X(geom_4326),ST_Y(geom_4326) FROM v3_spatial.reference_points WHERE reference_id='city_hall_square'")).one()
            if tuple(anchor)!=(12.568809986,55.675902629):raise ValueError('Inherited SQL public anchor changed')
        if len(areas)!=11 or set(populations)!={r['area_id'] for r in areas}:raise ValueError('Incomplete inherited context')
        for r in areas:
            expected=float(Decimal(income[r['area_id']]['equiv_disposable_income_2024'])/Decimal(100000))
            if (r['population_period']!='2026Q3' or r['population_count']!=populations[r['area_id']] or r['crs_epsg']!=25832
                or not math.isclose(r['income_100k_dkk'],expected,abs_tol=1e-12)
                or not math.isclose(r['area_km2'],r['native_area_m2']/1e6,abs_tol=1e-12)
                or not math.isclose(r['log_population_density'],gross_density(r['population_count'],r['native_area_m2'],'EPSG:25832'),abs_tol=1e-12)):
                raise ValueError('Inherited SQL context differs from exact sources/formula/gross geometry')
        return areas, {'income_decision_sha256':sha256_file(PROJECT_ROOT/'config/qualified_income_decision.json'),
                        'income_records_sha256':canonical_hash(source_rows()),'qualified_area_count':11,
                        'population_period':'2026Q3 (2026-07-01; one day after batch)',
                        'income_period':'2024','density_definition':'log(population/gross native assignment polygon km2); water inclusion and statistical boundary vintage unverified; no rescaling',
                        'district_population_sha256':sha256_file(city_path),'municipality_population_sha256':sha256_file(national)}
    finally:engine.dispose()


def prepare(conn, paths, *, read_only=False):
    s=paths.scope; policy=load_policy(); p=policy['cities'][s.city]
    if s.design_id!=DEFINITION_VERSION:raise ValueError('Active context design required')
    listing_policy=json.loads((PROJECT_ROOT/'archive/previous_analysis/config/listing_reuse_accessibility_only.json').read_text())['cities'][s.city]
    digest=listing_policy['manifest_sha256'];reuse=reuse_listing_source(conn,s,digest)
    geo=selected_evidence(conn,s,digest)
    records=[]
    for source in p['sources']:
        verify_evidence(paths.root,source['receipt']);r=source['record']
        if sha256_file(paths.root/r['local_location'])!=r['sha256']:raise ValueError('Context raw source changed')
        if json.loads((paths.root/source['receipt']['path']).read_text())!=r:
            raise ValueError('Context source policy differs from immutable receipt')
        if r.get('reused_from') and sha256_file(paths.root/r['reused_from'])!=r['sha256']:
            raise ValueError('Approved original V3 source bytes changed')
        records.append(r)
    for pin in p['failed_receipts']:verify_evidence(paths.root,pin)
    if s.city=='copenhagen_frederiksberg':
        for pin in policy['v3_evidence']:verify_evidence(paths.root,pin)
    recordmap={r['source_id']:r for r in records};point=anchor_point(p,recordmap)
    if point is not None:
        mask=conn.scalar(text('SELECT ST_Covers(geom,ST_SetSRID(ST_MakePoint(:lon,:lat),4326)) FROM v4_spatial.geography_masks WHERE '+SCOPE_SQL+' AND design_id=:design_id'),{**s.params(),'run_id':geo['source_geography_run_id'] if 'source_geography_run_id' in geo else json.loads((PROJECT_ROOT/'archive/previous_analysis/config/geography_reuse_accessibility_only.json').read_text())['cities'][s.city]['run_id'],'lon':point.x,'lat':point.y})
        if mask is not True:raise ValueError('Public civic anchor outside approved municipal mask')
    assignments=[];areas=[];cells=[];blockers=[]
    if s.city=='copenhagen_frederiksberg':
        areas,diagnostics=copenhagen_context()
        rows=read_listing_audit(conn,s,digest)
        gs=json.loads((PROJECT_ROOT/'archive/previous_analysis/config/geography_reuse_accessibility_only.json').read_text())['cities'][s.city]
        audits=conn.execute(text('SELECT record FROM v4_spatial.geography_listing_audit WHERE '+SCOPE_SQL+' AND design_id=:design_id ORDER BY listing_id'),{**s.params(),'run_id':gs['run_id']}).scalars().all()
        if geo['analysis_status']!='QUALIFIED_INHERITED_OPERATIONAL' or not p['context_join_allowed']:raise ValueError('Unapproved Copenhagen context join')
        assignments=join_context(audits,areas);listingmap={str(r['listing_id']):r for r in rows}
        if set(listingmap)!={r['listing_id'] for r in assignments}:raise ValueError('Context row multiplication/loss')
        project=Transformer.from_crs(4326,p['metric_crs'],always_xy=True).transform
        centre=Point(*project(point.x,point.y))
        for r in assignments:
            raw=listingmap[r['listing_id']];lon,lat=raw.get('longitude'),raw.get('latitude')
            finite=(isinstance(lon,(int,float)) and isinstance(lat,(int,float))
                    and math.isfinite(lon) and math.isfinite(lat) and -180<=lon<=180 and -90<=lat<=90)
            r['distance_centre_euclidean_km']=Point(*project(lon,lat)).distance(centre)/1000 if finite else None
        diagnostics['listing_rows']=len(assignments);diagnostics['joined_rows']=sum(r['area_id'] is not None for r in assignments)
        diagnostics['unmatched_or_outside_rows']=len(assignments)-diagnostics['joined_rows']
        for a in areas:
            for measure,value,unit,period in [('population',a['population_count'],'persons','2026Q3'),('log_population_density',a['log_population_density'],'log persons/km2','2026Q3'),('income_100k_dkk',a['income_100k_dkk'],'100000 DKK','2024')]:
                cells.append({'source_id':'approved_v3_context','native_id':a['area_id'],'measure':measure,'value':value,'unit':unit,'currency':'DKK' if measure=='income_100k_dkk' else None,'reference_period':period,'geography':'V3 official ten districts plus Frederiksberg peer','source_sha256':diagnostics['income_records_sha256'] if measure=='income_100k_dkk' else diagnostics['district_population_sha256'] if a['area_id'].startswith('cph_') else diagnostics['municipality_population_sha256'],'record':{'native_gross_area_m2':a['native_area_m2'],'metric_crs':p['metric_crs'],'source_validation':'QUALIFIED_INHERITED_WITH_CAVEATS'}})
    else:
        if p['context_join_allowed']:raise ValueError('New-city listing joins not authorized with unqualified analysis geography')
        cells,diagnostics=native_statistics(s.city,paths,recordmap)
        blockers.extend(geo['blockers']);blockers.append('Area-dependent density/context assignment NOT_JOINED; qualified matching analysis geometry required')
        blockers.append('Three-city income concept/scaling not qualified; frozen pre-fit researcher income decision required')
        if s.city=='oslo':blockers.extend(['INN003 combines Sentrum, Marka and no registered address (88); cannot distribute to polygons 16/17','Oslo statistical-source reuse licence unresolved; SSB upstream licence does not establish city-service terms'])
    if point is None:blockers.append(p['anchor_blocker'])
    manifest={'version':s.version,'city':s.city,'snapshot':s.snapshot,'purpose':s.purpose,'records':sorted(records,key=lambda r:r['source_id'])}
    md=canonical_hash(manifest)
    if read_only and not paths.manifest(md).is_file():raise ValueError('Original context manifest absent; audit cannot create it')
    if not read_only:_,manifest=freeze_sources(paths,records)
    summary={'definition_version':DEFINITION,**s.params(),'status':'BLOCKED' if blockers else 'QUALIFIED',
             'manifest_sha256':md,'listing_manifest_sha256':digest,'listing_run_id':reuse['source_scope']['run_id'],
             'geography_manifest_sha256':geo['geography_manifest_sha256'],
             'geography_run_id':json.loads((PROJECT_ROOT/'archive/previous_analysis/config/geography_reuse_accessibility_only.json').read_text())['cities'][s.city]['run_id'],
             'policy_sha256':canonical_hash(p),'metric_crs':p['metric_crs'],'anchor':p['anchor'],
             'acquisition_status':'REUSED_APPROVED_V3' if s.city=='copenhagen_frederiksberg' else 'ACQUIRED_NATIVE_STATISTICS',
             'source_validation_status':'QUALIFIED_INHERITED_WITH_CAVEATS' if s.city=='copenhagen_frederiksberg' else 'VALIDATED_NATIVE_SOURCE_ONLY',
             'spatial_join_status':'JOINED_INHERITED_OPERATIONAL_WITH_UNMATCHED_RETAINED' if assignments else 'NOT_JOINED_BLOCKED_GEOGRAPHY',
             'final_qualification_status':'QUALIFIED_INHERITED_WITH_CAVEATS' if s.city=='copenhagen_frederiksberg' else 'BLOCKED',
             'income_mode':policy['income_mode'],'diagnostics':diagnostics,'native_context_cells':len(cells),
             'native_context_records_sha256':canonical_hash(cells),'private_assignments_sha256':canonical_hash(assignments),
             'blockers':blockers,'research_executed':False,'source_reingested':False,'samples_frozen':False}
    return summary,cells,assignments,manifest


def persist(conn, scope, summary, cells, assignments, manifest):
    verify_database(conn,synthetic=scope.purpose=='synthetic')
    if summary['city']!=scope.city or summary['design_id']!=scope.design_id or summary['definition_version']!=DEFINITION:
        raise ValueError('Context parent identity mismatch')
    if scope.city!='copenhagen_frederiksberg' and assignments:raise ValueError('Unqualified new-city listing joins forbidden')
    if canonical_hash(cells)!=summary['native_context_records_sha256'] or canonical_hash(assignments)!=summary['private_assignments_sha256']:
        raise ValueError('Context child hash mismatch')
    digest=register_manifest(conn,scope,manifest)
    if digest!=summary['manifest_sha256']:raise ValueError('Context manifest mismatch')
    params={**scope.params(),'manifest':digest,'geo_run':summary['geography_run_id'],'geo_manifest':summary['geography_manifest_sha256'],
            'listing_run':summary['listing_run_id'],'listing_manifest':summary['listing_manifest_sha256'],
            'definition':DEFINITION,'summary_sha':canonical_hash(summary),'summary':json.dumps(summary,allow_nan=False)}
    conn.execute(text('INSERT INTO v4_features.context_qualifications (version,run_id,city,snapshot,design_id,purpose,definition_version,manifest_sha256,geography_run_id,geography_manifest_sha256,listing_run_id,listing_manifest_sha256,summary_sha256,summary) VALUES (:version,:run_id,:city,:snapshot,:design_id,:purpose,:definition,:manifest,:geo_run,:geo_manifest,:listing_run,:listing_manifest,:summary_sha,CAST(:summary AS jsonb))'),params)
    if cells:conn.execute(text('INSERT INTO v4_features.native_context_cells VALUES (:version,:run_id,:city,:snapshot,:design_id,:source_id,:native_id,:measure,:value,:unit,:reference_period,CAST(:record AS jsonb))'),[{**scope.params(),**r,'record':json.dumps(r,allow_nan=False)} for r in cells])
    if assignments:conn.execute(text('INSERT INTO v4_features.listing_context_audit VALUES (:version,:run_id,:city,:snapshot,:design_id,:listing_id,CAST(:record AS jsonb))'),[{**scope.params(),**r,'record':json.dumps(r,allow_nan=False)} for r in assignments])


def evidence(conn,scope):
    row=conn.execute(text('SELECT summary,summary_sha256 FROM v4_features.context_qualifications WHERE '+SCOPE_SQL+' AND design_id=:design_id'),scope.params()).one_or_none()
    if row is None or canonical_hash(row.summary)!=row.summary_sha256:raise ValueError('Frozen context receipt missing/changed')
    return row.summary


def selected_context(conn,scope,listing_manifest):
    policy=load_policy();selection=json.loads(SELECTION.read_text())
    if selection['design_id']!=scope.design_id:raise ValueError('Context selection design mismatch')
    chosen=selection['cities'][scope.city]
    c=Scope(scope.version,scope.city,scope.snapshot,chosen['run_id'],design_id=scope.design_id)
    if chosen['snapshot']!=scope.snapshot:raise ValueError('Context snapshot mismatch')
    summary=evidence(conn,c)
    if summary['manifest_sha256']!=chosen['manifest_sha256']:raise ValueError('Context selected manifest mismatch')
    if summary['listing_manifest_sha256']!=listing_manifest or summary['policy_sha256']!=canonical_hash(policy['cities'][scope.city]) or canonical_hash(summary)!=chosen['summary_sha256']:
        raise ValueError('Context source/policy/summary linkage mismatch')
    p=policy['cities'][scope.city]
    manifest=conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),{**scope.params(),'digest':chosen['manifest_sha256']})
    expected={'version':scope.version,'city':scope.city,'snapshot':scope.snapshot,'purpose':scope.purpose,
              'records':sorted([x['record'] for x in p['sources']],key=lambda r:r['source_id'])}
    if manifest!=expected or canonical_hash(manifest)!=chosen['manifest_sha256']:raise ValueError('Context immutable SQL manifest differs from pinned source policy')
    if scope.city=='copenhagen_frederiksberg':
        for pin in policy['v3_evidence']:verify_evidence(PROJECT_ROOT,pin)
    for x in p['sources']:
        verify_evidence(PROJECT_ROOT,x['receipt']);r=x['record']
        if sha256_file(PROJECT_ROOT/r['local_location'])!=r['sha256']:raise ValueError('Context source bytes changed')
        if r.get('reused_from') and sha256_file(PROJECT_ROOT/r['reused_from'])!=r['sha256']:raise ValueError('Original approved V3 context source changed')
    for pin in p['failed_receipts']:verify_evidence(PROJECT_ROOT,pin)
    return summary


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=('acquire','freeze','audit'))
    parser.add_argument('--version',required=True,choices=(VERSION,));parser.add_argument('--city',required=True,choices=CITIES)
    parser.add_argument('--snapshot',required=True);parser.add_argument('--run-id',required=True)
    parser.add_argument('--design-id',required=True,choices=(DEFINITION_VERSION,));args=parser.parse_args(argv);engine=None
    try:
        s=Scope(args.version,args.city,args.snapshot,args.run_id,design_id=args.design_id);paths=Paths(s)
        if args.command=='acquire':
            # Replay only exact inspected official requests. Existing immutable receipts are reused; never fetch a latest replacement.
            for x in load_policy()['cities'][s.city]['sources']:
                r=x['record'];reuse=None
                if r.get('reused_from'):reuse=(PROJECT_ROOT/r['reused_from'],r['sha256'],r['acquired_at_utc'])
                actual=acquire(paths,r['source_id'],r['filename'],r['source_url'],extent=r['geographic_extent'],licence=r['licence'],reference_period=r['reference_period'],source_crs=r['source_crs'],selection=r['selection'],reuse=reuse,request_json=r.get('request_json'),request_form=r.get('request_form'))
                if actual!=r:raise ValueError('Frozen context source receipt differs; create separately authorized new evidence')
            print(json.dumps({'status':'ACQUIRED_PINNED_SOURCES','research_executed':False}));return 0
        engine=get_engine()
        with engine.begin() as conn:
            if args.command=='audit':conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            verify_database(conn)
            if args.command=='freeze' and conn.scalar(text('SELECT count(*) FROM v4_features.context_qualifications WHERE '+SCOPE_SQL+' AND design_id=:design_id'),s.params()):raise ValueError('Committed context identity exists; use read-only audit')
            summary,cells,assignments,manifest=prepare(conn,paths,read_only=args.command=='audit')
            if args.command=='freeze':persist(conn,s,summary,cells,assignments,manifest)
            else:
                if summary!=evidence(conn,s):raise ValueError('Recomputed context differs from immutable SQL checkpoint')
                stored=conn.execute(text('SELECT record FROM v4_features.native_context_cells WHERE '+SCOPE_SQL+' AND design_id=:design_id'),s.params()).scalars().all()
                order=lambda r:(r['source_id'],r['native_id'],r['measure'])
                if sorted(stored,key=order)!=sorted(cells,key=order):raise ValueError('Native SQL context differs from verified source cells')
                stored_assignments=conn.execute(text('SELECT record FROM v4_features.listing_context_audit WHERE '+SCOPE_SQL+' AND design_id=:design_id ORDER BY listing_id'),s.params()).scalars().all()
                if stored_assignments!=assignments:raise ValueError('Private SQL context assignment differs from verified many-to-one join')
            print(json.dumps(summary,indent=2,allow_nan=False))
        return 2 if summary['status']=='BLOCKED' else 0
    except Exception as error:
        print(json.dumps({'status':'BLOCKED','reason':str(error) if isinstance(error,(ValueError,RuntimeError)) else type(error).__name__,'research_executed':False}));return 2
    finally:
        if engine is not None:engine.dispose()


if __name__=='__main__':raise SystemExit(main())
