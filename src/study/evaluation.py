"""Fresh empirical fits and immutable fold/direction packages after pre-fit gates."""
from __future__ import annotations
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,CITIES,MODELS
from src.study.store import commit_package,dependencies,read_package
from src.study.modeling import fit_source,predict_source,metrics,transfer
from src.study.validation import outer_splits,inner_splits
from src.study.sample_freeze import records


def prefit(conn):
    design,cities=load_design()
    required=['geography','context','accessibility','reference','sample','validation']
    selections={family:json.loads((PROJECT_ROOT/f'config/study/{family}_selection.json').read_text()) for family in required}
    result={};frames={}
    for city in CITIES:
        result[city]={}
        for family in required:
            if city not in selections[family]:raise ValueError('BLOCKED missing '+family+' for '+city)
            selection=selections[family][city]
            summary,dep=read_package(conn,selection['run_id'],city,family)
            if canonical_hash(summary)!=selection['summary_sha256']:raise ValueError('Frozen upstream summary mismatch')
            result[city][family]=selection
        sample,_=read_package(conn,selections['sample'][city]['run_id'],city,'sample')
        if sample['primary_fold_status']!='QUALIFIED':raise ValueError('BLOCKED city fold support: '+city)
        result[city]['association_inference_status']=sample['association_inference_status']
        result[city]['association_missing_fraction']=sample['association_missing_fraction']
        if not sample['all_models_same_rows'] or sample['outcome_imputed']:raise ValueError('Invalid sample/observed outcome')
        frame=pd.DataFrame(records(conn,selections['sample'],city,'sample','prediction_sample'))
        if canonical_hash(json_records(frame))!=sample['record_sha256']:raise ValueError('Frozen sample records differ')
        frames[city]=frame
        folds=outer_splits(frame,city)
        outer=records(conn,selections['validation'],city,'validation','outer_test')
        inner=records(conn,selections['validation'],city,'validation','inner_validation')
        validation,_=read_package(conn,selections['validation'][city]['run_id'],city,'validation')
        if canonical_hash(outer)!=validation['outer_hash'] or canonical_hash(inner)!=validation['inner_hash']:raise ValueError('Saved fold records changed')
        expected_outer=[];expected_inner=[];ids=frame.listing_id.to_numpy()
        for scheme,parts in folds.items():
            for fold,tr,te in parts:
                expected_outer.extend({'listing_id':str(ids[i]),'scheme':scheme,'outer_test_fold':str(fold)} for i in te)
                for f,(_,val) in enumerate(inner_splits(frame.iloc[tr]),1):
                    expected_inner.extend({'listing_id':str(ids[tr[i]]),'scheme':scheme,'outer_fold':str(fold),'inner_validation_fold':f} for i in val)
        if outer!=expected_outer or inner!=expected_inner:raise ValueError('Saved outcome-blind membership recomputation differs')
    return frames,selections,{'status':'READY_PREDICTIVE_WITH_DOCUMENTED_ASSOCIATION_GATES','design_id':design['design_id'],'cities':result,'candidate_file_sha256':design['candidates']['file_sha256'],
                              'source_snapshot':design['accessibility']['preferred_osm_timestamp'],'income_required':False,'housing_required':False,
                              'models_fitted_at_freeze':False,'sample_and_fold_membership_verified':True}


def freeze_prefit():
    engine=get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY');_,_,report=prefit(conn)
        write_once(PROJECT_ROOT/'docs/analysis/prefit_freeze.json',(json.dumps(report,indent=2)+'\n').encode())
    finally:engine.dispose()
    return report


