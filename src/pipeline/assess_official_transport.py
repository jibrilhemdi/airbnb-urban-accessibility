"""Assess official source completeness, retaining only verified existing candidates.

PostGIS stores original source copies, existence decisions and aggregate results.
No frozen feature/network/model is replaced and no outcome is read. Distances,
boundaries and connectivity diagnostics use EPSG:25832 throughout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import networkx as nx
import pandas as pd
import pyogrio
import shapely
from bs4 import BeautifulSoup
from pyproj import CRS
from sqlalchemy import text

from src.db.connection import get_engine
from src.db.migrations import migrate
from src.db.sources import prepare_source, register_records
from src.ingestion.common import PROJECT_ROOT, USER_AGENT, read_manifest, sha256_file, update_manifest, utc_now, write_json
from src.ingestion.download_official_transport import verify_archive, write_inventory


METRO_URL = "https://m.dk/da/"
MOVIA_URL = "https://geoservices.moviatrafik.dk/arcgis/rest/services/WebGIS/bus_webGIS/MapServer/1"
EXPORT = PROJECT_ROOT / "outputs/tables/official_transport/assessment.json"
POLICY_VERSION = "official_transport_existing_only_v1"
SCOPES = """scopes AS (
    SELECT municipality_code AS scope, geom_25832 AS geom FROM spatial.official_municipalities
    UNION ALL SELECT area_kind, geom_25832 FROM spatial.study_area
    WHERE area_kind IN ('official_study_area','buffered_extraction_extent')
)"""


def normalize_name(value) -> str:
    if value is None:
        return ""
    value = re.sub(r"\([^)]*\)", "", str(value))
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def normalize_stop_number(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (float, int)) and float(value).is_integer():
        return str(int(value))
    return str(value).strip() or None


def explicit_status(dataset: str, attributes: dict) -> tuple[str, str]:
    """Unknown values stay unknown; there is no default 'existing'."""
    field = {"cykeldata_kk": "status", "cykelrute_total": "rute_statu"}.get(dataset)
    if field is None:
        return "unknown", "No explicit existence-status rule for this source schema"
    value = attributes.get(field)
    status = {
        "Eksisterende": "existing", "Anlagt rute": "existing",
        "Planlagt": "planned", "Planlagt rute": "planned",
        "Projekteret": "projected", "Projekteret rute": "projected",
    }.get(value, "unknown")
    return status, f"Source field {field}={value!r}; exact documented label rule"


def interval_status(attributes: dict, assessed_on: date) -> tuple[str, str]:
    try:
        start = datetime.strptime(str(attributes["ExistsFrom"]), "%Y%m%d").date()
        end = datetime.strptime(str(attributes["ExistsUpTo"]), "%Y%m%d").date()
    except (ValueError, TypeError, KeyError):
        return "unknown", "Missing/invalid operator validity interval; not filled"
    if end < start:
        return "unknown", "Inverted operator validity interval"
    if start > assessed_on:
        return "planned", "Operator validity begins after the assessment date"
    if end < assessed_on:
        return "unknown", "Operator record validity ended; not an existing candidate"
    return "existing", f"Operator BUS record validity interval includes {assessed_on.isoformat()}"


def metro_reference(payload: bytes) -> list[dict]:
    soup = BeautifulSoup(payload, "html.parser")
    stations = {}
    for item in soup.find_all("li"):
        link = item.find("a", href=True)
        label = item.find("span", class_="font-medium")
        if link and label and "/da/planlaeg-rejsen/" in link["href"]:
            name = label.get_text(" ", strip=True)
            if name:
                stations[link["href"]] = {"name": name, "href": link["href"]}
    if len(stations) < 20:
        raise ValueError("Could not identify the operator's operating-line station list")
    return list(stations.values())


def acquire_evidence(assessed_on: date, bbox: list[float]) -> Path:
    directory = PROJECT_ROOT / "data/raw/official_transport_validation" / assessed_on.isoformat()
    if directory.exists():
        metadata = json.loads((directory / "acquisition_metadata.json").read_text())
        if metadata["query_bbox_25832"] != bbox:
            raise ValueError("Saved reference-query extent differs; use a separate collection date")
        for name, entry in metadata["files"].items():
            if sha256_file(directory / name) != entry["sha256"]:
                raise ValueError(f"Reference source changed: {name}")
        return directory
    payloads, entries = {}, {}

    def collect(name: str, url: str, extent: str, crs: str | None = None):
        with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=90) as response:
            payload = response.read()
            entry = {"provider": "Metro operator / Movia official validation evidence", "source_url": url,
                     "downloaded_at_utc": utc_now(), "content_type": response.headers.get("Content-Type"),
                     "source_last_modified": response.headers.get("Last-Modified"), "source_date": None,
                     "geographic_extent": extent, "source_crs": crs,
                     "asset": name, "local_path": (directory / name).relative_to(PROJECT_ROOT).as_posix(),
                     "sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload), "status": "downloaded"}
        payloads[name], entries[name] = payload, entry
        return payload

    collect("metro_operating_lines.html", METRO_URL, "Copenhagen Metro operating lines/stations; no coordinates supplied")
    metro_reference(payloads["metro_operating_lines.html"])
    service = json.loads(collect("movia_layer_metadata.json", MOVIA_URL + "?f=json", "Movia regional stop-service metadata", "EPSG:25832"))
    if "error" in service or service.get("geometryType") != "esriGeometryPoint":
        raise ValueError("Unexpected official operator stop service")
    envelope = {"xmin": bbox[0], "ymin": bbox[1], "xmax": bbox[2], "ymax": bbox[3], "spatialReference": {"wkid": 25832}}
    query = {"where": "Transportform='BUS'", "geometry": json.dumps(envelope), "geometryType": "esriGeometryEnvelope",
             "inSR": "25832", "spatialRel": "esriSpatialRelIntersects", "returnIdsOnly": "true", "f": "json"}
    extent = json.dumps({"query_bbox": bbox, "crs": "EPSG:25832", "purpose": "Envelope of official municipal study area buffered 2000 m"})
    ids_payload = json.loads(collect("movia_bus_ids.json", MOVIA_URL + "/query?" + urlencode(query), extent, "EPSG:25832"))
    if "error" in ids_payload or "objectIds" not in ids_payload:
        raise ValueError("Operator did not return a complete bus record-ID inventory")
    object_ids = sorted(ids_payload["objectIds"])
    received = []
    # Small public GET requests avoid the service proxy's URL-length limit.
    for page, start in enumerate(range(0, len(object_ids), 100)):
        ids = object_ids[start:start + 100]
        url = MOVIA_URL + "/query?" + urlencode({"objectIds": ",".join(map(str, ids)), "outFields": "*", "outSR": "25832", "returnGeometry": "true", "f": "json"})
        data = json.loads(collect(f"movia_bus_page_{page:03d}.json", url, extent, "EPSG:25832"))
        if "error" in data or data.get("exceededTransferLimit"):
            raise ValueError("Incomplete operator reference page")
        received.extend(f["attributes"]["OBJECTID"] for f in data["features"])
    if sorted(received) != object_ids:
        raise ValueError("Operator page IDs differ from the complete ID inventory")
    metadata = {"assessed_on": assessed_on.isoformat(), "acquired_at_utc": utc_now(), "query_bbox_25832": bbox,
                "geographic_extent": extent, "reference_feature_count": len(received), "files": entries,
                "notes": "Current-date operator references; not a complete historical reconstruction of June 2026"}
    metadata_bytes = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode()
    directory.mkdir(parents=True, exist_ok=False)
    for name, payload in {**payloads, "acquisition_metadata.json": metadata_bytes}.items():
        with (directory / name).open("xb") as handle:
            handle.write(payload)
    metadata_entry = {"provider": "Metro operator / Movia official validation evidence", "source_url": MOVIA_URL,
                      "asset": "validation_acquisition_metadata", "downloaded_at_utc": metadata["acquired_at_utc"],
                      "geographic_extent": extent, "source_crs": "EPSG:25832", "status": "generated_metadata",
                      "local_path": (directory / "acquisition_metadata.json").relative_to(PROJECT_ROOT).as_posix(),
                      "sha256": hashlib.sha256(metadata_bytes).hexdigest(), "size_bytes": len(metadata_bytes)}
    update_manifest([*entries.values(), metadata_entry])
    print(f"Archived operator evidence: {len(received):,} reference bus records", flush=True)
    return directory


def json_attributes(row) -> dict:
    result = {}
    for name, value in row.items():
        if name == "geometry":
            continue
        if value is None or pd.isna(value):
            result[name] = None
        elif isinstance(value, (date, datetime)):
            result[name] = value.isoformat()
        elif hasattr(value, "item"):
            result[name] = value.item()
        else:
            result[name] = value
    return result


def persist_source(conn, source_file_id: int, dataset: str, records: list[dict], epsg: int):
    existing = conn.scalar(text("SELECT count(*) FROM raw.official_transport_source_features WHERE source_file_id=:id"), {"id": source_file_id})
    if existing:
        if existing != len(records):
            raise ValueError("Persistent original-source row count differs from the verified file")
        return
    statement = text("""INSERT INTO raw.official_transport_source_features
        (source_file_id,source_row,dataset,attributes,source_crs_epsg,geom_source,geom_25832)
        VALUES (:id,:row,:dataset,CAST(:attributes AS jsonb),:epsg,
          ST_GeomFromWKB(:wkb,:epsg),ST_Force2D(ST_Transform(ST_GeomFromWKB(:wkb,:epsg),25832)))""")
    params = [{"id": source_file_id, "row": i + 1, "dataset": dataset, "epsg": epsg,
               "attributes": json.dumps(r["attributes"], ensure_ascii=False, allow_nan=False),
               "wkb": r["geometry"].wkb if r["geometry"] is not None else None}
              for i, r in enumerate(records)]
    if params:
        conn.execute(statement, params)


def graph_diagnostic(conn, source_ids: list[int], assessment_id: str, existing_only: bool) -> dict:
    datasets = ["cykeldata_kk", "cykelrute_total"] if existing_only else ["vejmidte_geodk_labels", "stimidter_parker", "sti_frberg"]
    status_filter = "AND s.existence_status='existing'" if existing_only else ""
    rows = conn.execute(text(f"""SELECT ST_AsBinary(ST_Transform(f.geom_source,25832)) FROM raw.official_transport_source_features f
        JOIN meta.official_transport_feature_status s USING(source_file_id,source_row)
        WHERE f.source_file_id=ANY(:ids) AND f.dataset=ANY(:datasets) AND s.assessment_id=:assessment
        AND GeometryType(f.geom_25832) IN ('LINESTRING','MULTILINESTRING') {status_filter}"""),
        {"ids": source_ids, "datasets": datasets, "assessment": assessment_id})
    graph = nx.Graph()
    features = 0
    for row in rows:
        geom = shapely.from_wkb(bytes(row[0]))
        features += 1
        for line in geom.geoms if geom.geom_type == "MultiLineString" else [geom]:
            coords = list(line.coords)
            if len(coords) >= 2:
                # A raw geometry diagnostic only: exact endpoint coordinates,
                # retaining Z where present; no invented crossing/snapping links.
                graph.add_edge(tuple(coords[0]), tuple(coords[-1]))
    components = list(nx.connected_components(graph))
    return {"source_features": features, "endpoint_nodes": graph.number_of_nodes(), "endpoint_edges": graph.number_of_edges(),
            "components": len(components), "largest_component_nodes": max(map(len, components), default=0),
            "method": "Exact full-coordinate endpoints; no gap bridging, intersection noding or routability claim",
            "eligibility": "existing-status cycling records only" if existing_only else "Unverified-status walking geometry; diagnostic only, excluded from existing candidates",
            "crs": "EPSG:25832"}


def rows(conn, query, params=None):
    return [dict(row) for row in conn.execute(text(query), params or {}).mappings()]


def comparison_input_hashes(conn) -> dict:
    """Fingerprint the geometry-only PostGIS inputs used by the diagnostics."""
    sources = {
        "spatial.official_municipalities": "SELECT municipality_code,ST_AsEWKB(geom_25832) FROM spatial.official_municipalities ORDER BY municipality_code",
        "spatial.study_area": "SELECT area_kind,ST_AsEWKB(geom_25832) FROM spatial.study_area WHERE area_kind IN ('official_study_area','buffered_extraction_extent') ORDER BY area_kind",
        "spatial.transit_stations": "SELECT station_key,ST_AsEWKB(geom_25832) FROM spatial.transit_stations ORDER BY station_key",
        "spatial.bus_stops_canonical": "SELECT bus_stop_key,ST_AsEWKB(geom_25832) FROM spatial.bus_stops_canonical ORDER BY bus_stop_key",
    }
    result = {}
    for table, query in sources.items():
        digest, count = hashlib.sha256(), 0
        for key, geom in conn.execute(text(query)):
            digest.update(json.dumps(key, ensure_ascii=False).encode())
            digest.update(b"\n")
            digest.update(bytes(geom) if geom is not None else b"NULL")
            digest.update(b"\n")
            count += 1
        result[table] = {"rows": count, "sha256": digest.hexdigest(), "crs": "EPSG:25832"}
    return result


def assess(conn, ids: list[int], reference_ids: list[int], assessment_id: str, assessed_on: date) -> dict:
    params = {"ids": ids, "ref_ids": reference_ids, "assessment": assessment_id}
    source = """source AS (SELECT f.*,s.existence_status FROM raw.official_transport_source_features f
        JOIN meta.official_transport_feature_status s USING(source_file_id,source_row)
        WHERE s.assessment_id=:assessment AND f.source_file_id=ANY(:ids))"""
    summaries = rows(conn, f"""WITH {source} SELECT dataset,count(*) AS records,
        count(*) FILTER(WHERE existence_status='existing') AS existing,
        count(*) FILTER(WHERE existence_status='planned') AS planned,
        count(*) FILTER(WHERE existence_status='projected') AS projected,
        count(*) FILTER(WHERE existence_status='unknown') AS unknown,
        count(*) FILTER(WHERE geom_25832 IS NULL OR ST_IsEmpty(geom_25832)) AS missing_or_empty_geometry,
        count(*) FILTER(WHERE NOT ST_IsValid(geom_25832)) AS invalid_geometry
        FROM source GROUP BY dataset ORDER BY dataset""", params)
    spatial = rows(conn, f"""WITH {source}, {SCOPES}
        SELECT dataset,scope,count(*) AS intersecting_records,
          count(*) FILTER(WHERE existence_status='existing') AS existing_records
        FROM source CROSS JOIN scopes WHERE CASE WHEN ST_IsValid(geom_25832)
          THEN ST_Intersects(geom_25832,scopes.geom) ELSE false END
        GROUP BY dataset,scope ORDER BY dataset,scope""", params)
    duplicates = rows(conn, f"""WITH {source}, duplicate_groups AS (
        SELECT dataset,ST_AsEWKB(geom_25832) AS geometry_key,count(*) n FROM source
        WHERE geom_25832 IS NOT NULL GROUP BY dataset,ST_AsEWKB(geom_25832) HAVING count(*)>1)
        SELECT dataset,count(*) AS duplicate_geometry_groups,sum(n-1)::int AS excess_records
        FROM duplicate_groups GROUP BY dataset ORDER BY dataset""", params)
    public_station_duplicates = rows(conn, f"""WITH {source}
        SELECT a.attributes->>'objekt_typ' AS station_type,a.attributes->>'navn' AS name,
        count(DISTINCT (a.source_file_id,a.source_row)) AS records,
        max(ST_Distance(a.geom_25832,b.geom_25832)) AS max_separation_m
        FROM source a JOIN source b USING(dataset)
        WHERE a.dataset='station_oversigtskort' AND a.attributes->>'objekt_typ'=b.attributes->>'objekt_typ'
          AND a.attributes->>'navn'=b.attributes->>'navn'
        GROUP BY a.attributes->>'objekt_typ',a.attributes->>'navn'
        HAVING count(DISTINCT (a.source_file_id,a.source_row))>1""", params)
    operator_coverage = rows(conn, f"""WITH {SCOPES}, operator AS (
        SELECT f.* FROM raw.official_transport_source_features f
        JOIN meta.official_transport_feature_status s USING(source_file_id,source_row)
        WHERE f.source_file_id=ANY(:ref_ids) AND f.dataset='movia_operator_bus_reference'
          AND s.assessment_id=:assessment AND s.existence_status='existing'), archive AS (
        SELECT * FROM raw.official_transport_source_features WHERE source_file_id=ANY(:ids) AND dataset='stoppesteder_movia')
        SELECT scope,count(*) AS operator_existing_stops,
          count(*) FILTER(WHERE a.source_row IS NOT NULL) AS matching_archive_stop_numbers,
          count(*) FILTER(WHERE a.source_row IS NOT NULL AND ST_DWithin(o.geom_25832,a.geom_25832,25)) AS matching_id_within_25m,
          count(*) FILTER(WHERE a.source_row IS NOT NULL AND ST_DWithin(o.geom_25832,a.geom_25832,100)) AS matching_id_within_100m
        FROM operator o CROSS JOIN scopes LEFT JOIN archive a
          ON a.attributes->>'stopnr'=o.attributes->>'StopNr'
        WHERE ST_Covers(scopes.geom,o.geom_25832) GROUP BY scope ORDER BY scope""", params)
    osm_matches = []
    for dataset, table, label in [("station_oversigtskort", "spatial.transit_stations", "station"),
                                  ("stoppesteder_movia", "spatial.bus_stops_canonical", "bus")]:
        for eligible in [False, True]:
            status_filter = "AND s.existence_status='existing'" if eligible else ""
            # Compute candidates once: inlining this join repeats the status
            # scan for every OSM point and scope without changing the result.
            result = rows(conn, f"""WITH {SCOPES}, candidates AS MATERIALIZED (
                SELECT f.geom_25832 FROM raw.official_transport_source_features f
                JOIN meta.official_transport_feature_status s USING(source_file_id,source_row)
                WHERE f.source_file_id=ANY(:ids) AND f.dataset=:dataset
                  AND s.assessment_id=:assessment {status_filter})
                SELECT scope,count(*) AS osm_reference_points,
                  count(*) FILTER(WHERE ST_DWithin(o.geom_25832,n.geom_25832,50)) AS within_50m,
                  count(*) FILTER(WHERE ST_DWithin(o.geom_25832,n.geom_25832,100)) AS within_100m,
                  count(*) FILTER(WHERE ST_DWithin(o.geom_25832,n.geom_25832,250)) AS within_250m
                FROM {table} o CROSS JOIN scopes LEFT JOIN LATERAL
                  (SELECT c.geom_25832 FROM candidates c ORDER BY c.geom_25832 <-> o.geom_25832 LIMIT 1) n ON true
                WHERE ST_Covers(scopes.geom,o.geom_25832) GROUP BY scope ORDER BY scope""", {**params, "dataset": dataset})
            osm_matches.extend({**r, "kind": label, "official_candidates": "existing only" if eligible else "all source rows (diagnostic only)"} for r in result)
    return {"dataset_status": summaries, "spatial_scope_counts": spatial, "duplicate_geometries": duplicates,
            "same_type_station_name_duplicates": public_station_duplicates, "operator_bus_coverage": operator_coverage,
            "osm_comparison": osm_matches,
            "existing_cycling_endpoint_graph": graph_diagnostic(conn, ids, assessment_id, True),
            "unverified_walking_endpoint_graph": graph_diagnostic(conn, ids, assessment_id, False),
            "assessed_on": assessed_on.isoformat(), "complete": True}


def run(assessed_on: date):
    from src.pipeline.run_final_presentation import verify_science
    science_count = verify_science()
    engine = get_engine()
    try:
        with engine.connect() as conn:
            bbox = list(conn.execute(text("""SELECT ST_XMin(g),ST_YMin(g),ST_XMax(g),ST_YMax(g)
                FROM (SELECT ST_Envelope(ST_Buffer(geom_25832,2000)) g FROM spatial.study_area
                      WHERE area_kind='official_study_area') x""")).one())
        evidence_directory = acquire_evidence(assessed_on, bbox)
        archives = sorted((PROJECT_ROOT / "data/raw/official_transport").glob("*/acquisition_metadata.json"))
        latest, archive_records = {}, []
        for path in archives:
            archive_records.extend(verify_archive(path.parent))
            for dataset in json.loads(path.read_text())["datasets"]:
                latest[dataset["asset"]] = (path.parent, dataset)
        official_sources = [(name, directory / name / layer["member"]) for name, (directory, dataset) in latest.items() for layer in dataset["layers"]]
        evidence_sources = sorted(evidence_directory.iterdir())
        manifest = {e["local_path"]: e for e in read_manifest()["files"]}
        prepared = [prepare_source(path, manifest=manifest) for _, path in official_sources] + [prepare_source(path, manifest=manifest) for path in evidence_sources]
        registered = register_records(engine, prepared)
        source_ids = {r["relative_path"]: sid for r, sid in zip(prepared, registered)}
        # Include DBF/PRJ/SHX and metadata, not only SHP geometry bytes.
        hashes = {r["relative_path"]: r["file_hash_sha256"] for r in archive_records + prepared}
        with engine.connect() as conn:
            comparison_hashes = comparison_input_hashes(conn)
        code_hash = sha256_file(Path(__file__))
        signature = hashlib.sha256(json.dumps({"hashes": hashes, "comparison": comparison_hashes,
                                              "date": assessed_on.isoformat(), "code": code_hash}, sort_keys=True).encode()).hexdigest()
        assessment_id = POLICY_VERSION + "_" + signature[:16]
        policy = {"version": POLICY_VERSION, "script_sha256": code_hash, "metric_crs": "EPSG:25832",
                  "dimensions": "Original source dimensions retained in geom_source; geom_25832 is a derived 2D metric geometry; endpoint diagnostic retains original Z",
                  "attribute_serialization": "Source dates/timestamps use ISO 8601 text in JSON; source missing values remain JSON null",
                  "source_crs": ["EPSG:4326", "EPSG:25832"], "status": "Only explicit existing labels or current-date operator corroboration qualify; unknown, planned and projected are excluded",
                  "metro_matching": "NFKC, casefold, whitespace normalization and parenthetical suffix removal; no inferred geographic/name aliases",
                  "bus_matching": "Exact stop number plus valid operator BUS interval on assessment date; no name-only merge",
                  "diagnostic_distances_m": [25, 50, 100, 250], "purpose": "Fixed source-discrepancy diagnostics, not tuned accessibility/model parameters",
                  "reference_query_scope": "EPSG:25832 envelope of official municipal union buffered 2000 m",
                  "historical_limit": "Current operator evidence does not establish complete June 2026 positions/service state",
                  "outcome_and_model_access": "No outcome columns, modelling or predictive evaluation"}
        print("Applying source-assessment migration", flush=True)
        migrate(engine)
        with engine.begin() as conn:
            ids = []
            for dataset, path in official_sources:
                sid = source_ids[path.relative_to(PROJECT_ROOT).as_posix()]
                frame = pyogrio.read_dataframe(path)
                epsg = CRS(frame.crs).to_epsg()
                if epsg not in (4326, 25832):
                    raise ValueError(f"Unsupported/unrecorded source CRS: {frame.crs}")
                records = [{"attributes": json_attributes(row), "geometry": row.geometry} for _, row in frame.iterrows()]
                persist_source(conn, sid, dataset, records, epsg)
                ids.append(sid)
                print(f"Verified PostGIS source copy: {dataset}, {len(records):,} rows", flush=True)
            reference_ids, reference_bus_status = [], {}
            for path in sorted(evidence_directory.glob("movia_bus_page_*.json")):
                sid = source_ids[path.relative_to(PROJECT_ROOT).as_posix()]
                data = json.loads(path.read_text())
                records = []
                for feature in data["features"]:
                    geom = feature.get("geometry")
                    records.append({"attributes": feature["attributes"], "geometry": shapely.Point(geom["x"], geom["y"]) if geom else None})
                    number = normalize_stop_number(feature["attributes"].get("StopNr"))
                    if number in reference_bus_status:
                        raise ValueError("Duplicate operator stop number; resolve reference identity before matching")
                    reference_bus_status[number] = interval_status(feature["attributes"], assessed_on)
                persist_source(conn, sid, "movia_operator_bus_reference", records, 25832)
                reference_ids.append(sid)
            metro_path = evidence_directory / "metro_operating_lines.html"
            metro_names = metro_reference(metro_path.read_bytes())
            metro_id = source_ids[metro_path.relative_to(PROJECT_ROOT).as_posix()]
            persist_source(conn, metro_id, "metro_operator_reference", [{"attributes": r, "geometry": None} for r in metro_names], 25832)
            operating_names = {normalize_name(r["name"]) for r in metro_names}
            conn.execute(text("""INSERT INTO meta.official_transport_assessments(assessment_id,assessed_on,policy,input_sha256,results)
                VALUES(:id,:date,CAST(:policy AS jsonb),CAST(:hashes AS jsonb),'{}'::jsonb)
                ON CONFLICT(assessment_id) DO NOTHING"""), {"id": assessment_id, "date": assessed_on, "policy": json.dumps(policy), "hashes": json.dumps(hashes)})
            source_rows = rows(conn, "SELECT source_file_id,source_row,dataset,attributes FROM raw.official_transport_source_features WHERE source_file_id=ANY(:ids)", {"ids": ids + reference_ids})
            statuses = []
            matched_metro = set()
            uncorroborated_metro = set()
            for row in source_rows:
                dataset, attributes = row["dataset"], row["attributes"]
                status, basis = explicit_status(dataset, attributes)
                if dataset == "movia_operator_bus_reference":
                    status, basis = interval_status(attributes, assessed_on)
                elif dataset == "stoppesteder_movia":
                    number = normalize_stop_number(attributes.get("stopnr"))
                    status, basis = reference_bus_status.get(number, ("unknown", "Stop number absent from the current operator reference query"))
                    basis = "Exact operator stop-number lookup: " + basis
                elif dataset == "station_oversigtskort" and attributes.get("objekt_typ") == "Metrostation":
                    name = normalize_name(attributes.get("navn"))
                    if name in operating_names:
                        status, basis = "existing", f"Name occurs on operating metro line list acquired {assessed_on.isoformat()}; coordinates/vintage not certified"
                        matched_metro.add(name)
                    else:
                        uncorroborated_metro.add(attributes.get("navn"))
                statuses.append({"assessment": assessment_id, "id": row["source_file_id"], "row": row["source_row"], "status": status, "evidence": basis})
            conn.execute(text("""INSERT INTO meta.official_transport_feature_status
                (assessment_id,source_file_id,source_row,existence_status,evidence)
                VALUES(:assessment,:id,:row,:status,:evidence) ON CONFLICT DO NOTHING"""), statuses)
            print("Computing boundary, status and source-comparison diagnostics in EPSG:25832", flush=True)
            metrics = assess(conn, ids, reference_ids, assessment_id, assessed_on)
            if comparison_input_hashes(conn) != comparison_hashes:
                raise RuntimeError("PostGIS comparison geometry changed during the assessment; retry")
            metrics.update({"assessment_id": assessment_id, "policy": policy, "input_sha256": hashes,
                "comparison_input_geometry_sha256": comparison_hashes,
                "authoritative_tables": ["raw.official_transport_source_features", "meta.official_transport_feature_status", "meta.official_transport_assessments"],
                "metro_operator_comparison": {"operator_unique_station_names": len(operating_names), "matched_unique_names": len(matched_metro),
                    "unmatched_operator_names": sorted(operating_names - matched_metro), "uncorroborated_source_names": sorted(uncorroborated_metro)},
                "limitations": ["OSM is a discrepancy reference, not ground truth; counts and proximity cannot prove completeness", "No routing suitability is inferred from raw line geometry connectivity", "Unknown existence status is excluded, not imputed", "Operator references describe October 2026, not a complete June 2026 reconstruction"]})
            conn.execute(text("UPDATE meta.official_transport_assessments SET results=CAST(:results AS jsonb) WHERE assessment_id=:id"), {"id": assessment_id, "results": json.dumps(metrics, ensure_ascii=False, allow_nan=False)})
            eligible = conn.scalar(text("SELECT count(*) FROM spatial.official_transport_existing_candidates WHERE existence_status!='existing'"))
            if eligible:
                raise AssertionError("Non-existing records entered the existing-candidate view")
        with engine.connect() as conn:
            saved = conn.scalar(text("SELECT results FROM meta.official_transport_assessments WHERE assessment_id=:id"), {"id": assessment_id})
        write_json(EXPORT, saved)
        write_inventory(next(iter(latest.values()))[0])
        for archive in archives:
            verify_archive(archive.parent)
        if verify_science() != science_count:
            raise AssertionError("Frozen scientific-file inventory changed")
        print(f"Completed {assessment_id}; results exported from PostGIS to {EXPORT.relative_to(PROJECT_ROOT)}", flush=True)
        return saved
    finally:
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assessed-on", required=True, help="Assessment/acquisition date in Europe/Copenhagen, YYYY-MM-DD")
    run(date.fromisoformat(parser.parse_args().assessed_on))
