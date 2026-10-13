# Version 3 qualified income protocol amendment

Area income is operationalised as 2024 equivalised disposable income derived from decile means. Copenhagen city-district values use Copenhagen Municipality's KKIND5, while Frederiksberg uses Statistics Denmark's nominal IFOR35. Both sources represent closely aligned equivalised-disposable-income concepts and use ten person-based decile groups, but some table-specific processing details cannot be proven identical. The measure is therefore treated as pragmatically harmonised. All primary models include the measure, and a prespecified no-income robustness analysis tests whether substantive accessibility conclusions depend on this cross-source context variable.

Accepted by explicit user decision on 4 October 2026. Preflight status: `qualified_accepted`; record metadata: `qualified`.

## Frozen source table

     analysis_area        analysis_area_name source_table equiv_disposable_income_2024
            cph_01                  Indre By       KKIND5                     439867.1
            cph_02                  Østerbro       KKIND5                     396447.1
            cph_03                  Nørrebro       KKIND5                     282754.4
            cph_04 Vesterbro-Kongens Enghave       KKIND5                     345346.9
            cph_05                     Valby       KKIND5                     328052.7
            cph_06                   Vanløse       KKIND5                     352122.4
            cph_07            Brønshøj-Husum       KKIND5                     319085.2
            cph_08                Bispebjerg       KKIND5                     275846.2
            cph_09                Amager Øst       KKIND5                     335103.6
            cph_10               Amager Vest       KKIND5                     340653.8
frederiksberg_0147             Frederiksberg       IFOR35                     404647.2

Each of the eleven areas has all ten observed decile means. Common transformation: `(d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8 + d9 + d10) / 10`. Values are annual DKK; the model uses `income_100k_dkk = equiv_disposable_income_2024 / 100000`.

KKIND5 raw price basis remains `not_confirmed`; IFOR35 uses nominal current prices (`006`). Pragmatically harmonised equivalised disposable income; exact table-specific weighting, finite-count/tie handling, eligibility, variable version, income-treatment and KKIND5 raw price-basis details cannot be proven identical. Equal weighting follows the conceptual ten equal person groups; no model-dependent weights are used.

## Supportive QA

Copenhagen published totals: KKIND5 340,620.1 DKK, nominal IFOR35 340,949.1 DKK; City minus national −329 DKK (absolute 329 DKK; −0.0964953%). Tenth-decile discrepancy: −3,376 DKK. This small aggregate difference supports the practical decision but does not prove exact equivalence. Eligible district/decile counts and a weighted district reconstruction remain NULL.

## Mandatory robustness and provenance

M0_no_income, ME_no_income, MW_no_income and MEW_no_income omit only income. They use the identical frozen sample, saved random-5/geographic-11 outer and four inner folds, training-only preprocessing, thirty XGBoost candidates and tuning budgets. Outputs compare OLS accessibility coefficients, RMSE, MAE, R², paired ΔRMSE and per-area geographic performance. Prespecified material-change flags are documented in `config/qualified_income_decision.json`; they never select the primary model.

The source table is authoritative in PostgreSQL `v3_features.qualified_area_income`; aggregate CSVs are exports. Every record retains institution/table/year/basis/deciles/transformation/value/source URL/acquisition/extent/SHA/qualification. Raw files and all earlier source investigations remain intact in `archive/income_investigations` and `reports/income_harmonisation_previous_sources.md`. The municipal investigation is historical evidence; it is not reopened and the unsent contact draft remains unsent. No CTX family or Frederiksberg dummy is added.

## Limitations

Qualified cross-source comparability leaves unresolved processing and price-basis details. The mandatory no-income analysis measures dependence of accessibility conclusions on that context control.
