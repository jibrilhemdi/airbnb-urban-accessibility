# V4 repository audit

Audit date: 11 October 2026, Europe/Copenhagen. Scope: branch safeguards and
safe baseline only. No research pipeline or scientific rerun was performed.

## Instructions and initial Git safety

Repository root: `/Users/jibrilhemdi/Documents/Projects/thesis-urban-accessibility`.
Read the root `AGENTS.md` (all twelve original rules retained). No ancestor
AGENTS.md/AGENTS.override.md was present in the inspected path from `/` to the
project, and no root override or nested instructions apply to `docs/v4/` or
`scripts/`. Instructions in the ignored legacy archive and detached worktree
apply to those trees, which were not edited. The user's step-specific Git and
scientific instructions also govern this checkpoint.

Initial active branch was `v3`, HEAD and upstream `origin/v3` both
`6150e3f3b4e6db01dd5bf5842404212343d1344a`. There were no tracked modifications,
staged changes or nonignored untracked files. No merge, rebase, cherry-pick,
revert, bisect, sequencer or index-lock state was found. Ignored local research
inputs, `.env`, archives, outputs and packaging remained present and protected.

Two registered worktrees were inspected:

| Worktree | Initial state |
| --- | --- |
| Repository root | clean, `v3` at `6150e3f3b4e6db01dd5bf5842404212343d1344a` |
| `.kilo/worktrees/storm-acoustic` | clean, detached at `7de587997157863e0ba1d36c3f39bdd45f2b9d23` |

`origin` was the sole configured remote, with identical fetch/push URL
`https://github.com/jibrilhemdi/airbnb-urban-accessibility.git`, consistent with
this project's tracked source/history. No URL was created or changed.
`git fetch origin` succeeded through the normal approval-controlled execution
path after the sandbox denied writing `.git/FETCH_HEAD`.

## Recorded base and V3 evidence

Fetched main/base SHA: **`c1e919bca9dfbe89de9e67135fb432fdb0f020e6`**.
It is the 11 October 2026 merge commit “Merge pull request #1 from jibrilhemdi/v3”,
with parents `7de587997157863e0ba1d36c3f39bdd45f2b9d23` and
`6150e3f3b4e6db01dd5bf5842404212343d1344a`.

Fetched V3 tip: **`6150e3f3b4e6db01dd5bf5842404212343d1344a`**, “Introduce
version 3 source pipeline without research data”. The merge base of fetched
main/V3 is that V3 tip. `git diff origin/v3 origin/main` is empty: both ancestry
and content establish V3 integration. This does not rely on an assumption
about squash-merge ancestry.

Neither local nor fetched remote `v4` existed. Created it using
`git switch -c v4 origin/main --no-track`, from the recorded fetched main tip.
No existing V4 branch was reset or recreated. Local main remains
`7de587997157863e0ba1d36c3f39bdd45f2b9d23`; local V3 remains its recorded tip;
the detached worktree is unchanged. No later main commits were merged.
Initial upstream is established only by the explicit V4 push.

## Root, configuration and actual entry points

Inspected the root, README, Makefile, environment example, Compose definition,
requirements, `.python-version`, ignore rules, all active configuration
structures, methodological docs, tests, SQL migration/query definitions and
the current runners. Raw rows and credentials were not printed or staged.

The active code is V3. `config/research_design.json` identifies
`research_design_v3`, eleven analysis areas, source CRS EPSG:4326 and metric
CRS EPSG:25832. It retains the qualified-income amendment and mandatory
no-income robustness. `src/pipeline/model_specification.py` defines the
existing V3 four-model ladder and no-income variants; it does not implement
V4's required H block. Existing documentation remains historical V3 evidence,
not a substitute V4 specification. The V4 contract takes precedence for the
V4 sequence without rewriting these frozen configurations/documents.

