"""Nested training-only price-tail and inherited reputation sensitivities."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator,RegressorMixin,clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV
from xgboost import XGBRegressor
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,MODELS
from src.study.sample_freeze import records
from src.study.validation import outer_splits,inner_splits
from src.study.store import commit_package,dependencies
from src.study.modeling import metrics


class TrainingTailRegressor(RegressorMixin,BaseEstimator):
    def __init__(self,pipeline=None):self.pipeline=pipeline
    def fit(self,X,y):
        y=np.asarray(y,float);self.thresholds_=np.quantile(y,[.01,.99]);keep=(y>=self.thresholds_[0])&(y<=self.thresholds_[1])
        self.training_n_=int(keep.sum())
        if X.loc[keep].isna().all().any():raise ValueError('Tail-restricted training predictor wholly missing')
        self.pipeline_=clone(self.pipeline).fit(X.loc[keep],y[keep]);return self
    def predict(self,X):return self.pipeline_.predict(X)


def run(city,scenarios=('training_price_tail','reputation')):
    design,_=load_design();chosen=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text());engine=get_engine();pointers=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY');frame=pd.DataFrame(records(conn,chosen,city,'sample','prediction_sample'))
        folds=outer_splits(frame,city)['neighbourhood']
        candidates=json.loads((PROJECT_ROOT/design['candidates']['path']).read_text())['candidates']
        for scenario in scenarios:
            for fold,tr,te in folds:
                train,test=frame.iloc[tr].copy(),frame.iloc[te].copy();predictions=[];scores=[];tuning=[]
                for estimator in ('OLS','XGBoost'):
                    for model in MODELS:
                        features=list(design['models'][model])
                        if scenario=='reputation':
                            for part in (train,test):part['log1p_number_of_reviews']=np.log1p(part.number_of_reviews)
                            features+=['log1p_number_of_reviews','review_scores_rating']
                        numeric=[f for f in features if f!='property_type']
                        if train[features].isna().all().any():raise ValueError('Required training predictor wholly missing')
                        prep=ColumnTransformer([('numeric',SimpleImputer(strategy='median',add_indicator=True),numeric),
                                                ('category',OneHotEncoder(drop='first',handle_unknown='ignore',sparse_output=False),['property_type'])])
                        learner=LinearRegression() if estimator=='OLS' else XGBRegressor(objective='reg:squarederror',random_state=design['validation']['random_seed'],n_jobs=1,tree_method='hist')
                        pipeline=Pipeline([('prep',prep),('model',learner)])
                        target=TrainingTailRegressor(pipeline) if scenario=='training_price_tail' else pipeline
                        if estimator=='XGBoost':
                            prefix='pipeline__model__' if scenario=='training_price_tail' else 'model__'
                            grid=[{prefix+k:[v] for k,v in c.items()} for c in candidates]
                            search=GridSearchCV(target,grid,cv=inner_splits(train),scoring='neg_root_mean_squared_error',n_jobs=2,error_score='raise')
                            search.fit(train[features],train.log_price.to_numpy(float));fit=search.best_estimator_
                            selected={'candidate_count':30,'inner_folds':4,'selected_parameters':search.best_params_,'candidate_scores':(-search.cv_results_['mean_test_score']).tolist()}
                        else:fit=target.fit(train[features],train.log_price.to_numpy(float));selected={}
                        p=np.asarray(fit.predict(test[features]),float);y=test.log_price.to_numpy(float)
                        scores.append({'estimator':estimator,'model':model,**metrics(y,p)})
                        tuning.append({'estimator':estimator,'model':model,**selected,
                                       'source_tail_thresholds':fit.thresholds_.tolist() if scenario=='training_price_tail' else None})
                        predictions.extend({'listing_id':str(row.listing_id),'operational_group':row.operational_group,'estimator':estimator,'model':model,
                                            'log_price':float(a),'prediction':float(b),'squared_error':float((a-b)**2),'absolute_error':float(abs(a-b))}
                                           for row,a,b in zip(test.itertuples(),y,p,strict=True))
                summary={'city':city,'scenario':scenario,'status':'COMPLETE_FOLD','fold':str(fold),'n':len(frame),'train_n':len(tr),'test_n':len(te),
                         'metrics':scores,'prediction_hash':canonical_hash(predictions),'full_heldout_evaluation':True,
                         'preprocessing':'Tail thresholds and preprocessing fit inside each inner/outer training partition; no target restriction'}
                with engine.begin() as conn:
                    identity=commit_package(conn,city=city,family='robustness',summary=summary,records={'predictions':predictions,'tuning':tuning},
                                            deps=dependencies({'sample':chosen[city],'code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_training_sensitivity.py')}))
                pointers.append({'run_id':identity,'scenario':scenario,'fold':str(fold),'summary_sha256':canonical_hash(summary)})
                print(city,scenario,fold,'COMPLETE_FOLD',flush=True)
        write_once(PROJECT_ROOT/'runs'/city/'training_sensitivity_selection.json',(json.dumps(pointers,indent=2)+'\n').encode())
    finally:engine.dispose()
    return pointers


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--city',required=True)
    args=parser.parse_args();run(args.city)
