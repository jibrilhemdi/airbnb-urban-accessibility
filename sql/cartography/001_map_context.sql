-- Presentation context only: no study samples, features or fitted packages.
CREATE SCHEMA IF NOT EXISTS cartography;
CREATE TABLE cartography.schema_migrations (
    migration_name text PRIMARY KEY,
    sha256 text NOT NULL
);
CREATE TABLE cartography.sources (
    source_id text PRIMARY KEY,
    metadata jsonb NOT NULL
);
CREATE TABLE cartography.features (
    city text NOT NULL,
    feature_key text NOT NULL,
    role text NOT NULL CHECK (role IN ('surrounding_municipality','civic_reference')),
    source_id text NOT NULL REFERENCES cartography.sources(source_id),
    properties jsonb NOT NULL,
    geom geometry(Geometry,4326) NOT NULL,
    PRIMARY KEY (city,feature_key),
    CHECK (ST_IsValid(geom) AND NOT ST_IsEmpty(geom))
);
CREATE FUNCTION cartography.refuse_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Cartographic sources/features are immutable';
END;
$$;
CREATE TRIGGER sources_immutable BEFORE UPDATE OR DELETE ON cartography.sources
FOR EACH ROW EXECUTE FUNCTION cartography.refuse_mutation();
CREATE TRIGGER features_immutable BEFORE UPDATE OR DELETE ON cartography.features
FOR EACH ROW EXECUTE FUNCTION cartography.refuse_mutation();
