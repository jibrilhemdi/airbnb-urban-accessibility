"""Thin V4 adapter: dedicated connection, checksum migration, insert-only storage."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.v4.identity import Scope
from src.v4.specification import DEFINITION_VERSION, model_definition

MIGRATIONS = PROJECT_ROOT / 'sql/v4_migrations'
SCOPE_SQL = 'version=:version AND run_id=:run_id AND city=:city AND snapshot=:snapshot'


def verify_database(conn, *, synthetic: bool = False) -> str:
    name = conn.scalar(text('SELECT current_database()'))
    valid = bool(re.fullmatch(r'test_v4_[0-9a-f]{32}', name)) if synthetic else name == 'thesis_accessibility_v4'
    if not valid:
        raise RuntimeError('Refuse V4 access to a V3/unapproved database')
    if conn.scalar(text("SELECT EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name LIKE 'v3_%' OR schema_name='meta')")):
        raise RuntimeError('V3/legacy schemas found; dedicated V4 database required')
    return name


def get_engine(env_path: Path = PROJECT_ROOT / '.env.v4'):
    # Never load .env, DB_* or mutate process environment (V3 settings stay V3).
    file_settings = dotenv_values(env_path) if env_path.is_file() else {}
    names = ('HOST', 'PORT', 'NAME', 'USER', 'PASSWORD')
    settings = {k: os.environ.get('V4_DB_' + k, file_settings.get('V4_DB_' + k)) for k in names}
    if any(not value for value in settings.values()):
        raise RuntimeError('Missing V4_DB_* settings; use .env.v4.example and a separately provisioned V4 database')
    if settings['NAME'] != 'thesis_accessibility_v4':
        raise RuntimeError('V4_DB_NAME must be thesis_accessibility_v4')
    try:
        port = int(settings['PORT'])
        if not 1 <= port <= 65535:
            raise ValueError()
    except ValueError as error:
        raise RuntimeError('Invalid V4_DB_PORT') from error
    return create_engine(URL.create('postgresql+psycopg2', username=settings['USER'], password=settings['PASSWORD'],
                                   host=settings['HOST'], port=port, database=settings['NAME']),
                         pool_pre_ping=True, connect_args={'connect_timeout': 5})


def migrate(engine, *, synthetic: bool = False, directory: Path = MIGRATIONS) -> list[str]:
    """V3 convention: transaction + advisory lock + applied file hash, V4 ledger only."""
    files = sorted(directory.glob('[0-9][0-9][0-9]_*.sql'))
    if not files or files[0].name != '023_v4_multicity_persistence.sql':
        raise RuntimeError('Expected V4 migration 023 (V3 ends at 022)')
    applied_now = []
    with engine.begin() as conn:
        verify_database(conn, synthetic=synthetic)
        conn.execute(text('SELECT pg_advisory_xact_lock(2026101104)'))
        conn.exec_driver_sql('CREATE SCHEMA IF NOT EXISTS v4_analysis')
        conn.exec_driver_sql('CREATE TABLE IF NOT EXISTS v4_analysis.schema_migrations '
                             '(migration_name text PRIMARY KEY, file_hash_sha256 text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())')
        applied = dict(conn.execute(text('SELECT migration_name,file_hash_sha256 FROM v4_analysis.schema_migrations')).all())
        if set(applied) - {p.name for p in files}:
            raise RuntimeError('Applied V4 migration missing from repository')
        for path in files:
            digest = sha256_file(path)
            if path.name in applied:
                if applied[path.name] != digest:
                    raise RuntimeError('Applied V4 migration changed: ' + path.name)
                continue
            conn.exec_driver_sql(path.read_text())
            conn.execute(text('INSERT INTO v4_analysis.schema_migrations VALUES (:name,:digest,now())'),
                         {'name': path.name, 'digest': digest})
            applied_now.append(path.name)
    return applied_now


def begin_run(conn, scope: Scope, dependencies: dict, *, reporting: dict | None = None) -> None:
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    if scope.purpose == 'research':
        from src.v4.cities import city_blockers, load_cities
        blockers = city_blockers(scope.version, scope.city)
        frozen_snapshot = load_cities()['cities'][scope.city]['snapshot_date']['value']
        if blockers or scope.snapshot != frozen_snapshot or not dependencies.get('source_manifests'):
            raise RuntimeError('BLOCKED: qualified city/H and source freeze required before creating a research run')
    conn.execute(text('INSERT INTO v4_analysis.runs '
                      '(version,run_id,city,snapshot,purpose,definition_version,scientific_sha256,scientific_dependencies,reporting_dependencies) '
                      'VALUES (:version,:run_id,:city,:snapshot,:purpose,:definition,:digest,CAST(:science AS jsonb),CAST(:reporting AS jsonb))'),
                 {**scope.params(), 'definition': DEFINITION_VERSION, 'digest': canonical_hash(dependencies),
                  'science': json.dumps(dependencies, allow_nan=False), 'reporting': json.dumps(reporting or {})})


def register_manifest(conn, scope: Scope, manifest: dict) -> str:
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    for key in ('version', 'city', 'snapshot', 'purpose'):
        if manifest.get(key) != scope.params()[key]:
            raise ValueError('Manifest city/version/snapshot/purpose mismatch')
    required = ('source_id', 'filename', 'source_url', 'acquired_at_utc', 'geographic_extent', 'source_crs', 'sha256')
    if any(not all(record.get(k) for k in required) for record in manifest['records']):
        raise ValueError('Complete immutable source provenance required')
    ids = [record['source_id'] for record in manifest['records']]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Duplicate/missing manifest source IDs')
    digest = canonical_hash(manifest)
    existing = conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE '
                                'version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),
                           {**scope.params(), 'digest': digest})
    if existing is not None:
        if existing != manifest:
            raise RuntimeError('Immutable manifest collision')
        return digest
    conn.execute(text('INSERT INTO v4_raw.source_manifests VALUES '
                      '(:version,:city,:snapshot,:digest,:purpose,CAST(:manifest AS jsonb))'),
                 {**scope.params(), 'digest': digest, 'manifest': json.dumps(manifest, allow_nan=False)})
    return digest


def verify_record_scope(record: dict, scope: Scope) -> None:
    aliases = {'version': 'version', 'city': 'city', 'city_id': 'city',
               'snapshot': 'snapshot', 'snapshot_date': 'snapshot', 'run_id': 'run_id'}
    for field, target in aliases.items():
        if field in record and record[field] != scope.params()[target]:
            raise ValueError('Record identity conflicts with explicit V4 scope: ' + field)


def observations(conn, scope: Scope, manifest_sha256: str, source_id: str, frame) -> None:
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    records = json_records(frame)  # Shared null-preserving serializer; never use V3 replacing persist().
    ids = [r.get('listing_id') for r in records]
    if any(i is None or str(i) == '' for i in ids) or len(set(map(str, ids))) != len(ids):
        raise ValueError('Missing/duplicate listing IDs; refuse silent deduplication')
    for record in records:
        verify_record_scope(record, scope)
        if 'source_id' in record and record['source_id'] != source_id:
            raise ValueError('Record source conflicts with scoped source manifest')
        conn.execute(text('INSERT INTO v4_raw.observations VALUES '
                          '(:version,:run_id,:city,:snapshot,:listing_id,:source_id,:area,:digest,CAST(:record AS jsonb))'),
                     {**scope.params(), 'listing_id': str(record['listing_id']), 'source_id': source_id,
                      'area': record.get('source_area_id'), 'digest': manifest_sha256, 'record': json.dumps(record, allow_nan=False)})


def persist_artifact(conn, scope: Scope, model: str, family: str, artifact: str, frame, *, scenario: str = 'primary') -> None:
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    from src.pipeline.output_paths import FAMILIES
    from src.v4.identity import token
    if family not in FAMILIES:
        raise ValueError('Unknown semantic artifact family')
    token(artifact)
    definition = model_definition(model, scenario=scenario)['definition_id']
    for index, record in enumerate(json_records(frame)):
        verify_record_scope(record, scope)
        conn.execute(text('INSERT INTO v4_analysis.artifacts VALUES '
                          '(:version,:run_id,:city,:snapshot,:definition,:family,:artifact,:key,CAST(:record AS jsonb))'),
                     {**scope.params(), 'definition': definition, 'family': family, 'artifact': artifact,
                      'key': str(index), 'record': json.dumps(record, allow_nan=False)})


def complete_run(conn, scope: Scope) -> None:
    verify_database(conn, synthetic=scope.purpose == 'synthetic')
    result = conn.execute(text('UPDATE v4_analysis.runs SET status=\'completed\' WHERE ' + SCOPE_SQL + " AND status='running'"), scope.params())
    if result.rowcount != 1:
        raise RuntimeError('Run missing or already stopped/completed')
