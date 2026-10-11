# V4 step log

Read this log and `IMPLEMENTATION_CONTRACT.md` at every step. Append one entry
per requested step with its scope, intended files, actual checks, blockers and
checkpoint state. Commit/push SHAs and verification are reported after the
commit outside that commit; a later entry may reference an earlier SHA.

## Step 1 — branch safeguards and repository audit

Date: 11 October 2026 (Europe/Copenhagen).

Scope: establish V4 only. No research pipeline, acquisition, migrations,
ingestion, empirical modelling or frozen-document regeneration authorized.

Branch: newly created `v4` from fetched main
`c1e919bca9dfbe89de9e67135fb432fdb0f020e6`, without moving local main or V3.
Remote: existing `origin`; URL and V3 merge evidence are in `repository_audit.md`.

Changes: retain original AGENTS.md guidance and append V4 rules; add this log,
the implementation contract, repository audit, checksum-only protected V3
manifest and a reusable safe baseline/checksum utility. Reserve separate V4
database/run/output identities without provisioning them. Require H in exactly
M0/ME/MW/MEW, preserve observed asking-price Y and separate city models.

Validation completed:

- `make compile`: passed.
- `.venv/bin/python scripts/v4_repository_checks.py --baseline-tests`: 94
  discovered, 71 passed, 23 explicitly skipped, zero failures/errors. Live DB
  and V3 integration flags disabled; candidate-export write isolated in a
  temporary directory. Existing V3 tests unchanged.
- Existing read-only input/archive/syntax functions: 204 frozen raw files,
  793 legacy files and active V3 naming/syntax passed.
- Read-only SQL baseline: all 22 applied migration hashes match source files;
  completed V3 run and five V3 schemas verified. No V4 namespace provisioned.
- Capture followed by `--verify ... --database`: all 1,696 protected file
  records and all five ordered SQL analytical fingerprints unchanged after
  baseline tests. No raw/restricted contents or row-level predictions exported.
- Five temporary synthetic guard tests passed: missing/changed files,
  added V3 files and protected symlinks rejected; V4 roots excluded; existing
  baseline capture cannot be overwritten.
- Checker AST parse and `git diff --check`: passed. Intended publication set
  is exactly AGENTS.md, the three V4 Markdown documents, the checksum-only
  manifest and `scripts/v4_repository_checks.py`; review confirms no data or
  credentials in that set.

Checkpoint state before commit: **READY_TO_COMMIT**; no step-specific blocker.
Commit and push verification are subsequent required actions, reported outside
this commit. No V4 empirical completion is claimed. H qualification and the remaining V4
scientific/implementation gates have not been evaluated and remain BLOCKED for
dependent empirical work. This documentation checkpoint does not clear them.

Requested commit: `chore(v4): establish branch safeguards and repository audit`.
Initial push must set upstream and explicitly target `refs/heads/v4` on origin;
remote HEAD equality must be reported after committing. Failure is LOCAL_ONLY.

## Step 2 — housing context standard in all four models

Date: 11 October 2026 (Europe/Copenhagen).

Starting checkpoint: `ddda2192181c112ca02aba2f7123405ea9150cff`, verified on
local/remote V4 with upstream `origin/v4`; fetched remote was unchanged and
the worktree/staging area were clean. Recorded main base remains
`c1e919bca9dfbe89de9e67135fb432fdb0f020e6`. No Git operation or worktree
conflict was present. All work in this step stays on V4.

Scope: amend the active V4 specification/configuration and consistency tests
only. No research pipeline, data acquisition, source qualification, migration,
empirical modelling or frozen V3 document regeneration.

Read the contract/audit/log and actual V3 Markdown specification/dictionary,
configuration, source-registration implementation/local manifest, candidate
freeze, inference/fold rules and both supporting V3 DOCX XML texts/addenda.
No existing V4 proposal, research plan, specification, dictionary, registry or
active V4 DOCX was found. The six new V4 Markdown documents are clearly labelled
newly authored from available evidence/user decision; no unavailable draft
contents, housing sources, values, city roster or supervisor approval invented.
No active eight-model ladder existed in the available V4 baseline to edit;
every newly established active definition uses the four required models.

Changes:

- Version `v4_housing_standard_20261011`: M0=X+H, ME=X+H+E,
  MW=X+H+W, MEW=X+H+E+W; exact inherited X/E/W, H exactly once.
- Revised RQ1–RQ4 for representation differences, accessibility information
  conditional on housing, geographic/random and cross-city differences, and
  network gains across housing contexts. Primary MEW/ME, replacement MW/ME,
  additional ME/M0, MW/M0, MEW/M0; no adding-H estimand/no-H fallback.
- Retain June 2026 target, separate city OLS/XGBoost models, observed log
  nightly asking-price Y, one housing-qualified prediction sample and matched
  folds per city. Separately document a common OLS union-of-core complete-case
  association sample; no-income reuses both samples and retains H.
- Prefer full-year 2025 apartment sale-price/m2; preserve native values and
  frozen within-city external-area `H=(midrank-0.5)/G_ref`, average tie ranks
  and equal area weighting; log native housing price is a scale sensitivity.
- Carry forward actual thresholds, all 30 frozen candidates, seeds, inference
  and mandatory no-income material-change rules. Thresholds are safeguards,
  not power guarantees. No temporal panel, residential-price outcome model,
  gentrification score or causal housing-price/displacement claim.
- Explicitly record that V3 results were already observed; no retrospective
  preregistration or supervisor approval claim. Authoritative Markdown/index
  distinguishes active V4 from preserved V3/history. No supported V4 DOCX
  workflow/file exists; V3 DOCX is superseded for V4 use, and separately held
  earlier V4 drafts are stale/superseded until a supported regeneration.
- New V4 JSON and read-only metadata utility do not alter V3 configuration,
  runners, migrations, raw data, completed outputs or historical drafts.

Validation completed:

- Targeted `test_v4_specification.py`: 11 tests passed, including versioned
  model/block uniqueness, inherited feature equality, sensitivity retention,
  forbidden-ladder/fallback rejection, contrast priorities, candidate/hash
  equality, sample/missingness rules and Markdown/index/link consistency.
- `make compile` and AST/naming checks: passed.
- `.venv/bin/python scripts/v4_repository_checks.py --baseline-tests`: 105
  discovered, 82 passed, 23 explicitly skipped, zero failures/errors, 44.410s.
  Live DB/integration flags disabled; synthetic evaluator persistence/export
  mocked and the candidate-helper export redirected to a temporary directory.
- `--verify docs/v4/protected_v3_manifest.json --database`: all 1,696 protected
  file records, 22 applied migration hashes and five SQL fingerprints unchanged;
  database checks used read-only transactions. A final filesystem comparison
  after the full suite also confirms unchanged protected V3 bytes.
