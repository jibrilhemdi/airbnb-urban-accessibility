# V4 implementation contract — accessibility-only amendment

Design ID: `v4_accessibility_only_20261011`. Amended 11 October 2026,
Europe/Copenhagen. Continue the existing `v4` branch. Read this contract,
[step_log.md](step_log.md) and applicable AGENTS/override instructions at every
step. The latest user amendment supersedes housing-default instructions.
Older contract bytes are preserved in
[the historical snapshot](history/housing_standard_20261011_before_A01/README.md).

## Authority, history and current step

A01 adopts the supplied revision bundle under
`docs/v4/revisions/accessibility_only_20261011/`, reconciles actual repository
facts and documents dependencies. Only this directory was preauthorized as
untracked input; stop on any other unrelated edits/staged work/unfinished Git
operation. The bundle contains proposed documents/templates, not implemented
pipeline code, source qualifications or completed runs. V3 results and housing
feasibility were already observed. Supervisor approval is not recorded; there
is no retrospective preregistration claim.

Implement only the explicitly requested A-step. A01 authorizes document/scope
changes and read-only/source-preservation checks, not A02 dependency refactoring,
new migrations, provider contact, listing downloads, geography acquisition,
routing, samples/folds or empirical fitting. A02 was separately requested and implements the scope/identity transition,
including append-only migration 026 and read-only checks. A03 was separately
authorized for geography/source-vintage qualification only; its
[dated audit](geography_qualification_A03_20261011.md) records partial qualification,
append-only migration 027 and genuine new-city analysis-area blockers. A04–A12
remain future instructions and require their own user request. Synthetic fixtures are tests, never research
results. A safe PARTIAL/BLOCKED checkpoint does not pass scientific gates.

## Scientific model contract

| Model | Required blocks |
| --- | --- |
| M0 | X |
| ME | X + E |
| MW | X + W |
| MEW | X + E + W |

Y is `log_price=log(price_nightly)`, from original positive observed Airbnb
nightly asking price, never statistically imputed or replaced by quote fields.
Reuse the verified 30 June 2026 batch; scrape/requested/returned-stay dates are
separate. Retain separate native-currency city OLS/XGBoost models for exactly
`copenhagen_frederiksberg`, `oslo`, `stockholm`. No temporal panel, residential
outcome, gentrification score or causal housing/displacement claim.

X retains inherited listing/host/rental/amenity controls, population density,
qualified income and centrality; E/W are matched Euclidean/walking measures.
A02 retains inherited categorical `property_type` under the instruction to remove
only housing-derived dependencies; this explicitly supersedes the supplied prose
exclusion as recorded in [model_contract.md](model_contract.md). Do not silently change X.
No H or residential-price/rent proxy enters any primary model or required
sensitivity. There is no `no_housing` variant: accessibility-only is the primary
revised design. Mandatory no-income removes only qualified income on matched
rows/folds; income is distinct from property prices. New-city income requires
qualification; a common no-income primary mode needs an explicit pre-fit
researcher decision, never a silent fallback.

RQ1 measures representation differences; RQ2 tests paired predictive information;
RQ3 compares cities/validation settings. Housing RQ4 is withdrawn. Report all
five contrasts: ME/M0, MW/M0, MEW/M0, MW/ME (replacement), MEW/ME (add-on).
MEW versus ME is an explicit reporting amendment relative to v3's four named
contrasts, already named in housing-inclusive V4. Negative added-minus-reference
error favours the added model; crossing zero is not equivalence.

One common accessibility-supported prediction sample per city serves all four
models; separately document common OLS association complete cases of X+E+W.
Above 5% required-predictor missingness, association inference pauses pending
validated treatment. Learned prediction preprocessing/tuning uses training data
only; never select variables, thresholds, taxonomy or hyperparameters from outer
outcomes. Preserve 30 candidates, four inner spatial folds, inherited thresholds,
no-income robustness, inference and diagnostics. New-city >=500 train/>=30 test
primary folds and common 1.5 km geometric checks are explicit revised safeguards,
not power guarantees. Actual qualified areas determine clusters, not 127 RegSO
components or an assumed eleven-city count.

## Retired and genuine dependencies

