import unittest
import warnings
import numpy as np
import pandas as pd
from src.study.validation import support,inner_splits
from src.study.modeling import transfer,fit_source,metrics
from src.study.specification import load_design


class ValidationTransferTests(unittest.TestCase):
    def test_fourteen_fails_fifteen_passes_and_train_floor(self):
        with self.assertRaises(ValueError):support(['a']*14+['b']*500,{'a','b'})
        support(['a']*15+['b']*500+['c']*500,{'a','b','c'})
        with self.assertRaises(ValueError):support(['a']*15+['b']*499,{'a','b'})
        with self.assertRaises(ValueError):support(['a']*1000,{'a','missing'})

    def fixture(self,city,n=80):
        design,_=load_design();rng=np.random.default_rng(32)
        frame=pd.DataFrame({f:rng.normal(size=n) for f in design['models']['MEW'] if f!='property_type'})
        frame['city']=city;frame['property_type']='Entire rental unit';frame['listing_id']=[str(i) for i in range(n)]
        frame['metric_x']=np.arange(n)*1000;frame['metric_y']=np.arange(n)%7*1000
        frame['log_price']=5+frame.accommodates*.5+rng.normal(size=n)*.01
        return frame

    def test_source_only_pipeline_target_price_and_category_isolation(self):
        source=self.fixture('oslo');target=self.fixture('stockholm');target['property_type']='Entire villa'
        source.loc[0,'bedrooms']=np.nan;target.loc[0,'bedrooms']=np.nan
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',UserWarning)
            a=transfer(source,target,'oslo','stockholm','M0','OLS',5.,5.)
            altered=target.copy();altered['log_price']+=1000;altered['bedrooms']=target.bedrooms
            b=transfer(source,altered,'oslo','stockholm','M0','OLS',5.,999.)
        np.testing.assert_array_equal(a['prediction'],b['prediction'])
        np.testing.assert_array_equal(a['fit'].named_steps['prep'].named_transformers_['numeric'].statistics_,
                                      b['fit'].named_steps['prep'].named_transformers_['numeric'].statistics_)
        self.assertEqual(a['fit'].named_steps['prep'].named_transformers_['category'].categories_[0].tolist(),['Entire rental unit'])
        self.assertFalse(a['target_fit'])

    def test_inner_groups_are_spatial_and_outcome_blind(self):
        frame=self.fixture('oslo');a=inner_splits(frame);frame.log_price+=10000;b=inner_splits(frame)
        for (tr,te),(tr2,te2) in zip(a,b,strict=True):
            self.assertFalse(set(tr)&set(te));np.testing.assert_array_equal(tr,tr2);np.testing.assert_array_equal(te,te2)

    def test_all_missing_training_predictor_and_mixed_cities_refused(self):
        frame=self.fixture('oslo');frame['bedrooms']=np.nan
        with self.assertRaises(ValueError):fit_source(frame,'M0','OLS',frame.log_price)
        frame=self.fixture('oslo');frame.loc[0,'city']='stockholm'
        with self.assertRaises(ValueError):fit_source(frame,'M0','OLS',frame.log_price)

    def test_metrics_recalculation(self):
        value=metrics([0,2],[1,1]);self.assertEqual(value['rmse'],1);self.assertEqual(value['mae'],1)
        self.assertIsNone(value['pearson'])
