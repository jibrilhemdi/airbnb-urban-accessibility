-- Isolated Version 3 analytical namespace. Historical records are retained.

CREATE SCHEMA IF NOT EXISTS v3_raw;

CREATE SCHEMA IF NOT EXISTS v3_clean;

CREATE SCHEMA IF NOT EXISTS v3_spatial;

CREATE SCHEMA IF NOT EXISTS v3_features;

CREATE SCHEMA IF NOT EXISTS v3_analysis;

CREATE TABLE IF NOT EXISTS v3_clean.airbnb_listings (
    snapshot_date date NOT NULL,
    listing_id bigint NOT NULL,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    last_scraped date,
    neighbourhood_cleansed text,
    room_type text,
    property_type text,
    latitude double precision,
    longitude double precision,
    geom geometry(Point, 4326),
    geom_25832 geometry(Point, 25832),
    price_raw text,
    price_nightly numeric(14, 2),
    log_price double precision,
    accommodates integer,
    bedrooms numeric,
    bathrooms numeric,
    bathrooms_text text,
    amenities_raw text,
    minimum_nights integer,
    instant_bookable text,
    host_is_superhost text,
    host_listings_count integer,
    calculated_host_listings_count integer,
    number_of_reviews integer,
    number_of_reviews_ltm integer,
    review_scores_rating numeric,
    in_study_area boolean NOT NULL,
    entire_home_apt boolean NOT NULL,
    conventional_residential boolean NOT NULL,
    valid_price boolean NOT NULL,
    valid_coordinates boolean NOT NULL,
    primary_sample_candidate boolean NOT NULL,
    cleaned_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (snapshot_date, listing_id),
    CHECK (NOT primary_sample_candidate OR
           (in_study_area AND entire_home_apt AND conventional_residential
            AND valid_price AND valid_coordinates))
);

CREATE INDEX IF NOT EXISTS airbnb_listings_geom_gist
    ON v3_clean.airbnb_listings USING gist (geom);
CREATE INDEX IF NOT EXISTS airbnb_listings_geom_25832_gist
    ON v3_clean.airbnb_listings USING gist (geom_25832);
CREATE INDEX IF NOT EXISTS airbnb_listings_primary_candidate_idx
    ON v3_clean.airbnb_listings (snapshot_date, primary_sample_candidate);

CREATE OR REPLACE VIEW v3_analysis.airbnb_primary_sample_candidates AS
SELECT * FROM v3_clean.airbnb_listings WHERE primary_sample_candidate;


-- Context observations retain their own geography, period, concept and source.
-- Municipality measures are never stored as neighbourhood attributes.
CREATE TABLE IF NOT EXISTS v3_clean.municipality_context_measures (
    municipality_code text NOT NULL CHECK (municipality_code IN ('101', '147')),
    municipality_name text NOT NULL,
    measure_code text NOT NULL,
    reference_period text NOT NULL,
    value numeric NOT NULL,
    unit text NOT NULL,
    population_definition text NOT NULL,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    cleaned_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (municipality_code, measure_code, reference_period)
);

CREATE TABLE IF NOT EXISTS v3_clean.copenhagen_district_context_measures (
    district_code text NOT NULL CHECK (district_code ~ '^10(0[1-9]|10)$'),
    district_name text NOT NULL,
    measure_code text NOT NULL,
    reference_period text NOT NULL,
    value numeric NOT NULL,
    unit text NOT NULL,
    population_definition text NOT NULL,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    cleaned_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (district_code, measure_code, reference_period)
);