- `git diff --check`, exact intended-path review and safe publication review:
  passed. Intended files are the V4 contract/log, six new V4 Markdown documents,
  `config/v4/research_design.json`, `src/v4/__init__.py`,
  `src/v4/specification.py` and `tests/test_v4_specification.py`. No raw/private
  data, credentials, V3 source edits or binary documents are staged.

Checkpoint state before commit: **READY_TO_COMMIT**, no specification-step
blocker. The subsequent commit/push/remote-SHA check is required and reported
outside this commit; it does not authorize dependent empirical work.

Empirical blockers: no qualified V4 H source/reference geography or authorized
city roster is recorded. Data/coverage/CRS/fold/sample/rank/inference gates
remain unassessed and BLOCKED. Narrower-city or descriptive-only scope requires
an explicit amendment. This specification checkpoint does not clear those gates.

Requested commit: `docs(v4): make housing context standard in all four models`.
Push explicitly with `git push origin HEAD:refs/heads/v4`, then verify remote
V4 SHA equals local HEAD and report it outside this commit. Failure is LOCAL_ONLY.

## Step 3 — isolated multi-city configuration and persistence

Date: 11 October 2026, Europe/Copenhagen. Requested scope: architecture only
for `copenhagen_frederiksberg`, `oslo`, `stockholm`; no research pipeline or
empirical run. Previous completed checkpoint is
`4fa135dfd7257c43872a9b718603d0c49d670ed9` (specification amendment), already
published on V4. Read AGENTS, contract, preserved audit, amended specification,
active documents/configuration and this log before implementation. Root is the
only applicable AGENTS file for the edited trees.

Git safety: started clean on `v4`, fetched the recorded unchanged `origin` URL,
confirmed local/remote V4 equality and recorded main base
`c1e919bca9dfbe89de9e67135fb432fdb0f020e6`. Both registered worktrees retained
their branches/HEADs; detached worktree remained clean. No staged/unrelated
work or unfinished operations were mixed in. Main/V3 were neither moved nor
pushed and no later main commits were merged. The preserved audit remains
step-1 evidence; this entry records current architecture changes.

Implemented:

- Versioned `config/v4/cities.json` with exactly the user-authorized roster.
  Copenhagen boundaries/CRS/currency/June snapshot/public anchor, population
  period and actual KKIND5/IFOR35 mappings use local checksum-backed evidence.
  Different boundary vintages/unknown district source date are retained.
  Oslo/Stockholm unknowns and all H qualifications remain explicitly null;
  validation fails rather than substituting Copenhagen assumptions. Updated
  active V4 documents/design to name the roster; scientific model/threshold/
  candidate/inference definitions are unchanged. No V3 or historical draft edits.
- Thin `src/v4` adapters reuse existing checksums, canonical hashes, semantic
  output validation and null-preserving record serialization. No replacing V3
  writer, legacy runner or scientific V3 mutator is called. Dedicated V4-prefixed
  connection settings cannot inherit `.env`/`DB_*`; database identity and absence
  of V3/legacy schemas are checked before mutations.
- New append-only migration 023 in **sql/v4_migrations**, after inspecting the
  actual 001–022 files/applied ledger. Separate discovery prevents the V3 runner
  applying it. V4 ledger uses transaction/advisory lock/checksums/idempotence.
  Creates isolated source manifests, observations, source-area geometry/context,
  run, versioned private artifacts and whitelisted aggregate metrics. Composite
  version/run/city/snapshot/source-area keys prevent collisions; duplicate IDs
  are errors. Source/analytical records cannot be overwritten/deleted/truncated;
  completed runs cannot reopen or accept writes. Child locks serialize completion.
- Scoped V4 raw/intermediate/cache/run/export/report paths, exclusively created
  source manifests and cache entries, checksum/provenance checks and traversal
  refusal. Synthetic paths require temporary roots outside the project; SQL
  synthetic purpose requires owned `test_v4_<UUID>` databases. No production
  V4 database or research run/source/output was created.
- Scientific hashes freeze selected city, design, sources, code, migrations,
  pinned requirements and actual installed Python/package/PROJ/GEOS environment.
  Reporting code, Markdown/logs/Git SHA and other-city configuration changes
  are separate. Cache keys require every documented dependency and scope/purpose;
  integrity/dependency mismatches reject reuse. Reports verify science/raw hashes
  and export only aggregate metrics, never private artifacts or observations.
- Implemented/documented `v4-setup`, `v4-test`, `v4-test-db`, `v4-preflight`,
  `v4-run`, `v4-report` in existing Make/Python conventions. Setup applies only
  to a separately provisioned V4 DB; no Compose or sharing changes. Preflight/run
  are read-only and fail closed on missing qualification and unimplemented
  empirical stages. Report's completed-run aggregate export is tested using
  synthetic fixtures; no claim of an implemented V4 fit is made.
- Extended ignore rules for V4 outputs/manifests, restricted housing, route
  caches, credentials, dumps and private listing predictions; no existing files
  untracked. Added an empty `.env.v4.example`, not credentials. Extended the V4
  baseline checker only to exclude the new V4-only SQL directory and disable
  opt-in V4 DB tests during the safe full baseline; original protected manifest
  and all applied V3 migration bytes are unchanged.

Actual validation:

- `make compile`: passed on final code.
- `make v4-test`: 33 discovered, **24 passed / 9 opt-in DB tests skipped**;
  final run 0.162s. Covers roster/evidence/null gates, absence of city defaults,
  namespace/path traversal/symlinks, immutable source IDs/checksums, every cache
  dependency/city/purpose change, scientific/reporting hash separation, shared
  scientific imports, explicit CLI selection/dispatch/refusal, and unchanged
  scientific/document-definition checks.
- `make v4-test-db`: **9 passed**, final run 1.196s. Real PostGIS migration
  first application/repeat/hash drift; duplicate listing/source-area IDs and
  city/snapshot/run isolation; scoped source registration; recorded CRS mismatch;
  outcome null preservation; conflicting record city metadata; V3 model-label/
  production-purpose refusal; completed-run update/insert/delete/truncate refusal;
  aggregate-only separated reports, overwrite/incompleteness/raw-drift rejection.
  Only uniquely owned disposable DBs were created and removed. Initial test
  failure exposed PL/pgSQL row-field resolution in a shared trigger; fixed and
  rerun successfully before any production application or published migration.
- Safe full baseline via `scripts/v4_repository_checks.py --baseline-tests`:
  **127 discovered, 95 passed / 32 skipped**, zero failures/errors, 54.281s.
  V3 live mutations disabled; candidate export redirected to a temporary directory.
  Final targeted V4/DB checks cover subsequent guard refinements.
- `--verify docs/v4/protected_v3_manifest.json --database`: **1,696 protected
  file records, 22 applied V3 migration hashes and five SQL fingerprints unchanged**,
  using read-only transactions. Final filesystem comparison after tests also
  matched all 1,696 records. No raw values or credentials published.
