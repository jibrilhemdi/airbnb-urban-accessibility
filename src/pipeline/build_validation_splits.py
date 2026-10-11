"""Freeze random, eleven-area, buffered and shifted geometric outer/inner folds."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold,GroupKFold
from sqlalchemy import text
from src.db.connection import get_engine
from src.ingestion.common import PROJECT_ROOT,write_json
from src.pipeline.protocol import AREA_NAMES,DESIGN,SEED,INNER_SEED,canonical_hash
from src.pipeline.build_analysis_dataset import load_dataset,dataset_hash
from src.pipeline.storage import export,json_records

def grouped_labels(groups,n_splits,seed):
    """Balance group sizes deterministically using no outcomes or predictors."""
    values,counts=np.unique(groups,return_counts=True)
    if len(values)<n_splits:raise RuntimeError('Insufficient groups for spatial validation')
    rng=np.random.default_rng(seed);order=rng.permutation(len(values));order=order[np.argsort(-counts[order],kind='stable')]
    totals=np.zeros(n_splits,dtype=int);mapping={}
    for i in order:
        fold=int(np.argmin(totals));mapping[values[i]]=fold+1;totals[fold]+=counts[i]
    return np.array([mapping[g] for g in groups])
def inner_splits(train):
    groups=(np.floor(train.metric_x/1000).astype(int).astype(str)+':'+np.floor(train.metric_y/1000).astype(int).astype(str)).to_numpy()
    labels=grouped_labels(groups,DESIGN['inner_folds'],INNER_SEED)
    return [(np.flatnonzero(labels!=f),np.flatnonzero(labels==f)) for f in range(1,DESIGN['inner_folds']+1)]
def make_outer(frame,buffer_membership=None):
    if set(frame.analysis_area)!=set(AREA_NAMES):raise RuntimeError('Exactly eleven peer areas required for primary geographic folds')
    n=len(frame);result={};random=np.zeros(n,dtype=int)
    for fold,(_,test) in enumerate(KFold(5,shuffle=True,random_state=SEED).split(frame),1):random[test]=fold
    for scheme,labels in [('random_5',random),('geographic_11',frame.analysis_area.to_numpy())]:
        result[scheme]=[(str(f),np.flatnonzero(labels!=f),np.flatnonzero(labels==f)) for f in sorted(set(labels))]
    for size in DESIGN['block_sizes_m']:
        for fx,fy in DESIGN['grid_origin_fractions']:
            groups=(np.floor((frame.metric_x-size*fx)/size).astype(int).astype(str)+':'+np.floor((frame.metric_y-size*fy)/size).astype(int).astype(str)).to_numpy()
            labels=grouped_labels(groups,5,SEED+size+int(fx*100+fy*10))
            result[f'blocks_{size}m_origin_{fx:g}_{fy:g}']=[(str(f),np.flatnonzero(labels!=f),np.flatnonzero(labels==f)) for f in range(1,6)]
    if buffer_membership is not None:
        for distance in DESIGN['buffers_m']:
            folds=[]
            for area in AREA_NAMES:
                test=np.flatnonzero(frame.analysis_area.to_numpy()==area)
                exclusion=buffer_membership[(distance,area)]
                train=np.flatnonzero((frame.analysis_area.to_numpy()!=area)&~exclusion)
                if len(train)<500 or len(test)<30:raise RuntimeError(f'Buffered fold infeasible: {area}, {distance} m')
                folds.append((area,train,test))
            result[f'buffered_area_{distance}m']=folds
    return result

def support_diagnostics(frame,splits):
    rows=[];record_rows=[]
    from src.pipeline.model_specification import FEATURES,CATEGORICAL
    for fold,tr,te in splits:
        train,test=frame.iloc[tr],frame.iloc[te];outside=np.zeros(len(te),bool)
        for variable in FEATURES['MEW']:
            if variable in CATEGORICAL:
                bad=~test[variable].isin(set(train[variable].dropna()));outside|=bad.to_numpy()
                rows.append({'heldout_analysis_area':fold,'variable':variable,'train_levels':json.dumps(sorted(train[variable].dropna().unique())),
                    'test_levels':json.dumps(sorted(test[variable].dropna().unique())),'outside_n':int(bad.sum()),'test_n':len(test),'outside_fraction':float(bad.mean())})
            else:
                tq=train[variable].quantile([0,.05,.25,.5,.75,.95,1]);vq=test[variable].quantile([0,.05,.25,.5,.75,.95,1])
                bad=(test[variable]<tq.iloc[0])|(test[variable]>tq.iloc[-1]);outside|=bad.to_numpy()
                row={'heldout_analysis_area':fold,'variable':variable,'outside_n':int(bad.sum()),'test_n':len(test),'outside_fraction':float(bad.mean())}
                for label,q in [('min',0),('q05',.05),('q25',.25),('median',.5),('q75',.75),('q95',.95),('max',1)]:row['train_'+label]=tq.loc[q];row['test_'+label]=vq.loc[q]
                rows.append(row)
        record_rows.append({'heldout_analysis_area':fold,'test_n':len(test),'records_outside_any_training_support_n':int(outside.sum()),'extrapolation_fraction':float(outside.mean())})
    return pd.DataFrame(rows),pd.DataFrame(record_rows)

def saved_outer(conn,frame,schemes=None):
    keys={(str(r['snapshot_date'])[:10],int(r['listing_id'])):i for i,r in frame.iterrows()}
    rows=conn.execute(text('SELECT snapshot_date,listing_id,scheme,outer_fold,role FROM v3_analysis.outer_assignments ORDER BY scheme,outer_fold,listing_id')).mappings().all()
    grouped={}
    for row in rows:
        if schemes is not None and row['scheme'] not in schemes:continue
        key=(row['scheme'],row['outer_fold']);grouped.setdefault(key,{'train':[],'test':[],'excluded':[]})[row['role']].append(keys[(str(row['snapshot_date']),row['listing_id'])])
    result={}
    for (scheme,fold),roles in grouped.items():result.setdefault(scheme,[]).append((fold,np.array(roles['train'],int),np.array(roles['test'],int)))
    if not result:raise RuntimeError('Saved V3 outer folds missing')
    return result

def assignment_hashes(conn):
    outer=[dict(snapshot=str(r[0]),id=int(r[1]),scheme=r[2],fold=r[3],role=r[4]) for r in conn.execute(text('SELECT snapshot_date,listing_id,scheme,outer_fold,role FROM v3_analysis.outer_assignments ORDER BY scheme,outer_fold,snapshot_date,listing_id'))]
    inner=[dict(snapshot=str(r[0]),id=int(r[1]),scheme=r[2],fold=r[3],inner=int(r[4])) for r in conn.execute(text('SELECT snapshot_date,listing_id,scheme,outer_fold,inner_fold FROM v3_analysis.inner_assignments ORDER BY scheme,outer_fold,snapshot_date,listing_id'))]
    return {'outer_assignments_sha256':canonical_hash(outer),'inner_assignments_sha256':canonical_hash(inner),'outer_rows':len(outer),'inner_rows':len(inner)}

def build(engine):
    with engine.connect() as conn:
        frame=load_dataset(conn);buffers={}
        for distance in DESIGN['buffers_m']:
            for area in AREA_NAMES:
                ids=set(conn.execute(text('SELECT l.listing_id FROM v3_clean.airbnb_listings l JOIN v3_spatial.analysis_areas a ON a.area_id=:area '
                    'WHERE ST_DWithin(l.geom_25832,a.geom_25832,:distance)'),{'area':area,'distance':distance}).scalars())
                buffers[(distance,area)]=frame.listing_id.isin(ids).to_numpy()
    outer=make_outer(frame,buffers);assignments=[];inners=[];summary=[]
    for scheme,folds in outer.items():
        for fold,tr,te in folds:
            train=frame.iloc[tr]
            inner=inner_splits(train)
            train_set,test_set=set(tr),set(te)
            if train_set & test_set:raise RuntimeError('Outer leakage')
            for i,row in frame.iterrows():
                assignments.append(dict(snapshot=str(row.snapshot_date)[:10],id=int(row.listing_id),scheme=scheme,fold=fold,role='train' if i in train_set else 'test' if i in test_set else 'excluded'))
            for f,(_,val) in enumerate(inner,1):
                for i in val:
                    row=train.iloc[i];inners.append(dict(snapshot=str(row.snapshot_date)[:10],id=int(row.listing_id),scheme=scheme,fold=fold,inner=f))
            summary.append({'scheme':scheme,'outer_fold':fold,'train_n':len(tr),'test_n':len(te),'excluded_n':len(frame)-len(tr)-len(te),'inner_folds':len(inner),'crs_epsg':25832})
    with engine.begin() as conn:
        if conn.scalar(text('SELECT count(*) FROM v3_analysis.outer_assignments')):raise RuntimeError('Validation assignments already frozen')
        conn.execute(text('INSERT INTO v3_analysis.outer_assignments(snapshot_date,listing_id,scheme,outer_fold,role) VALUES(:snapshot,:id,:scheme,:fold,:role)'),assignments)
        conn.execute(text('INSERT INTO v3_analysis.inner_assignments(snapshot_date,listing_id,scheme,outer_fold,inner_fold) VALUES(:snapshot,:id,:scheme,:fold,:inner)'),inners)
    details,areas=support_diagnostics(frame,outer['geographic_11'])
    export('validation','predictor_support.csv',details);export('validation','extrapolation_by_analysis_area.csv',areas);export('validation','fold_summary.csv',pd.DataFrame(summary))
    with engine.connect() as conn:hashes=assignment_hashes(conn)
    metadata={'version':'validation_splits_v3','dataset_sha256':dataset_hash(frame),**hashes,'design':DESIGN,'outcomes_used':False}
    write_json(PROJECT_ROOT/'outputs/tables/validation/splits_metadata.json',metadata);return metadata
if __name__=='__main__':
    engine=get_engine()
    try: print(json.dumps(build(engine),indent=2))
    finally:engine.dispose()
