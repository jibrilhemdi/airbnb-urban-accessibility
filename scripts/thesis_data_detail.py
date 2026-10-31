"""Read-only manuscript map geometry and original-source missingness counts."""
from __future__ import annotations

from collections import defaultdict
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform
from sqlalchemy import text

from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash
from src.provenance.identity import Scope
from src.provenance.source_reuse import reuse_listing_source
from src.provenance.specification import DEFINITION_VERSION
from src.reporting import thesis_style as theme
from src.reporting.thesis_cartography import load_layers
from src.reporting.thesis_outputs import (
    CAPITAL_COLOURS, CONTEXT_BORDER, CONTEXT_FILL, STAR_COLOUR, map_geography, outline,
)
from thesis_water_context import load_water
from src.study.sources import get_engine
from src.study.specification import CITIES, load_design
from src.study.store import read_package

QUERY = ROOT / "sql/queries/thesis_missingness_by_accommodation.sql"


def read_details():
    design, cities = load_design()
    selected = json.loads((ROOT / "config/study/geography_selection.json").read_text())
    data = {"cities": cities, "geometries": {}, "districts": {}}
    counts, provenance = {}, {"transaction": "READ ONLY", "sources": {}}
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
            if conn.scalar(text("SELECT current_database()")) != "thesis_accessibility_v4":
                raise ValueError("Wrong authoritative database")
            data["cartographic_context"], cartography = load_layers(conn)
            provenance["cartography"] = cartography
            data["display_water"], provenance["display_water"] = load_water(conn)
            for city in CITIES:
                pointer = selected[city]
                summary, _ = read_package(conn, pointer["run_id"], city, "geography")
                if canonical_hash(summary) != pointer["summary_sha256"]:
                    raise ValueError("Selected geography summary changed")
                rows = conn.execute(text(
                    "SELECT geometry_key,properties,ST_AsGeoJSON(geom,15) AS geometry "
                    "FROM study.geometries WHERE run_id=:run AND city=:city "
                    "AND family='geography' AND (geometry_key='mask' OR geometry_key LIKE 'group:%') "
                    "ORDER BY geometry_key"), {"run": pointer["run_id"], "city": city}).mappings().all()
                data["geometries"][city] = [
                    {"key": r["geometry_key"], "properties": r["properties"],
                    "geometry": shape(json.loads(r["geometry"]))} for r in rows
                ]
                groups = [r["properties"] for r in rows if r["geometry_key"].startswith("group:")]
                names = [r["group"] for r in groups]
                mapping = cities[city]["operational_mapping"]
                if (len(names) != cities[city]["operational_count"]
                        or len(names) != len(set(names))
                        or set(names) != set(mapping.values())
                        or set(names) != {r["name"] for r in summary["groups"]}):
                    raise ValueError("Frozen district names/counts disagree with study geography")
                for group in groups:
                    expected = sorted(raw for raw, name in mapping.items() if name == group["group"])
                    if sorted(group["raw_components"]) != expected:
                        raise ValueError("Frozen provider-to-group mapping differs")
                data["districts"][city] = sorted(groups, key=lambda r: r["group"])
                geometry_digest = canonical_hash([dict(r) for r in rows])
                old = cities[city]["historical_listing_selection"]
                scope = Scope(old["source_version"], old["city"], old["snapshot"],
                              old["run_id"], design_id=DEFINITION_VERSION)
                approved = reuse_listing_source(conn, scope, old["manifest_sha256"])
                raw = [dict(r) for r in conn.execute(text(QUERY.read_text()), approved["source_scope"]).mappings()]
                groups = defaultdict(lambda: {"n": 0, "missing_price": 0, "missing_bedrooms": 0})
                for row in raw:
                    room, prop = row["room_type"], row["property_type"]
                    if room == "Entire home/apt":
                        label = prop if prop in design["sample"]["property_types"] else "Other entire property types" if prop else "Entire dwelling: missing type"
                    elif room in {"Private room", "Shared room", "Hotel room"}:
                        label = room
                    elif room is None:
                        label = "Missing room type"
                    else:
                        raise ValueError(f"Unreviewed room category: {room}")
                    for key in groups[label]:
                        value = int(row[key])
                        if value < 0 or (key != "n" and value > row["n"]):
                            raise ValueError("Invalid missingness count")
                        groups[label][key] += value
                original = approved["summary"]["counts"]
                if sum(r["n"] for r in groups.values()) != original["raw"]:
                    raise ValueError("Accommodation counts do not cover original source")
                eligible = [groups[p] for p in design["sample"]["property_types"] if p in groups]
                if sum(r["n"] for r in eligible) != original["dwelling_filtered"]:
                    raise ValueError("Eligible dwelling count disagrees with ingestion")
                if sum(r["missing_price"] for r in eligible) != original["eligible_missing_price"]:
                    raise ValueError("Missing price definition disagrees with source audit")
                counts[city] = dict(groups)
                provenance["sources"][city] = {
                    "geography": pointer, "geometry_records_sha256": geometry_digest,
                    "listing_scope": approved["source_scope"],
                    "listing_manifest_sha256": approved["manifest_sha256"],
                    "original_counts_sha256": canonical_hash(original),
                    "source_category_aggregates_sha256": canonical_hash(raw),
                    "original_n": original["raw"],
                }
    finally:
        engine.dispose()
    provenance["accommodation_missingness"] = counts
    provenance["operational_groups"] = data["districts"]
    provenance["code"] = {p: sha256_file(ROOT / p) for p in (
        "scripts/thesis_data_detail.py", "sql/queries/thesis_missingness_by_accommodation.sql",
        "src/reporting/thesis_outputs.py", "src/reporting/thesis_style.py",
        "config/study/cities.json", "config/study/geography_selection.json",
        "config/reporting/map_context.json",
        "scripts/thesis_water_context.py", "sql/cartography/002_manuscript_water.sql",
        "config/reporting/manuscript_water.json",
    )}
    provenance["spatial_crs"] = {"source": "EPSG:4326", "panels": {c: cities[c]["metric_crs"] for c in CITIES}}
    return data, counts, provenance


