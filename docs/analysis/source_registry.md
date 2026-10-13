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
[its dated report](../../archive/previous_analysis/docs/rinkeby_polygon_check_20261012.md).

New externally acquired files require immutable receipts containing source URL,
acquisition UTC time, extent, reference/snapshot time, explicit CRS, checksum and
licence. Failures remain failures with their response hashes; no downloaded HTML
error is labeled acquired data. Raw and restricted content remains off Git.

Selected source qualification is now implemented for all three prediction
samples. `geography_audit.json`, `context_audit.json`, `accessibility_audit.json`
and `sample_audit.json` are dated freeze evidence; their earlier pending-fit
statuses are preserved rather than rewritten to describe later stages.
Model/transfer/reporting selectors certify those later stages separately.
Stockholm uses the directly published11-unit2025 population and2024 native
land+water area spreadsheets pinned in `stockholm_population_sources.json`;
no RegSO allocation was needed. Native area/vintage/footprint and unspecified
city-source redistribution licence limitations remain explicit. All newly
acquired OSM objects use the common2026-06-30T23:59:59Z snapshot. Failed
overloaded/timeout attempts remain in the attempt registries with checksums.

The generated `outputs/tables/research/new_source_receipts.csv` indexes selected
new source receipts; original approved listing/mask/context manifest references
remain in the city/source registries and preservation evidence. A transport
receipt's pending-validation label is original acquisition evidence, not the
final scientific qualification status. No raw licence is retroactively invented.

## Map presentation context — 13 October 2026

The researcher requests the archived geography-map design with actual surrounding
municipalities, white study-neighbourhood borders, grey non-study borders, capital
legends and civic stars. Supplemental display geometry is registered in a separate
immutable `cartography` PostGIS schema and pinned by
[the map-context selector](../../config/reporting/map_context.json). It is not a
sample mask, validation geography, model feature or replacement analytical source.
The existing frozen SQL packages, sources, samples, folds and fits are unchanged.

Copenhagen reuses the capital-region DAGI/DAWA download acquired 29 September 2026.
Stockholm reuses the nationally acquired [SCB RegSO 2025 source](https://www.scb.se/en/services/open-data-api/open-geodata/open-data-for-regso--regional-statistical-areas/),
unioned by the original municipality code using all polygons of each selected
municipality; it is context, not an invented neighbourhood crosswalk. Source CRS
is EPSG:3006 and reference date 1 January 2025. Oslo's surrounding municipalities
come from Kartverket's official
[neighbour-list endpoint](https://ws.geonorge.no/kommuneinfo/v1/kommuner/0301/nabokommuner)
and corresponding area endpoints. New Oslo bytes have immutable acquisition
receipts and checksums; their current-at-retrieval vintage is disclosed and is
not represented as the frozen June 2026 analytical geography.

The context selection uses distance within 3.5 km of each accepted study mask,
in each city's recorded metric CRS. Squares and viewport clipping affect display
only. Every original operational group remains; boundaries are displayed inside
the accepted mask. No geometry is repaired or synthesized. Copenhagen's star
is the preserved public `city_hall_square` point (Rådhuspladsen). Oslo and Stockholm
use their frozen, source-verified City Hall points; they are labelled City Hall,
not falsely identified as separately validated square coordinates.
