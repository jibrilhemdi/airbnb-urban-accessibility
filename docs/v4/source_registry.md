# V4 source registry — active Markdown

Definition version: `v4_housing_standard_20261011`. Decision date: 11 October
2026. Newly authored from accessible source evidence. This is a qualification
register, not a claim of V4 acquisition or a replacement for the authoritative
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
| Airbnb outcome/property/host data | Inside Airbnb V3 Copenhagen/Frederiksberg extract dated 30 June 2026; immutable local paths/hashes | Matched June 2026 target retained; roster explicitly authorized; each city's exact snapshot/extent must be qualified |
| Housing H | User-proposed full-year 2025 apartment residential sale-price/m2; no qualified V4 provider/file identified | BLOCKED: source, acquisition date, extent, checksum, unit/currency, statistic, transaction/coverage evidence and official area mapping unresolved |
| Population/density X | V3 City/Statistics Denmark sources, qualified geography and population 2026 Q3 | Retain concept/limitations; qualify per-city reference period, density geography and CRS |
| Income X | V3 Copenhagen KKIND5 and Frederiksberg nominal IFOR35, 2024 ten-decile arithmetic means, documented qualified acceptance | Inherited qualification applies to those sources only; new-city sources require compatible concepts and provenance |
| Boundaries/centrality | V3 official national/municipal geometry, City Hall anchor; source EPSG:4326 and operations EPSG:25832 | Copenhagen local boundary/anchor/CRS evidence versioned in cities.json; Oslo/Stockholm and every housing crosswalk unresolved; never fabricate |
| OSM network/stations/bus/POIs E/W | Frozen V3 extraction/taxonomy and deterministic consolidation; matched endpoint universe | Qualify each city extraction/coverage/snaps/topology; preserve inherited thresholds and category rules |
| Tuning | Actual frozen V3 30-candidate list with seed/hash, copied under a V4 configuration identity | Definition inherited; no V4 fitting or data readiness certified |

No source URL, acquisition date, extent, transaction count or price value is
invented for H. Corresponding unknown fields remain null in configuration.
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

The specification step performed no acquisition or migration. The architecture
step adds immutable V4 manifest registration and migration 023, tested only in
a disposable database. No production V4 sources/results are registered and no
temporal Airbnb panel, residential-price outcome model or gentrification score
is introduced. See the [specification](preanalysis_specification.md) and
[document index](document_index.md) for authority and interpretation limits.
