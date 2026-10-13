-- A02: new design identities only. No historical row/source/policy rewrite.
ALTER TABLE v4_analysis.runs DROP CONSTRAINT runs_definition_version_check;
ALTER TABLE v4_analysis.runs ADD CONSTRAINT runs_definition_version_check CHECK (
 definition_version IN ('v4_housing_standard_20261011','v4_accessibility_only_20261011'));

ALTER TABLE v4_analysis.artifacts DROP CONSTRAINT artifacts_definition_id_check;
ALTER TABLE v4_analysis.artifacts ADD CONSTRAINT artifacts_definition_id_check CHECK (
 definition_id ~ '^v4_housing_standard_20261011:(no_income:|log_native_housing:)?(M0|ME|MW|MEW)$'
 OR definition_id ~ '^v4_accessibility_only_20261011:(no_income:)?(M0|ME|MW|MEW)$');
ALTER TABLE v4_analysis.aggregate_metrics DROP CONSTRAINT aggregate_metrics_definition_id_check;
ALTER TABLE v4_analysis.aggregate_metrics ADD CONSTRAINT aggregate_metrics_definition_id_check CHECK (
 definition_id ~ '^v4_housing_standard_20261011:(no_income:|log_native_housing:)?(M0|ME|MW|MEW)$'
 OR definition_id ~ '^v4_accessibility_only_20261011:(no_income:)?(M0|ME|MW|MEW)$');

-- Separate estimator/validation from the model and sensitivity. Historical
-- artifact fields remain NULL rather than inventing retrospective provenance.
ALTER TABLE v4_analysis.artifacts ADD COLUMN engine text CHECK (engine IN ('OLS','XGBoost'));
ALTER TABLE v4_analysis.artifacts ADD COLUMN validation text CHECK (validation IN ('random','geographic'));
ALTER TABLE v4_analysis.artifacts ADD CONSTRAINT accessibility_artifact_dimensions CHECK (
 definition_id !~ '^v4_accessibility_only_20261011:' OR (engine IS NOT NULL AND validation IS NOT NULL));
-- Expand the artifact key only; each historical unique key remains unique with
-- NULL dimensions. Historical append-only/completed-run guards stay active.
ALTER TABLE v4_analysis.artifacts DROP CONSTRAINT artifacts_pkey;
CREATE UNIQUE INDEX artifact_identity_nulls_not_distinct ON v4_analysis.artifacts
 (version,run_id,city,snapshot,definition_id,engine,validation,family,artifact,record_key) NULLS NOT DISTINCT;

-- Derive dimensions at read time: no backfill or table rewrite of completed
-- historical records, and no invented retrospective estimator/validation.
CREATE VIEW v4_analysis.artifact_dimensions AS
 SELECT a.*, split_part(definition_id,':',1) AS design_id,
 CASE WHEN split_part(definition_id,':',3)='' THEN split_part(definition_id,':',2)
 ELSE split_part(definition_id,':',3) END AS model,
 CASE WHEN split_part(definition_id,':',3)='' THEN 'primary'
 ELSE split_part(definition_id,':',2) END AS sensitivity
 FROM v4_analysis.artifacts a;
CREATE VIEW v4_analysis.aggregate_dimensions AS
 SELECT m.*, split_part(definition_id,':',1) AS design_id,
 CASE WHEN split_part(definition_id,':',3)='' THEN split_part(definition_id,':',2)
 ELSE split_part(definition_id,':',3) END AS model,
 CASE WHEN split_part(definition_id,':',3)='' THEN 'primary'
 ELSE split_part(definition_id,':',2) END AS sensitivity
 FROM v4_analysis.aggregate_metrics m;

CREATE FUNCTION v4_analysis.guard_definition_scope() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE parent_definition text;
BEGIN
 SELECT definition_version INTO parent_definition FROM v4_analysis.runs
 WHERE version=NEW.version AND run_id=NEW.run_id AND city=NEW.city AND snapshot=NEW.snapshot;
 IF parent_definition IS DISTINCT FROM split_part(NEW.definition_id,':',1) THEN
  RAISE EXCEPTION 'Model definition and parent scientific design mismatch';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER guard_definition_scope BEFORE INSERT ON v4_analysis.artifacts
 FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_definition_scope();
CREATE TRIGGER guard_definition_scope BEFORE INSERT ON v4_analysis.aggregate_metrics
 FOR EACH ROW EXECUTE FUNCTION v4_analysis.guard_definition_scope();
