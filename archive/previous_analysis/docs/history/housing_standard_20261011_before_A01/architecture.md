# V4 multi-city architecture — active Markdown

Architecture version: `v4_cities_20261011`. Scientific definition:
`v4_housing_standard_20261011`. User-authorized cities are exactly
`copenhagen_frederiksberg`, `oslo`, `stockholm`. The architecture step established
isolation/persistence; the subsequent [listing step](listing_acquisition.md)
adds acquisition/audit ingestion only. V3 results were already observed. Housing
qualification and modelling stages remain **BLOCKED**; no fitting is implemented.

## Reuse and city qualification

The thin `src/v4` adapters reuse existing streaming checksums, canonical JSON
hashing, null-preserving DataFrame serialization and semantic output families.
They deliberately do not invoke the V3 replacing artifact writer, spatial/context
builders, preflight, migration runner or research runner. V3 entry points and
completed artifacts remain unchanged. No second analytical store is introduced.

`config/v4/cities.json` contains independently versioned records for every city,
with source evidence paths/checksums and explicit unresolved values. The user
specified the roster, matched June 2026 target and preferred 2025 housing period;
those decisions do not establish provider availability or acquisition dates.
Copenhagen/Frederiksberg's available local V3 evidence supports municipal/district
boundaries, 30 June snapshot, DKK, EPSG:25832, the public City Hall Square anchor,
2026Q3 population, 2024 income and the KKIND5/IFOR35 local crosswalk. Differing
boundary vintages and unknown district source date are retained. Evidence reuse
is not a V4 source freeze; V3 raw paths are only read and checksum-verified.

Oslo/Stockholm now have checksum-backed 30 June snapshot and native currency
evidence (NOK/SEK). Oslo current municipal geometry is acquired but vintage is
unresolved; Stockholm municipality 0180 is verified separately from county 01,
but its geometry API returns 401. Metric CRS, public anchor,
population/income reference periods, mappings and H remain unresolved.
No Copenhagen geometry, projection, districts, decile mapping or inferred currency
is substituted. Qualification requires source evidence; edited/missing evidence
or nonmetric CRS fails validation. Housing source, frozen external reference
frame and coverage decision are unresolved for all three cities. The inherited
`income_100k_dkk` feature name is not permission to put NOK/SEK values into DKK
units; compatible source-native measurement/feature mapping must be explicitly
qualified before modelling. Mandatory no-income still includes H.

## Authoritative persistence and immutability

PostgreSQL/PostGIS remains authoritative. `.env.v4` or `V4_DB_*` environment
variables select only `thesis_accessibility_v4`. `.env`, `DB_*` and V3 schemas
are never inherited. `.env.v4.example` contains empty connection fields and no
credentials. Provision the database separately; `v4-setup` never creates or drops
production databases or changes Compose/sharing infrastructure.

The architecture migration is **023**, after the 22 verified V3 migrations;
the append-only listing/boundary audit migration is **024**.
`sql/v4_migrations/023_v4_multicity_persistence.sql` uses a separate discovery
root so `make db-migrate` cannot accidentally apply it to V3. The V4 adapter
checks database identity/absence of V3 or legacy schemas before DDL, then applies
new files transactionally under an advisory lock and a checksummed
`v4_analysis.schema_migrations` ledger. Repeat application is a no-op; changed
applied bytes or missing applied files cause failure. Append later migrations;
never change applied migrations. The baseline checker excludes only this new
V4 migration directory; all original SQL identities/checksums remain protected.

Five V4 schemas reserve raw, clean, spatial, feature and analytical identities.
Implemented tables are source manifests, observations, source-area geometry,
area context, runs, private artifacts and aggregate metrics. `v4_clean` is reserved
for later qualified cleaning; no cleaning or model algorithm is invented here.
Rows carry version, city and snapshot; run records/observations/artifacts also
carry run ID. Native source-area IDs are keyed with source ID inside their city,
snapshot and run. Observation IDs are unique within the run/city/snapshot;
repeated IDs within one batch or existing scope are errors, while the same ID
in another city, snapshot or run is independent. Outcome nulls stay null.
Model IDs include `v4_housing_standard_20261011`; bare V3 `M0` is rejected.

Source manifests and analytical records are insert-only; truncation is rejected. Completed runs cannot
be reopened, changed, appended to or implicitly resumed. Child writes lock their
parent run, serializing them with completion. Scientific run identities cannot
be updated. A changed source creates a new manifest; existing bytes/records are
never overwritten. Registration checks manifest scope, provenance and unique
source IDs. Observation/source-area source IDs must exist in that scoped manifest.
Housing crosswalks are not inferred from provider neighbourhood IDs.

Migration 024 adds an independent ingestion ledger, row-number raw/audit keys
that preserve duplicate/missing IDs, and official study geometries in EPSG:4326
with native CRS/vintage/source-area identity. No modelling run is created.
Audit children share the parent's creation transaction; after commit the entire
audit is immutable. Preliminary scopes remain frozen; acquisition evidence
selects one final audit per city, never combines duplicate snapshots.

