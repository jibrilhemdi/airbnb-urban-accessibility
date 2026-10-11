# V4 matched-listing acquisition and boundary audit

Definition `v4_listing_ingestion_20261011`; acquisition only, no fitted models.
Read the implementation contract, active specification and step log first.

## Inherited rules checked before ingestion

The actual V3 `src/pipeline/build_airbnb_sample.py` constant and
`sql/queries/build_clean_airbnb_listings.sql` match the user's six dwelling
types exactly: Entire rental unit, Entire condo, Entire home, Entire loft,
Entire townhouse and Entire villa; room_type must be Entire home/apt.
No dwelling-rule discrepancy or minimum-review/activity primary filter was
found. V4 imports that constant and the strict observed-price parser without
executing a V3 pipeline. V3's room-category QA recognises only its three
observed room types; V4 retains all raw categories and applies the exact
dwelling predicate rather than assuming another city's category universe.

The safe full baseline exposed V3 source discovery's recursive scan into the
new reserved V4 raw directory. Its sole compatibility change excludes that
specific tree from V3 registration. Unknown legacy providers still fail and
all existing V3 source checks remain active. A temporary synthetic isolation
test covers both cases; no V3 row/import/migration/result is regenerated.

Geography discrepancy: V3's initial `in_study_area` flag uses its provider
neighbourhood lookup, followed by later official spatial assignment. V4's
acquisition audit directly tests official municipal geometry with `covers`
in EPSG:4326, including boundary points. Coordinates are provider-anonymised;
membership is operational, not an address-level claim. No V3 code is changed.
Provider labels, official analysis areas and future native housing areas are
distinct fields; the latter two are NULL at this stage, never invented from
provider labels. Copenhagen's study union uses municipalities 0101 and 0147,
not its district collection. No Copenhagen metric projection is used elsewhere.

## Reproducible commands

`make v4-acquire VERSION=research_design_v4 CITY=<city> SNAPSHOT=2026-06-30
RUN_ID=research_v4_<city>_<UTC timestamp>` fetches exact catalogue/archive
evidence and detailed listings, freezes ignored raw receipts/manifests and
writes a private inspection audit. It does not write a database/model run.

`make v4-ingest` with the same explicit arguments applies the dedicated V4
checksum migrations and atomically persists the raw row/audit/boundaries and
aggregate summary in PostgreSQL/PostGIS. It requires `.env.v4` settings and
the isolated `thesis_accessibility_v4` database; it cannot connect using V3
settings. This step's append-only migration is 024; 023 is unchanged.
An ingestion ledger is independent of housing-gated model runs. It is immutable
on commit and cannot be reopened, overwritten or appended to. Repeated run IDs
fail. No model sample, feature matrix, housing assignment or fit is created.

Raw locations follow `data/raw/v4/research_design_v4/<city>/2026-06-30/`;
manifests use `data/metadata/v4/` with content-hash names; inspection audits use
scoped `data/interim/v4/`; database-derived aggregate exports use `reports/v4/`.
All remain ignored. V3 Copenhagen files are checksum-verified, copied unchanged
into this separate source freeze, and record their original retrieval date and
reuse path. No raw source or frozen V3 provenance is rewritten.

Receipts record exact URL/final URL, catalogue selection, retrieval UTC,
reference period, licence, checksum, local location, HTTP status and applicable
CRS. Retries use the same immutable receipt and never pretend cached bytes were
newly retrieved. Failed attempts are frozen with status and URL, not response
contents/credentials. Resolving a frozen failed source requires a separately
identified acquisition amendment rather than silently replacing its receipt.

The adapter discovers Gatsby archive query IDs from the official catalogue
page-data response, and selects exactly one city/30 June 2026 entry. There is
no latest-snapshot fallback. CSV schema, gzip decoding, source scrape ID, actual
scrape dates, quoted-stay fields and quote currencies are independently audited.
The official linked dictionary defines price in local currency. The export's
literal `$` is a formatting token; observed native DKK/NOK/SEK is checked against
quote.currency, not inferred as USD. The inherited explicitly declared US
export grouping/decimal convention is retained; other formats are rejected,
never guessed from ambiguous separators. Invalid nonempty prices retain their
raw text and a flagged NULL parse; they block qualification. They are never
treated as an ordinary missing outcome or replaced by quoted alternatives.