def compact_map(data):
    """Keep frozen boundaries; overlay separate display-only sea/lake polygons."""
    theme.setup()
    fig = plt.figure(figsize=(12.5, 5.7))
    panel_width = .306
    for i, city in enumerate(CITIES):
        ax = fig.add_axes([.02 + i * .327, .129, panel_width, panel_width * 12.5 / 5.7])
        map_geography(ax, data, city)
        project = Transformer.from_crs(4326, data["cities"][city]["metric_crs"], always_xy=True).transform
        outline(ax, transform(project, data["display_water"][city]),
                facecolor="#EEF4F7", edgecolor="#C7D8E0", linewidth=.35, zorder=3)
        for label in ax.texts:
            if label.get_text().startswith("EPSG:"):
                label.set_zorder(21)
        arrows = [item for item in ax.texts if item.get_text() == "N\n(grid)"]
        if len(arrows) != 1:
            raise ValueError("Expected one grid-north annotation per city")
        arrows[0].set_text("N")
    fig.text(.02, .985, "Capital cities and their study neighbourhoods", fontsize=19,
             weight="bold", va="top")
    fig.text(.02, .925, "White study boundaries · grey surrounding municipalities · verified civic references",
             fontsize=10, color=theme.INK, va="top")
    handles = [Patch(facecolor=CAPITAL_COLOURS[c], edgecolor="white", label=data["cities"][c]["display_name"]) for c in CITIES]
    handles.extend([
        Patch(facecolor=CONTEXT_FILL, edgecolor=CONTEXT_BORDER, label="Surrounding municipalities"),
        Line2D([], [], marker="*", markersize=10, color=STAR_COLOUR,
               markeredgecolor="white", linestyle="None", label="City Hall / Square"),
        Patch(facecolor="#EEF4F7", edgecolor="#C7D8E0", label="Sea, lakes and rivers"),
    ])
    fig.legend(handles=handles, ncol=6, loc="upper center", bbox_to_anchor=(.5, .89),
               frameon=False, fontsize=8)
    fig.text(.02, .058, "Sources: Inside Airbnb; DAGI/DAWA; Kartverket; Statistics Sweden; verified civic references. "
             "Municipal context is display only.\n"
             "Generated using European Union's Copernicus Land Monitoring Service information: "
             "EU-Hydro 2006–2012 (adapted; display only).", fontsize=8, color=theme.INK, va="top")
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        panel = ax.get_window_extent(renderer)
        if abs(panel.width - panel.height) > 2:
            raise ValueError("Map panel is not square")
    blob = io.BytesIO()
    fig.savefig(blob, format="png", dpi=300, bbox_inches="tight", pad_inches=.04,
                metadata={"Software": "Reproducible manuscript cartography"})
    plt.close(fig)
    return blob.getvalue()
