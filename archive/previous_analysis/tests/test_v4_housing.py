"""Synthetic source fixtures only: no empirical housing values or production writes."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from src.v4.housing import (annual_mean, bm_metadata, bm_csv, bol018, jsonstat_cells,
                            number, oslo_geography, standalone_gates, load_policy, collect)
from src.v4.identity import Paths, Scope
from src.v4.listings import acquire


def dataset():
    labels = {'ContentsCode': {'content':'eliminated'}, 'år':{'7':'2025'},
              'geografi':{'42':'10201'}, 'boligtype':{'1':'Blokkleilighet'},
              'statistikkvariabel':{'0':'Antall salg','1':'Gjennomsnitt antall kvadratmeter','2':'Gjennomsnitt kvadratmeterpris'}}
    return {'class':'dataset','version':'2.0','id':list(labels),'size':[1,1,1,1,3],
            'dimension':{k:{'category':{'index':{v:i for i,v in enumerate(values)},'label':values}} for k,values in labels.items()},
            'value':[25,70,10000],'status':{}}


class HousingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.paths=Paths(Scope('research_design_v4','oslo','2026-06-30','synthetic_v4_oslo_20261011T000000Z','synthetic'),self.root)

    def test_numeric_locale_units_suppression_and_zero_are_explicit(self):
        self.assertEqual(number('12.345,50',locale='danish_display'),12345.5)
        self.assertEqual(number('12345.50'),12345.5)
        self.assertEqual(number('0',count=True),0)
        for v in ('..','...',':','-',None,''):self.assertIsNone(number(v))
        for v in ('NaN','inf','-1','1,234','1 234',True):
            with self.subTest(v=v),self.assertRaises(ValueError):number(v)
        with self.assertRaises(ValueError):number('1.5',count=True)
        with self.assertRaises(ValueError):number('12',locale='guess')

    def test_annual_aggregation_requires_exact_denominators_not_medians(self):
        quarters=[{'period':'2025K'+str(i),'price_m2_native':i*100,'sale_count':i*10} for i in range(1,5)]
        self.assertEqual(annual_mean(quarters,statistic='arithmetic_mean',same_sample_denominators_verified=True),300)
        for statistic, proof in [('median',True),('arithmetic_mean',False)]:
            with self.assertRaises(ValueError):annual_mean(quarters,statistic=statistic,same_sample_denominators_verified=proof)
        for changed in (quarters[:3],quarters+[quarters[0]],[{**r,'period':'2026K1'} for r in quarters],
                        [{**r,'price_m2_native':None} for r in quarters],[{**r,'sale_count':None} for r in quarters]):
            with self.assertRaises(ValueError):annual_mean(changed,statistic='arithmetic_mean',same_sample_denominators_verified=True)

    def test_bm_actual_no_header_export_has_verified_native_ids_and_quarter_order(self):
        p=self.root/'metadata.html';p.write_text('<select name="var1"><option value="1800">1800-1999 Frederiksberg C</option></select>'
        '<select name="var2"><option value="2">Ejerlejlighed</option></select><select name="var3"><option value="REAL">Realiseret handelspris</option></select>'
        '<select name="var4">'+''.join('<option value="2025K'+str(i)+'">2025K'+str(i)+'</option>' for i in range(1,5))+'</select>')
        m=bm_metadata(p);html=self.root/'query.html';html.write_text('<table id="pxtable"><tr><td>Title</td></tr><tr><th></th>'+''.join('<th>2025K'+str(i)+'</th>' for i in range(1,5))+'</tr></table>')
        csv=self.root/'values.csv';csv.write_text('Realiseret handelspris;Ejerlejlighed;1800-1999 Frederiksberg C;100;..;0;400\n')
        parsed=bm_csv(csv,m,html,measure='Realiseret handelspris');self.assertEqual(parsed[('1800','2025K1')],100)
        self.assertIsNone(parsed[('1800','2025K2')]);self.assertEqual(parsed[('1800','2025K3')],0)
        csv.write_text(csv.read_text()*2)
        with self.assertRaisesRegex(ValueError,'Duplicate'):bm_csv(csv,m,html,measure='Realiseret handelspris')
        csv.write_text('Realiseret handelspris;Ejerlejlighed;unknown;100;200;300;400\n')
        with self.assertRaises(ValueError):bm_csv(csv,m,html,measure='Realiseret handelspris')
        html.write_text(html.read_text().replace('2025K4','2026K1'))
        with self.assertRaises(ValueError):bm_csv(csv,m,html,measure='Realiseret handelspris')

    def test_jsonstat_schema_dimensions_duplicates_sparse_missing_and_flags(self):
        d=dataset();self.assertEqual(len(jsonstat_cells(d)),3)
        d['value']={'0':25,'2':10000};self.assertIsNone(jsonstat_cells(d)[1][1])
        for mutate in (lambda x:x.update(value=[1]),lambda x:x.update(size=[1,1,1,1,0]),
                       lambda x:x['dimension']['statistikkvariabel']['category']['index'].update({'2':1}),
                       lambda x:x.update(status={'2':'-' }),lambda x:x.update(version='1.0')):
            bad=dataset();mutate(bad)
            with self.assertRaises(ValueError):jsonstat_cells(bad)

    def test_bol018_api_positions_not_native_area_ids_and_revisions_not_mixed(self):
        d=dataset();m={'title':'BOL018 synthetic','variables':[{'code':k,'values':list(v['category']['label']),
           'valueTexts':list(v['category']['label'].values())} for k,v in d['dimension'].items() if k!='ContentsCode']}
        rows=bol018(d,m,{'10201':('grunnkretsomrade','Synthetic')},'fixture');self.assertEqual(rows[0]['source_area_id'],'10201')
        self.assertEqual(rows[0]['api_geography_code'],'42');self.assertEqual(rows[0]['unit'],'NOK/m2')
        self.assertTrue(rows[0]['native_housing_join_pending'])
        d['value']=[0,None,None];d['status']={'1':'-','2':'-'}
        r=bol018(d,m,{},'fixture')[0];self.assertIsNone(r['price_m2_native']);self.assertEqual(r['sale_count'],0)
        self.assertEqual(r['geography_level'],'unresolved_native_geography')
        with self.assertRaises(ValueError):bol018(d,{**m,'title':'BOL012 old standard'}, {},'fixture')

    def test_hierarchy_uses_actual_source_columns_not_geocode_digit_guessing(self):
        p=self.root/'geo.xlsx';pd.DataFrame([{'Bydel_nr':'1','Bydel_navn':'B','Delbydel_2017_nr':'102','Delbydel_2017_navn':'D',
                                            'Grunnkretsområde_nr':'10201','Grunnkretsområde_navn':'G'}]).to_excel(p,index=False,sheet_name='Sheet1')
        self.assertEqual(oslo_geography(p)['10201'],('grunnkretsomrade','G'))
        pd.DataFrame([{'guessed':'code'}]).to_excel(p,index=False,sheet_name='Sheet1')
        with self.assertRaises(ValueError):oslo_geography(p)

    def test_source_qa_never_certifies_joined_sample_or_boundary(self):
        rows=[dict(source_area_id=str(i),geography_level='fixture',price_m2_native=10000+i,sale_count=20,annual=True) for i in range(10)]
        args=dict(legal_reuse_verified=True,annual_measure_verified=True,geography_definitions_verified=True,boundary_provisional=True)
        g=standalone_gates(rows,**args);self.assertEqual(g['preliminary_qa_status'],'PRELIMINARY_QA_PASSED')
        self.assertEqual(g['spatial_status'],'PROVISIONAL_BOUNDARY');self.assertEqual(g['final_qualification'],'BLOCKED')
        self.assertIsNone(g['listing_housing_coverage']);self.assertFalse(g['listing_H_assigned'])
        for changed in (rows[:9],[{**r,'price_m2_native':0} for r in rows],[{**r,'price_m2_native':10000} for r in rows],
                        [{**r,'sale_count':19} for r in rows],[{**r,'annual':False} for r in rows]):
            self.assertEqual(standalone_gates(changed,**args)['preliminary_qa_status'],'BLOCKED')
        self.assertEqual(standalone_gates(rows,**{**args,'legal_reuse_verified':False})['preliminary_qa_status'],'BLOCKED')

    def test_public_query_receipt_is_immutable_and_changed_query_fails_before_network(self):
        class Response:
            status=200;url='https://example.org/public';headers={}
            def read(self):return b'{"class":"dataset"}'
            def __enter__(self):return self
            def __exit__(self,*args):pass
        args=dict(extent='synthetic',licence='fixture',reference_period='2025',selection={'fixture':True})
        with patch('src.v4.listings.urlopen',return_value=Response()) as network:
            first=acquire(self.paths,'fixture','query.json','https://example.org/public',request_json={'year':'2025'},**args)
            self.assertEqual(acquire(self.paths,'fixture','query.json','https://example.org/public',request_json={'year':'2025'},**args),first)
            with self.assertRaisesRegex(ValueError,'query mismatch'):
                acquire(self.paths,'fixture','query.json','https://example.org/public',request_json={'year':'2026'},**args)
            self.assertEqual(network.call_count,1)

    def test_changed_source_receipt_or_safeguards_fail_closed(self):
        p=load_policy();bad=deepcopy(p);bad['safeguards']['minimum_usable_areas']=1
        target=self.root/'policy.json';target.write_text(json.dumps(bad))
        with patch('src.v4.housing.POLICY',target),self.assertRaises(ValueError):load_policy()
        entry=p['cities']['oslo']['sources'][0]
        with patch('src.v4.housing.acquire',return_value={'status':'acquired','sha256':'wrong'}):
            with self.assertRaises((ValueError,FileNotFoundError)):collect(self.paths,p)

    def test_safe_export_schema_has_no_listing_data_or_price_rows(self):
        from src.v4.housing import evidence
        class Result:
            def mappings(self):return self
            def one(self):return {'summary':{'parsed_rows':1,'status':'BLOCKED','raw_private':'never export'},'manifest_sha256':'a'*64}
        class Connection:
            def execute(self,*args):return Result()
            def scalar(self,stmt,params=None):
                return {'records':[{'source_id':'fixture','raw_private':'do not export'}]} if 'manifest FROM' in str(stmt) else 1
        with patch('src.v4.housing.verify_database'):
            result=evidence(Connection(),self.paths)
        self.assertNotIn('record',result);self.assertNotIn('raw_private',result);self.assertNotIn('raw_private',result['sources'][0])
