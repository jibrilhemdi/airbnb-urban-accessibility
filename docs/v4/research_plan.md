> **Live A02 reconciliation — 11 October 2026.** Active design:
> `v4_accessibility_only_20261011`. The canonical executable registry and
> separate new-design configuration now implement X/E/W without housing.
> Historical configurations, source ledgers and receipts remain immutable.
> Full empirical readiness remains BLOCKED by A03–A07 and genuine city inputs;
> no acquisition, routes, sample/fold creation or fitting occurred in A02.
> V3 results and housing feasibility were already known; supervisor approval
> is not recorded. [A02 implementation audit](pipeline_scope_audit_A02_20261011.md)
> records the actual implementation and tests; the [A01 audit](current_state_audit_20261011.md)
> retains its original checkpoint evidence and input-version discrepancies.
>
> **Baseline reconciliation resolved under A02:** the instruction to remove
> only housing-derived active dependencies retains categorical `property_type`
> from the actual frozen v3 baseline, alongside the 17 numeric/amenity/context
> controls. This explicitly supersedes the supplied revision's prose exclusion;
> the supplied bundle itself remains unchanged. See [model_contract.md](model_contract.md).

# End-to-End Research Plan
## Urban accessibility and Airbnb asking prices
### Copenhagen–Frederiksberg · Oslo · Stockholm

**Version 4 revised · Accessibility-only amendment · 11 October 2026**

**Scientific design:** `v4_accessibility_only_20261011`
**Git branch:** existing `v4`
**Execution prompts:** A01–A12; these replace the unexecuted housing-inclusive prompts.

## Research contract

Extend the completed v3 accessibility study to two additional cities. Keep the listing-level log asking-price outcome, matched Euclidean/walking measures, baseline controls, OLS, XGBoost and spatial validation. Remove residential property prices from the active design entirely. Do not substitute rents, current property advertisements or a new gentrification outcome.

The primary models are M0 = X; ME = X + E; MW = X + W; MEW = X + E + W. All four share a common prediction sample and folds within each city. There is no H, H-suffixed model family, housing-qualified sample or housing-based validation rule.

## Current starting point

The supplied audits document three acquired June 2026 listing snapshots, a resolved operational Stockholm municipal mask, an unresolved Oslo boundary-vintage issue and partial housing-source acquisition [A1–A4]. They do not document completed three-city accessibility models. The complete live repository and current Git state must be inspected by Codex; this document does not claim to have accessed or modified them.

Preserve the completed v3 research and all v4 acquisition evidence. Mark housing work as discontinued for the new design, not as failed coding or successfully qualified data. Do not delete its records or undo commits. The original main/v3 branches and historical database ledgers remain untouched.

**Reading map.** Sections 1–3 define scope and data readiness; 4–8 specify measurements, samples and estimation; 9–10 define robustness and execution controls; 11–13 provide checkpoints, outputs and release tests. The companion proposal explains the literature and contribution. Numerical rules below are inherited or explicitly labelled project decisions, not statistical-power guarantees.

<!-- PAGE -->
# 1. Scope amendment and decision history

## 1.1 Active and retired components

| Component | Revised decision |
|---|---|
| Cities | Copenhagen–Frederiksberg, Oslo, Stockholm; same batch, separate models |
| Outcome | Log original positive observed Airbnb advertised nightly price |
| Baseline X | Inherited listing/host/amenity controls, density, qualified income, centrality |
| Models | M0, ME, MW, MEW; predictive OLS and XGBoost |
| Geographic evaluation | Official-area holdouts plus common geometric sensitivities |
| Residential prices | Removed from model inputs, samples, readiness gates and analyses |
| Housing acquisition | Preserve as historical evidence; do not pursue providers or portals |
| Causal housing/gentrification | Outside scope |
| V3 | Immutable historical results and accepted scientific decisions |

No-income is not synonymous with no-housing. Housing is excluded everywhere by the new scope; income remains a separate inherited control and sensitivity question.

RQ1 compares matched accessibility representations; RQ2 evaluates their paired
predictive information; RQ3 compares geographic/random validation and cities.
The former housing RQ4 is withdrawn.

