import json
from pathlib import Path
import tempfile
import unittest
from src.db.sources import prepare_all_sources
from src.study.accessibility import elements
from unittest.mock import patch


class SourceIsolationTests(unittest.TestCase):
    def test_new_scoped_sources_never_enter_historical_registration(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'data/raw/neighbourhoods/copenhagen/response.json'
            source.parent.mkdir(parents=True);source.write_text('{}')
            manifest=root/'manifest.json';manifest.write_text(json.dumps({'files':[]}))
            self.assertEqual(prepare_all_sources(project_root=root,manifest_path=manifest),[])
            rogue=root/'data/raw/unknown_legacy_provider/source.json';rogue.parent.mkdir(parents=True);rogue.write_text('{}')
            with self.assertRaises(ValueError):prepare_all_sources(project_root=root,manifest_path=manifest)

    def test_http_success_with_query_remark_or_empty_data_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'response.json'
            for value in [{'remark':'Query timed out','elements':[{'type':'node','id':1}]},{'elements':[]}]:
                path.write_text(json.dumps(value))
                with patch('src.study.accessibility.verify_source',return_value=path):
                    with self.assertRaises(ValueError):elements([{'snapshot':'2026-06-30T23:59:59Z'}])
