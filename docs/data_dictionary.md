# Qualified area-income dictionary

The authoritative eleven-row source freeze is `v3_features.qualified_area_income`; CSVs are exports. The analytical sample dictionary is generated separately when the full run reaches dataset construction.

| Field | Definition |
| --- | --- |
| `analysis_area` / `analysis_area_name` | Official ten Copenhagen districts plus Frederiksberg as eleven peer areas. Not a primary predictor. |
| `equiv_disposable_income_2024` | Annual DKK arithmetic mean of ten published equivalised-disposable-income decile means, common year 2024. |
| `income_100k_dkk` | Core M0 predictor: `equiv_disposable_income_2024 / 100000`; inherited by ME/MW/MEW. |
| `source_institution` / `source_table` / `source_geography` | Copenhagen Municipality KKIND5 district codes 1001–1010; Statistics Denmark IFOR35 municipality 147 for Frederiksberg. |
| `year` / `price_basis` | 2024; IFOR35 nominal current prices (006); KKIND5 `not_confirmed`, retained as an explicit qualification. |
| `deciles` | Exactly ten observed ordered means as decimal strings; missing/suppressed/nonfinite/ambiguous national zero cells fail. Negative incomes remain observed values. |
| `transformation` | Frozen common sum(d1…d10)/10. Equal weighting follows ten conceptual equal person groups; no Airbnb-dependent weights. |
| `harmonisation_status` / `qualification` | Record metadata `qualified`; active acceptance `qualified_accepted`. Unresolved exact weighting/ties/eligibility/variable version/income-treatment/City price-basis details remain explicit. |
| `source_path` / `source_checksum` / `source_file_id` | Immutable raw CSV, SHA-256 and PostgreSQL meta.source_files identity. All metadata/selections also checksum checked. |
| `source_url` / `acquired_at_utc` / `geographic_extent` | Original institutional source URL, acquisition timestamp and stated extent. Preserved in the frozen record and source inventory. |
| `eligible_person_count` | Explicit NULL; exact 2024 eligible group/district counts unavailable. Never substitute total population or listing counts. |
| `log_population_density` | Natural log of population / gross official assignment-polygon km², EPSG:25832; population 2026 Q3. |

Copenhagen published-total QA: 340620.1 vs 340949.1 DKK, signed −329 DKK, −0.0964953%, tenth decile −3376 DKK. Supportive only; weighted district reconstruction remains NULL. Historical candidate and municipal evidence tables retain their original unverified statuses.

Mandatory no-income models omit only `income_100k_dkk`. The transparent original value remains diagnostic metadata and is excluded from their predictors. See `config/qualified_income_decision.json` and `reports/income_harmonisation_status.md`.
