"""One semantic dependency runner for a fail-closed, provenance-tracked V3 rebuild."""
from __future__ import annotations
import argparse
import importlib
import json
import subprocess
import sys
from datetime import datetime,timezone
from sqlalchemy import text
from src.db.connection import get_engine,database_settings
from src.db.migrations import migrate,database_check,version3_schema_check
from src.ingestion.common import PROJECT_ROOT,write_json
from src.pipeline.protocol import verify_inputs,verify_income_evidence,freeze_run_dependencies,verify_run_dependencies
from src.pipeline.audit_reproducibility import archive_check,naming_check,software_versions
from src.pipeline.build_tuning_candidates import build as build_candidates

DEPENDENCIES=[
 ('airbnb_sample','build_airbnb_sample','main'),
 ('context_sources','ingest_area_context','main'),
 ('analysis_areas_and_centrality','build_spatial_features','main'),
 ('core_area_context','build_area_context','build'),
 ('frozen_osm_inputs','acquire_osm','acquire'),
 ('rail_and_opportunity_taxonomy_and_euclidean','build_euclidean_accessibility','main'),
 ('bus_taxonomy_deduplication_and_euclidean','build_bus_euclidean_accessibility','run'),
 ('walking_graph_and_rail_opportunities','build_walking_accessibility','main'),
 ('core_bus_walking','build_bus_walking_accessibility','run'),
 ('walking_exports','export_walking_accessibility','export'),
 ('accessibility_quality','qa_accessibility','run'),
 ('matched_destination_boundary','audit_destination_boundary','run'),
 ('price_observability','audit_price_observability','run'),
 ('frozen_analysis_dataset_and_dictionary','build_analysis_dataset','build'),
 ('outer_and_inner_validation_splits','build_validation_splits','build'),
 ('primary_ols_xgboost_oof_uncertainty_and_heldout_shap','run_primary_models','run'),
 ('mandatory_no_income_robustness','run_income_robustness','run'),
 ('spatial_diagnostics','run_spatial_diagnostics','run'),
 ('threshold_speed_and_decay_features','build_opportunity_variants','build'),
 ('accessibility_sample_covariate_and_spatial_robustness','run_robustness_analyses','run'),
 ('conditional_spatial_error_robustness','run_spatial_error_robustness','run'),
 ('publication_tables_figures_and_report','build_final_outputs','run'),
 ('claims_audit','export_claims_audit','run'),
 ('latex_and_presentation','prepare_final_outputs','run'),
 ('reproducibility_audit','audit_reproducibility','audit_run')]

ENGINE_ONLY={'core_area_context','accessibility_quality','matched_destination_boundary','price_observability','frozen_analysis_dataset_and_dictionary','outer_and_inner_validation_splits','threshold_speed_and_decay_features'}
RUN_COMPONENTS={'primary_ols_xgboost_oof_uncertainty_and_heldout_shap','mandatory_no_income_robustness','spatial_diagnostics','accessibility_sample_covariate_and_spatial_robustness','conditional_spatial_error_robustness','publication_tables_figures_and_report','claims_audit','reproducibility_audit'}

def preflight(check_database=True):
    checks={};failures=[]
    def check(name,function):
        try:checks[name]={'status':'passed','details':function()}
        except Exception as error:checks[name]={'status':'failed','reason':str(error)};failures.append(name)
    check('immutable_inputs',lambda:{'verified_files':len(verify_inputs()['files'])})
    check('legacy_archive',archive_check);check('semantic_names',naming_check)
    check('fixed_candidates',lambda:{'candidates':len(build_candidates()['candidates'])})
    check('income_harmonisation',verify_income_evidence)
    if check_database:
        def db():
            engine=get_engine()
            try:
                from src.pipeline.qualified_income import verify_sql
                with engine.connect() as conn:income=verify_sql(conn)
                return {**database_check(engine,database_settings()['DB_NAME']),**version3_schema_check(engine),**income}
            finally:engine.dispose()
        check('database',db)
    for _,module,_ in DEPENDENCIES:check('import/'+module,lambda module=module:importlib.import_module('src.pipeline.'+module).__name__)
    result={'version':'preflight_v3','status':'passed' if not failures else 'blocked','checks':checks,'blocking_checks':failures,
        'dependency_order':[name for name,_,_ in DEPENDENCIES],'scope':'pre-execution validation; no scientific results generated'}
    write_json(PROJECT_ROOT/'outputs/tables/reproducibility/preflight.json',result);return result

