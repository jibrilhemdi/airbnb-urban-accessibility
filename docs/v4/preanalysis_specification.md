# V4 scientific specification — active Markdown

Definition version: `v4_housing_standard_20261011`. Decision date: 11 October
2026. This newly authored V4 amendment uses the actual active V3 specification,
dictionary, source registry, configuration and supporting documents. It does
not reproduce an unavailable earlier V4 draft. V3 results were already observed;
this is not retrospective preregistration. Supervisor approval is not recorded.
Empirical execution is BLOCKED pending qualification and separate authorization.

## Outcome, population and city scope

Use a matched June 2026 Inside Airbnb snapshot target, one listing per city and
snapshot, with separate city models. The known V3 date is 30 June 2026; other
city dates remain unresolved, not silently substituted. The user-authorized
roster is `copenhagen_frederiksberg`, `oslo`, `stockholm`; evidence and unresolved
fields are versioned in `config/v4/cities.json`. Copenhagen evidence is inherited
locally; its CRS, districts and income mapping are never defaults for other cities.
The primary product segment retains conventional residential entire dwellings,
with the six inherited property types documented in the dictionary. There is
no minimum-review or minimum-availability primary restriction.

Y is `log_price = log(price_nightly)` for observed, positive, parseable Airbnb
nightly asking prices in their native currency. Never statistically impute
either outcome or combine unlike prices row by row. Count every exclusion.
Missing outcomes remain missing. No temporal Airbnb panel, residential-price
outcome model or gentrification score is introduced. Associations/predictions
do not identify causal housing-price or displacement effects.

## Primary models

| Model | Required blocks |
| --- | --- |
| M0 | X + H |
| ME | X + H + E |
| MW | X + H + W |
| MEW | X + H + E + W |

OLS uses an intercept plus the stated blocks; XGBoost uses the same conceptual
features. X is exactly the inherited qualified baseline, excluding H/E/W:
property type, accommodates, bedrooms, source-derived effective bathrooms,
log(1+minimum nights), superhost, log(1+host listing count), the eight fixed
amenity indicators, log population density, qualified income and prespecified
City Hall centrality distance. No extra instant-bookable/review/reputation,
area identifier, municipality indicator or housing feature is silently added
to X from older supporting-draft suggestions. A new city's centrality anchor
and context sources must be explicitly qualified before execution.

H appears exactly once in each primary model. E contains separate nearest
eligible rail and deduplicated bus Euclidean km plus log(1+food/social) and
log(1+cultural/tourist) counts. W contains matched nearest rail and bus walking
minutes plus the corresponding log(1+network opportunity) counts. There is
no active eight-model ladder, H-suffixed primary label or automatic no-H fallback.
Model IDs include the definition version, e.g.
`v4_housing_standard_20261011:M0`; V3 M0 excludes H and is not this model.

## Research questions and paired contrasts

RQ1 compares accessibility representations. RQ2 evaluates predictive accessibility
information conditional on X+H. RQ3 compares geographic versus random validation
and cross-city differences. RQ4 describes variation in network gains across
externally measured housing contexts. RQ4 uses paired held-out gains at the
external-area level against continuous frozen H, without introducing another
primary model or choosing context partitions from outer results.

Primary contrast: MEW versus ME. Replacement contrast: MW versus ME.

| Priority | Added / reference | Interpretation |
| --- | --- | --- |
| Primary | MEW / ME | Network information beyond Euclidean access, conditional on X+H |
| Replacement | MW / ME | Walking replacing Euclidean representation with X+H fixed |
| Additional | ME / M0 | Euclidean accessibility beyond X+H |
| Additional | MW / M0 | Walking accessibility beyond X+H |
| Additional | MEW / M0 | Both accessibility representations beyond X+H |

Delta error is added minus reference; negative ΔRMSE/ΔMAE favours added.
RMSE and MAE on log price are primary metrics; R² is secondary. All comparisons
are paired on identical observations/outcomes/folds within city and engine.
No contrast estimates the incremental benefit of adding H. A separately
authorized no-H sensitivity would be required to estimate that quantity.
Cross-city differences remain descriptive and acknowledge source, sample,
area-count and support differences; cities are not pooled into one estimator.

## Housing definition and qualification

Prefer full-year 2025 apartment residential sale-price/m2. Preserve native
positive finite prices, currency, reported statistic, geography, coverage and
source provenance. Mean/median or other source statistics must be explicitly
qualified and frozen; their availability/comparability is not assumed.
Alternatives to the preferred year/measure require an explicit amendment.

Freeze a qualified external-area reference frame separately within each city,
independent of Airbnb listings, outcomes and validation folds. Each reference
area contributes once with equal weight. Include the whole frozen qualified
frame, even where no eligible Airbnb listing is observed. G_ref is its positive
area count. Compute average ordinal ranks for ties in native sale-price/m2 and
use `H=(midrank-0.5)/G_ref`. Preserve reference membership, values, ties, ranks,
G_ref, provenance and checksums. Never rerank on the listing sample, training
fold or test fold, or weight ranks by Airbnb counts. This is a fixed external
measurement, not learned Airbnb preprocessing. Missing/suppressed external
prices cannot be assigned zero or silently removed to redefine the frame.

The prespecified housing-scale sensitivity replaces the midrank H feature
with `log(housing_price_m2_native)` in the same four blocks, sample and folds;
it does not add four primary models. Retain native units without invented
currency conversion. Housing values/mappings are never statistically imputed.

Qualification must establish source, date, geographic extent, checksum,
period, property type, unit/currency, statistic, coverage and documented area
mapping. A city without qualified H is BLOCKED from the primary ladder.
Listing-level housing exclusions require qualified coverage rules and an
explicit count/reason audit. Narrower-city or descriptive-only scope requires
an explicit amendment, never silent omission of H.

