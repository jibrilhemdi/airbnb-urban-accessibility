# A01 current-state and dependency audit — 11 October 2026

Active scientific design: `v4_accessibility_only_20261011`.
Checkpoint state: **PARTIAL — documentary amendment adopted; new-design runtime
and empirical readiness BLOCKED pending A02–A07 and city inputs**. A01 runs no
acquisition, source import, migration, route building, H assignment or models.
V3 results and housing feasibility were already known. No supervisor approval
or retrospective preregistration is claimed.

## Git and instruction evidence

Actual project root:
`/Users/jibrilhemdi/Documents/Projects/thesis-urban-accessibility`.
Root AGENTS is the applicable instruction source; inspected ancestors have no
AGENTS/override. No nested project instructions apply to the edited documents.
Read the previous contract/log, actual V3 specification/deviations/model code,
all active V4 design documents, listing acquisition, dated Stockholm amendment,
housing acquisition/access requirements and the supplied revision.

At entry local HEAD and fetched origin/v4 were both
`25d60d36ef6d6359fbad74c20bc40c48764b7691`, the housing-source checkpoint.
The earlier Stockholm commit `92f607be0ed44db6746bf4b09d2bebe023d6cde3`
is an ancestor, not the current tip. The recorded main base
`c1e919bca9dfbe89de9e67135fb432fdb0f020e6` remains an ancestor; fetched main
still equals it. Local main `7de587997157863e0ba1d36c3f39bdd45f2b9d23`,
local v3 `6150e3f3b4e6db01dd5bf5842404212343d1344a`, and detached
`.kilo/worktrees/storm-acoustic` at the local-main SHA remain unchanged.
Sole remote: existing origin, fetch/push URL
`https://github.com/jibrilhemdi/airbnb-urban-accessibility.git`.
Fetch succeeded; local/remote V4 had no divergence. No staged work or unfinished
merge/rebase/cherry-pick/revert/bisect/sequencer/index lock was found. The only
untracked input was the explicitly authorized revision directory. No branch was
recreated, reset, rebased or merged; no published commit rewritten.

## Revision provenance and explicit discrepancies

All **25 delivered files plus file_manifest.json** are present at
`docs/v4/revisions/accessibility_only_20261011/`; every size/SHA256 matches the
supplied manifest. The manifest itself has SHA256
`f849f25d464dcd873bf21e458e79128a7e03f48782903e065d513b00436af139`.
The bundle remains unchanged. Both supplied Word files were inspected via their
OOXML document text/design stamps and archive membership; no embedded raw-data
or macro file was found. They are reference exports, not regenerated reconciled
active specifications. Authoritative live science is Markdown.

Supplied-input provenance is a separate record, not proof that each referenced
input exists here. Live `thesis_results_v3.zip` matches supplied SHA256
`9a9f494f28944439ee81d391af52317b9ffba568ab362025f60b284df187bd8c`
(12,530,387 bytes). Current Stockholm/housing acquisition/access Markdown hashes
match the supplied input record. The literature matrix and the three named old
external V4 draft/playbook files were not located in the live repository. Their
content or verification is not invented. Imported literature rationale is
attributed to the supplied revision; A01 performs no new literature research.

The supplied `listing_acquisition.md` hash is
`380c5b85bbe20af279250222187a68931e2fa74172ef13a17a01c61d14d8e43c`
for 8,580 bytes. Actual preserved live file is 10,390 bytes with the hash below.
This is an explicit input-version discrepancy, not silently identical provenance.
Use the actual current audit plus selected SQL scopes below; their reported counts
agree with the revision's source-count tables. No original audit is overwritten.

| Live unchanged evidence file | SHA256 |
| --- | --- |
| `listing_acquisition.md` | `4fe869657afad360c53d25890d89ef4793a1e3fd83fb3d79ab0fdfd5c873204a` |
| `stockholm_boundary_amendment_20261011.md` | `e56ed18c0712824e4170719f2cc212078e1925e4b673e4d77d0a598dc898b5f1` |
| `housing_acquisition.md` | `809c535816227807eb43b509701bab521bac3180417630621bc40c9bb83df75d` |
| `housing_access_requirements.md` | `c39fc9c9a1f00f9f16227e56f9e6127453f4bffb436511d5035e2a0b734050ee` |

