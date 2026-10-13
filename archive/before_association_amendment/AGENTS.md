1. Never modify raw source files in place. Raw data are immutable.

2. PostgreSQL/PostGIS is the authoritative persistent analytical data layer.
   Intermediate CSVs may be created for inspection/export, but should not
   become alternative undocumented sources of truth.

3. Never silently fill missing data.

4. Never statistically impute the outcome variable `price_nightly` or `log_price`.

5. Any learned preprocessing, imputation, feature selection, or tuning used
   for predictive evaluation must be fitted using training data only.

6. Never use the outer test fold to choose hyperparameters, accessibility
   thresholds, POI categories, variables, or preprocessing decisions.

7. All spatial operations must record the CRS used.

8. All externally acquired data must record source, acquisition date,
   geographic extent, and—where possible—a file checksum.

9. Do not fabricate geographic mappings, neighbourhoods, variables, or values
   when required data are unavailable.

10. Do not add new modelling techniques solely because they improve headline
    performance. Deviations from the pre-analysis specification must be logged.

11. Prefer reusable scripts/functions and SQL migrations over manual notebook
    operations.

12. Every analysis table and figure must be reproducible from code.

## Active comprehensive rerun

The researcher request of 13 October 2026 supersedes the former sequential
scope below. Read [the active contract](docs/analysis/implementation_contract.md),
[design](config/study/design.json), [plan](docs/analysis/research_plan.md), and
[execution log](docs/analysis/execution_log.md). The previous instructions are
preserved byte-for-byte in `history/previous_scope/AGENTS.md`; dated audits and
the former step log remain historical evidence.

Work only on the existing `v4` branch. Execute the comprehensive task without
ordinary stage confirmations. Income and residential prices are outside all
primary and required analyses. Use operational Inside Airbnb neighbourhoods
(11/17/11); preserve raw labels. Geographic support requires at least 15 test
and 500 complementary training observations in the frozen common sample.
Use separate native-currency log-price city models and six directional
city-relative log-price transfer experiments. No target-city fitting/tuning or
intercept recalibration. Recompute all derived research results; reuse only
verified immutable sources and audited infrastructure. New active paths and
identities use functional names. Historical migrations, schemas, ledgers,
sources and completed results keep their original identities and bytes.

At each checkpoint test, review safe staged files, update the execution log,
commit, push `HEAD:refs/heads/v4` to recorded origin, and verify remote equality.
Never alter main/v3, reset/rebase/force-push, stash unrelated work or overwrite
completed results. A failed push is LOCAL_ONLY. A scientific blocker stops its
dependent work; continue independent work. Fixtures are tests, never results.

## Historical sequence safeguards (superseded by the explicit rerun request)

Read [the active accessibility-only V4 contract](docs/v4/IMPLEMENTATION_CONTRACT.md),
[the step log](docs/v4/step_log.md) and [document index](docs/v4/document_index.md)
at every step. Design `v4_accessibility_only_20261011` supersedes the historical
housing-inclusive instructions. Continue the existing `v4` branch and execute
only the requested A01–A12 step; synthetic fixtures are tests, never research results.

- Work, commit and push exclusively on `v4`, using the remote and main base
  recorded in [the repository audit](docs/v4/repository_audit.md). Stop if other
  work, unfinished Git operations, ambiguous lineage or divergence would mix
  into the step. Never discard/stash other work, reset an existing V4 branch,
  merge later main commits automatically, force-push, amend published commits,
  change tags, push main/v3 or merge V4 into main.
- Primary models are exactly `M0=X`, `ME=X+E`, `MW=X+W`, `MEW=X+E+W`.
  Residential prices/H are absent from primary models and required sensitivities.
  Retain density, qualified income, centrality and matched no-income robustness;
  income is distinct from property prices. Housing acquisition, samples, sales/
  coverage gates, folds and subgroups are NOT_REQUIRED_SCOPE_AMENDED. Preserve
  their historical evidence/statuses; do not pursue unsent requests. Genuine
  geography/context/accessibility gates remain. A02 implements the active registry and scope checks; full empirical readiness
  remains BLOCKED pending city/source/sample/fold/estimator qualification. Read
  [the A03 geography audit](docs/v4/geography_qualification_A03_20261011.md) for
  qualified operational masks/CRS and remaining Oslo/Stockholm analysis blockers;
  do not reinterpret their municipal masks as validation areas. Read
  [the A04 context audit](docs/v4/context_qualification_A04_20261011.md) for native
  source validation versus spatial/final qualification. No common no-income
  primary mode is activated; the pre-fit income proposal requires an explicit decision.
- Y remains log observed Airbnb nightly asking price. Fit separate city
  models; make no causal housing-price or displacement claims.
- Preserve V3 artifacts and applied migrations. Use separate V4 run,
  database and output identities. Never upload raw/restricted data,
  credentials or private row-level predictions.
- Before finishing each step, run relevant checks, inspect and stage only
  intended safe files, update the step log, commit, and push `HEAD` explicitly
  to `refs/heads/v4` on the recorded remote. Set upstream on the initial push;
  verify remote V4 SHA equals local HEAD.
- Report status, actual tests, changed files, commit SHA, push verification
  and blockers. Do not record a commit's own SHA inside that commit.
- Missing data or failed scientific gates mean `BLOCKED`, never an invented
  substitute. A safe blocker-documentation checkpoint may be committed/pushed
  but does not authorize dependent empirical work. Push failure means
  `LOCAL_ONLY`: stop before the next step.
