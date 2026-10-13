"""Independent sensitivity metrics and exhaustive, explicit completion registry."""
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
from src.reporting.study_results import paired
from src.study.modeling import metrics

SCENARIOS=['apartment_condo','reviewed_only','walking_15','walking_20','boundary_far','training_price_tail','reputation',
           'buffer_500','buffer_1000','speed_4p0','speed_5p4','continuous_decay','density_same_year','density_land_only']


def audit_scenario(conn,city,scenario,chosen,design):
    parts=[];folds=[]
    for selection in chosen:
        summary,_=read_package(conn,selection['run_id'],city,'robustness')
        if canonical_hash(summary)!=selection['summary_sha256'] or summary['scenario']!=scenario:raise ValueError('Sensitivity selection identity differs')
        folds.append({k:summary.get(k) for k in ['fold','status','reason','n','train_n','test_n','original_train_n']})
        if summary['status']=='INFEASIBLE':continue
        rows=conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city AND family='robustness' "
                               "AND artifact='predictions' ORDER BY record_key::integer"),{'run':selection['run_id'],'city':city}).scalars().all()
        if canonical_hash(rows)!=summary['prediction_hash']:raise ValueError('Sensitivity prediction hash differs')
        frame=pd.DataFrame(rows)
        if not np.allclose(frame.squared_error,(frame.log_price-frame.prediction)**2,rtol=1e-12,atol=1e-12):raise ValueError('Sensitivity squared losses differ')
        if not np.allclose(frame.absolute_error,abs(frame.log_price-frame.prediction),rtol=1e-12,atol=1e-12):raise ValueError('Sensitivity absolute losses differ')
        for score in summary['metrics']:
            part=frame.loc[(frame.estimator==score['estimator'])&(frame.model==score['model'])]
            recalculated=metrics(part.log_price,part.prediction)
            if any(score[k]!=v for k,v in recalculated.items()):raise ValueError('Independent sensitivity fold metric differs')
        parts.append(frame)
    if not parts:return {'city':city,'scenario':scenario,'status':'INFEASIBLE','folds':folds,'performance':[],'contrasts':[]}
    if any(f['status']=='INFEASIBLE' for f in folds):
        return {'city':city,'scenario':scenario,'status':'PARTIAL_INFEASIBLE','folds':folds,'performance':[],
                'reason':'At least one registered neighbourhood holdout violates fixed support; no pooled partial score presented','contrasts':[]}
    if len(folds)!=load_design()[1][city]['operational_count']:raise ValueError('Sensitivity lacks every registered neighbourhood fold')
    pooled=pd.concat(parts,ignore_index=True);performance=[];contrasts=[];ids=None
    for (estimator,model),part in pooled.groupby(['estimator','model']):
        if part.listing_id.duplicated().any():raise ValueError('Repeated sensitivity held-out listing')
        keys=set(part.listing_id)
        if ids is not None and keys!=ids:raise ValueError('Sensitivity four-model rows differ')
        ids=keys;performance.append({'city':city,'scenario':scenario,'estimator':estimator,'model':model,**metrics(part.log_price,part.prediction)})
    if len(performance)!=8:raise ValueError('Sensitivity estimator/model ladder incomplete')
    for estimator,part in pooled.groupby('estimator'):
        for added,reference in design['contrasts']:
            contrasts.append({'city':city,'scenario':scenario,'estimator':estimator,
                              **paired(part,added,reference,design['group_bootstrap_replications'],design['validation']['random_seed'],'log_price')})
    return {'city':city,'scenario':scenario,'status':'COMPLETE','folds':folds,'performance':performance,'contrasts':contrasts,
            'independent_saved_prediction_metric_recalculation':'PASS','four_models_identical_heldout_rows':'PASS'}


