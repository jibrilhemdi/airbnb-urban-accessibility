"""Fresh common samples and outcome-blind fold packages from current-design SQL."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.study.sources import get_engine,historical_inputs,write_once
from src.study.samples import listing_controls
from src.study.specification import load_design,CITIES
from src.study.store import commit_package,dependencies,read_package
from src.study.validation import outer_splits,inner_splits,support


def records(conn,selected,city,family,artifact):
    return conn.execute(text('SELECT record FROM study.records WHERE run_id=:run AND city=:city AND family=:family '
                             'AND artifact=:artifact ORDER BY record_key::integer'),
                        {'run':selected[city]['run_id'],'city':city,'family':family,'artifact':artifact}).scalars().all()


def freeze():
    target=PROJECT_ROOT/'config/study/sample_selection.json'
    if target.exists():raise ValueError('Samples already frozen; no replacement')
    design,cities=load_design()
    chosen={family:json.loads((PROJECT_ROOT/f'config/study/{family}_selection.json').read_text()) for family in ['geography','context','accessibility']}
    engine=get_engine();selected={};validation={};public={}
    try:
        for city in CITIES:
            with engine.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                rows,_,source=historical_inputs(conn,city)
                geo=records(conn,chosen['geography'],city,'geography','assignment')
                context=records(conn,chosen['context'],city,'context','context')
                accessibility=records(conn,chosen['accessibility'],city,'accessibility','features')
                feature_summary,_=read_package(conn,chosen['accessibility'][city]['run_id'],city,'accessibility')
                if canonical_hash(accessibility)!=feature_summary['records_sha256']:raise ValueError('Fresh feature records changed')
            eligible=[r for r in rows if r['dwelling_eligible'] and r['positive_price'] and r['inside_boundary']]
            controls=listing_controls(eligible)
            frame=pd.DataFrame(controls)
            frame=frame.merge(pd.DataFrame(geo)[['listing_id','raw_label','operational_group','assignment_status']],on='listing_id',validate='one_to_one')
            frame=frame.merge(pd.DataFrame(context).drop(columns='operational_group'),on='listing_id',validate='one_to_one')
            frame=frame.merge(pd.DataFrame(accessibility),on='listing_id',validate='one_to_one')
            flow=[{'stage':'raw','n':source['counts']['raw']},{'stage':'eligible_dwelling','n':source['counts']['dwelling_filtered']},
                  {'stage':'positive_observed_price','n':source['counts']['positive_price']},{'stage':'inside_study_area','n':len(frame)}]
            for stage,condition in [('unique_operational_geography',frame.assignment_status.eq('unique')),
                                    ('qualified_context',frame.log_population_density.notna()&frame.distance_centre_euclidean_km.notna()),
                                    ('matched_accessibility_support',frame.common_support.eq(True))]:
                frame=frame.loc[condition.loc[frame.index]].copy();flow.append({'stage':stage,'n':len(frame)})
            frame['city']=city;frame=frame.sort_values('listing_id').reset_index(drop=True)
            if frame.listing_id.duplicated().any() or frame.log_price.isna().any() or not np.allclose(frame.log_price,np.log(frame.price_nightly)):
                raise ValueError('Sample keys/observed outcome invalid; no imputation')
            required=design['models']['MEW'];missing=frame[required].isna().any(axis=1)
            association=frame.loc[~missing].copy();flow.extend([{'stage':'common_prediction','n':len(frame)},{'stage':'common_ols_association','n':len(association)}])
            summary={'city':city,'status':'COMMON_SAMPLES_FROZEN','prediction_n':len(frame),'association_n':len(association),
                     'association_missing_fraction':float(missing.mean()),'association_inference_status':'BLOCKED_MATERIAL_MISSINGNESS' if missing.mean()>design['association_missing_limit'] else 'READY_FOR_RANK_DIAGNOSTIC',
                     'sample_flow':flow,'group_counts':frame.operational_group.value_counts().sort_index().to_dict(),
                     'record_sha256':canonical_hash(json_records(frame)),'required_predictor_missing':frame[required].isna().sum().to_dict(),
                     'all_models_same_rows':True,'historical_sample_reused':False,'outcome_imputed':False,'metric_crs':cities[city]['metric_crs']}
            try:
                summary['support']=support(frame.operational_group,set(cities[city]['operational_mapping'].values()))
                folds=outer_splits(frame,city);summary['primary_fold_status']='QUALIFIED'
            except ValueError as exc:
                folds=None;summary['primary_fold_status']='BLOCKED';summary['fold_blocker']=str(exc)
            with engine.begin() as conn:
                identity=commit_package(conn,city=city,family='sample',summary=summary,
                                        records={'prediction_sample':json_records(frame),'association_sample':json_records(association)},
                                        deps=dependencies({'source':source,'upstream':{f:chosen[f][city] for f in chosen}}))
            selected[city]={'run_id':identity,'summary_sha256':canonical_hash(summary)}
            public[city]={'sample':summary,'validation':None}
            if folds is not None:
                outer=[];inner=[];fold_summary=[]
                for scheme,parts in folds.items():
                    for fold,tr,te in parts:
                        outer.extend({'listing_id':str(frame.iloc[i].listing_id),'scheme':scheme,'outer_test_fold':str(fold)} for i in te)
                        splits=inner_splits(frame.iloc[tr])
                        for f,(_,validation_indices) in enumerate(splits,1):
                            inner.extend({'listing_id':str(frame.iloc[tr[i]].listing_id),'scheme':scheme,'outer_fold':str(fold),'inner_validation_fold':f} for i in validation_indices)
                        fold_summary.append({'scheme':scheme,'fold':str(fold),'train_n':len(tr),'test_n':len(te),'inner_folds':len(splits)})
                freeze_summary={'city':city,'status':'FOLDS_FROZEN','outer_test_membership_n':len(outer),'inner_membership_n':len(inner),
                                'outer_hash':canonical_hash(outer),'inner_hash':canonical_hash(inner),'metric_crs':cities[city]['metric_crs'],
                                'training_rule':'Outer train is complement of saved test membership; inner train is complement within outer train',
                                'outcomes_used_for_membership':False,'folds':fold_summary,'sample':selected[city]}
                with engine.begin() as conn:
                    fold_id=commit_package(conn,city=city,family='validation',summary=freeze_summary,
                                           records={'outer_test':outer,'inner_validation':inner},deps=dependencies({'sample':selected[city]}))
                validation[city]={'run_id':fold_id,'summary_sha256':canonical_hash(freeze_summary)}
                public[city]['validation']=freeze_summary
            print(city,'prediction',len(frame),'association',len(association),'folds',summary['primary_fold_status'],flush=True)
        write_once(target,(json.dumps(selected,indent=2)+'\n').encode())
        write_once(PROJECT_ROOT/'config/study/validation_selection.json',(json.dumps(validation,indent=2)+'\n').encode())
        write_once(PROJECT_ROOT/'docs/analysis/sample_audit.json',(json.dumps(public,indent=2,ensure_ascii=False)+'\n').encode())
    finally:engine.dispose()
    return public
