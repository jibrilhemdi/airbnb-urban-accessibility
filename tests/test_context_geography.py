"""Peer-area grouping is kept separate from primary predictive features."""
import unittest
from src.pipeline.protocol import AREA_NAMES,verify_income_evidence
from src.pipeline.model_specification import FEATURES,BASE_NUMERIC,E_NUMERIC,W_NUMERIC
from src.pipeline.smoke_checks import synthetic_frame
from src.pipeline.build_validation_splits import make_outer
class ContextGeographyTest(unittest.TestCase):
    def test_each_peer_area_held_out_once(self):
        frame=synthetic_frame();outer=make_outer(frame)['geographic_11']
        self.assertEqual(len(outer),11);self.assertEqual({x[0] for x in outer},set(AREA_NAMES))
        observed=[]
        for area,train,test in outer:
            self.assertTrue(frame.iloc[test].analysis_area.eq(area).all())
            self.assertFalse(frame.iloc[train].analysis_area.eq(area).any())
            observed.extend(test.tolist())
        self.assertEqual(sorted(observed),list(range(len(frame))))
    def test_context_bus_and_rail_are_core_without_area_dummy(self):
        for fs,columns in FEATURES.items():
            self.assertIn('log_population_density',columns);self.assertIn('income_100k_dkk',columns)
            self.assertNotIn('analysis_area',columns);self.assertNotIn('official_municipality_code',columns)
        self.assertIn('nearest_bus_euclidean_km',E_NUMERIC);self.assertIn('nearest_station_euclidean_km',E_NUMERIC)
        self.assertIn('nearest_bus_walking_minutes',W_NUMERIC);self.assertIn('nearest_station_walking_minutes',W_NUMERIC)
    def test_unverified_income_blocks_instead_of_being_relabeled(self):
        from unittest.mock import patch
        with patch('src.pipeline.protocol.DESIGN',{'income_harmonisation':{'status':'unverified','reason':'denominator unresolved','evidence':None}}):
            with self.assertRaisesRegex(RuntimeError,'unverified'):verify_income_evidence()
