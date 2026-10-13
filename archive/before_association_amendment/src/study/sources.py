"""Immutable source acquisition and explicit read-only historical source reuse."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from shapely.geometry import shape
from sqlalchemy import text

from src.ingestion.common import PROJECT_ROOT, USER_AGENT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.v4.identity import Scope
from src.v4.listings import audit_listings
from src.v4.persistence import get_engine
from src.v4.source_reuse import reuse_listing_source
from src.v4.specification import DEFINITION_VERSION
from src.study.specification import load_design, neutral_token


def write_once(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(content)


def acquire(url, *, city, role, extent, crs, licence, snapshot, body=None, timeout=45):
    neutral_token(city)
    neutral_token(role)
    if 'listings.csv' in url:
        raise ValueError('Airbnb listings are verified reuse only')
    now = datetime.now(timezone.utc)
    directory = PROJECT_ROOT / 'data/raw' / role / city / now.strftime('%Y%m%dT%H%M%S%fZ')
    request = Request(url, data=body, headers={'User-Agent': USER_AGENT,
                                             'Content-Type': 'application/x-www-form-urlencoded'})
    status, failure, headers = None, None, {}
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
            status = response.status
            headers = {k: response.headers.get(k) for k in ('Last-Modified', 'ETag', 'Content-Type')}
    except HTTPError as error:
        status, failure, payload = error.code, str(error), error.read()
    except (URLError, TimeoutError, OSError) as error:
        failure, payload = str(error), b''
    receipt = {'source_url': url, 'city': city, 'role': role,
               'acquired_at_utc': now.isoformat(), 'geographic_extent': extent,
               'source_crs': crs, 'licence': licence, 'snapshot': snapshot,
               'status': 'transport_success_pending_validation' if failure is None else 'failed',
               'http_status': status, 'failure': failure, 'headers': headers,
               'sha256': hashlib.sha256(payload).hexdigest(), 'size_bytes': len(payload),
               'request_body_sha256': hashlib.sha256(body).hexdigest() if body else None,
               'path': (directory / 'response.json').relative_to(PROJECT_ROOT).as_posix()}
    write_once(directory / 'response.json', payload)
    if body is not None:
        write_once(directory / 'request.txt', body)
    write_once(directory / 'receipt.json', (json.dumps(receipt, indent=2, ensure_ascii=False)+'\n').encode())
    receipt['receipt_path'] = (directory / 'receipt.json').relative_to(PROJECT_ROOT).as_posix()
    receipt['receipt_sha256'] = sha256_file(directory / 'receipt.json')
    return receipt


def verify_source(record):
    path = PROJECT_ROOT / record['path']
    if not path.resolve().is_relative_to(PROJECT_ROOT) or sha256_file(path) != record['sha256']:
        raise ValueError('Source path/hash mismatch')
    if record.get('receipt_path') and sha256_file(PROJECT_ROOT / record['receipt_path']) != record['receipt_sha256']:
        raise ValueError('Source receipt changed')
    return path


def historical_inputs(conn, city):
    """Fresh source audit, never previous derived sample/features/results."""
    design, cities = load_design()
    config = cities[city]
    selected = config['historical_listing_selection']
    scope = Scope(selected['source_version'], selected['city'], selected['snapshot'],
                  selected['run_id'], design_id=DEFINITION_VERSION)
    approved = reuse_listing_source(conn, scope, selected['manifest_sha256'])
    records = [r for r in approved['manifest']['records'] if r['filename'] == 'listings.csv.gz']
    if len(records) != 1:
        raise ValueError('Exactly one approved detailed listing source required')
    record = records[0]
    path = PROJECT_ROOT / 'data/raw/v4' / scope.version / scope.city / scope.snapshot / record['source_id'] / record['filename']
    geography = config['historical_geography_selection']
    params = {'version': scope.version, 'city': scope.city, 'snapshot': scope.snapshot,
              'run_id': geography['run_id']}
    row = conn.execute(text('SELECT summary,summary_sha256 FROM v4_spatial.geography_qualifications '
                            'WHERE version=:version AND city=:city AND snapshot=:snapshot AND run_id=:run_id'), params).one()
    if row.summary_sha256 != geography['summary_sha256'] or canonical_hash(row.summary) != geography['summary_sha256']:
        raise ValueError('Accepted geography source pin changed')
    mask = shape(json.loads(conn.scalar(text('SELECT ST_AsGeoJSON(geom,15) FROM v4_spatial.geography_masks '
                                           'WHERE version=:version AND city=:city AND snapshot=:snapshot AND run_id=:run_id'), params)))
    if not mask.is_valid or mask.is_empty:
        raise ValueError('Accepted municipal mask is invalid')
    old_summary = approved['summary']
    rows, summary = audit_listings(path, scrape_id=old_summary['scrape_id'], currency=config['currency'], boundary=mask)
    if summary['blockers']:
        raise ValueError('Source audit failed: ' + '; '.join(summary['blockers']))
    return rows, mask, {'city': city, 'snapshot': design['snapshot'], 'currency': config['currency'],
                        'listing_manifest_sha256': selected['manifest_sha256'],
                        'listing_sha256': record['sha256'], 'source_reingested': False,
                        'counts': summary['counts'], 'mask_summary_sha256': geography['summary_sha256'],
                        'covers_crs': 'EPSG:4326', 'metric_crs': config['metric_crs']}


def acquire_neighbourhoods():
    _, cities = load_design()
    output = {}
    for city, config in cities.items():
        if city == 'stockholm':
            prior = json.loads((PROJECT_ROOT / 'docs/v4/rinkeby_polygon_check_20261012.json').read_text())
            src = prior['sources']['airbnb']
            receipt = prior['airbnb_receipt_record']
            record = {'path': src['path'], 'sha256': src['sha256'],
                      'receipt_path': src['receipt']['path'], 'receipt_sha256': src['receipt']['sha256'],
                      'source_url': receipt['source_url'], 'acquired_at_utc': receipt['acquired_at_utc'],
                      'source_crs': 'OGC:CRS84', 'licence': 'CC BY 4.0, Inside Airbnb catalogue; original cartographic provenance unknown',
                      'snapshot': '2026-06-30', 'geographic_extent': 'Stockholm provider neighbourhoods',
                      'status': 'verified_preserved_source'}
            verify_source(record)
        else:
            record = acquire(config['neighbourhood_url'], city=city, role='neighbourhoods',
                             extent=city+' provider neighbourhoods', crs='OGC:CRS84',
                             licence='CC BY 4.0, Inside Airbnb catalogue; original cartographic provenance unknown',
                             snapshot='2026-06-30')
        output[city] = record
    return output
