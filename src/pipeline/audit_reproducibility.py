"""Repository integrity and complete current-run reproducibility checks."""
from __future__ import annotations
import argparse
import ast
import json
import platform
import re
from importlib import metadata
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT,sha256_file,write_json
from src.pipeline.protocol import verify_inputs,freeze_run_dependencies,verify_run_dependencies
from src.pipeline.build_tuning_candidates import load_candidates
from src.pipeline.storage import load_artifact,persist
from src.pipeline.build_analysis_dataset import load_dataset,dataset_hash
HISTORICAL=re.compile(r'(?i)(ph'+r'ase(?:\d*)|post'+r'completion|pre_'+r'freeze|pre-'+r'freeze)')
def archive_check():
    root=PROJECT_ROOT/'archive/legacy_v2'
    manifest=json.loads((root/'archive_checksums.json').read_text())
    extra=json.loads((root/'supplementary_archive_checksums.json').read_text())
    manifest={**manifest,**extra}
    changed=[name for name,digest in manifest.items() if not (root/name).is_file() or sha256_file(root/name)!=digest]
    if changed:raise RuntimeError(f'Legacy archive bytes changed: {changed}')
    return {'archived_files_verified':len(manifest),'archive_manifest_sha256':sha256_file(root/'archive_checksums.json')}
def naming_check():
    errors=[]
    for base in ['src','tests']:
        for path in sorted((PROJECT_ROOT/base).rglob('*.py')):
            if HISTORICAL.search(path.name) or HISTORICAL.search(path.read_text()):errors.append(path.relative_to(PROJECT_ROOT).as_posix())
            ast.parse(path.read_text(),filename=str(path))
    for base in ['outputs/tables','outputs/figures']:
        for path in (PROJECT_ROOT/base).rglob('*'):
            if HISTORICAL.search(path.relative_to(PROJECT_ROOT/base).as_posix()):errors.append(path.relative_to(PROJECT_ROOT).as_posix())
    for filename in ['Makefile','README.md','requirements.txt','config/osmconf.ini',
                     'config/project.yml','config/research_design.json','config/xgboost_candidates.json']:
        if HISTORICAL.search((PROJECT_ROOT/filename).read_text()):errors.append(filename)
    if errors:raise RuntimeError(f'Unexpected historical terminology in active files: {errors}')
    return {'active_naming_check':'passed'}
def software_versions():
    versions={}
    for distribution in metadata.distributions():
        name=distribution.metadata.get('Name')
        if name:versions[name]=distribution.version
    return {'python':platform.python_version(),'platform':platform.platform(),'packages':dict(sorted(versions.items()))}
def repository_audit():
    return {**archive_check(),**naming_check(),'frozen_inputs':verify_inputs(),'dependencies':freeze_run_dependencies(),'software':software_versions(),
        'scope':'repository and immutable inputs only; does not certify an analytical rerun'}
