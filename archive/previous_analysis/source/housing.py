"""Step 5: immutable housing-source audits, never H assignment or model fitting."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from decimal import Decimal, InvalidOperation
import io
import itertools
import json
from pathlib import Path
import re
import zipfile

from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.v4.identity import Paths, Scope, freeze_sources, write_once
from src.v4.listings import acquire, encoded_json
from src.v4.persistence import get_engine, register_manifest, verify_database, SCOPE_SQL

DEFINITION = 'v4_housing_sources_20261011'
POLICY = PROJECT_ROOT / 'config/v4/housing_sources.json'
QUARTERS = ('2025K1', '2025K2', '2025K3', '2025K4')


def number(value, *, locale='dot_decimal', count=False):
    """Explicit source locale; suppressed/missing stays NULL, never zero."""
    if value is None or value in ('', '..', '...', '-', ':'):
        return None
    if isinstance(value, bool):
        raise ValueError('Boolean is not a housing measurement')
    value = str(value)
    if locale == 'dot_decimal':
        pattern = r'[0-9]+(?:\.[0-9]+)?'
    elif locale == 'danish_display':
        pattern = r'(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+)(?:,[0-9]+)?'
    else:
        raise ValueError('Unqualified numeric locale')
    if not re.fullmatch(pattern, value):
        raise ValueError('Invalid housing numeric cell/locale')
    if locale == 'danish_display':
        value = value.replace('.', '').replace(',', '.')
    try:
        result = Decimal(value)
    except InvalidOperation as error:
        raise ValueError('Invalid housing measurement') from error
    if not result.is_finite() or result < 0 or (count and result != result.to_integral_value()):
        raise ValueError('Invalid housing measurement/count')
    return int(result) if count else float(result)


def annual_mean(quarters, *, statistic, same_sample_denominators_verified):
    """Only mathematically justified aggregation; real BM inputs lack this proof."""
    if statistic != 'arithmetic_mean' or not same_sample_denominators_verified:
        raise ValueError('Annual aggregation BLOCKED: exact mean denominators required; never average medians')
    if len(quarters) != 4 or {r['period'] for r in quarters} != set(QUARTERS):
        raise ValueError('Exactly four nonoverlapping 2025 quarters required')
    if any(r['price_m2_native'] is None or r['sale_count'] is None or r['sale_count'] <= 0 for r in quarters):
        raise ValueError('Suppressed/unknown quarter cannot be manufactured')
    total = sum(r['sale_count'] for r in quarters)
    return sum(r['price_m2_native'] * r['sale_count'] for r in quarters) / total


def bm_metadata(path):
    soup = BeautifulSoup(path.read_bytes().decode('cp1252'), 'html.parser')
    selects = {s.get('name'): s for s in soup.find_all('select')}
    if not {'var1', 'var2', 'var3', 'var4'} <= set(selects):
        raise ValueError('BM native selector schema absent')
    options = {k: {o['value']: o.get_text(' ', strip=True) for o in selects[k].find_all('option')}
               for k in ('var1', 'var2', 'var3', 'var4')}
    if options['var2'].get('2') != 'Ejerlejlighed' or not set(QUARTERS) <= set(options['var4']):
        raise ValueError('BM property category/reference period changed')
    if len(set(options['var1'].values())) != len(options['var1']):
        raise ValueError('Ambiguous native postal labels')
    return options


def bm_csv(path, metadata, query_html, *, measure):
    """Actual export has no header; its frozen HTML supplies quarter order."""
    table = BeautifulSoup(query_html.read_bytes().decode('cp1252'), 'html.parser').find('table', id='pxtable')
    if table is None or [c.get_text(' ', strip=True) for c in table.find_all('tr')[1].find_all(['th', 'td'])] != ['', *QUARTERS]:
        raise ValueError('BM quarter order unverified')
    labels = {label: code for code, label in metadata['var1'].items()}
    result = {}; native = list(csv.reader(io.StringIO(path.read_bytes().decode('cp1252')), delimiter=';'))
    for cells in native:
        if len(cells) != 7 or cells[:2] != [measure, 'Ejerlejlighed'] or cells[2] not in labels:
            raise ValueError('BM CSV schema/property/measure/geography failure')
        area = labels[cells[2]]
        for period, value in zip(QUARTERS, cells[3:]):
            key = (area, period)
            if key in result:
                raise ValueError('Duplicate BM native area/period')
            result[key] = number(value, count=measure == 'Solgte boliger')
    if {a for a, _ in result} != set(metadata['var1']):
        raise ValueError('BM source area frame incomplete; no silent omission')
    return result


def jsonstat_cells(dataset):
    """Validate actual JSON-stat dimensions, dense/sparse cells and suppression."""
    if dataset.get('class') != 'dataset' or dataset.get('version') != '2.0':
        raise ValueError('JSON-stat2 dataset required')
    ids, sizes = dataset['id'], dataset['size']
    if len(ids) != len(set(ids)) or len(ids) != len(sizes) or any(type(s) is not int or s < 1 for s in sizes):
        raise ValueError('Invalid JSON-stat dimension frame')
    categories = []
    for code, size in zip(ids, sizes):
        category = dataset['dimension'][code]['category']; index = category['index']
        if not isinstance(index, dict) or sorted(index.values()) != list(range(size)):
            raise ValueError('Duplicate/incomplete JSON-stat category indices')
        labels = category['label']
        if set(labels) != set(index) or len(set(labels.values())) != len(labels):
            raise ValueError('Ambiguous/missing JSON-stat native labels')
        categories.append([(key, labels[key]) for key in sorted(index, key=index.get)])
    total = 1
    for size in sizes:
        total *= size
    values, statuses = dataset['value'], dataset.get('status', {})
    def cells(value):
        if isinstance(value, list):
            if len(value) != total:
                raise ValueError('Truncated JSON-stat cells')
            return {str(i): cell for i, cell in enumerate(value)}
        if not isinstance(value, dict) or any(not k.isdigit() or not 0 <= int(k) < total for k in value):
            raise ValueError('Invalid sparse JSON-stat cells')
        return value
    values = cells(values)
    if statuses:
        statuses = cells(statuses)
    result = []
    for i, selection in enumerate(itertools.product(*categories)):
        value = values.get(str(i)); status = statuses.get(str(i))
        if status and value is not None:
            raise ValueError('Flagged nonmissing measurement requires explicit source review')
        result.append((dict(zip(ids, selection)), value, status))
    return result


def oslo_geography(path):
    """Official XLSX preserves native IDs/names; API positions are not area IDs."""
    frame = pd.read_excel(path, sheet_name='Sheet1', dtype=str).fillna('')
    result = {}
    for level, code, name in [('bydel', 'Bydel_nr', 'Bydel_navn'),
                              ('delbydel_2017', 'Delbydel_2017_nr', 'Delbydel_2017_navn'),
                              ('grunnkretsomrade', 'Grunnkretsområde_nr', 'Grunnkretsområde_navn')]:
        if not {code, name} <= set(frame):
            raise ValueError('Official Oslo geographic schema changed')
        for area, label in frame[[code, name]].drop_duplicates().values.tolist():
            if not area:
                continue
            if area in result and result[area] != (level, label):
                raise ValueError('Ambiguous Oslo geography; no guessed crosswalk')
            result[area] = (level, label)
    return result


def bol018(dataset, metadata, geography, source_id):
    expected = {'ContentsCode', 'år', 'geografi', 'boligtype', 'statistikkvariabel'}
    if set(dataset['id']) != expected or 'BOL018' not in metadata['title']:
        raise ValueError('BOL018 schema/table mismatch')
    meta = {v['code']: dict(zip(v['values'], v['valueTexts'])) for v in metadata['variables']}
    if set(meta) != expected - {'ContentsCode'}:
        raise ValueError('BOL018 metadata dimension change')
    groups = {}
    for dims, value, status in jsonstat_cells(dataset):
        for code in meta:
            if meta[code].get(dims[code][0]) != dims[code][1]:
                raise ValueError('BOL018 query labels disagree with frozen metadata')
        if dims['år'][1] != '2025' or dims['boligtype'][1] != 'Blokkleilighet':
            raise ValueError('Wrong BOL018 reference period/category')
        api_code, area = dims['geografi']; measure = dims['statistikkvariabel'][1]
        if measure not in {'Antall salg', 'Gjennomsnitt antall kvadratmeter', 'Gjennomsnitt kvadratmeterpris'}:
            raise ValueError('Unknown BOL018 measurement')
        group = groups.setdefault(area, {'api_geography_code': api_code, 'cells': {}, 'flags': {}})
        if measure in group['cells']:
            raise ValueError('Duplicate BOL018 area/measure')
        group['cells'][measure] = number(value, count=measure == 'Antall salg'); group['flags'][measure] = status
    result = []
    if len(groups) != len(meta['geografi']):
        raise ValueError('Incomplete BOL018 native frame')
    for area, group in groups.items():
        if len(group['cells']) != 3:
            raise ValueError('Incomplete BOL018 measurements')
        level, name = geography.get(area, ('unresolved_native_geography', None))
        # 100000 is not guessed to be a municipal total. It remains unresolved.
        price = group['cells']['Gjennomsnitt kvadratmeterpris']
        if price is not None and price <= 0:
            raise ValueError('Nonpositive native housing price')
        result.append(dict(source_id=source_id, source_area_id=area, area_name=name, geography_level=level,
                           period='2025', property_category='Blokkleilighet', currency='NOK', unit='NOK/m2',
                           statistic='source_reported_mean', price_m2_native=price,
                           sale_count=group['cells']['Antall salg'], mean_area_m2=group['cells']['Gjennomsnitt antall kvadratmeter'],
                           source_flags=group['flags'], api_geography_code=group['api_geography_code'],
                           annual=True, area_definition='BRA/BRA-i', native_housing_join_pending=True))
    return result


def standalone_gates(records, *, legal_reuse_verified, annual_measure_verified,
                     geography_definitions_verified, boundary_provisional):
    """Source QA is distinct from final sample coverage; never QUALIFIED in Step 5."""
    annual = [r for r in records if r['annual'] and r['geography_level'] != 'unresolved_native_geography']
    supported = [r for r in annual if r['price_m2_native'] is not None and r['price_m2_native'] > 0
                 and r['sale_count'] is not None and r['sale_count'] >= 20]
    per_level = {}
    for level in sorted({r['geography_level'] for r in records}):
        rows = [r for r in records if r['geography_level'] == level]
        good = [r for r in supported if r['geography_level'] == level]
        per_level[level] = dict(native_areas=len({r['source_area_id'] for r in rows}),
                               missing_prices=sum(r['price_m2_native'] is None for r in rows),
                               nonpositive_prices=sum(r['price_m2_native'] is not None and r['price_m2_native'] <= 0 for r in rows),
                               unknown_sale_counts=sum(r['sale_count'] is None for r in rows),
                               zero_sale_counts=sum(r['sale_count'] == 0 for r in rows),
                               preferred_annual_support_areas=len(good),
                               distinct_supported_prices=len({r['price_m2_native'] for r in good}))
    enough = any(v['preferred_annual_support_areas'] >= 10 and v['distinct_supported_prices'] > 1 for v in per_level.values())
    passed = bool(records and legal_reuse_verified and annual_measure_verified and geography_definitions_verified and enough)
    return dict(metadata_status='METADATA_VERIFIED', data_status='DATA_ACQUIRED' if records else 'BLOCKED',
                preliminary_qa_status='PRELIMINARY_QA_PASSED' if passed else 'BLOCKED',
                spatial_status='PROVISIONAL_BOUNDARY' if boundary_provisional else 'SPATIAL_JOIN_PENDING',
                final_qualification='BLOCKED', model_gate='BLOCKED', listing_housing_coverage=None,
                represented_housing_areas=None, low_high_group_support=None, per_level=per_level,
                reference_frame_frozen=False, listing_H_assigned=False)


def load_policy():
    policy = json.loads(POLICY.read_text())
    if policy.get('version') != 'research_design_v4' or policy.get('definition_version') != DEFINITION:
        raise ValueError('Explicit V4 housing policy required')
    if policy['safeguards'] != {'preferred_minimum_annual_sales': 20, 'minimum_usable_areas': 10,
                              'minimum_final_listing_coverage': 0.8, 'minimum_areas_per_housing_group': 4,
                              'minimum_listings_per_housing_group': 100}:
        raise ValueError('Prospective housing safeguards changed; amendment required')
    return policy


def collect(paths, policy):
    entry = policy['cities'][paths.scope.city]; acquired = []; failures = []
    for spec in entry['sources']:
        kwargs = {key: spec[key] for key in ('extent', 'licence', 'reference_period', 'selection')}
        for key in ('request_json', 'request_form'):
            if spec.get(key) is not None:
                kwargs[key] = spec[key]
        record = acquire(paths, spec['source_id'], spec['filename'], spec['source_url'], **kwargs)
        receipt = paths.source(spec['source_id'], spec['filename'] + '.receipt.json')
        if sha256_file(receipt) != spec['receipt_sha256'] or record.get('sha256') != spec.get('sha256'):
            raise ValueError('Housing source/receipt changed; new source identity and amendment required')
        record = {**record, 'receipt_sha256': sha256_file(receipt)}
        (acquired if record['status'] == 'acquired' else failures).append(record)
    by_id = {r['source_id']:r for r in acquired}
    for source_id, grant in entry.get('verified_licences',{}).items():
        if source_id not in by_id:
            continue
        proof = by_id[grant['evidence_source_id']]
        proof_text = paths.source(proof['source_id'],proof['filename']).read_text()
        if grant['required_literal'] not in proof_text:
            raise ValueError('Frozen housing licence evidence does not support grant')
        # Enrich a NEW manifest; the earlier pending-licence receipt stays immutable.
        record = by_id[source_id]
        record['acquisition_receipt_licence'] = record['licence']
        record['licence'] = grant['licence']
        record['licence_evidence'] = {'source_id':proof['source_id'],'sha256':proof['sha256']}
    _, manifest = freeze_sources(paths, acquired)
    return manifest, failures


def assess(paths, policy, manifest, failures):
    city = paths.scope.city; entry = policy['cities'][city]; roles = entry['roles']
    by_id = {r['source_id']: r for r in manifest['records']}
    def source(role):
        r = by_id[roles[role]]
        return paths.source(r['source_id'], r['filename'])
    records = []; source_qa = {}; parser_errors = []
    try:
        if city == 'copenhagen_frederiksberg':
            m = bm_metadata(source('price_metadata')); cm = bm_metadata(source('count_metadata'))
            if m['var1'] != cm['var1']:
                raise ValueError('BM price/count native frames differ')
            prices = bm_csv(source('price_data'), m, source('price_query'), measure='Realiseret handelspris')
            counts = bm_csv(source('count_data'), cm, source('count_query'), measure='Solgte boliger')
            for (area, period), price in prices.items():
                records.append(dict(source_id=roles['price_data'], count_source_id=roles['count_data'], source_area_id=area,
                                    area_name=m['var1'][area], geography_level='native_postal_group', period=period,
                                    property_category='Ejerlejlighed', currency='DKK', unit='DKK/m2', statistic='source_reported_quarter_mean',
                                    price_m2_native=price, sale_count=counts[(area, period)], annual=False,
                                    issues=['nonpositive_reported_price'] if price is not None and price <= 0 else [],
                                    area_definition='Finans Danmark weighted floor area; apartment BBR area 100%', native_housing_join_pending=True))
            source_qa = dict(native_postal_groups=len(m['var1']), quarters=list(QUARTERS),
                             frederiksberg_groups_verified=all(m['var1'].get(k, '').startswith(k) for k in ('1800', '2000')),
                             copenhagen_labels_present=any('Kbh.K.' in label for label in m['var1'].values()),
                             municipal_membership='UNRESOLVED; both documented DAWA queries returned HTTP 410',
                             annual_measure='BLOCKED_EXACT_PRICE_DENOMINATORS_UNVERIFIED',
                             missing_quarter_prices=sum(v is None for v in prices.values()),
                             nonpositive_quarter_prices=sum(v is not None and v <= 0 for v in prices.values()),
                             positive_quarter_prices=sum(v is not None and v > 0 for v in prices.values()),
                             zero_price_with_positive_sales=sum(v == 0 and counts[k] is not None and counts[k] > 0 for k,v in prices.items()),
                             missing_price_with_at_least_five_reported_sales=sum(v is None and counts[k] is not None and counts[k]>=5 for k,v in prices.items()),
                             groups_with_four_positive_quarters=sum(all(prices[(area,q)] is not None and prices[(area,q)] > 0 for q in QUARTERS) for area in m['var1']),
                             suppressed_price_policy='provider minimum five trades; NULL retained',
                             annual_prices_constructed=0)
        elif city == 'oslo':
            d = json.loads(source('price_data').read_text(encoding='utf-8-sig'))
            m = json.loads(source('price_metadata').read_text(encoding='utf-8-sig'))
            records = bol018(d, m, oslo_geography(source('geography')), roles['price_data'])
            source_qa = dict(schema=d['id'], sizes=d['size'], updated=d['updated'], native_geographic_rows=len(records),
                             source='Boligmappa AS via Oslo municipality', reference_period='2025',
                             property_category='Blokkleilighet', area_definition='BRA/BRA-i',
                             price_definition='contract consideration including cooperative common debt',
                             revision='BOL018 replaced BOL012 April 2026; entire series revised to BRA/BRA-i',
                             unavailable_mean_cells=sum(v is None for v in d['value']),
                             null_status_symbols=dict(Counter(d.get('status',{}).values())),
                             suppression_rule='No explicit privacy suppression threshold located; low-count caution documented; NULL/dash retained',
                             unresolved_geographic_ids=[r['source_area_id'] for r in records if r['area_name'] is None],
                             geography_definition='Official hierarchy uses delbydel_2017; polygon vintage not qualified')
            licence = BeautifulSoup(source('licence').read_bytes(),'html.parser')
            if not any('NLOD_2_0' in a['href'] for a in licence.find_all('a',href=True)):
                raise ValueError('Oslo platform NLOD 2.0 licence evidence changed')
            alternative = json.loads(source('alternative_data').read_text())
            alt_cells = jsonstat_cells(alternative)
            if len(alt_cells) != 2 or any(dims['Region'][0] != '0301' or dims['Tid'][1] != '2025'
                                        or dims['Boligtype'][1] != 'Blokkleiligheter' for dims,_,_ in alt_cells):
                raise ValueError('SSB annual alternative scope changed')
            if {dims['ContentsCode'][0] for dims,_,_ in alt_cells} != {'KvPris','Omsetninger'}:
                raise ValueError('SSB alternative measurement schema changed')
            for dims,value,_ in alt_cells:
                number(value,count=dims['ContentsCode'][0]=='Omsetninger')
            source_qa['ssb_14545_alternative'] = dict(reference_period='2025',municipality='0301',geographic_units=1,
                                                     schema_verified=True,target_neighbourhood_measure=False)
        else:
            d = json.loads(source('sokhem_data').read_text())
            if d.get('license') != 'CC BY 4.0' or not isinstance(d.get('rows'), list) or not d['rows']:
                raise ValueError('SokHem documented open export schema/licence changed')
            slugs = [r['slug'] for r in d['rows']]
            valid_slugs = [s for s in slugs if isinstance(s,str) and s]
            duplicate_slugs = sorted(k for k,v in Counter(valid_slugs).items() if v>1)
            missing_slugs = len(slugs)-len(valid_slugs)
            if duplicate_slugs or missing_slugs:
                parser_errors.append('SokHem export has missing/duplicate municipality identifiers; no deduplication or target-H adoption')
            stockholm = [r for r in d['rows'] if r['slug'] == 'stockholm']
            if len(stockholm) != 1:
                raise ValueError('Stockholm municipal export absent/ambiguous')
            for row in d['rows']:
                number(row['soldCount'], count=True); number(row['medianPricePerSqm'])
            with zipfile.ZipFile(source('scb_data')) as archive:
                if archive.namelist() != ['TAB1151_sv.csv']:
                    raise ValueError('SCB bulk member changed')
                rows = list(csv.DictReader(io.StringIO(archive.read('TAB1151_sv.csv').decode('cp1252'))))
            if not rows or set(rows[0]) != {'region', 'år', 'tabellinnehåll', 'Försäljning av bostadsrätter'}:
                raise ValueError('SCB native bulk schema changed')
            selected = [r for r in rows if r['år'] == '2025']
            keys = [(r['region'], r['tabellinnehåll']) for r in selected]
            if not selected or len(keys) != len(set(keys)):
                raise ValueError('SCB 2025 cells absent/duplicate')
            source_qa = dict(sokhem_export_municipalities=len(d['rows']), stockholm_export_units=1,
                             sokhem_unique_municipality_slugs=len(set(valid_slugs)), sokhem_duplicate_slugs=duplicate_slugs,
                             sokhem_missing_municipality_slugs=missing_slugs,
                             sokhem_licence=d['license'], sokhem_last_sale=d['lastSoldAt'], sokhem_sample_floor=d['sampleFloor'],
                             sokhem_period='rolling; full-year 2025 not supplied', sokhem_property_scope='apartment-only not established in municipal export',
                             scb_2025_regions=len({r['region'] for r in selected}), scb_units='counts and total transaction prices in tkr, not price/m2',
                             scb_geography='county/metropolitan/national; not neighbourhood units', neighbourhood_2025_price_rows_acquired=0)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        parser_errors.append(type(error).__name__ + ': ' + str(error)); records = []
    gates = standalone_gates(records, legal_reuse_verified=entry['legal_reuse_verified'],
                             annual_measure_verified=entry['annual_measure_verified'],
                             geography_definitions_verified=entry['geography_definitions_verified'],
                             boundary_provisional=city == 'oslo')
    gates['metadata_status'] = 'BLOCKED' if parser_errors else 'METADATA_VERIFIED'
    # Stockholm acquired open alternative data, but no valid target housing records.
    if city == 'stockholm':
        gates['data_status'] = 'DATA_ACQUIRED'
        gates['target_data_status'] = 'BLOCKED'
        gates['acquisition_scope'] = 'ALTERNATIVES_ONLY; no 2025 neighbourhood target data'
    summary = dict(definition_version=DEFINITION, status='BLOCKED', **gates,
                   source_qa=source_qa, parsed_rows=len(records), source_files=len(manifest['records']),
                   parser_errors=parser_errors, blockers=entry['blockers'] + parser_errors,
                   failed_acquisitions=[{k:r.get(k) for k in ('source_id','source_url','http_status','status','receipt_sha256')} for r in failures],
                   policy_sha256=sha256_file(POLICY), adapter_sha256=sha256_file(Path(__file__)),
                   models_fitted=0, walking_features_calculated=0, step6_executed=False)
    return records, summary


def persist_housing(conn, scope, manifest, records, summary):
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    digest = register_manifest(conn, scope, manifest)
    conn.execute(text('INSERT INTO v4_raw.housing_ingestions '
                      '(version,run_id,city,snapshot,purpose,definition_version,manifest_sha256,summary) '
                      'VALUES (:version,:run_id,:city,:snapshot,:purpose,:definition,:digest,CAST(:summary AS jsonb))'),
                 {**scope.params(), 'definition':DEFINITION, 'digest':digest, 'summary':json.dumps(summary, allow_nan=False)})
    ids = {r['source_id'] for r in manifest['records']}; keys = set()
    for r in records:
        key = (r['source_id'],r['source_area_id'],r['geography_level'],r['period'])
        if key in keys or r['source_id'] not in ids or (r.get('count_source_id') and r['count_source_id'] not in ids):
            raise ValueError('Duplicate housing key/unregistered source')
        keys.add(key)
        conn.execute(text('INSERT INTO v4_raw.housing_area_period_audit '
                          '(version,run_id,city,snapshot,source_id,source_area_id,geography_level,period,record) '
                          'VALUES (:version,:run_id,:city,:snapshot,:source_id,:source_area_id,:geography_level,:period,CAST(:record AS jsonb))'),
                     {**scope.params(), **{k:r[k] for k in ('source_id','source_area_id','geography_level','period')},
                      'record':json.dumps(r, allow_nan=False)})
    return digest


def evidence(conn, paths):
    verify_database(conn, synthetic=paths.scope.purpose == 'synthetic')
    p = paths.scope.params()
    row = conn.execute(text('SELECT summary,manifest_sha256 FROM v4_raw.housing_ingestions WHERE '+SCOPE_SQL),p).mappings().one()
    actual = conn.scalar(text('SELECT count(*) FROM v4_raw.housing_area_period_audit WHERE '+SCOPE_SQL),p)
    if actual != row['summary']['parsed_rows']:
        raise ValueError('Authoritative housing audit counts differ')
    if row['summary'].get('per_level'):
        sql = """SELECT geography_level, count(DISTINCT source_area_id) AS native_areas,
          count(*) FILTER(WHERE record->>'price_m2_native' IS NULL) AS missing_prices,
          count(*) FILTER(WHERE (record->>'price_m2_native')::double precision<=0) AS nonpositive_prices,
          count(*) FILTER(WHERE record->>'sale_count' IS NULL) AS unknown_sale_counts,
          count(*) FILTER(WHERE (record->>'sale_count')::double precision=0) AS zero_sale_counts,
          count(*) FILTER(WHERE geography_level<>'unresolved_native_geography' AND record->>'annual'='true'
            AND (record->>'price_m2_native')::double precision>0 AND (record->>'sale_count')::double precision>=20) AS preferred_annual_support_areas,
          count(DISTINCT (record->>'price_m2_native')::double precision) FILTER(WHERE geography_level<>'unresolved_native_geography'
            AND record->>'annual'='true' AND (record->>'price_m2_native')::double precision>0
            AND (record->>'sale_count')::double precision>=20) AS distinct_supported_prices
          FROM v4_raw.housing_area_period_audit WHERE """ + SCOPE_SQL + ' GROUP BY geography_level'
        native = {r['geography_level']:{k:v for k,v in r.items() if k!='geography_level'}
                  for r in conn.execute(text(sql),p).mappings()}
        if native != row['summary']['per_level']:
            raise ValueError('PostgreSQL standalone housing QA differs from frozen source audit')
    manifest = conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE '
                                'version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),
                           {**p,'digest':row['manifest_sha256']})
    safe_sources = [{k:r.get(k) for k in ('source_id','source_url','final_url','acquired_at_utc','reference_period',
                                         'geographic_extent','source_crs','licence','local_location','sha256','receipt_sha256','size_bytes',
                                         'request_method','request_sha256')} for r in manifest['records']]
    fields = ('definition_version','status','metadata_status','data_status','target_data_status','acquisition_scope',
              'preliminary_qa_status','spatial_status','final_qualification','model_gate','listing_housing_coverage',
              'represented_housing_areas','low_high_group_support','per_level','reference_frame_frozen','listing_H_assigned',
              'source_qa','parsed_rows','source_files','parser_errors','blockers','failed_acquisitions','policy_sha256',
              'adapter_sha256','models_fitted','walking_features_calculated','step6_executed')
    return {**p, **{k:row['summary'][k] for k in fields if k in row['summary']},
            'manifest_sha256':row['manifest_sha256'], 'sources':safe_sources}


def _main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['acquire','ingest','audit'])
    for name in ('version','city','snapshot','run-id'):
        parser.add_argument('--'+name, required=True)
    a = parser.parse_args(argv); scope = Scope(a.version,a.city,a.snapshot,a.run_id); paths = Paths(scope)
    policy = load_policy()
    if a.command == 'acquire':
        manifest, failures = collect(paths,policy); _, summary = assess(paths,policy,manifest,failures)
        print(json.dumps({'city':scope.city,'status':summary['status'],'source_files':len(manifest['records']),
                          'parsed_rows':summary['parsed_rows'],'blockers':summary['blockers']}))
        return 2
    engine = get_engine()
    try:
        if a.command == 'ingest':
            with engine.connect() as conn:
                verify_database(conn)
                if conn.scalar(text('SELECT EXISTS(SELECT 1 FROM v4_raw.housing_ingestions WHERE '+SCOPE_SQL+')'),scope.params()):
                    raise ValueError('Committed housing ingestion cannot reopen; use audit')
            manifest, failures = collect(paths,policy); records, summary = assess(paths,policy,manifest,failures)
            with engine.begin() as conn:
                persist_housing(conn,scope,manifest,records,summary)
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            result = evidence(conn,paths)
        target = paths.report('housing_source_audit.json'); content=encoded_json(result)
        if target.exists():
            if target.read_bytes() != content:
                raise ValueError('Immutable housing report mismatch; never overwrite')
        else:
            write_once(target,content)
        print(json.dumps({'city':scope.city,'status':result['status'],'preliminary_qa_status':result['preliminary_qa_status'],
                          'parsed_rows':result['parsed_rows'],'manifest_sha256':result['manifest_sha256'],'models_fitted':0}))
        return 2  # A safe source checkpoint is not empirical qualification.
    finally:
        engine.dispose()


def main(argv=None):
    try:
        return _main(argv)
    except (ValueError,RuntimeError) as error:
        print(json.dumps({'status':'BLOCKED','reason':str(error),'models_fitted':0,'step6_executed':False}))
        return 2
    except (SQLAlchemyError,OSError,KeyError) as error:
        # Never emit SQL parameters, source cells, private paths or credentials.
        print(json.dumps({'status':'BLOCKED','reason':type(error).__name__,'models_fitted':0,'step6_executed':False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
