# End-to-end research plan

The [proposal](../scientific_proposal.md) defines four questions and the
[specification](preanalysis_specification.md) freezes their methods. All scientific
outputs must be recomputed. Dependencies determine execution; a source, geography,
context or support failure blocks dependent fitting while independent work continues.

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
Historical modules/sources/migrations retain original paths through compatibility
adapters. Root historical scientific documents are preserved rather than overwritten.
There is one active runner; previous commands remain reproduction interfaces.

The [execution log](execution_log.md) records actual status. Configuration or
synthetic tests do not establish empirical readiness or completed research.

Completed predictive city ladders, random/six geometric variants, all six
transfers and registered predictive robustness are preserved after dependency
checks. Under the explicitly approved post-observation 10% eligibility limit,
all three cities' complete-case association stages and dependent spatial/fixed-
effect checks are rerun. Final status follows generated execution and release
audits, not merely passage of the amended gate. The previous 5% blocker remains
in the archived report and historical execution log.
