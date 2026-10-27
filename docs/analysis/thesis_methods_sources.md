# Methods manuscript checks — 27 October 2026

The chapter describes the completed executed design. This is reporting, not a
new specification, source acquisition, fit, inference run or scientific amendment.
The source files named below remain unchanged. Their hashes are recorded in
`thesis_report/tables/methods_assets_manifest.json`.

## Primary references checked

- [Chen and Guestrin (2016)](https://arxiv.org/abs/1603.02754), with the
  [paper text](https://arxiv.org/html/1603.02754v3): XGBoost as tree boosting.
  Added `methods_chen2016`; the description does not claim that flexibility
  guarantees a predictive improvement.
- [Roberts et al. (2017)](https://doi.org/10.1111/ecog.02881), also checked via
  [the author's publication page](https://florianhartig.github.io/publications/roberts2017cross/):
  choose validation geography for the prediction task and recognise the limits
  of blocked evaluation. Only the original abstract/publication metadata were
  used, not the page's separately labelled AI-generated synopsis. Existing
  citation key `roberts2017` is retained; inherited duplicate entries are not
  silently reconciled.
- [MacKinnon, Nielsen and Webb (2023)](https://doi.org/10.1016/j.jeconom.2022.04.001):
  cluster-robust inference and restricted wild-cluster bootstrap. Added
  `methods_mnw2023`. No claim of reliable independent-cluster inference despite
  the remaining spatial dependence or small number of groups is introduced.
  The author's supplementary landing page timed out; the publisher's paper
  supplies the verified metadata and method reference.

## Checks against executed code

- `src/study/modeling.py`: numeric median imputation and missingness indicators;
  first-category-dropped one-hot property encoding with unknown categories
  ignored; no standard scaling; intercept OLS; squared-error XGBoost; exact
  30-candidate/four-inner-fold mean-RMSE selection. Preprocessing is inside each
  training/tuning pipeline; all-missing required training predictors block.
- `src/study/validation.py`: leave-one-operational-neighbourhood-out; 15 test /
  500 complementary training support; inner size-balanced folds of 1 km cells;
  random five-fold and six grids (1, 1.5, 2 km; zero and half-block origins).
- `src/study/accessibility.py`: shared deduplicated destinations, directed foot
  graph, both connectors, speed 5 km/h, nearest-category km/minutes, primary
  833 m/10-minute opportunities and log(1+count). The common support includes
  source-edge coverage checks; route missingness is never a zero count.
- `src/reporting/study_results.py`: pooled listing-level RMSE and supporting
  metrics; five paired contrasts; 2,000 whole-neighbourhood resamples with
  replacement and 2.5/97.5 percentiles, conditional on saved predictions.
- `src/study/association.py`, `src/reporting/study_diagnostics.py`, and
  `src/pipeline/inference.py`: genuine union complete cases, current uniform
  post-observation 10% eligibility, rank/condition/VIF diagnostics, HC3 and
  coefficient-wise restricted WCR11 using Webb six-point weights with CRV1
  studentisation, 9,999 replications and no multiplicity correction.
- `src/reporting/study_spatial.py`: eight-neighbour/499-permutation diagnostics;
  the trigger uses held-out OLS MW residuals, |I| > 0.05 and p < 0.05.
  Triggered GM_Error_Het sensitivity is MW only. Area-fixed-effect checks cover
  all four models and absorb area-constant density. These are association
  checks, not additional predictive estimators.
- `src/study/modeling.py` / `evaluation.py`: source-only tuning, preprocessing
  and refitting for all six ordered city pairs. Target observed prices enter
  the frozen target benchmark and scoring, not fitting or recalibration.
- Robustness settings/statuses follow `design.json`, the current plan and the
  completed registry. Existing fitted artifacts and primary samples stay fixed.

## Table 4.3 percentage definition

The former bedroom-count display is replaced with the missing asking-price
percentage: 100 × missing-price count / original listing N within the same city
and accommodation type. City totals use total missing prices / total N, not
an average of category percentages. N=0 has an undefined percentage and is
shown as a dash. Original blank counts and source grouping are unchanged;
nonpositive observed prices are not recoded as missing. The database remains
the authoritative source; rendering runs only read-only queries.

The checkpoint includes only the verified Roberts entry needed by Methods from
the existing working bibliography; unrelated bibliography edits are not staged.
The working bibliography itself remains byte-identical. An isolated build using
only checkpoint content also compiles, so it does not depend on the researcher's
uncommitted literature or bibliography additions. The full local reading build
continues to include those researcher drafts.

## Figure regeneration feedback — 27 October 2026

The four requested images under `archive/before_output_cleanup/outputs/figures/reporting/`
are visual references from the earlier Copenhagen analysis. In particular, its
price/validation sample of 12,412 is not the final 12,408. The historical
pipeline is not rerun and the archived PNGs/manifests remain byte-preserved.

`scripts/build_thesis_explanatory_figures.py` creates four manuscript PNGs from
the current pinned study, without changing scientific selectors or fits:

- Price histograms read the final common predictive samples in PostGIS for
  Copenhagen (12,408), Oslo (8,529) and Stockholm (2,495). Native-currency panels
  stop at each city's 99th percentile for display; log panels include every
  observation. The manifest records bins/counts, quantiles and observations
  above the display range. No analytical trimming or outcome filling occurs.
- The catchment uses current SQL destinations and the exact OSM network sources
  recorded in the final Copenhagen accessibility package. The executed graph
  builder and pedestrian-direction code must match that package's hashes, and
  all graph QA fields must reproduce exactly. A read-only public illustration
  then routes from the nearest node on the largest weak component to City Hall
  Square +1,500 m east/-1,050 m northing, with a node-ID tie break. This retains
  the earlier public location rule, independent of prices/listing locations.
  Origin connector is zero; destination snap connectors count against the
  10-minute/5 km/h budget. Both panels show identical current destinations
  within 833 m. No listing feature is rebuilt and no service-area polygon is
  inferred. Node ID, counts, current snapshot, graph QA and source receipts
  are recorded in the new manifest. Coincidentally unchanged displayed counts
  do not mean old analytical values were copied.
- The random/neighbourhood illustration joins the saved outer-test memberships
  to the exact common sample. It displays random fold 1 and the saved Nørrebro
  holdout. Every scheme has one membership per listing; full support counts
  match the frozen validation summary. Fixed-size pies show the training/test
  shares at 500 m cell centres only where total N is at least five. No listing
  coordinates, identifiers or membership rows are exported. Display suppression
  does not alter training/test counts or fitted evaluations.
- The six grid panels use the saved 1/1.5/2 km configurations, at zero and
  half-cell shifts on both axes. Every occupied cell must belong to a single
  saved test fold. Cells with fewer than five observations are suppressed.
  Colours are local fold identifiers, not corresponding regions across panels.
  The maps explain holdout geometry; they are not new performance results.

The two validation illustrations use the frozen Copenhagen provider geography;
surrounding municipalities are the existing presentation-only context. They
are examples of the three-city design, not claimed to display all cities.
Spatial source coordinates are EPSG:4326 and all illustration operations are
EPSG:25832. North arrows use N, with grid north specified in captions.

The new manifest pins SQL summary and record hashes, all scientific package
identities, source selectors, archived visual-reference hashes, code and output
hashes. The generator's deterministic `--check` compares every PNG and manifest
byte. No acquisition, database write, feature replacement, fold regeneration,
fitting, tuning or new scientific result is performed. The simpler native
LaTeX workflow remains reproducible but is replaced in the manuscript by the
more informative geographic illustration.
