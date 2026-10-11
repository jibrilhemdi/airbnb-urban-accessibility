"""Spatial diagnostics must never silently lose observations on date formatting."""
import unittest
import pandas as pd
from src.pipeline.run_spatial_diagnostics import residual_coordinates

class SpatialResidualJoinTests(unittest.TestCase):
    def fixture(self):
        part=pd.DataFrame({'snapshot_date':['2026-06-30']*2,'listing_id':[1,2],'residual':[.1,-.2]})
        frame=pd.DataFrame({'snapshot_date':['2026-06-30T00:00:00.000']*2,'listing_id':[2,1],
            'metric_x':[20.,10.],'metric_y':[40.,30.]})
        return part,frame
    def test_equivalent_date_formats_join_all_correct_coordinates(self):
        part,frame=self.fixture();joined=residual_coordinates(part,frame)
        self.assertEqual(len(joined),2);self.assertEqual(joined.metric_x.tolist(),[10.,20.])
        self.assertEqual(part.snapshot_date.iloc[0],'2026-06-30')
        self.assertEqual(frame.snapshot_date.iloc[0],'2026-06-30T00:00:00.000')
    def test_missing_or_duplicate_observation_is_rejected(self):
        part,frame=self.fixture()
        with self.assertRaises(RuntimeError):residual_coordinates(part,frame.iloc[:1])
        with self.assertRaises(pd.errors.MergeError):residual_coordinates(part,pd.concat([frame,frame.iloc[:1]]))
    def test_an_actual_day_difference_cannot_be_normalised_away(self):
        part,frame=self.fixture();frame.loc[0,'snapshot_date']='2026-07-01T00:00:00.000'
        with self.assertRaises(RuntimeError):residual_coordinates(part,frame)

if __name__=='__main__':unittest.main()
