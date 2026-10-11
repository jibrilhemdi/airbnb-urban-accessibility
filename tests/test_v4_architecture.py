"""Synthetic fixtures exercise isolation; no research results or production writes."""
from contextlib import redirect_stdout, redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash
from src.v4.cities import CITIES, VERSION, city_blockers, load_cities
from src.v4.cli import main
from src.v4.identity import Paths, Scope, cache_read, cache_write, freeze_sources, scientific_dependencies, write_once
from src.v4.persistence import get_engine, verify_database


def scope(city='oslo', purpose='synthetic', stamp='20261011T120000Z'):
    return Scope(VERSION, city, '2026-06-30', ('synthetic' if purpose == 'synthetic' else 'research') + '_v4_' + city + '_' + stamp, purpose)


def source_fixture(paths):
    path = paths.source('fixture', 'source.txt')
    write_once(path, b'synthetic fixture, never a research result\n')
    records = [{'source_id': 'fixture', 'filename': 'source.txt', 'source_url': 'synthetic://fixture',
                'acquired_at_utc': '2026-10-11T12:00:00Z', 'geographic_extent': 'synthetic',
                'source_crs': 'not_spatial', 'sha256': sha256_file(path)}]
    return records


class CityConfigurationTests(unittest.TestCase):
    def test_roster_evidence_and_fail_closed_unknowns(self):
        config = load_cities()
        self.assertEqual(set(config['cities']), set(CITIES))
        blocked = city_blockers(VERSION, 'copenhagen_frederiksberg')
        self.assertEqual(blocked, ['housing: unresolved/unqualified'])
        for city in ('oslo', 'stockholm'):
            blockers = city_blockers(VERSION, city)
            self.assertEqual(len(blockers), 8 if city == 'oslo' else 7)
            if city == 'oslo':
                self.assertIn('study_boundary: unresolved/unqualified', blockers)
            else:
                self.assertFalse(any(x.startswith('study_boundary:') for x in blockers))
                self.assertEqual(config['cities'][city]['study_boundary']['value'][0]['source_date'],'2025-01-01')
            self.assertIn('housing: unresolved/unqualified', blockers)
            self.assertEqual(config['cities'][city]['snapshot_date']['value'], '2026-06-30')
            self.assertTrue(config['cities'][city]['snapshot_date']['evidence'])

    def test_no_city_projection_or_income_fallback(self):
        for city in ('oslo', 'stockholm'):
            record = load_cities()['cities'][city]
            for field in ('metric_crs', 'context_mapping', 'central_anchor'):
                self.assertIsNone(record[field]['value'])
            self.assertEqual(record['currency']['value'], {'oslo':'NOK','stockholm':'SEK'}[city])
        mapping = load_cities()['cities']['copenhagen_frederiksberg']['context_mapping']['value']
        self.assertEqual(len(mapping), 11)
        self.assertEqual(mapping[-1]['income_source_id'], 'IFOR35')
        self.assertEqual({r['income_source_id'] for r in mapping[:-1]}, {'KKIND5'})

    def test_changed_evidence_and_bad_metric_crs_fail(self):
        config = load_cities()
        config['cities']['copenhagen_frederiksberg']['metric_crs']['value'] = 'EPSG:4326'
        self.assertTrue(any('projected metres' in x for x in city_blockers(VERSION, 'copenhagen_frederiksberg', config=config)))
        config['cities']['copenhagen_frederiksberg']['currency']['evidence'][0]['sha256'] = '0' * 64
        self.assertIn('currency: evidence missing/changed', city_blockers(VERSION, 'copenhagen_frederiksberg', config=config))

    def test_explicit_version_city_snapshot_and_identity(self):
        for version, city in [('research_design_v3', 'oslo'), (VERSION, 'copenhagen')]:
            with self.assertRaises(ValueError):
                city_blockers(version, city)
        with self.assertRaises(ValueError):
            Scope(VERSION, 'oslo', '2026-07-01', 'research_v4_oslo_20261011T120000Z')
        with self.assertRaises(ValueError):
            Scope(VERSION, 'oslo', '2026-06-30', 'research_v4_stockholm_20261011T120000Z')


class ScopedFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paths = Paths(scope(), Path(self.temp.name))

    def test_city_run_and_snapshot_isolation(self):
        a = self.paths
        b = Paths(scope('stockholm'), a.root)
        c = Paths(scope(stamp='20261011T130000Z'), a.root)
        d = Paths(Scope(VERSION, 'oslo', '2026-06-29', scope().run_id, 'synthetic'), a.root)
        self.assertNotEqual(a.source('fixture', 'data.csv'), b.source('fixture', 'data.csv'))
        self.assertNotEqual(a.source('fixture', 'data.csv'), d.source('fixture', 'data.csv'))
        self.assertNotEqual(a.output('tables', 'reporting', 'metrics.csv'), c.output('tables', 'reporting', 'metrics.csv'))
        self.assertNotEqual(a.intermediate('data.csv'), c.intermediate('data.csv'))
        self.assertNotEqual(a.report('report.json'), b.report('report.json'))
        with self.assertRaises(ValueError):
            Paths(scope())

    def test_traversal_and_symlink_refusal(self):
        with self.assertRaises(ValueError):
            self.paths.source('../stockholm', 'data.csv')
        with self.assertRaises(ValueError):
            self.paths.output('tables', 'reporting', '../data.csv')
        (self.paths.root / 'data').symlink_to(PROJECT_ROOT / 'data', target_is_directory=True)
        with self.assertRaises(ValueError):
            self.paths.source('fixture', 'source.txt')

    def test_manifest_immutability_duplicate_source_and_checksum(self):
        records = source_fixture(self.paths)
        path, manifest = freeze_sources(self.paths, records)
        self.assertEqual(freeze_sources(self.paths, records), (path, manifest))
        with self.assertRaises(FileExistsError):
            write_once(path, b'changed')
        with self.assertRaises(ValueError):
            freeze_sources(self.paths, records * 2)
        bad = deepcopy(records)
        bad[0]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            freeze_sources(self.paths, bad)
        other = Paths(scope('stockholm'), self.paths.root)
        with self.assertRaises(FileNotFoundError):
            freeze_sources(other, records)

    def test_cache_all_dependencies_city_and_integrity(self):
        dependencies = {'scientific_sha256': 'a' * 64, 'source_manifests': {'fixture': 'b' * 64},
                        'boundary_sha256': 'c' * 64, 'metric_crs': 'synthetic_crs',
                        'network_sha256': 'd' * 64, 'taxonomy_sha256': 'e' * 64,
                        'routing_parameters': {'speed': 5}, 'software': {'routing': 'fixture_v1'}}
        cache_write(self.paths, dependencies, {'distance': 42})
        self.assertEqual(cache_read(self.paths, dependencies), {'distance': 42})
        for key in dependencies:
            changed = deepcopy(dependencies)
            changed[key] = {'changed': True} if isinstance(changed[key], dict) else 'changed'
            self.assertIsNone(cache_read(self.paths, changed), key)
        self.assertIsNone(cache_read(Paths(scope('stockholm'), self.paths.root), dependencies))
        other_purpose = Paths(scope(purpose='research'), self.paths.root)
        self.assertIsNone(cache_read(other_purpose, dependencies))
        with self.assertRaises(ValueError):
            self.paths.cache({'scientific_sha256': 'a' * 64})
        with self.assertRaises(RuntimeError):
            cache_write(self.paths, dependencies, {'distance': 43})
        self.paths.cache(dependencies).write_text('{}')  # Corruption fixture only, outside project.
        with self.assertRaises((RuntimeError, KeyError)):
            cache_read(self.paths, dependencies)

    def test_scientific_hash_excludes_reporting_documents_and_other_city(self):
        science = scientific_dependencies('oslo', source_manifests={'fixture': 'hash'})
        hashed = science['code_and_environment']
        self.assertNotIn('src/v4/reporting.py', hashed)
        self.assertNotIn('src/v4/cli.py', hashed)
        self.assertFalse(any(p.startswith('docs/') for p in hashed))
        from src.v4.specification import load_design
        design = load_design()
        design['status'] = 'changed reporting status'
        design['active_documents'] = ['new_document.md']
        design['provenance']['new_commit'] = 'abcdef'
        self.assertEqual(science, scientific_dependencies('oslo', design=design, source_manifests={'fixture': 'hash'}))
        cities = load_cities()
        cities['cities']['stockholm']['currency']['value'] = 'fixture'
        self.assertEqual(science, scientific_dependencies('oslo', cities=cities, source_manifests={'fixture': 'hash'}))
        design['inherited_safeguards']['walking_speed_kmh'] = 6
        self.assertNotEqual(canonical_hash(science), canonical_hash(scientific_dependencies('oslo', design=design, source_manifests={'fixture': 'hash'})))
        self.assertNotEqual(canonical_hash(science), canonical_hash(scientific_dependencies('oslo', source_manifests={'fixture': 'changed'})))

    def test_housing_policy_changes_invalidate_only_the_selected_city(self):
        path = PROJECT_ROOT / 'config/v4/housing_sources.json'
        native = path.read_text()
        load_json = json.loads
        policy = load_json(native)
        original = scientific_dependencies('oslo')
        policy['cities']['stockholm']['blockers'].append('Synthetic other-city change')
        with patch('src.v4.identity.json.loads', side_effect=lambda s: deepcopy(policy) if s == native else load_json(s)):
            self.assertEqual(original, scientific_dependencies('oslo'))
        policy['cities']['oslo']['sources'][0]['sha256'] = '0' * 64
        with patch('src.v4.identity.json.loads', side_effect=lambda s: deepcopy(policy) if s == native else load_json(s)):
            self.assertNotEqual(canonical_hash(original), canonical_hash(scientific_dependencies('oslo')))

    def test_shared_scientific_imports_are_declared(self):
        import ast
        declared = set(scientific_dependencies('oslo')['code_and_environment'])
        for path in (PROJECT_ROOT / 'src/v4').glob('*.py'):
            if path.name in {'reporting.py', 'cli.py'}:
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('src.') and not node.module.startswith('src.v4'):
                    self.assertIn(node.module.replace('.', '/') + '.py', declared)


