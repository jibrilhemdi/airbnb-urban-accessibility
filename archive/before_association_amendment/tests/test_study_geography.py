import unittest
from shapely.geometry import box
from src.study.geography import audit, metric_transform


class GeographyTests(unittest.TestCase):
    def config(self):
        return {'metric_crs': 'EPSG:25832', 'operational_mapping': {'RawA': 'A', 'RawB': 'B'}}

    def row(self, key, x, label='RawA'):
        return {'listing_id': key, 'longitude': x, 'latitude': 55.1,
                'provider_neighbourhood': label, 'dwelling_eligible': True, 'positive_price': True}

    def test_unmatched_ambiguous_and_mismatch_retained(self):
        areas = [{'raw_label':'RawA','group':'A','geom':box(12,55,12.3,55.2)},
                 {'raw_label':'RawB','group':'B','geom':box(12.2,55,12.5,55.2)}]
        groups = [{'group':a['group'],'raw_components':[a['raw_label']],'geom':a['geom']} for a in areas]
        rows = [self.row('1',12.1),self.row('2',12.25),self.row('3',12.6),self.row('4',12.4)]
        summary, records = audit(rows,box(12,55,12.8,55.2),areas,groups,self.config())
        self.assertEqual(len(records),4)
        self.assertEqual([r['assignment_status'] for r in records],['unique','ambiguous','unmatched','unique'])
        self.assertEqual(records[3]['raw_label'],'RawA')
        self.assertEqual(summary['source_vs_polygon']['operational_label_mismatch'],1)
        self.assertEqual(summary['status'],'BLOCKED')

    def test_duplicate_and_nonmetric_refused(self):
        with self.assertRaises(ValueError):
            metric_transform('EPSG:4326')
        with self.assertRaises(ValueError):
            audit([self.row('1',12.1),self.row('1',12.1)],box(12,55,13,56),[],[],self.config())

    def test_merged_raw_boundary_is_one_operational_group(self):
        raw=[{'raw_label':'RawA','group':'Merged','geom':box(12,55,12.2,55.2)},
             {'raw_label':'RawB','group':'Merged','geom':box(12.2,55,12.4,55.2)}]
        config={'metric_crs':'EPSG:25832','operational_mapping':{'RawA':'Merged','RawB':'Merged'}}
        group=[{'group':'Merged','raw_components':['RawA','RawB'],'geom':box(12,55,12.4,55.2)}]
        _,rows=audit([self.row('1',12.2)],box(12,55,12.4,55.2),raw,group,config)
        self.assertEqual(rows[0]['assignment_status'],'unique')
        self.assertEqual(rows[0]['raw_polygon_hits'],['RawA','RawB'])
