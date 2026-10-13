"""Prespecified common-row sensitivity experiments; infeasible support is explicit."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sqlalchemy import text
from shapely.geometry import shape,LineString
from shapely.ops import transform,unary_union
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,CITIES,MODELS
from src.study.sample_freeze import records
from src.study.store import commit_package,dependencies,read_package
from src.study.validation import outer_splits,inner_splits
from src.study.modeling import fit_source,predict_source,metrics
from src.study.geography import metric_transform


def scenario_frame(frame,scenario,city,conn):
    design,_=load_design();result=frame.copy()
    if scenario=='apartment_condo':result=result.loc[result.property_type.isin(['Entire rental unit','Entire condo'])].copy()
    elif scenario=='reviewed_only':result=result.loc[result.number_of_reviews>0].copy()
    elif scenario in {'walking_15','walking_20'}:
        minutes=int(scenario.split('_')[1])
        for category in ('food','culture'):
            for measure in ('e','w'):result['log1p_'+category+'_'+measure]=np.log1p(result[f'{category}_{measure}_{minutes}'])
    elif scenario=='boundary_far':
        selected=json.loads((PROJECT_ROOT/'config/study/geography_selection.json').read_text())[city]
        geo=conn.scalar(text("SELECT ST_AsGeoJSON(geom,15) FROM study.geometries WHERE run_id=:run AND city=:city AND geometry_key='mask'"),
                        {'run':selected['run_id'],'city':city})
        mask=transform(metric_transform(load_design()[1][city]['metric_crs']),shape(json.loads(geo)))
        pieces=list(mask.geoms) if mask.geom_type=='MultiPolygon' else [mask]
        outer=unary_union([LineString(p.exterior.coords) for p in pieces])
        from shapely.geometry import Point
        keep=np.array([outer.distance(Point(x,y))>150 for x,y in result[['metric_x','metric_y']].to_numpy(float)])
        result=result.loc[keep].copy()
    else:raise ValueError('Unknown registered scenario')
    return result.reset_index(drop=True)


def run(city,scenarios=('apartment_condo','reviewed_only','walking_15','walking_20','boundary_far')):
    design,_=load_design();selection=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text())
    engine=get_engine();pointers=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            original=pd.DataFrame(records(conn,selection,city,'sample','prediction_sample'))
            frames={scenario:scenario_frame(original,scenario,city,conn) for scenario in scenarios}
        for scenario,frame in frames.items():
            try:folds=outer_splits(frame,city)['neighbourhood']
            except ValueError as exc:
                summary={'city':city,'scenario':scenario,'status':'INFEASIBLE','reason':str(exc),'n':len(frame),'primary_sample_unchanged':True}
                with engine.begin() as conn:
                    identity=commit_package(conn,city=city,family='robustness',summary=summary,
                                            deps=dependencies({'sample':selection[city],'scenario_code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_robustness.py')}))
                pointers.append({'run_id':identity,'scenario':scenario,'status':'INFEASIBLE','summary_sha256':canonical_hash(summary)})
                print(city,scenario,'INFEASIBLE',str(exc),flush=True);continue
            for fold,tr,te in folds:
                train,test=frame.iloc[tr],frame.iloc[te];private=[];scores=[];tuning=[]
                for estimator in ('OLS','XGBoost'):
                    for model in MODELS:
                        fit,choice=fit_source(train,model,estimator,train.log_price.to_numpy(float))
                        p=np.asarray(predict_source(fit,test,model),float);y=test.log_price.to_numpy(float)
                        scores.append({'estimator':estimator,'model':model,**metrics(y,p)})
                        tuning.append({'estimator':estimator,'model':model,'source_training':choice})
                        private.extend({'listing_id':str(row.listing_id),'operational_group':row.operational_group,'estimator':estimator,'model':model,
                                        'log_price':float(observed),'prediction':float(predicted),'squared_error':float((observed-predicted)**2),
                                        'absolute_error':float(abs(observed-predicted))} for row,observed,predicted in zip(test.itertuples(),y,p,strict=True))
                summary={'city':city,'scenario':scenario,'status':'COMPLETE_FOLD','fold':str(fold),'n':len(frame),'test_n':len(te),'train_n':len(tr),
                         'metrics':scores,'prediction_hash':canonical_hash(private),'primary_sample_unchanged':True}
                with engine.begin() as conn:
                    identity=commit_package(conn,city=city,family='robustness',summary=summary,records={'predictions':private,'tuning':tuning},
                                            deps=dependencies({'sample':selection[city],'scenario_code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_robustness.py')}))
                pointers.append({'run_id':identity,'scenario':scenario,'status':'COMPLETE_FOLD','fold':str(fold),'summary_sha256':canonical_hash(summary)})
                print(city,scenario,fold,'COMPLETE_FOLD',flush=True)
        write_once(PROJECT_ROOT/'runs'/city/'robustness_selection.json',(json.dumps(pointers,indent=2)+'\n').encode())
    finally:engine.dispose()
    return pointers


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--city',required=True,choices=CITIES)
    args=parser.parse_args();run(args.city)
