"""Freeze a common V3 sample from PostgreSQL with explicit exclusions/missingness."""
from __future__ import annotations
import json
import re
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.db.connection import get_engine
from src.ingestion.common import write_json,PROJECT_ROOT
from src.pipeline.protocol import canonical_hash,verify_income_evidence,AREA_NAMES
from src.pipeline.model_specification import AMENITIES,FEATURES,prepare_features
from src.pipeline.storage import export,json_records
VERSION='analysis_dataset_v3'
def bathroom_value(structured,source_text):
    if pd.notna(structured):return float(structured),'structured'
    if source_text=='Half-bath':return .5,'source_text'
    if isinstance(source_text,str) and re.fullmatch(r'[0-9]+(?:\.[0-9]+)? baths?',source_text,re.I):return float(source_text.split()[0]),'source_text'
    return np.nan,'missing'
def load_dataset(conn):
    records=conn.execute(text('SELECT record FROM v3_analysis.dataset_records ORDER BY snapshot_date,listing_id')).scalars().all()
    if not records:raise RuntimeError('Frozen V3 dataset missing')
    return pd.DataFrame(records)
def dataset_hash(frame):
    columns=sorted(frame.columns)
    return canonical_hash(json_records(frame.sort_values(['snapshot_date','listing_id'])[columns]))
