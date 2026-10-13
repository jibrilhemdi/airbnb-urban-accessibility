# Comprehensive research implementation contract

Adopted 13 October 2026 from the exact [researcher request](../../history/research_request/request.txt).
Copenhagen refers to the combined Copenhagen–Frederiksberg study area.
The existing branch `v4` is the only active version marker. This request
authorizes the complete workflow and explicitly resolves the earlier income,
provider-geography and minimum-holdout decisions. Older records remain dated
historical evidence; they are never rewritten to imply success.

The canonical executable definition is [design.json](../../config/study/design.json).
There are exactly four models: M0=X, ME=X+E, MW=X+W, MEW=X+E+W.
X retains audited common dwelling/host/amenity controls, density and civic-anchor
distance. The new registry excludes income and residential-price variables.
Within-city outcomes are log original observed positive native-currency asking
prices. Only transfer uses city-relative log price, with one frozen benchmark
from the eligible inside-mask positive-price reference sample before feature
filtering. Missing outcomes are never filled or replaced by quote prices.

Primary geographic validation leaves out one operational provider neighbourhood.
All four models share rows, outcomes and folds. Minimum test support is 15 and
complementary training support 500. An unsupported group blocks the city fold
freeze; no omission, threshold reduction or outcome-guided grouping is allowed.
The former threshold 30 remains a diagnostic. Random validation is a benchmark;
fixed 1.5 km blocks at zero and half-block origins are required robustness.
All learned preprocessing and the unchanged 30-candidate/four-inner-fold search
use training data only. Transfer preprocessing, fitting and tuning use the source
city only. Target outcomes enter only the frozen benchmark and evaluation.

Raw source bytes, applied migrations, historical databases, completed runs and
protected artifacts are immutable. [Path inventory](path_inventory.json) was
captured before refactoring. Existing roots containing old labels are compatibility
and historical locations. New configuration, code, outputs and scientific IDs
use functional names. No final result is copied from earlier analyses. The
active entry point is `python -m src.study.cli`; old entry points remain historical
reproduction interfaces and cannot certify the new design.

PostgreSQL/PostGIS is the persistent analytical authority. New neutral schemas
may coexist in the dedicated existing database without changing its immutable
historical name or existing rows. Raw sources, coordinates, private folds,
predictions, model files and credentials remain ignored. Public maps use 500 m
cells with at least five observations. Record source, actual acquisition time,
extent, CRS, checksum, licence and snapshot/reference date separately.

Use recorded origin `https://github.com/jibrilhemdi/airbnb-urban-accessibility.git`
and recorded main base `c1e919bca9dfbe89de9e67135fb432fdb0f020e6`.
Only normal incremental commits on existing `v4`; push explicitly
`HEAD:refs/heads/v4`, then verify remote SHA. No reset, rebase, force-push,
published amendment, tag change, main/v3 modification, automatic later-main merge
or destructive cleanup. Stop on unrelated edits, unfinished operations or
divergence. A failed push is LOCAL_ONLY; missing scientific inputs are BLOCKED.

The [execution log](execution_log.md) records actual work, checks and blockers.
No checkpoint's own SHA is written into itself. A specification freeze is not a
sample/feature/model freeze. Do not claim a fully rerun study until every required
city, direction, robustness output and independent recalculation is complete.
