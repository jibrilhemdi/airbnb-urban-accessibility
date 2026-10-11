-- Explicit V3 protocol amendment; applied migrations 001--021 remain unchanged.
ALTER TABLE v3_features.area_context DROP CONSTRAINT area_context_income_harmonisation_status_check;
ALTER TABLE v3_features.area_context ADD CONSTRAINT area_context_income_harmonisation_status_check
 CHECK(income_harmonisation_status IN ('verified','unverified','qualified'));
ALTER TABLE v3_features.area_context ADD COLUMN equiv_disposable_income_2024 numeric;
CREATE TABLE v3_features.qualified_area_income (
 analysis_area text PRIMARY KEY,
 reference_year integer NOT NULL CHECK(reference_year=2024),
 equiv_disposable_income_2024 numeric NOT NULL CHECK(equiv_disposable_income_2024>0),
 harmonisation_status text NOT NULL CHECK(harmonisation_status='qualified'),
 source_file_id bigint NOT NULL REFERENCES meta.source_files,
 record jsonb NOT NULL,
 CHECK(jsonb_array_length(record->'deciles')=10),
 CHECK(record->>'harmonisation_status'='qualified'),
 CHECK(record->>'analysis_area'=analysis_area),
 CHECK((record->>'equiv_disposable_income_2024')::numeric=equiv_disposable_income_2024)
);
COMMENT ON TABLE v3_features.qualified_area_income IS
 'Frozen source-derived KKIND5/nominal IFOR35 2024 common arithmetic decile means; qualified cross-source comparability. CSVs are exports.';
