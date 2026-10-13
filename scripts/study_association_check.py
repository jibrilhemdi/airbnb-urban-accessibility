"""Independently recalculate complete-case OLS and HC3, and reproduce inference."""
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.preprocessing import OneHotEncoder
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,CITIES,MODELS
from src.study.sample_freeze import records
from src.study.store import read_package
from src.study.association import qualify
from src.pipeline.inference import wild_cluster_bootstrap_t
from src.pipeline.protocol import canonical_hash
from src.spatial.spatial_diagnostics import moran_knn


def run():
    design,_=load_design();engine=get_engine();results={}
    samples=json.loads((ROOT/'config/study/sample_selection.json').read_text())
    selected=json.loads((ROOT/'config/study/association_selection.json').read_text())
    spatial=json.loads((ROOT/'config/study/spatial_diagnostic_selection.json').read_text())
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                prediction=pd.DataFrame(records(conn,samples,city,'sample','prediction_sample'))
                saved=pd.DataFrame(records(conn,samples,city,'sample','association_sample'))
                frame,gate=qualify(prediction,saved,design)
                summary,_=read_package(conn,selected[city]['run_id'],city,'reporting')
                if canonical_hash(summary)!=selected[city]['summary_sha256']:raise ValueError('Association summary differs')
                coefficients=pd.DataFrame(records(conn,selected,city,'reporting','association_coefficients'))
                vifs=pd.DataFrame(records(conn,selected,city,'reporting','vif'))
                residuals=pd.DataFrame(records(conn,selected,city,'reporting','association_residuals'))
                checked=0
                for model in MODELS:
                    numeric=[f for f in design['models'][model] if f!='property_type']
                    encoder=OneHotEncoder(drop='first',handle_unknown='ignore',sparse_output=False)
                    cats=encoder.fit_transform(frame[['property_type']])
                    names=['Intercept',*numeric,*encoder.get_feature_names_out(['property_type'])]
                    X=np.column_stack([np.ones(len(frame)),frame[numeric].to_numpy(float),cats]);y=frame.log_price.to_numpy(float)
                    beta=np.linalg.lstsq(X,y,rcond=None)[0];residual=y-X@beta
                    bread=np.linalg.inv(X.T@X);leverage=np.einsum('ij,jk,ik->i',X,bread,X)
                    score=X*(residual/(1-leverage))[:,None]
                    se=np.sqrt(np.diag(bread@(score.T@score)@bread))
                    table=coefficients.loc[coefficients.model==model].set_index('term').loc[names]
                    for actual,expected in [(beta,table.coefficient),(se,table.hc3_se),
                                            (beta-norm.ppf(.975)*se,table.hc3_ci_low),(beta+norm.ppf(.975)*se,table.hc3_ci_high)]:
                        np.testing.assert_allclose(actual,expected,rtol=1e-7,atol=1e-9)
                    observed=residuals.loc[residuals.model==model].set_index('listing_id').loc[frame.listing_id.astype(str)].residual
                    np.testing.assert_allclose(residual,observed,rtol=1e-7,atol=1e-9)
                    wild=wild_cluster_bootstrap_t(X,y,frame.operational_group.to_numpy(),replications=9999,seed=design['validation']['random_seed'])
                    np.testing.assert_allclose(wild.wild_cluster_p_value,table.wild_cluster_p_value,rtol=0,atol=0)
                    if not (table.wild_replications.eq(9999).all() and table.clusters.eq(frame.operational_group.nunique()).all()):
                        raise ValueError('Wild-cluster budget/groups differ')
                    diagnostic=next(d for d in summary['models'] if d['model']==model)
                    moran=moran_knn(residual,frame[['metric_x','metric_y']].to_numpy(float),seed=design['validation']['random_seed'])
                    for key in ['moran_i','permutation_p_two_sided']:
                        np.testing.assert_allclose(moran[key],diagnostic['residual_moran'][key],rtol=1e-7,atol=1e-9)
                    for i,name in enumerate(names[1:],1):
                        other=np.delete(X,i,axis=1);fit=other@np.linalg.lstsq(other,X[:,i],rcond=None)[0]
                        r2=1-np.sum((X[:,i]-fit)**2)/np.sum((X[:,i]-X[:,i].mean())**2)
                        value=vifs.loc[(vifs.model==model)&(vifs.term==name),'vif'].item()
                        np.testing.assert_allclose(1/(1-r2),value,rtol=1e-6)
                    checked+=len(table)
                sp,_=read_package(conn,spatial[city]['run_id'],city,'reporting')
                if sp['fixed_effect_status']!='COMPLETE' or sp['spatial_error_status'] not in {'COMPLETE','NOT_APPLICABLE_TRIGGER_NOT_MET'}:
                    raise ValueError('Required dependent inference incomplete')
                results[city]={**gate,'status':'PASS','coefficients_hc3_and_wild_checked':checked,
                               'ols_recalculation':'NumPy least-squares; independent HC3 sandwich and normal intervals',
                               'wild_reproduction':'9999 restricted Webb draws; exact p-values',
                               'vif_and_residual_moran':'PASS','fixed_effect_status':sp['fixed_effect_status'],
                               'spatial_error_status':sp['spatial_error_status']}
    finally:engine.dispose()
    write_once(ROOT/'docs/analysis/association_recalculation_audit.json',(json.dumps(results,indent=2)+'\n').encode())
    return results


if __name__=='__main__':print(json.dumps(run(),indent=2))
