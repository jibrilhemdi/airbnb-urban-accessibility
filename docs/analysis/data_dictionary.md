# Common feature dictionary and harmonization

All four models share the final common prediction rows. Context/accessibility qualification is pending; this table freezes definitions rather than claiming empirical completeness. Income and residential prices are absent.

| Feature | Copenhagen | Oslo | Stockholm | Common definition | Units | Transformation | Qualification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `accommodates` | Same definition | Same definition | Same definition | accommodates | count | none | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `bedrooms` | Same definition | Same definition | Same definition | bedrooms | count | none | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `bathrooms_effective` | Same definition | Same definition | Same definition | Structured bathrooms, else inherited exact text parser | bathrooms | explicit parser provenance | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `log1p_minimum_nights` | Same definition | Same definition | Same definition | minimum nights | count | log1p | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `superhost` | Same definition | Same definition | Same definition | Source superhost status | 0/1 | t/true/yes and f/false/no mapping; missing NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `log1p_host_listings_count` | Same definition | Same definition | Same definition | host listings count | count | log1p | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_wifi` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_dishwasher` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_washer` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_dryer` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_workspace` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_free_parking` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_private_balcony` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `amenity_self_checkin` | Same definition | Same definition | Same definition | Prespecified exact source amenity indicator | 0/1 | missing JSON retained NULL | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `log_population_density` | Same definition | Same definition | Same definition | Official population / compatible matching area | persons/km² | natural log | QUALIFIED_SOURCE_NATIVE_WITH_RECORDED_LIMITS; see context_audit.json |
| `distance_centre_euclidean_km` | Same definition | Same definition | Same definition | Metric Euclidean distance to frozen OSM civic anchor | km | none | QUALIFIED_SOURCE_NATIVE_WITH_RECORDED_LIMITS; see context_audit.json |
| `property_type` | Same definition | Same definition | Same definition | One of six conventional dwelling types | category | source-only one-hot; unknown levels ignored | INHERITED_PARSER; CITY_SCHEMA_AUDIT_PENDING |
| `nearest_station_euclidean_km` | Same definition | Same definition | Same definition | Nearest matched rail or bus destination | km | none | SOURCE_QUALIFICATION_PENDING |
| `nearest_bus_euclidean_km` | Same definition | Same definition | Same definition | Nearest matched rail or bus destination | km | none | SOURCE_QUALIFICATION_PENDING |
| `log1p_food_e` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | SOURCE_QUALIFICATION_PENDING |
| `log1p_culture_e` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | SOURCE_QUALIFICATION_PENDING |
| `nearest_station_walking_minutes` | Same definition | Same definition | Same definition | Nearest matched rail or bus destination | minutes | none | SOURCE_QUALIFICATION_PENDING |
| `nearest_bus_walking_minutes` | Same definition | Same definition | Same definition | Nearest matched rail or bus destination | minutes | none | SOURCE_QUALIFICATION_PENDING |
| `log1p_food_w` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | SOURCE_QUALIFICATION_PENDING |
| `log1p_culture_w` | Same definition | Same definition | Same definition | Matched destination opportunity count | count | log1p; 833m E /10min W | SOURCE_QUALIFICATION_PENDING |

Outcome: within-city `log_price` is log original positive observed native nightly asking price. Transfer `relative_log_price` subtracts the one city reference mean computed before feature exclusions. Raw label, raw polygon source, operational group, private source key, CRS, sample/fold/source hashes and bathroom parser provenance remain separate identifiers/audit fields.
