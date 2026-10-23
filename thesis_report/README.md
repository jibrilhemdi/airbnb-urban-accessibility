# Writing the thesis

Edit [main.tex](main.tex). It contains the cover details, all prose, chapter
order, figure/table placements and appendix prompts. The supplied UCPH example
provides the `memoir` class and SAMF cover; body chapters use numbered sections.
Chapters 5--7 contain the results, discussion and conclusion draft based on the
frozen final evidence. The earlier chapters and appendices still contain writing
prompts. The manuscript is not a finished thesis or a newly reviewed literature
survey.

| File | What to edit |
| --- | --- |
| `main.tex` | Title, author, supervisors, submission date and all thesis text |
| `preamble.tex` | Fonts, margins, spacing, bibliography style and draft-note appearance |
| `references.bib` | Verified bibliographic entries |
| `figures/` | Copies of final generated figures selected for the manuscript |
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
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

This produces `build/main.pdf`. The LaTeX dependencies use a TeX distribution,
separate from the project's unchanged Python `requirements.txt`. The bibliography
uses Biber, which `latexmk` invokes when needed. The initial `.bib` file contains
no invented entries; an empty-bibliography warning is expected until references
are added and cited.
The unchanged KU package also emits a harmless package-name/path warning when
loaded from `supplements/`.

For the manual Overleaf move, upload the **contents of `thesis_report/`**, keeping
the `supplements/` and `figures/` directories. Exclude `.DS_Store` and `build/`.
Select the root `main.tex` as the main document and **XeLaTeX** as compiler.
No repository-relative research file is required to compile: evidence paths
in comments are writing references, not LaTeX dependencies. Upload selected
public figures separately when you add them; do not upload the research repo,
private data, credentials, individual predictions or model files.

Keep `tables/` in the upload: the six result tables are included by `main.tex`.
Their accepted numerical content is generated from the final aggregate exports,
with original paths, checksums and scientific run identities recorded in
`tables/manifest.json`. Edit chapter prose in `main.tex`; edit table presentation
in `scripts/build_thesis_chapter_tables.py`, then regenerate from the repository
root using the audited environment:

```sh
.venv/bin/python scripts/build_thesis_chapter_tables.py
.venv/bin/python scripts/build_thesis_chapter_tables.py --check
```

Regeneration requires the existing local `outputs/tables/`, `outputs/metrics/`
and pinned reporting manifest. Compiling the uploaded manuscript only needs the
generated files already in `tables/`. The script verifies source checksums and
does not refit models, rerun scientific stages or alter analytical exports.

## Recommended explanation flow

The reader should follow one argument: **why this problem matters → what the
concepts mean → what is observed → how the comparison works → what the evidence
shows → what it means**. A four-RQ structure is already the current study design.

| Chapter | Reader's question | Keep the emphasis on |
| --- | --- | --- |
| 1. Introduction | Why compare accessibility representations? | Motivation, gap, contribution, RQ1–RQ4 and scope |
| 2. Conceptual framework and literature | Why might representation and geography matter? | Concepts and checked literature that motivate the comparison |
| 3. Study areas and data | What population and measurements are available? | Geography, sources, selection, missingness, outcomes and controls |
| 4. Methods | How is each question answered fairly? | Matched E/W definitions, four models, training-only evaluation, associations and transfer |
| 5. Results | What is the answer to each question? | RQ1 measurement → RQ2 prediction/association → RQ3 geography → RQ4 transfer |
| 6. Discussion | What do the combined answers mean? | Literature, explanations, limitations, implications and future work |
| 7. Conclusion | What has the thesis established? | Direct qualified answers and the combined contribution |
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
until the end. No fixed chapter word budget is imposed here; use the programme's
actual requirements and supervisor advice.

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
Length and tone: [approximate words; clear academic English].
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
