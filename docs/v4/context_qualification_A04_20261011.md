# A04 baseline context qualification — 11 October 2026

Design `v4_accessibility_only_20261011`. **PARTIAL / BLOCKED** three-city research
readiness. Only population, income and civic-anchor source/context work was
executed. No housing acquisition/contact, Airbnb redownload/reingestion,
new analysis-geography choice, network/routes, final samples/folds or fitting.
The selected listings and A03/Stockholm amendments remain immutable.

Entry: clean existing `v4` at `161d556fa806197446217e59041e9d59dc341e3a`, fetched
recorded origin with zero ahead/behind; no unfinished operation/unrelated input.
Remote URL/main base remain those in the repository audit. Local main/v3 and
the detached worktree are preserved. Read root AGENTS, active contract/log,
A02/A03 audits, Oslo amendment, active specification and supplied revised
proposal/plan/A04 prompt. V3 source/code/config/SQL/tests and actual Makefile were
inspected. Historical housing and raw data remain unchanged and outside scope.

## Actual states

| City | Acquired/reused | Source validation | Listing-level spatial context | Final context qualification |
| --- | --- | --- | --- | --- |
| Copenhagen–Frederiksberg | Four exact V3 population/income files reused by SHA; no remote re-fetch | Eleven accepted source/formula/SQL contexts independently reproduced | 23,144 retained audit rows; 23,066 compatible unique joins; 78 outside/unmatched remain NULL | QUALIFIED_INHERITED_WITH_CAVEATS; three-city income/future scientific gates still block empirical work |
| Oslo | Official BEF001 2026 + INN003 2024; civic point and schema/definition evidence acquired | 19 population units, 17 income units; all observed, native variation present; statistical reuse terms unresolved | NOT_JOINED; zero derived listing context rows, not zero population or missing-area counts | BLOCKED: A03 borough licence/Marka support, compatible income geography, source terms and three-city income policy |
| Stockholm | Official SCB population 2025 + income 2024, 127 RegSO2025 native units | 127 population + 381 income/count cells, no missing source cells; exact native ID match to preserved mask components; CC0 | NOT_JOINED; RegSO matching is source QA, not approved analysis geography or borough crosswalk | BLOCKED: current borough polygons, public anchor coordinate and three-city income policy |

The authoritative independent checkpoint tables are PostgreSQL/PostGIS
`thesis_accessibility_v4.v4_features.context_qualifications`,
`native_context_cells`, and private `listing_context_audit`, added by
**028_v4_context_qualification.sql**. CSV/JSON exports are not alternative stores.
The [safe SQL aggregate export](context_qualification_A04_20261011.json) and
[source registry](context_source_registry_A04_20261011.json) carry exact hashes,
units, dates, requests and status distinctions. New context identities are
`research_v4_<city>_20261011T210800Z`; the identifier is separate from actual
source retrieval and SQL creation times. Original selected listing/geography
run identities and manifest hashes remain explicit in each new SQL parent.

## Copenhagen–Frederiksberg: inherited context retained

Reproduced `config/qualified_income_decision.json` SHA256
`355ab55de7e9cdf00995979806ae818093b599ff417ee805b2ea3fb12c5cc9e9` and SQL's eleven
income records SHA256
`53d6522c6db041d3cfaafebe44b313980ebab7c7381f0529d41d342316d1637d`.
Formula: `(d1 + ... + d10)/10`; model scale `/100000 DKK`. Each of 110 decile
means is observed. Exact KKIND5/IFOR35 raw and selection hashes are in the registry.
KKIND5 basis remains not_confirmed; IFOR35 uses nominal current-price selector
006. Eligibility/finite-count/tie/weighting/variable-treatment details remain
qualified caveats. This settled construction is not reopened by dropping H.

Population is inherited **2026Q3, 1 July 2026**, one day after the Airbnb batch:
KKBEF1 total sex/age/marital status, native codes 1001–1010, plus FOLK1A 147 total.
KKBEF1 SHA `953f29d57f9d62fecc747a68830f97cc6acb54ff8e364c0b180c48503bb26009`;
FOLK1A SHA `62af775af77d0cdfd82a50f497c3ffd8c1ec18e57ca7c7821b2a51c815b5caa8`.
Selectors, native code mapping and every source count are checked against SQL.
No municipal total is redistributed or rescaled to force a match.

