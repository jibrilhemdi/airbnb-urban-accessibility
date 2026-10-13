"""Independent metrics and paired geographic stability from saved predictions."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,CITIES,MODELS
from src.study.store import read_package,commit_package,dependencies
from src.study.modeling import metrics


def paired(part,added,reference,replications,seed,outcome):
    a=part.loc[part.model==added];b=part.loc[part.model==reference]
    paired=a.merge(b,on=['listing_id','operational_group'],suffixes=('_a','_b'),validate='one_to_one')
    if len(paired)!=len(a) or len(paired)!=len(b) or not np.array_equal(paired[outcome+'_a'],paired[outcome+'_b']):raise ValueError('Paired target observations/outcomes differ')
    loss_a=(paired[outcome+'_a']-paired.prediction_a)**2;loss_b=(paired[outcome+'_b']-paired.prediction_b)**2
    losses=pd.DataFrame({'group':paired.operational_group,'a':loss_a,'b':loss_b})
    groups=losses.groupby('group').agg(n=('a','size'),a=('a','sum'),b=('b','sum')).sort_index()
    draws=np.random.default_rng(seed).integers(0,len(groups),size=(replications,len(groups)))
    count=groups.n.to_numpy()[draws].sum(axis=1)
    delta=np.sqrt(groups.a.to_numpy()[draws].sum(axis=1)/count)-np.sqrt(groups.b.to_numpy()[draws].sum(axis=1)/count)
    base=float(np.sqrt(loss_b.mean()));candidate=float(np.sqrt(loss_a.mean()))
    return {'added':added,'reference':reference,'n':len(paired),'delta_rmse':candidate-base,
            'proportional_change':(candidate-base)/base,'stability_low':float(np.quantile(delta,.025)),
            'stability_high':float(np.quantile(delta,.975)),'resampling_groups':len(groups),'replications':replications,
            'interpretation':'Geographic composition stability; overlapping training sets and spatial dependence remain'}


def predictions(conn,identity,city,family):
    summary,_=read_package(conn,identity,city,family)
    rows=conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city AND family=:family "
                           "AND artifact='predictions' ORDER BY record_key::integer"),{'run':identity,'city':city,'family':family}).scalars().all()
    if canonical_hash(rows)!=summary['prediction_hash']:raise ValueError('Saved prediction hash differs')
    frame=pd.DataFrame(rows)
    outcome='log_price' if family=='within_city' else 'relative_log_price'
    expected=(frame[outcome]-frame.prediction)**2
    if not np.allclose(frame.squared_error,expected,atol=1e-12,rtol=1e-12):raise ValueError('Saved squared losses do not recalculate')
    if not np.allclose(frame.absolute_error,abs(frame[outcome]-frame.prediction),atol=1e-12,rtol=1e-12):raise ValueError('Saved absolute losses do not recalculate')
    return summary,frame


def within_tables(scheme='neighbourhood'):
    design,_=load_design();engine=get_engine();table=[];contrast=[];pointers={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                path=PROJECT_ROOT/'runs'/city/('within_city_'+scheme+'_selection.json')
                selections=json.loads(path.read_text());parts=[]
                for chosen in selections:
                    summary,frame=predictions(conn,chosen['run_id'],city,'within_city')
                    if canonical_hash(summary)!=chosen['summary_sha256'] or summary['scheme']!=scheme:raise ValueError('Selected fold identity differs')
                    for fit in summary['fitted_models']:
                        if sha256_file(PROJECT_ROOT/fit['path'])!=fit['sha256']:raise ValueError('Private fitted model bytes changed')
                    parts.append(frame)
                pooled=pd.concat(parts,ignore_index=True)
                keys=None
                for (estimator,model),part in pooled.groupby(['estimator','model']):
                    if part.listing_id.duplicated().any():raise ValueError('OOF observations repeated')
                    ids=set(part.listing_id)
                    if keys is not None and ids!=keys:raise ValueError('Four models differ in held-out rows')
                    keys=ids;table.append({'city':city,'scheme':scheme,'estimator':estimator,'model':model,**metrics(part.log_price,part.prediction)})
                for estimator,part in pooled.groupby('estimator'):
                    for a,b in design['contrasts']:
                        contrast.append({'city':city,'scheme':scheme,'estimator':estimator,
                                         **paired(part,a,b,design['group_bootstrap_replications'],design['validation']['random_seed'],'log_price')})
        with engine.begin() as conn:
            for city in CITIES:
                summary={'city':city,'status':'VERIFIED_WITHIN_CITY_RESULTS','scheme':scheme,
                         'performance':[r for r in table if r['city']==city],'contrasts':[r for r in contrast if r['city']==city],
                         'independent_metric_recalculation':'PASS','four_models_identical_rows':'PASS'}
                identity=commit_package(conn,city=city,family='reporting',summary=summary,
                                        deps=dependencies({'reporter_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_results.py')}))
                pointers[city]={'run_id':identity,'summary_sha256':canonical_hash(summary)}
        directory=PROJECT_ROOT/'outputs/metrics'/scheme
        directory.mkdir(parents=True,exist_ok=True)
        write_once(directory/'performance.csv',pd.DataFrame(table).to_csv(index=False).encode())
        write_once(directory/'paired_contrasts.csv',pd.DataFrame(contrast).to_csv(index=False).encode())
        write_once(PROJECT_ROOT/'config/study'/('results_'+scheme+'.json'),(json.dumps(pointers,indent=2)+'\n').encode())
        return table,contrast
    finally:engine.dispose()


def transfer_tables():
    design,_=load_design();selections=json.loads((PROJECT_ROOT/'runs/transfer/selection.json').read_text())
    engine=get_engine();table=[];contrast=[];frames={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for chosen in selections:
                summary,frame=predictions(conn,chosen['run_id'],chosen['city'],'transfer')
                if canonical_hash(summary)!=chosen['summary_sha256'] or summary['target_fit'] or summary['target_tuning']:raise ValueError('Transfer identity/leakage flag differs')
                frame['model']=chosen['model'];key=(chosen['city'],chosen['target_city'],chosen['estimator'])
                frames.setdefault(key,[]).append(frame)
                value=metrics(frame.relative_log_price,frame.prediction)
                if value!=summary['metrics']:raise ValueError('Independent transfer metric differs')
                table.append({'source_city':chosen['city'],'target_city':chosen['target_city'],'estimator':chosen['estimator'],'model':chosen['model'],**value})
            for (source,target,estimator),parts in frames.items():
                part=pd.concat(parts,ignore_index=True)
                if set(part.model)!=set(MODELS):raise ValueError('Incomplete directional model ladder')
                for a,b in design['contrasts']:
                    contrast.append({'source_city':source,'target_city':target,'estimator':estimator,
                                     **paired(part,a,b,design['group_bootstrap_replications'],design['validation']['random_seed'],'relative_log_price')})
        if len(table)!=48:raise ValueError('Exactly six directions × four models × two estimators required')
        pointers={}
        with engine.begin() as conn:
            for source in CITIES:
                summary={'city':source,'status':'VERIFIED_TRANSFER_RESULTS','performance':[r for r in table if r['source_city']==source],
                         'contrasts':[r for r in contrast if r['source_city']==source],'independent_metric_recalculation':'PASS',
                         'outcome':'Frozen city-relative log asking price; not absolute unseen-city price deployment'}
                identity=commit_package(conn,city=source,family='reporting',summary=summary,
                                        deps=dependencies({'reporter_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_results.py')}))
                pointers[source]={'run_id':identity,'summary_sha256':canonical_hash(summary)}
        directory=PROJECT_ROOT/'outputs/metrics/transfer';directory.mkdir(parents=True,exist_ok=True)
        write_once(directory/'performance.csv',pd.DataFrame(table).to_csv(index=False).encode())
        write_once(directory/'paired_contrasts.csv',pd.DataFrame(contrast).to_csv(index=False).encode())
        write_once(PROJECT_ROOT/'config/study/results_transfer.json',(json.dumps(pointers,indent=2)+'\n').encode())
        return table,contrast
    finally:engine.dispose()
