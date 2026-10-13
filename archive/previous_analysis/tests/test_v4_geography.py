"""Synthetic A03 fixtures only; no production sources/namespaces/database writes."""
import copy
import unittest
from shapely.geometry import Polygon, mapping
from src.v4.geography import (polygon, declared_crs, oslo_municipality, oslo_areas,
                              spatial_audit, load_policy, DEFINITION)
from src.v4.specification import DEFINITION_VERSION


def square(left=0, right=0.01):
    return Polygon([(left,0),(right,0),(right,0.01),(left,0.01)])


def area(name, geom, municipality=None):
    return {'area_id': name, 'native_id': name, 'name': name, 'geom': geom,
            'source_crs': 'EPSG:4326', **({'municipality':municipality} if municipality else {})}


def listing(key='1', x=0.005, y=0.005, positive=True):
    return {'listing_id':key,'longitude':x,'latitude':y,'dwelling_eligible':True,'positive_price':positive}


class V4GeographyTests(unittest.TestCase):
    def test_polygon_crs_and_topology_fail_closed(self):
        for geom in [Polygon([(0,0),(1,1),(0,1),(1,0)]), Polygon()]:
            with self.assertRaises(ValueError):polygon(mapping(geom),4326,25833)
        with self.assertRaises(ValueError):polygon(mapping(square()),4326,4326)
        for doc in [{},{'crs':{'properties':{'name':'EPSG:3857'}}}]:
            with self.assertRaises(ValueError):declared_crs(doc,25833)

    def test_strict_covers_ties_and_gaps_remain_unresolved(self):
        a,b=area('a',square(0,0.004)),area('b',square(0.004,0.008))
        rows=[listing('1',x=0.002),listing('2',x=0.004),listing('3',x=0.009),listing('4',x=0.02)]
        summary,records=spatial_audit(rows,square(),[b,a],'EPSG:3857')
        self.assertEqual([r['status'] for r in records],['unique','ambiguous','unmatched','outside_boundary'])
        self.assertEqual(records[1]['candidates'],['a','b']);self.assertIsNone(records[1]['area_id'])
        self.assertGreater(summary['coverage']['mask_uncovered_m2'],0)
        self.assertFalse(summary['fold_memberships_frozen'])

    def test_overlap_detected_not_silently_repaired(self):
        summary,records=spatial_audit([listing()],square(),[area('a',square()),area('b',square())],'EPSG:3857')
        self.assertGreater(summary['coverage']['summed_overlap_m2'],0)
        self.assertEqual(records[0]['status'],'ambiguous')

    def test_price_free_support_and_missing_outcome_retention(self):
        rows=[listing(),listing('2',positive=False)]
        first,_=spatial_audit(rows,square(),[area('a',square())],'EPSG:3857')
        for r in rows:r.update(price_nightly=999999,log_price=-100,native_housing_area_id=None)
        second,records=spatial_audit(rows,square(),[area('a',square())],'EPSG:3857')
        self.assertEqual(first,second);self.assertEqual(len(records),2)
        self.assertEqual(second['areas'][0]['listing_support']['raw'],2)
        self.assertEqual(second['areas'][0]['proposed_holdout_positive'],1)
        self.assertFalse(second['areas'][0]['count_safeguard_met'])
        self.assertFalse(second['housing_required'])

    def test_invalid_coordinates_not_outside_zero_or_imputed(self):
        summary,records=spatial_audit([listing(x=None)],square(),[],'EPSG:3857')
        self.assertEqual(summary['counts']['invalid_coordinates'],1)
        self.assertIsNone(records[0]['inside_boundary']);self.assertIsNone(summary['native_area_count'])
        self.assertNotIn('outside_raw',summary['counts'])

    def test_duplicates_fail_and_municipality_compatibility_is_required(self):
        with self.assertRaises(ValueError):spatial_audit([listing(),listing()],square(),[],'EPSG:3857')
        with self.assertRaises(ValueError):spatial_audit([],square(),[area('a',square()),area('a',square())],'EPSG:3857')
        _,records=spatial_audit([listing()],square(),[area('a',square(),municipality='0101')],'EPSG:3857',municipalities={'0147':square()})
        self.assertEqual(records[0]['status'],'municipality_mismatch_or_tie');self.assertIsNone(records[0]['area_id'])

    def test_outer_boundary_diagnostic_excludes_holes(self):
        mask=Polygon(square(0,0.05).exterior.coords,[[(.02,.002),(.03,.002),(.03,.008),(.02,.008)]])
        _,records=spatial_audit([listing(x=.019,y=.005)],mask,[],'EPSG:3857')
        self.assertFalse(records[0]['near_outer_150m'])

    def test_oslo_code_schema_and_intentional_marka_components(self):
        doc={'crs':{'properties':{'name':'EPSG:25833'}},'features':[]}
        for fid,(code,x) in enumerate([('01',250000),('17',251000),('17',252000)]):
            g=Polygon([(x,6600000),(x+500,6600000),(x+500,6600500),(x,6600500)])
            doc['features'].append({'properties':{'kommunenum':'0301','BYDEL':code,'FID':fid},'geometry':mapping(g)})
        names={'01':'Fixture 1','17':'Fixture Marka'}
        actual=oslo_areas(doc,names);self.assertEqual(actual[1]['components'],2)
        for field,value in [('kommunenum','01'),('BYDEL','99'),('FID',1)]:
            bad=copy.deepcopy(doc);bad['features'][0]['properties'][field]=value
            with self.assertRaises(ValueError):oslo_areas(bad,names)
        bad=copy.deepcopy(doc);bad['features'].pop()
        with self.assertRaises(ValueError):oslo_areas(bad,names)
        municipal={'crs':doc['crs'],'features':[{'properties':{'objtype':'Kommune','kommunenummer':'0301'},'geometry':doc['features'][0]['geometry']}]}
        self.assertEqual(oslo_municipality(municipal)['properties']['kommunenummer'],'0301')
        municipal['features'][0]['properties']['kommunenummer']='0302'
        with self.assertRaises(ValueError):oslo_municipality(municipal)

    def test_separate_city_policy_preserves_genuine_blocks(self):
        policy=load_policy();self.assertEqual(policy['design_id'],DEFINITION_VERSION)
        self.assertEqual(policy['definition_version'],DEFINITION)
        self.assertEqual(policy['cities']['oslo']['metric_crs'],'EPSG:25833')
        self.assertEqual(policy['cities']['stockholm']['metric_crs'],'EPSG:3006')
        self.assertEqual(policy['cities']['stockholm']['analysis_status'],'BLOCKED')
        self.assertEqual(policy['cities']['oslo']['analysis_status'],'BLOCKED')
        self.assertEqual(policy['cities']['copenhagen_frederiksberg']['analysis_status'],'QUALIFIED_INHERITED_OPERATIONAL')

    def test_amendment_is_narrow_and_keeps_context_and_support_gates(self):
        from src.v4.geography import apply_geography_amendment, OSLO_VINTAGE_WARNING
        old=[OSLO_VINTAGE_WARNING,'study_boundary: unresolved/unqualified','metric_crs: unresolved/unqualified',
             'context_mapping: unresolved/unqualified','V4 sample/fold blocked','invalid original price']
        summary={'city':'oslo','mask_status':'RESOLVED_WITH_DOCUMENTED_SOURCE_AMENDMENT','blockers':['Marka support blocked']}
        revised=apply_geography_amendment(old,summary)
        self.assertNotIn(OSLO_VINTAGE_WARNING,revised)
        self.assertIn('context_mapping: unresolved/unqualified',revised)
        self.assertIn('V4 sample/fold blocked',revised);self.assertIn('invalid original price',revised)
        self.assertIn('A03 geography: Marka support blocked',revised)
        summary['mask_status']='BLOCKED';self.assertIn(OSLO_VINTAGE_WARNING,apply_geography_amendment(old,summary))
