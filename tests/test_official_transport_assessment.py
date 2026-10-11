"""Guard the existing-only policy against future records and missing evidence."""

from datetime import date
import os
import pandas as pd
import unittest
from sqlalchemy import text

from src.db.connection import get_engine
from src.pipeline.assess_official_transport import explicit_status, interval_status, json_attributes, normalize_name, normalize_stop_number


class OfficialTransportAssessmentTest(unittest.TestCase):
    def test_source_labels_exclude_future_and_unknown_infrastructure(self):
        cases = [
            ("cykeldata_kk", {"status": "Eksisterende"}, "existing"),
            ("cykeldata_kk", {"status": "Planlagt"}, "planned"),
            ("cykeldata_kk", {"status": "Projekteret"}, "projected"),
            ("cykelrute_total", {"rute_statu": "Anlagt rute"}, "existing"),
            ("cykelrute_total", {"rute_statu": "Planlagt rute"}, "planned"),
            ("cykelrute_total", {"rute_statu": "Projekteret rute"}, "projected"),
            ("cykeldata_kk", {"status": None}, "unknown"),
            ("cykeldata_kk", {"status": "new undocumented label"}, "unknown"),
            ("vejmidte_geodk_labels", {}, "unknown"),
        ]
        for dataset, attributes, expected in cases:
            with self.subTest(dataset=dataset, attributes=attributes):
                self.assertEqual(explicit_status(dataset, attributes)[0], expected)

    def test_operator_interval_must_cover_assessment_date(self):
        day = date(2026, 10, 4)
        cases = [(20261004, 20261004, "existing"), (20261005, 21001231, "planned"),
                 (20120412, 20261003, "unknown"), (20261005, 20261001, "unknown"),
                 (None, 21001231, "unknown"), (20260230, 21001231, "unknown")]
        for start, end, expected in cases:
            with self.subTest(start=start, end=end):
                self.assertEqual(interval_status({"ExistsFrom": start, "ExistsUpTo": end}, day)[0], expected)
        self.assertEqual(interval_status({}, day)[0], "unknown")

    def test_name_normalization_does_not_invent_airport_alias(self):
        self.assertEqual(normalize_name(" DR Byen (Universitetet) "), normalize_name("DR Byen"))
        self.assertNotEqual(normalize_name("Lufthavnen"), normalize_name("Københavns Lufthavn"))
        self.assertEqual(normalize_name(None), "")

    def test_stop_identity_preserves_missing_and_string_identifiers(self):
        self.assertIsNone(normalize_stop_number(None))
        self.assertIsNone(normalize_stop_number(float("nan")))
        self.assertEqual(normalize_stop_number(123.0), "123")
        self.assertEqual(normalize_stop_number("00123"), "00123")

    def test_source_date_serialization_preserves_dates_and_missing_values(self):
        result = json_attributes(pd.Series({"created": pd.Timestamp("2024-02-03"),
                                           "missing": pd.NaT, "geometry": None}))
        self.assertEqual(result, {"created": "2024-02-03T00:00:00", "missing": None})


@unittest.skipUnless(os.environ.get("THESIS_DB_TEST") == "1", "Set THESIS_DB_TEST=1 for local PostGIS checks")
class LiveOfficialTransportAssessmentTest(unittest.TestCase):
    def test_existing_view_contains_exactly_eligible_original_records(self):
        engine = get_engine()
        try:
            with engine.connect() as conn:
                assessment = conn.scalar(text("SELECT assessment_id FROM meta.official_transport_assessments WHERE results->>'complete'='true' ORDER BY assessed_at DESC LIMIT 1"))
                self.assertIsNotNone(assessment)
                differences = conn.scalar(text("""WITH eligible AS (
                    SELECT f.source_file_id,f.source_row FROM raw.official_transport_source_features f
                    JOIN meta.official_transport_feature_status s USING(source_file_id,source_row)
                    WHERE s.assessment_id=:assessment AND s.existence_status='existing'
                      AND f.dataset NOT IN ('movia_operator_bus_reference','metro_operator_reference')),
                    actual AS (SELECT source_file_id,source_row FROM spatial.official_transport_existing_candidates),
                    differences AS ((SELECT * FROM eligible EXCEPT SELECT * FROM actual)
                                    UNION ALL (SELECT * FROM actual EXCEPT SELECT * FROM eligible))
                    SELECT count(*) FROM differences"""), {"assessment": assessment})
                self.assertEqual(differences, 0)
                prohibited = conn.scalar(text("""SELECT count(*) FROM spatial.official_transport_existing_candidates
                    WHERE existence_status!='existing' OR attributes->>'status' IN ('Planlagt','Projekteret')
                      OR attributes->>'rute_statu' IN ('Planlagt rute','Projekteret rute')"""))
                self.assertEqual(prohibited, 0)
        finally:
            engine.dispose()

    def test_original_road_z_is_preserved_and_metric_geometry_is_planar(self):
        engine = get_engine()
        try:
            with engine.connect() as conn:
                count, invalid = conn.execute(text("""SELECT count(*),count(*) FILTER (
                    WHERE ST_NDims(geom_source)!=3 OR ST_SRID(geom_source)!=4326
                      OR ST_NDims(geom_25832)!=2 OR ST_SRID(geom_25832)!=25832)
                    FROM raw.official_transport_source_features WHERE dataset='vejmidte_geodk_labels'""")).one()
                self.assertGreater(count, 0)
                self.assertEqual(invalid, 0)
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
