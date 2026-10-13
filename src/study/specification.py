"""Validated final design; no historical scientific defaults are inherited silently."""
from __future__ import annotations

import json
import re
from pathlib import Path

from src.ingestion.common import PROJECT_ROOT, sha256_file
from src.pipeline.protocol import canonical_hash

CONFIG = PROJECT_ROOT / 'config/study'
CITIES = ('copenhagen', 'oslo', 'stockholm')
MODELS = ('M0', 'ME', 'MW', 'MEW')


def neutral_token(value):
    if (not isinstance(value, str) or not re.fullmatch(r'[a-z][a-z0-9_]*', value)
            or re.search(r'(?:^|_)(?:v\d+|a\d+|version)(?:_|$)', value, re.I)):
        raise ValueError('Functional identity required; sequential version/stage markers forbidden')
    return value


def load_design(root=PROJECT_ROOT):
    design = json.loads((root / 'config/study/design.json').read_text())
    cities = json.loads((root / 'config/study/cities.json').read_text())
    neutral_token(design['design_id'])
    if tuple(design['cities']) != CITIES or set(cities) != set(CITIES):
        raise ValueError('Exactly three isolated cities required')
    x, e, w = (design['blocks'][k] for k in ('X', 'E', 'W'))
    expected = {'M0': x, 'ME': x + e, 'MW': x + w, 'MEW': x + e + w}
    if design['models'] != expected:
        raise ValueError('Four exact common X/E/W models required')
    if any(re.search(r'income|housing|residential_price|rent_price', f, re.I) for f in x+e+w):
        raise ValueError('Excluded scientific dependency in feature registry')
    if any(len(v) != len(set(v)) for v in expected.values()):
        raise ValueError('Duplicate feature membership')
    if (design['validation']['minimum_test'] != 15 or design['validation']['minimum_train'] != 500
            or design['validation']['inner_spatial_folds'] != 4):
        raise ValueError('Frozen support/inner-fold decision changed')
    pairs = [[s, t] for s in CITIES for t in CITIES if s != t]
    if design['transfer_directions'] != pairs:
        raise ValueError('Six distinct single-source directional transfers required')
    for city, n in zip(CITIES, (11, 17, 11), strict=True):
        c = cities[city]
        if c['operational_count'] != n or len(set(c['operational_mapping'].values())) != n:
            raise ValueError('Operational groups differ from researcher amendment')
    candidate = root / design['candidates']['path']
    if sha256_file(candidate) != design['candidates']['file_sha256']:
        raise ValueError('Preserved candidate bytes changed')
    candidates = json.loads(candidate.read_text())['candidates']
    if len(candidates) != 30 or len({canonical_hash(c) for c in candidates}) != 30:
        raise ValueError('Exactly thirty unique inherited candidates required')
    return design, cities


def operational_group(city, raw_label):
    _, cities = load_design()
    if city not in CITIES:
        raise ValueError('Unknown city')
    if raw_label not in cities[city]['operational_mapping']:
        raise ValueError('Unmapped raw label; no inferred spelling/group assignment')
    return cities[city]['operational_mapping'][raw_label]
