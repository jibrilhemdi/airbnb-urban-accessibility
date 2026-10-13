"""One configuration file must preserve separate database destinations."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.db.connection import get_engine as historical_engine
from src.provenance.persistence import get_engine as study_engine
from src.ingestion.common import PROJECT_ROOT


class SharedEnvironmentTests(unittest.TestCase):
    def config(self,directory,study=True):
        path=Path(directory)/'.env'
        content='DB_HOST=127.0.0.1\nDB_PORT=5433\nDB_NAME=thesis_accessibility\nDB_USER=baseline\nDB_PASSWORD=fixture\n'
        if study:
            content+='STUDY_DB_HOST=127.0.0.1\nSTUDY_DB_PORT=5433\nSTUDY_DB_NAME=thesis_accessibility_v4\nSTUDY_DB_USER=analysis\nSTUDY_DB_PASSWORD=fixture\n'
        path.write_text(content)
        return path

    def test_shared_file_keeps_connections_separate(self):
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{},clear=True):
            path=self.config(directory)
            legacy=historical_engine(path);current=study_engine(path)
            try:
                self.assertEqual(legacy.url.database,'thesis_accessibility')
                self.assertEqual(current.url.database,'thesis_accessibility_v4')
                self.assertEqual(legacy.url.username,'baseline')
                self.assertEqual(current.url.username,'analysis')
            finally:legacy.dispose();current.dispose()

    def test_study_settings_never_fall_back_to_historical_settings(self):
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{},clear=True):
            with self.assertRaisesRegex(RuntimeError,'Missing STUDY_DB_'):
                study_engine(self.config(directory,study=False))

    def test_default_file_is_env_and_reading_does_not_mutate_environment(self):
        self.assertEqual(study_engine.__defaults__,(PROJECT_ROOT/'.env',))
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'STUDY_DB_USER':'override'},clear=True):
            before=dict(os.environ);engine=study_engine(self.config(directory))
            try:
                self.assertEqual(engine.url.username,'override')
                self.assertEqual(dict(os.environ),before)
            finally:engine.dispose()
