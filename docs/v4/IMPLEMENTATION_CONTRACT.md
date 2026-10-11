# V4 implementation contract

Established 11 October 2026 (Europe/Copenhagen). This contract applies to the
V4 sequence. Read it and `step_log.md` at the start of every step, alongside
applicable AGENTS.md / AGENTS.override.md instructions. Existing data-governance
and scientific safeguards remain in force.

## Authorized scope

Implement only the step explicitly requested. The initial checkpoint established
the branch, repository audit and protected baseline. The 11 October 2026
specification amendment establishes authoritative V4 Markdown, configuration
and consistency checks; it does not authorize acquisition, ingestion,
migration, feature construction, model fitting, pipeline execution or
regeneration of frozen V3 documents/results.
The subsequent architecture step authorizes V4 city configuration, isolation
adapters, an append-only V4 migration and disposable-database tests only.
The listing/boundary step additionally authorizes matched 30 June 2026 official
catalogue acquisition, checksum/schema-qualified immutable V3 reuse, official
municipal geometry acquisition/audit, dedicated local V4 database provisioning,
append-only migration 024, raw/audit ingestion and safe aggregate provenance
exports. It does not authorize model fitting, model samples, housing assignment,
network features or the research pipeline. Boundary access/vintage blockers are
recorded in [listing_acquisition.md](listing_acquisition.md) and
`listing_acquisition_audit.json`; raw/credentials remain private.
See [architecture.md](architecture.md) for implemented command behavior and
unresolved empirical gates. The roster is `copenhagen_frederiksberg`, `oslo`,
`stockholm`; narrower scope still requires an amendment.
Synthetic fixtures may exercise tests; they must never be research results.

## Scientific contract

The primary V4 models are exactly:

| Model | Required blocks |
| --- | --- |
| M0 | X + H |
| ME | X + H + E |
| MW | X + H + W |
| MEW | X + H + E + W |

The active definition version is `v4_housing_standard_20261011`; model IDs must
carry it so V3 M0 cannot be confused with V4 M0. X is the inherited qualified
baseline excluding H/E/W; E and W denote matched Euclidean and walking
accessibility. [The specification](preanalysis_specification.md),
[dictionary](data_dictionary.md) and `config/v4/research_design.json` define
the exact blocks. Their empirical implementation and qualification remain gated.
H is required neighbourhood residential sale-price context in all four
models. There are no H-suffixed models and no automatic no-housing ladder.
Unqualified, missing or incompatible H blocks dependent empirical work;
dropping H, inventing neighbourhood mappings or substituting another measure
is not an acceptable way to proceed.

Primary contrast: MEW versus ME. Replacement: MW versus ME. Additional:
ME/M0, MW/M0, MEW/M0. No adding-H benefit is estimated without a separately
authorized no-H sensitivity. Prefer full-year 2025 apartment sale-price/m2,
preserving native values and frozen within-city external-area midrank
`H=(midrank-0.5)/G_ref`; log native price remains a prespecified sensitivity.
All four models share a housing-qualified prediction sample and saved folds
within city; a separate common OLS association sample is documented. Mandatory
no-income sensitivity retains H. Preserve existing thresholds, candidates and
inference; numerical safeguards are not power guarantees.

The matched snapshot target is June 2026; retain OLS/XGBoost and separate city
models. Narrower-city or descriptive-only scope requires an explicit amendment
if a city lacks qualified H. No temporal Airbnb panel, residential-price outcome
model or gentrification score is authorized. V3 results were already observed;
supervisor approval is not recorded and there is no retrospective preregistration
claim. [The document index](document_index.md) records Markdown authority and
the absent/stale/superseded status of V4 DOCX material.

Y remains the natural log of observed Airbnb nightly asking price:
`log_price = log(price_nightly)` for valid observed prices. Never statistically
impute either outcome. Fit separate models for each authorized city; do not
infer the V4 city list from the existing V3 regional geography. Results describe
asking-price associations/prediction, with no causal housing-price or
displacement claims.

Never silently fill missing data. Learned predictive preprocessing,
imputation, feature selection and tuning must use training data only. Never
use the outer test fold to choose hyperparameters, accessibility thresholds,
POI categories, variables or preprocessing. Do not add techniques for headline
performance. Log any departure from the pre-analysis specification before
dependent empirical work. External sources require source, acquisition date,
extent and checksums where possible. Spatial operations must record their CRS.

## Data and identity isolation

