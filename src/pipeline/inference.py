"""Small-area inference and paired geographic predictive uncertainty."""
from __future__ import annotations
import numpy as np
import pandas as pd
from src.pipeline.protocol import DESIGN,SEED,AREA_NAMES

def wild_cluster_bootstrap_t(X,y,groups,replications=None,seed=SEED):
    """Restricted wild cluster bootstrap-t (WCR11), Webb six-point weights.

    Fits H0: coefficient=0 separately for every term. Cluster-robust HC1
    studentisation is recomputed in every replication via exact sufficient
    statistics. No conventional small-cluster p-value is reported as definitive.
    """
    X=np.asarray(X,float);y=np.asarray(y,float);groups=np.asarray(groups)
    n,k=X.shape;labels=np.unique(groups);g=len(labels)
    if g<6 or n<=k or np.linalg.matrix_rank(X)!=k:raise RuntimeError('Wild bootstrap requires full-rank design and at least six areas')
    B=np.linalg.inv(X.T@X);beta=B@X.T@y;residual=y-X@beta
    H=np.array([X[groups==label].T@X[groups==label] for label in labels])
    scores=np.array([X[groups==label].T@residual[groups==label] for label in labels])
    adj=g/(g-1)*(n-1)/(n-k)
    se=np.sqrt(adj*np.sum((scores@B)**2,axis=0))
    repetitions=replications or DESIGN['wild_cluster_replications']
    webb=np.array([-np.sqrt(1.5),-1,-np.sqrt(.5),np.sqrt(.5),1,np.sqrt(1.5)])
    weights=np.random.default_rng(seed).choice(webb,size=(repetitions,g))
    rows=[]
    for j in range(k):
        if not np.isfinite(se[j]) or se[j]<=0:raise RuntimeError('Zero/invalid clustered studentising variance')
        shift=B[:,j]*(beta[j]/B[j,j])
        restricted_scores=scores+np.einsum('gij,j->gi',H,shift)
        delta=(weights@restricted_scores)@B
        boot_scores=weights*(restricted_scores@B[:,j])[None,:]-delta@np.einsum('gij,j->gi',H,B[:,j]).T
        boot_se=np.sqrt(adj*np.sum(boot_scores**2,axis=1))
        if not np.isfinite(boot_se).all() or np.any(boot_se<=0):raise RuntimeError('Bootstrap studentisation failed; no silent removal of draws')
        t_observed=beta[j]/se[j];t_boot=delta[:,j]/boot_se
        p=(1+np.sum(np.abs(t_boot)>=abs(t_observed)))/(repetitions+1)
        rows.append({'term_index':j,'wild_cluster_p_value':float(p),'cluster_t_statistic':float(t_observed),
            'wild_replications':repetitions,'clusters':g,'wild_method':'restricted WCR11; Webb six-point; CRV1 studentisation','wild_seed':seed})
    return pd.DataFrame(rows)

COMPARISONS=[('ME','M0'),('MW','M0'),('MEW','M0'),('MW','ME')]
def paired_incremental(oof,replications=None,seed=SEED,comparisons=None):
    """Delta = added minus reference: negative errors favour added features.

    Resample the eleven areas with replacement, retaining every listing in
    each selected area. Metrics are recomputed from paired loss sums/counts;
    RMSE differences are never approximated by differences in mean RMSE.
    """
    area_rows=[];pooled_rows=[];bootstrap_rows=[]
    repetitions=replications or DESIGN['area_bootstrap_replications']
    for (scheme,model),part in oof.groupby(['scheme','model']):
        if model=='train_mean':continue
        for added,reference in (comparisons if comparisons is not None else COMPARISONS):
            a=part.loc[part.feature_set==added];b=part.loc[part.feature_set==reference]
            paired=a.merge(b,on=['snapshot_date','listing_id','outer_fold','analysis_area'],suffixes=('_added','_reference'),validate='one_to_one')
            if len(paired)!=len(a) or len(paired)!=len(b):raise RuntimeError('Paired OOF losses do not share observations')
            if not np.allclose(paired.log_price_added,paired.log_price_reference):raise RuntimeError('Paired outcome mismatch')
            pooled={'scheme':scheme,'model':model,'added':added,'reference':reference,'n':len(paired),
                'delta_rmse':float(np.sqrt(paired.squared_error_added.mean())-np.sqrt(paired.squared_error_reference.mean())),
                'delta_mae':float(paired.absolute_error_added.mean()-paired.absolute_error_reference.mean())}
            area=[]
            for name,p in paired.groupby('analysis_area'):
                row={'scheme':scheme,'model':model,'added':added,'reference':reference,'analysis_area':name,'n':len(p),
                    'delta_rmse':float(np.sqrt(p.squared_error_added.mean())-np.sqrt(p.squared_error_reference.mean())),
                    'delta_mae':float(p.absolute_error_added.mean()-p.absolute_error_reference.mean())}
                area_rows.append(row);area.append(row)
            if scheme=='geographic_11':
                if set(paired.analysis_area)!=set(AREA_NAMES):raise RuntimeError('Primary uncertainty needs all eleven held-out areas')
                sums=paired.groupby('analysis_area').agg(n=('listing_id','size'),sa=('squared_error_added','sum'),sb=('squared_error_reference','sum'),aa=('absolute_error_added','sum'),ab=('absolute_error_reference','sum')).sort_index()
                draws=np.random.default_rng(seed).integers(0,11,size=(repetitions,11))
                n=sums.n.to_numpy()[draws].sum(axis=1)
                dr=np.sqrt(sums.sa.to_numpy()[draws].sum(axis=1)/n)-np.sqrt(sums.sb.to_numpy()[draws].sum(axis=1)/n)
                dm=(sums.aa.to_numpy()[draws].sum(axis=1)-sums.ab.to_numpy()[draws].sum(axis=1))/n
                for metric,values in [('rmse',dr),('mae',dm)]:
                    pooled['delta_'+metric+'_bootstrap_low']=float(np.quantile(values,.025));pooled['delta_'+metric+'_bootstrap_high']=float(np.quantile(values,.975))
                    pooled['bootstrap_fraction_'+metric+'_improved']=float(np.mean(values<0))
                    arr=np.array([r['delta_'+metric] for r in area]);pooled['area_delta_'+metric+'_median']=float(np.median(arr));pooled['area_delta_'+metric+'_q25']=float(np.quantile(arr,.25));pooled['area_delta_'+metric+'_q75']=float(np.quantile(arr,.75))
                bootstrap_rows.extend({'scheme':scheme,'model':model,'added':added,'reference':reference,'replication':i+1,'delta_rmse':float(dr[i]),'delta_mae':float(dm[i]),'resampled_listing_n':int(n[i])} for i in range(repetitions))
                pooled['bootstrap_replications']=repetitions;pooled['bootstrap_seed']=seed
            pooled_rows.append(pooled)
    return pd.DataFrame(pooled_rows),pd.DataFrame(area_rows),pd.DataFrame(bootstrap_rows)
