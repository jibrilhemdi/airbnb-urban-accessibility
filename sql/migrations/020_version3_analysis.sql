-- Authoritative V3 analytical records and per-run evaluation artifacts.
CREATE TABLE v3_features.area_context (
 analysis_area text PRIMARY KEY, analysis_area_name text NOT NULL,
 population_count integer NOT NULL CHECK(population_count>0), population_period text NOT NULL,
 area_km2 double precision NOT NULL CHECK(area_km2>0),
 log_population_density double precision NOT NULL,
 income_100k_dkk double precision NOT NULL CHECK(income_100k_dkk>0), income_period text NOT NULL,
 income_harmonisation_status text NOT NULL CHECK(income_harmonisation_status IN ('verified','unverified')),
 population_source_file_id bigint NOT NULL REFERENCES meta.source_files,
 income_source_file_id bigint NOT NULL REFERENCES meta.source_files,
 boundary_source_file_id bigint NOT NULL REFERENCES meta.source_files,
 context_version text NOT NULL DEFAULT 'area_context_v3',
 crs_epsg integer NOT NULL CHECK(crs_epsg=25832), provenance jsonb NOT NULL
);
CREATE TABLE v3_spatial.bus_stops (
 bus_stop_key text PRIMARY KEY, source_file_id bigint NOT NULL REFERENCES meta.source_files,
 taxonomy_version text NOT NULL, osm_object_type text NOT NULL, osm_id bigint NOT NULL,
 selection_rule text NOT NULL, tags jsonb NOT NULL, canonical_key text NOT NULL,
 dedup_reason text NOT NULL, geom geometry(Point,4326) NOT NULL,
 geom_25832 geometry(Point,25832) NOT NULL
);
CREATE INDEX bus_stops_metric_gist ON v3_spatial.bus_stops USING gist(geom_25832);
CREATE VIEW v3_spatial.canonical_bus_stops AS
 SELECT * FROM v3_spatial.bus_stops WHERE bus_stop_key=canonical_key;
CREATE TABLE v3_features.bus_accessibility (
 snapshot_date date NOT NULL, listing_id bigint NOT NULL,
 source_file_id bigint NOT NULL REFERENCES meta.source_files,
 taxonomy_version text NOT NULL, nearest_bus_euclidean_key text,
 nearest_bus_euclidean_m double precision, nearest_bus_walking_key text,
 bus_walking_distance_m double precision, nearest_bus_walking_minutes double precision,
 network_id text REFERENCES v3_spatial.walking_networks,
 destination_snap_m double precision, routing_status text,
 euclidean_coverage_complete boolean, walking_coverage_complete boolean,
 walking_speed_kmh double precision NOT NULL DEFAULT 5 CHECK(walking_speed_kmh=5),
 distance_crs_epsg integer NOT NULL DEFAULT 25832 CHECK(distance_crs_epsg=25832),
 PRIMARY KEY(snapshot_date,listing_id),
 FOREIGN KEY(snapshot_date,listing_id) REFERENCES v3_clean.airbnb_listings
);
CREATE TABLE v3_spatial.bus_destination_snaps (
 network_id text NOT NULL REFERENCES v3_spatial.walking_networks,
 bus_stop_key text NOT NULL REFERENCES v3_spatial.bus_stops,
 snapped_node_id bigint NOT NULL, snap_distance_m double precision NOT NULL,
 component_id integer NOT NULL, PRIMARY KEY(network_id,bus_stop_key)
);
CREATE TABLE v3_features.opportunity_variants (
 snapshot_date date NOT NULL, listing_id bigint NOT NULL,
 definition text NOT NULL, category text NOT NULL,
 euclidean_value double precision, walking_value double precision,
 walking_speed_kmh double precision NOT NULL, time_budget_minutes double precision,
 matched_euclidean_radius_m integer, decay_lambda double precision,
 feature_version text NOT NULL DEFAULT 'opportunity_variants_v3',
 crs_epsg integer NOT NULL DEFAULT 25832 CHECK(crs_epsg=25832),
 PRIMARY KEY(snapshot_date,listing_id,definition,category),
 FOREIGN KEY(snapshot_date,listing_id) REFERENCES v3_clean.airbnb_listings
);
CREATE TABLE v3_analysis.runs (
 run_id text PRIMARY KEY, status text NOT NULL, metadata jsonb NOT NULL,
 started_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz
);
CREATE TABLE v3_analysis.dataset_records (
 snapshot_date date NOT NULL, listing_id bigint NOT NULL, analysis_area text NOT NULL,
 dataset_version text NOT NULL, record jsonb NOT NULL,
 PRIMARY KEY(snapshot_date,listing_id),
 FOREIGN KEY(snapshot_date,listing_id) REFERENCES v3_clean.airbnb_listings
);
CREATE TABLE v3_analysis.outer_assignments (
 snapshot_date date NOT NULL, listing_id bigint NOT NULL, scheme text NOT NULL,
 outer_fold text NOT NULL, role text NOT NULL CHECK(role IN ('train','test','excluded')),
 split_version text NOT NULL DEFAULT 'validation_splits_v3',
 PRIMARY KEY(snapshot_date,listing_id,scheme,outer_fold)
);
CREATE TABLE v3_analysis.inner_assignments (
 snapshot_date date NOT NULL, listing_id bigint NOT NULL, scheme text NOT NULL,
 outer_fold text NOT NULL, inner_fold integer NOT NULL,
 PRIMARY KEY(snapshot_date,listing_id,scheme,outer_fold)
);
CREATE TABLE v3_analysis.artifacts (
 run_id text NOT NULL REFERENCES v3_analysis.runs, family text NOT NULL,
 artifact text NOT NULL, record_key text NOT NULL, record jsonb NOT NULL,
 PRIMARY KEY(run_id,family,artifact,record_key)
);
COMMENT ON TABLE v3_analysis.artifacts IS
 'Authoritative per-run OOF losses, held-out SHAP, tuning candidates/selections and inference. Aggregate CSVs are exports.';
