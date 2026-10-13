# End-to-end research plan

The [proposal](scientific_proposal.md) defines four questions and the
[specification](preanalysis_specification.md) freezes their methods. The complete
three-city rerun has finished. The reporting completion task consumes these
frozen results without refitting, tuning or reacquiring sources. Dependencies
determined scientific execution; a source, geography, context or support failure
blocked dependent fitting while independent work continued.

| Work | Required evidence |
| --- | --- |
| Repository preservation and design | Branch/remote safety; pre-change checksums; neutral entry/configuration; explicit amendment |
| Operational geography | Verified provider polygons; raw labels; 11/17/11 groups; strict unique assignment; overlaps/gaps/mask QA |
| Context | Official population and matching denominator/crosswalk; three pinned OSM civic anchors |
| OSM sources | Common snapshot; inherited taxonomy/consolidation; licences/receipts/extent; network and destination completeness |
| Accessibility | Recomputed matched E/W; connectors, direction, components, failures, zeros and boundary coverage |
| Sample/fold freeze | Reference benchmarks; common prediction/association samples; 15/500 support; primary/random/geometric/inner membership |
| City models | Fresh OLS/XGBoost fits, all candidates, private OOF predictions, paired contrasts and diagnostic checks |
| Robustness | Every registered sensitivity accounted for; common within-variant rows/folds; no results-based design decisions |
| Transfer | Six source-only tuned relative-price directional fits and matched target evaluation |
| Reporting | Code-generated tables/figures; claim/output links; independent metrics; full preservation and Git verification |

The active layout is `config/study/`, `src/study/`, `docs/analysis/`, functional
raw-source directories and private `runs/<city>/` or `runs/transfer/<direction>/`.
Historical modules/sources/migrations retain original identities through
checksum-aware archive adapters. Prior scientific documents are preserved in
the archive before active documentation is updated.
There is one active runner; previous commands remain reproduction interfaces.

The [execution log](https://github.com/jibrilhemdi/airbnb-urban-accessibility/blob/v4/docs/analysis/execution_log.md) records actual status. Configuration or
synthetic tests do not establish empirical readiness or completed research.

Completed predictive city ladders, random/six geometric variants, all six
transfers and registered predictive robustness are preserved after dependency
checks. Under the explicitly approved post-observation 10% eligibility limit,
all three cities' complete-case association stages and dependent spatial/fixed-
effect checks were rerun. Final status follows generated execution and release
audits, not merely passage of the amended gate. The previous 5% blocker remains
in the archived report and historical execution log.

Current generated execution: all three association ladders and all triggered
spatial-error/area fixed-effect checks completed. The final release audit
verifies the complete required registry and unchanged predictive/transfer fits.

## Thesis reporting and release

Income and residential property prices are absent. Inside Airbnb operational
neighbourhood validation uses the frozen 15-observation outer-test and
500-observation complementary-training minima. All six source-only pairwise
transfers predict city-relative log asking price, with no target fitting,
tuning or recalibration. The uniform 10% association eligibility amendment was
made after observing missingness and is explicitly not preregistered.

The reporting sequence is: inventory all existing deliverables; pin final SQL
packages and saved prediction hashes; map every deliverable to RQ1–RQ4;
generate publication figures and tables; visually review; synthesize evidence
and claims; independently recalculate metrics; verify historical preservation;
assemble and hash-check the safe package; publish only on the existing branch.
The initial [gap audit](initial_deliverable_gap_audit.md) remains historical
evidence of the reporting work required, rather than being rewritten as success.

The generated [results report](research_results.md),
[RQ synthesis](findings_by_research_question.md),
[recommendations](thesis_figure_recommendations.md) and
[claims audit](final_claims_for_thesis.md) define the thesis writing handover.
Ten main figures and eight main tables are recommended; eight additional
figures and full diagnostic/robustness tables belong in appendices. Sample
flow is table-only to avoid an uninformative duplicate graphic. All figures
have high-resolution PNG and vector PDF/SVG versions.

Markdown proposal, plan and results are authoritative. No supported active
DOCX/PDF document export pipeline exists; the archived income-addendum updater
does not support this design. Document exports are explicitly outside this
release, while scientific figure vector exports are included.
