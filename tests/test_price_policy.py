"""The strict source-price policy preserves missing/nonpositive outcomes."""
import unittest
from src.ingestion.price import source_price
class PricePolicyTest(unittest.TestCase):
    def test_missing_outcome_stays_missing(self):
        self.assertEqual(source_price(None),(None,None));self.assertEqual(source_price(''),(None,None))
        self.assertEqual(source_price('$0.00'),(0,None))
    def test_currency_format_does_not_change_numeric_value(self):
        import math
        self.assertEqual(source_price('$1,200.00'),(1200,math.log(1200)))
        self.assertEqual(source_price('$900.00'),(900,math.log(900)))
    def test_invalid_nonempty_source_is_not_inferred(self):
        for value in ['unknown','900 DKK','900','$1,20.00']:
            with self.assertRaises(ValueError):source_price(value)
