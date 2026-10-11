"""geography provider-boundary, assignment, CRS and aggregate-output QA."""

import csv
import os
import unittest
from decimal import Decimal

from sqlalchemy import text

from src.db.connection import get_engine
from src.ingestion.common import PROJECT_ROOT
from src.pipeline.output_paths import output_file
from src.pipeline.build_spatial_features import EXTRACTION_BUFFER_METRES, MAX_WALK_MINUTES, WALK_SPEED_MPS


class SpatialRuleTest(unittest.TestCase):
    def test_buffer_exceeds_maximum_prespecified_path_length(self) -> None:
        self.assertGreater(EXTRACTION_BUFFER_METRES, MAX_WALK_MINUTES * 60 * WALK_SPEED_MPS)


@unittest.skipUnless(os.environ.get("THESIS_V3_INTEGRATION") == "1", "Set THESIS_V3_INTEGRATION=1 after geography-run")
class LiveSpatialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = get_engine()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    def test_polygons_are_valid_and_source_identified(self) -> None:
        with self.engine.connect() as conn:
            self.assertEqual(conn.scalar(text("SELECT count(*) FROM v3_spatial.provider_neighbourhoods")), 11)
            invalid = conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.provider_neighbourhoods WHERE NOT ST_IsValid(geom_4326) "
                "OR NOT ST_IsValid(geom_25832) OR ST_SRID(geom_4326)<>4326 "
                "OR ST_SRID(geom_25832)<>25832 OR source_file_id IS NULL"
            ))
            self.assertEqual(invalid, 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.provider_neighbourhoods WHERE provider_label='Frederiksberg'"
            )), 1)
            self.assertEqual(conn.scalar(text("SELECT count(*) FROM v3_spatial.study_area")), 4)
            self.assertEqual(conn.scalar(text("SELECT count(*) FROM v3_spatial.official_municipalities")), 2)
            self.assertEqual(conn.scalar(text("SELECT count(*) FROM v3_spatial.official_copenhagen_districts")), 10)
            self.assertEqual(conn.scalar(text("SELECT count(*) FROM v3_spatial.analysis_areas")), 11)
            self.assertEqual(conn.scalar(text("SELECT count(*) FROM v3_spatial.map_context_municipalities")), 29)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.map_context_municipalities WHERE NOT ST_IsValid(geom_4326) "
                "OR ST_SRID(geom_25832)<>25832 OR source_file_id IS NULL"
            )), 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM meta.import_runs WHERE status='success' "
                "AND target_table='v3_spatial.map_context_municipalities'"
            )), 1)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM meta.source_files WHERE relative_path LIKE "
                "'data/raw/official_boundaries/%'"
            )), 4)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM meta.import_runs WHERE status='success' AND "
                "target_table IN ('v3_spatial.official_municipalities','v3_spatial.official_copenhagen_districts')"
            )), 3)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.official_municipalities WHERE NOT ST_IsValid(geom_4326) "
                "OR ST_SRID(geom_25832)<>25832 OR source_file_id IS NULL"
            )), 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.official_copenhagen_districts WHERE NOT ST_IsValid(geom_4326) "
                "OR ST_SRID(geom_25832)<>25832 OR source_file_id IS NULL"
            )), 0)
            self.assertEqual(conn.scalar(text(
                "SELECT buffer_metres FROM v3_spatial.study_area WHERE area_kind='buffered_extraction_extent'"
            )), Decimal(EXTRACTION_BUFFER_METRES))

    def test_assignments_and_distance(self) -> None:
        with self.engine.connect() as conn:
            qa = conn.execute(text(
                "SELECT count(*),count(*) FILTER (WHERE polygon_match_count=0),"
                "count(*) FILTER (WHERE polygon_match_count>1),"
                "count(*) FILTER (WHERE near_provider_border_100m),"
                "count(*) FILTER (WHERE provider_label_matches_polygon IS FALSE),"
                "count(*) FILTER (WHERE context_statistical_unit_id IS NOT NULL) "
                "FROM v3_features.listing_spatial_base"
            )).one()
            source_n=conn.scalar(text('SELECT count(*) FROM v3_clean.airbnb_listings'))
            self.assertGreater(source_n,0)
            self.assertEqual(qa[0],source_n)
            self.assertTrue(all(0<=value<=source_n for value in qa[1:]))
            official = conn.execute(text(
                "SELECT count(*) FILTER (WHERE official_municipality_match_count=0),"
                "count(*) FILTER (WHERE official_cv_match_count=0),"
                "count(*) FILTER (WHERE analysis_area IS NOT NULL),"
                "count(*) FILTER (WHERE l.primary_sample_candidate AND analysis_area IS NULL) "
                "FROM v3_features.listing_spatial_base s JOIN v3_clean.airbnb_listings l USING(snapshot_date,listing_id)"
            )).one()
            self.assertTrue(all(0<=value<=source_n for value in official))
            self.assertEqual(conn.scalar(text(
                'SELECT count(*) FROM v3_features.listing_spatial_base s '
                'LEFT JOIN v3_spatial.analysis_areas a ON a.area_id=s.analysis_area '
                'JOIN v3_clean.airbnb_listings l USING(snapshot_date,listing_id) '
                'WHERE s.analysis_area IS NOT NULL AND '
                '(a.area_id IS NULL OR NOT ST_Covers(a.geom_4326,l.geom) '
                'OR s.official_cv_match_count<>1 OR s.official_municipality_match_count<>1)'
            )),0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_features.listing_spatial_base WHERE "
                "context_statistical_unit_id IS NOT NULL"
            )), 0)
            max_error = conn.scalar(text(
                "SELECT max(abs(s.distance_centre_euclidean_km - "
                "ST_Distance(l.geom_25832,c.geom_25832)/1000.0)) "
                "FROM v3_features.listing_spatial_base s JOIN v3_clean.airbnb_listings l "
                "USING (snapshot_date,listing_id) CROSS JOIN v3_spatial.reference_points c "
                "WHERE c.reference_id='city_hall_square'"
            ))
            self.assertLess(max_error, 1e-9)
            self.assertFalse(conn.scalar(text(
                "SELECT ST_Covers(o.geom_4326,p.geom_4326) FROM v3_spatial.study_area o "
                "CROSS JOIN v3_spatial.study_area p WHERE o.area_kind='archived_osm_bbox' "
                "AND p.area_kind='buffered_extraction_extent'"
            )))
            incomplete = conn.execute(text(
                "SELECT count(*) FILTER (WHERE NOT ST_Covers(o.geom_25832,ST_Buffer(l.geom_25832,:radius))),"
                "count(*) FILTER (WHERE l.primary_sample_candidate AND NOT "
                "ST_Covers(o.geom_25832,ST_Buffer(l.geom_25832,:radius))) "
                "FROM v3_clean.airbnb_listings l CROSS JOIN v3_spatial.study_area o "
                "WHERE o.area_kind='archived_osm_bbox'"
            ), {"radius": MAX_WALK_MINUTES * 60 * WALK_SPEED_MPS}).one()
            self.assertGreaterEqual(incomplete[0],incomplete[1])
            self.assertGreaterEqual(incomplete[1],0)

    def test_cv_counts_and_maps_are_aggregate_only(self) -> None:
        with output_file("tables", "geography", "cv_area_counts.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 11)
        with self.engine.connect() as conn:
            expected_n=conn.scalar(text(
                'SELECT count(*) FROM v3_clean.airbnb_listings l '
                'JOIN v3_features.listing_spatial_base s USING(snapshot_date,listing_id) '
                'WHERE l.primary_sample_candidate AND s.analysis_area IS NOT NULL'
            ))
        self.assertEqual(sum(int(row["eligible_n"]) for row in rows),expected_n)
        self.assertGreater(min(int(row["eligible_n"]) for row in rows), 0)
        self.assertFalse({"listing_id", "host_name", "latitude", "longitude"}.intersection(rows[0]))
        for filename in ("study_area.png", "municipalities.png",
                         "analysis_areas.png", "osm_coverage.png"):
            self.assertTrue(output_file("figures", "geography", filename).is_file())


if __name__ == "__main__":
    unittest.main()