class CommandTests(unittest.TestCase):
    def test_commands_require_explicit_selection_and_block_without_mutation(self):
        args = ['--version', VERSION, '--city', 'oslo', '--snapshot', '2026-06-30', '--run-id', scope(purpose='research').run_id]
        for command in ('preflight', 'run'):
            out = io.StringIO()
            with redirect_stdout(out), patch('src.v4.runtime.get_engine') as engine:
                self.assertEqual(main([command, *args, '--offline']), 2)
            engine.assert_not_called()
            result = json.loads(out.getvalue())
            self.assertEqual(result['status'], 'BLOCKED')
            self.assertEqual(result['mutations'], 0)
            self.assertFalse(result['research_executed'])
        out = io.StringIO()
        with patch('src.v4.runtime.get_engine', side_effect=RuntimeError('Dedicated V4 settings missing')), redirect_stdout(out):
            self.assertEqual(main(['preflight', *args]), 2)
        self.assertIn('Dedicated V4 settings missing', json.loads(out.getvalue())['blockers'])
        from src.v4.runtime import preflight
        other_snapshot = Scope(VERSION, 'copenhagen_frederiksberg', '2026-06-29', 'research_v4_copenhagen_frederiksberg_20261011T120000Z')
        self.assertTrue(any('Selected snapshot differs' in b for b in preflight(other_snapshot, offline=True)['blockers']))
        for command in ('setup', 'report'):
            with patch('src.v4.cli.get_engine', side_effect=RuntimeError('V4 settings missing')), redirect_stdout(io.StringIO()):
                self.assertEqual(main([command, *args]), 2)
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(['preflight', '--city', 'oslo'])

    def test_setup_dispatch_and_report_dispatch_are_real(self):
        args = ['--version', VERSION, '--city', 'oslo', '--snapshot', '2026-06-30', '--run-id', scope(purpose='research').run_id]
        with patch('src.v4.cli.get_engine') as engine, patch('src.v4.cli.migrate', return_value=['023_v4_multicity_persistence.sql']) as migrate, redirect_stdout(io.StringIO()):
            self.assertEqual(main(['setup', *args]), 0)
            migrate.assert_called_once_with(engine.return_value)
        with patch('src.v4.cli.get_engine'), patch('src.v4.cli.report', return_value={'status': 'AGGREGATE_EXPORT'}) as report, redirect_stdout(io.StringIO()):
            self.assertEqual(main(['report', *args]), 0)
            report.assert_called_once()

    def test_legacy_connection_is_never_inherited(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / '.env.v4'
            config.write_text('DB_NAME=thesis_accessibility\nDB_USER=legacy\nDB_PASSWORD=never_used\n')
            with patch.dict('os.environ', {}, clear=True), self.assertRaises(RuntimeError):
                get_engine(config)
            config.write_text('V4_DB_NAME=thesis_accessibility\nV4_DB_USER=fixture\nV4_DB_PASSWORD=fixture\nV4_DB_HOST=localhost\nV4_DB_PORT=5433\n')
            with patch.dict('os.environ', {}, clear=True), self.assertRaises(RuntimeError):
                get_engine(config)
        conn = MagicMock()
        conn.scalar.return_value = 'thesis_accessibility'
        with self.assertRaises(RuntimeError):
            verify_database(conn)
        self.assertEqual(conn.scalar.call_count, 1)