-- Provider polygons are candidate geography, not official municipality/district boundaries.
CREATE TABLE IF NOT EXISTS v3_spatial.provider_neighbourhoods (
    area_id text PRIMARY KEY,
    provider_label text NOT NULL UNIQUE,
    municipality_proxy text NOT NULL CHECK (municipality_proxy IN ('Copenhagen', 'Frederiksberg')),
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    source_crs_text text NOT NULL,
    source_crs_basis text NOT NULL,
    geom_source geometry(MultiPolygon, 4326) NOT NULL,
    geom_4326 geometry(MultiPolygon, 4326) NOT NULL,
    geom_25832 geometry(MultiPolygon, 25832) NOT NULL,
    boundary_25832 geometry(MultiLineString, 25832) NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS provider_neighbourhoods_geom_4326_gist
    ON v3_spatial.provider_neighbourhoods USING gist (geom_4326);
CREATE INDEX IF NOT EXISTS provider_neighbourhoods_geom_25832_gist
    ON v3_spatial.provider_neighbourhoods USING gist (geom_25832);
CREATE INDEX IF NOT EXISTS provider_neighbourhoods_boundary_25832_gist
    ON v3_spatial.provider_neighbourhoods USING gist (boundary_25832);

CREATE TABLE IF NOT EXISTS v3_spatial.study_area (
    area_kind text PRIMARY KEY,
    description text NOT NULL,
    source_file_id bigint REFERENCES meta.source_files(source_file_id),
    buffer_metres numeric,
    crs_for_operations integer NOT NULL DEFAULT 25832 CHECK (crs_for_operations = 25832),
    geom_4326 geometry(MultiPolygon, 4326) NOT NULL,
    geom_25832 geometry(MultiPolygon, 25832) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS study_area_geom_4326_gist ON v3_spatial.study_area USING gist (geom_4326);
CREATE INDEX IF NOT EXISTS study_area_geom_25832_gist ON v3_spatial.study_area USING gist (geom_25832);

CREATE TABLE IF NOT EXISTS v3_spatial.reference_points (
    reference_id text PRIMARY KEY,
    description text NOT NULL,
    source_url text NOT NULL,
    source_accessed_on date NOT NULL,
    source_crs_text text NOT NULL,
    geom_4326 geometry(Point, 4326) NOT NULL,
    geom_25832 geometry(Point, 25832) NOT NULL
);
CREATE INDEX IF NOT EXISTS reference_points_geom_25832_gist
    ON v3_spatial.reference_points USING gist (geom_25832);

CREATE TABLE IF NOT EXISTS v3_features.listing_spatial_base (
    snapshot_date date NOT NULL,
    listing_id bigint NOT NULL,
    municipality_proxy text,
    cv_area_id text REFERENCES v3_spatial.provider_neighbourhoods(area_id),
    provider_neighbourhood text,
    polygon_match_count integer NOT NULL CHECK (polygon_match_count >= 0),
    provider_label_matches_polygon boolean,
    assignment_status text NOT NULL,
    context_statistical_unit_id text,
    context_assignment_status text NOT NULL,
    near_provider_border_100m boolean NOT NULL,
    distance_centre_euclidean_km double precision NOT NULL CHECK (distance_centre_euclidean_km >= 0),
    distance_crs_epsg integer NOT NULL DEFAULT 25832 CHECK (distance_crs_epsg = 25832),
    built_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (snapshot_date, listing_id),
    FOREIGN KEY (snapshot_date, listing_id) REFERENCES v3_clean.airbnb_listings(snapshot_date, listing_id),
    CHECK (context_statistical_unit_id IS NULL OR context_assignment_status = 'verified')
);
CREATE INDEX IF NOT EXISTS listing_spatial_base_cv_area_idx
    ON v3_features.listing_spatial_base (cv_area_id, snapshot_date);


-- Official municipality boundaries: DAWA/DAGI; district boundaries: Copenhagen municipal WFS.
CREATE TABLE IF NOT EXISTS v3_spatial.official_municipalities (
    municipality_code text PRIMARY KEY,
    municipality_name text NOT NULL,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    source_crs_epsg integer NOT NULL CHECK (source_crs_epsg = 4326),
    source_geo_changed_at timestamptz,
    geom_source geometry(MultiPolygon,4326) NOT NULL,
    geom_4326 geometry(MultiPolygon,4326) NOT NULL,
    geom_25832 geometry(MultiPolygon,25832) NOT NULL,
    boundary_25832 geometry(MultiLineString,25832) NOT NULL
);
CREATE INDEX IF NOT EXISTS official_municipalities_geom_gist ON v3_spatial.official_municipalities USING gist(geom_4326);
CREATE INDEX IF NOT EXISTS official_municipalities_metric_gist ON v3_spatial.official_municipalities USING gist(geom_25832);

CREATE TABLE IF NOT EXISTS v3_spatial.official_copenhagen_districts (
    district_number integer PRIMARY KEY CHECK (district_number BETWEEN 1 AND 10),
    district_name text NOT NULL UNIQUE,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    source_crs_epsg integer NOT NULL CHECK (source_crs_epsg = 4326),
    geom_source geometry(MultiPolygon,4326) NOT NULL,
    geom_4326 geometry(MultiPolygon,4326) NOT NULL,
    geom_25832 geometry(MultiPolygon,25832) NOT NULL,
    boundary_25832 geometry(MultiLineString,25832) NOT NULL
);
CREATE INDEX IF NOT EXISTS official_districts_geom_gist ON v3_spatial.official_copenhagen_districts USING gist(geom_4326);
CREATE INDEX IF NOT EXISTS official_districts_metric_gist ON v3_spatial.official_copenhagen_districts USING gist(geom_25832);

-- Canonical candidate CV units: ten official Copenhagen districts plus Frederiksberg municipality.
CREATE OR REPLACE VIEW v3_spatial.analysis_areas AS
SELECT 'cph_' || lpad(district_number::text,2,'0') AS area_id, district_name AS area_name,
       '0101'::text AS municipality_code, source_file_id, geom_4326, geom_25832, boundary_25832
FROM v3_spatial.official_copenhagen_districts
UNION ALL
SELECT 'frederiksberg_0147', municipality_name, municipality_code,
       source_file_id, geom_4326, geom_25832, boundary_25832
FROM v3_spatial.official_municipalities WHERE municipality_code='0147';

ALTER TABLE v3_features.listing_spatial_base
    ADD COLUMN IF NOT EXISTS official_municipality_code text,
    ADD COLUMN IF NOT EXISTS official_municipality_match_count integer,
    ADD COLUMN IF NOT EXISTS analysis_area text,
    ADD COLUMN IF NOT EXISTS official_cv_match_count integer,
    ADD COLUMN IF NOT EXISTS official_assignment_status text,
    ADD COLUMN IF NOT EXISTS near_official_border_100m boolean;
CREATE INDEX IF NOT EXISTS listing_spatial_base_official_cv_idx
    ON v3_features.listing_spatial_base (analysis_area,snapshot_date);


-- Official neighbouring municipalities are cartographic context only.
-- Keep them separate from the two-municipality study-area table.
CREATE TABLE IF NOT EXISTS v3_spatial.map_context_municipalities (
    municipality_code text PRIMARY KEY,
    municipality_name text NOT NULL,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    source_crs_epsg integer NOT NULL CHECK (source_crs_epsg = 4326),
    geom_source geometry(MultiPolygon,4326) NOT NULL,
    geom_4326 geometry(MultiPolygon,4326) NOT NULL,
    geom_25832 geometry(MultiPolygon,25832) NOT NULL
);
CREATE INDEX IF NOT EXISTS map_context_municipalities_geom_gist
    ON v3_spatial.map_context_municipalities USING gist(geom_4326);
CREATE INDEX IF NOT EXISTS map_context_municipalities_metric_gist
    ON v3_spatial.map_context_municipalities USING gist(geom_25832);


-- immutable-source OSM element copy, auditable destinations and Euclidean v3_features.
CREATE TABLE IF NOT EXISTS v3_raw.osm_elements (
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    osm_type text NOT NULL CHECK (osm_type IN ('node','way','relation')),
    osm_id bigint NOT NULL,
    element jsonb NOT NULL,
    PRIMARY KEY (source_file_id,osm_type,osm_id)
);

CREATE TABLE IF NOT EXISTS v3_spatial.osm_destination_candidates (
    candidate_key text PRIMARY KEY,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    taxonomy_version text NOT NULL,
    category text NOT NULL CHECK (category IN ('food_social','cultural_tourist','station')),
    osm_type text NOT NULL CHECK (osm_type IN ('node','way','relation')),
    osm_id bigint NOT NULL,
    name text,
    normalized_name text NOT NULL,
    wikidata text,
    tags jsonb NOT NULL,
    position_method text NOT NULL CHECK (position_method IN ('osm_node','gdal_point_on_surface')),
    geom geometry(Point,4326) NOT NULL,
    geom_25832 geometry(Point,25832) NOT NULL,
    canonical_candidate_key text REFERENCES v3_spatial.osm_destination_candidates(candidate_key),
    dedup_reason text,
    UNIQUE (source_file_id,category,osm_type,osm_id)
);
CREATE INDEX IF NOT EXISTS osm_candidates_metric_gist
    ON v3_spatial.osm_destination_candidates USING gist (geom_25832);
CREATE INDEX IF NOT EXISTS osm_candidates_category_name_idx
    ON v3_spatial.osm_destination_candidates (category,normalized_name);

CREATE TABLE IF NOT EXISTS v3_spatial.osm_pois (
    destination_key text PRIMARY KEY REFERENCES v3_spatial.osm_destination_candidates(candidate_key),
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    taxonomy_version text NOT NULL,
    category text NOT NULL CHECK (category IN ('food_social','cultural_tourist')),
    osm_type text NOT NULL,
    osm_id bigint NOT NULL,
    name text,
    tags jsonb NOT NULL,
    position_method text NOT NULL,
    merged_osm_refs jsonb NOT NULL,
    duplicate_count integer NOT NULL CHECK (duplicate_count >= 0),
    geom geometry(Point,4326) NOT NULL,
    geom_25832 geometry(Point,25832) NOT NULL
);
CREATE INDEX IF NOT EXISTS osm_pois_metric_gist ON v3_spatial.osm_pois USING gist (geom_25832);
CREATE INDEX IF NOT EXISTS osm_pois_category_idx ON v3_spatial.osm_pois (category);

CREATE TABLE IF NOT EXISTS v3_spatial.transit_stations (
    station_key text PRIMARY KEY REFERENCES v3_spatial.osm_destination_candidates(candidate_key),
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    taxonomy_version text NOT NULL,
    station_mode text NOT NULL CHECK (station_mode IN ('metro','urban_rail','rail')),
    osm_type text NOT NULL,
    osm_id bigint NOT NULL,
    name text NOT NULL,
    tags jsonb NOT NULL,
    position_method text NOT NULL,
    merged_osm_refs jsonb NOT NULL,
    duplicate_count integer NOT NULL CHECK (duplicate_count >= 0),
    geom geometry(Point,4326) NOT NULL,
    geom_25832 geometry(Point,25832) NOT NULL
);
CREATE INDEX IF NOT EXISTS transit_stations_metric_gist
    ON v3_spatial.transit_stations USING gist (geom_25832);

CREATE TABLE IF NOT EXISTS v3_features.euclidean_accessibility (
    snapshot_date date NOT NULL,
    listing_id bigint NOT NULL,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    taxonomy_version text NOT NULL,
    valid_coordinates boolean NOT NULL,
    count_coverage_complete boolean,
    source_edge_distance_m double precision CHECK (source_edge_distance_m >= 0),
    nearest_station_coverage_complete boolean,
    nearest_station_key text REFERENCES v3_spatial.transit_stations(station_key),
    nearest_station_distance_m double precision CHECK (nearest_station_distance_m >= 0),
    food_social_833m integer CHECK (food_social_833m >= 0),
    food_social_1250m integer CHECK (food_social_1250m >= 0),
    food_social_1667m integer CHECK (food_social_1667m >= 0),
    cultural_tourist_833m integer CHECK (cultural_tourist_833m >= 0),
    cultural_tourist_1250m integer CHECK (cultural_tourist_1250m >= 0),
    cultural_tourist_1667m integer CHECK (cultural_tourist_1667m >= 0),
    distance_crs_epsg integer NOT NULL DEFAULT 25832 CHECK (distance_crs_epsg = 25832),
    built_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (snapshot_date,listing_id),
    FOREIGN KEY (snapshot_date,listing_id) REFERENCES v3_clean.airbnb_listings(snapshot_date,listing_id)
);
CREATE INDEX IF NOT EXISTS euclidean_accessibility_source_idx
    ON v3_features.euclidean_accessibility (source_file_id,taxonomy_version);


-- versioned pedestrian graph, auditable snaps, and listing-level routes.
CREATE TABLE IF NOT EXISTS v3_spatial.walking_networks (
    network_id text PRIMARY KEY,
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    source_sha256 char(64) NOT NULL,
    source_date date,
    network_type text NOT NULL,
    filter_version text NOT NULL,
    filter_spec jsonb NOT NULL,
    source_crs_epsg integer NOT NULL CHECK (source_crs_epsg=4326),
    metric_crs_epsg integer NOT NULL CHECK (metric_crs_epsg=25832),
    node_count integer NOT NULL CHECK (node_count>0),
    source_segment_count integer NOT NULL CHECK (source_segment_count>0),
    directed_arc_count integer NOT NULL CHECK (directed_arc_count>0),
    weak_component_count integer NOT NULL CHECK (weak_component_count>0),
    largest_component_nodes integer NOT NULL CHECK (largest_component_nodes>0),
    built_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_file_id,filter_version)
);

CREATE TABLE IF NOT EXISTS v3_spatial.walking_nodes (
    network_id text NOT NULL REFERENCES v3_spatial.walking_networks(network_id),
    osm_node_id bigint NOT NULL,
    lon double precision NOT NULL,
    lat double precision NOT NULL,
    component_id integer NOT NULL CHECK (component_id>0),
    geom_25832 geometry(Point,25832) NOT NULL,
    PRIMARY KEY (network_id,osm_node_id),
    CHECK (lon BETWEEN 12 AND 13 AND lat BETWEEN 55 AND 56)
);
CREATE INDEX IF NOT EXISTS walking_nodes_metric_gist ON v3_spatial.walking_nodes USING gist(geom_25832);
CREATE INDEX IF NOT EXISTS walking_nodes_component_idx ON v3_spatial.walking_nodes(network_id,component_id);

CREATE TABLE IF NOT EXISTS v3_spatial.walking_edges (
    network_id text NOT NULL REFERENCES v3_spatial.walking_networks(network_id),
    osm_way_id bigint NOT NULL,
    segment_index integer NOT NULL,
    from_node_id bigint NOT NULL,
    to_node_id bigint NOT NULL,
    length_m double precision NOT NULL CHECK (length_m>0),
    highway text NOT NULL,
    forward_allowed boolean NOT NULL,
    reverse_allowed boolean NOT NULL,
    PRIMARY KEY (network_id,osm_way_id,segment_index),
    FOREIGN KEY (network_id,from_node_id) REFERENCES v3_spatial.walking_nodes(network_id,osm_node_id),
    FOREIGN KEY (network_id,to_node_id) REFERENCES v3_spatial.walking_nodes(network_id,osm_node_id),
    CHECK (forward_allowed OR reverse_allowed)
);
CREATE INDEX IF NOT EXISTS walking_edges_from_idx ON v3_spatial.walking_edges(network_id,from_node_id);
CREATE INDEX IF NOT EXISTS walking_edges_to_idx ON v3_spatial.walking_edges(network_id,to_node_id);

CREATE TABLE IF NOT EXISTS v3_spatial.walking_destination_snaps (
    network_id text NOT NULL REFERENCES v3_spatial.walking_networks(network_id),
    destination_kind text NOT NULL CHECK (destination_kind IN ('poi','station')),
    destination_key text NOT NULL,
    category text NOT NULL CHECK (category IN ('food_social','cultural_tourist','station')),
    snapped_node_id bigint NOT NULL,
    component_id integer NOT NULL,
    snap_distance_m double precision NOT NULL CHECK (snap_distance_m>=0),
    large_snap boolean NOT NULL,
    severe_snap boolean NOT NULL,
    PRIMARY KEY (network_id,destination_kind,destination_key),
    FOREIGN KEY (network_id,snapped_node_id) REFERENCES v3_spatial.walking_nodes(network_id,osm_node_id)
);
CREATE INDEX IF NOT EXISTS walking_dest_snaps_node_idx ON v3_spatial.walking_destination_snaps(network_id,snapped_node_id);

CREATE TABLE IF NOT EXISTS v3_features.walking_listing_snaps (
    network_id text NOT NULL REFERENCES v3_spatial.walking_networks(network_id),
    snapshot_date date NOT NULL,
    listing_id bigint NOT NULL,
    snapped_node_id bigint,
    component_id integer,
    snap_distance_m double precision CHECK (snap_distance_m>=0),
    large_snap boolean,
    severe_snap boolean,
    PRIMARY KEY (network_id,snapshot_date,listing_id),
    FOREIGN KEY (snapshot_date,listing_id) REFERENCES v3_clean.airbnb_listings(snapshot_date,listing_id),
    FOREIGN KEY (network_id,snapped_node_id) REFERENCES v3_spatial.walking_nodes(network_id,osm_node_id)
);
CREATE INDEX IF NOT EXISTS walking_listing_snaps_node_idx ON v3_features.walking_listing_snaps(network_id,snapped_node_id);

CREATE TABLE IF NOT EXISTS v3_features.walking_accessibility (
    snapshot_date date NOT NULL,
    listing_id bigint NOT NULL,
    network_id text NOT NULL REFERENCES v3_spatial.walking_networks(network_id),
    destination_taxonomy_version text NOT NULL,
    walking_speed_kmh numeric(4,2) NOT NULL CHECK (walking_speed_kmh=5.00),
    snapped_node_id bigint,
    listing_snap_distance_m double precision CHECK (listing_snap_distance_m>=0),
    nearest_station_key text REFERENCES v3_spatial.transit_stations(station_key),
    nearest_station_network_distance_m double precision CHECK (nearest_station_network_distance_m>=0),
    nearest_station_walking_minutes double precision CHECK (nearest_station_walking_minutes>=0),
    nearest_station_coverage_complete boolean,
    food_social_w_10 integer CHECK (food_social_w_10>=0),
    food_social_w_15 integer CHECK (food_social_w_15>=0),
    food_social_w_20 integer CHECK (food_social_w_20>=0),
    cultural_tourist_w_10 integer CHECK (cultural_tourist_w_10>=0),
    cultural_tourist_w_15 integer CHECK (cultural_tourist_w_15>=0),
    cultural_tourist_w_20 integer CHECK (cultural_tourist_w_20>=0),
    routing_status text NOT NULL CHECK (routing_status IN ('ok','invalid_coordinates','no_walk_node','no_reachable_station')),
    distance_crs_epsg integer NOT NULL CHECK (distance_crs_epsg=25832),
    built_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (snapshot_date,listing_id),
    FOREIGN KEY (snapshot_date,listing_id) REFERENCES v3_clean.airbnb_listings(snapshot_date,listing_id),
    FOREIGN KEY (network_id,snapped_node_id) REFERENCES v3_spatial.walking_nodes(network_id,osm_node_id)
);
CREATE INDEX IF NOT EXISTS walking_accessibility_network_idx ON v3_features.walking_accessibility(network_id,routing_status);


-- Purpose-based feature versions are independent of immutable source vintages.
ALTER TABLE v3_clean.airbnb_listings ADD COLUMN sample_version text NOT NULL DEFAULT 'airbnb_sample_v3';
ALTER TABLE v3_spatial.official_copenhagen_districts ADD COLUMN area_version text NOT NULL DEFAULT 'analysis_areas_v3';
ALTER TABLE v3_spatial.official_municipalities ADD COLUMN area_version text NOT NULL DEFAULT 'analysis_areas_v3';
ALTER TABLE v3_features.listing_spatial_base ADD COLUMN feature_version text NOT NULL DEFAULT 'spatial_features_v3';
ALTER TABLE v3_features.euclidean_accessibility ADD COLUMN feature_version text NOT NULL DEFAULT 'euclidean_accessibility_v3';
ALTER TABLE v3_features.walking_accessibility ADD COLUMN feature_version text NOT NULL DEFAULT 'walking_accessibility_v3';
