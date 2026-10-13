import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from src.reporting.study_training_sensitivity import TrainingTailRegressor
from src.reporting.study_results import paired
from src.study.sources import write_once
from src.reporting.study_extended_sensitivity import buffer_training
from src.study.cli import completion_status,main
from unittest.mock import patch
import contextlib
import io


class ReportingGuards(unittest.TestCase):
    def test_complete_release_exposes_all_three_association_cities(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'docs/analysis/release_audit.json';path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'full_rerun_complete':True,'primary_prediction_cities_complete':3,
                                        'association_cities_complete':3,'six_transfer_directions_complete':True,'blocker':None}))
            result=completion_status(root)
            self.assertEqual(result['status'],'COMPLETE')
            self.assertEqual(result['association_cities_complete'],3)
            self.assertEqual(result['completed_transfer_directions'],6)

    def test_scientific_blocker_cannot_be_reported_as_full_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'docs/analysis/release_audit.json';path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'full_rerun_complete':False,'primary_prediction_cities_complete':3,
                                        'six_transfer_directions_complete':True,'blocker':'Stockholm missingness'}))
            result=completion_status(root)
            self.assertEqual(result['status'],'PARTIAL_BLOCKED_INFERENCE')
            self.assertTrue(result['models_fitted']);self.assertEqual(result['completed_transfer_directions'],6)
            self.assertFalse(result['full_rerun_complete'])

    def test_completed_transfer_refused_before_any_new_fit(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);path=root/'runs/transfer/selection.json';path.parent.mkdir(parents=True);path.write_text('[]')
            with patch('src.study.cli.PROJECT_ROOT',root),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit) as raised:
                main(['transfer'])
            self.assertEqual(raised.exception.code,2)

    def test_buffer_excludes_training_near_any_heldout_point_only(self):
        train=pd.DataFrame({'listing_id':['a','b','c','d'],'metric_x':[0.,500.,1200.,2000.], 'metric_y':[0.,0.,0.,0.]})
        target=pd.DataFrame({'listing_id':['t1','t2'],'metric_x':[0.,2000.],'metric_y':[0.,0.]})
        original=target.copy(deep=True)
        self.assertEqual(buffer_training(train,target,500).listing_id.tolist(),['b','c'])
        self.assertEqual(len(buffer_training(train,target,1000)),0)
        pd.testing.assert_frame_equal(target,original)

    def test_tail_thresholds_are_training_only_and_test_rows_retained(self):
        X=pd.DataFrame({'x':np.arange(100.)});y=np.arange(100.)
        fit=TrainingTailRegressor(Pipeline([('model',LinearRegression())])).fit(X,y)
        self.assertEqual(fit.training_n_,98)
        np.testing.assert_allclose(fit.thresholds_,[.99,98.01])
        target=pd.DataFrame({'x':[-10000.,10000.]})
        self.assertEqual(len(fit.predict(target)),2)
        np.testing.assert_allclose(fit.thresholds_,[.99,98.01])

    def test_paired_losses_require_identical_keys_and_outcomes(self):
        part=pd.DataFrame([{'model':model,'listing_id':str(i),'operational_group':'a' if i<2 else 'b',
                            'log_price':float(i),'prediction':float(i)+(1 if model=='M0' else .5)}
                           for model in ('M0','ME') for i in range(4)])
        result=paired(part,'ME','M0',100,42,'log_price')
        self.assertAlmostEqual(result['delta_rmse'],-.5)
        altered=part.copy();altered.loc[4,'log_price']=999
        with self.assertRaises(ValueError):paired(altered,'ME','M0',100,42,'log_price')
        with self.assertRaises(ValueError):paired(part.iloc[:-1],'ME','M0',100,42,'log_price')

    def test_immutable_output_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'output.json';write_once(path,b'first')
            with self.assertRaises(FileExistsError):write_once(path,b'second')
            self.assertEqual(path.read_bytes(),b'first')
