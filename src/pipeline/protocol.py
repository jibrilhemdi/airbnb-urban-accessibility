"""Frozen scientific constants and fail-closed source/protocol validation."""
from __future__ import annotations
import hashlib
import json
import math
from src.ingestion.common import PROJECT_ROOT,sha256_file
DESIGN_PATH=PROJECT_ROOT/'config/research_design.json'
INPUTS_PATH=PROJECT_ROOT/'config/frozen_inputs.json'
DESIGN=json.loads(DESIGN_PATH.read_text())
SEED=DESIGN['seed']; INNER_SEED=DESIGN['inner_seed']
METRIC_EPSG=DESIGN['crs']['metric']
METRES_PER_MINUTE=5000/60
DECAY_LAMBDA=math.log(2)/10
AREA_NAMES=tuple([f'cph_{i:02}' for i in range(1,11)]+['frederiksberg_0147'])
def canonical_hash(value)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False,default=str).encode()).hexdigest()
def verify_inputs()->dict:
    frozen=json.loads(INPUTS_PATH.read_text())['files']
    changed=[name for name,digest in frozen.items() if not (PROJECT_ROOT/name).is_file() or sha256_file(PROJECT_ROOT/name)!=digest]
    if changed: raise RuntimeError(f'Frozen dependencies changed or disappeared: {changed}')
    actual={p.relative_to(PROJECT_ROOT).as_posix() for p in (PROJECT_ROOT/'data/raw').rglob('*') if p.is_file() and p.name!='.DS_Store'}
    if actual!=set(frozen): raise RuntimeError('Raw input membership changed; explicitly register a new source freeze')
    return {'files':frozen,'manifest_sha256':sha256_file(INPUTS_PATH)}
def verify_income_evidence()->dict:
    from src.pipeline.qualified_income import validate
    return validate(DESIGN)
def freeze_run_dependencies()->dict:
    return {'input_manifest_sha256':sha256_file(INPUTS_PATH),'design_sha256':sha256_file(DESIGN_PATH),
        'source_sha256':{p.relative_to(PROJECT_ROOT).as_posix():sha256_file(p) for base,pattern in [('src','*.py'),('sql','*.sql'),('config','*'),('docs/design','*')] for p in sorted((PROJECT_ROOT/base).rglob(pattern)) if p.is_file()}}
def verify_run_dependencies(expected:dict):
    if freeze_run_dependencies()!=expected: raise RuntimeError('Code, protocol or input freeze changed during the run')
