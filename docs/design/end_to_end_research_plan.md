# End-to-end research plan

## Completed three-city analysis and thesis handover

Programme: MSc Social Data Science, University of Copenhagen. Updated: **14 October 2026**. Status: **scientific execution complete; this revision reconciles documentation**, rather than instructing another empirical rerun. Copenhagen denotes Copenhagen–Frederiksberg.

## 1. Authority, status and research questions

The 13 October attachments are pre-implementation drafts. They are historical inputs, not executable instructions for the current repository. The authoritative design is [config/study/design.json](../../config/study/design.json), with [the final specification](../analysis/preanalysis_specification.md), [the recorded amendment](../analysis/association_missingness_amendment_20261013.md), immutable SQL selectors and completed audits. Existing code and verified raw bytes supported the harmonized all-city rerun; completed results are now preserved during reporting/document changes. No reset, database replacement, reacquisition or model refit is requested by this revision.

| Research question | Current scope |
| --- | --- |
| RQ1 | Matched E/W accessibility measurement across cities. |
| RQ2 | Within-city predictive information and complementary adjusted associations. |
| RQ3 | Geographic generalization and neighbourhood/block heterogeneity. |
| RQ4 | Six directional source-only relative-price transfers. |

The attached proposal's three-question structure is superseded by this four-question reporting structure. The completed empirical evidence is observational. No causal housing/displacement claim, universal network superiority or claim that all directions are independent replications is allowed.

## 2. Scientific choices implemented

| Choice | Implemented definition |
| --- | --- |
| Listings | June 2026 detailed Inside Airbnb snapshots; Entire home/apt in the six conventional dwelling types. |
| Within-city outcome | Natural log of original positive observed nightly asking price in native currency. |
| Transfer outcome | Native log price minus the frozen city reference mean; transfer only. |
| Models | M0=X; ME=X+E; MW=X+W; MEW=X+E+W. |
| Controls | Common listing/dwelling, host, eight amenity, native density and OSM civic-distance controls; income and residential prices excluded. |
| Validation geography | 11 Copenhagen, 17 Oslo and 11 grouped Stockholm Inside Airbnb operational neighbourhoods. |
| Primary support | At least 15 final test observations and 500 complementary training observations; former 30 threshold retained diagnostically. |
| Analytical OSM snapshot | 2026-06-30T23:59:59Z for all three cities. |
| Primary accessibility | 5 km/h directed pedestrian graph, both snap connectors, 10-minute opportunities and matched rounded 833 m Euclidean radius. |
| Tuning | The same 30 XGBoost candidates and four geography-aware inner folds; training-only fitted preprocessing. |
| Association eligibility | Uniform 10% union required-predictor missingness limit, amended after observation; genuine complete cases only. |
| Persistent authority | Existing dedicated PostgreSQL/PostGIS analytical layer and immutable study packages. |

The 15-observation support decision preceded final fitting after support inspection. The later 5%→10% association decision followed observation of Stockholm's 5.8918% missingness. Both timings remain disclosed. Neither threshold is retrospectively called preregistered or a universal standard.

## 3. Sources, geography and context — COMPLETE

Raw listing bytes, original source strings, receipts and applied migrations remain unchanged. Selected files are checksum-, schema- and snapshot-verified; previous derived models are not substituted for the final harmonized estimates. The earlier acquisition-stage reference counts are retained separately from final feature-qualified samples.

| City | Raw listings | Conventional entire dwellings | Positive-price reference N | Prediction N | Association N | Holdout groups |
| --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | 23144 | 21080 | 12508 | 12408 | 12285 | 11 |
| Oslo | 13391 | 11776 | 8557 | 8529 | 8152 | 17 |
| Stockholm | 4806 | 3834 | 2510 | 2495 | 2348 | 11 |

