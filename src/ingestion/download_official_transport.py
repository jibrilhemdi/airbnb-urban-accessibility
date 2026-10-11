"""Archive public official transport shapefiles for later assessment, without feature/model changes."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pyogrio

from src.ingestion.common import PROJECT_ROOT, USER_AGENT, read_manifest, sha256_file, update_manifest, utc_now


WFS = "https://wfs-kbhkort.kk.dk/k101/ows"
CATALOGUE = "https://admin.opendata.dk/api/3/action/package_search?fq=organization:city-of-copenhagen&rows=1000"
CAPABILITIES = WFS + "?service=WFS&version=1.0.0&request=GetCapabilities"
# Names are advertised by the official service; never inferred from map appearances.
DATASETS = {
    "cykeldata_kk": ("cykeldata", "Combined cycling infrastructure/routes; inspect route types before use."),
    "vejmidte_geodk_labels": ("vejmidter", "Provider describes this as road-name/code data for map labels; routing suitability unverified."),
    "cykelsti": (None, "Cycle-track layer; completeness and attribute meanings unverified."),
    "cykelrute_total": (None, "Service explicitly includes planned and future supercycle routes; do not treat all as existing."),
    "stimidter_parker": (None, "Park-path centre lines; not a complete pedestrian network."),
    "sti_frberg": (None, "Frederiksberg-named path layer served by Copenhagen; originating custodian and completeness unverified."),
    "fodgaengerfelt": (None, "Pedestrian-crossing markings; not a pedestrian routing network."),
    "jernbane_oversigtskort": (None, "Railway overview geometry; operating status and metro coverage unverified; no timetables."),
    "jernbane_ovs_omegn": (None, "Surrounding-area railway overview geometry; no timetables."),
    "station_oversigtskort": (None, "Station overview layer; station types, entrances and completeness unverified."),
    "stoppesteder_movia": (None, "Movia stop layer served by Copenhagen; municipality coverage, stop types and infrastructure vintage require assessment; no timetables."),
}


def fetch(url: str) -> tuple[bytes, dict]:
    with urlopen(Request(url, headers={"User-Agent": USER_AGENT}), timeout=90) as response:
        return response.read(), {
            "source_url": url, "resolved_url": response.url,
            "downloaded_at_utc": utc_now(), "content_type": response.headers.get("Content-Type"),
            "source_last_modified": response.headers.get("Last-Modified"),
        }


def inspect_zip(path: Path) -> list[dict]:
    """Read the original ZIP without transforming coordinates or geometries."""
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"Corrupt ZIP: {path.name}")
        names = archive.namelist()
        for name in names:
            member = Path(name)
            if member.is_absolute() or ".." in member.parts:
                raise ValueError(f"Unsafe ZIP member: {name}")
        shapes = [name for name in names if name.lower().endswith(".shp")]
        if not shapes:
            raise ValueError(f"No shapefile in response: {path.name}")
        for shape in shapes:
            stem = str(Path(shape).with_suffix(""))
            if not all(stem + ext in names for ext in (".dbf", ".shx", ".prj")):
                raise ValueError(f"Incomplete shapefile bundle: {shape}")
    result = []
    for shape in shapes:
        info = pyogrio.read_info(f"/vsizip/{path.as_posix()}/{shape}", force_feature_count=True, force_total_bounds=True)
        if not info["crs"]:
            raise ValueError(f"Missing CRS: {shape}")
        result.append({
            "member": shape, "source_crs": info["crs"], "feature_count": int(info["features"]),
            "geometry_type": info["geometry_type"], "fields": info["fields"].tolist(),
            "bbox_in_source_crs": list(info["total_bounds"]) if info["total_bounds"] is not None else None,
        })
    return result


def verify_archive(directory: Path) -> list[dict]:
    """Verify this collection independently of unrelated user-added raw files."""
    from src.db.sources import prepare_source

    metadata = json.loads((directory / "acquisition_metadata.json").read_text())
    expected = set(metadata["files"]) | {"acquisition_metadata.json"}
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*")
              if p.is_file() and p.name != ".DS_Store" and not p.name.startswith("._")}
    if expected != actual:
        raise ValueError("Transport archive file inventory differs from acquisition metadata")
    manifest = {r["local_path"]: r for r in read_manifest()["files"]}
    result = []
    for name in sorted(expected):
        path = directory / name
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        if relative not in manifest:
            raise ValueError(f"Missing source-manifest entry: {relative}")
        result.append(prepare_source(path, manifest=manifest))
        if name in metadata["files"] and hashlib.sha256(path.read_bytes()).hexdigest() != metadata["files"][name]["sha256"]:
            raise ValueError(f"Archived file differs from metadata: {name}")
    return result


def assessment_rows(metrics: dict) -> list[str]:
    """Render the aggregate export of the authoritative PostGIS assessment."""
    scope_names = {"0101": "Copenhagen", "0147": "Frederiksberg",
                   "official_study_area": "Municipal union", "planned_15min_extraction": "Union + 1,500 m buffer"}
    rows = ["## Existing-infrastructure completeness assessment", "",
        f"Assessment date: **{metrics['assessed_on']}**. Assessment ID: `{metrics['assessment_id']}`. **The acquired SHP collection does not establish a complete replacement for OSM.**", "",
        "Only explicit existing source labels or corroboration by current operator records qualify as existing candidates. Planned, projected and unknown status are excluded from `spatial.official_transport_existing_candidates`; original records remain immutable. This is a source-assessment view, not an analytical replacement. An existing record is not necessarily a usable routing edge or verified station entrance.", "",
        "| Dataset | Total | Existing candidates | Planned | Projected | Unknown | Missing/empty geometry | Invalid geometry |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in metrics["dataset_status"]:
        rows.append(f"| `{r['dataset']}` | " + " | ".join(f"{r[k]:,}" for k in ("records", "existing", "planned", "projected", "unknown", "missing_or_empty_geometry", "invalid_geometry")) + " |")
    rows.extend(["", "### Bus stops: independent official comparison", "",
        "Reference: [Movia official stop service](https://geoservices.moviatrafik.dk/arcgis/rest/services/WebGIS/bus_webGIS/MapServer/1). Archive complete object-ID queries and every returned page for BUS records in the EPSG:25832 envelope of the municipal union buffered 2,000 m. The comparison below selects reference records whose validity interval includes the assessment date, then assigns them by actual official boundary geometry. Exact stop numbers identify matches; proximity alone does not merge stops.", "",
        "| Scope | Current operator BUS records | IDs present in SHP | Matched ID within 25 m | Matched ID within 100 m | IDs absent from SHP |",
        "|---|---:|---:|---:|---:|---:|"])
    for r in metrics["operator_bus_coverage"]:
        rows.append(f"| {scope_names.get(r['scope'],r['scope'])} | {r['operator_existing_stops']:,} | {r['matching_archive_stop_numbers']:,} | {r['matching_id_within_25m']:,} | {r['matching_id_within_100m']:,} | {r['operator_existing_stops']-r['matching_archive_stop_numbers']:,} |")
    metro = metrics["metro_operator_comparison"]
    rows.extend(["", "### Stations and railway maps", "",
        f"The [Metro operator's operating-line station list](https://m.dk/da/) contains {metro['operator_unique_station_names']} unique names; {metro['matched_unique_names']} match SHP metro names after documented case/whitespace/parenthetical normalization. Unmatched operator names: {', '.join(metro['unmatched_operator_names']) or 'none'}. Uncorroborated SHP names: {', '.join(metro['uncorroborated_source_names']) or 'none'}. A name difference is not proof of a missing geographic station; unresolved aliases stay unknown.", "",
        "Same-type station-name duplicates are retained for review, without automatic merging:", "",
        "| Type | Name | Source records | Maximum separation (m) |", "|---|---|---:|---:|"])
    for r in metrics["same_type_station_name_duplicates"]:
        rows.append(f"| {r['station_type']} | {r['name']} | {r['records']} | {r['max_separation_m']:.2f} |")
    rows.extend(["", "S-train/other-station operating status and completeness have not been independently established. Railway overview geometry supplies neither operating services nor station entrances or schedules. Do not replace the entire station set from a metro name comparison.", "",
        "### Geographic scope", "",
        "Counts use actual geometry intersections with official boundaries in EPSG:25832, not source municipality labels. Line/polygon records may intersect several scopes, so counts are not additive. The existing 1,500 m extraction buffer retains its database name `planned_15min_extraction`; that name describes an analysis extent, not proposed infrastructure.", "",
        "| Dataset | Scope | All intersecting records | Existing candidates |", "|---|---|---:|---:|"])
    for r in metrics["spatial_scope_counts"]:
        rows.append(f"| `{r['dataset']}` | {scope_names.get(r['scope'],r['scope'])} | {r['intersecting_records']:,} | {r['existing_records']:,} |")
    rows.extend(["", "### Walking and cycling network suitability", "",
        "A complete pedestrian graph cannot be certified from these files: road-label centre lines, park paths, Frederiksberg paths and crossing markings lack verified existence status and consistent pedestrian permissions, directions, entrance connections and crossing/bridge levels. They are excluded from strict existing candidates until corroborated. The explicit existing cycling subset also lacks a validated routing topology and complete cross-municipal coverage.", "",
        "Exact-endpoint connectivity is a diagnostic, with no snapping, invented gap links or intersection noding. It does not prove that separated components are physically disconnected, nor that geometric crossings are traversable. Z coordinates are retained where supplied.", "",
        "| Raw-geometry diagnostic | Line records | Endpoint nodes | Edges | Components | Largest component nodes |",
        "|---|---:|---:|---:|---:|---:|"])
    for label,key in [("Existing-labelled cycling", "existing_cycling_endpoint_graph"), ("Unverified walking geometry (ineligible)", "unverified_walking_endpoint_graph")]:
        r = metrics[key]
        rows.append(f"| {label} | " + " | ".join(f"{r[k]:,}" for k in ("source_features","endpoint_nodes","endpoint_edges","components","largest_component_nodes")) + " |")
    rows.extend(["", "Identical EWKB geometry duplicates are counted, not removed:", "",
        "| Dataset | Duplicate geometry groups | Excess records |", "|---|---:|---:|"])
    for r in metrics["duplicate_geometries"]:
        rows.append(f"| `{r['dataset']}` | {r['duplicate_geometry_groups']:,} | {r['excess_records']:,} |")
    rows.extend(["", "### OSM discrepancy checks", "",
        "OSM is a comparison source, not ground truth. Fixed 50/100/250 m nearest-point checks flag representation differences; they do not certify coverage, entrances or identity and are not tuned using prices, outcomes or model performance.", "",
        "| Kind | Official subset | Scope | OSM points | Within 50 m | Within 100 m | Within 250 m |",
        "|---|---|---|---:|---:|---:|---:|"])
    for r in metrics["osm_comparison"]:
        rows.append(f"| {r['kind']} | {r['official_candidates']} | {scope_names.get(r['scope'],r['scope'])} | {r['osm_reference_points']:,} | {r['within_50m']:,} | {r['within_100m']:,} | {r['within_250m']:,} |")
    rows.extend(["", "### Date, persistence and reproducibility", "",
        "The 3–4 October dates are acquisition dates. The operator comparison describes 4 October 2026, not a complete reconstruction of the thesis's June 2026 infrastructure. SHP infrastructure vintages remain unverified. Explicit cycling status labels have no verified effective date. Current-date existence alone is insufficient for historical substitution.", "",
        f"Authoritative source copies, per-record decisions and results are stored in PostGIS `raw.official_transport_source_features`, `meta.official_transport_feature_status` and `meta.official_transport_assessments`. `outputs/tables/official_transport/assessment.json` is a reproducible aggregate export from these tables, not a separate source of truth. Operator evidence is retained under `data/raw/official_transport_validation/{metrics['assessed_on']}/`, with URLs, acquisition timestamps, query extent, EPSG:25832 and SHA-256 recorded in the source manifest. Metro reference names have no invented coordinates. Original source dimensions remain in `geom_source`; planar checks use a derived 2D `geom_25832`.", "",
        "Reproduce the assessment and update this same report:", "", "```sh",
        f".venv/bin/python -m src.pipeline.assess_official_transport --assessed-on {metrics['assessed_on']}", "```", "",
        "The assessment adds source-quality tables and migration 018. Frozen scientific artifact hashes are verified before and after; no primary destinations, walking graph, features, folds or models are replaced. The live provenance registry and schema now include this audit extension, so the whole live database is not identical to the frozen snapshot.", ""])
    return rows


def write_inventory(directory: Path, *, report_path: Path | None = None) -> Path:
    """Maintain one cumulative inventory from every immutable dated acquisition."""
    collections = []
    for metadata_path in sorted(directory.parent.glob("*/acquisition_metadata.json")):
        metadata = json.loads(metadata_path.read_text())
        stamp = date.fromisoformat(metadata["retrieval_date"]).isoformat()
        if metadata_path.parent.name != stamp:
            raise ValueError(f"Archive directory and acquisition date disagree: {metadata_path}")
        collections.append((metadata_path.parent, metadata))
    if not collections:
        raise ValueError("No official transport acquisition records found")

    latest = {}
    for archive_directory, metadata in collections:
        for dataset in metadata["datasets"]:
            latest[dataset["asset"]] = (archive_directory, metadata, dataset)

    def candidate(name: str) -> str:
        if name not in latest:
            return "Not acquired"
        return f"`{name}` ({latest[name][2]['feature_count']:,} archived features)"

    total_shapes = sum(len(d["layers"]) for _, m in collections for d in m["datasets"])
    total_files = sum(len(m["files"]) + 1 for _, m in collections)
    rows = [
        "# Official transport source inventory", "",
        "## Analytical source decision — 2026-10-04", "",
        "**User decision: do not use this official transport SHP collection in the thesis analysis. Retain the existing OSM transport inputs.** The archived official files, operator evidence and PostGIS source-quality assessment are retained as reference material only. Existing-status candidate records are audit results, not approved analytical inputs. This decision concerns the assessed transport collection; it does not change the use of official municipal boundaries or other official sources already used in the thesis. See the dated decision in `docs/decision_log.md`.", "",
        f"The archive currently contains **{len(latest)} distinct official datasets**, **{total_shapes} original SHP files** across **{len(collections)} dated acquisitions**, and **{total_files} raw/source-metadata files**. Original ZIPs and unmodified extracted shapefile bundles remain under `data/raw/official_transport/YYYY-MM-DD/`.", "",
        "This is the single cumulative report. Each download regenerates it from all saved acquisition records, retaining dated entries below. The inventory uses the most recently acquired version of each dataset; earlier raw versions remain immutable. An acquisition date records when the source was downloaded, not when the infrastructure was built, updated or operational.", "",
        "Sources: [City of Copenhagen public WFS](https://wfs-kbhkort.kk.dk/k101/ows?service=WFS&version=1.0.0&request=GetCapabilities) and its [Open Data DK catalogue](https://www.opendata.dk/city-of-copenhagen). These are provider-supplied SHP exports, not conversions from OSM.", "",
        "## Current inventory", "",
        "| Dataset / directory | Acquired | Features | Source CRS | Catalogue licence | Limitations |",
        "|---|---|---:|---|---|---|",
    ]
    for name, (_, metadata, dataset) in latest.items():
        rows.append(f"| `{name}` | {metadata['retrieval_date']} | {dataset['feature_count']:,} | {', '.join(dataset['source_crs'])} | {dataset['license'] or 'Not verified for individual layer'} | {dataset['caveats']} |")
    rows.extend(["", "## Can these replace the current OSM inputs?", "",
        "**A full replacement is not established.** The official files are candidates for source validation; no analytical source has been replaced.", "",
        "| Current or proposed input | Official candidate | Replacement status |",
        "|---|---|---|",
        f"| Rail/metro/S-train destination points | {candidate('station_oversigtskort')} | Candidate after checking current operating status, duplicates, coordinate meaning, complete buffered study-area coverage and vintage. Counts alone do not establish completeness. |",
        f"| Bus-stop destination points | {candidate('stoppesteder_movia')} | Candidate after validation; establish Copenhagen, Frederiksberg and surrounding-buffer coverage. See the source municipality labels below. |",
        "| Walking routing graph | Road-label centre lines, park paths, `sti_frberg` and crossing markings | No complete connected pedestrian graph has been validated. Check access rules, connectivity, bridge/underpass levels, entrances and buffer coverage before substitution. |",
        "| Cycling network | Cycle tracks and cycling/supercycle routes | Useful source layers; filter existing versus planned/projected infrastructure and validate legal directions, connections and cross-municipal coverage. Cycling is not an input in the frozen primary analysis. |",
        "| Railway alignment maps | Two railway overview layers | Useful map context, but not operating services or timetables. |",
        "| Food/social and cultural/tourist destinations | No replacement acquired in this transport collection | Existing OSM destination sets remain required for the current analysis. |",
        "| Timetable-sensitive transit accessibility | No GTFS/NeTEx acquired | Unavailable from this SHP collection. |", "",
        "The frozen comparison uses the same canonical station/food/culture points and walking graph for its Euclidean and walking measures. Replacing station or stop points may still require the OSM walking graph; changing a destination source changes the resulting features. Validate sources without using outcome values or test-fold model scores to choose them. Any analytical replacement follows the documented scientific-version workflow, rather than overwriting frozen v1.", "",
        "## Source attribute checks", "",
        "These counts are reproduced from the original SHP attributes. They describe provider labels, not a spatial boundary assignment, verified operational status, or evidence of complete network coverage. Missing labels remain explicitly missing. No spatial transformation is performed.", "",
        "| Dataset | Source field | Source value | Rows |", "|---|---|---|---:|",
    ])
    checks = {
        "station_oversigtskort": ("objekt_typ", "kommune"),
        "stoppesteder_movia": ("kommune",),
        "cykeldata_kk": ("status", "kommune"),
        "cykelrute_total": ("rute_statu",),
        "sti_frberg": ("feat_type", "komnavn"),
    }
    for name, fields in checks.items():
        if name not in latest:
            continue
        archive_directory, _, dataset = latest[name]
        # These selected layers have a single SHP; retain raw attribute values.
        shape = archive_directory / name / dataset["layers"][0]["member"]
        attributes = pyogrio.read_dataframe(shape, columns=list(fields), read_geometry=False)
        for field in fields:
            counts = [{"value": str(value), "rows": int(count)}
                      for value, count in attributes[field].value_counts(dropna=True).items()]
            missing = int(attributes[field].isna().sum())
            if missing:
                counts.append({"value": None, "rows": missing})
            for item in counts:
                value = "Missing (NULL)" if item["value"] is None else item["value"].replace("|", "\\|")
                rows.append(f"| `{name}` | `{field}` | {value} | {item['rows']:,} |")
    rows.extend(["", "Source cycling status labels distinguish existing, planned and projected infrastructure; none are silently recoded. Station labels include S-train, metro and other stations; the independent operating-status assessment below is separate from these raw labels. The Copenhagen-served `sti_frberg` has Frederiksberg labels; that does not establish a complete municipality walking network.", ""])
    assessment_export = PROJECT_ROOT / "outputs/tables/official_transport/assessment.json"
    if assessment_export.exists():
        metrics = json.loads(assessment_export.read_text())
        assessed_hashes = metrics["input_sha256"]
        current_shapes = [archive_directory / name / layer["member"]
                          for name, (archive_directory, _, dataset) in latest.items() for layer in dataset["layers"]]
        if all(assessed_hashes.get(p.relative_to(PROJECT_ROOT).as_posix()) == sha256_file(p) for p in current_shapes):
            rows.extend(assessment_rows(metrics))
        else:
            rows.extend(["## Assessment needs updating", "", "The saved assessment does not cover every current SHP checksum. Re-run the source assessment before qualifying the current inventory as existing infrastructure.", ""])
    rows.extend([
        "## Acquisition history", "",
        "Dated collections are additive source acquisitions. A later acquisition does not by itself establish newer infrastructure, corrected data or a replacement for an earlier layer.", "",
    ])
    seen = set()
    for archive_directory, metadata in collections:
        stamp = metadata["retrieval_date"]
        names = [d["asset"] for d in metadata["datasets"]]
        added = [name for name in names if name not in seen]
        repeated = [name for name in names if name in seen]
        shapes = sum(len(d["layers"]) for d in metadata["datasets"])
        rows.extend([f"### {stamp}", "",
            f"Archive: `{archive_directory.relative_to(PROJECT_ROOT).as_posix()}/`. {len(names)} {'dataset' if len(names) == 1 else 'datasets'}, {shapes} SHP {'file' if shapes == 1 else 'files'} and {len(metadata['files']) + 1} raw/source-metadata files.", "",
            "Added to the cumulative inventory: " + (", ".join(f"`{name}`" for name in added) or "none") + ".",
        ])
        if repeated:
            rows.extend(["", "Previously acquired datasets collected again: " + ", ".join(f"`{name}`" for name in repeated) + ". The current inventory selects this later acquisition; earlier source files remain archived."])
        if stamp == "2026-10-03":
            rows.extend(["", "Initial acquisition: cycling, road-label centre lines, park/Frederiksberg paths, crossings, railway overview lines and station points. Mixed geometry in `cykelsti` and `stimidter_parker` produced separate line and point SHP files. The bus-stop layer was already advertised in the saved service metadata but was missed in the initial selection."])
        if stamp == "2026-10-04" and "stoppesteder_movia" in names:
            rows.extend(["", "Added the previously missed `stoppesteder_movia` stop layer in a separate collection. This corrects the acquisition omission; it is not evidence that the provider first published bus stops on this date. The 3 October source archive is unchanged."])
            if assessment_export.exists():
                rows.extend(["", "Subsequent source assessment: archived independent Metro/Movia operator evidence and applied an existing-only candidate policy. Geographic checks establish missing bus-stop IDs in Frederiksberg, Copenhagen and the study buffer; cycling planned/projected records are excluded. Full pedestrian/cycling routing suitability and historical June 2026 completeness remain unestablished. Results and dates are maintained in this same report."])
        selected = " ".join(names)
        rows.extend(["", "Verify this dated archive and regenerate the cumulative report:", "", "```sh",
            f".venv/bin/python -m src.ingestion.download_official_transport --retrieval-date {stamp} --datasets {selected} --register-provenance",
            "```", "",
        ])
        seen.update(names)
    rows.extend(["## Provenance, verification and remaining access gaps", "",
        "ZIP integrity, SHP/SHX/DBF/PRJ components, readable CRS and feature counts were checked during acquisition. Each returned count matched an independently archived WFS `resultType=hits` response; those counts establish response completeness, not real-world coverage. SHA-256, original URLs, acquisition timestamps, advertised EPSG:4326 extents, actual SHP bounds/CRS and fields are retained in each `acquisition_metadata.json` and `data/metadata/source_manifest.json`.", "",
        "Catalogue-linked licences are recorded where available. Individual WFS layers without licence metadata require confirmation before reuse or redistribution. Infrastructure vintages remain unknown; catalogue modification dates are not used as source dates. Raw sources and source-manifest hashes are preserved. PostgreSQL/PostGIS `meta.source_files` stores registered provenance; no geometry from this collection has been imported into analytical feature tables.", "",
        "The 3 October investigation confirmed [GeoDanmark60_SHP](https://confluence.kds.dk/pages/viewpage.action?pageId=25724273), including municipal downloads in EPSG:25832. It remains unacquired because the documented service requires registered account credentials. The documented legacy extract service is retiring on 15 January 2027; check the provider's current access route when obtaining access.", "",
        "The direct map configuration linked by [Frederiksberg's cycling page](https://www.frederiksberg.dk/by-bolig-og-miljoe/trafik/kom-rundt-i-byen/cyklister) returned HTTP 404 in the 3 October investigation. No direct Frederiksberg SHP export was verified; the original custodian of the Copenhagen-served `sti_frberg` is unverified.", "",
        "[Rejseplanen](https://labs.rejseplanen.dk/hc/da/articles/24750139021341-Oversigt-over-udstillede-data) documents separate schedule and stop-data access. No GTFS was acquired. The SHP station/stop geometry does not supply timetable-sensitive accessibility.", "",
        "Existing dated archives are checked without another download or replacement. Use a new acquisition date for a new immutable collection. Future runs update this same report and add a dated history entry. `--register-provenance` registers only the selected collection, without changing analytical tables, routing, models, folds or the scientific freeze.", "",
    ])
    report = report_path or PROJECT_ROOT / "reports/official_transport_source_inventory.md"
    report.write_text("\n".join(rows), encoding="utf-8")
    return report


def acquire(retrieval_date: str, dataset_names: list[str] | None = None) -> Path:
    date.fromisoformat(retrieval_date)
    selected = list(DATASETS) if dataset_names is None else dataset_names
    if not selected or len(set(selected)) != len(selected) or any(name not in DATASETS for name in selected):
        raise ValueError("Specify distinct advertised dataset names from DATASETS")
    destination = PROJECT_ROOT / "data/raw/official_transport" / retrieval_date
    if destination.exists():
        # Verify the archive and return without replacing any raw file.
        verify_archive(destination)
        if dataset_names is not None:
            saved = json.loads((destination / "acquisition_metadata.json").read_text())
            if set(selected) != {d["asset"] for d in saved["datasets"]}:
                raise ValueError("Existing dated archive has a different dataset selection; choose a new date")
        return destination

    catalogue_bytes, catalogue_headers = fetch(CATALOGUE)
    catalogue = json.loads(catalogue_bytes)
    packages = catalogue["result"]["results"]
    if not catalogue["success"] or len(packages) != catalogue["result"]["count"]:
        raise ValueError("Incomplete official catalogue response")
    by_name = {p["name"]: p for p in packages}
    caps_bytes, caps_headers = fetch(CAPABILITIES)
    caps = ET.fromstring(caps_bytes)
    advertised = {f.findtext("{*}Name"): f for f in caps.findall(".//{*}FeatureType")}
    payloads = {"copenhagen_catalogue.json": catalogue_bytes, "copenhagen_wfs_capabilities.xml": caps_bytes}
    records = {}
    for name, headers in (("copenhagen_catalogue.json", catalogue_headers), ("copenhagen_wfs_capabilities.xml", caps_headers)):
        records[name] = {**headers, "asset": "official_transport_source_metadata", "provider": "City of Copenhagen / Open Data DK", "geographic_extent": "Copenhagen public catalogue/service; see per-layer extents", "source_crs": None}
    metadata = {"retrieval_date": retrieval_date, "acquired_at_utc": utc_now(), "purpose": "Source archive for possible later use; no analytical ingestion, routing or modelling", "datasets": [], "files": records}
    with tempfile.TemporaryDirectory(prefix="official_transport_") as temporary:
        for name in selected:
            package_name, caveat = DATASETS[name]
            feature = advertised.get("k101:" + name)
            if feature is None:
                raise ValueError(f"Layer is not advertised: {name}")
            package = by_name[package_name] if package_name else None
            if package:
                resource = next(r for r in package["resources"] if r["format"].upper() == "SHP")
                url = resource["url"]
            else:
                url = WFS + "?" + urlencode({"service": "WFS", "version": "1.0.0", "request": "GetFeature", "typeName": "k101:" + name, "outputFormat": "SHAPE-ZIP", "SRSNAME": "EPSG:25832"})
            hit_url = WFS + "?" + urlencode({"service": "WFS", "version": "1.1.0", "request": "GetFeature", "typeName": "k101:" + name, "resultType": "hits"})
            hits_bytes, hits_headers = fetch(hit_url)
            expected_count = int(ET.fromstring(hits_bytes).attrib["numberOfFeatures"])
            payload, headers = fetch(url)
            staged = Path(temporary) / (name + ".zip")
            staged.write_bytes(payload)
            layers = inspect_zip(staged)
            returned_count = sum(layer["feature_count"] for layer in layers)
            if returned_count != expected_count:
                raise ValueError(f"Possible truncated/changing response for {name}: expected {expected_count}, received {returned_count}")
            bbox = feature.find("{*}LatLongBoundingBox")
            extent = {k: float(v) for k, v in bbox.attrib.items()} if bbox is not None else None
            entry = {
                **headers, "provider": "City of Copenhagen public WFS",
                "asset": name, "source_page": "https://www.opendata.dk/city-of-copenhagen/" + package_name if package_name else CAPABILITIES,
                "source_crs": sorted({layer["source_crs"] for layer in layers}),
                "geographic_extent": json.dumps({"bbox_crs": "EPSG:4326", "advertised_bbox": extent}, sort_keys=True),
                "license": package["license_id"] if package else None,
                "license_status": "catalogue licence recorded" if package else "not verified for this individual WFS layer",
                "source_date": None, "source_date_note": "Live service state; catalogue timestamps are not dataset vintages",
                "caveats": caveat, "wfs_type_name": "k101:" + name,
            }
            payloads[name + ".zip"] = payload
            records[name + ".zip"] = entry
            payloads[name + "_hits.xml"] = hits_bytes
            records[name + "_hits.xml"] = {**entry, **hits_headers, "asset": name + "_feature_count_metadata"}
            with zipfile.ZipFile(io.BytesIO(payload)) as archive:
                for member in archive.infolist():
                    if not member.is_dir():
                        local = name + "/" + member.filename
                        payloads[local] = archive.read(member)
                        records[local] = {**entry, "archive_member": member.filename, "archive_path": name + ".zip"}
            metadata["datasets"].append({**entry, "archive_path": name + ".zip", "feature_count": returned_count, "expected_wfs_feature_count": expected_count, "layers": layers})
            print(f"Validated {name}: {returned_count:,} features, {len(payload):,} ZIP bytes", flush=True)

    for name, payload in payloads.items():
        records[name].update({"sha256": hashlib.sha256(payload).hexdigest(), "size_bytes": len(payload), "status": "downloaded"})
    payloads["acquisition_metadata.json"] = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode()
    records["acquisition_metadata.json"] = {"provider": "City of Copenhagen public WFS", "source_url": CAPABILITIES, "asset": "official_transport_acquisition_metadata", "downloaded_at_utc": metadata["acquired_at_utc"], "geographic_extent": "Per-layer bounding boxes and CRS are recorded in this acquisition metadata", "sha256": hashlib.sha256(payloads["acquisition_metadata.json"]).hexdigest(), "size_bytes": len(payloads["acquisition_metadata.json"]), "status": "generated_metadata"}
    destination.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(payload)
    update_manifest([{**entry, "local_path": (destination / name).relative_to(PROJECT_ROOT).as_posix()} for name, entry in records.items()])
    verify_archive(destination)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retrieval-date", required=True, help="Acquisition date YYYY-MM-DD; use a new date for a new archive")
    parser.add_argument("--datasets", nargs="+", choices=list(DATASETS), help="Acquire selected layers only; defaults to all advertised candidates")
    parser.add_argument("--register-provenance", action="store_true", help="Register only this archive's provenance in meta.source_files; no spatial/analytical import")
    args = parser.parse_args()
    directory = acquire(args.retrieval_date, args.datasets)
    write_inventory(directory)
    if args.register_provenance:
        from src.db.connection import get_engine
        from src.db.sources import register_records
        engine = get_engine()
        try:
            ids = register_records(engine, verify_archive(directory))
            print(f"Verified and registered {len(ids)} source files in PostGIS metadata")
        finally:
            engine.dispose()
    print(directory)
