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
