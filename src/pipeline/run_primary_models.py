"""Nested V3 OLS/XGBoost evaluation and explanations on held-out observations."""
from __future__ import annotations
import json
import time
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sqlalchemy import text
from xgboost import XGBRegressor,DMatrix
from src.db.connection import get_engine
from src.ingestion.common import PROJECT_ROOT,write_json
from src.pipeline.protocol import DESIGN,SEED,canonical_hash,verify_income_evidence
from src.pipeline.model_specification import FEATURES,ALL_FEATURES,CATEGORICAL,build_preprocessor
from src.pipeline.build_analysis_dataset import load_dataset,dataset_hash
from src.pipeline.build_validation_splits import saved_outer,inner_splits
from src.pipeline.build_tuning_candidates import load_candidates,SPACE
from src.pipeline.inference import paired_incremental,wild_cluster_bootstrap_t
from src.pipeline.storage import persist,load_artifact,export

def metrics(y,p):
    return {'n':len(y),'rmse_log':float(np.sqrt(mean_squared_error(y,p))),'mae_log':float(mean_absolute_error(y,p)),'r2_log':float(r2_score(y,p))}
def xgb_pipeline(feature_set,extra=()):
    return Pipeline([('prep',build_preprocessor(feature_set,extra)),('xgb',XGBRegressor(objective='reg:squarederror',tree_method='hist',random_state=SEED,n_jobs=2,verbosity=0))])
def saved_inner(conn,train,scheme,fold):
    records=conn.execute(text('SELECT snapshot_date,listing_id,inner_fold FROM v3_analysis.inner_assignments WHERE scheme=:scheme AND outer_fold=:fold'),{'scheme':scheme,'fold':fold}).mappings().all()
    keys={(str(r.snapshot_date)[:10],int(r.listing_id)):i for i,r in train.iterrows()}
    labels=np.zeros(len(train),int)
    if len(records)!=len(train):raise RuntimeError('Saved inner training assignments incomplete')
    for row in records:
        key=(str(row['snapshot_date']),row['listing_id'])
        if key not in keys:raise RuntimeError('Outer test/excluded observation leaked into inner assignments')
        labels[keys[key]]=row['inner_fold']
    if set(labels)!=set(range(1,DESIGN['inner_folds']+1)):raise RuntimeError('Inner folds missing')
    groups=(np.floor(train.metric_x/1000).astype(int).astype(str)+':'+np.floor(train.metric_y/1000).astype(int).astype(str)).to_numpy()
    splits=[]
    for f in range(1,DESIGN['inner_folds']+1):
        tr=np.flatnonzero(labels!=f);va=np.flatnonzero(labels==f)
        if set(groups[tr]) & set(groups[va]):raise RuntimeError('Inner grid-block leakage')
        splits.append((tr,va))
    return splits

def explain_heldout(fit,test,feature_set,scheme,fold):
    prep=fit.named_steps['prep'];estimator=fit.named_steps['xgb'];X=np.asarray(prep.transform(test),float)
    names=list(prep.get_feature_names_out())
    contributions=estimator.get_booster().predict(DMatrix(X),pred_contribs=True,approx_contribs=False)
    prediction=fit.predict(test)
    if not np.allclose(contributions.sum(axis=1),prediction,atol=1e-4):raise RuntimeError('Held-out SHAP does not reconstruct predictions')
    return [dict(snapshot_date=str(row.snapshot_date)[:10],listing_id=int(row.listing_id),analysis_area=row.analysis_area,
        feature_set=feature_set,scheme=scheme,outer_fold=fold,prediction=float(prediction[i]),base_value=float(contributions[i,-1]),
        shap={name:float(contributions[i,j]) for j,name in enumerate(names)},method='exact TreeSHAP, tree-path-dependent; outer held-out')
        for i,(_,row) in enumerate(test.iterrows())]

