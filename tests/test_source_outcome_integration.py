"""Small actual-source smoke check in a temporary, rolled-back SQL table."""
import os
import unittest
from pathlib import Path
from sqlalchemy import text
from src.db.connection import get_engine
from src.db.migrations import version3_schema_check
from src.ingestion.common import PROJECT_ROOT
from src.ingestion.price import source_price

@unittest.skipUnless(os.environ.get('THESIS_DB_TEST')=='1','Set THESIS_DB_TEST=1 for temporary-table source smoke')
class SourceOutcomeIntegrationTest(unittest.TestCase):
    def test_actual_source_cleaning_preserves_missing_price_and_metric_crs(self):
        engine=get_engine()
        try:
            check=version3_schema_check(engine)
            before=check['current_clean_listing_rows']
            with engine.connect() as conn:
                transaction=conn.begin()
                try:
                    listings_id=conn.scalar(text("SELECT source_file_id FROM meta.source_files WHERE relative_path='data/raw/inside_airbnb/copenhagen/2026-06-30/data/listings.csv.gz'"))
                    lookup_id=conn.scalar(text("SELECT source_file_id FROM meta.source_files WHERE relative_path='data/raw/inside_airbnb/copenhagen/2026-06-30/visualisations/neighbourhoods.csv'"))
                    conn.execute(text('CREATE TEMPORARY TABLE outcome_smoke (LIKE v3_clean.airbnb_listings INCLUDING DEFAULTS) ON COMMIT DROP'))
                    query=(PROJECT_ROOT/'sql/queries/build_clean_airbnb_listings.sql').read_text()
                    query=query.replace('WHERE _source_file_id = :listings_file_id','WHERE _source_file_id = :listings_file_id ORDER BY _source_row_number LIMIT 30',1)
                    query=query.replace('INSERT INTO v3_clean.airbnb_listings','INSERT INTO pg_temp.outcome_smoke',1)
                    conn.execute(text(query),{'snapshot_date':'2026-06-30','listings_file_id':listings_id,'lookup_file_id':lookup_id})
                    rows=conn.execute(text('SELECT r.price,c.price_nightly,c.log_price,ST_SRID(c.geom_25832) AS metric_epsg FROM pg_temp.outcome_smoke c JOIN raw.inside_airbnb_listings r ON r._source_file_id=c.source_file_id AND r.id::bigint=c.listing_id')).all()
                    self.assertEqual(len(rows),30)
                    for raw,price,log_price,crs in rows:
                        expected_price,expected_log=source_price(raw)
                        self.assertEqual(price is None,expected_price is None);self.assertEqual(log_price is None,expected_log is None)
                        if expected_price is not None:self.assertAlmostEqual(float(price),expected_price)
                        if expected_log is not None:self.assertAlmostEqual(log_price,expected_log)
                        self.assertEqual(crs,25832)
                    missing=conn.scalar(text('SELECT count(*) FROM pg_temp.outcome_smoke WHERE price_nightly IS NULL'))
                    self.assertGreater(missing,0)
                finally:transaction.rollback()
            self.assertEqual(version3_schema_check(engine)['current_clean_listing_rows'],before)
        finally:engine.dispose()
