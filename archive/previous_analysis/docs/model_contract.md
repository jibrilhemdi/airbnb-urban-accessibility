# Active V4 model contract — A02 executable registry

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
run, validation and variant separate. Migration 026 adds the new IDs, parent-design isolation and separate artifact
estimator/validation dimensions. No historical source, run or model row is
relabelled; applied migrations 023–025 remain unchanged.

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

**Explicit A02 baseline resolution:** actual `src/pipeline/model_specification.py`
and frozen prior V4 configuration include categorical `property_type`. The A02
instruction to remove only housing-derived dependencies retains it alongside all
17 inherited numeric/amenity/context controls. This supersedes the supplied
revision's prose exclusion; no other predictor is silently changed. It is a
listing-type categorical control, not residential-price context.

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

## Actual executable state after A02

`src/v4/specification.py` and `config/v4/research_design_accessibility_only.json`
are the canonical active registry. `config/v4/cities_accessibility_only.json`
keeps verified non-housing fields and unresolved city inputs. Frozen
`config/v4/research_design.json` / `cities.json` and
`src/v4/historical_specification.py` retain the historical design. Explicit
scientific selection is separate from the unchanged `research_design_v4` source
namespace. Existing acquisition adapters keep their historical Scope default;
the analytical CLI explicitly defaults to the new design.

Approved old listing scopes are read by manifest hash without duplicate ingestion.
New output/cache identities include design. Active scientific hashes exclude the
housing policy/module/audit migration; provenance still verifies every applied
migration. Reporting reads aggregate metrics only and enforces parent-design
identity. Housing-free scope checks pass synthetic fixtures with NULL housing
fields; ordinary price/geography/context/accessibility failure still blocks.
`v4-run` remains an empirical refusal stub pending A07. No city qualification,
source acquisition, routing, feature construction or fit is claimed by A02.
See [the A02 audit](pipeline_scope_audit_A02_20261011.md).
