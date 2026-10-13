# Stockholm boundary-source amendment — 11 October 2026

Definition: `v4_stockholm_regso_boundary_20261011`. User-authorized targeted
Step 4 recovery only. Stockholm listing-boundary acquisition is
**RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT**. Housing-price qualification,
official analysis/housing-area assignments and modelling remain **BLOCKED**.
No models, features, housing assignments or later steps were executed.

## Original blocker and immutable evidence

The original Lantmäteriet municipal-items authentication probe returned HTTP
401 on 11 October 2026 at 14:17:18 UTC. No municipality polygon was acquired.
Its frozen receipt remains at
`data/raw/v4/research_design_v4/stockholm/2026-06-30/official_boundary/boundary.json.receipt.json`,
SHA256 `4b2f5684acd99a26626b3dd1d3a97b299b7c3e8f9c50f0dcf430784e45d0c041`.
The corresponding boundary file still does not exist. The original committed
ingestion `research_v4_stockholm_20261011T143812Z`, its earlier audit identities,
source manifest `d1722807bff5391a1064b995af36713d03c99586a6194c94f141fde5fd9397b6`
and NULL municipal counts remain unchanged. The historical public evidence is
preserved in `listing_acquisition_audit.json`; this dated amendment supersedes
only its Stockholm boundary interpretation, never its frozen records.

The preserved detailed June listing file has SHA256
`6d0ff60954da6e05b73ed741fe7ebbff5b57fe3b18acf4696acf5b824e4e6d6f`.
It was read locally, without downloading Airbnb again. Batch date remains
2026-06-30; actual scrape dates remain June 30 and July 3. No county URL,
provider neighbourhood or previous sample count determines municipal membership.

## Official source, licence and actual schema

