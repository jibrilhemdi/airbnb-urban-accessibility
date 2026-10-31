"""Regenerate thesis illustrations from frozen SQL packages, without model fitting.

Only the public-origin catchment rebuilds a pedestrian graph in memory, using
the exact checksummed OSM sources and executed graph builder. It never rebuilds
listing features. Validation PNGs display individual approximate provider
locations at the researcher's request; no coordinate tables or identifiers
are exported. Block maps retain their minimum-five display rule.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Patch, Rectangle
from matplotlib.ticker import MaxNLocator
from matplotlib.text import Text
import networkx as nx
import numpy as np
import pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from shapely.geometry import shape
from shapely.ops import transform
from sqlalchemy import text

from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.reporting import thesis_style as theme
from src.reporting.thesis_cartography import load_layers
from src.reporting.thesis_outputs import outline
from src.reporting.thesis_sources import verify_catalog
from src.study.accessibility import elements, pedestrian_graph
from src.study.archive import preserved_path
from src.study.sample_freeze import records
from src.study.sources import get_engine
from src.study.specification import CITIES, load_design
from src.study.store import read_package

NAMES = ("catchment_comparison", "price_distributions",
         "random_vs_loao_validation_schematic", "spatial_grid_sensitivities")
FOLDS = [theme.BLUE, theme.SAND, theme.GREEN, theme.LILAC, "#DCC8C4"]
FIGURE_TEXT = []


def package_identities(conn):
    return [dict(r) for r in conn.execute(text(
        "SELECT run_id,city,family,summary_sha256,dependencies_sha256 "
        "FROM study.checkpoints ORDER BY run_id")).mappings()]


def load():
    catalog = verify_catalog()
    design, cities = load_design()
    pointers = {f: json.loads((ROOT / f"config/study/{f}_selection.json").read_text())
                for f in ("sample", "validation", "geography", "accessibility")}
    data = {"design": design, "cities": cities, "frames": {}, "sources": {},
            "catalog_sha256": sha256_file(ROOT / "reports/frozen_reporting_sources.json"),
            "geometries": {}, "folds": {}, "validation": {}, "assignments": {}}
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
            identities = package_identities(conn)
            if canonical_hash(identities) != catalog["sql_packages_sha256"]:
                raise ValueError("Frozen scientific SQL identities changed")
            data["sql_packages_sha256"] = canonical_hash(identities)
            for city in CITIES:
                item = pointers["sample"][city]
                summary, _ = read_package(conn, item["run_id"], city, "sample")
                rows = records(conn, pointers["sample"], city, "sample", "prediction_sample")
                if canonical_hash(summary) != item["summary_sha256"]:
                    raise ValueError("Sample selection changed")
                frame = pd.DataFrame(rows)
                if canonical_hash(json_records(frame)) != summary["record_sha256"]:
                    raise ValueError("Prediction sample changed")
                if (len(frame) != summary["prediction_n"] or frame.listing_id.duplicated().any()
                        or not np.isfinite(frame[["price_nightly", "log_price", "metric_x", "metric_y"]]).all().all()
                        or not (frame.price_nightly > 0).all()
                        or not np.allclose(frame.log_price, np.log(frame.price_nightly))):
                    raise ValueError("Invalid original observed prices or sample coordinates")
                data["frames"][city] = frame
                data["sources"][f"sample:{city}"] = {**item, "record_sha256": summary["record_sha256"], "n": len(frame)}
            for city in CITIES:
                for family in ("validation", "accessibility", "geography"):
                    if family == "accessibility" and city != "copenhagen":
                        continue
                    item = pointers[family][city]
                    summary, deps = read_package(conn, item["run_id"], city, family)
                    if canonical_hash(summary) != item["summary_sha256"]:
                        raise ValueError("Frozen selection changed: " + family)
                    data["sources"][family + ":" + city] = item
                    if family == "validation":
                        rows = records(conn, pointers[family], city, family, "outer_test")
                        if canonical_hash(rows) != summary["outer_hash"]:
                            raise ValueError("Saved outer fold assignments changed")
                        data["folds"][city] = pd.DataFrame(rows)
                        data["validation"][city] = summary
                        data["sources"][family + ":" + city] = {**item, "outer_hash": summary["outer_hash"]}
                    elif family == "accessibility":
                        rows = records(conn, pointers[family], city, family, "destinations")
                        if canonical_hash(rows) != summary["destination_universe_sha256"]:
                            raise ValueError("Frozen destination universe changed")
                        data["destinations"] = pd.DataFrame(rows)
                        data["accessibility"], data["accessibility_deps"] = summary, deps
                    else:
                        rows = [dict(r) for r in conn.execute(text(
                            "SELECT geometry_key,properties,ST_AsGeoJSON(geom,15) AS geometry "
                            "FROM study.geometries WHERE run_id=:run AND city=:city AND family='geography' "
                            "ORDER BY geometry_key"), {"run": item["run_id"], "city": city}).mappings()]
                        data["geometries"][city] = {r["geometry_key"]: shape(json.loads(r["geometry"])) for r in rows}
                        data["sources"][family + ":" + city] = {**item, "geometry_sha256": canonical_hash(rows)}
            data["context"], data["sources"]["cartographic_context"] = load_layers(conn)
            if package_identities(conn) != identities:
                raise ValueError("SQL identities changed during read-only loading")
    finally:
        engine.dispose()
    for city in CITIES:
        frame = data["frames"][city].copy()
        frame["listing_id"] = frame.listing_id.astype(str)
        merged = data["folds"][city].merge(frame[["listing_id", "metric_x", "metric_y", "operational_group"]],
                                     on="listing_id", validate="many_to_one")
        if len(merged) != len(data["folds"][city]):
            raise ValueError("Incomplete sample/fold join")
        for scheme, part in merged.groupby("scheme"):
            if len(part) != len(frame) or part.listing_id.duplicated().any():
                raise ValueError("Invalid common held-out membership: " + scheme)
            actual = part.groupby("outer_test_fold").size().to_dict()
            expected = {r["fold"]: r["test_n"] for r in data["validation"][city]["folds"] if r["scheme"] == scheme}
            if actual != expected:
                raise ValueError("Saved fold counts differ")
            if scheme == "neighbourhood" and not part.outer_test_fold.eq(part.operational_group).all():
                raise ValueError("Neighbourhood holdout membership differs")
        data["assignments"][city] = merged
    return data


def png(fig):
    buffer = io.BytesIO()
    fig.canvas.draw()
    FIGURE_TEXT.append([t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()])
    fig.savefig(buffer, format="png", dpi=300, bbox_inches="tight", pad_inches=.06)
    plt.close(fig)
    return buffer.getvalue()


def prices(data):
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 7.2))
    fig.subplots_adjust(left=.065, right=.99, top=.89, bottom=.09, hspace=.51, wspace=.27)
    details = {}
    low = min(f.log_price.min() for f in data["frames"].values())
    high = max(f.log_price.max() for f in data["frames"].values())
    log_edges = np.linspace(low, high, 46)
    for col, city in enumerate(CITIES):
        frame = data["frames"][city]
        unit = data["cities"][city]["currency"]
        upper = float(frame.price_nightly.quantile(.99))
        omitted = int((frame.price_nightly > upper).sum())
        edges = np.linspace(0, upper, 46)
        ax = axes[0, col]
        counts, _, _ = ax.hist(frame.price_nightly, bins=edges, color=theme.BLUE, edgecolor="white", linewidth=.4)
        ax.set_title(data["cities"][city]["display_name"] + f" · N = {len(frame):,}", loc="left", fontsize=14, pad=29)
        ax.text(0, 1.02, "Original prices (up to 99th percentile)", transform=ax.transAxes, fontsize=11, color=theme.INK)
        ax.text(.98, .94, f"{omitted:,} above range\n99th percentile: {upper:,.0f} {unit}",
                ha="right", va="top", transform=ax.transAxes, fontsize=10, color=theme.INK)
        ax.set_xlabel(f"Nightly asking price ({unit})")
        ax = axes[1, col]
        log_counts, _, _ = ax.hist(frame.log_price, bins=log_edges, color=theme.SAND, edgecolor="white", linewidth=.4)
        ax.set_title("Full log-price distribution", loc="left", fontsize=12)
        ax.set_xlabel(f"Natural log of asking price ({unit})")
        ax.set_xlim(low, high)
        for row in range(2):
            ax = axes[row, col]
            ax.set_axisbelow(True)
            ax.grid(axis="y", alpha=.6)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
            ax.xaxis.set_major_locator(MaxNLocator(nbins=4))
            ax.tick_params(length=0)
        axes[0, col].set_ylabel("Listings" if col == 0 else "")
        axes[1, col].set_ylabel("Listings" if col == 0 else "")
        if int(counts.sum()) + omitted != len(frame) or int(log_counts.sum()) != len(frame):
            raise ValueError("Histogram does not account for every observed price")
        details[city] = {"n": len(frame), "currency": unit, "raw_99th_percentile": upper,
                         "raw_above_display": omitted, "raw_bins": edges.tolist(),
                         "raw_counts": counts.astype(int).tolist(), "log_bins": log_edges.tolist(),
                         "log_counts": log_counts.astype(int).tolist()}
    return png(fig), details


def base_map(ax, data, city="copenhagen", *, bounds=None):
    project = Transformer.from_crs(4326, data["cities"][city]["metric_crs"], always_xy=True).transform
    mask = transform(project, data["geometries"][city]["mask"])
    for item in data["context"][city]:
        if item["role"] == "surrounding_municipality":
            outline(ax, transform(project, item["geometry"]), facecolor="#E4EAE7", edgecolor="#BCC8C4", lw=.6, zorder=1)
    outline(ax, mask, facecolor="#F8FAF9", edgecolor=theme.DARK[0], lw=1, zorder=2)
    for key, geometry in data["geometries"][city].items():
        if key.startswith("group:"):
            outline(ax, transform(project, geometry).intersection(mask), facecolor="none", edgecolor="#9EB4C0", lw=.6, zorder=7)
    xmin, ymin, xmax, ymax = np.asarray(mask.bounds) / 1000
    span = max(xmax-xmin, ymax-ymin) * 1.08
    xc, yc = (xmin+xmax)/2, (ymin+ymax)/2
    ax.set(xlim=(xc-span/2, xc+span/2), ylim=(yc-span/2, yc+span/2))
    if bounds is None:
        theme.map_frame(ax)
        for item in ax.texts:
            if item.get_text() == "N\n(grid)":
                item.set_text("N")
            item.set_fontsize(11)
    else:
        ax.set(xlim=(bounds[0],bounds[2]), ylim=(bounds[1],bounds[3]), aspect="equal", xticks=[], yticks=[])
        ax.set_facecolor("#EEF4F7")
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.annotate("N",xy=(.92,.95),xytext=(.92,.82),xycoords="axes fraction",ha="center",
                    fontsize=10,weight="bold",color=theme.NAVY,
                    arrowprops={"arrowstyle":"-|>","color":theme.NAVY},zorder=20)
        span = bounds[2]-bounds[0]
        distance = 2 if span < 25 else 5
        x, y = bounds[0]+.06*span, bounds[1]+.04*(bounds[3]-bounds[1])
        ax.plot([x,x+distance],[y,y],color=theme.NAVY,lw=2,zorder=20)
        ax.text(x+distance/2,y+.02*(bounds[3]-bounds[1]),f"{distance} km",ha="center",fontsize=10,
                bbox={"facecolor":"white","edgecolor":"none","alpha":.9,"pad":2},zorder=20)
    return mask


TEST_AREAS = {"copenhagen": "Nørrebro", "oslo": "Grünerløkka", "stockholm": "Södermalm"}


def validation(data, city="copenhagen"):
    project = Transformer.from_crs(4326, data["cities"][city]["metric_crs"], always_xy=True).transform
    mask = transform(project, data["geometries"][city]["mask"])
    xmin, ymin, xmax, ymax = np.asarray(mask.bounds)/1000
    padding = .02*max(xmax-xmin, ymax-ymin)
    bounds = (xmin-padding, ymin-padding, xmax+padding, ymax+padding)
    width, margin, gutter = 12.4, .22, .22
    panel_width = (width-2*margin-gutter)/2
    panel_height = panel_width*(bounds[3]-bounds[1])/(bounds[2]-bounds[0])
    footer, header = .98, 1.14
    height = footer+panel_height+header
    fig = plt.figure(figsize=(width, height))
    lefts = [margin, margin+panel_width+gutter]
    axes = [fig.add_axes([left/width, footer/height, panel_width/width, panel_height/height]) for left in lefts]
    top = footer+panel_height
    fig.text(margin/width, (top+.86)/height, "Two ways to test prediction", fontsize=18, weight="bold")
    label = "Copenhagen & Frederiksberg" if city == "copenhagen" else data["cities"][city]["display_name"]
    fig.text(margin/width, (top+.58)/height,
             f"{label} · {len(data['frames'][city]):,} listings · one saved split per design", fontsize=10.5, color=theme.INK)
    details = {"city": city, "metric_crs": data["cities"][city]["metric_crs"],
               "neighbourhood_example_rule": "Named public central neighbourhood, selected without prices or model performance",
               "shared_map_bounds_km": list(bounds), "marker_area_rule": "3 square points per listing, equal for train and test",
               "display_rule": "One dot at each listing's approximate provider location; no aggregation, jitter or sampling",
               "authorisation": "31 October 2026 feedback explicitly requests actual dots to represent listings; replaces earlier aggregated-dot choice for validation illustrations only"}
    descriptions = ["Training and test listings are spatially mixed.\nNearby listings can enter both sets.",
                    "One whole neighbourhood is held out.\nPrediction is tested in an unseen area."]
    for i, (ax, scheme, heldout, title) in enumerate(zip(axes, ("random", "neighbourhood"),
            ("1", TEST_AREAS[city]), ("Random cross-validation", "Leave-one-area-out cross-validation"), strict=True)):
        part = data["assignments"][city].loc[lambda f: f.scheme.eq(scheme)].copy()
        part["test"] = part.outer_test_fold.eq(heldout).astype(int)
        if not part.test.any():
            raise ValueError("Requested saved split is unavailable: " + city)
        x, y = part.metric_x/1000, part.metric_y/1000
        if not (x.between(bounds[0], bounds[2]) & y.between(bounds[1], bounds[3])).all():
            raise ValueError("Listing would be clipped by the map bounds")
        base_map(ax, data, city, bounds=bounds)
        if scheme == "neighbourhood":
            geom = transform(project, data["geometries"][city]["group:"+heldout]).intersection(mask)
            outline(ax, geom, facecolor=theme.SAND, edgecolor=theme.DARK[1], lw=1.4, alpha=.42, zorder=2.5)
        plotted = {}
        for role, test, color, alpha in (("train", 0, theme.BLUE, .62), ("test", 1, theme.SAND, .9)):
            shown = part.loc[part.test.eq(test)]
            points = ax.scatter(shown.metric_x/1000, shown.metric_y/1000,
                       s=3, color=color, alpha=alpha, linewidths=0,
                       zorder=3 if role == "train" else 4)
            plotted[role] = len(points.get_offsets())
        if sum(plotted.values()) != len(part):
            raise ValueError("Every listing must have exactly one plotted dot")
        if scheme == "neighbourhood":
            outline(ax, geom, facecolor="none", edgecolor=theme.DARK[1], lw=1.4, zorder=9)
            target = geom.representative_point()
            ax.annotate(heldout+"\nTest area", xy=(target.x/1000, target.y/1000),
                        xytext=(.04,.92), textcoords="axes fraction", fontsize=11, weight="bold",
                        color=theme.DARK[1], ha="left", va="top",
                        bbox={"boxstyle":"round,pad=.35","facecolor":"white","edgecolor":"none","alpha":.94},
                        arrowprops={"arrowstyle":"->","color":theme.DARK[1],"lw":1.1}, zorder=11)
        ntest = int(part.test.sum())
        fig.text(lefts[i]/width, (top+.31)/height, f"{chr(65+i)}  {title}", fontsize=13, weight="bold")
        example = "Fold 1 of 5" if i == 0 else f"{heldout} held out · {data['cities'][city]['operational_count']} area folds"
        fig.text(lefts[i]/width, (top+.085)/height,
                 f"{example}  |  Train {len(part)-ntest:,} · Test {ntest:,}", fontsize=10, color=theme.INK)
        fig.text((lefts[i]+panel_width/2)/width, (footer-.055)/height, descriptions[i],
                 ha="center", va="top", fontsize=10, color=theme.INK, linespacing=1.3)
        details[scheme] = {"heldout":heldout, "train_n":len(part)-ntest, "test_n":ntest,
                           "plotted_training_dots":plotted["train"], "plotted_test_dots":plotted["test"],
                           "suppressed_listings":0}
    fig.legend(handles=[Line2D([],[],marker="o",linestyle="",color=c,markersize=6,label=l)
                        for c,l in ((theme.BLUE,"Training"),(theme.SAND,"Test"))],
               loc="upper center", bbox_to_anchor=(.5,(footer-.40)/height), ncol=2, fontsize=10, borderaxespad=0)
    fig.text(margin/width, .075/height,
             "One dot per listing at its approximate provider location · Saved sample, folds and provider boundaries · "
             +data["cities"][city]["metric_crs"], fontsize=8.5, color=theme.INK)
    return png(fig), details


def grids(data, city="copenhagen"):
    fig, axes = plt.subplots(2, 3, figsize=(11.5, 9))
    fig.subplots_adjust(left=.015, right=.985, top=.915, bottom=.065, wspace=.04, hspace=.15)
    fig.text(.015, .99, data["cities"][city]["display_name"]+" · six spatial block designs · "
             +data["cities"][city]["metric_crs"], va="top", fontsize=17, weight="bold")
    details = {"city":city, "metric_crs":data["cities"][city]["metric_crs"]}
    project = Transformer.from_crs(4326,data["cities"][city]["metric_crs"],always_xy=True).transform
    xmin,ymin,xmax,ymax = np.asarray(transform(project,data["geometries"][city]["mask"]).bounds)/1000
    side = max(xmax-xmin,ymax-ymin)*1.08
    xc,yc = (xmin+xmax)/2,(ymin+ymax)/2
    bounds = (xc-side/2,yc-side/2,xc+side/2,yc+side/2)
    for row, shift in enumerate((0, .5)):
        for col, size in enumerate((1000, 1500, 2000)):
            ax = axes[row, col]
            scheme = f"blocks_{size}m_origin_{shift:g}_{shift:g}".replace(".", "p")
            part = data["assignments"][city].loc[lambda f: f.scheme.eq(scheme)].copy()
            if part.empty:
                raise ValueError("Missing saved block configuration")
            part["gx"] = np.floor((part.metric_x-size*shift)/size).astype(int)
            part["gy"] = np.floor((part.metric_y-size*shift)/size).astype(int)
            cells = part.groupby(["gx", "gy"]).agg(n=("listing_id", "size"),
                        fold=("outer_test_fold", "first"), unique=("outer_test_fold", "nunique")).reset_index()
            if not cells.unique.eq(1).all() or set(part.outer_test_fold) != set("12345"):
                raise ValueError("Saved spatial cell crosses folds or fold is missing")
            base_map(ax, data, city, bounds=bounds)
            visible = cells.loc[cells.n >= 5]
            for cell in visible.itertuples():
                ax.add_patch(Rectangle(((cell.gx*size+size*shift)/1000, (cell.gy*size+size*shift)/1000),
                              size/1000, size/1000, facecolor=FOLDS[int(cell.fold)-1], edgecolor="white", lw=.55, zorder=4))
            label = "no shift" if shift == 0 else "half-cell shift"
            ax.set_title(f"{size/1000:g} km · {label}", loc="left", fontsize=15)
            details[scheme] = {"cell_size_m": size, "origin_fraction": [shift, shift], "visible_cells": len(visible),
                               "suppressed_cells": len(cells)-len(visible), "test_n": len(part)}
    fig.legend(handles=[Patch(color=c, label=str(i)) for i, c in enumerate(FOLDS, 1)],
               title="Saved test fold", title_fontsize=13,
               ncol=5, loc="lower center", bbox_to_anchor=(.5, .005), fontsize=13)
    return png(fig), details


def catchment(data):
    deps = data["accessibility_deps"]
    for name in ("src/study/accessibility.py", "src/spatial/walking_network.py"):
        if sha256_file(ROOT / name) != deps["code"][name]:
            raise ValueError("Executed graph builder changed")
    sources = deps["osm_sources"]["osm_network"]
    graph, metric, qa = pedestrian_graph(elements(sources), "EPSG:25832")
    if qa != data["accessibility"]["graph"]:
        raise ValueError("Public illustration graph does not reproduce frozen graph summary")
    reference = next(r for r in data["context"]["copenhagen"] if r["role"] == "civic_reference")
    point = transform(Transformer.from_crs(4326, 25832, always_xy=True).transform, reference["geometry"])
    target = np.array([point.x+1500, point.y-1050])
    component = max(nx.weakly_connected_components(graph), key=len)
    origin = min(component, key=lambda n: (float(np.sum((np.asarray(metric[n])-target)**2)), n))
    xy = np.asarray(metric[origin])
    ids = np.asarray(list(metric), dtype=np.int64)
    coords = np.asarray([metric[n] for n in ids])
    tree = cKDTree(coords)
    radius = data["design"]["accessibility"]["euclidean_radius_m"]
    speed = data["design"]["accessibility"]["walking_speed_kmh"]
    minutes = data["design"]["accessibility"]["primary_minutes"]
    budget = speed*1000/60*minutes
    candidates = data["destinations"].loc[lambda f: f.category.isin(["food_social", "cultural_tourist"])].copy()
    candidates = candidates.loc[np.linalg.norm(candidates[["x", "y"]].to_numpy()-xy, axis=1) <= radius].copy()
    snap, idx = tree.query(candidates[["x", "y"]])
    costs = nx.single_source_dijkstra_path_length(graph, origin, cutoff=budget, weight="length_m")
    reached = np.array([costs.get(int(ids[i]), np.inf)+d <= budget for i, d in zip(idx, snap, strict=True)])
    candidates["reachable"] = reached
    if candidates.empty or candidates.destination_key.duplicated().any():
        raise ValueError("Empty or duplicated public catchment destination universe")
    segments, reachable = [], []
    for u, v, attr in graph.edges(data=True):
        a, b = np.asarray(metric[u]), np.asarray(metric[v])
        if (np.abs(a-xy) <= 980).all() and (np.abs(b-xy) <= 980).all():
            segments.append([a, b])
            fraction = min(1, max(0, (budget-costs.get(u, np.inf))/attr["length_m"]))
            if fraction > 0:
                reachable.append([a, a+fraction*(b-a)])
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 5.9))
    fig.subplots_adjust(left=.01, right=.99, top=.91, bottom=.12, wspace=.045)
    teal = "#5D9D8C"
    labels = [("food_social", "o", "#D7957E", "Food/social"),
              ("cultural_tourist", "^", "#779DB9", "Culture/tourism")]
    for i, ax in enumerate(axes):
        ax.add_patch(Circle(xy, radius, facecolor="#D9EAE5" if i == 0 else "none",
                            edgecolor=teal, lw=1.1, alpha=.7, linestyle="-" if i == 0 else "--", zorder=1))
        ax.add_collection(LineCollection(segments, colors="#D3DFE1", linewidths=.5, zorder=2))
        if i == 1:
            ax.add_collection(LineCollection(reachable, colors=teal, linewidths=1.5, zorder=3))
        for cat, marker, color, _ in labels:
            points = candidates.loc[candidates.category.eq(cat)]
            ax.scatter(points.x, points.y, s=27, marker=marker, c=color, alpha=1 if i == 0 else .2,
                       edgecolors="white", linewidths=.4, zorder=4)
            if i == 1:
                shown = points.loc[points.reachable]
                ax.scatter(shown.x, shown.y, s=29, marker=marker, c=color,
                           edgecolors=theme.NAVY, linewidths=.5, zorder=5)
        ax.plot(*xy, marker="*", color="#D5A349", markersize=14, markeredgecolor=theme.NAVY, zorder=6)
        ax.set(xlim=(xy[0]-920, xy[0]+920), ylim=(xy[1]-920, xy[1]+920), aspect="equal", xticks=[], yticks=[])
        ax.plot([xy[0]-800, xy[0]-300], [xy[1]-810]*2, color=theme.NAVY, lw=2)
        ax.text(xy[0]-550, xy[1]-770, "500 m", ha="center", fontsize=12, bbox={"facecolor":"white", "edgecolor":"none", "alpha":.85})
        ax.annotate("N", xy=(.93,.95), xytext=(.93,.82), xycoords="axes fraction", ha="center", weight="bold",
                    arrowprops={"arrowstyle":"-|>","color":theme.NAVY})
        ax.set_title(f"A  Straight-line radius: {len(candidates)} destinations" if i == 0
                     else f"B  Walking: {int(reached.sum())} destinations reached", loc="left", fontsize=15)
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#D4DFE4")
    handles = [Line2D([], [], marker="*", linestyle="", color="#D5A349", markeredgecolor=theme.NAVY,
                     markersize=11, label="Public network-node origin"), Line2D([], [], color=teal, lw=2, label="Reachable route")]
    handles += [Line2D([], [], marker=m, linestyle="", color=c, markersize=7, label=l) for _, m, c, l in labels]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(.5,.015), fontsize=12)
    details = {"crs": "EPSG:25832", "snapshot": data["accessibility"]["source_snapshot"],
               "origin_rule": "Nearest node on largest weak component to verified City Hall Square +1500 m east / -1050 m northing; distance/node-id tie break",
               "origin_osm_node_id": int(origin), "origin_xy": xy.tolist(), "radius_m": radius,
               "walking_speed_kmh": speed, "walking_minutes": minutes, "walking_budget_m": budget,
               "origin_connector_m": 0, "destination_connectors_included": True,
               "candidate_n": len(candidates), "reachable_n": int(reached.sum()),
               "counts_by_category": {cat: {"candidate": int(candidates.category.eq(cat).sum()),
                    "reachable": int((candidates.category.eq(cat) & candidates.reachable).sum())} for cat, *_ in labels},
               "graph_summary": qa, "network_sources": sources,
               "scope": "Public cartographic example only; no listing accessibility feature is recomputed"}
    return png(fig), details


def render():
    theme.setup()
    plt.rcParams.update({"font.size": 13, "axes.labelsize": 12,
                         "xtick.labelsize": 12, "ytick.labelsize": 12})
    data = load()
    outputs, details, embedded_text = {}, {}, {}
    jobs = list(zip(NAMES, (catchment, prices, validation, grids), strict=True))
    for city in ("oslo", "stockholm"):
        jobs.extend([(f"random_vs_loao_validation_schematic_{city}", lambda d, c=city: validation(d,c)),
                     (f"spatial_grid_sensitivities_{city}", lambda d, c=city: grids(d,c))])
    for name, function in jobs:
        content, info = function(data)
        outputs[f"figures/{name}.png"] = content
        details[name] = info
        embedded_text[name] = FIGURE_TEXT.pop()
        print("Rendered", name, flush=True)
    historic = json.loads((ROOT / "archive/before_output_cleanup/manifest.json").read_text())["files"]
    originals = {}
    for name in NAMES:
        original = f"outputs/figures/reporting/{name}.png"
        item = next(r for r in historic if r["original_path"] == original)
        path = preserved_path(original, item["sha256"])
        originals[original] = {"archived_path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path),
                               "scientific_values_reused": False}
    inputs = ["config/study/design.json", "config/study/cities.json", "config/reporting/map_context.json",
              "src/study/accessibility.py", "src/spatial/walking_network.py", "src/reporting/thesis_style.py",
              "src/reporting/thesis_cartography.py", "src/reporting/thesis_outputs.py",
              "src/reporting/thesis_sources.py", "src/study/sample_freeze.py", "src/study/store.py",
              "src/study/sources.py", "src/study/archive.py", "src/pipeline/protocol.py",
              "src/pipeline/storage.py", "src/ingestion/common.py"]
    inputs += [f"config/study/{f}_selection.json" for f in ("sample", "validation", "geography", "accessibility")]
    manifest = {"generator": Path(__file__).relative_to(ROOT).as_posix(), "generator_sha256": sha256_file(Path(__file__)),
                "inputs": {p: sha256_file(ROOT/p) for p in inputs}, "sql_sources": data["sources"],
                "sql_packages_sha256": data["sql_packages_sha256"], "catalog_sha256": data["catalog_sha256"],
                "archived_visual_references": originals, "figures": details,
                "embedded_figure_text": embedded_text,
                "outputs": {p: hashlib.sha256(raw).hexdigest() for p, raw in outputs.items()},
                "privacy": "Validation PNGs show individual approximate provider locations at researcher request. No identifiers or coordinate tables are exported. Block maps suppress cells with N<5; other aggregation rules are unchanged.",
                "style_request": "31 October 2026: archived blue/orange layout with one actual dot per listing, superseding the prior aggregated-dot choice for the three validation illustrations",
                "crs": {"listing_source": "EPSG:4326", "city_maps": {c:data["cities"][c]["metric_crs"] for c in CITIES},
                        "sample_coordinates": {c: data["cities"][c]["metric_crs"] for c in CITIES}},
                "models_refitted": False, "listing_features_recomputed": False, "database_writes": False}
    outputs["tables/explanatory_figures_manifest.json"] = (json.dumps(manifest, indent=2, ensure_ascii=False)+"\n").encode()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name, content in render().items():
        path = ROOT / "thesis_report" / name
        if args.check:
            if not path.is_file() or path.read_bytes() != content:
                raise ValueError("Figure or provenance differs: " + name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print("PASS: eight current-study figures and provenance" if args.check else "Wrote eight current-study thesis figures")


if __name__ == "__main__":
    main()