## 1.2 Knowledge and authorization

Record that Copenhagen v3 estimates and the housing feasibility audits were already observed. The user has explicitly authorized a change of scope, not a claim of supervisor approval or a retrospective pre-registration. Freeze the revised design before viewing new-city conditional price-model results. Data inspection may establish schema, coverage, missingness and fold feasibility, but must not select sources or geographies based on model scores.

The active document index must state that this plan and proposal supersede housing-inclusive v4 instructions. Preserve old scientific statements in dated history rather than applying a global search-and-replace to all files. Old housing statuses remain BLOCKED where historically true; a separate design-dependency entry becomes NOT_REQUIRED_SCOPE_AMENDED.

## 1.3 Definition and run identity

Store `design_id`, city, snapshot, `run_id`, estimator, model, validation and sensitivity variant separately. Use the four canonical model labels only. A new v4 M0 row cannot be confused with either v3 M0 or housing-inclusive v4 M0. Reuse raw data through explicit approved source-manifest links rather than duplicate imports. New feature/model outputs receive new identities; legacy receipts and applied migration bytes remain unchanged.

<!-- PAGE -->
# 2. Listing acquisition and municipal geography

## 2.1 Reuse verified acquired files

| City | Raw | Eligible dwelling | Positive price | Inside operational mask and positive |
|---|---:|---:|---:|---:|
| Copenhagen–Frederiksberg | 23,144 | 21,080 | 12,521 | 12,508 |
| Oslo | 13,391 | 11,776 | 8,557 | 8,557 |
| Stockholm | 4,806 | 3,834 | 2,510 | 2,510 |

Counts are reported in A1, with Stockholm replaced only by the superseding A2 evidence. They are not final feature-qualified samples. Verify live SQL scopes/hashes before reuse; do not force new counts to match historical values or sum superseded ingestions as extra listings. Do not redownload the same Airbnb batch simply because the modelling design ID changes.

Retain room type Entire home/apt and the six frozen dwelling labels. Audit price parsing, unique observation keys, source schema, missing prices and scope. Preserve raw quote fields for QA without substituting them for the original price. Record scrape, batch, requested stay and actual returned-stay evidence independently [A1].

## 2.2 Stockholm: preserve the accepted municipal mask

A2 documents SCB RegSO 2025_v2, reference 2025-01-01, EPSG:3006, municipality 0180. The 127 selected valid areas dissolve into the operational municipal union; the amendment records checks and limits on exact 2026 certification. Retain that freeze and its 150-metre outer-boundary flags. It does not authorize automatic district assignments or 127 cross-validation clusters.

## 2.3 Oslo: targeted operational-vintage decision

A1 reports a verified current-at-retrieval municipality polygon with unverified reference vintage. A03 authorizes a targeted recovery, not silent approval: seek official vintage/change information or a source-dated polygon; verify municipality ID, licence, topology, coverage and independent metadata. If exact June 2026 linework is unavailable but checks support operational use, create a dated amendment accepting the stated source vintage with explicit limitations. Never claim that matching total area proves identical linework. If evidence is inadequate or conflicting, keep dependent analysis blocked.

Preserve original receipts and a newly qualified geometry under a new source identity. Do not redownload Airbnb. Municipal masks, analysis areas and statistical-source areas are separate objects.

<!-- PAGE -->
# 3. Analysis areas and baseline context

## 3.1 Official analysis geography

Preserve the ten Copenhagen districts plus Frederiksberg as eleven peer analysis areas. Obtain authoritative Oslo and Stockholm borough/district polygons with IDs, reference date and licensing. Select the level based on substantive comparability, source compatibility and eligible-listing support, not outcomes. Freeze a complete, nonoverlapping assignment with deterministic boundary-tie handling.

For new-city administrative holdouts, inspect eligible counts and polygon sizes. Where a small area cannot meet the declared test threshold, use a deterministic, geographically justified adjacent-area grouping fixed before fitting, or report the design infeasible. Never rename provider neighbourhood strings as official districts. RegSO may serve a separately approved analysis geography only after its suitability is evaluated; the municipal-mask construction is not that approval.

