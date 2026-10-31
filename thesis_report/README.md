# Writing the thesis

Edit [main.tex](main.tex). It contains the cover details, all prose, chapter
order, figure/table placements and appendix prompts. The supplied UCPH example
provides the `memoir` class and SAMF cover; body chapters use numbered sections.
Chapters 4--5 contain the study-area/data and methods drafts; Chapters 6--8 contain the results,
discussion and conclusion drafts based on frozen final evidence. Other chapters
and appendices may contain researcher-written text or writing prompts. The
manuscript still requires a final editorial and citation review.

| File | What to edit |
| --- | --- |
| `main.tex` | Title, author, supervisors, submission date and all thesis text |
| `preamble.tex` | Fonts, margins, spacing, bibliography style and draft-note appearance |
| `references.bib` | All literature, dataset, governance and Methods references |
| `main.pdf` | Canonical compiled thesis; generated locally and excluded from Git |
| `.latexmkrc` | XeLaTeX build settings; auxiliary files stay in `build/` |
| `figures/` | Manuscript maps and code-generated explanatory diagrams |
| `tables/` | Generated aggregate result tables and their checksum/source manifest |
| `supplements/` | Original supplied template, examples and licensed UCPH logos; leave intact |

The active entry point is **`thesis_report/main.tex`**. The original
`supplements/main.tex` remains an unchanged historical starter. The optional
cover image is disabled, and the example's dummy text and PhD submission
statement are not part of the draft. Confirm the working title, name,
supervisors, date and programme-specific submission requirements yourself.

## Build locally or move to Overleaf

From the project root:

```sh
cd thesis_report
latexmk -interaction=nonstopmode -halt-on-error main.tex
```

This produces **`main.pdf` beside `main.tex`**. The local `.latexmkrc` selects
XeLaTeX and places auxiliary files in `build/`. The LaTeX dependencies use a TeX
distribution, separate from the project's unchanged Python `requirements.txt`.
Biber reads only `references.bib`; all unique entries from the former data and
Methods bibliographies have been merged there. Duplicate literature keys were
removed while retaining the first definition previously selected by Biber.
The former chapter-preview PDFs and separate bibliography files are retired;
their pre-consolidation copies and checksums remain in the local archive.
Do not maintain separate chapter drafts or PDFs. Edit all prose in `main.tex`
and all citations in `references.bib`, then rebuild this one manuscript.
The unchanged KU package also emits a harmless package-name/path warning when
loaded from `supplements/`.

For the manual Overleaf move, upload the **contents of `thesis_report/`**, keeping
the `supplements/` and `figures/` directories. Exclude `.DS_Store` and `build/`.
Select the root `main.tex` as the main document and **XeLaTeX** as compiler.
No repository-relative research file is required to compile: evidence paths
in comments are writing references, not LaTeX dependencies. Upload selected
public figures separately when you add them; do not upload the research repo,
private data, credentials, individual predictions or model files.

Keep `tables/`, `figures/` and `references.bib` in the upload. The
Chapter 4 map and four tables accompany the six result tables in `main.tex`.
The six result tables are generated from the final aggregate exports,
with original paths, checksums and scientific run identities recorded in
`tables/manifest.json`. Edit chapter prose in `main.tex`; edit table presentation
in `scripts/build_thesis_chapter_tables.py`, then regenerate from the repository
root using the audited environment:

```sh
.venv/bin/python scripts/build_thesis_chapter_tables.py
.venv/bin/python scripts/build_thesis_chapter_tables.py --check
```

Regeneration requires the existing local `outputs/tables/`, `outputs/metrics/`,
pinned reporting manifest and local PostGIS connection from `.env`. Table 6.1
adds arithmetic means from the frozen common predictive samples through
`scripts/thesis_accessibility_summary.py`. It checks every original quantile
against the pinned export, averages original counts/distances, and records
sample/code hashes in `tables/manifest.json`. The original export is unchanged.
Compiling the uploaded manuscript only needs the generated files already in
`tables/`. The script verifies source checksums and
does not refit models, rerun scientific stages or alter analytical exports.

