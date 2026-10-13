"""Publication artifacts from verified SQL summaries and safe aggregated samples."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT
from src.study.sources import get_engine,write_once
from src.study.specification import CITIES,MODELS,load_design
from src.study.store import read_package
from src.study.sample_freeze import records


def save_figure(fig,path):
    buffer=io.BytesIO();fig.savefig(buffer,format='png')
    write_once(path,buffer.getvalue())


def primary_gallery():
    result=json.loads((PROJECT_ROOT/'config/study/results_neighbourhood.json').read_text())
    samples=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text())
    engine=get_engine();performance=[];contrasts=[];measurement=[];safe=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                summary,_=read_package(conn,result[city]['run_id'],city,'reporting')
                performance.extend(summary['performance']);contrasts.extend(summary['contrasts'])
                frame=pd.DataFrame(records(conn,samples,city,'sample','prediction_sample'))
                for concept in ['station','bus']:
                    straight=frame['nearest_'+concept+'_euclidean_km'];network=frame['nearest_'+concept+'_walking_minutes']*5/60
                    measurement.append({'city':city,'concept':concept,'n':len(frame),'euclidean_median_km':float(straight.median()),
                                        'network_median_km':float(network.median()),'nearest_measure_difference_median_km':float((network-straight).median()),
                                        'interpretation':'Same category universe; nearest destination may differ. Difference is not same-destination circuity.'})
                for concept in ['food','culture']:
                    e=frame[concept+'_e_10'];w=frame[concept+'_w_10']
                    measurement.append({'city':city,'concept':concept,'n':len(frame),'euclidean_median_opportunities':float(e.median()),
                                        'network_median_opportunities':float(w.median()),'zero_network_fraction':float(w.eq(0).mean()),
                                        'difference_mean':float((w-e).mean())})
                cells=frame.assign(cell_x=(np.floor(frame.metric_x/500)*500),cell_y=(np.floor(frame.metric_y/500)*500)).groupby(['cell_x','cell_y']).agg(
                    n=('listing_id','size'),rail_minutes=('nearest_station_walking_minutes','mean'),food=('food_w_10','mean')).reset_index()
                cells=cells.loc[cells.n>=5]
                safe.extend(cells.assign(city=city).to_dict('records'))
    finally:engine.dispose()
    out=PROJECT_ROOT/'outputs/figures/research';out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False})
    p=pd.DataFrame(performance)
    fig,axes=plt.subplots(1,3,figsize=(11,3.7),sharey=False)
    for ax,city in zip(axes,CITIES,strict=True):
        for estimator,style in [('OLS','o-'),('XGBoost','s-')]:
            rows=p.loc[(p.city==city)&(p.estimator==estimator)].set_index('model').loc[list(MODELS)]
            ax.plot(range(4),rows.rmse,style,label=estimator)
        ax.set_xticks(range(4),MODELS);ax.set_title(city.title());ax.set_ylabel('Neighbourhood OOF RMSE (log price)');ax.grid(alpha=.2)
    axes[0].legend();fig.tight_layout();save_figure(fig,out/'within_city_performance.png');plt.close(fig)
    c=pd.DataFrame(contrasts);fig,axes=plt.subplots(1,3,figsize=(12,4.4))
    for ax,city in zip(axes,CITIES,strict=True):
        rows=c.loc[(c.city==city)&(c.estimator=='XGBoost')].reset_index(drop=True)
        for i,r in rows.iterrows():
            ax.plot([r.stability_low,r.stability_high],[i,i],color='#327c91',lw=2);ax.scatter(r.delta_rmse,i,color='#143e52')
        ax.axvline(0,color='grey',lw=1);ax.set_yticks(range(len(rows)),rows.added+' − '+rows.reference)
        ax.set_title(city.title());ax.set_xlabel('ΔRMSE; negative favours candidate');ax.grid(axis='x',alpha=.2)
    fig.suptitle('Geographic composition stability; not independent-sample confidence intervals',fontsize=10)
    fig.tight_layout();save_figure(fig,out/'accessibility_gains.png');plt.close(fig)
    cells=pd.DataFrame(safe);fig,axes=plt.subplots(1,3,figsize=(12,4.7))
    vmax=float(cells.rail_minutes.quantile(.95))
    for ax,city in zip(axes,CITIES,strict=True):
        part=cells.loc[cells.city==city]
        artist=ax.scatter(part.cell_x/1000,part.cell_y/1000,c=part.rail_minutes,s=12,marker='s',cmap='viridis',vmin=0,vmax=vmax)
        ax.set_aspect('equal');ax.set_title(city.title());ax.set_xlabel('Metric easting (km)');ax.set_ylabel('Metric northing (km)')
    fig.colorbar(artist,ax=axes,label='Mean nearest rail walking minutes',shrink=.65)
    fig.suptitle('500 m cells; fewer than five observations suppressed. © OpenStreetMap contributors, ODbL',fontsize=10)
    fig.subplots_adjust(wspace=.4,top=.88,bottom=.12);save_figure(fig,out/'accessibility_cells.png');plt.close(fig)
    directory=PROJECT_ROOT/'outputs/tables/research';directory.mkdir(parents=True,exist_ok=True)
    write_once(directory/'measurement_comparison.csv',pd.DataFrame(measurement).to_csv(index=False).encode())
    write_once(directory/'safe_accessibility_cells.csv',cells.to_csv(index=False).encode())
    return {'figures':[str(x.relative_to(PROJECT_ROOT)) for x in sorted(out.glob('*.png'))],'measurement_rows':len(measurement),'public_cells':len(cells),'map_grid_m':500,'minimum_cell_n':5}


def transfer_gallery():
    selections=json.loads((PROJECT_ROOT/'config/study/results_transfer.json').read_text());engine=get_engine();rows=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                summary,_=read_package(conn,selections[city]['run_id'],city,'reporting');rows.extend(summary['performance'])
    finally:engine.dispose()
    frame=pd.DataFrame(rows);out=PROJECT_ROOT/'outputs/figures/research';out.mkdir(parents=True,exist_ok=True)
    for estimator in ('OLS','XGBoost'):
        fig,axes=plt.subplots(1,4,figsize=(13,3.8));vmin=float(frame.rmse.min());vmax=float(frame.rmse.max())
        for ax,model in zip(axes,MODELS,strict=True):
            part=frame.loc[(frame.estimator==estimator)&(frame.model==model)]
            matrix=part.pivot(index='source_city',columns='target_city',values='rmse').reindex(index=CITIES,columns=CITIES)
            artist=ax.imshow(matrix.to_numpy(),vmin=vmin,vmax=vmax,cmap='viridis')
            for i in range(3):
                for j in range(3):
                    if i!=j:ax.text(j,i,f'{matrix.iloc[i,j]:.3f}',ha='center',va='center',color='white')
            ax.set_xticks(range(3),[c.title() for c in CITIES],rotation=45,ha='right');ax.set_yticks(range(3),[c.title() for c in CITIES]);ax.set_title(model)
        fig.colorbar(artist,ax=axes,label='Relative log-price RMSE',shrink=.7)
        fig.suptitle(estimator+' directional transfer: rows source, columns target; diagonal not tested')
        fig.subplots_adjust(wspace=.6,top=.82,bottom=.3);save_figure(fig,out/(estimator.lower()+'_transfer_matrix.png'));plt.close(fig)


if __name__=='__main__':print(json.dumps(primary_gallery(),indent=2))
