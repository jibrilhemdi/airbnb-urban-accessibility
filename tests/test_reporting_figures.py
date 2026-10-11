"""Publication privacy and frozen-result lineage checks."""
import unittest
import numpy as np
import pandas as pd
from src.pipeline.reporting_figures import grid_summary, join_features
from src.pipeline.render_reporting_figures import scientific_dependency_guard

class ReportingIntegrityTests(unittest.TestCase):
    def test_cell_suppression_counts_observed_values(self):
        frame=pd.DataFrame({'metric_x':[1]*6+[501]*5,'metric_y':[1]*11,'price':[1,2,3,4,np.nan,np.nan,1,2,3,4,5]})
        result=grid_summary(frame,'price')
        self.assertEqual(len(result),1)
        self.assertEqual(result.iloc[0].gx,1)
        self.assertEqual(result.iloc[0].n,5)
        self.assertEqual(result.iloc[0].value,3)
        self.assertEqual(frame.price.isna().sum(),2)

    def test_snapshot_normalisation_retains_every_observation(self):
        frame=pd.DataFrame({'snapshot_date':['2026-06-30T00:00:00.000']*2,'listing_id':[1,2],'value':[4,5]})
        heldout=pd.DataFrame({'snapshot_date':['2026-06-30']*2,'listing_id':[2,1],'shap':[.2,.1]})
        joined=join_features(heldout,frame)
        self.assertEqual(joined.value.tolist(),[5,4])
        with self.assertRaises(ValueError):join_features(heldout.iloc[:1],frame)
        with self.assertRaises(pd.errors.MergeError):join_features(pd.concat([heldout,heldout.iloc[:1]]),frame)

    def test_only_presentation_dependencies_may_change(self):
        original={'input_manifest_sha256':'raw','design_sha256':'design','source_sha256':{'src/pipeline/run_primary_models.py':'model','src/pipeline/build_final_outputs.py':'old'}}
        current={**original,'source_sha256':{**original['source_sha256'],'src/pipeline/build_final_outputs.py':'new','src/pipeline/reporting_figures.py':'plot'}}
        self.assertEqual(len(scientific_dependency_guard(original,current)),2)
        changed={**current,'source_sha256':{**current['source_sha256'],'src/pipeline/run_primary_models.py':'changed'}}
        with self.assertRaises(RuntimeError):scientific_dependency_guard(original,changed)
        with self.assertRaises(RuntimeError):scientific_dependency_guard(original,{**current,'design_sha256':'changed'})

class CatchmentReachabilityTests(unittest.TestCase):
    def test_budget_includes_stored_destination_connector(self):
        from src.pipeline.reporting_figures import poi_reachability
        pois=pd.DataFrame({'snapped_node_id':[1,2,3,4],'snap_distance_m':[100,100,0,0]})
        result=poi_reachability(pois,{1:700,2:750,4:800},800)
        self.assertEqual(result.tolist(),[True,False,False,True])

    def test_missing_routing_evidence_is_not_classified_as_unreachable(self):
        from src.pipeline.reporting_figures import poi_reachability
        for variable in ['snapped_node_id','snap_distance_m']:
            pois=pd.DataFrame({'snapped_node_id':[1],'snap_distance_m':[20]})
            pois[variable]=np.nan
            with self.assertRaises(ValueError):poi_reachability(pois,{1:10},800)
