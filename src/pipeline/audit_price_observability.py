"""Explicit outcome observability audit; no outcome imputation or price selection."""
import pandas as pd
from sqlalchemy import text
from src.pipeline.storage import export

def run(engine):
    with engine.connect() as conn:
        table=pd.read_sql(text('SELECT s.analysis_area,count(*) AS residential_n,count(*) FILTER(WHERE NOT l.valid_price) AS missing_or_invalid_price_n,'
            'count(*) FILTER(WHERE l.valid_price) AS observed_price_n FROM v3_clean.airbnb_listings l JOIN v3_features.listing_spatial_base s USING(snapshot_date,listing_id) '
            'WHERE l.entire_home_apt AND l.conventional_residential AND l.valid_coordinates GROUP BY s.analysis_area ORDER BY s.analysis_area'),conn)
    table['missing_fraction']=table.missing_or_invalid_price_n/table.residential_n
    export('analysis_dataset','price_observability.csv',table);return {'areas':len(table),'residential_n':int(table.residential_n.sum())}
