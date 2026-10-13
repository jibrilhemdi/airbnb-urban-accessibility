"""Publish fresh association evidence while preserving completed prediction outputs."""
from __future__ import annotations
import json
import subprocess
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.study.archive import preserved_path
from src.study.sources import get_engine,write_once
from src.study.specification import CITIES,load_design
from src.study.sample_freeze import records
from src.reporting.study_report import selected,markdown
from src.reporting.study_figures import save_figure


def run():
    prior=json.loads((PROJECT_ROOT/'archive/before_association_amendment/docs/analysis/final_artifact_inventory.json').read_text())
    for item in prior:
        path=preserved_path(item['path'],item['sha256'])
        if path.stat().st_size!=item['bytes']:raise ValueError('Original public artifact size differs')
    design,_=load_design();engine=get_engine();execution=[];diagnostics=[];moran=[];spatial_execution=[];coefficients=[]
    chosen=json.loads((PROJECT_ROOT/'config/study/association_selection.json').read_text())
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            association=selected(conn,'association_selection');spatial=selected(conn,'spatial_diagnostic_selection')
            for city in CITIES:
                summary=association[city]
                if summary['status']!='COMPLETE_ASSOCIATION':raise ValueError('Association execution incomplete')
                execution.append({'city':city,'association_execution_status':summary['status'],**{k:summary[k] for k in ['prediction_n','association_n','missing_fraction','association_missing_limit','inferential_imputation','complete_case_records_sha256']}})
                for row in summary['models']:
                    diagnostics.append({'city':city,**{k:v for k,v in row.items() if k!='residual_moran'}})
                    moran.append({'city':city,'model':row['model'],**row['residual_moran']})
                sp=spatial[city]
                spatial_execution.append({'city':city,'spatial_error_status':sp['spatial_error_status'],'fixed_effect_status':sp['fixed_effect_status'],
                                          'metric_crs':sp['metric_crs'],'absorbed_predictor':'log_population_density','trigger':sp['trigger']})
                coefficients.extend({'city':city,**r} for r in records(conn,chosen,city,'reporting','association_coefficients'))
    finally:engine.dispose()
    out=PROJECT_ROOT/'outputs/tables/research'
    for name,rows in [('association_execution_status',execution),('association_diagnostics',diagnostics),('association_residual_moran',moran),('association_spatial_execution',spatial_execution)]:
        write_once(out/(name+'.csv'),pd.DataFrame(rows).to_csv(index=False).encode())
    terms=design['blocks']['E']+design['blocks']['W'];table=pd.DataFrame([r for r in coefficients if r['model']=='MEW' and r['term'] in terms])
    fig,axes=plt.subplots(1,3,figsize=(14,6),layout='constrained',sharey=True)
    for ax,city in zip(axes,CITIES,strict=True):
        part=table.loc[table.city==city].set_index('term').loc[terms]
        ax.errorbar(part.coefficient,np.arange(len(terms)),xerr=np.vstack([part.coefficient-part.hc3_ci_low,part.hc3_ci_high-part.coefficient]),fmt='o',capsize=3)
        ax.axvline(0,color='grey',lw=1);ax.set_title(city.title());ax.set_yticks(np.arange(len(terms)),terms)
        ax.set_xlabel('Adjusted log-price coefficient (95% HC3 CI)');ax.grid(axis='x',alpha=.2)
    axes[0].invert_yaxis();fig.suptitle('MEW complete-case associations; predictor-specific units; observational, noncausal')
    save_figure(fig,PROJECT_ROOT/'outputs/figures/research/association_accessibility_coefficients.png');plt.close(fig)
    report=(PROJECT_ROOT/'docs/analysis/research_report.md').read_text()
    for name in ['accessibility_cells','ols_transfer_matrix','xgboost_transfer_matrix','ols_transfer_gains','xgboost_transfer_gains']:
        report=report.replace(name+'.png',name+'_publication.png')
    report+='\n\n## Fresh complete-case association inference\n\n'+markdown(execution)+'\n\n'+markdown(table.to_dict('records'),['city','term','coefficient','hc3_ci_low','hc3_ci_high','wild_cluster_p_value'])
    report+='\n\n![Accessibility association coefficients](../../outputs/figures/research/association_accessibility_coefficients.png)\n\n'+markdown(spatial_execution)
    report+='\n\nFull coefficient, VIF, rank/condition, residual Moran and spatial/fixed-effect tables are exported under `outputs/tables/research/association_*.csv` and `spatial_association_coefficients.csv`. Original predictive and transfer figures remain byte-identical. The post-observation 10% eligibility amendment is disclosed above; inference uses only genuinely complete cases.\n'
    write_once(PROJECT_ROOT/'docs/analysis/research_report_publication.md',report.encode())
    primary=json.loads((PROJECT_ROOT/'archive/before_association_amendment/docs/analysis/primary_results.json').read_text());primary['association']=association;primary['spatial_association']=spatial
    write_once(PROJECT_ROOT/'docs/analysis/primary_results.json',(json.dumps(primary,indent=2)+'\n').encode())
    commits=subprocess.check_output(['git','log','--reverse','--format=%H %s','55571d42601024d75e941f207c53a57552edbf9f..HEAD'],cwd=PROJECT_ROOT,text=True).splitlines()
    write_once(PROJECT_ROOT/'docs/analysis/checkpoint_history.json',(json.dumps({'checkpoint_commits_before_final_publication':commits,'final_checkpoint_sha':'Supplied externally after commit/push'},indent=2)+'\n').encode())
    audit={'status':'PASS','previous72_artifacts_preserved_at_original_or_archived_paths':True,'association_cities_complete':3,
           'association_execution':execution,'spatial_execution':spatial_execution,'association_only_outputs_regenerated':True,
           'post_observation_amendment':True,'old_missingness_limit':.05,'new_missingness_limit':.10,
           'code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_publication.py')}
    write_once(PROJECT_ROOT/'docs/analysis/publication_audit.json',(json.dumps(audit,indent=2)+'\n').encode())
    return audit


if __name__=='__main__':print(json.dumps(run(),indent=2))
