"""Read-only descriptive means from the verified frozen predictive samples.

Keep the completed aggregate exports unchanged. Validate their original
quantiles against PostGIS before adding arithmetic means to the manuscript.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from sqlalchemy import text

from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.reporting.thesis_sources import verify_catalog
from src.study.sample_freeze import records
from src.study.sources import get_engine
from src.study.specification import CITIES, load_design
from src.study.store import read_package


def summarise(published):
    catalog = verify_catalog()
    design, cities = load_design()
    selected = json.loads((ROOT / "config/study/sample_selection.json").read_text())
    if (design["accessibility"]["walking_speed_kmh"] != 5
            or design["accessibility"]["primary_minutes"] != 10):
        raise ValueError("Frozen display definitions changed")
    summaries, sources = {}, {}
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
            if conn.scalar(text("SELECT current_database()")) != "thesis_accessibility_v4":
                raise ValueError("Wrong analytical database")
            packages = [dict(r) for r in conn.execute(text(
                "SELECT run_id,city,family,summary_sha256,dependencies_sha256 "
                "FROM study.checkpoints ORDER BY run_id")).mappings()]
            if canonical_hash(packages) != catalog["sql_packages_sha256"]:
                raise ValueError("Frozen scientific SQL identities changed")
            for city in CITIES:
                item = selected[city]
                summary, _ = read_package(conn, item["run_id"], city, "sample")
                frame = pd.DataFrame(records(conn, selected, city, "sample", "prediction_sample"))
                if (canonical_hash(summary) != item["summary_sha256"]
                        or canonical_hash(json_records(frame)) != summary["record_sha256"]
                        or len(frame) != summary["prediction_n"]
                        or frame.listing_id.duplicated().any()):
                    raise ValueError("Frozen common predictive sample changed")
                label = "Copenhagen" if city == "copenhagen" else city.title()
                for concept in ("station", "bus", "food", "culture"):
                    for rep, short in (("Euclidean", "e"), ("Walking", "w")):
                        if concept in {"station", "bus"}:
                            column = f"nearest_{concept}_" + ("euclidean_km" if short == "e" else "walking_minutes")
                            values = frame[column].to_numpy(dtype=float)
                            if short == "w":
                                values = values * 5 / 60
                        else:
                            column = f"{concept}_{short}_10"
                            values = frame[column].to_numpy(dtype=float)
                            if not np.equal(values, np.floor(values)).all():
                                raise ValueError("Original opportunity counts must be integers")
                        if len(values) != len(frame) or not np.isfinite(values).all() or (values < 0).any():
                            raise ValueError("Missing/invalid accessibility cannot be filled")
                        matches = [r for r in published if r["city"] == label and r["concept"] == concept and r["representation"] == rep]
                        if len(matches) != 1 or int(matches[0]["n"]) != len(values):
                            raise ValueError("Published accessibility sample differs")
                        original = matches[0]
                        for field, q in (("minimum", 0), ("p05", .05), ("p25", .25),
                                         ("median", .5), ("p75", .75), ("p95", .95), ("maximum", 1)):
                            if not np.isclose(np.quantile(values, q), float(original[field]), rtol=1e-10, atol=1e-10):
                                raise ValueError(f"Published {field} does not reproduce: {label}/{concept}/{rep}")
                        summaries[f"{label}:{concept}:{rep}"] = {
                            "mean": float(np.mean(values)), "median": float(np.median(values)),
                            "n": len(values), "source_column": column,
                            "display_conversion": "minutes × 5/60 to km" if concept in {"station", "bus"} and short == "w" else "original units"}
                sources[city] = {**item, "record_sha256": summary["record_sha256"],
                                 "n": len(frame), "metric_crs": cities[city]["metric_crs"]}
    finally:
        engine.dispose()
    paths = ["scripts/thesis_accessibility_summary.py", "src/study/sample_freeze.py",
             "src/study/store.py", "src/pipeline/protocol.py", "src/pipeline/storage.py",
             "config/study/sample_selection.json", "config/study/design.json"]
    return summaries, {"transaction": "READ ONLY", "sql_packages_sha256": catalog["sql_packages_sha256"],
                       "sources": sources, "code_and_selection": {p: sha256_file(ROOT / p) for p in paths},
                       "summaries": summaries, "missing_data_filled": False,
                       "definition": "Arithmetic mean of original distances/counts, not mean log accessibility"}
