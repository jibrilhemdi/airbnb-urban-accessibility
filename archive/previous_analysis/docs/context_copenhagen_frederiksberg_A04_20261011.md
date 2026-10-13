# A04 Copenhagen–Frederiksberg context status — 11 October 2026

Design `v4_accessibility_only_20261011`. Final context status **QUALIFIED_INHERITED_WITH_CAVEATS**.

- Acquisition: `REUSED_APPROVED_V3`.
- Source validation: `QUALIFIED_INHERITED_WITH_CAVEATS`.
- Spatial join: `JOINED_INHERITED_OPERATIONAL_WITH_UNMATCHED_RETAINED`.
- Native persisted context cells: 33.
- Metric CRS: `EPSG:25832`.
- Source run: `research_v4_copenhagen_frederiksberg_20261011T210800Z`.
- Source manifest SHA256: `187f3de5cb9cf4526128c5441954d48bca99fb06044094098fb468b53ef9f91d`.

Context source QA:

```json
{
  "joined_rows": 23066,
  "listing_rows": 23144,
  "income_period": "2024",
  "population_period": "2026Q3 (2026-07-01; one day after batch)",
  "density_definition": "log(population/gross native assignment polygon km2); water inclusion and statistical boundary vintage unverified; no rescaling",
  "qualified_area_count": 11,
  "income_records_sha256": "53d6522c6db041d3cfaafebe44b313980ebab7c7381f0529d41d342316d1637d",
  "income_decision_sha256": "355ab55de7e9cdf00995979806ae818093b599ff417ee805b2ea3fb12c5cc9e9",
  "unmatched_or_outside_rows": 78,
  "district_population_sha256": "953f29d57f9d62fecc747a68830f97cc6acb54ff8e364c0b180c48503bb26009",
  "municipality_population_sha256": "62af775af77d0cdfd82a50f497c3ffd8c1ec18e57ca7c7821b2a51c815b5caa8"
}
```

Outstanding requirements:

Inherited geographic/income caveats remain; three-city income decision and later scientific stages still block empirical work.

No A05+, final samples/folds, routes or fitting. No primary income-mode change.
See [the full A04 audit](context_qualification_A04_20261011.md) and
[source registry](context_source_registry_A04_20261011.json) for exact periods,
units, concepts, limitations and receipts. Public civic coordinates only; listing
coordinates and listing-level contexts stay ignored/private.
