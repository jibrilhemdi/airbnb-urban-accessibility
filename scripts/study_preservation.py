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


def verify(database=False):
    expected = json.loads((ROOT / 'docs/v4/protected_v3_manifest.json').read_text())
    for name, record in expected['files'].items():
        path = ROOT / name
        if (not path.is_file() or path.is_symlink() or sha256_file(path) != record['sha256']
                or path.stat().st_size != record['size_bytes']):
            raise RuntimeError('Protected historical bytes changed: ' + name)
    inventory = json.loads((ROOT / 'docs/analysis/path_inventory.json').read_text())
    changed = {'AGENTS.md', 'README.md', 'Makefile', '.gitignore', 'docs/v4/step_log.md'}
    for record in inventory['files']:
        if record['old_path'] in changed:
            continue
        if sha256_file(ROOT / record['old_path']) != record['sha256_before']:
            raise RuntimeError('Historical tracked file changed: ' + record['old_path'])
    if database:
        spec = importlib.util.spec_from_file_location('historical_checks', ROOT / 'scripts/v4_repository_checks.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if module.database_snapshot() != expected['database']:
            raise RuntimeError('Protected historical analytical SQL changed')
    return {'protected_files_verified': len(expected['files']),
            'tracked_baseline_verified': len(inventory['files']) - len(changed),
            'database_verified': database}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify(args.database), indent=2))