PostgreSQL/PostGIS remains the authoritative persistent analytical layer.
CSV files are inspection/export artifacts, never undocumented alternative
sources of truth. All analysis tables and figures must be generated by code.
Raw sources, applied SQL migration bytes and completed V3 outputs are protected;
never modify them in place or run V3 regeneration commands as a test.

The architecture step implements the following identities through
`src.v4.cli` and `sql/v4_migrations/023_v4_multicity_persistence.sql`. No
production database is provisioned or empirical pipeline executed by that
step; only disposable synthetic database tests apply the migration:

| Identity | V4 reservation |
| --- | --- |
| Database | `thesis_accessibility_v4`, separate from existing `thesis_accessibility` |
| Schemas | `v4_raw`, `v4_clean`, `v4_spatial`, `v4_features`, `v4_analysis` in the V4 database |
| Run | `research_v4_<city_slug>_<UTC timestamp>`; require an explicit city and unique ID |
| Outputs | `outputs/v4/<version>/<run_id>/<city>/<snapshot>/` and equivalent `reports/v4/` |
| New raw inputs | `data/raw/v4/`, with their own source freeze and provenance |
| Configuration | `config/v4/`; separate ignored local connection file, e.g. `.env.v4` |

Do not point a future V4 runner at V3 schemas, run IDs, connection settings or
output paths. It must verify isolation and fail closed before any mutation.
Existing `.env` remains the V3 connection; no credentials are recorded here.
Existing V3 runners/configuration implement the V3 specification and do not
become V4-compliant merely because the Git branch is named V4.

Never upload raw/restricted data, database dumps, archives containing research
data, credentials, private row-level predictions, fold memberships, SHAP rows
or listing coordinates. Public baseline evidence consists of paths, hashes,
counts, migration identities and run statuses, with no underlying row contents.
Future data/output roots must stay ignored; inspect Git ignore coverage before
creating them. The current `reports/v4/` path is already ignored by `/reports/`;
`outputs/v4/` and all private V4 roots are explicitly ignored before use.

## Git lifecycle

The recorded remote is `origin`, with the existing fetch/push URL
`https://github.com/jibrilhemdi/airbnb-urban-accessibility.git`. The recorded
base main SHA is `c1e919bca9dfbe89de9e67135fb432fdb0f020e6`. Refer to
`repository_audit.md` for the fetched V3 evidence and initial worktree state.
Do not create or change remote URLs. Stop if remote identity becomes ambiguous.

At each step, inspect status (including staged and untracked files), worktrees
and unfinished operations before edits. Stop if unrelated work would mix into
the step. Never discard, automatically stash, force-switch or commit others'
work. Ignored local research inputs are preserved, not staged.

Fetch the recorded existing remote before checking lineage. If neither local
nor remote V4 exists, create V4 from fetched main without moving local main.
If V4 exists, resume it without recreation/reset and verify its recorded base.
For local/remote V4 updates, permit only an unambiguous fast-forward; stop on
divergence or unexpected lineage. Do not automatically merge later main
commits. Inspect history/content for V3 merge evidence, including squash merges;
do not require ancestry as the sole proof.

Before finishing each step:

1. Run relevant safe checks and inspect protected-artifact preservation.
2. Inspect the complete diff and stage only intended safe files by explicit
   path. Inspect the staged diff and confirm the active branch is `v4`.
3. Update `step_log.md` with scope, changes, actual checks and blockers.
4. Commit with the requested message. Never record that commit's own SHA inside
   itself; report the SHA and push evidence after the commit, outside it.
5. Initially push with `git push --set-upstream origin HEAD:refs/heads/v4`;
   subsequently use `git push origin HEAD:refs/heads/v4`. Confirm the remote V4
   SHA from `git ls-remote --heads origin refs/heads/v4` equals `git rev-parse HEAD`.
6. Report status, tests actually run, changed files, commit SHA, verified push
   and blockers. A successful local commit alone is not a completed checkpoint.

Never push main/v3, force-push, amend published commits, change tags or merge
V4 into main. Never bypass authentication or approval controls.

## Stop states

Missing data or failed scientific gates mean **BLOCKED**, never an invented
substitute. A safe blocker-documentation checkpoint may be committed/pushed,
but does not authorize dependent empirical work. Resolve the specific gate in
an explicitly requested subsequent step. A push failure means **LOCAL_ONLY**;
report the failure and stop before the next step. No empirical V4 work is
authorized or certified by passing this bootstrap baseline.
