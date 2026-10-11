"""Synthetic listing/geometry fixtures stay in temporary roots, never production."""
from copy import deepcopy
import csv
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from shapely.geometry import Polygon, mapping

from src.ingestion.common import PROJECT_ROOT
from src.v4.identity import Paths
from src.v4.listings import (REQUIRED, acquire, audit_listings, boundary_geometry,
                             catalogue_selection, parse_price, CONVENTIONAL_PROPERTY_TYPES)
from test_v4_architecture import scope


class ListingAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'listings.csv.gz'
        self.boundary = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])

    def row(self, **overrides):
        row = {k: '' for k in REQUIRED}
        row.update(id='1', scrape_id='20260630053456', last_scraped='2026-07-02', source='city scrape',
                   room_type='Entire home/apt', property_type='Entire rental unit', price='$1,234.50',
                   latitude='1', longitude='1', neighbourhood_cleansed='PROVIDER_LABEL',
                   price_quote_checkin_date='2026-07-05', price_quote_checkout_date='2026-07-07',
                   price_quote_price_per_night='1234.50', price_quote_total_price='3000',
                   price_quote_raw=json.dumps({'quote': {'currency': 'NOK', 'date_match': True}}))
        row.update(overrides)
        return row

    def audit(self, rows, **kw):
        with gzip.open(self.path, 'wt', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
        return audit_listings(self.path, scrape_id='20260630053456', currency='NOK', boundary=self.boundary, **kw)

    def test_inherited_dwelling_filters_and_sql_match(self):
        expected = {'Entire rental unit', 'Entire condo', 'Entire home', 'Entire loft', 'Entire townhouse', 'Entire villa'}
        self.assertEqual(CONVENTIONAL_PROPERTY_TYPES, expected)
        sql = (PROJECT_ROOT / 'sql/queries/build_clean_airbnb_listings.sql').read_text()
        for value in expected: self.assertIn("'" + value + "'", sql)
        rows = [self.row(id=str(i+1), property_type=p) for i,p in enumerate(sorted(expected))]
        rows += [self.row(id='100', property_type='Entire serviced apartment'), self.row(id='101', room_type='Private room')]
        _, result = self.audit(rows)
        self.assertEqual(result['counts']['dwelling_filtered'], 6)
        self.assertEqual(result['counts']['positive_price'], 6)

    def test_missing_nonpositive_invalid_outcomes_and_duplicate_keys_preserved(self):
        rows = [self.row(price=''), self.row(id='2', price='$0.00'), self.row(id='3', price='1.234,50'),
                self.row(id='4'), self.row(id='4'), self.row(id='')]
        audit, result = self.audit(rows)
        self.assertEqual(len(audit), 6)
        self.assertIsNone(audit[0]['price_nightly']); self.assertIsNone(audit[0]['log_price'])
        self.assertIsNone(audit[1]['log_price']); self.assertIsNone(audit[2]['price_nightly'])
        self.assertEqual(result['counts']['eligible_missing_price'], 1)
        self.assertEqual(result['counts']['duplicate_records'], 2)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertIsNone(audit[0]['official_analysis_area_id']); self.assertIsNone(audit[0]['native_housing_area_id'])

    def test_boundary_covers_edge_excludes_outside_and_does_not_use_provider_label(self):
        audit, result = self.audit([self.row(), self.row(id='2', latitude='0'), self.row(id='3', longitude='3'), self.row(id='4', longitude='bad')])
        self.assertEqual([a['inside_boundary'] for a in audit], [True, True, False, None])
        self.assertEqual(result['counts']['inside_boundary_positive_price'], 2)
        self.assertEqual(result['spatial_crs'], 'EPSG:4326')
        _, missing = audit_listings(self.path, scrape_id='20260630053456', currency='NOK')
        self.assertIsNone(missing['counts']['inside_boundary_positive_price'])
        self.assertEqual(missing['counts']['boundary_unclassified'], 4)

    def test_locale_parser_is_explicit_and_never_guesses_currency(self):
        self.assertEqual(parse_price('$1,234.50')[0], 1234.5)
        self.assertEqual(parse_price(''), (None, None))
        for value in ('1.234,50', '$1,23', '1 234,50', 'NOK 1234.50', '$NaN', '$-3.00'):
            with self.assertRaises(ValueError): parse_price(value)
        with self.assertRaises(ValueError): parse_price('1.234,50', 'unverified_locale')

    def test_schema_scrape_currency_and_quoted_stay_failures(self):
        row = self.row(); row.pop('price_quote_raw')
        with self.assertRaisesRegex(ValueError, 'schema'): self.audit([row])
        for change, flag in [({'scrape_id':'newest'}, 'unexpected_scrape_id'), ({'last_scraped':'yesterday'},'invalid_scrape_date'),
                             ({'price_quote_checkout_date':'2026-07-01'},'invalid_quoted_stay'),
                             ({'price_quote_raw':'{}'},'invalid_quote_json'),
                             ({'price_quote_raw':json.dumps({'quote':[1]})},'invalid_quote_json'),
                             ({'price_quote_raw':json.dumps({'quote':{'currency':'USD'}})},'currency_mismatch')]:
            _, r = self.audit([self.row(**change)])
            self.assertEqual(r['counts'][flag], 1); self.assertEqual(r['status'], 'BLOCKED')
        _, r = self.audit([self.row(price_quote_price_per_night='1000')])
        self.assertEqual(r['counts']['price_quote_difference'], 1)
        self.assertEqual(r['actual_scrape_dates'], {'2026-07-02':1})
        self.assertEqual(r['quoted_stay_range'], ['2026-07-05','2026-07-07'])
        _, r = self.audit([self.row(price_quote_raw=json.dumps({'quote':{'currency':'NOK','date_match':None,'returned_checkin_date':None}}))])
        self.assertEqual(r['counts']['quote_date_match_unresolved'], 1)
        self.assertEqual(r['counts']['quote_returned_dates_missing'], 1)
        # Decimal half-cent rounding must not be misclassified by binary float noise.
        _, r = self.audit([self.row(price='$1000.00',price_quote_price_per_night='1000.00',
                          price_quote_raw=json.dumps({'quote':{'currency':'NOK','price_per_night':'1000.005'}}))])
        self.assertEqual(r['counts']['invalid_records'],0)
        self.assertEqual(r['counts']['quote_flattened_rounding_difference'],1)

    def test_boundary_municipality_crs_and_invalid_geometry(self):
        feature = {'type':'Feature','properties':{'kode':'0301'},'geometry':mapping(self.boundary)}
        self.assertEqual(boundary_geometry(feature, municipality='0301', crs='EPSG:4326'), self.boundary)
        with self.assertRaises(ValueError): boundary_geometry(feature, municipality='0180', crs='EPSG:4326')
        bad = deepcopy(feature); bad['properties']={'county':'03'}
        with self.assertRaises(ValueError): boundary_geometry(bad, municipality='0301', crs='EPSG:4326')
        bad = deepcopy(feature); bad['geometry']=mapping(Polygon([(0,0),(2,2),(2,0),(0,2),(0,0)]))
        with self.assertRaises(ValueError): boundary_geometry(bad, municipality='0301', crs='EPSG:4326')
        bad = deepcopy(feature); bad['crs']={'properties':{'name':'EPSG:4258'}}
        with self.assertRaisesRegex(ValueError,'CRS'): boundary_geometry(bad, municipality='0301', crs='EPSG:4326')


class AcquisitionTests(unittest.TestCase):
    def test_legacy_discovery_excludes_only_reserved_v4_namespace(self):
        from src.db.sources import prepare_all_sources
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            legacy=root/'data/raw/inside_airbnb/copenhagen/2026-06-30/data/listings.csv.gz'
            legacy.parent.mkdir(parents=True); legacy.write_bytes(b'synthetic legacy source')
            private=root/'data/raw/v4/research_design_v4/oslo/2026-06-30/listings.csv.gz'
            private.parent.mkdir(parents=True); private.write_bytes(b'synthetic private V4 source')
            manifest=root/'manifest.json'; manifest.write_text('{"files":[]}')
            records=prepare_all_sources(project_root=root,manifest_path=manifest)
            self.assertEqual([r['relative_path'] for r in records],[legacy.relative_to(root).as_posix()])
            unknown=root/'data/raw/unknown/source.csv'; unknown.parent.mkdir(); unknown.write_text('synthetic')
            with self.assertRaisesRegex(ValueError,'Unrecognized'):
                prepare_all_sources(project_root=root,manifest_path=manifest)
    def test_exact_catalogue_selection_no_newest_fallback(self):
        entry={'city':'Oslo','publishDate':'2026-06-30','dataRoot':'https://data.insideairbnb.com/norway/oslo/oslo/'}
        doc={'data':{'allData':{'datasets':[entry]}}}
        self.assertTrue(catalogue_selection(doc,'Oslo','2026-06-30')[1].endswith('/2026-06-30/data/listings.csv.gz'))
        with self.assertRaises(ValueError): catalogue_selection(doc,'Oslo','2026-06-29')
        doc['data']['allData']['datasets'].append(entry)
        with self.assertRaises(ValueError): catalogue_selection(doc,'Oslo','2026-06-30')

    def test_immutable_acquisition_receipt_and_failed_auth_probe(self):
        with tempfile.TemporaryDirectory() as root:
            paths=Paths(scope(),Path(root))
            kwargs=dict(extent='synthetic',licence='synthetic',reference_period='2026-06-30',selection={'municipality':'synthetic'})
            response=io.BytesIO(b'synthetic raw bytes'); response.status=200; response.url='https://official.example/source'; response.headers={}
            with patch('src.v4.listings.urlopen',return_value=response):
                first=acquire(paths,'fixture','source.txt',response.url,**kwargs)
            with patch('src.v4.listings.urlopen') as request:
                self.assertEqual(acquire(paths,'fixture','source.txt',response.url,**kwargs), first)
                request.assert_not_called()
            with self.assertRaises(ValueError): acquire(paths,'fixture','source.txt','https://official.example/other',**kwargs)
            with patch('src.v4.listings.urlopen',side_effect=HTTPError(response.url,401,'Missing Credentials',{},None)):
                blocked=acquire(paths,'restricted','source.txt',response.url,**kwargs)
            self.assertEqual(blocked['http_status'],401); self.assertIsNone(blocked['local_location'])
            self.assertFalse(paths.source('restricted','source.txt').exists())
            self.assertNotIn('credentials',json.dumps(blocked).lower())
            before=paths.source('restricted','source.txt.receipt.json').read_bytes()
            with patch('src.v4.listings.urlopen') as retry:
                self.assertEqual(acquire(paths,'restricted','source.txt',response.url,**kwargs),blocked)
                retry.assert_not_called()
            self.assertEqual(paths.source('restricted','source.txt.receipt.json').read_bytes(),before)

    def test_official_unicode_catalogue_path_is_encoded_only_for_transport(self):
        with tempfile.TemporaryDirectory() as root:
            paths=Paths(scope('stockholm'),Path(root))
            url='https://data.insideairbnb.com/sweden/stockholms-län/stockholm/2026-06-30/data/listings.csv.gz'
            response=io.BytesIO(b'synthetic'); response.status=200; response.url=url; response.headers={}
            with patch('src.v4.listings.urlopen',return_value=response) as request:
                record=acquire(paths,'fixture','source.txt',url,extent='synthetic',licence='synthetic',reference_period='2026-06-30')
            self.assertIn('stockholms-l%C3%A4n',request.call_args[0][0].full_url)
            self.assertEqual(record['source_url'],url)


if __name__ == '__main__': unittest.main()
