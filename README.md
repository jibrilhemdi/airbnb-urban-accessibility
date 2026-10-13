# Airbnb prices and urban accessibility

A completed study of Copenhagen–Frederiksberg, Oslo and Stockholm, using
Inside Airbnb listings from June 2026. It compares straight-line and walking
accessibility, prediction in unseen neighbourhoods, and transfer between cities.

Start with the [results](reports/research_results.md) and
[findings by research question](reports/findings_by_research_question.md).
The [placement guide](reports/thesis_figure_recommendations.md) selects ten main
figures and eight main tables for the thesis.

| Location | What you will find |
| --- | --- |
| [outputs/](outputs/README.md) | Current thesis outputs: figures, tables and supporting metrics |
| `outputs/figures/` | 18 figures, PNG only, 300 dpi |
| `outputs/tables/` | Thesis tables: readable Markdown and full-precision CSV |
| `outputs/metrics/` | Neighbourhood results, robustness and aggregate diagnostics |
| `outputs/thesis_results.zip` | One portable copy of the outputs, reports and provenance |
| `reports/` | Results, writing guidance, claims and verification manifests |
| `archive/` | Previous outputs and documentation, preserved with checksums |

Models are **M0** (controls), **ME** (+ Euclidean accessibility), **MW**
(+ walking accessibility) and **MEW** (+ both). The study uses OLS and XGBoost,
with neighbourhood holdouts and six directional city transfers. Results are
observational; within-city errors use log nightly price, while transfer errors
use city-relative log price. Missing prices are excluded, never imputed.
The [10% association missingness amendment](docs/analysis/association_missingness_amendment_20261013.md)
was made after observing the data.

To verify the outputs in the audited environment:

```sh
python -m pip install -r requirements.txt
make thesis-check
make thesis-release
make test
```

PostgreSQL/PostGIS is the analytical authority. Reproduction also requires the
private source data and saved predictions; connection settings use one `.env`
with [this template](config/environment.example). See
[reproduction instructions](docs/analysis/reproducibility.md) for scientific
checks and commands. Raw data, credentials, fitted models and individual
predictions are excluded from the public outputs. Work remains on `v4`.
