"""Fresh outcomes, reference benchmarks and explicit inherited control parsing."""
from __future__ import annotations
import json
import math
import numpy as np
import pandas as pd
from src.pipeline.build_analysis_dataset import bathroom_value
from src.study.specification import load_design


def reference_sample(rows):
    selected = [r for r in rows if r['dwelling_eligible'] and r['inside_boundary'] and r['positive_price']]
    if not selected:
        raise ValueError('Empty positive observed inside-mask reference sample')
    records = [{'listing_id': r['listing_id'], 'price_nightly': r['price_nightly'], 'log_price': r['log_price']} for r in selected]
    for r in records:
        if r['price_nightly'] <= 0 or not math.isfinite(r['log_price']) or not math.isclose(r['log_price'], math.log(r['price_nightly']), abs_tol=1e-12):
            raise ValueError('Reference outcome is not original observed positive log price')
    mean = float(np.mean([r['log_price'] for r in records]))
    return {'reference_n': len(records), 'mean_log_price': mean, 'geometric_mean_price': math.exp(mean),
            'before_accessibility_exclusions': True, 'outcome_imputed': False}, records


def listing_controls(rows):
    design, _ = load_design()
    result = []
    amenities = {'amenity_wifi':'Wifi','amenity_dishwasher':'Dishwasher','amenity_washer':'Washer',
                 'amenity_dryer':'Dryer','amenity_workspace':'Dedicated workspace',
                 'amenity_free_parking':'Free parking on premises','amenity_private_balcony':'Private patio or balcony',
                 'amenity_self_checkin':'Self check-in'}
    def number(value):
        if value in ('', None):
            return None
        parsed = float(value)
        if not math.isfinite(parsed) or parsed < 0:
            raise ValueError('Invalid source control; no silent replacement')
        return parsed
    for row in rows:
        raw = row['raw']
        structured = number(raw['bathrooms'])
        bathroom, provenance = bathroom_value(np.nan if structured is None else structured, raw['bathrooms_text'])
        record = {'listing_id': row['listing_id'], 'property_type': raw['property_type'],
                  'accommodates': number(raw['accommodates']), 'bedrooms': number(raw['bedrooms']),
                  'bathrooms_effective': None if pd.isna(bathroom) else bathroom, 'bathrooms_source': provenance,
                  'superhost': {'t':1.,'true':1.,'yes':1.,'f':0.,'false':0.,'no':0.}.get(raw['host_is_superhost']),
                  'price_nightly': row['price_nightly'], 'log_price': row['log_price'],
                  'number_of_reviews': number(raw['number_of_reviews']),
                  'review_scores_rating': number(raw['review_scores_rating'])}
        for src, dst in [('minimum_nights','log1p_minimum_nights'),('host_listings_count','log1p_host_listings_count')]:
            v = number(raw[src]); record[dst] = None if v is None else math.log1p(v)
        values = json.loads(raw['amenities']) if raw['amenities'] else None
        if values is not None and (not isinstance(values, list) or any(not isinstance(x, str) for x in values)):
            raise ValueError('Malformed amenities; no inferred absence')
        for dst, key in amenities.items():
            record[dst] = None if values is None else float(key in values)
        result.append(record)
    return result
