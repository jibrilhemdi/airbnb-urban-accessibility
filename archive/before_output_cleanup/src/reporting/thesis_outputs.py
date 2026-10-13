"""Deterministic thesis figures/tables: frozen SQL reads, no scientific fitting."""
from __future__ import annotations
import io
import json
import textwrap
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize,LogNorm
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Rectangle
from pyproj import Transformer
from shapely.ops import transform
from src.ingestion.common import sha256_file
from src.study.sources import write_once
from src.reporting.thesis_sources import ROOT,CITIES,MODELS,LABELS,SCHEMES,load
from src.reporting.thesis_tables import build,display,presentation,markdown,FEATURE_LABELS,VALIDATION_LABELS,ROBUSTNESS_LABELS
from src.reporting.thesis_audit import FIGURES,TABLES
from src.reporting import thesis_style as theme

COLOURS=theme.COLOURS
COMMAND='.venv/bin/python -m src.reporting.thesis_refresh --render'


class Registry:
    def __init__(self,data,revise=False,figure_stage=None):self.data=data;self.items=[];self.layout=[];self.revise=revise;self.figure_stage=figure_stage

    def refs(self,roles):
        refs=[]
        for role in roles:
            if role=='within_city':refs.extend(self.data['fold_sources'])
            elif role=='transfer_predictions':refs.extend(self.data['transfer_sources'])
            elif role=='validation':
                for scheme in SCHEMES:refs.extend(self.data['sources'][scheme])
            elif role=='design':refs.append({'path':'config/study/design.json','sha256':self.data['catalog']['files']['config/study/design.json'],'artifact':'final X/E/W registry'})
            elif role=='synthesis':
                for name in ['neighbourhood','transfer','interpretation','association']:refs.extend(self.data['sources'][name])
            else:refs.extend(self.data['sources'][role])
        return list({json.dumps(r,sort_keys=True):r for r in refs}.values())

    def register(self,path,rq,roles,caption,**details):
        filename=details.pop('registered_filename',None) or str(path.relative_to(ROOT))
        self.items.append({'filename':filename,'sha256':sha256_file(path),'bytes':path.stat().st_size,
                           'research_question':rq,'publication_status':'THESIS_READY_PENDING_FINAL_RELEASE_AUDIT',
                           'source_run_artifact':self.refs(roles),'source_catalog_sha256':self.data['catalog']['source_catalog_sha256'],
                           'generation_command':COMMAND,'caption':caption,'private_row_export':False,**details})

    def table(self,name,frame,rq,roles,caption,compact=None,category='tables'):
        out=ROOT/'outputs'/category/'thesis';out.mkdir(parents=True,exist_ok=True)
        for suffix,content in [('csv',display(frame).to_csv(index=False).encode()),('md',('# '+name.replace('_',' ').title()+'\n\n'+caption+'\n\n'+markdown(compact if compact is not None else display(frame))+'\n').encode())]:
            path=out/(name+'.'+suffix)
            if path.exists():
                if not self.revise or path.read_bytes()!=content:raise ValueError('Draft numeric/aggregate table changed during layout revision')
            else:write_once(path,content)
            self.register(path,rq,roles,caption,kind='table',logical_name=name,rows=len(frame))

    def figure(self,name,fig,rq,roles,caption,**details):
        caption=theme.decorate(fig,name,caption)
        fig.canvas.draw();renderer=fig.canvas.get_renderer();width,height=fig.canvas.get_width_height();clipped=[]
        hidden_ticks=set()
        for ax in fig.axes:
            for axis,limits in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
                for tick in [*axis.get_major_ticks(),*axis.get_minor_ticks()]:
                    if not min(limits)<=tick.get_loc()<=max(limits):hidden_ticks.update([id(tick.label1),id(tick.label2)])
        for item in fig.findobj(matplotlib.text.Text):
            if id(item) in hidden_ticks:continue
            if not item.get_visible() or not item.get_text():continue
            box=item.get_window_extent(renderer)
            if box.x0 < -2 or box.y0 < -2 or box.x1 > width+2 or box.y1 > height+2:clipped.append(item.get_text())
        caption_box=fig._thesis_caption.get_window_extent(renderer)
        caption_collision=fig._supxlabel is not None and caption_box.overlaps(fig._supxlabel.get_window_extent(renderer))
        header_boxes=[fig._thesis_heading.get_window_extent(renderer),fig._thesis_subtitle.get_window_extent(renderer)]
        header_collision=any(box.overlaps(legend.get_window_extent(renderer)) for box in header_boxes for legend in fig.legends)
        self.layout.append({'figure':name,'canvas_pixels':[width,height],'out_of_canvas_text':clipped,
                            'caption_overlaps_axis_label':bool(caption_collision),'header_overlaps_legend':bool(header_collision)})
        out=self.figure_stage or ROOT/'outputs/figures/thesis';out.mkdir(parents=True,exist_ok=True)
        for suffix in ['png','pdf','svg']:
            blob=io.BytesIO();metadata={'Software':'Frozen thesis reporting'} if suffix=='png' else {'CreationDate':None,'ModDate':None,'Creator':'Frozen thesis reporting'} if suffix=='pdf' else {'Date':None,'Creator':'Frozen thesis reporting'}
            fig.savefig(blob,format=suffix,dpi=300,metadata=metadata)
            path=out/(name+'.'+suffix)
            if path.exists():
                if not self.revise:raise ValueError('Existing figure requires explicit pending-layout revision')
                path.write_bytes(blob.getvalue())
            else:write_once(path,blob.getvalue())
            self.register(path,rq,roles,caption,kind='figure',logical_name=name,
                          registered_filename='outputs/figures/thesis/'+path.name,
                          style_id=theme.STYLE_ID,formats=['PNG300dpi','PDF vector','SVG vector'],page_inches=list(fig.get_size_inches()),**details)
        plt.close(fig)


