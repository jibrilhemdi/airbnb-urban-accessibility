"""Pastel thesis figures from frozen PostgreSQL results; no model fitting.

All map coordinates use EPSG:25832. Listing maps disclose 500 m cell summaries
only where at least five observations have a nonmissing plotted value.
"""
from __future__ import annotations
import html
import json
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm, ListedColormap
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, Patch
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT, write_json, sha256_file
from src.pipeline.output_paths import output_file
from src.pipeline.storage import load_artifact
from src.pipeline.run_spatial_diagnostics import residual_coordinates

NAVY='#183449'; INK='#486174'; BLUE='#A9C8D7'; SAND='#E9BF86'; GREEN='#B7D4C4'; LILAC='#CEC2DE'
PALETTE=[BLUE,SAND,GREEN,LILAC]; DARK=['#527F96','#AF7F42','#608A77','#88759E']
SEQUENTIAL=LinearSegmentedColormap.from_list('pastel_blue',['#F1F5F6','#C7DDE4','#94B9CB','#5D8DA5'])
DENSITY=LinearSegmentedColormap.from_list('pastel_density',['#DCE9EF','#A9C8D7','#5D8DA5'])
DIVERGING=LinearSegmentedColormap.from_list('pastel_signed',['#7FAABC','#F8F7F3','#DFB176'])
MODEL_LABELS={'M0':'Baseline','ME':'Euclidean','MW':'Walking','MEW':'Combined'}
LABELS={'nearest_station_walking_minutes':'Rail station · walking minutes','nearest_bus_walking_minutes':'Bus stop · walking minutes',
 'nearest_station_euclidean_km':'Rail station · straight-line km','nearest_bus_euclidean_km':'Bus stop · straight-line km',
 'log1p_food_w':'Food & social · log(1 + walking count)','log1p_culture_w':'Culture & tourism · log(1 + walking count)',
 'log1p_food_e':'Food & social · log(1 + straight-line count)','log1p_culture_e':'Culture & tourism · log(1 + straight-line count)',
 'distance_centre_euclidean_km':'Distance to City Hall · km','income_100k_dkk':'Area income · 100,000 DKK',
 'log_population_density':'Area population density · log','log1p_minimum_nights':'Minimum nights · log(1 + nights)',
 'log1p_host_listings_count':'Host listings · log(1 + count)','bathrooms_effective':'Bathrooms','accommodates':'Guest capacity',
 'bedrooms':'Bedrooms','superhost':'Superhost'}
CATEGORIES={1:'Research workflow',2:'Study area and listings',3:'Price distribution and spatial pattern',4:'Euclidean and network catchments',
 5:'Accessibility measure comparison',6:'Accessibility interpretation',7:'Random and geographic performance',8:'Validation geography',9:'Residual spatial diagnostics'}

def label(feature):
    if feature in LABELS:return LABELS[feature]
    if feature.startswith('property_type_'):return 'Property · '+feature.removeprefix('property_type_')
    if feature.startswith('missingindicator_'):return 'Missing · '+label(feature.removeprefix('missingindicator_'))
    return feature.removeprefix('amenity_').replace('_',' ').capitalize()

def grid_summary(frame,variable,size=500,minimum=5):
    """Suppress small nonmissing cells without substituting missing values."""
    data=frame[['metric_x','metric_y',variable]].copy()
    if data[['metric_x','metric_y']].isna().any().any():raise ValueError('Missing map coordinates')
    data['gx']=np.floor(data.metric_x/size);data['gy']=np.floor(data.metric_y/size)
    grouped=data.groupby(['gx','gy'])[variable].agg(n='count',value='median').reset_index()
    return grouped.loc[grouped.n>=minimum].copy()

def join_features(part,frame):
    left=part.copy();right=frame.copy();keys=['snapshot_date','listing_id']
    for table in (left,right):
        table['snapshot_date']=table.snapshot_date.astype(str).str[:10]
        pd.to_datetime(table.snapshot_date,format='%Y-%m-%d',errors='raise')
    result=left.merge(right,on=keys,validate='one_to_one',suffixes=('','_source'))
    if len(result)!=len(left) or len(result)!=len(right):raise ValueError('Held-out join lost frozen observations')
    return result

def poi_reachability(pois,cost,budget):
    """Reach uses directed node distance plus the stored endpoint connector."""
    if pois[['snapped_node_id','snap_distance_m']].isna().any().any():raise ValueError('Missing POI routing evidence')
    if (pois.snap_distance_m<0).any():raise ValueError('Negative POI snap connector')
    return np.array([cost.get(int(r.snapped_node_id),np.inf)+float(r.snap_distance_m)<=budget for r in pois.itertuples()],dtype=bool)


