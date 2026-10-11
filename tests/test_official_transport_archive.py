"""Check source integrity and preserve unknown official transport metadata explicitly."""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.db.sources import prepare_source
from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.ingestion.download_official_transport import inspect_zip, verify_archive, write_inventory


class OfficialTransportArchiveTest(unittest.TestCase):
    def test_zip_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../outside.shp", b"invalid")
            with self.assertRaisesRegex(ValueError, "Unsafe ZIP member"):
                inspect_zip(path)

    def test_missing_shapefile_components_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("source.shp", b"invalid")
            with self.assertRaisesRegex(ValueError, "Incomplete shapefile bundle"):
                inspect_zip(path)

    def test_provenance_retains_actual_extent_crs_and_unknown_licence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "data/raw/official_transport/2026-10-03/source.zip"
            path.parent.mkdir(parents=True)
            path.write_bytes(b"sample source")
            relative = path.relative_to(root).as_posix()
            entry = {"local_path": relative, "sha256": sha256_file(path), "size_bytes": path.stat().st_size,
                     "source_url": "https://example.test/official", "downloaded_at_utc": "2026-10-03T21:00:00+00:00",
                     "geographic_extent": "documented per-layer extent", "source_crs": ["EPSG:25832"],
                     "license": None, "source_date": None}
            result = prepare_source(path, project_root=root, manifest={relative: entry})
            self.assertEqual(result["geographic_extent"], entry["geographic_extent"])
            self.assertEqual(result["acquisition_date"].isoformat(), "2026-10-03")
            self.assertIsNone(result["source_date"])
            notes = json.loads(result["notes"])
            self.assertEqual(notes["source_crs"], ["EPSG:25832"])
            self.assertIsNone(notes["license"])

    def test_downloaded_collection_verifies_without_mutation(self):
        directory = PROJECT_ROOT / "data/raw/official_transport/2026-10-03"
        if not directory.exists():
            self.skipTest("Local official source archive is unavailable")
        before = {p.relative_to(directory).as_posix(): sha256_file(p) for p in directory.rglob("*") if p.is_file()}
        records = verify_archive(directory)
        after = {p.relative_to(directory).as_posix(): sha256_file(p) for p in directory.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(len(records), 83)
        self.assertTrue(all(r["source_url"] and r["geographic_extent"] for r in records))

    def test_inventory_retains_both_acquisitions_in_one_report(self):
        raw_root = PROJECT_ROOT / "data/raw/official_transport"
        first = raw_root / "2026-10-03"
        second = raw_root / "2026-10-04"
        if not all((p / "acquisition_metadata.json").exists() for p in (first, second)):
            self.skipTest("Local official source collections are unavailable")
        before = {p.relative_to(raw_root).as_posix(): sha256_file(p)
                  for p in raw_root.rglob("*") if p.is_file()}
        for collection in (first, second):
            verify_archive(collection)
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / "official_transport_source_inventory.md"
            self.assertEqual(write_inventory(first, report_path=report), report)
            original = report.read_bytes()
            text = original.decode()
            self.assertIn("### 2026-10-03", text)
            self.assertIn("### 2026-10-04", text)
            self.assertIn("`stoppesteder_movia`", text)
            self.assertIn("`station_oversigtskort`", text)
            self.assertIn("previously missed", text)
            self.assertIn("Missing (NULL)", text)
            self.assertEqual(write_inventory(second, report_path=report), report)
            self.assertEqual(report.read_bytes(), original)
            self.assertEqual(list(Path(temporary).iterdir()), [report])
        after = {p.relative_to(raw_root).as_posix(): sha256_file(p)
                 for p in raw_root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
