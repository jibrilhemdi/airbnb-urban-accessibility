"""A03 geography qualification only: immutable evidence, price-free support, no folds."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import tempfile
from zipfile import ZipFile

from pyproj import CRS, Transformer
from shapely.geometry import Point, LineString, shape, mapping
from shapely.ops import transform, unary_union
from shapely.validation import explain_validity
from sqlalchemy import text

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.v4.cities import CITIES, VERSION
from src.v4.identity import Paths, Scope, freeze_sources
from src.v4.listings import acquire
from src.v4.persistence import get_engine, register_manifest, verify_database, SCOPE_SQL
from src.v4.source_reuse import POLICY as LISTING_POLICY, reuse_listing_source, read_listing_audit
from src.v4.specification import DEFINITION_VERSION

DEFINITION = 'v4_geography_A03_20261011'
POLICY = PROJECT_ROOT / 'config/v4/geography_A03_20261011.json'


def polygon(document, source_crs, metric_crs):
    """Refuse invalid/empty/nonpolygon sources; never buffer(0), snap or make_valid."""
    geom = shape(document)
    if geom.geom_type not in {'Polygon', 'MultiPolygon'} or geom.is_empty or not geom.is_valid:
        raise ValueError('Unqualified polygon: ' + explain_validity(geom))
    native, metric = CRS.from_user_input(source_crs), CRS.from_user_input(metric_crs)
    if not metric.is_projected or any(a.unit_conversion_factor != 1 for a in metric.axis_info):
        raise ValueError('City-specific metric CRS in metres required')
    projected = transform(Transformer.from_crs(native, metric, always_xy=True).transform, geom)
    if not projected.is_valid or not math.isfinite(projected.area) or projected.area <= 0:
        raise ValueError('Invalid CRS transformation/area')
    return projected


def declared_crs(document, expected):
    name = document.get('crs', {}).get('properties', {}).get('name')
    if name is None or CRS.from_user_input(name) != CRS.from_user_input(expected):
        raise ValueError('Missing/wrong declared source CRS')


def oslo_municipality(document):
    declared_crs(document, 'EPSG:25833')
    selected = [f for f in document['features'] if f['properties'].get('objtype') == 'Kommune']
    if len(selected) != 1 or selected[0]['properties'].get('kommunenummer') != '0301':
        raise ValueError('Exact Oslo municipality 0301 polygon required')
    return selected[0]


def oslo_areas(document, names):
    declared_crs(document, 'EPSG:25833')
    groups, seen = {}, set()
    for feature in document['features']:
        p = feature['properties']; code = p.get('BYDEL')
        if p.get('kommunenum') != '0301' or code not in names or p.get('FID') in seen:
            raise ValueError('Wrong Oslo municipality/code or duplicate component ID')
        seen.add(p['FID'])
        g = polygon(feature['geometry'], 'EPSG:25833', 'EPSG:25833')
        groups.setdefault(code, []).append(g)
    if set(groups) != set(names):
        raise ValueError('Missing native Oslo statistical area')
    # Source actually contains two named Marka components. No other duplicate area is allowed.
    if any(len(gs) != (2 if code == '17' else 1) for code, gs in groups.items()):
        raise ValueError('Unexpected duplicate Oslo area components')
    back = Transformer.from_crs(25833, 4326, always_xy=True).transform
    return [{'area_id': 'oslo_' + code, 'native_id': code, 'name': names[code],
             'source_crs': 'EPSG:25833', 'components': len(gs),
             'geom': transform(back, unary_union(gs))} for code, gs in sorted(groups.items())]


def stockholm_archive(path):
    """Inspect public archive as a candidate, not a silent current-area substitute."""
    import geopandas as gpd
    with ZipFile(path) as archive, tempfile.TemporaryDirectory() as directory:
        members = [n for n in archive.namelist() if '/Adm_area.' in n]
        if not members:
            raise ValueError('Official archive administrative layer absent')
        for name in members:
            (Path(directory) / Path(name).name).write_bytes(archive.read(name))
        frame = gpd.read_file(Path(directory) / 'Adm_area.shp')
        if CRS.from_user_input(frame.crs) != CRS.from_epsg(3011):
            raise ValueError('Unexpected Stockholm archive CRS')
        required = {'GRUPP', 'KATEGORI', 'RAMKLIPP', 'NAMN', 'ADM_ID'}
        if not required.issubset(frame.columns):
            raise ValueError('Missing actual Stockholm administrative schema')
        selected = frame.loc[frame.GRUPP == 'Stadsdelsnämndsområde']
        ids = selected.ADM_ID.tolist()
        if selected.ADM_ID.isna().any() or len(ids) != len(set(ids)):
            raise ValueError('Duplicate/missing native Stockholm archive IDs')
        return {'status': 'REJECTED_NOT_CURRENT_QUALIFIED_GEOGRAPHY', 'native_count': len(selected),
                'native_ids': sorted(str(int(i)) for i in ids),
                'names': sorted(selected.NAMN.tolist()), 'source_crs': 'EPSG:3011',
                'clipped_count': int((selected.RAMKLIPP == 'yes').sum()),
                'invalid_count': int((~selected.geometry.is_valid).sum()),
                'invalid_reasons': [explain_validity(g) for g in selected.geometry if not g.is_valid],
                'archive_member_date': list(archive.getinfo(next(n for n in members if n.endswith('.shp'))).date_time),
                'current_required_count': 11, 'qualified_analysis_area_count': None,
                'unqualified_archive_area_sum_km2': float(selected.to_crs(3006).geometry.area.sum()/1e6),
                'coverage_qualified': False, 'holdout_support': None,
                'reason': '13 old boroughs, all RAMKLIPP=yes, invalid geometry; not the current 11-area scheme. No repair/merger inferred.'}


def spatial_audit(rows, mask, areas, metric_crs, *, municipalities=None):
    """Covers in source longitude/latitude, strict unique assignment as inherited V3.

    Uses eligibility/positive-price flags only, never amounts, errors or housing.
    Returns a public aggregate and private assignment records for PostgreSQL only.
    """
    to_metric = Transformer.from_crs(4326, metric_crs, always_xy=True).transform
    m = polygon(mapping(mask), 4326, metric_crs)
    ids = [a['area_id'] for a in areas]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate analysis-area ID')
    metrics = {a['area_id']: polygon(mapping(a['geom']), 4326, metric_crs) for a in areas}
    union = unary_union(list(metrics.values())) if areas else None
    support = {a: Counter(raw=0, dwelling=0, positive=0, near_analysis_boundary_positive=0) for a in ids}
    outer = unary_union([LineString(g.exterior.coords) for g in (list(m.geoms) if m.geom_type == 'MultiPolygon' else [m])])
    counts = Counter({k: 0 for k in ('raw', 'dwelling_filtered', 'positive_price', 'invalid_coordinates')})
    statuses, raw_statuses, dwelling_statuses, assignments = Counter(), Counter(), Counter(), []
    listing_ids = [str(r['listing_id']) for r in rows]
    if len(listing_ids) != len(set(listing_ids)) or any(i in {'None', ''} for i in listing_ids):
        raise ValueError('Duplicate/missing listing IDs: preserve source audit; no silent deduplication')
    for row in rows:
        eligible, positive = bool(row['dwelling_eligible']), bool(row['dwelling_eligible'] and row['positive_price'])
        counts['raw'] += 1; counts['dwelling_filtered'] += eligible; counts['positive_price'] += positive
        x, y = row['longitude'], row['latitude']
        finite = (isinstance(x, (int, float)) and isinstance(y, (int, float))
                  and math.isfinite(x) and math.isfinite(y) and -180 <= x <= 180 and -90 <= y <= 90)
        record = {'listing_id': str(row['listing_id']), 'area_id': None, 'candidates': [],
                  'inside_boundary': None, 'near_outer_150m': None, 'near_area_150m': None}
        if not finite:
            counts['invalid_coordinates'] += 1; record['status'] = 'invalid_coordinates'; assignments.append(record); continue
        point = Point(x, y); projected = transform(to_metric, point); inside = mask.covers(point)
        record.update(inside_boundary=inside, near_outer_150m=outer.distance(projected) <= 150)
        for suffix, flag in [('raw', True), ('dwelling', eligible), ('positive', positive)]:
            counts['inside_' + suffix] += inside and flag
            counts['outside_' + suffix] += not inside and flag
            counts['near_outer_150m_' + suffix] += record['near_outer_150m'] and flag
        hits = sorted(a['area_id'] for a in areas if a['geom'].covers(point)) if inside else []
        record['candidates'] = hits
        municipal_matches = [k for k, g in (municipalities or {}).items() if g.covers(point)]
        compatible = (municipalities is None or (len(municipal_matches) == 1 and len(hits) == 1
                      and next(a for a in areas if a['area_id'] == hits[0])['municipality'] == municipal_matches[0]))
        status = ('outside_boundary' if not inside else 'analysis_geometry_unavailable' if not areas
                  else 'unmatched' if not hits else 'ambiguous' if len(hits) != 1 else 'unique' if compatible
                  else 'municipality_mismatch_or_tie')
        record['status'] = status
        raw_statuses[status] += 1
        if eligible: dwelling_statuses[status] += 1
        if inside and positive: statuses[status] += 1
        if status == 'unique':
            record['area_id'] = hits[0]; near = metrics[hits[0]].boundary.distance(projected) <= 150
            record['near_area_150m'] = near
            c = support[hits[0]]; c['raw'] += 1; c['dwelling'] += eligible; c['positive'] += positive
            c['near_analysis_boundary_positive'] += near and positive
        assignments.append(record)
    overlap = []
    for i, a in enumerate(sorted(ids)):
        for b in sorted(ids)[i+1:]:
            value = metrics[a].intersection(metrics[b]).area
            if value > 0: overlap.append({'areas': [a, b], 'overlap_m2': value})
    total = sum(c['positive'] for c in support.values())
    safe_areas = [{k: v for k, v in a.items() if k not in {'geom'}} | {
        'gross_area_km2': metrics[a['area_id']].area / 1e6, 'valid': True,
        'connected_pieces': len(metrics[a['area_id']].geoms) if metrics[a['area_id']].geom_type == 'MultiPolygon' else 1,
        'listing_support': dict(support[a['area_id']]),
        'proposed_holdout_positive': support[a['area_id']]['positive'],
        'proposed_training_positive': total - support[a['area_id']]['positive'],
        'count_safeguard_met': support[a['area_id']]['positive'] >= 30 and total - support[a['area_id']]['positive'] >= 500,
    } for a in sorted(areas, key=lambda a: a['area_id'])]
    summary = {'metric_crs': metric_crs, 'covers_crs': 'EPSG:4326',
               'tie_policy': 'strict_unique_else_unresolved; municipality compatibility required for Copenhagen',
               'counts': dict(counts), 'assignment_status_raw': dict(raw_statuses),
               'assignment_status_dwelling': dict(dwelling_statuses), 'inside_positive_assignment_status': dict(statuses),
               'mask': {'valid': m.is_valid, 'geometry_type': m.geom_type, 'gross_area_km2': m.area/1e6,
                        'bounds_metric': list(m.bounds), 'connected_pieces': len(m.geoms) if m.geom_type == 'MultiPolygon' else 1},
               'native_area_count': len(areas) if areas else None,
               'proposed_supported_holdout_count': sum(a['count_safeguard_met'] for a in safe_areas) if areas else None,
               'proposed_holdout_count': len(areas) if areas else None, 'areas': safe_areas,
               'coverage': {'union_gross_area_km2': union.area/1e6, 'summed_overlap_m2': sum(metrics[a].area for a in ids)-union.area,
                            'mask_uncovered_m2': m.difference(union).area, 'outside_mask_m2': union.difference(m).area,
                            'pairs_with_positive_overlap': overlap} if areas else None,
               'final_sample_frozen': False, 'fold_memberships_frozen': False,
               'housing_required': False, 'research_models_fitted': False}
    return summary, assignments


def load_policy(root=PROJECT_ROOT):
    policy = json.loads((root / POLICY.relative_to(PROJECT_ROOT)).read_text())
    if policy['definition_version'] != DEFINITION or policy['design_id'] != DEFINITION_VERSION or set(policy['cities']) != set(CITIES):
        raise ValueError('Explicit A03 city/design definition required')
    return policy


def verify_evidence(root, item):
    path = root / item['path']
    if not path.resolve().is_relative_to(root.resolve()) or sha256_file(path) != item['sha256']:
        raise ValueError('Geography evidence missing/changed')
    return path


def prepare(conn, paths, *, read_only=False):
    s = paths.scope
    if s.design_id != DEFINITION_VERSION: raise ValueError('A03 requires accessibility-only design')
    policy = load_policy(paths.root)['cities'][s.city]
    if s.run_id != policy['run_id']:
        raise ValueError('Explicit frozen A03 geography run identity required')
    selected = json.loads(LISTING_POLICY.read_text())['cities'][s.city]
    source = reuse_listing_source(conn, s, selected['manifest_sha256'], root=paths.root)
    rows = read_listing_audit(conn, s, selected['manifest_sha256'], root=paths.root)
    original = conn.execute(text('SELECT source_area_id,ST_AsGeoJSON(geom,9) FROM v4_spatial.study_boundaries WHERE '+SCOPE_SQL), source['source_scope']).all()
    if not original: raise ValueError('Approved municipal geometry absent')
    municipalities = {code: shape(json.loads(g)) for code, g in original}
    old = unary_union(list(municipalities.values())); mask = old; areas = []; records = []
    for item in policy['sources']:
        original_path = verify_evidence(paths.root, item)
        if item.get('receipt'):
            receipt_path = verify_evidence(paths.root, item['receipt'])
            receipt = json.loads(receipt_path.read_text())
            if receipt.get('sha256') != item['sha256'] or receipt.get('status') != 'acquired':
                raise ValueError('Geography source receipt mismatch')
            record = {**receipt, **item['qualified_provenance']}
        else:
            if read_only and (not paths.source(item['source_id'],item['filename']).is_file()
                              or not paths.source(item['source_id'],item['filename']+'.receipt.json').is_file()):
                raise ValueError('Read-only audit requires the original frozen V4 source copy/receipt')
            record = acquire(paths, item['source_id'], item['filename'], item['source_url'],
                             extent=item['geographic_extent'], licence=item['licence'], reference_period=item['reference_period'],
                             source_crs=item['source_crs'], reuse=(original_path, item['sha256'], item['acquired_at_utc']))
        records.append(record)
    # Failure receipts are pinned independently; never mislabel them as acquired polygons.
    for failed in policy.get('failed_or_rejected_receipts', []): verify_evidence(paths.root, failed)
    if s.city == 'copenhagen_frederiksberg':
        districts = json.loads(verify_evidence(paths.root, policy['districts']).read_text())
        declared_crs(districts, 4326)
        if {f['properties']['bydel_nr'] for f in districts['features']} != set(range(1,11)) or len(districts['features']) != 10:
            raise ValueError('Exactly ten Copenhagen official districts required')
        areas = [{'area_id': 'cph_'+str(f['properties']['bydel_nr']).zfill(2), 'native_id': str(f['properties']['bydel_nr']),
                  'name': f['properties']['navn'], 'municipality': '0101', 'source_crs': 'EPSG:4326', 'components': 1,
                  'geom': shape(f['geometry'])} for f in districts['features']]
        areas.append({'area_id': 'frederiksberg_0147', 'native_id': '0147', 'name': 'Frederiksberg', 'municipality': '0147',
                      'source_crs': 'EPSG:4326', 'components': 1, 'geom': municipalities['0147']})
    elif s.city == 'oslo':
        with ZipFile(verify_evidence(paths.root, policy['municipality_archive'])) as archive:
            member = policy['municipality_member']; feature = oslo_municipality(json.loads(archive.read(member)))
        if any(feature['properties'].get(k) != v for k,v in policy['municipality_attributes'].items()):
            raise ValueError('Dated Oslo municipal attributes changed')
        mask = transform(Transformer.from_crs(25833,4326,always_xy=True).transform,
                         polygon(feature['geometry'],25833,25833))
        import pandas as pd
        codes = pd.read_excel(verify_evidence(paths.root, policy['codes']))[['Bydel_nr','Bydel_navn']].drop_duplicates()
        names = {str(int(r.Bydel_nr)).zfill(2): r.Bydel_navn for r in codes.itertuples() if int(r.Bydel_nr) != 99}
        if names != policy['native_codes']: raise ValueError('Official Oslo code mapping changed')
        areas = oslo_areas(json.loads(verify_evidence(paths.root, policy['boroughs']).read_text()), names)
    summary, assignments = spatial_audit(rows, mask, areas, policy['metric_crs'],
                                         municipalities=municipalities if s.city=='copenhagen_frederiksberg' else None)
    summary.update(definition_version=DEFINITION, design_id=s.design_id, city=s.city, snapshot=s.snapshot,
                   source_listing_run_id=selected['run_id'], listing_manifest_sha256=selected['manifest_sha256'],
                   policy_sha256=canonical_hash(policy), status=policy['status'], mask_status=policy['mask_status'],
                   analysis_status=policy['analysis_status'], blockers=policy['blockers'],
                   certification_limits=policy['certification_limits'], source_reingested=False,
                   adjacent_grouping='NONE_FROZEN; sparse/unqualified cases remain blocked')
    if s.city == 'oslo':
        native_old = transform(Transformer.from_crs(4326,25833,always_xy=True).transform,old)
        native_new = transform(Transformer.from_crs(4326,25833,always_xy=True).transform,mask)
        summary['old_vs_amended_mask'] = {'symmetric_difference_m2': native_old.symmetric_difference(native_new).area,
                                         'hausdorff_m': native_old.hausdorff_distance(native_new),
                                         'changed_listing_inclusion': sum(a['inside_boundary'] != r['inside_boundary'] for a,r in zip(assignments,rows) if a['inside_boundary'] is not None)}
    if s.city == 'stockholm':
        summary['rejected_archive'] = stockholm_archive(verify_evidence(paths.root, policy['archive']))
        summary['expected_current_borough_names'] = policy['current_borough_names']
    # A frozen policy cannot approve observations that contradict its qualification.
    if summary['analysis_status'] == 'QUALIFIED_INHERITED_OPERATIONAL':
        if not areas or any(not a['count_safeguard_met'] for a in summary['areas']) or any(k!='unique' and v for k,v in summary['inside_positive_assignment_status'].items()):
            raise ValueError('Qualified operational analysis policy contradicted by listing support')
    candidate = {'version':s.version,'city':s.city,'snapshot':s.snapshot,'purpose':s.purpose,
                 'records':sorted(records,key=lambda r:r['source_id'])}
    if read_only and not paths.manifest(canonical_hash(candidate)).is_file():
        raise ValueError('Read-only audit requires the original frozen manifest file')
    _, manifest = freeze_sources(paths, records)
    summary['geography_manifest_sha256'] = canonical_hash(manifest)
    return summary, assignments, areas, mask, manifest


def persist(conn, scope, summary, assignments, areas, mask, manifest):
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    if scope.design_id != DEFINITION_VERSION or summary['design_id'] != scope.design_id or summary['city'] != scope.city:
        raise ValueError('Geography qualification identity mismatch')
    digest = register_manifest(conn, scope, manifest)
    if digest != summary['geography_manifest_sha256']: raise ValueError('Geography manifest mismatch')
    listing_run = summary['source_listing_run_id']
    approved = conn.execute(text('SELECT purpose,manifest_sha256 FROM v4_raw.listing_ingestions WHERE '+SCOPE_SQL),
                            {**scope.params(),'run_id':listing_run}).one_or_none()
    if approved is None or approved.purpose != scope.purpose or approved.manifest_sha256 != summary['listing_manifest_sha256']:
        raise ValueError('Approved listing parent purpose/hash mismatch')
    q = {**scope.params(), 'definition': DEFINITION, 'digest': digest, 'listing_run': listing_run,
         'listing_digest': summary['listing_manifest_sha256'], 'summary_hash': canonical_hash(summary),
         'summary': json.dumps(summary,allow_nan=False)}
    conn.execute(text('INSERT INTO v4_spatial.geography_qualifications '
                      '(version,run_id,city,snapshot,design_id,purpose,definition_version,manifest_sha256,listing_run_id,listing_manifest_sha256,summary_sha256,summary) '
                      'VALUES (:version,:run_id,:city,:snapshot,:design_id,:purpose,:definition,:digest,:listing_run,:listing_digest,:summary_hash,CAST(:summary AS jsonb))'), q)
    to4326 = json.dumps(mapping(mask),allow_nan=False)
    conn.execute(text('INSERT INTO v4_spatial.geography_masks VALUES (:version,:run_id,:city,:snapshot,:design_id,ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geom),4326)))'),{**scope.params(),'geom':to4326})
    for area in areas:
        conn.execute(text('INSERT INTO v4_spatial.analysis_geography VALUES (:version,:run_id,:city,:snapshot,:design_id,:area,:native,:name,ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geom),4326)))'),
                     {**scope.params(),'area':area['area_id'],'native':area['native_id'],'name':area['name'],'geom':json.dumps(mapping(area['geom']),allow_nan=False)})
    if assignments:
        conn.execute(text('INSERT INTO v4_spatial.geography_listing_audit VALUES (:version,:run_id,:city,:snapshot,:design_id,:listing,:area,CAST(:record AS jsonb))'),
                     [{**scope.params(),'listing':r['listing_id'],'area':r['area_id'],'record':json.dumps(r,allow_nan=False)} for r in assignments])


def evidence(conn, scope):
    row = conn.execute(text('SELECT summary,summary_sha256 FROM v4_spatial.geography_qualifications WHERE '+SCOPE_SQL+' AND design_id=:design_id'),scope.params()).one_or_none()
    if row is None or canonical_hash(row.summary) != row.summary_sha256: raise ValueError('Frozen A03 qualification missing/changed')
    return row.summary




def verify_sql_counts(conn, scope, summary):
    params={**scope.params(),'listing_run':summary['source_listing_run_id'],
            'srid':int(summary['metric_crs'].split(':')[1])}
    query = text("""WITH oldmask AS (
      SELECT ST_UnaryUnion(ST_Collect(geom)) g FROM v4_spatial.study_boundaries
      WHERE version=:version AND run_id=:listing_run AND city=:city AND snapshot=:snapshot
    ), newmask AS (
      SELECT geom g FROM v4_spatial.geography_masks WHERE version=:version AND run_id=:run_id
      AND city=:city AND snapshot=:snapshot AND design_id=:design_id
    ), outerlines AS (
      SELECT ST_Collect(ST_ExteriorRing((d).geom)) g FROM newmask,
      LATERAL ST_Dump(ST_Transform(newmask.g,:srid)) d
    ), points AS (
      SELECT (record->>'dwelling_eligible')::boolean dwelling,(record->>'positive_price')::boolean positive,
      ST_SetSRID(ST_MakePoint((record->>'longitude')::double precision,
                             (record->>'latitude')::double precision),4326) g
      FROM v4_raw.listing_audit WHERE version=:version AND run_id=:listing_run AND city=:city AND snapshot=:snapshot
    ) SELECT count(*) raw,count(*) FILTER(WHERE ST_Covers(newmask.g,points.g)) inside_raw,
      count(*) FILTER(WHERE dwelling AND positive AND ST_Covers(newmask.g,points.g)) inside_positive,
      count(*) FILTER(WHERE ST_Covers(newmask.g,points.g) IS DISTINCT FROM ST_Covers(oldmask.g,points.g)) changed_inclusion_vs_exact_old_sql,
      count(*) FILTER(WHERE dwelling AND positive AND ST_DWithin(outerlines.g,ST_Transform(points.g,:srid),150)) near_outer_150m_positive
      FROM points,oldmask,newmask,outerlines""")
    result=dict(conn.execute(query,params).mappings().one())
    if any(result[k] != summary['counts'][k] for k in ('raw','inside_raw','inside_positive','near_outer_150m_positive')):
        raise ValueError('Independent PostGIS counts differ from frozen A03 audit')
    # A nonzero old/new change would require a documented listing-mask amendment.
    if result['changed_inclusion_vs_exact_old_sql'] != 0:
        raise ValueError('Unexpected change against exact preserved municipal SQL masks')
    return result


SELECTION = PROJECT_ROOT / 'config/v4/geography_reuse_accessibility_only.json'
OSLO_VINTAGE_WARNING = 'Oslo boundary is current-at-retrieval; geometry vintage not supplied by API; temporal qualification unresolved'


def selected_evidence(conn, scope, listing_manifest):
    """Narrow read-only A03 overlay; never marks context/samples/folds READY."""
    if scope.design_id != DEFINITION_VERSION:
        raise ValueError('A03 evidence requires the revised design')
    policy = load_policy()['cities'][scope.city]
    selection = json.loads(SELECTION.read_text())
    if selection['design_id'] != scope.design_id or selection['source_version'] != scope.version:
        raise ValueError('Geography selection design/version mismatch')
    chosen = selection['cities'][scope.city]
    if chosen['snapshot'] != scope.snapshot or chosen['run_id'] != policy['run_id']:
        raise ValueError('Geography snapshot/run mismatch')
    geo = Scope(scope.version, scope.city, scope.snapshot, chosen['run_id'], design_id=scope.design_id)
    summary = evidence(conn, geo)
    if (canonical_hash(summary) != chosen['summary_sha256'] or summary['policy_sha256'] != canonical_hash(policy)
            or summary['listing_manifest_sha256'] != listing_manifest
            or summary['geography_manifest_sha256'] != chosen['geography_manifest_sha256']):
        raise ValueError('Frozen geography policy/summary/listing linkage mismatch')
    for item in policy['sources']:
        verify_evidence(PROJECT_ROOT, item)
        if item.get('receipt'):verify_evidence(PROJECT_ROOT, item['receipt'])
    for item in policy.get('failed_or_rejected_receipts', []):verify_evidence(PROJECT_ROOT, item)
    manifest = conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),
                           {**scope.params(),'digest':chosen['geography_manifest_sha256']})
    if manifest is None or canonical_hash(manifest) != chosen['geography_manifest_sha256']:
        raise ValueError('Frozen geography manifest mismatch')
    for item in manifest['records']:
        if sha256_file(Paths(scope).source(item['source_id'],item['filename'])) != item['sha256']:
            raise ValueError('Frozen geography raw source changed')
    return summary


def apply_geography_amendment(blockers, summary):
    """Only verified mask/metric evidence waives the exact superseded vintage warning."""
    resolved = summary['mask_status'] in {'QUALIFIED_INHERITED_OPERATIONAL', 'RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT'}
    result = [b for b in blockers if not (resolved and (b.startswith('study_boundary:') or b.startswith('metric_crs:')
              or (summary['city']=='oslo' and b == OSLO_VINTAGE_WARNING)))]
    result.extend('A03 geography: '+b for b in summary['blockers'])
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('freeze','audit'))
    parser.add_argument('--version',required=True,choices=(VERSION,));parser.add_argument('--city',required=True,choices=CITIES)
    parser.add_argument('--snapshot',required=True);parser.add_argument('--run-id',required=True)
    parser.add_argument('--design-id',required=True,choices=(DEFINITION_VERSION,))
    args=parser.parse_args(argv);engine=None;sql_check=None
    try:
        s=Scope(args.version,args.city,args.snapshot,args.run_id,design_id=args.design_id);paths=Paths(s);engine=get_engine()
        if args.command=='freeze':
            with engine.begin() as conn:
                verify_database(conn)
                if conn.scalar(text('SELECT count(*) FROM v4_spatial.geography_qualifications WHERE '+SCOPE_SQL+' AND design_id=:design_id'),s.params()):
                    raise ValueError('Committed geography identity exists; use read-only audit, never reopen')
                summary,assignments,areas,mask,manifest=prepare(conn,paths)
                persist(conn,s,summary,assignments,areas,mask,manifest)
        else:
            with engine.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                frozen=evidence(conn,s);summary,_,_,_,_=prepare(conn,paths,read_only=True)
                if summary != frozen: raise ValueError('Recomputed geographic evidence differs from immutable SQL ledger')
                sql_check=verify_sql_counts(conn,s,summary)
        print(json.dumps({**s.params(),'status':summary['status'],'mask_status':summary['mask_status'],
                          'analysis_status':summary['analysis_status'],'counts':summary['counts'],
                          'geography_manifest_sha256':summary['geography_manifest_sha256'],
                          'summary_sha256':canonical_hash(summary),'blockers':summary['blockers'],
                          'geography_audit':summary,'independent_postgis_check':sql_check,
                          'research_executed':False,'source_reingested':False,'folds_frozen':False},indent=2))
        return 2 if summary['status']=='BLOCKED' else 0
    except Exception as error:
        print(json.dumps({'status':'BLOCKED','reason':str(error) if isinstance(error,(RuntimeError,ValueError)) else type(error).__name__, 'research_executed':False}))
        return 2
    finally:
        if engine is not None:engine.dispose()


if __name__=='__main__':raise SystemExit(main())