## 3.2 Density and centrality

Retain log population density and public civic-centre distance. Use gross qualified polygon area, document inclusion of water, and preserve original population reference periods and denominators. Do not substitute listing density or rescale district totals to an unrelated municipal total. Qualify each city’s metric CRS and anchor coordinates. Copenhagen’s accepted v3 definitions remain the starting point; do not copy its CRS or City Hall coordinate into other cities.

Prefer coherent reference periods, but disclose any necessary timing difference. These are spatial explanatory models using documented external data, not a real-time June forecasting exercise. Post-snapshot publication and historical reference period are separate fields.

## 3.3 Income protocol

Preserve Copenhagen’s accepted KKIND5/nominal IFOR35 2024 equivalised-disposable-income construction: the arithmetic mean of ten decile means, divided by 100,000 DKK for its v3 model scale. Its documented harmonisation qualifications remain [P1].

For Oslo and Stockholm, inspect official measures of disposable income/resources with explicit unit, population, household-equivalence treatment, period and geography. The old housing-source qualification does not prove income coverage. Preserve native values; any common transformation is specified before fitting and learned scaling is training-only. Do not substitute gross earnings or median income while labelling it identical to the Copenhagen measure.

Default: qualified income in X, with matched no-income sensitivity. If a defensible common income specification cannot be qualified, write a pre-fit decision for a common no-income comparative baseline and separately labelled local income analyses. Do not silently vary the primary feature concept by city. The fallback requires an explicit researcher decision; expensive fitting pauses until the mode is frozen, while safe measurement work may continue.

<!-- PAGE -->
# 4. Accessibility construction and QA

## 4.1 Matched feature blocks

| Family | E | W |
|---|---|---|
| Rail/metro/commuter access | Nearest eligible destination distance, km | Nearest reachable eligible destination, minutes |
| Bus access | Nearest consolidated stop distance, km | Nearest reachable consolidated stop, minutes |
| Food/social opportunities | log1p count within 833 m | log1p count within 10 minutes |
| Culture/tourism opportunities | log1p count within 833 m | log1p count within 10 minutes |

“Nearest” is computed within each representation over the same eligible destination universe; the nearest object need not be the same. The walking speed is exactly 5 km/h = 83.333… metres/minute. The 833-metre Euclidean radius is rounded; inequalities use the exact budget where necessary. A walking route must include origin and destination connector distances [P1].

## 4.2 Destination taxonomy and networks

Reuse the v3 rail/POI definitions and deterministic bus consolidation: same-representation compatible objects within 3 metres, unnamed objects within 0.5 metres; mutually nearest compatible platform/stop-position pairs within 25 metres. Preserve conflicting references and opposite carriageways rather than merging solely on shared names. Keep original objects, canonical keys and decision reasons.

Audit local tagging, duplicate stations, tram/rail-category treatment and destination completeness before fitting. Adding new local categories requires a documented concept-matching decision, not a price-driven improvement. Respect pedestrian access, direction and network topology; bridges/underpasses are not connected by proximity alone.

Use a >=2-kilometre extraction buffer as a starting coverage rule, expanding when nearest-destination and route checks require it. Separate municipal listing selection from the wider routing/destination extraction. Unreachable access, a genuine zero count and missing extraction data must remain different states.

## 4.3 Temporal and cache consistency

Record graph/POI source timestamps, extracts, CRS, taxonomy and algorithm hashes. Audit whether Copenhagen’s cached v3 measures are comparable to the new cities’ extraction policy. Reuse only on matching dependencies; otherwise compute new Copenhagen features inside v4 without overwriting v3. Current OSM does not certify June 2026 topology. Freeze a common defensible extraction strategy and disclose residual temporal mismatch.

QA covers snap distances, route length, reachability, disconnected components, edge effects, E/W discrepancies and opportunity-count checks. Use public locations for illustrative catchments. No GTFS, scheduled transit times, automatic new routing modes or new amenity families are required.

<!-- PAGE -->
# 5. Samples, missingness and freezes

## 5.1 Three distinct data states

