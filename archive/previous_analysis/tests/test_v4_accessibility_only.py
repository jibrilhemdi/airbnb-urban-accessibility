"""A02 synthetic scope/registry checks; no research samples, routing or fits."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.ingestion.common import PROJECT_ROOT
from src.pipeline.model_specification import FEATURES as V3_FEATURES
from src.pipeline.protocol import canonical_hash
from src.v4.cities import VERSION, city_blockers, load_cities
from src.v4.identity import Paths, Scope, scientific_dependencies
from src.v4.readiness import REQUIRED_QUALIFICATIONS, scope_check
from src.v4.runtime import preflight
from src.v4.specification import (DEFINITION_VERSION, HISTORICAL_VERSION, INHERITED_BLOCKS,
                                   PRIMARY_BLOCKS, load_design, model_definition, validate_definition)
from test_v4_architecture import scope


def qualified_fixture():
    features = model_definition('MEW')['features']
    frame = pd.DataFrame({f: [1., 2.] for f in features})
    frame['property_type'] = ['Entire rental unit', 'Entire condo']
    frame['listing_id'] = ['synthetic_a', 'synthetic_b']
    frame['price_nightly'] = [100., 200.]
    frame['log_price'] = np.log(frame['price_nightly'])
    frame['inside_boundary'] = True
    frame['official_analysis_area_id'] = ['synthetic_area_a', 'synthetic_area_b']
    frame['native_housing_area_id'] = None
    return frame, {k: True for k in REQUIRED_QUALIFICATIONS}


class AccessibilityRegistryTests(unittest.TestCase):
    def test_exact_primary_and_no_income_membership_inherit_v3(self):
        design=load_design()
        self.assertEqual(design['blocks'],INHERITED_BLOCKS)
        self.assertEqual(set(design['primary_models']),set(PRIMARY_BLOCKS))
        for name,blocks in PRIMARY_BLOCKS.items():
            primary=model_definition(name)
            self.assertEqual(primary['features'],tuple(f for b in blocks for f in INHERITED_BLOCKS[b]))
            self.assertEqual(set(primary['features']),set(V3_FEATURES[name]))
            self.assertEqual(primary['design_id'],DEFINITION_VERSION)
            self.assertEqual(primary['definition_id'],DEFINITION_VERSION+':'+name)
            self.assertEqual(primary['scenario'],'primary')
            sensitivity=model_definition(name,scenario='no_income')
            self.assertEqual(sensitivity['features'],tuple(f for f in primary['features'] if f!='income_100k_dkk'))
            self.assertEqual(sensitivity['definition_id'],DEFINITION_VERSION+':no_income:'+name)
            historical=model_definition(name,design_id=HISTORICAL_VERSION)
            self.assertIn('housing_context_midrank',historical['features'])
            self.assertNotEqual(primary['definition_id'],historical['definition_id'])
        self.assertEqual(len([f for f in INHERITED_BLOCKS['X'] if f.startswith('amenity_')]),8)

    def test_proxies_extra_models_variants_and_definition_overrides_rejected(self):
        for proxy in ['housing_context_midrank','housing_price_m2_native','log_housing_price_m2_native','residential_rent','rent_proxy']:
            design=load_design();design['blocks']['X'].append(proxy)
            with self.subTest(proxy=proxy),self.assertRaises(ValueError):validate_definition(design)
        for scenario in ['no_housing','log_native_housing']:
            with self.assertRaises(ValueError):model_definition('M0',scenario=scenario)
        for name in ['M0_H','M0_no_income','M1']:
            with self.assertRaises(ValueError):model_definition(name)
        for mutate in [lambda d:d.update(design_id=HISTORICAL_VERSION),
                       lambda d:d['primary_models']['M0'].update(definition_id='M0'),
                       lambda d:d['blocks']['X'].remove('property_type'),
                       lambda d:d['blocks']['X'].remove('log_population_density'),
                       lambda d:d.update(housing={'required':False}),
                       lambda d:d['no_income_sensitivity'].update(mandatory=False)]:
            design=load_design();mutate(design)
            with self.assertRaises(ValueError):validate_definition(design)

    def test_frozen_candidates_thresholds_and_source_policy_preserved(self):
        active=load_design();historical=load_design(design_id=HISTORICAL_VERSION)
        for key in ['inherited_safeguards','additional_inherited_safeguards','income','comparisons']:
            self.assertEqual(active[key],historical[key])
        for key in ['candidates','candidates_sha256','search_space','candidate_seed','candidate_count']:
            self.assertEqual(active['tuning'][key],historical['tuning'][key])
        self.assertEqual(active['no_income_sensitivity']['material_change_rules'],historical['no_income_sensitivity']['material_change_rules'])
        self.assertNotIn('housing_missingness',active['samples'])
        self.assertIn('union_X_E_W',active['samples']['ols_association'])
        self.assertEqual(len(active['research_questions']),3)


class HousingFreeScopeTests(unittest.TestCase):
    def test_null_housing_and_no_housing_files_pass_without_filtering(self):
        frame,qualified=qualified_fixture();original=frame.copy(deep=True)
        with tempfile.TemporaryDirectory() as root:
            self.assertFalse(list(Path(root).rglob('*')))
            result=scope_check(frame,qualifications=qualified)
        self.assertEqual(result['status'],'SCOPE_CHECK_PASSED')
        self.assertEqual(result['rows_checked'],2);self.assertEqual(result['rows_removed'],0)
        pd.testing.assert_frame_equal(frame,original)
        frame=frame.drop(columns=['native_housing_area_id'])
        self.assertEqual(scope_check(frame,qualifications=qualified)['status'],'SCOPE_CHECK_PASSED')

    def test_invalid_airbnb_prices_still_block_and_are_never_filled(self):
        for value in [None,0,-1,float('inf'),'bad']:
            frame,qualified=qualified_fixture();frame['price_nightly']=frame['price_nightly'].astype(object)
            frame.loc[0,'price_nightly']=value
            result=scope_check(frame,qualifications=qualified)
            self.assertEqual(result['status'],'BLOCKED')
            self.assertTrue(any('Airbnb outcome' in b for b in result['blockers']))
            self.assertEqual(result['rows_removed'],0)
        frame,qualified=qualified_fixture();frame.loc[0,'log_price']=0.
        self.assertEqual(scope_check(frame,qualifications=qualified)['status'],'BLOCKED')

    def test_unresolved_geography_context_and_required_features_still_block(self):
        for gate in REQUIRED_QUALIFICATIONS:
            frame,qualified=qualified_fixture();qualified[gate]=False
            self.assertEqual(scope_check(frame,qualifications=qualified)['status'],'BLOCKED')
        for name,value in [('official_analysis_area_id',None),('inside_boundary',None),('inside_boundary',False),
                           ('income_100k_dkk',None),('log_population_density',float('inf')),('nearest_bus_walking_minutes',None)]:
            frame,qualified=qualified_fixture();frame[name]=value
            self.assertEqual(scope_check(frame,qualifications=qualified)['status'],'BLOCKED')
        frame,qualified=qualified_fixture();frame.loc[1,'listing_id']=frame.loc[0,'listing_id']
        self.assertEqual(scope_check(frame,qualifications=qualified)['status'],'BLOCKED')

    def test_geographic_gates_survive_city_scope_amendment(self):
        self.assertEqual(city_blockers(VERSION,'copenhagen_frederiksberg'),[])
        for city in ['oslo','stockholm']:
            blockers=city_blockers(VERSION,city)
            self.assertTrue(blockers)
            self.assertFalse(any('housing' in b for b in blockers))
            self.assertIn('context_mapping: unresolved/unqualified',blockers)
        self.assertIn('study_boundary: unresolved/unqualified',city_blockers(VERSION,'oslo'))
        self.assertIn('housing: unresolved/unqualified',city_blockers(VERSION,'copenhagen_frederiksberg',design_id=HISTORICAL_VERSION))
        result=preflight(scope(purpose='research'),offline=True)
        self.assertEqual(result['status'],'BLOCKED');self.assertEqual(result['mutations'],0)
        self.assertFalse(result['research_executed'])


class ActiveDependencyIsolationTests(unittest.TestCase):
    def test_historical_acquisition_envelope_and_path_are_unchanged(self):
        old=Scope(VERSION,'oslo','2026-06-30','synthetic_v4_oslo_20261011T120000Z','synthetic')
        self.assertEqual(old.design_id,HISTORICAL_VERSION)
        self.assertEqual(old.params(),{'version':VERSION,'city':'oslo','snapshot':'2026-06-30',
                                      'run_id':old.run_id,'purpose':'synthetic'})
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(Paths(old,Path(root)).report('audit.json'),
                             Path(root).resolve()/'reports/v4'/VERSION/old.run_id/'oslo/2026-06-30/audit.json')

    def test_source_paths_reused_but_outputs_and_cache_separate_by_design(self):
        with tempfile.TemporaryDirectory() as root:
            new=Paths(scope(),Path(root));old=Paths(scope(design_id=HISTORICAL_VERSION),Path(root))
            self.assertEqual(new.source('fixture','listing.gz'),old.source('fixture','listing.gz'))
            self.assertNotEqual(new.intermediate('features.json'),old.intermediate('features.json'))
            self.assertNotEqual(new.output('tables','reporting','metrics.csv'),old.output('tables','reporting','metrics.csv'))
            self.assertNotEqual(new.report('audit.json'),old.report('audit.json'))
            dependencies={'scientific_sha256':'a'*64,'source_manifests':{},'boundary_sha256':'b'*64,
                          'metric_crs':'synthetic','network_sha256':'c'*64,'taxonomy_sha256':'d'*64,
                          'routing_parameters':{},'software':{}}
            self.assertNotEqual(new.cache(dependencies),old.cache(dependencies))

    def test_housing_files_and_policies_absent_from_new_scientific_hash(self):
        science=scientific_dependencies('oslo')
        self.assertNotIn('housing_sources',science['listing_source_policy'])
        for path in ['src/v4/housing.py','src/v4/historical_specification.py','sql/v4_migrations/025_v4_housing_source_audit.sql']:
            self.assertNotIn(path,science['code_and_environment'])
        original_read=Path.read_text;original_exists=Path.is_file
        def read(path,*args,**kwargs):
            if path.name=='housing_sources.json':raise AssertionError('Active design tried to read housing policy')
            return original_read(path,*args,**kwargs)
        def exists(path):
            return False if path.name in {'housing_sources.json','housing.py'} else original_exists(path)
        with patch.object(Path,'read_text',read),patch.object(Path,'is_file',exists):
            self.assertEqual(science,scientific_dependencies('oslo'))
        self.assertIn('housing_sources',scientific_dependencies('oslo',design_id=HISTORICAL_VERSION)['listing_source_policy'])
        changed=load_design();changed['status']='only reporting';changed['provenance']['commit']='new'
        self.assertEqual(science,scientific_dependencies('oslo',design=changed))
        changed=load_cities();changed['cities']['stockholm']['currency']['value']='fixture'
        self.assertEqual(science,scientific_dependencies('oslo',cities=changed))
        changed['cities']['oslo']['context_mapping']['value']=[{'changed':True}]
        self.assertNotEqual(canonical_hash(science),canonical_hash(scientific_dependencies('oslo',cities=changed)))


if __name__=='__main__':unittest.main()
