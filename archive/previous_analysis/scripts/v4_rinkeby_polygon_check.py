"""Read-only historical polygon comparison; no assignments or qualifications.

Uses ignored, checksum-pinned sources. Does not access SQL, listings, outcomes,
network services or model runners. Emits public geometry diagnostics only.
"""
from pathlib import Path
import argparse
import json
import math
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import geopandas as gpd
from pyproj import CRS, Transformer
from shapely.geometry import shape
from shapely.ops import transform
from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash

AUDIT = ROOT / 'docs/v4/rinkeby_polygon_check_20261012.json'


def metrics(target, candidate, metric_crs='EPSG:3006'):
    crs = CRS.from_user_input(metric_crs)
    if not crs.is_projected or any(a.unit_conversion_factor != 1 for a in crs.axis_info):
        raise ValueError('Recorded projected metre CRS required')
    for geometry in (target, candidate):
        if (geometry.geom_type not in {'Polygon', 'MultiPolygon'} or geometry.is_empty
                or not geometry.is_valid or not math.isfinite(geometry.area) or geometry.area <= 0):
            raise ValueError('Invalid/empty polygon; no repair permitted')
    intersection = target.intersection(candidate).area
    return {'target_area_km2': target.area / 1e6,
            'official_area_km2': candidate.area / 1e6,
            'intersection_km2': intersection / 1e6,
            'target_overlap_pct': 100 * intersection / target.area,
            'official_overlap_pct': 100 * intersection / candidate.area,
            'intersection_over_union_pct': 100 * intersection / target.union(candidate).area,
            'symmetric_difference_km2': target.symmetric_difference(candidate).area / 1e6,
            'hausdorff_m': target.hausdorff_distance(candidate)}


def target_geometry(document):
    if document.get('type') != 'FeatureCollection' or document.get('crs') is not None:
        raise ValueError('Expected inspected unlabelled RFC7946 GeoJSON collection')
    selected = [f for f in document['features']
                if f['properties'].get('neighbourhood') == 'Rinkeby-Tensta']
    if len(selected) != 1:
        raise ValueError('Exactly one target label required')
    geom = shape(selected[0]['geometry'])
    west, south, east, north = geom.bounds
    if not (17 < west < east < 19 and 58 < south < north < 61):
        raise ValueError('Coordinates inconsistent with geographic Stockholm extent')
    # Explicit GeoJSON default, not a claim that original cartographic provenance
    # or date is known. The measured comparison uses Stockholm's metric CRS.
    return transform(Transformer.from_crs('OGC:CRS84', 'EPSG:3006', always_xy=True).transform, geom)


def inspect(audit):
    sources = audit['sources']
    for source in sources.values():
        if sha256_file(ROOT / source['path']) != source['sha256']:
            raise ValueError('Pinned source changed or missing')
        receipt = source.get('receipt')
        if receipt and sha256_file(ROOT / receipt['path']) != receipt['sha256']:
            raise ValueError('Frozen acquisition receipt changed')
    manifest = json.loads((ROOT / audit['manifest']['path']).read_text())
    if canonical_hash(manifest) != audit['manifest']['sha256']:
        raise ValueError('Discovery manifest changed')
    if manifest['records'] != [audit['airbnb_receipt_record']]:
        raise ValueError('Discovery manifest/receipt linkage mismatch')
    receipt = sources['airbnb']['receipt']
    if json.loads((ROOT / receipt['path']).read_text()) != audit['airbnb_receipt_record']:
        raise ValueError('Source receipt mismatch')
    catalogue = json.loads((ROOT / sources['catalogue']['path']).read_text())
    matches = [d for d in catalogue['data']['allData']['datasets']
               if d['city'] == 'Stockholm' and d['publishDate'] == '2026-06-30']
    if len(matches) != 1 or (matches[0]['dataRoot'] + '2026-06-30/visualisations/neighbourhoods.geojson'
                           != audit['airbnb_receipt_record']['source_url']):
        raise ValueError('Wrong batch or unverified catalogue selection')
    document = json.loads((ROOT / sources['airbnb']['path']).read_text())
    target = target_geometry(document)
    with ZipFile(ROOT / sources['official_archive']['path']) as archive, tempfile.TemporaryDirectory() as directory:
        members = [n for n in archive.namelist() if '/Adm_area.' in n]
        if not members:
            raise ValueError('Inspected administrative archive layer missing')
        for name in members:
            (Path(directory) / Path(name).name).write_bytes(archive.read(name))
        frame = gpd.read_file(Path(directory) / 'Adm_area.shp')
        if CRS.from_user_input(frame.crs) != CRS.from_epsg(3011):
            raise ValueError('Official archive source CRS changed')
        native = frame.loc[frame.GRUPP == 'Stadsdelsnämndsområde'].to_crs(3006)
        if native.ADM_ID.isna().any() or native.ADM_ID.duplicated().any():
            raise ValueError('Missing/duplicate official area IDs')
        comparisons, skipped = [], []
        for _, row in native.iterrows():
            if not row.geometry.is_valid:
                skipped.append(row.NAMN)
                continue
            comparisons.append({'name': row.NAMN, 'native_id': str(int(row.ADM_ID)),
                                'clipped': row.RAMKLIPP, **metrics(target, row.geometry)})
        names = {r['name'] for r in comparisons}
        if not {'Rinkeby-Kista', 'Spånga-Tensta'} <= names:
            raise ValueError('Required valid official comparison polygons unavailable')
    comparisons.sort(key=lambda r: (-r['target_overlap_pct'], r['name']))
    return {'status': 'HISTORICAL_CORRESPONDENCE_ONLY_CURRENT_CROSSWALK_UNQUALIFIED',
            'metric_crs': 'EPSG:3006', 'airbnb_feature_count': len(document['features']),
            'official_native_count': len(native), 'invalid_official_candidates_skipped': sorted(skipped),
            'best_historical_candidate': comparisons[0]['name'], 'comparisons': comparisons,
            'sql_mutations': 0, 'listing_assignments_changed': False,
            'analysis_geography_qualified': False, 'research_executed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true', help='Compare against the frozen safe diagnostic export')
    args = parser.parse_args()
    audit = json.loads(AUDIT.read_text())
    result = inspect(audit)
    if args.verify and result != audit['result']:
        raise ValueError('Recomputed diagnostics differ from recorded inspection')
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
