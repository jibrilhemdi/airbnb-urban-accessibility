"""Scientific safety checks independent of the real outcome/model results."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import networkx as nx
import numpy as np
import pandas as pd
import statsmodels.api as sm
from src.pipeline.protocol import AREA_NAMES,DESIGN,SEED,canonical_hash
from src.pipeline.model_specification import build_preprocessor,FEATURES
from src.pipeline.build_tuning_candidates import generate,SPACE,load_candidates
from src.pipeline.build_validation_splits import make_outer,inner_splits,support_diagnostics
from src.pipeline.build_opportunity_variants import calculate
from src.pipeline.inference import wild_cluster_bootstrap_t,paired_incremental
from src.pipeline.smoke_checks import synthetic_frame
from src.pipeline.output_paths import output_file

class CandidateAndLeakageTests(unittest.TestCase):
    def test_fixed_candidate_budget_and_hash(self):
        first=generate();self.assertEqual(first,generate());candidates=first['candidates']
        self.assertEqual(len(candidates),30);self.assertEqual(len({canonical_hash(c) for c in candidates}),30)
        self.assertEqual(first['candidates_sha256'],canonical_hash(candidates))
        for c in candidates:
            self.assertEqual(set(c),set(SPACE))
            for k,v in c.items():self.assertIn(v,SPACE[k])
    def test_tampered_candidate_freeze_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'candidates.json';data=generate();data['candidates'][0]['max_depth']=99;path.write_text(json.dumps(data))
            with patch('src.pipeline.build_tuning_candidates.PATH',path):
                with self.assertRaisesRegex(RuntimeError,'freeze mismatch'):load_candidates()
    def test_medians_and_categories_are_learned_only_from_training(self):
        train=synthetic_frame();train.loc[0,'bedrooms']=np.nan
        test=train.iloc[:4].copy();test['bedrooms']=1e8;test['property_type']='Held-out category'
        prep=build_preprocessor('M0');prep.fit(train);medians=prep.named_transformers_['numeric'].statistics_.copy()
        with self.assertWarns(UserWarning):transformed=prep.transform(test)
        np.testing.assert_array_equal(medians,prep.named_transformers_['numeric'].statistics_)
        self.assertAlmostEqual(medians[1],train.bedrooms.median());self.assertTrue(np.isfinite(transformed).all())
        self.assertNotIn('Held-out category',prep.named_transformers_['category'].categories_[0])
    def test_outer_geometry_never_uses_outcomes(self):
        frame=synthetic_frame();first=make_outer(frame);frame['log_price']=np.arange(len(frame))*1e8;second=make_outer(frame)
        for scheme in first:
            for a,b in zip(first[scheme],second[scheme]):
                self.assertEqual(a[0],b[0]);np.testing.assert_array_equal(a[1],b[1]);np.testing.assert_array_equal(a[2],b[2])
    def test_inner_blocks_never_leak(self):
        train=synthetic_frame();groups=(np.floor(train.metric_x/1000).astype(int).astype(str)+':'+np.floor(train.metric_y/1000).astype(int).astype(str))
        val_indices=[]
        for learning,validation in inner_splits(train):
            self.assertFalse(set(groups.iloc[learning])&set(groups.iloc[validation]));val_indices.extend(validation)
        self.assertEqual(sorted(val_indices),list(range(len(train))))
    def test_geometric_grids_keep_whole_blocks_and_shift_origins(self):
        frame=synthetic_frame();outer=make_outer(frame)
        for size in DESIGN['block_sizes_m']:
            for fx,fy in DESIGN['grid_origin_fractions']:
                name=f'blocks_{size}m_origin_{fx:g}_{fy:g}';groups=np.column_stack([np.floor((frame.metric_x-size*fx)/size),np.floor((frame.metric_y-size*fy)/size)])
                for _,train,test in outer[name]:self.assertFalse({tuple(x) for x in groups[train]}&{tuple(x) for x in groups[test]})
    def test_predictor_support_detects_real_extrapolation(self):
        frame=synthetic_frame();frame.loc[frame.analysis_area==AREA_NAMES[0],'income_100k_dkk']=99
        details,areas=support_diagnostics(frame,make_outer(frame)['geographic_11'])
        selected=details.loc[(details.heldout_analysis_area==AREA_NAMES[0])&(details.variable=='income_100k_dkk')].iloc[0]
        self.assertEqual(selected.outside_fraction,1);self.assertEqual(areas.loc[areas.heldout_analysis_area==AREA_NAMES[0],'extrapolation_fraction'].iloc[0],1)

class RoutingSensitivityTests(unittest.TestCase):
    def test_decay_has_no_threshold_cutoff_and_unreachable_is_zero(self):
        graph=nx.DiGraph();graph.add_edge(1,2,length_m=2000);graph.add_node(3)
        origins=[dict(snapshot_date='2000-01-01',listing_id=1,snapped_node_id=1,snap_distance_m=0,x=0,y=0)]
        pois=[dict(snapped_node_id=2,snap_distance_m=0,category='food_social'),dict(snapped_node_id=3,snap_distance_m=0,category='cultural_tourist')]
        rows=calculate(graph,origins,pois,np.array([[2000.,0],[0,100]]));data={(r['definition'],r['category']):r for r in rows}
        self.assertAlmostEqual(data[('continuous_decay','food_social')]['walking_value'],2**(-2.4))
        self.assertGreater(data[('continuous_decay','food_social')]['walking_value'],0)
        self.assertEqual(data[('continuous_decay','cultural_tourist')]['walking_value'],0)
        self.assertGreater(data[('continuous_decay','cultural_tourist')]['euclidean_value'],0)
        self.assertEqual(data[('threshold_20','food_social')]['walking_value'],0)
    def test_speed_budget_and_connectors(self):
        graph=nx.DiGraph();graph.add_edge(1,2,length_m=780)
        origins=[dict(snapshot_date='2000-01-01',listing_id=1,snapped_node_id=1,snap_distance_m=20,x=0,y=0)]
        pois=[dict(snapped_node_id=2,snap_distance_m=30,category='food_social')]
        rows=calculate(graph,origins,pois,np.array([[800.,0]]));data={r['definition']:r for r in rows if r['category']=='food_social'}
        self.assertEqual(data['speed_4']['walking_value'],0);self.assertEqual(data['speed_5_4']['walking_value'],1)
        self.assertEqual(data['threshold_15']['budget'],15);self.assertEqual(data['speed_4']['budget'],10)
        from src.spatial.walking_routing import grouped_opportunities
        from src.spatial.walking_network import RADII_M
        counts,_=grouped_opportunities(graph,origins,pois);self.assertEqual(counts[1][('food_social',RADII_M[0])],1)

class InferenceTests(unittest.TestCase):
    def test_wild_cluster_statistics_match_independent_brute_refits(self):
        rng=np.random.default_rng(17);groups=np.repeat(np.arange(11),20);X=np.column_stack([np.ones(len(groups)),rng.normal(size=len(groups)),rng.normal(size=len(groups))])
        y=X@np.array([1,.2,-.1])+np.repeat(rng.normal(size=11),20)+rng.normal(size=len(groups))
        repetitions=99;seed=44;result=wild_cluster_bootstrap_t(X,y,groups,repetitions,seed)
        observed=sm.OLS(y,X).fit(cov_type='cluster',cov_kwds={'groups':groups,'use_correction':True})
        restricted=sm.OLS(y,X[:,[0,2]]).fit();fitted=restricted.fittedvalues;u=restricted.resid
        webb=np.array([-np.sqrt(1.5),-1,-np.sqrt(.5),np.sqrt(.5),1,np.sqrt(1.5)])
        weights=np.random.default_rng(seed).choice(webb,size=(repetitions,11));statistics=[]
        for w in weights:
            fit=sm.OLS(fitted+u*w[groups],X).fit(cov_type='cluster',cov_kwds={'groups':groups,'use_correction':True})
            statistics.append(fit.tvalues[1])
        p=(1+np.sum(np.abs(statistics)>=abs(observed.tvalues[1])))/(repetitions+1)
        self.assertAlmostEqual(result.iloc[1].cluster_t_statistic,observed.tvalues[1],places=10)
        self.assertAlmostEqual(result.iloc[1].wild_cluster_p_value,p,places=10)
    def test_area_bootstrap_resamples_clusters_with_listing_weights(self):
        rows=[];id=0
        for area_index,area in enumerate(AREA_NAMES):
            for _ in range(area_index+2):
                id+=1
                for fs,shift in [('M0',0),('ME',.01),('MW',.02),('MEW',.03)]:
                    residual=.2+area_index*.01-shift
                    rows.append({'snapshot_date':'2000-01-01','listing_id':id,'analysis_area':area,'outer_fold':area,'scheme':'geographic_11','model':'XGBoost','feature_set':fs,'log_price':6.,'prediction':6.-residual,'residual':residual,'squared_error':residual**2,'absolute_error':abs(residual)})
        table=pd.DataFrame(rows);pooled,per_area,draws=paired_incremental(table,replications=99,seed=44)
        selected=draws.loc[(draws.added=='MW')&(draws.reference=='M0')].iloc[0]
        sampled=np.random.default_rng(44).integers(0,11,size=(99,11))[0]
        expanded=pd.concat([table.loc[(table.analysis_area==AREA_NAMES[g])&(table.feature_set.isin(['M0','MW']))] for g in sampled])
        expected=np.sqrt(expanded.loc[expanded.feature_set=='MW','squared_error'].mean())-np.sqrt(expanded.loc[expanded.feature_set=='M0','squared_error'].mean())
        self.assertAlmostEqual(selected.delta_rmse,expected)
        self.assertEqual(selected.resampled_listing_n,len(expanded)//2)
        self.assertEqual(len(draws),4*99);self.assertEqual(len(per_area),44)

class PathAndBusTests(unittest.TestCase):
    def test_semantic_paths_reject_traversal(self):
        for name in ['../secret.csv','/tmp/a.csv']:
            with self.assertRaises(ValueError):output_file('tables','primary_models',name)
        self.assertEqual(output_file('tables','primary_models','model_performance.csv').parts[-2:],('primary_models','model_performance.csv'))
    def test_bus_taxonomy_and_opposite_carriageway_consolidation(self):
        from src.pipeline.build_bus_euclidean_accessibility import selection_rule,consolidate
        self.assertIsNotNone(selection_rule({'public_transport':'stop_position','bus':'yes'}))
        self.assertIsNone(selection_rule({'public_transport':'platform','tram':'yes'}))
        stops=pd.DataFrame([
            dict(bus_stop_key='node/1',type='node',tags={'highway':'bus_stop','name':'A'},x=0,y=0,stop_areas=[1]),
            dict(bus_stop_key='node/2',type='node',tags={'public_transport':'stop_position','bus':'yes','name':'A'},x=5,y=0,stop_areas=[1]),
            dict(bus_stop_key='node/3',type='node',tags={'highway':'bus_stop','name':'A'},x=0,y=20,stop_areas=[1]),
            dict(bus_stop_key='node/4',type='node',tags={'public_transport':'stop_position','bus':'yes','name':'A'},x=5,y=20,stop_areas=[1]),
        ])
        result=consolidate(stops);mapping={r['bus_stop_key']:r['canonical_key'] for r in result}
        self.assertEqual(mapping['node/1'],mapping['node/2']);self.assertEqual(mapping['node/3'],mapping['node/4']);self.assertNotEqual(mapping['node/1'],mapping['node/3'])
    def test_conflicting_bus_refs_are_not_merged(self):
        from src.pipeline.build_bus_euclidean_accessibility import consolidate
        stops=pd.DataFrame([dict(bus_stop_key='node/1',type='node',tags={'name':'A','ref':'north'},x=0,y=0,stop_areas=[]),dict(bus_stop_key='node/2',type='node',tags={'name':'A','ref':'south'},x=0,y=0,stop_areas=[])])
        result=consolidate(stops)
        self.assertEqual(len({r['canonical_key'] for r in result}),2)
        stops['tags']=[{'ref':'north'},{'ref':'south'}]
        self.assertEqual(len({r['canonical_key'] for r in consolidate(stops)}),2)

class EvaluatorSmokeTest(unittest.TestCase):
    def test_all_feature_blocks_keep_paired_heldout_losses_and_equal_tuning_budget(self):
        from contextlib import contextmanager
        from src.pipeline.run_primary_models import evaluate_cv
        from src.pipeline.build_tuning_candidates import build
        # Verify the frozen candidates without exporting test files into outputs/.
        with patch('src.pipeline.build_tuning_candidates.write_json'):
            build()
        frame=synthetic_frame(n_per_area=8)
        fold,train,test=make_outer(frame)['geographic_11'][0]
        class MemoryEngine:
            @contextmanager
            def connect(self):yield None
            @contextmanager
            def begin(self):yield None
        captured={}
        def capture(conn,run,family,name,value):captured[name]=value
        with patch('src.pipeline.run_primary_models.persist',capture),patch('src.pipeline.run_primary_models.export'),patch('builtins.print'):
            output=evaluate_cv(frame,{'synthetic_geographic':[(fold,train,test)]},MemoryEngine(),'explicit_synthetic_test',saved_training=False)
        oof=output['oof_predictions'];tuning=output['xgboost_tuning'];shap=output['heldout_shap']
        self.assertEqual(len(oof),9*len(test));self.assertEqual(len(shap),4*len(test))
        self.assertEqual(set(tuning.feature_set),set(FEATURES));self.assertTrue(tuning.groupby('feature_set').size().eq(30).all())
        self.assertTrue(tuning.groupby('feature_set').selected.sum().eq(1).all())
        self.assertEqual(tuning.candidate_sha256.nunique(),1)
        self.assertFalse(set(oof.listing_id)&set(frame.iloc[train].listing_id))
        np.testing.assert_allclose(oof.squared_error,(oof.log_price-oof.prediction)**2)
        for _,row in shap.iterrows():self.assertAlmostEqual(row.base_value+sum(row.shap.values()),row.prediction,places=4)
        self.assertIn('preprocessing/synthetic_geographic/'+fold,captured)
