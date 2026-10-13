# Thesis-ready research release

This package contains final frozen three-city results, publication figures,
aggregate tables, RQ findings, scientific claims and current Markdown documents.
Ten main figures and eight main tables are recommended in
[the placement guide](reports/thesis_figure_recommendations.md). Start with
[research results](reports/research_results.md) and
[RQ findings](reports/findings_by_research_question.md).

PNG figures are300dpi; PDF and SVG are vector exports. Sample flow is a compact
table. Suppressed map/relationship/prediction bins require n≥5. The package
contains no raw listings, individual coordinates, host identifiers, credentials,
model bytes or individual predictions. Native-currency within-city outcomes and
city-relative transfer outcomes remain distinct. No model was refitted for this
reporting release. The disclosed10% association eligibility amendment was made
after observing missingness and is not presented as preregistered.

Markdown proposal, research plan and results are authoritative. The repository
has no supported active DOCX/PDF document renderer for this four-RQ design;
document exports are therefore not supplied. This does not affect vector figures.

## Reproduction and verification

Use the final repository checkpoint recorded in the external handover and the
single pinned requirements file. PostgreSQL/PostGIS remains authoritative;
private sources and saved predictions are required to reproduce analytical
aggregates, and remain outside this public package. In the repository run
`make thesis-check`, `make thesis-science-check` and `make thesis-release`.
Generation commands are write-once and refuse to overwrite completed results.
Exact reporting code is copied under manifests/reporting_code; supporting
repository modules and frozen source selectors remain in the repository.

[Release manifest](manifests/release_manifest.json) records every bundled file,
SHA256, final source run/artifact, RQ, publication status and generation command.
The manifest excludes itself from its own file-hash list. The ZIP contains every
registered file plus that manifest, with fixed timestamps and sorted paths.
Rebased Markdown links resolve within this package when evidence is bundled;
other preserved evidence links to the recorded repository branch. Original
repository artifact/synthesis manifests retain their source paths and hashes;
the release manifest records the hashes after link-only rebasing.
