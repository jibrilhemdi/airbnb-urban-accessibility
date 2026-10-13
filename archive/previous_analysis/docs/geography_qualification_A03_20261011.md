# A03 geography qualification — 11 October 2026

Design **v4_accessibility_only_20261011**. Checkpoint **PARTIAL / BLOCKED**:
Copenhagen's inherited operational analysis geography is qualified; Oslo's
municipal vintage blocker is resolved with a limited, dated source amendment;
Oslo and Stockholm analysis geography remains blocked. No A04 income/context
acquisition, networks, final samples/folds, routes or fitting was performed.
Housing-price inputs are **NOT_REQUIRED_SCOPE_AMENDED**, not geographic gates.

## Actual entry, sources and immutable identities

Existing clean `v4`, fetched origin/local starting HEAD
`be13d5b602d361b6173c0d336483053e06d75c3d`, zero divergence; no staged work,
other edits or unfinished Git operation. Recorded origin remains
`https://github.com/jibrilhemdi/airbnb-urban-accessibility.git`.
Local main/v3 and detached worktree refs are unchanged. Read AGENTS, contract,
A02 audit/log, active/revised proposal/plan, original V3 geography code, listing
and Stockholm acquisition records, configurations, migrations and tests.

Read-only reuse selects exactly the original Copenhagen and Oslo runs
`research_v4_<city>_20261011T143812Z` and amended Stockholm
`research_v4_stockholm_20261011T151637Z`. Exact approved listing-manifest hashes:

| City | Approved listing manifest SHA256 |
| --- | --- |
| Copenhagen–Frederiksberg | `e6dedcc9d12545559337cc3a512d97d6a8b8b636cd1ab329ad52dcd13c2e2b13` |
| Oslo | `c08f5ebdaf01ba445cc68e2e0c77b9290c246903f67408013556a071b84252f8` |
| Stockholm | `d1d923db415dbf2218560947e3fd862657e343317f36fee284fa36e36cc0d172` |

SQL identity/purpose/canonical manifest and all approved source bytes were checked.
No Airbnb reacquisition or duplicate listing ingestion. The 13 old listing
ledgers include superseded/audit identities; they are never summed as independent
observations. New A03 geography records, not listing/model runs, use
`research_v4_<city>_20261011T210000Z`. This is a preallocated job identifier,
separate from actual retrieval and SQL creation timestamps.

[The safe aggregate JSON](geography_qualification_A03_20261011.json) is an export
of authoritative committed SQL summaries. [The source registry JSON](geography_source_registry_A03_20261011.json)
records actual URLs, reference/retrieval dates, licences/unknowns, CRS, checksums,
locations, transport failures and rejected sources. No raw content, listing
coordinates, private predictions or listing-level records is included.
`config/v4/geography_A03_20261011.json` pins sources/receipts/decisions;
`geography_reuse_accessibility_only.json` pins the new SQL summaries/manifests.
Prior configurations and applied migration bytes remain unchanged.

## Geometry and assignments

All primary masks use established **covers in EPSG:4326**, including literal
boundary points. Metric area/distance use Copenhagen EPSG:25832, Oslo EPSG:25833,
Stockholm EPSG:3006. The inherited V3 area rule is **exactly one area and one
compatible municipality**, otherwise NULL/unresolved. Sorted candidate IDs make
ties reproducible; no lexicographic winner, nearest-centroid assignment or silent
repair is introduced. All input rows are retained, including missing prices,
outside/unmatched/uncertain rows. Duplicate listing/area/component IDs fail,
except Oslo's explicitly verified two Marka polygon components.

PostGIS mask GeoJSON transport is explicitly nine decimal places; projection
round trips cause sub-millimetre registration differences. Native source areas
and transported QA areas are distinguished, not declared bit-identical linework.
Independent PostGIS covers tests against **exact original stored masks** reproduce
the counts and find zero listing inclusion changes in every city. Outer 150 m
flags use exterior rings of the dissolved municipal mask, excluding interior
holes and shared municipality borders. Area-border flags are separately recorded
per uniquely assigned analysis area. No exact-address inference is made.

| City | Raw | Dwelling | Positive observed | Inside raw | Inside dwelling | Inside positive | Outside positive | Outer-near positive |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Copenhagen–Frederiksberg | 23,144 | 21,080 | 12,521 | 23,068 | 21,021 | 12,508 | 13 | 1,233 |
| Oslo | 13,391 | 11,776 | 8,557 | 13,391 | 11,776 | 8,557 | 0 | 29 |
| Stockholm | 4,806 | 3,834 | 2,510 | 4,806 | 3,834 | 2,510 | 0 | 49 |

Invalid coordinates and duplicate IDs are verified zero in the selected audit
layers; original invalid/schema/price audits remain preserved. These are support/
acquisition counts, **not final prediction or association samples**. Original
positive-price flags measure availability only; no monetary values, price-model
scores or housing fields select areas/groupings. All four model blocks remain
M0=X, ME=X+E, MW=X+W, MEW=X+E+W. Counts need not equal V3's final feature sample.

