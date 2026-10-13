"""Atomic immutable stage packages in authoritative PostGIS; no old-row writes."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import re

from shapely.geometry import mapping
from sqlalchemy import text

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.specification import CITIES, load_design, neutral_token
from src.study.sources import get_engine

MIGRATION = PROJECT_ROOT / 'sql/study_migrations/029_study_foundation.sql'


def verify_database(conn, purpose='research'):
    name = conn.scalar(text('SELECT current_database()'))
    if not (name == 'thesis_accessibility_v4' if purpose == 'research' else re.fullmatch(r'test_study_[0-9a-f]{32}', name)):
        raise ValueError('Dedicated approved research or disposable test database required')
    if conn.scalar(text("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name LIKE 'v3_%' OR schema_name='meta')")):
        raise ValueError('Historical baseline database is never a writable research destination')


def setup(engine, purpose='research'):
    with engine.begin() as conn:
        verify_database(conn, purpose)
        conn.execute(text('SELECT pg_advisory_xact_lock(2026101301)'))
        exists = conn.scalar(text("SELECT to_regclass('study.schema_migrations') IS NOT NULL"))
        if exists:
            applied = dict(conn.execute(text('SELECT migration_name,file_hash_sha256 FROM study.schema_migrations')).all())
            if applied != {MIGRATION.name: sha256_file(MIGRATION)}:
                raise ValueError('Study migration ledger or applied bytes differ')
            return []
        conn.exec_driver_sql(MIGRATION.read_text())
        conn.execute(text('INSERT INTO study.schema_migrations(migration_name,file_hash_sha256) VALUES (:name,:digest)'),
                     {'name': MIGRATION.name, 'digest': sha256_file(MIGRATION)})
        return [MIGRATION.name]


def run_id(city, family):
    return neutral_token(city+'_'+family+'_'+datetime.now(timezone.utc).strftime('%Y%m%dt%H%M%S%fz'))


def dependencies(extra=None):
    design, cities = load_design()
    compatibility = ['src/ingestion/common.py','src/ingestion/price.py','src/pipeline/protocol.py',
                     'src/pipeline/build_analysis_dataset.py','src/pipeline/build_airbnb_sample.py',
                     'src/pipeline/model_specification.py','src/pipeline/osm_taxonomy.py',
                     'src/pipeline/build_bus_euclidean_accessibility.py','src/spatial/walking_network.py',
                     'src/spatial/walking_routing.py','src/provenance/source_reuse.py','src/provenance/identity.py',
                     'src/provenance/listings.py','src/provenance/persistence.py','src/provenance/specification.py']
    paths = sorted([*(PROJECT_ROOT / 'src/study').glob('*.py'),*(PROJECT_ROOT / p for p in compatibility)])
    return {'design': design, 'cities': cities, 'code': {p.relative_to(PROJECT_ROOT).as_posix(): sha256_file(p) for p in paths},
            'requirements_sha256': sha256_file(PROJECT_ROOT/'requirements.txt'), **(extra or {})}


def commit_package(conn, *, city, family, summary, records=None, geometries=None, deps=None, identity=None, purpose='research'):
    verify_database(conn, purpose)
    if city not in CITIES:
        raise ValueError('City isolation required')
    identity = run_id(city, family) if identity is None else neutral_token(identity)
    science = dependencies() if deps is None else deps
    params = {'run': identity, 'city': city, 'family': neutral_token(family), 'purpose': purpose,
              'deps': json.dumps(science, allow_nan=False), 'dh': canonical_hash(science),
              'summary': json.dumps(summary, allow_nan=False), 'sh': canonical_hash(summary)}
    conn.execute(text("INSERT INTO study.checkpoints(run_id,city,family,purpose,design_id,snapshot,dependencies,dependencies_sha256,summary,summary_sha256) "
                      "VALUES(:run,:city,:family,:purpose,'three_city_accessibility_transfer','2026-06-30',CAST(:deps AS jsonb),:dh,CAST(:summary AS jsonb),:sh)"), params)
    for artifact, rows in (records or {}).items():
        neutral_token(artifact)
        payload = []
        for i, record in enumerate(rows):
            if record.get('city', city) != city:
                raise ValueError('Record city conflicts with package')
            payload.append({'run': identity, 'city': city, 'family': family, 'artifact': artifact,
                            'key': str(i), 'record': json.dumps(record, allow_nan=False)})
        if payload:
            conn.execute(text('INSERT INTO study.records VALUES (:run,:city,:family,:artifact,:key,CAST(:record AS jsonb))'), payload)
    for key, geom, props in geometries or []:
        conn.execute(text('INSERT INTO study.geometries VALUES (:run,:city,:family,:key,CAST(:properties AS jsonb),'
                          'ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geojson),4326)))'),
                     {'run': identity, 'city': city, 'family': family, 'key': key,
                      'properties': json.dumps(props, allow_nan=False), 'geojson': json.dumps(mapping(geom))})
    return identity


def read_package(conn, identity, city, family):
    row = conn.execute(text('SELECT summary,summary_sha256,dependencies,dependencies_sha256 FROM study.checkpoints '
                            'WHERE run_id=:run AND city=:city AND family=:family'),
                       {'run': identity, 'city': city, 'family': family}).one()
    if canonical_hash(row.summary) != row.summary_sha256 or canonical_hash(row.dependencies) != row.dependencies_sha256:
        raise ValueError('Authoritative package integrity mismatch')
    return row.summary, row.dependencies
