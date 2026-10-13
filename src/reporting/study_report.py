"""Generate public aggregate tables, figures and the scientific handover from SQL."""
from __future__ import annotations
import json
import platform
from importlib.metadata import version
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd
from sqlalchemy import text
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once
from src.study.specification import CITIES,MODELS,load_design
from src.study.store import read_package
from src.reporting.study_figures import save_figure


def markdown(rows,columns=None):
    frame=pd.DataFrame(rows)
    if columns is not None:frame=frame[columns]
    def cell(value):
        if value is None or isinstance(value,float) and np.isnan(value):return '—'
        if isinstance(value,float):return f'{value:.6f}'
        return str(value).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(str,frame.columns))+' |','| '+' | '.join(['---']*len(frame.columns))+' |',
                      *['| '+' | '.join(map(cell,row))+' |' for row in frame.itertuples(index=False,name=None)]])


def selected(conn,name,family='reporting'):
    selectors=json.loads((PROJECT_ROOT/'config/study'/(name+'.json')).read_text());result={}
    for city in CITIES:
        summary,_=read_package(conn,selectors[city]['run_id'],city,family)
        if canonical_hash(summary)!=selectors[city]['summary_sha256']:raise ValueError('Public report selector summary differs')
        result[city]=summary
    return result


def preserve_or_write(path,content):
    if path.exists():
        if path.read_bytes()!=content:raise ValueError('Unarchived completed report artifact differs: '+str(path))
    else:write_once(path,content)


def source_rows():
    seen={};roles=['neighbourhood_sources','stockholm_population_sources','osm_sources','destination_geometry_sources']
    def walk(value,registry):
        if isinstance(value,dict):
            if 'source_url' in value and 'sha256' in value:
                digest=value['sha256']
                if digest:
                    seen[digest]={k:value.get(k) for k in ['city','role','source_url','acquired_at_utc','snapshot','geographic_extent','source_crs','licence','sha256','size_bytes','status','receipt_sha256']}
                    seen[digest]['registry']=registry
            for child in value.values():walk(child,registry)
        elif isinstance(value,list):
            for child in value:walk(child,registry)
    for role in roles:walk(json.loads((PROJECT_ROOT/'config/study'/(role+'.json')).read_text()),role)
    return list(seen.values())


def reused_sources(conn,cities):
    output=[]
    def source(record,city,role):
        keys=['source_url','acquired_at_utc','verified_at_utc','reference_period','geographic_extent','source_crs','licence','sha256','size_bytes','status']
        return {'city':city,'role':role,'disposition':'verified immutable source reuse',**{k:record.get(k) for k in keys}}
    for city,config in cities.items():
        selected=config['historical_listing_selection']
        manifest=conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),
                             {'version':selected['source_version'],'city':selected['city'],'snapshot':selected['snapshot'],'digest':selected['manifest_sha256']})
        if canonical_hash(manifest)!=selected['manifest_sha256']:raise ValueError('Original selected source manifest differs')
        for record in manifest['records']:
            if record['filename']=='listings.csv.gz' or record['filename'].endswith('.geojson'):
                output.append(source(record,city,'detailed_listings' if record['filename']=='listings.csv.gz' else 'preserved_geometry'))
    policy=json.loads((PROJECT_ROOT/'archive/previous_analysis/config/context_A04_20261011.json').read_text())['cities']
    for city,old_city in [('copenhagen','copenhagen_frederiksberg'),('oslo','oslo')]:
        for entry in policy[old_city]['sources']:
            r=entry['record']
            if r['filename'] in {'KKBEF1.csv','FOLK1A.csv'} or r['source_id'] in {'a04_20261011_population_data','a04_20261011_population_schema'}:
                output.append(source(r,city,'native_population'))
    return output


