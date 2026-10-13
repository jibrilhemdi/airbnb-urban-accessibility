# Thesis outputs

This folder contains the current results for Copenhagen–Frederiksberg, Oslo
and Stockholm. Start with the [results report](../reports/research_results.md)
and [figure/table placement guide](../reports/thesis_figure_recommendations.md).

| Folder or file | Contents |
| --- | --- |
| `figures/` | 18 PNG figures at 300 dpi; no PDF/SVG duplicates |
| `tables/` | 12 thesis tables, each as CSV and readable Markdown |
| `metrics/` | 10 supporting views, each as CSV and Markdown |
| `thesis_results.zip` | Portable outputs, reports, methods and provenance |

Use `primary_model_performance.png` for city model comparisons,
`neighbourhood_performance_variation.png` for local variation, and
`transfer_performance.png` for cross-city results. `study_areas.png` and
`accessibility_spatial.png` show square city panels with frozen neighbourhood
boundaries. Map cells require at least five observations.

M0 uses controls; ME adds Euclidean accessibility; MW adds walking accessibility;
MEW adds both. Lower RMSE is better. A negative ΔRMSE favours the first model in
the comparison. Within-city errors are in log-price units; transfer errors are
in city-relative log-price units.

CSV files retain full precision. Figure captions explain intervals, suppression
and display limits. The [artifact manifest](../reports/thesis_artifact_manifest.json)
and package manifest (`reports/thesis_release_manifest.json`) record checksums
and frozen source identities. Verify with `make thesis-check` and
`make thesis-release` from the repository root.

Previous outputs are preserved in
[the archive](../archive/before_output_cleanup/manifest.json). No raw listings,
individual predictions, credentials or fitted models are included here.
