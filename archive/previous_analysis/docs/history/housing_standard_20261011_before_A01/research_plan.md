# V4 research plan — active Markdown

Definition version: `v4_housing_standard_20261011`. Decision date: 11 October
2026. Newly authored from accessible repository evidence and the user decision.
V3 results were already observed; this is not retrospective preregistration.
Supervisor approval is not recorded. This step changes specification only.

## Primary models

| Model | Required blocks |
| --- | --- |
| M0 | X + H |
| ME | X + H + E |
| MW | X + H + W |
| MEW | X + H + E + W |

X is the inherited qualified baseline excluding H/E/W; every model contains
H exactly once. Use OLS and XGBoost separately by city on log observed Airbnb
nightly asking price. No active eight-model ladder, H-suffixed model labels or
automatic no-H fallback is permitted. The primary comparison is MEW versus ME;
replacement is MW versus ME; additional comparisons are ME/M0, MW/M0, MEW/M0.
No incremental benefit of adding H is identified by this ladder.

## Research tasks and gates

1. The authorized roster is `copenhagen_frederiksberg`, `oslo`, `stockholm`.
   Qualify and freeze matched June 2026 snapshot dates,
   boundaries, statistical units and projected CRS. Available V3 geography is
   evidence for its own case study only. Do not invent a second city, polygon
   crosswalk or snapshot. Missing evidence means BLOCKED.
2. Qualify external H independently of Airbnb price/model results: preferably
   full-year 2025 apartment sale-price/m2, including period, unit, currency,
   source statistic, transactions/coverage where available, boundary compatibility,
   license, acquisition date and checksum. Freeze one reference row per external
   area per city and retain native values. Compute the within-city external-area
   midrank using `H=(midrank-0.5)/G_ref`, never listing-weighted or reranked in
   folds. Log native price is the prespecified sensitivity. Missing qualified H
   blocks the city; alternate periods/measures require an explicit amendment.
3. Qualify the inherited X context and matching E/W destinations in each city.
   Carry forward the qualified income concept with documented uncertainty;
   Copenhagen/Frederiksberg qualification does not certify other city sources.
   Retain 5 km/h, 10-minute/833 m primary accessibility and all existing
   sensitivity thresholds/taxonomy safeguards without outcome-based selection.
4. Build and audit one housing-qualified prediction sample per city shared by
   M0/ME/MW/MEW. Save matched random-five, leave-one-qualified-area-out and
   training-only spatial-inner-four assignments. Counts/area feasibility are
   derived, not assumed to equal V3's eleven-area regional design.
5. Document a separate common OLS association sample using complete cases of
   the union X+H+E+W and observed Y. More than 5% union-predictor missingness
   blocks association inference until a separately specified/validated
   multiple-imputation and pooling procedure exists. Do not use model-specific
   complete-case samples or a median-imputed inference substitute.
6. In a subsequently authorized empirical step, fit the four versioned models
   with OLS/XGBoost, matched folds and the frozen 30 candidates. Run mandatory
   no-income sensitivity retaining H on unchanged samples/folds. Evaluate log
   native housing scale on the same prediction sample/folds. Keep all learned
   preprocessing, imputation and tuning inside training data.
7. Report RQ1 measurement differences; RQ2 accessibility information conditional
   on X+H; RQ3 geographic/random and cross-city differences; RQ4 variation in
   paired network gains across housing contexts. Prioritize MEW versus ME, then
   MW versus ME, with the three additional baseline contrasts. For RQ4, show
   area-level paired held-out error differences against continuous frozen H,
   with observation counts and support limitations. Do not select bins,
   interactions, cities or thresholds from outer errors. This descriptive
   comparison introduces no additional primary model.
8. Produce reproducible aggregate tables/figures and provenance certificates
   under separate V4 database/run/output identities. Keep private predictions,
   folds, SHAP and coordinates in PostgreSQL; never publish restricted rows.

Every empirical task above requires its own requested step and passed gates.
Numerical safeguards, including minimum fold/cluster counts, are not power
guarantees. Failed rank, coverage, extrapolation or scientific gates are reported
as BLOCKED, without silent omission of H or city scope. Narrower-city or
descriptive-only work requires an explicit amendment.

## Interpretation and document maintenance

Retain HC3 and restricted WCR11/Webb/CRV1 inference, 9,999 wild replications,
2,000 paired area-bootstrap resamples and all existing diagnostic rules. The
[specification](preanalysis_specification.md) records exact inherited values;
new city unit/cluster sufficiency must be qualified before applying them.
No temporal Airbnb panel, residential-price outcome model, gentrification score
or causal housing-price/displacement claim is part of this plan.

Markdown is authoritative. The [document index](document_index.md) records that
no active V4 DOCX or supported V4 regeneration workflow exists in this repository.
Do not use the V3 income-DOCX updater to manufacture V4 supporting documents.
