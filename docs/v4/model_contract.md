# Active V4 model contract — scientific adoption, A02 integration pending

Design ID: `v4_accessibility_only_20261011`, 11 October 2026. This is the
researcher-authorized accessibility-only primary design, not a `no_housing`
sensitivity of `v4_housing_standard_20261011`. V3 results and housing feasibility
were already observed; no supervisor approval or retrospective registration.

| Model | Required blocks |
| --- | --- |
| M0 | X |
| ME | X + E |
| MW | X + W |
| MEW | X + E + W |

New scientific IDs are `v4_accessibility_only_20261011:M0`,
`v4_accessibility_only_20261011:ME`, `v4_accessibility_only_20261011:MW`,
`v4_accessibility_only_20261011:MEW`. Keep design, model, estimator, city, snapshot,
run, validation and variant separate. The old SQL permits only housing-standard
IDs; A01 does not insert or relabel rows and does not claim these new IDs work
in the current executable adapter. A02 must implement version isolation with
append-only changes as needed, never edit applied migrations.

## X, E, W and the outcome

Y is log original positive observed Airbnb nightly asking price in separate
native-currency city models. No replacement by quoted totals/rates or imputation.
X retains capacity/bedrooms/effective bathrooms, minimum-night/host/rental
controls, eight prespecified amenities, population density, qualified income
and centrality. [The dictionary](data_dictionary.md) records exact actual v3
field names and qualification limits. Neither E/W nor residential prices are X.

E/W each contain separate nearest rail and bus access plus food/social and
culture/tourism opportunities, using matched destination universes; E is km and
833 m opportunities, W minutes and 10-minute opportunities at exactly 5 km/h.
Both endpoint connectors and city-appropriate metric CRS are required.

**Explicit pending reconciliation:** actual `src/pipeline/model_specification.py`
and frozen prior V4 configuration include categorical `property_type`. The
supplied revision says not to include it. All 17 inherited numeric/amenity/context
controls are retained; whether the inherited categorical control remains must
be resolved explicitly before A02 finalizes membership or any model is fitted.
This is not solved by renaming property type as housing context. No automatic
predictor deletion, silently altered baseline or invented approval is recorded.

Qualified income remains distinct from residential prices. Mandatory no-income
robustness removes only income on its matched sample/folds with the full tuning
budget. A common no-income primary comparative mode requires an explicit pre-fit
researcher decision if new-city harmonisation fails.

## Comparisons, samples and gates

Report ME/M0, MW/M0, MEW/M0, MW/ME (replacement) and MEW/ME (add-on). MEW versus
ME extends v3's named four-contrast reporting list; it was already included in
housing-inclusive V4. Added-minus-reference error below zero favours added.
All primary comparisons share one accessibility-supported S_pred per city,
ordered observations/outcomes/folds and OLS/XGBoost conceptual blocks. Separate
S_assoc uses common complete cases of X+E+W; >5% union-predictor missingness blocks
association inference pending validated treatment. Training-only learned
preprocessing, four inner folds and 30 frozen candidates remain mandatory.

Residential prices/H/rent proxies are absent from all primary models and required
sensitivities. H acquisition, licensing prerequisites, price-qualified samples,
sales/coverage thresholds, H-area folds, ranks/log-H sensitivity and housing
subgroups are **NOT_REQUIRED_SCOPE_AMENDED**. Historical sources retain their
actual failures/preliminary status. There is no new housing-source request.
Ordinary geography, context, observed-price validity, destination/support,
fold feasibility, inference rank and privacy gates remain real. See
[the active specification](preanalysis_specification.md) and
[the current dependency audit](current_state_audit_20261011.md).

## Actual executable state at A01

`config/v4/research_design.json`, `src/v4/specification.py`, `src/v4/cities.py`,
`src/v4/runtime.py` and migration 023 still impose housing-standard definitions,
qualification and model-ID constraints. `src/v4/identity.py` still hashes housing
policy/module dependencies. Housing source-audit migration 025 and its adapters
are preserved historical capability. Runtime/config/database changes and their
new-design tests belong to A02. The supplied `model_spec_template.json` is a
reference template, not a drop-in configuration or implemented canonical registry.
No new-design executable readiness or empirical result is claimed by A01.
