# Version 3 migration and rerun audit

Explicit income protocol amendment accepted on 4 October 2026. Preflight: passed.
Income decision: qualified_accepted; metadata: qualified. Full empirical execution status: complete.

The successful V3 refactor remains intact. Prior source/module/output mappings and original audit records are preserved in docs/migration_mapping.json, archive/legacy_v2 and the checksum archive of the expanded municipal income investigation.
Original analytical schemas and all historical source investigations remain preserved. Raw sources are immutable; PostgreSQL/PostGIS remains authoritative. Aggregate CSVs are exports.

Applied migration hashes verified: 22. Original migrations 001–021 are unchanged. Additive migration 022 creates qualified_area_income and adds its transparent context field.

Verified raw files: 204; preserved legacy files: 793.

## Income amendment

Area income is operationalised as 2024 equivalised disposable income derived from decile means. Copenhagen city-district values use Copenhagen Municipality's KKIND5, while Frederiksberg uses Statistics Denmark's nominal IFOR35. Both sources represent closely aligned equivalised-disposable-income concepts and use ten person-based decile groups, but some table-specific processing details cannot be proven identical. The measure is therefore treated as pragmatically harmonised. All primary models include the measure, and a prespecified no-income robustness analysis tests whether substantive accessibility conclusions depend on this cross-source context variable.

Eleven rows / 110 observed decile means; common transformation: (d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8 + d9 + d10) / 10. Authoritative SQL table: v3_features.qualified_area_income. Full deciles/provenance/basis/SHA/qualification export: outputs/tables/area_context/qualified_area_income_2024.csv.

Supportive Copenhagen published-total QA: 340620.1 vs 340949.1 DKK, −329 DKK, −0.0964953%, tenth decile −3376 DKK. Missing eligible weights remain NULL; this is not proof of exact equivalence.

Mandatory M0_no_income/ME_no_income/MW_no_income/MEW_no_income (OLS and XGBoost) omit only income, reusing the primary sample and saved random-five/geographic-eleven outer and inner-four folds, preprocessing and thirty candidates. The complete audit requires paired metrics, OLS accessibility coefficients, ΔRMSE, all area results and conclusion flags.

## Documentation and checks

Updated both repository V3 DOCX copies, specification, decision log, income status, data dictionary, source inventory and reproducibility metadata. Original Downloads documents and every non-document DOCX member remain unchanged.
qualified_income_tests.txt: 81 discovered; 58 passed; 23 explicitly skipped
qualified_income_database_tests.txt: 81 discovered; 65 passed; 16 explicitly skipped

Blocking preflight checks: [].

## Dependency order

1. airbnb_sample — src.pipeline.build_airbnb_sample.main
2. context_sources — src.pipeline.ingest_area_context.main
3. analysis_areas_and_centrality — src.pipeline.build_spatial_features.main
4. core_area_context — src.pipeline.build_area_context.build
5. frozen_osm_inputs — src.pipeline.acquire_osm.acquire
6. rail_and_opportunity_taxonomy_and_euclidean — src.pipeline.build_euclidean_accessibility.main
7. bus_taxonomy_deduplication_and_euclidean — src.pipeline.build_bus_euclidean_accessibility.run
8. walking_graph_and_rail_opportunities — src.pipeline.build_walking_accessibility.main
9. core_bus_walking — src.pipeline.build_bus_walking_accessibility.run
10. walking_exports — src.pipeline.export_walking_accessibility.export
11. accessibility_quality — src.pipeline.qa_accessibility.run
12. matched_destination_boundary — src.pipeline.audit_destination_boundary.run
13. price_observability — src.pipeline.audit_price_observability.run
14. frozen_analysis_dataset_and_dictionary — src.pipeline.build_analysis_dataset.build
15. outer_and_inner_validation_splits — src.pipeline.build_validation_splits.build
16. primary_ols_xgboost_oof_uncertainty_and_heldout_shap — src.pipeline.run_primary_models.run
17. mandatory_no_income_robustness — src.pipeline.run_income_robustness.run
18. spatial_diagnostics — src.pipeline.run_spatial_diagnostics.run
19. threshold_speed_and_decay_features — src.pipeline.build_opportunity_variants.build
20. accessibility_sample_covariate_and_spatial_robustness — src.pipeline.run_robustness_analyses.run
21. conditional_spatial_error_robustness — src.pipeline.run_spatial_error_robustness.run
22. publication_tables_figures_and_report — src.pipeline.build_final_outputs.run
23. claims_audit — src.pipeline.export_claims_audit.run
24. latex_and_presentation — src.pipeline.prepare_final_outputs.run
25. reproducibility_audit — src.pipeline.audit_reproducibility.audit_run

## Execution evidence

Run research_v3_20261004T111510Z; completed components: airbnb_sample, context_sources, walking_exports, core_bus_walking, core_area_context, frozen_osm_inputs, price_observability, accessibility_quality, matched_destination_boundary, analysis_areas_and_centrality, mandatory_no_income_robustness, outer_and_inner_validation_splits, walking_graph_and_rail_opportunities, frozen_analysis_dataset_and_dictionary, bus_taxonomy_deduplication_and_euclidean, rail_and_opportunity_taxonomy_and_euclidean, primary_ols_xgboost_oof_uncertainty_and_heldout_shap, spatial_diagnostics, threshold_speed_and_decay_features, accessibility_sample_covariate_and_spatial_robustness, conditional_spatial_error_robustness, publication_tables_figures_and_report, claims_audit, latex_and_presentation, reproducibility_audit.
No recorded execution error.

Material OLS missingness above 5% remains an independent scientific stop pending the specified multiple-imputation/pooling implementation. No inferential substitute or silently overwritten/resumed namespace is permitted.

## Final validation

Run `research_v3_20261004T111510Z` completed all 25 dependency stages. The complete analytical reproducibility audit and mandatory no-income audit passed. The final opt-in integration suite passed all 89 tests with no skips; earlier named test logs above record the initial adoption checks.

The frozen sample contains 12,412 listings, including 1,304 in Frederiksberg. All ten robustness specifications completed; their 784 outer-fold/feature-set tuning groups each evaluated the frozen 30 candidates. All 67 income-investigation archive files still match their checksum manifests. Both working-tree formatting checks passed. Final verification metadata: `outputs/tables/reproducibility/qualified_income_final_validation.json`.