- Actual Make preflight (Oslo offline) and run refusal (Copenhagen offline):
  expected **exit 2 / BLOCKED**, `mutations=0`, `research_executed=false`.
  Setup/report CLI dispatch and successful migration/report functions tested;
  Make recipe wiring checked with `make -n`; production setup/report not invoked.
- Ignore probes cover private raw housing, route cache, V4 predictions,
  `.env.v4`, dumps and credential JSON; example remains trackable. Active links,
  Markdown definitions and `git diff --check` passed. Final intended-path/staged
  review passed before commit; no research/raw/private/binary outputs are staged.

Checkpoint: **READY_TO_COMMIT** for this architecture step. Dependent empirical
work is **BLOCKED**: all three cities lack qualified H; Oslo/Stockholm still lack
qualified geography/snapshot/CRS/anchor/currency/context sources; a production
V4 database/source freeze/common samples/folds and empirical stage dispatch are
not yet provisioned/qualified/implemented. These are future requested gates,
not invented substitutes or permission for a no-H/narrower-city ladder.

Requested commit: `feat(v4): add isolated multi-city configuration and persistence`.
Push explicitly with `git push origin HEAD:refs/heads/v4`; verify remote V4 SHA
matches local HEAD and report it outside this commit. Push failure is LOCAL_ONLY.
This entry does not record its own commit SHA or claim a push before it occurs.

## Step 4 — matched listings and official study-boundary audit

11 October 2026, Europe/Copenhagen. Starting published V4 checkpoint:
`8396046e60081604d539d83ff600198b23ea512f`. Read root AGENTS, contract,
repository audit, amended specification, dictionary, source registry/configuration
and this log. Initial worktree/staging area was clean; fetched recorded origin,
confirmed local/remote V4 equality, recorded main base and expected ancestry.
Both worktrees and main/V3 identities were preserved. No unrelated work or
unfinished Git operation was mixed in. No raw source, applied migration,
completed V3 output or historical document was replaced or regenerated.

Scope: acquisition/ingestion audit only. No research model fitting, pipeline,
housing assignment, prediction/OLS sample freeze, income mapping, analysis-area
assignment or accessibility construction. The four housing-required model
definitions, contrasts, thresholds, candidates and inference rules are unchanged.

Implemented/acquired:

- `src/v4/listings.py` reuses the actual six-type V3 constant and strict observed
  price parser, checks the exact official catalogue/archive selection, freezes
  raw receipts/manifests exclusively and audits schema, ID uniqueness, prices,
  native quote currency, scrape/batch dates, quoted stay and municipal geometry.
  The actual Python and SQL dwelling rules match the user's request exactly;
  no primary review/activity threshold was introduced. The initial V3 geography
  lookup discrepancy and V4 official-geometric audit are documented before
  ingestion in `listing_acquisition.md`.
- Official 30 June 2026 archive entries found for all three cities. Copenhagen
  verified/reused at SHA `d0c81b5c30c0fa48ca2e77005d6e8418c6f491ee4af8dbac881ff7f5fd01ff71`;
  unchanged bytes copied to V4 with original acquisition provenance. Oslo and
  Stockholm downloaded from the exact official selected URLs, HTTP 200, with
  hashes `2a3c604bb3113e04e65ff4573cfe7ee23b0015a0d04bc824b761c2a1b85add2c`
  and `6d0ff60954da6e05b73ed741fe7ebbff5b57fe3b18acf4696acf5b824e4e6d6f`.
  All three schemas have the same 90 detailed columns. No latest substitution,
  inherited sample-count assumption, price imputation or raw-row publication.
- Raw/dwelling/positive counts: Copenhagen 23,144 / 21,080 / 12,521;
  Oslo 13,391 / 11,776 / 8,557; Stockholm catalogue extract 4,806 / 3,834 /
  2,510. Missing-price eligible rows 8,559 / 3,219 / 1,324 remain in the audit.
  Final audits have zero invalid/duplicate records and zero nonpositive eligible
  parsed prices. These are source audits, never qualified model-sample sizes.
- Copenhagen + Frederiksberg municipal geometries reused at original hashes,
  vintages 27 March 2026 and 16 January 2024. District evidence moved to a
  separate inherited analysis-area-source node; provider neighbourhood labels
  and future housing-native areas remain separate, with no invented assignment.
  Oslo Kartverket municipality 0301 geometry acquired with explicit EPSG:4326,
  checksum `864c039bfaf1890460f8859865a489009a4ccbe64bbcd7c962abb59735f880fb`.
  Oslo geometry vintage is explicitly unknown/current at retrieval, blocking
  temporal qualification. Stockholm SCB registry confirms municipality 0180
  in county 01; Lantmäteriet municipal items probe returns **HTTP 401**. No
  authentication bypass, county/neighbourhood substitution or simplified SCB
  thematic geometry (explicitly unsuitable for analysis) is used. Stockholm
  municipal inside counts are NULL. Inside dwelling/positive counts are 12,508
  Copenhagen/Frederiksberg and 8,557 Oslo, subject to the recorded vintage gate.
- Native quote currencies independently confirm DKK/NOK/SEK and the official
  dictionary defines price in local currency. The literal export dollar symbol
  is a numeric-format artifact, never USD conversion. Actual scrape dates are
  30 June–4 July Copenhagen, 30 June–3 July Oslo and 30 June/3 July Stockholm;
  requested quoted-stay endpoints extend through 3 July 2027. All returned
  dates/date_match values are NULL, not proof of a matched returned stay.
  Flattened requested dates and observed/flattened nightly prices agree. Nested
  rate rounding differences (3,556 / 2,369 / 793) are within half a native cent,
  compared with Decimal strings; no alternative amount replaces the outcome.
- Provisioned only `thesis_accessibility_v4` on the audited local server and an
  ignored owner-only `.env.v4`, refusing any existing DB/config takeover. Applied
  unchanged architecture migration 023 plus new append-only 024. No V3 schema
  mutation, Compose/sharing change or credential publication. Raw/audit keys
  preserve all rows (including invalid/duplicates in fixtures); committed audits
  reject further inserts/updates/deletes/truncates. Audit ledgers are independent
  of H-gated modelling runs. The V4 modelling-run count is **zero**.
- Explicitly selected immutable ingestion IDs end in **20261011T143812Z**,
  one per city. Earlier audits at 141934Z, 142446Z and 142610Z remain immutable and are
  superseded for this checkpoint, not summed or treated as additional snapshots.
  This preserves all provenance of audit refinements without overwriting rows.
- Implemented/tested `v4-acquire`, `v4-ingest`, `v4-listing-audit`; SQL-derived
  public evidence uses a whitelist/count/hash check and is reviewed in
  `listing_acquisition_audit.json`. Raw rows/coordinates/host information/private
  outputs and connection credentials remain ignored. Active V4 Markdown/index,
  snapshot/currency configuration and selected-city scientific dependencies
  updated. Reporting/log/Markdown edits remain outside scientific hashes.