def run_within_city(city,schemes=None):
    engine=get_engine();selected=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY');frames,selections,certificate=prefit(conn)
        if not (PROJECT_ROOT/'docs/analysis/prefit_freeze.json').exists():raise ValueError('Pre-fit report must be frozen before any empirical fit')
        if json.loads((PROJECT_ROOT/'docs/analysis/prefit_freeze.json').read_text())!=certificate:raise ValueError('Pre-fit certificate changed')
        frame=frames[city];folds=outer_splits(frame,city);all_results=[]
        for scheme,parts in folds.items():
            if schemes is not None and scheme not in schemes:continue
            for fold,tr,te in parts:
                train,test=frame.iloc[tr],frame.iloc[te];private=[];tuning=[];fold_metrics=[]
                for estimator in ('OLS','XGBoost'):
                    for model in MODELS:
                        fit,choice=fit_source(train,model,estimator,train.log_price.to_numpy(float))
                        p=np.asarray(predict_source(fit,test,model),float);y=test.log_price.to_numpy(float)
                        record={'scheme':scheme,'fold':str(fold),'estimator':estimator,'model':model,'train_n':len(tr),**metrics(y,p)}
                        fold_metrics.append(record);tuning.append({**record,'training':choice})
                        private.extend({'listing_id':str(row.listing_id),'operational_group':row.operational_group,
                                        'scheme':scheme,'fold':str(fold),'estimator':estimator,'model':model,
                                        'log_price':float(observed),'prediction':float(predicted),'squared_error':float((observed-predicted)**2),
                                        'absolute_error':float(abs(observed-predicted))} for row,observed,predicted in zip(test.itertuples(),y,p,strict=True))
                        print(city,scheme,fold,estimator,model,record['rmse'],flush=True)
                summary={'city':city,'status':'COMPLETE_FOLD','scheme':scheme,'fold':str(fold),'metrics':fold_metrics,
                         'prediction_hash':canonical_hash(private),'prediction_n':len(private),'train_n':len(tr),'test_n':len(te),'historical_fit_reused':False}
                with engine.begin() as conn:
                    identity=commit_package(conn,city=city,family='within_city',summary=summary,
                                            records={'predictions':private,'tuning':tuning},deps=dependencies({'prefit':certificate,'sample':selections['sample'][city],'validation':selections['validation'][city]}))
                selected.append({'run_id':identity,'summary_sha256':canonical_hash(summary),'scheme':scheme,'fold':str(fold)})
        directory=PROJECT_ROOT/'runs'/city
        write_once(directory/'within_city_selection.json',(json.dumps(selected,indent=2)+'\n').encode())
    finally:engine.dispose()
    return selected


def run_transfer():
    engine=get_engine();selected=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY');frames,selections,certificate=prefit(conn)
            reference={c:read_package(conn,selections['reference'][c]['run_id'],c,'reference')[0]['mean_log_price'] for c in CITIES}
        if json.loads((PROJECT_ROOT/'docs/analysis/prefit_freeze.json').read_text())!=certificate:raise ValueError('Pre-fit certificate changed')
        for source in CITIES:
            for estimator in ('OLS','XGBoost'):
                for model in MODELS:
                    train=frames[source]
                    fit,choice=fit_source(train,model,estimator,train.log_price.to_numpy(float)-reference[source])
                    # Both directions out of this source use the same fresh source
                    # fit and tuning, with separate target evaluation identities.
                    for target in CITIES:
                        if target==source:continue
                        test=frames[target];p=np.asarray(predict_source(fit,test,model),float)
                        y=test.log_price.to_numpy(float)-reference[target]
                        private=[{'listing_id':str(row.listing_id),'operational_group':row.operational_group,'relative_log_price':float(observed),
                                  'prediction':float(predicted),'squared_error':float((observed-predicted)**2),'absolute_error':float(abs(observed-predicted))}
                                 for row,observed,predicted in zip(test.itertuples(),y,p,strict=True)]
                        summary={'city':source,'status':'COMPLETE_DIRECTION_MODEL','source_city':source,'target_city':target,'estimator':estimator,'model':model,
                                 'source_n':len(train),'source_mean_log_price':reference[source],'target_mean_log_price':reference[target],
                                 'metrics':metrics(y,p),'prediction_hash':canonical_hash(private),'tuning':choice,'target_fit':False,'target_tuning':False,
                                 'target_intercept_recalibration':False,'historical_fit_reused':False}
                        with engine.begin() as conn:
                            identity=commit_package(conn,city=source,family='transfer',summary=summary,records={'predictions':private},
                                                    deps=dependencies({'prefit':certificate,'source_sample':selections['sample'][source],
                                                       'target_sample':selections['sample'][target],'references':selections['reference']}))
                        selected.append({'run_id':identity,'city':source,'target_city':target,'estimator':estimator,'model':model,'summary_sha256':canonical_hash(summary)})
                        print(source,'to',target,estimator,model,summary['metrics']['rmse'],flush=True)
        write_once(PROJECT_ROOT/'runs/transfer/selection.json',(json.dumps(selected,indent=2)+'\n').encode())
    finally:engine.dispose()
    return selected