Chapter 4 assets are reproduced from pinned final aggregate exports and audit
metadata and read-only PostGIS queries, without data acquisition, analytical
writes or model fitting:

```sh
.venv/bin/python scripts/build_thesis_data_assets.py
.venv/bin/python scripts/build_thesis_data_assets.py --check
```

The Section 4.1 district table lists the frozen operational group names from
PostGIS and verifies them against the accepted provider mapping and final group
counts (11/17/11). It distinguishes these analytical labels from a claim about
current official districts.

The manuscript map rerenders the frozen geometry with compact spacing and `N`
arrow labels. Sea, lakes and rivers are shown using a separate, adapted
Copernicus EU-Hydro 2006--2012 display layer; analytical masks, group boundaries,
area denominators and samples remain unchanged. Its immutable source responses,
checksums and acquisition receipts are local under `data/raw/cartographic_context/`,
and its authoritative geometry is isolated in `cartography.manuscript_water`
in PostGIS. The frozen selector is `config/reporting/manuscript_water.json`;
`scripts/thesis_water_context.py` checks it without reacquisition.
The completed original in `outputs/figures/study_areas.png` remains
unchanged. The accommodation table reports blank-price counts and percentages in original
source records before all filters; room categories are descriptive only. The
generator and its `--check` require the existing local PostGIS connection from
`.env` and issue read-only queries. Input/output checksums, query/code hashes
and scientific source identities are in
`tables/data_assets_manifest.json`. The new source bibliography is documented
in [the reference checks](../docs/analysis/thesis_data_chapter_sources.md).

The Methods comparison table and an optional native LaTeX workflow diagram are
generated from the executed design, without new estimates or fitting:

```sh
.venv/bin/python scripts/build_thesis_methods_assets.py
.venv/bin/python scripts/build_thesis_methods_assets.py --check
```

The manuscript uses the geographic validation comparison described below in
place of the optional three-box workflow. The inputs and code hashes for the
table/workflow are in `tables/methods_assets_manifest.json`; reference/implementation
checks are in [the Methods source note](../docs/analysis/thesis_methods_sources.md).

Eight further figures are regenerated for the current study rather than copied
from the archived single-city analysis:

```sh
.venv/bin/python scripts/build_thesis_explanatory_figures.py
.venv/bin/python scripts/build_thesis_explanatory_figures.py --check
```

`price_distributions.png` describes all three current common predictive samples
in Chapter 4. `catchment_comparison.png`,
`random_vs_loao_validation_schematic.png` and `spatial_grid_sensitivities.png`
explain accessibility, neighbourhood holdouts and the six block configurations
in Methods. The main-text maps use Copenhagen; `_oslo.png` and `_stockholm.png`
companions to both validation figures appear in Appendix B. The three block
figures reserve a white gap above the “Saved test fold” legend; the generator
verifies at least 10 points between the legend and the maps. Keep all eight
PNGs in the Overleaf upload.

The generator reads the existing PostGIS samples, saved outer memberships,
destinations and geometry in read-only transactions. The catchment alone
reconstructs the public pedestrian graph in memory from its exact preserved
OSM sources, checking it against the frozen graph summary. It routes from a
public node, never a listing, and does not recompute listing features or fit
models. At the researcher's explicit request on 31 October 2026, the three
validation illustrations now show one dot per listing at its approximate
Inside Airbnb location, with equal marker sizes and the archived blue/orange
layout and held-out-area callout. This replaces the earlier 500 m cell-centre
dot display for these illustrations only. No coordinate table or listing
identifier is exported. There is no jitter, sampling or cell suppression in
the validation dot maps; coincident locations may overlap. Block-map
minimum-five suppression and other location-summary rules remain unchanged.
Oslo holds out Grünerløkka and Stockholm Södermalm, using their saved
memberships and native projected CRSs.
Hashes, sources, CRSs, histogram counts, display exclusions
and public-origin details are in `tables/explanatory_figures_manifest.json`.
The archived figures and completed analytical outputs remain unchanged.

