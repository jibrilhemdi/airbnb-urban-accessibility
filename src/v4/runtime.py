"""Read-only architectural preflight; empirical stages remain explicitly gated."""
from __future__ import annotations

from sqlalchemy import text
from src.v4.cities import city_blockers, load_cities
from src.v4.identity import Scope
from src.v4.persistence import get_engine, verify_database, MIGRATIONS
from src.ingestion.common import sha256_file


def preflight(scope: Scope, *, offline: bool = False) -> dict:
    blockers = city_blockers(scope.version, scope.city)
    frozen_snapshot = load_cities()['cities'][scope.city]['snapshot_date']['value']
    if frozen_snapshot is not None and scope.snapshot != frozen_snapshot:
        blockers.append('Selected snapshot differs from the city-qualified snapshot')
    blockers.append('V4 source freeze, common samples/folds and scientific QA are not yet implemented/qualified')
    blockers.append('V4 empirical stage dispatch is not implemented in this architecture step')
    if offline:
        blockers.append('V4 database not checked (--offline)')
    else:
        engine = None
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                verify_database(conn)
                history = dict(conn.execute(text('SELECT migration_name,file_hash_sha256 FROM v4_analysis.schema_migrations')).all())
                expected = {p.name: sha256_file(p) for p in MIGRATIONS.glob('*.sql')}
                if history != expected:
                    blockers.append('V4 migration ledger/hash mismatch')
                if conn.scalar(text('SELECT count(*) FROM v4_analysis.runs WHERE version=:version AND run_id=:run_id AND city=:city AND snapshot=:snapshot'), scope.params()):
                    blockers.append('Run ID already exists; never overwrite/resume implicitly')
        except RuntimeError as error:
            blockers.append(str(error))
        except Exception as error:
            blockers.append('V4 database check failed: ' + type(error).__name__)
        finally:
            if engine is not None:
                engine.dispose()
    return {**scope.params(), 'status': 'BLOCKED' if blockers else 'READY', 'blockers': blockers,
            'mutations': 0, 'research_executed': False}


def run(scope: Scope, *, offline: bool = False) -> dict:
    # Reuse preflight, never dispatch a V3 stage against V4 configurations.
    result = preflight(scope, offline=offline)
    if result['status'] != 'READY':
        return result
    raise RuntimeError('No V4 empirical stage has been authorized/implemented')
