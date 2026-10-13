"""Synthetic A04 fixtures; no production source acquisition or listing export."""
import math
import unittest
from src.v4.context import gross_density, jsonstat_cells, join_context, load_policy
from src.v4.identity import scientific_dependencies
from src.v4.specification import DEFINITION_VERSION


def fixture():
    meta={'variables':[{'code':'Region','values':['0180R001_RegSO2025','0180R002_RegSO2025'],'valueTexts':['A','B']},
                       {'code':'ContentsCode','values':['mean','persons'],'valueTexts':['Mean','Persons']},
                       {'code':'Tid','values':['2024'],'valueTexts':['2024']}]}
    doc={'version':'2.0','class':'dataset','id':['Region','ContentsCode','Tid'],'size':[2,2,1],
         'dimension':{'Region':{'category':{'index':{'0180R001_RegSO2025':0,'0180R002_RegSO2025':1},'label':{'0180R001_RegSO2025':'A','0180R002_RegSO2025':'B'}}},
                      'ContentsCode':{'category':{'index':{'persons':0,'mean':1},'label':{'mean':'Mean','persons':'Persons'},'unit':{'mean':{'base':'tusentals kronor'},'persons':{'base':'antal'}}}},
                      'Tid':{'category':{'index':{'2024':0},'label':{'2024':'2024'}}}},'value':[10,200,20,None]}
    receipt={'selection':{'selected_codes':{'Region':['0180R001_RegSO2025','0180R002_RegSO2025'],'ContentsCode':['mean','persons'],'Tid':['2024']}}}
    return doc,meta,receipt


class ContextTests(unittest.TestCase):
    def test_native_id_measure_order_missingness_and_units(self):
        rows=jsonstat_cells(*fixture())
        self.assertEqual(rows[0]['keys']['ContentsCode'],'persons')
        self.assertEqual(rows[0]['unit'],'antal');self.assertEqual(rows[1]['unit'],'tusentals kronor')
        self.assertIsNone(rows[-1]['value']);self.assertEqual(len(rows),4)

    def test_native_measure_variation_and_missing_values_remain_separate(self):
        doc,meta,receipt=fixture();doc['value']=[10,200,20,350]
        cells=jsonstat_cells(doc,meta,receipt)
        for measure,expected in [('persons',{10,20}),('mean',{200,350})]:
            observed={r['value'] for r in cells if r['keys']['ContentsCode']==measure}
            self.assertEqual(observed,expected);self.assertGreater(len(observed),1)
        doc['value'][2]=None;doc['value'][3]=0
        cells=jsonstat_cells(doc,meta,receipt)
        self.assertIsNone(cells[2]['value']);self.assertEqual(cells[3]['value'],0)
        self.assertEqual({r['keys']['Tid'] for r in cells},{'2024'})
        self.assertEqual(len({tuple(sorted(r['keys'].items())) for r in cells}),4)

    def test_year_selector_label_units_and_schema_fail_closed(self):
        for mutation in ('year','label','units','schema','vector','nonfinite','duplicate'):
            doc,meta,receipt=fixture()
            if mutation=='year':receipt['selection']['selected_codes']['Tid']=['2025']
            if mutation=='label':doc['dimension']['Region']['category']['label']['0180R001_RegSO2025']='County 01'
            if mutation=='units':doc['dimension']['ContentsCode']['category'].pop('unit')
            if mutation=='schema':doc['id'].append('housing_price')
            if mutation=='vector':doc['value'].pop()
            if mutation=='nonfinite':doc['value'][0]=float('nan')
            if mutation=='duplicate':doc['dimension']['Region']['category']['index']=['0180R001_RegSO2025']*2
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):jsonstat_cells(doc,meta,receipt)

    def test_many_to_one_preserves_missing_ambiguous_outside_and_null_housing(self):
        areas=[{'area_id':'a','log_population_density':3.,'income_100k_dkk':4.}]
        rows=[{'listing_id':str(i),'area_id':'a','status':status,'inside_boundary':inside,'housing_area':None} for i,status,inside in [(1,'unique',True),(2,'unique',True),(3,'ambiguous',True),(4,'unique',False)]]
        actual=join_context(rows,areas);self.assertEqual(len(actual),4)
        self.assertEqual(actual[0]['log_population_density'],actual[1]['log_population_density'])
        self.assertIsNone(actual[2]['income_100k_dkk']);self.assertIsNone(actual[3]['area_id'])
        with self.assertRaises(ValueError):join_context(rows,areas*2)
        with self.assertRaises(ValueError):join_context(rows*2,areas)

    def test_gross_area_formula_water_not_removed_and_crs(self):
        self.assertAlmostEqual(gross_density(100,2e6,'EPSG:3006'),math.log(50))
        self.assertIsNone(gross_density(None,2e6,'EPSG:25833'))
        for pop,area,crs in [(0,2e6,'EPSG:3006'),(100,0,'EPSG:3006'),(100,2e6,'EPSG:4326')]:
            with self.assertRaises(ValueError):gross_density(pop,area,crs)

    def test_policy_source_vs_join_state_and_unchanged_income_mode(self):
        policy=load_policy()
        self.assertEqual(policy['design_id'],DEFINITION_VERSION)
        self.assertEqual(policy['income_mode'],'QUALIFIED_INCOME_PRIMARY_WITH_MATCHED_NO_INCOME_SENSITIVITY')
        for city in ['oslo','stockholm']:
            self.assertFalse(policy['cities'][city]['context_join_allowed'])
            ids={r['record']['source_id'] for r in policy['cities'][city]['sources']}
            self.assertIn('a04_20261011_population_data',ids);self.assertIn('a04_20261011_income_data',ids)
        self.assertIsNone(policy['cities']['stockholm']['anchor'])
        self.assertEqual(policy['cities']['oslo']['anchor']['source_crs'],'EPSG:4258')

    def test_context_provenance_scientific_hash_not_documentation(self):
        for city in ['oslo','stockholm','copenhagen_frederiksberg']:
            deps=scientific_dependencies(city)
            self.assertIn('context_qualification',deps['listing_source_policy'])
            self.assertIn('src/v4/context.py',deps['code_and_environment'])
            self.assertFalse(any(p.endswith('.md') for p in deps['code_and_environment']))
