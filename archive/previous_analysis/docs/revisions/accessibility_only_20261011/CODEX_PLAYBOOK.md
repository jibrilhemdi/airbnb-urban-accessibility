# V4 accessibility-only — replacement Codex playbook

11 October 2026 · Design `v4_accessibility_only_20261011` · Continue branch `v4`.

This sequence replaces the remaining housing-inclusive prompts. Do not restart old Prompt 5 or continue its housing Step 6. It resumes after the existing listing/boundary/housing-acquisition checkpoints and preserves their evidence.

## Before starting

1. Download and unzip the revision bundle outside your repository.
2. Copy its CONTENTS into `docs/v4/revisions/accessibility_only_20261011/` in the current project. Do not overwrite old proposal/plan files manually. This intentionally creates new untracked documentation; A01 recognizes that path as this step's input.
3. Open the existing project in Codex with your preferred High reasoning setting. Paste A01. Use one prompt/session at a time; do not run concurrent editing agents on this branch.
4. Continue only after each prior step's required checks and remote push are verified. Do not interpret a safely committed blocker as a passed scientific gate.

The supplied bundle contains documentation/templates, not executable research code or already-run models. Codex must inspect actual repository state and implement/adapt commands. Do not supply credentials in prompts. No housing provider requests or purchases are authorized.

## What changes

M0=X; ME=X+E; MW=X+W; MEW=X+E+W. H, housing-price acquisition, H-qualified samples, price-area folds and H-group analysis are removed. Existing density/income/centrality controls remain subject to their original qualification. No-income remains a separate sensitivity. The accepted Stockholm mask and the unresolved Oslo vintage are not erased.

## Checkpoints

- **A01: Amend the active scope; preserve completed work** — `prompts/A01_amend_scope_and_preserve_evidence.txt`
- **A02: Remove housing requirements from the active pipeline** — `prompts/A02_remove_housing_from_active_dependencies.txt`
- **A03: Qualify city geography and resolve Oslo vintage** — `prompts/A03_qualify_geography_and_oslo_vintage.txt`
- **A04: Qualify population, income and centrality** — `prompts/A04_qualify_baseline_context.txt`
- **A05: Build matched Euclidean and walking accessibility** — `prompts/A05_build_matched_accessibility.txt`
- **A06: Freeze common samples, spatial folds and tuning** — `prompts/A06_freeze_samples_folds_and_candidates.txt`
- **A07: Validate the model pipeline before empirical fitting** — `prompts/A07_validate_models_and_execution.txt`
- **A08: Execute or explicitly reuse Copenhagen results** — `prompts/A08_run_copenhagen.txt`
- **A09: Execute Oslo under the same frozen design** — `prompts/A09_run_oslo.txt`
- **A10: Execute Stockholm under the same frozen design** — `prompts/A10_run_stockholm.txt`
- **A11: Run robustness and compare cities** — `prompts/A11_robustness_and_cross_city_synthesis.txt`
- **A12: Finalize documents and reproducibility handover** — `prompts/A12_release_and_documentation.txt`

Each numbered section below is a complete standalone prompt. Copy only its fenced text; do not combine the entire sequence into one instruction.

---

## A01 — Amend the active scope; preserve completed work

