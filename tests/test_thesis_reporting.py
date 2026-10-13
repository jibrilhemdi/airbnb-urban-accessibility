"""Every selected thesis artifact must have final provenance and safe content."""
import unittest
import json
from pathlib import Path
from src.reporting.thesis_sources import ROOT,verify_catalog
from src.reporting.thesis_validate import artifacts,FORBIDDEN,STALE
import pandas as pd


class ThesisReportingTests(unittest.TestCase):
    def test_every_main_recommendation_exists_has_final_lineage_and_functional_name(self):
        catalog=verify_catalog();manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text())
        items={item['filename']:item for item in manifest['items']}
        recommendations=json.loads((ROOT/'reports/thesis_recommendations.json').read_text())
        for item in recommendations:
            with self.subTest(artifact=item['file']):
                self.assertTrue((ROOT/item['file']).is_file())
                self.assertIn(item['file'],items)
                self.assertFalse(STALE.search(Path(item['file']).name))
                self.assertEqual(items[item['file']]['source_catalog_sha256'],catalog['source_catalog_sha256'])
                self.assertTrue(items[item['file']]['source_run_artifact'])

    def test_full_publication_artifact_and_numeric_integrity(self):
        result=artifacts()
        self.assertEqual(result['figure_sets'],18)
        self.assertEqual(result['table_and_aggregate_views'],22)
        self.assertFalse(result['models_refitted'])

    def test_private_prediction_and_coordinate_rows_never_enter_public_exports(self):
        manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text())
        for item in manifest['items']:
            if item['filename'].endswith('.csv'):
                frame=pd.read_csv(ROOT/item['filename']);self.assertFalse(set(frame)&FORBIDDEN)
                if item['logical_name'].endswith(('_bins','_cells')):self.assertTrue(frame.n.ge(5).all())

    def test_release_hashes_local_links_zip_membership_and_complete_deliverables(self):
        from src.reporting.thesis_release import verify
        result=verify()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['private_data_check'],'PASS')
        audit=json.loads((ROOT/'reports/thesis_delivery_audit.json').read_text())
        self.assertEqual(audit['status'],'COMPLETE_THESIS_REPORTING')
        self.assertEqual(audit['remaining_required_deliverables'],[])
        self.assertTrue(all(item['completion_status'] in {'READY','NOT_NEEDED'} for item in audit['required_deliverables']))

    def test_style_refresh_preserves_all_numerical_exports_and_original_reference(self):
        import ast
        from src.reporting.thesis_refresh import baseline
        from src.reporting import thesis_style
        previous=baseline()
        self.assertEqual(len(previous['numeric_exports_immutable']),44)
        # Match the actual original source's literal colour definitions.
        reference=ast.parse((ROOT/'src/pipeline/reporting_figures.py').read_text())
        tokens={}
        for node in reference.body:
            if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in {'NAVY','INK','BLUE','SAND','GREEN','LILAC','DARK'}:
                tokens[node.targets[0].id]=ast.literal_eval(node.value)
        for name,value in tokens.items():self.assertEqual(getattr(thesis_style,name),value)
        manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text())
        self.assertEqual(manifest['style']['style_id'],thesis_style.STYLE_ID)
        self.assertTrue(all(not row['caption_overlaps_axis_label'] and not row['header_overlaps_legend'] for row in manifest['layout_checks']))

    def test_current_outputs_have_one_location_and_png_figures_only(self):
        outputs=ROOT/'outputs'
        self.assertEqual({p.name for p in outputs.iterdir() if p.is_dir()},{'figures','tables','metrics'})
        figures=list((outputs/'figures').iterdir())
        self.assertEqual(len(figures),18)
        self.assertTrue(all(p.suffix=='.png' for p in figures))
        manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text())
        expected={item['filename'] for item in manifest['items']}|{'outputs/README.md','outputs/thesis_results.zip'}
        actual={str(p.relative_to(ROOT)) for p in outputs.rglob('*') if p.is_file() and p.name!='.DS_Store'}
        self.assertEqual(actual,expected)

    def test_square_maps_include_all_frozen_neighbourhood_boundaries_and_labels_fit(self):
        manifest=json.loads((ROOT/'reports/thesis_artifact_manifest.json').read_text())
        maps=[row for row in manifest['layout_checks'] if row['map_panels']]
        self.assertEqual({row['figure'] for row in maps},{'study_areas','accessibility_spatial'})
        for row in maps:
            self.assertEqual([p['neighbourhood_boundaries'] for p in row['map_panels']],[11,17,11])
            self.assertTrue(all(p['square'] for p in row['map_panels']))
            for panel in row['map_panels']:
                context=panel['cartographic_context']
                self.assertGreater(context['surrounding_municipalities'],0)
                self.assertEqual(context['study_boundary_colour'],'white')
                self.assertEqual(context['context_boundary_colour'],'#A5B4B0')
                self.assertTrue(context['civic_reference_geometry_sha256'])
                self.assertIn(context['capital'],{'Copenhagen','Oslo','Stockholm'})
        self.assertTrue(all(not row['data_text_outside_axes'] for row in manifest['layout_checks']))
        self.assertTrue(all(not row['plotted_values_outside_axes'] for row in manifest['layout_checks']))
        chart=next(item for item in manifest['items'] if item['logical_name']=='neighbourhood_performance_variation')
        self.assertEqual(chart['plot_orientation'],'horizontal')
