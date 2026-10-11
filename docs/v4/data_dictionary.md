# V4 data dictionary — accessibility-only

Design ID: `v4_accessibility_only_20261011`, 11 October 2026. These are scientific
field definitions, not a claim of implemented feature tables or sample freezes.
V3 results and housing feasibility were already observed. Supervisor approval
is not recorded. A02 implements the canonical registry and version-isolated SQL/output identities; empirical gates remain BLOCKED.

## Outcome, keys and samples

| Field | Definition / rule |
| --- | --- |
| `city_id` | Copenhagen–Frederiksberg, Oslo or Stockholm; explicit city scope |
| `snapshot_date` | Verified catalogue batch 2026-06-30; distinct scrape/stay dates |
| `listing_id` | Private source key; unique with city/snapshot after QA, no duplicate ingestion |
| `price_nightly` | Original positive observed nightly Airbnb asking price, native DKK/NOK/SEK; never replace with quote fields or impute |
| `log_price` | Natural log of original observed positive price; Y, never impute |
| `analysis_area` | Qualified official grouping/holdout unit; not provider labels or a primary numeric predictor |
| `design_id` / `definition_id` | New scientific/model identity; separate from city/run/estimator/model/validation/variant |
| `prediction_sample_id` | S_pred: one common eligible, assigned and accessibility-supported sample per city; no residential-price filter |
| `association_sample_id` | Separate common OLS complete cases of X+E+W and observed Y; >5% union-predictor missingness pauses inference |

Retain `room_type=Entire home/apt` and exactly: Entire rental unit, Entire condo,
Entire home, Entire loft, Entire townhouse, Entire villa. No primary minimum
review/activity/availability filter. Missing-price eligible listings remain in
acquisition audits. Count observed-price, coordinate, geography and accessibility
exclusions; NULL historical housing-area fields never define new eligibility.
Learned encodings/imputation/scaling use training data only; all-missing required
training predictors fail. All four models share ordered keys, outcomes and folds.

## X — inherited baseline and explicit live reconciliation


| Feature | Definition |
| --- | --- |
| `property_type` | Inherited categorical control retained under A02 remove-only-housing instruction; supplied prose exclusion explicitly superseded, bundle unchanged |
| `accommodates` | Observed capacity |
| `bedrooms` | Source bedrooms; missingness retained until authorized training preprocessing |
| `bathrooms_effective` | Source-derived effective bathrooms; parser provenance retained |
| `log1p_minimum_nights` | log(1+minimum nights) |
| `superhost` | Source superhost indicator |
| `log1p_host_listings_count` | log(1+host listings count) |
| `amenity_wifi` | Prespecified Wi-Fi indicator |
| `amenity_dishwasher` | Prespecified dishwasher indicator |
| `amenity_washer` | Prespecified washer indicator |
| `amenity_dryer` | Prespecified dryer indicator |
| `amenity_workspace` | Prespecified dedicated-workspace indicator |
| `amenity_free_parking` | Prespecified free-parking indicator |
| `amenity_private_balcony` | Prespecified private balcony/patio indicator |
| `amenity_self_checkin` | Prespecified self-check-in indicator |
| `log_population_density` | Log population / gross qualified assignment-polygon km²; V3 population 2026 Q3 and EPSG:25832, water/vintage limitations retained |
| `income_100k_dkk` | Inherited qualified 2024 equivalised-disposable-income arithmetic decile mean /100000 for the V3 DKK sources; other cities require qualified compatible measurement |
| `distance_centre_euclidean_km` | Distance to the prespecified public City Hall anchor in the qualified projected CRS; new-city anchor needs evidence |

The V3 native income field is `equiv_disposable_income_2024`; Copenhagen KKIND5
and Frederiksberg nominal IFOR35 are pragmatically harmonised, not perfectly
identical. The formula is sum(d1…d10)/10; source/selection hashes, documented
qualification and unconfirmed City raw price-basis details are retained.
Unavailable eligible weights remain NULL. E and W are separate from X; residential-price variables are outside the new scope.
No area indicator, instant-bookable or review field is added to the primary X.

The revision bundle omits/excludes categorical property type although the
actual v3 executable registry and previous V4 dictionary include it. This is a
recorded unresolved baseline-membership decision, not evidence of a housing
proxy and not authorization for silent predictor removal. Qualified income
remains core; a common no-income primary mode requires a pre-fit user decision
if new-city harmonisation fails. Mandatory matched no-income robustness remains.
No NOK/SEK observation is inserted into a DKK-labelled field without a qualified
source-native mapping/transformation decision.

## E and W — matched accessibility


| Block | Feature | Definition |
| --- | --- | --- |
| E | `nearest_station_euclidean_km` | Nearest eligible rail/metro/urban-rail station Euclidean distance in km |
| E | `nearest_bus_euclidean_km` | Nearest eligible deduplicated bus-stop Euclidean distance in km |
| E | `log1p_food_e` | log(1+matched food/social POIs within 833 m) |
| E | `log1p_culture_e` | log(1+matched cultural/tourist POIs within 833 m) |
| W | `nearest_station_walking_minutes` | Directed network walking minutes to the matched eligible station set, including connectors |
| W | `nearest_bus_walking_minutes` | Directed network walking minutes to the matched bus-stop set, including connectors |
| W | `log1p_food_w` | log(1+matched food/social POIs reachable within 10 minutes at 5 km/h) |
| W | `log1p_culture_w` | log(1+matched cultural/tourist POIs reachable within 10 minutes at 5 km/h) |


Baseline speed exactly 5 km/h; include both endpoint connectors and pedestrian
topology. Record city-appropriate CRS and matched destination universe. Preserve
15/20-minute, 4.0/5.4 km/h and 10-minute-half-life decay sensitivities, inherited
consolidation/taxonomy and training-only preprocessing. Missing extraction,
unreachable destinations and genuine zero opportunities remain distinct.

## Primary model membership

| Model | Required blocks |
| --- | --- |
| M0 | X |
| ME | X + E |
| MW | X + W |
| MEW | X + E + W |

Use new design-qualified IDs; no H/residential-price/rent proxy is a primary
or required-sensitivity feature. No-income omits only income from its qualified
X; it is distinct from the primary revised design. Contrast directions, samples,
validation and inference are in [preanalysis_specification.md](preanalysis_specification.md).

## Retired fields retained as historical source evidence

Existing nullable `native_housing_area_id`, housing source-audit records,
midrank/log-native-price definitions and annual-sale/coverage/group thresholds
are NOT_REQUIRED_SCOPE_AMENDED, not new-design features, sample filters or
fold rules. Historical [housing_acquisition.md](housing_acquisition.md) and
[housing_access_requirements.md](housing_access_requirements.md) remain unchanged
and superseded for active dependency purposes. Preserve their original BLOCKED
statuses and unsent requests. No property-price assignment or source request is
authorized. See [the model contract](model_contract.md) and
[the current-state audit](current_state_audit_20261011.md).
