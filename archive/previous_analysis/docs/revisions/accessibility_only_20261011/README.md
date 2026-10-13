# Airbnb thesis — revised v4 accessibility-only package

**Decision:** drop residential property prices and expand the existing accessibility study to Copenhagen–Frederiksberg, Oslo and Stockholm.

**Design ID:** v4_accessibility_only_20261011. **Branch:** continue existing v4.

## Start here

Read docs/scientific_proposal_v4_accessibility_only.docx for the research argument and docs/end_to_end_plan_v4_accessibility_only.docx for execution. Identical-content Markdown sources are included.

To use Codex: unzip this bundle outside the repository, then copy its CONTENTS into docs/v4/revisions/accessibility_only_20261011/ in your current project. Do not manually overwrite the older active documents or delete old housing files. This intentional new directory is allowed as A01 input; unrelated edits are not.

Open the project in Codex and paste prompts/A01_amend_scope_and_preserve_evidence.txt. Then use A02–A12 sequentially. Each step updates the log, tests, commits, pushes only v4 and verifies the remote SHA. CODEX_PLAYBOOK.md includes every complete standalone prompt. RECOVERY_PROMPT.txt covers interrupted work/pushes.

## Contents

- docs/: updated scientific proposal and end-to-end plan (Word + Markdown).
- prompts/: twelve complete copy-paste checkpoints.
- support/: revised pre-analysis specification, implementation contract, source registry, scope change log, model-spec template and supplied-input hashes.
- CODEX_PLAYBOOK.md: sequencing instructions and all prompts.
- RECOVERY_PROMPT.txt: conservative checkpoint recovery.
- file_manifest.json: SHA256 for included deliverables (excluding itself).

## Critical scope rules

M0=X; ME=X+E; MW=X+W; MEW=X+E+W. H is absent everywhere in the active model design. No H-qualified sample, price-area fold, transaction-count gate or price-provider request remains. Keep income/density/centrality as inherited concepts, with an explicit pre-fit income policy if new-city harmonisation fails.

Keep successful listing acquisitions, the accepted Stockholm operational municipal mask and all housing-investigation history. Oslo's boundary vintage and new-city analysis/context inputs still need qualification. Do not reset v4 to main or undo completed migrations/commits.

## Status

These are documentation and instructions, not executable project code or completed research runs. The actual repository must supply current paths, commands, data, status and tests. No Git pushes or model fits were performed while preparing this bundle. The model JSON is a template to map to the live schema, not a drop-in replacement for frozen configuration.

Updated 11 October 2026. Earlier v3 and housing-inclusive v4 deliverables were not overwritten.
