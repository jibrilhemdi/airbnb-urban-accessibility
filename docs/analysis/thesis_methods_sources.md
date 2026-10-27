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
