"""Explicit read-only access to approved immutable listing scopes by manifest hash."""
from __future__ import annotations

import json
import re
from pathlib import Path
from sqlalchemy import text

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.v4.identity import Paths, Scope
from src.v4.persistence import SCOPE_SQL, verify_database
from src.v4.specification import DEFINITION_VERSION

POLICY = PROJECT_ROOT / 'config/v4/listing_reuse_accessibility_only.json'
# These are private audit fields. Raw/provider/housing columns cannot leak into
# analytical selection by SELECT * or by a housing-area join/filter.
LISTING_FIELDS = ('listing_id', 'dwelling_eligible', 'price_nightly', 'log_price', 'positive_price',
                  'inside_boundary', 'longitude', 'latitude', 'official_analysis_area_id', 'issues')


def reuse_listing_source(conn, scope: Scope, manifest_sha256: str, *, root: Path = PROJECT_ROOT,
                        policy: dict | None = None) -> dict:
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    if scope.design_id != DEFINITION_VERSION or not re.fullmatch('[0-9a-f]{64}', manifest_sha256):
        raise ValueError('Revised design and exact source manifest hash required')
    if policy is not None and scope.purpose != 'synthetic':
        raise ValueError('Research reuse requires the recorded policy, not a caller override')
    policy = json.loads(POLICY.read_text()) if policy is None else policy
    selected = policy['cities'][scope.city]
    if (policy['design_id'] != scope.design_id or policy['source_version'] != scope.version
            or selected['manifest_sha256'] != manifest_sha256 or selected['snapshot'] != scope.snapshot):
        raise ValueError('Source not approved for selected design/city/snapshot/hash')
    source = {**scope.params(), 'run_id': selected['run_id'], 'digest': manifest_sha256}
    row = conn.execute(text('SELECT summary,manifest_sha256,purpose FROM v4_raw.listing_ingestions WHERE '
                            + SCOPE_SQL), source).mappings().one_or_none()
    if row is None or row['manifest_sha256'] != manifest_sha256 or row['purpose'] != scope.purpose:
        raise RuntimeError('Approved immutable listing ingestion missing/mismatched')
    manifest = conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE '
                               'version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'), source)
    if manifest is None or canonical_hash(manifest) != manifest_sha256:
        raise RuntimeError('Approved source manifest integrity mismatch')
    for key in ('version', 'city', 'snapshot', 'purpose'):
        if manifest.get(key) != scope.params()[key]:
            raise ValueError('Source manifest scope mismatch')
    # Source paths are independent of the new design/run. Never copy/reingest.
    paths = Paths(scope, root)
    for record in manifest['records']:
        if sha256_file(paths.source(record['source_id'], record['filename'])) != record['sha256']:
            raise RuntimeError('Approved frozen source bytes changed/missing')
    return {'source_scope': {k: source[k] for k in ('version', 'run_id', 'city', 'snapshot')},
            'manifest_sha256': manifest_sha256, 'manifest': manifest,
            'summary': row['summary'], 'mutations': 0, 'source_reingested': False}


def read_listing_audit(conn, scope: Scope, manifest_sha256: str, **kwargs) -> list[dict]:
    """All audit rows, including missing prices; no implicit model sample or H filter."""
    approved = reuse_listing_source(conn, scope, manifest_sha256, **kwargs)
    keys = ','.join("'" + k + "',record->'" + k + "'" for k in LISTING_FIELDS)
    query = text('SELECT jsonb_build_object(' + keys + ') FROM v4_raw.listing_audit WHERE '
                 + SCOPE_SQL + ' ORDER BY row_number')
    return conn.execute(query, approved['source_scope']).scalars().all()
