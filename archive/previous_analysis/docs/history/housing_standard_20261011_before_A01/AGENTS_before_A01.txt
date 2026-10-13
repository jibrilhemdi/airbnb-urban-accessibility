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

## V4 sequence safeguards

Read [the V4 contract](docs/v4/IMPLEMENTATION_CONTRACT.md) and
[the step log](docs/v4/step_log.md) at every step. Implement only the requested
step; synthetic fixtures are tests, never research results.

- Work, commit and push exclusively on `v4`, using the remote and main base
  recorded in [the repository audit](docs/v4/repository_audit.md). Stop if other
  work, unfinished Git operations, ambiguous lineage or divergence would mix
  into the step. Never discard/stash other work, reset an existing V4 branch,
  merge later main commits automatically, force-push, amend published commits,
  change tags, push main/v3 or merge V4 into main.
- Primary V4 models are exactly `M0=X+H`, `ME=X+H+E`, `MW=X+H+W`,
  `MEW=X+H+E+W`. H is required neighbourhood residential sale-price context.
  No H-suffixed models or automatic no-housing ladder.
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
