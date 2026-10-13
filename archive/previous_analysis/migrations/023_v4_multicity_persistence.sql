-- V4 only. Apply through src.v4.persistence, never the V3 migration runner.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA v4_raw;
CREATE SCHEMA v4_clean;
CREATE SCHEMA v4_spatial;
CREATE SCHEMA v4_features;
-- v4_analysis and its checksum ledger are bootstrapped transactionally by adapter.

CREATE TABLE v4_analysis.runs (
    version text NOT NULL CHECK (version='research_design_v4'),
    run_id text NOT NULL,
    city text NOT NULL CHECK (city IN ('copenhagen_frederiksberg','oslo','stockholm')),
    snapshot date NOT NULL CHECK (snapshot >= DATE '2026-06-01' AND snapshot < DATE '2026-07-01'),
    purpose text NOT NULL CHECK (purpose IN ('research','synthetic')),
    definition_version text NOT NULL CHECK (definition_version='v4_housing_standard_20261011'),
    scientific_sha256 text NOT NULL CHECK (scientific_sha256 ~ '^[0-9a-f]{64}$'),
    scientific_dependencies jsonb NOT NULL,
    reporting_dependencies jsonb NOT NULL DEFAULT '{}'::jsonb,
    status text NOT NULL DEFAULT 'running' CHECK (status IN ('running','blocked','failed','completed')),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (version,run_id,city,snapshot),
    CHECK (run_id ~ ('^' || CASE purpose WHEN 'research' THEN 'research' ELSE 'synthetic' END || '_v4_' || city || '_[0-9]{8}T[0-9]{6}Z$'))
);

CREATE TABLE v4_raw.source_manifests (
    version text NOT NULL CHECK (version='research_design_v4'),
    city text NOT NULL CHECK (city IN ('copenhagen_frederiksberg','oslo','stockholm')),
    snapshot date NOT NULL CHECK (snapshot >= DATE '2026-06-01' AND snapshot < DATE '2026-07-01'),
    manifest_sha256 text NOT NULL CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
    purpose text NOT NULL CHECK (purpose IN ('research','synthetic')),
    manifest jsonb NOT NULL,
    PRIMARY KEY(version,city,snapshot,manifest_sha256)
);

CREATE TABLE v4_raw.observations (
    version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
    listing_id text NOT NULL CHECK (listing_id <> ''),
    source_id text NOT NULL CHECK (source_id <> ''),
    source_area_id text, -- native source area; do not infer a housing crosswalk
    manifest_sha256 text NOT NULL,
    record jsonb NOT NULL,
    PRIMARY KEY(version,run_id,city,snapshot,listing_id),
    FOREIGN KEY(version,run_id,city,snapshot) REFERENCES v4_analysis.runs,
    FOREIGN KEY(version,city,snapshot,manifest_sha256) REFERENCES v4_raw.source_manifests
);

CREATE TABLE v4_spatial.source_areas (
    version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
    source_id text NOT NULL, source_area_id text NOT NULL,
    manifest_sha256 text NOT NULL,
    metric_crs integer NOT NULL CHECK (metric_crs > 0 AND metric_crs <> 4326),
    geom geometry(MultiPolygon) NOT NULL CHECK (ST_SRID(geom)=metric_crs),
    PRIMARY KEY(version,run_id,city,snapshot,source_id,source_area_id),
    FOREIGN KEY(version,run_id,city,snapshot) REFERENCES v4_analysis.runs,
    FOREIGN KEY(version,city,snapshot,manifest_sha256) REFERENCES v4_raw.source_manifests
);

CREATE TABLE v4_features.area_context (
    version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
    source_id text NOT NULL, source_area_id text NOT NULL,
    record jsonb NOT NULL,
    PRIMARY KEY(version,run_id,city,snapshot,source_id,source_area_id),
    FOREIGN KEY(version,run_id,city,snapshot,source_id,source_area_id) REFERENCES v4_spatial.source_areas
);

CREATE TABLE v4_analysis.artifacts (
    version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
    definition_id text NOT NULL CHECK (definition_id ~ '^v4_housing_standard_20261011:(no_income:|log_native_housing:)?(M0|ME|MW|MEW)$'),
    family text NOT NULL, artifact text NOT NULL, record_key text NOT NULL,
    record jsonb NOT NULL,
    PRIMARY KEY(version,run_id,city,snapshot,definition_id,family,artifact,record_key),
    FOREIGN KEY(version,run_id,city,snapshot) REFERENCES v4_analysis.runs
);

