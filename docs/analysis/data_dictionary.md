# Common feature dictionary and harmonization

All four models share the frozen common prediction rows. Source, native context and matched accessibility qualifications are implemented; missing listing controls remain explicit and learned preprocessing uses training data only. Income and residential prices are absent. Stockholm association inference remains blocked by the union missingness guard; this does not block predictive preprocessing.

| Feature | Copenhagen | Oslo | Stockholm | Common definition | Units | Transformation | Qualification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `accommodates` | Same definition | Same definition | Same definition | accommodates | count | none | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `bedrooms` | Same definition | Same definition | Same definition | bedrooms | count | none | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `bathrooms_effective` | Same definition | Same definition | Same definition | Structured bathrooms, else inherited exact text parser | bathrooms | explicit parser provenance | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `log1p_minimum_nights` | Same definition | Same definition | Same definition | minimum nights | count | log1p | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `superhost` | Same definition | Same definition | Same definition | Source superhost status | 0/1 | t/true/yes and f/false/no mapping; missing NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `log1p_host_listings_count` | Same definition | Same definition | Same definition | host listings count | count | log1p | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_wifi` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_dishwasher` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_washer` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_dryer` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_workspace` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_free_parking` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_private_balcony` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `amenity_self_checkin` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `log_population_density` | Same definition | Same definition | Same definition | Official population / compatible matching area | persons/km² | natural log | QUALIFIED_SOURCE_NATIVE_WITH_RECORDED_LIMITS; see context_audit.json |
| `distance_centre_euclidean_km` | Same definition | Same definition | Same definition | Metric Euclidean distance to frozen OSM civic anchor | km | none | QUALIFIED_SOURCE_NATIVE_WITH_RECORDED_LIMITS; see context_audit.json |
| `property_type` | Same definition | Same definition | Same definition | One of six conventional dwelling types | category | source-only one-hot; unknown levels ignored | FRESH_SOURCE_PARSED; missingness audited in sample_audit.json |
| `nearest_station_euclidean_km` | Same definition | Same definition | Same definition | Nearest matched named rail/metro/urban-rail station | km | none | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |
| `nearest_bus_euclidean_km` | Same definition | Same definition | Same definition | Nearest matched consolidated bus stop | km | none | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |
| `log1p_food_e` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |
| `log1p_culture_e` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |
| `nearest_station_walking_minutes` | Same definition | Same definition | Same definition | Minimum directed foot-network cost to matched rail stations including both connectors | minutes | none | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |
| `nearest_bus_walking_minutes` | Same definition | Same definition | Same definition | Minimum directed foot-network cost to matched bus stops including both connectors | minutes | none | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |
| `log1p_food_w` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |
| `log1p_culture_w` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | MATCHED_SOURCE_RECOMPUTED; see accessibility_audit.json and sample_audit.json |

Outcome: within-city `log_price` is log original positive observed native nightly asking price. Transfer `relative_log_price` subtracts the one city reference mean computed before feature exclusions. Raw label, raw polygon source, operational group, private source key, CRS, sample/fold/source hashes and bathroom parser provenance remain separate identifiers/audit fields.

Exact inherited taxonomy: food uses restaurant/cafe/bar/pub; culture uses
museum/gallery/attraction/viewpoint, theatre and monument/castle/palace.
The query's broader candidate tags are filtered by the preserved category
function, not by observed prices. Named stations use railway station/halt or
qualified public-transport station mode tags; bus stops follow the inherited
consolidation adapter. Each E/W pair uses the same resulting category universe.
Shortest routes include source and destination connectors and directed foot
permissions at5km/h. Route failure remains missing; a finite zero accessible
opportunity count remains an observed zero. Primary feature filtering is common
to all four models.

Training-only imputation indicators and one-hot levels are derived model columns,
not new scientific variables chosen after outcomes. Descriptive contribution
tables report each encoded term's actual observation count; encodings are learned
within training, so a term unavailable in a particular fold is not fabricated.
Never interpret SHAP allocation among correlated E/W features as causal attribution.
