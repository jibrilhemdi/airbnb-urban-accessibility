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