def setup_style():
    theme.setup()


def grid(rows=1,cols=3,size=None,**kwargs):return plt.subplots(rows,cols,figsize=theme.canvas_size(size or (7.2,3.2*rows)),layout='constrained',squeeze=False,**kwargs)


def city_titles(axes):
    for row in axes:
        for ax,city in zip(row,CITIES,strict=True):ax.set_title(LABELS[city])


def intervals(ax,part,y,colour):
    ax.hlines(y,part.stability_low,part.stability_high,color=colour,lw=1.7)
    ax.vlines(part.stability_low,np.asarray(y)-.07,np.asarray(y)+.07,color=colour,lw=1.2)
    ax.vlines(part.stability_high,np.asarray(y)-.07,np.asarray(y)+.07,color=colour,lw=1.2)
    ax.plot(part.delta_rmse,y,'o',color=colour,markerfacecolor=theme.FILLS.get(colour,theme.BLUE),ms=6)


def outline(ax,geom,**kwargs):
    pieces=list(geom.geoms) if geom.geom_type=='MultiPolygon' else [geom]
    for piece in pieces:
        x,y=piece.exterior.xy;ax.fill(np.asarray(x)/1000,np.asarray(y)/1000,**kwargs)
        for ring in piece.interiors:
            x,y=ring.xy;ax.plot(np.asarray(x)/1000,np.asarray(y)/1000,color='#777777',lw=.3)