| Make target | Actual entry point / behavior |
| --- | --- |
| `compile` | `.venv/bin/python -m compileall src` by default |
| `test` | `.venv/bin/python -m unittest discover -s tests -v`; see isolation below |
| `integration-test` | Same suite with `THESIS_DB_TEST=1 THESIS_V3_INTEGRATION=1`; some tests migrate/register/import, so not run |
| `db-up`, `db-down`, `db-psql` | Docker Compose using local `.env`; not run |
| `db-connect`, `db-check` | `src.db.cli connect/check`; read-only checks |
| `db-migrate`, `db-register` | `src.db.cli migrate/register-sources`; mutate database, not run |
| `db-diagnose` | `src.db.diagnose`; not needed for this checkpoint |
| `pipeline`, `reproduce` | `src.pipeline.run_pipeline --run`; not run |
| `preflight` | Same runner with `--preflight`; writes preflight and candidate exports, not run |
| `smoke` | Same runner with `--smoke`; writes a synthetic V3 certificate, not run |
| `candidates` | `src.pipeline.build_tuning_candidates`; writes candidate export, not run directly |
| `audit` | `src.pipeline.audit_reproducibility --repository-only`; writes V3 audit export, not run directly |
| `migration-audit` | `src.pipeline.build_migration_audit`; regenerates docs/exports, not run |
| `income-evidence`, `income-deciles` | `src.ingestion.acquire_income_evidence` (optionally `--deciles`); not run |
| `municipal-income-evidence` | `src.ingestion.acquire_municipal_income_evidence`; not run |
| `income-audit`, `income-docs` | `src.pipeline.qualified_income` / `update_income_documentation`; can migrate/write exports/DOCX, not run |
| `reporting` | `src.pipeline.render_reporting_figures`; regenerates completed reporting, not run |

The full runner lists 25 dependency stages, from `build_airbnb_sample` through
`audit_reproducibility.audit_run`; the exact semantic sequence is recorded in
`docs/migration_rerun_audit.md` and the `DEPENDENCIES` constant. Its `--resume`
supports only documented operational V3 failures. `src.pipeline.rebuild_project`
delegates to this runner. None is a V4 runner.

`src/db/migrations.py` applies sorted legacy migrations 001–018 followed by
current migrations 019–022, using `meta.schema_migrations` checksums and a
transaction/advisory lock. Migration 019 creates isolated V3 data schemas;
020 adds analytical records/runs/folds/artifacts; 021 neutralizes provider
diagnostics; 022 adds qualified area income. The cleaning query is
`sql/queries/build_clean_airbnb_listings.sql`. No migration or query was applied
in this step. All 22 applied migration hashes match current file bytes.

V3 outputs route through `src/pipeline/output_paths.py`; SQL artifact storage
is in `src/pipeline/storage.py`. Its persistence replaces records for the
selected V3 run/family/artifact. Neither module currently provides V4 identity
isolation. Future V4 execution must implement the separate identities reserved
in the contract before any mutation.

## Authoritative store and observed environment

PostgreSQL/PostGIS is authoritative; local CSVs/figures are exports. Configuration
is read through `src/db/connection.py`, from local ignored `.env` with existing
environment overrides. Credentials were neither published nor changed.
Compose configures `postgis/postgis:16-3.5`, linux/amd64, a named `postgis_data`
volume and a loopback host port (default 5433). This is configuration evidence,
not an assertion that Compose was started during this step.

Read-only connections verified the existing `thesis_accessibility` database:
PostgreSQL **16.9 (Debian 16.9-1.pgdg110+1)**, PostGIS **3.5**
(`USE_GEOS=1 USE_PROJ=1 USE_STATS=1`). Five V3 schemas are present:
`v3_raw`, `v3_clean`, `v3_spatial`, `v3_features`, `v3_analysis`.
No V4 schemas were found. No V4 database was created or connection provisioned.

SQL contains completed run `research_v3_20261004T111510Z` and three historical
income investigation runs with their original blocked statuses. Local
`run_metadata.json` records complete execution; the original analytical
`reproducibility_audit.json` and current `reporting_refresh_audit.json` record
passed audits. These existing certificates were inspected/hashed, never
regenerated. Their presence and preserved bytes do not certify a V4 result.

Environment observed: Darwin 25.5.0 arm64; Git 2.50.1 (Apple Git-155);
`.venv/bin/python` reports Python **3.13.5**, matching `.python-version`.
All **23** pinned direct requirements match installed package metadata.
Docker, psql and make executables are present. No dependencies were installed
or updated. SQL permission checks initially encountered the filesystem/network
sandbox; approved read-only access succeeded. No approval/authentication control
was bypassed.

## Protected V3 checksum baseline

`protected_v3_manifest.json` contains **1,696** SHA-256/size file records,
all 22 applied migration identities and five ordered analytical SQL table
fingerprints. It contains no raw file contents, credentials, predictions or
private row records. SHA-256 of the manifest itself:
`2ef92016429509fc75d35d20a3531781406303c26f558c02d8257aaa38c551cd`.

