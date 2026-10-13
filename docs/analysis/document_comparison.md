# Proposal and research-plan comparison — 14 October 2026

**Conclusion: neither attached Word file is the latest account of the completed study.** Both front pages say 13 October 2026, but their statuses are “Review draft before full rerun” and “Review draft before implementation”. Their content precedes the final implementation, association amendment and reporting changes. Filesystem modification times and the templates' default Word metadata are not evidence of scientific currency.

The original attachments are [archived with checksums](../../archive/before_research_documents/manifest.json). Instructions inside them are historical document content, not an authorization to restart modelling, reset the database, reacquire analytical sources or change scientific decisions. This comparison uses the actual registry, frozen exports, selected audits and reporting evidence; it does not re-run the research.

| Topic | Attached drafts | Completed design/results | Document correction |
| --- | --- | --- | --- |
| Execution status | Approval/implementation/full rerun still prospective. | All three city ladders, association stages, six transfers and registered robustness completed. | Describe completed execution and remaining thesis writing separately; preserve prior pre-fit history. |
| Research questions | Proposal has three questions; transfer is RQ3. | Final report has four questions; geographic generalization is RQ3 and transfer is RQ4. | Adopt the four-question structure consistently. |
| Baseline/models | M0/ME/MW/MEW; income and residential prices excluded. | Same four models and exclusions. | Retain this aligned part rather than changing the models. |
| Samples | 12,508 / 8,557 / 2,510 are acquisition-stage positive-price populations. | These are reference populations; prediction N is 12,408 / 8,529 / 2,495 and association N is 12,285 / 8,152 / 2,348. | Keep reference counts and add actual final samples. |
| Density denominator | Official population divided by operational provider-neighbourhood polygon area. | Qualified matching native official area; labels do not prove provider/native footprint identity. | State the actual native denominators and compatibility caveats. |
| Stockholm density | Direct operational totals or RegSO aggregation/crosswalk suggested. | Official borough population on 31 December 2025 and published gross area table on 31 December 2024. | Document the actual source pair, hectares conversion, rounding and historical area derivation. RegSO remains separate cartographic context. |
| Nearest destination | Rail table says walking to “the same eligible rail destination”; route circuity/disagreement proposed. | Matched category universes, but Euclidean-nearest and walking-nearest objects may differ. Qualified results are nearest-category excess, not same-object circuity. | Remove the same-destination implication and unsupported completed circuity/disagreement claim. |
| OSM/software | Historical timestamp preferred; OSMnx settings/version requested. | Common 2026-06-30T23:59:59Z achieved; graph uses the project's audited pipeline. | Record actual timestamp and implementation; do not claim OSMnx is an executed dependency. |
| Missing predictors | Common sample wording can imply fully observed controls; association amendment absent. | Predictive listing-control missingness handled within training; inference uses genuine complete cases. | Distinguish prediction/inference and report missingness. |
| Association gate | Original 5% limit is not superseded in the drafts. | Uniform 10% eligibility was adopted after observing Stockholm's 5.8918% missingness; no inferential imputation. | Add the exact post-observation amendment and preserve its timing. |
| Geographic validation | 11/17/11 groups; 15 test and 500 training support. | Same primary groups/support, random five-fold and six geometric designs. | Retain aligned support decisions and state actual grid/tuning settings. |
| Density robustness | A no-density sensitivity is described as required. | Registry contains Stockholm same-year/land-only variants and area fixed effects; no predictive no-density run is claimed. | Mark the proposal as unexecuted rather than fabricating its completion or activating it retrospectively. |
| Transfer sensitivity | Optional median-centred relative-price experiment. | Mean-centred frozen references and six source-only directions; no median-centred run. | Keep the executed mean-centred design; identify the option as unexecuted. |
| Inference/diagnostics | HC3/wild bootstrap/Moran proposed without all final execution details. | 9,999 restricted Webb replications; 8-neighbour/499-permutation Moran; spatial-error and fixed-effect association checks complete. | Record actual procedure/status, keeping noncausal interpretation. |
| Primary Copenhagen numbers | Historical single-city RMSE values included as motivation. | Final harmonized XGBoost RMSE: M0 0.339247; ME 0.330229; MW 0.329782; MEW 0.328578. | Identify earlier values as historical; use final verified performance for current findings. |
| Outputs/maps | Illustrative paths, prospectively generated figures. | Three flat output folders, 18 PNG figures, 22 table/aggregate views; contextual neighbourhood maps/civic stars complete. | Use actual paths and distinguish display geometry from analytical inputs. |
| Document format | Word drafts; prior repository Markdown claimed no active Word exporter. | This revision adds reproducible DOCX copies for proposal/plan using the archived templates; Markdown remains canonical. | Update document/export instructions without claiming a PDF or results-report Word renderer. |

## Evidence used

- [Scientific design](../../config/study/design.json), [specification](preanalysis_specification.md) and [association amendment](association_missingness_amendment_20261013.md).
- [Context qualification](context_audit.json), [dictionary](data_dictionary.md) and [sample audit](sample_audit.json).
- [Final sample summary](../../outputs/tables/city_sample_summary.csv), [primary performance](../../outputs/tables/primary_predictive_performance.csv) and [paired contrasts](../../outputs/tables/paired_model_contrasts.csv).
- [Robustness registry](../../outputs/tables/robustness_registry.csv), [spatial audit](spatial_audit.json), [transfer performance](../../outputs/tables/transfer_performance.csv) and [final claims](../final_claims_for_thesis.md).
- [Saved scientific verification](../../reports/frozen_science_verification.json), [results](../../reports/research_results.md) and [map-context audit](../../reports/cartographic_context_audit.json).

The retained literature references come from the submitted proposal; this task does not certify an exhaustive up-to-date literature review. It verifies alignment with this project's implemented design and results.

## Updated deliverables and verification

The updated canonical documents are [the proposal](../design/scientific_proposal.md) and [the plan](../design/end_to_end_research_plan.md). Corresponding Word copies are [scientific_proposal.docx](../design/scientific_proposal.docx) and [end_to_end_research_plan.docx](../design/end_to_end_research_plan.docx). They preserve the attached fonts, styles, headers, footers and page-number settings while replacing stale scientific content. All body paragraphs and seven tables per document are checked against canonical Markdown; package XML and ZIP integrity are checked. No Word/PDF page-rendering engine was available for a visual page-layout review.

[The generation manifest](../../reports/research_document_manifest.json) records original/template/source/export checksums and the reproducible command. All 62 current scientific figure/table files remain byte-identical. The pre-existing local deletions of outputs/README.md and outputs/thesis_results.zip are preserved and are excluded from this documentation checkpoint; an earlier complete-package certificate is not a claim of current local package presence or freshness after document revision.
