"""Verify Stockholm's bedroom missingness against immutable source and SQL rows."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
from src.ingestion.common import sha256_file
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.study.sample_freeze import records
from src.study.sources import get_engine, historical_inputs, write_once
from src.study.specification import load_design
from src.study.store import read_package


def audit():
    city = 'stockholm'
    selected = json.loads((ROOT / 'config/study/sample_selection.json').read_text())
    design, _ = load_design()
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            rows, _, source = historical_inputs(conn, city)
            frozen = records(conn, selected, city, 'sample', 'prediction_sample')
            summary, frozen_dependencies = read_package(conn, selected[city]['run_id'], city, 'sample')
            if canonical_hash(summary) != selected[city]['summary_sha256']:
                raise ValueError('Frozen sample summary differs')
            if canonical_hash(json_records(pd.DataFrame(frozen))) != summary['record_sha256']:
                raise ValueError('Frozen sample rows differ')
    finally:
        engine.dispose()
    raw = {row['listing_id']: row['raw'] for row in rows}
    if len(raw) != len(rows):
        raise ValueError('Duplicate source listing keys')
    missing_types = Counter()
    missing_n = 0
    for row in frozen:
        original = raw[row['listing_id']]['bedrooms']
        expected = None if original in ('', None) else float(original)
        if expected != row['bedrooms']:
            raise ValueError('Source bedroom value differs from frozen sample')
        if expected is None:
            missing_n += 1
            missing_types['empty_string' if original == '' else 'null'] += 1
    frame = pd.DataFrame(frozen)
    union_n = int(frame[design['models']['MEW']].isna().any(axis=1).sum())
    if union_n != missing_n or union_n != len(frozen) - summary['association_n']:
        raise ValueError('Missingness is not exclusively source bedroom blanks')
    limit = frozen_dependencies['design']['association_missing_limit']
    fraction = union_n / len(frozen)
    if fraction != summary['association_missing_fraction'] or fraction <= limit:
        raise ValueError('Frozen missingness gate differs')
    return {
        'status': 'SOURCE_VERIFIED_INFERENCE_REMAINS_BLOCKED', 'city': city,
        'prediction_n': len(frozen), 'association_complete_case_n': summary['association_n'],
        'required_predictor_missing_n': union_n, 'sole_missing_predictor': 'bedrooms',
        'original_source_missing_types': dict(missing_types),
        'bedroom_named_source_columns': sorted(k for k in rows[0]['raw'] if 'bedroom' in k.lower()),
        'all_frozen_bedroom_values_equal_original_source': True,
        'missing_fraction': fraction, 'frozen_missing_limit': limit,
        'minimum_observed_values_needed_to_meet_unchanged_gate': union_n - math.floor(limit * len(frozen)),
        'listing_source_sha256': source['listing_sha256'],
        'sample_selection': selected[city], 'sample_records_sha256': summary['record_sha256'],
        'design_file_sha256': sha256_file(ROOT / 'archive/before_association_amendment/config/study/design.json'),
        'source_parser_sha256': sha256_file(ROOT / 'src/study/samples.py'),
        'audit_script_sha256': sha256_file(ROOT / 'archive/before_association_amendment/scripts/study_missingness_source_check.py'),
        'database_transaction': 'READ ONLY', 'raw_or_sql_rows_changed': False,
        'models_refitted': False, 'outcome_imputed': False,
        'decision_required': 'Explicit validated missing-data amendment before dependent inference',
        'alternative_bedroom_values_qualified': False,
        'interpretation': 'Source blanks, not a parsing loss. No text-based reconstruction, proxy substitution or inferential imputation performed.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    result = audit()
    destination = ROOT / 'docs/analysis/missingness_source_audit.json'
    if args.verify:
        if json.loads(destination.read_text()) != result:
            raise ValueError('Recorded source missingness audit differs')
    else:
        write_once(destination, (json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(result, indent=2))
