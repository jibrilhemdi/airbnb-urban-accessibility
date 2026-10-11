"""Explicitly synthetic smoke checks; these are never scientific results."""
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV
from src.pipeline.protocol import SEED,AREA_NAMES
from src.pipeline.model_specification import FEATURES,build_preprocessor
from src.pipeline.build_validation_splits import make_outer,inner_splits
from src.pipeline.build_tuning_candidates import build,load_candidates
from src.pipeline.run_primary_models import xgb_pipeline,explain_heldout
from src.ingestion.common import PROJECT_ROOT,write_json

def synthetic_frame(n_per_area=20):
    rng=np.random.default_rng(SEED);n=n_per_area*11
    frame=pd.DataFrame({c:rng.uniform(.1,2,n) for c in FEATURES['MEW'] if c!='property_type'})
    frame['property_type']=np.where(np.arange(n)%2,'Entire condo','Entire rental unit')
    frame['analysis_area']=np.repeat(AREA_NAMES,n_per_area);frame['metric_x']=np.repeat(np.arange(11)*2000,n_per_area)+rng.uniform(0,1800,n)
    frame['metric_y']=rng.uniform(0,15000,n);frame['listing_id']=np.arange(n)+1;frame['snapshot_date']='2000-01-01'
    frame['log_price']=6+frame.accommodates*.2+rng.normal(0,.1,n);frame['price_nightly']=np.exp(frame.log_price)
    return frame

def run():
    build();frame=synthetic_frame();outer=make_outer(frame);fold,tr,te=outer['geographic_11'][0]
    train,test=frame.iloc[tr].reset_index(drop=True),frame.iloc[te].reset_index(drop=True)
    train.loc[0,'bedrooms']=np.nan;test.loc[:,'bedrooms']=99999
    prep=build_preprocessor('M0');prep.fit(train);median=prep.named_transformers_['numeric'].statistics_[1]
    if median!=train.bedrooms.median():raise RuntimeError('Synthetic training-only median smoke check failed')
    inner=inner_splits(train);candidates=load_candidates()['candidates']
    grid=[{'xgb__'+k:[v] for k,v in c.items()} for c in candidates]
    search=GridSearchCV(xgb_pipeline('MW'),grid,cv=inner,scoring='neg_root_mean_squared_error',error_score='raise',n_jobs=1)
    search.fit(train,train.log_price);shap=explain_heldout(search.best_estimator_,test,'MW','synthetic_geographic',fold)
    result={'status':'passed','scope':'synthetic computational smoke only; no real listing results',
        'synthetic_n':len(frame),'outer_training_n':len(train),'heldout_n':len(test),'candidates_evaluated':len(candidates),
        'inner_grouped_folds':len(inner),'training_only_median':True,'heldout_shap_reconstruction':True,'shap_records':len(shap)}
    write_json(PROJECT_ROOT/'outputs/tables/reproducibility/synthetic_smoke_checks.json',result);return result
if __name__=='__main__':print(run())
