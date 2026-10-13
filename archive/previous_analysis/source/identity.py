"""Scoped paths, immutable manifests and dependency-complete cache identities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import json
from importlib.metadata import version as installed_version
import platform
import sys
from pathlib import Path
import re

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.output_paths import output_file
from src.pipeline.protocol import canonical_hash
from src.v4.cities import CITIES, VERSION, load_cities
from src.v4.specification import DEFINITIONS, DEFINITION_VERSION, HISTORICAL_VERSION, load_design


def token(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value):
        raise ValueError('Unsafe or missing identity component')
    return value


@dataclass(frozen=True)
class Scope:
    version: str
    city: str
    snapshot: str
    run_id: str
    purpose: str = 'research'
    # Existing acquisition adapters remain in their original identity. The active
    # analytical CLI explicitly selects the revised design.
    design_id: str = HISTORICAL_VERSION

    def __post_init__(self):
        if (self.version != VERSION or self.city not in CITIES or self.purpose not in {'research', 'synthetic'}
                or self.design_id not in DEFINITIONS):
            raise ValueError('Explicit V4 version, city and purpose required')
        if date.fromisoformat(self.snapshot).isoformat() != self.snapshot or not self.snapshot.startswith('2026-06-'):
            raise ValueError('Matched June 2026 snapshot required')
        prefix = 'research_v4_' if self.purpose == 'research' else 'synthetic_v4_'
        if not re.fullmatch(prefix + self.city + r'_\d{8}T\d{6}Z', self.run_id):
            raise ValueError('Run ID must identify V4, city and UTC timestamp')
        datetime.strptime(self.run_id.rsplit('_', 1)[-1], '%Y%m%dT%H%M%SZ')

    def params(self) -> dict:
        params = {'version': self.version, 'city': self.city, 'snapshot': self.snapshot,
                  'run_id': self.run_id, 'purpose': self.purpose}
        # Do not change frozen acquisition/export envelopes simply because a new
        # analytical design now exists. New science carries its explicit design.
        if self.design_id != HISTORICAL_VERSION:
            params['design_id'] = self.design_id
        return params


class Paths:
    def __init__(self, scope: Scope, root: Path = PROJECT_ROOT):
        self.scope, self.root = scope, root.resolve()
        if scope.purpose == 'synthetic' and self.root.is_relative_to(PROJECT_ROOT.resolve()):
            raise ValueError('Synthetic filesystem fixtures require a temporary root outside the project')

    def _path(self, *parts: str) -> Path:
        path = self.root.joinpath(*parts)
        if not path.resolve().is_relative_to(self.root):
            raise ValueError('Path/symlink escapes output root')
        return path

    def source(self, source_id: str, name: str) -> Path:
        s = self.scope
        return self._path('data', 'raw', 'v4', s.version, s.city, s.snapshot, token(source_id), token(name))

    def intermediate(self, name: str) -> Path:
        s = self.scope
        return self._path('data', 'interim', 'v4', *self._output_identity(), token(name))

    def _output_identity(self) -> tuple[str, ...]:
        s = self.scope
        # Preserve historical source/report locations. New science gets new paths.
        design = (s.design_id,) if s.design_id != HISTORICAL_VERSION else ()
        return (s.version, *design, s.run_id, s.city, s.snapshot)

    def output(self, kind: str, family: str, name: str) -> Path:
        # Reuse V3 semantic validation, but never its unscoped destination.
        output_file(kind, family, name)
        s = self.scope
        return self._path('outputs', 'v4', *self._output_identity(), kind, family, name)

    def report(self, name: str) -> Path:
        s = self.scope
        return self._path('reports', 'v4', *self._output_identity(), token(name))

    def manifest(self, digest: str) -> Path:
        s = self.scope
        return self._path('data', 'metadata', 'v4', s.version, s.city, s.snapshot, token(digest) + '.json')

    def cache(self, dependencies: dict) -> Path:
        required = {'scientific_sha256', 'source_manifests', 'boundary_sha256', 'metric_crs',
                    'network_sha256', 'taxonomy_sha256', 'routing_parameters', 'software'}
        if set(dependencies) != required or any(value is None for value in dependencies.values()):
            raise ValueError('Complete routing/cache dependency set required')
        s = self.scope
        identity = {'version': s.version, 'city': s.city, 'snapshot': s.snapshot,
                    'purpose': s.purpose, 'dependencies': dependencies}
        if s.design_id != HISTORICAL_VERSION:
            identity['design_id'] = s.design_id
        digest = canonical_hash(identity)
        return self._path('data', 'interim', 'v4', s.version, s.city, s.snapshot, 'route_cache', digest + '.json')


def write_once(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(content)


def freeze_sources(paths: Paths, records: list[dict]) -> tuple[Path, dict]:
    """Freeze provenance only after verifying bytes in this city's V4 raw location."""
    ids = [record['source_id'] for record in records]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Missing/duplicate source IDs; do not silently deduplicate')
    for record in records:
        expected = paths.source(record['source_id'], record['filename'])
        if any(not record.get(k) for k in ('source_url', 'acquired_at_utc', 'geographic_extent', 'sha256', 'source_crs')):
            raise ValueError('Complete source provenance including explicit CRS required')
        if sha256_file(expected) != record['sha256']:
            raise ValueError('Source bytes changed or wrong city/snapshot')
    s = paths.scope
    manifest = {'version': s.version, 'city': s.city, 'snapshot': s.snapshot,
                'purpose': s.purpose, 'records': sorted(records, key=lambda r: r['source_id'])}
    destination = paths.manifest(canonical_hash(manifest))
    content = (json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    if destination.exists():
        if destination.read_bytes() != content:
            raise RuntimeError('Immutable manifest collision')
    else:
        write_once(destination, content)
    return destination, manifest


def scientific_dependencies(city: str, *, root: Path = PROJECT_ROOT, design: dict | None = None,
                            cities: dict | None = None, source_manifests: dict | None = None,
                            design_id: str = DEFINITION_VERSION) -> dict:
    """Separate scientific dependencies from reporting, Git metadata and Markdown.

    Future scientific modules under src/v4 are included automatically. New shared
    science imports must be added to shared below; CI checks this dependency list.
    Source manifests must be frozen/verified before empirical use (preflight gate).
    """
    if city not in CITIES:
        raise ValueError('Authorized city required')
    design = dict(load_design(design_id=design_id) if design is None else design)
    if design_id not in DEFINITIONS or design['definition_version'] != design_id:
        raise ValueError('Scientific design identity mismatch')
    for key in ('active_documents', 'document_index', 'status', 'provenance', 'identities', 'execution_authorized_by_this_configuration', 'cities'):
        design.pop(key, None)
    cities = load_cities(design_id=design_id) if cities is None else cities
    shared = ['src/ingestion/common.py', 'src/ingestion/price.py', 'src/pipeline/build_airbnb_sample.py', 'src/pipeline/output_paths.py',
              'src/pipeline/protocol.py', 'src/pipeline/storage.py', 'src/pipeline/model_specification.py', 'src/db/connection.py',
              'src/pipeline/qualified_income.py', 'src/pipeline/investigate_income_harmonisation.py',
              'src/ingestion/acquire_income_evidence.py', 'src/ingestion/download_copenhagen_statbank.py', 'requirements.txt']
    files = [root / path for path in shared]
    excluded = {'cli.py', 'reporting.py'}
    if design_id == DEFINITION_VERSION:
        excluded |= {'housing.py', 'historical_specification.py'}
    files += [p for p in (root / 'src/v4').glob('*.py') if p.name not in excluded]
    files += [p for p in (root / 'sql/v4_migrations').glob('*.sql')
              if design_id == HISTORICAL_VERSION or p.name != '025_v4_housing_source_audit.sql']
    source_policy = json.loads((root / 'config/v4/listing_sources.json').read_text())
    source_policy = {**{k: v for k, v in source_policy.items() if k != 'cities'},
                     'city': source_policy['cities'][city]}
    if design_id == DEFINITION_VERSION:
        reuse = json.loads((root / 'config/v4/listing_reuse_accessibility_only.json').read_text())
        source_policy['approved_reuse'] = {'design_id': reuse['design_id'], 'source_version': reuse['source_version'],
                                          'selection': reuse['selection'], 'city': reuse['cities'][city]}
    geography_policy = root / 'config/v4/geography_A03_20261011.json'
    if design_id == DEFINITION_VERSION and geography_policy.is_file():
        geography = json.loads(geography_policy.read_text())
        source_policy['geography_qualification'] = {'definition_version': geography['definition_version'],
                                                   'design_id': geography['design_id'], 'city': geography['cities'][city]}
    geography_selection = root / 'config/v4/geography_reuse_accessibility_only.json'
    if design_id == DEFINITION_VERSION and geography_selection.is_file():
        selected_geo = json.loads(geography_selection.read_text())
        source_policy['geography_selection'] = {'design_id': selected_geo['design_id'],
                                                'city': selected_geo['cities'][city]}
    context_policy = root / 'config/v4/context_A04_20261011.json'
    if design_id == DEFINITION_VERSION and context_policy.is_file():
        context = json.loads(context_policy.read_text())
        source_policy['context_qualification'] = {'definition_version':context['definition_version'],
            'income_mode':context['income_mode'], 'income_decision':context['income_decision'], 'city':context['cities'][city],
            'v3_evidence':context['v3_evidence'] if city=='copenhagen_frederiksberg' else []}
    context_selection = root / 'config/v4/context_reuse_accessibility_only.json'
    if design_id == DEFINITION_VERSION and context_selection.is_file():
        selected_context = json.loads(context_selection.read_text())
        source_policy['context_selection'] = {'design_id':selected_context['design_id'], 'city':selected_context['cities'][city]}
    amendment_path = root / 'config/v4/stockholm_boundary_amendment.json'
    if city == 'stockholm' and amendment_path.is_file():
        source_policy['boundary_amendment'] = json.loads(amendment_path.read_text())
    housing_policy_path = root / 'config/v4/housing_sources.json'
    if design_id == HISTORICAL_VERSION and housing_policy_path.is_file():
        housing_policy = json.loads(housing_policy_path.read_text())
        source_policy['housing_sources'] = {
            'definition_version': housing_policy['definition_version'],
            'safeguards': housing_policy['safeguards'],
            'city': housing_policy['cities'][city],
        }
    packages = re.findall(r'^([A-Za-z0-9_-]+)==', (root / 'requirements.txt').read_text(), re.M)
    from pyproj import proj_version_str
    from shapely import geos_version_string
    environment = {'python': sys.version, 'platform': platform.platform(),
                   'packages': {name: installed_version(name) for name in packages},
                   'proj': proj_version_str, 'geos': geos_version_string}
    return {'design': design, 'environment': environment, 'city': city, 'listing_source_policy': source_policy, 'city_definition_version': cities['city_definition_version'],
            'city_configuration': cities['cities'][city], 'source_manifests': source_manifests or {},
            'code_and_environment': {p.relative_to(root).as_posix(): sha256_file(p) for p in sorted(files)}}


def cache_write(paths: Paths, dependencies: dict, payload: dict) -> Path:
    destination = paths.cache(dependencies)
    envelope = {'dependencies': dependencies, 'payload_sha256': canonical_hash(payload), 'payload': payload}
    content = json.dumps(envelope, sort_keys=True, allow_nan=False).encode()
    if destination.exists():
        if destination.read_bytes() != content:
            raise RuntimeError('Refuse to overwrite immutable cache')
    else:
        write_once(destination, content)
    return destination


def cache_read(paths: Paths, dependencies: dict) -> dict | None:
    destination = paths.cache(dependencies)
    if not destination.exists():
        return None
    envelope = json.loads(destination.read_text())
    if envelope['dependencies'] != dependencies or canonical_hash(envelope['payload']) != envelope['payload_sha256']:
        raise RuntimeError('Cache integrity/dependency mismatch')
    return envelope['payload']
