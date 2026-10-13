"""Verify exact historical bytes and optionally analytical SQL fingerprints."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.ingestion.common import sha256_file
from src.study.archive import preserved_path


def historical_store():
    """Fingerprint every historical dedicated-store table without exporting rows."""
    import hashlib
    from sqlalchemy import text
    from src.provenance.persistence import get_engine
    engine = get_engine()
    result = {}
    try:
        with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            tables = conn.execute(text("SELECT table_schema,table_name FROM information_schema.tables "
                                       "WHERE table_schema LIKE 'v4_%' AND table_type='BASE TABLE' ORDER BY 1,2")).all()
            for schema, table in tables:
                columns = conn.execute(text("SELECT a.attname FROM pg_index i JOIN pg_attribute a "
                                            "ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey) "
                                            "WHERE i.indrelid=to_regclass(:table) AND i.indisprimary ORDER BY a.attnum"),
                                       {'table': schema+'.'+table}).scalars().all()
                # Child partition tables can lack a local PK. Canonical full-row
                # text provides deterministic ordering with duplicate multiplicity.
                order = ','.join('"'+c+'"' for c in columns) if columns else 'row_to_json(t)::text'
                digest, n = hashlib.sha256(), 0
                for record in conn.execution_options(stream_results=True).execute(
                        text('SELECT row_to_json(t)::text FROM "'+schema+'"."'+table+'" t ORDER BY '+order)).scalars():
                    digest.update((record+'\n').encode()); n += 1
                result[schema+'.'+table] = {'rows': n, 'sha256': digest.hexdigest()}
    finally:
        engine.dispose()
    return result


def verify(database=False):
    expected = json.loads((ROOT / 'archive/previous_analysis/docs/protected_v3_manifest.json').read_text())
    for name, record in expected['files'].items():
        if name=='thesis_results_v3.zip':
            decision=json.loads((ROOT/'docs/analysis/archive_manifest.json').read_text())['researcher_exclusions']
            if name in decision:continue
        path = preserved_path(name,record['sha256'])
        if (not path.is_file() or path.is_symlink() or sha256_file(path) != record['sha256']
                or path.stat().st_size != record['size_bytes']):
            raise RuntimeError('Protected historical bytes changed: ' + name)
    inventory = json.loads((ROOT / 'docs/analysis/path_inventory.json').read_text())
    changed = {'AGENTS.md', 'README.md', 'Makefile', '.gitignore', 'docs/v4/step_log.md'}
    for record in inventory['files']:
        if record.get('action')=='extend_historical_source_isolation_with_exact_archived_code':
            if (sha256_file(preserved_path(record['archive_path'],record['sha256_before']))!=record['sha256_before']
                    or sha256_file(ROOT / record['old_path'])!=record['sha256_after']):
                raise RuntimeError('Audited compatibility extension or original code bytes changed')
            continue
        if record['old_path'] in changed:
            continue
        if sha256_file(preserved_path(record['old_path'],record['sha256_before'])) != record['sha256_before']:
            raise RuntimeError('Historical tracked file changed: ' + record['old_path'])
    if database:
        spec = importlib.util.spec_from_file_location('historical_checks', ROOT / 'archive/previous_analysis/scripts/v4_repository_checks.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.ROOT = ROOT
        if module.database_snapshot() != expected['database']:
            raise RuntimeError('Protected historical analytical SQL changed')
    return {'protected_files_verified': len(expected['files'])-1,
            'researcher_exclusions': ['thesis_results_v3.zip: explicitly no longer required'],
            'tracked_baseline_verified': len(inventory['files']) - len(changed),
            'database_verified': database}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', action='store_true')
    parser.add_argument('--capture-store', action='store_true')
    parser.add_argument('--verify-store', action='store_true')
    args = parser.parse_args()
    if args.capture_store or args.verify_store:
        path = ROOT / 'docs/analysis/historical_store.json'
        actual = historical_store()
        if args.capture_store:
            with path.open('x') as handle:
                handle.write(json.dumps(actual, indent=2)+'\n')
        elif json.loads(path.read_text()) != actual:
            raise RuntimeError('Historical dedicated store changed')
        print('Historical dedicated store tables verified:', len(actual))
    print(json.dumps(verify(args.database), indent=2))
