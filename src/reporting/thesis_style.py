"""The existing V3 pastel visual language, applied to current frozen evidence."""
from __future__ import annotations
import re
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap,to_rgb
from matplotlib.ticker import MaxNLocator
from src.ingestion.common import sha256_file
from src.reporting.thesis_sources import ROOT
from src.study.archive import preserved_path

NAVY='#183449';INK='#486174';BLUE='#A9C8D7';SAND='#E9BF86';GREEN='#B7D4C4';LILAC='#CEC2DE'
PALETTE=[BLUE,SAND,GREEN,LILAC];DARK=['#527F96','#AF7F42','#608A77','#88759E']
SEQUENTIAL=LinearSegmentedColormap.from_list('pastel_blue',['#F1F5F6','#C7DDE4','#94B9CB','#5D8DA5'])
DENSITY=LinearSegmentedColormap.from_list('pastel_density',['#DCE9EF','#A9C8D7','#5D8DA5'])
DIVERGING=LinearSegmentedColormap.from_list('pastel_signed',['#7FAABC','#F8F7F3','#DFB176'])
COLOURS={'M0':DARK[0],'ME':DARK[1],'MW':DARK[2],'MEW':DARK[3],
         'OLS':DARK[0],'XGBoost':DARK[1],'Euclidean':DARK[0],'Walking':DARK[1]}
FILLS=dict(zip(DARK,PALETTE))
STYLE_ID='pastel_reference'
HEADINGS={
 'study_areas':('Capital cities and their study neighbourhoods','White study boundaries · grey surrounding municipalities · verified civic references'),
 'nearest_access_relationship':('Straight-line and walking access','Rail stations and bus stops · paired measurements on common samples'),
 'nearest_access_divergence':('Where accessibility measures diverge','Nearest-category distance excess · median and distribution ranges'),
 'opportunity_comparison':('Reachable urban opportunities','Food & social · culture & tourism · matched travel budgets'),
 'accessibility_spatial':('Walking access across study neighbourhoods','Neighbourhood context · mean within 500 m cells · at least five observations per cell'),
 'primary_model_performance':('Prediction in geographically unseen neighbourhoods','Pooled held-out error · lower RMSE is better'),
 'paired_accessibility_contrasts':('What accessibility adds to prediction','Paired changes in geographic held-out RMSE · negative values indicate improvement'),
 'association_accessibility':('Conditional accessibility associations','Complete-case OLS · combined model · adjusted observational associations'),
 'heldout_feature_contributions':('What explains held-out predictions','Combined model · existing XGBoost TreeSHAP contributions'),
 'validation_strategy_comparison':('Evaluation under different validation geographies','Random folds · neighbourhood holdouts · six spatial-block configurations'),
 'neighbourhood_performance_variation':('Accessibility gains vary across neighbourhoods','Walking versus baseline · paired held-out errors'),
 'robustness_contrasts':('Accessibility gains under robustness checks','Registered specifications · paired walking-versus-baseline changes'),
 'transfer_performance':('Pricing relationships across cities','Source-only relative-price transfer · rows are source, columns are target'),
 'transfer_accessibility_gains':('What accessibility adds to cross-city transfer','Relative-price errors · accessibility versus baseline'),
 'transfer_network_comparison':('Walking versus straight-line transfer','Network replacement and add-on · all six directional experiments'),
 'transfer_prediction_diagnostics':('Transferred predictions and observed relative prices','Combined XGBoost model · frozen target predictions'),
 'directional_transfer_asymmetry':('Transferability depends on direction','Forward minus reverse RMSE · descriptive comparisons'),
 'residual_spatial_diagnostics':('Residual spatial dependence','Frozen Moran diagnostics · observed outcomes and held-out residuals')}
HORIZONTAL={'nearest_access_divergence','association_accessibility','heldout_feature_contributions',
            'neighbourhood_performance_variation','robustness_contrasts','transfer_network_comparison',
            'directional_transfer_asymmetry','residual_spatial_diagnostics'}
SHARED_CATEGORIES={'nearest_access_divergence','association_accessibility','heldout_feature_contributions',
                   'robustness_contrasts','directional_transfer_asymmetry','residual_spatial_diagnostics'}


def reference():
    path=ROOT/'src/pipeline/reporting_figures.py'
    return {'style_id':STYLE_ID,'reference_source':str(path.relative_to(ROOT)),'reference_source_sha256':sha256_file(path),
            'reference_figures':{name:sha256_file(preserved_path('outputs/figures/reporting/'+name)) for name in
                ['predictive_performance.png','incremental_performance.png','measure_comparison.png','nearest_station_walking_minutes_map.png']},
            'font':'DejaVu Sans','navy':NAVY,'ink':INK,'pastel_palette':PALETTE,'stroke_palette':DARK,
            'heading':'bold navy','grid':'light #E7EEF1','PNG_dpi':300,'formats':['PNG'],
            'scientific_values_reused_from_reference':False}


def setup():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':NAVY,'axes.labelcolor':INK,
        'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#D4DFE4','axes.titleweight':'bold',
        'axes.titlesize':12,'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':10,
        'legend.fontsize':10,'legend.frameon':False,'axes.spines.top':False,'axes.spines.right':False,
        'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','figure.dpi':100,
        'savefig.dpi':300,'svg.hashsalt':'frozen_thesis_pastel','svg.fonttype':'none','pdf.fonttype':42,
        'grid.color':'#E7EEF1','grid.linewidth':.8,'axes.linewidth':.8,'lines.linewidth':1.5})


