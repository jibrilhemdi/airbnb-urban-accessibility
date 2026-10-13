# Airbnb prices and urban accessibility

This thesis studies Copenhagen–Frederiksberg, Oslo and Stockholm using June 2026
Inside Airbnb listings. It asks how walking and straight-line accessibility
differ, what they add to nightly-price prediction, how results vary across
neighbourhoods, and how pricing relationships transfer between capital cities.

The analysis is complete. Start with the [results](reports/research_results.md),
[findings by research question](reports/findings_by_research_question.md), and
[thesis figure/table guide](reports/thesis_figure_recommendations.md).

## Data and methods

| City | Prediction sample | Complete-case association sample |
| --- | ---: | ---: |
| Copenhagen–Frederiksberg | 12,408 | 12,285 |
| Oslo | 8,529 | 8,152 |
| Stockholm | 2,495 | 2,348 |

The study combines observed Airbnb asking prices, Inside Airbnb neighbourhood
polygons, official population density, and OpenStreetMap pedestrian networks
and destinations. Housing prices and income are excluded. Missing nightly prices
are excluded, never imputed.

**M0** contains dwelling, host, amenity, density and centrality controls;
**ME** adds Euclidean accessibility; **MW** adds walking accessibility;
**MEW** adds both. OLS and XGBoost use identical city samples and folds.
Neighbourhood holdouts are primary; random and spatial-block validation are
comparisons. Preprocessing and tuning use training data only.

All six directional transfers use source-city fitting and tuning, with no target
refitting. Within-city outcomes are log nightly prices; transfer outcomes are
city-relative log prices. Results are observational. Accessibility improves
primary XGBoost point errors in Copenhagen and Stockholm, with small adverse
changes in Oslo; walking is not universally superior. The
[10% complete-case eligibility amendment](docs/analysis/association_missingness_amendment_20261013.md)
was made after observing missingness and is explicitly disclosed.

## Use and reproduce the project

| Location | Purpose |
| --- | --- |
| `src/study/` | Scientific workflow, samples, validation and models |
| `src/reporting/` | Frozen-result figures, tables, reports and map context |
| `config/study/` | Scientific definitions and immutable run selectors |
| `outputs/figures/`, `tables/`, `metrics/` | Current 300-dpi PNG figures and CSV/Markdown results |
| `reports/` | Findings, writing guidance, provenance and verification |
| `docs/analysis/` | Methods, source registry, decisions and execution log |
| `archive/` | Checksum-preserved previous outputs and implementation |

Install the pinned dependencies in the audited Python 3.13 environment. Connection
settings use one `.env`; [config/environment.example](config/environment.example)
is the template. PostgreSQL/PostGIS is the persistent data layer.

```sh
python -m pip install -r requirements.txt
make study-status
make thesis-check
make thesis-release
make test
```

`outputs/thesis_results.zip` is the portable public package. Scientific
reproduction also requires private sources and saved predictions; see the
[reproduction guide](docs/analysis/reproducibility.md) and
[specification](docs/analysis/preanalysis_specification.md). Completed selectors
prevent accidental refitting. Raw data, credentials, fitted models and individual
predictions stay outside the public release. Work remains on `v4`.
