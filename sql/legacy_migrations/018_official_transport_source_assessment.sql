-- Source-quality assessment only: no frozen feature, network or model is replaced.
-- Original coordinates retain their source SRID; every metric operation uses EPSG:25832.
CREATE TABLE IF NOT EXISTS raw.official_transport_source_features (
    source_file_id bigint NOT NULL REFERENCES meta.source_files(source_file_id),
    source_row integer NOT NULL,
    dataset text NOT NULL,
    attributes jsonb NOT NULL,
    source_crs_epsg integer NOT NULL CHECK (source_crs_epsg IN (4326,25832)),
    geom_source geometry,
    geom_25832 geometry(Geometry,25832),
    PRIMARY KEY(source_file_id,source_row)
);
CREATE INDEX IF NOT EXISTS official_transport_source_geom_idx
    ON raw.official_transport_source_features USING gist(geom_25832);
CREATE INDEX IF NOT EXISTS official_transport_source_dataset_idx
    ON raw.official_transport_source_features(dataset,source_file_id);

CREATE TABLE IF NOT EXISTS meta.official_transport_assessments (
    assessment_id text PRIMARY KEY,
    assessed_on date NOT NULL,
    policy jsonb NOT NULL,
    input_sha256 jsonb NOT NULL,
    results jsonb NOT NULL,
    assessed_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS meta.official_transport_feature_status (
    assessment_id text NOT NULL REFERENCES meta.official_transport_assessments(assessment_id),
    source_file_id bigint NOT NULL,
    source_row integer NOT NULL,
    existence_status text NOT NULL CHECK (existence_status IN ('existing','planned','projected','unknown')),
    evidence text NOT NULL,
    PRIMARY KEY(assessment_id,source_file_id,source_row),
    FOREIGN KEY(source_file_id,source_row)
        REFERENCES raw.official_transport_source_features(source_file_id,source_row)
);
COMMENT ON TABLE meta.official_transport_feature_status IS
    'Only existing records are eligible candidates. Unknown status is preserved and not silently treated as existing. Operator evidence is current-date evidence, not a historical June 2026 reconstruction.';

CREATE OR REPLACE VIEW spatial.official_transport_existing_candidates AS
WITH latest AS (
    SELECT assessment_id FROM meta.official_transport_assessments
    WHERE results->>'complete'='true' ORDER BY assessed_at DESC LIMIT 1
)
SELECT f.*, s.assessment_id, s.existence_status, s.evidence
FROM raw.official_transport_source_features f
JOIN meta.official_transport_feature_status s USING(source_file_id,source_row)
JOIN latest USING(assessment_id)
WHERE s.existence_status='existing'
  AND f.dataset NOT IN ('movia_operator_bus_reference','metro_operator_reference');
COMMENT ON VIEW spatial.official_transport_existing_candidates IS
    'Source-validation candidates only, not a replacement for frozen features. Planned, projected and unknown infrastructure are excluded.';
