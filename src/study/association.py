"""Association eligibility and complete cases; no predictive preprocessing."""
from __future__ import annotations
import math
import numpy as np
import pandas as pd
from src.pipeline.storage import json_records
from src.pipeline.protocol import canonical_hash


def permitted(missing_fraction, limit):
    if not math.isfinite(missing_fraction) or not 0 <= missing_fraction <= 1:
        raise ValueError('Invalid association missing fraction')
    if not math.isfinite(limit) or not 0 <= limit <= 1:
        raise ValueError('Invalid association eligibility limit')
    return missing_fraction <= limit


def qualify(prediction, saved_complete_cases, design):
    required = design['models']['MEW']
    missing = prediction[required].isna().any(axis=1)
    complete = prediction.loc[~missing].copy().reset_index(drop=True)
    if canonical_hash(json_records(complete)) != canonical_hash(json_records(saved_complete_cases.reset_index(drop=True))):
        raise ValueError('Reconstructed union complete cases differ from frozen SQL sample')
    if complete[required].isna().any().any() or not np.isfinite(complete.log_price).all():
        raise ValueError('Association requires complete predictors and observed outcome')
    fraction = float(missing.mean())
    return complete, {'prediction_n': len(prediction), 'association_n': len(complete),
                      'missing_n': int(missing.sum()), 'missing_fraction': fraction,
                      'association_missing_limit': design['association_missing_limit'],
                      'eligibility': 'PASS' if permitted(fraction, design['association_missing_limit']) else 'BLOCKED_MATERIAL_MISSINGNESS',
                      'complete_case_records_sha256': canonical_hash(json_records(complete)),
                      'inferential_imputation': False, 'outcome_imputed': False}