## Copenhagen–Frederiksberg

Retain municipalities **0101 + 0147**, official district `bydel_nr` **1–10**,
versioned IDs `cph_01`–`cph_10`, and peer `frederiksberg_0147`. Source hashes are
unchanged: Copenhagen municipality `55967e4b…032a1`, Frederiksberg
`1d8bf7fe…031`, districts `3addcdf7…0d75c3`. Exact hashes/URLs are in the registry.
Municipal source dates are 2026-03-27 / 2024-01-16; district reference date was
not provided, inherited retrieval is 2026-09-29. This retains V3 operational
geography, not a newly certified June cadastral partition.

Municipal mask gross **100.40664277 km²**, 37 connected pieces. All 11 area
geometries are valid; union gross **101.53736570 km²**. Source differences are
not hidden: district/Frederiksberg overlaps total **798.63 m²** (six pairs),
municipal mask uncovered **252,124.55 m²**, area excess outside mask
**1,382,847.48 m²**. They are registration/territorial-footprint differences in
inherited sources, not zero-overlap/full-territory certification. No clipping,
snapping or density-denominator change is performed. A04 must preserve/audit
source-specific gross denominators and statistical-unit compatibility.

Of 23,068 raw listings inside the mask, **23,066 assign uniquely and two remain
unmatched**. Neither unmatched record is an eligible positive-price observation.
All **12,508** eligible positive inside observations have unique compatible area
assignment. This supports the **limited inherited operational assignment**
qualification with all mismatches kept in the audit, not a global geometry pass.

| Native/proposed area | Eligible positive holdout support |
| --- | ---: |
| cph_01 | 1,840 |
| cph_02 | 1,421 |
| cph_03 | 2,208 |
| cph_04 | 2,174 |
| cph_05 | 481 |
| cph_06 | 274 |
| cph_07 | 221 |
| cph_08 | 534 |
| cph_09 | 983 |
| cph_10 | 1,067 |
| frederiksberg_0147 | 1,305 |

Eleven native/proposed holdouts meet current >=30 test/>=500 complementary
training count safeguards. Per-area gross area, pieces, raw/dwelling support,
border flags and complementary counts are in the JSON. Final matched feature
support, membership and buffers still wait for A06. No new grouping is frozen.

## Oslo

See [the separate dated Oslo amendment](oslo_boundary_amendment_A03_20261011.md).
Verified Kartverket code **0301**, CCBY4.0, dated EPSG:25833 polygon: catalogue
reference 2026-01-01, extraction 2025-12-10, polygon update 2025-11-11.
Source identity, topology, bounds, independent official area metadata and relevant
change checks support **operational use with certification limits**. Neither
same rounded area nor absence of a listed change proves exact June linework.
Source and transported gross areas are approximately **481.04034033 km²**.
Original API uncertainty remains immutable historical evidence.

The city-published level is the June-effective **15 boroughs plus Sentrum and
Marka**, official statistical codes `01`–`17`, represented by 18 polygons.
These district/service/statistical units offer a documented city-specific
administrative-scale option comparable in role, not presumed equal in size to
Copenhagen districts. New IDs `oslo_01`–`oslo_17` preserve native codes separately.
All 13,391 raw/8,557 positive eligible inside listings assign uniquely.

| Native/proposed area | Eligible positive holdout support |
| --- | ---: |
| oslo_01 | 1,564 |
| oslo_02 | 1,526 |
| oslo_03 | 993 |
| oslo_04 | 1,002 |
| oslo_05 | 1,222 |
| oslo_06 | 242 |
| oslo_07 | 276 |
| oslo_08 | 382 |
| oslo_09 | 219 |
| oslo_10 | 56 |
| oslo_11 | 36 |
| oslo_12 | 136 |
| oslo_13 | 253 |
| oslo_14 | 415 |
| oslo_15 | 86 |
| oslo_16 | 132 |
| oslo_17 (Marka) | 17 |

**Analysis geography BLOCKED:** ArcGIS item/layer licence is unstated, and Marka
has only 23 dwelling-filtered / 17 positive eligible listings. Sixteen of 17
proposed native holdouts meet count safeguards; native count is not a qualified
fold count. No unsupported-area omission, price-selected regrouping or inferred
Marka service-area allocation is made. The actual small coverage/overlap
registration differences remain provisional, not repaired. Clear source reuse
terms plus a verified, substantively justified sparse-area allocation/grouping
are required before Oslo geography can support A04/A06 dependent assignments.
Future eight-borough reform is effective 2028, not June 2026 geography.

## Stockholm

Retain exactly the accepted **SCB RegSO 2025_v2**, municipality **0180**,
reference **2025-01-01**, EPSG:3006 operational mask. Original 127 RegSO IDs are
source components, **not validation areas**. Native gross area
**215.7572992247 km²**; transported SQL QA **215.7572993397 km²**. The original
amendment, RegSO sources/receipts and original Lantmäteriet 401/NULL ledger stay
unchanged. No new mask substitution or RegSO analysis suitability decision.