**Acquisition audit universe:** all imported listings plus eligibility, boundary and price flags. Missing-price eligible dwellings remain available for selection diagnostics.

**S_pred(city):** eligible conventional dwellings with positive observed price, valid municipal/analysis-area assignment and common accessibility support. Every primary model and predictive estimator uses the same ordered keys/outcomes within the relevant comparison. There is no housing-price filter and no inherited H-qualified row subset.

**S_assoc(city):** a common OLS association sample derived under the inherited <=5% any-required-predictor missingness rule. Record its difference from S_pred. Above that threshold, pause inferential OLS until a validated missing-data approach is specified; do not present training-median-imputed coefficients as completed inferential analysis.

## 5.2 Predictor treatment

Recover exact v3 parsing for effective bathrooms, amenities, host fields and transformations. Retain the actual inherited categorical `property_type` control under the A02 remove-only-housing instruction, as well as the inherited numeric controls. Do not add coordinates, reviews, revenue, availability, area IDs or municipality flags as undeclared primary predictors. Add reviews/reputation only in their registered sensitivity.

Fit learned medians, encoders, indicator rules and scaling within each inner training split and then the outer training partition. Test entirely missing training columns explicitly. Never impute Y. H and housing-derived columns are excluded by a canonical feature whitelist, not merely left missing.

Report exclusion flow and missingness by city, area and dwelling category. Do not select the final dataset from a discontinued housing table or require non-null `native_housing_area_id`. Historical nullable housing fields may remain in raw audits but have no analytical eligibility role.

## 5.3 Freeze sequence

1. **Source/measurement freeze:** selected source scopes, municipal and analysis polygons, context selections, OSM extracts and definitions.
2. **Design/sample freeze:** baseline income mode, canonical feature blocks, eligible observation IDs, sensitivity rules and thresholds.
3. **Validation/execution freeze:** outer/inner memberships, candidate list, code/environment dependencies and run manifest.

All are established before empirical model comparison. A corrected source, changed feature parser or amended fold policy creates a new dependency identity and marks affected results for replacement. An editorial document change alone must not imply that fitted models were rerun.

<!-- PAGE -->
# 6. Model definitions and comparative estimands

## 6.1 Exact baseline

X contains accommodates; bedrooms; effective bathrooms; log1p minimum nights; superhost; log1p host listings; Wi-Fi; dishwasher; washer; dryer; workspace; free parking; private balcony; self check-in; log population density; qualified income under the frozen income mode; and central-anchor distance.

| Label | Model inputs |
|---|---|
| M0 | X |
| ME | X + E |
| MW | X + W |
| MEW | X + E + W |

Fit predictive OLS and XGBoost separately for each city. Association OLS is a separate analysis family. A training-mean prediction is a benchmark, not a fifth substantive model. No primary model requires residential prices or receives an H suffix.

## 6.2 Paired questions

| Comparison | Question |
|---|---|
| ME minus M0 | Does Euclidean accessibility add information? |
| MW minus M0 | Does walking accessibility add information? |
| MEW minus M0 | Does the combined block add information? |
| MW minus ME | Does replacing E with W help? |
| MEW minus ME | Does W add information beyond E? |

The final row is explicit in the revised design; it was not listed among v3’s frozen paired comparisons. Report it as an amendment. The two network contrasts answer different questions and must not be interchanged.

Define Delta RMSE = RMSE_added − RMSE_reference. Negative values favour added information. Define proportional improvement = 100 × (RMSE_reference − RMSE_added) / RMSE_reference. Calculate from matched OOF predictions, not averages of unmatched model folds. Use MAE and R² as complementary metrics; undefined fold R² remains missing with a reason.

## 6.3 City comparison

Report all city estimates, relative changes, fold distributions and equal-area summaries. Cross-city synthesis is primarily descriptive and does not pool raw nightly prices in different currencies. Log-error scores still depend on sample mix and task difficulty, so proportional gains and benchmark performance are important. Do not interpret the biggest absolute error as the least valuable network or as an institutional effect.

No new fourth research question requires urban-form covariates. Route disagreement may be related descriptively to where gains occur using existing outputs, labelled exploratory and kept separate from the primary comparisons.

