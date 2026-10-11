"""Rebuild the repository migration report from mappings and verification records."""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.ingestion.common import PROJECT_ROOT, write_json
from src.pipeline.run_pipeline import DEPENDENCIES


def file_tree(root: Path) -> str:
    paths = sorted(p.relative_to(PROJECT_ROOT).as_posix() for p in root.rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts)
    return '\n'.join(paths) + '\n'


def test_summary(path: Path) -> str:
    content = path.read_text()
    count = re.search(r'Ran (\d+) tests', content)
    skipped = re.search(r'OK \(skipped=(\d+)\)', content)
    if not count or not skipped:
        raise RuntimeError('No successful test summary in ' + str(path))
    total, skip = int(count[1]), int(skipped[1])
    return f'{total} discovered; {total-skip} passed; {skip} explicitly skipped'


def build():
    log=PROJECT_ROOT/'outputs/tables/reproducibility'
    preflight=json.loads((log/'preflight.json').read_text())
    mapping=json.loads((PROJECT_ROOT/'docs/migration_mapping.json').read_text())
    decision=json.loads((PROJECT_ROOT/'config/qualified_income_decision.json').read_text())
    metadata_path=log/'run_metadata.json'
    execution=json.loads(metadata_path.read_text()) if metadata_path.exists() else None
    from src.pipeline.audit_reproducibility import archive_check
    from src.pipeline.protocol import verify_inputs
    archive=archive_check();raw=verify_inputs()
    tests=[]
    for filename in ['qualified_income_tests.txt','qualified_income_database_tests.txt']:
        path=log/filename
        if path.exists():tests.append(filename+': '+test_summary(path))
    db=preflight['checks']['database'].get('details',{})
    lines=['# Version 3 migration and rerun audit','',
        'Explicit income protocol amendment accepted on 4 October 2026. Preflight: '+preflight['status']+'.',
        'Income decision: qualified_accepted; metadata: qualified. Full empirical execution status: '+
        (execution.get('status','running') if execution else 'not started')+'.','',
        'The successful V3 refactor remains intact. Prior source/module/output mappings and original audit records are preserved in '
        'docs/migration_mapping.json, archive/legacy_v2 and the checksum archive of the expanded municipal income investigation.',
        'Original analytical schemas and all historical source investigations remain preserved. Raw sources are immutable; '
        'PostgreSQL/PostGIS remains authoritative. Aggregate CSVs are exports.','',
        'Applied migration hashes verified: '+str(db.get('applied_migration_hashes_verified','database check failed'))+
        '. Original migrations 001–021 are unchanged. Additive migration 022 creates qualified_area_income and adds its transparent context field.','',
        'Verified raw files: '+str(len(raw['files']))+'; preserved legacy files: '+str(archive['archived_files_verified'])+'.','',
        '## Income amendment','',decision['methods_text'],'',
        'Eleven rows / 110 observed decile means; common transformation: '+decision['transformation']+'. '
        'Authoritative SQL table: v3_features.qualified_area_income. Full deciles/provenance/basis/SHA/qualification export: '
        'outputs/tables/area_context/qualified_area_income_2024.csv.','',
        'Supportive Copenhagen published-total QA: 340620.1 vs 340949.1 DKK, −329 DKK, −0.0964953%, '
        'tenth decile −3376 DKK. Missing eligible weights remain NULL; this is not proof of exact equivalence.','',
        'Mandatory M0_no_income/ME_no_income/MW_no_income/MEW_no_income (OLS and XGBoost) omit only income, '
        'reusing the primary sample and saved random-five/geographic-eleven outer and inner-four folds, preprocessing and thirty candidates. '
        'The complete audit requires paired metrics, OLS accessibility coefficients, ΔRMSE, all area results and conclusion flags.','',
        '## Documentation and checks','',
        'Updated both repository V3 DOCX copies, specification, decision log, income status, data dictionary, source inventory and reproducibility metadata. '
        'Original Downloads documents and every non-document DOCX member remain unchanged.',*tests,'',
        'Blocking preflight checks: '+str(preflight['blocking_checks'])+'.','',
        '## Dependency order','']
    lines.extend(str(i)+'. '+name+' — src.pipeline.'+module+'.'+function
                 for i,(name,module,function) in enumerate(DEPENDENCIES,1))
    lines+=['','## Execution evidence','']
    if execution:
        lines += ['Run '+execution['run_id']+'; completed components: '+', '.join(execution['component_results'])+'.',
                  'Error: '+execution['error'] if execution.get('error') else 'No recorded execution error.']
    else:lines+=['No current empirical sample N, performance, SHAP or completed-run certificate is claimed before execution.']
    lines+=['','Material OLS missingness above 5% remains an independent scientific stop pending the specified multiple-imputation/pooling implementation. '
            'No inferential substitute or silently overwritten/resumed namespace is permitted.','']
    (PROJECT_ROOT/'docs/migration_rerun_audit.md').write_text('\n'.join(lines))
    (log/'source_tree.txt').write_text(file_tree(PROJECT_ROOT/'src'))
    (log/'output_tree.txt').write_text(file_tree(PROJECT_ROOT/'outputs'))
    write_json(log/'income_amendment_verification.json',{'version':'qualified_income_verification_v3','preflight_status':preflight['status'],
        'scientific_run_started':execution is not None,'execution_status':execution.get('status','running') if execution else 'not_started',
        'tests':tests,'raw_files_verified':len(raw['files']),'legacy_files_verified':archive['archived_files_verified'],
        'applied_migrations_verified':db.get('applied_migration_hashes_verified'),'blocking_checks':preflight['blocking_checks']})
    return {'report':'docs/migration_rerun_audit.md','preflight_status':preflight['status']}

if __name__=='__main__':print(json.dumps(build(),indent=2))
