-- A04 independent, immutable source/context checkpoints; never model runs.
CREATE TABLE v4_features.context_qualifications (
 version text NOT NULL CHECK(version='research_design_v4'),run_id text NOT NULL,
 city text NOT NULL CHECK(city IN ('copenhagen_frederiksberg','oslo','stockholm')),
 snapshot date NOT NULL CHECK(snapshot=DATE '2026-06-30'),
 design_id text NOT NULL CHECK(design_id='v4_accessibility_only_20261011'),
 purpose text NOT NULL CHECK(purpose IN ('research','synthetic')),
 definition_version text NOT NULL CHECK(definition_version='v4_context_A04_20261011'),
 manifest_sha256 text NOT NULL,geography_run_id text NOT NULL,geography_manifest_sha256 text NOT NULL,
 listing_run_id text NOT NULL,listing_manifest_sha256 text NOT NULL,
 summary_sha256 text NOT NULL CHECK(summary_sha256 ~ '^[0-9a-f]{64}$'),summary jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),creation_transaction xid8 NOT NULL DEFAULT pg_current_xact_id(),
 PRIMARY KEY(version,run_id,city,snapshot,design_id),
 FOREIGN KEY(version,city,snapshot,manifest_sha256) REFERENCES v4_raw.source_manifests,
 FOREIGN KEY(version,geography_run_id,city,snapshot,design_id) REFERENCES v4_spatial.geography_qualifications,
 FOREIGN KEY(version,listing_run_id,city,snapshot) REFERENCES v4_raw.listing_ingestions(version,run_id,city,snapshot),
 CHECK(run_id ~ ('^' || CASE purpose WHEN 'research' THEN 'research' ELSE 'synthetic' END || '_v4_' || city || '_[0-9]{8}T[0-9]{6}Z$')),
 CHECK(summary->>'city'=city AND summary->>'design_id'=design_id),
 CHECK(summary->>'status' IN ('QUALIFIED','BLOCKED'))
);
CREATE TABLE v4_features.native_context_cells (
 version text NOT NULL,run_id text NOT NULL,city text NOT NULL,snapshot date NOT NULL,design_id text NOT NULL,
 source_id text NOT NULL,native_id text NOT NULL,measure text NOT NULL,
 value double precision CHECK(value IS NULL OR (value > '-Infinity'::double precision AND value < 'Infinity'::double precision)),
 unit text NOT NULL,reference_period text NOT NULL,record jsonb NOT NULL,
 PRIMARY KEY(version,run_id,city,snapshot,design_id,source_id,native_id,measure),
 FOREIGN KEY(version,run_id,city,snapshot,design_id) REFERENCES v4_features.context_qualifications,
 CHECK(record->>'native_id'=native_id AND record->>'measure'=measure AND record->>'unit'=unit
       AND record->>'reference_period'=reference_period)
);
CREATE TABLE v4_features.listing_context_audit (
 version text NOT NULL,run_id text NOT NULL,city text NOT NULL CHECK(city='copenhagen_frederiksberg'),
 snapshot date NOT NULL,design_id text NOT NULL,listing_id text NOT NULL,record jsonb NOT NULL,
 PRIMARY KEY(version,run_id,city,snapshot,design_id,listing_id),
 FOREIGN KEY(version,run_id,city,snapshot,design_id) REFERENCES v4_features.context_qualifications,
 CHECK(record->>'listing_id'=listing_id)
);
CREATE FUNCTION v4_features.guard_context_parent() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Committed context qualification is immutable'; END IF;
 IF NEW.creation_transaction <> pg_current_xact_id() THEN RAISE EXCEPTION 'Invalid context transaction'; END IF;
 IF (NEW.purpose='synthetic') <> (current_database() ~ '^test_v4_[0-9a-f]{32}$') THEN RAISE EXCEPTION 'Context database purpose mismatch'; END IF;
 IF NOT EXISTS(SELECT 1 FROM v4_spatial.geography_qualifications g WHERE g.version=NEW.version AND g.run_id=NEW.geography_run_id
 AND g.city=NEW.city AND g.snapshot=NEW.snapshot AND g.design_id=NEW.design_id AND g.purpose=NEW.purpose
 AND g.manifest_sha256=NEW.geography_manifest_sha256 AND g.listing_run_id=NEW.listing_run_id AND g.listing_manifest_sha256=NEW.listing_manifest_sha256)
 OR NOT EXISTS(SELECT 1 FROM v4_raw.source_manifests m WHERE m.version=NEW.version AND m.city=NEW.city AND m.snapshot=NEW.snapshot
 AND m.manifest_sha256=NEW.manifest_sha256 AND m.purpose=NEW.purpose)
 THEN RAISE EXCEPTION 'Context source/geography/purpose mismatch'; END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION v4_features.guard_context_child() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Context child is append-only'; END IF;
 IF NOT EXISTS(SELECT 1 FROM v4_features.context_qualifications p WHERE p.version=NEW.version AND p.run_id=NEW.run_id
 AND p.city=NEW.city AND p.snapshot=NEW.snapshot AND p.design_id=NEW.design_id AND p.creation_transaction=pg_current_xact_id())
 THEN RAISE EXCEPTION 'Committed context checkpoint cannot grow'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER guard_context_parent BEFORE INSERT OR UPDATE OR DELETE ON v4_features.context_qualifications
 FOR EACH ROW EXECUTE FUNCTION v4_features.guard_context_parent();
CREATE TRIGGER guard_native_context BEFORE INSERT OR UPDATE OR DELETE ON v4_features.native_context_cells
 FOR EACH ROW EXECUTE FUNCTION v4_features.guard_context_child();
CREATE TRIGGER guard_listing_context BEFORE INSERT OR UPDATE OR DELETE ON v4_features.listing_context_audit
 FOR EACH ROW EXECUTE FUNCTION v4_features.guard_context_child();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_features.context_qualifications
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_features.native_context_cells
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_features.listing_context_audit
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