def maps(data,reg):
    crs={c:data['cities'][c]['metric_crs'] for c in CITIES}
    fig,axes=grid(size=(10.5,4.8))
    for ax,city in zip(axes[0],CITIES,strict=True):
        project=Transformer.from_crs('EPSG:4326',crs[city],always_xy=True).transform
        for item in sorted(data['geometries'][city],key=lambda item:item['key']!='mask'):
            geom=transform(project,item['geometry'])
            outline(ax,geom,facecolor='#F5F6F2' if item['key']=='mask' else theme.BLUE,edgecolor='#668A9A',linewidth=.7,alpha=.7)
        ax.set_aspect('equal');ax.set_title(f"{LABELS[city]}\n{data['cities'][city]['operational_count']} neighbourhoods")
        ax.set_xlabel('Easting (km)');ax.set_ylabel('Northing (km)')
        ax.text(.02,.98,crs[city],transform=ax.transAxes,va='top',fontsize=8,bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
        theme.map_frame(ax)
    reg.figure('study_areas',fig,'Design',['geography'],
               'Public frozen study masks and provider operational neighbourhood polygons used for primary validation. Municipal masks are membership geometry, not validation units. No individual listings. Inside Airbnb, CC BY4.0; accepted mask sources/vintages are in the source registry. Panel extents differ.',spatial_crs={'source':'EPSG:4326','panels':crs},page_orientation='landscape')
    cells=[]
    for city in CITIES:
        frame=data['frames'][city]
        part=frame.assign(cell_x=np.floor(frame.metric_x/500)*500,cell_y=np.floor(frame.metric_y/500)*500).groupby(['cell_x','cell_y']).agg(n=('listing_id','size'),mean_rail_walking_minutes=('nearest_station_walking_minutes','mean')).reset_index()
        cells.extend(part.loc[part.n>=5].assign(city=city,metric_crs=crs[city]).to_dict('records'))
    cells=pd.DataFrame(cells);cap=float(cells.mean_rail_walking_minutes.quantile(.95));norm=Normalize(0,cap)
    fig,axes=grid(size=(10.5,4.8))
    for ax,city in zip(axes[0],CITIES,strict=True):
        project=Transformer.from_crs('EPSG:4326',crs[city],always_xy=True).transform
        for item in sorted(data['geometries'][city],key=lambda item:item['key']!='mask'):
            outline(ax,transform(project,item['geometry']),facecolor='#F5F6F2' if item['key']=='mask' else 'none',edgecolor='#668A9A',linewidth=.55)
        for cell in cells.loc[cells.city==city].itertuples():
            ax.add_patch(Rectangle((cell.cell_x/1000,cell.cell_y/1000),.5,.5,facecolor=theme.SEQUENTIAL(norm(cell.mean_rail_walking_minutes)),edgecolor='none',zorder=2.5))
        for item in data['geometries'][city]:outline(ax,transform(project,item['geometry']),facecolor='none',edgecolor='#668A9A',linewidth=.55,zorder=3)
        ax.autoscale_view();ax.set_aspect('equal');ax.set_title(LABELS[city]);ax.set_xlabel('Easting (km)');ax.set_ylabel('Northing (km)')
        ax.text(.02,.98,crs[city],transform=ax.transAxes,va='top',fontsize=8,bbox={'facecolor':'white','alpha':.85,'edgecolor':'none'})
        theme.map_frame(ax)
    fig.colorbar(ScalarMappable(norm=norm,cmap=theme.SEQUENTIAL),ax=axes.ravel().tolist(),label='Mean rail walking time (minutes)',orientation='horizontal',shrink=.6,fraction=.045,pad=.06,panchor=False)
    reg.figure('accessibility_spatial',fig,'RQ1',['sample','geography'],
               'Mean nearest-rail walking minutes in500 m cells with at least five observations. Shared colour scale capped at pooled95th percentile for display; uncapped aggregate values remain in the accompanying table. Boundaries are the frozen provider geography. © OpenStreetMap contributors, ODbL; Inside Airbnb CC BY4.0.',spatial_crs={'source':'EPSG:4326','panels':crs},minimum_aggregate_n=5,colour_cap_minutes=cap,page_orientation='landscape')
    reg.table('accessibility_spatial_cells',cells,'RQ1',['sample'],
              'Only500 m cells with n≥5; no individual coordinates. Values are uncapped means of frozen walking accessibility.',category='metrics')


def measurement(data,tables,reg):
    fig,axes=grid(2,size=(10.5,7.2));bins=[];artists=[];speed=data['design']['accessibility']['walking_speed_kmh']
    for row,concept in enumerate(['station','bus']):
        maximum=max(float(max(data['frames'][c]['nearest_'+concept+'_euclidean_km'].max(),data['frames'][c]['nearest_'+concept+'_walking_minutes'].max()*speed/60)) for c in CITIES)
        limit=np.log1p(maximum)*1.02
        for ax,city in zip(axes[row],CITIES,strict=True):
            frame=data['frames'][city];e=frame['nearest_'+concept+'_euclidean_km'];w=frame['nearest_'+concept+'_walking_minutes']*speed/60
            artist=ax.hexbin(np.log1p(e),np.log1p(w),gridsize=30,mincnt=5,bins='log',extent=(0,limit,0,limit),cmap=theme.DENSITY)
            artists.append(artist)
            ax.plot([0,limit],[0,limit],color=theme.DARK[1],linestyle='--',lw=1.2);ax.set_xlim(0,limit);ax.set_ylim(0,limit)
            ticks=np.linspace(0,limit,4);labels=[f'{np.expm1(t):g}' if t==0 else f'{np.expm1(t):.1f}' for t in ticks]
            ax.set_xticks(ticks,labels);ax.set_yticks(ticks,labels);ax.set_title(LABELS[city]+(' — rail' if concept=='station' else ' — bus'))
            for xy,n in zip(artist.get_offsets(),artist.get_array(),strict=True):
                if n<5:raise ValueError('Private small bin')
                bins.append({'city':city,'concept':concept,'euclidean_km_bin_center':float(np.expm1(xy[0])),
                             'walking_km_bin_center':float(np.expm1(xy[1])),'n':int(n)})
            stats=next(r for r in data['interpretation'][city]['measurement'] if r['concept']==concept)
            ax.text(.04,.92,f"Spearman ρ = {stats['spearman']:.2f}",transform=ax.transAxes,fontsize=8)
    norm=LogNorm(vmin=5,vmax=max(float(a.get_array().max()) for a in artists))
    for artist in artists:artist.set_norm(norm)
    fig.colorbar(ScalarMappable(norm=norm,cmap=theme.DENSITY),ax=axes.ravel().tolist(),label='Listings per displayed hexagon',shrink=.75)
    fig.supxlabel('Straight-line distance (km)');fig.supylabel('Walking-equivalent distance (km)')
    reg.figure('nearest_access_relationship',fig,'RQ1',['sample','interpretation'],
               'Matched nearest-category Euclidean and walking-equivalent distances. Walking minutes convert using the frozen5 km/h speed. Plotting log(1+distance) retains zeros and tails; tick labels are km. Hexagons require n≥5. Colour shows logarithmic bin frequency; diagonal is equality. Nearest destinations may differ, so this is not same-destination circuity.',minimum_aggregate_n=5,page_orientation='landscape')
    reg.table('nearest_access_relationship_bins',pd.DataFrame(bins),'RQ1',['sample'],
              'Suppressed nearest-access hexagons; only bins with n≥5, no private locations or IDs.',category='metrics')
    fig,axes=grid(size=(7.2,3.4));maximum=float(tables['nearest_access_divergence'].p95.max())
    for ax,city in zip(axes[0],CITIES,strict=True):
        part=tables['nearest_access_divergence'].loc[lambda p:p.city==city].set_index('concept').loc[['station','bus']]
        y=np.arange(2);ax.hlines(y,part.p05,part.p95,color=theme.INK,lw=1);ax.hlines(y,part.p25,part.p75,color=theme.SAND,lw=5)
        ax.plot(part['median'],y,'o',color=COLOURS['Walking'],markerfacecolor=theme.SAND,ms=6);ax.set_yticks(y,['Rail','Bus']);ax.set_ylim(1.5,-.5);ax.set_title(LABELS[city]);ax.set_xlim(0,maximum*1.05);ax.axvline(0,color=theme.INK,lw=.8,ls='--')
    fig.supxlabel('Walking-equivalent minus straight-line nearest distance (km)')
    reg.figure('nearest_access_divergence',fig,'RQ1',['interpretation'],
               'Frozen nearest-category distance excess: median dots, interquartile thick bars and5th–95th percentile thin bars. These are distribution summaries, not confidence intervals or same-object route circuity.')
    fig,axes=grid(2,size=(7.2,5.8),sharey='row')
    for row,concept in enumerate(['food','culture']):
        for ax,city in zip(axes[row],CITIES,strict=True):
            part=tables['accessibility_descriptive_statistics'].loc[lambda p:(p.city==city)&(p.concept==concept)].set_index('representation').loc[['Euclidean','Walking']]
            for i,representation in enumerate(['Euclidean','Walking']):
                r=part.loc[representation];colour=COLOURS[representation];ax.vlines(i,r.p25,r.p75,color=colour,lw=1.8);ax.hlines([r.p25,r.p75],i-.06,i+.06,color=colour,lw=1.2);ax.plot(i,r['median'],'o',color=colour,markerfacecolor=theme.FILLS[colour],ms=7)
            ax.set_xticks([0,1],['Euclidean','Walking']);ax.set_xlim(-.5,1.5);ax.set_ylim(bottom=0);ax.set_title(LABELS[city]+('\nFood/social' if concept=='food' else '\nCulture/tourism'));ax.set_ylabel('Destinations')
    reg.figure('opportunity_comparison',fig,'RQ1',['interpretation'],
               'Median reachable destinations (dots) and interquartile ranges (bars) for frozen nominal10-minute walking and matched833 m Euclidean budgets. Same deduplicated category universe within each city. Zero counts are observed zeros; no route failures are filled.')


def prediction(data,tables,reg):
    performance=tables['primary_predictive_performance'];folds=tables['neighbourhood_performance'];contrasts=tables['paired_model_contrasts']
    fig,axes=grid(size=(7.2,3.8),sharey=True)
    for ax,city in zip(axes[0],CITIES,strict=True):
        for estimator,offset,marker in [('OLS',-.07,'o'),('XGBoost',.07,'s')]:
            part=performance.loc[(performance.city==city)&(performance.estimator==estimator)].set_index('model').loc[list(MODELS)]
            stats=folds.loc[(folds.city==city)&(folds.estimator==estimator)].groupby('model').rmse.quantile([.1,.9]).unstack().loc[list(MODELS)]
            x=np.arange(4)+offset;ax.vlines(x,stats[.1],stats[.9],color=theme.FILLS[COLOURS[estimator]],lw=1.5,alpha=.9)
            ax.plot(x,part.rmse,marker+'-',color=COLOURS[estimator],markerfacecolor=theme.FILLS[COLOURS[estimator]],label=estimator,ms=6)
        ax.set_xticks(range(4),MODELS);ax.set_title(LABELS[city]);ax.grid(axis='y',alpha=.2)
    fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=2);fig.supylabel('RMSE · log nightly price')
    reg.figure('primary_model_performance',fig,'RQ2',['neighbourhood','within_city'],
               'Points are pooled listing-weighted OOF RMSE. Whiskers are10th–90th percentiles of unweighted heldout-neighbourhood RMSE, not inferential confidence intervals; pooled points need not equal fold medians. Four models share each city’s observations and folds. Native-currency log outcomes; lower error is better.')
    fig,axes=grid(2,size=(10.5,6.3),sharey=True);order=[tuple(p) for p in data['design']['contrasts']]
    for row,estimator in enumerate(['OLS','XGBoost']):
        for ax,city in zip(axes[row],CITIES,strict=True):
            part=contrasts.loc[(contrasts.city==city)&(contrasts.estimator==estimator)].set_index(['added','reference']).loc[order]
            for i,r in enumerate(part.itertuples()):
                colour=theme.DARK[i%4];ax.vlines(i,r.stability_low,r.stability_high,color=colour,lw=1.8)
                ax.hlines([r.stability_low,r.stability_high],i-.07,i+.07,color=colour,lw=1.2)
                ax.plot(i,r.delta_rmse,'o',color=colour,markerfacecolor=theme.PALETTE[i%4],ms=6)
            ax.axhline(0,color=theme.INK,lw=1,ls='--');ax.set_xticks(range(5),[f'{a}\n− {b}' for a,b in order]);ax.set_title(LABELS[city]+' — '+estimator)
    fig.supylabel('ΔRMSE · log nightly price')
    reg.figure('paired_accessibility_contrasts',fig,'RQ2',['neighbourhood'],
               'All five primary paired comparisons. Bars are frozen95% geographic-composition stability ranges from2,000 neighbourhood resamples. They are not independent-sample confidence intervals; a range crossing zero does not establish equivalence. MW−ME is replacement; MEW−ME is network add-on.')
    fig,axes=grid(size=(10.5,5.2),sharex=True);terms=data['design']['blocks']['E']+data['design']['blocks']['W']
    for ax,city in zip(axes[0],CITIES,strict=True):
        part=tables['association_results'].loc[lambda p:(p.city==city)&(p.model=='MEW')].set_index('term').loc[terms]
        y=np.arange(len(terms));ax.hlines(y,part.hc3_ci_low,part.hc3_ci_high,color=theme.DARK[0],lw=1.7);ax.plot(part.coefficient,y,'o',color=theme.DARK[0],markerfacecolor=theme.BLUE,ms=6)
        ax.set_yticks(y,[textwrap.fill(FEATURE_LABELS[t],23) for t in terms]);ax.invert_yaxis();ax.axvline(0,color='grey',lw=.8);ax.set_title(LABELS[city])
    fig.supxlabel('Adjusted log-price coefficient per predictor unit')
    reg.figure('association_accessibility',fig,'RQ2',['association'],
               'Complete-case MEW adjusted observational associations, not causal effects or predictive importance. Rail/bus Euclidean predictors use km, walking uses minutes and opportunities use log(1+count); coefficient magnitudes across different units are not rankings. HC3 intervals shown;9,999-replication restricted Webb results are in the table. Uniform10% eligibility is a disclosed post-observation amendment.',page_orientation='landscape')
    shap=tables['heldout_feature_contributions'].loc[lambda p:p.model=='MEW']
    terms=shap.groupby('term').mean_abs.mean().sort_values(ascending=False).head(10).index.tolist()
    fig,axes=grid(size=(10.5,5),sharex=True)
    for ax,city in zip(axes[0],CITIES,strict=True):
        part=shap.loc[shap.city==city].set_index('term').reindex(terms)
        focal=set(data['design']['blocks']['E']+data['design']['blocks']['W'])
        ax.barh(range(len(terms)),part.mean_abs,color=[theme.SAND if t in focal else theme.BLUE for t in terms],height=.66);ax.set_yticks(range(len(terms)),[textwrap.fill(FEATURE_LABELS.get(t,t.replace('missingindicator_','Missing indicator: ').replace('property_type_','Property: ')),22) for t in terms]);ax.invert_yaxis();ax.set_title(LABELS[city])
    fig.supxlabel('Mean absolute heldout TreeSHAP contribution (log-price units)')
    reg.figure('heldout_feature_contributions',fig,'RQ2',['interpretation'],
               'Existing heldout XGBoost MEW contributions only; no new SHAP calculation or model fit. Ten encoded terms selected for display by across-city mean magnitude; this does not change the model. Unavailable encodings remain missing rather than zero. Each term’s actual support is in the table. Correlated E/W attribution is descriptive, not causal.',page_orientation='landscape')