The [official city borough page](https://start.stockholm/om-stockholms-stad/politik-och-demokrati/namnder-och-bolagsstyrelser/stadsdelsnamnder/)
(updated 2026-03-19) identifies **11 current boroughs**, chosen as the substantive
analysis-level target. Their full polygon IDs/vintage/support remain unresolved.
Official dataset metadata
`GetMetaDataById?id=719b8823-a3f2-41a1-9b32-0259e60afda7&showmetadataview`
redirects to `catalog.signin`. The immutable transport receipt reports HTTP200
for that HTML redirect; the new manifest explicitly labels **failed geometry
access**, not a successfully acquired boundary. No login/bypass was attempted.

The public official archive
`https://dataportalen.stockholm.se/dataportalen/Data/Stadsbyggnadskontoret/SHP_utanfastigheter_nya_granser.zip`
was acquired once, SHA256
`7e92c9e664ffe51aec4a2ecfa409bdd4d2fb1421aa474af3f0c80e52f1c3da27`.
Actual administrative layer is **Adm_area**, source CRS **EPSG:3011**, fields
`GRUPP/KATEGORI/RAMKLIPP/NAMN/ADM_ID`. Selects **13 old borough polygons**, all
`RAMKLIPP=yes`; **Skarpnäck is invalid**. Member date 2020-12-10 is distinct from
HTTP Last-Modified 2025-11-14 and current retrieval. No repair or merger is
inferred from name resemblance. The archive is preserved **REJECTED** evidence.
Its gross area sum is unqualified, not a coverage certification. Unused archive
address/building layers were not used for listing/address inference.

**Stockholm analysis geography BLOCKED:** obtain official current 11-borough
polygons with stable IDs, source dates, clear reuse terms and valid full-city
coverage through a legitimate public release or separately authorized import.
Qualified native count, holdout counts and borough assignments remain **NULL**,
not zero. All 4,806 rows retain `analysis_geometry_unavailable`. An operational
RegSO analysis option would need a separately documented suitability decision;
it is not silently substituted here. Income/density/context remain A04.

## Architecture, reproducibility and genuine remaining tasks

Append-only migration **027_v4_geography_qualification.sql** creates independent
geography parent/mask/area/private-assignment audit tables. Purpose/city/design/
listing-source-manifest guards, unique IDs, valid geometry, committed-parent
transaction guards and UPDATE/DELETE/TRUNCATE refusal preserve old ledgers.
No old table/migration is changed. New source manifests include rejected evidence
without approving it for features. Raw sources/receipts/intermediate data remain
ignored. PostgreSQL/PostGIS is authoritative; committed JSON is aggregate export.

`src/v4/geography.py` reuses acquisition, source-freeze, V4 identity/connection,
manifest and approved-listing readers. A03 adds no estimator/framework/route runner.
Full source URLs and immutable GET/POST requests are in the registry; the existing
`acquire` function is the adapter for separately identified future recovery.
Never rerun Airbnb acquisition to recover analysis polygons. Missing pinned
sources fail rather than fetch replacements automatically.

Supported, implemented and exercised commands:

```sh
make v4-geography-freeze VERSION=research_design_v4 CITY=oslo SNAPSHOT=2026-06-30 RUN_ID=research_v4_oslo_20261011T210000Z
make v4-geography-audit VERSION=research_design_v4 CITY=oslo SNAPSHOT=2026-06-30 RUN_ID=research_v4_oslo_20261011T210000Z
```

Default design is accessibility-only; explicit `DESIGN_ID` is supported through
existing Makefile conventions. Freeze refuses committed run IDs. **For these
committed identities use audit only**, never rerun freeze to reopen them.
Audit recomputes sources, geometries, support and counts against immutable SQL;
Oslo/Stockholm return CLI/Make exit2 while preserving a truthful blocked checkpoint.
Full safe `geography_audit` JSON appears in command output; no listing rows.
The aggregate JSON can be reproduced by reading `geography.evidence` for the
three selected identities and comparing the audit output. No data CSV becomes
an alternative store. Final fold membership is not an A03 output.

Read-only preflight verifies the selected A03 policy, raw/receipt/manifest hashes,
SQL summary hashes and exact listing link. It replaces only qualified mask/metric
warnings, including the **exact old Oslo vintage warning**, not context/price/
sample/feature/support requirements. Old city definitions remain unchanged.
Scientific dependencies include city-specific A03 policy/selection; Markdown,
reporting/log edits stay outside science hashes. New-city context mappings and
central anchors are unresolved; income is not acquired. A04 remains unexecuted
and would require its own prompt plus qualified inputs for the affected city.
Copenhagen geography is ready for the next authorized context audit; Oslo mask/
metric QA is ready but analysis-dependent tasks are blocked; Stockholm mask/
metric QA is ready but borough-dependent tasks are blocked. A05 networks and
A06 final samples/folds, A07–A12 empirical work are not authorized here.

## Actual checks

Final check results and preservation counts are appended in the step log after
execution. Unit/SQL tests retain historical housing assertions and genuine
geography/context failures. No skipped historical assertion or false all-city
readiness claim is used to obtain a successful checkpoint.
