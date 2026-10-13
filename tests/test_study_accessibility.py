import unittest
import networkx as nx
from pyproj import Transformer
from src.study.accessibility import pedestrian_graph,destinations,measurements


class AccessibilityTests(unittest.TestCase):
    def test_direction_and_node_identity_preserved(self):
        way={'type':'way','id':1,'nodes':[1,2],'geometry':[{'lon':12.,'lat':55.},{'lon':12.001,'lat':55.}],
             'tags':{'highway':'footway','oneway:foot':'yes'}}
        graph,_,qa=pedestrian_graph([way],'EPSG:25832')
        self.assertTrue(graph.has_edge(1,2));self.assertFalse(graph.has_edge(2,1));self.assertEqual(qa['nodes'],2)
        conflicting={**way,'id':2,'geometry':[{'lon':12.01,'lat':55.},{'lon':12.001,'lat':55.}]}
        with self.assertRaises(ValueError):pedestrian_graph([way,conflicting],'EPSG:25832')

    def test_matched_universe_and_connector_routes(self):
        project=Transformer.from_crs(4326,25832,always_xy=True);x,y=project.transform(12,55)
        metric={1:(x,y),2:(x+500,y),3:(x+200,y+400)}
        graph=nx.DiGraph();graph.add_edge(1,3,length_m=500);graph.add_edge(3,2,length_m=500)
        dest=[{'category':c,'destination_key':c,'x':x+500,'y':y} for c in ['bus','station','food_social','cultural_tourist']]
        rows,qa=measurements(graph,metric,dest,[{'listing_id':'a','longitude':12,'latitude':55}],[54,11,56,13],'EPSG:25832')
        self.assertEqual(rows[0]['food_e_10'],1);self.assertEqual(rows[0]['food_w_10'],0)
        self.assertEqual(rows[0]['food_w_15'],1)
        self.assertAlmostEqual(rows[0]['nearest_station_walking_minutes'],12)
        self.assertTrue(qa['same_destination_universe'])

    def test_failed_route_separate_from_opportunity_zero(self):
        project=Transformer.from_crs(4326,25832,always_xy=True);x,y=project.transform(12,55)
        metric={1:(x,y),2:(x+100,y)};graph=nx.DiGraph();graph.add_nodes_from(metric)
        dest=[{'category':c,'destination_key':c,'x':x+100,'y':y} for c in ['bus','station','food_social','cultural_tourist']]
        rows,_=measurements(graph,metric,dest,[{'listing_id':'a','longitude':12,'latitude':55}],[54,11,56,13],'EPSG:25832')
        self.assertIsNone(rows[0]['nearest_bus_walking_minutes']);self.assertEqual(rows[0]['food_w_10'],0)
        self.assertFalse(rows[0]['common_support'])
