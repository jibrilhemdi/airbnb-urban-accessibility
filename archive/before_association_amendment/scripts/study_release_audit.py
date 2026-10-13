"""Read-only final source, model, SQL, public-output and branch verification."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import joblib
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,verify_source,write_once
from src.study.specification import load_design,CITIES,neutral_token
from src.study.store import read_package,MIGRATION
from src.study.sample_freeze import records
from src.reporting.study_results import predictions


def run():
    design,_=load_design();sources={};receipts={}
    def walk(value):
        if isinstance(value,dict):
            if isinstance(value.get('local_location'),str) and isinstance(value.get('sha256'),str):
                walk({'path':value['local_location'],'sha256':value['sha256']})
            if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str) and len(value['sha256'])==64:
                path=verify_source(value)
                if str(path) in sources and sources[str(path)]!=value['sha256']:raise ValueError('Conflicting source checksum')
                sources[str(path)]=value['sha256']
                if value.get('receipt_path'):receipts[value['receipt_path']]=value['receipt_sha256']
            for child in value.values():walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
    for path in (ROOT/'config/study').glob('*.json'):walk(json.loads(path.read_text()))
    engine=get_engine();models={};package_count=0;transfer_checks=0;historical_model_hashes=set()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            ledger=dict(conn.execute(text('SELECT migration_name,file_hash_sha256 FROM study.schema_migrations')).all())
            if ledger!={MIGRATION.name:sha256_file(MIGRATION)}:raise ValueError('Applied neutral migration bytes differ')
            rows=conn.execute(text('SELECT run_id,city,family,summary,summary_sha256,dependencies,dependencies_sha256 FROM study.checkpoints ORDER BY run_id')).mappings().all()
            for row in rows:
                neutral_token(row['run_id']);package_count+=1
                if canonical_hash(row['summary'])!=row['summary_sha256'] or canonical_hash(row['dependencies'])!=row['dependencies_sha256']:raise ValueError('SQL package metadata hash differs')
                summary=row['summary']
                for model in summary.get('fitted_models',[]):
                    if sha256_file(ROOT/model['path'])!=model['sha256']:raise ValueError('Saved fold model changed')
                    models[model['path']]=model['sha256']
                if 'fitted_source_model' in summary:
                    model=summary['fitted_source_model']
                    if sha256_file(ROOT/model['path'])!=model['sha256']:raise ValueError('Saved source model changed')
                    models[model['path']]=model['sha256']
            chosen=json.loads((ROOT/'config/study/sample_selection.json').read_text())
            frames={city:pd.DataFrame(records(conn,chosen,city,'sample','prediction_sample')) for city in CITIES}
            _,cities=load_design()
            context_select=json.loads((ROOT/'config/study/context_selection.json').read_text())
            native_policy=json.loads((ROOT/'config/v4/context_A04_20261011.json').read_text())['cities']
            for city in CITIES:
                context,_=read_package(conn,context_select[city]['run_id'],city,'context')
                walk([unit['sources'] for unit in context['density_units']])
                source=cities[city]['historical_listing_selection']
                manifest=conn.scalar(text('SELECT manifest FROM v4_raw.source_manifests WHERE version=:version AND city=:city AND snapshot=:snapshot AND manifest_sha256=:digest'),
                                     {'version':source['source_version'],'city':source['city'],'snapshot':source['snapshot'],'digest':source['manifest_sha256']})
                if canonical_hash(manifest)!=source['manifest_sha256']:raise ValueError('Approved reused source manifest hash differs')
                walk(manifest)
            for old_city in ['copenhagen_frederiksberg','oslo']:
                for entry in native_policy[old_city]['sources']:
                    r=entry['record']
                    if r['filename'] in {'KKBEF1.csv','FOLK1A.csv'} or r['source_id'] in {'a04_20261011_population_data','a04_20261011_population_schema'}:walk(entry)
            schemes=['neighbourhood','random']+[f'blocks_{size}m_origin_{origin}' for size in [1000,1500,2000] for origin in ['0_0','0p5_0p5']]
            for scheme in schemes:
                result=json.loads((ROOT/'config/study'/('results_'+scheme+'.json')).read_text())
                for city in CITIES:
                    summary,_=read_package(conn,result[city]['run_id'],city,'reporting')
                    if canonical_hash(summary)!=result[city]['summary_sha256']:raise ValueError('Verified city results summary differs')
                    expected={(estimator,model) for estimator in ['OLS','XGBoost'] for model in design['models']}
                    actual={(r['estimator'],r['model']) for r in summary['performance']}
                    if actual!=expected or len(summary['performance'])!=8 or any(r['n']!=len(frames[city]) for r in summary['performance']):
                        raise ValueError('Primary/random/grid results lack exact frozen city sample and estimator/model ladder')
            references=json.loads((ROOT/'config/study/reference_selection.json').read_text())
            mean={city:read_package(conn,references[city]['run_id'],city,'reference')[0]['mean_log_price'] for city in CITIES}
            outgoing={}
            for selection in json.loads((ROOT/'runs/transfer/selection.json').read_text()):
                summary,frame=predictions(conn,selection['run_id'],selection['city'],'transfer')
                model=summary['fitted_source_model'];fit=joblib.load(ROOT/model['path'])
                target=frames[selection['target_city']]
                if frame.listing_id.tolist()!=target.listing_id.tolist():raise ValueError('Target prediction/source order differs')
                if not np.allclose(frame.relative_log_price,target.log_price-mean[selection['target_city']],atol=1e-12):raise ValueError('Target frozen benchmark differs')
                actual=fit.predict(target[design['models'][selection['model']]])
                if not np.allclose(actual,frame.prediction,rtol=1e-12,atol=1e-12):raise ValueError('Saved target prediction not reproducible from source pipeline')
                key=(selection['city'],selection['estimator'],selection['model']);outgoing.setdefault(key,set()).add(model['sha256']);transfer_checks+=1
            if transfer_checks!=48 or len(outgoing)!=24 or any(len(v)!=1 for v in outgoing.values()):raise ValueError('Directional/source pipeline cardinality differs')
        inventory=json.loads((ROOT/'docs/analysis/public_output_inventory.json').read_text())
        for row in inventory:
            path=ROOT/row['path']
            if sha256_file(path)!=row['sha256'] or path.stat().st_size!=row['bytes']:raise ValueError('Public generated output changed')
            if any(token in row['path'] for token in ['predictions','models/','data/raw','runs/']):raise ValueError('Private artifact in public inventory')
            if path.suffix=='.csv':
                headers=pd.read_csv(path,nrows=0).columns
                if any(h in headers for h in ['listing_id','latitude','longitude','metric_x','metric_y','record_key']):raise ValueError('Individual location/prediction key in public table')
                if {'cell_x','cell_y'}.issubset(headers):
                    cells=pd.read_csv(path)
                    if cells.n.lt(5).any():raise ValueError('Public map cell support below5')
        def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
        if git('branch','--show-current')!='v4':raise ValueError('Wrong work branch')
        main=git('rev-parse','refs/heads/main');prior=git('rev-parse','refs/heads/v3')
        if main!='7de587997157863e0ba1d36c3f39bdd45f2b9d23' or prior!='6150e3f3b4e6db01dd5bf5842404212343d1344a':raise ValueError('Historical branch moved')
        report={'status':'PASS_WITH_DOCUMENTED_SCIENTIFIC_BLOCKERS','design_id':design['design_id'],'source_files_checksum_verified':len(sources),
                'source_receipts_checksum_verified':len(receipts),'immutable_sql_packages_verified':package_count,'saved_model_files_checksum_verified':len(models),
                'transfer_predictions_reproduced_from_frozen_source_pipelines':transfer_checks,'distinct_shared_source_models':len(outgoing),
                'public_aggregate_artifacts_checksum_verified':len(inventory),'public_row_privacy_and_cell_support':'PASS',
                'neutral_migration_integrity':'PASS','main_sha_unchanged':main,'previous_branch_sha_unchanged':prior,
                'primary_random_six_grid_frozen_sample_cardinality':'PASS',
                'full_rerun_complete':False,'primary_prediction_cities_complete':3,'six_transfer_directions_complete':True,
                'blocker':'Stockholm association union predictor missingness exceeds frozen5% guard; dependent inference blocked',
                'historical_numeric_results_reused_as_final':False}
        write_once(ROOT/'docs/analysis/release_audit.json',(json.dumps(report,indent=2)+'\n').encode())
        return report
    finally:engine.dispose()


if __name__=='__main__':print(json.dumps(run(),indent=2))
