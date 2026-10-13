# Revised pre-analysis specification — accessibility-only v4

11 October 2026. Design `v4_accessibility_only_20261011`. This is a prospective amendment after v3 results and housing-source feasibility were observed. Approval status remains explicit. The accompanying plan gives full rationale and execution rules.

## 1. Scope and samples

Cities: Copenhagen–Frederiksberg, Oslo, Stockholm. Separate models; matched acquired batch 30 June 2026. Original positive observed nightly price in native currency; natural log outcome. Batch, scrape, requested and returned stay dates are distinct; no outcome replacement by quote fields. No price imputation, primary minimum-review filter, historical Airbnb panel or residential-market outcome.

Eligible room type Entire home/apt and property types Entire rental unit, Entire condo, Entire home, Entire loft, Entire townhouse, Entire villa. Apartment/condo sensitivity retains the first two. Verify exact inherited labels/parser against actual code.

S_pred is the common eligible, geographically assigned, accessibility-supported prediction sample in each city. Every model uses the same observations/outcomes/folds. No H qualification, residential-price coverage or native-price-area assignment affects membership. Preserve broader acquisition/missing-price audits. S_assoc is separate, common across OLS association models; complete-case inference requires <=5% missing any required predictor. Material missingness blocks inferential OLS pending validated amendment, not all predictive work.

## 2. Baseline and features

X: accommodates; bedrooms; effective bathrooms; log1p minimum nights; superhost; log1p host listings; Wi-Fi; dishwasher; washer; dryer; workspace; free parking; private balcony; self check-in; log population density; qualified income; central civic-anchor distance.

Do not include primary raw coordinates, area/municipality flags, outcome-derived aggregates, reviews/reputation, availability, revenue, residential prices or housing proxies. Exact parsers come from v3. Retain accepted Copenhagen income (2024 mean of ten equivalised-disposable-income decile means /100000 DKK) and documented source qualifications. New-city income requires a concept/period/geography decision. Common no-income primary fallback requires explicit pre-fit approval; mandatory no-income sensitivity otherwise omits income only on matched rows/folds.

E: nearest eligible rail and consolidated bus distances in km; log1p food/social and culture/tourism counts within rounded 833 m. W: nearest reachable rail and bus minutes; matching opportunity counts within 10 min. Same candidate destination universe within city; nearest destination can differ by representation. Speed exactly 5 km/h; both endpoint connectors; pedestrian topology. City-appropriate metric CRS, common defensible OSM policy, audited extraction/coverage. Starting buffer >=2 km, expand when required. Preserve inherited bus consolidation (3 m compatible same-representation, 0.5 m unnamed, mutually nearest compatible cross-representation pairs <=25 m).

## 3. Four models and contrasts

M0=X; ME=X+E; MW=X+W; MEW=X+E+W. No H anywhere, including required sensitivities. OLS prediction and XGBoost; association OLS separately. Training mean is a separate benchmark.

Comparisons: ME-M0, MW-M0, MEW-M0, MW-ME, MEW-ME. The final add-on contrast is an explicit amendment relative to v3's enumerated contrast list. Replacement and add-on have different interpretations.

Delta RMSE=added-reference, negative favours added. Report proportional RMSE reduction, MAE, defined R2, fold distributions, equal-area results. No automatically adopted equivalence or minimum-practical-gain threshold. Crossing zero is not equivalence. Separate city results and relative improvements; no mixed-currency raw-price pooling or three-city causal regression.

## 4. Geography and validation

Copenhagen official eleven-area leave-one-area-out remains the baseline where qualified. Oslo/Stockholm official analysis polygons and any price-free sparse-area grouping must be qualified/frozen; no automatic 127-RegSO clustering. Retain Stockholm's accepted operational municipal-mask amendment. A03 permits only evidence-qualified Oslo vintage recovery; no exact-date claim from a current-at-retrieval API or matching area alone.

New-city primary folds use the explicit revised >=500 train/>=30 test safeguard. Housing area counts/80% coverage/group support no longer apply. Random outer five-fold benchmark is a different prediction setting. Common five-fold 1.5 km geometric blocks with zero/half-block origins are required for comparison; retain full v3 grid/buffer registry.

Inner tuning: four training-only spatial folds using 1 km blocks and deterministic balancing, inherited seed 20261005. Recover exact 30 unique v3 XGBoost candidates; reconstruct only if necessary with documented pools/seed 20261006. Freeze all memberships and candidates before conditional price-model evaluation. No outer-test early stopping or outcome-guided boundaries.

Fit imputation/encoding/scaling on the relevant training split only. Entirely missing required training columns fail. Store private OOF predictions/losses, candidate scores/choices and dependency provenance.

## 5. Inference and diagnostics

Paired geographic group resampling: 2000 replications, matched losses retained, descriptive stability ranges rather than definitive independence-based intervals. Preserve actual holdout count and small-group caveats.

Association OLS: HC3; rank/condition/VIF; restricted WCR11 bootstrap-t with Webb weights, CRV1 and 9999 replications, actual qualified area clusters, not universally eleven. Wild p-values accompany HC3 intervals rather than being labelled bootstrap intervals.

Spatial Moran: 8 nearest neighbours, 499 permutations, metric coordinates. One heteroskedasticity-robust spatial-error association sensitivity if OLS MW OOF residual |I|>0.05 and permutation p<0.05. No new broad spatial-model family.

## 6. Robustness and scope discipline

Retain matched no-income; apartment/condo-only; reviewed-only; training-derived 1st/99th price trimming with full held-out evaluation; separate reputation controls; 15/20-minute opportunities; speed 4/5.4 km/h at 10 min; continuous decay with 10-minute half-life over all reachable destinations in identical frozen universe; fixed-effect association sensitivity with area-constant slopes absorbed; original 1/1.5/2 km outer grids at both origins and 500/1000 m exclusion buffers.

Report 150 m boundary-near coordinate diagnostic. Any exclusion sensitivity must use a common within-variant sample for all models. Do not claim it corrects true coordinates. Public maps: 500 m cells, at least five observations.

All variants are COMPLETE/INFEASIBLE/DEFERRED/FAILED/NOT_APPLICABLE with exact reasons. Pre-fit resource amendments are visible; no silent candidate or robustness reduction after results. No mandatory new urban-form/moderator dataset.

## 7. Execution history

Use a new immutable scientific identity on existing v4. Preserve all v3/acquisition/housing records. Reuse only explicit hash-qualified sources/artifacts; do not rerun imports. Housing statuses are outside new scope, not changed to qualified. Resolve real non-housing blockers before fitting. Every A-step is a separate safe commit and verified push to v4. No merge to main is requested.