```text
# A01 — Amend the active scope; preserve completed work

The user has changed the research scope: remove residential housing/property prices and only extend the v3 accessibility study to Copenhagen–Frederiksberg, Oslo and Stockholm. This replaces the old housing-inclusive v4 instructions. Continue the EXISTING v4 branch; do not recreate it from main.

First read applicable AGENTS.md, docs/v4/IMPLEMENTATION_CONTRACT.md, the step log, active design documents, actual v3 specification, listing_acquisition.md, stockholm_boundary_amendment_20261011.md, housing_acquisition.md and housing_access_requirements.md. Locate their actual repository paths. Also read the newly supplied revision bundle at docs/v4/revisions/accessibility_only_20261011/.

That newly copied bundle is an explicitly intended untracked input for this step. Stop on any OTHER unrelated tracked/untracked changes, staged work, unfinished Git operations or divergent history. Confirm v4, the recorded remote and prior pushed HEAD; do not assume the reported earlier Stockholm commit is the current tip. Fetch/check safely without resetting or rebasing.

Adopt design_id v4_accessibility_only_20261011:
M0=X; ME=X+E; MW=X+W; MEW=X+E+W.
Y remains log original positive observed Airbnb nightly price. H is removed from every primary model and required sensitivity. Retain density, qualified income, centrality and inherited no-income robustness; do not equate income with residential prices.

Update active proposal, end-to-end plan, pre-analysis specification, dictionary, model contract, document index and AGENTS pointer. Use the supplied revision as the intended scientific amendment, reconciling actual live implementation facts explicitly. Preserve older versions/learning history, not a global text replacement. Log that v3 results and housing feasibility were already known. Do not invent supervisor approval.

Retire property-price acquisition/access, price-qualified samples, housing coverage/sales thresholds, H-area folds and H-subgroup analyses from the new design. Record NOT_REQUIRED_SCOPE_AMENDED separately; do not relabel historically BLOCKED data as qualified.

Preserve all listing/raw/SQL receipts, Stockholm's operational municipal-mask amendment, housing acquisitions and applied migrations. Oslo's boundary-vintage issue and new-city analysis/context qualification remain genuine dependencies. Do not send access requests, redownload Airbnb, build routes or fit models.

Write a current-state/dependency audit and a mapping from old steps to new A01–A12. Mark unexecuted housing prompts superseded. Scope-incompatible tests may be reported as expected pending A02, never falsely passed or weakened globally. If the imported bundle is absent, stop and name the missing path.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: docs(v4): amend scope to three-city accessibility only
```

---

## A02 — Remove housing requirements from the active pipeline

```text
# A02 — Remove housing requirements from the active pipeline

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Inspect active code/configuration/database constraints. Implement the new design without removing historical housing data or rewriting an immutable definition.

Build one canonical primary registry: M0=X; ME=X+E; MW=X+W; MEW=X+E+W. H and all residential-price/rent proxies must be absent from features, SQL selection, model prerequisites, reports and required sensitivities. There is no no_housing variant; this is the primary revised design. Preserve estimator, city, model, validation and sensitivity identifiers separately.

Retain inherited capacity/bedroom/bathroom, rental/host, eight amenity, density, qualified-income and centrality controls. Do not silently alter their definitions. Remove only housing-derived active dependencies.

Trace downstream remnants: H-qualified samples, non-null housing-area joins, annual sales thresholds, 80% housing coverage gates, native-H-area minimums, H reference ranks, H-safe folds, H-group support and housing-source dependency hashes. Retire them explicitly for this design rather than spoofing approvals. Ordinary geographic support tests remain.

Use the existing authoritative PostgreSQL/PostGIS architecture. Inspect actual migrations; add a new append-only migration/definition only if needed. Do not edit applied migration bytes, completed rows, old failure receipts or frozen design policies. Keep historical housing adapters/audits intact and excluded from the new runner's required path.

Allow explicit read-only reuse of approved old listing/source scopes by manifest hash; changing design ID must not trigger duplicate ingestion. New feature/model outputs get new identities. Preserve v3 isolation and current source guards.

Test that a revised pipeline with no housing files and NULL housing-area fields passes this scope check, while invalid Airbnb prices, unresolved required geography and actual context/feature failures still block. Test exact feature membership, model-version isolation and no accidental housing row filters. Do not disable all preflight or suppress historical tests to get a green run.

No new source acquisition, routing or empirical fitting in this step.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: refactor(v4): remove housing from active models and readiness gates
```

---

## A03 — Qualify city geography and resolve Oslo vintage

```text
# A03 — Qualify city geography and resolve Oslo vintage

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Reuse the three acquired June listing snapshots and preserved municipal geometries; verify hashes and chosen ingestion identities. Do not repeat Airbnb downloads or count superseded ingestions twice.

Copenhagen: retain both municipalities and the ten official districts plus Frederiksberg as peer analysis areas. Verify scope/assignment compatibility without forcing acquisition counts to equal v3's final sample.

Stockholm: retain the accepted SCB RegSO 2025_v2 municipal mask, code 0180, reference 2025-01-01. The 127 components are not automatically validation areas. Acquire/qualify official analysis-area polygons and map their IDs/vintage separately; a RegSO analysis option requires its own documented suitability decision.

Oslo: this prompt authorizes a TARGETED boundary-vintage recovery/amendment. Inspect official municipality source, code, licence, change information and available source-dated geometry. Prefer verifiable dated polygons. If exact June 2026 geometry cannot be obtained, operational use of a documented source is authorized only after identity, valid topology, extent, independent metadata/area and relevant change checks support it. Record source/reference/retrieval dates and exact certification limits. Equal area alone does not prove linework identity. Inadequate/conflicting evidence means BLOCKED, not automatic acceptance.

Preserve old receipts and add a separately identified new amendment; do not overwrite or relabel the original uncertainty. Use legitimate public sources, not credentials, purchases, terms acceptance or access-control bypasses.

For Oslo/Stockholm, choose a documented official borough/district level using substantive comparability and price-free listing support. Validate nonoverlap/coverage, stable IDs, source CRS, city-specific metric CRS, deterministic boundary ties and any adjacent-area grouping. Do not choose geography using price-model scores or import old housing-area fold rules.

Report native area and proposed holdout counts, coverage, gross areas and boundary-near flags. Preserve unmatched/uncertain cases in audits; no exact-address inference. Freeze qualified sources, but final fold memberships wait for A06.

No income acquisition, route computation or modelling yet. State which city-dependent tasks are ready or blocked.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: feat(v4): qualify analysis geography and document Oslo vintage
```

