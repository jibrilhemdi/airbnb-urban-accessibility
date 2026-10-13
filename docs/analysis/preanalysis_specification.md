# Final scientific specification

Adopted 13 October 2026 after historical analyses and geographic-support
inspection, before any final-design fitting. This is an explicit researcher
amendment, not retrospective preregistration. The exact request and previous
instructions are preserved in `archive/`.

Study three separate cities using verified June 2026 detailed listings. Retain
Entire home/apt and exactly Entire rental unit, Entire condo, Entire home,
Entire loft, Entire townhouse, Entire villa. No primary activity/review threshold.
Preserve missing-price eligible observations in auditing. Positive original
observed native prices define actual log price; never impute the outcome.

Accepted municipal masks define study-area membership using covers in EPSG:4326.
Provider polygons define operational validation groups, never official-boundary
certification. Keep raw label, polygon source and derived group separately.
Copenhagen has 11 groups, Oslo 17, Stockholm's 14 raw labels map to 11 frozen
groups exactly as specified in configuration. Rinkeby-Tensta's historical polygon
correspondence is evidence of a likely source naming error, not exact identity.

X uses the common inherited registry with income removed. E/W match one deduplicated
destination universe per city. Inherited taxonomy, consolidation, directed
pedestrian restrictions, both connectors, 5 km/h speed, 10-minute opportunities,
rounded 833 m Euclidean radius and log1p counts are frozen before results.
Primary city CRSs are EPSG:25832, EPSG:25833, EPSG:3006. Prefer common OSM time
2026-06-30T23:59:59Z; fallback requires one explicit common frozen time, reliable
source receipts and a documented temporal amendment, never mixed arbitrary vintages.
Use OSM civic/town-hall features for centrality with pinned element IDs, tags,
coordinates and snapshot. Existing tourism/SSR points remain historical evidence.

Density is population divided by source-compatible area in km², modeled as log
density. Aggregate compatible units using sum(population)/sum(area), never means
of densities or proportional redistribution of unlocated/split-unit population.
Stockholm needs direct official statistics or a validated clean RegSO crosswalk.
Provider group names alone do not establish compatibility with official counts.

Freeze the price reference sample before accessibility/model filtering:
eligible conventional entire homes, inside accepted mask, positive observed price.
Store N, mean(log(price)), exp(mean(log(price))) and source hashes per city.
Transfer alone uses log(price)-mean(log(price)); every model uses the same benchmark.

The common prediction sample requires observed outcome, unique qualified geography,
qualified context and all required matched accessibility support. Predictive
listing-control missingness remains explicit; median/indicator imputation and
category encoding are fitted within each training split. An all-missing required
training predictor blocks fitting. Common association complete cases use the union
X+E+W; more than 10% missing any required predictor pauses association inference.
The previous 5% eligibility limit was changed uniformly after observing
Stockholm's 5.891783567% missingness; see the dated
[post-observation amendment](association_missingness_amendment_20261013.md).
This 10% limit is a researcher-design threshold, not a universal standard.
No inferential median-imputation substitute is authorized.

Primary outer folds leave out one operational neighbourhood: test N>=15,
complementary training N>=500 in the final common sample. The 15 threshold is
an explicit post-inspection pre-fit feasibility amendment, not a universal rule.
Retain the earlier 30 threshold as a support diagnostic. Random five-fold CV and
five-fold 1.5 km blocks at origins (0,0) and (750,750) m are prespecified.
Inner tuning uses four size-balanced 1 km spatial-block folds and seed20261005.
Random seed20261004; reuse all 30 exact unique candidates, never outcome-driven
search changes. Inner preprocessing is fitted anew; no outer early stopping.

Fit OLS and XGBoost for M0, ME, MW, MEW with paired rows/outcomes/folds. Report
RMSE, MAE, R² and fold support; delta=candidate-reference (negative favors candidate)
and proportional change for ME/M0, MW/M0, MEW/M0, MW/ME, MEW/ME.
Use 2000 geographic-group paired resamples for descriptive stability summaries.
Association inference retains HC3, full-rank/condition/VIF diagnostics and
9999-replication restricted wild-cluster bootstrap with actual groups.
Moran diagnostics: 8 neighbours, 499 permutations. Preserve the registered
heteroskedastic spatial-error sensitivity trigger |I|>0.05 and p<0.05.

Transfer has six ordered source/target pairs. Tune with source-only spatial folds,
refit on full eligible source analytical sample, apply fitted preprocessing/model
unchanged to target. No pooled source cities, target fit, intercept recalibration,
target tuning or target-driven category encoding/feature decisions. Evaluate relative
RMSE, MAE, R², Pearson and Spearman on identical target rows; paired uncertainty
resamples target neighbourhoods. No six-direction pseudo-independent significance test.

Retain registered apartment/condo, reviewed-only, training-only price-tail,
reputation, 15/20-minute opportunities, speed4/5.4, 10-minute-half-life decay,
boundary150 m, density-definition, area fixed-effect, grid1/1.5/2 km at two origins
and buffer500/1000 m checks. Account for every variant as COMPLETE, BLOCKED,
INFEASIBLE, FAILED or NOT_APPLICABLE with exact reasons. No silent post-score
reduction. Income and residential-price analyses are historical only.

Freeze and verify all source, feature, sample, fold, candidate and software hashes
before fitting. Preserve every derived artifact privately in PostGIS and immutable
run exports; reports read generated artifacts. No old fitted result is reusable
as a final result. Release requires all three cities, six transfers, diagnostics,
robustness and independent prediction-to-metric recalculation.
