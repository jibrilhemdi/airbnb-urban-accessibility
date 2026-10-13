# V4 architecture — accessibility-only registry and preserved sources

Active scientific design: `v4_accessibility_only_20261011`. A02 implements the
registry, scope gates, manifest reuse and identity/persistence extension.
Full research readiness remains **BLOCKED** pending A03–A07. See
[the A02 audit](pipeline_scope_audit_A02_20261011.md),
[the historical architecture](history/housing_standard_20261011_before_A01/architecture.md)
and [the unchanged A01 state audit](current_state_audit_20261011.md).

PostgreSQL/PostGIS `thesis_accessibility_v4` remains authoritative, using only
V4-prefixed settings. Applied migrations 023–025 and raw/audit ledgers are
preserved; append-only migration 026 extends new design identities/guards.
No V3 connection, discovery roots, source data or completed output is changed.

`src/v4/specification.py` / `research_design_accessibility_only.json` provide one
canonical primary registry. Historical `research_design.json` / `cities.json`
and the byte-preserved historical specification remain accessible by explicit
old design ID; their model definitions never become aliases for new M0.
The active city configuration removes housing prerequisites without qualifying
Oslo's vintage or unresolved city context/CRS/anchor/income fields.

Source identity remains `research_design_v4` + city/snapshot/source/manifest hash.
Analytical identity adds `design_id`, with new feature/model paths and cache keys.
Old source paths are reused read-only by exact approved hash without duplicate
imports. Existing acquisition adapters keep their historical Scope default;
the analytical CLI explicitly defaults to the new design. All raw/manifests and
old reports remain in place. Housing adapters/audits and migration 025 remain
historical capability, excluded from required new-design science hashes/paths.
Markdown/Git/reporting edits do not change scientific hashes.

Separate design/model/sensitivity/estimator/validation dimensions and parent-
design SQL checks prevent V3/old-V4/new-V4 label collisions. No record can be
added to a completed run, and no old ingestion can be reopened. Reports export
aggregate metrics only; private listing audit reads are not public exports.

Actual Make commands still use `src.v4.cli`, with analytical `DESIGN_ID` selection
and optional preflight `--source-manifest`; source acquisition/audit entry points
remain unchanged. `scope_check` exercises supplied candidates without filtering
on housing fields; price integrity, ordinary geography, context and accessibility
support remain required. `v4-preflight` reports remaining blocks read-only;
`v4-run` is an empirical refusal stub until separately requested A07 implements
and validates dispatch. No route, sample/fold or fitted estimator is added in A02.

## A04 context-only checkpoints

`make v4-context-acquire`, `v4-context-freeze` and `v4-context-audit` use existing
explicit V4 version/design/city/snapshot/run arguments. They replay pinned native
statistical requests or read approved old sources; independent migration028
links source/geo/listing parents. These are context checkpoints, never model
runs. Only approved Copenhagen geometry permits private many-to-one listing
context. Oslo/Stockholm native source cells remain separate from listing joins,
validation units and primary-income approval. Frozen records cannot be reopened.
See [the A04 audit](context_qualification_A04_20261011.md) for exercised commands,
actual states, source limitations and remaining gates. Read-only preflight checks
selected A04 source/summary evidence, reports its separate states and retains
ordinary feature/support/sample/fold requirements and the income-policy blocker.