- Full baseline exposed V3 source discovery scanning the reserved V4 directory.
  The sole legacy compatibility edit excludes precisely `data/raw/v4` from
  legacy registration; unknown legacy providers still fail. Regression tested
  with temporary fixtures. Existing V3 entry points/scientific filters and all
  V3 source checks retain their behavior for V3 inputs.

Actual checks:

- `make compile`: passed on final code.
- Final safe baseline `scripts/v4_repository_checks.py --baseline-tests`:
  **140 discovered, 105 passed / 35 explicitly skipped**, zero failures/errors,
  70.273s. Live V3 integration and production mutation flags disabled; candidate
  export redirected to a temporary directory. Synthetic model fixtures are
  tests only. Initial baseline discovery error resolved by the narrow namespace
  exclusion, then full suite rerun successfully.
- Final V4 targeted suite: **46 discovered,
  34 passed / 12 opt-in DB skipped**. The full baseline includes the added
  namespace test, Decimal rounding regression and all active definition tests.
  Final review also added non-object quote JSON to the schema-failure cases;
  the targeted suite passed after the guard refinement and real sources were
  re-audited under the final adapter checksum with identical source/count evidence.
- Final `make v4-test-db`: **12 passed**, 1.498s, in a fresh owned temporary
  PostGIS DB. Tests migration idempotence/hash drift, city/run/snapshot isolation,
  duplicates and NULL outcome preservation, source/CRS identities, committed
  audit/fit immutability, late-row refusal and safe public export/overwrite refusal.
  Initial synthetic fixture/savepoint issues were corrected and retested before
  production application. One interrupted synthetic fixture DB was explicitly
  removed by its known owned name after confirming no active connections;
  final count of remaining disposable test DBs is **zero**.
- Acquisition and ingestion/export main entry points exercised on real scoped
  sources: Copenhagen acquisition/ingestion audit succeeds; Oslo/Stockholm emit
  the expected **exit 2 / BLOCKED**, retaining real audit rows and exact source
  failures. Missing Swedish access does not invent observations or municipal
  coverage. Independent SQL selected-row counts match all three aggregates;
  public evidence matches the exact ingestion-code SHA/schema/currency/date audit.
- V4 production migration repeat returned `[]`; recorded 023/024 hashes match
  files. Offline Oslo preflight remains **BLOCKED**, `mutations=0`,
  `research_executed=false`. No research runner or model fit was invoked.
- `--verify docs/v4/protected_v3_manifest.json --database`: all **1,696 protected
  files, 22 applied V3 migration hashes and five SQL fingerprints unchanged**,
  read-only. Final filesystem comparison follows all tests. Ignore probes verify
  raw V4 listings, local `.env.v4` and private reports are excluded. Diff/staged
  path and safe-publication checks are required before commit.

Checkpoint: **READY_TO_COMMIT — BLOCKED DATA QUALIFICATION**. This safe
acquisition/blocker checkpoint fulfils the authorized adapter/audit work but
does not clear Stockholm geometry access/selection/licence/vintage, Oslo vintage,
new-city projected CRS/anchor/context or any city's H/sample/fold gates.
No narrower-city/descriptive modelling scope or no-H substitute is authorized.
Exact source links, retrieval timestamps, licences, hashes, selection and local
locations are in the safe audit. No supervisor approval/preregistration invented.

Requested commit: `feat(v4): ingest matched city listings and study boundaries`.
Push `HEAD` explicitly to `refs/heads/v4` on recorded origin and verify remote
SHA equals local HEAD after commit; report outside this commit. Failure is
LOCAL_ONLY. This entry does not record its own commit SHA or claim a future push.

## Step 4 targeted Stockholm recovery — 11 October 2026

Scope: user-authorized evaluation of SCB RegSO 2025 as an operational Stockholm
municipal boundary substitute; no later steps, feature/housing assignments or
model fits. Read AGENTS, contract, repository audit, active specification,
listing acquisition, source policy/registry, receipts, ledger and tests. Sole
recorded origin fetched; local/remote V4 both started at
`7256241cf26802a015673b247fdfb627a4ba6589`, with the recorded main base in ancestry,
clean tracked/untracked/staged state and no unfinished Git operation. Existing
worktrees/remotes were preserved; no main/V3 branch change.

Outcome: Stockholm listing-boundary acquisition is
**RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT**. The dated
[source amendment](stockholm_boundary_amendment_20261011.md) and separate
`stockholm_boundary_amendment_20261011_audit.json` hold the evidence. Original
Lantmäteriet HTTP 401 receipt, all earlier ledgers/NULL counts, previous public
listing audit and private frozen exports remain unchanged. Airbnb was not
downloaded again. Existing 023/024 migrations/storage were sufficient; neither
migration was edited and no new migration was necessary.

Verified source: official SCB page-linked WFS GeoPackage, CC0, actual layer
`RegSO_2025`, geometry column `sp_geometry`, native EPSG:3006, version `2025_v2`,
reference 2025-01-01. Retrieved 2026-10-11T15:03:48+00:00; GeoPackage SHA256
`df9bb507bb360020885b47620a5e7bba6c633322236ddaf32ff2a20935c58a5a`.
Actual `kommunkod=0180` selects 127 unique valid polygons; county 01 is only
a consistency check. Dissolve: valid, nonempty, one component, zero holes,
zero measurable overlap, complete selected coverage, zero adjacent municipal
intersection area. Area 215.75729922473672 km² agrees with independently
published official 2025/2026 municipality totals to 0.77526328 m², within the
50 m² source rounding interval. Reviewed municipal-change sections of three
official 2025/first-half-2026 notices; no municipal entries, distinct from the
Stockholm parish merger. Accepted as SCB-derived **2025 operational geometry**,
not exact certified Lantmäteriet June 2026 linework. Bounds/vintage limitations
and the authenticated import option are explicit in the amendment.

New immutable ingestion: `research_v4_stockholm_20261011T151637Z`, in the dedicated
PostgreSQL/PostGIS V4 database. Manifest:
`d1d923db415dbf2218560947e3fd862657e343317f36fee284fa36e36cc0d172`, combining
eight existing verified source records and 12 separately identified SCB sources.
Reuse existing acquisition, manifest, listing-audit and insert-only persistence
functions. New explicit `v4-stockholm-boundary` command and pinned policy prevent
silent substitution/reopening. Source-amendment policy participates in Stockholm
scientific dependencies; reporting/Markdown/log edits remain excluded.

