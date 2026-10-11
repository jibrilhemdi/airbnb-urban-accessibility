# V4 Step 5 — housing source acquisition and qualification

Audit date: 11 October 2026, Europe/Copenhagen. Source-adapter definition:
`v4_housing_sources_20261011`; scientific model definition remains
`v4_housing_standard_20261011`. **Safe implementation checkpoint with partial
data acquisition; final housing qualification is BLOCKED for every city.**
V3 results were already observed. No supervisor approval or retrospective
preregistration is claimed. This step does not execute Step 6 or later work.

## Scope and source selection

Investigated official statistical/municipal sources first, then publicly
downloadable historical aggregates and explicitly licensed alternatives, then
research-access options. No source was chosen using Airbnb model performance.
The [candidate registry](housing_source_registry.json) records 15 investigated
candidates, their access distinctions, source periods, constructs, geography,
rights, timestamps, file hashes and rejection/access reasons. It documents a
bounded discovery effort, not proof that no other suitable public source exists.

Preferred construct: completed residential apartment sale-price/m² for calendar
2025, before the June 2026 Airbnb batch. Keep native DKK/NOK/SEK and source
statistics. Neither rolling medians nor municipal totals are substitutes for
the required annual neighbourhood measure. Annual means require exact matching
denominators; medians cannot be combined by averaging. All four primary models
remain `M0=X+H`, `ME=X+H+E`, `MW=X+H+W`, `MEW=X+H+E+W`, with H exactly once.
Missing H blocks the ladder; no housing-free substitute or H-suffixed label.
Y remains log observed Airbnb nightly asking price, with separate city models.

## Acquired source data and immutable evidence

The separately pinned [source policy](../../config/v4/housing_sources.json)
records actual URLs, public queries, native selection, receipt/file SHA256 and
source identities. Source bytes and receipts are ignored under
`data/raw/v4/research_design_v4/<city>/2026-06-30/housing_discovery_20261011_*/`.
The path's snapshot identifies the V4 listing design, not the housing period.
All source periods are recorded separately. There are **40 acquired source
files and 43 receipts**, including three frozen failed requests. This includes
metadata/methodology/access evidence; it is not 40 housing datasets.

Six statistical extracts were downloaded: BM011/BM021 quarterly CSVs, Oslo
BOL018 annual JSON-stat2, SSB 14545 annual Oslo JSON-stat2, SCB TAB1151 historical
bulk CSV ZIP and SökHem's current sold JSON. Oslo's official geographic hierarchy
XLSX and the two Danish municipal housing reports were also acquired. Public
aggregate SQL evidence is in [housing_acquisition_audit.json](housing_acquisition_audit.json).
It contains the final new run IDs, source timestamps, hashes, safe counts and
separate statuses. It contains no native price rows or listing coordinates.

Initial acquisition receipts retain their provisional licence labels. New
manifests can record subsequently verified NLOD/CC0/CC BY grants and the hashed
licence evidence without rewriting those original receipts. Immutable source
changes or changed queries require a new source campaign/policy; completed
ingestions never reopen. Temporary URLs in the Danish export receipts are
observed public export URLs, not durable APIs. The frozen exports remain locally
reproducible; a later fresh retrieval needs a new source identity/query receipt
and verification if those temporary URLs expire or provider data change.

## Copenhagen–Frederiksberg

