"""Source/training-only predictive estimation for the exact common feature ladder."""
from __future__ import annotations
import json
import numpy as np
from scipy.stats import pearsonr,spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

from src.ingestion.common import PROJECT_ROOT
from src.study.specification import load_design,CITIES
from src.study.validation import inner_splits


def metrics(y,prediction):
    y=np.asarray(y,float);p=np.asarray(prediction,float)
    if y.shape!=p.shape or not len(y) or not np.isfinite(y).all() or not np.isfinite(p).all():raise ValueError('Invalid saved outcome/prediction')
    variable=np.ptp(y)>0 and np.ptp(p)>0
    return {'n':len(y),'rmse':float(np.sqrt(mean_squared_error(y,p))),'mae':float(mean_absolute_error(y,p)),
            'r2':float(r2_score(y,p,force_finite=False)) if len(y)>1 and np.ptp(y)>0 else None,
            'pearson':float(pearsonr(y,p).statistic) if variable else None,
            'spearman':float(spearmanr(y,p).statistic) if variable else None}


def fit_source(train,model,estimator,y):
    """No target dataframe, target outcome, benchmark or validation can enter fitting."""
    design,_=load_design();features=design['models'][model]
    if len(set(train.city))!=1 or train.city.iloc[0] not in CITIES:raise ValueError('One isolated source city required')
    y=np.asarray(y,float)
    if len(y)!=len(train) or not np.isfinite(y).all():raise ValueError('Observed source outcome required; never impute')
    numeric=[f for f in features if f!='property_type']
    def qualified(part):
        if part[features].isna().all().any():raise ValueError('All-missing required training predictor')
        if np.isinf(part[numeric].to_numpy(float)).any():raise ValueError('Nonfinite source predictor')
    qualified(train)
    prep=ColumnTransformer([('numeric',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),numeric),
                            ('category',OneHotEncoder(drop='first',handle_unknown='ignore',sparse_output=False),['property_type'])],
                           remainder='drop',verbose_feature_names_out=False)
    if estimator=='OLS':
        fit=Pipeline([('prep',prep),('model',LinearRegression())]).fit(train[features],y)
        return fit,{'estimator':'OLS','source_n':len(train),'tuning':None}
    if estimator!='XGBoost':raise ValueError('Only frozen OLS/XGBoost estimators allowed')
    splits=inner_splits(train)
    for tr,_ in splits:qualified(train.iloc[tr])
    candidates=json.loads((PROJECT_ROOT/design['candidates']['path']).read_text())['candidates']
    grid=[{'model__'+k:[v] for k,v in candidate.items()} for candidate in candidates]
    pipeline=Pipeline([('prep',prep),('model',XGBRegressor(objective='reg:squarederror',random_state=design['validation']['random_seed'],n_jobs=1,tree_method='hist'))])
    import os
    workers=int(os.environ.get('STUDY_MODEL_WORKERS','4'))
    if workers<1 or workers>8:raise ValueError('Bounded operational worker count required')
    search=GridSearchCV(pipeline,grid,scoring='neg_root_mean_squared_error',cv=splits,refit=True,n_jobs=workers,error_score='raise')
    search.fit(train[features],y)
    return search.best_estimator_,{'estimator':'XGBoost','source_n':len(train),'candidate_count':len(candidates),
                                 'inner_folds':len(splits),'selected_parameters':search.best_params_,
                                 'candidate_scores':(-search.cv_results_['mean_test_score']).tolist()}


def predict_source(fit,target,model):
    design,_=load_design()
    return fit.predict(target[design['models'][model]])


def transfer(train,target,source_city,target_city,model,estimator,source_mean,target_mean):
    if source_city==target_city or source_city not in CITIES or target_city not in CITIES:raise ValueError('Directional distinct source/target cities required')
    if not train.city.eq(source_city).all() or not target.city.eq(target_city).all():raise ValueError('City isolation failed')
    if not np.isfinite([source_mean,target_mean]).all():raise ValueError('Both frozen reference benchmarks required')
    fit,tuning=fit_source(train,model,estimator,train.log_price.to_numpy(float)-source_mean)
    # Access target outcomes only after complete source-only fitting/prediction.
    prediction=predict_source(fit,target,model)
    observed=target.log_price.to_numpy(float)-target_mean
    return {'source_city':source_city,'target_city':target_city,'model':model,'estimator':estimator,
            'prediction':prediction,'observed_relative':observed,'metrics':metrics(observed,prediction),
            'tuning':tuning,'fit':fit,'target_fit':False,'target_intercept_recalibration':False}