**Baseline discrepancy:** actual `src/pipeline/model_specification.py` defines
`CATEGORICAL=('property_type',)` and includes it in all four primary and no-income
V3 feature sets. Frozen prior V4 X also includes it. The supplied new prose omits
it and explicitly forbids primary property type in the plan. This is separate
from housing removal. The researcher was asked to resolve it; until clarified,
A01 records membership as pending A02 rather than silently deleting an inherited
control or asserting the two baselines are identical. All 17 inherited numeric/
amenity/context controls remain required. This blocks final executable membership
and fitting, not safe scope-history documentation.

## Authoritative data and selected source scopes

Read-only access verifies PostgreSQL/PostGIS `thesis_accessibility_v4`, isolated
from V3 `thesis_accessibility`. Existing `.env.v4` remains ignored/private;
credentials are neither printed nor changed. Migrations 023/024/025 in
`sql/v4_migrations/` exactly match the applied checksummed ledger. No migration
is appended/applied in A01. Legacy 001–022 and V3 fingerprints are protected by
`protected_v3_manifest.json`.

Select one immutable ingestion per city, never add earlier audit versions as
new observations. Target source namespace remains `research_design_v4` and
snapshot 2026-06-30; the new design must later reference them explicitly by hash.

**copenhagen_frederiksberg**: `research_v4_copenhagen_frederiksberg_20261011T143812Z`; manifest
`e6dedcc9d12545559337cc3a512d97d6a8b8b636cd1ab329ad52dcd13c2e2b13`.

**oslo**: `research_v4_oslo_20261011T143812Z`; manifest
`c08f5ebdaf01ba445cc68e2e0c77b9290c246903f67408013556a071b84252f8`.

**stockholm**: `research_v4_stockholm_20261011T151637Z`; manifest
`d1d923db415dbf2218560947e3fd862657e343317f36fee284fa36e36cc0d172`.

| City | Raw | Dwelling-filtered | Positive-price dwelling | Inside mask + positive dwelling |
| --- | ---: | ---: | ---: | ---: |
| copenhagen frederiksberg | 23144 | 21080 | 12521 | 12508 |
| oslo | 13391 | 11776 | 8557 | 8557 |
| stockholm | 4806 | 3834 | 2510 | 2510 |

These counts were read from the selected authoritative committed ledger and
matched preserved public audit evidence. They are not final S_pred/S_assoc.
Source/audit key QA reports zero invalid/duplicate records in each selected
scope. Missing-price dwellings remain audited: 8,559 / 3,219 / 1,324 respectively.
Batch is 30 June 2026, actual scrapes extend into July, requested stays into 2027;
returned stay dates remain unverified. Quote fields never replace original price.

Stockholm selection uses municipality 0180's SCB-derived RegSO 2025_v2 union
(reference 2025-01-01, native EPSG:3006) with covers in EPSG:4326. Preserve its
127 selected components, accepted temporal limitations and 150 m outer-boundary
counts (96 raw / 69 dwelling / 49 positive). This is operational municipal mask
qualification, not certified June 2026 linework or analysis-area approval.
Original Lantmäteriet 401 receipt/NULL-count ingestions remain frozen.

Oslo's 0301 current-at-retrieval municipal polygon still lacks source vintage.
Its 8,557 count remains provisional for temporal qualification. A01 does not
write a boundary amendment or infer a vintage from Last-Modified/equal area.
Copenhagen plus Frederiksberg remain the joint study scope; official district
and municipal vintages/limitations are retained, no provider labels substituted.

## Preservation inventory and provenance checks

Before edits, **199 existing V4 local source/receipt/manifest/export files** were
captured by hash only to a temporary inventory, then checked unchanged. Existing
SQL summary/manifest/migration ledgers were fingerprinted read-only using
canonical sequence-row JSON (source manifests/period dates serialized explicitly).

| Preserved V4 ledger | Rows | Canonical sequence-row SHA256 |
| --- | ---: | --- |
| listing_ingestions | 13 | `2de6f04c64fbcb1b13ad8f6f7c5a8d333f29b69b8f5e5ddf184b403dae8f5185` |
| housing_ingestions | 3 | `66b8839e8fd1f1ccaf66906736c8f0b64dc8c54f344f2a2574f078ff5505e1ee` |
| source_manifests | 8 | `4d20ad9ba6fb8bf0e56213afe70dce983ee26315cfd1fbb1228cfbec9e2fdfcb` |
| schema_migrations | 3 | `ecc51804504f0f03503ded32cbe8ffcf51eece6a4277e08e6650e79885ef11cd` |

