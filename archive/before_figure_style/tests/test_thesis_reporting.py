"""Every selected thesis artifact must have final provenance and safe content."""
import unittest
import json
from pathlib import Path
from src.reporting.thesis_sources import ROOT,verify_catalog
from src.reporting.thesis_validate import artifacts,FORBIDDEN,STALE
import pandas as pd


class ThesisReportingTests(unittest.TestCase):
    def test_every_main_recommendation_exists_has_final_lineage_and_functional_name(self):
        catalog=verify_catalog();manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text())
        items={item['filename']:item for item in manifest['items']}
        recommendations=json.loads((ROOT/'reports/thesis_recommendations.json').read_text())
        for item in recommendations:
            with self.subTest(artifact=item['file']):
                self.assertTrue((ROOT/item['file']).is_file())
                self.assertIn(item['file'],items)
                self.assertFalse(STALE.search(Path(item['file']).name))
                self.assertEqual(items[item['file']]['source_catalog_sha256'],catalog['source_catalog_sha256'])
                self.assertTrue(items[item['file']]['source_run_artifact'])

    def test_full_publication_artifact_and_numeric_integrity(self):
        result=artifacts()
        self.assertEqual(result['figure_sets'],18)
        self.assertEqual(result['table_and_aggregate_views'],22)
        self.assertFalse(result['models_refitted'])

    def test_private_prediction_and_coordinate_rows_never_enter_public_exports(self):
        manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text())
        for item in manifest['items']:
            if item['filename'].endswith('.csv'):
                frame=pd.read_csv(ROOT/item['filename']);self.assertFalse(set(frame)&FORBIDDEN)
                if item['logical_name'].endswith(('_bins','_cells')):self.assertTrue(frame.n.ge(5).all())

    def test_release_hashes_local_links_zip_membership_and_complete_deliverables(self):
        from src.reporting.thesis_release import verify
        result=verify()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['private_data_check'],'PASS')
        audit=json.loads((ROOT/'reports/thesis_delivery_audit.json').read_text())
        self.assertEqual(audit['status'],'COMPLETE_THESIS_REPORTING')
        self.assertEqual(audit['remaining_required_deliverables'],[])
        self.assertTrue(all(item['completion_status'] in {'READY','NOT_NEEDED'} for item in audit['required_deliverables']))
