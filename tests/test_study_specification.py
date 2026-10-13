import unittest

from src.study.specification import load_design, neutral_token, operational_group


class FinalDesignTests(unittest.TestCase):
    def test_registry_and_directions(self):
        design, cities = load_design()
        self.assertEqual(set(design['models']), {'M0', 'ME', 'MW', 'MEW'})
        self.assertNotIn('income_100k_dkk', design['models']['MEW'])
        self.assertEqual(len(design['transfer_directions']), 6)
        self.assertEqual(cities['stockholm']['operational_count'], 11)

    def test_stockholm_raw_labels_preserved(self):
        raw = 'Rinkeby-Tensta'
        self.assertEqual(operational_group('stockholm', raw), 'Järva')
        self.assertEqual(raw, 'Rinkeby-Tensta')
        self.assertEqual(operational_group('stockholm', 'Spånga-Tensta'), 'Järva')
        self.assertEqual(operational_group('stockholm', 'Norrmalms'), 'Norra innerstaden')
        self.assertEqual(operational_group('stockholm', 'Östermalms'), 'Norra innerstaden')

    def test_exact_labels_only(self):
        self.assertEqual(operational_group('copenhagen', 'Nrrebro'), 'Nørrebro')
        with self.assertRaises(ValueError):
            operational_group('oslo', 'Unknown')
        with self.assertRaises(ValueError):
            operational_group('stockholm', 'Rinkeby-Kista')

    def test_functional_identity(self):
        self.assertEqual(neutral_token('oslo_primary_20261013'), 'oslo_primary_20261013')
        for value in ('research_v4_oslo', 'a07_sample', 'output_v3', '../escape', 'version_final'):
            with self.assertRaises(ValueError):
                neutral_token(value)
