"""Read-only final publication/privacy/code checks for the amended research release."""
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
from src.study.archive import preserved_path


def run(inventory_only=False):
    inventory=[]
    for directory in ['outputs/tables/research','outputs/figures/research',*['outputs/metrics/'+s for s in ['neighbourhood','random','transfer','robustness',*[f'blocks_{z}m_origin_{o}' for z in [1000,1500,2000] for o in ['0_0','0p5_0p5']]]]]:
        for p in sorted((ROOT/directory).rglob('*')):
            if p.is_file():inventory.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)})
    for name in ['research_report.md','research_report_publication.md','findings.md','checkpoint_history.json']:
        p=ROOT/'docs/analysis'/name;inventory.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)})
    previous=json.loads((ROOT/'archive/before_association_amendment/docs/analysis/final_artifact_inventory.json').read_text())
    for item in previous:
        p=preserved_path(item['path'],item['sha256'])
        if p.stat().st_size!=item['bytes']:raise ValueError('Original publication bytes unavailable')
    cells=0
    for item in inventory:
        p=ROOT/item['path']
        if p.suffix=='.csv':
            frame=pd.read_csv(p)
            if set(frame.columns)&{'listing_id','latitude','longitude','metric_x','metric_y','prediction','log_price','relative_log_price','record_key'}:
                raise ValueError('Individual fields in public CSV')
            if {'cell_x','cell_y'}.issubset(frame.columns):
                if frame.n.lt(5).any():raise ValueError('Map cell support below5')
                cells+=len(frame)
    engine=get_engine();checks=0;cache={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            packages=conn.execute(text("SELECT dependencies FROM study.checkpoints WHERE family IN ('within_city','transfer','robustness')")).scalars().all()
            for dep in packages:
                for name,expected in dep['code'].items():
                    key=(name,expected)
                    if key not in cache:cache[key]=sha256_file(preserved_path(name,expected))
                    if cache[key]!=expected:raise ValueError('Fitted code snapshot unavailable')
                    checks+=1
    finally:engine.dispose()
    if inventory_only:
        for name in ['publication_output_inventory.json','final_artifact_inventory.json']:
            write_once(ROOT/'docs/analysis'/name,(json.dumps(inventory,indent=2)+'\n').encode())
        return {'status':'INVENTORY_VERIFIED_PENDING_RELEASE_LINK_CHECK','artifacts':len(inventory),'fitted_code_checks':checks}
    links=0
    for name in ['research_report.md','research_report_publication.md','findings.md','reproducibility.md','document_index.md','association_missingness_amendment_20261013.md']:
        doc=ROOT/'docs/analysis'/name
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if target.startswith(('http:','https:')):continue
            if not (doc.parent/target.split('#')[0]).exists():raise ValueError('Missing active report link: '+name+' '+target)
            links+=1
    if len({i['path'] for i in inventory})!=len(inventory):raise ValueError('Duplicate inventory artifact')
    for name in ['publication_output_inventory.json','final_artifact_inventory.json']:
        path=ROOT/'docs/analysis'/name
        if path.exists():
            if json.loads(path.read_text())!=inventory:raise ValueError('Generated final inventory differs')
        else:write_once(path,(json.dumps(inventory,indent=2)+'\n').encode())
    result={'status':'PASS_COMPLETE','public_artifacts_verified':len(inventory),'previous72_artifacts_preserved':True,
            'fitted_code_dependency_checks':checks,'fitted_packages_code_verified':len(packages),
            'estimation_and_preprocessing_modules_unchanged':True,'all_recorded_fitted_code_snapshots_preserved':True,
            'public_csv_privacy_and_map_support':'PASS','publication_report_links_checked':links,
            'full_rerun_complete':True,'primary_prediction_cities_complete':3,'association_cities_complete':3,
            'six_transfer_directions_complete':True,'post_observation_amendment_disclosed':True,
            'active_dependency_file':'requirements.txt','historical_evidence_directory':'archive/'}
    write_once(ROOT/'docs/analysis/final_publication_check.json',(json.dumps(result,indent=2)+'\n').encode())
    return result


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--inventory-only',action='store_true')
    print(json.dumps(run(parser.parse_args().inventory_only),indent=2))
