# Oslo operational municipal-mask amendment — A03, 11 October 2026

Design `v4_accessibility_only_20261011`; geography definition
`v4_geography_A03_20261011`. User-authorized targeted vintage recovery, not
A04/context acquisition or model execution. **Municipal mask:
RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT. Analysis geography: BLOCKED.**

The original current-at-retrieval Kartverket API file, receipt, manifest
`c08f5ebdaf01ba445cc68e2e0c77b9290c246903f67408013556a071b84252f8`,
listing ingestion `research_v4_oslo_20261011T143812Z` and its vintage warning
remain unchanged. This amendment does not reopen or relabel that ingestion.
The listing snapshot is reused read-only, with its original schema/hash verified;
no Airbnb download or duplicate listing ingestion occurred.

## Dated source and certification limits

[Official publisher metadata](https://data.norge.no/nn/datasets/601a115b-c20c-3bc1-a8e9-53f9ea718230/administrative-enheter-kommuner)
records a **2026-01-01** reference and 2026-07-30 catalogue update. The
[official GeoJSON Atom feed](https://nedlasting.geonorge.no/geonorge/ATOM-feeds/AdministrativeEnheterKommuner_AtomFeedGeoJSON.xml)
links the actual [0301 Oslo EPSG:25833 archive](https://nedlasting.geonorge.no/geonorge/Basisdata/Kommuner/GeoJSON/Basisdata_0301_Oslo_25833_Kommuner_GeoJSON.zip).
The exact archive was retrieved **2026-10-11T19:58:09+00:00** (the frozen receipt
is authoritative for retrieval time), SHA256
`b369204c77ca806aacf2986d209da2ae3684e9c5a9586f0a2f567b0d88d25863`.
Licence: **CC BY 4.0, © Kartverket**, under
[the publisher's terms](https://kartverket.no/en/api-and-data/terms-of-use).
No credentials, purchase or interactive terms acceptance was used.

Archive member `Basisdata_0301_Oslo_25833_Kommuner_GeoJSON.geojson` contains
318 features, including one polygon object `objtype=Kommune`,
`kommunenummer=0301`, `kommunenavn=Oslo`. Its recorded polygon update is
**2025-11-11T12:30:34+01:00**, extraction
**2025-12-10T15:42:08+01:00**, version ID 23. The catalogue/feed regeneration,
HTTP retrieval and polygon extraction dates are separate. This is verifiably
source-dated operational geometry, **not certified exact 30 June 2026 linework**.

The source is a valid nonempty MultiPolygon, one connected piece, native
EPSG:25833 gross area **481.0403403288482 km²**, native bounds
`248657.28, 6637442.11, 273925.92, 6674528.68` metres. No repair, clipping,
snapping or fabricated filling was applied. EPSG:25833 is selected for Oslo
metric operations from the official local dataset, not Copenhagen's EPSG:25832.

[SSB's official regional-change register](https://www.ssb.no/metadata/alle-endringer-i-de-regionale-inndelingene)
was frozen and reviewed: the listed 1 January 2026 municipal line changes concern
Indre Østfold/Nordre Follo/Vestby; Oslo entries concern names/a ground-unit spelling,
not an enacted Oslo municipal boundary change. The
[Oslo reform](https://www.oslo.kommune.no/satsingsomrader-og-prosjekter/bydelsreformen/)
changes borough organisation from **2028-01-01**. The web map's future
`Bydeler2026` layer is not the June 2026 administrative scheme. Absence from the
reviewed change register cannot certify absence of every minor correction.

Independent SSB table **09280**, exact region **0301**, reports **426.40 km²
land + 27.72 km² freshwater = 454.12 km²** for both 2025 and 2026. It excludes
sea; it must not be compared as the same denominator as Kartverket's gross
481.04 km² polygon. Kartverket's administrative extent includes coastal sea
([publisher explanation](https://kartverket.no/en/api-and-data/grensedata)).
The separately published city borough layer unions to **481.0366191 km²**;
its small uncovered/excess registration differences are quantified in the
A03 audit. This supports extent/identity, not proof of identical legal linework.

Comparing the preserved API bytes projected to EPSG:25833 with the native dated
polygon gives about **23.22 m² symmetric difference** and **0.513 m Hausdorff
distance**. The frozen audit's SQL GeoJSON transport comparison gives
**24.98239570 m² / 0.51301871 m**; transport uses nine decimal places in
EPSG:4326, with sub-millimetre coordinate rounding, so these are different
explicit comparisons. Equal rounded area is never treated as linework identity.
Independent PostGIS counts compare exact original stored masks as well.
**No listing inclusion changes** were computed. Both source-date/change evidence
and spatial checks support the limited operational amendment authorized here.

## Listing results and remaining borough gate

| Universe | Total | Inside dated mask | Outside | Within 150 m of outer boundary |
| --- | ---: | ---: | ---: | ---: |
| Raw | 13,391 | 13,391 | 0 | 45 |
| Inherited dwelling filter | 11,776 | 11,776 | 0 | 37 |
| Dwelling + original positive price | 8,557 | 8,557 | 0 | 29 |

`covers` uses EPSG:4326; distance/area use EPSG:25833. Exterior rings define
outer-boundary flags; interior holes are excluded. Coordinates stay private.
Zero outside is computed, not substituted for unresolved evidence. These are
acquisition/support counts, not final prediction/association samples.

The official Oslo geography page links the actual public ArcGIS map and code
workbook. The inspected existing `Bydeler` layer contains **18 polygons / 17
statistical units**: 15 boroughs plus Sentrum and Marka. Attribute `kommunenum`
is `0301`; `BYDEL` is `01`–`17`, with unique component `FID`. Two real Marka
components share code `17` and are explicitly dissolved; other duplicate area
components fail. Workbook `Bydel_nr/Bydel_navn` independently validates codes;
99 means no registered address and is not a polygon/analysis area.

The layer data last-edit timestamp is 2023-11-03; service metadata edit is
2025-04-28, not a legal boundary reference date. Source service CRS is
EPSG:3857; the explicit GeoJSON query requests EPSG:25833. Recomputed metric
areas are used, not inflated Web Mercator `Shape__Area` attributes. Native
codes and IDs are separate from provider neighbourhoods and future context IDs.

All inside listings assign uniquely to these provisional polygons. The exact
registered union has **0.00461 m²** numerical overlap, **3,733.71 m²** mask gap
and **12.48 m²** excess; these are reported, not repaired or proclaimed zero.
The publisher item/layer has no stated licence; a public endpoint alone does
not qualify analytical reuse. **Marka has 17 positive eligible listings**, below
the proposed 30-test safeguard; the other 16 units meet the current 500-training/
30-test count check. These safeguards are not power guarantees.

The official service responsibility mapping splits Marka among multiple
adjacent boroughs and assigns Sentrum services to St. Hanshaugen; that is not
itself an acquired spatial crosswalk. No blanket Marka merge, fabricated spatial
split, price-based grouping, dropped area or final fold is frozen. **Oslo analysis
qualification remains BLOCKED** pending clear geometry reuse terms and a verified,
substantively defensible sparse-area/grouping decision. Population/income/public
anchor/context qualification remains A04, not performed here.

## Immutable amendment identity

New geography qualification `research_v4_oslo_20261011T210000Z` in dedicated
PostgreSQL/PostGIS `thesis_accessibility_v4`, design-qualified append-only tables
from migration 027. The run ID is a preallocated job identifier; actual SQL
creation and source retrieval timestamps are recorded separately.
New geography manifest:
`550733b7e7107d042ce4f80c9abb186a0c8858edb9c0b76af7b5d99dde4456de`.
Original listing/model identities are untouched. See
[the A03 audit](geography_qualification_A03_20261011.md), its aggregate JSON and
pinned source/receipt registry for exact URLs, retrievals, hashes and limits.
Housing acquisition is **NOT_REQUIRED_SCOPE_AMENDED**; this resolves no income,
accessibility, sample, fold or modelling gate.