class Figures:
    def __init__(self,engine,run_id,frame,tables):
        self.engine=engine;self.run_id=run_id;self.frame=frame;self.tables=tables;self.records=[]
        plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':NAVY,'axes.labelcolor':INK,
            'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#D4DFE4','axes.titleweight':'bold',
            'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white',
            'savefig.facecolor':'white'})
        with engine.connect() as conn:
            self.areas=pd.read_sql(text('SELECT area_id,area_name,ST_AsGeoJSON(geom_25832) AS geojson,ST_X(ST_PointOnSurface(geom_25832)) AS x,ST_Y(ST_PointOnSurface(geom_25832)) AS y FROM v3_spatial.analysis_areas ORDER BY area_id'),conn)
            self.context=conn.execute(text("SELECT ST_AsGeoJSON(c.geom_25832) FROM v3_spatial.map_context_municipalities c CROSS JOIN v3_spatial.study_area s WHERE s.area_kind='official_study_area' AND c.municipality_code NOT IN ('0101','0147') AND ST_DWithin(c.geom_25832,s.geom_25832,3500)")).scalars().all()
            self.bounds=conn.execute(text('SELECT ST_XMin(g),ST_YMin(g),ST_XMax(g),ST_YMax(g) FROM (SELECT ST_Extent(geom_25832)::geometry g FROM v3_spatial.analysis_areas) q')).one()
        self.names=dict(zip(self.areas.area_id,self.areas.area_name))

    def canvas(self,title,subtitle='',shape=(1,1),size=(11,6.6)):
        fig,axes=plt.subplots(*shape,figsize=size,squeeze=False)
        fig.subplots_adjust(left=.11,right=.95,bottom=.14,top=.85,wspace=.27,hspace=.42)
        fig.text(.065,.965,title,fontsize=18,weight='bold',color=NAVY)
        fig.text(.065,.920,subtitle,fontsize=10,color=INK)
        return fig,axes

    def save(self,fig,name,title,category,caption,source='v3_analysis primary_models',crs=None):
        # Measure visible chart decorations and legends, so footnotes follow
        # the actual content rather than a fixed, oversized bottom margin.
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
        boxes=[ax.get_tightbbox(renderer) for ax in fig.axes if ax.get_visible()]
        boxes.extend(artist.get_window_extent(renderer) for artist in [*fig.legends,*fig.texts[2:]] if artist.get_visible())
        content_top=max(box.y1 for box in boxes if box is not None)
        content_bottom=min(box.y0 for box in boxes if box is not None)
        point_height=fig.dpi/72/fig.bbox.height
        subtitle_y=content_top/fig.bbox.height+12*point_height
        fig.texts[1].set_position((.065,subtitle_y))
        fig.texts[0].set_position((.065,subtitle_y+22*point_height))
        caption_y=(content_bottom-12*fig.dpi/72)/fig.bbox.height
        fig.text(.065,caption_y,textwrap.fill(caption,max(95,int(fig.get_figwidth()*12))),fontsize=8,color=INK,va='top')
        path=output_file('figures','reporting',name+'.png');path.parent.mkdir(parents=True,exist_ok=True)
        fig.savefig(path,dpi=220,bbox_inches='tight',pad_inches=.14)
        paths=[path.relative_to(PROJECT_ROOT).as_posix()]
        # Only obsolete generated siblings in the active reporting folder.
        for suffix in ('.pdf','.svg'):path.with_suffix(suffix).unlink(missing_ok=True)
        plt.close(fig)
        self.records.append({'name':name,'title':title,'planned_category':category,'caption':caption,'source':source,'crs_epsg':crs,
            'paths':paths,'sha256':{p:sha256_file(PROJECT_ROOT/p) for p in paths}})

    def clean(self,ax,axis='x'):
        ax.set_axisbelow(True);ax.grid(axis=axis,color='#E7EEF1',linewidth=.8);ax.tick_params(length=0,pad=7)

    def base_map(self,ax,area_values=None,cmap=SEQUENTIAL,norm=None,ids=False):
        from src.pipeline.build_analysis_areas import _rings
        for geo in self.context:_rings(ax,json.loads(geo),fill='#E4EAE7',edge='#BAC8C2',linewidth=.4)
        for r in self.areas.itertuples():
            fill='#F5F6F2' if area_values is None else cmap(norm(area_values[r.area_id]))
            _rings(ax,json.loads(r.geojson),fill=fill,edge='#9FB4BD',linewidth=.6)
        xmin,ymin,xmax,ymax=self.bounds;pad=max(xmax-xmin,ymax-ymin)*.07
        ax.set(xlim=(xmin-pad,xmax+pad),ylim=(ymin-pad,ymax+pad),aspect='equal',facecolor='#EEF4F7')
        ax.set_xticks([]);ax.set_yticks([])
        for spine in ax.spines.values():spine.set_visible(False)
        ax.annotate('N',xy=(.92,.96),xytext=(.92,.85),xycoords='axes fraction',ha='center',weight='bold',fontsize=9,
            arrowprops={'arrowstyle':'-|>','color':NAVY},zorder=15)
        x=xmin+.05*(xmax-xmin);y=ymin+.01*(ymax-ymin)
        ax.plot([x,x+2000],[y,y],lw=2,color=NAVY,zorder=15);ax.text(x+1000,y+180,'2 km',ha='center',fontsize=8,zorder=15,
            bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':2})
        if ids:self.area_ids(ax)

    def area_ids(self,ax):
        for r in self.areas.itertuples():
            code=r.area_id.removeprefix('cph_') if r.area_id.startswith('cph_') else 'F'
            ax.text(r.x,r.y,code,ha='center',va='center',fontsize=8,weight='bold',zorder=14,
                bbox={'boxstyle':'round,pad=.25','facecolor':'white','alpha':.85,'edgecolor':'none'})

    def outlines(self,ax):
        from src.pipeline.build_analysis_areas import _rings
        for geo in self.areas.geojson:_rings(ax,json.loads(geo),fill='none',edge='#668A9A',linewidth=.55,outline_only=True)

    def cells(self,ax,grid,cmap,norm,size=500):
        for r in grid.itertuples():ax.add_patch(Rectangle((r.gx*size,r.gy*size),size,size,facecolor=cmap(norm(r.value)),edgecolor='none',zorder=2.5))
        self.outlines(ax)

    def district_key(self,fig,x=.735,y=.635):
        """Map IDs are paired with the actual official names, never inferred."""
        fig.text(x,y,'Analysis area key',fontsize=10,weight='bold',color=NAVY)
        for i,r in enumerate(self.areas.itertuples()):
            code=r.area_id.removeprefix('cph_') if r.area_id.startswith('cph_') else 'F'
            row_y=y-.046-i*.038
            fig.text(x,row_y,code,fontsize=9,weight='bold',color=NAVY)
            fig.text(x+.033,row_y,r.area_name,fontsize=9,color=INK)

    def shared_category_rows(self,fig,axes,left=.17,common_x=True):
        """Share row positions and show their category labels once per row."""
        for row in axes:
            reference=row[0]
            ticks=reference.get_yticks()
            labels=[t.get_text() for t in reference.get_yticklabels()]
            for ax in row[1:]:
                if not np.array_equal(ticks,ax.get_yticks()) or labels!=[t.get_text() for t in ax.get_yticklabels()]:
                    raise ValueError('Cannot share category axes with different rows')
                ax.sharey(reference)
                ax.tick_params(axis='y',labelleft=False,left=False)
                ax.spines['left'].set_visible(False)
        if common_x:
            for row in axes:
                limits=[ax.get_xlim() for ax in row]
                for ax in row:ax.set_xlim(min(p[0] for p in limits),max(p[1] for p in limits))
        for ax in axes.flat:ax.xaxis.set_major_locator(MaxNLocator(nbins=5,min_n_ticks=3))
        fig.subplots_adjust(left=left,wspace=.16)

    def map_figure(self,variable,title,unit,category=3,frame=None,name=None,signed=False,extra=''):
        data=self.frame if frame is None else frame;grid=grid_summary(data,variable)
        if grid.empty:raise RuntimeError('No disclosable map cells')
        fig,axes=self.canvas(title,'Median within 500 m cells · at least five observed values per cell',size=(12.6,8.8));ax=axes[0,0]
        fig.subplots_adjust(left=.055,right=.69,bottom=.12,top=.86)
        self.base_map(ax)
        if signed:
            limit=max(abs(grid.value.min()),abs(grid.value.max()),1e-9);norm=TwoSlopeNorm(0,-limit,limit);cmap=DIVERGING
        else:norm=Normalize(grid.value.min(),grid.value.max());cmap=SEQUENTIAL
        self.cells(ax,grid,cmap,norm);self.area_ids(ax)
        cax=fig.add_axes([.735,.75,.215,.018]);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal')
        fig.text(.735,.805,unit.replace('\n',' '),fontsize=9,color=INK)
        self.district_key(fig)
        self.save(fig,name or variable+'_map',title,category,
            'Cells with fewer than five nonmissing observations are suppressed. Official area boundaries; projected CRS EPSG:25832. '+extra,source=('v3_analysis.dataset_records; v3_spatial official areas' if frame is None else 'v3_analysis primary_models/oof_predictions and spatial_moran; v3_spatial official areas'),crs=25832)

    def workflow(self):
        fig,axes=self.canvas('From listings to held-out evidence','Version 3 research design · the completed analysis, step by step',size=(12,7));ax=axes[0,0];ax.set_axis_off()
        steps=[('01  Sources','Inside Airbnb · official geography\nArea context · OSM destinations'),('02  Spatial measures','Straight-line and walking access\nSeparate rail, bus and opportunities'),('03  Common sample',f'{len(self.frame):,} observed prices · 11 areas\nFrederiksberg is one peer area'),('04  Validation','Random 5-fold · geographic 11-fold\nSaved outer and inner assignments'),('05  Models','OLS inference · XGBoost prediction\nTraining-only preprocessing and tuning'),('06  Interpretation','Held-out errors and SHAP\nSpatial diagnostics · prespecified checks')]
        for i,(heading,body) in enumerate(steps):
            col=i%3;row=i//3;x=col*.345;y=.62-row*.52
            ax.add_patch(FancyBboxPatch((x,y),.30,.34,boxstyle='round,pad=.012,rounding_size=.025',facecolor=PALETTE[i%4],edgecolor='none',transform=ax.transAxes))
            ax.text(x+.02,y+.26,heading,transform=ax.transAxes,weight='bold',fontsize=11)
            ax.text(x+.02,y+.10,body,transform=ax.transAxes,fontsize=9,linespacing=1.8)
            if col<2:ax.annotate('',xy=(x+.335,y+.17),xytext=(x+.305,y+.17),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':INK})
        self.save(fig,'research_workflow','Research workflow',1,'Thirty frozen candidates and four inner folds per XGBoost tuning group. Income has qualified cross-source comparability; the no-income sensitivity is mandatory.',source='config/research_design.json; completed run metadata')

    def study(self):
        with self.engine.connect() as conn:
            stations=pd.read_sql(text('SELECT ST_X(geom_25832) x,ST_Y(geom_25832) y FROM v3_spatial.transit_stations'),conn)
            bus=pd.read_sql(text('SELECT ST_X(geom_25832) x,ST_Y(geom_25832) y FROM v3_spatial.canonical_bus_stops'),conn)
        fig,axes=self.canvas('The study area and analytical sample','Ten Copenhagen districts and Frederiksberg · public transport destinations',shape=(1,2),size=(13,8))
        for ax in axes.flat:self.base_map(ax)
        grid=grid_summary(self.frame.assign(listing_count=1),'listing_count');grid['value']=grid.n
        norm=Normalize(grid.n.min(),grid.n.max());self.cells(axes[0,0],grid,SEQUENTIAL,norm);self.area_ids(axes[0,0])
        axes[0,0].set_title('Listings per 500 m cell',loc='left',fontsize=11,pad=12)
        cax=fig.add_axes([.16,.17,.25,.016]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=SEQUENTIAL),cax=cax,orientation='horizontal');cb.set_label('Observed-price listings')
        ax=axes[0,1];ax.scatter(bus.x,bus.y,s=3,color='#CEA16A',alpha=.65,zorder=4,label='Canonical bus stops')
        ax.scatter(stations.x,stations.y,s=15,color='#527F96',edgecolor='white',lw=.4,zorder=5,label='Rail / metro / S-train');self.area_ids(ax)
        ax.set_title('Transport destination universe',loc='left',fontsize=11,pad=12);ax.legend(loc='upper center',bbox_to_anchor=(.5,-.04),fontsize=8,frameon=False,ncol=2)
        self.save(fig,'study_area_listings','Study area, listings and transport',2,'Listing cells with N < 5 are suppressed. Public destinations from the frozen OSM universe; map extent is the official study area. EPSG:25832.',source='v3_analysis.dataset_records; v3_spatial official areas and transport',crs=25832)

    def distributions(self):
        fig,axes=self.canvas('The distribution of nightly prices',f'{len(self.frame):,} observed-price listings · the same frozen sample in both panels',shape=(1,2))
        upper=self.frame.price_nightly.quantile(.99)
        ax=axes[0,0];ax.hist(self.frame.price_nightly,bins=np.linspace(0,upper,45),color=BLUE,edgecolor='white',lw=.6)
        ax.set(xlabel='Nightly price (DKK)',ylabel='Listings',title='Original price scale')
        omitted=int((self.frame.price_nightly>upper).sum());ax.text(.97,.95,f'Above plotted range: {omitted:,}\n99th percentile: {upper:,.0f} DKK',transform=ax.transAxes,ha='right',va='top',fontsize=9)
        ax=axes[0,1];ax.hist(self.frame.log_price,bins=45,color=SAND,edgecolor='white',lw=.6);ax.set(xlabel='Natural log of nightly price',ylabel='Listings',title='Full log-price distribution')
        for ax in axes.flat:self.clean(ax,'y')
        axes[0,1].set_ylabel('')
        self.save(fig,'price_distributions','Nightly price distributions',3,'The DKK panel displays values up to the 99th percentile for readability; no observations are removed from analysis. The log-price panel includes the full frozen sample.',source='v3_analysis.dataset_records')

    def comparison(self):
        pairs=[('nearest_station_euclidean_km','nearest_station_walking_minutes','Rail station'),('nearest_bus_euclidean_km','nearest_bus_walking_minutes','Bus stop'),('log1p_food_e','log1p_food_w','Food & social opportunities'),('log1p_culture_e','log1p_culture_w','Culture & tourism opportunities')]
        fig,axes=self.canvas('Straight-line and walking measures','Observed accessibility across the common listing sample',shape=(2,2),size=(12,9))
        for ax,(x,y,title) in zip(axes.flat,pairs):
            a=self.frame[x];b=self.frame[y];xx=a*12 if x.endswith('_km') else a
            ax.hexbin(xx,b,gridsize=42,mincnt=1,cmap=DENSITY,linewidths=0,rasterized=True)
            limits=[min(xx.min(),b.min()),max(xx.max(),b.max())];ax.plot(limits,limits,'--',color='#AF7F42',lw=1)
            ax.set_title(title,loc='left',fontsize=11)
            ax.set_xlabel('Straight-line equivalent minutes at 5 km/h' if x.endswith('_km') else 'Straight-line · log(1 + count)',fontsize=9)
            ax.set_ylabel('Walking minutes' if x.endswith('_km') else 'Walking · log(1 + count)',fontsize=9)
            ax.text(.04,.92,f'Spearman ρ = {a.corr(b,method="spearman"):.2f}',transform=ax.transAxes,fontsize=9)
            self.clean(ax,'both')
        self.save(fig,'measure_comparison','Euclidean versus walking measures',5,'Dashed lines denote equal values. Straight-line proximity is converted at 12 minutes per kilometre for display only; destination identities may differ. Opportunities use matched 833 m / 10 minute budgets. Darker blue denotes denser bins.',source='v3_analysis.dataset_records')

    def vertical_comparison(self,fig,axes,common_y=True,bottom=.22):
        """Upright categories and a shared value axis where units agree."""
        for row in axes:
            reference=row[0]
            ticks=reference.get_xticks();labels=[t.get_text() for t in reference.get_xticklabels()]
            for ax in row[1:]:
                if not np.array_equal(ticks,ax.get_xticks()) or labels!=[t.get_text() for t in ax.get_xticklabels()]:
                    raise ValueError('Cannot align charts with different categories')
            if common_y:
                limits=[ax.get_ylim() for ax in row]
                reference.set_ylim(min(p[0] for p in limits),max(p[1] for p in limits))
                for ax in row[1:]:
                    ax.sharey(reference);ax.tick_params(axis='y',labelleft=False,left=False);ax.set_ylabel('');ax.spines['left'].set_visible(False)
        for ax in axes.flat:ax.yaxis.set_major_locator(MaxNLocator(nbins=5,min_n_ticks=3));self.clean(ax,'y')
        fig.subplots_adjust(left=.10,right=.95,bottom=bottom,wspace=.13)

    @staticmethod
    def vertical_interval(ax,x,low,high,value,color,fill,cap=.065,filled=True):
        ax.vlines(x,low,high,color=color,lw=1.8)
        ax.hlines([low,high],x-cap,x+cap,color=color,lw=1.2)
        ax.scatter(x,value,s=50,facecolor=fill if filled else 'white',edgecolor=color,zorder=3)

    @staticmethod
    def contrast_label(added,reference):
        return MODEL_LABELS[added]+'\nvs '+MODEL_LABELS[reference].lower()

    def performance(self):
        part=self.tables['model_performance'];fig,axes=self.canvas('Prediction within and across areas','Pooled held-out error · lower RMSE is better',shape=(1,2),size=(12,6.7))
        for ax,scheme,title in zip(axes.flat,['random_5','geographic_11'],['Random · five folds','Geographic · eleven held-out areas']):
            for model,marker,color in [('OLS','o',DARK[0]),('XGBoost','s',DARK[1])]:
                data=part.loc[(part.scheme==scheme)&(part.model==model)].set_index('feature_set').reindex(MODEL_LABELS)
                ax.plot(np.arange(4),data.rmse_log,marker=marker,lw=1.5,color=color,label=model)
            ax.set_xticks(range(4),list(MODEL_LABELS.values()));ax.set_ylabel('RMSE · log nightly price');ax.set_title(title,loc='left',fontsize=11)
            ax.legend(frameon=False,fontsize=9,loc='upper right')
        selected=part.loc[part.model.isin(['OLS','XGBoost'])&part.feature_set.isin(MODEL_LABELS)]
        low=selected.rmse_log.min();high=selected.rmse_log.max();pad=(high-low)*.18
        for ax in axes.flat:ax.set_ylim(low-pad,high+pad)
        self.vertical_comparison(fig,axes)
        self.save(fig,'predictive_performance','Random and geographic performance',7,'Each point is pooled outer held-out RMSE, not a fold average. Identical vertical scales support comparison; no uncertainty interval is implied. Baseline includes property and area context; accessibility blocks are added separately.')

    def incremental(self):
        data=self.tables['incremental_performance'];fig,axes=self.canvas('What accessibility adds to prediction','Paired change in geographic held-out RMSE · negative values indicate improvement',shape=(1,2),size=(12,7))
        for ax,model in zip(axes.flat,['OLS','XGBoost']):
            part=data.loc[(data.scheme=='geographic_11')&(data.model==model)].reset_index(drop=True)
            for i,r in part.iterrows():self.vertical_interval(ax,i,r.delta_rmse_bootstrap_low,r.delta_rmse_bootstrap_high,r.delta_rmse,DARK[i%4],PALETTE[i%4])
            ax.set_xticks(range(len(part)),[self.contrast_label(r.added,r.reference) for r in part.itertuples()],fontsize=9)
            ax.axhline(0,color=INK,lw=1,ls='--');ax.set_title(model,loc='left');ax.set_ylabel('ΔRMSE · log nightly price')
        self.vertical_comparison(fig,axes,bottom=.25)
        self.save(fig,'incremental_performance','Incremental accessibility performance',7,'Vertical lines are 95% percentile intervals from 2,000 paired analysis-area bootstrap resamples. The same held-out observations enter each comparison. M0 baseline; ME Euclidean; MW walking; MEW combined.')

    def shap(self):
        part=self.tables['aggregate_shap'].loc[lambda d:(d.scheme=='geographic_11')&(d.feature_set=='MW')].nlargest(15,'mean_absolute_shap')
        fig,axes=self.canvas('What explains held-out predictions','Walking model · XGBoost · geographic cross-validation',size=(11.5,8));ax=axes[0,0];fig.subplots_adjust(left=.29,right=.95,bottom=.11)
        focal={'nearest_station_walking_minutes','nearest_bus_walking_minutes','log1p_food_w','log1p_culture_w'}
        ax.barh(range(len(part)),part.mean_absolute_shap,color=[SAND if f in focal else BLUE for f in part.feature],height=.66)
        names={'log1p_food_w':'Food & social opportunities','log1p_culture_w':'Culture & tourism opportunities',
            'nearest_station_walking_minutes':'Rail station walking time','nearest_bus_walking_minutes':'Bus stop walking time',
            'income_100k_dkk':'Area income','distance_centre_euclidean_km':'Distance to City Hall',
            'log1p_minimum_nights':'Minimum nights','log1p_host_listings_count':'Host listings'}
        ax.set_yticks(range(len(part)),[textwrap.fill(names.get(f,label(f)),30) for f in part.feature],fontsize=9)
        ax.set_ylim(len(part)-.5,-.5);ax.set_xlim(0,part.mean_absolute_shap.max()*1.07)
        ax.set_xlabel('Mean absolute SHAP contribution · log price');self.clean(ax)
        ax.legend(handles=[Patch(color=SAND,label='Accessibility'),Patch(color=BLUE,label='Other predictors')],frameon=False,loc='lower right',fontsize=9)
        self.save(fig,'heldout_shap','Held-out SHAP importance',6,'Exact TreeSHAP contributions are computed only for outer held-out observations. Importance describes prediction, not causal effects; correlated features can share importance.')
        with self.engine.connect() as conn:
            records=conn.execute(text("SELECT record FROM v3_analysis.artifacts WHERE run_id=:run AND family='primary_models' AND artifact='heldout_shap' AND record->>'scheme'='geographic_11' AND record->>'feature_set'='MW' ORDER BY record_key::integer"),{'run':self.run_id}).scalars().all()
        data=join_features(pd.DataFrame(records),self.frame)
        fig,axes=self.canvas('Accessibility in held-out predictions','Walking model · observed feature values and stored SHAP contributions',shape=(2,2),size=(12,9))
        for ax,feature in zip(axes.flat,['nearest_station_walking_minutes','nearest_bus_walking_minutes','log1p_food_w','log1p_culture_w']):
            y=np.array([s[feature] for s in data.shap]);x=data[feature].to_numpy(float)
            ax.hexbin(x,y,gridsize=40,mincnt=1,cmap=DENSITY,linewidths=0,rasterized=True);ax.axhline(0,color='#AF7F42',ls='--',lw=1)
            ax.set_xlabel(label(feature),fontsize=9);ax.set_ylabel('SHAP contribution · log price',fontsize=9);self.clean(ax,'both')
        self.save(fig,'heldout_shap_dependence','Held-out accessibility dependence',6,'Every contribution comes from a model that excluded that observation’s analysis area. Hexagons summarize point density; darker blue denotes denser bins. No smoothing, model refitting or causal interpretation is used.')

    def coefficients(self):
        data=self.tables['ols_coefficients'];fig,axes=self.canvas('Conditional accessibility associations','OLS · common complete-case sample · separate Euclidean and walking models',shape=(1,2),size=(13,7.5))
        for ax,fs,features in zip(axes.flat,['ME','MW'],[['nearest_station_euclidean_km','nearest_bus_euclidean_km','log1p_food_e','log1p_culture_e'],['nearest_station_walking_minutes','nearest_bus_walking_minutes','log1p_food_w','log1p_culture_w']]):
            part=data.loc[data.feature_set.eq(fs)].set_index('term').loc[features]
            for i,(term,r) in enumerate(part.iterrows()):self.vertical_interval(ax,i,r.hc3_ci_low,r.hc3_ci_high,r.coefficient,DARK[i%4],PALETTE[i%4],filled=r.wild_cluster_p_value<.05)
            ax.set_xticks(range(4),['Rail\nproximity','Bus\nproximity','Food &\nsocial','Culture &\ntourism']);ax.axhline(0,ls='--',lw=1,color=INK)
            ax.set_title(MODEL_LABELS[fs],loc='left');ax.set_ylabel('Coefficient · log price per predictor unit')
        self.vertical_comparison(fig,axes,common_y=False,bottom=.24)
        self.save(fig,'accessibility_coefficients','OLS accessibility coefficients',6,'Vertical lines: 95% HC3 intervals. Filled points: area wild-cluster bootstrap-t p < 0.05 (11 clusters; 9,999 draws). Proximity units: Euclidean km / walking minutes. Opportunity units: log(1 + count). Scales differ because proximity units differ; these are conditional associations.')

    def area_results(self):
        data=self.tables['incremental_by_analysis_area'];fig,axes=self.canvas('Accessibility gains vary by held-out area','Walking versus baseline · paired geographic held-out errors',shape=(1,2),size=(14,7.4))
        for ax,model in zip(axes.flat,['OLS','XGBoost']):
            part=data.loc[(data.model==model)&(data.scheme=='geographic_11')&(data.added=='MW')&(data.reference=='M0')].set_index('analysis_area').reindex(self.areas.area_id)
            ax.bar(np.arange(len(part)),part.delta_rmse,color=[SAND if a.startswith('frederiksberg') else BLUE for a in part.index],width=.65)
            ax.set_xticks(range(len(part)),[self.names[a] for a in part.index],fontsize=8)
            plt.setp(ax.get_xticklabels(),rotation=40,ha='right',rotation_mode='anchor')
            ax.axhline(0,color=INK,ls='--',lw=1);ax.set_title(model,loc='left');ax.set_ylabel('ΔRMSE · walking minus baseline')
        self.vertical_comparison(fig,axes,bottom=.30)
        self.save(fig,'area_incremental_performance','Held-out area accessibility gains',8,'Negative values indicate lower error after adding walking accessibility. Frederiksberg is one of eleven peer analysis areas. Each bar uses the complete held-out area; no uncertainty interval is implied.')
        data=self.tables['fold_performance'];fig,axes=self.canvas('Where geographic prediction is harder','XGBoost walking model · full-area held-out RMSE',size=(12.6,8.8));ax=axes[0,0];fig.subplots_adjust(left=.055,right=.69,top=.86,bottom=.12)
        part=data.loc[(data.scheme=='geographic_11')&(data.model=='XGBoost')&(data.feature_set=='MW')].set_index('heldout_analysis_area')
        vals=part.rmse_log.to_dict();norm=Normalize(min(vals.values()),max(vals.values()));self.base_map(ax,vals,SEQUENTIAL,norm,ids=True)
        cax=fig.add_axes([.735,.75,.215,.018]);fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=SEQUENTIAL),cax=cax,orientation='horizontal');fig.text(.735,.805,'Held-out RMSE · log nightly price',fontsize=9);self.district_key(fig)
        self.save(fig,'geographic_error_map','Geographic held-out error',8,'Colours show errors for each entire held-out analysis area. Labels 01–10 are Copenhagen districts; F is Frederiksberg. Official boundaries; EPSG:25832.',crs=25832)

    def validation_maps(self):
        with self.engine.connect() as conn:
            assignments=pd.read_sql(text("SELECT snapshot_date,listing_id,scheme,outer_fold FROM v3_analysis.outer_assignments WHERE role='test' AND scheme LIKE 'blocks_%'"),conn)
            buffers={d:conn.execute(text("SELECT ST_AsGeoJSON(ST_Buffer(geom_25832,:d)) FROM v3_spatial.analysis_areas WHERE area_id='frederiksberg_0147'"),{'d':d}).scalar_one() for d in [500,1000]}
        fig,axes=self.canvas('The geography of validation','Area hold-outs, saved grid folds and exclusion buffers',shape=(1,3),size=(14,6.4))
        self.base_map(axes[0,0],ids=True);axes[0,0].set_title('Eleven area hold-outs',loc='left',fontsize=10)
        for r in self.areas.itertuples():
            from src.pipeline.build_analysis_areas import _rings
            _rings(axes[0,0],json.loads(r.geojson),fill=SAND if r.area_id.startswith('frederiksberg') else BLUE,edge='white',linewidth=1)
        self.area_ids(axes[0,0])
        self.grid_map(axes[0,1],assignments,'blocks_1500m_origin_0_0',1500,0,0);axes[0,1].set_title('1.5 km grid · five folds',loc='left',fontsize=10)
        ax=axes[0,2];self.base_map(ax)
        from src.pipeline.build_analysis_areas import _rings
        for d,color in [(1000,LILAC),(500,SAND)]:_rings(ax,json.loads(buffers[d]),fill=color,edge=DARK[3],alpha=.5,linewidth=.8)
        target=self.areas.loc[self.areas.area_id=='frederiksberg_0147'].iloc[0];_rings(ax,json.loads(target.geojson),fill=BLUE,edge=DARK[0]);ax.set_title('Frederiksberg buffer example',loc='left',fontsize=10)
        ax.legend(handles=[Patch(color=BLUE,label='Held-out area'),Patch(color=SAND,label='500 m buffer'),Patch(color=LILAC,label='1,000 m buffer')],fontsize=7.5,frameon=False,loc='upper center',bbox_to_anchor=(.5,-.055))
        self.save(fig,'validation_geography','Outer validation geography',8,'Grid colours denote saved test-fold membership. Buffer zones exclude nearby training listings; Frederiksberg is a public geometric illustration. All spatial operations use EPSG:25832.',source='v3_analysis.outer_assignments; official area geometries',crs=25832)
        fig,axes=self.canvas('Grid size and origin sensitivity','The six saved spatial block designs · fold membership is independent of price',shape=(2,3),size=(14,11))
        for ax,(size,shift) in zip(axes.flat,[(s,h) for h in [0,.5] for s in [1000,1500,2000]]):
            scheme=f'blocks_{size}m_origin_{shift:g}_{shift:g}';self.grid_map(ax,assignments,scheme,size,shift,shift)
            ax.set_title(f'{size/1000:g} km · origin shift {shift:g} × cell width',loc='left',fontsize=10)
        self.save(fig,'spatial_grid_sensitivities','Spatial block sensitivity maps',8,'Pastel colours denote the five saved outer folds in each design; colours do not imply corresponding folds across designs. Cells containing fewer than five listings are suppressed. EPSG:25832.',source='v3_analysis.outer_assignments',crs=25832)

    def grid_map(self,ax,assignments,scheme,size,fx,fy):
        part=assignments.loc[assignments.scheme==scheme];data=join_features(part,self.frame)
        data['gx']=np.floor((data.metric_x-size*fx)/size);data['gy']=np.floor((data.metric_y-size*fy)/size)
        grouped=data.groupby(['gx','gy']).agg(n=('listing_id','size'),fold=('outer_fold','first'),unique=('outer_fold','nunique')).reset_index()
        if (grouped.unique!=1).any():raise ValueError('A saved grid cell spans multiple test folds')
        folds=sorted(part.outer_fold.unique());colors=PALETTE+['#DCC8C4'];mapping=dict(zip(folds,colors));self.base_map(ax)
        for r in grouped.loc[grouped.n>=5].itertuples():ax.add_patch(Rectangle((r.gx*size+size*fx,r.gy*size+size*fy),size,size,facecolor=mapping[r.fold],edgecolor='white',lw=.6,zorder=2.5))
        self.outlines(ax)
        ax.legend(handles=[Patch(color=mapping[f],label=f) for f in folds],title='Saved fold',title_fontsize=7.5,fontsize=7,ncol=5,frameon=False,loc='upper center',bbox_to_anchor=(.5,-.045),handlelength=1,columnspacing=.8)

    def validation_performance(self):
        data=self.tables['robustness_summary']
        part=data.loc[(data.analysis=='spatial_validation')&(data.feature_set=='MW')&data.model.isin(['OLS','XGBoost'])]
        schemes=sorted(part.scheme.unique())
        if len(schemes)!=8:raise RuntimeError('Expected six grid and two buffered validation designs')
        names=[]
        for scheme in schemes:
            if scheme.startswith('blocks_'):
                size=int(scheme.split('_')[1].removesuffix('m'));shift=scheme.split('_')[-1]
                names.append(f'{size/1000:g} km grid\nshift {shift}')
            else:names.append(scheme.removeprefix('buffered_area_').removesuffix('m')+' m\nbuffer')
        fig,axes=self.canvas('Prediction under alternative spatial hold-outs','Walking model · six grid designs and two area-buffer designs',shape=(1,2),size=(14,8))
        for ax,model,color in zip(axes.flat,['OLS','XGBoost'],[DARK[0],DARK[1]]):
            p=part.loc[part.model==model].set_index('scheme').reindex(schemes)
            ax.scatter(range(len(p)),p.rmse_log,color=color,s=45,label='Alternative spatial hold-out')
            primary=self.tables['model_performance'].loc[lambda d:(d.scheme=='geographic_11')&(d.feature_set=='MW')&(d.model==model)].rmse_log.iloc[0]
            ax.axhline(primary,color=color,ls='--',lw=1,label='Primary area hold-out')
            ax.set_xticks(range(len(p)),names,fontsize=8);ax.set_title(model,loc='left');ax.set_ylabel('Pooled held-out RMSE · log price')
            ax.legend(frameon=False,fontsize=8,loc='upper left')
        for ax in axes.flat:plt.setp(ax.get_xticklabels(),rotation=30,ha='right',rotation_mode='anchor')
        self.vertical_comparison(fig,axes,bottom=.29)
        self.save(fig,'spatial_validation_performance','Grid and buffer validation errors',8,'Dashed lines denote primary leave-one-area-out RMSE. Grid shifts are fractions of cell width. Buffer designs exclude nearby training listings; different hold-out schemes assess different spatial prediction tasks.',source='v3_analysis robustness/model_performance')

    def residuals(self):
        with self.engine.connect() as conn:
            rows=conn.execute(text("SELECT record FROM v3_analysis.artifacts WHERE run_id=:run AND family='primary_models' AND artifact='oof_predictions' AND record->>'scheme'='geographic_11' AND record->>'model'='XGBoost' AND record->>'feature_set' IN ('M0','MW')"),{'run':self.run_id}).scalars().all()
        data=pd.DataFrame(rows);moran=self.tables['spatial_moran']
        for fs,title in [('M0','baseline'),('MW','walking')]:
            part=data.loc[data.feature_set==fs];joined=residual_coordinates(part,self.frame)
            m=moran.loc[(moran.model=='XGBoost')&(moran.feature_set==fs)].iloc[0]
            self.map_figure('residual',f'Remaining spatial error · {title}','Median residual\nlog price',9,joined,'residual_'+fs.lower()+'_map',True,
                f'Outer held-out XGBoost residual = observed − predicted. Moran I = {m.moran_i:.3f}, two-sided permutation p = {m.permutation_p_two_sided:.3f}; k = {int(m.k)}, {int(m.permutations)} permutations.')
        fig,axes=self.canvas('Spatial dependence after prediction','Observed prices and geographic held-out residuals · frozen diagnostic specification',size=(11,6.7));ax=axes[0,0];fig.subplots_adjust(left=.26)
        p=moran.reset_index(drop=True)
        names=['Observed log price' if r.variable=='log_price' else f'{r.model} · {MODEL_LABELS[r.feature_set]}' for r in p.itertuples()]
        ax.barh(range(len(p)),p.moran_i,color=[LILAC]+[BLUE if r.feature_set=='M0' else SAND for r in list(p.itertuples())[1:]],height=.6);ax.set_yticks(range(len(p)),names);ax.invert_yaxis();ax.set_xlabel('Moran’s I');self.clean(ax)
        for i,r in p.iterrows():ax.text(r.moran_i+.003,i,f'p = {r.permutation_p_two_sided:.3f}',va='center',fontsize=9)
        ax.set_xlim(min(0,p.moran_i.min()),p.moran_i.max()+.07)
        self.save(fig,'spatial_moran_diagnostics','Residual spatial diagnostics',9,'Eight nearest neighbours in EPSG:25832; 499 permutations; two-sided permutation p-values. Material residual spatial dependence triggered the prespecified spatial-error robustness analysis.',crs=25832)

    def income(self):
        data=self.tables['income_incremental_comparison'];fig,axes=self.canvas('Does the income control change prediction?','Geographic paired accessibility gains · qualified income versus no-income sensitivity',shape=(1,2),size=(12,8))
        for ax,model in zip(axes.flat,['OLS','XGBoost']):
            p=data.loc[(data.scheme=='geographic_11')&(data.model==model)].reset_index(drop=True)
            for suffix,color,fill,offset in [('primary',DARK[0],BLUE,-.11),('no_income',DARK[1],SAND,.11)]:
                for i,r in p.iterrows():self.vertical_interval(ax,i+offset,r['delta_rmse_bootstrap_low_'+suffix],r['delta_rmse_bootstrap_high_'+suffix],r['delta_rmse_'+suffix],color,fill,cap=.045)
            ax.set_xticks(range(len(p)),[self.contrast_label(r.added,r.reference) for r in p.itertuples()],fontsize=9)
            ax.axhline(0,color=INK,ls='--',lw=1);ax.set_ylabel('ΔRMSE · log nightly price');ax.set_title(model,loc='left')
        self.vertical_comparison(fig,axes,bottom=.26)
        fig.legend(handles=[Line2D([],[],marker='o',color=DARK[0],markerfacecolor=BLUE,label='Qualified income'),Line2D([],[],marker='o',color=DARK[1],markerfacecolor=SAND,label='No income')],frameon=False,ncol=2,loc='lower center',bbox_to_anchor=(.5,.12),fontsize=9)
        self.save(fig,'income_sensitivity','Income-control sensitivity',7,'Same frozen observations, outer and inner assignments, and candidate set in both specifications. Vertical lines: paired area-bootstrap 95% intervals. Cross-source income comparability is qualified; sensitivity is not an equivalence test.',source='v3_analysis income_robustness')

    def robustness(self):
        p=self.tables['robustness_summary'];p=p.loc[(p.scheme.str.endswith('geographic_11'))&(p.feature_set=='MW')&p.model.isin(['OLS','XGBoost'])].copy()
        if p.empty:raise RuntimeError('Prespecified robustness results missing')
        fig,axes=self.canvas('Prespecified robustness checks','Walking model · geographic held-out RMSE · samples and measurement definitions may differ',shape=(1,2),size=(14,8))
        analyses=sorted(p.analysis.unique())
        names_by_analysis={'apartments':'Apartments','continuous_decay':'Continuous\ndecay','price_trim':'Price\ntrim','review_covariates':'Review\ncovariates','reviewed':'Reviewed\nlistings','speed_4':'4.0 km/h','speed_5_4':'5.4 km/h','threshold_15':'15-minute\nbudget','threshold_20':'20-minute\nbudget'}
        names=[names_by_analysis[a] for a in analyses]
        for ax,model,color in zip(axes.flat,['OLS','XGBoost'],[DARK[0],DARK[1]]):
            part=p.loc[p.model==model].set_index('analysis').reindex(analyses);ax.scatter(range(len(analyses)),part.rmse_log,color=color,s=45,label='Robustness specification')
            baseline=self.tables['model_performance'].loc[lambda d:(d.scheme=='geographic_11')&(d.feature_set=='MW')&(d.model==model)].rmse_log.iloc[0]
            ax.axhline(baseline,color=color,ls='--',alpha=.65,label='Primary walking model');ax.set_xticks(range(len(analyses)),names,fontsize=8);ax.set_title(model,loc='left');ax.set_ylabel('RMSE · log nightly price')
            ax.legend(frameon=False,fontsize=8,loc='center left')
        for ax in axes.flat:plt.setp(ax.get_xticklabels(),rotation=30,ha='right',rotation_mode='anchor')
        self.vertical_comparison(fig,axes,bottom=.29)
        self.save(fig,'robustness_summary','Prespecified robustness overview',7,'Dashed lines show primary walking-model error. These are descriptive checks, not a model-selection ranking; sample-restricted specifications evaluate different populations. Grid and buffer designs are displayed separately.',source='v3_analysis robustness/model_performance')

    def catchment(self):
        import networkx as nx
        # Keep V2's fixed public cartographic anchor, but use the frozen V3
        # graph, categories, snap connectors and 5 km/h / 10 minute budget.
        radius=833;budget=5000/60*10
        with self.engine.connect() as conn:
            network=conn.execute(text('SELECT network_id FROM v3_spatial.walking_networks')).scalars().all()
            if len(network)!=1:raise RuntimeError('Illustration needs the frozen walking network identity')
            centre=conn.execute(text("SELECT ST_X(geom_25832),ST_Y(geom_25832) FROM v3_spatial.reference_points WHERE reference_id='city_hall_square'")).one()
            component=conn.execute(text('SELECT component_id FROM v3_spatial.walking_nodes WHERE network_id=:net GROUP BY component_id ORDER BY count(*) DESC,component_id LIMIT 1'),{'net':network[0]}).scalar_one()
            origin=conn.execute(text('SELECT osm_node_id,ST_X(geom_25832),ST_Y(geom_25832) FROM v3_spatial.walking_nodes WHERE network_id=:net AND component_id=:component ORDER BY geom_25832 <-> ST_SetSRID(ST_MakePoint(:x,:y),25832),osm_node_id LIMIT 1'),{'net':network[0],'component':component,'x':centre[0]+1500,'y':centre[1]-1050}).one()
            params={'net':network[0],'x':origin[1],'y':origin[2]}
            nodes=pd.read_sql(text('SELECT osm_node_id,ST_X(geom_25832) x,ST_Y(geom_25832) y FROM v3_spatial.walking_nodes WHERE network_id=:net AND ST_DWithin(geom_25832,ST_SetSRID(ST_MakePoint(:x,:y),25832),1100)'),conn,params=params)
            edges=pd.read_sql(text('SELECT from_node_id,to_node_id,length_m,forward_allowed,reverse_allowed FROM v3_spatial.walking_edges WHERE network_id=:net AND from_node_id=ANY(:ids) AND to_node_id=ANY(:ids) ORDER BY osm_way_id,segment_index'),conn,params={'net':network[0],'ids':nodes.osm_node_id.tolist()})
            pois=pd.read_sql(text("SELECT p.destination_key,p.category,ST_X(p.geom_25832) x,ST_Y(p.geom_25832) y,s.snapped_node_id,s.snap_distance_m FROM v3_spatial.osm_pois p LEFT JOIN v3_spatial.walking_destination_snaps s ON s.destination_kind='poi' AND s.destination_key=p.destination_key AND s.network_id=:net WHERE ST_DWithin(p.geom_25832,ST_SetSRID(ST_MakePoint(:x,:y),25832),:radius) ORDER BY p.category,p.destination_key"),conn,params={**params,'radius':radius})
        if nodes.empty or edges.empty or pois.empty:raise RuntimeError('Public catchment geography is empty')
        if pois.destination_key.duplicated().any():raise RuntimeError('Repeated public catchment POI')
        xy=nodes.set_index('osm_node_id')[['x','y']].to_dict('index');graph=nx.DiGraph();graph.add_nodes_from(xy)
        for r in edges.itertuples():
            a=xy[r.from_node_id];b=xy[r.to_node_id];chord=np.hypot(a['x']-b['x'],a['y']-b['y'])
            if r.length_m<=0 or r.length_m<chord*.999:raise RuntimeError('Edge lengths incompatible with projected reachability window')
            for u,v,allowed in [(r.from_node_id,r.to_node_id,r.forward_allowed),(r.to_node_id,r.from_node_id,r.reverse_allowed)]:
                if allowed and (not graph.has_edge(u,v) or r.length_m<graph[u][v]['weight']):graph.add_edge(u,v,weight=r.length_m)
        cost=nx.single_source_dijkstra_path_length(graph,origin[0],cutoff=budget,weight='weight')
        pois['reachable']=poi_reachability(pois,cost,budget)
        segments=[];reachable=[]
        for r in edges.itertuples():
            a=xy[r.from_node_id];b=xy[r.to_node_id];segment=[(a['x'],a['y']),(b['x'],b['y'])];segments.append(segment)
            for u,v,allowed in [(r.from_node_id,r.to_node_id,r.forward_allowed),(r.to_node_id,r.from_node_id,r.reverse_allowed)]:
                if not allowed or u not in cost or r.length_m>graph[u][v]['weight']+1e-8:continue
                fraction=min(1,max(0,(budget-cost[u])/r.length_m))
                if fraction>0:
                    start=np.array([xy[u]['x'],xy[u]['y']]);stop=np.array([xy[v]['x'],xy[v]['y']]);reachable.append([start,start+fraction*(stop-start)])
        teal='#5D9D8C';coral='#D7957E';poi_blue='#779DB9'
        count=int(pois.reachable.sum())
        fig,axes=self.canvas('Same destinations, different access geometry','Public harbour-side illustration · 833 m straight-line radius and 10 minutes at 5 km/h',shape=(1,2),size=(13.2,8.5))
        fig.subplots_adjust(left=.04,right=.96,bottom=.21,top=.86,wspace=.055)
        titles=[f'A · Straight-line circle ({len(pois)} POIs)',f'B · Walking reach ({count} of {len(pois)} POIs reachable)']
        categories=[('food_social','o',coral,'Food / social POI'),('cultural_tourist','^',poi_blue,'Culture / tourism POI')]
        if not set(pois.category).issubset({c[0] for c in categories}):raise RuntimeError('Unexpected frozen POI category')
        for index,(ax,title) in enumerate(zip(axes.flat,titles)):
            ax.set_facecolor('white')
            if index==0:ax.add_patch(Circle((origin[1],origin[2]),radius,facecolor='#D9EAE5',edgecolor=teal,alpha=.7,lw=1.6,zorder=0))
            ax.add_collection(LineCollection(segments,colors='#CDDADB',linewidths=.6,zorder=1))
            if index==1:ax.add_collection(LineCollection(reachable,colors=teal,linewidths=2.3,alpha=.94,zorder=3))
            for category,marker,color,_ in categories:
                points=pois.loc[pois.category==category]
                ax.scatter(points.x,points.y,s=36,marker=marker,color=color,edgecolor='white',lw=.55,zorder=5,alpha=.96 if index==0 else .3)
                if index==1:
                    reached=points.loc[points.reachable]
                    ax.scatter(reached.x,reached.y,s=41,marker=marker,color=color,edgecolor=NAVY,lw=.55,zorder=6)
            ax.scatter(origin[1],origin[2],s=200,marker='*',color='#D5A349',edgecolor=NAVY,lw=.7,zorder=8)
            ax.set(xlim=(origin[1]-920,origin[1]+920),ylim=(origin[2]-920,origin[2]+920),aspect='equal')
            ax.set_xticks([]);ax.set_yticks([])
            for spine in ax.spines.values():spine.set_visible(True);spine.set_color('#BDCECB')
            ax.set_title(title,loc='left',fontsize=11,pad=12)
            ax.plot([origin[1]-810,origin[1]-310],[origin[2]-810,origin[2]-810],lw=2,color=NAVY,zorder=10)
            ax.text(origin[1]-560,origin[2]-765,'500 m',ha='center',fontsize=8,color=NAVY,zorder=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':2})
        handles=[Line2D([],[],marker='*',linestyle='',markerfacecolor='#D5A349',markeredgecolor=NAVY,markersize=12,label='Public OSM-node origin'),Line2D([],[],color=teal,lw=2.5,label='Reachable street segment')]
        handles.extend(Line2D([],[],marker=m,linestyle='',color=c,markersize=7,label=l) for _,m,c,l in categories)
        fig.legend(handles=handles,ncol=4,loc='lower center',bbox_to_anchor=(.5,.135),frameon=False,fontsize=9)
        fig.text(.5,.105,'Panel B: outlined POIs are reachable; faded POIs fall outside the walking budget.',ha='center',fontsize=9,color=INK)
        self.save(fig,'catchment_comparison','Euclidean and network catchment example',4,
            'Both panels show the same mapped POIs within 833 m. V2 public-anchor rule: nearest node on the largest component to City Hall +1,500 m east / −1,050 m northing. V3 directed walking reach includes destination snap connectors; no service-area polygon is inferred. EPSG:25832.',
            source=f'v3_spatial walking graph {network[0]}; osm_pois; walking_destination_snaps; origin node {origin[0]}',crs=25832)
        self.records[-1]['catchment']={'origin_osm_node_id':int(origin[0]),'origin_rule':'V2 public cartographic rule; City Hall +1500 m east, -1050 m northing; nearest node on largest graph component',
            'straight_line_radius_m':radius,'walking_budget_m':budget,'walking_speed_kmh':5,'walking_minutes':10,'candidate_pois':len(pois),'reachable_pois':count,
            'counts_by_category':{cat:{'candidate':int((pois.category==cat).sum()),'reachable':int(((pois.category==cat)&pois.reachable).sum())} for cat,_,_,_ in categories},
            'snap_connectors_included':True,'poi_pairing':'Identical destination keys in both panels','crs_epsg':25832}

    def render(self):
        self.workflow();self.study();self.distributions()
        self.map_figure('log_price','The spatial pattern of nightly prices','Median log\nnightly price')
        for variable,title,unit in [('nearest_station_walking_minutes','Walking access to rail stations','Median walking\nminutes'),('nearest_bus_walking_minutes','Walking access to bus stops','Median walking\nminutes'),('log1p_food_w','Food and social opportunities','Median log\n(1 + count)'),('log1p_culture_w','Cultural and tourist opportunities','Median log\n(1 + count)')]:self.map_figure(variable,title,unit,5)
        self.catchment();self.comparison();self.performance();self.incremental();self.shap();self.coefficients();self.area_results();self.validation_maps();self.validation_performance();self.residuals();self.income();self.robustness()
        coverage=[{'planned_category':k,'title':v,'status':'generated','figures':[r['name'] for r in self.records if r['planned_category']==k]} for k,v in CATEGORIES.items()]
        if any(not r['figures'] for r in coverage):raise RuntimeError('Incomplete planned figure coverage')
        manifest={'run_id':self.run_id,'scope':'Reporting-only rendering of completed analytical results; no model refitting',
            'style':'Geography reference: pastel blue, sand, green and lilac; navy headings; clean map frame',
            'publication_row_level_coordinates':False,'map_crs_epsg':25832,'listing_grid_m':500,'minimum_nonmissing_cell_n':5,
            'export_formats':['png'],'coverage':coverage,'figures':self.records}
        write_json(PROJECT_ROOT/'outputs/tables/reporting/figure_manifest.json',manifest);self.gallery()
        return manifest

    def gallery(self):
        css='body{font:15px/1.6 system-ui;color:#183449;background:#f5f8f9;margin:0}main{max-width:1180px;margin:auto;padding:45px 28px}h1{font-size:34px;margin:0}p{color:#486174}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:24px}article{background:white;padding:18px;border-radius:12px;border:1px solid #dce6e9}img{width:100%;height:auto}h2{margin-top:42px}h3{margin:0;font-size:18px}.caption{font-size:13px}a{color:#527f96}nav a{margin-right:18px}@media(max-width:500px){.grid{grid-template-columns:1fr}main{padding:24px 14px}}'
        web=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',f'<title>Version 3 thesis figures</title><style>{css}</style><main>',
            '<h1>Urban accessibility & Airbnb prices</h1><p>Version 3 thesis figures · Copenhagen and Frederiksberg · pastel geography style</p>',
            f'<p>{len(self.records)} reproducible figures. Analytical sample: {len(self.frame):,} listings. Every figure is available as a high-resolution PNG.</p>',
            '<nav><a href="research_results_v3.html">Results tables</a><a href="../outputs/tables/reporting/figure_manifest.json">Figure provenance</a></nav>']
        for category,title in CATEGORIES.items():
            web.append(f'<h2>{category:02} · {html.escape(title)}</h2><div class="grid">')
            for r in self.records:
                if r['planned_category']!=category:continue
                png=r['paths'][0];web.append(f'<article><h3>{html.escape(r["title"])}</h3><a href="../{png}"><img loading="lazy" src="../{png}" alt="{html.escape(r["title"])}"></a><p class="caption">{html.escape(r["caption"])}</p><nav>')
                for p in r['paths']:web.append(f'<a href="../{p}">{p.rsplit(".",1)[1].upper()}</a>')
                web.append('</nav></article>')
            web.append('</div>')
        web.append('</main></html>');(PROJECT_ROOT/'reports/reporting_figures_v3.html').write_text('\n'.join(web))

def run(engine,run_id,frame,tables):
    return Figures(engine,run_id,frame,tables).render()