Computed raw/dwelling/positive-price counts **4,806 / 3,834 / 2,510**, all inside
the operational union, **0 outside**, invalid/duplicate/unclassified **0**.
Preserved eligible missing-price records **1,324**, nonpositive **0**.
Within 150 m of dissolved exterior rings in EPSG:3006: **96 / 69 / 49** for the
same universes, all on the inside side. Membership remains covers in EPSG:4326;
PostGIS independently reproduced inclusion and distance indicators and aggregate
counts. The diagnostic excludes no listings. Official analysis/native housing
IDs remain NULL on every row; RegSO components are not inferred clusters or H
areas. Raw GeoPackage/receipts, private coordinates/rows/exports and credentials
remain ignored. The public JSON is exactly the whitelisted SQL export.

Actual checks:

- `make compile`: passed.
- `make v4-test`: **53 discovered, 40 passed, 13 opt-in DB skipped**, zero failures.
  Six new boundary unit tests cover municipality-versus-county selection,
  vintage/CRS/schema/ID and topology failures, no repair/fallback, exact municipal
  area metadata, dissolve/exterior-distance behavior and scientific policy hashes.
- `make v4-test-db`: **13 passed**, 1.329 s, fresh owned disposable PostGIS DB;
  temporary synthetic sources only. Covers qualified boundary ingestion, parent
  receipt and ledger preservation, append-only recovery, SQL covers/distance and safe
  export, refusal to reopen and normal migration/isolation guards. Initial new
  fixture distance and integer-versus-JSON key assertions were corrected and
  the full disposable suite rerun successfully. Remaining disposable DBs: zero.
- Safe `scripts/v4_repository_checks.py --baseline-tests`: **147 discovered,
  111 passed, 36 explicitly skipped**, zero errors/failures, 62.600 s. Live V3
  mutation flags disabled and candidate export isolated in a temporary root;
  synthetic evaluation fixtures are tests only, not research results.
- `--verify docs/v4/protected_v3_manifest.json --database`: **1,696 protected
  V3 files, 22 applied migration hashes and five SQL fingerprints unchanged**,
  read-only. No V3 regeneration command was invoked.
- Original **45** inventoried V4 frozen files/receipts/manifests/private exports
  unchanged. Original **12** ledger summaries/manifests have unchanged ordered
  SHA256 `2f4341a739750a46faea65b05cd59c7776dc7d115acdcc63161609e966f19acb`.
  There are now 13 immutable ingestion ledgers and **zero modelling runs**.
  All 20 amended source hashes and 12 new receipt hashes match; public export
  matches its recorded recovery-code/policy checksums and SQL export bytes.
- Actual `make v4-stockholm-boundary` ingestion and `make v4-listing-audit`
  export entry points passed under the recorded new identity. Read-only SQL
  verifies valid/nonempty stored geometry, SRID 4326/native EPSG:3006/reference
  2025-01-01, unchanged 023/024 hashes and zero analysis/housing assignments.
  Ignore probes and `git diff --check` pass; final explicit staged-file review
  is required before commit.

Stockholm's listing-boundary prerequisite is cleared for a separately requested
Step 5; none was executed or authorized here. Housing-price qualification and
modelling remain **BLOCKED**, as do Stockholm's general metric CRS/anchor/context
sources and Oslo's separate vintage issue. No automatic no-H ladder, narrower
city scope, supervisor approval or retrospective preregistration is introduced.

Checkpoint: **READY_TO_COMMIT — STOCKHOLM BOUNDARY RESOLVED WITH AMENDMENT**.
Intended safe files: Makefile; `config/v4/cities.json` and
`config/v4/stockholm_boundary_amendment.json`; `src/v4/stockholm_boundary.py`,
`src/v4/reporting.py`, `src/v4/identity.py`; the four V4 architecture/listings/
persistence/Stockholm-boundary test files; V4 contract, document index, active
specification, source registry, listing acquisition, step log, dated amendment
Markdown and its safe aggregate JSON. No raw/private source file is staged.
Requested commit: `fix(v4): resolve Stockholm boundary via audited SCB geometry`.
Push HEAD explicitly to recorded origin `refs/heads/v4` and verify remote/local
SHA equality after committing; report outside this commit. Push failure means
LOCAL_ONLY. This entry does not record its own commit SHA or claim a future push.

## Step 5 — housing sources and explicit qualification gates, 11 October 2026

Requested scope: the attached Step 5 instruction, read together with AGENTS,
this contract/log, active V4 specification/dictionary/source register, repository
audit and listing acquisition/boundary amendment. This step authorizes public
source discovery/acquisition and standalone source QA only. No Step 6, listing H
assignment/ranking, sample construction, walking features, model fitting or
empirical comparison was executed. Primary definitions and prospective
safeguards remain unchanged; V3 results were already observed.

Initial Git safety: clean `v4`, local/fetched origin at
`92f607be0ed44db6746bf4b09d2bebe023d6cde3`; recorded main base
`c1e919bca9dfbe89de9e67135fb432fdb0f020e6` retained. Sole configured remote is
the recorded origin; no remote URL, main/v3, tag, detached worktree or existing
commit changed. No unrelated work or unfinished Git operation was mixed in.

Acquisition: 15 candidate-source comparisons, 43 immutable new receipts,
40 acquired files (including metadata), three preserved Danish HTTP failures.
Six actual statistical extracts: Finans Danmark BM011 and BM021 2025 Q1–Q4
CSV, Oslo BOL018 2025 JSON-stat2, SSB 14545 Oslo 2025 JSON-stat2, SCB TAB1151
historical bulk CSV ZIP with 2025 cells, SökHem rolling municipal sold JSON
updated through 10 October 2026. Official Oslo geographic hierarchy XLSX,
municipal Danish housing reports and definitions/access evidence also frozen.
Anonymous public POST queries reuse the existing acquisition adapter, with
query hashes and immutable receipts. No authenticated access, contract
acceptance, application, purchase, raw redistribution or listing redownload.

Findings and city gates:

- Copenhagen/Frederiksberg: 605 national native postal groups × four quarters,
  2,420 source rows. Price cells: 464 positive, 529 NULL, 1,427 reported zero;
  every zero-price cell has zero reported sales. Seventeen NULL-price cells
  have at least five reported sales. Preserve native evidence; do not infer
  exact filtered price denominators from BM021 counts or construct an annual
  mean. Copenhagen and Frederiksberg source labels are present, but this is
  not a municipal reference frame or joined coverage. Annual construct,
  reusable-data permission and current native postal geometry/crosswalk remain
  BLOCKED. Both documented DAWA municipal queries returned HTTP 410. The DST
  anonymous documentation responses are outage notices, not successful metadata.
- Oslo: BOL018 annual 2025 apartment mean price/m² and counts acquired under
  the public platform's documented NLOD 2.0 evidence. Actual source codes are
  distinct from API category positions. The 452 rows include 17 bydeler, 98
  delbydeler (2017), 336 grunnkretsområder and unresolved native code 100000.
  Positive price/≥20-sales support is 16, 92 and 245 respectively; these nested
  counts are not added. Fourteen unavailable mean cells retain NULL/dash.
  PRELIMINARY_QA_PASSED; PROVISIONAL_BOUNDARY. Source-matching polygon vintage,
  municipal boundary vintage, reference-frame choice and joined support remain
  unresolved. No Step 4 boundary rewrite. SSB's one municipal unit is a
  supplementary alternative, insufficient as neighbourhood H.