Accepted masks determine membership with covers in EPSG:4326. Provider polygons determine operational validation groups, not current-official-boundary certification. Copenhagen normalizes the five documented source spelling/encoding variants; Oslo retains boroughs plus Sentrum/Marka; Stockholm preserves 14 raw labels and maps them to the fixed 11 operational groups. Source labels and original polygons are never rewritten. Unique assignments, overlaps/gaps, source/provider discrepancies and support are audited before modelling.

### Native density and centrality

Official population totals use their own qualified native-area denominators, not provider holdout polygon areas. Copenhagen uses 2026Q3 native district/municipal densities; Oslo uses 1 January 2026 population and native official 17-unit gross areas; Stockholm uses published 31 December 2025 borough populations and the 31 December 2024 gross land-plus-water area table, including its rounding and historical derivation caveats. Stockholm primary density is not a RegSO crosswalk aggregation. These boundaries and provider fold polygons have documented correspondence limits.

The exact [context audit](../analysis/context_audit.json) and [dictionary](../analysis/data_dictionary.md) preserve native IDs, periods, areas, source receipts and transformations. No unlocated population is distributed to groups or split source polygon. Frozen OSM civic anchors define analytical centrality; metric CRSs are Copenhagen EPSG:25832, Oslo EPSG:25833 and Stockholm EPSG:3006.

## 4. Networks and matched accessibility — COMPLETE

The common historical OSM timestamp, inherited destination taxonomy, deduplication, directed pedestrian restrictions, extraction extent and source/target connectors are frozen. Walking rail/bus measures minimize walking cost within the same category universe used by E. They are not constrained to the particular destination nearest in Euclidean distance. Counts use the common food/social and culture/tourism universes, transformed with log(1+count).

Network/destination coverage, connectors, components, boundaries, source failures and finite zero counts are qualified by [the accessibility audit](../analysis/accessibility_audit.json). Missing source/routing information remains missing; a reachable finite zero is an observed zero. Saved measurements support nearest-category distance excess, not same-object route circuity. The project builds the graph with its own audited pipeline; the draft's OSMnx-version requirement does not describe the executed implementation.

## 5. Samples, outcomes and preprocessing — COMPLETE

One common prediction sample per city is shared by every M0/ME/MW/MEW comparison. It requires observed price, qualified unique geography/context and common accessibility support. Listing-control missingness is explicit; predictive imputation, indicators and category encoding are fitted using training data only. No outer test or target city supplies fitted preprocessing statistics.

| City | Prediction N | Missing required predictors | Complete-case association N |
| --- | ---: | ---: | ---: |
| Copenhagen | 12,408 | 123 bedrooms (0.9913%) | 12,285 |
| Oslo | 8,529 | 376 bedrooms plus one minimum-night value (4.4202%) | 8,152 |
| Stockholm | 2,495 | 147 bedrooms (5.8918%) | 2,348 |

The common association sample is complete on X+E+W. The post-observation 10% rule permits the prescribed association procedure without filling missing bedrooms or outcomes. Missing prices remain excluded from every price model. Counts are verified from [the sample audit](../analysis/sample_audit.json) and [sample-flow table](../../outputs/tables/sample_flow.md).

### Frozen transfer references

Before feature filtering, each city reference includes eligible conventional entire dwellings with positive observed price inside its accepted mask. μ_city is mean log price over that population. There is one reference per city for every model and transfer direction.

| City | Reference N | Mean log price | Geometric mean asking price | Currency |
| --- | --- | --- | --- | --- |
| Copenhagen | 12508 | 7.505578 | 1818.156240 | DKK |
| Oslo | 8557 | 7.624645 | 2048.053064 | NOK |
| Stockholm | 2510 | 7.711207 | 2233.235220 | SEK |

Keep price_nightly, log_price and relative_log_price distinct. Only transfer subtracts μ_city. Reference populations and their source hashes are frozen independently of model-specific availability. Target outcomes enter their reference and scoring, not source fitting or calibration.

## 6. Within-city estimation and geographic validation — COMPLETE

