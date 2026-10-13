"""Source-traceable RQ findings, claims and thesis recommendations; no new fits."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from src.ingestion.common import sha256_file
from src.study.sources import write_once
from src.reporting.thesis_sources import ROOT,CITIES,LABELS,MODELS,SCHEMES,verify_catalog
from src.reporting.thesis_tables import markdown,VALIDATION_LABELS

COMMAND='.venv/bin/python -m src.reporting.thesis_synthesis'
MAIN_FIGURES=['study_areas','nearest_access_relationship','opportunity_comparison','primary_model_performance',
              'paired_accessibility_contrasts','validation_strategy_comparison','neighbourhood_performance_variation',
              'transfer_performance','transfer_network_comparison','directional_transfer_asymmetry']
MAIN_TABLES=['city_sample_summary','accessibility_descriptive_statistics','primary_predictive_performance','paired_model_contrasts',
             'validation_comparison','transfer_performance','transfer_contrasts','claims_and_limitations']
REASONS={
 'study_areas':('Design','Show the actual provider validation geography across all cities','Operational neighbourhoods are the geographic holdouts','Methods: study design'),
 'nearest_access_relationship':('RQ1','Reveal paired measurement relationships rather than isolated averages','Nearest network distances exceed straight-line distances; destinations can differ','Results: accessibility measurement'),
 'opportunity_comparison':('RQ1','Show both food/social and culture/tourism reachability','Matched walking opportunities are lower than straight-line opportunities','Results: accessibility measurement'),
 'primary_model_performance':('RQ2','Establish all four pooled model results with fold variation','Accessibility gains depend on city and estimator','Results: within-city prediction'),
 'paired_accessibility_contrasts':('RQ2','Put baseline gain, replacement and add-on on one clear scale','MW−ME and MEW−ME answer different comparisons','Results: accessibility contributions'),
 'validation_strategy_comparison':('RQ3','Compare geographically unseen evaluation with random CV','Changing holdout geometry changes error and model ordering','Results: geographic generalization'),
 'neighbourhood_performance_variation':('RQ3','Prevent citywide means from hiding local heterogeneity','Every heldout neighbourhood contributes an observed paired score','Results: spatial heterogeneity'),
 'transfer_performance':('RQ4','Cover six directions and all model ladders in one landscape figure','Source/target combinations have heterogeneous relative-price errors','Results: cross-city transfer'),
 'transfer_network_comparison':('RQ4','Expose network replacement and add-on directly','Walking is not universally better than Euclidean transfer','Results: transfer accessibility contributions'),
 'directional_transfer_asymmetry':('RQ4','Make direction reversal explicit','Different source/target tasks are not interchangeable','Results: transfer asymmetry')}


def run():
    catalog=verify_catalog();manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text());items=manifest['items'];claims=[];dependencies={}
    for item in items:
        if sha256_file(ROOT/item['filename'])!=item['sha256']:raise ValueError('Generated artifact differs before synthesis')
    def table(name,category='tables'):
        path=ROOT/f'outputs/{category}/thesis/{name}.csv';dependencies[str(path.relative_to(ROOT))]=sha256_file(path)
        return pd.read_csv(path)
    samples=table('city_sample_summary');desc=table('accessibility_descriptive_statistics');primary=table('primary_predictive_performance')
    paired=table('paired_model_contrasts');validation=table('validation_comparison');transfer=table('transfer_performance');tpaired=table('transfer_contrasts')
    association=table('association_results');robust=table('robustness_registry');neighbourhood=table('neighbourhood_performance','metrics');asym=table('directional_transfer_asymmetry','metrics')
    def numeric(identifier,source,column,filters,value,meaning):
        claims.append({'id':identifier,'source_file':source,'source_sha256':dependencies[source],'column':column,
                       'filters':filters,'value':float(value),'meaning':meaning})
        return float(value)
    def fig(name,caption):return f'![{caption}](../outputs/figures/thesis/{name}.png)\n\n'+caption
    def link(name,category='tables'):return f'[{name.replace("_"," ")}](../outputs/{category}/thesis/{name}.md)'
    nearest=[];opportunities=[]
    for city in [LABELS[c] for c in CITIES]:
        for concept in ['station','bus','food','culture']:
            part=desc.loc[(desc.city==city)&(desc.concept==concept)].set_index('representation')
            e=float(part.loc['Euclidean','median']);w=float(part.loc['Walking','median'])
            source='outputs/tables/thesis/accessibility_descriptive_statistics.csv'
            for measure,value in [('Euclidean',e),('Walking',w)]:numeric(f'RQ1_{city}_{concept}_{measure}',source,'median',{'city':city,'concept':concept,'representation':measure},value,'Frozen median accessibility')
            row={'City':city,'Concept':concept,'Euclidean median':e,'Walking median':w,'Unit':part.loc['Euclidean','unit']}
            (nearest if concept in ['station','bus'] else opportunities).append(row)
    local=[];direct=[]
    for r in paired.loc[(paired.estimator=='XGBoost')&(paired.reference=='M0')].itertuples():
        pct=100*r.proportional_change;source='outputs/tables/thesis/paired_model_contrasts.csv'
        numeric(f'RQ2_{r.city}_{r.added}',source,'delta_rmse',{'city':r.city,'estimator':r.estimator,'added':r.added,'reference':'M0'},r.delta_rmse,'XGBoost primary ΔRMSE')
        local.append({'City':r.city,'Model':r.added,'ΔRMSE':r.delta_rmse,'% RMSE change':pct,'Stability low':r.stability_low,'Stability high':r.stability_high})
    direct=paired.loc[paired.reference=='ME',['city','estimator','added','reference','delta_rmse','stability_low','stability_high']]
    generalization=[]
    for city in [LABELS[c] for c in CITIES]:
        for estimator in ['OLS','XGBoost']:
            base=validation.loc[(validation.city==city)&(validation.estimator==estimator)].set_index(['scheme','model'])
            block_deltas=[float(base.loc[(VALIDATION_LABELS[scheme],'MW'),'rmse']-base.loc[(VALIDATION_LABELS[scheme],'M0'),'rmse']) for scheme in SCHEMES[2:]]
            row={'City':city,'Estimator':estimator,'Primary M0 RMSE':base.loc[('Neighbourhood','M0'),'rmse'],
                 'Random M0 RMSE':base.loc[('Random','M0'),'rmse'],
                 'MW improves geometric variants':sum(d<0 for d in block_deltas),'Geometric variants':6}
            # Exported validation labels are human-readable; resolve block labels from the table itself below.
            generalization.append(row)
    counts=[]
    for estimator in ['OLS','XGBoost']:
        for model in ['ME','MW','MEW']:
            part=tpaired.loc[(tpaired.estimator==estimator)&(tpaired.added==model)&(tpaired.reference=='M0')]
            counts.append({'Estimator':estimator,'Model':model,'Improving directions':int(part.delta_rmse.lt(0).sum()),'Directions':len(part)})
    supported=[
     ('Accessibility measurements differ on matched categories','SUPPORTED','RQ1','Nearest relationships and opportunity summaries; compare final samples, not every listing/destination'),
     ('Accessibility lowers primary XGBoost RMSE in Copenhagen and Stockholm','SUPPORTED_WITH_QUALIFICATION','RQ2','Point gains on frozen neighbourhood validation; composition intervals can include zero'),
     ('Accessibility universally improves primary prediction','NOT_SUPPORTED','RQ2','Oslo point changes are adverse; estimator/validation dependence remains'),
     ('Walking accessibility is universally superior to Euclidean accessibility','NOT_SUPPORTED','RQ2/RQ4','Replacement/add-on contrasts vary by city, estimator and direction'),
     ('Euclidean and walking predictions are statistically equivalent','NOT_SUPPORTED','RQ2','Overlapping stability ranges or small point differences do not establish equivalence'),
     ('Geographic validation is harder than random CV for the observed primary tasks','SUPPORTED_WITH_QUALIFICATION','RQ3','Frozen task-specific M0 comparisons; not a universal rule for every configuration'),
     ('Primary accessibility gains are geographically uniform','NOT_SUPPORTED','RQ3','Neighbourhood and block results show heterogeneity and reversals'),
     ('Transferability depends on source/target direction','SUPPORTED_WITH_QUALIFICATION','RQ4','Observed relative-price errors and reversals; target distributions and N also change'),
     ('All six directions are independent significance-test replications','DO_NOT_CLAIM','RQ4','Shared source pipelines and overlapping targets invalidate that interpretation'),
     ('Relative-price transfer is zero-shot absolute-price deployment','DO_NOT_CLAIM','RQ4','Target reference mean uses observed target prices; no absolute deployment test'),
     ('Accessibility causes Airbnb prices or housing displacement','DO_NOT_CLAIM','All','Observational asking prices and adjusted associations do not identify causality'),
     ('Results represent every Nordic or European city','DO_NOT_CLAIM','All','Three selected capital-city samples do not establish that external validity'),
     ('The 10% eligibility limit was preregistered or universal','DO_NOT_CLAIM','RQ2','Explicitly changed after observing Stockholm missingness; complete-case selection remains a limitation')]
    claim_rows=[{'Candidate claim':a,'Status':b,'RQ':c,'Evidence and qualification':d} for a,b,c,d in supported]
    write_once(ROOT/'docs/final_claims_for_thesis.md',('# Final scientific claims for the thesis\n\nCopenhagen includes Frederiksberg. Claims refer only to the frozen final rerun and the disclosed post-observation10% association eligibility amendment.\n\n'+markdown(claim_rows)+'\n\nEvidence: [primary paired contrasts](../outputs/tables/thesis/paired_model_contrasts.md), [validation](../outputs/tables/thesis/validation_comparison.md), [transfer contrasts](../outputs/tables/thesis/transfer_contrasts.md) and [association results](../outputs/tables/thesis/association_results.md).\n').encode())
    recommendations=[]
    for name in MAIN_FIGURES:
        rq,reason,takeaway,section=REASONS[name];record=next(i for i in items if i['logical_name']==name and i['filename'].endswith('.pdf'))
        recommendations.append({'kind':'figure','name':name,'file':record['filename'],'research_question':rq,'reason':reason,'takeaway':takeaway,'suggested_section':section,'placement':'MAIN','source_catalog_sha256':record['source_catalog_sha256']})
    for name in MAIN_TABLES:
        record=next(i for i in items if i['logical_name']==name and i['filename'].endswith('.md'))
        recommendations.append({'kind':'table','name':name,'file':record['filename'],'research_question':record['research_question'],
                                'reason':'Compact factual basis for the associated RQ; full precision stays in CSV','takeaway':record['caption'],
                                'suggested_section':'Methods: samples' if name=='city_sample_summary' else 'Results: '+record['research_question'],
                                'placement':'MAIN','source_catalog_sha256':record['source_catalog_sha256']})
    for item in items:
        if item['kind']=='figure' and item['filename'].endswith('.pdf') and item['logical_name'] not in MAIN_FIGURES:
            recommendations.append({'kind':'figure','name':item['logical_name'],'file':item['filename'],'research_question':item['research_question'],
                                    'reason':'Useful diagnostic/complementary evidence; avoids duplicating the main narrative','takeaway':item['caption'],
                                    'suggested_section':'Appendix: '+item['research_question'],'placement':'APPENDIX','source_catalog_sha256':item['source_catalog_sha256']})
    write_once(ROOT/'reports/thesis_recommendations.json',(json.dumps(recommendations,indent=2,ensure_ascii=False)+'\n').encode())
    lines=['# Thesis figure and table recommendations','Ten main figures and eight main tables; eight further figures belong in appendices. Full feature definitions, all-model association coefficients, robustness registry, source support and aggregate diagnostics remain appendix/supplement tables. Landscape figures are explicitly marked in the artifact manifest. Use PDF/SVG in the thesis and PNG for review.','| Placement | Kind | RQ | Artifact | Reason | Takeaway | Thesis section |','| --- | --- | --- | --- | --- | --- | --- |']
    lines.extend('| '+' | '.join([r['placement'],r['kind'],r['research_question'],f"[{r['name']}](../{r['file']})",r['reason'],r['takeaway'],r['suggested_section']])+' |' for r in recommendations)
    write_once(ROOT/'reports/thesis_figure_recommendations.md',('\n\n'.join(lines)+'\n').encode())
    q1=['## RQ1','### 1. Evidence used',link('accessibility_descriptive_statistics')+'; '+link('nearest_access_divergence','metrics')+'; nearest relationships, opportunities and suppressed spatial maps.',
        '### 2. Headline result','Network and straight-line representations differ despite matched destination universes: walking nearest-category distances are longer and median reachable opportunities are fewer in these three samples.',
        '### 3. Important quantitative results',markdown(nearest),markdown(opportunities),
        '### 4. City heterogeneity','Distance distributions, food/culture opportunity levels and within-city spatial variation differ. Absolute counts also reflect different destination universes and source completeness.',
        '### 5. Robustness','Frozen15/20-minute, speed4/5.4 km/h, continuous decay and boundary-exclusion results are accounted for in the robustness registry; they do not redefine the primary10-minute/833 m comparison.',
        '### 6. Interpretation','Representations change the measured proximity/reachability concept. Nearest Euclidean and network destinations may differ, so distance excess is not same-destination route circuity.',
        '### 7. What cannot be claimed','No causal price effect, perfect OSM completeness, exact official neighbourhood equivalence or same-object route-circuity claim.',
        '### 8. Recommended figures/tables','Main: nearest-access relationships and opportunity comparison; T3. Appendix: nearest distance excess and accessibility maps.']
    q2=['## RQ2','### 1. Evidence used',link('primary_predictive_performance')+'; '+link('paired_model_contrasts')+'; '+link('association_results')+'; existing heldout contributions.',
        '### 2. Headline result','Primary accessibility models lower XGBoost point RMSE in Copenhagen and Stockholm but produce small adverse point changes in Oslo. Representation replacement and add-on are distinct; walking is not universally superior.',
        '### 3. Important quantitative results',markdown(local,precision=6),markdown(direct,precision=6),
        '### 4. City heterogeneity','The direction and magnitude vary by city and estimator. Complementary complete-case OLS associations describe adjustments conditional on X/E/W, not the heldout predictive estimand.',
        '### 5. Robustness','Frozen paired ranges describe neighbourhood-composition stability, not independent-sample confidence intervals. Reputation/tail/sample variants and geographic designs qualify the primary point pattern.',
        '### 6. Interpretation','Incremental prediction concerns information under the specified evaluation. HC3 and9,999 restricted Webb results are separately reported; SHAP allocation among correlated features is descriptive.',
        '### 7. What cannot be claimed','No causal coefficients, universal network superiority, significance from citywide point differences alone or statistical equivalence from overlapping intervals. The10% association eligibility change was post-observation.',
        '### 8. Recommended figures/tables','Main: model performance and all five paired contrasts; T4/T5. Appendix: complete-case coefficient figure/full T6 and frozen heldout feature contributions.']
    q3=['## RQ3','### 1. Evidence used',link('validation_comparison')+'; '+link('neighbourhood_performance','metrics')+'; '+link('robustness_registry')+'.',
        '### 2. Headline result','Geographic holdouts increase baseline error relative to random CV in these primary tasks, and accessibility gains vary across heldout neighbourhoods and geometric configurations.',
        '### 3. Important quantitative results',markdown(generalization,precision=6),
        '### 4. City heterogeneity','The geometric sign counts are descriptive comparisons of six correlated fixed configurations. They do not turn a neighbourhood gain into universal geographically unseen improvement.',
        '### 5. Robustness','All registered statuses remain explicit. Within-variant paired changes are comparable within each row; absolute errors across sample-changing variants are not a model-selection ranking.',
        '### 6. Interpretation','Validation geography changes the prediction task. Few groups, uneven fold sizes, overlapping training data and residual spatial dependence qualify stability and generalization statements.',
        '### 7. What cannot be claimed','No independent replication across grids, universal superiority, spatially independent errors or generalization to all Nordic cities.',
        '### 8. Recommended figures/tables','Main: strategy comparison and heldout-neighbourhood variation; T7. Appendix: robustness contrasts/full T10 and spatial diagnostics.']
    q4=['## RQ4','### 1. Evidence used',link('transfer_performance')+'; '+link('transfer_contrasts')+'; '+link('directional_transfer_asymmetry','metrics')+'; suppressed frozen-prediction diagnostics.',
        '### 2. Headline result','Relative-price transfer depends on source/target direction, estimator and representation. Accessibility helps in some directions and hurts in others; source-only transfer is not interchangeable across cities.',
        '### 3. Important quantitative results',markdown(counts),markdown(asym[['first_city','second_city','estimator','model','forward_rmse','reverse_rmse','forward_minus_reverse_rmse']],precision=6),
        '### 4. City heterogeneity','Each direction changes source covariate support and target distribution/sample size. Price centring removes citywide mean levels but not dispersion or conditional relationships.',
        '### 5. Robustness','All four models use identical target rows within each direction. Existing target-neighbourhood composition ranges are preserved; the identical source pipeline serves its two outgoing targets.',
        '### 6. Interpretation','These experiments evaluate structural relative-price transfer with an observed target benchmark; no target fitting, tuning, recalibration or pooled-source model is used.',
        '### 7. What cannot be claimed','No zero-shot absolute-price deployment or pseudo-independent six-direction significance test. Prediction diagnostic slopes and bins never alter model parameters.',
        '### 8. Recommended figures/tables','Main: performance matrices, network replacement/add-on and reversal asymmetry; T8/T9. Appendix: baseline-gain matrices and saved-prediction diagnostic panels.']
    write_once(ROOT/'reports/findings_by_research_question.md',('# Findings by research question\n\nCopenhagen includes Frederiksberg. All values below come from the final-run registered tables; no historical numeric result is substituted.\n\n'+'\n\n'.join(q1+q2+q3+q4)+'\n').encode())
    report=['# Thesis-ready research results','Copenhagen includes Frederiksberg. This reporting-only synthesis uses the frozen final rerun; no model was refitted. Within-city Y is log original positive nightly asking price. Transfer Y subtracts each city’s frozen eligible-reference mean. Income and property prices are absent; M0=X, ME=X+E, MW=X+W, MEW=X+E+W.',
            '## 1. Final samples',markdown(samples.drop(columns=['reference_mean_log_price','association_missing_limit_percent','geography_assigned','common_accessibility_support'])),link('sample_flow'),
            'Inside Airbnb operational groups define primary holdouts; accepted municipal masks define membership, not official validation-area certification. Minimum15 outer-test and500 complementary training observations are retained. The researcher changed association eligibility from5% to10% after observing Stockholm missingness; complete cases remain unchanged and no bedrooms/outcomes are filled.',fig('study_areas','Frozen public operational geography and accepted study masks; no individual listings.'),
            '## 2. RQ1 — measurement',markdown(nearest),markdown(opportunities),fig('nearest_access_relationship','Paired nearest-category distances; matched universes, not same-destination circuity.'),fig('opportunity_comparison','Median and interquartile opportunity counts under the frozen nominal10-minute budgets.'),
            'Walking distances and reachability differ from straight-line measurements. Display transformations, suppressed bins and map colour caps do not alter model features. '+link('accessibility_descriptive_statistics')+' and '+link('nearest_access_divergence','metrics')+' retain precise summaries. [Spatial map](../outputs/figures/thesis/accessibility_spatial.pdf) is appendix evidence.',
            '## 3. RQ2 — within-city prediction',markdown(primary.pivot(index=['city','estimator'],columns='model',values='rmse').reindex(columns=MODELS).reset_index(),precision=6),markdown(local,precision=6),fig('primary_model_performance','Pooled primary errors and descriptive fold variation.'),fig('paired_accessibility_contrasts','All five paired contrasts, including network replacement and add-on.'),
            'Accessibility point gains occur in Copenhagen/Stockholm with adverse Oslo changes. The intervals are neighbourhood-composition stability ranges, not independent-sample confidence intervals. '+link('paired_model_contrasts')+' provides every estimator/model comparison; heldout contributions are appendix interpretation, not causality.',
            '## 4. RQ2 complementary OLS associations',link('association_results'),fig('association_accessibility','MEW complete-case adjusted associations with95% HC3 intervals; predictor-specific units.'),
            'All three cities have four prescribed association models,9,999 restricted Webb draws, rank/condition/VIF diagnostics and residual checks. The transparent post-observation10% eligibility threshold permits complete-case inference but does not correct missingness selection or establish a universal standard. Collinear representations and differing predictor units limit coefficient/SHAP rankings; no causal effects are identified.',
            '## 5. RQ3 — geographic generalization',markdown(generalization,precision=6),fig('validation_strategy_comparison','Random, neighbourhood and all six fixed spatial-block configurations.'),link('validation_comparison'),
            '## 6. RQ3 — cross-city consistency',fig('neighbourhood_performance_variation','Paired MW−M0 errors for every primary neighbourhood.'),
            'The geographic sign counts and local scores qualify citywide averages. Different samples/dispersion, uneven folds, overlapping training sets and residual dependence prevent claims of independent cross-design replication. '+link('neighbourhood_performance','metrics')+' preserves all four model/estimator scores and '+link('neighbourhood_support','diagnostics')+' records support.',
            '## 7. RQ4 — cross-city transferability',markdown(transfer.pivot(index=['source_city','target_city','estimator'],columns='model',values='rmse').reindex(columns=MODELS).reset_index(),precision=6),markdown(counts),fig('transfer_performance','All six relative-price source→target directions and four models.'),fig('transfer_network_comparison','Direct network replacement/add-on with existing target-composition ranges.'),fig('directional_transfer_asymmetry','Descriptive reversal differences; source and target tasks change.'),
            'The observed target reference is used only for centring/evaluation. Twenty-four shared source pipelines produce48 estimator/model-direction prediction sets; no target fit/tuning/recalibration occurs. '+link('transfer_contrasts')+' includes all five comparisons. [Binned prediction diagnostics](../outputs/figures/thesis/transfer_prediction_diagnostics.pdf) and [baseline transfer gains](../outputs/figures/thesis/transfer_accessibility_gains.pdf) are appendix evidence, not new fitted models.',
            '## 8. Robustness',link('robustness_registry'),fig('robustness_contrasts','Within-variant paired MW−M0 changes, stability and genuine native-source N/A entries.'),
            'The exhaustive registry accounts for every requested variant. Training-tail restriction, imputation and tuning remain source-training-only. All triggered spatial-error and four-model area fixed-effect checks are complete; density is correctly absorbed. Variant samples/definitions can differ, so the plot is not an absolute-score ranking. [Residual spatial diagnostics](../outputs/figures/thesis/residual_spatial_diagnostics.pdf) remain appendix evidence.',
            '## 9. Main limitations','Original asking prices are not transactions/bookings/revenue. Strong missing-price attrition and complete-case selection constrain representativeness. Operational provider boundaries differ from municipal/native context footprints; population/area vintages, rounded Stockholm denominators and incomplete OSM coverage remain limitations. Displaced coordinates, connectors, components and finite extraction can affect accessibility. Few groups and spatial dependence qualify stability. Three capitals do not represent all Nordic cities. The10% eligibility rule was changed after inspecting missingness. Transfer uses observed target means and cannot certify absolute deployment.',
            '## 10. Claims supported',markdown(claim_rows),
            '[Figure/table recommendations](thesis_figure_recommendations.md), [RQ-by-RQ synthesis](findings_by_research_question.md), [final claims audit](../docs/final_claims_for_thesis.md), [initial gap audit](deliverable_gap_audit.md) and [artifact provenance](thesis_artifact_manifest.json) provide the complete writing/release trail. Markdown is authoritative: no supported active proposal/plan/results DOCX/PDF export pipeline exists. Scientific figures have deterministic PDF/SVG and300-dpi PNG exports.']
    write_once(ROOT/'reports/research_results.md',('\n\n'.join(report)+'\n').encode())
    write_once(ROOT/'reports/numeric_claims_registry.json',(json.dumps(claims,indent=2,ensure_ascii=False)+'\n').encode())
    docs=['docs/final_claims_for_thesis.md','reports/thesis_figure_recommendations.md','reports/thesis_recommendations.json',
          'reports/findings_by_research_question.md','reports/research_results.md','reports/numeric_claims_registry.json']
    provenance={'status':'SYNTHESIS_GENERATED_PENDING_RELEASE_AUDIT','models_refitted':False,'scientific_reconstruction':False,
                'source_catalog_sha256':catalog['source_catalog_sha256'],'generation_command':COMMAND,'input_table_hashes':dependencies,
                'generator_sha256':sha256_file(ROOT/'src/reporting/thesis_synthesis.py'),
                'items':[{'filename':p,'sha256':sha256_file(ROOT/p),'bytes':(ROOT/p).stat().st_size,'generation_command':COMMAND,
                          'research_question':'RQ1–RQ4','publication_status':'THESIS_READY_PENDING_RELEASE_AUDIT',
                          'source_run_artifact':'reports/thesis_artifact_manifest.json; numeric_claims_registry.json',
                          'source_catalog_sha256':catalog['source_catalog_sha256'],'private_row_export':False} for p in docs]}
    write_once(ROOT/'reports/thesis_synthesis_manifest.json',(json.dumps(provenance,indent=2,ensure_ascii=False)+'\n').encode())
    return {'main_figures':len(MAIN_FIGURES),'appendix_figures':8,'main_tables':len(MAIN_TABLES),'numeric_claims':len(claims),'models_refitted':False}


if __name__=='__main__':print(json.dumps(run(),indent=2))
