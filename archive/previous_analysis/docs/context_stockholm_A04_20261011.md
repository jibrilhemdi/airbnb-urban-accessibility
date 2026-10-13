# A04 Stockholm context status — 11 October 2026

Design `v4_accessibility_only_20261011`. Final context status **BLOCKED**.

- Acquisition: `ACQUIRED_NATIVE_STATISTICS`.
- Source validation: `VALIDATED_NATIVE_SOURCE_ONLY`.
- Spatial join: `NOT_JOINED_BLOCKED_GEOGRAPHY`.
- Native persisted context cells: 508.
- Metric CRS: `EPSG:3006`.
- Source run: `research_v4_stockholm_20261011T210800Z`.
- Source manifest SHA256: `5881346fef1e9bdd2349dc37b428b1179f0620bd5490176e8c96a81d48e86c6d`.

Context source QA:

```json
{
  "income": {
    "native_cells": 381,
    "missing_cells": 0,
    "source_updated": "2026-01-20T07:00:00Z",
    "distinct_observed_values": 371
  },
  "population": {
    "native_cells": 127,
    "missing_cells": 0,
    "source_updated": "2026-03-24T07:00:00Z",
    "distinct_observed_values": 127
  },
  "native_id_mask_match": {
    "count": 127,
    "status": "EXACT_NATIVE_ID_MATCH_ONLY_NOT_ANALYSIS_APPROVAL"
  }
}
```

Outstanding requirements:

- Current official 11-borough polygons with stable IDs, licence and valid full-city coverage remain unavailable: official metadata redirects to sign-in; public city archive is old, clipped and contains invalid geometry
- Area-dependent density/context assignment NOT_JOINED; qualified matching analysis geometry required
- Three-city income concept/scaling not qualified; frozen pre-fit researcher income decision required
- Public civic building/address verified as Stadshuset, Hantverkargatan 1; official city/tourism pages do not expose a verifiable point coordinate. Require a public source coordinate with explicit CRS/provenance; no guessed geocode.

A later official Stockholm Konst interior-artwork marker at Stadshuset is
recorded as separate discovery-only evidence, not an accepted civic point:
coordinate datum/CRS and reference-point suitability remain unqualified. Its
manifest/receipts are in the source registry. The original NULL-anchor SQL
checkpoint and source policy remain immutable.

No A05+, final samples/folds, routes or fitting. No primary income-mode change.
See [the full A04 audit](context_qualification_A04_20261011.md) and
[source registry](context_source_registry_A04_20261011.json) for exact periods,
units, concepts, limitations and receipts. Public civic coordinates only; listing
coordinates and listing-level contexts stay ignored/private.
