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

## Active research workflow

Read [the contract](docs/analysis/implementation_contract.md),
[design](config/study/design.json), [plan](docs/design/end_to_end_research_plan.md),
[association amendment](docs/analysis/association_missingness_amendment_20261013.md)
and [execution log](docs/analysis/execution_log.md).
The explicit post-observation association eligibility limit is 10% for all
three cities. Complete-case inference never fills missing bedrooms or outcomes.
Income and housing remain excluded. Models are exactly M0=X, ME=X+E, MW=X+W,
MEW=X+E+W; preserve the common predictive samples and source-only transfers.
Completed predictive/transfer fits stay unchanged after dependency checks.

Use functional active paths, one requirements.txt, one .env and one archive/. Python's
audited version is recorded in the environment audit and requirements comment.
Previous source adapters use src/provenance; archived evidence is resolved
through the checksum-aware archive manifest. Raw bytes, applied migrations,
persisted SQL/source identities and completed fitted artifacts remain immutable.
The researcher explicitly excludes the discarded historical ZIP from current
preservation checks; its old manifest entry stays historical evidence.

Work exclusively on the existing v4 branch and recorded origin; do not modify
main/v3, reset/rebase/force-push, rewrite published history, stash unrelated
work or overwrite unarchived completed results. Use normal incremental commits.
At each checkpoint test, review/stage only intended safe files, update the
execution log, push HEAD:refs/heads/v4 and verify remote SHA equals local HEAD.
Do not put a commit's own SHA inside that commit. Push failure is LOCAL_ONLY.
No private sources, credentials, row-level predictions or models enter Git.
Scientific blockers stop dependent work; continue independent work. Synthetic
fixtures are tests, never research results. Old instructions/audits remain
byte-preserved in archive/ and do not reactivate superseded stages.
