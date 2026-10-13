# Initial thesis deliverable-gap audit

Copenhagen includes Frederiksberg. This audit precedes generation; model completion does not establish thesis-reporting completeness.

Every one of49 existing figures was inspected visually and checked for dimensions, DPI and lineage. Thirty are historical; six are superseded layouts;13 final figures need page-width typography and300-dpi/vector redesign. None is deleted or overwritten.

| ID | RQ | Required evidence | Status | Existing output | Action |

| --- | --- | --- | --- | --- | --- |

| A1 | Design | Study area and operational neighbourhoods | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| B1 | RQ1 | Nearest straight-line versus network relationship | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| B2 | RQ1 | Nearest-category distance divergence | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| B3 | RQ1 | Food/social and culture/tourism opportunities | EXISTS_NEEDS_REDESIGN | outputs/figures/research/opportunity_comparison.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| B4 | RQ1 | Compact accessibility spatial panels | EXISTS_NEEDS_REDESIGN | outputs/figures/research/accessibility_cells_publication.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| C1 | RQ2 | Main pooled RMSE and heldout fold variation | EXISTS_NEEDS_REDESIGN | outputs/figures/research/within_city_performance.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| C2/C3 | RQ2 | All five paired accessibility contrasts | EXISTS_NEEDS_REDESIGN | outputs/figures/research/accessibility_gains.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| C4 | RQ2 | Adjusted OLS accessibility associations with HC3 intervals | EXISTS_NEEDS_REDESIGN | outputs/figures/research/association_accessibility_coefficients.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| C5 | RQ2 | Existing heldout predictive contributions | EXISTS_NEEDS_REDESIGN | outputs/figures/research/heldout_contributions_publication.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| D1 | RQ3 | Random/neighbourhood/geometric validation comparison | EXISTS_NEEDS_REDESIGN | outputs/figures/research/validation_comparison.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| D2 | RQ3 | Heldout neighbourhood heterogeneity | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| D3 | RQ3 | Registered robustness effect and stability summaries | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| E1 | RQ4 | Six-direction transfer performance matrices | EXISTS_NEEDS_REDESIGN | outputs/figures/research/xgboost_transfer_matrix_publication.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| E2 | RQ4 | Transfer accessibility gains relative to baseline | EXISTS_NEEDS_REDESIGN | outputs/figures/research/xgboost_transfer_gains_publication.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| E3 | RQ4 | Direct network-versus-Euclidean transfer contrasts | EXISTS_NEEDS_REDESIGN | outputs/figures/research/ols_transfer_gains_publication.png | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| E4 | RQ4 | Observed versus predicted relative-price diagnostics | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| E5 | RQ4 | Direction reversal asymmetry | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| F | Appendix | Prescribed residual spatial diagnostics | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs |

| A2 | Design | Every sample-flow stage by city | READY_EXISTING | outputs/tables/research/sample_flow.csv | Table-only treatment; preserve all stages without a separate sample-flow figure |

| T1 | Design | City/sample summary | EXISTS_NEEDS_REDESIGN | outputs/tables/research/sample_flow.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T2 | Design | Complete X/E/W feature definitions | EXISTS_NEEDS_REDESIGN | docs/analysis/data_dictionary.md, config/study/design.json | Generate full CSV plus readable Markdown summary from the pinned results |

| T3 | RQ1 | Accessibility descriptive statistics | EXISTS_NEEDS_REDESIGN | outputs/tables/research/measurement_comparison.json | Generate full CSV plus readable Markdown summary from the pinned results |

| T4 | RQ2 | Primary predictive performance | EXISTS_NEEDS_REDESIGN | outputs/tables/research/within_city_performance.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T5 | RQ2 | All five paired model contrasts and stability | EXISTS_NEEDS_REDESIGN | outputs/metrics/neighbourhood/paired_contrasts.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T6 | RQ2 | Final three-city OLS association results | EXISTS_NEEDS_REDESIGN | outputs/tables/research/association_coefficients.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T7 | RQ3 | Validation-strategy comparisons | EXISTS_NEEDS_REDESIGN | outputs/tables/research/validation_comparison.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T8 | RQ4 | All six transfer directions and four models | EXISTS_NEEDS_REDESIGN | outputs/tables/research/transfer_performance.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T9 | RQ4 | All transfer model contrasts and stability | EXISTS_NEEDS_REDESIGN | outputs/tables/research/transfer_accessibility_contrasts.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T10 | RQ3 | Every registered robustness status, estimand and result | EXISTS_NEEDS_REDESIGN | outputs/tables/research/robustness_registry.csv | Generate full CSV plus readable Markdown summary from the pinned results |

| T11 | All | RQ claims and limitations | MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS | None | Generate full CSV plus readable Markdown summary from the pinned results |

| Same-destination route circuity | All | Nearest Euclidean and nearest walking destinations can differ; no frozen same-object route-pair output exists | NOT_NEEDED | None | Document limitation; do not invent unsupported science or a document renderer |

| New fitted SHAP models | All | Existing heldout SHAP summaries are available; no new model fitting is needed | NOT_NEEDED | None | Document limitation; do not invent unsupported science or a document renderer |

| Active DOCX/PDF document exports | All | Only a historical income-addendum DOCX updater exists; no supported active Markdown document-export pipeline | NOT_NEEDED | None | Document limitation; do not invent unsupported science or a document renderer |


## Reconstruction boundary

No scientific reconstruction is needed: public provider geometries, common samples, saved predictions, full model contrasts, coefficients, robustness and heldout contributions already exist in the pinned final SQL packages. Missing plots require safe reporting aggregation only. No tuning, fitting, source acquisition, network rebuild, source definition or outcome changes are authorized.


## Publication and export limits

Preserve earlier results; create functional thesis paths. Use minimum-five aggregate spatial cells/bins, no row exports, shared styles and vector/300-dpi outputs. The historical DOCX income updater is not an active proposal/plan/results renderer. Markdown remains authoritative; no unreliable document pipeline is invented.


## Final-source evidence

[Frozen reporting catalog](frozen_reporting_sources.json) records all current selectors and751 immutable package identities. [Machine audit](deliverable_gap_audit.json) records all49 figure classifications and the exact initial gaps. The completion audit will be a separate file, retaining this initial evidence.
