"""Prespecified accessibility, sample/covariate and spatial-validation sensitivities."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.pipeline.protocol import DESIGN
from src.pipeline.model_specification import FEATURES
from src.pipeline.build_analysis_dataset import load_dataset
from src.pipeline.build_validation_splits import saved_outer
from src.pipeline.build_opportunity_variants import VARIANTS
from src.pipeline.run_primary_models import evaluate_cv
from src.pipeline.storage import persist,export

def accessibility_variant(frame,values,name):
    chosen=values.loc[values.definition==name]
    wide=chosen.pivot(index=['snapshot_date','listing_id'],columns='category',values=['euclidean_value','walking_value'])
    target=frame.copy();keys=pd.MultiIndex.from_arrays([target.snapshot_date.astype(str).str[:10],target.listing_id])
    if not keys.isin(wide.index).all():raise RuntimeError('Sensitivity opportunities are incomplete for the frozen primary sample')
    speed=next(v[1] for v in VARIANTS if v[0]==name)
    for category,short in [('food_social','food'),('cultural_tourist','culture')]:
        for mode,source in [('e','euclidean_value'),('w','walking_value')]:
            val=wide[(source,category)].reindex(keys).to_numpy(float)
            if not np.isfinite(val).all() or np.any(val<0):raise RuntimeError('Missing/negative robustness accessibility; never fill silently')
            target['log1p_'+short+'_'+mode]=np.log1p(val)
    # Speed sensitivity updates rail and bus times as well as opportunity budgets.
    if name.startswith('speed_'):
        target['nearest_station_walking_minutes']=target.nearest_station_network_distance_m/(speed*1000/60)
        target['nearest_bus_walking_minutes']=target.bus_walking_distance_m/(speed*1000/60)
    return target

def sample_variant(frame,outer,kind):
    folds={};rows=[]
    for scheme,scheme_folds in outer.items():
        new=[]
        for fold,tr,te in scheme_folds:
            if kind=='price_trim':
                low,high=frame.iloc[tr].log_price.quantile([.01,.99]);mask=frame.log_price.between(low,high).to_numpy()
            elif kind=='apartments':mask=frame.property_type.isin(['Entire rental unit','Entire condo']).to_numpy();low=high=None
            elif kind=='reviewed':mask=frame.number_of_reviews.gt(0).to_numpy();low=high=None
            else:raise ValueError(kind)
            new_tr=tr[mask[tr]];new_te=te[mask[te]]
            if len(new_tr)<500 or len(new_te)<30:raise RuntimeError(f'Sample robustness infeasible: {kind}, {scheme}, {fold}')
            rows.append({'analysis':kind,'scheme':scheme,'fold':fold,'train_n':len(new_tr),'test_n':len(new_te),'training_log_price_low':low,'training_log_price_high':high})
            new.append((fold,new_tr,new_te))
        folds[kind+'/'+scheme]=new
    return folds,pd.DataFrame(rows)

def run(engine,run_id):
    with engine.connect() as conn:
        frame=load_dataset(conn);outer=saved_outer(conn,frame);values=pd.read_sql(text('SELECT snapshot_date::text,listing_id,definition,category,euclidean_value,walking_value FROM v3_features.opportunity_variants'),conn)
    primary={k:v for k,v in outer.items() if k in ['random_5','geographic_11']}
    accumulated={};registry=[]
    def evaluate(label,data,splits,extra=(),saved=True):
        # Outer assignment names may be annotated for reporting; persisted split
        # loading uses the original scheme for accessibility/covariate variants.
        outputs=evaluate_cv(data,splits,engine,run_id,family='robustness',extra=extra,saved_training=saved,shap=False)
        for name,table in outputs.items():
            table=table.copy();table['analysis']=label;accumulated.setdefault(name,[]).append(table)
        registry.append({'analysis':label,'status':'completed','same_frozen_primary_sample':label not in ['apartments','reviewed','price_trim'],
            'feature_sets':list(FEATURES),'candidate_count':30,'inner_folds':DESIGN['inner_folds']})
        # Save every completed sensitivity before proceeding to the next.
        with engine.begin() as conn:
            for name,table in outputs.items():persist(conn,run_id,'robustness',label+'/'+name,table)
    for name,_,_,_ in VARIANTS:evaluate(name,accessibility_variant(frame,values,name),primary)
    for kind in ['apartments','reviewed','price_trim']:
        folds,summary=sample_variant(frame,primary,kind);evaluate(kind,frame,folds,saved=False)
        export('robustness',kind+'_sample_changes.csv',summary)
    reputation=frame.copy();reputation['log1p_reviews']=np.log1p(reputation.number_of_reviews)
    evaluate('review_covariates',reputation,primary,extra=('log1p_reviews','review_scores_rating'))
    geographic={k:v for k,v in outer.items() if k not in primary}
    evaluate('spatial_validation',frame,geographic)
    # Area fixed effects answer within-area associations only, never unseen-area prediction.
    from src.pipeline.run_primary_models import ols_inference
    from src.pipeline.run_spatial_error_robustness import area_fixed_effects
    fixed=area_fixed_effects(frame)
    accumulated['area_fixed_effects']=[fixed]
    with engine.begin() as conn:
        for name,tables in accumulated.items():persist(conn,run_id,'robustness',name,pd.concat(tables,ignore_index=True))
        persist(conn,run_id,'robustness','registry',registry)
    for name in ['model_performance','fold_performance','area_fixed_effects']:
        export('robustness',name+'.csv',pd.concat(accumulated[name],ignore_index=True))
    master=pd.concat(accumulated['model_performance'],ignore_index=True)
    blocks=master.loc[master.scheme.str.startswith('blocks_')]
    ranges=blocks.groupby(['model','feature_set']).agg(variants=('scheme','nunique'),rmse_min=('rmse_log','min'),rmse_max=('rmse_log','max'),mae_min=('mae_log','min'),mae_max=('mae_log','max')).reset_index()
    export('robustness','spatial_validation_range.csv',ranges)
    with engine.begin() as conn:persist(conn,run_id,'robustness','spatial_validation_range',ranges)
    export('robustness','registry.csv',pd.DataFrame(registry));return registry