-- Only these aggregate fields are available to public report exports.
CREATE TABLE v4_analysis.aggregate_metrics (
    version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
    definition_id text NOT NULL CHECK (definition_id ~ '^v4_housing_standard_20261011:(no_income:|log_native_housing:)?(M0|ME|MW|MEW)$'),
    engine text NOT NULL CHECK (engine IN ('OLS','XGBoost')),
    validation text NOT NULL CHECK (validation IN ('random','geographic')),
    n integer NOT NULL CHECK (n > 0),
    rmse double precision NOT NULL CHECK (rmse >= 0 AND rmse < 'Infinity'::double precision),
    mae double precision NOT NULL CHECK (mae >= 0 AND mae < 'Infinity'::double precision),
    PRIMARY KEY(version,run_id,city,snapshot,definition_id,engine,validation),
    FOREIGN KEY(version,run_id,city,snapshot) REFERENCES v4_analysis.runs
);

CREATE FUNCTION v4_analysis.guard_run() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP <> 'INSERT' THEN
        IF OLD.status='completed' THEN RAISE EXCEPTION 'Completed V4 run is immutable'; END IF;
        IF TG_OP='DELETE' THEN RAISE EXCEPTION 'V4 runs are append-only'; END IF;
        IF (NEW.version,NEW.run_id,NEW.city,NEW.snapshot,NEW.purpose,NEW.definition_version,NEW.scientific_sha256,NEW.scientific_dependencies)
           IS DISTINCT FROM
           (OLD.version,OLD.run_id,OLD.city,OLD.snapshot,OLD.purpose,OLD.definition_version,OLD.scientific_sha256,OLD.scientific_dependencies)
        THEN RAISE EXCEPTION 'V4 scientific run identity is immutable'; END IF;
    END IF;
    IF (NEW.purpose='synthetic') <> (current_database() ~ '^test_v4_[0-9a-f]{32}$') THEN
        RAISE EXCEPTION 'Synthetic/research database purpose mismatch';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_run BEFORE INSERT OR UPDATE OR DELETE ON v4_analysis.runs
    FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_run();

CREATE FUNCTION v4_raw.guard_manifest() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Source manifests are immutable'; END IF;
    IF (NEW.purpose='synthetic') <> (current_database() ~ '^test_v4_[0-9a-f]{32}$') THEN
        RAISE EXCEPTION 'Synthetic/research database purpose mismatch';
    END IF;
    IF NEW.manifest->>'version' IS DISTINCT FROM NEW.version OR
       NEW.manifest->>'city' IS DISTINCT FROM NEW.city OR
       NEW.manifest->>'snapshot' IS DISTINCT FROM NEW.snapshot::text OR
       NEW.manifest->>'purpose' IS DISTINCT FROM NEW.purpose THEN
        RAISE EXCEPTION 'Manifest scope mismatch';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_manifest BEFORE INSERT OR UPDATE OR DELETE ON v4_raw.source_manifests
    FOR EACH ROW EXECUTE FUNCTION v4_raw.guard_manifest();

CREATE FUNCTION v4_analysis.guard_child() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE parent_status text;
BEGIN
    IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'V4 analytical records are append-only'; END IF;
    -- Serialize inserts with completion; a concurrent late write cannot pass.
    SELECT status INTO parent_status FROM v4_analysis.runs
        WHERE version=NEW.version AND run_id=NEW.run_id AND city=NEW.city AND snapshot=NEW.snapshot FOR UPDATE;
    IF parent_status IS DISTINCT FROM 'running' THEN RAISE EXCEPTION 'V4 run missing, stopped or completed'; END IF;
    IF TG_TABLE_NAME IN ('observations','source_areas') THEN
      IF NOT EXISTS (
        SELECT 1 FROM v4_raw.source_manifests m,
            jsonb_array_elements(m.manifest->'records') r
        WHERE m.version=NEW.version AND m.city=NEW.city AND m.snapshot=NEW.snapshot
          AND m.manifest_sha256=NEW.manifest_sha256 AND r->>'source_id'=NEW.source_id
      ) THEN RAISE EXCEPTION 'Source ID is not in the scoped manifest'; END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_observations BEFORE INSERT OR UPDATE OR DELETE ON v4_raw.observations
    FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_child();
CREATE TRIGGER guard_areas BEFORE INSERT OR UPDATE OR DELETE ON v4_spatial.source_areas
    FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_child();
CREATE TRIGGER guard_context BEFORE INSERT OR UPDATE OR DELETE ON v4_features.area_context
    FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_child();
CREATE TRIGGER guard_artifacts BEFORE INSERT OR UPDATE OR DELETE ON v4_analysis.artifacts
    FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_child();
CREATE TRIGGER guard_metrics BEFORE INSERT OR UPDATE OR DELETE ON v4_analysis.aggregate_metrics
    FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_child();

CREATE FUNCTION v4_analysis.refuse_truncate() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'V4 tables are append-only; truncation is forbidden';
END $$;
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_analysis.runs
    FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_raw.source_manifests
    FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_raw.observations
    FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_spatial.source_areas
    FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_features.area_context
    FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_analysis.artifacts
    FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_analysis.aggregate_metrics
    FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
