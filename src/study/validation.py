"""Outcome-blind validation for the frozen common city sample."""
from __future__ import annotations
import numpy as np
from sklearn.model_selection import KFold
from src.pipeline.build_validation_splits import grouped_labels
from src.study.specification import load_design


def support(groups,expected,minimum_test=15,minimum_train=500):
    labels,counts=np.unique(np.asarray(groups),return_counts=True)
    if set(labels)!=set(expected):
        raise ValueError('Every frozen operational group must remain in the final sample')
    total=int(counts.sum())
    failures=[{'group':str(g),'test_n':int(n),'train_n':total-int(n)} for g,n in zip(labels,counts,strict=True)
              if n<minimum_test or total-n<minimum_train]
    if failures:
        raise ValueError('BLOCKED geographic support: '+str(failures))
    return [{'group':str(g),'test_n':int(n),'train_n':total-int(n),'former_30_met':bool(n>=30)} for g,n in zip(labels,counts,strict=True)]


def inner_splits(train):
    design,_=load_design();v=design['validation']
    coordinates=train[['metric_x','metric_y']].to_numpy(float)
    if not np.isfinite(coordinates).all():raise ValueError('Invalid metric coordinates')
    grid=np.floor(coordinates/v['inner_grid_m']).astype(int)
    groups=np.asarray([f'{x}:{y}' for x,y in grid])
    labels=grouped_labels(groups,v['inner_spatial_folds'],v['inner_seed'])
    return [(np.flatnonzero(labels!=f),np.flatnonzero(labels==f)) for f in range(1,v['inner_spatial_folds']+1)]


def outer_splits(frame,city):
    design,cities=load_design();v=design['validation']
    if not frame.city.eq(city).all() or frame.listing_id.duplicated().any():raise ValueError('City sample/key isolation failed')
    groups=frame.operational_group.to_numpy()
    expected=set(cities[city]['operational_mapping'].values())
    support(groups,expected,v['minimum_test'],v['minimum_train'])
    result={'neighbourhood':[(g,np.flatnonzero(groups!=g),np.flatnonzero(groups==g)) for g in sorted(expected)]}
    result['random']=[(str(f),tr,te) for f,(tr,te) in enumerate(KFold(v['random_folds'],shuffle=True,random_state=v['random_seed']).split(frame),1)]
    xy=frame[['metric_x','metric_y']].to_numpy(float)
    if not np.isfinite(xy).all():raise ValueError('Invalid metric coordinates')
    for size in v['geometric_sizes_m']:
        for fx,fy in v['geometric_origins_fractions']:
            block=np.floor((xy-np.array([size*fx,size*fy]))/size).astype(int)
            labels=grouped_labels(np.array([f'{x}:{y}' for x,y in block]),v['geometric_folds'],v['random_seed']+size+int(fx*100+fy*10))
            key=f'blocks_{size}m_origin_{fx:g}_{fy:g}'.replace('.','p')
            result[key]=[(str(f),np.flatnonzero(labels!=f),np.flatnonzero(labels==f)) for f in range(1,v['geometric_folds']+1)]
    for scheme,folds in result.items():
        visits=np.zeros(len(frame),int)
        for _,tr,te in folds:
            if set(tr)&set(te) or len(tr)+len(te)!=len(frame) or len(tr)<v['minimum_train'] or len(te)<v['minimum_test']:
                raise ValueError('Validation leakage, partition or support failure: '+scheme)
            visits[te]+=1
        if not np.all(visits==1):raise ValueError('Each observation must be held out exactly once per scheme')
    return result
