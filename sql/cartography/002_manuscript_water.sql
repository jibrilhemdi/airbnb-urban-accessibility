-- Display-only hydrography. Never used for masks, areas, samples or modelling.
CREATE TABLE cartography.manuscript_water (
    city text PRIMARY KEY,
    source_metadata jsonb NOT NULL,
    geom geometry(MultiPolygon,4326) NOT NULL,
    CHECK (ST_IsValid(geom) AND NOT ST_IsEmpty(geom))
);
CREATE TRIGGER manuscript_water_immutable
BEFORE UPDATE OR DELETE ON cartography.manuscript_water
FOR EACH ROW EXECUTE FUNCTION cartography.refuse_mutation();
