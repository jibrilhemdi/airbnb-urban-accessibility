# Urban accessibility, Airbnb asking prices and cross-city transfer

Copenhagen refers to the combined Copenhagen–Frederiksberg study area.
The study compares Copenhagen, Oslo and Stockholm using the preserved June 2026
Inside Airbnb detailed snapshots. It is observational and predictive. Previous
analyses and feasibility findings were observed before this explicit amendment;
the design is not retrospectively preregistered. Final empirical reporting must
use newly recomputed results under [the active specification](analysis/preanalysis_specification.md).

The questions are:

1. How do Euclidean and walking-network measures characterize urban accessibility
   differently across Copenhagen, Oslo and Stockholm?
2. How much predictive information do Euclidean and walking-network accessibility
   measures add to Airbnb asking-price models within each city?
3. How robust are the predictive gains from accessibility when models are
   evaluated in geographically unseen neighbourhoods, and how consistent are
   those gains across Copenhagen, Oslo and Stockholm?
4. To what extent do Airbnb pricing relationships learned in one city transfer
   to another city, and does accessibility improve this transferability?

Matched destinations isolate representation differences: straight-line proximity
and opportunities versus pedestrian travel times and opportunities. Density,
centrality and common dwelling, host and amenity controls form X. M0=X, ME=X+E,
MW=X+W and MEW=X+E+W are evaluated on identical city samples and held-out rows.
OLS provides adjusted associations and a predictive baseline; XGBoost evaluates
nonlinear predictive information using the inherited frozen search budget.
Geographic holdouts are primary, random folds a benchmark, geometric blocks a
robustness analysis. Neither representation is expected or required to win.

Within-city analysis predicts log observed nightly asking price in native
currency. Six separate directional transfers predict relative log price after
subtracting each city's frozen reference mean. Each fit uses one source city;
the target city's outcomes inform only its benchmark and evaluation. This tests
structural transferability after removing citywide price-level differences,
not absolute-price deployment in an unseen city.

Interpretation concerns measurement, adjusted associations, predictive information,
geographic generalization and transferability. It does not establish causal
effects on prices or neighbourhood change, universal network superiority or
representativeness of other Nordic/European cities. Missing-price selection,
anonymized coordinates, context boundary compatibility, OSM completeness and
timing mismatch remain limitations to measure and report.

The [research plan](analysis/research_plan.md) distinguishes implemented work
from blocked empirical stages. Historical evidence remains accessible through
the [preservation inventory](analysis/path_inventory.json).

Implementation is now documented in the generated
[publication handover](analysis/research_report_publication.md) and
[findings](analysis/findings.md). All three cities' primary predictive ladders,
the six single-source directional transfers and independent registered
robustness checks were freshly executed under this final design. Copenhagen
and Oslo association inference completed; Stockholm's preserved union-missingness
guard blocks its association and dependent inference. The full requested study
therefore remains partial. Reported numerical findings come from the new
authoritative SQL results, not earlier analyses or synthetic fixtures.
