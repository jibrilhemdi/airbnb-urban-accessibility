-- Step 5 source audits only: independent of housing-gated model runs and listing IDs.
CREATE TABLE v4_raw.housing_ingestions (
 version text NOT NULL CHECK(version='research_design_v4'), run_id text NOT NULL,
 city text NOT NULL CHECK(city IN ('copenhagen_frederiksberg','oslo','stockholm')),
 snapshot date NOT NULL CHECK(snapshot=DATE '2026-06-30'),
 purpose text NOT NULL CHECK(purpose IN ('research','synthetic')),
 definition_version text NOT NULL CHECK(definition_version='v4_housing_sources_20261011'),
 manifest_sha256 text NOT NULL, summary jsonb NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 creation_transaction xid8 NOT NULL DEFAULT pg_current_xact_id(),
 PRIMARY KEY(version,run_id,city,snapshot),
 FOREIGN KEY(version,city,snapshot,manifest_sha256) REFERENCES v4_raw.source_manifests,
 CHECK(run_id ~ ('^' || CASE purpose WHEN 'research' THEN 'research' ELSE 'synthetic' END || '_v4_' || city || '_[0-9]{8}T[0-9]{6}Z$'))
);
CREATE TABLE v4_raw.housing_area_period_audit (
 version text NOT NULL, run_id text NOT NULL, city text NOT NULL, snapshot date NOT NULL,
 source_id text NOT NULL CHECK(source_id<>''), source_area_id text NOT NULL CHECK(source_area_id<>''),
 geography_level text NOT NULL, period text NOT NULL, record jsonb NOT NULL,
 PRIMARY KEY(version,run_id,city,snapshot,source_id,source_area_id,geography_level,period),
 FOREIGN KEY(version,run_id,city,snapshot) REFERENCES v4_raw.housing_ingestions
);
CREATE FUNCTION v4_raw.guard_housing_child() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP <> 'INSERT' THEN RAISE EXCEPTION 'Housing source audits are append-only'; END IF;
 IF NOT EXISTS (SELECT 1 FROM v4_raw.housing_ingestions p JOIN v4_raw.source_manifests m
   USING(version,city,snapshot,manifest_sha256)
   WHERE p.version=NEW.version AND p.run_id=NEW.run_id AND p.city=NEW.city AND p.snapshot=NEW.snapshot
   AND p.creation_transaction=pg_current_xact_id()
   AND EXISTS(SELECT 1 FROM jsonb_array_elements(m.manifest->'records') r WHERE r->>'source_id'=NEW.source_id)) THEN
   RAISE EXCEPTION 'Committed/cross-scope housing audit or unregistered source';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER guard_housing_ingestion BEFORE INSERT OR UPDATE OR DELETE ON v4_raw.housing_ingestions
 FOR EACH ROW EXECUTE FUNCTION v4_raw.guard_ingestion();
CREATE TRIGGER guard_housing_child BEFORE INSERT OR UPDATE OR DELETE ON v4_raw.housing_area_period_audit
 FOR EACH ROW EXECUTE FUNCTION v4_raw.guard_housing_child();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_raw.housing_ingestions
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON v4_raw.housing_area_period_audit
 FOR EACH STATEMENT EXECUTE FUNCTION v4_analysis.refuse_truncate();