Covered files include 204 frozen raw inputs, 230 output files, eight reports,
1,203 archive files, eleven config files, four supporting design files and
23 SQL files. Interim/processed placeholders, metadata and the existing
private packaging ZIP are also hashed. `.DS_Store` is excluded as OS metadata.
V4-specific roots listed in the checker are excluded so future V4 artifacts
can have their own identity. No protected bytes were staged.

| Preserved SQL table | Rows | Ordered SHA-256 |
| --- | ---: | --- |
| `v3_analysis.runs` | 4 | `e2680e9a97d4931151eeed36f2927e7ad47987d753cc3e6f01dfdf00158ba52b` |
| `v3_analysis.dataset_records` | 12,412 | `4fb5092c4003f2e1e4fd73a5e7796df3be828e67396fefab928549bf7ee3fc9b` |
| `v3_analysis.outer_assignments` | 844,016 | `9279f9c952297115f9cac21be9db777062e1f5e686b3ebbeb1c4768346a0cb99` |
| `v3_analysis.inner_assignments` | 688,004 | `ca9d2af8aca961668f2667456fd6fb66ef68757bc3a8ba624f20dd97d0510069` |
| `v3_analysis.artifacts` | 8,618,337 | `42a02fc1b735645faabcb617cd47b6aef195147a84ddd318205ae32257755b59` |

SQL fingerprints stream UTF-8 `row_to_json(t)::text` with one LF per record,
ordered by the table's full primary key, inside a repeatable-read transaction
with `transaction_read_only=on`. No rows are written/exported; only the digest
and count survive. Applied migration hashes are compared with local SQL bytes.
This guards the five analytical tables, not every physical byte or every V3
feature/raw SQL table. File checks cover local raw sources and completed outputs.

The original frozen analytical dataset certificate additionally records
`d48158c146e0005a5fc3bb0326c71f2a34a38c07b7c07ef46d4cfd05e70ab8f9` under
its original dataset-hash algorithm. That differs intentionally from the
row-JSON table fingerprint above; this step does not recompute the scientific
dataset certificate.

## Safe baseline checks

Commands actually run:

```sh
make compile
.venv/bin/python scripts/v4_repository_checks.py --baseline-tests
.venv/bin/python scripts/v4_repository_checks.py --capture docs/v4/protected_v3_manifest.json --database
.venv/bin/python scripts/v4_repository_checks.py --verify docs/v4/protected_v3_manifest.json --database
git diff --check
```

Compilation passed. Isolated baseline discovery ran **94 tests** in 69.087
seconds: **71 passed, 23 explicitly skipped, zero failures/errors**. Live DB and
V3 integration opt-ins were explicitly disabled, since some tests apply
migrations or import/register sources. Synthetic evaluators run only as tests
with mocked SQL persistence/exports. The candidate helper's write to
`outputs/tables/validation/xgboost_candidates.json` was redirected to a temporary
directory. The existing candidate freeze was required to be present, so no
new freeze could be silently generated. The original tests were not modified.

Existing read-only Python functions `protocol.verify_inputs`,
`audit_reproducibility.archive_check` and `naming_check` passed: **204** frozen
raw input hashes/membership, **793** legacy archive checksums and V3 syntax/naming
checks. Their mutating CLI entry points were not invoked. New checker syntax
was parsed successfully. Five temporary synthetic guard tests passed for
changed/missing files, added files, symlinks, V4 exclusion and refusal to
overwrite an existing capture. Full baseline logs remain under `/tmp/`, outside V3
outputs; their contents were not needed as public research artifacts.

The source-registration unit check emitted the existing explicit warning for
`data/raw/municipalities.zip`: provenance is unverified and it is excluded from
analytical source registration. Its bytes are still protected by the manifest;
no provenance or geographic mapping was invented.

Final checksum and staged-file review results are recorded in `step_log.md`.
The successful checkpoint commit SHA and remote verification are reported
after committing, outside that commit. No scientific V4 gate has been cleared.

## Remaining gates

This step does not assess or qualify V4 housing context, city coverage,
geographic harmonisation, sample readiness or a V4 implementation. H and all
dependent scientific/implementation gates remain BLOCKED for empirical work
until the relevant requested steps pass. There is no no-housing substitute.
No blocker to this documentation-only checkpoint was found. A push failure
would make the checkpoint LOCAL_ONLY and prevent beginning the next step.
