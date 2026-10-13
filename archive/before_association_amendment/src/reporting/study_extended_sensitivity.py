"""Registered separation buffers and source-defined measurement/context checks."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once,verify_source
from src.study.specification import load_design,CITIES,MODELS
from src.study.sample_freeze import records
from src.study.validation import outer_splits,inner_splits
from src.study.modeling import fit_source,predict_source,metrics
from src.study.store import commit_package,dependencies,read_package
from src.study.context import STOCKHOLM_CODES


def buffer_training(train,test,metres):
    distance=cKDTree(test[['metric_x','metric_y']].to_numpy(float)).query(train[['metric_x','metric_y']].to_numpy(float))[0]
    return train.loc[distance>=metres].copy()


def variant_frame(conn,frame,city,scenario):
    result=frame.copy();definition={}
    if scenario.startswith('buffer_'):return result,{'buffer_m':int(scenario.split('_')[1]),'distance':'Minimum Euclidean distance from each training listing to any held-out listing in the frozen city metric CRS'}
    if scenario in {'speed_4p0','speed_5p4','continuous_decay'}:
        selected=json.loads((PROJECT_ROOT/'config/study/measurement_variant_selection.json').read_text())
        summary,_=read_package(conn,selected[city]['run_id'],city,'accessibility')
        variants=records(conn,selected,city,'accessibility','measurement_variants')
        if canonical_hash(variants)!=summary['record_sha256']:raise ValueError('Measurement variant records differ')
        result=result.merge(pd.DataFrame(variants),on='listing_id',validate='one_to_one')
        if len(result)!=len(frame):raise ValueError('Measurement sensitivity common support differs')
        for category in ('food','culture'):
            for measure in ('e','w'):
                suffix='decay' if scenario=='continuous_decay' else 'speed_'+scenario.split('_',1)[1]
                result['log1p_'+category+'_'+measure]=np.log1p(result[category+'_'+measure+'_'+suffix])
        if scenario.startswith('speed_'):
            speed=4. if scenario=='speed_4p0' else 5.4
            for concept in ('station','bus'):result['nearest_'+concept+'_walking_minutes']*=5/speed
            definition={'walking_speed_kmh':speed,'budget_minutes':10,'euclidean_radius_m':667 if speed==4 else 900}
        else:definition={'half_life_minutes':10,'includes_every_reachable_destination_in_frozen_universe':True,'arbitrary_cutoff':False}
        definition['measurement_selection']=selected[city]
    elif scenario in {'density_same_year','density_land_only'}:
        if city!='stockholm':raise ValueError('These native published denominator/vintage checks apply only to Stockholm')
        sources=json.loads((PROJECT_ROOT/'config/study/stockholm_population_sources.json').read_text())
        area=pd.read_excel(verify_source(sources['area']),header=None)
        values={}
        for code,group in STOCKHOLM_CODES.items():
            row=area.loc[area[0].eq(code)]
            if len(row)!=1:raise ValueError('Native density sensitivity unit missing/duplicated')
            row=row.iloc[0]
            if str(row[1]).replace(' - ','-').strip()!=group:raise ValueError('Native density name changed')
            denominator=float(row[4] if scenario=='density_same_year' else row[2])/100
            if denominator<=0:raise ValueError('Native density denominator unavailable')
            if scenario=='density_same_year':values[group]=float(np.log(float(row[5])/denominator))
            else:
                old=result.loc[result.operational_group.eq(group),'log_population_density'].unique()
                if len(old)!=1:raise ValueError('Frozen group density varies')
                values[group]=float(old[0]+np.log(float(row[4])/float(row[2])))
        result['log_population_density']=result.operational_group.map(values)
        definition={'source':sources['area'],'construction':'Published 2024 population / published gross area' if scenario=='density_same_year' else 'Frozen 2025 population / published native land-only area',
                    'provider_polygon_denominator_used':False,'primary_density_unchanged':True}
    else:raise ValueError('Unregistered extended sensitivity')
    return result,definition


def run(city,scenarios):
    design,cities=load_design();chosen=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text());engine=get_engine();pointers=[]
    code_hash=sha256_file(PROJECT_ROOT/'src/reporting/study_extended_sensitivity.py')
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY');original=pd.DataFrame(records(conn,chosen,city,'sample','prediction_sample'))
            frames={scenario:variant_frame(conn,original,city,scenario) for scenario in scenarios}
        for scenario,(frame,definition) in frames.items():
            for fold,tr,te in outer_splits(frame,city)['neighbourhood']:
                train,test=frame.iloc[tr],frame.iloc[te]
                if scenario.startswith('buffer_'):train=buffer_training(train,test,definition['buffer_m'])
                reason=None
                if len(train)<design['validation']['minimum_train']:reason='Buffered training support below frozen minimum500'
                else:
                    try:
                        splits=inner_splits(train)
                        if any(len(a)==0 or len(b)==0 for a,b in splits):reason='Four inner spatial folds infeasible after buffer'
                    except ValueError as exc:reason=str(exc)
                scores=[];private=[];tuning=[]
                if reason is None:
                    for estimator in ('OLS','XGBoost'):
                        for model in MODELS:
                            fit,choice=fit_source(train,model,estimator,train.log_price.to_numpy(float))
                            p=np.asarray(predict_source(fit,test,model),float);y=test.log_price.to_numpy(float)
                            scores.append({'estimator':estimator,'model':model,**metrics(y,p)})
                            tuning.append({'estimator':estimator,'model':model,'training':choice})
                            private.extend({'listing_id':str(row.listing_id),'operational_group':row.operational_group,'estimator':estimator,'model':model,
                                            'log_price':float(a),'prediction':float(b),'squared_error':float((a-b)**2),'absolute_error':float(abs(a-b))}
                                           for row,a,b in zip(test.itertuples(),y,p,strict=True))
                summary={'city':city,'scenario':scenario,'fold':str(fold),'status':'COMPLETE_FOLD' if reason is None else 'INFEASIBLE','reason':reason,
                         'n':len(frame),'test_n':len(test),'train_n':len(train),'original_train_n':len(tr),'definition':definition,
                         'metric_crs':cities[city]['metric_crs'],'prediction_hash':canonical_hash(private),'metrics':scores,'primary_sample_unchanged':True}
                with engine.begin() as conn:
                    identity=commit_package(conn,city=city,family='robustness',summary=summary,records={'predictions':private,'tuning':tuning},
                                            deps=dependencies({'sample':chosen[city],'scenario_code_sha256':code_hash}))
                pointers.append({'run_id':identity,'scenario':scenario,'fold':str(fold),'status':summary['status'],'summary_sha256':canonical_hash(summary)})
                print(city,scenario,fold,summary['status'],len(train),flush=True)
        name='extended_'+'_'.join(scenarios)+'_selection.json'
        write_once(PROJECT_ROOT/'runs'/city/name,(json.dumps(pointers,indent=2)+'\n').encode())
    finally:engine.dispose()
    return pointers


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--city',required=True,choices=CITIES);parser.add_argument('--scenarios',required=True,nargs='+')
    args=parser.parse_args();run(args.city,args.scenarios)
