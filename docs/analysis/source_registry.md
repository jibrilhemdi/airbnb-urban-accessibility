# Source and compatibility registry

Existing source selection is explicit in [cities.json](../../config/study/cities.json).
The adapter verifies canonical SQL manifests and every source SHA before reuse.
Airbnb listings must not be downloaded again. Native currencies, original prices,
quote fields, actual scrape times and the catalogue snapshot remain distinct.

| Source | Active purpose | Qualification requirement |
| --- | --- | --- |
| Preserved June detailed listings | Fresh source parsing/sample audit/outcome | Original manifest and raw hashes; no quote-price substitution |
| Accepted municipal masks | Inside-study QA | Preserve documented source vintages and city metric CRSs |
| Matching Inside Airbnb neighbourhood polygons | Primary operational validation | Source receipt; raw labels; strict unique assignment and topology QA |
| Official population statistics | Baseline density | Native IDs/time/unit verification; compatible matching area or clean aggregation |
| Historical Copenhagen population sources | Fresh native counts | Reuse source bytes; recompute assignment/formula rather than copy derived density |
| Oslo BEF001 |17 population units plus separate totals/unlocated | Verify17-unit crosswalk/denominator and city-service reuse terms |
| Stockholm population | Direct11-unit official source preferred | Otherwise validated127-RegSO crosswalk; no area-weighted split-unit allocation |
| OpenStreetMap | Network/destinations/civic anchors | One common frozen snapshot, exact queries and ODbL attribution; matched E/W universes |
| Existing XGBoost candidates | Same tuning budget | Preserved file hash, all30 unique definitions, source-training-only tuning |

Historical geography/context/source audits remain available at their original
locations through the inventory. Their old blocked statuses are not rewritten.
The new provider-geography and no-income amendments retire their corresponding
old prerequisites; they do not certify population compatibility, licences,
network quality or final fold support. The Rinkeby comparison is preserved in
[its dated report](../v4/rinkeby_polygon_check_20261012.md).

New externally acquired files require immutable receipts containing source URL,
acquisition UTC time, extent, reference/snapshot time, explicit CRS, checksum and
licence. Failures remain failures with their response hashes; no downloaded HTML
error is labeled acquired data. Raw and restricted content remains off Git.