Synthetic identities use `synthetic_v4_<city>_<UTC timestamp>`, permitted only in
an owned `test_v4_<UUID hex>` database. Research identities use
`research_v4_<city>_<UTC timestamp>` and are prohibited there. Synthetic filesystem
fixtures require a temporary root outside the project. Default tests cannot write
production namespaces. Live tests create/drop only their unique disposable
database on the audited local server, without running legacy migrations.

## Files, manifests and cache dependencies

| Purpose | Location |
| --- | --- |
| Immutable raw | `data/raw/v4/<version>/<city>/<snapshot>/<source_id>/<filename>` |
| Immutable source manifests | `data/metadata/v4/<version>/<city>/<snapshot>/<manifest_sha256>.json` |
| Intermediate inspection | `data/interim/v4/<version>/<run_id>/<city>/<snapshot>/` |
| Route cache | `data/interim/v4/<version>/<city>/<snapshot>/route_cache/<dependencies_sha256>.json` |
| Aggregate exports | `outputs/v4/<version>/<run_id>/<city>/<snapshot>/<kind>/<family>/` |
| Report receipts | `reports/v4/<version>/<run_id>/<city>/<snapshot>/` |

Paths validate components and reject traversal/symlink escapes. `write_once`
uses exclusive creation. Manifest creation verifies raw bytes and complete
provenance, including explicit source CRS (or `not_spatial`); filenames/checksums
are frozen. All raw, restricted housing, caches, credentials, dumps and private
listing predictions remain ignored. No existing files are untracked and no
sharing infrastructure is changed.

Cache reuse requires exact version/city/snapshot/purpose, scientific hash, frozen source
manifests, boundary hash, metric CRS, network hash, taxonomy hash, routing
parameters and software identity. Missing dependency keys fail; changing any
key gives a separate cache. Stored dependencies and payload hash are verified
on read. Identical content can be reused; conflicting writes cannot replace it.

Scientific dependency hashes include the scientific V4 modules, explicitly
listed reused helpers, V4 migrations, pinned requirements, actual installed
package/Python/PROJ/GEOS versions, scientific design,
selected city's versioned configuration and frozen source manifests. Acquisition
dependencies also select only that city's source policy. Reporting
code, CLI presentation, Markdown, logs and Git commit SHA are excluded. Editing
V4 documentation or another city's record does not invalidate an unchanged city
fit. New shared scientific imports must be included in the explicit dependency
list (tested); future scientific modules under `src/v4` are included automatically.
Report receipts independently hash reporting code. Reports verify scientific
identity and frozen raw hashes before exporting whitelisted aggregate metrics;
private artifact/observation tables are never report export sources.

## Implemented commands and limits

Use the existing virtual environment/Make conventions. Every operational target
requires explicit `VERSION`, `CITY`, `SNAPSHOT` and `RUN_ID`; there are no default
city or snapshot choices. For example, read-only configuration preflight:

```sh
make v4-preflight VERSION=research_design_v4 CITY=oslo SNAPSHOT=2026-06-30 \
  RUN_ID=research_v4_oslo_20261011T120000Z V4_PREFLIGHT_FLAGS=--offline
```

This date/ID illustrates command syntax, not qualified Oslo data. Expected exit
code is 2 (**BLOCKED**); no writes occur. Without `--offline`, the command also
checks the dedicated database identity, applied migration hashes and whether
the run ID already exists. Missing settings/connection/schema fail closed.

| Target | Implemented behavior / validation |
| --- | --- |
| `v4-setup` | Apply V4 migration only to an already provisioned dedicated DB; dispatch and migration success/idempotence tested against disposable fixtures |
| `v4-test` | V4 unit/specification suite; disposable-DB tests explicitly disabled |
| `v4-test-db` | Opt-in PostGIS tests in their owned temporary DB; requires current server role's CREATE DATABASE permission |
| `v4-preflight` | Read-only city/evidence/DB checks; emits explicit BLOCKED gates; offline and database-failure paths tested |
| `v4-run` | Calls the same preflight and refuses empirical work; refusal path tested, no model fitting implementation claimed |
| `v4-report` | Read-only SQL selection of completed scoped runs; immutable aggregate-only CSV/receipt export; success, incompleteness, source drift and overwrite rejection tested with temporary synthetic data |
| `v4-acquire` | Exact matched catalogue selection, immutable raw/receipt/manifest freeze and private inspection audit; no DB/model writes |
| `v4-ingest` | Dedicated V4 DB migrations and atomic immutable raw/listing/municipal audit; safe aggregate export, no modelling run |
| `v4-listing-audit` | Read-only SQL aggregate/provenance export with scope/count/hash checks; never exports listing records |

Setup/report use the same four identity variables as the example. CLI help is
`python -m src.v4.cli --help`; optional `--env` is supported for setup/report only.
The architecture step used only disposable databases. The listing step explicitly
provisioned the separate local V4 DB/private connection file and applied 023/024;
no Compose/sharing change, V3 database mutation or modelling run occurred.
Actual V4 modelling stages are future requested work. Even fully
filled city settings alone do not clear source freeze, sample/fold, coverage,
network, rank or inference gates. A city lacking qualified H remains BLOCKED;
there is no automatic no-H fallback or narrower-city scope.