<!-- PAGE -->
# 7. Geographic validation and support

## 7.1 Primary administrative holdouts

Keep Copenhagen’s eleven-area leave-one-area-out design where qualification supports it. Use frozen official-area holdouts in Oslo and Stockholm, with predetermined sparse-area grouping where justified. Preserve exact rows/folds across all four models and both predictive estimators. Store the actual number and geometry of held-out areas; do not copy “geographic_11” into every city.

Apply the inherited 500-training/30-test minimum to new-city primary folds as an explicit revised safeguard. It is not a guarantee of stable OLS clusters or statistical power. Report counts, area size, price-free covariate support and extrapolation indicators before fitting. If a valid fold design cannot be constructed, hold that city’s empirical run and document the issue rather than silently use random validation.

## 7.2 Other evaluation settings

Random five-fold outer validation uses seeded shuffled listings and the same prespecified tuning policy. It estimates another interspersed listing in the same city. Administrative-area constants in external context may span random train/test partitions; that does not make them target-derived, but the resulting task is different from withholding an area [R6].

The common geometric sensitivity uses five folds of 1.5-kilometre spatial blocks, at zero and diagonal half-block shifts. The original 1- and 2-kilometre grids and 500/1,000-metre holdout buffers are retained in the robustness registry. Every declared variant is reported; no grid is selected by outcome. City-appropriate projections and block origin rules are frozen.

The old H-area nesting requirement is withdrawn. Do not carry forward housing-based minimum-area counts, group medians or fold labels. Conversely, housing removal is not permission to ignore spatial separation altogether.

## 7.3 Inner tuning and uncertainty

Retain four training-only spatial inner folds based on 1-kilometre blocks, deterministic group-size balancing and inherited seeds. Inner folds are recomputed within each outer training scope without using the held-out outcomes. Freeze membership before tuning. Verify inner-fold feasibility and no overlap with the outer test set.

For geographic performance stability, resample whole matched held-out groups 2,000 times and recompute pooled losses. Keep paired predictions together. Report that overlapping training sets and dependence limit a literal confidence-interval interpretation. For very few holdout groups, emphasize fold results and sensitivity rather than p-value language. Do not bootstrap individual listings as independent spatial units or perform a three-city causal meta-regression.

<!-- PAGE -->
# 8. Estimation, diagnostics and computational budget

## 8.1 Training pipeline

Recover the exact v3 list of 30 unique XGBoost candidates and its hash. Reconstruct only if genuinely missing, using the documented pools and seed 20261006, with a logged deviation. Preserve the four inner folds and seed 20261005. No city receives a reduced search because its initial results are inconvenient. If resource constraints require a budget amendment, fix the same new protocol before empirical comparison.

Every candidate’s learned preprocessing is trained inside its inner-training split. Selected parameters are refitted using outer training data only. Do not use outer-test early stopping. Retain candidate scores, choices, boundary hits, missingness handling, predictor support, environment and random seeds. Compute held-out TreeSHAP from each tuned outer model; no arbitrary all-data fit replaces the evaluation models.

## 8.2 Cost accounting

For a city with K outer folds, four feature sets require 4 × K × (30 × 4 + 1) = 484K XGBoost fits, excluding optional final descriptive refits. Random five-fold benchmarking adds 2,420 fits per city. Sensitivities multiply this budget; fitting no-income doubles the corresponding full-ladder work. OLS, data engineering and SHAP have additional costs.

This is a count of prescribed fits, not a time promise. Profile synthetic or frozen-protocol workloads, document resource feasibility and use stage checkpoints. Never reduce candidates or sensitivity scope silently after inspecting empirical scores. Output partial completion truthfully when resources are insufficient.

## 8.3 Association and spatial diagnostics

Retain HC3 OLS coefficient intervals, rank/VIF/condition diagnostics and restricted WCR11 bootstrap-t sensitivity: Webb weights, CRV1, 9,999 replications. Cluster on the actual qualified analysis areas; the method’s name does not fix their number. Never treat conventional few-cluster standard errors as definitive or delete variables by significance.