- Stockholm: acquired SCB 2025 counts/total transaction price across 26 regional
  units, not neighbourhood price/m². Acquired CC BY 4.0 SökHem rolling municipal
  export (181 rows; 47 missing slugs, 134 unique valid slugs, no duplicate valid
  slug), not full-year 2025 neighbourhood apartment data. These are acquired
  alternatives, zero parsed target housing rows; this does not mean zero real
  transactions or zero missing data. Public Mäklarstatistik export/history
  facilities were inspected, but no download accepting contractual terms was
  made. Prepare unsent permission requests. The SCB-derived municipal mask
  remains resolved; native housing sources/areas remain independently BLOCKED.

All final H/model gates are BLOCKED. Joined listing coverage, represented areas,
housing-group support and external reference frame remain NULL/unfrozen.
Preferred 20 annual sales, 10 usable areas, 80% coverage and four areas/100
listings per group are unchanged project safeguards, not power guarantees.
Step 6 is partially ready at Oslo source-input level; a qualified three-city
workflow is BLOCKED by the exact source/legal/geographic dependencies above.
No subsequent work is authorized by this safe checkpoint.

Implementation: `src/v4/housing.py` reuses Paths/Scope/acquire/freeze/persistence;
native schema/period/category/unit checks, explicit missingness, source-hash
changes, geographic code preservation, mathematically restricted annual-mean
helper, separate preliminary/final gates, safe exports and immutable reruns.
Scientific hashes include selected-city housing policy; Markdown/log/reporting
and unrelated-city changes do not invalidate unchanged scientific dependencies.
New append-only migration **025_v4_housing_source_audit.sql** creates dedicated
insert-only source-audit parents/children, independent of listing/model runs.
No applied migration was edited. Documentation provides the source comparison,
cross-city matrix, geographic dependencies and exact unsent access/import
requirements. All raw files/receipts/private values remain ignored and unstaged.

Actual new immutable housing-audit ingestions (same target snapshot 2026-06-30):

| City | Run ID | Native source rows |
| --- | --- | ---: |
| Copenhagen/Frederiksberg | `research_v4_copenhagen_frederiksberg_20261011T172619Z` | 2,420 |
| Oslo | `research_v4_oslo_20261011T172619Z` | 452 |
| Stockholm | `research_v4_stockholm_20261011T172619Z` | 0 target rows; alternatives preserved |

Authoritative PostgreSQL aggregates independently match frozen source QA.
Exact manifests/URLs/timestamps/SHA256 and statuses are in
`housing_acquisition_audit.json`. Actual commands: `make v4-setup` applied only
025; a second migration application returned no changes. For each city,
`make v4-housing-acquire`, `make v4-housing-ingest`, `make v4-housing-audit`
were executed with these explicit identities. Expected exit 2/BLOCKED records
the final gate, while preserving successful acquisition/persistence. Audit
reruns compare identical existing export bytes. Each ingestion rerun refuses
reopening before acquisition. No model run was created.

Actual validation:

- `make v4-test`: 67 discovered, 51 passed, 16 opt-in DB tests skipped.
- `make v4-test-db`: 16/16 passed in owned disposable PostGIS databases,
  including migration idempotence/applied hashes, duplicate/native ID and city
  isolation, NULL preservation, independently computed SQL support counts,
  immutable parent/late-child guards, output privacy and source separation.
- `.venv/bin/python scripts/v4_repository_checks.py --baseline-tests`:
  161 discovered, 122 passed, 39 opt-in database/integration tests skipped.
  Candidate-helper writes redirected to temporary storage, no V3 regeneration.
- `make compile`: passed. `git diff --check`: passed.
- Read-only protected verifier: all 1,696 V3 files, 22 applied migration hashes
  and five ordered analytical SQL fingerprints unchanged.
- Before/after hashes: all 108 prior local V4 source/manifest/export files
  unchanged; all 13 original listing-ingestion summaries/manifests unchanged
  using the pre-step canonical sequence-row SHA256. Zero empirical model runs
  and zero listing H/native housing assignments. Source and receipt pins
  verified on cached acquisition rereads.

Stage only the intended V4 adapter/config/Makefile/new migration/tests and safe
Markdown/aggregate/metadata registry documents. Requested commit:
`feat(v4): add housing sources and explicit qualification gates`. Push HEAD
only to recorded origin `refs/heads/v4` and verify equality after committing;
report the SHA/push outside this commit. This entry does not record its own
commit SHA or claim a future push. Push failure means LOCAL_ONLY.

## A01 — accessibility-only scope amendment, 11 October 2026

Latest researcher request replaces the housing-inclusive V4 scientific scope.
Active design: **v4_accessibility_only_20261011**; exactly M0=X, ME=X+E,
MW=X+W, MEW=X+E+W. Y remains log original positive observed Airbnb nightly
asking price, separate native-currency city models. Retain inherited listing/
host/amenity controls, density, qualified income, centrality and matched no-income
robustness. Income is distinct from residential prices. RQ1–RQ3 concern matched
measurement, predictive information and cross-city/validation stability; housing
RQ4 is withdrawn. All five paired contrasts remain, including explicit MEW/ME
add-on reporting relative to v3's four named contrasts. V3 results and housing
feasibility were already known. No supervisor approval or retrospective
preregistration is asserted.

Scope: A01 documentation/current-state reconciliation only. Read applicable
root AGENTS (no ancestor/nested override), original contract and entire step log,
active V4 documents, actual V3 specification/deviations/model registry, listing
acquisition, dated Stockholm amendment, housing acquisition/access requirements
and supplied revision bundle. No A02 executable refactor, acquisition, ingestion,
migration, provider message/application/contract, route building, assignments,
samples/folds or empirical fit. Synthetic fixtures remain tests only.

Git entry state: existing `v4`, local/fetched origin both
`25d60d36ef6d6359fbad74c20bc40c48764b7691`, the housing-source checkpoint,
not the earlier Stockholm recovery tip. Recorded main/base
`c1e919bca9dfbe89de9e67135fb432fdb0f020e6` retained; no divergence or unfinished
operation. Only untracked input was the specifically authorized revision bundle;
no unrelated tracked/untracked or staged work. Existing remote URL/worktrees and
main/v3 identities unchanged. No reset/rebase/stash/merge or history rewrite.

Imported bundle: **25 delivered files plus file_manifest.json**, every size and
SHA256 verified. Preserve exact supplied bytes, including two reference Word
exports; inspect their document XML/design stamps and package membership. Their
exports are stale/superseded for reconciled active Markdown, not regenerated.
No supported V4 Word workflow exists; V3 `make income-docs` was not run. The
live V3 results ZIP matches supplied input hash. The bundle cites an older
listing-acquisition hash; actual preserved Markdown and selected live SQL counts
are explicitly reconciled in `current_state_audit_20261011.md`. Some external
literature/draft files were not located; no inaccessible content or fresh
literature verification is invented.

