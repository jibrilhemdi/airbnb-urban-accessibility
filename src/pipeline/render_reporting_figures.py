"""Rerender reporting without changing the frozen empirical run or its audit.

The original certificate remains in archive/reporting_refresh/.../before.
A distinct certificate verifies scientific dependencies and presentation output.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from sqlalchemy import text
from src.db.connection import get_engine
from src.ingestion.common import PROJECT_ROOT, sha256_file, write_json
from src.pipeline.protocol import freeze_run_dependencies, verify_inputs
from src.pipeline.build_analysis_dataset import load_dataset, dataset_hash
from src.pipeline.build_validation_splits import assignment_hashes
from src.pipeline import build_final_outputs, prepare_final_outputs

REPORTING_FILES={'src/pipeline/build_final_outputs.py','src/pipeline/prepare_final_outputs.py',
 'src/pipeline/reporting_figures.py','src/pipeline/render_reporting_figures.py'}

def scientific_dependency_guard(expected,actual):
    for name in ('input_manifest_sha256','design_sha256'):
        if expected[name]!=actual[name]:raise RuntimeError('Scientific freeze changed: '+name)
    before={k:v for k,v in expected['source_sha256'].items() if k not in REPORTING_FILES}
    after={k:v for k,v in actual['source_sha256'].items() if k not in REPORTING_FILES}
    if before!=after:raise RuntimeError('Non-reporting code, SQL, configuration or design documents changed')
    return sorted(k for k in REPORTING_FILES if expected['source_sha256'].get(k)!=actual['source_sha256'].get(k))

def artifact_fingerprints(conn,run_id):
    return {f'{r[0]}/{r[1]}':{'n':r[2],'ordered_record_md5':r[3]} for r in conn.execute(text(
        "SELECT family,artifact,count(*),md5(string_agg(md5(record::text),'' ORDER BY record_key::integer)) "
        "FROM v3_analysis.artifacts WHERE run_id=:run GROUP BY family,artifact ORDER BY family,artifact"),{'run':run_id})}

def run(run_id=None):
    engine=get_engine()
    with engine.connect() as conn:
        if run_id is None:run_id=conn.execute(text("SELECT run_id FROM v3_analysis.runs WHERE status='complete' ORDER BY started_at DESC LIMIT 1")).scalar_one()
        status,metadata=conn.execute(text('SELECT status,metadata FROM v3_analysis.runs WHERE run_id=:run'),{'run':run_id}).one()
        if status!='complete':raise RuntimeError('Reporting refresh requires a completed empirical run')
        verify_inputs();dependencies=freeze_run_dependencies()
        changes=scientific_dependency_guard(metadata['dependencies'],dependencies)
        original_hash=metadata['dataset_sha256'];actual_hash=dataset_hash(load_dataset(conn))
        if actual_hash!=original_hash:raise RuntimeError('Frozen analytical dataset changed')
        splits=assignment_hashes(conn);expected=metadata['component_results']['outer_and_inner_validation_splits']
        if any(splits[k]!=expected[k] for k in splits):raise RuntimeError('Frozen validation assignments changed')
        before=artifact_fingerprints(conn,run_id)
    archive=PROJECT_ROOT/f'archive/reporting_refresh/{run_id}/before'
    if not (archive/'checksums.json').exists():raise RuntimeError('Preserve the original reporting and audit before refreshing')
    preserved=json.loads((archive/'checksums.json').read_text())
    if any(sha256_file(archive/name)!=digest for name,digest in preserved.items()):raise RuntimeError('Original reporting archive changed')
    result=build_final_outputs.run(engine,run_id);prepare_final_outputs.run()
    with engine.connect() as conn:
        after=artifact_fingerprints(conn,run_id)
        if before!=after:raise RuntimeError('Analytical artifacts changed during reporting refresh')
        if dataset_hash(load_dataset(conn))!=original_hash:raise RuntimeError('Dataset changed during refresh')
        if assignment_hashes(conn)!=splits:raise RuntimeError('Validation assignments changed during refresh')
    if freeze_run_dependencies()!=dependencies:raise RuntimeError('Dependencies changed during rendering')
    manifest=json.loads((PROJECT_ROOT/'outputs/tables/reporting/figure_manifest.json').read_text())
    files=[PROJECT_ROOT/p for r in manifest['figures'] for p in r['paths']]
    files.extend([PROJECT_ROOT/'reports/reporting_figures_v3.html',PROJECT_ROOT/'reports/research_results_v3.html',PROJECT_ROOT/'reports/research_results_v3.md',PROJECT_ROOT/'outputs/tables/reporting/figure_manifest.json',PROJECT_ROOT/'outputs/tables/reporting/output_manifest.json'])
    certificate={'run_id':run_id,'status':'passed','scope':'Reporting-only refresh; original empirical audit is preserved and not replaced',
        'created_utc':datetime.now(timezone.utc).isoformat(),'original_certificate':str((archive/'outputs/tables/reproducibility/reproducibility_audit.json').relative_to(PROJECT_ROOT)),
        'original_certificate_sha256':sha256_file(archive/'outputs/tables/reproducibility/reproducibility_audit.json'),
        'dataset_sha256':original_hash,'validation_assignments':splits,'analytical_artifacts_unchanged':before==after,
        'analytical_artifact_fingerprints':after,'scientific_dependencies_verified':True,'allowed_reporting_changes':changes,
        'reporting_source_sha256':{k:dependencies['source_sha256'][k] for k in sorted(REPORTING_FILES)},
        'figure_count':len(manifest['figures']),'planned_categories':len(manifest['coverage']),
        'output_sha256':{str(p.relative_to(PROJECT_ROOT)):sha256_file(p) for p in files}}
    write_json(PROJECT_ROOT/'outputs/tables/reporting/reporting_refresh_audit.json',certificate)
    print(json.dumps({'run_id':run_id,'status':'passed','figures':len(manifest['figures']),'planned_categories':len(manifest['coverage']),**result}))
    return certificate

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-id');args=parser.parse_args();run(args.run_id)