def evaluate_cv(frame,outer,engine,run_id,family='primary_models',extra=(),saved_training=True,shap=True,feature_sets=None):
    """Same fixed candidates and saved training-only splits for every feature set."""
    candidates=load_candidates()['candidates'];grid=[{'xgb__'+k:[v] for k,v in c.items()} for c in candidates]
    feature_sets=feature_sets or tuple(FEATURES);fold_metrics=[];tuning=[];preprocessing=[];all_oof=[];all_shap=[]
    for scheme,folds in outer.items():
        for fold,tr,te in folds:
            train=frame.iloc[tr].reset_index(drop=True);test=frame.iloc[te].reset_index(drop=True)
            if not len(train) or len(test)<2:raise RuntimeError('Empty/too-small evaluation fold')
            with engine.connect() as conn:inner=saved_inner(conn,train,scheme,fold) if saved_training else inner_splits(train)
            y=train.log_price.to_numpy(float);yt=test.log_price.to_numpy(float)
            if np.isnan(y).any() or np.isnan(yt).any():raise RuntimeError('Never impute an outcome')
            fold_oof=[];fold_shap=[]
            specifications=[('train_mean','none')]+[(model,fs) for model in ['OLS','XGBoost'] for fs in feature_sets]
            for model,fs in specifications:
                started=time.monotonic()
                if model=='train_mean':prediction=np.full(len(test),y.mean());fit=None
                else:
                    columns=ALL_FEATURES[fs]+tuple(extra)
                    if train[list(columns)].isna().all().any():raise RuntimeError('Training predictor has no support for a learned imputation statistic')
                    for it,iv in inner:
                        if train.iloc[it][list(columns)].isna().all().any():raise RuntimeError('Inner-training predictor is entirely missing')
                    if model=='OLS':
                        fit=Pipeline([('prep',build_preprocessor(fs,extra)),('ols',LinearRegression())]);fit.fit(train,y)
                    else:
                        search=GridSearchCV(xgb_pipeline(fs,extra),grid,scoring='neg_root_mean_squared_error',cv=inner,refit=True,n_jobs=1,error_score='raise',return_train_score=False)
                        search.fit(train,y);fit=search.best_estimator_;selected={k.removeprefix('xgb__'):v for k,v in search.best_params_.items()}
                        boundary={k:('minimum' if selected[k]==min(values) else 'maximum' if selected[k]==max(values) else 'interior') for k,values in SPACE.items()}
                        for i,candidate in enumerate(candidates):
                            tuning.append({'scheme':scheme,'outer_fold':fold,'feature_set':fs,'candidate_id':i+1,'candidate':candidate,
                                'inner_rmse':float(-search.cv_results_['mean_test_score'][i]),'inner_score_sd':float(search.cv_results_['std_test_score'][i]),
                                'selected':i==search.best_index_,'selected_parameters':selected if i==search.best_index_ else None,'boundary_hits':boundary if i==search.best_index_ else None,
                                'candidate_sha256':canonical_hash(candidates),'train_n':len(train),'inner_folds':len(inner)})
                    prediction=fit.predict(test)
                    prep=fit.named_steps['prep'];imp=prep.named_transformers_['numeric']
                    preprocessing.append({'scheme':scheme,'outer_fold':fold,'feature_set':fs,'model':model,
                        'train_n':len(train),'train_missing_counts':train[list(columns)].isna().sum().to_dict(),
                        'numeric_columns':list(prep.transformers_[0][2]),'training_medians':imp.statistics_.tolist(),
                        'missing_indicator_positions':imp.indicator_.features_.tolist(),'training_category_levels':[x.tolist() for x in prep.named_transformers_['category'].categories_]})
                    if model=='XGBoost' and shap:fold_shap.extend(explain_heldout(fit,test,fs,scheme,fold))
                fold_metrics.append({'scheme':scheme,'outer_fold':fold,'heldout_analysis_area':fold if scheme.rsplit('/',1)[-1].startswith(('geographic','buffered')) else None,
                    'model':model,'feature_set':fs,'train_n':len(train),**metrics(yt,prediction)})
                for i,row in test.iterrows():
                    residual=float(yt[i]-prediction[i]);fold_oof.append({'snapshot_date':str(row.snapshot_date)[:10],'listing_id':int(row.listing_id),
                        'analysis_area':row.analysis_area,'scheme':scheme,'outer_fold':fold,'heldout_analysis_area':fold if scheme.rsplit('/',1)[-1].startswith(('geographic','buffered')) else None,
                        'feature_set':fs,'model':model,'log_price':float(yt[i]),'prediction':float(prediction[i]),'residual':residual,
                        'squared_error':residual**2,'absolute_error':abs(residual)})
                print(f'{family}: {scheme} / {fold} / {model} / {fs}, {time.monotonic()-started:.1f}s',flush=True)
            with engine.begin() as conn:
                persist(conn,run_id,family,f'oof/{scheme}/{fold}',fold_oof);persist(conn,run_id,family,f'shap/{scheme}/{fold}',fold_shap)
                persist(conn,run_id,family,f'tuning/{scheme}/{fold}',[r for r in tuning if r['scheme']==scheme and r['outer_fold']==fold])
                persist(conn,run_id,family,f'preprocessing/{scheme}/{fold}',[r for r in preprocessing if r['scheme']==scheme and r['outer_fold']==fold])
            all_oof.extend(fold_oof);all_shap.extend(fold_shap)
    oof=pd.DataFrame(all_oof);folds=pd.DataFrame(fold_metrics);pooled=[]
    for (scheme,model,fs),p in oof.groupby(['scheme','model','feature_set']):
        row={'scheme':scheme,'model':model,'feature_set':fs,**metrics(p.log_price,p.prediction)}
        f=folds.loc[(folds.scheme==scheme)&(folds.model==model)&(folds.feature_set==fs)]
        for metric in ['rmse_log','mae_log','r2_log']:
            for q,label in [(.25,'q25'),(.5,'median'),(.75,'q75')]:row['fold_'+metric+'_'+label]=float(f[metric].quantile(q))
        pooled.append(row)
    summaries={}
    for (scheme,fs),part in pd.DataFrame(all_shap).groupby(['scheme','feature_set']) if all_shap else []:
        sums={}
        for values in part.shap:
            for name,value in values.items():sums[name]=sums.get(name,0)+abs(value)
        for name,value in sums.items():summaries[(scheme,fs,name)]={'scheme':scheme,'feature_set':fs,'feature':name,'heldout_n':len(part),'mean_absolute_shap':value/len(part)}
    artifacts={'oof_predictions':oof,'fold_performance':folds,'model_performance':pd.DataFrame(pooled),
        'xgboost_tuning':pd.DataFrame(tuning),'preprocessing':pd.DataFrame(preprocessing),'heldout_shap':pd.DataFrame(all_shap),'aggregate_shap':pd.DataFrame(summaries.values())}
    with engine.begin() as conn:
        for name,table in artifacts.items():persist(conn,run_id,family,name,table)
    for name in ['fold_performance','model_performance','aggregate_shap']:export(family,name+'.csv',artifacts[name])
    selected=artifacts['xgboost_tuning'].loc[artifacts['xgboost_tuning'].selected].copy()
    export(family,'selected_parameters.csv',selected)
    boundaries=[]
    for (scheme,fs),part in selected.groupby(['scheme','feature_set']):
        for parameter in SPACE:
            hits=[v[parameter] for v in part.boundary_hits]
            boundaries.append({'scheme':scheme,'feature_set':fs,'parameter':parameter,'outer_folds':len(hits),
                'minimum_hits':hits.count('minimum'),'maximum_hits':hits.count('maximum'),'boundary_fraction':sum(x!='interior' for x in hits)/len(hits)})
    export(family,'tuning_boundary_diagnostics.csv',pd.DataFrame(boundaries))
    return artifacts

