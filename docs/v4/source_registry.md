# V4 source registry — active Markdown

Definition version: `v4_housing_standard_20261011`. Decision date: 11 October
2026. Newly authored from accessible source evidence. This is a qualification
register and current acquisition evidence, not a replacement for the authoritative
PostgreSQL source registry. V3 results were already observed; supervisor approval
is not recorded and this is not retrospective preregistration.

## Existing evidence and authoritative store

The actual local V3 manifest is `data/metadata/source_manifest.json`: 195
manifest records, including 191 under data/raw. The frozen input configuration
contains 204 raw file identities. These describe different inventories; neither
count is invented as V4 source coverage. Actual registration is implemented in
`src/db/sources.py`, with provenance persisted in PostgreSQL `meta.source_files`
and raw source rows kept immutable. Acquisition sidecars/source selections also
carry provenance. The unlabelled `data/raw/municipalities.zip` remains frozen
but explicitly excluded from analytical registration due to unknown provenance.

Do not copy private source rows into this Markdown or version control. V4
provenance belongs to its separate authoritative database identity. CSV exports
are not a second analytical store. All externally acquired data require source,
acquisition date, geographic extent and checksums where possible. Record native
and metric CRS for spatial data/operations and explicit unknowns.

## V4 qualification register

| Source role | Available evidence | V4 status / required gate |
| --- | --- | --- |
| Airbnb outcome/property/host data | Three detailed 30 June 2026 catalogue entries/files verified; Copenhagen reused at protected hash, Oslo/Stockholm officially downloaded; 90 identical columns | Acquired/ingested audit only; 41,341 source rows per selected freeze, missing-price rows retained; no model sample qualified |
| Housing H | Step 5: Finans Danmark BM011/BM021 2025 quarterly native postal aggregates acquired; Oslo BOL018 2025 annual native apartment statistics acquired; Stockholm SCB annual regional and SökHem rolling municipal alternatives acquired and rejected as target H | Oslo standalone PRELIMINARY_QA_PASSED, PROVISIONAL_BOUNDARY; Copenhagen annual construction/licence/geography BLOCKED; Stockholm target period/measure/area BLOCKED. All final H/model gates BLOCKED; no listing assignment or reference frame frozen |
| Population/density X | V3 City/Statistics Denmark sources, qualified geography and population 2026 Q3 | Retain concept/limitations; qualify per-city reference period, density geography and CRS |
| Income X | V3 Copenhagen KKIND5 and Frederiksberg nominal IFOR35, 2024 ten-decile arithmetic means, documented qualified acceptance | Inherited qualification applies to those sources only; new-city sources require compatible concepts and provenance |
| Boundaries/centrality | Copenhagen 0101 + Frederiksberg 0147 municipal geometry reused; Oslo 0301 current official geometry acquired; Stockholm 0180 operational union derived from 127 SCB RegSO 2025 polygons | Stockholm listing boundary RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT, reference 2025-01-01; original Lantmäteriet 401 retained. Oslo vintage unresolved; new-city general metric CRS/anchor and every housing crosswalk unresolved; provider labels never substituted |
| OSM network/stations/bus/POIs E/W | Frozen V3 extraction/taxonomy and deterministic consolidation; matched endpoint universe | Qualify each city extraction/coverage/snaps/topology; preserve inherited thresholds and category rules |
| Tuning | Actual frozen V3 30-candidate list with seed/hash, copied under a V4 configuration identity | Definition inherited; no V4 fitting or data readiness certified |

Source URLs, timestamps, checksums, native schemas and public queries are now
recorded in the [Step 5 source comparison](housing_source_registry.json),
[housing acquisition audit](housing_acquisition.md) and
`config/v4/housing_sources.json`. Qualified H configuration values, joined
coverage and reference-frame fields remain null: source acquisition is distinct
from qualification. No source value, geographic mapping or transaction count
is invented. Raw values and private source files stay out of Git.
Prefer full-year 2025 apartment sale-price/m2; alternate period/measure needs
an explicit amendment. Preserve native reported values/currency and freeze
one qualified external-area frame per city, independent of Airbnb. Average
tie ranks and equal area weights give `H=(midrank-0.5)/G_ref`; log native price
is the prespecified sensitivity. Missing values cannot be silently filled or
removed to redefine the reference frame.

Every primary model M0/ME/MW/MEW includes H exactly once. No-income sensitivity
still includes H. A city without qualified H is BLOCKED from the primary
ladder. Narrower-city or descriptive-only scope needs an explicit amendment;
there is no automatic no-H fallback. None of the contrasts estimates adding-H
benefit without a separately authorized no-H sensitivity.

The specification step performed no acquisition/migration. Architecture added
023 and disposable tests. The listing step provisions `thesis_accessibility_v4`,
applies unchanged 023 plus new 024 and registers immutable source manifests/raw
audits with version/city/batch/ingestion identity. See
[listing acquisition](listing_acquisition.md) and `listing_acquisition_audit.json`
for exact URLs, timestamps, licences, hashes, safe counts and blockers.
The active Stockholm-only update is
[the 11 October boundary-source amendment](stockholm_boundary_amendment_20261011.md)
and its separate SQL-derived `stockholm_boundary_amendment_20261011_audit.json`.
SCB's official GeoPackage is CC0, native EPSG:3006, version 2025_v2/reference
2025-01-01; actual `kommunkod=0180` is used, never county 01. This municipal mask
does not qualify RegSO as the analysis or housing geography. Official/native
area IDs remain unassigned. Step 5 independently audits native housing sources;
this mask does not supply qualified housing data. The old listing audit/failed receipt and every committed ingestion
remain immutable. No source is silently replaced or retried under its old identity.
V3 remains untouched, no V4 fitted results exist, and no
temporal Airbnb panel, residential-price outcome model or gentrification score
is introduced. See the [specification](preanalysis_specification.md) and
[document index](document_index.md) for authority and interpretation limits.

Step 5 uses append-only migration 025 and dedicated `v4_raw.housing_ingestions`
and `v4_raw.housing_area_period_audit`. The SQL-derived
`housing_acquisition_audit.json` contains safe counts/status/provenance only.
Native price/count cells remain authoritative in PostgreSQL, separate from
future qualified research tables. Neither a bydel/delbydel hierarchy nor RegSO
is silently selected as the housing reference frame. See
[unsent access requests](housing_access_requirements.md) for exact missing
inputs; no application, terms acceptance or purchase was made.
