-- Acquisition audit is independent of housing-gated model runs. V4 DB only.
CREATE TABLE v4_raw.listing_ingestions (
 version text NOT NULL CHECK (version='research_design_v4'), run_id text NOT NULL,
 city text NOT NULL CHECK (city IN ('copenhagen_frederiksberg','oslo','stockholm')),
 snapshot date NOT NULL CHECK (snapshot=DATE '2026-06-30'),
 purpose text NOT NULL CHECK (purpose IN ('research','synthetic')),
 definition_version text NOT NULL CHECK (definition_version='v4_listing_ingestion_20261011'),
 manifest_sha256 text NOT NULL, summary jsonb NOT NULL, created_at timestamptz NOT NULL,
 creation_transaction xid8 NOT NULL DEFAULT pg_current_xact_id(),
 PRIMARY KEY(version,run_id,city,snapshot),
 FOREIGN KEY(version,city,snapshot,manifest_sha256) REFERENCES v4_raw.source_manifests,
 CHECK (run_id ~ ('^' || CASE purpose WHEN 'research' THEN 'research' ELSE 'synthetic' END || '_v4_' || city || '_[0-9]{8}T[0-9]{6}Z$'))
);
CREATE TABLE v4_raw.listing_audit (
 version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
 row_number integer NOT NULL CHECK (row_number>0), listing_id text NOT NULL,
 record jsonb NOT NULL,
 PRIMARY KEY(version,run_id,city,snapshot,row_number),
 FOREIGN KEY(version,run_id,city,snapshot) REFERENCES v4_raw.listing_ingestions
);
-- No uniqueness assumption on listing_id here: duplicate/invalid source rows retained.
CREATE INDEX listing_audit_listing_key ON v4_raw.listing_audit(version,city,snapshot,listing_id);
CREATE TABLE v4_spatial.study_boundaries (
 version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
 source_id text NOT NULL, source_area_id text NOT NULL,
 manifest_sha256 text NOT NULL, native_crs text NOT NULL, vintage text NOT NULL,
 geom geometry(MultiPolygon,4326) NOT NULL CHECK (ST_IsValid(geom) AND NOT ST_IsEmpty(geom)),
 PRIMARY KEY(version,run_id,city,snapshot,source_id,source_area_id),
 FOREIGN KEY(version,run_id,city,snapshot) REFERENCES v4_raw.listing_ingestions,
 FOREIGN KEY(version,city,snapshot,manifest_sha256) REFERENCES v4_raw.source_manifests
);
CREATE FUNCTION v4_raw.guard_ingestion() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Completed ingestion audit is immutable'; END IF;
 IF NEW.creation_transaction <> pg_current_xact_id() THEN RAISE EXCEPTION 'Invalid ingestion transaction'; END IF;
 IF (NEW.purpose='synthetic') <> (current_database() ~ '^test_v4_[0-9a-f]{32}$') THEN
   RAISE EXCEPTION 'Synthetic/research database purpose mismatch';
 END IF;
 IF NOT EXISTS (SELECT 1 FROM v4_raw.source_manifests m WHERE m.version=NEW.version
   AND m.city=NEW.city AND m.snapshot=NEW.snapshot AND m.manifest_sha256=NEW.manifest_sha256
   AND m.purpose=NEW.purpose) THEN RAISE EXCEPTION 'Ingestion manifest purpose mismatch'; END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION v4_raw.guard_audit_child() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Ingestion records are append-only'; END IF;
 -- Children must be inserted in the parent's transaction. A committed audit cannot grow.
 IF NOT EXISTS (SELECT 1 FROM v4_raw.listing_ingestions p WHERE p.version=NEW.version
   AND p.run_id=NEW.run_id AND p.city=NEW.city AND p.snapshot=NEW.snapshot
   AND p.creation_transaction = pg_current_xact_id()) THEN
   RAISE EXCEPTION 'Committed ingestion audit cannot accept new records';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER guard_ingestion BEFORE INSERT OR UPDATE OR DELETE ON v4_raw.listing_ingestions
 FOR EACH ROW EXECUTE FUNCTION v4_raw.guard_ingestion();
CREATE TRIGGER guard_listing_audit BEFORE INSERT OR UPDATE OR DELETE ON v4_raw.listing_audit
 FOR EACH ROW EXECUTE FUNCTION v4_raw.guard_audit_child();
CREATE TRIGGER guard_study_boundary BEFORE INSERT OR UPDATE OR DELETE ON v4_spatial.study_boundaries
 FOR EACH ROW EXECUTE FUNCTION v4_raw.guard_audit_child();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_raw.listing_ingestions
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_raw.listing_audit
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_spatial.study_boundaries
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