Changes: amend active proposal, end-to-end plan, pre-analysis specification,
dictionary, model/execution contract, source/dependency registry, architecture
status, document index and AGENTS pointer. Create explicit model contract,
documentation-only scope decision JSON, live current-state/dependency audit and
old-to-new A01–A12 step mapping. Preserve exact before-A01 bytes of eight active
documents plus AGENTS in a dated historical snapshot/checksum manifest, and
preserve all previous step-log entries. No global replacement across history.

Retire housing/provider acquisition and unsent access requests, price-qualified
samples, sale-count/coverage/area thresholds, housing-area folds/ranks/log-H
sensitivities and subgroup analysis as **NOT_REQUIRED_SCOPE_AMENDED** for the
new design. Historical final BLOCKED and Oslo preliminary source statuses remain
unchanged. All unexecuted old housing prompts, especially old Step 6 and its
dependent sample/fold/subgroup instructions, are superseded. A02–A12 are mapped
future checkpoints, not simultaneously authorized work.

Actual runtime/config/code and applied SQL still encode
`v4_housing_standard_20261011` in `research_design_v4`: canonical model registry,
city housing prerequisite, log-native-H scenario, old model-ID SQL constraints
and housing source/module scientific hashes. These remain intentionally intact
pending separately requested A02. A01 does not fake housing approval, weaken
readiness, relabel rows or claim a new executable registry/preflight exists.
Documentation/Git changes leave legacy scientific hashes unchanged for all cities.

Explicit baseline discrepancy: executable v3 and frozen prior V4 X include
categorical `property_type`; supplied revision prose excludes it. The researcher
was asked to resolve that difference. Without clarification, final categorical
membership is pending A02/pre-fit resolution rather than silently changed. All
17 inherited numeric/amenity/context controls remain required. This open decision
is distinct from H removal and is recorded in the active model contract/dictionary.

Live source counts, read from selected immutable SQL scopes:

| City | Raw | Dwelling | Positive dwelling | Inside mask + positive |
| --- | ---: | ---: | ---: | ---: |
| Copenhagen–Frederiksberg | 23,144 | 21,080 | 12,521 | 12,508 |
| Oslo | 13,391 | 11,776 | 8,557 | 8,557 |
| Stockholm | 4,806 | 3,834 | 2,510 | 2,510 |

These are acquisition counts, not S_pred/S_assoc. Select original Copenhagen/
Oslo `20261011T143812Z` ingestions and amended Stockholm `20261011T151637Z`
by their exact manifest hashes; never add superseded audits or duplicate imports.
Missing-price dwellings and quote/date/currency limitations remain visible.
Stockholm's accepted SCB-derived 2025 operational mask and original 401/NULL
ledger remain unchanged. RegSO components are not automatically analysis areas.
Oslo municipal vintage remains BLOCKED; new-city analysis/context/metric-CRS/
anchor/density/income and matched-source/network/sample/fold qualification still
require A03–A07. No city omission or income fallback is silently activated.

Actual relevant validation (tests unchanged):

- Temporary A01 documentation checks PASS: exact four-model tables/IDs,
  retained inherited candidate-field names/E/W, retired-dependency statuses,
  all active local links, nine exact historical snapshots and unchanged legacy
  scientific hashes. No new executable readiness is claimed.
- `make v4-test`: **67 discovered; 48 passed, 16 opt-in DB skipped, three
  failing methods with eight assertion failures**. Expected scope mismatches:
  `test_active_markdown_definitions_match_machine_configuration` still asserts
  housing-standard active Markdown/RQs; `test_dictionary_lists_every_actual_feature_and_model_versions`
  requires discontinued H; `test_active_links_resolve_and_docx_status_is_explicit`
  forbids any V4 Word file despite authorized imported reference exports.
  All links independently pass. These methods are pending proper A02 version/
  document-scoping updates, not suppressed, weakened or falsely passed.
- Safe `scripts/v4_repository_checks.py --baseline-tests`: **161 discovered;
  119 passed, 39 skipped, the same three methods/eight assertion failures**.
  Candidate export isolated in temporary storage; live V3 mutations disabled.
  No extra failure outside the documented scope/document mismatches.
- `make v4-test-db`: **16/16 PASS**, owned disposable PostGIS databases only;
  preserved migrations/identity/immutability/source/audit/aggregate guards tested.
- `make compile`: PASS. Tracked live-document `git diff --check`: PASS.
  Staged `git diff --cached --check` returns exit 2 solely for three original
  Markdown two-space hard breaks: supplied plan lines 7/8 and proposal line 9.
  These are reviewed intentional source formatting, preserved to keep the
  imported manifest hashes unchanged; no check or hook is bypassed. No other
  staged whitespace diagnostic occurs.
- Read-only protected verifier: **1,696 V3 files, 22 applied migration hashes
  and five analytical SQL fingerprints unchanged**.
- All **199** preexisting V4 raw/receipt/manifest/export file hashes unchanged;
  all **13 listing ledgers, three housing ledgers, eight registered source
  manifests and three V4 applied migration records** unchanged by ordered hashes.
  **92** registered source byte checks and **43** housing receipt pins PASS;
  original Stockholm 401 receipt unchanged. Zero empirical model runs and zero
  new official/native housing-area assignments. No source re-download/import.

Checkpoint: **PARTIAL — A01 documentary scope adopted; executable/scientific
readiness BLOCKED pending A02 and genuine per-city dependencies**. The baseline
membership discrepancy remains explicit until answered. This safe checkpoint
does not authorize the next A-step. Stage only active/history/imported V4 safe
documents and AGENTS; no source code/configuration/test/migration bytes changed,
no raw/private/credential/individual-row file staged. Requested commit:
`docs(v4): amend scope to three-city accessibility only`.
Push HEAD explicitly to recorded origin `refs/heads/v4`, verify remote/local SHA
after committing, and report outside the commit. No own commit SHA or future
push success is recorded here; push failure means LOCAL_ONLY.

## A02 — remove housing from active pipeline, 11 October 2026

Current user request separately authorizes A02 only. Existing `v4` branch at
entry/fetched origin `f5a6913c362ebaef01d828baf778164c538626cd`, clean worktree,
no unrelated edits/staging/unfinished operations/divergence. Recorded origin
URL/base/main/v3/worktree references retained. Read applicable root AGENTS,
contract/log, active design/model/A01 audit and revised supplied proposal/plan,
actual V3 feature registry, V4 code/config/SQL constraints/runners/tests/Makefile.
No new acquisition, provider contact, Airbnb download, routing, sample/fold
construction, estimator implementation or empirical fit occurs in this step.

