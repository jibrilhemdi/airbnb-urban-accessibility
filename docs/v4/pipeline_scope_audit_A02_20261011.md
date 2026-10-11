# A02 pipeline-scope audit — 11 October 2026

Active design: `v4_accessibility_only_20261011`. A02 implements housing-free
scope and identity checks only; empirical readiness remains **BLOCKED** pending
A03–A07 and genuine city data. No source acquisition, routes, feature/sample/fold
construction or fitting is authorized or performed.

## Entry and preserved evidence

Existing branch `v4`, clean entry/fetched origin tip
`f5a6913c362ebaef01d828baf778164c538626cd`; no divergence, other edits or unfinished
Git operation. Recorded origin remains
`https://github.com/jibrilhemdi/airbnb-urban-accessibility.git`; recorded main base
`c1e919bca9dfbe89de9e67135fb432fdb0f020e6` and local main/v3/worktree refs are
preserved. Read root AGENTS, active contract/log, A01 audit/model contract and
supplied revised proposal/plan, actual source/config/code/tests/migrations.
V3 results and housing feasibility were already known; no approval invented.

Frozen `config/v4/research_design.json`, `cities.json`, `housing_sources.json`,
listing/Stockholm policies, applied migrations 023–025, all acquisition adapters,
raw/manifest/receipt/SQL evidence and imported bundle/history remain intact.
`src/v4/historical_specification.py` preserves the prior specification module's
exact bytes and validates the old housing design. Historical assertions remain
executed against that registry and the exact before-A01 Markdown snapshot.
The A01 audit/log and historically BLOCKED housing-source statuses are retained.

## Canonical registry and baseline resolution

One active registry: `src/v4/specification.py` loads
`config/v4/research_design_accessibility_only.json`. Primary M0=X, ME=X+E,
MW=X+W, MEW=X+E+W; no-income removes only income. Neither `no_housing` nor
`log_native_housing` is an active scenario. Exact inherited X/E/W membership is
validated against V3's actual constants; no rent/residential-price proxy can be
added by editing a block. Seeds, 30 frozen candidates, inference/measurement
thresholds and no-income change rules remain unchanged. Outcome is log original
positive observed Airbnb nightly asking price, separate native-currency cities.

The A02 instruction to remove **only housing-derived active dependencies**
resolves A01's `property_type` discrepancy in favour of retaining the actual V3
categorical control. This is explicitly documented rather than silently changing
X. It supersedes the supplied prose exclusion; supplied bytes remain unchanged.
New-city income concepts/scales remain unqualified, not assigned Copenhagen's
income/projection by implication.

## Dependency-remnant trace

| Prior remnant | Revised implementation |
| --- | --- |
| Primary H and log-native-H sensitivity | Removed from active registry/config; historical registry retained |
| Housing-qualified prediction/OLS samples | Config requires common accessibility-supported S_pred and union X/E/W S_assoc; sample construction is A06 |
| Non-null native housing-area join/filter | Private SQL audit reader selects a whitelist without housing fields and reads every approved audit row; no H join/WHERE filter |
| Annual sales, 80% coverage, minimum native areas | No active city/scope prerequisites; historical source policy remains unchanged |
| External H ranks/reference frame | No active feature/required source or sensitivity |
| H-safe folds and H-group support | No active validation/group gate; ordinary analysis geography/support still required |
| Housing-source scientific hashes | Active hash excludes housing policy/module, historical specification and migration 025; applied-migration integrity still checks all files |
| Housing failure in reports | New model reports read only aggregate metrics and enforce selected design; frozen historical listing/housing audit reports retain their true old statuses |

## Source reuse, identity and persistence

`config/v4/listing_reuse_accessibility_only.json` records the exact selected
listing run/hash per city from A01, including amended Stockholm scope.
`src/v4/source_reuse.py` performs SELECT/checksum operations only: checks exact
city/snapshot/purpose/run/hash, canonical manifest and frozen source bytes.
Neither re-download nor INSERT/UPDATE ingestion is called. All audit rows,
including missing prices and NULL housing/analysis IDs, remain visible in the
private whitelisted read; this is not a final model sample or public export.
Boundary vintage and analysis-area/context qualification remain independent.

`Scope.design_id` separates science from the unchanged `research_design_v4`
source namespace. Existing acquisition adapters retain the historical default;
the analytical CLI explicitly defaults to the new design and supports
`--design-id`. New intermediate/output/report paths and cache identity include
the new design. Raw/manifest paths stay identical across designs. Markdown,
Git/reporting metadata remain separate from scientific dependencies.

Migration **026_v4_accessibility_only_definition.sql** is append-only. It extends
allowed run/model IDs, validates parent-design consistency, and exposes separate
model/sensitivity/estimator/validation dimensions. Historical artifact estimator/
validation fields remain NULL, without fabricated retrospective values. The
artifact unique key includes estimator/validation with NULLs treated as equal;
completed/append-only/truncation/source/purpose guards remain. Historical records
are never relabelled or reopened. Migration 026 was tested in owned disposable PostGIS databases, then applied
through the supported V4 setup target to `thesis_accessibility_v4`. Its applied
SHA256 is `57031e2bb082f5dd2e5ec1733d1a0db82a0a014a52ffe09a27abeaceb79a46c7`;
original migration records/bytes and all existing source/run rows stay unchanged.
Derived dimensions use views rather than backfilling/re-writing completed rows.

## Scope versus full readiness

