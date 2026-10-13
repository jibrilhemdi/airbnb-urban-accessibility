# V4 data dictionary — active Markdown

Definition version: `v4_housing_standard_20261011`. Decision date: 11 October
2026. Newly authored from accessible V3 definitions and the user's decision.
These are field specifications, not a claim that V4 columns or data exist.
V3 results were already observed; supervisor approval is not recorded and this
is not retrospective preregistration.

## Primary models

| Model | Required blocks |
| --- | --- |
| M0 | X + H |
| ME | X + H + E |
| MW | X + H + W |
| MEW | X + H + E + W |

X is the inherited qualified baseline excluding H/E/W; H occurs exactly once
in each model. V4 model identifiers include `v4_housing_standard_20261011` and
must not be confused with V3 labels. The primary contrast is MEW versus ME,
replacement MW versus ME, additional ME/M0, MW/M0 and MEW/M0. Mandatory
no-income sensitivity omits only income and still includes H. No automatic
no-H fallback, H-suffixed primary models or adding-H estimand is authorized.

## Outcome and identity

| Field | Definition / rule |
| --- | --- |
| `city_id` | Explicit `copenhagen_frederiksberg`, `oslo` or `stockholm`; qualification remains gated |
| `snapshot_date` | Matched June 2026 target; actual city dates require source evidence |
| `listing_id` | Source ID; unique with city and snapshot, private analytical key |
| `price_nightly` | Observed positive Airbnb nightly asking price in native currency; never impute |
| `log_price` | Natural log of observed `price_nightly`; Y, never impute |
| `analysis_area` | Qualified geographic grouping/holdout unit, not a primary feature |
| `definition_id` | Versioned model/scenario identity, not a feature |
| `prediction_sample_id` | One frozen housing-qualified comparison sample per city |
| `association_sample_id` | Separate common OLS complete-case sample over X+H+E+W and observed Y |

Conventional entire-dwelling property eligibility inherits the actual six
types: Entire rental unit, Entire condo, Entire home, Entire townhouse,
Entire villa, Entire loft. No primary review-count/availability restriction.
Missing outcome, coordinates, housing or geographic/accessibility coverage
exclusions are counted and explained; failed city housing qualification blocks
the city rather than silently creating a no-H sample.

## X — inherited qualified baseline only

| Feature | Definition |
| --- | --- |
| `property_type` | Inherited categorical property type, training-fitted encoding for prediction |
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
Unavailable eligible weights remain NULL. Neither H, E nor W is embedded in X.
No area indicator, instant-bookable or review field is added to the primary X.

## H — required neighbourhood residential sale-price context

| Field | Definition / missingness rule |
| --- | --- |
| `housing_price_m2_native` | Prefer full-year 2025 apartment sale-price/m2, positive finite native reported value; never invent/impute |
| `housing_price_currency` | Source-native currency, preserved without invented conversion |
| `housing_reference_period` | Actual period and coverage; preferred 2025 full year, alternative requires explicit amendment |
| `housing_statistic` | Source-reported mean/median/etc. must be qualified and frozen, not assumed |
| `housing_property_scope` | Apartment residential sales; incompatible scope cannot silently substitute |
| `housing_external_area_id` | Source area linked by an evidenced frozen geographic mapping |
| `housing_reference_frame_id` | Within-city external-area membership/values frozen independently of Airbnb outcomes and folds |
| `housing_midrank` | Average ordinal rank for native-price ties; one equal-weight observation per reference area |
| `G_ref` | Positive count of areas in the frozen qualified external frame, including areas without Airbnb listings |
| `housing_context_midrank` | Primary H: `H=(midrank-0.5)/G_ref`; no listing-weighted or fold/sample reranking |
| `log_housing_price_m2_native` | Prespecified sensitivity log(native housing price), replaces the H scale on the same sample/folds |
| `housing_transaction_count` | Observed source count if available; unknown remains NULL |
| `housing_source` / `housing_source_sha256` | Actual provenance/checksum; currently unqualified, not invented |

Source/acquisition date/extent, period, unit, currency, statistic, coverage and
mapping are scientific gates. Missing/suppressed external values cannot be
assigned zero or silently removed to change G_ref. A city without qualified H
is BLOCKED. Narrower-city or descriptive-only scope requires an explicit
amendment. No housing-price outcome or gentrification score is defined.

## E and W — matched accessibility features

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

Inherited thresholds, 30 candidates, inference rules and mandatory no-income
sensitivity are detailed in the [specification](preanalysis_specification.md).
Numerical thresholds are safeguards, not power guarantees. Predictor learning
stays within training data; H is externally measured and is never imputed.
Prediction and common OLS association samples remain separate and versioned.

## Implemented Step 5 source-audit fields

Definition `v4_housing_sources_20261011` preserves `source_id`,
`source_area_id`, `geography_level`, `period`, `property_category`, `currency`,
`unit`, `statistic`, `price_m2_native`, `sale_count`, source flags and documented
area definitions in PostgreSQL `v4_raw.housing_area_period_audit`. NULL prices
and unknown counts remain NULL; reported Copenhagen zero prices are retained
as flagged source evidence, never qualified H. Oslo API category positions are
separate from actual native geographic codes. Quarterly Copenhagen rows and
nested Oslo levels are source audits, not additive counts of qualified areas.

The parent `v4_raw.housing_ingestions` freezes source manifest and source QA
under version/run/city/snapshot. No `H`, `log_H`, reference ranks, listing
assignment, analysis-area mapping or group labels are created in Step 5.
Future housing IDs remain distinct from study masks, official analysis areas
and provider neighbourhood labels until an authorized geographic assignment.
