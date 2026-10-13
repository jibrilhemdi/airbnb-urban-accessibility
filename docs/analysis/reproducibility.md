# Reproducing the active study

The canonical design is `config/study/design.json`; scientific decisions,
source/time/CRS/receipt hashes and immutable SQL selectors are under
`config/study/` and `docs/analysis/`. Use `.venv/bin/python` and the pinned
original `requirements.txt` plus `requirements-study.txt`. The generated
software inventory records the actual environment, rather than implying that
unbounded dependency ranges uniquely reproduce it.

PostGIS schema `study` in the existing dedicated analytical database is the
persistent authority. Its inherited database name is retained for provenance;
new scientific identities are neutral. Applied original migrations are
unchanged; append-only `sql/study_migrations/029_study_foundation.sql` provides
atomic immutable packages. Child records cannot grow after their parent
transaction commits. Research writes cannot target the historical baseline
database. Integration tests create and remove only their own UUID-named
disposable databases; their fixtures are never research results.

Raw/source receipts are private. Verify the selected original listing manifests
and file checksums before reuse. Do not redownload detailed listings or edit raw
bytes. Source acquisitions and failed responses retain actual acquisition date,
URL, extent, CRS, snapshot/reference date, licence and checksums. Historical
source IDs are compatibility references, not newly minted stage/version names.

The implementation order is:

```sh
make study-test
make study-test-db
make study-setup
make study-geography-audit
make study-context-audit
```

An existing completed database/source freeze must not be regenerated in place.
The source-to-model sequence is exposed through `python -m src.study.cli`:
geography, context, accessibility, sample and pre-fit freezes, then within-city
and transfer commands. For a genuinely separate rerun, first create new explicit
functional source/selection/output identities; the write-once selectors prevent
accidental replacement of completed experiments. Never remove a selector to
make a completed experiment writable. Existing run identities remain reproducible
evidence. A missing source or failed scientific gate blocks dependent fitting.

```sh
.venv/bin/python -m src.study.cli within-city --city copenhagen --scheme neighbourhood
.venv/bin/python -m src.study.cli transfer
.venv/bin/python -m src.reporting.study_robustness --city copenhagen
.venv/bin/python -m src.reporting.study_training_sensitivity --city copenhagen
.venv/bin/python -m src.reporting.study_measurement_sensitivity
.venv/bin/python -m src.reporting.study_extended_sensitivity --city copenhagen --scenarios buffer_500 buffer_1000
.venv/bin/python -m src.reporting.study_extended_sensitivity --city stockholm --scenarios density_same_year density_land_only
.venv/bin/python -m src.reporting.study_extended_sensitivity --city copenhagen --scenarios speed_4p0 speed_5p4 continuous_decay
```

City arguments extend these commands to Oslo and Stockholm; validation schemes
cover random and each frozen1/1.5/2km zero/half-origin block design. Every fresh
fit retains the exact30 candidates and four source-training-only inner folds.
`STUDY_MODEL_WORKERS` controls bounded operational concurrency only; it does
not change candidates or source-only fitting. Primary fold packages persist
private model bytes/hashes, predictions, losses, tuning and held-out contributions.
Transfer stores24 fresh source fitted pipelines and48 target applications.
Robustness stores predictions, fold support, tuning and hashes in SQL.

Independent reporters recalculate metrics from stored predictions, check losses,
paired keys/outcomes, four-model rows and fitted pipeline bytes. Reports read
authoritative SQL summaries. `study_results.within_tables(scheme)` verifies each
validation scheme; `study_results.transfer_tables()` verifies all six directions;
`study_robustness_results` exhaustively verifies every registered sensitivity.
`study_interpretation` checks source hashes and reconstructs frozen XGBoost target
predictions/contribution sums; target calibration coefficients are descriptive
evaluation only and never modify a model. `study_report` generates aggregate
tables, public figures and the research handover. Completed exports refuse
overwriting, including presentation artifacts.

Preservation verification:

```sh
.venv/bin/python scripts/study_preservation.py --verify-store --database
.venv/bin/python scripts/study_spatial_check.py
THESIS_STUDY_DB_TEST=1 .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q src/study src/reporting scripts tests
git diff --check
```

The preservation inventory checks1,696 protected original files,263 archived/
unchanged tracked baseline files,20 original dedicated-store tables, five
protected analytical fingerprints and22 original migration hashes. These counts
describe the preservation audit; public output hashes are recorded separately.
Only reviewed aggregate tables/figures and documentation may be published;
raw/restricted data, individual coordinates, folds, models, credentials and
listing-level predictions remain ignored and private.

Publication review uses `python -m src.reporting.study_publication` and
`python -m src.reporting.study_findings`. These consume verified SQL summaries,
preserve the original generated report/figures, and create corrected presentation
artifacts plus code-generated interpretation. No model, sample, statistic,
feature or threshold changes. The initial and publication inventories retain
separate checksums. Actual association-execution status is distinguished from
the frozen sample's earlier readiness label.

After all fits and release audits completed, only the CLI status/entry guards
were updated to expose the actual blocked release and refuse accidental refits.
Exact pre-release CLI bytes are archived at
`history/implementation/cli_before_release.py`; their checksum matches the
fitted packages' source-code dependency. Analytical source/model modules remain
unchanged. Status intentionally returns2 while the scientific inference gate is
blocked; it still reports three fitted predictive cities and six completed transfers.

The final code-snapshot audit also found an intermediate evaluation-driver
digest recorded while primary fits were running, before transfer model-file
serialization was added. Exact bytes are recovered by combining the committed
primary driver with the preceding committed transfer function; the recovered
SHA256 exactly equals the immutable recorded digest, not an inferred equivalent.
They are preserved at `history/implementation/evaluation_before_transfer_artifacts.py`.
The primary fitting/contribution code and every estimation/preprocessing module
are identical; the later difference only saves transfer pipeline bytes and
directional artifact identities. `study_publication_check.py` verifies every
fitted package's recorded source snapshot against current or exact archived bytes.

Git work is exclusively on `v4` with the recorded origin and main base. Every
checkpoint uses normal incremental commits and `git push origin HEAD:refs/heads/v4`,
followed by remote/local SHA equality. The final commit's own SHA is supplied in
the external handover, not written into that commit. `main`, `v3`, tags and the
existing detached worktree are preserved.