Primary outer folds leave out each operational neighbourhood with the fixed 15/500 support gate. Random five-fold CV and six five-fold grids (1, 1.5 and 2 km, each at zero and half-grid origins) are distinct evaluation tasks. The inner search uses four size-balanced 1 km spatial-block folds and the preserved candidate list/seeds. Inner preprocessing is fitted anew; selected candidates are refitted on outer training data. No outer-test early stopping, feature selection or threshold tuning occurs.

Predictive OLS and XGBoost have saved held-out predictions and losses for each required model. Metrics are recomputed from those predictions. All five contrasts remain paired: ME−M0, MW−M0, MEW−M0, MW−ME and MEW−ME. ΔRMSE is candidate minus reference; negative is improvement. The 2,000 group-resampled ranges describe geographic-composition stability conditional on the predictions, not independent-sample inference or equivalence.

Primary XGBoost error is:

| City | M0 | ME | MW | MEW |
| --- | --- | --- | --- | --- |
| Copenhagen | 0.339247 | 0.330229 | 0.329782 | 0.328578 |
| Oslo | 0.349470 | 0.350149 | 0.350349 | 0.351829 |
| Stockholm | 0.406336 | 0.389245 | 0.386442 | 0.387750 |

All-model OLS/XGBoost metrics, folds and comparisons are in [the results](../../reports/research_results.md) and [paired contrasts](../../outputs/tables/paired_model_contrasts.md). Geographic evaluation is harder than random evaluation in the observed M0 tasks; gains vary by city, neighbourhood and block design. Do not replace heterogeneity with a universal ranking.

## 7. Source-only cross-city transfer — COMPLETE

The six separate directions are Copenhagen→Oslo, Copenhagen→Stockholm, Oslo→Copenhagen, Oslo→Stockholm, Stockholm→Copenhagen and Stockholm→Oslo. Source-relative models fit/tune on source observations only; preprocessing and the final source pipeline are applied unchanged to both targets. The 24 shared source pipelines produce 48 estimator/model-direction applications. No pooled source training, target intercept, target refitting, recalibration, target-driven encoder or alternative μ_city is introduced.

RMSE, MAE, R², Pearson and Spearman use the same target rows for each comparison. Paired target-neighbourhood resamples are conditional descriptive stability measures; directions share models/targets and are not independent replications. Target observed prices define the benchmark, so transfer is not absolute-price deployment to a market with unknown price level. [Transfer performance](../../outputs/tables/transfer_performance.md), [contrasts](../../outputs/tables/transfer_contrasts.md) and [directional diagnostics](../../outputs/metrics/directional_transfer_asymmetry.md) retain every direction. Optional median centring in the draft was not executed and is not now activated.

## 8. Associations, spatial checks and robustness — COMPLETE

The four common complete-case OLS association ladders use HC3 intervals, rank/condition/VIF diagnostics and 9,999 restricted Webb wild-cluster replications. Eight-neighbour Moran statistics with 499 seeded permutations triggered the registered heteroskedastic spatial-error association sensitivity for all three cities. Four-model area fixed-effect checks are complete, absorbing area-constant density. Predictive imputation is never used to manufacture inferential observations.

The [robustness registry](../../outputs/tables/robustness_registry.md) contains 75 city/check entries: 71 COMPLETE and four NOT_APPLICABLE. Its scope is:

| Family | Actual status and interpretation |
| --- | --- |
| Validation | Random five-fold, six fixed grids, former support threshold, 500/1,000 m geographic buffers complete. |
| Samples/controls | Apartment/condo-only, reviewed-only, training-only price tails and reputation checks complete on variant-common rows/folds. |
| Accessibility | 15/20-minute opportunities, 4/5.4 km/h speeds, continuous decay and boundary-near exclusion complete. |
| Density | Stockholm same-year/land-only variants complete; corresponding Copenhagen/Oslo alternatives explicitly not applicable. |
| Association | Area fixed effects and triggered spatial-error sensitivities complete. |