def run():
    design,_=load_design();engine=get_engine();registry=[];performance=[];contrasts=[];pointers={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                chosen=[]
                for pattern in ('robustness_selection.json','training_sensitivity_selection.json','extended_*_selection.json'):
                    for path in sorted((PROJECT_ROOT/'runs'/city).glob(pattern)):chosen.extend(json.loads(path.read_text()))
                for scenario in SCENARIOS:
                    selections=[s for s in chosen if s['scenario']==scenario]
                    if city!='stockholm' and scenario.startswith('density_'):
                        registry.append({'city':city,'scenario':scenario,'status':'NOT_APPLICABLE',
                                         'reason':'Native matching gross-area density is qualified without Stockholm published-vintage/land-denominator discrepancy; no fabricated alternate denominator'})
                        continue
                    if not selections:raise ValueError('Required sensitivity incomplete: '+city+' '+scenario)
                    result=audit_scenario(conn,city,scenario,selections,design)
                    performance.extend(result.pop('performance'));contrasts.extend(result.pop('contrasts'));registry.append(result)
        samples=json.loads((PROJECT_ROOT/'docs/analysis/sample_audit.json').read_text())
        spatial=json.loads((PROJECT_ROOT/'docs/analysis/spatial_audit.json').read_text())
        for city in CITIES:
            groups=samples[city]['sample']['group_counts']
            registry.append({'city':city,'scenario':'former_support_threshold','status':'COMPLETE','minimum_group_n':min(groups.values()),
                             'all_groups_meet_former_30':all(n>=30 for n in groups.values()),'primary_threshold_unchanged':15})
            registry.append({'city':city,'scenario':'missing_price_audit','status':'COMPLETE','sample_flow':samples[city]['sample']['sample_flow'],
                             'outcome_imputed':False,'reference_sample_before_feature_filtering':True})
            registry.append({'city':city,'scenario':'area_fixed_effects','status':spatial[city]['fixed_effect_status'],
                             'reason':'Area-constant density absorbed; adjusted associations only'})
            registry.append({'city':city,'scenario':'spatial_error','status':spatial[city]['spatial_error_status'],'trigger':spatial[city]['trigger']})
        schemes=['random']+[f'blocks_{size}m_origin_{origin}' for size in (1000,1500,2000) for origin in ('0_0','0p5_0p5')]
        for scheme in schemes:
            selected=json.loads((PROJECT_ROOT/'config/study'/('results_'+scheme+'.json')).read_text())
            for city in CITIES:
                with engine.connect() as conn:
                    summary,_=read_package(conn,selected[city]['run_id'],city,'reporting')
                    if summary['independent_metric_recalculation']!='PASS':raise ValueError('Geometric/random metrics lack independent verification')
                registry.append({'city':city,'scenario':scheme,'status':'COMPLETE','results':selected[city]})
        for city in CITIES:
            city_registry=[r for r in registry if r['city']==city]
            complete=all(r['status'] in {'COMPLETE','NOT_APPLICABLE','NOT_APPLICABLE_TRIGGER_NOT_MET'} for r in city_registry)
            summary={'city':city,'status':'ROBUSTNESS_COMPLETE' if complete else 'ROBUSTNESS_ACCOUNTED_WITH_DOCUMENTED_SCIENTIFIC_BLOCKERS','registry':city_registry,
                     'performance':[r for r in performance if r['city']==city],'contrasts':[r for r in contrasts if r['city']==city]}
            with engine.begin() as conn:
                identity=commit_package(conn,city=city,family='reporting',summary=summary,
                                        deps=dependencies({'reporter_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_robustness_results.py')}))
            pointers[city]={'run_id':identity,'summary_sha256':canonical_hash(summary)}
        out=PROJECT_ROOT/'outputs/metrics/robustness';out.mkdir(parents=True,exist_ok=True)
        for name,data in [('performance.csv',performance),('paired_contrasts.csv',contrasts)]:
            content=pd.DataFrame(data).to_csv(index=False).encode();path=out/name
            if path.exists():
                if path.read_bytes()!=content:raise ValueError('Completed predictive robustness metrics changed')
            else:write_once(path,content)
        write_once(PROJECT_ROOT/'config/study/robustness_results_selection.json',(json.dumps(pointers,indent=2)+'\n').encode())
        write_once(PROJECT_ROOT/'docs/analysis/robustness_audit.json',(json.dumps(registry,indent=2,ensure_ascii=False)+'\n').encode())
        return {'registry_rows':len(registry),'performance_rows':len(performance),'contrast_rows':len(contrasts)}
    finally:engine.dispose()


if __name__=='__main__':print(json.dumps(run(),indent=2))
