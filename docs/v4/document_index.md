# V4 document index and provenance

Active definition version: `v4_housing_standard_20261011`, 11 October 2026.
**Authoritative V4 material is Markdown plus its versioned machine-readable
configuration.** The following five documents were absent before this step and
are newly authored from accessible V3 evidence and the user's latest decision.
No inaccessible V4 proposal or historical eight-model draft was reconstructed.

| Document | Role / status |
| --- | --- |
| [proposal.md](proposal.md) | Active V4 proposal and revised research questions |
| [research_plan.md](research_plan.md) | Active V4 gated research plan |
| [preanalysis_specification.md](preanalysis_specification.md) | Active V4 scientific definitions, samples, comparisons, safeguards and inference |
| [data_dictionary.md](data_dictionary.md) | Active V4 field/block definitions; not a claim of implemented data columns |
| [source_registry.md](source_registry.md) | Active V4 qualification register, explicit missing evidence |
| [architecture.md](architecture.md) | Active V4 isolation, command behavior and persistence contract |
| `config/v4/cities.json` | Versioned three-city evidence and unresolved fields |
| `config/v4/research_design.json` | Active V4 machine-readable definitions, inherited candidates and unresolved gates |
| [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md) | Active V4 execution/Git/data governance |
| [step_log.md](step_log.md) | Requested steps, changes, actual checks and blockers |
| [repository_audit.md](repository_audit.md) | Preserved step-1 repository evidence, not a current research proposal |
| `protected_v3_manifest.json` | Preserved checksum-only baseline; never replace to conceal drift |

## Preserved V3 and historical material

The actual active V3 specification is `docs/preanalysis_specification.md`, with
`docs/data_dictionary.md`, `config/research_design.json` (`research_design_v3`),
`src/pipeline/model_specification.py`, the local source manifest and PostgreSQL
registry. These remain authoritative for the completed V3 identity, unchanged.
They are superseded for V4 model definitions, not rewritten as V4 material.

Existing V3 supporting files are
`docs/design/airbnb_urban_accessibility_scientific_thesis_proposal_v3.docx` and
`docs/design/airbnb_urban_accessibility_end_to_end_research_plan_v3.docx`, including
their preserved baseline copies. Their XML text and income addenda were read.
Older draft wording does not supersede the actual active V3 specification.
Historical archives/drafts remain unchanged and are not active V4 instructions.

V3 results were already observed before this amendment, including completed
run `research_v3_20261004T111510Z`. The amendment is prospective for V4 only;
do not invent supervisor approval or claim retrospective preregistration.

## DOCX status and supported workflow

**No existing active V4 DOCX file was found in the repository; no V4 DOCX was
generated in this step.** No supported V4 Markdown-to-DOCX regeneration workflow
was found. The existing `make income-docs` invokes
`src.pipeline.update_income_documentation` and appends V3 income amendments to
the two fixed V3 files using their historical DOCX baselines. It is not a V4
regeneration workflow and was not invoked.

Existing V3 DOCX files are preserved V3 supporting material, **superseded for
V4 use**. Any separately held earlier V4 DOCX/draft is **stale/superseded for
active V4 decisions** until regenerated from this authoritative Markdown by a
supported, explicitly requested V4 workflow. Its existence/content cannot be
verified from this repository, so no fictitious path or approval is recorded.
If an active V4 DOCX is later added, update this index with its source/version,
workflow/checksum and regeneration status; do not distribute an unstamped or
stale binary as the active V4 specification.
