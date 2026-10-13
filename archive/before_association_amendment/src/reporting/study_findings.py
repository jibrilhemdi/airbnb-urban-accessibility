"""Read-only, code-generated RQ interpretation from verified authoritative results."""
from __future__ import annotations
import json
import pandas as pd
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.study.sources import get_engine,write_once
from src.study.specification import CITIES,MODELS
from src.reporting.study_report import selected,markdown


def run():
    engine=get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            primary=selected(conn,'results_neighbourhood');transfer=selected(conn,'results_transfer');measure=selected(conn,'interpretation_selection')
            schemes=['random']+[f'blocks_{size}m_origin_{origin}' for size in [1000,1500,2000] for origin in ['0_0','0p5_0p5']]
            alternatives={scheme:selected(conn,'results_'+scheme) for scheme in schemes}
        measurements=[];local=[];geographic=[];direction=[]
        for city in CITIES:
            for row in measure[city]['measurement']:
                if row['concept'] in ['station','bus']:
                    measurements.append({'city':city,'concept':row['concept'],'unit':'km','euclidean_median':row['euclidean_km']['median'],
                                         'walking_median':row['walking_km']['median']})
                elif row['minutes']==10:
                    measurements.append({'city':city,'concept':row['concept'],'unit':'10-minute opportunities','euclidean_median':row['euclidean_opportunities']['median'],
                                         'walking_median':row['walking_opportunities']['median']})
            for row in primary[city]['contrasts']:
                if row['reference']=='M0':local.append({'city':city,'estimator':row['estimator'],'model':row['added'],
                                                       'delta_rmse':row['delta_rmse'],'percentage_change':100*row['proportional_change'],
                                                       'stability_low':row['stability_low'],'stability_high':row['stability_high']})
            for estimator in ['OLS','XGBoost']:
                for model in ['ME','MW','MEW']:
                    deltas={}
                    for scheme,result in alternatives.items():
                        scores=pd.DataFrame(result[city]['performance']);part=scores.loc[scores.estimator==estimator].set_index('model')
                        deltas[scheme]=float(part.loc[model,'rmse']-part.loc['M0','rmse'])
                    p=next(r for r in primary[city]['contrasts'] if r['estimator']==estimator and r['added']==model and r['reference']=='M0')
                    geographic.append({'city':city,'estimator':estimator,'model':model,'primary_delta_rmse':p['delta_rmse'],
                                       'random_delta_rmse':deltas['random'],'improving_geometric_variants':sum(v<0 for k,v in deltas.items() if k!='random'),
                                       'geometric_variants':6,'geometric_delta_min':min(v for k,v in deltas.items() if k!='random'),
                                       'geometric_delta_max':max(v for k,v in deltas.items() if k!='random')})
            for row in transfer[city]['contrasts']:
                if row['reference']=='M0':direction.append({'source_city':row['source_city'],'target_city':row['target_city'],'estimator':row['estimator'],'model':row['added'],
                                                            'delta_rmse':row['delta_rmse'],'percentage_change':100*row['proportional_change'],
                                                            'stability_low':row['stability_low'],'stability_high':row['stability_high']})
        output=['# Generated findings and interpretation',
                'Read with the [publication research handover](research_report_publication.md). All numerical values below are extracted from verified authoritative SQL summaries by `python -m src.reporting.study_findings`; no previous analysis value or result prose is substituted.',
                '## RQ1: representation changes measurement',markdown(measurements),
                'Network travel generally lengthens nearest-category distances and reduces the median locally reachable opportunities relative to matched straight-line measures. The table describes the analytical sample, not all destinations or listings in a city. Nearest destinations can differ between representations, so these differences are not same-destination circuity. The map and full distributions provide the spatial and distributional detail.',
                '## RQ2: incremental within-city prediction',markdown(local),
                'Negative changes favour the accessibility model. The neighbourhood results show improvements in Copenhagen and Stockholm, with small adverse changes in Oslo. Walking is not universally superior to Euclidean accessibility, and adding both representations does not always beat either alone. The reported stability ranges describe geographic composition sensitivity; their signs do not establish causal effects or statistical equivalence.',
                '## RQ3: gains depend on geographic separation',markdown(geographic),
                'Neighbourhood and geometric validation answer different generalization questions. The following sign counts are descriptive comparisons across correlated fixed designs; they are not independent replications or pooled significance tests. A gain in primary neighbourhood validation can reverse when the held-out units change. Random validation remains a benchmark and does not certify geographically unseen performance. Different error levels across cities also reflect their outcome distributions and sample supports.']
        for row in geographic:
            if row['estimator']=='XGBoost' and row['model']=='MW':
                output.append(f"For XGBoost walking versus baseline in {row['city'].title()}, the neighbourhood ΔRMSE is {row['primary_delta_rmse']:+.6f}; random ΔRMSE is {row['random_delta_rmse']:+.6f}; walking lowers error in {row['improving_geometric_variants']} of the {row['geometric_variants']} registered geometric variants.")
        output+=['## RQ4: relative pricing relationships transfer unevenly',markdown(direction),
                 'These tests remove citywide price-level differences using an observed target benchmark. They evaluate relative pricing transfer and do not demonstrate absolute-price deployment in a truly unseen city. Reversing a direction changes both the fitted source relationship and the target distribution; asymmetric errors and bias are expected to require substantive interpretation rather than an assumption of interchangeability. No target correction was applied.']
        for estimator in ['OLS','XGBoost']:
            for model in ['ME','MW','MEW']:
                rows=[r for r in direction if r['estimator']==estimator and r['model']==model]
                output.append(f"{estimator} {model} lowers relative-price RMSE versus M0 in {sum(r['delta_rmse']<0 for r in rows)} of {len(rows)} directions. This count summarizes heterogeneous patterns and is not an independent-direction significance test.")
        output+=['## Inferential limitation',
                 'Copenhagen and Oslo association coefficients and registered dependent checks are complete. Stockholm exceeds the frozen 5% union predictor-missingness guard, so its association and dependent inference remain blocked. Predictive median/indicator preprocessing was training-only and was not substituted for inferential imputation. All outcomes remain observed original asking prices. The full study is partial despite complete independent predictive and transfer work.']
        path=PROJECT_ROOT/'docs/analysis/findings.md';write_once(path,('\n\n'.join(output)+'\n').encode())
        tables=PROJECT_ROOT/'outputs/tables/research'
        for name,rows in [('interpretation_measurements',measurements),('interpretation_local_gains',local),('interpretation_geographic_consistency',geographic),('interpretation_transfer_gains',direction)]:
            write_once(tables/(name+'.csv'),pd.DataFrame(rows).to_csv(index=False).encode())
        return {'status':'GENERATED_FROM_VERIFIED_SQL','finding_file_sha256':sha256_file(path),'geographic_rows':len(geographic),'directional_rows':len(direction)}
    finally:engine.dispose()


if __name__=='__main__':print(json.dumps(run(),indent=2))
