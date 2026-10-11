"""Recovery cannot bypass design drift, partial components or scientific errors."""
import copy
import unittest
from src.pipeline.run_pipeline import DEPENDENCIES,resume_metadata

class RecoveryTests(unittest.TestCase):
    def fixture(self):
        deps={'input_manifest_sha256':'raw','design_sha256':'design','source_sha256':{'src/pipeline/run_pipeline.py':'old','config/research_design.json':'frozen'}}
        previous={'status':'failed','error':'Object of type date is not JSON serializable','dependencies':deps,
            'component_results':{name:{} for name,_,_ in DEPENDENCIES[:10]}}
        current=copy.deepcopy(deps);current['source_sha256']['src/pipeline/run_pipeline.py']='new'
        return previous,current
    def test_metadata_repair_retains_completed_components_and_old_dependencies(self):
        previous,current=self.fixture();result=resume_metadata(previous,current)
        self.assertEqual(result['status'],'running');self.assertEqual(result['component_results'],previous['component_results'])
        self.assertEqual(result['initial_dependencies'],previous['dependencies'])
        self.assertEqual(result['dependencies'],current);self.assertEqual(len(result['recovery_events']),1)
        self.assertEqual(previous['status'],'failed')
    def test_scientific_failure_cannot_resume(self):
        previous,current=self.fixture();previous['error']='OLS material missingness'
        with self.assertRaises(RuntimeError):resume_metadata(previous,current)
    def test_configuration_input_and_other_code_drift_cannot_resume(self):
        for path in ['raw','design','other_source']:
            previous,current=self.fixture()
            if path=='raw':current['input_manifest_sha256']='changed'
            elif path=='design':current['design_sha256']='changed'
            else:current['source_sha256']['other.py']='added'
            with self.subTest(path=path),self.assertRaises(RuntimeError):resume_metadata(previous,current)
    def test_nonprefix_component_records_cannot_resume(self):
        previous,current=self.fixture();previous['component_results'].pop('core_bus_walking')
        with self.assertRaises(RuntimeError):resume_metadata(previous,current)
    def test_spatial_join_recovery_is_limited_to_its_recorded_prefix_and_files(self):
        previous,current=self.fixture();previous['error']='Expected more than k projected two-dimensional points'
        previous['component_results']={name:{} for name,_,_ in DEPENDENCIES[:17]}
        previous['dependencies']['source_sha256']['src/pipeline/run_spatial_diagnostics.py']='old'
        current['source_sha256']['src/pipeline/run_spatial_diagnostics.py']='new'
        self.assertEqual(resume_metadata(previous,current)['status'],'running')
        current['source_sha256']['src/pipeline/run_primary_models.py']='changed'
        with self.assertRaises(RuntimeError):resume_metadata(previous,current)

if __name__=='__main__':unittest.main()