## Recommended explanation flow

The reader should follow one argument: **why this problem matters → what the
concepts mean → what is observed → how the comparison works → what the evidence
shows → what it means**. A four-RQ structure is already the current study design.

| Chapter | Reader's question | Keep the emphasis on |
| --- | --- | --- |
| 1. Introduction | Why compare accessibility representations? | Motivation, gap, contribution, RQ1–RQ4 and scope |
| 2. Related literature | What does prior Airbnb research show? | Recent accessibility/pricing studies, Euclidean and walking-network measures, and geographic generalization |
| 3. Theoretical framework | Which theories frame the study? | Hedonic pricing, spatial hedonic pricing, accessibility and analytical expectations |
| 4. Study areas and data | What population and measurements are available, and what are the legal and ethical considerations? | Geography, sources, selection, missingness, variables, privacy and verified source-use requirements |
| 5. Methods | How is each question answered fairly? | Matched E/W definitions, four models, training-only evaluation, associations and transfer |
| 6. Results | What is the answer to each question? | RQ1 measurement → RQ2 prediction/association → RQ3 geography → RQ4 transfer |
| 7. Discussion | What do the combined answers mean? | Literature, explanations, limitations, implications and future work |
| 8. Conclusion | What has the thesis established? | Direct qualified answers and the combined contribution |
| Appendices | Where can I check details? | Provenance/dictionary, full diagnostics, robustness and decision chronology |

Keep one results chapter initially: the same three cities and four models recur
across the RQs, so readers can compare them without three repeated city reports.
Use city-specific paragraphs within each RQ. In each results section, give a
direct answer, present the supporting table/figure, explain the important
contrast and qualification, then bridge to the next question. RQ1 establishes
measurement differences; RQ2 tests their information value; RQ3 checks dependence
on geography; RQ4 asks what survives a change of city.

Define each concept once. Put substantive definitions in data/methods, findings
in results, and possible mechanisms and literature comparisons in discussion.
Keep full coefficients, tuning details and robustness grids in appendices;
summarize their consequences in the main text. Let every figure/table support
a specific sentence rather than adding all available outputs.

Write in this order: **data and methods → RQ results → discussion → introduction
and conclusion → abstract**. Revise the introduction after writing the results
so the promised contribution matches the completed evidence. Keep the abstract
until the end. The requested overall ceiling is **72,000 characters** (30 ×
2,400), including spaces. Treat it as a shared budget across the manuscript,
not a separate allowance for each chapter. Check the programme's rules for what
counts (for example, references, tables and appendices) before submission;
reserve room for the unfinished sections and verify the final count under those
rules.

## Moving sections between ChatGPT, DeepSeek and Codex

Use `main.tex` as the one accepted manuscript. Website conversations are drafting
workspaces. Exchange one labelled section at a time, then paste the reviewed
replacement into that section. Stable `\label{...}` keys make sections easy to
identify; keep existing labels and citation keys when revising text.

For each writing session, provide the research questions, the relevant methods
constraints, the current section, and the exact aggregate evidence or checked
literature it needs. Comments beginning `Evidence:`, `Tables:` or `Figures:` in
`main.tex` name outputs under `outputs/tables/`, `outputs/metrics/` and
`outputs/figures/` in the repository. Websites
cannot read local paths: paste the relevant content or attach the safe aggregate
artifact. Treat new references, mechanisms and factual assertions as suggestions
until verified. If two tools suggest alternatives, choose one locally before
requesting another revision.

Copy and adapt this prompt:

