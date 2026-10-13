"""Synthetic RegSO fixtures; no private source rows or production namespaces."""
from copy import deepcopy
from contextlib import redirect_stdout
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import geopandas as gpd
from shapely.geometry import Polygon, box
from pyproj import Transformer

from src.v4.stockholm_boundary import (load_policy, qualify_regso, municipal_areas,
                                      location_diagnostic, main)
from src.v4.identity import scientific_dependencies
from src.pipeline.protocol import canonical_hash


def fixture():
    # Two adjacent Stockholm areas and a separate same-county municipality.
    frame = gpd.GeoDataFrame(dict(regsokod=['0180R001','0180R002','0181R001'],
        kommunkod=['0180','0180','0181'], lanskod=['01']*3, version=['2025_v2']*3,
        referensdatum=['20250101']*3, objekttyp=['regso']*3),
        geometry=[box(670000,6580000,670200,6580200), box(670200,6580000,670400,6580200),
                  box(670800,6580000,671000,6580200)], crs=3006)
    policy = load_policy(); policy['qualified_area_ids']=['0180R001','0180R002']
    return frame, {'2025':80000.0,'2026':80000.0}, policy


class StockholmBoundaryTests(unittest.TestCase):
    def test_exact_municipality_selection_valid_dissolve_and_coverage(self):
        native, geographic, qa = qualify_regso(*fixture())
        self.assertEqual(qa['selected_features'],2)
        self.assertEqual(qa['selected_area_ids'],['0180R001','0180R002'])
        self.assertEqual(native.area,80000)
        self.assertEqual(qa['other_municipality_overlap_m2'],0)
        self.assertTrue(geographic.is_valid)
        self.assertEqual(qa['components'],1); self.assertEqual(qa['holes'],0)
        self.assertFalse(qa['certified_2026_geometry'])

    def test_schema_crs_vintage_county_ids_and_empty_selection_fail_closed(self):
        frame, areas, policy = fixture()
        mutations = [lambda f:f.drop(columns=['kommunkod']), lambda f:f.set_crs(4326,allow_override=True),
                     lambda f:f.assign(referensdatum='20260101'), lambda f:f.assign(version='2020'),
                     lambda f:f.assign(lanskod='02'), lambda f:f.assign(kommunkod='01'),
                     lambda f:f.assign(regsokod=['0180R001','0180R001','0181R001'])]
        for change in mutations:
            with self.subTest(change=change), self.assertRaises(ValueError):
                qualify_regso(change(frame.copy()),areas,policy)

    def test_no_geometry_repair_or_silent_overlap_gap_or_area_acceptance(self):
        frame, areas, policy = fixture()
        for geometry in [Polygon(), Polygon([(0,0),(2,2),(2,0),(0,2),(0,0)]),
                         box(670100,6580000,670300,6580200),
                         box(670300,6580000,670500,6580200)]:
            changed=frame.copy(); changed.loc[1,'geometry']=geometry
            with self.subTest(geometry=geometry.geom_type), self.assertRaises(ValueError):
                qualify_regso(changed,areas,policy)
        with self.assertRaisesRegex(ValueError,'area'):
            qualify_regso(frame,{'2025':100000,'2026':80000},policy)
        changed=frame.copy(); changed.loc[2,'geometry']=box(670100,6580000,670200,6580100)
        with self.assertRaisesRegex(ValueError,'another municipality'):
            qualify_regso(changed,areas,policy)

    def test_outer_boundary_distance_ignores_regso_internal_edge(self):
        frame, areas, policy=fixture()
        # Enlarge fixture to put the shared internal edge >150m from exteriors.
        frame.loc[0,'geometry']=box(670000,6580000,670500,6581000)
        frame.loc[1,'geometry']=box(670500,6580000,671000,6581000)
        frame.loc[2,'geometry']=box(672000,6580000,672100,6580100)
        native, geographic, _=qualify_regso(frame,{'2025':1000000,'2026':1000000},policy)
        to_geo=Transformer.from_crs(3006,4326,always_xy=True)
        rows=[]
        for x,y,inside in [(670500,6580500,True),(670100,6580500,True),(669900,6580500,False)]:
            lon,lat=to_geo.transform(x,y)
            rows.append(dict(longitude=lon,latitude=lat,inside_boundary=inside,
                             dwelling_eligible=True,positive_price=True,
                             official_analysis_area_id=None,native_housing_area_id=None))
        counts=location_diagnostic(rows,native)
        self.assertEqual(counts['boundary_150m_raw'],2)
        self.assertEqual(counts['inside_boundary_150m_positive_price'],1)
        self.assertEqual(counts['outside_boundary_150m_positive_price'],1)
        self.assertGreater(rows[0]['distance_to_outer_boundary_m'],150)
        self.assertTrue(all(r['official_analysis_area_id'] is None and r['native_housing_area_id'] is None for r in rows))

    def test_official_area_csv_exact_region_units_and_encoding(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'areas.zip'
            rows=[['0180 Stockholm','totalt',y,'Hektar','21575.73'] for y in ['2025','2026']]
            rows += [['01 Stockholms län','totalt','2025','Hektar','1']]
            out=io.StringIO(); writer=csv.writer(out)
            writer.writerow(['region','arealtyp','år','tabellinnehåll','Land- och vattenareal per den 1 januari']);writer.writerows(rows)
            with zipfile.ZipFile(path,'w') as z:z.writestr('TAB6420_sv.csv',out.getvalue().encode('cp1252'))
            self.assertEqual(municipal_areas(path),{'2025':215757300.0,'2026':215757300.0})
            with zipfile.ZipFile(path,'w') as z:z.writestr('other.csv',out.getvalue().encode('cp1252'))
            with self.assertRaises(ValueError):municipal_areas(path)

    def test_only_stockholm_command_and_scientific_policy_identity(self):
        out=io.StringIO()
        with redirect_stdout(out), patch('src.v4.stockholm_boundary.get_engine') as connect:
            code=main(['audit','--version','research_design_v4','--city','oslo',
                       '--snapshot','2026-06-30','--run-id','research_v4_oslo_20261011T120000Z',
                       '--previous-run-id','research_v4_stockholm_20261011T143812Z'])
        self.assertEqual(code,2);connect.assert_not_called()
        self.assertEqual(json.loads(out.getvalue())['models_fitted'],0)
        original=scientific_dependencies('stockholm')
        self.assertIn('boundary_amendment',original['listing_source_policy'])
        changed=deepcopy(original);changed['listing_source_policy']['boundary_amendment']['reference_date']='2026-01-01'
        self.assertNotEqual(canonical_hash(original),canonical_hash(changed))
        self.assertNotIn('boundary_amendment',scientific_dependencies('oslo')['listing_source_policy'])


if __name__ == '__main__':unittest.main()