def generalization(data,tables,reg):
    values=tables['validation_comparison'];fig,axes=grid(2,size=(10.5,7.2),sharey='row')
    for row,estimator in enumerate(['OLS','XGBoost']):
        for ax,city in zip(axes[row],CITIES,strict=True):
            for model in MODELS:
                part=values.loc[(values.city==city)&(values.estimator==estimator)&(values.model==model)].set_index('scheme').loc[SCHEMES]
                ax.plot(range(8),part.rmse,'o-',color=COLOURS[model],markerfacecolor=theme.FILLS[COLOURS[model]],label=model,ms=5,lw=1.5)
            ax.set_xticks(range(8),[VALIDATION_LABELS[s] for s in SCHEMES],rotation=60,ha='right');ax.set_title(LABELS[city]+' — '+estimator);ax.set_ylabel('OOF RMSE (log price)');ax.grid(axis='y',alpha=.2)
    fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=4)
    reg.figure('validation_strategy_comparison',fig,'RQ3',['validation'],
               'Pooled OOF errors on the same frozen city samples under random, primary neighbourhood and six fixed spatial-block configurations. Lines connect categorical designs, not a continuous treatment. Different holdout geometry changes the prediction task; overlapping training sets and correlated configurations prevent independent-replication claims.',page_orientation='landscape')
    folds=tables['neighbourhood_performance'];fig,axes=grid(size=(10.5,7.3),sharex=True)
    for ax,city in zip(axes[0],CITIES,strict=True):
        names=sorted(folds.loc[folds.city==city,'fold'].unique());y=np.arange(len(names))
        for estimator,offset,marker in [('OLS',-.12,'o'),('XGBoost',.12,'s')]:
            part=folds.loc[(folds.city==city)&(folds.estimator==estimator)].pivot(index='fold',columns='model',values='rmse').loc[names]
            ax.plot(part.MW-part.M0,y+offset,marker,color=COLOURS[estimator],markerfacecolor=theme.FILLS[COLOURS[estimator]],label=estimator,ms=6)
        ax.set_yticks(y,[textwrap.fill(str(n),19) for n in names]);ax.invert_yaxis();ax.axvline(0,color='grey',lw=.8);ax.set_title(LABELS[city]);ax.grid(axis='x',alpha=.2)
    fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=2);fig.supxlabel('ΔRMSE · walking model minus baseline')
    reg.figure('neighbourhood_performance_variation',fig,'RQ3',['within_city'],
               'Every primary heldout operational neighbourhood: paired walking-versus-baseline error for OLS and XGBoost. Dots are full-fold scores, not independent confidence intervals. Minimum15 test/500 complementary training support is unchanged; full names, counts and all four model scores are exported.',page_orientation='landscape')
    contrast=tables['robustness_contrasts'];scenarios=['primary',*ROBUSTNESS_LABELS.keys()];scenarios=list(dict.fromkeys(scenarios))
    fig,axes=grid(2,size=(10.5,9),sharex=True)
    for row,estimator in enumerate(['OLS','XGBoost']):
        for ax,city in zip(axes[row],CITIES,strict=True):
            primary=tables['paired_model_contrasts'].loc[lambda p:(p.city==city)&(p.estimator==estimator)&(p.added=='MW')&(p.reference=='M0')].assign(scenario='primary')
            part=pd.concat([primary,contrast.loc[(contrast.city==city)&(contrast.estimator==estimator)&(contrast.added=='MW')&(contrast.reference=='M0')]]).set_index('scenario')
            for y,scenario in enumerate(scenarios):
                if scenario in part.index:
                    r=part.loc[scenario];ax.hlines(y,r.stability_low,r.stability_high,color=COLOURS[estimator],lw=1.5);ax.plot(r.delta_rmse,y,'o',color=theme.NAVY if scenario=='primary' else COLOURS[estimator],markerfacecolor=theme.FILLS[COLOURS[estimator]],ms=5)
                else:ax.text(.97,y,'N/A',transform=ax.get_yaxis_transform(),ha='right',fontsize=7,color='grey')
            ax.set_yticks(range(len(scenarios)),[textwrap.fill(ROBUSTNESS_LABELS[s],21) for s in scenarios]);ax.invert_yaxis();ax.axvline(0,color='grey',lw=.8);ax.set_title(LABELS[city]+' — '+estimator)
    fig.supxlabel('ΔRMSE · walking model minus baseline')
    reg.figure('robustness_contrasts',fig,'RQ3',['robustness','neighbourhood'],
               'Every registered predictive family: paired MW−M0 point changes and frozen95% geographic-composition stability ranges. N/A denotes native density checks inapplicable to Copenhagen/Oslo; no value is filled. Samples and measurement definitions differ across rows, so this is not an absolute-score ranking or pass/fail test.',page_orientation='landscape')