---

## A04 — Qualify population, income and centrality

```text
# A04 — Qualify population, income and centrality

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Acquire/validate only the inherited non-price baseline context for the three cities: population density, qualified income and central civic-anchor distance. Housing and property portals remain out of scope.

Preserve Copenhagen's accepted v3 KKIND5/nominal IFOR35 2024 equivalised-disposable-income calculation and its documented caveats. Do not reopen that settled construction merely because H was abandoned. Recover its exact source/selection hashes and formula. Retain v3 density/anchor definitions as the starting point.

For Oslo and Stockholm, prefer official public statistics with explicit reference year, population/household unit, equivalence treatment, native currency, statistic, geography and licence. Use confirmed selectors and boundaries. Do not describe gross earnings, household median and equivalised mean as the same construct. Keep metadata-checked, acquired, joined and accepted states distinct.

Construct log density from documented population and gross matching polygon area. Record water inclusion and source timing; do not substitute listing density or redistribute municipal totals without a justified method. Qualify public anchor coordinates and the appropriate metric CRS per city.

Baseline income policy: retain qualified income in primary X with a matched no-income sensitivity. If a defensible three-city concept cannot be qualified, write a concise pre-fit decision recommending the common no-income comparison and separately labelled local-income models. Do not activate that change or vary the primary concept by city without an explicit researcher decision. Safe context/feature work may continue; empirical fitting must wait for a frozen income mode.

Test many-to-one assignment, native IDs, units, years, missingness, within-city variation, no row multiplication, gross-area calculation and predictor provenance. Do not globally impute missing predictors. Carry source qualifications into the active dictionary.

Report exact resolved and outstanding context requirements. No walking routing, sample freeze or model fits in this step.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: feat(v4): harmonize baseline population income and centrality
```

---

## A05 — Build matched Euclidean and walking accessibility

```text
# A05 — Build matched Euclidean and walking accessibility

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Reuse the v3 algorithms where scientifically compatible. Begin with an outcome-blind audit of city qualification and graph/destination source dates. Do not route a geography-blocked city or silently mix different OSM observation policies.

Reuse Copenhagen features only if source, taxonomy, algorithm, CRS, scope and extraction dependencies match the new design. Otherwise compute separate v4 features; never overwrite v3. Explicitly link cached artifacts to their originating source manifests, not a guessed path.

Keep identical eligible destination universes for E and W within each city: rail/metro/commuter stops, consolidated bus stops, food/social and culture/tourism opportunities. Preserve exact v3 taxonomy and identity-compatible consolidation; log local tagging exceptions before fitting. Do not choose categories using Airbnb price results.

Baseline: exactly 5 km/h; 10-minute walking opportunities; rounded 833-metre Euclidean opportunities; nearest rail and bus separately; E distances in km, W in minutes; log1p counts. Nearest eligible objects may differ by representation. Include origin/destination connector distances and actual pedestrian restrictions/topology.

Use city-appropriate metric projections. Start with the declared >=2 km extraction buffer, expanding where coverage/nearest-destination audits demand it. Keep listing study boundaries distinct from the wider graph/POI extent. Do not join bridges or underpasses merely because geometry is nearby.

Distinguish genuine zero opportunities, unreachable destinations and missing source/routing data. Test snaps, connectors, route lengths, disconnected components, E/W bounds within rounding tolerance and common candidate universes. Preserve the inherited 15/20-minute, speed and decay interfaces without fitting models.

Write feature and measurement-coverage audits; describe residual OSM timing limitations rather than claiming a reconstruction of June 2026. No housing data checks or geographic housing joins may execute.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: feat(v4): extend matched accessibility features to all cities
```