The original observed `price` remains the outcome candidate. Quote totals,
nightly rates, requested/returned dates and raw JSON remain raw audit fields.
Differences are counted, never used to replace/impute price or relabel a quoted
stay as the batch/scrape date. Eligible missing/nonpositive-price listings stay
in the audit. Positive observed price is necessary for the eventual prediction
sample; no prediction sample is qualified here. Invalid/duplicate source IDs
stay under row-number audit keys and block subsequent uniqueness qualification.

`make v4-listing-audit` with the same identity reads the committed SQL audit,
checks source hashes and independent SQL raw/dwelling/positive counts, and writes
only whitelisted aggregate/provenance evidence. It performs no acquisition or
database mutation. This checkpoint copies those reviewed safe exports to
`listing_acquisition_audit.json`; private fields/rows are never exported.

Selected audits use timestamp `20261011T143812Z`. All files have the same
90-column detailed schema; positive observed prices agree with the flattened
quoted-nightly field. Nested quote rates carry more decimals: 3,556 / 2,369 / 793
Copenhagen/Oslo/Stockholm amounts differ only within half a native currency cent
after source rounding. Decimal-string comparisons avoid binary floating-point
false positives; no amount is substituted. All returned dates and date_match
values are NULL. Flattened dates match requested dates; the returned stay is
not independently verified. Requested check-in/checkout ranges span
30 June 2026–3 July 2027, not just the June batch.

| City | Raw | Dwelling | Positive observed price | Inside municipality + dwelling + positive | Eligible missing price | Invalid / duplicate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Copenhagen/Frederiksberg | 23,144 | 21,080 | 12,521 | 12,508 | 8,559 | 0 / 0 |
| Oslo | 13,391 | 11,776 | 8,557 | 8,557 | 3,219 | 0 / 0 |
| Stockholm catalogue extract | 4,806 | 3,834 | 2,510 | UNRESOLVED | 1,324 | 0 / 0 |

These are acquisition counts, not housing-qualified prediction/OLS samples.
PostgreSQL is authoritative; preliminary audits remain immutable and are
superseded by the explicitly selected scopes, never summed as new listings.

## Blocked boundary adapter

Oslo uses the Kartverket municipal `0301/omrade` API with explicit EPSG:4326.
The API's current geometry is a verified municipality, but its geometry vintage
is not supplied; retain current-at-retrieval and mark temporal qualification
unresolved. Do not assign a June/annual vintage from HTTP Last-Modified.

Stockholm's official Lantmäteriet municipal collection probe is
`https://api.lantmateriet.se/ogc-features/v1/administrativ-indelning/collections/kommuner/items?f=json&limit=1`.
This is an authentication probe, not a selected Stockholm geometry. If access
requires credentials, do not bypass it; qualified municipal API feature selection,
licence and vintage remain unresolved. The publicly accessible collection
metadata does not supply an acquired municipal polygon. Do not substitute the
Stockholms län extract/provider neighbourhoods or SCB's simplified thematic
boundaries: SCB explicitly states those are unsuitable for analysis.
SCB's official 2026 code register verifies Stockholm municipality **0180** within
county **01 Stockholms län**; that code evidence does not supply a polygon.
Inside-boundary counts are NULL when the official geometry is unavailable,
never zero or the county's listing count. Resolving this blocker requires an
authorized source/selection amendment and a new freeze.

Safe public evidence and actual aggregate counts are recorded separately in
`listing_acquisition_audit.json`. Raw rows, coordinates, IDs, host details and
credentials are never committed. H/context/analysis-area and model-sample gates
remain BLOCKED regardless of acquisition success.