The [official SCB RegSO open-geodata page](https://www.scb.se/en/services/open-data-api/open-geodata/open-data-for-regso--regional-statistical-areas/)
states that RegSO follows municipal/county boundaries dated **2025-01-01**.
This is RegSO 2025, not SCB's separate simplified thematic municipal dataset.
The page's GeoPackage link uses the documented WFS service:

`https://geodata.scb.se/geoserver/stat/wfs?service=WFS&REQUEST=GetFeature&version=1.1.0&TYPENAMES=stat:RegSO_2025&outputFormat=geopackage`

The frozen request has equivalent decoded query parameters; the adapter verifies
that equivalence against the actual official page link. GetCapabilities advertises
`stat:RegSO_2025`; DescribeFeatureType confirms the attributes. Actual GeoPackage
metadata declares layer `RegSO_2025`, geometry column `sp_geometry`, POLYGON,
**EPSG:3006 (SWEREF99 TM, metres)**. Actual attributes are `objectid`,
`objektidentitet`, `objekttyp`, `regsokod`, `regsonamn`, `lanskod`, `kommunkod`,
`version`, `ansvarig_organisation`, `referensdatum`. The acquired layer contains
3,363 features across 290 municipal codes. Stockholm records report version
`2025_v2` and `referensdatum=20250101`.

SCB's [open-data terms](https://www.scb.se/en/services/open-data-api/) specify
**CC0**. The official page, licence, capabilities, schema, national GeoPackage,
municipal metadata and three change notices have separate immutable receipts.
The GeoPackage was retrieved **2026-10-11T15:03:48+00:00**, 33,775,616 bytes,
SHA256 `df9bb507bb360020885b47620a5e7bba6c633322236ddaf32ff2a20935c58a5a`.
Its ignored local path is
`data/raw/v4/research_design_v4/stockholm/2026-06-30/scb_regso_2025_20261011_geopackage/regso_2025.gpkg`.
The initial acquisition receipt's pending CRS is preserved; the new manifest
records the schema-qualified EPSG:3006 and selected municipality. All source
URLs, retrieval dates, reference periods, licences, locations and checksums
are in `stockholm_boundary_amendment_20261011_audit.json` and the pinned policy
`config/v4/stockholm_boundary_amendment.json`. Neither contains listing rows.

## Selection and spatial qualification

Select exactly `kommunkod == '0180'`; county `lanskod == '01'` is a consistency
check, never the selection predicate. The frozen official national code register
maps **0180 to Stockholm**. Independently, the official municipal area table
identifies `0180 Stockholm`, distinct from `01 Stockholms län` and statistical
subareas. All 127 selected `regsokod` values are individually recorded in the
policy and public QA evidence: the observed frame is `0180R001`–`0180R127`.

All selected geometries are nonempty, valid polygons with unique IDs. Dissolving
them in EPSG:3006 produces one valid, nonempty Polygon, with **one connected
component, zero holes and zero measurable overlap**. Every selected polygon is
covered by the union; its intersection area with neighbouring municipal features
is zero. No repair, snapping, buffering, simplified geometry or fabricated gap
filling was applied. The sum and dissolved area agree within numerical precision.
Area/CRS/topology qualification was fixed before inspecting listing inclusion.

- Dissolved area: **215.75729922473672 km²**, including water.
- Native bounds (xmin, ymin, xmax, ymax), metres:
  **656773.4550000001, 6569491.489000004, 682485.6301999995, 6592667.161700003**.
- Transformed EPSG:4326 bounds (west, south, east, north):
  **17.76069141783934, 59.22725239359198, 18.200078043280886, 59.440283928718145**.
- Bounds are finite and within geographic coordinate limits; transformed
  topology is valid. Independent exact 2026 boundary linework/bounds were not
  acquired, so these are operational bounds, not certified municipal extremes.

The independent [official municipal land/water-area table](https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__MI__MI0802/Areal2025/)
uses Lantmäteriet-derived input and orthogonal SWEREF99 TM area calculation.
For both 2025-01-01 and 2026-01-01 it reports total **21,575.73 hectares**
(215.7573 km²), and land-only 18,822.34 hectares. The total includes inland and
sea water; comparing the union with land-only area would be incorrect.
The union differs from each official total by **−0.77526328 m²**, within the
**50 m²** half-unit rounding interval of 0.01 hectares. The national bulk CSV
uses Windows-1252 and decimal points; exact region, units and year keys are
validated rather than inferred from ambiguous labels.

## Vintage investigation and interpretation limit

Reviewed official SCB municipal-change section A in these frozen notices:

- [2025 first half, revised](https://www.scb.se/contentassets/e6949501a9bd4f6196316fa5e67fadbf/grpl25_kv1_2_rev.pdf),
  revised 26 November 2025, default implementation 2026-01-01.
- [2025 second half](https://www.scb.se/contentassets/e6949501a9bd4f6196316fa5e67fadbf/grpl25_kv3_4.pdf),
  19 December 2025, default implementation 2026-01-01.
- [2026 first half](https://www.scb.se/contentassets/e6949501a9bd4f6196316fa5e67fadbf/grpl26_kv1_2.pdf),
  16 June 2026, default implementation 2027-01-01 unless specified otherwise.

Their municipal-change sections contain no entries. The revised 2025 notice
does list a Stockholm church-parish merger (Hedvig Eleonora/Oscars); that is
not a municipal boundary change. Equal official 2025/2026 municipal totals and
these notices support operational use, but do not prove absence of subprecision
linework corrections or changes outside the notices' reporting coverage.
This amendment explicitly accepts **SCB-derived 2025 operational geometry**
for the June 2026 listing audit. It is **not an exact certified Lantmäteriet
2026 boundary**. Authenticated Lantmäteriet import remains the option for a
separately authorized exact-vintage comparison; it would require another
immutable amendment, not replacement of this freeze.

## Deterministic listing results and uncertainty

Membership remains the established union **covers** listing point in EPSG:4326,
including points on the boundary. Python results were independently reproduced
against stored geometry in PostGIS. Listing coordinates remain private.

| Audit universe | Total | Inside union | Outside union | Within 150 m of outer boundary |
| --- | ---: | ---: | ---: | ---: |
| Raw detailed records | 4,806 | 4,806 | 0 | 96 |
| Inherited dwelling filter | 3,834 | 3,834 | 0 | 69 |
| Dwelling + positive observed price | 2,510 | 2,510 | 0 | 49 |

Invalid records, duplicate records and unclassified coordinates each count
**zero**, as computed. Missing-price eligible records remain in the audit:
**1,324**, with zero eligible nonpositive prices. Zero outside is an observed
geometric result; the old unresolved counts remain NULL in the original ledger.
These counts are not housing-qualified prediction or OLS samples.

The 150 m diagnostic measures distance in EPSG:3006 to the dissolved polygon's
exterior ring, inclusive on either side. Internal RegSO edges are removed by
the dissolve. PostGIS transformation/distance checks reproduce the diagnostic.
All 96 near-boundary raw records are on the operational inside side. No listing
is removed, moved or assigned a true address by this diagnostic. Source coordinates
are anonymised; location and boundary-vintage uncertainty remain explicit.

## New persistence identity and later assignments

New immutable ingestion: **`research_v4_stockholm_20261011T151637Z`**.
New source manifest: `d1d923db415dbf2218560947e3fd862657e343317f36fee284fa36e36cc0d172`;
manifest-file SHA256 `ba24796f7f5e816d6d1736dc6df3d378ffae4622b4d2837a95f619f05e7fae14`.
It combines verified existing listing/catalogue/code evidence with 12 new SCB
sources. The original 401 receipt is linked separately by its hash and failed
attempt status; it is never relabelled as successful. PostgreSQL/PostGIS remains
authoritative: existing insert-only migration 024 stores the new union and all
raw/audit rows atomically. No migration change or new modelling run was needed.
The SQL-derived ignored GeoJSON export is an inspection/configuration artifact,
SHA256 `61723f07fc6f8e730d1c8f578e5e1f779a2f450ea09cabbdf5523421305a01fa`.

RegSO IDs identify components used to derive this **municipal mask** only.
`official_analysis_area_id` and `native_housing_area_id` remain NULL for every
audit row. Stockholm districts/basområden, other analysis geographies and future
native property-price areas require their own source/vintage/coverage checks
and explicit spatial crosswalks. Do not use the 127 RegSO count as an inferential
cluster count, H reference-frame size or automatic housing mapping. RegSO would
be an analysis/housing geography only if those actual sources use it and their
separate qualification succeeds. No residential-price source was acquired here.
EPSG:3006 is qualified for this source's QA/distance operations; unrelated city
projection/anchor/context decisions remain separately gated.

Stockholm's listing-boundary prerequisite is cleared for a **separately requested
Step 5**. This request does not execute or authorize that step. Housing acquisition
and qualification, common samples/folds and modelling remain BLOCKED; Oslo's
separate boundary-vintage blocker is unchanged. V3 results were already observed;
no supervisor approval or retrospective preregistration is claimed.

## Supported recovery commands

The new adapter reuses `acquire`, `freeze_sources`, `audit_listings`, dedicated
V4 database verification, `persist_ingestion` and the existing safe export.
It reads the named parent ledger and checks its summary/manifest and every raw
checksum. It acquires only the explicitly pinned SCB sources; it never invokes
the Airbnb acquisition adapter. Repeated committed ingestion IDs and existing
exports fail closed. Resolve changed source bytes with a new amendment.

```sh
make v4-stockholm-boundary VERSION=research_design_v4 CITY=stockholm \
  SNAPSHOT=2026-06-30 RUN_ID=research_v4_stockholm_<new_UTC_timestamp> \
  PREVIOUS_RUN_ID=research_v4_stockholm_20261011T143812Z
make v4-listing-audit VERSION=research_design_v4 CITY=stockholm \
  SNAPSHOT=2026-06-30 RUN_ID=research_v4_stockholm_<that_new_UTC_timestamp>
```

An inspection-only variant is `python -m src.v4.stockholm_boundary audit`
with the same five explicit arguments; it reads SQL without mutation and writes
an ignored immutable inspection audit. The recorded ingestion/export commands
were exercised, not merely added to documentation. Synthetic tests use temporary
filesystem roots and an owned disposable PostGIS database, never research namespaces.
