# Three-city urban accessibility research

The active study compares accessibility measurement, within-city price prediction,
geographic generalization and directional relative-price transfer across Copenhagen,
Oslo and Stockholm. [Scientific proposal](docs/scientific_proposal.md),
[specification](docs/analysis/preanalysis_specification.md),
[research plan](docs/analysis/research_plan.md) and
[execution log](docs/analysis/execution_log.md) define the actual design and status.

[Publication research handover](docs/analysis/research_report_publication.md),
[generated findings](docs/analysis/findings.md) and
[release audit](docs/analysis/release_audit.json) report the completed work.
All three predictive city ladders, all six relative-price transfers and registered
independent robustness checks completed. The full study is **PARTIAL / BLOCKED**:
Stockholm association inference and its dependent checks exceed the frozen
predictor-missingness guard. No inferential-imputation substitute was used.

Active configuration is in `config/study/`; the single active entry point is
`src/study/cli.py`. Use functional private run/output paths. PostgreSQL/PostGIS
is authoritative; raw source data and completed historical objects are immutable.
The existing `v4` branch is the only active version identifier.

```sh
make study-design
make study-status
make study-test
make compile
```

Status returns a nonzero exit when the empirical workflow is incomplete. A design
freeze or passing synthetic test is not an empirical result. Listing-level data,
credentials, coordinates, folds and predictions are private and ignored.
Completed fit selectors refuse refitting at the CLI; use audits or provision
explicit new identities for a separate rerun. Public aggregate artifact hashes
are recorded in the publication inventory; initial completed artifacts are retained.

The [path inventory](docs/analysis/path_inventory.json) records pre-change hashes
and compatibility decisions. Previous project instructions and entry documentation
remain unchanged in [history](history/previous_scope/README.md). Existing source,
pipeline and migration paths provide historical reproduction and audited reusable
helpers; their frozen configurations/results do not govern or certify the final
rerun. No old derived numerical result is accepted as a final-design result.
