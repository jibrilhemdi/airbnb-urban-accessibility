"""Descriptive measurement, frozen-model contributions and transfer diagnostics."""
from __future__ import annotations
import io
import json
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import text
from xgboost import DMatrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once
from src.study.specification import CITIES,MODELS,load_design
from src.study.sample_freeze import records
from src.study.store import commit_package,dependencies,read_package
from src.reporting.study_results import predictions
from src.reporting.study_figures import save_figure


def describe(values):
    values=np.asarray(values,float)
    if not np.isfinite(values).all():raise ValueError('Measurement diagnostics require observed finite values')
    return dict(zip(['minimum','p05','p25','median','p75','p95','maximum'],map(float,np.quantile(values,[0,.05,.25,.5,.75,.95,1])),strict=True))


def run():
    design,cities=load_design();sample=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text())
    transfers=json.loads((PROJECT_ROOT/'runs/transfer/selection.json').read_text())
    engine=get_engine();measurement=[];shap=[];calibration=[];histograms=[];model_audit=[];pointers={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            frames={c:pd.DataFrame(records(conn,sample,c,'sample','prediction_sample')) for c in CITIES}
            for city,frame in frames.items():
                for concept in ('station','bus'):
                    e=frame['nearest_'+concept+'_euclidean_km'].to_numpy(float)
                    w=frame['nearest_'+concept+'_walking_minutes'].to_numpy(float)*5/60
                    measurement.append({'city':city,'concept':concept,'n':len(frame),'euclidean_km':describe(e),'walking_km':describe(w),
                                        'nearest_measure_difference_km':describe(w-e),'spearman':float(pd.Series(e).corr(pd.Series(w),method='spearman')),
                                        'meaning':'Nearest category measures may choose different destinations; this is not same-destination route circuity'})
                    # Fixed distance bins are descriptive and do not change fitting.
                    for label,values in [('Euclidean',e),('Walking',w)]:
                        count,edges=np.histogram(values,bins=[0,.1,.25,.5,.75,1,1.5,2,3,5,10,np.inf])
                        histograms.extend({'city':city,'concept':concept,'measure':label,'lower_km':float(edges[i]),
                                           'upper_km':float(edges[i+1]) if np.isfinite(edges[i+1]) else None,'n':int(n)} for i,n in enumerate(count))
                for category in ('food','culture'):
                    for minutes in (10,15,20):
                        e=frame[f'{category}_e_{minutes}'].to_numpy(float);w=frame[f'{category}_w_{minutes}'].to_numpy(float)
                        measurement.append({'city':city,'concept':category,'minutes':minutes,'n':len(frame),'euclidean_opportunities':describe(e),
                                            'walking_opportunities':describe(w),'walking_minus_euclidean':describe(w-e),
                                            'zero_euclidean_fraction':float(np.mean(e==0)),'zero_walking_fraction':float(np.mean(w==0)),
                                            'spearman':float(pd.Series(e).corr(pd.Series(w),method='spearman'))})
                selected=json.loads((PROJECT_ROOT/'runs'/city/'within_city_neighbourhood_selection.json').read_text())
                ids=[r['run_id'] for r in selected]
                rows=conn.execute(text("SELECT record->>'model' AS model, kv.key AS term, AVG(ABS(kv.value::double precision)) AS mean_abs, "
                                       "AVG(kv.value::double precision) AS mean_signed, COUNT(*) AS n FROM study.records "
                                       "CROSS JOIN LATERAL jsonb_each_text(record->'contributions') AS kv "
                                       "WHERE run_id=ANY(:runs) AND city=:city AND artifact='heldout_contributions' "
                                       "GROUP BY record->>'model',kv.key ORDER BY model,mean_abs DESC"),{'runs':ids,'city':city}).mappings().all()
                shap.extend({'city':city,'scope':'neighbourhood_heldout','estimator':'XGBoost',**dict(row)} for row in rows)
            for chosen in transfers:
                summary,frame=predictions(conn,chosen['run_id'],chosen['city'],'transfer')
                model=summary['fitted_source_model'];digest=sha256_file(PROJECT_ROOT/model['path'])
                if digest!=model['sha256']:raise ValueError('Frozen transfer source pipeline bytes changed')
                if any(summary[k] for k in ('target_fit','target_tuning','target_intercept_recalibration')):raise ValueError('Target-data fit flags violate transfer contract')
                model_audit.append({'source':chosen['city'],'target':chosen['target_city'],'estimator':chosen['estimator'],'model':chosen['model'],'sha256':digest})
                p=frame.prediction.to_numpy(float);y=frame.relative_log_price.to_numpy(float)
                slope,intercept=np.polyfit(p,y,1)
                calibration.append({'source_city':chosen['city'],'target_city':chosen['target_city'],'estimator':chosen['estimator'],'model':chosen['model'],
                                    'n':len(frame),'mean_prediction_minus_observed':float(np.mean(p-y)),'observed_on_prediction_slope':float(slope),
                                    'observed_on_prediction_intercept':float(intercept),'mean_prediction':float(p.mean()),'mean_observed':float(y.mean()),
                                    'meaning':'Post-fit descriptive target calibration; these coefficients never modify predictions or model selection'})
                if chosen['estimator']=='XGBoost':
                    fit=joblib.load(PROJECT_ROOT/model['path']);target=frames[chosen['target_city']]
                    prep=fit.named_steps['prep'];matrix=prep.transform(target)
                    values=fit.named_steps['model'].get_booster().predict(DMatrix(matrix),pred_contribs=True)
                    expected=fit.predict(target[design['models'][chosen['model']]])
                    if not np.allclose(values.sum(axis=1),expected,atol=1e-4):raise ValueError('Transfer contribution sum differs from frozen prediction')
                    if not np.allclose(expected,p,atol=1e-12):raise ValueError('Reloaded source pipeline does not reproduce saved target predictions')
                    shap.extend({'city':chosen['city'],'target_city':chosen['target_city'],'scope':'directional_transfer','estimator':'XGBoost','model':chosen['model'],
                                 'term':name,'mean_abs':float(np.mean(abs(values[:,i]))),'mean_signed':float(np.mean(values[:,i])),'n':len(target)}
                                for i,name in enumerate(prep.get_feature_names_out()))
            audit=pd.DataFrame(model_audit)
            if len(audit)!=48 or audit.groupby(['source','estimator','model']).sha256.nunique().ne(1).any():raise ValueError('Two outgoing transfers must use identical frozen source pipeline')
        for city in CITIES:
            public={'city':city,'status':'DESCRIPTIVE_DIAGNOSTICS_COMPLETE','measurement':[r for r in measurement if r['city']==city],
                    'transfer_calibration':[r for r in calibration if r['source_city']==city],
                    'source_pipeline_hash_audit':'PASS','outgoing_targets_share_identical_source_pipeline':True,
                    'heldout_and_transfer_contribution_interpretation':'Descriptive predictive contributions; correlated features share credit; not causal effects',
                    'metric_crs':cities[city]['metric_crs']}
            with engine.begin() as conn:
                identity=commit_package(conn,city=city,family='reporting',summary=public,
                                        records={'contribution_summary':[r for r in shap if r['city']==city]},
                                        deps=dependencies({'code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_interpretation.py')}))
            pointers[city]={'run_id':identity,'summary_sha256':canonical_hash(public)}
        out=PROJECT_ROOT/'outputs/tables/research';out.mkdir(parents=True,exist_ok=True)
        for name,rows in [('measurement_distributions',measurement),('measurement_histograms',histograms),('contribution_summary',shap),('transfer_calibration',calibration),('transfer_model_hash_audit',model_audit)]:
            write_once(out/(name+'.json'),(json.dumps(rows,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode())
        write_once(out/'contribution_summary.csv',pd.DataFrame(shap).to_csv(index=False).encode())
        write_once(out/'transfer_calibration.csv',pd.DataFrame(calibration).to_csv(index=False).encode())
        write_once(PROJECT_ROOT/'config/study/interpretation_selection.json',(json.dumps(pointers,indent=2)+'\n').encode())
        figures(measurement,histograms,shap,calibration)
        return {'measurement_rows':len(measurement),'contribution_rows':len(shap),'transfer_calibration_rows':len(calibration),'source_model_hashes_verified':len(model_audit)}
    finally:engine.dispose()


def figures(measurement,histograms,shap,calibration):
    out=PROJECT_ROOT/'outputs/figures/research'
    hist=pd.DataFrame(histograms);fig,axes=plt.subplots(2,3,figsize=(12,6),sharex=True)
    labels=['0–.1','.1–.25','.25–.5','.5–.75','.75–1','1–1.5','1.5–2','2–3','3–5','5–10','10+']
    for col,city in enumerate(CITIES):
        for row,concept in enumerate(('station','bus')):
            ax=axes[row,col]
            for measure,shift in [('Euclidean',-.18),('Walking',.18)]:
                part=hist.loc[(hist.city==city)&(hist.concept==concept)&(hist.measure==measure)]
                ax.bar(np.arange(len(part))+shift,part.n/part.n.sum(),width=.36,label=measure)
            ax.set_title(city.title()+' — '+concept);ax.set_xticks(range(11),labels,rotation=60,fontsize=7);ax.set_ylabel('Share of analytical listings')
    axes[0,0].legend();fig.suptitle('Nearest category distance (km); destinations may differ between measures',fontsize=10)
    fig.tight_layout();save_figure(fig,out/'nearest_distance_distributions.png');plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,city in zip(axes,CITIES,strict=True):
        part=[r for r in measurement if r['city']==city and r.get('minutes')==10]
        for i,r in enumerate(part):
            ax.bar(i-.18,r['euclidean_opportunities']['median'],.36,label='Euclidean' if i==0 else None)
            ax.bar(i+.18,r['walking_opportunities']['median'],.36,label='Walking' if i==0 else None)
        ax.set_xticks(range(2),[r['concept'].title() for r in part]);ax.set_title(city.title());ax.set_ylabel('Median 10-minute opportunities')
    axes[0].legend();fig.tight_layout();save_figure(fig,out/'opportunity_comparison.png');plt.close(fig)
    data=pd.DataFrame(shap);fig,axes=plt.subplots(1,3,figsize=(13,5))
    for ax,city in zip(axes,CITIES,strict=True):
        part=data.loc[(data.city==city)&(data.scope=='neighbourhood_heldout')&(data.model=='MEW')].nlargest(10,'mean_abs').sort_values('mean_abs')
        ax.barh(part.term,part.mean_abs,color='#327c91');ax.set_title(city.title());ax.set_xlabel('Mean absolute held-out contribution (log price)')
    fig.suptitle('Frozen XGBoost MEW: descriptive contributions, no causal interpretation',fontsize=10)
    fig.tight_layout();save_figure(fig,out/'heldout_contributions.png');plt.close(fig)
    selected=pd.DataFrame(calibration);fig,axes=plt.subplots(1,2,figsize=(10,5))
    for ax,estimator in zip(axes,('OLS','XGBoost'),strict=True):
        part=selected.loc[(selected.estimator==estimator)&(selected.model=='MEW')]
        labels=part.source_city.str.title()+' → '+part.target_city.str.title()
        ax.barh(labels,part.mean_prediction_minus_observed,color='#327c91');ax.axvline(0,color='grey');ax.set_title(estimator+' MEW');ax.set_xlabel('Mean prediction − observed relative log price')
    fig.suptitle('Directional transfer bias; evaluation only, no target recalibration',fontsize=10)
    fig.tight_layout();save_figure(fig,out/'transfer_bias.png');plt.close(fig)


if __name__=='__main__':print(json.dumps(run(),indent=2))