def transfers(data,tables,reg):
    performance=tables['transfer_performance'];contrasts=tables['transfer_contrasts'];cities=list(CITIES)
    fig,axes=grid(2,4,size=(10.5,6.2));vmin=float(performance.rmse.min());vmax=float(performance.rmse.max())
    for row,estimator in enumerate(['OLS','XGBoost']):
        for ax,model in zip(axes[row],MODELS,strict=True):
            matrix=performance.loc[(performance.estimator==estimator)&(performance.model==model)].pivot(index='source_city',columns='target_city',values='rmse').reindex(index=cities,columns=cities)
            artist=ax.imshow(np.ma.masked_invalid(matrix.to_numpy()),vmin=vmin,vmax=vmax,cmap=theme.SEQUENTIAL)
            ax.set_facecolor('#F1F5F6');ax.set_title(estimator+' '+model);ax.set_xticks(range(3),[LABELS[c] for c in cities],rotation=45,ha='right');ax.set_yticks(range(3),[LABELS[c] for c in cities])
            for i in range(3):
                for j in range(3):
                    if i!=j:ax.text(j,i,f'{matrix.iloc[i,j]:.3f}',ha='center',va='center',fontsize=10,color=theme.annotation_colour(matrix.iloc[i,j],artist))
    fig.colorbar(artist,ax=axes.ravel().tolist(),label='Relative log-price RMSE',shrink=.72)
    reg.figure('transfer_performance',fig,'RQ4',['transfer'],
               'All six source→target directions for both estimators and all four models. Rows are source, columns target; diagonal is untested, never zero. Common colour scale. Source-only fitted pipelines and observed target price benchmarks are frozen; no target fitting/recalibration or absolute-price deployment.',page_orientation='landscape')
    fig,axes=grid(2,size=(10.5,6.3));part=contrasts.loc[contrasts.reference=='M0'];bound=float(max(abs(part.delta_rmse.min()),abs(part.delta_rmse.max())))
    for row,estimator in enumerate(['OLS','XGBoost']):
        for ax,model in zip(axes[row],['ME','MW','MEW'],strict=True):
            matrix=part.loc[(part.estimator==estimator)&(part.added==model)].pivot(index='source_city',columns='target_city',values='delta_rmse').reindex(index=cities,columns=cities)
            artist=ax.imshow(np.ma.masked_invalid(matrix.to_numpy()),vmin=-bound,vmax=bound,cmap=theme.DIVERGING);ax.set_facecolor('#F1F5F6');ax.set_title(estimator+': '+model+' − M0')
            ax.set_xticks(range(3),[LABELS[c] for c in cities],rotation=45,ha='right');ax.set_yticks(range(3),[LABELS[c] for c in cities])
            for i in range(3):
                for j in range(3):
                    if i!=j:ax.text(j,i,f'{matrix.iloc[i,j]:+.3f}',ha='center',va='center',fontsize=10,color=theme.annotation_colour(matrix.iloc[i,j],artist))
    fig.colorbar(artist,ax=axes.ravel().tolist(),label='Δ relative RMSE; negative improves',shrink=.7)
    reg.figure('transfer_accessibility_gains',fig,'RQ4',['transfer'],
               'All six directional accessibility-versus-baseline point contrasts. Same target observations within every comparison; negative values favour accessibility. These correlated directional results are not pooled into an independent significance test.',page_orientation='landscape')
    pairs=[(s,t) for s in CITIES for t in CITIES if s!=t];fig,axes=grid(2,2,size=(10.5,7.2),sharex=True,sharey=True)
    for row,estimator in enumerate(['OLS','XGBoost']):
        for ax,comparison in zip(axes[row],[('MW','ME'),('MEW','ME')],strict=True):
            part=contrasts.loc[(contrasts.estimator==estimator)&(contrasts.added==comparison[0])&(contrasts.reference==comparison[1])].set_index(['source_city','target_city']).loc[pairs]
            intervals(ax,part,np.arange(6),COLOURS[estimator]);ax.set_yticks(range(6),[LABELS[s]+' → '+LABELS[t] for s,t in pairs]);ax.set_ylim(5.5,-.5);ax.axvline(0,color='grey',lw=.8);ax.set_title(estimator+': '+comparison[0]+' − '+comparison[1])
    fig.supxlabel('Δ relative RMSE; negative improves')
    reg.figure('transfer_network_comparison',fig,'RQ4',['transfer'],
               'Direct network replacement (MW−ME) and add-on (MEW−ME) for all six directions. Bars are existing95% target-neighbourhood composition stability ranges; they do not establish independent directions or equivalence.',page_orientation='landscape')
    fig,axes=grid(2,size=(10.5,7.0));diagnostic_bins=[]
    selected={k:f for k,f in data['transfer_predictions'].items() if k[2:] == ('XGBoost','MEW')}
    low=min(float(min(f.relative_log_price.min(),f.prediction.min())) for f in selected.values());high=max(float(max(f.relative_log_price.max(),f.prediction.max())) for f in selected.values());edges=np.linspace(low,high,41)
    diagnostic_artists=[]
    for ax,(source,target) in zip(axes.ravel(),pairs,strict=True):
        frame=selected[(source,target,'XGBoost','MEW')];counts,x,y=np.histogram2d(frame.relative_log_price,frame.prediction,bins=[edges,edges])
        masked=np.ma.masked_where(counts.T<5,counts.T);diagnostic_artists.append(ax.pcolormesh(x,y,masked,cmap=theme.DENSITY,shading='flat'));ax.plot([low,high],[low,high],'--',color=theme.DARK[1],lw=1.2)
        ax.set_xlim(low,high);ax.set_ylim(low,high);ax.set_aspect('equal');ax.set_title(LABELS[source]+' → '+LABELS[target]);ax.set_xlabel('Observed relative log price');ax.set_ylabel('Predicted relative log price')
        score=performance.loc[(performance.source_city==source)&(performance.target_city==target)&(performance.estimator=='XGBoost')&(performance.model=='MEW')].iloc[0]
        ax.text(.03,.92,f'RMSE={score.rmse:.3f}; N={int(score.n):,}',transform=ax.transAxes,fontsize=8)
        for i,j in np.argwhere(counts>=5):diagnostic_bins.append({'source_city':source,'target_city':target,'estimator':'XGBoost','model':'MEW',
            'observed_bin_low':float(x[i]),'observed_bin_high':float(x[i+1]),'predicted_bin_low':float(y[j]),'predicted_bin_high':float(y[j+1]),'n':int(counts[i,j])})
    norm=LogNorm(vmin=5,vmax=max(float(a.get_array().max()) for a in diagnostic_artists))
    for artist in diagnostic_artists:artist.set_norm(norm)
    fig.colorbar(ScalarMappable(norm=norm,cmap=theme.DENSITY),ax=axes.ravel().tolist(),label='Target listings per displayed bin',shrink=.7)
    reg.figure('transfer_prediction_diagnostics',fig,'RQ4',['transfer_predictions','transfer'],
               'Saved XGBoost MEW predictions versus actual relative log price in all six directions. Only aggregate rectangular bins with n≥5 are displayed; every target row remains in full metrics. Shared axes; diagonal is perfect relative prediction. No row export, target fitting, smoothing or recalibration.',minimum_aggregate_n=5,page_orientation='landscape')
    reg.table('transfer_prediction_bins',pd.DataFrame(diagnostic_bins),'RQ4',['transfer_predictions'],
              'Suppressed aggregate price-prediction bins with n≥5; no individual price/prediction pairs or identifiers.',category='diagnostics')
    asym=tables['directional_transfer_asymmetry'];fig,axes=grid(1,2,size=(7.2,4.3),sharex=True)
    for ax,estimator in zip(axes[0],['OLS','XGBoost'],strict=True):
        part=asym.loc[asym.estimator==estimator];names=[(LABELS[CITIES[i]],LABELS[CITIES[j]]) for i,j in [(0,1),(0,2),(1,2)]]
        for offset,model in zip([-.24,-.08,.08,.24],MODELS,strict=True):
            rows=part.loc[part.model==model].set_index(['first_city','second_city']).loc[names]
            ax.plot(rows.forward_minus_reverse_rmse,np.arange(3)+offset,'o',color=COLOURS[model],markerfacecolor=theme.FILLS[COLOURS[model]],label=model,ms=6)
        ax.set_yticks(range(3),[a+' ↔ '+b for a,b in names]);ax.invert_yaxis();ax.axvline(0,color='grey',lw=.8);ax.set_title(estimator)
    fig.legend(*axes[0,0].get_legend_handles_labels(),loc='outside upper center',ncol=4);fig.supxlabel('RMSE(first → second) − RMSE(second → first)')
    reg.figure('directional_transfer_asymmetry',fig,'RQ4',['transfer'],
               'All three reversed city pairs for both estimators and every model. Descriptive differences only: changing direction changes training city, target distribution and sample size. No independent-direction test or exchangeability assumption is made.')