def ols_inference(frame,feature_sets=None):
    rows=[];ladder=[];vifs=[]
    for fs,cols in (feature_sets if feature_sets is not None else FEATURES).items():
        fraction=float(frame[list(cols)].isna().any(axis=1).mean())
        if fraction>DESIGN['ols_material_missing_fraction']:
            raise RuntimeError(f'OLS {fs} has material missingness ({fraction:.1%}); planned MICE and pooled uncertainty require a separate specified implementation. No median-imputed inferential substitute.')
        complete=frame.dropna(subset=list(cols)+['log_price']).copy()
        prep=build_preprocessor(fs);matrix=prep.fit_transform(complete);X=sm.add_constant(np.asarray(matrix,float),has_constant='add')
        names=['Intercept',*prep.get_feature_names_out()]
        if np.linalg.matrix_rank(X)!=X.shape[1]:raise RuntimeError('OLS design is rank deficient; do not silently remove variables')
        fit=sm.OLS(complete.log_price.to_numpy(float),X).fit(cov_type='HC3');ci=fit.conf_int()
        wild=wild_cluster_bootstrap_t(X,complete.log_price.to_numpy(float),complete.analysis_area.to_numpy())
        for j,name in enumerate(names):rows.append({'feature_set':fs,'term':name,'n':len(complete),'complete_case_excluded_n':len(frame)-len(complete),
            'coefficient':float(fit.params[j]),'hc3_se':float(fit.bse[j]),'hc3_ci_low':float(ci[j,0]),'hc3_ci_high':float(ci[j,1]),'hc3_p_value':float(fit.pvalues[j]),
            **wild.iloc[j].drop('term_index').to_dict()})
        ladder.append({'feature_set':fs,'n':len(complete),'adjusted_r2':float(fit.rsquared_adj),'aic':float(fit.aic),'bic':float(fit.bic),'condition_number':float(fit.condition_number)})
        corr=np.corrcoef(matrix,rowvar=False)
        inv=np.linalg.inv(corr)
        vifs.extend({'feature_set':fs,'variable':name,'vif':float(value),'n_complete':len(complete)} for name,value in zip(names[1:],np.diag(inv)))
    return {'ols_coefficients':pd.DataFrame(rows),'ols_ladder':pd.DataFrame(ladder),'vif_diagnostics':pd.DataFrame(vifs)}

