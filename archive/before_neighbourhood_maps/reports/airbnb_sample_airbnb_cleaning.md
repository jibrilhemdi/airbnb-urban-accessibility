# Version 3 Airbnb sample construction

Snapshot 2026-06-30. PostgreSQL V3 cleaned listings were rebuilt from immutable source imports. No outcome was imputed. Sample flags select conventional entire homes with observed positive listed DKK prices and valid coordinates. Official assignment, core context and accessibility completeness are handled explicitly downstream.

| Sample rule | Remaining N | Excluded N |
|---|---:|---:|
| raw_listings | 23,144 | 0 |
| in_study_area | 23,144 | 0 |
| entire_home_apt | 21,368 | 1,776 |
| conventional_residential | 21,080 | 288 |
| valid_positive_price | 12,521 | 8,559 |
| valid_coordinates | 12,521 | 0 |

Source amenity prevalence and missingness are descriptive audits only. The eight primary amenity variables are prespecified in `model_specification.py`; no prevalence or model performance selects the Version 3 feature set. Missing amenity JSON remains missing, not an inferred absence. Distances use source EPSG:4326 and metric EPSG:25832. Reviews and calendar availability are not bookings or realised occupancy.
