# Rinkeby-Tensta polygon correspondence — 12 October 2026

Design `v4_accessibility_only_20261011`. Targeted user-requested name/geometry
verification only. **Historical correspondence supported; current borough
crosswalk and analysis qualification remain UNQUALIFIED/BLOCKED.** No A05+, routes,
fits, income assignment, source relabelling or completed-ledger change.

The preserved June 2026 listing labels include **Rinkeby-Tensta**. We acquired
only the matching Inside Airbnb neighbourhood GeoJSON, selected from the frozen
Stockholm catalogue's exact 2026-06-30 data root; no listings were downloaded.
The file contains 14 neighbourhood polygons and exactly one target label.

## Computed polygon comparison

The target is a valid MultiPolygon. Compared with all 12 valid candidates in the
preserved official city archive's 13 historical borough polygons, its strongest
match is **Rinkeby-Kista**, not Spånga-Tensta:

| Diagnostic | Official historical Rinkeby-Kista | Official historical Spånga-Tensta |
| --- | ---: | ---: |
| Target polygon area | 11.949263 km² | 11.949263 km² |
| Official comparison area | 12.008041 km² | 12.861808 km² |
| Intersection area | 11.814190 km² | 0.027987 km² |
| Share of Airbnb target covered | **98.8696%** | **0.2342%** |
| Share of official comparison covered | 98.3857% | 0.2176% |
| Intersection / union | 97.2913% | 0.1129% |
| Symmetric difference | 0.328924 km² | 24.755097 km² |
| Discrete Hausdorff distance | 171.9655 m | 3396.6368 m |

This is strong evidence that the provider's label refers approximately to
**historical Rinkeby-Kista**, despite saying Rinkeby-Tensta. It is an inference
from measured spatial correspondence, not an exact identity certification.
Neither the raw label nor any stored listing assignment has been changed.

The official city documents that Rinkeby-Kista and Spånga-Tensta merged into
Järva on 1 July 2023. That history does not establish that the old/provider
polygon unions equal current Järva linework. [City merger information](https://start.stockholm/om-stockholms-stad/utredningar-statistik-och-fakta/statistik/omradesfakta/).

## Source and CRS limits

- [Inside Airbnb neighbourhood GeoJSON](https://data.insideairbnb.com/sweden/stockholms-l%C3%A4n/stockholm/2026-06-30/visualisations/neighbourhoods.geojson): exact batch2026-06-30, retrieved2026-10-12T14:09:33Z, SHA256 `9be3b672288e508e155f7e830b076ae9640fdf97063dad6cb7117ee116649274`. HTTP Last-Modified is2026-07-03, not a certified original boundary date. Catalogue licence CC BY4.0; original cartographic provenance/vintage remains unverified.
- [Preserved official Stockholm archive](https://dataportalen.stockholm.se/dataportalen/Data/Stadsbyggnadskontoret/SHP_utanfastigheter_nya_granser.zip): SHA256 `7e92c9e664ffe51aec4a2ecfa409bdd4d2fb1421aa474af3f0c80e52f1c3da27`, administrative layer `Adm_area`, archive member2020-12-10. Rinkeby-Kista `ADM_ID=1` and Spånga-Tensta `ADM_ID=3` are valid but `RAMKLIPP=yes`. The archive remains rejected for current analysis qualification; its reuse terms are not newly qualified.
- Airbnb GeoJSON has no explicit CRS member: this inspection records the longitude/latitude WGS84 default **OGC:CRS84** under [RFC7946 section4](https://www.rfc-editor.org/rfc/rfc7946#section-4), with plausible Stockholm coordinate bounds. Official `.prj` declares **EPSG:3011**. Both are transformed to **EPSG:3006**, Stockholm's metric CRS, for all area/distance operations.
- No repairs, snapping or buffering were used. Hausdorff values use GEOS/Shapely's discrete algorithm, not a certified continuous maximum boundary error. Invalid historical Skarpnäck was skipped and reported, never repaired. Clipping, unknown original Airbnb vintage and boundary generalisation remain possible contributors to differences; their specific contributions were not established.

## Reproduction and preservation

```sh
.venv/bin/python scripts/v4_rinkeby_polygon_check.py --verify
```

The command verifies raw/receipt/catalogue/manifest SHA pins and recomputes the
[safe diagnostic export](rinkeby_polygon_check_20261012.json). It uses temporary
extraction of only the administrative layer, performs no network/SQL access,
and reads no listing IDs, coordinates or outcomes. Raw files remain ignored.
The new discovery-only identity `research_v4_stockholm_20261012T140933Z` and
manifest `b1a8d35f0359004f1cd339d30dab6ac699c386511e1c69eba23b6bde4a27b1c3`
are independent of all committed ingestion/qualification/model identities.
No SQL rows or scientific source-selection policies are changed. PostGIS remains
authoritative for existing analytical records; this export is an inspection,
not a replacement analytical store or an approved crosswalk.

This narrows the naming issue but **does not resolve Stockholm's current borough
geometry, RegSO-to-borough income mapping, civic-anchor or income-comparability
gates**. Read [the A03 audit](geography_qualification_A03_20261011.md) and
[A04 context audit](context_qualification_A04_20261011.md) for unchanged statuses.
