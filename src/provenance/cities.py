"""Explicit, evidence-backed city configuration; no cross-city defaults."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path

from pyproj import CRS
from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.provenance.specification import DEFINITION_VERSION, HISTORICAL_VERSION

VERSION = 'research_design_v4'
CITY_VERSION = 'v4_cities_accessibility_only_20261011'
CITIES = ('copenhagen_frederiksberg', 'oslo', 'stockholm')
FIELDS = ('study_boundary', 'snapshot_date', 'currency', 'metric_crs', 'central_anchor',
          'population_reference_period', 'income_reference_period', 'context_mapping',
          'source_identifiers')


def load_cities(path: Path | None = None, *, design_id: str = DEFINITION_VERSION) -> dict:
    if design_id not in {DEFINITION_VERSION, HISTORICAL_VERSION}:
        raise ValueError('Explicit supported city design required')
    historical = design_id == HISTORICAL_VERSION
    path = path or PROJECT_ROOT / ('archive/previous_analysis/config/cities.json' if historical else 'archive/previous_analysis/config/cities_accessibility_only.json')
    config = json.loads(path.read_text())
    expected = 'v4_cities_20261011' if historical else CITY_VERSION
    if (config.get('version') != VERSION or config.get('city_definition_version') != expected
            or (not historical and config.get('design_id') != design_id)):
        raise ValueError('Explicit V4 city definition version required')
    if set(config['cities']) != set(CITIES):
        raise ValueError('Require exactly the authorized three cities')
    return config


def city_blockers(version: str, city: str, *, config: dict | None = None,
                  root: Path = PROJECT_ROOT, design_id: str = DEFINITION_VERSION) -> list[str]:
    if version != VERSION or city not in CITIES:
        raise ValueError('Explicit V4 version and authorized city required')
    if design_id not in {DEFINITION_VERSION, HISTORICAL_VERSION}:
        raise ValueError('Explicit supported city design required')
    config = load_cities(design_id=design_id) if config is None else config
    record = config['cities'][city]
    blockers = []
    for field in (*FIELDS, *(['housing'] if design_id == HISTORICAL_VERSION else [])):
        node = record.get(field, {})
        value, evidence = node.get('value'), node.get('evidence', [])
        if node.get('status') != 'verified_local_evidence' or value is None or not evidence:
            blockers.append(field + ': unresolved/unqualified')
            continue
        for proof in evidence:
            path = root / proof['path']
            if (not path.resolve().is_relative_to(root.resolve()) or not path.is_file()
                    or sha256_file(path) != proof['sha256']):
                blockers.append(field + ': evidence missing/changed')
        try:
            if field == 'snapshot_date' and date.fromisoformat(value).strftime('%Y-%m') != '2026-06':
                raise ValueError('matched June 2026 required')
            if field == 'metric_crs':
                crs = CRS.from_user_input(value)
                if not crs.is_projected or any(a.unit_conversion_factor != 1 for a in crs.axis_info):
                    raise ValueError('projected metres required')
            if field == 'currency' and (len(value) != 3 or not value.isupper()):
                raise ValueError('source-native currency code required')
            if field == 'central_anchor':
                if (value['crs'] != 'EPSG:4326' or not -180 <= value['longitude'] <= 180
                        or not -90 <= value['latitude'] <= 90 or not value['source_url']):
                    raise ValueError('public anchor provenance and longitude/latitude required')
            if field == 'study_boundary':
                for boundary in value:
                    path = root / boundary['path']
                    if not path.resolve().is_relative_to(root.resolve()) or sha256_file(path) != boundary['sha256']:
                        raise ValueError('boundary checksum mismatch')
            if field == 'context_mapping':
                ids = [row['source_area_id'] for row in value]
                if not ids or len(ids) != len(set(ids)):
                    raise ValueError('duplicate/missing local source-area IDs')
                if any(not row.get('income_source_id') or not row.get('income_geography') for row in value):
                    raise ValueError('income crosswalk unresolved')
            if field == 'housing' and not all(value.get(k) for k in (
                    'qualified_source_id', 'reference_frame_sha256', 'coverage_decision_sha256')):
                raise ValueError('qualified H source, external frame and coverage decision required')
        except (ValueError, TypeError, KeyError, OSError) as error:
            blockers.append(field + ': ' + str(error))
    return blockers