def run():
    design,cities=load_design();engine=get_engine();within=[];transfer=[];contrasts=[];geometric=[];association=[];vif=[];spatial_coefficients=[];flow=[];comparison=[];references=[];robust=[];robust_metrics=[];contributions=[]
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            geo=selected(conn,'geography_selection','geography');ref=selected(conn,'reference_selection','reference')
            context=selected(conn,'context_selection','context');access=selected(conn,'accessibility_selection','accessibility');samples=selected(conn,'sample_selection','sample')
            reused=reused_sources(conn,cities)
            primary=selected(conn,'results_neighbourhood');directions=selected(conn,'results_transfer');sensitivity=selected(conn,'robustness_results_selection');interpretation=selected(conn,'interpretation_selection')
            interp_select=json.loads((PROJECT_ROOT/'config/study/interpretation_selection.json').read_text())
            for city in CITIES:
                contributions.extend(conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city AND artifact='contribution_summary' ORDER BY record_key::integer"),
                                                  {'run':interp_select[city]['run_id'],'city':city}).scalars())
                within.extend(primary[city]['performance']);transfer.extend(directions[city]['performance']);contrasts.extend(directions[city]['contrasts'])
                robust.extend(sensitivity[city]['registry']);robust_metrics.extend(sensitivity[city]['performance'])
                flow.extend({'city':city,**row} for row in samples[city]['sample_flow'])
                references.append({'city':city,'reference_n':ref[city]['reference_n'],'mean_log_price':ref[city]['mean_log_price'],
                                   'geometric_mean_price':ref[city]['geometric_mean_price'],'currency':cities[city]['currency']})
                comparison.append({'city':city,'prediction_n':samples[city]['prediction_n'],'association_n':samples[city]['association_n'],
                                   'association_missing_fraction':samples[city]['association_missing_fraction'],'operational_groups':cities[city]['operational_count'],
                                   'minimum_group_n':min(samples[city]['group_counts'].values()),'metric_crs':cities[city]['metric_crs'],
                                   'association_status':selected(conn,'association_selection')[city]['status']})
                assoc_select=json.loads((PROJECT_ROOT/'config/study/association_selection.json').read_text())[city]
                for artifact,target in [('association_coefficients',association),('vif',vif)]:
                    target.extend({'city':city,**row} for row in conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city AND artifact=:artifact ORDER BY record_key::integer"),
                                                                           {'run':assoc_select['run_id'],'city':city,'artifact':artifact}).scalars())
                sp_select=json.loads((PROJECT_ROOT/'config/study/spatial_diagnostic_selection.json').read_text())[city]
                for artifact in ['spatial_error','area_fixed_effects']:
                    spatial_coefficients.extend({'city':city,'analysis':artifact,**row} for row in conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city AND artifact=:artifact ORDER BY record_key::integer"),
                                                                               {'run':sp_select['run_id'],'city':city,'artifact':artifact}).scalars())
            for scheme in ['random']+[f'blocks_{size}m_origin_{origin}' for size in [1000,1500,2000] for origin in ['0_0','0p5_0p5']]:
                results=selected(conn,'results_'+scheme)
                geometric.extend(r for city in CITIES for r in results[city]['performance'])
        tables={'sample_flow':flow,'city_comparability':comparison,'price_references':references,'within_city_performance':within,
                'transfer_performance':transfer,'transfer_accessibility_contrasts':contrasts,'validation_comparison':geometric,
                'association_coefficients':association,'association_vif':vif,'spatial_association_coefficients':spatial_coefficients,
                'robustness_registry':robust,'robustness_performance':robust_metrics,'new_source_receipts':source_rows(),'reused_source_receipts':reused,
                'native_density_units':[{'city':city,**{k:v for k,v in unit.items() if k!='sources'}} for city in CITIES for unit in context[city]['density_units']],
                'geography_groups':[{'city':city,**group,'prediction_n':samples[city]['group_counts'][group['name']]} for city in CITIES for group in geo[city]['groups']]}
        out=PROJECT_ROOT/'outputs/tables/research';out.mkdir(parents=True,exist_ok=True)
        for name,rows in tables.items():preserve_or_write(out/(name+'.csv'),pd.DataFrame(rows).to_csv(index=False).encode())
        proposal=(PROJECT_ROOT/'docs/design/scientific_proposal.md').read_text();questions=proposal.split('The questions are:\n\n',1)[1].split('\n\nMatched destinations',1)[0]
        w=pd.DataFrame(within);t=pd.DataFrame(transfer);c=pd.DataFrame(contrasts)
        blocks=pd.DataFrame(geometric);registry=pd.DataFrame(robust)
        asymmetry=[]
        for i,source in enumerate(CITIES):
            for target in CITIES[i+1:]:
                for estimator in ('OLS','XGBoost'):
                    for model in MODELS:
                        a=t.loc[(t.source_city==source)&(t.target_city==target)&(t.estimator==estimator)&(t.model==model)].iloc[0]
                        b=t.loc[(t.source_city==target)&(t.target_city==source)&(t.estimator==estimator)&(t.model==model)].iloc[0]
                        asymmetry.append({'first_direction':source+' → '+target,'reverse_direction':target+' → '+source,'estimator':estimator,'model':model,
                                          'first_rmse':float(a.rmse),'reverse_rmse':float(b.rmse),'first_minus_reverse':float(a.rmse-b.rmse)})
        preserve_or_write(out/'directional_asymmetry.csv',pd.DataFrame(asymmetry).to_csv(index=False).encode())
        report=['# Three-city accessibility and relative-price transfer research handover',
                'Generated by `python -m src.reporting.study_report` from immutable authoritative PostGIS packages and verified saved predictions. Copenhagen means the combined Copenhagen–Frederiksberg study area.',
                '**Scientific analysis status: COMPLETE.** Three predictive city ladders, three freshly rerun complete-case association ladders, all six transfers and registered robustness checks completed. The researcher changed the association eligibility limit from 5% to 10% uniformly after observing Stockholm’s 5.891783567% missingness; this is a post-observation amendment, not preregistration or a universal standard. The 147 bedroom blanks remain unfilled. Completed predictive/transfer artifacts were dependency-verified and preserved. See the final release audit for verification status and the [dated amendment](association_missingness_amendment_20261013.md).',
                '## Scientific design and questions',questions,
                'The final design was amended after historical results and feasibility evidence had been observed. It is not retrospectively preregistered. M0=X; ME=X+E; MW=X+W; MEW=X+E+W. X contains the common dwelling, host, amenity, native density and civic-distance controls. Four models share rows, observed outcomes and folds within each city. Within-city outcomes are log original observed positive native nightly asking prices.',
                '## Samples, geography and outcomes',markdown(comparison),markdown(references),
                'Reference samples are frozen before accessibility/model filtering. Transfer alone subtracts the frozen city mean log price. This evaluates relative pricing relationships after removing citywide levels. It is not absolute-price deployment in a truly unseen city. Target outcomes enter only the benchmark and evaluation.',
                markdown(pd.DataFrame(flow).pivot(index='stage',columns='city',values='n').reindex([r['stage'] for r in samples['copenhagen']['sample_flow']]).reset_index().to_dict('records')),
                'Provider operational groups are 11/17/11. Stockholm preserves the explicit 14-label-to-11-group mapping; source labels remain separate. Municipal masks define study-area membership, not primary validation groups. Copenhagen spelling normalization is derived only. All final primary groups satisfy test≥15 and train≥500; the former test≥30 rule is a reported diagnostic. Exact mask/provider/native context boundary identity is not claimed.',
                '## Sources and harmonization',
                'Existing verified detailed Airbnb downloads and accepted mask/source bytes were reused with matching checksums; listings were not downloaded or reingested. Copenhagen and Oslo provider polygons, Stockholm official native population/area spreadsheets, same-time OSM networks/destinations and civic objects were newly acquired. Stockholm provider polygon evidence was preserved and reused. Failed acquisitions and HTTP200 timeout remarks remain failed evidence, not empty destination data.',
                'Copenhagen density uses freshly decoded KKBEF1/FOLK1A counts and matching native gross geometry. Oslo sums all 106 BEF001 age cells within each native unit and divides by matching gross official geometry; totals and unlocated residents are never redistributed. Stockholm uses direct official 2025 population and the published 2024 native land+water area table, with rounded hectares and historical area derivation. This avoids unverified RegSO allocation. Density crosses to provider group labels explicitly without claiming identical boundaries. Stockholm density sensitivities examine same-year numerator and land-only denominator. The source table and source registries retain exact URLs, dates, extent, CRS, licences and checksums; raw files stay private.',
                'OSM snapshot is 2026-06-30T23:59:59Z in all three cities. Inherited destination taxonomy, deduplication, bus consolidation, directed pedestrian restrictions and both snapping connectors are unchanged. Primary walking speed is 5 km/h; primary opportunities use 10 minutes and matched rounded 833 m Euclidean radius. Civic anchors are pinned town/city-hall OSM objects from the same snapshot. © OpenStreetMap contributors, ODbL.',
                '## RQ1 — measurement differences',
                'Generated distributions and opportunity comparisons use the same category universe. Nearest Euclidean and nearest network features can select different objects; their difference is not same-destination circuity. Shortest paths, coordinate displacement, access restrictions, finite extraction extent and destination completeness limit interpretation.',
                '![Nearest-distance distributions](../../outputs/figures/research/nearest_distance_distributions.png)',
                '![Opportunity comparison](../../outputs/figures/research/opportunity_comparison.png)',
                '![Accessibility map](../../outputs/figures/research/accessibility_cells.png)',
                'Maps use 500 m cells with at least five analytical observations. CRSs are recorded per city; map coordinates and aggregation do not assert exact listing locations.',
                '## RQ2 — within-city predictive information and associations',
                markdown(within,['city','estimator','model','n','rmse','mae','r2']),
                'Fresh XGBoost fits use the exact inherited 30 candidates and four source-training-only 1 km inner spatial folds. Predictive OLS uses unpenalized ordinary least squares with the same training-only preprocessing. Median/indicator preprocessing and category encoding are fitted within each inner and outer training partition. No outer fold determines thresholds, categories, variables or tuning. Held-out TreeSHAP summaries are descriptive predictive contributions, with contribution sums verified against frozen predictions; they do not identify causal effects.',
                '![Primary performance](../../outputs/figures/research/within_city_performance.png)',
                '![Held-out contributions](../../outputs/figures/research/heldout_contributions_publication.png)',
                'Association coefficients use the common union complete-case sample, HC3 and 9,999 restricted Webb wild-cluster replications over actual operational groups. Complete Copenhagen/Oslo coefficient, VIF and condition diagnostics are exported. All three cities now contribute freshly rerun complete-case coefficients under the uniform 10% post-observation eligibility amendment; no inferential imputation was produced. Spatial residual diagnostics use 8 nearest neighbours and 499 permutations. Triggered spatial-error and area fixed-effect association checks are documented separately; area-constant density is absorbed in fixed effects.',
                markdown([r for r in association if r['model']=='MEW' and r['term'] in design['blocks']['E']+design['blocks']['W']],['city','model','term','coefficient','hc3_ci_low','hc3_ci_high','wild_cluster_p_value']),
                '## RQ3 — geographic separation and consistency',
                'Leave-one-operational-neighbourhood-out is primary. Random five-fold validation is a benchmark. Six geometric variants use 1/1.5/2 km blocks at zero and half-block origins, with five balanced outer folds. Registered 500/1,000 m buffers remove training observations near any held-out point while retaining the held-out sample. Descriptive paired resampling uses 2,000 geographic-group draws; overlapping training samples and residual spatial dependence remain. These are stability summaries, not independent-listing confidence intervals or equivalence tests.',
                '![Validation comparison](../../outputs/figures/research/validation_comparison.png)',
                '![Geographic composition stability](../../outputs/figures/research/accessibility_gains.png)',
                '## RQ4 — six directional transfers',
                markdown(transfer,['source_city','target_city','estimator','model','n','rmse','mae','r2','pearson','spearman']),
                'Each estimator/model is freshly tuned and refitted on one full source-city analytical sample. The identical fitted source pipeline is applied unchanged to its two targets; all 48 directional source-model hashes were independently checked. There is no two-city source pooling, target fitting, target tuning, intercept recalibration or target-driven preprocessing. All model contrasts use identical target observations. Directional results are not pooled into a pseudo-independent significance test.',
                markdown([r for r in asymmetry if r['estimator']=='XGBoost' and r['model']=='MEW']),
                'The reverse-direction comparisons quantify asymmetry rather than interchangeable replications: the training city, target distribution and target sample size change. Removing citywide log-price means does not remove differences in covariate support, dispersion or pricing relationships. Bias and observed-on-prediction slope diagnostics are evaluation summaries only; no correction is applied.',
                '![XGBoost transfer RMSE](../../outputs/figures/research/xgboost_transfer_matrix.png)',
                '![XGBoost accessibility gains](../../outputs/figures/research/xgboost_transfer_gains.png)',
                '![Transfer bias](../../outputs/figures/research/transfer_bias.png)',
                '## Robustness and scientific blockers',
                markdown(registry[['city','scenario','status']].to_dict('records')),
                'Every registered sensitivity is recorded with its exact construction, fold support, status and independently recalculated results. INFEASIBLE or blocked variants do not relax support, silently drop groups or become a substituted pooled partial result. Price-tail thresholds use training-only 1st/99th percentiles inside each inner/outer fit; all original held-out observations remain evaluated. Continuous decay includes all reachable destinations within the finite frozen extracted universe, with a 10-minute half-life and no arbitrary distance cutoff.',
                '## Limitations and claim discipline',
                markdown([{'issue':'Observed asking prices','consequence':'Not transaction revenue, booked rates, causal willingness-to-pay or a temporal panel.'},
                          {'issue':'Missing observed prices','consequence':'Strong source attrition; missing outcomes are never imputed. Price-reference and model samples differ transparently.'},
                          {'issue':'Post-observation association eligibility amendment','consequence':'The researcher raised the uniform limit from 5% to 10% after seeing Stockholm missingness. Complete-case selection may still bias adjusted observational associations; no inferential imputation is used.'},
                          {'issue':'Operational geography','consequence':'Provider folds and native population units have documented footprint/period differences; no exact official-boundary certification.'},
                          {'issue':'Context vintages','consequence':'Native population periods differ; Stockholm gross area is rounded and historically derived; direct matching statistics avoid fabricated allocation.'},
                          {'issue':'OSM and coordinates','consequence':'Completeness, map timing, displacement, connectors, component separation and finite extraction boundaries constrain measurement.'},
                          {'issue':'Validation uncertainty','consequence':'Few geographic groups, overlapping training sets and spatial dependence; stability ranges do not establish independence or equivalence.'},
                          {'issue':'Relative transfer','consequence':'Target price benchmark is observed; results measure structural relative-price transfer, not unseen-city absolute-price deployment.'},
                          {'issue':'External validity','consequence':'Three capitals do not represent every Nordic or European city; network superiority is not assumed.'}]),
                '## Reproduction, preservation and output inventory',
                'Active configuration: `config/study/`; active source-to-model code: `src/study/`; diagnostic/report code: `src/reporting/study_*.py`; immutable authoritative schema: `study`; private runs: `runs/<city>/` and `runs/transfer/`; public aggregate tables/figures: `outputs/tables/research/` and `outputs/figures/research/`; active scientific documents: `docs/analysis/` and `docs/design/scientific_proposal.md`. Historical applied migrations, databases, raw bytes, evidence and original protected analytical artifacts remain preserved. Only the compatibility source scanner received a narrow, tested extension with exact original bytes archived.',
                'See [reproducibility](reproducibility.md), [execution log](execution_log.md), [source registry](source_registry.md), [feature dictionary](data_dictionary.md), [decision log](decision_log.md), [deviations](deviations_from_preanalysis.md) and the generated release audit. Public result tables contain aggregates; raw sources, models, coordinates, memberships and individual predictions remain private. Final Git checkpoint SHA and verified remote equality are supplied in the final handover rather than embedded in their own commit. `main` and `v3` preservation is checked against the initial audit.',
                'The results support measurement and predictive comparisons with cross-city heterogeneity. They do not establish that accessibility causes prices or that Airbnb changes neighbourhoods. Frozen model selection and source definitions were not revised in response to these results.']
        # Pattern statements derive from generated paired contrasts, not typed empirical values.
        primary_contrasts=[r for city in CITIES for r in primary[city]['contrasts'] if r['estimator']=='XGBoost' and r['reference']=='M0']
        pattern=[{'city':r['city'],'model':r['added'],'delta_rmse':r['delta_rmse'],'proportional_change':r['proportional_change'],
                  'direction':'lower error' if r['delta_rmse']<0 else 'higher error'} for r in primary_contrasts]
        report.insert(report.index('## RQ3 — geographic separation and consistency'),markdown(pattern))
        write_once(PROJECT_ROOT/'docs/analysis/research_report.md',('\n\n'.join(report)+'\n').encode())
        software={'python':platform.python_version(),'platform':platform.platform(),'packages':{name:version(name) for name in ['numpy','pandas','scipy','scikit-learn','xgboost','statsmodels','shapely','pyproj','networkx','SQLAlchemy','psycopg2-binary','openpyxl','libpysal','spreg','matplotlib','joblib']}}
        write_once(PROJECT_ROOT/'docs/analysis/software_environment.json',(json.dumps(software,indent=2)+'\n').encode())
        inventory=[]
        metric_schemes=['neighbourhood','random','transfer','robustness']+[f'blocks_{size}m_origin_{origin}' for size in [1000,1500,2000] for origin in ['0_0','0p5_0p5']]
        for directory in ['outputs/tables/research','outputs/figures/research',*['outputs/metrics/'+scheme for scheme in metric_schemes]]:
            for path in sorted((PROJECT_ROOT/directory).rglob('*')):
                if path.is_file():inventory.append({'path':path.relative_to(PROJECT_ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':sha256_file(path)})
        write_once(PROJECT_ROOT/'docs/analysis/public_output_inventory.json',(json.dumps(inventory,indent=2)+'\n').encode())
        return {'status':'COMPLETE_ANALYSIS','primary_city_count':3,'completed_transfer_directions':6,'public_artifacts':len(inventory)}
    finally:engine.dispose()


def figures(transfer,contrasts,within,geometric,robust_metrics,contributions):
    out=PROJECT_ROOT/'outputs/figures/research';part=pd.DataFrame(contrasts)
    for estimator in ('OLS','XGBoost'):
        selected=part.loc[part.estimator==estimator];bound=float(np.abs(selected.delta_rmse).max())
        fig,axes=plt.subplots(1,5,figsize=(15,4))
        for ax,(added,reference) in zip(axes,load_design()[0]['contrasts'],strict=True):
            values=selected.loc[(selected.added==added)&(selected.reference==reference)]
            matrix=values.pivot(index='source_city',columns='target_city',values='delta_rmse').reindex(index=CITIES,columns=CITIES)
            artist=ax.imshow(matrix.to_numpy(),cmap='RdBu_r',vmin=-bound,vmax=bound)
            for i in range(3):
                for j in range(3):
                    if i!=j:ax.text(j,i,f'{matrix.iloc[i,j]:+.3f}',ha='center',va='center',fontsize=8)
            ax.set_title(added+' − '+reference);ax.set_xticks(range(3),[c.title() for c in CITIES],rotation=45,ha='right');ax.set_yticks(range(3),[c.title() for c in CITIES])
        fig.colorbar(artist,ax=axes,label='Δ relative log-price RMSE; negative improves',shrink=.65)
        fig.suptitle(estimator+' directional accessibility contrasts; rows source, columns target')
        fig.subplots_adjust(wspace=.75,bottom=.3,top=.85);save_figure(fig,out/(estimator.lower()+'_transfer_gains.png'));plt.close(fig)
    data=pd.DataFrame([*within,*geometric]);fig,axes=plt.subplots(1,3,figsize=(14,5))
    schemes=['neighbourhood','random']+[f'blocks_{s}m_origin_{o}' for s in [1000,1500,2000] for o in ['0_0','0p5_0p5']]
    labels=['Neighbourhood','Random','1 km zero','1 km half','1.5 km zero','1.5 km half','2 km zero','2 km half']
    for ax,city in zip(axes,CITIES,strict=True):
        for model in MODELS:
            rows=data.loc[(data.city==city)&(data.estimator=='XGBoost')&(data.model==model)].set_index('scheme').reindex(schemes)
            ax.plot(range(len(schemes)),rows.rmse,'o-',label=model,ms=3)
        ax.set_xticks(range(len(schemes)),labels,rotation=60,ha='right');ax.set_title(city.title());ax.set_ylabel('OOF RMSE (native log price)')
    axes[0].legend(ncol=2);fig.tight_layout();save_figure(fig,out/'validation_comparison.png');plt.close(fig)
    contributions=pd.DataFrame(contributions)
    fig,axes=plt.subplots(1,3,figsize=(14,5))
    for ax,city in zip(axes,CITIES,strict=True):
        part=contributions.loc[(contributions.city==city)&(contributions.scope=='neighbourhood_heldout')&(contributions.model=='MEW')].nlargest(10,'mean_abs').sort_values('mean_abs')
        ax.barh(part.term,part.mean_abs,color='#327c91');ax.set_title(city.title());ax.set_xlabel('Contribution magnitude (log price)')
    fig.suptitle('Frozen XGBoost MEW: mean absolute held-out contributions; no causal interpretation',fontsize=10)
    fig.tight_layout();save_figure(fig,out/'heldout_contributions_publication.png');plt.close(fig)


if __name__=='__main__':print(json.dumps(run(),indent=2))