```text
Task: revise only [section title and LaTeX label] for my MSc thesis.
Purpose: [what this section must establish for the reader].
Length and tone: [character budget including spaces; clear academic English].
Overall thesis ceiling: 72,000 characters including spaces; reserve space for
other sections and apply the programme's counting rules.
Current section: [paste LaTeX].
Evidence: [paste verified aggregate output, definitions or checked sources].
Required qualifications: [paste the relevant study/claim constraints].

Return replacement LaTeX for this section only, preserving its label and
existing citation keys. Use ordinary paragraphs and LaTeX, not Markdown.
Do not invent numbers, references, geography or completed analyses.
Mark missing evidence with \draftnote{...}. Treat proposed interpretations
as interpretations. List suggested factual/citation checks separately from
the replacement text. Do not change the study design or other sections.
```

After accepting a section, compile, check numbers/units against its evidence,
verify citations and read the transition to the neighbouring sections. Make
small incremental Git checkpoints on `v4`; commit only intended safe manuscript
changes. Remove resolved `\draftnote{...}` prompts. `\draftnotesfalse` hides
remaining prompts for a clean reading copy, but does not resolve them.

## Evidence to use while writing

The manuscript is an editable narrative. The executed design and verified
scientific outputs remain authoritative for definitions and results.

| Need | Current evidence |
| --- | --- |
| Overall scientific account | [End-to-end plan](../docs/design/end_to_end_research_plan.md) and [proposal](../docs/design/scientific_proposal.md) |
| Exact model/validation definitions | [Design registry](../config/study/design.json) and [specification](../docs/analysis/preanalysis_specification.md) |
| Verified results | [Research results](../reports/research_results.md) and [RQ synthesis](../reports/findings_by_research_question.md) |
| Figure/table selection and captions | [Placement guide](../reports/thesis_figure_recommendations.md) |
| Allowed interpretations | [Claims and limitations](../docs/final_claims_for_thesis.md) |
| Missingness decision chronology | [Association amendment](../docs/analysis/association_missingness_amendment_20261013.md) |
| Definitions, sources and caveats | [Data dictionary](../docs/analysis/data_dictionary.md) and [source registry](../docs/analysis/source_registry.md) |

Keep `M0=X`, `ME=X+E`, `MW=X+W` and `MEW=X+E+W`; income and housing prices
remain excluded. Keep common predictive samples/folds, training-only learned
preprocessing and source-only transfer. Associations use genuinely complete
cases; the uniform 10% eligibility limit was adopted after observation.
Do not conflate native log-price prediction, city-relative transfer and adjusted
observational associations. A measured E/W difference is not universal network
predictive superiority. Target centring uses observed target prices. Neither
overlapping stability ranges nor dependent directions establish equivalence or
independent replications.

For a figure, copy the unchanged final 300-dpi PNG from `../outputs/figures/`
into `figures/` after choosing it using the guide. Retain the figure's source,
CRS, scope and privacy qualifications in its caption. Record the original path
and checksum in a nearby comment when inserting it. The copies are manuscript
assets, not alternative analytical sources. Do not manually edit their values.
For tables, use a reproducible export from the final generated aggregate view;
do not transcribe numerical results from AI output.

Basic LaTeX patterns (replace placeholders before using):

```latex
% Cite only a checked entry in references.bib:
\parencite{verified-key}
\textcite{verified-key}

% Reference a stable label:
Section~\ref{sec:rq2-results}

% After copying the final figure into figures/:
\begin{figure}[tbp]
  \centering
  \includegraphics[width=\textwidth]{primary_model_performance.png}
  \caption{Describe the comparison and retain the source qualifications.}
  \label{fig:primary-performance}
\end{figure}
```

Use `\begin{landscape} ... \end{landscape}` around wide transfer figures if
needed. Escape `%`, `&` and `_` in ordinary text as `\%`, `\&` and `\_`.
Before submission, resolve prompts, replace cover placeholders, verify every
citation and numeric claim, check the PDF visually, and confirm any required
declarations with the programme.