def resume_metadata(previous,current):
    """Narrow documented operational recoveries; never bypass scientific failures."""
    repairs={
        'Object of type date is not JSON serializable':
            ({'src/pipeline/run_pipeline.py'},'walking_exports','Normalise component metadata to JSON-safe values'),
        'Expected more than k projected two-dimensional points':
            ({'src/pipeline/run_pipeline.py','src/pipeline/run_spatial_diagnostics.py'},'mandatory_no_income_robustness',
             'Normalise equivalent date/timestamp join keys and require complete spatial diagnostic coverage')}
    if previous.get('status')!='failed' or previous.get('error') not in repairs:
        raise RuntimeError('Only documented operational failures are eligible for recovery')
    allowed,last_completed,repair=repairs[previous['error']]
    old=previous['dependencies']
    if old['input_manifest_sha256']!=current['input_manifest_sha256'] or old['design_sha256']!=current['design_sha256']:
        raise RuntimeError('Recovery cannot change raw inputs or scientific design')
    before=old['source_sha256'];after=current['source_sha256']
    changed={p for p in set(before)|set(after) if before.get(p)!=after.get(p)}
    if changed!=allowed:
        raise RuntimeError('Recovery permits only the documented repair files: '+str(sorted(changed)))
    completed=set(previous['component_results']);names=[name for name,_,_ in DEPENDENCIES]
    if not completed or completed!=set(names[:len(completed)]) or names[len(completed)-1]!=last_completed:
        raise RuntimeError('Recovery requires exactly the completed prefix through '+last_completed)
    result=json.loads(json.dumps(previous));result['initial_dependencies']=result.get('initial_dependencies',old)
    result.setdefault('recovery_events',[]).append({'time_utc':datetime.now(timezone.utc).isoformat(),
        'reason':previous['error'],'change':repair+'; resume completed prefix without rebuilding data',
        'previous_dependencies':old,'replacement_dependencies':current,'completed_components':names[:len(completed)]})
    result['dependencies']=current;result['status']='running';result.pop('error',None)
    return result

def verify_spatial_recovery(conn,run_id):
    """Prove that the failure was a date representation join, with complete models."""
    from src.pipeline.build_analysis_dataset import load_dataset
    from src.pipeline.storage import load_artifact
    from src.pipeline.run_spatial_diagnostics import residual_coordinates
    from src.pipeline.run_income_robustness import audit
    frame=load_dataset(conn);oof=load_artifact(conn,run_id,'primary_models','oof_predictions')
    evidence=audit(conn,run_id,len(frame))
    streams=0
    for model in ['OLS','XGBoost']:
        for fs in ['M0','MW']:
            part=oof.loc[(oof.scheme=='geographic_11')&(oof.model==model)&(oof.feature_set==fs)]
            old=part.merge(frame[['snapshot_date','listing_id']],on=['snapshot_date','listing_id'])
            if len(old)!=0 or len(frame)<=8:
                raise RuntimeError('Spatial recovery is restricted to the proved empty date-representation join')
            corrected=residual_coordinates(part,frame)
            if len(corrected)!=len(frame):raise RuntimeError('Spatial recovery observations are incomplete')
            streams+=1
    return {**evidence,'spatial_streams_verified':streams,'spatial_rows_per_stream':len(frame),
        'original_join_rows':0,'scientific_design_changed':False}