Best candidate: Finans Danmark/e-nettet's
[BM011](https://rkr.statistikbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=BM011)
and [BM021](https://rkr.statistikbank.dk/statbank5a/SelectVarVal/Define.asp?MainTable=BM021).
The actual native selector supplies `EJKAT20=2` (Ejerlejlighed), completed-price
selection `REAL`, sales selection `SALG` and 2025K1–2025K4. Their interface exposes
anonymous CSV export; the observed option is semicolon format 6. Queries stayed
below the published anonymous 20,000-cell limit. The unrelated DST API returned
HTTP 400 for BM011; the native public export succeeded without authentication.

The CSV has **no header**, CP1252 encoding and seven fields: measure, category,
native postal label, then the four quarters. The frozen query HTML independently
verifies that quarter order. Native labels are resolved to actual selector IDs;
no guessed postcode parsing/mapping. BM011 and BM021 native frames match.
The national extraction has **605 postal groups × four quarters = 2,420 area-period
records**, retaining reported counts and original prices. Named Copenhagen and
Frederiksberg groups are present, including source IDs 1800 and 2000 for
Frederiksberg. This does not establish exact municipal spatial coverage.

Actual national price cells: **464 positive, 529 unavailable (`..`), 1,427 reported
zero**. All zero-price cells have zero reported sales. Zero values are retained
as reported, flagged nonpositive and never treated as qualified housing prices.
Counts remain observed; missing prices are not converted to zero. **95 national
groups** have four positive quarters; this is neither a city housing-frame count
nor a joined Airbnb coverage result. The SQL audit records the denominator
diagnostic as well as these counts: **17 missing price cells have at least five
reported sales**. Missingness cannot be explained solely by the provider's
minimum-five-sales rule, and sale counts cannot be presumed to equal the
published price statistic's filtered denominator.

The [official methodology](https://finansdanmark.dk/tal-og-data/boligstatistik/boligmarkedsstatistikken/datagrundlaget-for-statistikken/)
describes trade-level price ratios, arithmetic postal/municipal means, price
filters and delayed-registration corrections. Apartment area uses BBR apartment
area at 100%; broader property types use weighted floor area. Published price
filters/corrections and the separately reported sale counts do not establish
that BM021 counts are the exact denominators of BM011's published means.
**No annual mean was constructed.** Request the provider's annual statistic or
exact same-sample quarterly numerator/denominator evidence before aggregation.

Access is publicly downloadable; an explicit reusable-data licence/academic
permission was not located. DST's free-attribution policy does not automatically
apply to independent Finans Danmark statistics. Frozen anonymous DST documentation
responses were HTTP 200 **temporary service-outage notices**, not the requested
metadata/policy. These were not reclassified as successful source qualification.

The Copenhagen housing report has apartment-price figures through 2025Q2;
Frederiksberg's 2025 publication uses earlier 2024 price data, including first-three-
quarter averages. Neither supplies the target full-year neighbourhood dataset.
They were inspected as official alternatives, not reverse-engineered into H.
Restricted/custom DST property-sales access remains an unrequested option.

Both documented DAWA postcode queries for municipalities **0101** and **0147**
returned **HTTP 410**. Their failed receipts remain frozen. Obtain a verified
replacement official postal geography/crosswalk and vintage; source postal groups,
municipalities, Airbnb labels and official statistical districts are distinct.
The study continues to include both Copenhagen and Frederiksberg.

Status: metadata and quarterly DATA_ACQUIRED; standalone annual H QA **BLOCKED**
on annual denominators, reuse permission and native geography. Final source frame,
Step 6 assignment and Step 8 coverage/group support remain pending.

## Oslo

Best substantive/temporal candidate:
[BOL018](https://statistikkbanken.oslo.kommune.no/statbank/pxweb/no/db1/db1__Boliger%20og%20byggevirksomhet__Boligpriser/ok-bol018.px/).
Actual API metadata supplies codes and value labels; the request selects year
value **7 → 2025**, category **1 → Blokkleilighet**, all native geographic
positions and three measurements. API position is not a native area ID.
JSON-stat2 dimensions are `ContentsCode`, `år`, `geografi`, `boligtype`,
`statistikkvariabel`; the acquired shape is **1 × 1 × 452 × 1 × 3**.
Source update: **2026-05-04T06:00:00Z**. Query/schema and source checksums are frozen.

BOL018 replaced BOL012 in April 2026. It applies BRA/BRA-i to the whole series;
the old P-rom series is not combined with it. The source measures contract price
per interior m² for sold apartments in blocks of at least two storeys; cooperative
common debt is included. Its annual sale counts concern free, complete, single-unit
transactions with sufficient area/price information. This source-reported mean
is retained; it is not converted to a ratio-of-total-prices/total-area statistic.

The [official hierarchy](https://www.oslo.kommune.no/statistikk/geografiske-inndelinger/)
XLSX supplies the actual native code/name mappings: 17 bydeler, 98 delbydeler
(2017 classification), 336 grunnkretsområder represented in BOL018. The remaining
native code **100000** is unresolved and is not guessed to be a municipal total.
The three known levels are nested alternatives, **never added together to form
a housing reference frame or summed for city transaction totals**.

| Native level | Reported areas | Missing price | Areas with positive price and ≥20 annual sales | Distinct supported prices |
| --- | ---: | ---: | ---: | ---: |
| Bydel | 17 | 1 | 16 | 16 |
| Delbydel (2017) | 98 | 1 | 92 | 92 |
| Grunnkretsområde | 336 | 5 | 245 | 244 |
| Unresolved native geography | 1 | 0 | 0 | 0 |

All counts are observed. Seven known geographic rows have zero sales and missing
mean price/area; the 14 missing mean cells carry source flag `-`. No explicit
privacy suppression threshold was located; no claim that these nulls are protected
counts is made. Low-count caution is documented. All rows remain in the audit.
The [government catalogue](https://data.norge.no/nb/datasets/3b424c78-4975-4d3e-ae0b-5a5ce32cdccb/oslo-kommune-apne-data-i-statistikkbanken)
identifies Statistikkbanken's platform distribution as **NLOD 2.0** (catalogue
update 2025-07-30; older descriptive entries retained). Preserve attribution,
provider limitations and the distinction between catalogue evidence and any
future restricted delivery terms.

SSB **14545**, actual region **0301**, category **03 → Blokkleiligheter**, calendar
2025, supplies a downloaded annual municipal mean/count comparison. The county
code 03 was not substituted. Its two JSON-stat cells validate, but one municipal
unit cannot supply neighbourhood variation. It is an alternative/source check,
not H replicated across areas.

Status: **METADATA_VERIFIED / DATA_ACQUIRED / PRELIMINARY_QA_PASSED** for standalone
annual BOL018 assessment; **PROVISIONAL_BOUNDARY / BLOCKED** for final spatial/H
qualification. The unresolved Step 4 municipal-boundary vintage is unchanged.
Source-matching native polygons/vintage and Step 6 joins are also pending; the
hierarchy XLSX is not a geometry layer. Discovery/acquisition proceeded despite
the municipal issue, as authorized. No boundary amendment was made.

## Stockholm

The documented **SCB RegSO 2025_v2 operational municipal mask** remains resolved:
127 areas actually attributed to municipality **0180**, reference 2025-01-01,
with the limits in [the frozen amendment](stockholm_boundary_amendment_20261011.md).
This is not certified 2026 Lantmäteriet geometry. Those components do not become
housing-price areas, an H reference frame or inferential clusters automatically.

Open alternatives were investigated before research/commercial routes:

- **SCB:** [FastprisBRFRegionAr / TAB1151](https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__BO__BO0501__BO0501C/FastprisBRFRegionAr/)
  bulk download acquired. Calendar 2025 is present across 26 national/regional
  units. The columns are `region`, `år`, `tabellinnehåll`, `Försäljning av bostadsrätter`;
  counts and mean/median **total price in thousand SEK**, not neighbourhood
  price/m². Official CC0 evidence is frozen. Rejected as primary H on unit,
  resolution and unqualified apartment-only scope. No invented floor-area division.
- **Stockholm City:** official yearbook and area-facts pages acquired/inspected.
  No verifiable downloadable 2025 neighbourhood apartment price/m² dataset was
  located there. Contextual tables and district populations are not price data.
  An unsent municipal request is prepared; absence in this inspection does not
  prove the source cannot exist.
- **SökHem:** [explicitly licensed open exports](https://sokhem.se/sv/statistik/oppna-data)
  genuinely permit CC BY 4.0 reuse with attribution. `sold.json` downloaded and
  inspected: 181 municipal rows, **47 missing slugs, 134 unique valid slugs and
  zero duplicate nonmissing slugs**, one Stockholm entry. Last sale is
  **2026-10-10**, rolling period; municipal export apartment-only scope is not
  established. No annual-2025 neighbourhood target rows acquired. Its separate
  Stockholm RegSO-named page is rolling twelve months, includes post-Airbnb
  transactions, and exposes no observed licensed calendar-2025 neighbourhood
  download. CC BY terms for the two documented exports are not automatically
  transferred to an unacquired historical area dataset. Never average medians.
- **Svensk Mäklarstatistik:** public Stockholm Excel buttons and annual-history
  chart labels exist. [Published download terms](https://www.maklarstatistik.se/wp-content/uploads/Svensk-Maklarstatistik-Allmanna-Villkor.pdf)
  attach contractual conditions to statistical downloads. No Excel/data export
  was requested and no terms were accepted. Historical annual subarea content,
  exact IDs/counts/polygons and academic redistribution permission remain
  unresolved. Its published minimum-25-transaction relevance rule differs from
  the project's preferred annual-20 safeguard. The
  [research page](https://www.maklarstatistik.se/om-statistiken/forskning/)
  invites university contact; it does not establish automatic approval, free
  delivery or a purchase requirement. An unsent request is prepared.

Status: alternative open **DATA_ACQUIRED**, but target neighbourhood annual
data/preliminary QA **BLOCKED**. Municipality-mask status does not qualify a
residential price source. Request licensed 2025 area data from open providers
first; any institutional/contractual route requires separate approval.

## Cross-city comparability and final gates

| Attribute | Copenhagen–Frederiksberg | Oslo | Stockholm |
| --- | --- | --- | --- |
| Target completed apartment construct | Candidate quarterly Ejerlejlighed means | Annual Blokkleilighet means | No qualified neighbourhood target file |
| Period | Four 2025 quarters, annual aggregation blocked | Calendar 2025 | SCB annual regional alternatives; SökHem rolling into October 2026 |
| Area denominator | Apartment BBR area; filtering/corrections | BRA/BRA-i including interior storage | Target unresolved; SCB total-price unit unsuitable |
| Price statistic | Source quarterly arithmetic mean | Source annual mean, cooperative debt included | SCB total mean/median; SökHem rolling median |
| Native currency | DKK | NOK | SEK |
| Candidate geography | Postal groups; city crosswalk pending | Bydel/delbydel/GO; polygons/vintage pending | Housing geography independently unresolved |
| Rights | Public download; reusable licence unresolved | NLOD platform evidence; source limitations retained | CC0/CC BY alternatives; contractual historical export unresolved |
| Final H qualification | BLOCKED | BLOCKED / PROVISIONAL_BOUNDARY | BLOCKED |

Native ranks do not cure category, area-denominator, period, source-selection or
statistic differences. No cross-currency pooling/conversion was performed.
No final H ranks/log-H assignments, listing joins, samples/folds, network features,
fitting, residential outcome model or gentrification score were produced.

Preserve prospective safeguards: preferably ≥20 known annual sales per area,
≥10 usable distinct areas with variation; final sample ≥80% housing coverage,
≥10 represented areas, lower/higher groups each ≥4 areas and ≥100 listings.
These are project safeguards, not power guarantees. Step 5 standalone supported
area counts are not final represented-area counts. Coverage and housing-group
support remain **NULL / NOT_ASSESSED**, never fabricated percentages or zero.
No external reference frame is frozen until its geography/qualification is approved.

## Implementation, persistence and commands

`src.v4.housing` reuses the existing immutable `acquire`, `Paths`, `Scope`,
`freeze_sources`, `register_manifest` and dedicated V4 database guards. The source
adapter adds public JSON/form POST query receipts to the existing downloader;
GET behavior and original receipts are preserved. Schema/type/locale/period,
duplicate IDs, unavailable cells and source drift fail closed. Raw data, parsed
audit records and research-ready H are explicitly different states.

New append-only migration **025_v4_housing_source_audit.sql** follows the actual
023/024 ledger. No applied migration was edited. Authoritative storage is
PostgreSQL/PostGIS `thesis_accessibility_v4`: independent `v4_raw.housing_ingestions`
and `v4_raw.housing_area_period_audit`, scoped by version/run/city/snapshot/source/
native geography/period. Insert-only guards prevent reopening, late children,
cross-city/source mistakes, update/delete/truncate. Housing audits do not create
model runs or mutate listing ingestions. SQL independently checks counts,
missingness, supported-area counts and price variation against the source audit.

Use explicit identities; commands return **exit 2 / BLOCKED** for this safe
checkpoint because final scientific gates remain blocked. That does not erase
successfully downloaded or parsed data. Missing raw cache, source revisions or
expired public export URLs need a new reviewed source identity, not overwrite.

```sh
make v4-housing-acquire VERSION=research_design_v4 CITY=<authorized_city> \
  SNAPSHOT=2026-06-30 RUN_ID=research_v4_<city>_<UTC_timestamp>
make v4-setup VERSION=research_design_v4 CITY=<authorized_city> \
  SNAPSHOT=2026-06-30 RUN_ID=research_v4_<city>_<UTC_timestamp>
make v4-housing-ingest VERSION=research_design_v4 CITY=<authorized_city> \
  SNAPSHOT=2026-06-30 RUN_ID=research_v4_<city>_<new_UTC_timestamp>
make v4-housing-audit VERSION=research_design_v4 CITY=<authorized_city> \
  SNAPSHOT=2026-06-30 RUN_ID=<the_committed_housing_ingestion_id>
make v4-test
make v4-test-db
```

Acquisition cache rereads verify immutable bytes/receipts; no unnecessary redownload.
Audit reruns read committed SQL and compare existing export bytes, without writing
over them. Ingestion reruns with a committed ID refuse before acquisition. New
source policy affects scientific dependencies; Markdown/log/reporting changes do
not enter them. See the [access requirements](housing_access_requirements.md) for
unsent drafts and manual-import specification. Step 6 is **not ready as a fully
qualified three-city workflow**; Oslo source-level input is partially ready, but
its geography and other cities' specific scientific/access inputs remain blocked.