Retain eight-neighbour Moran’s I with 499 seeded permutations for log price and selected geographic OOF residuals. Use metric coordinates, deterministic tie handling and private observation IDs. One spatial-error association sensitivity may be run if the frozen OLS MW trigger |I| > 0.05 and p < 0.05 passes. A failed association gate does not make completed predictive results invalid, but it prevents claiming complete association analysis.

<!-- PAGE -->
# 9. Robustness and limitations registry

| Check | Rule and interpretation |
|---|---|
| No-income | Omit only income; same sample/folds and budget; no H in either version |
| Apartment/condo only | Same within-variant rows for all four models; separate sample effect from feature effect |
| Reviewed listings | Sensitivity only; no primary review restriction |
| Price trimming | Derive 1st/99th cutoffs inside training partitions; retain the full held-out test sample |
| Reputation controls | Separate variant with training-only handling of missing reviews/ratings |
| 15/20-minute opportunities | Same speed and destinations; matched 1,250/1,667-metre radii |
| 4.0/5.4 km/h | Fixed 10-minute budget; matched 667/900-metre radii and recomputed travel times |
| Continuous decay | Half-life 10 minutes; identical frozen destinations, all reachable contributions, no arbitrary time cutoff |
| Spatial blocks and buffers | Common 1.5-kilometre shifts plus inherited full v3 grid/buffer registry |
| Location uncertainty | Report 150-metre boundary-near flags; any exclusion reruns all compared models on identical subsets |
| Income/area association | Retain inherited fixed-effect sensitivity only as association analysis; area-constant slopes are absorbed |

The inherited thresholds and diagnostic significance rules remain project decisions. The primary conclusion is not chosen from whichever variant yields the largest gain. No numeric “practical equivalence” threshold is imported automatically from the retired housing proposal; such a criterion needs an explicit pre-fit decision.

For continuous decay the finite extraction universe is a limitation, not evidence that no destinations exist beyond it. For spatial buffers, a fold with fewer than 500 training or 30 test listings is marked infeasible rather than changed after scores are seen. The 150-metre distance is an audit scale, not proof of each listing’s actual displacement.

Each registered check has status COMPLETE, INFEASIBLE, DEFERRED, FAILED or NOT_APPLICABLE with an explanation. Completion of primary fits does not imply completion of robustness. Any pre-fit prioritization/deferral is recorded in the analysis freeze. Do not turn a failed run into evidence of no effect.

Cross-sectional asking prices, missing-price selection, quote timing, anonymized coordinates, local income definitions, OSM coverage and spatial-scale differences remain central limitations. None is fixed simply by adding two cities [P1; A1; D1].

<!-- PAGE -->
# 10. Repository and data governance

## 10.1 Preserve evidence; change active dependencies

Keep the existing v4 branch. Do not reset to main, revert the housing commits wholesale, rewrite published history or delete applied migrations. Inspect the actual schema before adapting it: a new design may need a new append-only migration or policy row, never an in-place rewrite of a frozen definition.

Keep housing tables/adapters/tests as historical capability where possible, but remove their invocation and prerequisites from the new primary runner. A missing residential-price file, unavailable licence or NULL housing-area ID must not block this design. Test that explicitly. Do not fake qualified statuses to bypass old constraints; add a correctly scoped new definition.

Keep SQL/PostGIS authoritative where established. The supplied audits identify an isolated v4 database and append-only source ingestion. Reuse their APIs, paths and guards; do not silently migrate the study to an independent CSV-only framework. Discover the next actual migration number instead of assuming 026.

## 10.2 Git checkpoint protocol

Every A-step reads applicable AGENTS.md, the active contract and step log. Verify branch v4 and the recorded remote. Stop on unrelated changes, divergent history, unfinished operations or ambiguous provenance. Never auto-stash, force-push, amend a published commit, accept external terms or bypass authentication.

For each step: run relevant checks; review the diff; stage only intended safe files; record step status; commit; push HEAD explicitly to the recorded remote’s refs/heads/v4; verify remote SHA equals local HEAD. Report the SHA outside its own commit. A failed push is LOCAL_ONLY and pauses the next step. A safe blocked checkpoint may be committed, but cannot be called scientifically ready.