def canvas_size(size):
    width,height=size
    return max(11.5,width*1.2),height*1.15+1.5


def clean_caption(caption):
    return re.sub(r'\b(Frozen|frozen|existing|are|in|pooled|from|and|Uniform|uniform|Minimum|minimum|Only|only|nominal|matched)(?=\d)',r'\1 ',caption)


def decorate(fig,name,caption):
    width,height=fig.get_size_inches();caption=clean_caption(caption)
    lines=textwrap.wrap(caption,width=int(width*12))
    footer=.44+len(lines)*.15;header=.9;legend=.35 if fig.legends else 0
    fig.get_layout_engine().set(rect=(.012,footer/height,.975,(height-footer-header-legend)/height),
                                w_pad=.07,h_pad=.08,wspace=.1,hspace=.12)
    title,subtitle=HEADINGS[name]
    fig._thesis_heading=fig.text(.04,1-.16/height,title,fontsize=20,weight='bold',color=NAVY,va='top')
    fig._thesis_subtitle=fig.text(.04,1-.57/height,subtitle,fontsize=11,color=INK,va='top')
    fig._thesis_caption=fig.text(.04,.12/height,'\n'.join(lines),fontsize=9,color=INK,va='bottom',linespacing=1.25)
    if fig._supxlabel is not None:
        fig._supxlabel._autopos=False
        fig._supxlabel.set_y((footer-.20)/height)
        fig._supxlabel.set_verticalalignment('bottom')
    if fig._supylabel is not None:fig._supylabel.set_y((footer+height-header-legend)/(2*height))
    for item in fig.legends:
        item.set_loc('upper center');item.set_bbox_to_anchor((.5,1-header/height),transform=fig.transFigure)
        item.set_frame_on(False)
    axes=[ax for ax in fig.axes if not hasattr(ax,'_colorbar')]
    for ax in axes:
        heading=ax.get_title();ax.set_title('',loc='center');ax.set_title(heading,loc='left',pad=10)
        ax.tick_params(length=0,pad=6)
        ax.grid(False);ax.set_axisbelow(True)
        if name not in {'study_areas','accessibility_spatial','transfer_performance','transfer_accessibility_gains'}:
            direction='both' if name in {'nearest_access_relationship','transfer_prediction_diagnostics'} else 'x' if name in HORIZONTAL else 'y'
            ax.grid(axis=direction,color='#E7EEF1',linewidth=.8,alpha=1)
        if name in HORIZONTAL:ax.xaxis.set_major_locator(MaxNLocator(nbins=5,min_n_ticks=3))
        if name in {'opportunity_comparison','validation_strategy_comparison'} and ax.get_subplotspec().colspan.start>0:ax.set_ylabel('')
    if name in SHARED_CATEGORIES:
        rows={}
        for ax in axes:rows.setdefault(round(ax.get_subplotspec().rowspan.start),[]).append(ax)
        for row in rows.values():
            labels=[t.get_text() for t in row[0].get_yticklabels()]
            for ax in row[1:]:
                if [t.get_text() for t in ax.get_yticklabels()]!=labels:raise ValueError('Category labels differ between city facets')
                ax.tick_params(axis='y',labelleft=False);ax.set_ylabel('');ax.spines['left'].set_visible(False)
    return caption


def map_frame(ax):
    """Scale bars use existing metric-km coordinates; arrow denotes grid north."""
    ax.set_xlabel('');ax.set_ylabel('');ax.set_xticks([]);ax.set_yticks([]);ax.set_facecolor('#EEF4F7')
    # Equal projected distances and equal x/y spans make every panel square.
    xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
    side=max(xmax-xmin,ymax-ymin);xc=(xmin+xmax)/2;yc=(ymin+ymax)/2
    ax.set_xlim(xc-side/2,xc+side/2);ax.set_ylim(yc-side/2,yc+side/2)
    ax.set_aspect('equal',adjustable='box');ax.set_box_aspect(1);ax.set_anchor('N')
    for spine in ax.spines.values():spine.set_visible(True);spine.set_color('#D4DFE4');spine.set_linewidth(.8)
    ax.annotate('N\n(grid)',xy=(.92,.92),xytext=(.92,.76),xycoords='axes fraction',ha='center',
                fontsize=8,weight='bold',color=NAVY,arrowprops={'arrowstyle':'-|>','color':NAVY},zorder=20)
    xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim();span=(xmax-xmin)*.18
    exponent=10**np.floor(np.log10(span));choices=np.array([1,2,5])*exponent
    eligible=choices[choices<=span];distance=float(eligible[-1] if len(eligible) else exponent/2)
    x=xmin+.06*(xmax-xmin);y=ymin+.045*(ymax-ymin)
    ax.plot([x,x+distance],[y,y],color=NAVY,lw=2,zorder=20)
    ax.text(x+distance/2,y+.018*(ymax-ymin),f'{distance:g} km',ha='center',fontsize=8,zorder=20,
            bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':2})


def annotation_colour(value,artist):
    rgb=artist.cmap(artist.norm(value))[:3]
    def luminance(colour):
        array=np.asarray(colour);linear=np.where(array<=.04045,array/12.92,((array+.055)/1.055)**2.4)
        return float(linear@np.array([.2126,.7152,.0722]))
    background=luminance(rgb);ink=luminance(to_rgb(NAVY))
    return NAVY if (background+.05)/(ink+.05)>=1.05/(background+.05) else 'white'
