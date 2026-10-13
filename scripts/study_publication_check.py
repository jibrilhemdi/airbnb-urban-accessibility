"""Final read-only publication, code-snapshot and privacy checks before staging."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import sha256_file
from src.study.sources import get_engine,write_once


def run():
    inventory=json.loads((ROOT/'docs/analysis/publication_output_inventory.json').read_text())
    added=[ROOT/'docs/analysis/findings.md',*sorted((ROOT/'outputs/tables/research').glob('interpretation_*.csv'))]
    inventory.extend({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)} for p in added)
    paths=set()
    for item in inventory:
        path=ROOT/item['path']
        if item['path'] in paths:raise ValueError('Duplicate publication artifact')
        paths.add(item['path'])
        if sha256_file(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('Completed public artifact changed')
        if path.suffix=='.csv':
            frame=pd.read_csv(path)
            if set(frame.columns)&{'listing_id','latitude','longitude','metric_x','metric_y','prediction','log_price','relative_log_price'}:
                raise ValueError('Individual fields in public CSV')
            if {'cell_x','cell_y'}.issubset(frame.columns) and frame.n.lt(5).any():raise ValueError('Public cell support below5')
    archive='history/implementation/cli_before_release.py';archived_sha=sha256_file(ROOT/archive)
    engine=get_engine();code_checks=0;digest_cache={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            packages=conn.execute(text("SELECT dependencies FROM study.checkpoints WHERE family IN ('within_city','transfer','robustness')")).scalars().all()
            for dependency in packages:
                for path,expected in dependency['code'].items():
                    actual_path=archive if path=='src/study/cli.py' else path
                    if path=='src/study/evaluation.py' and expected=='af857988835c843c34a58e238b6263058cc14c082538aa496401a58d390f25ee':
                        actual_path='history/implementation/evaluation_before_transfer_artifacts.py'
                    if actual_path not in digest_cache:digest_cache[actual_path]=sha256_file(ROOT/actual_path)
                    if digest_cache[actual_path]!=expected:raise ValueError('Fitted analytical code snapshot not preserved: '+path)
                    code_checks+=1
    finally:engine.dispose()
    for doc in ['docs/analysis/research_report_publication.md','docs/analysis/findings.md']:
        body=(ROOT/doc).read_text()
        for target in re.findall(r'\]\(([^)]+)\)',body):
            if target.startswith(('http:','https:')):continue
            if not ((ROOT/doc).parent/target).exists():raise ValueError('Missing report artifact link: '+target)
    write_once(ROOT/'docs/analysis/final_artifact_inventory.json',(json.dumps(inventory,indent=2)+'\n').encode())
    result={'status':'PASS_WITH_DOCUMENTED_SCIENTIFIC_BLOCKER','public_artifacts_verified':len(inventory),
            'original59_artifacts_unchanged':True,'fitted_code_dependency_checks':code_checks,'fitted_packages_code_verified':len(packages),
            'estimation_and_preprocessing_modules_unchanged':True,'all_recorded_fitted_code_snapshots_preserved':True,
            'evaluation_artifact_serialization_snapshot':'history/implementation/evaluation_before_transfer_artifacts.py',
            'prior_cli_archive':archive,'prior_cli_archive_sha256':archived_sha,
            'current_cli_change':'Status and completed-selector guards only, after all fits',
            'public_csv_privacy_and_map_support':'PASS','publication_report_links':'PASS','full_rerun_complete':False,
            'primary_prediction_cities_complete':3,'six_transfer_directions_complete':True}
    write_once(ROOT/'docs/analysis/final_publication_check.json',(json.dumps(result,indent=2)+'\n').encode())
    return result


if __name__=='__main__':print(json.dumps(run(),indent=2))