## 10.3 Privacy and reproducibility

Do not commit raw listing rows, host/owner identifiers, coordinates, restricted housing extracts, credentials, database dumps or private OOF predictions. Preserve sources locally with licences/checksums. Public maps use 500-metre aggregate cells and suppress fewer than five observations. Licences and attribution still apply to retained data and geography.

Store code, feature, sample, fold, candidate, environment and source identities with each fitted run. Separate scientific dependencies from editorial files so a documentation commit does not pretend to create new estimates. Resume only matching immutable dependencies; otherwise create a new run and mark old results superseded without deleting them.

<!-- PAGE -->
# 11. Sequential execution checkpoints

The companion playbook contains twelve standalone copy-paste prompts. Old housing steps are superseded; do not continue old Step 6. Run one prompt at a time in the same project, committing and verifying a v4 push after each.

| Prompt | Work package | Evidence required before advancing |
|---|---|---|
| A01 | Audit live state and amend active scientific documents | New design contract; old housing scope retained as history |
| A02 | Decouple housing from active code/readiness | No-H model registry and successful housing-free preflight tests |
| A03 | Qualify municipal/analysis geographies | Oslo amendment or exact remaining blocker; Stockholm mask preserved |
| A04 | Qualify baseline population, income and centrality | Context dictionary, source joins and frozen income decision |
| A05 | Build/reuse matched E/W features | Source/graph hashes, route and destination QA |
| A06 | Freeze samples, folds and candidate list | Paired rows, valid primary/random/geometric folds, no housing selection |
| A07 | Validate models and resumable execution | Synthetic end-to-end, leakage and interrupted-run tests; pre-fit manifest |
| A08 | Copenhagen primary execution | Audited reuse decision or new v4 estimates; complete OOF records |
| A09 | Oslo primary execution | City-specific gates and actual OOF completeness |
| A10 | Stockholm primary execution | City-specific gates and actual OOF completeness |
| A11 | Robustness and cross-city synthesis | All variants accounted for; comparable definitions; paired contrasts |
| A12 | Final documents and reproducibility handover | Claims-to-output audit, source/privacy checks, verified final v4 push |

## Planning sequence

A01–A04 resolve scope and measurement inputs; A05–A07 prepare features and freeze the statistical protocol; A08–A10 produce city results; A11–A12 complete evaluation and reporting. This is a dependency-based research schedule, not an estimate of assistant or Codex runtime.

Do not start all cities in parallel editing sessions. Computational jobs may be parallelized only through the tested runner under frozen dependencies and adequate resources. More processing is not a substitute for unresolved geography or a missing income-policy decision.

A narrower two-city empirical scope is not automatically authorized. If a remaining non-housing dependency makes one city infeasible, document options and obtain a scope decision before changing the title or primary research questions.

<!-- PAGE -->
# 12. Tables, figures and writing plan

## 12.1 Required outputs

| Output | Main purpose |
|---|---|
| Source/period/geography table | Establish what was acquired, accepted and reused |
| Sample-construction table | Show attrition from raw listings to each common sample |
| Variable and measurement table | Define X, E, W and all units/transforms |
| City/area descriptive maps | Explain study boundaries, coverage and context safely |
| E/W disagreement diagnostics | Answer RQ1 without relying on price-model results |
| Fold maps and support table | Define the actual generalisation settings |
| Performance/paired-comparison tables | Answer RQ2 with five prespecified contrasts |
| Cross-city relative-gain figure | Compare patterns while showing sample/task differences |
| Income and robustness summary | Show sensitivity, failures and unexecuted checks |
| Association/SHAP/spatial diagnostics | Complement prediction without causal language |
| Reproducibility and claim audit | Link every empirical statement to a source/run/output |

All primary tables label M0, ME, MW, MEW and state that residential prices are excluded. Model-version hashes distinguish their earlier meanings. Avoid presenting v3 and revised v4 as paired identical-sample experiments unless that equality has actually been verified.

## 12.2 Chapter order