Canonical active design: **v4_accessibility_only_20261011**. Exactly M0=X,
ME=X+E, MW=X+W, MEW=X+E+W; no H/residential-price/rent proxy in primary or
required no-income features. No no_housing/log-native-H variant. Retain all
17 inherited numeric/amenity/context controls plus categorical `property_type`.
The A02 instruction to remove only housing-derived dependencies resolves A01's
baseline discrepancy by retaining the actual V3 categorical control, explicitly
superseding the supplied prose exclusion. The supplied bundle stays unchanged.
Y remains log original positive observed nightly Airbnb price; no filling or
quote substitution. Exact candidates, seeds, thresholds, no-income material-
change rules, separate cities/engines/validation and five contrasts retained.

Changes: separate active research-design/city/reuse-policy JSONs; canonical
specification registry, housing-free scope check and read-only source reuse;
version-aware city/identity/runtime/persistence/CLI/report adapters; append-only
migration 026; scope/version/source/upgrade tests; active documentation/status/
index/AGENTS pointer and this log. Old research/city/housing/source policies and
all acquisition adapters stay byte-for-byte intact. The original specification
module is preserved byte-for-byte as `src/v4/historical_specification.py`; old
model/source assertions remain executed under their explicit historical scope.
No globally disabled preflight or historical test and no fake H qualification.

Retirement trace is in `pipeline_scope_audit_A02_20261011.md`: H-qualified
samples/non-null housing joins, annual sales/80% coverage/native-area minimums,
reference ranks/H-safe folds/H-group support and housing-source/module/migration
scientific hashes are absent from active dependencies. Historical source audits
remain BLOCKED/preliminary exactly as recorded; retired requirements are
NOT_REQUIRED_SCOPE_AMENDED. Ordinary geographical support, analysis/context
qualification, price integrity and missing/invalid required feature checks stay.
There was no completed V4 H/sample/fold/model output to relabel or regenerate.

Approved source hashes select the original Copenhagen/Oslo listing runs and
amended Stockholm run exactly as A01 recorded. Explicit `--source-manifest`
checks SQL identity/purpose/manifest/raw checksums read-only; audit SQL selects
only whitelisted private listing fields and all rows, including missing prices
and NULL area assignments. Housing fields never become an INNER JOIN/WHERE
filter. Design changes create no duplicate ingestion. New analytical output/
cache identities include design_id; raw/manifest locations are unchanged.
Historical acquisition metadata envelopes and report paths remain unchanged;
existing acquisition Scope default remains historical; analytical CLI explicitly
selects the new design. Reporting uses safe aggregate dimensions and refuses a
selected design different from the completed run. Scientific/reporting/log hashes
remain separated; housing-policy changes no longer invalidate the new design.

Migration **026_v4_accessibility_only_definition.sql** is the next actual
migration after 025. Tested in owned disposable PostGIS databases, then applied
through `make v4-setup` to dedicated `thesis_accessibility_v4`, with only 026
reported newly applied. Applied hash:
`57031e2bb082f5dd2e5ec1733d1a0db82a0a014a52ffe09a27abeaceb79a46c7`.
No applied 023–025 bytes/records changed. Schema extends allowed design/model
IDs, parent-design guards and separate artifact estimator/validation keys;
derived model/sensitivity/design dimensions are views, without backfilling old
completed rows or inventing old estimator/validation metadata. All old
append-only/completed/source/purpose/truncation guards remain active.

Actual final relevant checks:

- `make v4-test`: **81 discovered, 62 PASS, 19 opt-in DB skipped**, exit 0.
- `make v4-test-db`: **19/19 PASS**, exit 0; owned disposable UUID databases.
  Upgrade preserves a committed completed historical run/record and its guards;
  tests cover migration idempotence/hash rejection, model/engine/validation/
  sensitivity isolation, conflicting artifact metadata, cross-design completion/
  report/write refusal, all-row read-only source reuse and NULL housing fields,
  bad hash/city/source bytes, duplicates/immutability/privacy and unchanged
  historical housing adapter/receipt behavior.
- Safe `scripts/v4_repository_checks.py --baseline-tests`: **175 discovered,
  133 PASS, 42 opt-in skipped**, exit 0; temporary candidate export, live V3
  mutation flags disabled. Historical registry/Markdown assertions now target
  immutable historical material; active checks target the new scientific scope
  and exact supplied reference DOCX inventory. A01's three failing methods are
  properly scoped and now pass, without suppressing historical tests.
- Housing-free synthetic scope tests pass with no housing files and absent/NULL
  housing-area fields, no row filtering or filling. Invalid original prices,
  log-price mismatches, IDs, geographic/context/support failures and entirely
  missing/nonfinite required predictors still BLOCK. A passed scope check is
  explicitly not empirical readiness or research data.
- `make compile` and tracked/staged `git diff --check`: PASS.
- Supported production V4 `make v4-setup`: SETUP_COMPLETE, only 026 applied,
  research_executed=false; no new run/source ingestion created.
- Actual read-only `make v4-preflight` for all three selected city hashes:
  **BLOCKED**, expected CLI/Make exit 2, mutations=0, source_reingested=false,
  research_executed=false. Old listing manifests/bytes reused successfully; no
  housing or migration mismatch blocker. Copenhagen still awaits common
  accessibility/source freeze/samples/folds/scientific dispatch; Oslo retains
  its vintage warning/seven unresolved city fields; Stockholm retains six
  unresolved non-housing city fields. No acquisition/run target was executed.
- Before/after protected verifier: **1,696 V3 files**, 22 applied migration hashes
  and five analytical SQL fingerprints unchanged.
- **252** captured evidence/source/config/history files unchanged, exact original
  step-log prefix retained, old specification copied exactly. **Eight** original
  V4 SQL table fingerprints unchanged (including all raw listing/housing audit
  rows and study geometries); original migration rows unchanged with only 026
  appended. **92** source-byte pins/eight canonical manifests PASS. Existing
  13 listing ingestions/three housing ingestions/eight manifests and original
  Stockholm failed-access/NULL-count history preserved. Analytical runs remain
  zero. No raw/restricted/private/credential file is to be staged.

Checkpoint: **A02 IMPLEMENTED_SCOPE_CHECKPOINT; research readiness PARTIAL/
BLOCKED** pending genuinely required A03–A07 city geography/context/accessibility/
sample/fold/estimator evidence. Housing access/acquisition is not required under
this design and is not marked historically qualified. A03 and empirical work are
not executed or authorized by this checkpoint. Stage only intended safe code/
config/new SQL/tests/Makefile/Markdown; requested commit:
`refactor(v4): remove housing from active models and readiness gates`.
Push HEAD explicitly to recorded origin refs/heads/v4 and verify actual remote
SHA equality afterward. No own commit SHA or future push success is recorded
inside this commit; push failure means LOCAL_ONLY and pauses the sequence.
