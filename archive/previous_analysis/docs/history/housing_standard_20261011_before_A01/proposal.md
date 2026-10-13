# V4 scientific proposal — active Markdown

Definition version: `v4_housing_standard_20261011`. Decision date: 11 October
2026. Newly authored from the accessible V3 specification/supporting documents
and the user's V4 decision; this is not a transcription of an unavailable draft.
V3 results were already observed. This is a prospective V4 amendment, not
retrospective preregistration. Supervisor approval is not recorded.

The study compares matched Euclidean and walking-network accessibility for
observed Airbnb nightly asking prices, conditional on an inherited qualified
baseline and neighbourhood residential sale-price context. Models are fitted
separately by city. The matched snapshot target is June 2026. The authorized
V4 roster is `copenhagen_frederiksberg`, `oslo` and `stockholm`, explicitly
authorized for this architecture step. Per-city source and housing qualification
remain BLOCKED; the existing V3 extract alone does not establish V4 readiness.

## Research questions

- RQ1: How do matched Euclidean and walking-network accessibility
  representations differ within each city?
- RQ2: What predictive accessibility information remains conditional on the
  qualified baseline X and housing context H?
- RQ3: How do geographic versus random validation and cross-city differences
  change prediction error and accessibility comparisons?
- RQ4: How do held-out network gains vary across externally measured housing
  contexts within and between cities?

## Primary models

| Model | Required blocks |
| --- | --- |
| M0 | X + H |
| ME | X + H + E |
| MW | X + H + W |
| MEW | X + H + E + W |

X is the inherited qualified baseline excluding H/E/W. H occurs exactly once
in every model. OLS and XGBoost use these four blocks. There is no active
eight-model ladder, H-suffixed model label or automatic no-H fallback.

The primary contrast is **MEW versus ME**: walking-network information added
to Euclidean accessibility conditional on X+H. The replacement contrast is
**MW versus ME**. Additional contrasts are **ME/M0, MW/M0 and MEW/M0**.
No comparison here estimates the incremental benefit of adding H; that needs
a separately authorized no-H sensitivity.

H preferably measures full-year 2025 apartment sale-price/m2. Preserve native
values, currency and source statistic. Primary scale uses the frozen within-city
external-area midrank: `H=(midrank-0.5)/G_ref`. Log native price is a
prespecified scale sensitivity. See the [specification](preanalysis_specification.md)
for the reference frame and qualification gates.

All four models use one housing-qualified prediction sample per city and
matched saved outer/inner folds. OLS associations have a separately documented
common association sample. Mandatory no-income sensitivity removes only
income and still includes H, with the same samples/folds/candidates. Existing
thresholds, candidate budget and inference rules are retained; numerical
thresholds are project safeguards, not power guarantees.

RQ4 describes paired held-out network gains against frozen external housing
context; it does not introduce another primary model, an outcome-selected
housing partition or a causal mechanism. Cross-city comparisons describe
variation in samples, measurements and generalization tasks, not treatment
effects. Y is log observed nightly asking price, not residential sale price,
revenue or occupancy. There is no temporal Airbnb panel, residential-price
outcome model or gentrification score, and no causal housing-price/displacement
claim.

A city without qualified H is BLOCKED from the primary ladder. Narrower-city
or descriptive-only scope needs an explicit amendment. This proposal does not
authorize empirical execution. The [research plan](research_plan.md),
[dictionary](data_dictionary.md), [source registry](source_registry.md),
[document index](document_index.md) and `config/v4/research_design.json` complete
the active V4 material; V3 documents and historical drafts stay unchanged.
