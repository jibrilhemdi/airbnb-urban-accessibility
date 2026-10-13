"""Prespecified Moran and bounded spatial-error/fixed-effect association checks."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from libpysal.weights import KNN
from spreg import GM_Error_Het
from src.spatial.spatial_diagnostics import moran_knn
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,CITIES,MODELS
from src.study.store import commit_package,dependencies,read_package
from src.study.sample_freeze import records
from src.reporting.study_results import predictions
from src.study.association import qualify


def run():
    design,cities=load_design();chosen=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text())
    engine=get_engine();public={};pointers={}
    try:
        for city in CITIES:
            with engine.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                frame=pd.DataFrame(records(conn,chosen,city,'sample','prediction_sample'))
                association=pd.DataFrame(records(conn,chosen,city,'sample','association_sample'))
                association,eligibility=qualify(frame,association,design)
                sample,_=read_package(conn,chosen[city]['run_id'],city,'sample')
                selected=json.loads((PROJECT_ROOT/'runs'/city/'within_city_neighbourhood_selection.json').read_text())
                parts=[predictions(conn,s['run_id'],city,'within_city')[1] for s in selected]
            pooled=pd.concat(parts,ignore_index=True)
            xy=frame[['metric_x','metric_y']].to_numpy(float)
            diagnostics=[{'variable':'log_price','estimator':'none','model':'none',**moran_knn(frame.log_price.to_numpy(float),xy,seed=design['validation']['random_seed'])}]
            for estimator in ('OLS','XGBoost'):
                for model in ('M0','MW'):
                    part=pooled.loc[(pooled.estimator==estimator)&(pooled.model==model)]
                    joined=part.merge(frame[['listing_id','metric_x','metric_y']],on='listing_id',validate='one_to_one')
                    if len(joined)!=len(frame):raise ValueError('Spatial residual coordinate join dropped rows')
                    diagnostics.append({'variable':'oof_residual','estimator':estimator,'model':model,
                                        **moran_knn((joined.log_price-joined.prediction).to_numpy(float),joined[['metric_x','metric_y']].to_numpy(float),seed=design['validation']['random_seed'])})
            ols_mw=[d for d in diagnostics if d['estimator']=='OLS' and d['model']=='MW'][0]
            triggered=abs(ols_mw['moran_i'])>.05 and ols_mw['permutation_p_two_sided']<.05
            coefficients=[];fixed=[]
            blocked=eligibility['eligibility']!='PASS'
            spatial_status='BLOCKED_ASSOCIATION_MISSINGNESS' if triggered and blocked else 'NOT_APPLICABLE_TRIGGER_NOT_MET' if not triggered else 'COMPLETE'
            if triggered and not blocked:
                features=design['models']['MW'];numeric=[f for f in features if f!='property_type']
                cats=pd.get_dummies(association[['property_type']],drop_first=True,dtype=float)
                matrix=np.column_stack([association[numeric].to_numpy(float),cats.to_numpy(float)])
                weights=KNN.from_array(association[['metric_x','metric_y']].to_numpy(float),k=8);weights.transform='R'
                fit=GM_Error_Het(association.log_price.to_numpy(float).reshape(-1,1),matrix,w=weights,name_x=[*numeric,*cats.columns],name_y='log_price')
                coefficients=[{'term':name,'coefficient':float(beta),'standard_error':float(se),'n':len(association),'scope':'Spatial-error adjusted association'}
                              for name,beta,se in zip(fit.name_x,np.asarray(fit.betas).ravel(),np.asarray(fit.std_err).ravel(),strict=True)]
            if not blocked:
                for model in MODELS:
                    numeric=[f for f in design['models'][model] if f not in {'property_type','log_population_density'}]
                    cats=pd.get_dummies(association[['property_type','operational_group']],drop_first=True,dtype=float)
                    X=np.column_stack([np.ones(len(association)),association[numeric].to_numpy(float),cats.to_numpy(float)])
                    if np.linalg.matrix_rank(X)!=X.shape[1]:raise ValueError('Fixed-effect association is not identified')
                    fit=sm.OLS(association.log_price.to_numpy(float),X).fit(cov_type='HC3');ci=fit.conf_int()
                    fixed.extend({'model':model,'term':name,'coefficient':float(fit.params[i]),'hc3_se':float(fit.bse[i]),
                                  'hc3_ci_low':float(ci[i,0]),'hc3_ci_high':float(ci[i,1]),'n':len(association),
                                  'scope':'Within-operational-area adjusted association; area-constant density absorbed'}
                                 for i,name in enumerate(['Intercept',*numeric,*cats.columns]))
            summary={'city':city,'status':'SPATIAL_DIAGNOSTICS_COMPLETE','metric_crs':cities[city]['metric_crs'],'moran':diagnostics,**eligibility,
                     'absorbed_area_constant_predictors':['log_population_density'],
                     'spatial_error_status':spatial_status,'fixed_effect_status':'BLOCKED_ASSOCIATION_MISSINGNESS' if blocked else 'COMPLETE',
                     'trigger':'OLS MW neighbourhood OOF residual |I|>.05 and two-sided permutation p<.05; no causal interpretation'}
            with engine.begin() as conn:
                identity=commit_package(conn,city=city,family='reporting',summary=summary,
                                        records={'spatial_error':coefficients,'area_fixed_effects':fixed},
                                        deps=dependencies({'sample':chosen[city],'spatial_code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_spatial.py')}))
            public[city]=summary;pointers[city]={'run_id':identity,'summary_sha256':canonical_hash(summary)}
            print(city,spatial_status,summary['fixed_effect_status'],flush=True)
        write_once(PROJECT_ROOT/'config/study/spatial_diagnostic_selection.json',(json.dumps(pointers,indent=2)+'\n').encode())
        write_once(PROJECT_ROOT/'docs/analysis/spatial_audit.json',(json.dumps(public,indent=2,ensure_ascii=False)+'\n').encode())
    finally:engine.dispose()
    return public


if __name__=='__main__':run()
