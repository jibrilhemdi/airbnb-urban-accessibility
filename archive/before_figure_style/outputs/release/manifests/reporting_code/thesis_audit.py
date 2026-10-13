"""Initial, immutable RQ deliverable and visual-figure audit before generation."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import shutil
from PIL import Image
from src.ingestion.common import sha256_file
from src.study.sources import write_once
from src.reporting.thesis_sources import ROOT,capture,CATALOG

FIGURES=[
 ('A1','Study area and operational neighbourhoods','Design','study_areas',None,'geography'),
 ('B1','Nearest straight-line versus network relationship','RQ1','nearest_access_relationship',None,'sample'),
 ('B2','Nearest-category distance divergence','RQ1','nearest_access_divergence',None,'interpretation'),
 ('B3','Food/social and culture/tourism opportunities','RQ1','opportunity_comparison','opportunity_comparison.png','sample'),
 ('B4','Compact accessibility spatial panels','RQ1','accessibility_spatial','accessibility_cells_publication.png','sample'),
 ('C1','Main pooled RMSE and heldout fold variation','RQ2','primary_model_performance','within_city_performance.png','neighbourhood'),
 ('C2/C3','All five paired accessibility contrasts','RQ2','paired_accessibility_contrasts','accessibility_gains.png','neighbourhood'),
 ('C4','Adjusted OLS accessibility associations with HC3 intervals','RQ2','association_accessibility','association_accessibility_coefficients.png','association'),
 ('C5','Existing heldout predictive contributions','RQ2','heldout_feature_contributions','heldout_contributions_publication.png','interpretation'),
 ('D1','Random/neighbourhood/geometric validation comparison','RQ3','validation_strategy_comparison','validation_comparison.png','validation'),
 ('D2','Heldout neighbourhood heterogeneity','RQ3','neighbourhood_performance_variation',None,'within_city'),
 ('D3','Registered robustness effect and stability summaries','RQ3','robustness_contrasts',None,'robustness'),
 ('E1','Six-direction transfer performance matrices','RQ4','transfer_performance','xgboost_transfer_matrix_publication.png','transfer'),
 ('E2','Transfer accessibility gains relative to baseline','RQ4','transfer_accessibility_gains','xgboost_transfer_gains_publication.png','transfer'),
 ('E3','Direct network-versus-Euclidean transfer contrasts','RQ4','transfer_network_comparison','ols_transfer_gains_publication.png','transfer'),
 ('E4','Observed versus predicted relative-price diagnostics','RQ4','transfer_prediction_diagnostics',None,'transfer'),
 ('E5','Direction reversal asymmetry','RQ4','directional_transfer_asymmetry',None,'transfer'),
 ('F','Prescribed residual spatial diagnostics','Appendix','residual_spatial_diagnostics',None,'spatial')]
TABLES=[('T1','City/sample summary','Design','city_sample_summary','sample_flow.csv','sample'),
 ('T2','Complete X/E/W feature definitions','Design','feature_definitions',None,'design'),
 ('T3','Accessibility descriptive statistics','RQ1','accessibility_descriptive_statistics',None,'interpretation'),
 ('T4','Primary predictive performance','RQ2','primary_predictive_performance','within_city_performance.csv','neighbourhood'),
 ('T5','All five paired model contrasts and stability','RQ2','paired_model_contrasts',None,'neighbourhood'),
 ('T6','Final three-city OLS association results','RQ2','association_results','association_coefficients.csv','association'),
 ('T7','Validation-strategy comparisons','RQ3','validation_comparison','validation_comparison.csv','validation'),
 ('T8','All six transfer directions and four models','RQ4','transfer_performance','transfer_performance.csv','transfer'),
 ('T9','All transfer model contrasts and stability','RQ4','transfer_contrasts','transfer_accessibility_contrasts.csv','transfer'),
 ('T10','Every registered robustness status, estimand and result','RQ3','robustness_registry','robustness_registry.csv','robustness'),
 ('T11','RQ claims and limitations','All','claims_and_limitations',None,'synthesis')]


def run():
    catalog=capture();rows=[];figure_reviews=[]
    paths=sorted((ROOT/'outputs/figures').rglob('*.png'))
    original_superseded={'accessibility_cells.png','heldout_contributions.png','ols_transfer_matrix.png','xgboost_transfer_matrix.png','ols_transfer_gains.png','xgboost_transfer_gains.png'}
    for p in paths:
        final=p.parent.name=='research';duplicate=final and p.name in original_superseded
        with Image.open(p) as img:size=list(img.size);dpi=list(img.info.get('dpi',(0,0)))
        decision='REDESIGN' if final and not duplicate else 'DROP'
        reason=('Final numeric lineage, but 100/140-dpi PNG only; native labels/long panels need readable page-width vector redesign' if decision=='REDESIGN'
                else 'Superseded initial layout; original remains immutable' if duplicate else 'Historical single-city geography/results; not the final three-city no-income design')
        figure_reviews.append({'path':str(p.relative_to(ROOT)),'sha256':sha256_file(p),'pixels':size,'dpi':dpi,
                               'decision':decision,'reason':reason,'visually_inspected':True,
                               'visual_review_method':'Nine original-resolution six-panel contact sheets; every one of49 source figures reviewed',
                               'scientific_lineage':'FINAL_RERUN' if final else 'HISTORICAL_NOT_FOR_FINAL_RESULTS',
                               'historical_source_preserved':True,'publication_ready':False,
                               'issues':['insufficient raster publication resolution','no vector export','page-width typography'] if decision=='REDESIGN' else [reason]})
    for identifier,evidence,rq,name,old,role in FIGURES:
        existing=[] if old is None else ['outputs/figures/research/'+old]
        rows.append({'id':identifier,'research_question':rq,'required_evidence':evidence,'kind':'figure',
                     'existing_output':existing,'existing_filename':old,'source_artifact_or_run':role,
                     'source_registry':'reports/frozen_reporting_sources.json',
                     'status':'EXISTS_NEEDS_REDESIGN' if existing else 'MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS',
                     'thesis_usefulness':evidence,'publication_readiness':'Pending common style, vector/300-dpi output and provenance validation',
                     'missing_output':'outputs/figures/thesis/'+name+'.pdf',
                     'action_required':'Generate one compact figure from verified frozen SQL; PNG/PDF/SVG; retain all original outputs'})
    rows.append({'id':'A2','research_question':'Design','required_evidence':'Every sample-flow stage by city','kind':'table',
                 'existing_output':['outputs/tables/research/sample_flow.csv'],'existing_filename':'sample_flow.csv',
                 'source_artifact_or_run':'sample','source_registry':'reports/frozen_reporting_sources.json',
                 'status':'READY_EXISTING','thesis_usefulness':'A compact sample-flow table is clearer than a redundant flow graphic',
                 'publication_readiness':'Numeric evidence ready; format into T1 plus appendix flow table','missing_output':None,
                 'action_required':'Table-only treatment; preserve all stages without a separate sample-flow figure'})
    for identifier,evidence,rq,name,old,role in TABLES:
        existing=[] if old is None else ['outputs/tables/research/'+old]
        if identifier=='T5':existing=['outputs/metrics/neighbourhood/paired_contrasts.csv']
        if identifier=='T3':existing=['outputs/tables/research/measurement_comparison.json']
        if identifier=='T2':existing=['docs/analysis/data_dictionary.md','config/study/design.json']
        rows.append({'id':identifier,'research_question':rq,'required_evidence':evidence,'kind':'table','existing_output':existing,
                     'existing_filename':old,'source_artifact_or_run':role,'source_registry':'reports/frozen_reporting_sources.json',
                     'status':'EXISTS_NEEDS_REDESIGN' if existing else 'MISSING_CAN_GENERATE_FROM_FROZEN_RESULTS',
                     'thesis_usefulness':evidence,'publication_readiness':'Need publication formatting and exact final-source references',
                     'missing_output':'outputs/tables/thesis/'+name+'.md','action_required':'Generate full CSV plus readable Markdown summary from the pinned results'})
    for name,reason in [('Same-destination route circuity','Nearest Euclidean and nearest walking destinations can differ; no frozen same-object route-pair output exists'),
                        ('New fitted SHAP models','Existing heldout SHAP summaries are available; no new model fitting is needed'),
                        ('Active DOCX/PDF document exports','Only a historical income-addendum DOCX updater exists; no supported active Markdown document-export pipeline')]:
        rows.append({'id':name,'research_question':'All','kind':'scope','required_evidence':reason,'existing_output':[],
                     'source_artifact_or_run':None,'status':'NOT_NEEDED','thesis_usefulness':reason,
                     'publication_readiness':'Markdown authoritative; scientific figure PDF/SVG exports are supported',
                     'missing_output':None,'action_required':'Document limitation; do not invent unsupported science or a document renderer'})
    counts={}
    for name in ['outputs/figures','outputs/tables','outputs/metrics','outputs/diagnostics','outputs/models','reports','runs','outputs/release']:
        p=ROOT/name;files=[f for f in p.rglob('*') if f.is_file() and f.name not in {'.DS_Store','.gitkeep'}] if p.exists() else []
        counts[name]={'files':len(files),'formats':dict(Counter(f.suffix for f in files))}
    audit={'status':'INITIAL_DELIVERABLE_GAPS_IDENTIFIED','base_checkpoint':'f782bef3aad7c11359cc9af2b4e03c6414bf772b',
           'scientific_model_execution':'COMPLETE','thesis_reporting_layer':'INCOMPLETE_PENDING_GENERATION_AND_RELEASE_AUDIT',
           'frozen_source_catalog_sha256':catalog['source_catalog_sha256'],'deliverables':rows,'figure_reviews':figure_reviews,
           'figure_review_counts':dict(Counter(r['decision'] for r in figure_reviews)),'existing_directory_inventory':counts,
           'scientific_reconstruction_required':False,'models_refitted':False,'source_acquisition_required':False,
           'recommendation':'Approximately10 main figures and8 main tables; remaining useful outputs in appendices'}
    write_once(ROOT/'reports/deliverable_gap_audit.json',(json.dumps(audit,indent=2,ensure_ascii=False)+'\n').encode())
    body=['# Initial thesis deliverable-gap audit','Copenhagen includes Frederiksberg. This audit precedes generation; model completion does not establish thesis-reporting completeness.',
          'Every one of49 existing figures was inspected visually and checked for dimensions, DPI and lineage. Thirty are historical; six are superseded layouts;13 final figures need page-width typography and300-dpi/vector redesign. None is deleted or overwritten.',
          '| ID | RQ | Required evidence | Status | Existing output | Action |','| --- | --- | --- | --- | --- | --- |']
    body.extend('| '+' | '.join([r['id'],r['research_question'],r['required_evidence'],r['status'],', '.join(r['existing_output']) or 'None',r['action_required']])+' |' for r in rows)
    body+=['\n## Reconstruction boundary','No scientific reconstruction is needed: public provider geometries, common samples, saved predictions, full model contrasts, coefficients, robustness and heldout contributions already exist in the pinned final SQL packages. Missing plots require safe reporting aggregation only. No tuning, fitting, source acquisition, network rebuild, source definition or outcome changes are authorized.',
           '\n## Publication and export limits','Preserve earlier results; create functional thesis paths. Use minimum-five aggregate spatial cells/bins, no row exports, shared styles and vector/300-dpi outputs. The historical DOCX income updater is not an active proposal/plan/results renderer. Markdown remains authoritative; no unreliable document pipeline is invented.',
           '\n## Final-source evidence','[Frozen reporting catalog](frozen_reporting_sources.json) records all current selectors and751 immutable package identities. [Machine audit](deliverable_gap_audit.json) records all49 figure classifications and the exact initial gaps. The completion audit will be a separate file, retaining this initial evidence.']
    write_once(ROOT/'reports/deliverable_gap_audit.md',('\n\n'.join(body)+'\n').encode())
    return audit


if __name__=='__main__':print(json.dumps({k:v for k,v in run().items() if k not in {'deliverables','figure_reviews'}},indent=2))
