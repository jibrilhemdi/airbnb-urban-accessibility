"""Mandatory paired no-income sensitivity, using the primary frozen sample/folds."""
from __future__ import annotations
import numpy as np
import pandas as pd
from src.pipeline.protocol import DESIGN, verify_income_evidence
from src.pipeline.model_specification import NO_INCOME_FEATURES, E_NUMERIC, W_NUMERIC
from src.pipeline.build_analysis_dataset import load_dataset
from src.pipeline.build_validation_splits import saved_outer, assignment_hashes
from src.pipeline.run_primary_models import evaluate_cv, ols_inference, metrics
from src.pipeline.inference import COMPARISONS, paired_incremental
from src.pipeline.storage import persist, load_artifact, export

FAMILY='income_robustness'

def compare_metrics(primary,sensitivity,keys):
    other=sensitivity.copy();other['feature_set']=other.feature_set.str.removesuffix('_no_income')
    table=primary.merge(other,on=keys,suffixes=('_primary','_no_income'),validate='one_to_one')
    if len(table)!=len(primary) or len(table)!=len(other):raise RuntimeError('Income sensitivity metric coverage mismatch')
    for metric in ['rmse_log','mae_log','r2_log']:
        table['change_'+metric]=table[metric+'_no_income']-table[metric+'_primary']
    return table

def compare_coefficients(primary,sensitivity,rules):
    p=primary.loc[primary.term.isin(E_NUMERIC+W_NUMERIC)].copy()
    s=sensitivity.loc[sensitivity.term.isin(E_NUMERIC+W_NUMERIC)].copy()
    s['feature_set']=s.feature_set.str.removesuffix('_no_income')
    result=p.merge(s,on=['feature_set','term'],suffixes=('_primary','_no_income'),validate='one_to_one')
    if len(result)!=len(p) or len(result)!=len(s):raise RuntimeError('Accessibility coefficient coverage changed')
    result['coefficient_change']=result.coefficient_no_income-result.coefficient_primary
    floor=rules['coefficient_near_zero_floor']
    result['relative_change_with_floor']=result.coefficient_change.abs()/result.coefficient_primary.abs().clip(lower=floor)
    result['magnitude_sensitivity_flag']=result.relative_change_with_floor>=rules['coefficient_magnitude_relative_change']
    support=(result.wild_cluster_p_value_primary<rules['wild_support_p_threshold']) | (result.wild_cluster_p_value_no_income<rules['wild_support_p_threshold'])
    result['material_direction_change']=(result.coefficient_primary*result.coefficient_no_income<0)&support
    return result

def compare_incremental(primary,sensitivity):
    other=sensitivity.copy()
    for col in ['added','reference']:other[col]=other[col].str.removesuffix('_no_income')
    keys=['scheme','model','added','reference']
    if 'analysis_area' in primary:keys+=['analysis_area']
    table=primary.merge(other,on=keys,suffixes=('_primary','_no_income'),validate='one_to_one')
    if len(table)!=len(primary) or len(table)!=len(other):raise RuntimeError('Income sensitivity incremental coverage mismatch')
    table['change_delta_rmse']=table.delta_rmse_no_income-table.delta_rmse_primary
    table['delta_rmse_sign_reversal']=(table.delta_rmse_no_income*table.delta_rmse_primary<0)
    return table

def per_area_metrics(oof):
    return pd.DataFrame([{**dict(zip(['scheme','model','feature_set','analysis_area'],key)),
        **metrics(p.log_price,p.prediction)} for key,p in oof.loc[oof.scheme=='geographic_11'].groupby(['scheme','model','feature_set','analysis_area'])])

