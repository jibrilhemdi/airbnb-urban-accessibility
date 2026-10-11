"""V4 bootstrap checks: hash protected V3 bytes and run isolated baseline tests.

No research runner, migration, ingestion, model result, or reporting refresh is
invoked. Database checks use a repeatable-read, read-only transaction. Only
hashes, counts, migration names and run statuses leave that transaction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PROTECTED_ROOTS = (
    "data/raw", "data/interim", "data/processed", "data/metadata",
    "outputs", "reports", "archive", "config", "docs/design", "sql",
)
V4_ROOTS = ("data/raw/v4", "data/interim/v4", "data/processed/v4",
            "data/metadata/v4", "outputs/v4", "reports/v4", "config/v4")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def protected_files() -> dict:
    result = {}
    for base in PROTECTED_ROOTS:
        for path in sorted((ROOT / base).rglob("*")):
            relative = path.relative_to(ROOT).as_posix()
            if path.name == ".DS_Store" or any(
                relative == p or relative.startswith(p + "/") for p in V4_ROOTS
            ):
                continue
            if path.is_symlink():
                raise RuntimeError("Protected symlink requires review: " + relative)
            if path.is_file():
                result[relative] = {"sha256": sha256_file(path),
                                    "size_bytes": path.stat().st_size}
    # Existing local packaging is private; only its checksum is recorded.
    for path in sorted(ROOT.glob("*.zip")):
        result[path.name] = {"sha256": sha256_file(path),
                             "size_bytes": path.stat().st_size}
    return dict(sorted(result.items()))


def database_snapshot() -> dict:
    from sqlalchemy import text
    from src.db.connection import get_engine

    engine = get_engine()
    try:
        with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
            conn.exec_driver_sql("SET LOCAL statement_timeout = '120s'")
            identity = dict(conn.execute(text(
                "SELECT current_database() AS database, "
                "current_setting('server_version') AS postgresql, "
                "postgis_version() AS postgis, "
                "current_setting('transaction_read_only') AS read_only"
            )).mappings().one())
            migrations = []
            for name, digest in conn.execute(text(
                "SELECT migration_name,trim(file_hash_sha256) "
                "FROM meta.schema_migrations ORDER BY migration_name"
            )):
                paths = [ROOT / base / name for base in
                         ("sql/legacy_migrations", "sql/migrations")]
                matches = [p for p in paths if p.is_file()]
                if len(matches) != 1 or sha256_file(matches[0]) != digest:
                    raise RuntimeError("Applied migration checksum mismatch: " + name)
                migrations.append({"path": matches[0].relative_to(ROOT).as_posix(),
                                   "sha256": digest})
            runs = [dict(r) for r in conn.execute(text(
                "SELECT run_id,status FROM v3_analysis.runs ORDER BY run_id"
            )).mappings()]
            fingerprints = {}
            # Stable primary-key ordering, UTF-8 row JSON and one LF per record.
            # Private rows are streamed into SHA-256, never written or printed.
            orders = {
                "runs": "run_id",
                "dataset_records": "snapshot_date,listing_id",
                "outer_assignments": "snapshot_date,listing_id,scheme,outer_fold",
                "inner_assignments": "snapshot_date,listing_id,scheme,outer_fold",
                "artifacts": "run_id,family,artifact,record_key",
            }
            for table, order in orders.items():
                digest = hashlib.sha256()
                count = 0
                rows = conn.execution_options(stream_results=True).execute(text(
                    f"SELECT row_to_json(t)::text FROM v3_analysis.{table} t ORDER BY {order}"
                ))
                for (record,) in rows:
                    digest.update(record.encode("utf-8") + b"\n")
                    count += 1
                fingerprints["v3_analysis." + table] = {
                    "rows": count, "ordered_row_sha256": digest.hexdigest()}
            schemas = conn.execute(text(
                "SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name LIKE 'v3_%' OR schema_name LIKE 'v4_%' "
                "ORDER BY schema_name"
            )).scalars().all()
            return {**identity, "schemas": schemas, "applied_migrations": migrations,
                    "runs": runs, "analytical_fingerprints": fingerprints}
    finally:
        engine.dispose()


def baseline_tests() -> None:
    os.environ["THESIS_DB_TEST"] = "0"
    os.environ["THESIS_V3_INTEGRATION"] = "0"
    from src.pipeline import build_tuning_candidates as candidates
    if not candidates.PATH.is_file():
        raise RuntimeError("Missing V3 candidate freeze; baseline must not create it")
    original_write = candidates.write_json
    expected = ROOT / "outputs/tables/validation/xgboost_candidates.json"
    with tempfile.TemporaryDirectory(prefix="v4-baseline-") as directory:
        def isolated_write(path, value):
            if Path(path) != expected:
                raise RuntimeError("Unexpected candidate-helper write: " + str(path))
            original_write(Path(directory) / "xgboost_candidates.json", value)

        with patch.object(candidates, "write_json", isolated_write):
            suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
            result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--capture", type=Path)
    actions.add_argument("--verify", type=Path)
    actions.add_argument("--baseline-tests", action="store_true")
    parser.add_argument("--database", action="store_true")
    args = parser.parse_args()
    if args.baseline_tests:
        if args.database:
            parser.error("Baseline tests never enable live database tests")
        baseline_tests()
        return
    if args.capture and args.capture.exists():
        raise RuntimeError("Refusing to overwrite a protected baseline")
    snapshot = {"format": "v4_protected_v3_sha256_v1", "files": protected_files()}
    if args.database:
        snapshot["database"] = database_snapshot()
    if args.capture:
        args.capture.parent.mkdir(parents=True, exist_ok=True)
        with args.capture.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
        print("Captured protected V3 baseline:", len(snapshot["files"]), "files")
    else:
        expected = json.loads(args.verify.read_text())
        if "database" in expected and not args.database:
            raise RuntimeError("Baseline includes SQL; verification requires --database")
        if snapshot != expected:
            raise RuntimeError("Protected V3 baseline changed; inspect before proceeding")
        print("Protected V3 baseline unchanged:", len(snapshot["files"]), "files",
              "and SQL fingerprints" if args.database else "")


if __name__ == "__main__":
    main()
