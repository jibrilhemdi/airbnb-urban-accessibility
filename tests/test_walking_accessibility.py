"""walking accessibility foot-routing, immutable destination and PostGIS QA."""

import os
import unittest
import csv
from importlib.util import find_spec

import networkx as nx
import numpy as np
from sqlalchemy import text

from src.db.connection import get_engine
from src.db.migrations import migrate
from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.output_paths import output_file
from src.pipeline.acquire_osm import PBF_NAME, existing_archive
HAS_ROUTING_DEPS = find_spec("osmium") is not None and find_spec("pyproj") is not None
if HAS_ROUTING_DEPS:
    from src.spatial.walking_network import METRES_PER_MINUTE, RADII_M, walking_directions
    from src.spatial.walking_routing import grouped_opportunities, station_distance_labels


@unittest.skipUnless(HAS_ROUTING_DEPS, "Install requirements.txt for walking accessibility routing tests")
class RoutingRulesTest(unittest.TestCase):
    def test_constant_speed_and_access(self) -> None:
        np.testing.assert_allclose(RADII_M, (5000/6, 1250, 5000/3))
        self.assertAlmostEqual(METRES_PER_MINUTE, 5000/60)
        self.assertEqual(walking_directions({"highway": "footway"}), (True, True))
        self.assertEqual(walking_directions({"highway": "residential", "oneway": "yes"}), (True, True))
        self.assertEqual(walking_directions({"highway": "steps", "oneway:foot": "yes"}), (True, False))
        self.assertEqual(walking_directions({"highway": "footway", "foot": "no"}), (False, False))
        self.assertEqual(walking_directions({"highway": "service", "access": "private"}), (False, False))
        self.assertEqual(walking_directions({"highway": "service", "access": "private", "foot": "yes"}),
                         (True, True))
        self.assertEqual(walking_directions({"highway": "cycleway"}), (False, False))
        self.assertEqual(walking_directions({"highway": "cycleway", "foot": "designated"}), (True, True))
        self.assertEqual(walking_directions({"highway": "motorway", "foot": "yes"}), (False, False))

    def test_station_and_poi_connector_distances(self) -> None:
        graph = nx.DiGraph()
        graph.add_edge(1, 2, length_m=300)
        graph.add_edge(2, 1, length_m=300)
        graph.add_edge(2, 3, length_m=600)
        graph.add_edge(3, 2, length_m=600)
        graph.add_edge(3, 4, length_m=100)
        station_distance, station_key = station_distance_labels(graph, [
            {"snapped_node_id": 3, "snap_distance_m": 50, "destination_key": "station-a"},
            {"snapped_node_id": 4, "snap_distance_m": 900, "destination_key": "station-b"},
        ])
        self.assertEqual(station_distance[1], 950)
        self.assertEqual(station_key[1], "station-a")
        listings = [{"listing_id": 10, "snapped_node_id": 1, "snap_distance_m": 20},
                    {"listing_id": 11, "snapped_node_id": 1, "snap_distance_m": 550}]
        pois = [
            {"snapped_node_id": 2, "category": "food_social", "snap_distance_m": 10},
            {"snapped_node_id": 3, "category": "cultural_tourist", "snap_distance_m": 20},
            {"snapped_node_id": 4, "category": "food_social", "snap_distance_m": 700},
        ]
        counts, bench = grouped_opportunities(graph, listings, pois)
        self.assertEqual(bench["unique_origin_nodes"], 1)
        self.assertEqual(counts[10][("food_social", RADII_M[0])], 1)
        self.assertEqual(counts[11][("food_social", RADII_M[0])], 0)
        self.assertEqual(counts[10][("cultural_tourist", RADII_M[1])], 1)
        self.assertEqual(counts[10][("food_social", RADII_M[2])], 1)


@unittest.skipUnless(HAS_ROUTING_DEPS and os.environ.get("THESIS_V3_INTEGRATION") == "1",
                     "Install requirements.txt and set THESIS_V3_INTEGRATION=1 after walking_accessibility-run")
class LiveWalkingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = get_engine()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    def test_network_and_migration(self) -> None:
        self.assertEqual(migrate(self.engine), [])
        with self.engine.connect() as conn:
            network = conn.execute(text(
                "SELECT network_id,node_count,source_segment_count,directed_arc_count,weak_component_count "
                "FROM v3_spatial.walking_networks"
            )).one()
            self.assertGreater(network.node_count, 100000)
            self.assertGreater(network.source_segment_count, 100000)
            self.assertGreater(network.weak_component_count, 1)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.walking_nodes WHERE network_id=:id"
            ), {"id": network.network_id}), network.node_count)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.walking_edges WHERE network_id=:id"
            ), {"id": network.network_id}), network.source_segment_count)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_spatial.walking_nodes WHERE ST_SRID(geom_25832)<>25832 "
                "OR NOT ST_IsValid(geom_25832)"
            )), 0)
            source = conn.execute(text(
                "SELECT trim(n.source_sha256),trim(s.file_hash_sha256),s.relative_path "
                "FROM v3_spatial.walking_networks n JOIN meta.source_files s USING(source_file_id)"
            )).one()
            self.assertEqual(source[0], source[1])
            self.assertEqual(source[0], sha256_file(existing_archive() / PBF_NAME))
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM meta.import_runs WHERE target_table LIKE "
                "'v3_spatial.walking_networks:%' AND status='success'"
            )), 1)

    def test_same_canonical_destinations_and_listing_cardinality(self) -> None:
        with self.engine.connect() as conn:
            qa = conn.execute(text(
                "SELECT (SELECT count(*) FROM v3_spatial.walking_destination_snaps) AS snaps,"
                "(SELECT count(*) FROM v3_spatial.osm_pois)+(SELECT count(*) FROM v3_spatial.transit_stations) AS canonical,"
                "(SELECT count(*) FROM v3_features.walking_listing_snaps) AS listing_snaps,"
                "(SELECT count(*) FROM v3_features.walking_accessibility) AS features"
            )).one()
            source_n = conn.scalar(text('SELECT count(*) FROM v3_clean.airbnb_listings'))
            self.assertGreater(qa.canonical, 0)
            self.assertEqual(qa.snaps, qa.canonical)
            self.assertEqual((qa.listing_snaps, qa.features), (source_n, source_n))
            missing = conn.scalar(text(
                "SELECT count(*) FROM (SELECT destination_key FROM v3_spatial.osm_pois "
                "UNION ALL SELECT station_key FROM v3_spatial.transit_stations) d "
                "LEFT JOIN v3_spatial.walking_destination_snaps s USING(destination_key) "
                "WHERE s.destination_key IS NULL"
            ))
            self.assertEqual(missing, 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_features.walking_accessibility f LEFT JOIN v3_clean.airbnb_listings l "
                "USING(snapshot_date,listing_id) WHERE l.listing_id IS NULL"
            )), 0)

    def test_network_bounds_and_flags(self) -> None:
        with self.engine.connect() as conn:
            # Recount at exact (unrounded) network budgets. The requested rounded
            # Euclidean columns differ by a third of a metre at 10 and 20 minutes.
            for category in ('food_social', 'cultural_tourist'):
                for minutes in (10, 15, 20):
                    bad = conn.scalar(text(
                        f'SELECT count(*) FROM v3_features.walking_accessibility w '
                        'JOIN v3_clean.airbnb_listings l USING(snapshot_date,listing_id) '
                        f'WHERE w.{category}_w_{minutes} > (SELECT count(*) FROM v3_spatial.osm_pois p '
                        'WHERE p.category=:category AND ST_DWithin(p.geom_25832,l.geom_25832,:radius))'
                    ), {'category':category,'radius':minutes*METRES_PER_MINUTE})
                    self.assertEqual(bad, 0)
            self.assertEqual(conn.scalar(text(
                'SELECT count(*) FROM v3_features.walking_accessibility w '
                'JOIN v3_features.euclidean_accessibility e USING(snapshot_date,listing_id) '
                'WHERE w.nearest_station_network_distance_m+0.1<e.nearest_station_distance_m'
            )),0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_features.walking_accessibility WHERE routing_status='ok' "
                "AND abs(nearest_station_walking_minutes*:speed-nearest_station_network_distance_m)>0.000001"
            ), {'speed':METRES_PER_MINUTE}), 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_features.walking_accessibility WHERE "
                "food_social_w_10>food_social_w_15 OR food_social_w_15>food_social_w_20 "
                "OR cultural_tourist_w_10>cultural_tourist_w_15 "
                "OR cultural_tourist_w_15>cultural_tourist_w_20"
            )), 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_features.walking_accessibility WHERE "
                "routing_status='no_reachable_station' AND nearest_station_walking_minutes IS NOT NULL"
            )), 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_features.walking_accessibility WHERE "
                "nearest_station_coverage_complete IS FALSE"
            )), 0)
            self.assertEqual(conn.scalar(text(
                "SELECT count(*) FROM v3_features.walking_listing_snaps WHERE "
                "large_snap<>(snap_distance_m>100) OR severe_snap<>(snap_distance_m>250)"
            )), 0)

    def test_public_exports_are_aggregated(self) -> None:
        for filename, expected in (("feature_summary.csv", 8),
                                   ("euclidean_network_comparison.csv", 6),
                                   ("snap_diagnostics.csv", 3),
                                   ("area_comparison.csv", None),
                                   ("source_coverage.csv", 2)):
            with output_file("tables", "walking_accessibility", filename).open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            if expected is not None:
                self.assertEqual(len(rows), expected)
            else:
                with self.engine.connect() as conn:
                    areas=set(conn.execute(text('SELECT area_id FROM v3_spatial.analysis_areas')).scalars())
                self.assertEqual({r['analysis_area'] for r in rows}-{'unassigned'}, areas)
            self.assertFalse({"listing_id", "host_name", "latitude", "longitude", "name"}
                             .intersection(rows[0]))


if __name__ == "__main__":
    unittest.main()
