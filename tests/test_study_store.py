import os
import unittest
import uuid
from sqlalchemy import create_engine,text
from src.study.store import setup,commit_package,read_package
from src.study.sources import get_engine


@unittest.skipUnless(os.environ.get('THESIS_STUDY_DB_TEST')=='1','Owned disposable PostGIS opt-in')
class StoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.name='test_study_'+uuid.uuid4().hex
        base=get_engine();cls.url=base.url
        try:
            with base.connect().execution_options(isolation_level='AUTOCOMMIT') as c:
                c.exec_driver_sql('CREATE DATABASE '+cls.name)
        finally:base.dispose()
        cls.engine=create_engine(cls.url.set(database=cls.name),connect_args={'connect_timeout':5})
        with cls.engine.begin() as c:c.exec_driver_sql('CREATE EXTENSION postgis')
        setup(cls.engine,'synthetic')

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose();base=get_engine()
        try:
            with base.connect().execution_options(isolation_level='AUTOCOMMIT') as c:
                c.exec_driver_sql('DROP DATABASE '+cls.name)
        finally:base.dispose()

    def package(self,city='oslo'):
        name='fixture_'+uuid.uuid4().hex
        with self.engine.begin() as c:
            commit_package(c,city=city,family='geography',summary={'status':'FIXTURE'},
                           records={'assignment':[{'listing_id':'1','city':city}]},
                           deps={'fixture':True},identity=name,purpose='synthetic')
        return name

    def test_idempotent_migration_roundtrip(self):
        self.assertEqual(setup(self.engine,'synthetic'),[])
        name=self.package()
        with self.engine.connect() as c:
            self.assertEqual(read_package(c,name,'oslo','geography')[0],{'status':'FIXTURE'})

    def test_completed_records_cannot_grow_or_change(self):
        name=self.package()
        for sql in ["INSERT INTO study.records VALUES (:run,'oslo','geography','assignment','99','{}')",
                    "UPDATE study.checkpoints SET summary='{}' WHERE run_id=:run",
                    "DELETE FROM study.records WHERE run_id=:run",
                    'TRUNCATE study.checkpoints CASCADE']:
            with self.assertRaises(Exception):
                with self.engine.begin() as c:c.execute(text(sql),{'run':name})

    def test_wrong_city_or_database_refused(self):
        name='fixture_'+uuid.uuid4().hex
        with self.assertRaises(ValueError):
            with self.engine.begin() as c:
                commit_package(c,city='oslo',family='geography',summary={},
                               records={'assignment':[{'city':'stockholm'}]},deps={},identity=name,purpose='synthetic')
        with self.assertRaises(ValueError):
            setup(self.engine,'research')

    def test_historical_labels_forbidden_in_new_identity(self):
        with self.assertRaises(ValueError):
            with self.engine.begin() as c:
                commit_package(c,city='oslo',family='geography',summary={},deps={},identity='research_v4_oslo',purpose='synthetic')
