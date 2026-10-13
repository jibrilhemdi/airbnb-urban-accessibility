"""Explicit Stockholm source amendment; audit ingestion only, never model fitting."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import json
import math
from pathlib import Path
import sqlite3
import xml.etree.ElementTree as ET
import zipfile
from urllib.parse import parse_qsl, urlsplit

from bs4 import BeautifulSoup
import geopandas as gpd
from pyproj import CRS, Transformer
from shapely.geometry import MultiLineString, Point, mapping
from shapely.ops import transform, unary_union
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.v4.identity import Paths, Scope, freeze_sources, write_once
from src.v4.listings import acquire, audit_listings, encoded_json, persist_ingestion
from src.v4.persistence import SCOPE_SQL, get_engine, verify_database

POLICY = PROJECT_ROOT / 'config/v4/stockholm_boundary_amendment.json'
RESOLVED = 'RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT'


def load_policy():
    policy = json.loads(POLICY.read_text())
    if (policy['version'], policy['city'], policy['municipality'], policy['snapshot']) != (
            'research_design_v4', 'stockholm', '0180', '2026-06-30'):
        raise ValueError('Explicit authorized Stockholm amendment required')
    return policy


def municipal_areas(path):
    """Official bulk CSV is Windows-1252, decimal point; no guessed region match."""
    with zipfile.ZipFile(path) as archive:
        if archive.namelist() != ['TAB6420_sv.csv']:
            raise ValueError('Official municipal area archive schema changed')
        rows = csv.DictReader(io.StringIO(archive.read('TAB6420_sv.csv').decode('cp1252')))
        selected = [r for r in rows if r['region'] == '0180 Stockholm'
                    and r['arealtyp'] == 'totalt' and r['tabellinnehåll'] == 'Hektar'
                    and r['år'] in {'2025', '2026'}]
    if len(selected) != 2 or {r['år'] for r in selected} != {'2025', '2026'}:
        raise ValueError('Independent Stockholm municipality area metadata absent/duplicate')
    result = {r['år']: float(r['Land- och vattenareal per den 1 januari']) * 10000 for r in selected}
    if any(not math.isfinite(v) or v <= 0 for v in result.values()):
        raise ValueError('Invalid official municipal area')
    return result


def qualify_regso(frame, areas, policy):
    """Validate actual municipal attributes and topology before seeing listing counts."""
    required = {'regsokod', 'kommunkod', 'lanskod', 'version', 'referensdatum', 'objekttyp'}
    if not required <= set(frame.columns) or frame.crs != CRS.from_epsg(3006):
        raise ValueError('RegSO schema/CRS unqualified; EPSG:3006 required')
    if frame.regsokod.isna().any() or not frame.regsokod.is_unique:
        raise ValueError('Missing/duplicate RegSO IDs')
    selected = frame.loc[frame.kommunkod == '0180'].sort_values('regsokod')
    ids = selected.regsokod.tolist()
    if not ids or ids != policy['qualified_area_ids']:
        raise ValueError('Stockholm 0180 area frame changed/absent; new amendment required')
    for field, value in [('lanskod', '01'), ('version', policy['dataset_version']),
                         ('referensdatum', '20250101'), ('objekttyp', 'regso')]:
        if not selected[field].eq(value).all():
            raise ValueError('RegSO municipality/date/version attributes disagree')
    if (selected.geometry.isna().any() or selected.geometry.is_empty.any()
            or not selected.geometry.is_valid.all()
            or not selected.geom_type.isin(['Polygon', 'MultiPolygon']).all()):
        raise ValueError('Invalid/nonpolygon RegSO geometry; no automatic repair')
    union = unary_union(selected.geometry)
    if union.is_empty or not union.is_valid or union.geom_type not in {'Polygon', 'MultiPolygon'}:
        raise ValueError('Invalid dissolved boundary')
    parts = list(union.geoms) if union.geom_type == 'MultiPolygon' else [union]
    holes = sum(len(part.interiors) for part in parts)
    if len(parts) != policy['expected_components'] or holes != policy['expected_holes']:
        raise ValueError('Unexpected disconnected pieces/holes; investigate coverage before amendment')
    tolerance = policy['numerical_overlap_tolerance_m2']
    overlap = max(0.0, float(selected.area.sum()) - union.area)
    if overlap > tolerance or not all(union.covers(g) for g in selected.geometry):
        raise ValueError('RegSO overlap/coverage failure')
    # Adjacent municipalities may touch; positive area intersection must not occur.
    neighbours = frame.iloc[frame.sindex.query(union, predicate='intersects')]
    other_overlap = sum(g.intersection(union).area for g in neighbours.loc[neighbours.kommunkod != '0180'].geometry)
    if other_overlap > tolerance:
        raise ValueError('Stockholm geometry overlaps another municipality')
    if set(areas) != {'2025', '2026'} or any(
            abs(union.area - value) > policy['area_comparison_rounding_m2'] for value in areas.values()):
        raise ValueError('Independent municipal area/coverage check failed')
    geographic = transform(Transformer.from_crs(3006, 4326, always_xy=True).transform, union)
    xmin, ymin, xmax, ymax = geographic.bounds
    if (not geographic.is_valid or geographic.is_empty
            or not all(math.isfinite(v) for v in geographic.bounds)
            or not (-180 <= xmin <= xmax <= 180 and -90 <= ymin <= ymax <= 90)):
        raise ValueError('Transformed study boundary invalid')
    qa = dict(status='QUALIFIED_OPERATIONAL_2025', source_label='SCB-derived RegSO 2025 operational municipal union',
              reference_date='2025-01-01', dataset_version=policy['dataset_version'],
              certified_2026_geometry=False, native_crs='EPSG:3006', membership_crs='EPSG:4326',
              national_features=len(frame), national_municipalities=int(frame.kommunkod.nunique()),
              municipality_field='kommunkod', municipality_code='0180', county_code='01',
              area_id_field='regsokod', selected_area_ids=ids, selected_features=len(ids),
              geometry_type=union.geom_type, valid=True, empty=False, components=len(parts), holes=holes,
              summed_area_m2=float(selected.area.sum()), union_area_m2=union.area,
              overlap_m2=overlap, other_municipality_overlap_m2=other_overlap,
              coverage_all_selected=True, bounds_native=list(union.bounds), bounds_4326=list(geographic.bounds),
              official_municipal_area_m2=areas, official_area_difference_m2={k: union.area-v for k,v in areas.items()},
              area_rounding_tolerance_m2=policy['area_comparison_rounding_m2'],
              temporal_status=policy['temporal_review']['status'])
    return union, geographic, qa


def location_diagnostic(rows, native_union):
    """150m of dissolved exterior rings, excluding internal RegSO edges and holes."""
    parts = list(native_union.geoms) if native_union.geom_type == 'MultiPolygon' else [native_union]
    outer = MultiLineString([p.exterior for p in parts])
    project = Transformer.from_crs(4326, 3006, always_xy=True)
    counts = Counter()
    for row in rows:
        if row['longitude'] is None:
            row['distance_to_outer_boundary_m'] = None
            continue
        point = Point(*project.transform(row['longitude'], row['latitude']))
        distance = outer.distance(point)
        row['distance_to_outer_boundary_m'] = distance  # private audit only
        near = distance <= 150
        dwelling = row['dwelling_eligible']; positive = dwelling and row['positive_price']
        for group, eligible in [('raw', True), ('dwelling', dwelling), ('positive_price', positive)]:
            counts['outside_boundary_'+group] += int(eligible and row['inside_boundary'] is False)
            counts['boundary_150m_'+group] += int(eligible and near)
            for side, flag in [('inside', True), ('outside', False)]:
                counts[side+'_boundary_150m_'+group] += int(eligible and near and row['inside_boundary'] is flag)
    return dict(counts)


def scb_sources(paths, policy):
    """Only explicit SCB acquisition; Airbnb is read from its preserved freeze."""
    records = []
    for expected in policy['sources']:
        record = acquire(paths, expected['source_id'], expected['filename'], expected['source_url'],
                         extent=expected['geographic_extent'], licence=expected['licence'],
                         reference_period=expected['reference_period'], source_crs=expected['source_crs'],
                         selection=expected['selection'])
        if record['status'] != 'acquired' or record['sha256'] != expected['sha256']:
            raise ValueError('BLOCKED: SCB frozen acquisition unavailable/changed; new source amendment required')
        records.append(dict(record, receipt_sha256=sha256_file(paths.source(record['source_id'], record['filename']+'.receipt.json'))))
    by_suffix = {r['source_id'].removeprefix('scb_regso_2025_20261011_'): r for r in records}
    def source(key):
        r = by_suffix[key]
        return paths.source(r['source_id'], r['filename'])
    def url_identity(url):
        parts=urlsplit(url)
        return parts.scheme, parts.netloc, parts.path, sorted((k.lower(),v) for k,v in parse_qsl(parts.query))
    links=BeautifulSoup(source('page').read_text(),'html.parser').find_all('a',href=True)
    if url_identity(by_suffix['geopackage']['source_url']) not in [url_identity(a['href']) for a in links]:
        raise ValueError('GeoPackage URL is not linked by the frozen official RegSO page')
    if 'licence CC0' not in BeautifulSoup(source('licence').read_text(),'html.parser').get_text(' ',strip=True):
        raise ValueError('Official SCB open-data licence unverified')
    # Verify advertised feature type and actual DescribeFeatureType, not inferred names.
    caps = ET.parse(source('capabilities'))
    if 'stat:RegSO_2025' not in [e.text for e in caps.iter() if e.tag.endswith('}Name')]:
        raise ValueError('RegSO 2025 not advertised by official WFS')
    schema = ET.parse(source('schema'))
    names = {e.attrib.get('name') for e in schema.iter()}
    if not {'RegSO_2025', 'kommunkod', 'regsokod', 'referensdatum', 'sp_geometry'} <= names:
        raise ValueError('Official RegSO WFS schema changed')
    with sqlite3.connect(source('geopackage').resolve().as_uri()+'?mode=ro', uri=True) as conn:
        if conn.execute('SELECT table_name,data_type,srs_id FROM gpkg_contents').fetchall() != [('RegSO_2025', 'features', 3006)]:
            raise ValueError('Actual GeoPackage layer/CRS differs from qualified source')
        if conn.execute('SELECT column_name,geometry_type_name,srs_id FROM gpkg_geometry_columns').fetchall() != [('sp_geometry', 'POLYGON', 3006)]:
            raise ValueError('Actual GeoPackage geometry schema differs')
    frame = gpd.read_file(source('geopackage'), layer='RegSO_2025')
    native, geographic, qa = qualify_regso(frame, municipal_areas(source('area_statistics_TAB6420_sv')), policy)
    # Original pending-CRS receipt is immutable; qualification is recorded in this NEW manifest.
    boundary = dict(by_suffix['geopackage'], source_crs='EPSG:3006', reference_period='2025-01-01',
                    selection={**by_suffix['geopackage']['selection'], 'municipality':'0180',
                               'municipality_field':'kommunkod', 'area_id_field':'regsokod',
                               'selected_area_ids':qa['selected_area_ids'], 'dataset_version':'2025_v2'})
    records = [boundary if r['source_id'] == boundary['source_id'] else r for r in records]
    return records, boundary, native, geographic, qa


def recover(conn, paths, previous_run_id, policy):
    s = paths.scope
    verify_database(conn, synthetic=s.purpose == 'synthetic')
    if s.city != 'stockholm' or s.snapshot != policy['snapshot'] or previous_run_id != policy['parent_run_id'] or s.run_id == previous_run_id:
        raise ValueError('Separate Stockholm recovery identity and exact parent audit required')
    if conn.scalar(text('SELECT EXISTS (SELECT 1 FROM v4_raw.listing_ingestions WHERE '+SCOPE_SQL+')'), s.params()):
        raise RuntimeError('Refuse to reopen an immutable ingestion ledger')
    parent = conn.execute(text('SELECT summary,manifest_sha256 FROM v4_raw.listing_ingestions WHERE '+SCOPE_SQL),
                          {**s.params(), 'run_id':previous_run_id}).mappings().one()
    if parent['manifest_sha256'] != policy['parent_manifest_sha256'] or canonical_hash(parent['summary']) != policy['parent_summary_sha256']:
        raise ValueError('Original parent ledger changed/unqualified')
    original = conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),
                           {**s.params(), 'digest':parent['manifest_sha256']})
    if canonical_hash(original) != policy['parent_manifest_sha256']:
        raise ValueError('Original source manifest changed')
    for record in original['records']:
        if sha256_file(paths.source(record['source_id'], record['filename'])) != record['sha256']:
            raise ValueError('Original frozen source changed')
    failure_path = paths.source('official_boundary', 'boundary.json.receipt.json')
    failure = json.loads(failure_path.read_text())
    if sha256_file(failure_path) != policy['failed_receipt_sha256'] or failure['status'] != 'BLOCKED' or failure['http_status'] != 401:
        raise ValueError('Original failed-access receipt changed')
    if paths.source('official_boundary', 'boundary.json').exists():
        raise ValueError('Unexpected geometry at frozen failed source location')
    code_html = paths.source('official_scope_codes', 'municipal_codes.html').read_text()
    if '0180 Stockholm' not in BeautifulSoup(code_html, 'html.parser').get_text(' ', strip=True):
        raise ValueError('Official national code mapping unverified')
    listing_path = paths.source('inside_airbnb', 'listings.csv.gz')
    if sha256_file(listing_path) != policy['listing_sha256']:
        raise ValueError('Preserved June Stockholm snapshot hash mismatch')
    records, boundary_record, native, geographic, qa = scb_sources(paths, policy)
    _, manifest = freeze_sources(paths, original['records'] + records)
    rows, summary = audit_listings(listing_path, scrape_id=parent['summary']['scrape_id'], currency='SEK', boundary=geographic)
    summary['counts'].update(location_diagnostic(rows, native))
    summary.update(batch_date=s.snapshot, manifest_sha256=canonical_hash(manifest), attempts=[failure],
                   ingestion_code_sha256=sha256_file(PROJECT_ROOT/'src/v4/listings.py'),
                   recovery_code_sha256=sha256_file(Path(__file__)), boundary_qa=qa,
                   boundary_amendment={'definition_version':policy['definition_version'], 'date':policy['amendment_date'],
                       'previous_run_id':previous_run_id, 'previous_manifest_sha256':parent['manifest_sha256'],
                       'previous_summary_sha256':policy['parent_summary_sha256'], 'failed_receipt_sha256':policy['failed_receipt_sha256'],
                       'policy_sha256':sha256_file(POLICY), 'housing_gate':'BLOCKED', 'modelling_gate':'BLOCKED',
                       'location_uncertainty_metres':150, 'distance_crs':'EPSG:3006',
                       'distance_policy':'distance <=150m to dissolved exterior rings; no internal RegSO edges; no exclusions',
                       'analysis_area_assignment':'UNRESOLVED_DISTINCT_GEOGRAPHY', 'housing_area_assignment':'UNRESOLVED_DISTINCT_GEOGRAPHY'})
    if summary['blockers']:
        raise ValueError('Listing quality gate failed; no successful boundary ingestion')
    summary['status'] = RESOLVED
    return manifest, rows, summary, [(boundary_record, geographic)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['audit', 'ingest'])
    for name in ['version', 'city', 'snapshot', 'run-id', 'previous-run-id']:
        parser.add_argument('--'+name, required=True)
    args = parser.parse_args(argv)
    engine = None
    try:
        paths = Paths(Scope(args.version, args.city, args.snapshot, args.run_id))
        policy = load_policy()
        if paths.scope.city != 'stockholm':
            raise ValueError('Stockholm-only source amendment')
        destinations = ([paths.report('listing_audit.json'), paths.intermediate('study_boundary.geojson')]
                        if args.command == 'ingest' else [paths.intermediate('stockholm_boundary_audit.json')])
        if any(path.exists() for path in destinations):
            raise RuntimeError('Refuse to overwrite existing amendment artifacts')
        engine = get_engine()
        with engine.connect() as conn, conn.begin():
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            manifest, rows, summary, boundaries = recover(conn, paths, args.previous_run_id, policy)
        if args.command == 'ingest':
            # Reuse existing append-only migrations/storage. Never reopen the old audit.
            with engine.begin() as conn:
                persist_ingestion(conn, paths.scope, manifest, rows, summary, boundaries)
                union_json = conn.scalar(text('SELECT ST_AsGeoJSON(geom,15) FROM v4_spatial.study_boundaries WHERE '+SCOPE_SQL), paths.scope.params())
            write_once(paths.intermediate('study_boundary.geojson'), encoded_json(
                {'type':'Feature', 'properties':{'kode':'0180', 'source':'SCB-derived RegSO 2025 operational union',
                 'reference_date':'2025-01-01', 'manifest_sha256':summary['manifest_sha256']},
                 'geometry':json.loads(union_json), 'crs':{'type':'name','properties':{'name':'EPSG:4326'}}}))
            write_once(paths.report('listing_audit.json'), encoded_json(summary))
        else:
            write_once(paths.intermediate('stockholm_boundary_audit.json'), encoded_json(summary))
        print(json.dumps({'status':summary['status'], 'counts':summary['counts'], 'models_fitted':0}))
        return 0
    except SQLAlchemyError:
        print(json.dumps({'status':'BLOCKED', 'reason':'V4 immutable audit/database access failed', 'models_fitted':0}))
        return 2
    except (ValueError, RuntimeError, OSError, KeyError, ET.ParseError, zipfile.BadZipFile):
        print(json.dumps({'status':'BLOCKED', 'reason':'Stockholm source/schema/geometry/identity qualification failed; inspect private evidence', 'models_fitted':0}))
        return 2
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == '__main__':
    raise SystemExit(main())
