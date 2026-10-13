"""Matched-source acquisition and audit only; never constructs/fits a model sample."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from urllib.parse import quote as url_quote, urlsplit, urlunsplit, urlencode

from pyproj import CRS, Transformer
from shapely.geometry import Point, shape, mapping
from shapely.ops import transform, unary_union
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.ingestion.common import PROJECT_ROOT, USER_AGENT, sha256_file, utc_now
from src.ingestion.price import source_price
from src.pipeline.build_airbnb_sample import CONVENTIONAL_PROPERTY_TYPES
from src.pipeline.protocol import canonical_hash
from src.provenance.cities import VERSION, CITIES
from src.provenance.identity import Scope, Paths, write_once, freeze_sources
from src.provenance.persistence import get_engine, migrate, register_manifest, verify_database

DEFINITION = 'v4_listing_ingestion_20261011'
REQUIRED = frozenset(('id', 'scrape_id', 'last_scraped', 'source', 'room_type', 'property_type',
                      'accommodates', 'bedrooms', 'bathrooms', 'bathrooms_text', 'minimum_nights',
                      'host_is_superhost', 'host_total_listings_count', 'amenities',
                      'price', 'latitude', 'longitude', 'neighbourhood_cleansed',
                      'price_quote_checkin_date', 'price_quote_checkout_date',
                      'price_quote_total_price', 'price_quote_price_per_night', 'price_quote_raw'))


def load_sources():
    return json.loads((PROJECT_ROOT / 'archive/previous_analysis/config/listing_sources.json').read_text())


def encoded_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + '\n').encode()


def acquire(paths, source_id, filename, url, *, extent, licence, reference_period,
            source_crs='not_spatial', selection=None, reuse=None, request_json=None,
            request_form=None):
    """Exclusive raw creation + immutable receipt; cached retrieval dates never rewritten.

    A crash leaving bytes without a receipt fails closed. No force/replacement option.
    HTTP failures freeze only the status/URL, never a credential or response body.
    """
    if request_json is not None and request_form is not None:
        raise ValueError('Choose one public request encoding')
    body = None
    headers = {'User-Agent': USER_AGENT}
    if request_json is not None:
        body = json.dumps(request_json, sort_keys=True, allow_nan=False).encode()
        headers['Content-Type'] = 'application/json'
    elif request_form is not None:
        body = urlencode(request_form, doseq=True).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    method = 'POST' if body is not None else 'GET'
    body_hash = hashlib.sha256(body).hexdigest() if body is not None else None
    if reuse and body is not None:
        raise ValueError('Source reuse cannot issue a query')
    destination = paths.source(source_id, filename)
    receipt = paths.source(source_id, filename + '.receipt.json')
    if receipt.exists():
        record = json.loads(receipt.read_text())
        if record['source_url'] != url or record['selection'] != selection or record['reference_period'] != reference_period:
            raise ValueError('Immutable source selection mismatch')
        if record.get('request_method', 'GET') != method or record.get('request_sha256') != body_hash:
            raise ValueError('Immutable source query mismatch')
        if record['status'] == 'acquired' and sha256_file(destination) != record['sha256']:
            raise ValueError('Immutable source bytes changed')
        return record
    if destination.exists():
        raise RuntimeError('Raw source exists without receipt; investigate, never overwrite')
    now = utc_now()
    record = dict(source_id=source_id, filename=filename, source_url=url, acquired_at_utc=now,
                  geographic_extent=extent, source_crs=source_crs, licence=licence,
                  reference_period=reference_period, selection=selection,
                  local_location=destination.relative_to(paths.root).as_posix())
    if body is not None:
        record.update(request_method=method, request_sha256=body_hash,
                      request_json=request_json, request_form=request_form)
    if reuse:
        path, digest, original_retrieval = reuse
        if sha256_file(path) != digest:
            raise ValueError('Protected V3 source hash mismatch')
        write_once(destination, path.read_bytes())
        record.update(reused_from=path.relative_to(PROJECT_ROOT).as_posix(),
                      acquired_at_utc=original_retrieval, verified_at_utc=now,
                      http_status=None, status='acquired')
    else:
        try:
            parts = urlsplit(url)
            transport_url = urlunsplit((parts.scheme, parts.netloc, url_quote(parts.path, safe='/%:@'), parts.query, parts.fragment))
            with urlopen(Request(transport_url, data=body, headers=headers, method=method), timeout=180) as response:
                # Detailed files are small enough for a single exclusive write; no partial raw files.
                content = response.read()
                record.update(http_status=response.status, final_url=response.url,
                              content_type=response.headers.get('Content-Type'),
                              last_modified=response.headers.get('Last-Modified'), status='acquired')
            write_once(destination, content)
        except HTTPError as error:
            record.update(status='BLOCKED', http_status=error.code, local_location=None)
        except (OSError, TimeoutError):
            record.update(status='BLOCKED', http_status=None, local_location=None,
                          error='Network acquisition failed; no observations substituted')
    if record['status'] == 'acquired':
        record.update(sha256=sha256_file(destination), size_bytes=destination.stat().st_size)
    write_once(receipt, encoded_json(record))
    return record


def catalogue_selection(catalogue, city, snapshot):
    entries = [d for d in catalogue['data']['allData']['datasets']
               if d['city'] == city and d['publishDate'] == snapshot]
    if len(entries) != 1:
        raise ValueError('BLOCKED: exact matched batch absent or ambiguous; no latest fallback')
    entry = entries[0]
    if not entry['dataRoot'].startswith('https://data.insideairbnb.com/'):
        raise ValueError('Unofficial data root')
    return entry, entry['dataRoot'] + snapshot + '/data/listings.csv.gz'


def parse_price(value, convention='inside_airbnb_us_export'):
    # Currency is independently verified: the literal export $ is not a USD claim.
    if convention != 'inside_airbnb_us_export':
        raise ValueError('Unqualified numeric locale; no automatic separator guessing')
    price, log_price = source_price(value)
    if price is not None and not math.isfinite(price):
        raise ValueError('Nonfinite price')
    return price, log_price


def boundary_geometry(document, *, municipality, crs):
    """Only explicit official municipal objects. County/neighbourhood shapes fail."""
    source_crs = CRS.from_user_input(crs)
    if document.get('type') == 'Feature':
        if document.get('properties', {}).get('kode') != municipality:
            raise ValueError('Wrong official municipality')
        geometry = document['geometry']
    elif document.get('kommunenummer') == municipality:
        geometry = document['omrade']
    else:
        raise ValueError('Municipal identity unresolved; county/provider areas are not boundaries')
    declared = document.get('crs', geometry.get('crs', {})).get('properties', {}).get('name')
    if declared and CRS.from_user_input(declared) != source_crs:
        raise ValueError('Boundary declared CRS mismatch')
    geom = shape(geometry)
    if geom.geom_type not in {'Polygon', 'MultiPolygon'} or geom.is_empty or not geom.is_valid:
        raise ValueError('Invalid study boundary; no automatic geometry repair')
    if source_crs != CRS.from_epsg(4326):
        geom = transform(Transformer.from_crs(source_crs, 'EPSG:4326', always_xy=True).transform, geom)
    xmin, ymin, xmax, ymax = geom.bounds
    if not (-180 <= xmin <= xmax <= 180 and -90 <= ymin <= ymax <= 90):
        raise ValueError('Invalid transformed boundary coordinates')
    return geom


def audit_listings(path, *, scrape_id, currency, boundary=None, price_format='inside_airbnb_us_export'):
    """Keep every original row, including invalid/duplicate IDs and missing outcomes.

    Audit keys are row numbers; unique listing ID qualification is a separate gate.
    Membership uses covers in EPSG:4326 (no distance/area operation, boundary included).
    """
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not REQUIRED <= set(fields):
            raise ValueError('BLOCKED: missing/duplicate detailed-listing schema fields')
        raw = list(reader)
    if not raw or any(None in row or any(v is None for v in row.values()) for row in raw):
        raise ValueError('BLOCKED: empty/truncated/malformed CSV')
    ids = Counter(row['id'] for row in raw)
    counters = Counter(); scraped = Counter(); quote_currency = Counter(); quote_nights = Counter()
    quote_dates = []; audits = []; blockers = []
    for number, row in enumerate(raw, 1):
        reasons = []
        valid_id = bool(re.fullmatch(r'[1-9][0-9]*', row['id']))
        duplicate = ids[row['id']] > 1
        if not valid_id: reasons.append('invalid_id')
        if duplicate: reasons.append('duplicate_id')
        if row['scrape_id'] != scrape_id: reasons.append('unexpected_scrape_id')
        try:
            date.fromisoformat(row['last_scraped'])
            scraped.update([row['last_scraped']])
        except ValueError:
            reasons.append('invalid_scrape_date')
        dwelling = row['room_type'] == 'Entire home/apt' and row['property_type'] in CONVENTIONAL_PROPERTY_TYPES
        try:
            price, log_price = parse_price(row['price'], price_format)
        except ValueError:
            price = log_price = None; reasons.append('invalid_price')
        positive = price is not None and price > 0
        try:
            lon, lat = float(row['longitude']), float(row['latitude'])
            if not math.isfinite(lon + lat) or not (-180 <= lon <= 180 and -90 <= lat <= 90): raise ValueError()
        except ValueError:
            lon = lat = None; reasons.append('invalid_coordinates')
        inside = None if boundary is None or lon is None else bool(boundary.covers(Point(lon, lat)))
        quote = None
        if row['price_quote_raw']:
            try:
                quote = json.loads(row['price_quote_raw'])['quote']
                if not isinstance(quote, dict): raise ValueError()
                quote_currency.update([str(quote.get('currency'))])
                if quote.get('currency') not in {None, currency}: reasons.append('currency_mismatch')
            except (ValueError, KeyError, TypeError):
                quote = None
                reasons.append('invalid_quote_json')
        checkin, checkout = row['price_quote_checkin_date'], row['price_quote_checkout_date']
        if checkin or checkout:
            try:
                start, end = date.fromisoformat(checkin), date.fromisoformat(checkout)
                nights = (end - start).days
                if nights <= 0: raise ValueError()
                quote_nights.update([nights]); quote_dates.extend((checkin, checkout))
            except ValueError: reasons.append('invalid_quoted_stay')
        elif quote: counters['quote_without_dates'] += 1
        if quote:
            counters['quote_rows'] += 1
            counters['quote_date_mismatch'] += int(quote.get('date_match') is False)
            counters['quote_date_match_unresolved'] += int(quote.get('date_match') is None)
            counters['quote_returned_dates_missing'] += int(not quote.get('returned_checkin_date') or not quote.get('returned_checkout_date'))
            counters['positive_price_currency_unresolved'] += int(positive and quote.get('currency') is None)
            if quote.get('requested_checkin_date') is not None:
                if checkin != quote['requested_checkin_date'] or checkout != quote.get('requested_checkout_date'):
                    reasons.append('quote_requested_dates_mismatch')
            for key, column in (('total_price', 'price_quote_total_price'), ('price_per_night', 'price_quote_price_per_night')):
                if row[column] and quote.get(key) is not None:
                    try:
                        a, b = Decimal(row[column]), Decimal(str(quote[key]))
                        if not a.is_finite() or not b.is_finite(): raise ValueError()
                        if a != b: counters['quote_flattened_rounding_difference'] += 1
                        # Flattened source amounts are rounded to two decimals. Compare
                        # decimal strings: binary 0.005 can spuriously exceed half a cent.
                        if abs(a-b) > Decimal('0.005'): reasons.append('quote_flattened_amount_mismatch')
                    except (ValueError, TypeError, InvalidOperation): reasons.append('invalid_quote_amount')
        elif positive:
            counters['positive_price_without_quote'] += 1
        # Compare only, never replace the inherited observed price with a quoted alternative.
        if row['price_quote_price_per_night']:
            try:
                quoted_price = float(row['price_quote_price_per_night'])
                if not math.isfinite(quoted_price): raise ValueError()
                if price is not None: counters['price_quote_difference'] += int(abs(price - quoted_price) > 0.005)
            except ValueError: reasons.append('invalid_quoted_price')
        counters['raw'] += 1
        counters['dwelling_filtered'] += int(dwelling)
        counters['positive_price'] += int(dwelling and positive)
        counters['eligible_missing_price'] += int(dwelling and row['price'] == '')
        counters['eligible_nonpositive_price'] += int(dwelling and price is not None and price <= 0)
        counters['inside_boundary_raw'] += int(inside is True)
        counters['inside_boundary_dwelling'] += int(dwelling and inside is True)
        counters['inside_boundary_positive_price'] += int(dwelling and positive and inside is True)
        counters['boundary_unclassified'] += int(inside is None)
        counters['duplicate_records'] += int(duplicate)
        counters['invalid_records'] += int(bool(reasons))
        counters['invalid_or_duplicate_records'] += int(bool(reasons) or duplicate)
        for reason in reasons: counters[reason] += 1
        audits.append(dict(row_number=number, listing_id=row['id'], raw=row, dwelling_eligible=dwelling,
                           price_nightly=price, log_price=log_price, positive_price=positive,
                           longitude=lon, latitude=lat, inside_boundary=inside, issues=reasons,
                           provider_neighbourhood=row['neighbourhood_cleansed'],
                           official_analysis_area_id=None, native_housing_area_id=None))
    for key in ('raw', 'dwelling_filtered', 'positive_price', 'eligible_missing_price', 'eligible_nonpositive_price',
                'invalid_records', 'duplicate_records', 'invalid_or_duplicate_records', 'boundary_unclassified',
                'quote_rows', 'quote_date_mismatch', 'price_quote_difference', 'quote_without_dates',
                'quote_date_match_unresolved', 'quote_returned_dates_missing', 'positive_price_currency_unresolved',
                'positive_price_without_quote', 'quote_flattened_rounding_difference'):
        counters.setdefault(key, 0)
    for key in ('inside_boundary_raw', 'inside_boundary_dwelling', 'inside_boundary_positive_price'):
        if boundary is None: counters[key] = None
        else: counters.setdefault(key, 0)
    if counters['invalid_or_duplicate_records']: blockers.append('Invalid/duplicate records require explicit qualification; no silent removal')
    if counters['positive_price_currency_unresolved']:
        blockers.append('Observed positive price with unresolved native quote currency')
    if boundary is None: blockers.append('Official municipal study boundary unavailable')
    if set(quote_currency) - {'None', currency} or not quote_currency.get(currency):
        blockers.append('Native quote currency unverified/mismatched')
    summary = dict(definition_version=DEFINITION, counts=dict(counters), schema=fields,
                   scrape_id=scrape_id, actual_scrape_dates=dict(sorted(scraped.items())),
                   quote_currency_counts=dict(quote_currency), quoted_stay_nights=dict(quote_nights),
                   quoted_stay_range=[min(quote_dates), max(quote_dates)] if quote_dates else None,
                   spatial_crs='EPSG:4326', membership_rule='official municipal union covers anonymised listing point',
                   price_format=price_format, currency=currency, blockers=blockers,
                   status='BLOCKED' if blockers else 'AUDITED_NOT_MODEL_SAMPLE')
    return audits, summary


def persist_ingestion(conn, scope, manifest, audits, summary, boundaries):
    """Atomic append-only ingestion ledger independent of housing-gated modelling runs."""
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    digest = register_manifest(conn, scope, manifest)
    p = {**scope.params(), 'digest': digest, 'definition': DEFINITION, 'summary': json.dumps(summary)}
    conn.execute(text('INSERT INTO v4_raw.listing_ingestions '
                      '(version,run_id,city,snapshot,purpose,definition_version,manifest_sha256,summary,created_at) VALUES '
                      '(:version,:run_id,:city,:snapshot,:purpose,:definition,:digest,CAST(:summary AS jsonb),now())'), p)
    for record, geom in boundaries:
        conn.execute(text('INSERT INTO v4_spatial.study_boundaries VALUES '
                          '(:version,:run_id,:city,:snapshot,:source,:area,:digest,:crs,:vintage,'
                          'ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geom),4326)))'),
                     {**p, 'source': record['source_id'], 'area': record['selection']['municipality'],
                      'crs': record['source_crs'], 'vintage': record['reference_period'],
                      'geom': json.dumps(mapping(geom))})
    query = text('INSERT INTO v4_raw.listing_audit VALUES '
                 '(:version,:run_id,:city,:snapshot,:row_number,:listing_id,CAST(:record AS jsonb))')
    for start in range(0, len(audits), 1000):
        conn.execute(query, [{**scope.params(), 'row_number': r['row_number'], 'listing_id': r['listing_id'],
                              'record': json.dumps(r, allow_nan=False)} for r in audits[start:start+1000]])
    # A commit freezes the ledger + all children. There is no fitted-model run.


def acquire_city(paths):
    config = load_sources(); s = paths.scope
    if s.snapshot != config['snapshot']:
        raise ValueError('Explicit 30 June 2026 batch required')
    cfg = config['cities'][s.city]; records = []; attempts = []
    def fetch(source, name, url, **kw):
        r = acquire(paths, source, name, url, **kw); attempts.append(r)
        if r['status'] == 'acquired': records.append(r)
        return r
    common = dict(extent='Inside Airbnb public catalogue', licence=config['licence'], reference_period='retrieval-time catalogue')
    page = fetch('catalogue', 'catalogue.html', config['catalogue_url'], **common)
    if page['status'] != 'acquired': raise RuntimeError('BLOCKED: official catalogue unavailable')
    html = paths.source('catalogue', 'catalogue.html').read_text()
    # Discover archive query IDs from the actual supported Gatsby page-data response.
    page_data = fetch('catalogue_page', 'page.json', 'https://insideairbnb.com/page-data/get-the-data/page-data.json', **common)
    if page_data['status'] != 'acquired': raise RuntimeError('BLOCKED: official catalogue archive metadata unavailable')
    hashes = json.loads(paths.source('catalogue_page', 'page.json').read_text())['staticQueryHashes']
    selected = None
    for h in hashes:
        if not re.fullmatch(r'[0-9]+', h): raise ValueError('Invalid official query ID')
        r = fetch('catalogue_' + h, 'archive.json', f'https://insideairbnb.com/page-data/sq/d/{h}.json', **common)
        if r['status'] != 'acquired': continue
        doc = json.loads(paths.source('catalogue_' + h, 'archive.json').read_text())
        if 'allData' in doc.get('data', {}):
            if selected is not None: raise ValueError('Ambiguous archive query')
            selected = catalogue_selection(doc, cfg['catalogue_city'], s.snapshot)
    if selected is None: raise RuntimeError('BLOCKED: exact matched catalogue entry unavailable')
    entry, url = selected
    if '1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4' not in html:
        raise ValueError('Official dictionary link changed; investigate')
    dictionary = fetch('dictionary', 'dictionary.csv', config['dictionary_url'], **common)
    if dictionary['status'] != 'acquired': raise RuntimeError('BLOCKED: official price dictionary unavailable')
    dictionary_rows = list(csv.reader(paths.source('dictionary', 'dictionary.csv').open()))
    if not any(r and r[0] == 'price' and any('local currency' in cell for cell in r) for r in dictionary_rows):
        raise ValueError('Official local-currency price definition changed')
    reuse = None
    if 'reuse_path' in cfg:
        reuse = (PROJECT_ROOT / cfg['reuse_path'], cfg['reuse_sha256'], cfg['original_retrieval'])
    listing = fetch('inside_airbnb', 'listings.csv.gz', url, extent=entry['region'],
                    licence=config['licence'], reference_period=s.snapshot, source_crs='EPSG:4326',
                    selection=entry, reuse=reuse)
    boundaries = []
    if s.city == 'copenhagen_frederiksberg':
        cities = json.loads((PROJECT_ROOT / 'archive/previous_analysis/config/cities.json').read_text())
        for b in cities['cities'][s.city]['study_boundary']['value'][:2]:
            code = re.search(r'/kommuner/([0-9]+)', b['source_url'])[1]
            r = fetch('municipality_' + code, 'boundary.geojson', b['source_url'], extent=b['geographic_extent'],
                      licence='https://dataforsyningen.dk/asset/PDF/rettigheder_vilkaar/Vilkår%20for%20brug%20af%20frie%20geografiske%20data.pdf',
                      reference_period=b['source_date'], source_crs='EPSG:4326', selection={'municipality': code},
                      reuse=(PROJECT_ROOT / b['path'], b['sha256'], b['acquired_at_utc']))
            boundaries.append((r, boundary_geometry(json.loads(paths.source(r['source_id'], r['filename']).read_text()), municipality=code, crs=r['source_crs'])))
    else:
        if s.city == 'stockholm':
            codes = fetch('official_scope_codes', 'municipal_codes.html', cfg['scope_codes_url'],
                          extent='Sweden county and municipal code registry', licence='SCB public code registry; reuse terms not independently qualified',
                          reference_period='2026', selection={'county': '01', 'municipality': '0180', 'name': 'Stockholm'})
            if codes['status'] != 'acquired': raise RuntimeError('BLOCKED: official municipal scope codes unavailable')
            code_html = paths.source('official_scope_codes', 'municipal_codes.html').read_text()
            if not re.search(r'0180\s+(?:<[^>]+>\s*)*Stockholm', code_html):
                raise ValueError('BLOCKED: official Stockholm municipal code unverified')
        r = fetch('official_boundary', 'boundary.json', cfg['boundary_url'], extent=cfg['catalogue_city'] + ' official municipal API',
                  licence=cfg['boundary_licence'], reference_period=cfg['boundary_vintage'] or 'current API at retrieval; geometry vintage UNRESOLVED',
                  source_crs='EPSG:4326', selection={'access_probe_only': True} if s.city == 'stockholm' else {'municipality': cfg['municipalities'][0]})
        if r['status'] == 'acquired':
            if s.city == 'stockholm': raise ValueError('BLOCKED: municipal API feature selection unverified; do not use generic feature')
            boundaries.append((r, boundary_geometry(json.loads(paths.source(r['source_id'], r['filename']).read_text()), municipality=cfg['municipalities'][0], crs=r['source_crs'])))
    _, manifest = freeze_sources(paths, records)
    if listing['status'] != 'acquired':
        summary = {'status': 'BLOCKED', 'counts': None, 'blockers': ['Matched detailed listings acquisition failed'], 'attempts': attempts}
        audits = []
    else:
        geom = unary_union([g for _, g in boundaries]) if boundaries else None
        audits, summary = audit_listings(paths.source('inside_airbnb', 'listings.csv.gz'), scrape_id=entry['scrapeID'],
                                        currency=cfg['currency'], boundary=geom, price_format=config['price_format'])
        summary.update(catalogue_selection=entry, batch_date=s.snapshot, attempts=attempts)
        if s.city == 'oslo':
            summary['blockers'].append('Oslo boundary is current-at-retrieval; geometry vintage not supplied by API; temporal qualification unresolved')
            summary['status'] = 'BLOCKED'
    summary['manifest_sha256'] = canonical_hash(manifest)
    summary['ingestion_code_sha256'] = sha256_file(Path(__file__))
    return manifest, audits, summary, boundaries


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('acquire', 'ingest', 'audit'))
    parser.add_argument('--version', required=True, choices=(VERSION,))
    parser.add_argument('--city', required=True, choices=CITIES)
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args(argv)
    try:
        s = Scope(args.version, args.city, args.snapshot, args.run_id)
        paths = Paths(s)
        if args.command == 'audit':
            from src.provenance.reporting import listing_evidence
            engine = get_engine()
            try:
                with engine.connect() as conn, conn.begin():
                    conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                    result = listing_evidence(conn, paths)
                print(json.dumps({'status': result['status'], 'city': s.city, 'counts': result['counts'], 'models_fitted': 0}))
                return 2 if result['status'] == 'BLOCKED' else 0
            finally:
                engine.dispose()
        manifest, rows, summary, boundaries = acquire_city(paths)
        if args.command == 'ingest':
            engine = get_engine()
            try:
                migrate(engine)
                with engine.begin() as conn:
                    persist_ingestion(conn, s, manifest, rows, summary, boundaries)
                    # Export only the persisted authoritative aggregate audit, never raw rows.
                    stored = conn.scalar(text('SELECT summary FROM v4_raw.listing_ingestions WHERE '
                                              'version=:version AND run_id=:run_id AND city=:city AND snapshot=:snapshot'), s.params())
                write_once(paths.report('listing_audit.json'), encoded_json(stored))
            finally:
                engine.dispose()
        else:
            write_once(paths.intermediate('acquisition_audit.json'), encoded_json(summary))
        print(json.dumps({'status': summary['status'], 'city': s.city, 'counts': summary['counts'],
                          'blockers': summary['blockers'], 'manifest_sha256': summary['manifest_sha256'],
                          'models_fitted': 0}))
        return 2 if summary['status'] == 'BLOCKED' else 0
    except SQLAlchemyError:
        print(json.dumps({'status': 'BLOCKED', 'reason': 'V4 database operation failed; inspect local database access/immutable run identity', 'models_fitted': 0}))
        return 2
    except (ValueError, RuntimeError, OSError) as error:
        # No response/row/credential content in public failures.
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error), 'models_fitted': 0}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