---

## A06 — Freeze common samples, spatial folds and tuning

```text
# A06 — Freeze common samples, spatial folds and tuning

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Read the approved geography/context/feature decisions. No empirical fitting or model-score inspection is permitted in this step.

Build one S_pred per city: inherited eligible entire-dwelling sample, positive original Airbnb price, valid operational scope/analysis assignment and common E/W feature support. ALL FOUR models share identical ordered keys/outcomes. Do not start from an old H-qualified subset or filter NULL housing fields. Keep the larger audit universe and sample attrition.

Define the common OLS association sample separately under the inherited <=5% any-required-predictor missingness rule. Above it, flag association inference only as blocked pending a validated amendment; do not substitute globally imputed inference. Learned prediction preprocessing stays inside training later.

Primary outer folds: Copenhagen's qualified eleven official areas; qualified Oslo/Stockholm official areas with deterministic, pre-fit sparse-area grouping if justified. Apply the explicit revised >=500 train/>=30 test rule and report actual K. No outcome-driven grouping or invented 11-cluster labels.

Freeze random five-fold benchmarking and common 1.5 km five-fold geometric blocks at zero and half-block origins. Preserve the broader inherited robustness registry. No H-area nesting rules.

Use four training-only spatial inner folds based on 1 km blocks and the inherited deterministic balancing/seeds. Recover and hash the exact 30-candidate v3 list; reconstruct only if genuinely absent, with a documented deviation. Verify inner feasibility and outer-test exclusion.

Freeze observation/fold manifests, source/feature hashes, candidate list, income mode, all five contrasts and robustness priorities. Comparisons are ME-M0, MW-M0, MEW-M0, MW-ME and MEW-ME; note the last is explicitly added in this amendment.

If the primary income mode or a required city input remains unresolved, checkpoint honestly and do not release that empirical run. Do not remove a city or income silently. Test pairing, disjointness, count rules and reproducibility.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: feat(v4): freeze accessibility samples spatial validation and tuning
```

---

## A07 — Validate the model pipeline before empirical fitting

```text
# A07 — Validate the model pipeline before empirical fitting

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Implement/reuse predictive OLS and XGBoost from one canonical registry: M0=X; ME=X+E; MW=X+W; MEW=X+E+W. Assert no residential-price columns, H-derived filters or housing requirements anywhere in the active execution path. Keep no-income sensitivity distinct from the primary model identity.

Use the frozen common city samples/folds/candidates. Fit learned preprocessing inside each inner-training split and refit only on outer training. No global imputation, outer-test early stopping, outcome-driven feature deletion or reduced city tuning budget. Entirely missing required training predictors fail explicitly.

Persist private OOF outcomes/predictions/losses, city/design/model/estimator/fold identity, candidates, selected parameters, seeds, source/feature/sample/fold hashes, environment and scientific code revision. Compute all five paired comparisons from saved OOF rows. Negative Delta RMSE favours the added model; include proportional reductions, MAE, defined R2 and equal-area summaries. Keep train_mean as a separate benchmark.

Validate association OLS, HC3, actual-area WCR11 inference and Moran/spatial-error interfaces separately. Do not invent eleven clusters in new cities. Preserve inherited robustness and held-out SHAP handling.

Implement stage checkpoints and resume only for matching immutable scientific dependencies. A code/data/design change affecting estimates creates a new identity and marks affected earlier city runs for replacement. Reporting-only changes do not relabel fitted results.

Run synthetic end-to-end tests, intentional leakage/wrong-city/missing-feature failures, interruption/resume tests and authoritative database checks. Synthetic results must never enter research namespaces or thesis tables.

Document the true fit budget (484K XGBoost fits per geographic city run, before sensitivities), available resources and an execution manifest. Do not promise completion or run empirical pilots that change the design based on scores. A08 is the first authorized empirical step.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: feat(v4): validate accessibility models and checkpointed execution
```

---

## A08 — Execute or explicitly reuse Copenhagen results