Introduction and RQs; literature and concept; comparative cases/data; measurement and evaluation methods; city results; comparative robustness; discussion and conclusion. Housing feasibility appears briefly in the design-amendment record, not as a promised incomplete results chapter.

Claims should be specific: “W reduced held-out log-price RMSE relative to E in this city under this fold design” is supported by paired predictions. “W is universally better” or “Airbnb causes expensive housing” is not. A failure to distinguish two estimates from zero does not prove practical equivalence.

## 12.3 Review items

Before fitting, review the new-city area choice, Oslo vintage statement, income mode, OSM timing policy, final feature universe, candidate list and computational/sensitivity scope. After fitting, review support, complete-versus-partial statuses and any scientific corrections; do not edit the pre-fit history to reflect the observed results.

The final report must not call all three cities complete when one primary gate, required test or fit remains blocked. Distinguish a technically successful checkpoint from completion of the research design.

<!-- PAGE -->
# 13. Release tests and stop rules

## 13.1 Mandatory acceptance tests

**Scope:** active primary registry is exactly M0/ME/MW/MEW without H. It rejects residential-price columns and does not depend on housing-data files, status, licence, sample or folds. Historical housing code/audits still retain their meanings.

**Data:** immutable raw-source receipts and protected v3 bytes match; no duplicate ingestion; city IDs, currencies and boundary provenance are correct; assignment produces no row multiplication. New design source links are explicit.

**Measurements:** destination universes match E/W; connector and routing QA pass; zero, missing and unreachable states are separate; city-specific CRS and source dates are recorded.

**Samples/folds:** paired observations/outcomes/folds are identical across models; learned preprocessing is training-only; no outer-test observations enter tuning; geometry grouping is outcome-blind. A no-income variant changes only income on its defined sample.

**Estimates:** required candidate budgets, fold counts and OOF observations are complete; metrics independently reproduce from saved losses. A code change that affects scientific outputs flags every affected city run, not just the city in which the bug was found.

**Publication/Git:** raw or restricted material is not staged; public map suppression and licences pass; documents use correct scope/model definitions; branch v4 only; final remote SHA matches local HEAD.

## 13.2 Status meanings

| Status | Meaning |
|---|---|
| READY_FOR_NEXT_STEP | This checkpoint and its relevant dependencies pass; not necessarily research complete |
| PARTIAL / BLOCKED | Safe progress exists, but named requirements are not satisfied |
| LOCAL_ONLY | Commit exists but remote push is not verified; do not advance |
| NOT_REQUIRED_SCOPE_AMENDED | Retired housing task is outside the new design; old evidence unchanged |
| COMPLETE_PRIMARY | Specified primary runs complete; robustness/documentation may still be incomplete |
| COMPLETE_RELEASE | All declared release requirements and reports pass |

Do not change an old BLOCKED source to QUALIFIED because the source is no longer needed. Do not suppress data-validity failures as scope retirement. Housing blocks are removed; geography, observed-price validity, common support, income decisions and safe execution remain real gates.

## 13.3 Source basis

P1/P2 are the supplied v3 specification, deviations and results; L1 is the audited literature matrix; A1–A4 are the four current acquisition/amendment files. R1–R10 and D1 are listed in the companion proposal. The package source registry records paths, hashes and selected primary-source verification. These documents specify a design; the live repository remains the authority for actual code, committed status and executed tests.


Live document authority: [index](document_index.md), [contract](IMPLEMENTATION_CONTRACT.md), [step mapping](step_mapping_A01_A12.md).


Live A03 checkpoint (11 October 2026): see [the geography audit](geography_qualification_A03_20261011.md).
Copenhagen retains 11 operational areas with explicit footprint/registration
exceptions and complete eligible positive-price assignment. Oslo's dated mask
is accepted operationally, while the 17-unit analysis option remains blocked by
licence and sparse Marka support. Stockholm retains SCB 2025_v2 municipality
0180 only as a mask; current 11-borough polygons remain unqualified. No housing
fold rules, RegSO validation shortcut or final A06 membership is introduced.
A04–A12 remain future work requiring their own prompt and qualified dependencies.
