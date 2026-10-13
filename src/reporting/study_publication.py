"""Final presentation review from verified SQL; preserve initial result artifacts."""
from __future__ import annotations
import json
import subprocess
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once
from src.study.specification import CITIES,MODELS,load_design
from src.study.sample_freeze import records
from src.reporting.study_report import selected,markdown
from src.reporting.study_figures import save_figure


def run():
    old_inventory=json.loads((PROJECT_ROOT/'docs/analysis/public_output_inventory.json').read_text())
    for item in old_inventory:
        if sha256_file(PROJECT_ROOT/item['path'])!=item['sha256']:raise ValueError('Initial completed artifact changed')
    design,cities=load_design();engine=get_engine();performance=[];contrasts=[];cells=[];execution=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            transfer=selected(conn,'results_transfer');association=selected(conn,'association_selection')
            samples=selected(conn,'sample_selection','sample')
            chosen=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text())
            for city in CITIES:
                performance.extend(transfer[city]['performance']);contrasts.extend(transfer[city]['contrasts'])
                execution.append({'city':city,'association_execution_status':association[city]['status'],
                                  'association_status_at_sample_freeze':samples[city]['association_inference_status'],
                                  'association_n':association[city]['association_n'],'missing_fraction':association[city]['missing_fraction']})
                frame=pd.DataFrame(records(conn,chosen,city,'sample','prediction_sample'))
                part=frame.assign(cell_x=np.floor(frame.metric_x/500)*500,cell_y=np.floor(frame.metric_y/500)*500).groupby(['cell_x','cell_y']).agg(
                    n=('listing_id','size'),rail_minutes=('nearest_station_walking_minutes','mean'),food=('food_w_10','mean')).reset_index()
                cells.extend(part.loc[part.n>=5].assign(city=city).to_dict('records'))
        out=PROJECT_ROOT/'outputs/figures/research';new_paths=[]
        data=pd.DataFrame(performance);gains=pd.DataFrame(contrasts)
        for estimator in ['OLS','XGBoost']:
            fig,axes=plt.subplots(1,4,figsize=(14,4.4),layout='constrained')
            vmin=float(data.rmse.min());vmax=float(data.rmse.max())
            for ax,model in zip(axes,MODELS,strict=True):
                matrix=data.loc[(data.estimator==estimator)&(data.model==model)].pivot(index='source_city',columns='target_city',values='rmse').reindex(index=CITIES,columns=CITIES)
                artist=ax.imshow(matrix.to_numpy(),vmin=vmin,vmax=vmax,cmap='viridis')
                for i in range(3):
                    for j in range(3):
                        if i!=j:ax.text(j,i,f'{matrix.iloc[i,j]:.3f}',ha='center',va='center',color='black' if (matrix.iloc[i,j]-vmin)/(vmax-vmin)>.6 else 'white')
                ax.set_xticks(range(3),[c.title() for c in CITIES],rotation=45,ha='right');ax.set_yticks(range(3),[c.title() for c in CITIES]);ax.set_title(model)
            fig.colorbar(artist,ax=axes,label='Relative log-price RMSE',shrink=.65)
            fig.suptitle(estimator+': rows source, columns target; diagonal not tested')
            path=out/(estimator.lower()+'_transfer_matrix_publication.png');save_figure(fig,path);plt.close(fig);new_paths.append(path)
            fig,axes=plt.subplots(1,5,figsize=(17,4.4),layout='constrained')
            part=gains.loc[gains.estimator==estimator];bound=float(abs(part.delta_rmse).max())
            for ax,(added,reference) in zip(axes,design['contrasts'],strict=True):
                matrix=part.loc[(part.added==added)&(part.reference==reference)].pivot(index='source_city',columns='target_city',values='delta_rmse').reindex(index=CITIES,columns=CITIES)
                artist=ax.imshow(matrix.to_numpy(),cmap='RdBu_r',vmin=-bound,vmax=bound)
                for i in range(3):
                    for j in range(3):
                        if i!=j:ax.text(j,i,f'{matrix.iloc[i,j]:+.3f}',ha='center',va='center',fontsize=8,color='white' if abs(matrix.iloc[i,j])/bound>.75 else 'black')
                ax.set_title(added+' − '+reference);ax.set_xticks(range(3),[c.title() for c in CITIES],rotation=45,ha='right');ax.set_yticks(range(3),[c.title() for c in CITIES])
            fig.colorbar(artist,ax=axes,label='ΔRMSE; negative improves',shrink=.65)
            fig.suptitle(estimator+' directional accessibility contrasts: rows source, columns target')
            path=out/(estimator.lower()+'_transfer_gains_publication.png');save_figure(fig,path);plt.close(fig);new_paths.append(path)
        data=pd.DataFrame(cells);vmax=float(data.rail_minutes.quantile(.95));fig,axes=plt.subplots(1,3,figsize=(13,5),layout='constrained')
        for ax,city in zip(axes,CITIES,strict=True):
            part=data.loc[data.city==city]
            artist=ax.scatter(part.cell_x/1000,part.cell_y/1000,c=part.rail_minutes,s=14,marker='s',cmap='viridis',vmin=0,vmax=vmax)
            ax.set_aspect('equal');ax.set_title(city.title()+' ('+cities[city]['metric_crs']+')');ax.set_xlabel('Easting (km)');ax.set_ylabel('Northing (km)')
        fig.colorbar(artist,ax=axes,label='Mean nearest rail walking minutes',shrink=.7)
        fig.suptitle('500 m cells, n≥5; colour capped at pooled95th percentile. © OpenStreetMap contributors, ODbL',fontsize=9)
        path=out/'accessibility_cells_publication.png';save_figure(fig,path);plt.close(fig);new_paths.append(path)
        table=PROJECT_ROOT/'outputs/tables/research/association_execution_status.csv';write_once(table,pd.DataFrame(execution).to_csv(index=False).encode());new_paths.append(table)
        original=PROJECT_ROOT/'docs/analysis/research_report.md';report=original.read_text()
        for name in ['accessibility_cells','ols_transfer_matrix','xgboost_transfer_matrix','ols_transfer_gains','xgboost_transfer_gains']:
            report=report.replace(name+'.png',name+'_publication.png')
        report=report.replace('Generated by `python -m src.reporting.study_report`','Generated by `python -m src.reporting.study_report`; publication review by `python -m src.reporting.study_publication`')
        report=report.replace('## Sources and harmonization','Current association execution (frozen candidate status above remains historical):\n\n'+markdown(execution)+'\n\n## Sources and harmonization')
        report+='\n\nPublication review corrects colour-bar layout and contrast, preserves every initial artifact and numerical result, and adds current association-execution labels from SQL. No model, sample, feature, threshold or statistic is changed.\n'
        path=PROJECT_ROOT/'docs/analysis/research_report_publication.md';write_once(path,report.encode());new_paths.append(path)
        commits=subprocess.check_output(['git','log','--reverse','--format=%H %s','55571d42601024d75e941f207c53a57552edbf9f..HEAD'],cwd=PROJECT_ROOT,text=True).splitlines()
        path=PROJECT_ROOT/'docs/analysis/checkpoint_history.json';write_once(path,(json.dumps({'checkpoint_commits_before_final_publication':commits,'final_checkpoint_sha':'Supplied externally after commit/push; never embedded in its own commit'},indent=2)+'\n').encode());new_paths.append(path)
        inventory=[*old_inventory,*[{'path':p.relative_to(PROJECT_ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)} for p in new_paths]]
        write_once(PROJECT_ROOT/'docs/analysis/publication_output_inventory.json',(json.dumps(inventory,indent=2)+'\n').encode())
        audit={'status':'PASS_WITH_DOCUMENTED_SCIENTIFIC_BLOCKERS','initial_release_audit_sha256':sha256_file(PROJECT_ROOT/'docs/analysis/release_audit.json'),
               'initial_research_report_sha256':sha256_file(original),'initial59_public_artifacts_unchanged':True,'publication_artifacts':len(new_paths),
               'all_public_artifacts':len(inventory),'public_map_cell_support_minimum':int(data.n.min()),'map_cells':len(data),
               'association_execution':execution,'models_or_statistics_changed':False,'full_rerun_complete':False,
               'primary_prediction_cities_complete':3,'six_transfer_directions_complete':True,'code_sha256':sha256_file(PROJECT_ROOT/'src/reporting/study_publication.py')}
        write_once(PROJECT_ROOT/'docs/analysis/publication_audit.json',(json.dumps(audit,indent=2)+'\n').encode())
        return audit
    finally:engine.dispose()


if __name__=='__main__':print(json.dumps(run(),indent=2))
