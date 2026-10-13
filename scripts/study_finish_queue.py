"""Dependency-driven completion of the current authorized immutable study run."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.study.sources import write_once
from src.study.specification import CITIES

SCENARIOS=['speed_4p0','speed_5p4','continuous_decay']
SCHEMES=[f'blocks_{size}m_origin_{origin}' for size in [1000,2000] for origin in ['0_0','0p5_0p5']]
JOINED='_'.join(SCHEMES)
MEASURE_NAME='extended_'+'_'.join(SCENARIOS)+'_selection.json'


def execute(args,label):
    path=Path('/private/tmp')/('study-'+label+'.log')
    with path.open('x') as log:
        completed=subprocess.run([str(ROOT/'.venv/bin/python'),*args],cwd=ROOT,env=environment(),stdout=log,stderr=subprocess.STDOUT)
    if completed.returncode:raise RuntimeError(label+' failed; inspect '+str(path))
    print(label,'COMPLETE',flush=True)


def environment():
    env=os.environ.copy();env.update({'STUDY_MODEL_WORKERS':'1','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MPLCONFIGDIR':'/private/tmp/study-mpl-cache'})
    return env


def main():
    processes={};logs=[];geometric_done=False;last=None
    try:
        while True:
            if (ROOT/'config/study/measurement_variant_selection.json').exists() and not processes:
                for city in CITIES:
                    if (ROOT/'runs'/city/MEASURE_NAME).exists():continue
                    log=Path('/private/tmp')/('study-'+city+'-measurement-models.log')
                    handle=log.open('x');logs.append(handle)
                    processes[city]=subprocess.Popen([str(ROOT/'.venv/bin/python'),'-u','-m','src.reporting.study_extended_sensitivity','--city',city,'--scenarios',*SCENARIOS],
                                                     cwd=ROOT,env=environment(),stdout=handle,stderr=subprocess.STDOUT)
                    print(city,'measurement model sensitivities STARTED',flush=True)
            for city,process in processes.items():
                code=process.poll()
                if code is not None and code!=0:raise RuntimeError(city+' measurement models failed')
            grids_ready=all((ROOT/'runs'/city/('within_city_'+JOINED+'_selection.json')).exists() for city in CITIES)
            if grids_ready and not geometric_done:
                for city in CITIES:
                    selections=json.loads((ROOT/'runs'/city/('within_city_'+JOINED+'_selection.json')).read_text())
                    for scheme in SCHEMES:
                        chosen=[s for s in selections if s['scheme']==scheme]
                        if len(chosen)!=5:raise ValueError('Exactly five outer folds required per frozen grid')
                        path=ROOT/'runs'/city/('within_city_'+scheme+'_selection.json')
                        if path.exists():
                            if json.loads(path.read_text())!=chosen:raise ValueError('Completed grid selector differs')
                        else:write_once(path,(json.dumps(chosen,indent=2)+'\n').encode())
                for scheme in SCHEMES:
                    if (ROOT/'config/study'/('results_'+scheme+'.json')).exists():continue
                    execute(['-c','from src.reporting.study_results import within_tables; a,b=within_tables('+repr(scheme)+'); print(len(a),len(b))'],'verify-'+scheme)
                geometric_done=True
            ready=geometric_done and all((ROOT/'runs'/city/'robustness_selection.json').exists()
                                        and (ROOT/'runs'/city/'training_sensitivity_selection.json').exists()
                                        and (ROOT/'runs'/city/MEASURE_NAME).exists() for city in CITIES)
            ready=ready and all(any((ROOT/'runs'/city).glob('extended_buffer_500_buffer_1000*_selection.json')) for city in CITIES)
            state=(geometric_done,tuple(city for city in CITIES if (ROOT/'runs'/city/'robustness_selection.json').exists()),
                   tuple(city for city in CITIES if (ROOT/'runs'/city/'training_sensitivity_selection.json').exists()),
                   tuple(city for city in CITIES if (ROOT/'runs'/city/MEASURE_NAME).exists()))
            if state!=last:print('dependency state',state,flush=True);last=state
            if ready:break
            time.sleep(20)
        if not (ROOT/'config/study/robustness_results_selection.json').exists():execute(['-m','src.reporting.study_robustness_results'],'verify-all-robustness')
        if not (ROOT/'docs/analysis/research_report.md').exists():execute(['-m','src.reporting.study_report'],'generate-research-report')
        if not (ROOT/'docs/analysis/release_audit.json').exists():execute(['scripts/study_release_audit.py'],'release-audit')
        print('ALL INDEPENDENT SCIENTIFIC COMPUTATION AND REPORTING COMPLETE; REVIEW AND GIT HANDOVER REMAIN',flush=True)
    finally:
        for handle in logs:handle.close()


if __name__=='__main__':main()
