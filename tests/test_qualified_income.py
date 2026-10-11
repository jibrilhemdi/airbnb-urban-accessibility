"""Qualified acceptance cannot bypass frozen data, formulas or robustness."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from src.ingestion.common import sha256_file
from src.pipeline.protocol import DESIGN
from src.pipeline.qualified_income import validate, source_rows, CONFIG_PATH
from src.pipeline.model_specification import FEATURES, NO_INCOME_FEATURES, build_preprocessor
from src.pipeline.run_income_robustness import compare_metrics, compare_incremental, compare_coefficients

class QualifiedIncomeTests(unittest.TestCase):
    def test_active_decision_has_eleven_complete_source_derived_means(self):
        result=validate(DESIGN);rows=source_rows()
        self.assertEqual(result['status'],'qualified_accepted')
        self.assertEqual(result['decile_cells'],110)
        self.assertEqual([r['source_table'] for r in rows].count('KKIND5'),10)
        self.assertEqual(rows[-1]['source_table'],'IFOR35')
        self.assertEqual(rows[-1]['price_basis'],'nominal_current_prices')
        self.assertEqual(rows[-1]['equiv_disposable_income_2024'],'404647.2')
        self.assertTrue(all(r['eligible_person_count'] is None and r['harmonisation_status']=='qualified' for r in rows))

    def test_approval_labels_and_disabled_robustness_fail(self):
        for status in ['unverified','verified','verified_equivalent']:
            d=copy.deepcopy(DESIGN);d['income_harmonisation']['status']=status
            with self.assertRaises(RuntimeError):validate(d)
        d=copy.deepcopy(DESIGN);d['no_income_robustness']['enabled']=False
        with self.assertRaises(RuntimeError):validate(d)

    def test_source_and_selection_hash_drift_fails(self):
        original=sha256_file
        for marker in ['KKIND5_2024.csv','IFOR35_2024.csv','KKIND5_2024_selection.json','IFOR35_2024_selection.json']:
            with self.subTest(marker=marker),patch('src.pipeline.qualified_income.sha256_file',
                side_effect=lambda p:'0'*64 if str(p).endswith(marker) else original(p)),self.assertRaises(RuntimeError):validate(DESIGN)

    def test_source_deciles_values_or_provenance_cannot_drift(self):
        for field,value in [('deciles',['1']*9),('year','2023'),('source_url',''),
                ('equiv_disposable_income_2024','1'),('qualification','')]:
            rows=source_rows();rows[0][field]=value
            with self.subTest(field=field),patch('src.pipeline.qualified_income.source_rows',return_value=rows),self.assertRaises(RuntimeError):validate(DESIGN)

    def test_even_rehashed_decision_cannot_change_year_or_formula(self):
        for field,value in [('year',2023),('transformation','weighted by listings'),('qualification','')]:
            frozen=json.loads(CONFIG_PATH.read_text());frozen[field]=value
            with tempfile.TemporaryDirectory() as directory:
                p=Path(directory)/'decision.json';p.write_text(json.dumps(frozen))
                d=copy.deepcopy(DESIGN);d['income_harmonisation']['decision_sha256']=sha256_file(p)
                with patch('src.pipeline.qualified_income.CONFIG_PATH',p),self.assertRaises(RuntimeError):validate(d)

    def test_no_income_preprocessor_omits_only_income(self):
        for name,cols in FEATURES.items():
            expected=tuple(c for c in cols if c!='income_100k_dkk')
            self.assertEqual(NO_INCOME_FEATURES[name+'_no_income'],expected)
            prep=build_preprocessor(name+'_no_income')
            self.assertNotIn('income_100k_dkk',prep.transformers[0][2])

    def test_paired_reporting_preserves_units_and_flags_reversal(self):
        p=pd.DataFrame([dict(scheme='geographic_11',model='OLS',feature_set='MW',rmse_log=.4,mae_log=.3,r2_log=.2)])
        s=p.copy();s.feature_set='MW_no_income';s.rmse_log=.5;s.mae_log=.35;s.r2_log=.1
        compared=compare_metrics(p,s,['scheme','model','feature_set'])
        self.assertAlmostEqual(compared.change_rmse_log.iloc[0],.1)
        self.assertAlmostEqual(compared.change_r2_log.iloc[0],-.1)
        p=pd.DataFrame([dict(scheme='geographic_11',model='OLS',added='MW',reference='ME',delta_rmse=-.02)])
        s=p.copy();s.added='MW_no_income';s.reference='ME_no_income';s.delta_rmse=.01
        self.assertTrue(compare_incremental(p,s).delta_rmse_sign_reversal.iloc[0])
        s=s.iloc[:0]
        with self.assertRaises(RuntimeError):compare_incremental(p,s)

    def test_coefficient_direction_flags_require_supported_reversal(self):
        p=pd.DataFrame([dict(feature_set='MW',term='nearest_bus_walking_minutes',coefficient=.1,wild_cluster_p_value=.03)])
        s=p.copy();s.feature_set='MW_no_income';s.coefficient=-.1;s.wild_cluster_p_value=.4
        rules=DESIGN['no_income_robustness']['material_change_rules']
        self.assertTrue(compare_coefficients(p,s,rules).material_direction_change.iloc[0])
        p.wild_cluster_p_value=.4
        self.assertFalse(compare_coefficients(p,s,rules).material_direction_change.iloc[0])

    def test_no_income_evaluation_uses_saved_splits_and_equal_candidates(self):
        from contextlib import contextmanager
        from src.pipeline.smoke_checks import synthetic_frame
        from src.pipeline.build_validation_splits import make_outer,inner_splits
        from src.pipeline.run_primary_models import evaluate_cv
        frame=synthetic_frame(n_per_area=8)
        fold,tr,te=make_outer(frame)['geographic_11'][0]
        saved=inner_splits(frame.iloc[tr].reset_index(drop=True))
        class MemoryEngine:
            @contextmanager
            def connect(self):yield None
            @contextmanager
            def begin(self):yield None
        with patch('src.pipeline.run_primary_models.saved_inner',return_value=saved) as reader,\
             patch('src.pipeline.run_primary_models.persist'),patch('src.pipeline.run_primary_models.export'),patch('builtins.print'):
            result=evaluate_cv(frame,{'geographic_11':[(fold,tr,te)]},MemoryEngine(),'synthetic_no_income',
                family='income_robustness',feature_sets=tuple(NO_INCOME_FEATURES),shap=False)
        self.assertEqual(reader.call_count,1)
        self.assertEqual(reader.call_args.args[2:],('geographic_11',fold))
        self.assertEqual(len(result['oof_predictions']),9*len(te))
        self.assertTrue(result['xgboost_tuning'].groupby('feature_set').size().eq(30).all())
        self.assertEqual(set(result['xgboost_tuning'].feature_set),set(NO_INCOME_FEATURES))
        self.assertEqual(len(result['preprocessing']),8)
        self.assertTrue(all('income_100k_dkk' not in c for c in result['preprocessing'].numeric_columns))

    @unittest.skipUnless(os.environ.get('THESIS_DB_TEST')=='1','Opt-in PostgreSQL check')
    def test_sql_freeze_rejects_changed_registration_without_committing(self):
        from sqlalchemy import text
        from src.db.connection import get_engine
        from src.pipeline.qualified_income import verify_sql
        engine=get_engine()
        try:
            with engine.connect() as conn:
                transaction=conn.begin()
                try:
                    self.assertEqual(verify_sql(conn)['qualified_income_rows'],11)
                    conn.execute(text("UPDATE v3_features.qualified_area_income SET source_file_id=(SELECT source_file_id FROM meta.source_files WHERE relative_path LIKE '%IFOR35_2024.csv') WHERE analysis_area='cph_01'"))
                    with self.assertRaises(RuntimeError):verify_sql(conn)
                finally:transaction.rollback()
                self.assertEqual(verify_sql(conn)['qualified_income_rows'],11)
        finally:engine.dispose()

if __name__=='__main__':unittest.main()