The eight registered manifests' canonical hashes and all **92 manifest-record
source byte checks** pass. All **43 housing receipt pins** pass, including failures;
the original Stockholm 401 receipt hash remains
`4b2f5684acd99a26626b3dd1d3a97b299b7c3e8f9c50f0dcf430784e45d0c041`.
Protected read-only verifier confirms 1,696 V3 files, 22 applied migration hashes
and five analytical SQL fingerprints unchanged. Prior active documents/AGENTS
are copied byte-for-byte into
[the dated historical snapshot](history/housing_standard_20261011_before_A01/README.md)
with a source-commit/checksum manifest; the old step log remains append-only.

V4 empirical model-run count is **zero**. Housing-audit ledgers remain three,
with source rows 2,420 Copenhagen national quarterly / 452 Oslo native annual /
zero Stockholm target rows (actual alternative files preserved). Their original
final BLOCKED statuses and Oslo preliminary QA are unchanged. No H/sample/fold
assignment is created. Reporting/Markdown changes do not change the current
legacy scientific hashes; the new scientific identity is documentary at A01.

## Active dependencies versus retired scope

| Component | New-design dependency status | Required next evidence |
| --- | --- | --- |
| Residential price/access acquisition | NOT_REQUIRED_SCOPE_AMENDED | Preserve history/rights; no provider contact |
| H and price-qualified samples/sales/coverage thresholds | NOT_REQUIRED_SCOPE_AMENDED | Remove from new runner at A02, never spoof qualification |
| H-area folds/ranks/log-H/group analysis/RQ4 | NOT_REQUIRED_SCOPE_AMENDED | Use ordinary qualified/geometric validation, no housing subgroup chapter |
| Executable new model identity and readiness | BLOCKED_PENDING_A02 | Version-isolated canonical registry/guards/hashes/tests |
| Categorical baseline membership | PENDING_EXPLICIT_RESOLUTION | Resolve bundle/live property_type discrepancy before membership freeze |
| Oslo municipal vintage | BLOCKED | Separately requested A03 evidence-qualified recovery/decision |
| Official analysis areas and city metric CRS | BLOCKED / INHERITED_NOT_V4_QUALIFIED | A03 authoritative IDs/vintage/topology/count-based grouping |
| Density/population, income and central anchors | New-city BLOCKED; Copenhagen inherited | A04 compatible sources/crosswalks/reference periods/income mode |
| Matched destinations/network timing and coverage | BLOCKED_PENDING_A05 | Exact source/taxonomy/algorithm/extraction/reuse dependencies |
| Common samples/folds and tuning membership | BLOCKED_PENDING_A06 | No H filter; matched keys, qualified support, frozen 30 candidates |
| Empirical dispatch/checkpoint/resume/estimators | BLOCKED_PENDING_A07 | Implemented synthetic validation; pre-fit manifest |
| City execution/robustness/release | NOT_EXECUTED | A08–A12 separately requested; exact-dependency V3 reuse not approved here |

Income is not property price and is not retired. A common no-income primary
comparative baseline needs an explicit pre-fit decision if harmonisation fails.
Ordinary spatial/inference support remains mandatory. A03 cannot silently use
RegSO components as city districts. Removing H does not qualify an unresolved
context field, permit city omission or authorize expensive fitting.

## Actual code/command boundary and tests

`config/v4/research_design.json` / `src/v4/specification.py` still require
`v4_housing_standard_20261011`, H and log-native housing sensitivity.
`src/v4/cities.py` includes housing in required fields; `runtime.py` still reports
those blockers and unimplemented scientific stages. `persistence.py` uses that
old registry; migration 023 hard-codes old definition/model-ID constraints.
`identity.py` still hashes housing source policy and housing module for the old
scientific identity. These are documented A02 work, not changed or falsely passed
in A01. Existing commands remain as in Makefile; no new command is claimed.

The active proposal/plan/specification/dictionary/model contract/index and AGENTS
now define the new scope. Historical tests that assert housing-default Markdown,
require H dictionary fields, or forbid any V4 DOCX will conflict with this
intentional amendment/input. Identify actual failing methods in the step log;
A02 must retain historical tests under their correct scope and add new-design
checks, not globally disable them. No failed/skipped test is called passed.
Relevant safe checks and precise actual results are appended to
[step_log.md](step_log.md). [step_mapping_A01_A12.md](step_mapping_A01_A12.md)
records supersession and each future acceptance gate. This checkpoint is
PARTIAL/BLOCKED for research readiness; it does not execute A02 or later work.
