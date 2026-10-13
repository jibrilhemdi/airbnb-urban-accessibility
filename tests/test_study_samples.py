import math
import unittest
from src.study.samples import reference_sample


class ReferenceTests(unittest.TestCase):
    def row(self,key,price,inside=True,eligible=True):
        return {'listing_id':key,'price_nightly':price,'log_price':math.log(price) if price and price>0 else None,
                'inside_boundary':inside,'dwelling_eligible':eligible,'positive_price':bool(price and price>0)}

    def test_reference_is_before_feature_and_model_filters(self):
        rows=[self.row('a',100),self.row('b',400),self.row('missing',None),self.row('outside',800,False)]
        summary,records=reference_sample(rows)
        self.assertEqual(summary['reference_n'],2)
        self.assertAlmostEqual(summary['geometric_mean_price'],200)
        self.assertEqual([r['listing_id'] for r in records],['a','b'])
        self.assertTrue(summary['before_accessibility_exclusions'])

    def test_imputed_or_changed_log_outcome_refused(self):
        row=self.row('a',100);row['log_price']=0
        with self.assertRaises(ValueError):reference_sample([row])
        with self.assertRaises(ValueError):reference_sample([self.row('missing',None)])
