"""Outcome and held-out residual spatial diagnostics with explicit metric CRS."""
import numpy as np
import pandas as pd
from src.pipeline.protocol import SEED
from src.pipeline.storage import load_artifact,persist,export
from src.pipeline.build_analysis_dataset import load_dataset
from src.spatial.spatial_diagnostics import moran_knn

def residual_coordinates(part,frame):
    """Join the same frozen observations despite date versus ISO timestamp text."""
    keys=['snapshot_date','listing_id']
    observations=part.copy();locations=frame[keys+['metric_x','metric_y']].copy()
    for table in [observations,locations]:
        table['snapshot_date']=table.snapshot_date.astype(str).str[:10]
        pd.to_datetime(table.snapshot_date,format='%Y-%m-%d',errors='raise')
    merged=observations.merge(locations,on=keys,validate='one_to_one')
    if len(merged)!=len(part) or len(merged)!=len(frame):
        raise RuntimeError('Spatial diagnostic join must retain every frozen held-out observation')
    return merged

def run(engine,run_id):
    with engine.connect() as conn:
        frame=load_dataset(conn);oof=load_artifact(conn,run_id,'primary_models','oof_predictions')
    xy=frame[['metric_x','metric_y']].to_numpy(float)
    rows=[{'variable':'log_price','model':'none','feature_set':'none','scheme':'descriptive',**moran_knn(frame.log_price.to_numpy(float),xy,seed=SEED)}]
    selected=oof.loc[(oof.scheme=='geographic_11')&(oof.feature_set.isin(['M0','MW']))&(oof.model.isin(['OLS','XGBoost']))]
    area=[]
    for (model,fs),part in selected.groupby(['model','feature_set']):
        merged=residual_coordinates(part,frame)
        rows.append({'variable':'residual','model':model,'feature_set':fs,'scheme':'geographic_11',**moran_knn(merged.residual.to_numpy(float),merged[['metric_x','metric_y']].to_numpy(float),seed=SEED)})
        for name,data in part.groupby('analysis_area'):area.append({'analysis_area':name,'model':model,'feature_set':fs,'n':len(data),'mean_residual':float(data.residual.mean()),'median_absolute_error':float(data.absolute_error.median())})
    table=pd.DataFrame(rows);residuals=pd.DataFrame(area)
    with engine.begin() as conn:persist(conn,run_id,'primary_models','spatial_moran',table);persist(conn,run_id,'primary_models','residual_by_analysis_area',residuals)
    export('primary_models','spatial_moran.csv',table);export('primary_models','residual_by_analysis_area.csv',residuals)
    return {'diagnostics':len(table),'crs_epsg':25832}
