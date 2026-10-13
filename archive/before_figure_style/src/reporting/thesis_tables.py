"""Publication tables and descriptive aggregates from frozen final SQL results."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from src.reporting.thesis_sources import ROOT,CITIES,LABELS,MODELS,SCHEMES

FEATURE_LABELS={
 'accommodates':'Guest capacity','bedrooms':'Bedrooms','bathrooms_effective':'Bathrooms',
 'log1p_minimum_nights':'Minimum nights','superhost':'Superhost','log1p_host_listings_count':'Host listings',
 'amenity_wifi':'Wi-Fi','amenity_dishwasher':'Dishwasher','amenity_washer':'Washer','amenity_dryer':'Dryer',
 'amenity_workspace':'Workspace','amenity_free_parking':'Free parking','amenity_private_balcony':'Private balcony',
 'amenity_self_checkin':'Self check-in','log_population_density':'Population density','distance_centre_euclidean_km':'Civic-centre distance',
 'property_type':'Property type','nearest_station_euclidean_km':'Rail: straight-line km','nearest_bus_euclidean_km':'Bus: straight-line km',
 'log1p_food_e':'Food: log(1 + Euclidean count)','log1p_culture_e':'Culture: log(1 + Euclidean count)',
 'nearest_station_walking_minutes':'Rail: walking minutes','nearest_bus_walking_minutes':'Bus: walking minutes',
 'log1p_food_w':'Food: log(1 + walking count)','log1p_culture_w':'Culture: log(1 + walking count)'}
VALIDATION_LABELS={'neighbourhood':'Neighbourhood','random':'Random'}
for size in [1000,1500,2000]:
    for origin in ['0_0','0p5_0p5']:
        VALIDATION_LABELS[f'blocks_{size}m_origin_{origin}']=f'{size/1000:g} km / '+('zero origin' if origin=='0_0' else 'half origin')
ROBUSTNESS_LABELS={'primary':'Primary','apartment_condo':'Apartment/condo','reviewed_only':'Reviewed listings',
 'walking_15':'15-minute opportunities','walking_20':'20-minute opportunities','boundary_far':'Boundary ≥150 m',
 'training_price_tail':'Training-only price tails','reputation':'Reputation controls','buffer_500':'500 m training buffer',
 'buffer_1000':'1,000 m training buffer','speed_4p0':'Walking speed 4 km/h','speed_5p4':'Walking speed 5.4 km/h',
 'continuous_decay':'Continuous decay','density_same_year':'Same-year density','density_land_only':'Land-only density'}


def markdown(frame,precision=4):
    frame=pd.DataFrame(frame)
    def cell(v):
        if v is None or isinstance(v,(float,np.floating)) and not np.isfinite(v):return '—'
        if isinstance(v,(float,np.floating)):return f'{v:.{precision}f}'
        return str(v).replace('|','\\|').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(str,frame.columns))+' |','| '+' | '.join(['---']*len(frame.columns))+' |',
                      *['| '+' | '.join(cell(x) for x in row)+' |' for row in frame.itertuples(index=False,name=None)]])


def display(frame):
    frame=frame.copy()
    for name in ['city','source_city','target_city']:
        if name in frame:frame[name]=frame[name].map(LABELS)
    if 'scheme' in frame:frame['scheme']=frame.scheme.map(VALIDATION_LABELS)
    return frame


def build(data):
    """No fitting or new uncertainty calculation; use existing contrasts/diagnostics."""
    summaries=[];flow=[];descriptive=[];divergence=[];groups=[]
    for city in CITIES:
        sample=data['sample'][city];ref=data['reference'][city];stages={r['stage']:r['n'] for r in sample['sample_flow']}
        summaries.append({'city':city,'raw_listings':stages['raw'],'eligible_conventional_dwellings':stages['eligible_dwelling'],
                          'positive_price_listings':stages['positive_observed_price'],'inside_study_area':stages['inside_study_area'],
                          'geography_assigned':stages['unique_operational_geography'],'common_accessibility_support':stages['matched_accessibility_support'],
                          'prediction_n':sample['prediction_n'],'association_n':sample['association_n'],
                          'operational_neighbourhoods':data['cities'][city]['operational_count'],
                          'association_missing_percent':100*sample['association_missing_fraction'],'association_missing_limit_percent':100*data['design']['association_missing_limit'],
                          'reference_n':ref['reference_n'],'reference_mean_log_price':ref['mean_log_price'],
                          'reference_geometric_mean_native_price':ref['geometric_mean_price'],'currency':data['cities'][city]['currency']})
        flow.extend({'city':city,**r} for r in sample['sample_flow'])
        groups.extend({'city':city,'neighbourhood':name,'test_n':n,'complementary_train_n':sample['prediction_n']-n,
                       'metric_crs':data['cities'][city]['metric_crs']} for name,n in sorted(sample['group_counts'].items()))
        for r in data['interpretation'][city]['measurement']:
            if r['concept'] in {'station','bus'}:
                for label,key in [('Euclidean','euclidean_km'),('Walking','walking_km')]:
                    descriptive.append({'city':city,'concept':r['concept'],'representation':label,'unit':'km',
                                        'derivation':'Walking minutes ×5/60' if label=='Walking' else 'Frozen Euclidean km','n':r['n'],**r[key]})
                divergence.append({'city':city,'concept':r['concept'],'n':r['n'],**r['nearest_measure_difference_km'],
                                   'spearman':r['spearman'],'unit':'walking-equivalent km minus Euclidean km',
                                   'interpretation':'Nearest category destinations may differ; not same-destination circuity'})
            elif r['minutes']==10:
                for label,key in [('Euclidean','euclidean_opportunities'),('Walking','walking_opportunities')]:
                    descriptive.append({'city':city,'concept':r['concept'],'representation':label,'unit':'destinations',
                                        'derivation':'Frozen nominal10-minute /833 m matched budgets','n':r['n'],**r[key]})
    performance=pd.DataFrame([r for c in CITIES for r in data['validation']['neighbourhood'][c]['performance']])
    contrasts=pd.DataFrame([r for c in CITIES for r in data['validation']['neighbourhood'][c]['contrasts']])
    validation=pd.DataFrame([r for scheme in SCHEMES for c in CITIES for r in data['validation'][scheme][c]['performance']])
    transfer=pd.DataFrame([r for c in CITIES for r in data['transfer'][c]['performance']])
    transfer_contrasts=pd.DataFrame([r for c in CITIES for r in data['transfer'][c]['contrasts']])
    robustness=pd.DataFrame([r for c in CITIES for r in data['robustness'][c]['contrasts']])
    registry=[]
    for city in CITIES:
        for item in data['robustness'][city]['registry']:
            scenario=item['scenario'];part=robustness.loc[(robustness.city==city)&(robustness.scenario==scenario)&(robustness.added=='MW')&(robustness.reference=='M0')]
            result='; '.join(f"{r.estimator} ΔRMSE={r.delta_rmse:+.6f} [{r.stability_low:+.6f},{r.stability_high:+.6f}]" for r in part.itertuples())
            if not result and scenario in SCHEMES:
                values=pd.DataFrame(data['validation'][scenario][city]['performance'])
                pieces=[]
                for estimator in ['OLS','XGBoost']:
                    scores=values.loc[values.estimator==estimator].set_index('model');pieces.append(f"{estimator} MW−M0 ΔRMSE={scores.loc['MW','rmse']-scores.loc['M0','rmse']:+.6f}")
                result='; '.join(pieces)
            if scenario=='area_fixed_effects':result='Four association models complete; density absorbed'
            if scenario=='spatial_error':result='Registered OLS MW trigger; GM_Error_Het complete'
            if scenario=='missing_price_audit':result='Original missing outcomes retained in attrition audit; never imputed'
            registry.append({'city':city,'robustness_check':scenario,'status':item['status'],
                             'estimand':'Adjusted association' if scenario in {'area_fixed_effects','spatial_error'} else 'Source/sample attrition' if scenario=='missing_price_audit' else 'Within-variant paired predictive error',
                             'result':result or item.get('reason','Not applicable under native source construction'),
                             'interpretation':'Geographic composition stability; sample/feature definitions may differ across variants' if len(part) else 'Registered check; does not alter primary models'})
    # Every active feature is parsed from the already qualified dictionary.
    dictionary={}
    for line in (ROOT/'docs/analysis/data_dictionary.md').read_text().splitlines():
        if line.startswith('| `'):
            fields=[x.strip() for x in line.strip('|').split('|')];dictionary[fields[0].strip('`')]=fields
    features=[]
    for block in ['X','E','W']:
        for feature in data['design']['blocks'][block]:
            fields=dictionary[feature]
            source='Original detailed Inside Airbnb export' if block=='X' else 'Matched frozen OSM destinations and Euclidean/directed-foot routing'
            if feature=='log_population_density':source='Qualified native official population and compatible gross area'
            if feature=='distance_centre_euclidean_km':source='Frozen OSM civic object and accepted city metric CRS'
            features.append({'block':block,'feature':feature,'concept':FEATURE_LABELS[feature],'source':source,'unit':fields[5],
                             'transformation':fields[6],'common_construction':fields[4],'qualification':fields[7]})
    coefficients=pd.DataFrame(data['coefficients']);folds=pd.DataFrame(data['fold_metrics']);contributions=pd.DataFrame(data['contributions'])
    asymmetry=[]
    for i,first in enumerate(CITIES):
        for second in CITIES[i+1:]:
            for estimator in ['OLS','XGBoost']:
                for model in MODELS:
                    a=transfer.loc[(transfer.source_city==first)&(transfer.target_city==second)&(transfer.estimator==estimator)&(transfer.model==model)].iloc[0]
                    b=transfer.loc[(transfer.source_city==second)&(transfer.target_city==first)&(transfer.estimator==estimator)&(transfer.model==model)].iloc[0]
                    asymmetry.append({'first_city':LABELS[first],'second_city':LABELS[second],'estimator':estimator,'model':model,
                                      'forward_rmse':a.rmse,'reverse_rmse':b.rmse,'forward_minus_reverse_rmse':a.rmse-b.rmse,
                                      'forward_target_n':a.n,'reverse_target_n':b.n})
    spatial=[]
    for city in CITIES:
        spatial.extend({'city':city,'metric_crs':data['cities'][city]['metric_crs'],**r} for r in data['spatial'][city]['moran'])
    claims=[{'research_question':'RQ1','supports':'Measurement differences on matched destination universes','does_not_support':'Same-destination circuity, complete OSM coverage or causal price effects'},
            {'research_question':'RQ2','supports':'City-specific paired predictive changes and complementary adjusted associations','does_not_support':'Universal network superiority, causal coefficients or statistical equivalence'},
            {'research_question':'RQ3','supports':'Observed heterogeneity across correlated fixed geographic designs','does_not_support':'Independent replication across grids or generalization to all Nordic cities'},
            {'research_question':'RQ4','supports':'Directional relative-price performance using an observed target reference','does_not_support':'Zero-shot absolute-price deployment, target recalibration or pseudo-independent six-direction tests'}]
    return {'city_sample_summary':pd.DataFrame(summaries),'sample_flow':pd.DataFrame(flow),'feature_definitions':pd.DataFrame(features),
            'accessibility_descriptive_statistics':pd.DataFrame(descriptive),'nearest_access_divergence':pd.DataFrame(divergence),
            'primary_predictive_performance':performance,'paired_model_contrasts':contrasts,'association_results':coefficients,
            'validation_comparison':validation,'transfer_performance':transfer,'transfer_contrasts':transfer_contrasts,
            'robustness_registry':pd.DataFrame(registry),'claims_and_limitations':pd.DataFrame(claims),
            'neighbourhood_performance':folds,'neighbourhood_support':pd.DataFrame(groups),'robustness_contrasts':robustness,
            'heldout_feature_contributions':contributions.loc[contributions.scope=='neighbourhood_heldout'].copy(),
            'directional_transfer_asymmetry':pd.DataFrame(asymmetry),'residual_spatial_diagnostics':pd.DataFrame(spatial)}


def presentation(name,frame,data):
    """Compact main tables; complete precision and uncertainty remain in CSV."""
    df=display(frame)
    if name=='city_sample_summary':return df.drop(columns=['association_missing_limit_percent','reference_mean_log_price','reference_n','geography_assigned','inside_study_area','common_accessibility_support'])
    if name=='primary_predictive_performance':return df.pivot(index=['city','estimator'],columns='model',values='rmse').reindex(columns=MODELS).reset_index()
    if name=='paired_model_contrasts':return df[['city','estimator','added','reference','delta_rmse','proportional_change','stability_low','stability_high']]
    if name=='association_results':
        selected=df.loc[(df.model=='MEW')&df.term.isin(data['design']['blocks']['E']+data['design']['blocks']['W'])].copy()
        selected['estimate']=selected.apply(lambda r:f"{r.coefficient:+.4f} [{r.hc3_ci_low:+.4f}, {r.hc3_ci_high:+.4f}]; Webb p={r.wild_cluster_p_value:.4f}",axis=1)
        result=selected.pivot(index='term',columns='city',values='estimate').reindex(index=data['design']['blocks']['E']+data['design']['blocks']['W'],columns=[LABELS[c] for c in CITIES]).reset_index()
        result['term']=result.term.map(FEATURE_LABELS);return result
    if name=='validation_comparison':
        rows=[]
        for city in CITIES:
            for est in ['OLS','XGBoost']:
                for label,schemes in [('Random',['random']),('Neighbourhood',['neighbourhood']),('Spatial blocks: six-design range',SCHEMES[2:])]:
                    part=frame.loc[(frame.city==city)&(frame.estimator==est)&frame.scheme.isin(schemes)]
                    row={'city':LABELS[city],'estimator':est,'validation':label}
                    for model in MODELS:
                        scores=part.loc[part.model==model,'rmse'];row[model]=f'{scores.iloc[0]:.4f}' if len(scores)==1 else f'{scores.min():.4f}–{scores.max():.4f}'
                    rows.append(row)
        return pd.DataFrame(rows)
    if name=='transfer_performance':return df.pivot(index=['source_city','target_city','estimator'],columns='model',values='rmse').reindex(columns=MODELS).reset_index()
    if name=='transfer_contrasts':return df[['source_city','target_city','estimator','added','reference','delta_rmse','stability_low','stability_high']]
    if name=='heldout_feature_contributions':return df[['city','model','term','mean_abs','mean_signed','n']]
    return df