`src/v4/readiness.py:scope_check` verifies supplied synthetic candidate rows
without removing or filling rows. NULL/absent housing fields and no housing
files pass this scope check; invalid original price/log-price, duplicate IDs,
unresolved/outside mask, absent official analysis IDs, failed context/support
qualification, missing columns or entirely missing/nonfinite required features
still block. A passed scope check is not source approval, frozen samples/folds
or permission to fit. Ordinary training-only preprocessing remains future work.

`v4-preflight` is read-only and never returns READY while scientific stages and
empirical dispatch are unimplemented. Oslo vintage and new-city context/CRS/
anchor fields remain unresolved. `v4-run` still refuses empirical dispatch;
A02 adds no estimator or route runner.

Actual supported commands (existing Makefile conventions):

```sh
make v4-test
make v4-test-db
make compile
make v4-setup VERSION=research_design_v4 DESIGN_ID=v4_accessibility_only_20261011 CITY=copenhagen_frederiksberg SNAPSHOT=2026-06-30 RUN_ID=research_v4_copenhagen_frederiksberg_20261011T180000Z
make v4-preflight VERSION=research_design_v4 DESIGN_ID=v4_accessibility_only_20261011 CITY=stockholm SNAPSHOT=2026-06-30 RUN_ID=research_v4_stockholm_20261011T180000Z V4_PREFLIGHT_FLAGS='--source-manifest d1d923db415dbf2218560947e3fd862657e343317f36fee284fa36e36cc0d172'
```

Setup applies only the checksummed V4 migration set to the dedicated V4 DB;
preflight uses the supplied run ID for read-only collision checks and creates no
run. Existing historical acquisition/audit commands are preserved, not invoked.

## Actual verification

- `make v4-test`: **81 discovered, 62 passed, 19 opt-in DB skipped**, exit 0.
- `make v4-test-db`: **19/19 passed**, exit 0; owned temporary UUID databases
  only. Includes historical completed-run upgrade preservation, migration
  idempotence/hash guards, estimator/validation/sensitivity/model separation,
  parent-design mismatch and completion refusal, source reuse with NULL housing
  fields and all audit rows retained, duplicate/source/city/immutability/privacy.
- Safe `scripts/v4_repository_checks.py --baseline-tests`: **175 discovered,
  133 passed, 42 opt-in skipped**, exit 0. Candidate export redirected to a
  temporary location, live V3 database/integration mutation flags disabled.
  No historical test is suppressed to obtain these results; housing assertions
  run on their immutable registry/history and active document checks are scoped
  to the amended definition and pinned supplied DOCX references.
- `make compile` and tracked/staged whitespace checks: PASS.
- Before/after protected checker: **1,696 V3 files**, **22** applied migrations
  and **five** analytical SQL fingerprints unchanged.
- **252** preserved evidence/source/config/history files unchanged, plus exact
  append-only step-log prefix. Prior specification module copied byte-for-byte.
- **Eight** original V4 SQL table fingerprints unchanged: listing ingestion/
  audit, housing ingestion/area-period audit, manifests, study boundaries,
  original migration rows and analytical runs. Only the migration ledger gains
  the new 026 row. **92** registered source-byte checks and eight manifest
  canonical hashes pass. Existing 13 listing ledgers, three housing ledgers,
  eight manifests, original 401/NULL receipt/scopes and zero fitted runs remain.
- Actual supported `make v4-setup` applies **only 026**, SETUP_COMPLETE,
  `research_executed=false`. No source/model run is created.
- Actual read-only `make v4-preflight` for all three cities with selected source
  hashes returns **BLOCKED**, CLI/Make exit 2 as expected, `mutations=0`,
  `source_reingested=false`, `research_executed=false`. All approved old hashes
  are reused successfully; no housing or migration mismatch blocker appears.
  Copenhagen retains matched-source/sample/fold/scientific-stage blocks;
  Oslo adds its source-provenance vintage warning and seven unresolved city
  fields; Stockholm has six unresolved non-housing context/CRS/anchor fields.

A02 is an **IMPLEMENTED_SCOPE_CHECKPOINT / PARTIAL research-readiness** result.
Housing failure is not a new-design gate; it is not retrospectively qualified.
Genuine city geography/context, matched accessibility, sample/fold and estimator
qualification remain **BLOCKED**. No fitted result, source acquisition or routing
is inferred from these checks; A03 is not executed or authorized here.

## Safe changed files

```text
AGENTS.md
Makefile
config/v4/cities_accessibility_only.json
config/v4/listing_reuse_accessibility_only.json
config/v4/research_design_accessibility_only.json
docs/v4/IMPLEMENTATION_CONTRACT.md
docs/v4/architecture.md
docs/v4/data_dictionary.md
docs/v4/document_index.md
docs/v4/model_contract.md
docs/v4/pipeline_scope_audit_A02_20261011.md
docs/v4/preanalysis_specification.md
docs/v4/proposal.md
docs/v4/research_plan.md
docs/v4/source_registry.md
docs/v4/step_log.md
docs/v4/step_mapping_A01_A12.md
sql/v4_migrations/026_v4_accessibility_only_definition.sql
src/v4/cities.py
src/v4/cli.py
src/v4/historical_specification.py
src/v4/identity.py
src/v4/persistence.py
src/v4/readiness.py
src/v4/reporting.py
src/v4/runtime.py
src/v4/source_reuse.py
src/v4/specification.py
tests/test_v4_accessibility_only.py
tests/test_v4_architecture.py
tests/test_v4_persistence.py
tests/test_v4_specification.py
```
