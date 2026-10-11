"""Canonical accessibility-only registry; frozen housing definitions stay separate."""
from __future__ import annotations

import json
from pathlib import Path

from src.pipeline.model_specification import BASE_NUMERIC, CATEGORICAL, E_NUMERIC, W_NUMERIC

DEFINITION_VERSION = 'v4_accessibility_only_20261011'
HISTORICAL_VERSION = 'v4_housing_standard_20261011'
DEFINITIONS = (DEFINITION_VERSION, HISTORICAL_VERSION)
CONFIG_PATH = Path(__file__).resolve().parents[2] / 'config/v4/research_design_accessibility_only.json'
PRIMARY_BLOCKS = {'M0': ['X'], 'ME': ['X', 'E'], 'MW': ['X', 'W'], 'MEW': ['X', 'E', 'W']}
INHERITED_BLOCKS = {'X': list(BASE_NUMERIC + CATEGORICAL), 'E': list(E_NUMERIC), 'W': list(W_NUMERIC)}
SCENARIOS = ('primary', 'no_income')


def validate_definition(design: dict) -> None:
    if (design.get('version') != 'research_design_v4'
            or design.get('design_id') != DEFINITION_VERSION
            or design.get('definition_version') != DEFINITION_VERSION):
        raise ValueError('Explicit accessibility-only design required; historical definitions are immutable')
    if design.get('blocks') != INHERITED_BLOCKS:
        raise ValueError('Require exact inherited X/E/W membership; no residential-price/rent proxies or silent control changes')
    expected = {name: {'definition_id': DEFINITION_VERSION + ':' + name, 'blocks': blocks}
                for name, blocks in PRIMARY_BLOCKS.items()}
    if design.get('primary_models') != expected:
        raise ValueError('Exactly the four version-qualified accessibility-only models are primary')
    if any(key in design for key in ('housing', 'automatic_no_housing_fallback',
                                    'incremental_benefit_of_housing_estimand_authorized')):
        raise ValueError('Housing policy is historical, not an active dependency/variant')
    sensitivity = design['no_income_sensitivity']
    if (not sensitivity['mandatory'] or sensitivity['omit_only'] != ['income_100k_dkk']
            or 'retain_housing' in sensitivity
            or sensitivity['definition_ids'] != {name: DEFINITION_VERSION + ':no_income:' + name for name in PRIMARY_BLOCKS}):
        raise ValueError('Mandatory no-income omits only income from the revised primary design')
    if 'housing_missingness' in design['samples'] or 'missing_qualified_housing_action' in design['cities']:
        raise ValueError('Retired housing sample/city gates cannot be active')


def load_design(path: Path = CONFIG_PATH, *, design_id: str = DEFINITION_VERSION) -> dict:
    if design_id == HISTORICAL_VERSION:
        from src.v4.historical_specification import load_design as historical_load
        return historical_load() if path == CONFIG_PATH else historical_load(path)
    if design_id != DEFINITION_VERSION:
        raise ValueError('Unknown scientific design')
    design = json.loads(path.read_text(encoding='utf-8'))
    validate_definition(design)
    return design


def model_definition(name: str, *, scenario: str = 'primary', design: dict | None = None,
                     design_id: str = DEFINITION_VERSION) -> dict:
    """Feature metadata only. Design, model and sensitivity remain separate."""
    if design_id == HISTORICAL_VERSION:
        from src.v4.historical_specification import model_definition as historical_model
        result = historical_model(name, scenario=scenario, design=design)
        return {**result, 'design_id': design_id}
    if design_id != DEFINITION_VERSION:
        raise ValueError('Unknown scientific design')
    design = load_design(design_id=design_id) if design is None else design
    validate_definition(design)
    if name not in PRIMARY_BLOCKS or scenario not in SCENARIOS:
        raise ValueError('Unknown model/sensitivity; no no_housing or residential-price variant')
    model = design['primary_models'][name]
    features = [f for block in model['blocks'] for f in design['blocks'][block]]
    identity = model['definition_id']
    if scenario == 'no_income':
        features.remove('income_100k_dkk')
        identity = design['no_income_sensitivity']['definition_ids'][name]
    return {'design_id': DEFINITION_VERSION, 'definition_id': identity, 'model': name,
            'scenario': scenario, 'features': tuple(features)}
