# Scope change log — housing-inclusive v4 to accessibility-only v4

Date: 11 October 2026. Requested by the researcher after reviewing housing-data feasibility.

| Item | Prior active v4 | Revised active v4 |
|---|---|---|
| Primary M0 | X+H | X |
| Other models | X+H+E / X+H+W / X+H+E+W | X+E / X+W / X+E+W |
| Model family | Four housing-default models (earlier draft had eight) | Four accessibility models without H |
| Main sample | Housing-qualified | Eligible/accessible common sample; no residential-price filter |
| Folds | Housing-unit-safe | Qualified official-area holdouts; geometric sensitivities |
| Research questions | Housing-context RQ4 included | Three accessibility/comparative RQs; RQ4 withdrawn |
| Residential source work | Required and blocked | Preserved historical feasibility; not a prerequisite |
| Income | Qualified income plus sensitivity | Retained; separate concept/qualification decision for new cities |
| Municipal geography | Stockholm amended; Oslo vintage unresolved | Preserve Stockholm; targeted qualified Oslo recovery remains required |
| Branch | v4 | Existing v4, unchanged |
| Definition | v4_housing_standard_20261011 (audit-reported) | v4_accessibility_only_20261011 |

## Retain

Original v3 sample/estimates/specification; accepted Copenhagen income; all listing snapshots/ingestion receipts; Stockholm source amendment; original Oslo qualification record; acquired housing statistics and unsent requests; applied migrations and published commits.

## Retire from new-design dependencies

H variables/derived ranks, housing availability/licence gates, price-area reference frames, annual transaction thresholds, housing sample-coverage thresholds, H folds/group tests, portal acquisition and provider contacts. Do not erase their previous failures or misleadingly mark them passed.

## Explicit new operational decisions

MEW-ME is reported in addition to the four v3 contrasts. New-city administrative geography/metric CRS and the extension of 500/30 fold feasibility must be frozen before fitting. A common spatial-scale check is retained for cross-city interpretation. No universal equivalence threshold is assumed. Income fallback is not silently activated.

## Old-to-new prompt mapping

Old Steps 1–5 and Stockholm recovery: preserve completed work. Old housing Step 6 and H-specific remainder: superseded. Begin new A01 (scope state), A02 (dependency refactor), then A03–A07 (geography/context/features/freeze/testing), A08–A10 (city execution), A11–A12 (robustness/release).

No actual live repository edits, source retrievals or fits were performed to create this package.