Property acquisition/access requests, H-qualified samples, housing-sale/coverage
thresholds, native-price-area folds, H subgroup/rank and log-H analyses are
**NOT_REQUIRED_SCOPE_AMENDED**. Preserve historical BLOCKED/preliminary source
statuses separately; never mark those sources QUALIFIED to bypass old code.
Housing requests remain unsent and are not to be pursued under this sequence.

Stockholm's documented SCB-derived 2025 operational municipal mask remains
RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT, not certified 2026 linework and not
automatically analysis geography. The original Oslo municipal-vintage blocker remains historical evidence;
current operational qualification is the separate A03 amendment below.
A03 resolves Oslo municipal vintage only through its dated operational
[amendment](oslo_boundary_amendment_A03_20261011.md); the original uncertainty
remains preserved. Copenhagen inherited analysis assignment is qualified with
reported registration limitations; Oslo/Stockholm analysis geography stays BLOCKED.
City metric CRS is source-qualified separately through A03 evidence.
Official analysis/context geography, public anchors, population,
income mode, matched destinations/networks, common support and fold identity
remain genuine required gates. Do not omit a city without an explicit amendment.

## Persistence, identity and privacy

PostgreSQL/PostGIS `thesis_accessibility_v4` remains authoritative with dedicated
`.env.v4`/V4_DB settings, never V3 `.env`/DB settings. CSVs are inspection/export,
not alternative stores. Preserve raw bytes, immutable receipts/ledgers, completed
V3 artifacts and applied migrations 001–025 in their respective discovery roots.
Migration 026 extends only the new-design schema/guards; original rows stay intact.
Migration 027 adds independent immutable geography receipts/areas/private audits,
without editing old rows, creating model runs or freezing final folds.
Never update/delete/truncate historical data or regenerate frozen V3 documents
merely to test. Source manifests are reused by verified hash, not redownload or
duplicate ingestion. Fitted V3 reuse requires an explicit exact-dependency audit
and truthful original provenance at A08; A01 approves no fitted reuse.

The new design requires version-qualified model identity distinct from V3 and
`v4_housing_standard_20261011`. A01 does not relabel their SQL rows or frozen
configuration. [The A01 state audit](current_state_audit_20261011.md) preserves the earlier
runtime constraints; [the A02 audit](pipeline_scope_audit_A02_20261011.md) records
the new registry, append-only migration 026 and remaining genuine gates. New feature/model outputs need separate design,
run, city, snapshot, estimator, model, validation and variant identities. Preserve
existing scientific-versus-reporting hash separation.

Never upload raw/restricted data, credentials, dumps, listing coordinates,
private predictions/folds/SHAP or individual rows. Keep current ignored V4
raw/intermediate/report/output roots. Public maps use 500 m cells and suppress
fewer than five observations. Record source/date/extent/checksum/licence and CRS;
never invent missing values or mappings. Every table/figure is code-reproducible.

## Git completion protocol

Recorded remote: `origin`, existing URL
`https://github.com/jibrilhemdi/airbnb-urban-accessibility.git`.
Recorded main base: `c1e919bca9dfbe89de9e67135fb432fdb0f020e6`.
Prior pushed A01 starting HEAD: `25d60d36ef6d6359fbad74c20bc40c48764b7691`.
Keep the existing branch; do not recreate/reset it, rebase, merge later main,
auto-stash/discard others' work, amend published commits, force-push, change tags,
modify/push main/v3 or open/merge a PR. Fetch the existing remote; stop on ambiguity,
divergence, unfinished operations or unrelated edits. Preserve all worktrees.

Before finishing each step:

1. Run relevant checks and source/provenance preservation verification. Scope-
   incompatible assertions may be expected pending A02, identified by exact
   test/reason; never claim a failed/skipped test passed or weaken global gates.
2. Inspect the diff; update the step log; stage only intended safe paths and
   inspect the staged diff. Confirm active branch `v4`.
3. Commit with the requested message. Never record that commit's own SHA in it.
4. Push `HEAD` explicitly to `refs/heads/v4` on recorded origin (upstream already
   exists); verify `git ls-remote --heads origin refs/heads/v4` equals local HEAD.
5. Report actual tests/files/run status/blockers/commit SHA/push verification.

Push failure means **LOCAL_ONLY** and pauses the sequence. Missing scientific
inputs mean **BLOCKED/PARTIAL**, not invented substitutes or permission for
later empirical work. Completion of A01 is not completion of the study.