def spatial(tables,reg):
    df=tables['residual_spatial_diagnostics'];fig,axes=grid(size=(7.2,3.6),sharex=True)
    for ax,city in zip(axes[0],CITIES,strict=True):
        part=df.loc[df.city==city].copy();labels=['Observed outcome' if r.variable=='log_price' else ('XGB' if r.estimator=='XGBoost' else r.estimator)+' '+r.model for r in part.itertuples()]
        fills=[theme.LILAC if r.variable=='log_price' else theme.BLUE if r.model=='M0' else theme.SAND for r in part.itertuples()]
        ax.barh(range(len(part)),part.moran_i,color=fills,height=.66);ax.set_yticks(range(len(part)),labels);ax.invert_yaxis();ax.set_title(LABELS[city]);ax.set_xlabel("Moran's I")
        for y,r in enumerate(part.itertuples()):ax.text(r.moran_i,y,f' p={r.permutation_p_two_sided:.3f}',va='center',fontsize=7)
        ax.margins(x=.35)
    reg.figure('residual_spatial_diagnostics',fig,'Appendix',['spatial'],
               'Frozen8-nearest-neighbour/499-permutation diagnostics for observed outcomes and primary OOF residuals. City metric CRSs retained. Material OLS MW residual dependence triggered the registered spatial-error association sensitivity in each city; prediction gains are not a claim of independent residuals.',spatial_crs={c:reg.data['cities'][c]['metric_crs'] for c in CITIES})