Density remains `log(population / gross native assignment-polygon km2)` in
EPSG:25832, independently checked against source-compatible V3 SQL polygon area.
Water inclusion and statistical-versus-polygon boundary vintage remain
unverified inherited limitations. Do not replace gross area with land-only,
clip polygons to the municipal mask or erase A03 registration gaps/overlaps.
All eleven contextual units have distinct population/income values; native
IDs remain the ten districts plus Frederiksberg peer, not provider labels.

Centrality retains City Hall Square `(12.568809986,55.675902629)` EPSG:4326,
inherited official tourism URL accessed 2026-09-29; distance is straight-line
Euclidean km after EPSG:25832 projection, matching actual V3 code/SQL.
The public point lies within the preserved mask. Every original listing audit
row is retained; NULL outside/ambiguous/missing context is not filled. A03's
12,508 eligible positive inside listings have compatible area assignment; this
is acquisition/context QA, not a final sample or a forced match to V3 fits.

## Oslo: native data validated, joins blocked

[Oslo's official Statbank](https://statistikkbanken.oslo.kommune.no/) supplies
actual public PxWeb table IDs **OK-BEF001.px** and **OK-INN003.px**. Frozen requests
use confirmed metadata selectors, not guessed codes. BEF001 selects both sexes,
all 106 single-year ages (last 105+) and year code36=2026; total ages within each
of 19 distinct source units, preserving municipality301, borough30101–30117
and unlocated30199 separately. Observation date **2026-01-01**; data update
2026-03-03, catalogue update2026-03-04 differ. Municipal totals are never summed
with boroughs. City anonymisation can yield discrepancies versus SSB10826;
no adjustment is applied.

INN003 selects year17=2024, all households0, mean variable0, city100000, native
borough1–15 and combined88. It is after-tax equivalised household income, NOK,
not gross earnings or a median. Student households are excluded, EU weights
1/0.5/0.3 are explicit, and equivalised income is assigned to household members.
Mean publication weighting is not established as identical to Copenhagen's.
Update2026-08-03 is later than the listing batch, while reference year stays2024.
**88 combines Sentrum, Marka and unregistered addresses**: it cannot be copied
onto separate16/17 polygons or disaggregated using population weights.

Public access and SSB attribution do not establish city-service reuse terms.
The receipts preserve UNRESOLVED_OSLO_STATBANK_REUSE_TERMS. No third-party licence
claim is treated as official verification. A03's ArcGIS licence and sparse Marka
issues remain; no listing join/density denominator or service split is accepted.
Official borough-level population/native income acquisition is useful safe
progress, not area-context approval.

The official [Kartverket SSR API](https://kartverket.no/en/api-and-data/stedsnavndata/brukarrettleiing-stadnamn-api)
returns exactly one active approved civic Rådhus, municipality0301,
stedsnummer854084. Representation point `(10.7336,59.91199)` is **EPSG:4258**,
the default confirmed in actual frozen OpenAPI. It transforms to EPSG:25833
for distance and lies in the approved operational municipal mask. It is a public
civic representation point, not an entrance survey or a June-specific location
certification. Source reference date is unavailable; actual retrieval is recorded.
[Official terms](https://kartverket.no/en/api-and-data/terms-of-use) are CC BY4.0,
©Kartverket. No listing-level distance/context output is finalized for Oslo.

## Stockholm: native RegSO statistics, no borough substitution

Actual SCB API tables **BE/BE0101/BE0101Y/FolkmDesoAldKon** and
**HE/HE0110/HE0110I/Tab3InkDesoRegso** were selected from official catalogues.
Population selectors: Region127 actual `0180R..._RegSO2025`, age totalt, sex1+2,
ContentsCode000007Y7, Tid2025. Reference **2025-12-31**, update2026-03-24.
Income selectors: same native units, Tid2024, mean000008AA, median000008AB and
eligible-person count000008A5. Units are **thousands SEK** for income and persons
for counts, not DKK/NOK. Mean and median remain separate. Reference year2024,
update2026-01-20; constant latest-year prices therefore mean2024 in this frozen
extract. CC0 is verified from [SCB's official open-data terms](https://www.scb.se/en/services/open-data-api/).

Economic standard assigns household disposable income to people using Sweden's
published consumption scale, including shared-residence child adjustments;
full-year household eligibility and realised capital gains/losses are documented.
The [pre-fit income proposal](income_decision_proposal_A04_20261011.md) records
substantive differences and an unactivated option requiring approval.

From population reference2025, SCB introduces Cell Key Method privacy noise;
sums need not equal independently published totals. Unlocated residents may be
allocated by SCB to central-place native areas for disclosure protection.
These are source limitations, not research imputation. No population redistribution,
exact-address inference or smoothing is performed. All127 native codes match
preserved RegSO2025_v2 components, but **no RegSO validation-area suitability
approval, borough crosswalk, listing join or density qualification is inferred**.
Approved matching analysis/context geography remains missing.

City pages identify **Stadshuset, Hantverkargatan1** as the public civic anchor.
The official visitor and city-tourism pages expose an address-only map search,
not verifiable point coordinates/CRS. The initial `/hitta-hit/` probe's404 receipt
is retained, followed by the actual linked `/infor-ditt-besok/hitta-hit/` evidence.
Anchor coordinates remain NULL/BLOCKED; no coordinate from memory, a search
snippet, third-party geocoder or an inaccessible cadastral portal is substituted.
Required input: a legitimately public, verifiable civic point coordinate with
explicit CRS/provenance. No provider access requests or authentication bypass occurred.

An additional official [Stockholm Konst page](https://www.stockholmkonst.se/konst/stadshuset-100-ar-interiort) publishes coordinates for an interior artwork at Stadshuset.
This later discovery is separately frozen under manifest
`873d2237f9a60b57d6e68e45a3b42eddc0b70f95f3bdbed1bef64769d368489a`,
with retrieval timestamps/checksums in the source registry. The page does not
state coordinate datum/CRS or certify this artwork marker as the designated
civic reference point. It is **DISCOVERY_ONLY_NOT_QUALIFIED**, not an assertion
that no public coordinates exist. Original NULL-anchor checkpoints remain intact;
qualification would require a separately identified, justified source amendment.
No artwork/image or page content is published, and website reuse terms remain
unresolved. This discovery-only manifest is not a fourth SQL context parent.

## Architecture, commands and outstanding work

`src/v4/context.py` reuses the existing immutable acquire/manifest, identity,
approved listing reader, A03 evidence and dedicated DB APIs. It adds a strict
JSON-stat2 decoder checking actual native keys/labels/units/selected years, retains
missing cells, tests finite values and variation, and separates source validation
from joins. Copenhagen copies approved SQL context into new V4 cells only after
source/formula verification; the source-compatible gross polygon is authoritative.
The new parent is linked to exact immutable geography/listing source hashes;
committed parents/children cannot grow, update/delete or truncate. Old rows stay
intact; no model run is created. Scientific city-specific context policy/source
selection and shared reader hashes are included separately from Markdown/logs.

Implemented and exercised targets:

```sh
make v4-context-acquire VERSION=research_design_v4 CITY=oslo SNAPSHOT=2026-06-30 RUN_ID=research_v4_oslo_20261011T210800Z
make v4-context-audit VERSION=research_design_v4 CITY=oslo SNAPSHOT=2026-06-30 RUN_ID=research_v4_oslo_20261011T210800Z
```

`v4-context-acquire` replays only frozen verified public requests and reuses
existing receipts; changed/missing evidence fails rather than selecting newer
statistics. `v4-context-freeze` created this independent checkpoint once;
**use audit for these committed identities**, never reopen them. Audit verifies
sources and every SQL child against deterministic recomputation. Copenhagen
returns0, Oslo/Stockholm return2 because scientific gates remain BLOCKED.
The initial container connection timed out; the same healthy configured container
recovered, with no restart/reset/service/environment change. A later verification
caught a record-order change between freeze/audit; original deterministic source
order was restored, original frozen records preserved, and all audits rerun.

Ready: Copenhagen inherited context; new-city native source discovery/validation;
Oslo public anchor and each A03 metric CRS. Blocked: Oslo geometry/licence/Marka/
income88 mapping/source terms; Stockholm current borough/context geometry and
anchor coordinate; a frozen defensible three-city income mode. New-city density
must wait for approved gross matching polygons, not municipal population allocation.
A05–A12 remain unexecuted and require their own request. A04 does not silently
change primary X or waive ordinary source/context/feature/price/support gates.

Actual tests/preservation counts and final SQL checkpoint verification are
recorded in [the step log](step_log.md). Supplied DOCX and historical V3 documents
remain unchanged; active Markdown is authoritative.
