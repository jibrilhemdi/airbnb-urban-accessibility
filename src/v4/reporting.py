"""Aggregate-only exports from completed, dependency-matched V4 SQL runs."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from sqlalchemy import text

from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash
from src.v4.identity import Paths, scientific_dependencies, write_once
from src.v4.persistence import SCOPE_SQL, verify_database


def listing_evidence(conn, paths: Paths) -> dict:
    """Whitelisted aggregate/provenance export; never select listing records."""
    s = paths.scope
    verify_database(conn, synthetic=s.purpose == 'synthetic')
    row = conn.execute(text('SELECT summary,manifest_sha256 FROM v4_raw.listing_ingestions WHERE ' + SCOPE_SQL), s.params()).mappings().one_or_none()
    if row is None:
        raise RuntimeError('No scoped ingestion audit; no invented observations')
    summary = row['summary']
    counts = ('raw', 'dwelling_filtered', 'positive_price', 'eligible_missing_price', 'eligible_nonpositive_price',
              'inside_boundary_raw', 'inside_boundary_dwelling', 'inside_boundary_positive_price',
              'invalid_records', 'duplicate_records', 'invalid_or_duplicate_records', 'boundary_unclassified',
              'quote_rows', 'quote_date_mismatch', 'price_quote_difference', 'quote_without_dates',
              'quote_date_match_unresolved', 'quote_returned_dates_missing', 'positive_price_currency_unresolved',
              'positive_price_without_quote', 'quote_flattened_rounding_difference')
    supplied_counts = summary.get('counts')
    aggregates = {k: supplied_counts[k] for k in counts if k in supplied_counts} if isinstance(supplied_counts, dict) else {k: None for k in counts}
    if any(v is not None and (type(v) is not int or v < 0) for v in aggregates.values()):
        raise ValueError('Invalid aggregate count export')
    actual = conn.execute(text('SELECT count(*) AS raw, '
                              "count(*) FILTER (WHERE record->>'dwelling_eligible'='true') AS dwelling_filtered, "
                              "count(*) FILTER (WHERE record->>'dwelling_eligible'='true' AND record->>'positive_price'='true') AS positive_price "
                              'FROM v4_raw.listing_audit WHERE ' + SCOPE_SQL), s.params()).mappings().one()
    for key, value in actual.items():
        if key in aggregates and aggregates[key] is not None and value != aggregates[key]:
            raise RuntimeError('Authoritative raw audit and aggregate counts disagree')
    manifest = conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE '
                                'version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),
                           {**s.params(), 'digest': row['manifest_sha256']})
    if canonical_hash(manifest) != row['manifest_sha256']:
        raise RuntimeError('Source manifest integrity mismatch')
    provenance = []
    for record in manifest['records']:
        if sha256_file(paths.source(record['source_id'], record['filename'])) != record['sha256']:
            raise RuntimeError('Frozen acquisition bytes changed')
        fields = ('source_id', 'filename', 'source_url', 'final_url', 'acquired_at_utc', 'verified_at_utc',
                  'geographic_extent', 'reference_period', 'selection', 'licence', 'sha256', 'size_bytes',
                  'source_crs', 'local_location', 'http_status', 'content_type', 'last_modified', 'reused_from')
        provenance.append({k: record[k] for k in fields if k in record})
    fields = ('definition_version', 'status', 'batch_date', 'scrape_id', 'actual_scrape_dates',
              'quote_currency_counts', 'quoted_stay_nights', 'quoted_stay_range', 'spatial_crs',
              'membership_rule', 'price_format', 'currency', 'blockers', 'schema', 'ingestion_code_sha256')
    result = {**s.params(), **{k: summary[k] for k in fields if k in summary}, 'counts': aggregates,
              'manifest_sha256': row['manifest_sha256'], 'sources': provenance,
              'failed_acquisitions': [{k: r.get(k) for k in ('source_id', 'source_url', 'acquired_at_utc',
                                     'reference_period', 'licence', 'http_status', 'status', 'selection')}
                                     for r in summary.get('attempts', []) if r.get('status') == 'BLOCKED'],
              'models_fitted': 0, 'prediction_sample_qualified': False}
    destination = paths.report('public_listing_audit.json')
    write_once(destination, (json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode())
    return result


def report(conn, paths: Paths) -> dict:
    s = paths.scope
    verify_database(conn, synthetic=s.purpose == 'synthetic')
    row = conn.execute(text('SELECT status,scientific_sha256,scientific_dependencies FROM v4_analysis.runs WHERE ' + SCOPE_SQL), s.params()).mappings().one_or_none()
    if row is None or row['status'] != 'completed':
        raise RuntimeError('Report requires an existing completed scoped V4 run')
    manifests = row['scientific_dependencies'].get('source_manifests', {})
    if not manifests:
        raise RuntimeError('Report requires frozen source manifests')
    for digest, manifest in manifests.items():
        if canonical_hash(manifest) != digest:
            raise RuntimeError('Source manifest checksum mismatch')
        for key in ('version', 'city', 'snapshot', 'purpose'):
            if manifest.get(key) != s.params()[key]:
                raise RuntimeError('Source manifest scope mismatch')
        for record in manifest['records']:
            if sha256_file(paths.source(record['source_id'], record['filename'])) != record['sha256']:
                raise RuntimeError('Frozen raw source bytes changed')
    current = scientific_dependencies(s.city, source_manifests=manifests)
    if canonical_hash(current) != row['scientific_sha256']:
        raise RuntimeError('Scientific dependencies changed; report cannot certify an unchanged fit')
    fields = ('definition_id', 'engine', 'validation', 'n', 'rmse', 'mae')
    rows = conn.execute(text('SELECT ' + ','.join(fields) + ' FROM v4_analysis.aggregate_metrics WHERE ' + SCOPE_SQL + ' ORDER BY definition_id,engine,validation'), s.params()).mappings().all()
    if not rows:
        raise RuntimeError('No aggregate metrics available; do not invent results')
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    target = paths.output('tables', 'reporting', 'aggregate_metrics.csv')
    metadata = {**s.params(), 'status': 'AGGREGATE_EXPORT', 'scientific_sha256': row['scientific_sha256'],
                'reporting_sha256': sha256_file(Path(__file__)), 'row_count': len(rows)}
    receipt = paths.report('aggregate_export.json')
    if target.exists() or receipt.exists():
        raise RuntimeError('Refuse to overwrite existing completed-run exports')
    write_once(target, out.getvalue().encode())
    write_once(receipt, (json.dumps(metadata, indent=2) + '\n').encode())
    return metadata
