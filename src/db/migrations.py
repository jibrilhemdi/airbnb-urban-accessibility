"""Apply checksum-verified SQL migrations transactionally."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, text

from src.ingestion.common import PROJECT_ROOT, sha256_file


MIGRATION_DIR = PROJECT_ROOT / "sql" / "migrations"
REQUIRED_SCHEMAS = ("meta", "raw", "clean", "spatial", "features", "analysis")
LOCK_KEY = 2026092901


def migrate(engine: Engine, migration_dir: Path = MIGRATION_DIR) -> list[str]:
    legacy_dir = PROJECT_ROOT / "sql/legacy_migrations"
    files = sorted(legacy_dir.glob("[0-9][0-9][0-9]_*.sql")) + sorted(migration_dir.glob("[0-9][0-9][0-9]_*.sql"))
    if not files or files[:3] != [
        legacy_dir / "001_enable_extensions.sql",
        legacy_dir / "002_create_schemas.sql",
        legacy_dir / "003_create_metadata_tables.sql",
    ]:
        raise RuntimeError("Expected database setup migrations 001, 002, and 003")
    applied_now: list[str] = []
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": LOCK_KEY})
        has_history = conn.scalar(text("SELECT to_regclass('meta.schema_migrations') IS NOT NULL"))
        applied = {}
        if has_history:
            applied = dict(conn.execute(text(
                "SELECT migration_name, file_hash_sha256 FROM meta.schema_migrations"
            )).all())
        for path in files:
            digest = sha256_file(path)
            if path.name in applied:
                if applied[path.name].strip() != digest:
                    raise RuntimeError(f"Migration changed after application: {path.name}")
                continue
            conn.exec_driver_sql(path.read_text(encoding="utf-8"))
            applied_now.append(path.name)
            if path.name == "003_create_metadata_tables.sql":
                for prior_name in applied_now:
                    prior_path = next(p for p in files if p.name == prior_name)
                    conn.execute(text(
                        "INSERT INTO meta.schema_migrations (migration_name, file_hash_sha256) "
                        "VALUES (:name, :digest)"
                    ), {"name": prior_name, "digest": sha256_file(prior_path)})
            elif has_history or path.name > "003_create_metadata_tables.sql":
                conn.execute(text(
                    "INSERT INTO meta.schema_migrations (migration_name, file_hash_sha256) "
                    "VALUES (:name, :digest)"
                ), {"name": path.name, "digest": digest})
    return applied_now


def database_check(engine: Engine, expected_name: str) -> dict[str, object]:
    with engine.connect() as conn:
        actual_name = conn.scalar(text("SELECT current_database()"))
        if actual_name != expected_name:
            raise RuntimeError("Connected database name does not match DB_NAME")
        version = conn.scalar(text("SHOW server_version"))
        postgis = conn.scalar(text("SELECT postgis_version()"))
        schemas = sorted(conn.execute(text(
            "SELECT schema_name FROM information_schema.schemata "
            "WHERE schema_name IN ('meta','raw','clean','spatial','features','analysis')"
        )).scalars().all())
        if set(schemas) != set(REQUIRED_SCHEMAS):
            raise RuntimeError(f"Missing required schemas: {sorted(set(REQUIRED_SCHEMAS) - set(schemas))}")
        migrations = conn.scalar(text("SELECT count(*) FROM meta.schema_migrations"))
    return {"database": actual_name, "postgresql_version": version, "postgis_version": postgis,
            "schemas": schemas, "applied_migrations": migrations}


def version3_schema_check(engine: Engine) -> dict:
    """Read-only checks for the independently persisted current analytical layer."""
    required = ('v3_raw','v3_clean','v3_spatial','v3_features','v3_analysis')
    relations = ('v3_raw.osm_elements','v3_clean.airbnb_listings','v3_spatial.analysis_areas',
                 'v3_features.area_context','v3_spatial.canonical_bus_stops','v3_features.bus_accessibility',
                 'v3_features.opportunity_variants','v3_analysis.dataset_records','v3_analysis.outer_assignments',
                 'v3_analysis.inner_assignments','v3_analysis.artifacts')
    with engine.connect() as conn:
        for relation in relations:
            if not conn.scalar(text('SELECT to_regclass(:relation) IS NOT NULL'), {'relation': relation}):
                raise RuntimeError('Missing Version 3 database relation: ' + relation)
        columns = set(conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_schema='v3_features' AND table_name='listing_spatial_base'")).scalars())
        if 'provider_area_id' not in columns or 'municipality_proxy' in columns:
            raise RuntimeError('V3 provider QA schema requires the neutral diagnostic migration')
        populated = conn.scalar(text('SELECT count(*) FROM v3_clean.airbnb_listings'))
        history = conn.execute(text('SELECT migration_name,trim(file_hash_sha256) FROM meta.schema_migrations ORDER BY migration_name')).all()
    for name,digest in history:
        directories = (PROJECT_ROOT/'sql/legacy_migrations', PROJECT_ROOT/'sql/migrations')
        path = next((directory/name for directory in directories if (directory/name).exists()),None)
        if path is None or sha256_file(path) != digest:
            raise RuntimeError('Applied SQL migration identity/hash changed: ' + name)
    return {'version3_schemas': list(required), 'required_relations': list(relations),
            'current_clean_listing_rows': populated, 'applied_migration_hashes_verified': len(history)}
