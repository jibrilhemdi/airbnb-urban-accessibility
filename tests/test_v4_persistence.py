"""Opt-in PostGIS tests create/drop only their owned test_v4_<UUID> database."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
import uuid

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, DBAPIError

from src.db.connection import get_engine as legacy_engine
from src.pipeline.protocol import canonical_hash
from src.v4.identity import Paths, scientific_dependencies, freeze_sources
from src.v4.persistence import (MIGRATIONS, begin_run, complete_run, migrate, observations,
                                persist_artifact, register_manifest, verify_database, SCOPE_SQL)
from src.v4.reporting import report
from src.v4.specification import model_definition
from test_v4_architecture import scope, source_fixture


@unittest.skipUnless(os.environ.get('THESIS_V4_DB_TEST') == '1', 'Opt-in disposable V4 database tests')
class V4PersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.name = 'test_v4_' + uuid.uuid4().hex
        if not re.fullmatch(r'test_v4_[0-9a-f]{32}', cls.name):
            raise RuntimeError('Unsafe test database name')
        original = legacy_engine()
        try:
            with original.connect() as conn:
                if conn.scalar(text('SELECT current_database()')) != 'thesis_accessibility':
                    raise RuntimeError('Unexpected audited server identity')
            url = original.url
        finally:
            original.dispose()
        cls.admin = create_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT')
        cls.engine = None
        cls.created = False
        try:
            with cls.admin.connect() as conn:
                conn.exec_driver_sql('CREATE DATABASE "' + cls.name + '"')
            cls.created = True
            cls.engine = create_engine(url.set(database=cls.name))
            cls.first_migration = migrate(cls.engine, synthetic=True)
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        if cls.engine is not None:
            cls.engine.dispose()
        if cls.created:
            with cls.admin.connect() as conn:
                conn.exec_driver_sql('DROP DATABASE "' + cls.name + '"')
            cls.created = False
        cls.admin.dispose()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paths = Paths(scope(), Path(self.temp.name))
        _, self.manifest = freeze_sources(self.paths, source_fixture(self.paths))
        self.digest = canonical_hash(self.manifest)
        self.science = scientific_dependencies('oslo', source_manifests={self.digest: self.manifest})
        self.conn = self.engine.connect()
        self.addCleanup(self.conn.close)
        tx = self.conn.begin()
        self.addCleanup(tx.rollback)
        begin_run(self.conn, self.paths.scope, self.science)
        register_manifest(self.conn, self.paths.scope, self.manifest)

    def test_migration_idempotence_and_applied_hash(self):
        self.assertEqual(self.first_migration, ['023_v4_multicity_persistence.sql', '024_v4_listing_boundary_audit.sql',
                                                '025_v4_housing_source_audit.sql', '026_v4_accessibility_only_definition.sql',
                                                '027_v4_geography_qualification.sql'])
        self.assertEqual(migrate(self.engine, synthetic=True), [])
        with tempfile.TemporaryDirectory() as directory:
            for original in MIGRATIONS.glob('*.sql'):
                (Path(directory) / original.name).write_bytes(original.read_bytes())
            migration = Path(directory) / '023_v4_multicity_persistence.sql'
            migration.write_text((MIGRATIONS / migration.name).read_text() + '\n-- changed fixture\n')
            with self.assertRaisesRegex(RuntimeError, 'changed'):
                migrate(self.engine, synthetic=True, directory=Path(directory))
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_analysis.schema_migrations')), 5)
        self.assertEqual(self.conn.scalar(text("SELECT count(*) FROM information_schema.schemata WHERE schema_name LIKE 'v3_%'")), 0)

    def test_housing_sources_persist_native_values_nulls_and_blocked_status(self):
        from src.v4.housing import persist_housing, evidence, standalone_gates, DEFINITION
        record = dict(source_id='fixture', source_area_id='native_0180R001', geography_level='synthetic_native_area',
                      period='2025', price_m2_native=None, sale_count=None, currency='SEK', unit='SEK/m2', annual=True)
        gates = standalone_gates([record], legal_reuse_verified=True, annual_measure_verified=True,
                                 geography_definitions_verified=True, boundary_provisional=False)
        summary = dict(definition_version=DEFINITION, parsed_rows=1, status='BLOCKED', **gates)
        persist_housing(self.conn,self.paths.scope,self.manifest,[record],summary)
        stored = self.conn.scalar(text('SELECT record FROM v4_raw.housing_area_period_audit WHERE '+SCOPE_SQL),self.paths.scope.params())
        self.assertIsNone(stored['price_m2_native']);self.assertIsNone(stored['sale_count'])
        result=evidence(self.conn,self.paths);self.assertEqual(result['parsed_rows'],1);self.assertFalse(result['listing_H_assigned'])
        self.assertNotIn('price_m2_native',result)
        self.assertEqual(result['per_level']['synthetic_native_area']['unknown_sale_counts'],1)
        self.assertEqual(result['per_level']['synthetic_native_area']['preferred_annual_support_areas'],0)
        with self.assertRaises(IntegrityError),self.conn.begin_nested():
            persist_housing(self.conn,self.paths.scope,self.manifest,[],dict(parsed_rows=0))
        for query in ('UPDATE v4_raw.housing_ingestions SET summary=summary',
                      'DELETE FROM v4_raw.housing_area_period_audit','TRUNCATE v4_raw.housing_ingestions'):
            with self.assertRaises(DBAPIError),self.conn.begin_nested():self.conn.execute(text(query))

    def test_housing_duplicate_key_unregistered_sources_and_city_isolation(self):
        from src.v4.housing import persist_housing
        record=dict(source_id='fixture',source_area_id='same',geography_level='native',period='2025',price_m2_native=10000)
        with self.assertRaises(ValueError),self.conn.begin_nested():
            persist_housing(self.conn,self.paths.scope,self.manifest,[record,record],dict(parsed_rows=2))
        with self.assertRaises(ValueError),self.conn.begin_nested():
            persist_housing(self.conn,self.paths.scope,self.manifest,[{**record,'source_id':'unregistered'}],dict(parsed_rows=1))
        persist_housing(self.conn,self.paths.scope,self.manifest,[record],dict(parsed_rows=1))
        other=Paths(scope('stockholm'),self.paths.root)
        _,manifest=freeze_sources(other,source_fixture(other))
        persist_housing(self.conn,other.scope,manifest,[record],dict(parsed_rows=1))
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_raw.housing_area_period_audit WHERE '+SCOPE_SQL),other.scope.params()),1)
        with self.assertRaises(ValueError):persist_housing(self.conn,other.scope,self.manifest,[],dict(parsed_rows=0))

    def test_committed_housing_parent_cannot_accept_late_rows(self):
        from src.v4.housing import persist_housing
        from src.v4.identity import Scope
        s=Scope('research_design_v4','stockholm','2026-06-30','synthetic_v4_stockholm_20261011T010005Z','synthetic')
        p=Paths(s,self.paths.root);_,m=freeze_sources(p,source_fixture(p))
        with self.engine.begin() as conn:persist_housing(conn,s,m,[],dict(parsed_rows=0,status='BLOCKED'))
        with self.assertRaises(DBAPIError),self.conn.begin_nested():
            self.conn.execute(text("INSERT INTO v4_raw.housing_area_period_audit VALUES (:version,:run_id,:city,:snapshot,'fixture','late','native','2025','{}'::jsonb)"),s.params())

    def test_city_isolation_and_duplicate_listing_ids(self):
        frame = pd.DataFrame([{'listing_id': 'same_id', 'source_area_id': 'native_area', 'price_nightly': None}])
        observations(self.conn, self.paths.scope, self.digest, 'fixture', frame)
        other = Paths(scope('stockholm'), self.paths.root)
        _, manifest = freeze_sources(other, source_fixture(other))
        begin_run(self.conn, other.scope, {'synthetic': True, 'design': {'design_id': other.scope.design_id}})
        digest = register_manifest(self.conn, other.scope, manifest)
        observations(self.conn, other.scope, digest, 'fixture', frame)
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_raw.observations')), 2)
        row = self.conn.scalar(text('SELECT record FROM v4_raw.observations WHERE ' + SCOPE_SQL), self.paths.scope.params())
        self.assertIsNone(row['price_nightly'])
        with self.assertRaises(IntegrityError), self.conn.begin_nested():
            observations(self.conn, self.paths.scope, self.digest, 'fixture', frame)
        with self.assertRaises(ValueError):
            observations(self.conn, self.paths.scope, self.digest, 'fixture', pd.concat([frame, frame]))
        with self.assertRaisesRegex(ValueError, 'identity conflicts'):
            observations(self.conn, self.paths.scope, self.digest, 'fixture', pd.DataFrame([{'listing_id': 'wrong_city', 'city': 'stockholm'}]))

    def test_snapshot_and_run_isolation(self):
        from src.v4.identity import Scope
        s = self.paths.scope
        other = Scope(s.version, s.city, '2026-06-29', s.run_id, s.purpose)
        begin_run(self.conn, other, {'synthetic': True, 'design': {'design_id': other.design_id}})
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_analysis.runs')), 2)

    def test_source_area_id_namespaces_and_recorded_crs(self):
        s = self.paths.scope
        query = text('INSERT INTO v4_spatial.source_areas VALUES '
                     '(:version,:run_id,:city,:snapshot,\'fixture\',\'same_native_area\',:digest,26910,'
                     "ST_GeomFromText('MULTIPOLYGON(((0 0,1 0,1 1,0 0)))',26910))")
        self.conn.execute(query, {**s.params(), 'digest': self.digest})
        with self.assertRaises(IntegrityError), self.conn.begin_nested():
            self.conn.execute(query, {**s.params(), 'digest': self.digest})
        other = Paths(scope('stockholm'), self.paths.root)
        _, manifest = freeze_sources(other, source_fixture(other))
        begin_run(self.conn, other.scope, {'synthetic': True, 'design': {'design_id': other.scope.design_id}})
        digest = register_manifest(self.conn, other.scope, manifest)
        self.conn.execute(query, {**other.scope.params(), 'digest': digest})
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_spatial.source_areas')), 2)
        with self.assertRaises(IntegrityError), self.conn.begin_nested():
            self.conn.execute(text('INSERT INTO v4_spatial.source_areas VALUES '
                                   '(:version,:run_id,:city,:snapshot,\'fixture\',\'wrong_crs_area\',:digest,26910,'
                                   "ST_GeomFromText('MULTIPOLYGON(((0 0,1 0,1 1,0 0)))',4326))"),
                              {**s.params(), 'digest': self.digest})

    def test_manifest_cross_city_and_source_ids_rejected(self):
        with self.assertRaises(ValueError):
            register_manifest(self.conn, scope('stockholm'), self.manifest)
        self.assertEqual(register_manifest(self.conn, self.paths.scope, self.manifest), self.digest)
        frame = pd.DataFrame([{'listing_id': 'fixture'}])
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            observations(self.conn, self.paths.scope, self.digest, 'unknown_source', frame)
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            self.conn.execute(text('UPDATE v4_raw.source_manifests SET manifest=manifest'))

    def test_completed_runs_and_records_cannot_be_overwritten(self):
        persist_artifact(self.conn, self.paths.scope, 'M0', 'primary_models', 'fixture', pd.DataFrame([{'listing_id': 'private_fixture'}]), engine='OLS', validation='random')
        complete_run(self.conn, self.paths.scope)
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            persist_artifact(self.conn, self.paths.scope, 'ME', 'primary_models', 'fixture', pd.DataFrame([{'x': 1}]), engine='OLS', validation='random')
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            self.conn.execute(text("UPDATE v4_analysis.runs SET status='running'"))
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            self.conn.execute(text('DELETE FROM v4_analysis.artifacts'))
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            self.conn.execute(text('TRUNCATE v4_analysis.artifacts'))
        with self.assertRaises(IntegrityError), self.conn.begin_nested():
            begin_run(self.conn, self.paths.scope, self.science)
        with self.assertRaises(RuntimeError):
            complete_run(self.conn, self.paths.scope)

    def test_legacy_model_labels_and_production_purpose_rejected(self):
        with self.assertRaises(RuntimeError):
            verify_database(self.conn)
        with self.assertRaises(RuntimeError):
            begin_run(self.conn, scope(purpose='research'), {'fixture': True})
        with self.assertRaisesRegex(DBAPIError, 'design mismatch|definition_id_check'), self.conn.begin_nested():
            self.conn.execute(text('INSERT INTO v4_analysis.artifacts VALUES (:version,:run_id,:city,:snapshot,\'M0\',\'primary_models\',\'fixture\',\'0\',\'{}\')'), self.paths.scope.params())

    def test_aggregate_report_output_separation_no_private_rows_and_immutability(self):
        s = self.paths.scope
        persist_artifact(self.conn, s, 'M0', 'primary_models', 'private_predictions', pd.DataFrame([{'listing_id': 'PRIVATE_SENTINEL'}]), engine='OLS', validation='random')
        self.conn.execute(text('INSERT INTO v4_analysis.aggregate_metrics VALUES '
                               '(:version,:run_id,:city,:snapshot,:definition,\'OLS\',\'random\',100,0.5,0.4)'),
                          {**s.params(), 'definition': model_definition('M0')['definition_id']})
        complete_run(self.conn, s)
        result = report(self.conn, self.paths)
        self.assertEqual(result['row_count'], 1)
        export = self.paths.output('tables', 'reporting', 'aggregate_metrics.csv')
        self.assertIn(model_definition('M0')['definition_id'], export.read_text())
        self.assertNotIn('PRIVATE_SENTINEL', export.read_text())
        self.assertFalse(Paths(scope('stockholm'), self.paths.root).output('tables', 'reporting', 'aggregate_metrics.csv').exists())
        with self.assertRaisesRegex(RuntimeError, 'overwrite'):
            report(self.conn, self.paths)

    def test_report_refuses_missing_incomplete_or_changed_science(self):
        with self.assertRaisesRegex(RuntimeError, 'completed'):
            report(self.conn, self.paths)
        complete_run(self.conn, self.paths.scope)
        source = self.paths.source('fixture', 'source.txt')
        source.write_text('changed synthetic fixture')
        with self.assertRaisesRegex(RuntimeError, 'bytes changed'):
            report(self.conn, self.paths)

    def test_listing_audit_preserves_duplicates_nulls_and_city_isolation(self):
        from src.v4.listings import persist_ingestion, DEFINITION
        rows = [{'row_number': 1, 'listing_id': 'duplicate', 'price_nightly': None},
                {'row_number': 2, 'listing_id': 'duplicate', 'price_nightly': 100}]
        summary = {'definition_version': DEFINITION, 'status': 'BLOCKED', 'counts': {'raw': 2}}
        persist_ingestion(self.conn, self.paths.scope, self.manifest, rows, summary, [])
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_raw.listing_audit WHERE ' + SCOPE_SQL), self.paths.scope.params()), 2)
        self.assertIsNone(self.conn.scalar(text("SELECT record->'price_nightly' FROM v4_raw.listing_audit WHERE row_number=1 AND " + SCOPE_SQL), self.paths.scope.params()))
        with self.assertRaises(IntegrityError), self.conn.begin_nested():
            persist_ingestion(self.conn, self.paths.scope, self.manifest, rows, summary, [])
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            self.conn.execute(text('UPDATE v4_raw.listing_audit SET record=record'))
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            self.conn.execute(text('TRUNCATE v4_raw.listing_audit'))
        other = Paths(scope('stockholm'), self.paths.root)
        _, manifest = freeze_sources(other, source_fixture(other))
        persist_ingestion(self.conn, other.scope, manifest, rows, summary, [])
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_raw.listing_audit WHERE ' + SCOPE_SQL), other.scope.params()), 2)

    def test_committed_ingestion_cannot_accept_late_rows(self):
        from src.v4.listings import persist_ingestion, DEFINITION
        from test_v4_architecture import scope as fixture_scope
        other = Paths(fixture_scope(stamp='20261011T140000Z'), self.paths.root)
        manifest = {**self.manifest, 'synthetic_fixture': 'committed_ingestion'}
        with self.engine.begin() as conn:
            persist_ingestion(conn, other.scope, manifest, [{'row_number':1,'listing_id':'synthetic'}],
                              {'definition_version':DEFINITION,'counts':{'raw':1}}, [])
        with self.assertRaises(DBAPIError), self.conn.begin_nested():
            self.conn.execute(text('INSERT INTO v4_raw.listing_audit VALUES '
                                   "(:version,:run_id,:city,:snapshot,2,'late','{}')"), other.scope.params())

    def test_listing_public_export_omits_private_rows_and_unknown_fields(self):
        from src.v4.listings import persist_ingestion, DEFINITION
        from src.v4.reporting import listing_evidence
        summary={'definition_version':DEFINITION,'status':'BLOCKED','counts':{'raw':1,'private_prediction':'PRIVATE_SENTINEL'},
                 'listing_id':'PRIVATE_SENTINEL','blockers':['Synthetic fixture only']}
        persist_ingestion(self.conn,self.paths.scope,self.manifest,[{'row_number':1,'listing_id':'PRIVATE_SENTINEL'}],summary,[])
        result=listing_evidence(self.conn,self.paths)
        self.assertNotIn('PRIVATE_SENTINEL',json.dumps(result))
        self.assertEqual(result['counts'],{'raw':1})
        with self.assertRaises(FileExistsError): listing_evidence(self.conn,self.paths)

    def test_stockholm_amendment_append_only_parent_failure_and_spatial_export(self):
        import csv
        import gzip
        from unittest.mock import patch
        from pyproj import Transformer
        from src.ingestion.common import sha256_file
        from src.v4.listings import REQUIRED, audit_listings, persist_ingestion, encoded_json
        from src.v4.reporting import listing_evidence
        from src.v4.stockholm_boundary import recover, qualify_regso, RESOLVED
        from test_v4_stockholm_boundary import fixture
        from test_v4_listings import ListingAuditTests
        parent_scope=scope('stockholm',stamp='20261011T121000Z')
        paths=Paths(scope('stockholm',stamp='20261011T122000Z'),self.paths.root)
        frame, areas, policy=fixture(); native,geographic,qa=qualify_regso(frame,areas,policy)
        project=Transformer.from_crs(3006,4326,always_xy=True)
        csv_rows=[]
        for number,x,price in [(1,670100,'$1,234.50'),(2,670500,'')]:
            lon,lat=project.transform(x,6580100)
            csv_rows.append(ListingAuditTests().row(id=str(number),longitude=str(lon),latitude=str(lat),price=price,
                price_quote_price_per_night='' if not price else '1234.50',
                price_quote_raw=json.dumps({'quote':{'currency':'SEK','date_match':True}})))
        listing=paths.source('inside_airbnb','listings.csv.gz'); listing.parent.mkdir(parents=True)
        with gzip.open(listing,'wt',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=sorted(REQUIRED));writer.writeheader();writer.writerows(csv_rows)
        codes=paths.source('official_scope_codes','municipal_codes.html');codes.parent.mkdir(parents=True)
        codes.write_text('<p>0180 Stockholm</p>')
        failure_path=paths.source('official_boundary','boundary.json.receipt.json');failure_path.parent.mkdir(parents=True)
        failure_path.write_bytes(encoded_json({'status':'BLOCKED','http_status':401,'local_location':None,
            'source_url':'https://api.lantmateriet.se/ogc-features/v1/administrativ-indelning/collections/kommuner/items?f=json&limit=1'}))
        def record(source,name,crs='not_spatial'):
            return {'source_id':source,'filename':name,'source_url':'synthetic://fixture',
                'acquired_at_utc':'2026-10-11T12:00:00Z','geographic_extent':'synthetic',
                'source_crs':crs,'sha256':sha256_file(paths.source(source,name)),'reference_period':'2025-01-01'}
        _,parent_manifest=freeze_sources(paths,[record('inside_airbnb','listings.csv.gz'),record('official_scope_codes','municipal_codes.html')])
        old_rows,old_summary=audit_listings(listing,scrape_id='20260630053456',currency='SEK')
        with self.engine.begin() as conn:
            persist_ingestion(conn,parent_scope,parent_manifest,old_rows,old_summary,[])
        policy.update(parent_run_id=parent_scope.run_id,parent_manifest_sha256=canonical_hash(parent_manifest),
            parent_summary_sha256=canonical_hash(old_summary),failed_receipt_sha256=sha256_file(failure_path),listing_sha256=sha256_file(listing))
        source=paths.source('scb_fixture','source.txt');source.parent.mkdir(parents=True);source.write_text('synthetic RegSO fixture')
        boundary_record={**record('scb_fixture','source.txt','EPSG:3006'),'selection':{'municipality':'0180'}}
        with self.engine.connect() as conn, conn.begin(), patch('src.v4.stockholm_boundary.scb_sources',
                return_value=([boundary_record],boundary_record,native,geographic,qa)), patch('src.v4.listings.urlopen') as download:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            manifest,rows,summary,boundaries=recover(conn,paths,parent_scope.run_id,policy)
            download.assert_not_called()
        summary['boundary_qa']['private_prediction']='PRIVATE_SENTINEL'
        summary['boundary_amendment']['private_coordinates']='PRIVATE_SENTINEL'
        with self.engine.begin() as conn:
            persist_ingestion(conn,paths.scope,manifest,rows,summary,boundaries)
        with self.engine.connect() as conn, conn.begin():
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            evidence=listing_evidence(conn,paths)
            self.assertEqual(evidence['status'],RESOLVED)
            self.assertEqual(evidence['counts']['inside_boundary_positive_price'],1)
            self.assertEqual(evidence['counts']['outside_boundary_dwelling'],1)
            self.assertEqual(evidence['counts']['boundary_150m_raw'],2)
            self.assertNotIn('PRIVATE_SENTINEL',json.dumps(evidence))
            stored_parent=conn.scalar(text('SELECT summary FROM v4_raw.listing_ingestions WHERE '+SCOPE_SQL),parent_scope.params())
            self.assertEqual(canonical_hash(stored_parent),canonical_hash(old_summary))
            self.assertIsNone(stored_parent['counts']['inside_boundary_raw'])
            with self.assertRaisesRegex(RuntimeError,'immutable ingestion'):
                recover(conn,paths,parent_scope.run_id,policy)
        self.assertEqual(sha256_file(failure_path),policy['failed_receipt_sha256'])
        self.assertEqual(sha256_file(listing),policy['listing_sha256'])

    def test_read_only_manifest_reuse_preserves_null_housing_and_all_audit_rows(self):
        from src.v4.listings import persist_ingestion, DEFINITION
        from src.v4.source_reuse import reuse_listing_source, read_listing_audit
        rows=[{'row_number':1,'listing_id':'synthetic_positive','dwelling_eligible':True,
               'price_nightly':100,'log_price':4.605170185988092,'positive_price':True,'inside_boundary':True,
               'native_housing_area_id':None,'official_analysis_area_id':None,'housing_context_midrank':None},
              {'row_number':2,'listing_id':'synthetic_missing','dwelling_eligible':True,'price_nightly':None,
               'native_housing_area_id':None}]
        persist_ingestion(self.conn,self.paths.scope,self.manifest,rows,
                          {'definition_version':DEFINITION,'counts':{'raw':2}},[])
        new_scope=scope(stamp='20261011T150000Z')
        policy={'design_id':new_scope.design_id,'source_version':new_scope.version,
                'cities':{'oslo':{'run_id':self.paths.scope.run_id,'manifest_sha256':self.digest,'snapshot':new_scope.snapshot}}}
        before=dict(self.conn.execute(text('SELECT count(*) AS n FROM v4_raw.listing_ingestions')).mappings().one())
        with self.conn.begin_nested():
            result=reuse_listing_source(self.conn,new_scope,self.digest,root=self.paths.root,policy=policy)
            selected=read_listing_audit(self.conn,new_scope,self.digest,root=self.paths.root,policy=policy)
        self.assertEqual(result['source_scope']['run_id'],self.paths.scope.run_id)
        self.assertEqual(result['mutations'],0);self.assertFalse(result['source_reingested'])
        self.assertEqual(len(selected),2)
        self.assertIsNone(selected[1]['price_nightly'])
        self.assertIsNone(selected[0]['official_analysis_area_id'])
        self.assertNotIn('native_housing_area_id',selected[0]);self.assertNotIn('housing_context_midrank',selected[0])
        after=dict(self.conn.execute(text('SELECT count(*) AS n FROM v4_raw.listing_ingestions')).mappings().one())
        self.assertEqual(before,after)
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_raw.listing_audit WHERE '+SCOPE_SQL),self.paths.scope.params()),2)
        with self.assertRaises(ValueError):reuse_listing_source(self.conn,new_scope,'0'*64,root=self.paths.root,policy=policy)
        with self.assertRaises(KeyError):reuse_listing_source(self.conn,scope('stockholm'),self.digest,root=self.paths.root,policy=policy)
        self.paths.source('fixture','source.txt').write_text('changed synthetic fixture')
        with self.assertRaisesRegex(RuntimeError,'bytes changed'):
            reuse_listing_source(self.conn,new_scope,self.digest,root=self.paths.root,policy=policy)

    def test_revised_model_version_engine_validation_and_sensitivity_isolation(self):
        from src.v4.specification import HISTORICAL_VERSION
        frame=pd.DataFrame([{'synthetic_statistic':1.}])
        for engine in ['OLS','XGBoost']:
            for validation in ['random','geographic']:
                for sensitivity in ['primary','no_income']:
                    persist_artifact(self.conn,self.paths.scope,'M0','primary_models','synthetic_fixture',frame,
                                     engine=engine,validation=validation,scenario=sensitivity)
        self.assertEqual(self.conn.scalar(text('SELECT count(*) FROM v4_analysis.artifacts')),8)
        dimensions=self.conn.execute(text('SELECT DISTINCT design_id,model,sensitivity,engine,validation FROM v4_analysis.artifact_dimensions')).all()
        self.assertEqual(len(dimensions),8)
        self.assertTrue(all(r.design_id==self.paths.scope.design_id and r.model=='M0' for r in dimensions))
        with self.assertRaises(ValueError):persist_artifact(self.conn,self.paths.scope,'M0','primary_models','fixture',frame)
        with self.assertRaisesRegex(ValueError,'metadata conflicts'):
            persist_artifact(self.conn,self.paths.scope,'M0','primary_models','fixture',pd.DataFrame([{'engine':'XGBoost'}]),
                             engine='OLS',validation='random')
        with self.assertRaisesRegex(ValueError,'identity conflicts'):
            persist_artifact(self.conn,self.paths.scope,'M0','primary_models','fixture',pd.DataFrame([{'design_id':HISTORICAL_VERSION}]),
                             engine='OLS',validation='random')
        with self.assertRaises(ValueError):persist_artifact(self.conn,self.paths.scope,'M0','primary_models','fixture',frame,
            engine='OLS',validation='random',scenario='no_housing')
        with self.assertRaises(IntegrityError),self.conn.begin_nested():
            persist_artifact(self.conn,self.paths.scope,'M0','primary_models','synthetic_fixture',frame,engine='OLS',validation='random')
        params={**self.paths.scope.params(),'definition':HISTORICAL_VERSION+':M0'}
        with self.assertRaisesRegex(DBAPIError,'design mismatch'),self.conn.begin_nested():
            self.conn.execute(text('INSERT INTO v4_analysis.aggregate_metrics '
                '(version,run_id,city,snapshot,definition_id,engine,validation,n,rmse,mae) '
                "VALUES (:version,:run_id,:city,:snapshot,:definition,'OLS','random',2,1,1)"),params)
        old=scope(stamp='20261011T160000Z',design_id=HISTORICAL_VERSION)
        begin_run(self.conn,old,{'synthetic':True})
        persist_artifact(self.conn,old,'M0','primary_models','historical_fixture',frame)
        with self.assertRaises(RuntimeError):complete_run(self.conn,scope(stamp='20261011T160000Z'))
        complete_run(self.conn,old)
        with self.assertRaisesRegex(RuntimeError,'design does not match'):
            report(self.conn,Paths(scope(stamp='20261011T160000Z'),self.paths.root))
        with self.assertRaises(DBAPIError),self.conn.begin_nested():
            self.conn.execute(text("INSERT INTO v4_analysis.artifacts (version,run_id,city,snapshot,definition_id,family,artifact,record_key,record,engine,validation) VALUES (:version,:run_id,:city,:snapshot,:definition,'primary_models','fixture','0','{}','OLS','random')"),
                              {**self.paths.scope.params(),'definition':self.paths.scope.design_id+':no_housing:M0'})

    def test_append_only_upgrade_preserves_completed_historical_run_and_guards(self):
        from src.v4.specification import HISTORICAL_VERSION
        name='test_v4_'+uuid.uuid4().hex
        with self.admin.connect() as admin:admin.exec_driver_sql('CREATE DATABASE "'+name+'"')
        upgrade=create_engine(self.engine.url.set(database=name))
        try:
            with tempfile.TemporaryDirectory() as directory:
                for p in MIGRATIONS.glob('*.sql'):
                    if p.name[:3]<'026':(Path(directory)/p.name).write_bytes(p.read_bytes())
                migrate(upgrade,synthetic=True,directory=Path(directory))
            old=scope(design_id=HISTORICAL_VERSION)
            with upgrade.begin() as conn:
                begin_run(conn,old,{'synthetic':True})
                conn.execute(text("INSERT INTO v4_analysis.artifacts VALUES (:version,:run_id,:city,:snapshot,:definition,'primary_models','historical','0',CAST(:record AS jsonb))"),
                             {**old.params(),'definition':HISTORICAL_VERSION+':M0','record':json.dumps({'native_housing_area_id':None})})
                complete_run(conn,old)
                before=conn.scalar(text('SELECT row_to_json(r)::text FROM v4_analysis.runs r'))
                old_record=conn.scalar(text('SELECT record FROM v4_analysis.artifacts'))
            self.assertEqual(migrate(upgrade,synthetic=True),['026_v4_accessibility_only_definition.sql', '027_v4_geography_qualification.sql'])
            self.assertEqual(migrate(upgrade,synthetic=True),[])
            with upgrade.begin() as conn:
                self.assertEqual(before,conn.scalar(text('SELECT row_to_json(r)::text FROM v4_analysis.runs r')))
                self.assertEqual(old_record,conn.scalar(text('SELECT record FROM v4_analysis.artifacts')))
                self.assertIsNone(conn.scalar(text('SELECT engine FROM v4_analysis.artifacts')))
                for query in ["UPDATE v4_analysis.runs SET status='running'","DELETE FROM v4_analysis.artifacts","TRUNCATE v4_analysis.artifacts"]:
                    with self.assertRaises(DBAPIError),conn.begin_nested():conn.execute(text(query))
        finally:
            upgrade.dispose()
            with self.admin.connect() as admin:admin.exec_driver_sql('DROP DATABASE "'+name+'"')


    def test_geography_append_only_isolation_and_committed_children(self):
        from shapely.geometry import Polygon
        from src.v4.geography import spatial_audit, persist, evidence, DEFINITION as GEO
        from src.v4.listings import persist_ingestion, DEFINITION as LISTINGS
        g=Polygon([(10,59),(10.01,59),(10.01,59.01),(10,59.01)])
        rows=[{'listing_id':'fixture_private','dwelling_eligible':True,'positive_price':False,'longitude':10.005,'latitude':59.005}]
        area={'area_id':'fixture_area','native_id':'fixture_area','name':'Fixture','source_crs':'EPSG:4326','geom':g}
        summary,assignments=spatial_audit(rows,g,[area],'EPSG:25833')
        parent=scope(stamp='20261011T220000Z');geo=scope(stamp='20261011T220001Z')
        manifest={**self.manifest,'synthetic_fixture':'A03_committed_geography'}
        digest=canonical_hash(manifest)
        summary.update(design_id=geo.design_id,city=geo.city,status='BLOCKED',definition_version=GEO,
                       source_listing_run_id=parent.run_id,listing_manifest_sha256=digest,geography_manifest_sha256=digest)
        with self.engine.begin() as conn:
            persist_ingestion(conn,parent,manifest,[{'row_number':1,'listing_id':'fixture_private'}],
                              {'definition_version':LISTINGS,'status':'BLOCKED','counts':{'raw':1}},[])
            persist(conn,geo,summary,assignments,[area],g,manifest)
        self.assertEqual(evidence(self.conn,geo),summary)
        stored=self.conn.scalar(text('SELECT record FROM v4_spatial.geography_listing_audit WHERE '+SCOPE_SQL),geo.params())
        self.assertNotIn('longitude',stored);self.assertFalse(stored['near_outer_150m'])
        for query in ['UPDATE v4_spatial.geography_qualifications SET summary=summary',
                      'DELETE FROM v4_spatial.analysis_geography','TRUNCATE v4_spatial.geography_listing_audit']:
            with self.assertRaises(DBAPIError),self.conn.begin_nested():self.conn.execute(text(query))
        with self.assertRaises(DBAPIError),self.conn.begin_nested():
            self.conn.execute(text("INSERT INTO v4_spatial.geography_listing_audit VALUES (:version,:run_id,:city,:snapshot,:design_id,'late',NULL,'{}')"),geo.params())
        with self.assertRaises(IntegrityError),self.conn.begin_nested():persist(self.conn,geo,summary,assignments,[area],g,manifest)
        from dataclasses import replace
        with self.assertRaisesRegex(ValueError,'identity mismatch'):
            persist(self.conn,replace(geo,city='stockholm',run_id='synthetic_v4_stockholm_20261011T220001Z'),summary,[],[],g,manifest)
        with self.assertRaises(ValueError):evidence(self.conn,replace(geo,run_id='synthetic_v4_oslo_20261011T220002Z'))