def run(engine,run_id):
    verify_income_evidence()
    with engine.connect() as conn:
        frame=load_dataset(conn);outer=saved_outer(conn,frame,schemes=['random_5','geographic_11']);hashes=assignment_hashes(conn)
        primary={name:load_artifact(conn,run_id,'primary_models',name) for name in
            ['ols_coefficients','model_performance','oof_predictions','incremental_performance','incremental_by_analysis_area']}
    inference=ols_inference(frame,NO_INCOME_FEATURES)
    with engine.begin() as conn:
        for name,table in inference.items():persist(conn,run_id,FAMILY,name,table)
    for name,table in inference.items():export(FAMILY,name+'.csv',table)
    outputs=evaluate_cv(frame,outer,engine,run_id,family=FAMILY,feature_sets=tuple(NO_INCOME_FEATURES),shap=False)
    incremental,areas,bootstrap=paired_incremental(outputs['oof_predictions'],
        comparisons=[(a+'_no_income',b+'_no_income') for a,b in COMPARISONS])
    rules=DESIGN['no_income_robustness']['material_change_rules']
    coefficients=compare_coefficients(primary['ols_coefficients'],inference['ols_coefficients'],rules)
    performance=compare_metrics(primary['model_performance'],outputs['model_performance'],['scheme','model','feature_set'])
    area_performance=compare_metrics(per_area_metrics(primary['oof_predictions']),per_area_metrics(outputs['oof_predictions']),
        ['scheme','model','feature_set','analysis_area'])
    increments=compare_incremental(primary['incremental_performance'],incremental)
    area_increments=compare_incremental(primary['incremental_by_analysis_area'],areas)
    # Pooled accessibility error-direction and MW/ME ranking reversals are substantive warning flags.
    flags=[{'kind':'pooled_delta_rmse_direction_or_MW_ME_ranking','scheme':r.scheme,'model':r.model,
        'comparison':r.added+'/'+r.reference,'material_change':bool(r.delta_rmse_sign_reversal)} for r in increments.itertuples()]
    flags += [{'kind':'ols_accessibility_direction_with_wild_support','feature_set':r.feature_set,
        'term':r.term,'material_change':bool(r.material_direction_change),
        'magnitude_sensitivity_flag':bool(r.magnitude_sensitivity_flag)} for r in coefficients.itertuples()]
    artifacts={'incremental_performance':incremental,'incremental_by_analysis_area':areas,'area_bootstrap':bootstrap,
        'accessibility_coefficient_comparison':coefficients,'performance_comparison':performance,
        'geographic_area_performance_comparison':area_performance,'incremental_comparison':increments,
        'geographic_area_incremental_comparison':area_increments,'conclusion_flags':pd.DataFrame(flags)}
    registry={'analysis':'no_income','status':'completed','mandatory':True,'same_frozen_primary_sample':True,
        'n':len(frame),'feature_sets':list(NO_INCOME_FEATURES),'candidate_count':30,'inner_folds':4,
        'outer_schemes':list(outer),'assignment_hashes':hashes,'material_change_rules':rules,
        'material_change_flagged':any(r['material_change'] for r in flags),
        'interpretation':'Prespecified sensitivity flags; retain primary models and review practical magnitudes/uncertainty'}
    with engine.begin() as conn:
        if assignment_hashes(conn)!=hashes:raise RuntimeError('Income sensitivity validation assignments changed')
        for name,table in artifacts.items():persist(conn,run_id,FAMILY,name,table)
        persist(conn,run_id,FAMILY,'registry',[registry])
    for name,table in artifacts.items():
        if name!='area_bootstrap':export(FAMILY,name+'.csv',table)
    export(FAMILY,'registry.csv',pd.DataFrame([registry]))
    return registry

def audit(conn,run_id,n):
    from src.pipeline.model_specification import FEATURES
    p=load_artifact(conn,run_id,'primary_models','oof_predictions')
    s=load_artifact(conn,run_id,FAMILY,'oof_predictions')
    if len(s)!=n*18 or set(s.feature_set)!=set(NO_INCOME_FEATURES)|{'none'}:
        raise RuntimeError('Mandatory no-income OOF matrix incomplete')
    normal=s.copy();normal['feature_set']=normal.feature_set.str.removesuffix('_no_income')
    keys=['snapshot_date','listing_id','scheme','outer_fold','model','feature_set','analysis_area']
    paired=p.merge(normal,on=keys,suffixes=('_primary','_no_income'),validate='one_to_one')
    if len(paired)!=len(p) or len(paired)!=len(s) or not np.allclose(paired.log_price_primary,paired.log_price_no_income):
        raise RuntimeError('Mandatory no-income sample/outcomes/outer folds differ from primary')
    if not np.allclose(s.squared_error,(s.log_price-s.prediction)**2) or not np.allclose(s.absolute_error,(s.log_price-s.prediction).abs()):
        raise RuntimeError('Mandatory no-income saved losses differ')
    tuning=load_artifact(conn,run_id,FAMILY,'xgboost_tuning')
    pt=load_artifact(conn,run_id,'primary_models','xgboost_tuning')
    normalized=tuning.copy();normalized['feature_set']=normalized.feature_set.str.removesuffix('_no_income')
    tk=['scheme','outer_fold','feature_set','candidate_id']
    paired_t=pt.merge(normalized,on=tk,suffixes=('_primary','_no_income'),validate='one_to_one')
    if len(paired_t)!=1920 or not paired_t.candidate_sha256_primary.eq(paired_t.candidate_sha256_no_income).all():
        raise RuntimeError('Mandatory no-income candidates/budget differ')
    if len(tuning.loc[tuning.selected])!=64:raise RuntimeError('Mandatory no-income selected tuning records incomplete')
    prep=load_artifact(conn,run_id,FAMILY,'preprocessing')
    if len(prep)!=128 or any('income_100k_dkk' in cols for cols in prep.numeric_columns):
        raise RuntimeError('No-income preprocessing has income or missing records')
    ols=load_artifact(conn,run_id,FAMILY,'ols_coefficients')
    if ols.empty or not ols.wild_replications.eq(9999).all() or not ols.clusters.eq(11).all():
        raise RuntimeError('Mandatory no-income OLS inference incomplete')
    reg=load_artifact(conn,run_id,FAMILY,'registry')
    if len(reg)!=1 or reg.iloc[0].assignment_hashes!=assignment_hashes(conn):
        raise RuntimeError('Mandatory no-income saved inner/outer assignments changed')
    for name in ['accessibility_coefficient_comparison','performance_comparison','geographic_area_performance_comparison',
        'incremental_comparison','geographic_area_incremental_comparison','conclusion_flags']:
        if load_artifact(conn,run_id,FAMILY,name).empty:raise RuntimeError('Mandatory income comparison missing: '+name)
    return {'no_income_robustness':'passed','no_income_oof_rows':len(s),'no_income_tuning_rows':len(tuning)}