def audit_run(engine,run_id):
    result=repository_audit()
    with engine.connect() as conn:
        expected=conn.scalar(text('SELECT metadata FROM v3_analysis.runs WHERE run_id=:run'),{'run':run_id})
        verify_run_dependencies(expected['dependencies'])
        frame=load_dataset(conn);oof=load_artifact(conn,run_id,'primary_models','oof_predictions')
        candidate=load_candidates();n=len(frame)
        if expected['dataset_sha256']!=dataset_hash(frame):raise RuntimeError('Dataset freeze mismatch')
        from src.pipeline.run_income_robustness import audit as audit_income
        income_audit=audit_income(conn,run_id,n)
        if len(oof)!=n*18:raise RuntimeError('Primary OOF coverage incomplete')
        keys=['snapshot_date','listing_id','scheme','model','feature_set']
        if oof[keys].duplicated().any():raise RuntimeError('Duplicate primary OOF predictions')
        for (scheme,model,fs),part in oof.groupby(['scheme','model','feature_set']):
            if len(part)!=n or part.outer_fold.nunique()!=(5 if scheme=='random_5' else 11):raise RuntimeError('Outer holdout coverage changed')
        if not np.allclose(oof.residual,oof.log_price-oof.prediction) or not np.allclose(oof.squared_error,oof.residual**2) or not np.allclose(oof.absolute_error,oof.residual.abs()):raise RuntimeError('Saved OOF loss mismatch')
        tuning=load_artifact(conn,run_id,'primary_models','xgboost_tuning')
        budgets=tuning.groupby(['scheme','outer_fold','feature_set']).size()
        if len(budgets)!=64 or not budgets.eq(30).all():raise RuntimeError('Unequal or incomplete tuning budget')
        selected=tuning.loc[tuning.selected]
        if len(selected)!=64:raise RuntimeError('Selected parameter records incomplete')
        shap=load_artifact(conn,run_id,'primary_models','heldout_shap')
        if len(shap)!=n*8:raise RuntimeError('Held-out SHAP incomplete')
        recon=np.array([r.base_value+sum(r.shap.values()) for _,r in shap.iterrows()])
        if not np.allclose(recon,shap.prediction,atol=1e-4):raise RuntimeError('Saved SHAP reconstruction failed')
        ols=load_artifact(conn,run_id,'primary_models','ols_coefficients')
        if ols.empty or not ols.wild_replications.eq(9999).all() or not ols.clusters.eq(11).all():raise RuntimeError('Area-aware inference incomplete')
        bootstrap=load_artifact(conn,run_id,'primary_models','area_bootstrap')
        if not bootstrap.groupby(['model','added','reference']).size().eq(2000).all() or len(bootstrap)!=16000:raise RuntimeError('Paired area bootstrap incomplete')
        artifact_names=set(conn.execute(text('SELECT DISTINCT artifact FROM v3_analysis.artifacts WHERE run_id=:run'),{'run':run_id}).scalars())
        for required in ['ols_coefficients','spatial_moran','model_performance','incremental_performance','spatial_error_metadata','registry']:
            if required not in artifact_names:raise RuntimeError('Required artifact missing: '+required)
        from src.pipeline.build_validation_splits import assignment_hashes
        current_hashes=assignment_hashes(conn)
        split_freeze=expected['component_results']['outer_and_inner_validation_splits']
        for key,value in current_hashes.items():
            if split_freeze[key]!=value:raise RuntimeError('Saved validation assignment hash mismatch: '+key)
        split_n=conn.scalar(text('SELECT count(*) FROM v3_analysis.outer_assignments'))
        inner_n=conn.scalar(text('SELECT count(*) FROM v3_analysis.inner_assignments'))
    outputs={p.relative_to(PROJECT_ROOT).as_posix():sha256_file(p) for base in ['outputs','reports'] for p in sorted((PROJECT_ROOT/base).rglob('*'))
        if p.is_file() and p.name!='.gitkeep' and p.name!='run_metadata.json' and p.name!='reproducibility_audit.json'}
    result.update(**income_audit,run_id=run_id,status='passed',scope='complete analytical run',analytical_n=n,dataset_sha256=dataset_hash(frame),
        candidate_sha256=candidate['candidates_sha256'],outer_assignment_rows=split_n,inner_assignment_rows=inner_n,output_sha256=outputs)
    with engine.begin() as conn:persist(conn,run_id,'reproducibility','audit',[result])
    write_json(PROJECT_ROOT/'outputs/tables/reproducibility/reproducibility_audit.json',result);return result
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repository-only',action='store_true');args=parser.parse_args()
    if not args.repository_only:raise SystemExit('Complete-run audit is invoked by run_pipeline')
    result=repository_audit();write_json(PROJECT_ROOT/'outputs/tables/reproducibility/repository_audit.json',result)
    print(json.dumps({k:result[k] for k in ['scope','archived_files_verified','active_naming_check']},indent=2))