A predictive no-density run, matched-object circuity analysis and median-centred transfer were discussed in the attachments but are not completed registered results. Income and housing studies remain historical and are not reactivated. Variant rows/measurements can differ; robustness is not an absolute-score ranking. See [the comparison audit](../analysis/document_comparison.md) for these draft-to-execution distinctions.

## 9. Reporting and presentation — COMPLETED SCIENTIFIC HANDOVER

Every figure/table derives from pinned final SQL/predictions, not handwritten numerical substitutes. Current public presentation contains 18 figures (PNG only, 300 dpi) and 22 CSV/Markdown views: 12 tables and 10 supporting metric/diagnostic views. Ten figures/eight tables are suggested for the main thesis; eight additional figures and remaining detailed views are appendix evidence. Canonical paths are outputs/figures, outputs/tables and outputs/metrics, with reports under reports/.

Both neighbourhood maps show unchanged study groups within actual surrounding municipalities, white study borders, grey non-study borders and verified civic stars. Copenhagen's display star marks City Hall Square; Oslo/Stockholm use their verified City Hall anchors. Display context is separately qualified in cartography and has no sample/model role. Plotted endpoint/annotation clipping, source hashes, native CRSs, scale bars, square panels and minimum-five 500 m cells/bins have been checked. All other scientific results remain frozen.

[The results report](../../reports/research_results.md), [RQ synthesis](../../reports/findings_by_research_question.md), [claims](../final_claims_for_thesis.md) and [placement guide](../../reports/thesis_figure_recommendations.md) are the thesis-writing handover. This revision supplies updated [proposal](scientific_proposal.md) and reproducible Word exports of proposal/plan in docs/. Markdown is authoritative; PDF and results-report Word rendering remain outside this exporter. The local output README and portable ZIP were already deleted in the working tree when this document task began; these pending user changes are preserved. Historical package certificates describe the previously published package and are not a claim that it is currently present locally.

## 10. Scientific verification and preservation

The latest saved scientific verification checks 87 original source files, 38 receipts, 751 immutable analytical packages, 1,176 saved model files, 682 prediction packages and 20,460 fitted-code dependencies. It reproduces 48 target applications from the saved source pipelines and primary/transfer RMSE. The historical checks cover 1,695 protected files, 263 tracked baseline records and 20 original dedicated-store tables. These counts certify existing results, not new fitting by this document update.

Use one requirements.txt, one .env and the audited Python environment. Configuration is in config/study; scientific code is in src/study; provenance adapters are in src/provenance; display sources are in config/reporting and the separate cartography schema. Raw sources, row-level memberships/predictions and fitted models stay private. Original attachments, prior documents and their checksums are retained in the archive.

## 11. Remaining writing work and change control

The analytical rerun and required registered checks are complete. Remaining thesis work is to incorporate the factual handover into the narrative, review claims/citations with the supervisor, and finalize any requested document formatting. This plan does not claim that a submitted thesis manuscript or newly checked literature review has been completed.

Documentation/export steps are: compare the supplied drafts with actual evidence; preserve originals; update canonical Markdown; render the two Word copies; verify document structure, numbers, links and source hashes; update the document index/log; publish only intended safe changes on the existing v4 branch. Do not stage pending unrelated deletions or restore them merely to make an old package test pass.

Missing scientific data, ambiguous geography, model leakage or a changed dependency would require an explicit decision and affected-stage rerun. Do not change the 15/500 support thresholds, group mapping, OSM universe/speed/radius, candidate budget or transfer reference after seeing scores. Do not refit completed models solely because a pre-implementation attachment says to rerun them. Do not imply no-density/circuity/median-centred analyses ran when they did not. Preserve the 10% amendment's post-observation timing and every historical blocker record. Normal incremental commits go only to v4, with explicit remote verification; no reset, rebase, force-push or main/v3 modification.
