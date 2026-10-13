"""Housing-free scope checks; no sample construction, fold creation or fitting."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

from src.v4.specification import DEFINITION_VERSION, model_definition

REQUIRED_QUALIFICATIONS = ('study_boundary', 'analysis_geography', 'context', 'accessibility_support')


def scope_check(frame: pd.DataFrame, *, qualifications: dict) -> dict:
    """Check supplied candidate rows without filtering, filling or mutating them.

    A passed scope check is not empirical readiness. Later steps must qualify
    sources and freeze samples/folds/preprocessing independently. Partial listing
    predictor missingness stays visible for training-only treatment; entirely
    missing or nonfinite required predictors block. Context/geography approval is
    explicit and never inferred from the presence of a housing audit.
    """
    blockers = [name + ': unresolved/unqualified' for name in REQUIRED_QUALIFICATIONS
                if qualifications.get(name) is not True]
    features = model_definition('MEW')['features']
    required = ('listing_id', 'price_nightly', 'log_price', 'inside_boundary',
                'official_analysis_area_id', *features)
    missing = set(required) - set(frame.columns)
    blockers += ['Missing required field: ' + name for name in sorted(missing)]
    if frame.empty:
        blockers.append('Empty candidate scope')
    if not missing and not frame.empty:
        ids = frame['listing_id']
        if ids.isna().any() or ids.astype(str).str.strip().eq('').any() or ids.astype(str).duplicated().any():
            blockers.append('Missing/duplicate listing IDs')
        try:
            price = pd.to_numeric(frame['price_nightly'], errors='raise').to_numpy(dtype=float)
            outcome = pd.to_numeric(frame['log_price'], errors='raise').to_numpy(dtype=float)
            if (not np.isfinite(price).all() or (price <= 0).any() or not np.isfinite(outcome).all()
                    or not np.allclose(outcome, np.log(price), rtol=1e-10, atol=1e-10)):
                blockers.append('Invalid original positive observed Airbnb outcome; never impute/replace')
        except (ValueError, TypeError):
            blockers.append('Invalid original positive observed Airbnb outcome; never impute/replace')
        if not frame['inside_boundary'].map(lambda x: isinstance(x, (bool, np.bool_)) and bool(x)).all():
            blockers.append('Unresolved/outside study-boundary membership')
        area = frame['official_analysis_area_id']
        if area.isna().any() or area.astype(str).str.strip().eq('').any():
            blockers.append('Unresolved official analysis geography')
        for feature in features:
            values = frame[feature]
            if values.isna().all():
                blockers.append(feature + ': entirely missing required predictor')
                continue
            if feature == 'property_type':
                if values.dropna().astype(str).str.strip().eq('').any():
                    blockers.append(feature + ': invalid categorical control')
                continue
            try:
                numbers = pd.to_numeric(values.dropna(), errors='raise').astype(float)
                if not all(math.isfinite(v) for v in numbers):
                    blockers.append(feature + ': nonfinite required predictor')
            except (ValueError, TypeError):
                blockers.append(feature + ': invalid numeric predictor')
    return {'design_id': DEFINITION_VERSION, 'status': 'BLOCKED' if blockers else 'SCOPE_CHECK_PASSED',
            'rows_checked': len(frame), 'rows_removed': 0, 'blockers': blockers,
            'research_executed': False}
