"""Missing municipal income must not inherit a national value or approval."""
import json
import unittest

from src.ingestion.common import PROJECT_ROOT
from src.pipeline.review_municipal_income_sources import area_coverage, source_reviews


class MissingMunicipalIncomeTests(unittest.TestCase):
    def test_eleven_peer_areas_remain_missing_without_verified_income(self):
        coverage = area_coverage()
        self.assertEqual(len(coverage), 11)
        self.assertTrue(all(r['proposed_harmonised_income_dkk'] is None for r in coverage))
        self.assertFalse(any(r['primary_eligible'] for r in coverage))
        frb = next(r for r in coverage if r['analysis_area'] == 'frederiksberg_0147')
        self.assertIsNone(frb['candidate_source_table'])
        self.assertEqual(frb['intended_source_institution'], 'Frederiksberg Municipality')
        self.assertEqual(frb['status'], 'matching_municipal_statistic_not_obtained')

    def test_municipal_leads_are_not_accepted_as_matching_means(self):
        config = json.loads((PROJECT_ROOT / 'config/municipal_income_investigation.json').read_text())
        reviews = source_reviews(config)
        self.assertTrue(reviews)
        self.assertTrue(any(r['institution'] == 'Frederiksberg Municipality' for r in reviews))
        self.assertTrue(all(r['institution'] in ['Frederiksberg Municipality', 'Copenhagen Municipality'] for r in reviews))
        self.assertFalse(any(r['accepted_for_primary'] or r['matching_2024_equivalised_mean_found'] for r in reviews))
        self.assertEqual(config['status'], 'unverified')


if __name__ == '__main__':
    unittest.main()
