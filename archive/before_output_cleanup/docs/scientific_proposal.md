# Urban accessibility, Airbnb asking prices and cross-city transfer

Copenhagen refers to the combined Copenhagen–Frederiksberg study area.
The completed study compares Copenhagen, Oslo and Stockholm using the preserved June 2026
Inside Airbnb detailed snapshots. It is observational and predictive. Previous
analyses and feasibility findings were observed before this explicit amendment;
the design is not retrospectively preregistered. Final empirical reporting uses
the complete rerun under [the active specification](analysis/preanalysis_specification.md),
with frozen fits preserved during the subsequent reporting task.

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
centrality and common dwelling, host and amenity controls form X. Income and
residential property prices are excluded; dwelling category remains a listing
control. M0=X, ME=X+E, MW=X+W and MEW=X+E+W were evaluated on identical city
samples and held-out rows.
OLS provides adjusted associations and a predictive baseline; XGBoost evaluates
nonlinear predictive information using the inherited frozen search budget.
Inside Airbnb operational neighbourhood holdouts are primary, with 11/17/11
groups and a minimum of 15 outer-test observations and 500 complementary
training observations. Random folds are a benchmark; six geometric-block
designs are robustness analyses. All learned transformations and the frozen
30-candidate, four-inner-fold search used training data only. Neither
representation was expected or required to win.

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

The [research plan](analysis/research_plan.md) records completed empirical and
reporting stages separately. Historical evidence remains accessible through
the [preservation inventory](analysis/path_inventory.json).

The primary factual basis for thesis writing is the generated
[research results](../reports/research_results.md), with
[RQ-by-RQ findings](../reports/findings_by_research_question.md),
[figure/table recommendations](../reports/thesis_figure_recommendations.md) and
[claims audit](final_claims_for_thesis.md). The earlier
[publication handover](analysis/research_report_publication.md) remains intact.
The predictive analyses and all six transfers are the completed, freshly
executed fits from this design. Association inference was rerun for all three
cities under the researcher-approved
[post-observation 10% missingness amendment](analysis/association_missingness_amendment_20261013.md).
The common complete-case samples and inference procedures remain unchanged.
The 10% choice is not presented as preregistered or a universal standard.
Numerical findings come from authoritative SQL. Scientific completeness is
certified by the preserved [scientific release audit](analysis/release_audit.json).
Thesis completeness additionally requires the expanded publication checks,
verified artifact manifest, populated release package and final reporting audit.
Authoritative documents are Markdown; no supported active DOCX/PDF document
renderer exists. Scientific figures have PNG, PDF and SVG exports.