```text
# A08 — Execute or explicitly reuse Copenhagen results

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

This prompt authorizes the frozen Copenhagen–Frederiksberg empirical analysis, not supervisor approval or any unapproved scientific change.

First require qualified sources, context/income mode, sample, folds, candidates, tests and immutable run manifest. Inspect whether the completed v3 artifacts exactly match the revised outcome, row set, controls, source/feature policy, transformations, folds, tuning and estimator implementation.

If exact reuse is defensible, create an explicit read-only v4 evidence linkage to the original v3 artifact/commit/hash. Do not copy values into a new table and pretend they are a new fit. Derive the new MEW-ME contrast from matched saved OOF predictions only where available and verified. If any substantive dependency differs, run new v4 estimates and explain the difference; never force N to 12,412 or overwrite v3.

Execute the prescribed predictive OLS and XGBoost ladders M0/ME/MW/MEW without H, under geographic and random validation as budgeted. Use full frozen tuning and paired samples. Execute separately eligible association components; report exact blockers rather than substitute imputed inference.

Verify one OOF prediction per observation/model/estimator/scheme, shared outcomes/folds, no housing predictors, candidate provenance and independently recomputed metrics. Record current scientific-code/run identities before fitting. Protected v3 and source receipts remain unchanged.

Checkpoint interrupted work truthfully as PARTIAL with an implemented resume command. Do not fabricate completed folds, silently reduce candidates or adopt a favourable sensitivity. Export only safe aggregates/manifests.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: run(v4): complete Copenhagen accessibility-only primary analysis
```

---

## A09 — Execute Oslo under the same frozen design

```text
# A09 — Execute Oslo under the same frozen design

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

This prompt authorizes only the frozen Oslo empirical analysis. Require the accepted Oslo municipal-vintage decision, official analysis areas, qualified context/income mode, matched E/W features, S_pred, folds/candidates and passing tests.

Do not inherit Copenhagen's currency, anchors, area IDs, CRS or counts. Use Oslo's recorded scope and source-manifest identity while preserving the common scientific definitions.

Run predictive OLS and XGBoost for M0, ME, MW and MEW without H, under the geographic and random schemes. Keep identical Oslo observations/folds across models and the complete frozen search budget. Run association inference only when separately qualified, with actual valid area clusters.

Persist and verify complete OOF rows, selected parameters, source/code lineage and all five paired contrasts. Independently recompute RMSE/MAE/R2 and relative changes. Report K, N, support limitations, missingness and actual completion.

A missing housing source must not block Oslo; unresolved real geography, context decision or feature data must. Do not silently switch to random-only evaluation or omit a city.

If a shared scientific-code bug is discovered, fix it in a separate versioned identity and record which prior Copenhagen results require replacement. Preserve superseded artifacts. Do not combine city scores produced by meaningfully different algorithms as an unchanged protocol.

Checkpoint partial or blocked work honestly. Do not run Stockholm or merge v4 into main.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: run(v4): complete Oslo accessibility-only primary analysis
```

---

## A10 — Execute Stockholm under the same frozen design

```text
# A10 — Execute Stockholm under the same frozen design

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

This prompt authorizes only the frozen Stockholm empirical analysis. Require its accepted operational municipal mask and independently qualified analysis areas, context/income mode, source/feature manifests, common S_pred, folds/candidates and tests.

The 127 SCB components in the municipal boundary amendment are NOT automatically 127 analysis clusters. Preserve the actual approved analysis/fold definition. Do not reopen property-price access or impose housing-transaction-count/coverage thresholds.

Run predictive OLS and XGBoost for M0, ME, MW and MEW without H, with geographic and random validation and the full common tuning budget. All models share the same Stockholm observations/folds. Use native currency and the verified city-specific metric CRS and anchor.

Verify observed-price validity, paired OOF completeness, whole official-area primary holdouts, candidate/code lineage and independently recomputed metrics. Respect actual smaller-sample fold feasibility; no outcome-based area merging or reduced model search.

Run the association component only when its separate missingness/inference requirements pass. Document operational-boundary and source-coordinate uncertainty. No missing housing dataset is a blocker under this design.

Preserve earlier city estimates. Shared scientific changes require identified affected reruns before comparative claims. A blocked city is reported as blocked, not silently replaced with provider labels or excluded from the thesis title.

Checkpoint truthfully, export safe aggregates and stop before synthesis.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: run(v4): complete Stockholm accessibility-only primary analysis
```

---

## A11 — Run robustness and compare cities

