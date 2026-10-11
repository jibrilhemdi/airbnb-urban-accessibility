# Active V4 source/dependency registry — accessibility-only

Design ID: `v4_accessibility_only_20261011`, 11 October 2026. PostgreSQL/PostGIS
remains authoritative. V3 results and housing feasibility were already known;
supervisor approval is not recorded. Source acquisition and scientific adoption
are distinct from final sample/model qualification.

| Role | Verified existing evidence | Active requirement/status |
| --- | --- | --- |
| Listings/Y/host/dwelling | Three frozen 30 June 2026 detailed snapshots, 90 columns, separate DKK/NOK/SEK; missing-price audits retained | Reuse approved manifest scopes by hash; common final samples pending A06 |
| Copenhagen/Frederiksberg mask | Both municipalities 0101/0147, preserved official source vintages | Retain covers policy; V4 analysis/context/feature qualification remains |
| Oslo mask | Preserved original API plus separately dated Kartverket 0301 archive, reference 2026-01-01/extraction 2025-12-10 | A03 RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT operational mask; exact June linework not certified |
| Stockholm mask | SCB RegSO 2025_v2 union, municipality 0180, 127 components, reference 2025-01-01 | RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT; operational 2025 mask only, not analysis clusters |
| Official analysis areas | A03 Copenhagen 11 inherited operational areas; Oslo 17 native statistical units/18 polygons provisional; Stockholm current 11-borough target lacks qualified polygons | Copenhagen assignment qualified with geometry exceptions; Oslo licence/Marka support and Stockholm full-current polygons BLOCKED; no final A06 folds |
| Population/density | Copenhagen 2026Q3/gross-area context inherited | Required A04; independent new-city sources/geography/denominators pending |
| Income | Accepted KKIND5/nominal IFOR35 2024 construction and no-income robustness | Retain qualification/limitations; new-city income and frozen comparative mode required A04 |
| Centrality/metric CRS | Copenhagen public City Hall/EPSG:25832 inherited; Stockholm EPSG:3006 qualified for boundary QA | A03 metric CRS: Oslo EPSG:25833, Stockholm EPSG:3006; public anchors/context remain A04; no default projection/mapping |
| Network/destinations | Frozen v3 taxonomy, consolidation, connectors and source caches | Matching city sources/extraction/coverage/reuse QA pending A05; no routes built in A01/A02 |
| Samples/folds/candidates | Exact v3 30-candidate list available; inherited protocol | New-city common samples/folds and selected references pending A06/A07 |
| Housing/property-price/rent sources | All Step 5 receipts, SQL records, failed/preliminary audits preserved | NOT_REQUIRED_SCOPE_AMENDED; historically BLOCKED final qualification remains unchanged |
| Housing access requests | Existing precise drafts/manual-import requirements | NOT_REQUIRED_SCOPE_AMENDED; remain unsent, not to be pursued |

Selected scope IDs/manifests and live counts are in
[current_state_audit_20261011.md](current_state_audit_20261011.md). The original
[listing acquisition](listing_acquisition.md), its aggregate JSON and the
[Stockholm amendment](stockholm_boundary_amendment_20261011.md)/separate aggregate
JSON remain unchanged. Their old housing references are historical scope facts,
not current instructions. Never redownload/reingest those files because design
identity changes; do not sum superseded ingestions as new listings.

[Housing acquisition](housing_acquisition.md), [access drafts](housing_access_requirements.md),
`housing_source_registry.json`, `housing_acquisition_audit.json`, pinned housing
policy and migration 025 remain historical feasibility evidence. Native source
values, licensing restrictions and failures are preserved; source permissions
still govern retained files. No price-source crosswalk, transaction-count gate,
80% housing-coverage gate, H-area fold, rank or subgroup becomes a dependency of
this new design. Income/population/analysis-area crosswalks are still required.

All sources need source URL, retrieval/reference dates, extent, licence and
checksum; spatial sources/operations need explicit CRS. Keep raw/private content
ignored. New unknowns remain unresolved. The supplied literature matrix and some
external draft files are not present in the live repository; their imported
provenance is not claimed newly verified. See the [document index](document_index.md)
and [active model contract](model_contract.md) for current authority and A02 limits.

A02 integrates the exact listing-manifest selections through read-only reuse.
See [the A02 pipeline audit](pipeline_scope_audit_A02_20261011.md) for applied
migration 026, checks and genuine non-housing preflight blocks. No source
qualification, new acquisition, housing-source status or original receipt changes
as a consequence of the design identity switch.


## A03 geography checkpoint

[Geography audit](geography_qualification_A03_20261011.md),
[aggregate JSON](geography_qualification_A03_20261011.json),
[exact source registry](geography_source_registry_A03_20261011.json) and
[Oslo operational amendment](oslo_boundary_amendment_A03_20261011.md) record actual
source/reference/retrieval dates, licences/unknowns, schemas, IDs, CRS, topology,
coverage, counts and blockers. Old listing/Stockholm/housing audits remain unchanged.
Only geography sources were acquired; no listing downloads, provider contact,
income, routes, networks or models. The public Stockholm archive is rejected:
old 13-area scheme, all clipped, one invalid polygon. RegSO is still only the mask.
New append-only SQL migration 027 and hash-pinned A03 reuse selectors preserve all
old completed ledgers. Official analysis IDs, provider labels and future context
IDs stay distinct. A04 and later work remain unexecuted; affected city-dependent
analysis/context/fold tasks cannot bypass the stated source/support blockers.
