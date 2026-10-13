# Active research document and artifact index

Copenhagen denotes the combined Copenhagen–Frederiksberg study area. The exact
comprehensive request supersedes the dated single-step instructions; original
documents and statuses remain historical evidence.

| Document or location | Purpose |
| --- | --- |
| [Scientific proposal](../scientific_proposal.md) | Four research questions, implemented model structure and claim discipline |
| [Implementation contract](implementation_contract.md) | Scientific/data/Git scope and immutable checkpoint rules |
| [Association amendment](association_missingness_amendment_20261013.md) | Explicit post-observation change from 5% to 10%, uniformly across cities |
| [Specification](preanalysis_specification.md) | Frozen outcomes, features, validation, tuning, inference and sensitivities |
| [Research plan](research_plan.md) | Dependency order and implemented versus blocked work |
| [Dictionary](data_dictionary.md) | Source-parsed controls, density, civic distance and matched E/W definitions |
| [Source registry](source_registry.md) | Source selection, acquisition/reuse requirements and qualifications |
| [Decision log](decision_log.md) | Explicit researcher amendment and pre-fit scientific choices |
| [Deviations](deviations_from_preanalysis.md) | Corrections, operational warnings, scientific gates and interpretation |
| [Execution log](execution_log.md) | Actual computations, tests, checkpoints and blockers |
| [Reproducibility](reproducibility.md) | Commands, SQL authority, private artifacts, immutability and preservation |
| [Publication research handover](research_report_publication.md) | Reviewed scientific tables/figures and full release status |
| [Generated findings](findings.md) | SQL-derived RQ interpretation, geographic consistency and transfer patterns |
| [Research handover](research_report.md) | Regenerated three-city association handover before publication additions |
| [Publication review](publication_audit.json) | Preserved predictive figures and freshly regenerated three-city association publication |
| [Checkpoint history](checkpoint_history.json) | Actual incremental commits before final publication; final SHA supplied externally |
| [Release audit](release_audit.json) | Independent source/model/output/migration/branch verification |
| [Output inventory](public_output_inventory.json) | Generated aggregate artifact hashes and sizes |
| [Publication output inventory](publication_output_inventory.json) | Initial and reviewed presentation artifacts with checksums |
| [Software environment](software_environment.json) | Actual Python/platform/library versions |
| [Geography audit](geography_audit.json) | Raw/polygon/group assignment, topology, support and reference samples |
| [Context audit](context_audit.json) | Native densities, exact sources, anchors, CRS and limitations |
| [Accessibility audit](accessibility_audit.json) | Directed graph/destinations, failures, coverage and matched features |
| [Sample audit](sample_audit.json) | Source attrition, common samples, missingness and fold support |
| [Pre-fit freeze](prefit_freeze.json) | Frozen source/feature/sample/fold/candidate evidence before fitting |
| [Association audit](association_audit.json) | Freshly completed three-city complete-case inference under the disclosed 10% rule |
| [Association recalculation](association_recalculation_audit.json) | Independent OLS/HC3/VIF and prescribed wild-cluster/Moran reproduction |
| [Archive manifest](archive_manifest.json) | Authorized relocations with original checksums and the explicit discarded-ZIP exclusion |
| [Missingness source audit](missingness_source_audit.json) | Read-only confirmation that Stockholm's missing bedrooms are original source blanks |
| [Spatial audit](spatial_audit.json) | Moran diagnostics, registered trigger and dependent checks |
| [Robustness audit](robustness_audit.json) | Exhaustive COMPLETE/BLOCKED/INFEASIBLE/NOT_APPLICABLE registry |
| [Initial path inventory](path_inventory.json) | Pre-change bytes, compatibility extension and archived entries |
| [Historical store inventory](historical_store.json) | Exact20 preserved dedicated-store table fingerprints |
| [Exact researcher request](../../archive/research_request/request.txt) | User-authorized comprehensive scientific amendment |
| [Prior entry snapshots](../../archive/previous_scope/README.md) | Preserved original instructions and entry documentation |

`config/study/` holds canonical city/model registries and immutable selectors.
`outputs/tables/research/`, `outputs/figures/research/` and functional
`outputs/metrics/<scheme>/` contain generated aggregates. Private raw files,
model bytes, row predictions and memberships stay under ignored source/run
locations and authoritative PostGIS packages. A listed expected final file is
not a completion claim; the release audit and execution log establish status.

Historical documents retain their original bytes and applied identifiers in the consolidated archive.
They do not reactivate retired source/model prerequisites or provide final
numerical results for the amended rerun.