def run(revise=False,preview=None):
    destination=ROOT/'reports/thesis_artifact_manifest.json'
    if preview is not None:
        baseline=json.loads((ROOT/'archive/before_figure_style/manifest.json').read_text())
        for item in baseline['numeric_exports_immutable']:
            if sha256_file(ROOT/item['original_path'])!=item['sha256']:raise ValueError('Published numerical export changed')
        if preview.exists():raise ValueError('Style preview must use a new output directory')
        preview.mkdir(parents=True);revise=True
    if destination.exists() and not revise:raise ValueError('Thesis artifacts exist; use verification or explicit pending-layout revision')
    if revise and preview is None:
        if (ROOT/'reports/thesis_delivery_audit.json').exists():raise ValueError('Reviewed release cannot be overwritten')
        prior=json.loads(destination.read_text())
        if prior['status']!='GENERATED_PENDING_VISUAL_AND_RELEASE_REVIEW':raise ValueError('Only unpublished pending-layout drafts may be revised')
        if not (ROOT/'archive/implementation/thesis_first_layout_manifest.json').exists():
            write_once(ROOT/'archive/implementation/thesis_first_layout_manifest.json',destination.read_bytes())
    data=load();tables=build(data);reg=Registry(data,revise,preview);setup_style()
    role={name:(rq,[source]) for _,_,rq,name,_,source in TABLES}
    for name in [r[3] for r in TABLES]:
        rq,roles=role[name]
        if name=='city_sample_summary':roles=['sample','reference','association']
        caption={'primary_predictive_performance':'Primary neighbourhood OOF RMSE by city/estimator/model; full CSV also retains MAE, R² and correlation. Four models share rows/folds.',
                 'paired_model_contrasts':'Candidate minus reference; negative improves. Existing95% geographic-composition stability ranges, not independent-sample confidence intervals; crossing zero is not equivalence.',
                 'association_results':'Full four-model complete-case OLS/HC3 and9,999 restricted Webb results in CSV. Display shows MEW accessibility terms. Uniform10% eligibility was amended after observing missingness; no inferential imputation or causal interpretation.',
                 'validation_comparison':'Spatial-block cells show the range over all six fixed configurations, not a pooled score. Full CSV retains every configuration and model.',
                 'transfer_performance':'Relative-price RMSE on all six source-only directions; no target fitting/recalibration; diagonal not tested. Full CSV retains MAE, R², Pearson and Spearman.',
                 'transfer_contrasts':'All five paired contrasts for six directions/two estimators; negative improves. Frozen95% target-neighbourhood composition stability ranges.'}.get(name,'Generated from explicitly pinned final SQL/results; definitions, selection limits and source identities remain unchanged.')
        reg.table(name,tables[name],rq,roles,caption,presentation(name,tables[name],data))
    for name,category,rq,roles in [('sample_flow','tables','Design',['sample']),('nearest_access_divergence','metrics','RQ1',['interpretation']),
                                 ('neighbourhood_performance','metrics','RQ3',['within_city']),('neighbourhood_support','diagnostics','Design',['sample']),
                                 ('robustness_contrasts','metrics','RQ3',['robustness']),('heldout_feature_contributions','metrics','RQ2',['interpretation']),
                                 ('directional_transfer_asymmetry','metrics','RQ4',['transfer']),('residual_spatial_diagnostics','diagnostics','Appendix',['spatial'])]:
        reg.table(name,tables[name],rq,roles,'Complete safe aggregate evidence; no individual source/prediction/location rows.',category=category)
    maps(data,reg);measurement(data,tables,reg);prediction(data,tables,reg);generalization(data,tables,reg);transfers(data,tables,reg);spatial(tables,reg)
    manifest={'status':'GENERATED_PENDING_VISUAL_AND_RELEASE_REVIEW','generation_command':COMMAND,
              'source_catalog_sha256':data['catalog']['source_catalog_sha256'],'models_refitted':False,'scientific_reconstruction':False,
              'items':reg.items,'layout_checks':reg.layout,'scientific_choice_changes':False,
              'style':{**theme.reference(),'city_order':[LABELS[c] for c in CITIES],
                       'model_order':list(MODELS),'delta_sign':'candidate minus reference; negative improves','deterministic_SVG_hashsalt':'frozen_thesis_pastel'}}
    manifest['generation_dependencies']={str(p.relative_to(ROOT)):sha256_file(p) for p in [*[ROOT/'src/reporting'/name for name in ['thesis_audit.py','thesis_sources.py','thesis_tables.py','thesis_outputs.py','thesis_style.py','thesis_refresh.py']],ROOT/'src/pipeline/reporting_figures.py',ROOT/'docs/analysis/data_dictionary.md',ROOT/'requirements.txt']}
    if preview is not None:
        manifest['presentation_refresh']={'prior_checkpoint':baseline['base_checkpoint'],'prior_manifest':'archive/before_figure_style/reports/thesis_artifact_manifest.json','numerical_exports_byte_identical':True,'user_requested_style':'Existing V3 pastel figures','preview_directory':str(preview)}
        write_once(preview/'thesis_artifact_manifest.json',(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode())
    elif revise:
        manifest['draft_layout_revision']='External legends; shared-axis ordering; compact divergence rows; common count colour scales; numeric/aggregate tables byte-identical'
        destination.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    else:write_once(destination,(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode())
    return {'figures':len(FIGURES),'artifact_files':len(reg.items),'tables_and_aggregate_views':len({r['logical_name'] for r in reg.items if r['kind']=='table'}),
            'out_of_canvas_text':{r['figure']:r['out_of_canvas_text'] for r in reg.layout if r['out_of_canvas_text']},'models_refitted':False,'preview_directory':str(preview) if preview else None}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--revise-layout',action='store_true')
    print(json.dumps(run(parser.parse_args().revise_layout),indent=2))
