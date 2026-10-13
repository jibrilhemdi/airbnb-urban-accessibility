"""Synthetic boundary diagnostics, never research sources or results."""
import unittest
from shapely.geometry import Polygon, box
from scripts.v4_rinkeby_polygon_check import metrics, target_geometry


class RinkebyPolygonTests(unittest.TestCase):
    def test_overlap_denominators_and_distance_units(self):
        result = metrics(box(0, 0, 1000, 1000), box(500, 0, 1500, 1000))
        self.assertEqual(result['target_overlap_pct'], 50)
        self.assertEqual(result['official_overlap_pct'], 50)
        self.assertAlmostEqual(result['intersection_over_union_pct'], 100 / 3)
        self.assertEqual(result['symmetric_difference_km2'], 1)
        self.assertEqual(result['hausdorff_m'], 500)
        disjoint = metrics(box(0, 0, 1, 1), box(2, 2, 3, 3))
        self.assertEqual(disjoint['intersection_over_union_pct'], 0)

    def test_invalid_empty_geometry_and_nonmetric_crs_refused(self):
        valid = box(0, 0, 1, 1)
        for g in [Polygon(), Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])]:
            with self.assertRaises(ValueError):
                metrics(g, valid)
        with self.assertRaises(ValueError):
            metrics(valid, valid, 'EPSG:4326')

    def test_exact_label_selection_and_crs_ambiguity_refused(self):
        feature = {'type': 'Feature', 'properties': {'neighbourhood': 'Rinkeby-Tensta'},
                   'geometry': {'type': 'Polygon', 'coordinates': [[[17.9, 59.4], [17.91, 59.4],
                               [17.91, 59.41], [17.9, 59.41], [17.9, 59.4]]]}}
        document = {'type': 'FeatureCollection', 'features': [feature]}
        self.assertTrue(target_geometry(document).is_valid)
        for bad in [{**document, 'features': [feature, feature]},
                    {**document, 'features': []}, {**document, 'crs': {'name': 'unknown'}}]:
            with self.assertRaises(ValueError):
                target_geometry(bad)
