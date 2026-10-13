-- A03 qualification receipts are independent of model runs and old ingestions.
CREATE TABLE v4_spatial.geography_qualifications (
 version text NOT NULL CHECK(version='research_design_v4'), run_id text NOT NULL,
 city text NOT NULL CHECK(city IN ('copenhagen_frederiksberg','oslo','stockholm')),
 snapshot date NOT NULL CHECK(snapshot=DATE '2026-06-30'),
 design_id text NOT NULL CHECK(design_id='v4_accessibility_only_20261011'),
 purpose text NOT NULL CHECK(purpose IN ('research','synthetic')),
 definition_version text NOT NULL CHECK(definition_version='v4_geography_A03_20261011'),
 manifest_sha256 text NOT NULL, listing_run_id text NOT NULL, listing_manifest_sha256 text NOT NULL,
 summary_sha256 text NOT NULL CHECK(summary_sha256 ~ '^[0-9a-f]{64}$'), summary jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 creation_transaction xid8 NOT NULL DEFAULT pg_current_xact_id(),
 PRIMARY KEY(version,run_id,city,snapshot,design_id),
 FOREIGN KEY(version,city,snapshot,manifest_sha256) REFERENCES v4_raw.source_manifests,
 FOREIGN KEY(version,city,snapshot,listing_manifest_sha256) REFERENCES v4_raw.source_manifests,
 FOREIGN KEY(version,listing_run_id,city,snapshot) REFERENCES v4_raw.listing_ingestions(version,run_id,city,snapshot),
 CHECK(run_id ~ ('^' || CASE purpose WHEN 'research' THEN 'research' ELSE 'synthetic' END || '_v4_' || city || '_[0-9]{8}T[0-9]{6}Z$')),
 CHECK(summary->>'design_id'=design_id AND summary->>'city'=city),
 CHECK(summary->>'status' IN ('QUALIFIED','BLOCKED'))
);
CREATE TABLE v4_spatial.geography_masks (
 version text NOT NULL,run_id text NOT NULL,city text NOT NULL,snapshot date NOT NULL,design_id text NOT NULL,
 geom geometry(MultiPolygon,4326) NOT NULL CHECK(ST_IsValid(geom) AND NOT ST_IsEmpty(geom)),
 PRIMARY KEY(version,run_id,city,snapshot,design_id),
 FOREIGN KEY(version,run_id,city,snapshot,design_id) REFERENCES v4_spatial.geography_qualifications
);
CREATE TABLE v4_spatial.analysis_geography (
 version text NOT NULL,run_id text NOT NULL,city text NOT NULL,snapshot date NOT NULL,design_id text NOT NULL,
 area_id text NOT NULL,native_id text NOT NULL,name text NOT NULL,
 geom geometry(MultiPolygon,4326) NOT NULL CHECK(ST_IsValid(geom) AND NOT ST_IsEmpty(geom)),
 PRIMARY KEY(version,run_id,city,snapshot,design_id,area_id),
 FOREIGN KEY(version,run_id,city,snapshot,design_id) REFERENCES v4_spatial.geography_qualifications,
 UNIQUE(version,run_id,city,snapshot,design_id,native_id)
);
CREATE TABLE v4_spatial.geography_listing_audit (
 version text NOT NULL,run_id text NOT NULL,city text NOT NULL,snapshot date NOT NULL,design_id text NOT NULL,
 listing_id text NOT NULL,area_id text,record jsonb NOT NULL,
 PRIMARY KEY(version,run_id,city,snapshot,design_id,listing_id),
 FOREIGN KEY(version,run_id,city,snapshot,design_id) REFERENCES v4_spatial.geography_qualifications,
 FOREIGN KEY(version,run_id,city,snapshot,design_id,area_id) REFERENCES v4_spatial.analysis_geography
);
CREATE FUNCTION v4_spatial.guard_geography_parent() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Committed geography qualification is immutable'; END IF;
 IF NEW.creation_transaction <> pg_current_xact_id() THEN RAISE EXCEPTION 'Invalid geography transaction'; END IF;
 IF (NEW.purpose='synthetic') <> (current_database() ~ '^test_v4_[0-9a-f]{32}$') THEN
   RAISE EXCEPTION 'Geography database purpose mismatch'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v4_raw.listing_ingestions l WHERE l.version=NEW.version AND l.run_id=NEW.listing_run_id
   AND l.city=NEW.city AND l.snapshot=NEW.snapshot AND l.purpose=NEW.purpose AND l.manifest_sha256=NEW.listing_manifest_sha256)
   OR NOT EXISTS (SELECT 1 FROM v4_raw.source_manifests m WHERE m.version=NEW.version AND m.city=NEW.city
   AND m.snapshot=NEW.snapshot AND m.manifest_sha256=NEW.manifest_sha256 AND m.purpose=NEW.purpose)
 THEN RAISE EXCEPTION 'Geography source/purpose mismatch'; END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION v4_spatial.guard_geography_child() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Geography audit is append-only'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v4_spatial.geography_qualifications p WHERE p.version=NEW.version AND p.run_id=NEW.run_id
   AND p.city=NEW.city AND p.snapshot=NEW.snapshot AND p.design_id=NEW.design_id
   AND p.creation_transaction=pg_current_xact_id()) THEN RAISE EXCEPTION 'Committed geography audit cannot grow'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER guard_geography_parent BEFORE INSERT OR UPDATE OR DELETE ON v4_spatial.geography_qualifications
 FOR EACH ROW EXECUTE FUNCTION v4_spatial.guard_geography_parent();
CREATE TRIGGER guard_geography_mask BEFORE INSERT OR UPDATE OR DELETE ON v4_spatial.geography_masks
 FOR EACH ROW EXECUTE FUNCTION v4_spatial.guard_geography_child();
CREATE TRIGGER guard_analysis_geography BEFORE INSERT OR UPDATE OR DELETE ON v4_spatial.analysis_geography
 FOR EACH ROW EXECUTE FUNCTION v4_spatial.guard_geography_child();
CREATE TRIGGER guard_geography_listing BEFORE INSERT OR UPDATE OR DELETE ON v4_spatial.geography_listing_audit
 FOR EACH ROW EXECUTE FUNCTION v4_spatial.guard_geography_child();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_spatial.geography_qualifications
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_spatial.geography_masks
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_spatial.analysis_geography
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_spatial.geography_listing_audit
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