def run(engine,run_id):
    verify_income_evidence()
    with engine.connect() as conn:
        frame=load_dataset(conn);outer=saved_outer(conn,frame,schemes=['random_5','geographic_11'])
    expected=json.loads((PROJECT_ROOT/'outputs/tables/analysis_dataset/dataset_freeze.json').read_text())
    if dataset_hash(frame)!=expected['dataset_sha256']:raise RuntimeError('Analytical dataset freeze changed')
    inference=ols_inference(frame)
    with engine.begin() as conn:
        persist(conn,run_id,'validation','xgboost_candidates',load_candidates()['candidates'])
        for name,table in inference.items():persist(conn,run_id,'primary_models',name,table)
    for name,table in inference.items():export('primary_models',name+'.csv',table)
    outputs=evaluate_cv(frame,outer,engine,run_id)
    incremental,areas,bootstrap=paired_incremental(outputs['oof_predictions'])
    with engine.begin() as conn:
        for name,table in [('incremental_performance',incremental),('incremental_by_analysis_area',areas),('area_bootstrap',bootstrap)]:persist(conn,run_id,'primary_models',name,table)
    export('primary_models','incremental_performance.csv',incremental);export('primary_models','incremental_by_analysis_area.csv',areas)
    return {'n':len(frame),'outer_folds':16,'feature_sets':list(FEATURES),'candidate_count':30}
if __name__=='__main__':raise SystemExit('Use run_pipeline to establish a provenance-tracked run')
