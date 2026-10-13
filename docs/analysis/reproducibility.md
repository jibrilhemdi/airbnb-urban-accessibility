# Reproducing the active study

The canonical design is `config/study/design.json`; scientific decisions,
source/time/CRS/receipt hashes and immutable SQL selectors are under
`config/study/` and `docs/analysis/`. Use `.venv/bin/python` and the pinned
single `requirements.txt` (including the existing openpyxl pin). The generated
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

The current preservation inventory checks1,695 protected original files,263 archived/
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

Before the association amendment, the CLI status/entry guards were updated to
expose the then-blocked release and refuse accidental refits.
Exact pre-release CLI bytes are archived at
`archive/implementation/cli_before_release.py`; their checksum matches the
fitted packages' source-code dependency. Analytical source/model modules remain
unchanged. That historical status returned2 while inference was blocked; current
status reports the completed amended scientific execution.

The final code-snapshot audit also found an intermediate evaluation-driver
digest recorded while primary fits were running, before transfer model-file
serialization was added. Exact bytes are recovered by combining the committed
primary driver with the preceding committed transfer function; the recovered
SHA256 exactly equals the immutable recorded digest, not an inferred equivalent.
They are preserved at `archive/implementation/evaluation_before_transfer_artifacts.py`.
The primary fitting/contribution code and every estimation/preprocessing module
are identical; the later difference only saves transfer pipeline bytes and
directional artifact identities. `study_publication_check.py` verifies every
fitted package's recorded source snapshot against current or exact archived bytes.

Git work is exclusively on `v4` with the recorded origin and main base. Every
checkpoint uses normal incremental commits and `git push origin HEAD:refs/heads/v4`,
followed by remote/local SHA equality. The final commit's own SHA is supplied in
the external handover, not written into that commit. `main`, `v3`, tags and the
existing detached worktree are preserved.


## Association amendment and consolidated layout

The uniform eligibility limit changed from 5% to 10% only after Stockholm's
missingness was observed; this is an explicit post-observation amendment.
Complete cases, outcomes, X/E/W, HC3, 9,999 Webb draws, Moran k8/499 and frozen
spatial triggers are retained. All three association ladders and dependent
checks were freshly computed, independently recalculated and published from SQL.
Completed predictive fits, transfers, features, samples, folds and SHAP are
preserved. The release audit verifies exact fitted-code snapshots, all saved
model bytes, prediction-package hashes and source-only transfer reproduction.

Use the single `.env`: STUDY_DB_* selects the dedicated source/research connection,
while DB_* selects the preserved historical connection. Neither inherits the other's settings.
The public setup template is `config/environment.example`; `.env` is the only
environment file at the repository root and remains ignored.
Python 3.13.5 is recorded in requirements.txt and software_environment.json;
there is no second active dependency file or separate .python-version file.
Source-provenance adapters are under src/provenance; previous version-labelled
code/config/docs/migrations/test interfaces and previous history/ contents are
consolidated under archive/. Applied SQL filenames, source IDs and database
names remain recorded identities. The archive manifest resolves old paths to
exact original bytes; no scientific value is fabricated during relocation.
The researcher explicitly excludes the discarded thesis_results_v3.zip from
current preservation verification; its original manifest entry is retained.

Completed selectors cannot be overwritten; a reproduction needs explicit new
reporting identities. Public inference outputs are association_execution_status,
association_coefficients, association_vif, association_diagnostics,
association_residual_moran, association_spatial_execution and
spatial_association_coefficients CSVs under outputs/tables/research/, plus the
association coefficient figure. The immutable sample audit still records the
historical 5% gate status; current execution comes from fresh selectors/audit.
Older partial reports and all 72 preceding public artifacts remain byte-
preserved at current or archived paths.

## Reproducing the thesis reporting layer

One root `.env`, one `requirements.txt` and the audited environment are used.
The final source catalog pins all751 analytical packages, selected summaries,
private prediction hashes and77 preceding public artifact hashes. Reporting
reads SQL without fitting or modifying research packages. CSVs are documented
aggregate exports, not replacement analytical stores.

```sh
make thesis-outputs
make thesis-synthesis
make thesis-check
make thesis-science-check
make thesis-release
```

Outputs are write-once; generation commands refuse to overwrite completed
exports. Use the separate check commands to verify existing bytes. The explicit
layout revision option applies only to an unpublished presentation draft,
requires byte-identical numerical exports and archives its initial manifest.
It cannot overwrite a certified thesis delivery. Reporting modules contain no
scientific fit calls. The scientific checker reuses the existing read-only
release verifier while capturing its report separately; it never overwrites
the completed scientific audit. It reproduces primary and transfer RMSE from
saved predictions and verifies all saved fitted pipeline bytes.

`reports/thesis_artifact_manifest.json` registers every public output with its
final run, RQ, generator and SHA256. `reports/thesis_synthesis_manifest.json`
and `reports/numeric_claims_registry.json` trace generated prose to those
outputs. New PNGs are300dpi, with PDF/SVG companions; aggregate cells and
prediction-display bins suppress counts below five. Release manifests and the
deterministic ZIP contain only reviewed figures, aggregate tables and documents.
Markdown is authoritative; the repository has no supported active DOCX/PDF
document-generation workflow for this four-RQ design.