def build(engine):
    verify_income_evidence()
    with engine.connect() as conn:
        frame=pd.read_sql(text('SELECT l.*,s.analysis_area,s.near_official_border_100m,s.distance_centre_euclidean_km,'
            'ST_X(l.geom_25832) AS metric_x,ST_Y(l.geom_25832) AS metric_y,'
            'c.log_population_density,c.equiv_disposable_income_2024,c.income_100k_dkk,c.income_harmonisation_status,'
            'e.nearest_station_distance_m AS nearest_station_euclidean_m,e.count_coverage_complete,'
            'e.food_social_833m,e.food_social_1250m,e.food_social_1667m,e.cultural_tourist_833m,e.cultural_tourist_1250m,e.cultural_tourist_1667m,'
            'w.nearest_station_walking_minutes,w.nearest_station_network_distance_m,w.food_social_w_10,w.food_social_w_15,w.food_social_w_20,'
            'w.cultural_tourist_w_10,w.cultural_tourist_w_15,w.cultural_tourist_w_20,w.nearest_station_coverage_complete AS rail_walk_coverage,'
            'b.nearest_bus_euclidean_m,b.nearest_bus_walking_minutes,b.bus_walking_distance_m,b.walking_coverage_complete AS bus_walk_coverage '
            'FROM v3_clean.airbnb_listings l LEFT JOIN v3_features.listing_spatial_base s USING(snapshot_date,listing_id) '
            'LEFT JOIN v3_features.area_context c USING(analysis_area) LEFT JOIN v3_features.euclidean_accessibility e USING(snapshot_date,listing_id) '
            'LEFT JOIN v3_features.walking_accessibility w USING(snapshot_date,listing_id) LEFT JOIN v3_features.bus_accessibility b USING(snapshot_date,listing_id) '
            'ORDER BY l.snapshot_date,l.listing_id'),conn)
    if frame[['snapshot_date','listing_id']].duplicated().any():raise RuntimeError('Dataset joins multiplied listing rows')
    original_n=len(frame);flow=[]
    rules=[('conventional_entire_home_with_observed_positive_price',frame.primary_sample_candidate),
        ('assigned_analysis_area',frame.analysis_area.notna()),('matched_opportunity_coverage',frame.count_coverage_complete.eq(True)),
        ('reachable_rail_and_bus',frame.nearest_station_walking_minutes.notna() & frame.nearest_bus_walking_minutes.notna()),
        ('complete_nearest_destination_coverage',frame.rail_walk_coverage.eq(True)&frame.bus_walk_coverage.eq(True))]
    selected=pd.Series(True,index=frame.index)
    for name,condition in rules:
        before=int(selected.sum());selected &= condition.fillna(False)
        flow.append({'rule':name,'remaining_n':int(selected.sum()),'excluded_n':before-int(selected.sum())})
    export('analysis_dataset','sample_construction.csv',pd.DataFrame(flow))
    frame=frame.loc[selected].copy().reset_index(drop=True)
    if set(frame.analysis_area)!=set(AREA_NAMES):raise RuntimeError('Common sample must contain all eleven analysis areas')
    if not frame.income_harmonisation_status.eq('qualified').all():raise RuntimeError('Income must match the qualified accepted protocol')
    bathroom=[bathroom_value(a,b) for a,b in zip(frame.bathrooms,frame.bathrooms_text)]
    frame['bathrooms_effective']=[r[0] for r in bathroom];frame['bathrooms_source']=[r[1] for r in bathroom]
    for source,target in [('minimum_nights','log1p_minimum_nights'),('host_listings_count','log1p_host_listings_count')]:frame[target]=np.log1p(pd.to_numeric(frame[source],errors='raise'))
    frame['superhost']=frame.host_is_superhost.map({'t':1.,'true':1.,'yes':1.,'f':0.,'false':0.,'no':0.})
    keys={'amenity_wifi':'Wifi','amenity_dishwasher':'Dishwasher','amenity_washer':'Washer','amenity_dryer':'Dryer','amenity_workspace':'Dedicated workspace','amenity_free_parking':'Free parking on premises','amenity_private_balcony':'Private patio or balcony','amenity_self_checkin':'Self check-in'}
    def amenity(raw,name):
        if pd.isna(raw):return np.nan
        values=json.loads(raw)
        if not isinstance(values,list):raise RuntimeError('Invalid source amenity JSON')
        return float(name in values)
    for col,name in keys.items():frame[col]=[amenity(raw,name) for raw in frame.amenities_raw]
    frame=prepare_features(frame)
    retain=['snapshot_date','listing_id','analysis_area','price_nightly','log_price','metric_x','metric_y','property_type','number_of_reviews','review_scores_rating',
        'equiv_disposable_income_2024','income_harmonisation_status',
        'near_official_border_100m','bathrooms_source','nearest_station_euclidean_m','nearest_bus_euclidean_m','nearest_station_network_distance_m','bus_walking_distance_m',
        'food_social_833m','food_social_1250m','food_social_1667m','cultural_tourist_833m','cultural_tourist_1250m','cultural_tourist_1667m',
        'food_social_w_10','food_social_w_15','food_social_w_20','cultural_tourist_w_10','cultural_tourist_w_15','cultural_tourist_w_20',*FEATURES['MEW']]
    frame=frame[list(dict.fromkeys(retain))]
    numeric=frame.select_dtypes(include='number')
    if np.isinf(numeric.to_numpy()).any():raise RuntimeError('Nonfinite predictor value; investigate source')
    missing=pd.DataFrame([{'variable':c,'n':len(frame),'missing_n':int(frame[c].isna().sum()),'missing_fraction':float(frame[c].isna().mean())} for c in frame.columns])
    export('analysis_dataset','missingness.csv',missing)
    export('analysis_dataset','analysis_area_counts.csv',frame.groupby('analysis_area').size().rename('n').reset_index())
    export('analysis_dataset','data_dictionary.csv',pd.DataFrame([{'variable':c,'type':str(frame[c].dtype),'role':'outcome' if c in ['price_nightly','log_price'] else 'predictor' if c in FEATURES['MEW'] else 'identifier_or_diagnostic','crs_epsg':25832 if c in ['metric_x','metric_y'] else None} for c in frame.columns]))
    rows=json_records(frame)
    with engine.begin() as conn:
        if conn.scalar(text('SELECT count(*) FROM v3_analysis.dataset_records')):raise RuntimeError('Analytical dataset is already frozen')
        conn.execute(text('INSERT INTO v3_analysis.dataset_records(snapshot_date,listing_id,analysis_area,dataset_version,record) VALUES(:snapshot,:id,:area,:version,CAST(:record AS jsonb))'),
            [dict(snapshot=r['snapshot_date'],id=r['listing_id'],area=r['analysis_area'],version=VERSION,record=json.dumps(r,allow_nan=False)) for r in rows])
    with engine.connect() as conn:roundtrip=load_dataset(conn)
    meta={'version':VERSION,'n':len(frame),'upstream_listing_n':original_n,'dataset_sha256':dataset_hash(roundtrip),'analysis_area_counts':frame.analysis_area.value_counts().to_dict(),
        'sample_construction':flow,'crs_epsg':25832,'outcome_imputed':False,'income_harmonisation_status':'qualified','geometry_private':True}
    write_json(PROJECT_ROOT/'outputs/tables/analysis_dataset/dataset_freeze.json',meta)
    return meta
if __name__=='__main__':
    engine=get_engine()
    try:print(json.dumps(build(engine),indent=2))
    finally:engine.dispose()
