# V4 architecture — current implementation versus adopted design

Active scientific design: `v4_accessibility_only_20261011`. A01 is documentation
adoption only. The existing executable/storage definition remains
`v4_housing_standard_20261011` in namespace `research_design_v4`, pending A02.
See [the exact historical architecture](history/housing_standard_20261011_before_A01/architecture.md)
for preserved implementation detail and [the state audit](current_state_audit_20261011.md)
for current, verified source scopes. No new-design runner is ready or claimed.

PostgreSQL/PostGIS `thesis_accessibility_v4` remains authoritative, with separate
V4-prefixed connection settings and five V4 schemas. Applied migrations 023
(isolation/persistence), 024 (listing/boundary audit), 025 (housing-source audit)
are unchanged. V3 uses its own database/discovery roots and completed run.
No database/schema migration or source ingestion occurs in A01.

Existing Paths/Scope/raw-manifest/cache/persistence guards enforce version,
run, city, snapshot, source identity, provenance and append-only records. Keep
all raw/manifests/exports in their original paths and reuse sources by verified
hash. New feature/model outputs must have a separate scientific identity after
A02 implements it. Never reopen committed source ingestions or relabel old
models. Existing cache reuse requires all scientific dependencies to match;
Markdown/Git/reporting changes are separate. Housing policy/modules still enter
the old scientific hash and must be decoupled from the new runner at A02 without
changing their historical bytes/meaning.

Actual Make targets remain setup/test/test-db/preflight/run/report plus listing
acquire/ingest/audit, Stockholm boundary recovery and historical housing source
audit commands. Their actual entries are `src.v4.cli`, `src.v4.listings`,
`src.v4.stockholm_boundary`, `src.v4.housing`, as wired in the Makefile. The
legacy `v4-run` remains a preflight refusal stub, not an empirical fit command.
A01 invokes no acquisition, routing or run target. Do not pass the new design
ID to an old command and pretend it supports that identity. A02 must implement
and test any new/changed selection before it is advertised as operational.

New-design scientific housing dependencies are NOT_REQUIRED_SCOPE_AMENDED.
Historical housing adapters/tests/tables remain, but their current presence or
old blockers do not establish new-design readiness. Genuine price integrity,
municipal vintage, analysis geography, context policy, matched accessibility,
samples/folds and estimator validation still block empirical execution. All
private roots remain ignored; no sharing infrastructure changes are authorized.
