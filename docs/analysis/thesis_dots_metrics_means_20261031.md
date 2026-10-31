# Validation dots, metric equations and descriptive means — 31 October 2026

The researcher's current feedback explicitly asks for Figure 5.2 to use
“actual dots to represent listings”. This supersedes their earlier choice of
500 m aggregated dots for this illustration. The exception applies to the
Copenhagen validation illustration and its already-requested Oslo/Stockholm
companions. The older implementation contract, prior instruction and old
images remain preserved as historical evidence. No frozen design selector or
scientific package is amended.

## Validation illustrations

`scripts/build_thesis_explanatory_figures.py` reads the verified frozen common
predictive samples and saved outer memberships from PostGIS in READ ONLY
transactions. Each illustrated split plots one three-square-point dot per
listing at its existing metric coordinates: blue training, orange test.
No jitter, sampling, cell snapping or display suppression is applied to these
three illustrations. Coincident locations can overlap. The generator checks
that every listing is in the map bounds and has exactly one plotted dot per
panel. Counts come from current memberships, not the archived 12,412-listing
Copenhagen analysis.

These are approximate Inside Airbnb locations, not independently verified
property addresses. No listing identifiers, coordinate tables or membership
rows are exported. The publication is a raster illustration only. The main
manuscript's data-governance paragraph, figure captions, writing guide and
figure manifest describe this exception. The three block figures retain their
existing cell suppression below five listings; other location-summary rules
are unchanged. No new claim of anonymity, consent or legal approval is made.

Source spatial CRS remains EPSG:4326. The plotted sample coordinates are the
frozen EPSG:25832 (Copenhagen), EPSG:25833 (Oslo) and EPSG:3006 (Stockholm)
coordinates, displayed in kilometres. Bounds, provider geometries, held-out
areas, fold choices, north arrows and scale bars are unchanged. The named
held-out examples remain Nørrebro, Grünerløkka and Södermalm. Archive colours,
layout and the held-out-area callout are retained.

## Metric definitions

Section 5.4 now defines MAE and predictive R² alongside RMSE, using the same
observed and saved predicted log prices. Definitions agree with
`src/study/modeling.py::metrics`: the R² denominator uses variation around the
evaluated sample's observed mean. The prose explains direction, negative R²,
the constant-outcome limitation, log-price units and pooled held-out scoring.
The evaluation mean is a scoring reference and is not passed into fitting.
No metric values, fitted models or saved predictions are recalculated or
replaced by this prose edit. These standard equations need no new reference.

## Means in Table 6.1

The original pinned `accessibility_descriptive_statistics.csv` lacks means.
It is unchanged. `scripts/thesis_accessibility_summary.py` instead reads the
same three frozen common predictive samples from authoritative PostGIS,
checking the selected summary and complete record hashes and all 751 frozen
scientific checkpoint identities. Every measure must be finite and nonnegative;
opportunity counts must be integers. Missing values stop the calculation.

For each of the 24 city/concept/representation cells, all seven originally
published quantiles/extrema and N must reproduce before the arithmetic mean is
added. Rail and bus walking minutes are multiplied by 5/60 to obtain kilometres,
as in the original display. Food/social and culture/tourism means average the
original saved `*_e_10` / `*_w_10` counts, not logarithms or inverted rounded
logarithms. No new accessibility measure, route or model feature is computed.

Table 6.1 has paired median/mean columns under each representation. Existing
median formatting stays unchanged; mean distances use three decimals and mean
counts one decimal. `tables/manifest.json` records full-precision descriptive
aggregates, sample/code identities and original export checksums. It is a
reproducible manuscript view, not an alternative undocumented analytical store.
The other five result tables and all completed scientific exports are unchanged.

Pre-edit manuscript, bibliography, PDF, affected figures/scripts and manifests
are preserved with checksums in `archive/thesis_dots_metrics_means_20261031/`.
All prose changes are in `main.tex`; references remain in `references.bib` and
the only canonical compiled manuscript is `thesis_report/main.pdf`. No separate
chapter draft or bibliography is introduced. Validation is recorded in the
execution log.
