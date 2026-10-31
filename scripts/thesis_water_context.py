"""Acquire/check display-only EU-Hydro water; persist it separately in PostGIS.

No analytical table, frozen mask, population denominator or model is changed.
Raw service responses are write-once, checksummed source evidence.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests
from pyproj import Transformer
from shapely.geometry import box, mapping, shape, MultiPolygon
from shapely.ops import transform, unary_union
from sqlalchemy import text

from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash
from src.reporting.thesis_sources import verify_catalog
from src.study.sources import get_engine, write_once
from src.study.specification import CITIES, load_design

SELECTOR = ROOT / "config/reporting/manuscript_water.json"
MIGRATION = ROOT / "sql/cartography/002_manuscript_water.sql"
SERVICE = "https://copernicus.discomap.eea.europa.eu/ArcGIS/rest/services/EUHydro/EU_Hydro_RiverNetworkDatabase/MapServer"
PRODUCT = "https://land.copernicus.eu/en/products/eu-hydro/eu-hydro-river-network-database"
POLICY = "https://land.copernicus.eu/en/data-policy"
LAYERS = {0: "Coastal_polygon", 1: "Transit_polygon", 2: "InlandWater", 19: "River_Net_polygon"}
RAW = ROOT / "data/raw/cartographic_context/eu_hydro/2026-10-31"


def source(url, filename, extent, params=None):
    path = RAW / filename
    receipt = Path(str(path) + ".receipt.json")
    if path.exists():
        record = json.loads(receipt.read_text())
        if record["sha256"] != sha256_file(path):
            raise ValueError("Preserved EU-Hydro source changed")
        if record["source_url"] != url or record["request_parameters"] != params:
            raise ValueError("Preserved source does not match the requested endpoint/parameters")
    else:
        response = requests.get(url, params=params, timeout=55)
        response.raise_for_status()
        write_once(path, response.content)
        record = {"path": str(path.relative_to(ROOT)), "source_url": url,
                  "request_parameters": params, "final_url": response.url,
                  "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
                  "geographic_extent": extent, "sha256": sha256_file(path),
                  "bytes": len(response.content), "http_status": response.status_code,
                  "source_crs": "Service EPSG:3857; requested GeoJSON EPSG:4326",
                  "reference_period": "2006–2012, EU-Hydro River Network Database V1",
                  "licence": "Copernicus full, open and free access; attribution and adaptation statement required",
                  "data_policy_url": POLICY, "product_url": PRODUCT,
                  "role": "display_only; never an analytical input"}
        write_once(receipt, (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode())
    return path.read_bytes(), record


def records(conn):
    return [dict(r) for r in conn.execute(text(
        "SELECT city,source_metadata,ST_AsGeoJSON(geom,17)::jsonb AS geometry "
        "FROM cartography.manuscript_water ORDER BY city")).mappings()]


def prepare():
    if SELECTOR.exists():
        raise ValueError("Water context already frozen; use --check")
    catalog = verify_catalog()
    _, cities = load_design()
    geo = json.loads((ROOT / "config/study/geography_selection.json").read_text())
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SET TRANSACTION READ ONLY")
            if conn.scalar(text("SELECT current_database()")) != "thesis_accessibility_v4":
                raise ValueError("Wrong authoritative database")
            checkpoints = [dict(r) for r in conn.execute(text(
                "SELECT run_id,city,family,summary_sha256,dependencies_sha256 "
                "FROM study.checkpoints ORDER BY run_id")).mappings()]
            if canonical_hash(checkpoints) != catalog["sql_packages_sha256"]:
                raise ValueError("Frozen analytical identities changed")
            masks = {c: shape(json.loads(conn.scalar(text(
                "SELECT ST_AsGeoJSON(geom,17) FROM study.geometries "
                "WHERE run_id=:run AND city=:city AND geometry_key='mask'"),
                {"run": geo[c]["run_id"], "city": c}))) for c in CITIES}
        extents = {}
        for city, mask in masks.items():
            crs = cities[city]["metric_crs"]
            native = transform(Transformer.from_crs(4326, crs, always_xy=True).transform, mask)
            x0, y0, x1, y1 = native.bounds
            side = max(x1-x0, y1-y0) * 1.25
            view = box((x0+x1-side)/2, (y0+y1-side)/2,
                       (x0+x1+side)/2, (y0+y1+side)/2)
            bounds = transform(Transformer.from_crs(crs, 4326, always_xy=True).transform, view).bounds
            extents[city] = box(bounds[0]-.01, bounds[1]-.01, bounds[2]+.01, bounds[3]+.01)
        for url, name in [(PRODUCT, "product.html"), (POLICY, "data_policy.html")]:
            source(url, name, "European EU-Hydro product documentation")
        for layer in LAYERS:
            source(f"{SERVICE}/{layer}", f"layer_{layer}.json", "European service layer", {"f": "json"})

        def acquire(task):
            city, layer = task
            extent = extents[city]
            params = {"f": "geojson", "where": "1=1", "geometry": ",".join(map(str, extent.bounds)),
                      "geometryType": "esriGeometryEnvelope", "inSR": 4326, "outSR": 4326,
                      "spatialRel": "esriSpatialRelIntersects", "outFields": "OBJECTID",
                      "returnGeometry": "true", "geometryPrecision": 7,
                      "maxAllowableOffset": .00002, "orderByFields": "OBJECTID", "resultRecordCount": 1000}
            raw, evidence = source(f"{SERVICE}/{layer}/query", f"{city}_{layer}.geojson",
                                   {"bbox": list(extent.bounds), "crs": "EPSG:4326"}, params)
            data = json.loads(raw)
            if data.get("error") or data.get("exceededTransferLimit") or data.get("properties", {}).get("exceededTransferLimit"):
                raise ValueError(f"Incomplete service response: {city}/{layer}")
            if len(data["features"]) >= params["resultRecordCount"]:
                raise ValueError(f"Potentially truncated response: {city}/{layer}")
            geoms = []
            for feature in data["features"]:
                geom = shape(feature["geometry"])
                if not geom.is_valid:
                    raise ValueError(f"Invalid source water geometry: {city}/{layer}; no repair")
                clipped = geom.intersection(extent)
                if not clipped.is_empty:
                    geoms.append(clipped)
            return city, layer, evidence, geoms

        with ThreadPoolExecutor(max_workers=4) as pool:
            acquired = list(pool.map(acquire, [(c, layer) for c in CITIES for layer in LAYERS]))
        rows = []
        for city in CITIES:
            parts = [p for c, _, _, geoms in acquired if c == city for p in geoms]
            water = unary_union(parts)
            if water.geom_type == "Polygon":
                water = MultiPolygon([water])
            if water.geom_type != "MultiPolygon" or not water.is_valid or water.is_empty:
                raise ValueError("Missing or invalid water context")
            metadata = {"sources": [e for c, _, e, _ in acquired if c == city],
                        "spatial_crs": "EPSG:4326", "clipped_to": list(extents[city].bounds),
                        "adaptation": "Service generalisation 0.00002 degrees; clip and union in EPSG:4326; display only",
                        "analytical_mask_changed": False}
            rows.append({"city": city, "metadata": json.dumps(metadata), "geometry": json.dumps(mapping(water))})
        with engine.begin() as conn:
            conn.exec_driver_sql("SELECT pg_advisory_xact_lock(2026103101)")
            if conn.scalar(text("SELECT to_regclass('cartography.manuscript_water') IS NOT NULL")):
                raise ValueError("Refuse to replace persisted water context")
            conn.exec_driver_sql(MIGRATION.read_text())
            conn.execute(text("INSERT INTO cartography.schema_migrations VALUES (:name,:sha)"),
                         {"name": MIGRATION.name, "sha": sha256_file(MIGRATION)})
            conn.execute(text("INSERT INTO cartography.manuscript_water VALUES "
                              "(:city,CAST(:metadata AS jsonb),ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(:geometry),4326)))"), rows)
            persisted = records(conn)
        docs = [json.loads(p.read_text()) for p in sorted(RAW.glob("*.receipt.json"))]
        result = {"purpose": "Figure 4.1 water display only; frozen analytical geography and all fits unchanged",
                  "source_receipts": docs, "records_sha256": canonical_hash(persisted),
                  "migration_sha256": sha256_file(MIGRATION), "geometry_crs": "EPSG:4326",
                  "panel_crs": {c: cities[c]["metric_crs"] for c in CITIES},
                  "frozen_sql_packages_sha256": catalog["sql_packages_sha256"]}
        write_once(SELECTOR, (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode())
        return {"cities": list(CITIES), "records_sha256": result["records_sha256"]}
    finally:
        engine.dispose()


def load_water(conn):
    selected = json.loads(SELECTOR.read_text())
    if sha256_file(MIGRATION) != selected["migration_sha256"]:
        raise ValueError("Water migration changed")
    for receipt in selected["source_receipts"]:
        if sha256_file(ROOT / receipt["path"]) != receipt["sha256"]:
            raise ValueError("EU-Hydro source bytes changed")
    rows = records(conn)
    if canonical_hash(rows) != selected["records_sha256"]:
        raise ValueError("Persisted display water changed")
    return {r["city"]: shape(r["geometry"]) for r in rows}, {
        "selector": str(SELECTOR.relative_to(ROOT)), "sha256": sha256_file(SELECTOR),
        "records_sha256": selected["records_sha256"], "role": "display only"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        print(json.dumps(prepare(), indent=2))
    else:
        engine = get_engine()
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql("SET TRANSACTION READ ONLY")
                water, provenance = load_water(conn)
                print(json.dumps({"valid_cities": list(water), **provenance}, indent=2))
        finally:
            engine.dispose()
