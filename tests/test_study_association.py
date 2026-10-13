import copy
import unittest
import numpy as np
import pandas as pd
from src.study.association import permitted,qualify
from src.study.specification import load_design


class AssociationAmendmentTests(unittest.TestCase):
    def test_uniform_strict_upper_gate(self):
        design,_=load_design()
        self.assertEqual(design['association_missing_limit'],.10)
        for fraction in (.099,.10,.058917835671342685):
            self.assertTrue(permitted(fraction,design['association_missing_limit']))
        self.assertFalse(permitted(.100000001,design['association_missing_limit']))
        for fraction in (np.nan,-.1,1.1):
            with self.assertRaises(ValueError):permitted(fraction,.10)

    def test_union_complete_cases_unchanged_without_imputation(self):
        design={'models':{'MEW':['bedrooms','walking','property_type']},'association_missing_limit':.10}
        prediction=pd.DataFrame({'listing_id':['a','b','c'],'bedrooms':[1.,np.nan,2.],
                                 'walking':[4.,5.,np.nan],'property_type':['apt']*3,'log_price':[3.,4.,5.]})
        original=prediction.copy(deep=True)
        expected=prediction.iloc[[0]].copy()
        complete,status=qualify(prediction,expected,design)
        pd.testing.assert_frame_equal(prediction,original)
        self.assertEqual(complete.listing_id.tolist(),['a'])
        self.assertFalse(status['inferential_imputation'])
        self.assertFalse(status['outcome_imputed'])
        altered=expected.copy();altered.loc[0,'bedrooms']=999.
        with self.assertRaises(ValueError):qualify(prediction,altered,design)

    def test_gate_does_not_select_features_or_predictive_preprocessing(self):
        design,_=load_design()
        self.assertEqual(design['models']['MEW'],design['blocks']['X']+design['blocks']['E']+design['blocks']['W'])
        self.assertFalse(any('income' in f or 'housing' in f for f in design['models']['MEW']))
        from pathlib import Path
        from src.ingestion.common import PROJECT_ROOT,sha256_file
        previous=PROJECT_ROOT/'archive/before_association_amendment/src/study/modeling.py'
        self.assertEqual(sha256_file(previous),sha256_file(PROJECT_ROOT/'src/study/modeling.py'))
