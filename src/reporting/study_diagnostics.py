"""Common-sample association and spatial diagnostics without inferential imputation."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.preprocessing import OneHotEncoder
from statsmodels.stats.outliers_influence import variance_inflation_factor
from src.pipeline.inference import wild_cluster_bootstrap_t
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,CITIES,MODELS
from src.study.store import commit_package,dependencies,read_package
from src.study.sample_freeze import records
from src.study.association import qualify
from src.spatial.spatial_diagnostics import moran_knn


def association():
    design,_=load_design();selected=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text())
    engine=get_engine();public={};pointers={}
    try:
        for city in CITIES:
            with engine.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                summary,_=read_package(conn,selected[city]['run_id'],city,'sample')
                prediction=pd.DataFrame(records(conn,selected,city,'sample','prediction_sample'))
                saved=pd.DataFrame(records(conn,selected,city,'sample','association_sample'))
                frame,eligibility=qualify(prediction,saved,design)
            output={};rows=[];fits=[];vif=[];private=[]
            if eligibility['eligibility']!='PASS':
                output={'city':city,'status':'BLOCKED_MATERIAL_MISSINGNESS',**eligibility,
                        'reason':'Union required-predictor missingness exceeds active eligibility limit; no inferential imputation',
                        'association_n':len(frame),'coefficients_produced':False}
            else:
                for model in MODELS:
                    features=design['models'][model];numeric=[f for f in features if f!='property_type']
                    matrix=frame[numeric].to_numpy(float)
                    encoder=OneHotEncoder(drop='first',handle_unknown='ignore',sparse_output=False)
                    categorical=encoder.fit_transform(frame[['property_type']])
                    names=['Intercept',*numeric,*encoder.get_feature_names_out(['property_type'])]
                    X=np.column_stack([np.ones(len(frame)),matrix,categorical]);y=frame.log_price.to_numpy(float)
                    if not np.isfinite(X).all() or np.linalg.matrix_rank(X)!=X.shape[1]:raise ValueError('Association rank/nonfinite failure; no silent variable removal')
                    fit=sm.OLS(y,X).fit(cov_type='HC3');ci=fit.conf_int()
                    wild=wild_cluster_bootstrap_t(X,y,frame.operational_group.to_numpy(),replications=design['wild_cluster_replications'],seed=design['validation']['random_seed'])
                    rows.extend({'model':model,'term':name,'n':len(frame),'coefficient':float(fit.params[i]),'hc3_se':float(fit.bse[i]),
                                 'hc3_ci_low':float(ci[i,0]),'hc3_ci_high':float(ci[i,1]),'hc3_p':float(fit.pvalues[i]),
                                 **wild.iloc[i].drop('term_index').to_dict()} for i,name in enumerate(names))
                    fits.append({'model':model,'n':len(frame),'adjusted_r2':float(fit.rsquared_adj),'condition_number':float(fit.condition_number),
                                 'aic':float(fit.aic),'bic':float(fit.bic),'rank':X.shape[1],
                                 'residual_moran':moran_knn(fit.resid,frame[['metric_x','metric_y']].to_numpy(float),seed=design['validation']['random_seed'])})
                    vif.extend({'model':model,'term':name,'vif':float(variance_inflation_factor(X,i))} for i,name in enumerate(names) if i>0)
                    private.extend({'listing_id':str(key),'model':model,'residual':float(value)} for key,value in zip(frame.listing_id,fit.resid,strict=True))
                output={'city':city,'status':'COMPLETE_ASSOCIATION',**eligibility,
                        'models':fits,'coefficients_produced':True,'covariance':'HC3; restricted Webb WCR11/CRV1 sensitivity; actual operational groups',
                        'income_required':False,'outcome_imputed':False,'interpretation':'Adjusted associations; no causal effect'}
            with engine.begin() as conn:
                identity=commit_package(conn,city=city,family='reporting',summary=output,
                                        records={'association_coefficients':json_records(pd.DataFrame(rows)),'association_diagnostics':fits,
                                                 'vif':vif,'association_residuals':private},
                                        deps=dependencies({'sample':selected[city],'diagnostic_code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_diagnostics.py'),
                                                           'wild_code_sha256':sha256_file(PROJECT_ROOT/'src/pipeline/inference.py')}))
            pointers[city]={'run_id':identity,'summary_sha256':canonical_hash(output)};public[city]=output
            print(city,output['status'],len(frame),flush=True)
        write_once(PROJECT_ROOT/'config/study/association_selection.json',(json.dumps(pointers,indent=2)+'\n').encode())
        write_once(PROJECT_ROOT/'docs/analysis/association_audit.json',(json.dumps(public,indent=2,ensure_ascii=False)+'\n').encode())
    finally:engine.dispose()
    return public


if __name__=='__main__':association()