def run(resume_run_id=None):
    result=preflight()
    if result['blocking_checks']:raise RuntimeError('Full rerun blocked by preflight: '+', '.join(result['blocking_checks']))
    # Required compile and normal unit suite before any expensive execution.
    log=PROJECT_ROOT/'outputs/tables/reproducibility';log.mkdir(parents=True,exist_ok=True)
    for label,command in [('compile',[sys.executable,'-m','compileall','src']),('tests',[sys.executable,'-m','unittest','discover','-s','tests','-v'])]:
        completed=subprocess.run(command,cwd=PROJECT_ROOT,text=True,capture_output=True)
        (log/(label+'.txt')).write_text(completed.stdout+completed.stderr)
        if completed.returncode:raise RuntimeError('Required '+label+' check failed; see '+str(log))
    dependencies=freeze_run_dependencies();engine=get_engine();run_id=resume_run_id or 'research_v3_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    metadata={'version':'research_run_v3','run_id':run_id,'dependencies':dependencies,'software':software_versions(),'commands':[[sys.executable,'-m','src.pipeline.run_pipeline','--run']],
        'component_results':{},'crs_epsg':25832,'protocol_deviations':[]}
    run_registered=False
    try:
        migrate(engine)
        with engine.begin() as conn:
            if resume_run_id:
                prior=conn.execute(text('SELECT status,metadata FROM v3_analysis.runs WHERE run_id=:run FOR UPDATE'),{'run':run_id}).mappings().one()
                if prior['status']!='failed':raise RuntimeError('Recovery requires a failed SQL run')
                metadata=resume_metadata(prior['metadata'],dependencies)
                if prior['metadata']['error']=='Expected more than k projected two-dimensional points':
                    metadata['recovery_events'][-1]['verification']=verify_spatial_recovery(conn,run_id)
                metadata['commands'].append([sys.executable,'-m','src.pipeline.run_pipeline','--resume',run_id])
                conn.execute(text("UPDATE v3_analysis.runs SET status='running',finished_at=NULL,metadata=CAST(:metadata AS jsonb) WHERE run_id=:run"),{'run':run_id,'metadata':json.dumps(metadata)})
            else:
                if conn.scalar(text('SELECT count(*) FROM v3_clean.airbnb_listings')):raise RuntimeError('V3 namespace is nonempty; explicitly version/resume instead of overwriting a frozen run')
                conn.execute(text('INSERT INTO v3_analysis.runs(run_id,status,metadata) VALUES(:run,:status,CAST(:metadata AS jsonb))'),{'run':run_id,'status':'running','metadata':json.dumps(metadata)})
        run_registered=True
        for name,module,function in DEPENDENCIES:
            if name in metadata['component_results']:continue
            verify_inputs();verify_run_dependencies(dependencies)
            print('Running '+name,flush=True)
            callable=getattr(importlib.import_module('src.pipeline.'+module),function)
            if name in RUN_COMPONENTS:answer=callable(engine,run_id)
            elif name in ENGINE_ONLY:answer=callable(engine)
            elif module=='build_airbnb_sample':answer=callable([])
            else:answer=callable()
            # SQL metadata already used this normalisation; use the same types in the file export.
            answer=json.loads(json.dumps(answer,default=str,allow_nan=False))
            metadata['component_results'][name]=answer
            if name=='frozen_analysis_dataset_and_dictionary':metadata['dataset_sha256']=answer['dataset_sha256']
            with engine.begin() as conn:conn.execute(text('UPDATE v3_analysis.runs SET metadata=CAST(:metadata AS jsonb) WHERE run_id=:run'),{'run':run_id,'metadata':json.dumps(metadata,default=str)})
            write_json(log/'run_metadata.json',metadata)
        metadata['status']='complete'
        with engine.begin() as conn:conn.execute(text("UPDATE v3_analysis.runs SET status='complete',finished_at=now(),metadata=CAST(:metadata AS jsonb) WHERE run_id=:run"),{'run':run_id,'metadata':json.dumps(metadata,default=str)})
        write_json(log/'run_metadata.json',metadata);return metadata
    except Exception as error:
        # A rejected recovery/fresh-run guard must not overwrite existing run metadata.
        if not run_registered:raise
        metadata['status']='failed';metadata['error']=str(error)
        with engine.begin() as conn:conn.execute(text("UPDATE v3_analysis.runs SET status='failed',finished_at=now(),metadata=CAST(:metadata AS jsonb) WHERE run_id=:run"),{'run':run_id,'metadata':json.dumps(metadata,default=str)})
        write_json(log/'run_metadata.json',metadata);raise
    finally:engine.dispose()

def main():
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--preflight',action='store_true');group.add_argument('--run',action='store_true');group.add_argument('--resume',metavar='RUN_ID');group.add_argument('--smoke',action='store_true');parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    if args.smoke:
        from src.pipeline.smoke_checks import run as smoke
        print(json.dumps(smoke(),indent=2));return
    if args.preflight:
        answer=preflight(not args.offline);print(json.dumps({'status':answer['status'],'blocking_checks':answer['blocking_checks']},indent=2));raise SystemExit(0 if answer['status']=='passed' else 2)
    if args.offline:raise SystemExit('A full run requires PostgreSQL/PostGIS')
    answer=run(args.resume);print(json.dumps({'run_id':answer['run_id'],'status':answer['status']},indent=2))
if __name__=='__main__':main()