```text
# A11 — Run robustness and compare cities

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Use the frozen protocol and saved OOF evidence. Require comparable city definitions; do not silently mix old v3, housing-inclusive v4 and new estimates. Authorized reuse must retain its actual original identity.

Execute the registered robustness programme in its frozen priority order: matched no-income; apartment/condo and reviewed samples; training-only price trimming; reputation controls; matched 15/20-minute, speed and decay alternatives; geometric blocks and buffers; location/boundary uncertainty; eligible association/spatial checks. All variants exclude H. No-income changes only income on the declared common sample/folds.

For every check, report COMPLETE, INFEASIBLE, DEFERRED, FAILED or NOT_APPLICABLE with reasons and dependencies. Do not quietly trim held-out observations, change candidate budgets, average unmatched fold metrics or remove unfavourable results. Explicit scope/resource amendments remain visible.

From paired OOF rows compute ME-M0, MW-M0, MEW-M0, MW-ME and MEW-ME for each city and estimator. Use 2,000 paired geographic group resamples as stability summaries; acknowledge overlapping training sets and few groups. Negative Delta RMSE favours added features. Add proportional improvements, equal-area summaries, K/N and support diagnostics.

Address RQ1 with E/W route/opportunity comparisons, RQ2 with paired model gains, and RQ3 with administrative/random/common-geometric comparisons. Do not regress national effects on three city estimates or claim gentrification, causal amenity values or observed tourist routes.

Route disagreement versus gain can be an explicitly exploratory interpretation using existing features, not a new mandatory RQ or excuse for additional datasets. No H-subgroup chapter.

Retain raw/city prices separately. Build safe aggregate comparative tables/figures using established project presentation conventions, privacy suppression and actual source licences.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: analysis(v4): evaluate robustness and comparative accessibility gains
```

---

## A12 — Finalize documents and reproducibility handover

```text
# A12 — Finalize documents and reproducibility handover

Read applicable AGENTS.md, the active v4 implementation contract, step log and the revised proposal/plan under docs/v4/revisions/accessibility_only_20261011/. Inspect actual paths and commands; do not invent them. Work only on the existing v4 branch. Implement only this prompt, then stop.

Generate the final research outputs from authoritative saved results, not manually entered metrics. Do not trigger unbudgeted duplicate full fitting during reporting.

Update the active revised proposal, end-to-end plan, pre-analysis/deviation record, dictionary, README, document index and claims-to-output audit to the ACTUAL implemented scope. Preserve the pre-fit versions and amendment history. If a city or required component is incomplete, state it and do not invent three-city completion.

All primary tables use M0, ME, MW and MEW without residential prices, with design/estimator/variant keys. Keep reused v3 and superseded housing-inclusive evidence separate and truthfully labelled. Remove active requests to acquire housing, H-qualified samples/folds and H-based claims, not their historical audit trail.

Deliver source/period/geography and sample-flow tables, variable definitions, E/W measurement diagnostics, fold maps, city metrics and all five paired contrasts, relative-gain synthesis, robustness status, association/spatial results and limitations. Distinguish association, prediction and causation throughout.

Run the full relevant tests, database/provenance checks, canonical feature and no-housing-dependency checks, v3-preservation checks and independent metric recomputation. A skipped required test is not a pass. Verify scientific hashes versus reporting-only changes and non-destructive reproducibility.

Review data sharing and map suppression: no identifiers, coordinates, private predictions, restricted extracts, credentials or unlicensed source material in Git. Regenerate current DOCX documents using the supported workflow and visually inspect them; otherwise clearly mark authoritative Markdown and stale exports.

Write release status and an exact completion/blocker report. Commit and push only v4. Do not modify main/v3, create a tag, open/merge a pull request or publish outside the repository without a separate request.

Completion protocol: run relevant tests and source/provenance checks; inspect the diff; update the step log; stage only intended safe files; commit with the message below; push HEAD explicitly to the recorded remote's refs/heads/v4; verify remote SHA equals local HEAD. Never force-push, modify main/v3, auto-stash, rewrite published history, upload private/raw data or merge a pull request. Stop on unrelated edits, ambiguous/divergent Git state or unverified dependencies. A blocked scientific task can have a safe documentation/code checkpoint, but report BLOCKED/PARTIAL; a failed push is LOCAL_ONLY and pauses the sequence. Report actual tests, files, run status, blockers, commit SHA and push verification. Do not put a commit's own SHA inside itself.

Commit: docs(v4): finalize accessibility-only research and reproducibility
```
