-- Neutral append-only analytical checkpoints; historical schemas remain untouched.
CREATE SCHEMA study;
CREATE TABLE study.schema_migrations (
 migration_name text PRIMARY KEY, file_hash_sha256 text NOT NULL,
 applied_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE study.checkpoints (
 run_id text NOT NULL CHECK(run_id ~ '^[a-z][a-z0-9_]*$' AND run_id !~ '(^|_)(v[0-9]+|a[0-9]+|version)(_|$)'),
 city text NOT NULL CHECK(city IN ('copenhagen','oslo','stockholm')),
 family text NOT NULL CHECK(family IN ('geography','context','accessibility','reference','sample','validation','within_city','transfer','robustness','reporting')),
 purpose text NOT NULL CHECK(purpose IN ('research','synthetic')),
 design_id text NOT NULL CHECK(design_id='three_city_accessibility_transfer'),
 snapshot date NOT NULL CHECK(snapshot=DATE '2026-06-30'),
 dependencies jsonb NOT NULL, dependencies_sha256 text NOT NULL CHECK(dependencies_sha256 ~ '^[0-9a-f]{64}$'),
 summary jsonb NOT NULL, summary_sha256 text NOT NULL CHECK(summary_sha256 ~ '^[0-9a-f]{64}$'),
 created_at timestamptz NOT NULL DEFAULT now(),
 creation_transaction xid8 NOT NULL DEFAULT pg_current_xact_id(),
 PRIMARY KEY(run_id,city,family)
);
CREATE TABLE study.records (
 run_id text NOT NULL, city text NOT NULL, family text NOT NULL,
 artifact text NOT NULL, record_key text NOT NULL, record jsonb NOT NULL,
 PRIMARY KEY(run_id,city,family,artifact,record_key),
 FOREIGN KEY(run_id,city,family) REFERENCES study.checkpoints
);
CREATE TABLE study.geometries (
 run_id text NOT NULL, city text NOT NULL, family text NOT NULL,
 geometry_key text NOT NULL, properties jsonb NOT NULL,
 geom geometry(MultiPolygon,4326) NOT NULL CHECK(ST_IsValid(geom) AND NOT ST_IsEmpty(geom)),
 PRIMARY KEY(run_id,city,family,geometry_key),
 FOREIGN KEY(run_id,city,family) REFERENCES study.checkpoints
);
CREATE FUNCTION study.refuse_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'Completed study records are immutable'; END $$;
CREATE FUNCTION study.guard_parent() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.creation_transaction <> pg_current_xact_id() THEN RAISE EXCEPTION 'Invalid checkpoint transaction'; END IF;
 IF (NEW.purpose='synthetic') <> (current_database() ~ '^test_study_[0-9a-f]{32}$') THEN
  RAISE EXCEPTION 'Synthetic/research database identity mismatch'; END IF;
 IF NEW.purpose='research' AND current_database()<>'thesis_accessibility_v4' THEN
  RAISE EXCEPTION 'Unapproved persistent research database'; END IF;
 RETURN NEW;
END $$;
CREATE FUNCTION study.guard_child() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NOT EXISTS (SELECT 1 FROM study.checkpoints p WHERE p.run_id=NEW.run_id AND p.city=NEW.city
  AND p.family=NEW.family AND p.creation_transaction=pg_current_xact_id()) THEN
  RAISE EXCEPTION 'Committed checkpoint cannot grow or mix cities'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER guard_parent BEFORE INSERT ON study.checkpoints FOR EACH ROW EXECUTE FUNCTION study.guard_parent();
CREATE TRIGGER guard_record BEFORE INSERT ON study.records FOR EACH ROW EXECUTE FUNCTION study.guard_child();
CREATE TRIGGER guard_geometry BEFORE INSERT ON study.geometries FOR EACH ROW EXECUTE FUNCTION study.guard_child();
CREATE TRIGGER immutable_parent BEFORE UPDATE OR DELETE ON study.checkpoints FOR EACH ROW EXECUTE FUNCTION study.refuse_mutation();
CREATE TRIGGER immutable_record BEFORE UPDATE OR DELETE ON study.records FOR EACH ROW EXECUTE FUNCTION study.refuse_mutation();
CREATE TRIGGER immutable_geometry BEFORE UPDATE OR DELETE ON study.geometries FOR EACH ROW EXECUTE FUNCTION study.refuse_mutation();
CREATE TRIGGER no_truncate_parent BEFORE TRUNCATE ON study.checkpoints FOR EACH STATEMENT EXECUTE FUNCTION study.refuse_mutation();
CREATE TRIGGER no_truncate_record BEFORE TRUNCATE ON study.records FOR EACH STATEMENT EXECUTE FUNCTION study.refuse_mutation();
CREATE TRIGGER no_truncate_geometry BEFORE TRUNCATE ON study.geometries FOR EACH STATEMENT EXECUTE FUNCTION study.refuse_mutation();