## Prediction and OLS association samples

Freeze one housing-qualified prediction sample per city using valid observed Y,
coordinates, official assignment, qualified H and matched E/W coverage/routing.
All four primary models use the identical sample and saved random/geographic
outer and spatial inner folds. No easier sample is constructed for M0 or ME.
Remaining X/E/W predictor missingness is explicit. Learned medians/indicators
and category encodings are fitted only within the relevant training partition;
entirely missing training predictors stop evaluation. Outer outcomes never
choose features, taxonomy, thresholds, preprocessing or candidate pools.

Separately freeze/document one common OLS association sample per city: complete
cases of the union X+H+E+W and observed Y within the prediction sample. Apply the
inherited 5% material-missingness limit to the fraction of prediction-sample
rows missing any predictor in that union. Above 5%, association inference is
BLOCKED until the multiple-imputation/pooling method is separately specified
and validated. No model-specific complete-case selection or median-imputed
inferential fallback is permitted. Record both sample identities, counts,
exclusions and checksums; prediction metrics refer to the prediction sample.

## Inherited income sensitivity

Keep the qualified baseline income concept: 2024 equivalised disposable income
as the arithmetic mean of ten published decile means, divided by 100,000 DKK
for the existing Copenhagen/Frederiksberg measure. KKIND5 and nominal IFOR35
retain their documented processing/price-basis uncertainties; missing eligible
weights remain NULL. Other-city income sources need their own qualification.

Mandatory no-income sensitivity removes only `income_100k_dkk` from X and
**still includes H**. It reuses both frozen samples, observed outcomes, saved
outer/inner folds, engines, candidates, tuning budget and training-only
preprocessing. Versioned scenario IDs distinguish it from primary models.
Report coefficients, metrics, paired gains and all geographic-area results.
Keep the inherited material-change flags: ΔRMSE sign/MW-versus-ME ranking
reversal; coefficient sign reversal with wild p<0.05 in either specification;
relative magnitude change ≥25% with a 0.01 coefficient floor. They do not
choose the primary specification or establish exact income equivalence.

## Inherited thresholds, tuning and inference

Retain baseline speed 5.0 km/h, budgets 10/15/20 minutes and matched rounded
Euclidean radii 833/1,250/1,667 m. Primary is 10 minutes/833 m. Speed sensitivities
are 4.0/5.4 km/h at 10 minutes, with 667/900 m analogues. Continuous decay uses
lambda=ln(2)/10 per minute, the identical frozen destination universe and no
finite cutoff for reachable network destinations. Include both snap connectors
and directed foot restrictions. Preserve taxonomy/deterministic consolidation:
25 m mutually-nearest identity-compatible platform/stop-position pairs,
3 m same-representation tolerance (0.5 m unnamed), conflicting refs retained.

Reuse the actual frozen **30** unique XGBoost candidates and discrete pools
from V3, seed 20261006, as copied with a V4 identity into configuration. Keep
four inner spatial folds on 1 km blocks, seed 20261005; random outer five folds,
seed 20261004; geographic leave-one-qualified-area-out within each city.
The V3 eleven-area regional count is historical, not an invented V4 city count.
Area adequacy must pass before geographic evaluation. Save folds before fitting,
retain training preprocessing/tuning records and compute exact held-out TreeSHAP.

Evaluate all 1,000/1,500/2,000 m geometric block variants at zero and half-block
origins and 500/1,000 m exclusion buffers. Sensitivity folds require at least
500 train and 30 test observations. Preserve apartment/condo-only, reviewed
listing and training-derived 1st/99th price-trimming sensitivities; review
covariates remain separate. No performance-selected grid or variable deletion.

OLS retains HC3 SEs/CIs and restricted WCR11 wild-cluster bootstrap-t by qualified
analysis area, Webb six-point weights, CRV1 studentisation, 9,999 seeded
replications, full rank and at least six clusters. Fail inadequate designs;
do not represent six clusters as an assurance of reliable power. Report VIF,
rank/condition number and support/extrapolation without deleting predictors.
Paired geographic error uncertainty resamples all qualified held-out areas in
that city with replacement 2,000 times, retaining every listing per sampled
area and recomputing pooled errors. Fixed V3 eleven-area indexing is not reused
for an unqualified V4 city. Percentile intervals describe stability, not causal
effects or third-decimal significance.

Retain eight-neighbour Moran's I with 499 seeded permutations. Only one
heteroskedasticity-robust spatial-error association sensitivity is contemplated
if OLS MW geographic residuals have |I|>0.05 and permutation p<0.05; all its
housing-context identification/rank gates must pass. No new SAR/SDM/GWR family.
Area fixed effects absorb area-constant H/context slopes; they cannot estimate
those absorbed coefficients. All numerical thresholds are project safeguards,
not power guarantees. All metric operations record the qualified CRS; inherited
V3 operations use EPSG:25832 and source coordinates EPSG:4326. Another city's
projected CRS must be explicitly qualified, not assumed from V3.

## Governance and implementation state

PostgreSQL/PostGIS is authoritative. Use separate V4 database/run/output identity;
raw data, V3 artifacts/migrations and historical drafts stay immutable. Public
maps retain 500 m cells with at least five nonmissing plotted observations;
restricted raw/private row-level predictions, folds, SHAP and coordinates stay
private. Record all external provenance and never fill missing scientific data.

`config/v4/research_design.json` is the versioned machine-readable specification;
`src/v4/specification.py` exposes model metadata only. No V4 runner, source
qualification, acquisition, migration or empirical result is implemented in
this step. Markdown is authoritative; see [document index](document_index.md)
for DOCX status and [source registry](source_registry.md) for unresolved inputs.
