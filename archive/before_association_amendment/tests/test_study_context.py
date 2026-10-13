import unittest
import numpy as np
import pandas as pd
from src.study.context import aggregate_density,parse_stockholm_density,STOCKHOLM_CODES


class DensityTests(unittest.TestCase):
    def test_aggregate_populations_and_areas_never_average_density(self):
        units=[{'population':100,'area_km2':1,'whole_unit_verified':True},
               {'population':100,'area_km2':9,'whole_unit_verified':True}]
        self.assertEqual(aggregate_density(units),20)
        self.assertIsNone(aggregate_density([{'population':None,'area_km2':1,'whole_unit_verified':True}]))
        with self.assertRaises(ValueError):aggregate_density([{'population':1,'area_km2':1,'whole_unit_verified':False}])

    def frames(self):
        pop=pd.DataFrame(np.full((23,10),None),dtype=object)
        area=pd.DataFrame(np.full((20,7),None),dtype=object)
        pop.iloc[0,0]='Folkmängd efter ålder 2025-12-31';pop.iloc[2,9]='Samtliga'
        area.iloc[0,0]='Areal och befolkningstäthet 2024-12-31';area.iloc[3,2:5]=['Land','Vatten','Totalt']
        for i,(code,name) in enumerate(STOCKHOLM_CODES.items(),4):
            pop.iloc[i,:]=[name,*([10]*8),80]
            area.iloc[i,:]=[code,name,90,10,100,70,0]
        return pop,area

    def test_direct_eleven_units_units_and_source_years(self):
        pop,area=self.frames()
        rows=parse_stockholm_density(pop,area,{'population':{},'area':{}})
        self.assertEqual(len(rows),11)
        self.assertEqual(rows[0]['area_km2'],1)
        self.assertEqual(rows[0]['population_density'],80)
        self.assertEqual(rows[0]['population'],80)

    def test_native_total_denominator_and_schema_refuse(self):
        pop,area=self.frames();pop.iloc[4,9]=81
        with self.assertRaises(ValueError):parse_stockholm_density(pop,area,{'population':{},'area':{}})
        pop,area=self.frames();area.iloc[4,4]=101
        with self.assertRaises(ValueError):parse_stockholm_density(pop,area,{'population':{},'area':{}})
        pop,area=self.frames();pop.iloc[0,0]='Unknown time'
        with self.assertRaises(ValueError):parse_stockholm_density(pop,area,{'population':{},'area':{}})
