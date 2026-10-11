"""Income evidence parsing and scientifically valid aggregation safeguards."""
import unittest
from decimal import Decimal
from unittest.mock import patch

from src.pipeline.investigate_income_harmonisation import (
    candidates, decile_mean, diagnostics, numeric_cell, reconstruct_municipality,
)
from src.pipeline.protocol import verify_income_evidence


class IncomeHarmonisationTests(unittest.TestCase):
    def test_missing_and_ambiguous_suppression_are_not_filled(self):
        for value in ('', '.', '..', 'NaN', 'Infinity'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                numeric_cell(value)
        self.assertEqual(numeric_cell('-200'),Decimal(-200))
        self.assertEqual(numeric_cell('0'),Decimal(0))
        with self.assertRaises(ValueError):
            numeric_cell('0',zero_is_suppression=True)

    def test_mean_requires_all_ten_deciles_and_retains_negative_income(self):
        self.assertEqual(decile_mean([-10]+[10]*9),Decimal(8))
        with self.assertRaises(ValueError):
            decile_mean([10]*9)
        with self.assertRaises(ValueError):
            decile_mean([10]*9+[None])
        self.assertEqual(decile_mean([1]+[11]*9,[9]+[1]*9),Decimal(6))

    def test_municipal_aggregation_requires_exact_population_weights(self):
        self.assertEqual(reconstruct_municipality({'a':100,'b':300},{'a':1,'b':3}),Decimal(250))
        with self.assertRaises(ValueError):
            reconstruct_municipality({'a':100,'b':300},{'a':1})
        with self.assertRaises(ValueError):
            reconstruct_municipality({'a':100},{'a':0})

    def test_actual_source_dimensions_and_official_crosswalk(self):
        records=candidates()
        self.assertEqual(len(records),15)
        city=[r for r in records if r['source_table']=='KKIND5' and r['analysis_area'] is not None]
        self.assertEqual(len(city),10)
        self.assertEqual(len({r['analysis_area'] for r in city}),10)
        frb=[r for r in records if r['analysis_area']=='frederiksberg_0147']
        self.assertEqual({r['price_unit_code'] for r in frb},{'005','006'})
        self.assertTrue(all(len(r['deciles'])==10 and r['harmonisation_status']=='unverified' for r in records))

    def test_diagnostics_do_not_invent_a_reconstructed_total(self):
        result=diagnostics(candidates())
        self.assertIsNone(result['reconstructed_from_ten_districts_dkk'])
        self.assertEqual(result['absolute_difference_dkk'],'329.0')
        self.assertEqual(result['decile_differences_city_minus_national_dkk'][-1],'-3376')
        self.assertTrue(result['exceeds_conditional_one_dkk_rounding_envelope'])
        self.assertEqual(result['status'],'blocked')
        evidence={'status':'unverified','reason':'Evidence alone is not a completed definition review',
                  'evidence':[{'path':'saved_metadata','sha256':'a'*64}]}
        with patch('src.pipeline.protocol.DESIGN',{'income_harmonisation':evidence}), self.assertRaises(RuntimeError):
            verify_income_evidence()


if __name__=='__main__':
    unittest.main()
