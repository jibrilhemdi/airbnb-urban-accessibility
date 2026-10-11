"""Explain saved random and LOAO splits using real, frozen project geography.

Run from the project root:
  MPLCONFIGDIR=/private/tmp/thesis-mpl .venv/bin/python scripts/plot_random_vs_loao_validation.py

PostgreSQL/PostGIS is authoritative. No source data or fold assignments are
changed, and no row-level coordinate exports are written. Missing real inputs
produce a diagnostic and a nonzero exit; there is no synthetic fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import textwrap

import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from sqlalchemy import text

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEFAULT_ROOT))
from src.db.connection import get_engine
from src.ingestion.common import sha256_file
from src.pipeline.build_analysis_dataset import load_dataset, dataset_hash
from src.pipeline.reporting_figures import Figures, BLUE, SAND, DARK

REFERENCES = [
    'outputs/figures/reporting/validation_geography.png',
    'outputs/figures/reporting/study_area_listings.png',
    'outputs/figures/geography/analysis_areas.png',
    'outputs/tables/validation/fold_summary.csv',
    'outputs/tables/validation/splits_metadata.json',
    'outputs/tables/geography/cv_area_counts.csv',
    'outputs/tables/analysis_dataset/analysis_area_counts.csv',
]
TRAIN = BLUE
TEST = SAND
INK = '#183449'


def inspect_project(root):
    if not root.is_dir():
        raise FileNotFoundError(f'Project directory missing: {root}. No boundaries or coordinates were loaded.')
    missing = [name for name in REFERENCES if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError('Required project reference files missing: ' + ', '.join(missing))
    # Include raw, processed and historical project data in discovery; omit
    # installed software and Git internals rather than analytical directories.
    command = ['rg', '--files', '--hidden', '--no-ignore', '-g', '!.git/**',
               '-g', '!.venv/**', '-g', '!node_modules/**']
    try:
        names = subprocess.run(command, cwd=root, check=True, capture_output=True, text=True).stdout.splitlines()
    except FileNotFoundError:
        names = [p.relative_to(root).as_posix() for p in root.rglob('*')
                 if p.is_file() and not {'.git', '.venv', 'node_modules'}.intersection(p.relative_to(root).parts)]
    extensions = {'.gpkg', '.geojson', '.shp', '.parquet', '.csv', '.feather', '.fgb', '.kml'}
    inventory = sorted(name for name in names if Path(name).suffix.lower() in extensions)
    metadata = json.loads((root / REFERENCES[4]).read_text())
    if metadata['design']['crs']['metric'] != 25832:
        raise ValueError('Expected the documented project metric CRS EPSG:25832')
    summary = pd.read_csv(root / REFERENCES[3], dtype={'outer_fold': str})
    final_counts = pd.read_csv(root / REFERENCES[6]).set_index('analysis_area')['n'].to_dict()
    geography_counts = pd.read_csv(root / REFERENCES[5]).set_index('area')
    for name in REFERENCES[:3]:
        if plt.imread(root / name).ndim != 3:
            raise ValueError(f'Unexpected reference image structure: {name}')
    return metadata, summary, final_counts, geography_counts, inventory


def load_inputs(root, metadata, summary, final_counts, geography_counts, area_id, random_fold):
    engine = get_engine(root / '.env')
    try:
        with engine.connect() as conn:
            conn.execute(text('SET TRANSACTION READ ONLY'))
            areas = gpd.read_postgis(text('SELECT area_id,area_name,geom_25832 AS geom FROM '
                                          'v3_spatial.analysis_areas ORDER BY area_id'), conn, geom_col='geom')
            if areas.empty or len(areas) != 11 or areas.crs.to_epsg() != 25832:
                raise ValueError('Missing or inconsistent 11-area processed geometry in v3_spatial.analysis_areas')
            if areas.geometry.isna().any() or areas.geometry.is_empty.any() or not areas.geometry.is_valid.all():
                raise ValueError('Invalid/missing processed analysis-area polygons')
            frame = load_dataset(conn)
            if dataset_hash(frame) != metadata['dataset_sha256']:
                raise ValueError('SQL final sample differs from the frozen validation metadata')
            run = conn.execute(text("SELECT run_id,metadata->>'dataset_sha256' FROM v3_analysis.runs "
                                    "WHERE status='complete' ORDER BY started_at DESC LIMIT 1")).one()
            if run[1] != metadata['dataset_sha256']:
                raise ValueError('Completed run and frozen sample do not match')
            coordinates = frame[['snapshot_date', 'listing_id', 'analysis_area', 'metric_x', 'metric_y']].copy()
            coordinates['snapshot_date'] = coordinates.snapshot_date.astype(str).str[:10]
            keys = ['snapshot_date', 'listing_id']
            if coordinates[keys].duplicated().any() or not np.isfinite(coordinates[['metric_x', 'metric_y']]).all().all():
                raise ValueError('Final-sample coordinates are missing, nonfinite, or duplicated')
            actual_counts = coordinates.groupby('analysis_area').size().to_dict()
            if actual_counts != final_counts or set(actual_counts) != set(areas.area_id):
                raise ValueError('Final-sample counts and processed polygon identifiers do not match')
            if any(int(geography_counts.loc[a, 'eligible_n']) < n for a, n in actual_counts.items()):
                raise ValueError('Final sample exceeds the upstream eligible geography counts')
            if area_id not in actual_counts:
                raise ValueError(f'Requested real held-out area not found: {area_id}')
            role_sources = {}
            for scheme, fold, name in [('random_5', random_fold, 'random_role'),
                                       ('geographic_11', area_id, 'loao_role')]:
                assignments = pd.read_sql(text('SELECT snapshot_date,listing_id,role FROM '
                    'v3_analysis.outer_assignments WHERE scheme=:scheme AND outer_fold=:fold '
                    'ORDER BY snapshot_date,listing_id'), conn, params={'scheme': scheme, 'fold': fold})
                if assignments.empty:
                    raise ValueError(f'Saved assignments missing: v3_analysis.outer_assignments, {scheme}/{fold}')
                assignments['snapshot_date'] = assignments.snapshot_date.astype(str).str[:10]
                if len(assignments) != len(coordinates) or set(assignments.role) != {'train', 'test'}:
                    raise ValueError(f'Incomplete or unexpected saved split: {scheme}/{fold}')
                expected = summary.loc[(summary.scheme == scheme) & (summary.outer_fold == fold)]
                if len(expected) != 1 or (expected.crs_epsg != 25832).any():
                    raise ValueError(f'Fold summary missing or CRS inconsistent: {scheme}/{fold}')
                counts = assignments.role.value_counts()
                if any(int(counts[role]) != int(expected.iloc[0][role + '_n']) for role in ['train', 'test']):
                    raise ValueError(f'Saved assignments disagree with fold_summary.csv: {scheme}/{fold}')
                role_sources[name] = {'scheme': scheme, 'outer_fold': fold, 'train_n': int(counts['train']),
                    'test_n': int(counts['test']), 'assignments_sha256': hashlib.sha256(
                        assignments.to_json(orient='records').encode()).hexdigest()}
                coordinates = coordinates.merge(assignments.rename(columns={'role': name}), on=keys,
                                                validate='one_to_one', how='left')
                if coordinates[name].isna().any():
                    raise ValueError(f'Saved assignment join lost final-sample rows: {scheme}/{fold}')
            if not np.array_equal(coordinates.loao_role.eq('test'), coordinates.analysis_area.eq(area_id)):
                raise ValueError('Saved LOAO assignments do not hold out exactly the requested whole area')
            for row in areas.itertuples():
                if row.area_name != geography_counts.loc[row.area_id, 'area_name']:
                    raise ValueError('Processed official area name differs from geography export')
            points = gpd.GeoDataFrame(coordinates, geometry=gpd.points_from_xy(coordinates.metric_x,
                                       coordinates.metric_y), crs=25832)
            # Use the reporting suite's own basemap renderer and SQL context,
            # so coastlines, neighbouring municipalities and framing match.
            map_style = Figures(engine, run[0], frame, {})
            if not map_style.context:
                raise ValueError('Official neighbouring-municipality context missing from v3_spatial.map_context_municipalities')
            return areas, points, role_sources, run[0], map_style
    finally:
        engine.dispose()


def draw(areas, points, roles, area_id, output, map_style):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'text.color': INK,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white'})
    xmin, ymin, xmax, ymax = areas.total_bounds
    padding = .02 * max(xmax - xmin, ymax - ymin)
    bounds = (xmin-padding, ymin-padding, xmax+padding, ymax+padding)
    # Size axes in inches from the real projected extent. Equal map aspect
    # then consumes the complete panel, rather than shrinking inside a slot.
    width = 12.4
    margin, gutter = .22, .22
    map_width = (width-2*margin-gutter)/2
    map_height = map_width*(bounds[3]-bounds[1])/(bounds[2]-bounds[0])
    footer, header = 1.16, 1.04
    height = footer+map_height+header
    fig = plt.figure(figsize=(width, height))
    panel_lefts = [margin, margin+map_width+gutter]
    axes = [fig.add_axes([left/width, footer/height, map_width/width, map_height/height])
            for left in panel_lefts]
    map_top = footer+map_height
    fig.text(margin/width, (map_top+.755)/height, 'Two ways to test prediction', fontsize=18, weight='bold')
    fig.text(margin/width, (map_top+.485)/height,
             f'Copenhagen & Frederiksberg · {len(points):,} Airbnb listings · one saved outer split per design',
             fontsize=9.5, color='#486174')
    held_out = areas.loc[areas.area_id == area_id]
    area_name = held_out.area_name.iloc[0]
    annotations = [
        'Train and test listings are spatially mixed.\nNearby listings can appear in both sets.',
        'One whole area is held out as the test set.\nThe model is evaluated on a geographically unseen area.',
    ]
    for i, (ax, role, title) in enumerate(zip(axes, ['random_role', 'loao_role'],
                         ['Random cross-validation', 'Leave-one-area-out cross-validation'])):
        map_style.base_map(ax)
        if i == 1:
            held_out.plot(ax=ax, facecolor=TEST, edgecolor=DARK[1], alpha=.42, linewidth=1.2, zorder=2.5)
        for state, color, alpha, size in [('train', TRAIN, .65, 3), ('test', TEST, .90, 5)]:
            p = points.loc[points[role] == state]
            ax.scatter(p.metric_x, p.metric_y, s=size, color=color, alpha=alpha,
                       linewidths=0, zorder=3 if state == 'train' else 4)
        # Place the outline above the points so the complete held-out area is clear.
        if i == 1:
            held_out.boundary.plot(ax=ax, color=DARK[1], linewidth=1.4, zorder=5)
            target = held_out.geometry.iloc[0].representative_point()
            ax.annotate(f'{area_name}\nTest area', xy=(target.x, target.y),
                xytext=(.05, .92), textcoords='axes fraction', fontsize=9, color=DARK[1],
                ha='left', va='top', weight='bold',
                bbox={'boxstyle': 'round,pad=.35', 'facecolor': 'white', 'edgecolor': 'none', 'alpha': .94},
                arrowprops={'arrowstyle': '->', 'color': DARK[1], 'lw': 1}, zorder=7)
        ax.set(xlim=(bounds[0], bounds[2]), ylim=(bounds[1], bounds[3]), aspect='equal')
        # GeoPandas adds CRS axis labels when the held-out polygon is plotted.
        ax.set_xlabel('');ax.set_ylabel('');ax.set_xticks([]);ax.set_yticks([])
        fig.text(panel_lefts[i]/width, (map_top+.245)/height,
                 f'{chr(65+i)}  {title}', fontsize=12.5, weight='bold')
        counts = roles[role]
        example = f"Fold {counts['outer_fold']} of 5" if i == 0 else f'{area_name} held out · 11 area folds'
        fig.text(panel_lefts[i]/width, (map_top+.065)/height,
                 f"{example}  |  Train {counts['train_n']:,} · Test {counts['test_n']:,}",
                 fontsize=8.7, color='#486174')
        fig.text((panel_lefts[i]+map_width/2)/width, (footer-.055)/height,
                 annotations[i], ha='center', va='top', fontsize=9, color='#486174', linespacing=1.3)
    fig.legend(handles=[Line2D([], [], marker='o', linestyle='', color=color,
                   markersize=6, label=name) for name, color in [('Training', TRAIN), ('Test', TEST)]],
               ncol=2, loc='upper center', bbox_to_anchor=(.5, (footer-.445)/height),
               frameon=False, fontsize=9, borderaxespad=0)
    caption = ('Random cross-validation evaluates prediction within a spatially mixed sample, while '
               'leave-one-area-out cross-validation evaluates whether the model generalises to a geographically unseen area.')
    fig.text(margin/width, (footer-.735)/height, textwrap.fill(caption, 153), fontsize=8.5,
             va='top', color='#486174', linespacing=1.25)
    fig.text(margin/width, (footer-1.075)/height,
             'Real final-sample coordinates and official processed boundaries · saved outer assignments · EPSG:25832',
             fontsize=7.5, color='#667D89')
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=300, bbox_inches='tight', pad_inches=.07, facecolor='white')
    plt.close(fig)
    return bounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--test-area', default='cph_03')
    parser.add_argument('--random-fold', default='1')
    args = parser.parse_args()
    root = args.project_root.resolve()
    try:
        metadata, summary, counts, geography, inventory = inspect_project(root)
        areas, points, roles, run_id, map_style = load_inputs(root, metadata, summary, counts, geography,
                                                   args.test_area, args.random_fold)
        output = root / 'outputs/figures/reporting/random_vs_loao_validation_schematic.png'
        bounds = draw(areas, points, roles, args.test_area, output, map_style)
        provenance = {'run_id': run_id, 'purpose': 'Validation design explanation; no results or model fitting',
            'crs_epsg': 25832, 'dataset_sha256': metadata['dataset_sha256'], 'sample_n': len(points),
            'all_listings_shown_in_each_panel': True, 'coordinate_jitter_or_sampling': False,
            'sources': ['v3_spatial.analysis_areas.geom_25832', 'v3_spatial.map_context_municipalities.geom_25832',
                        'v3_spatial.study_area', 'v3_analysis.dataset_records',
                        'v3_analysis.outer_assignments'], 'saved_splits': roles, 'shared_extent': list(bounds),
            'map_style': 'Existing reporting Figures.base_map: pastel blue/sand, pale blue water, sage neighbouring municipalities, north arrows and 2 km scale bars',
            'map_padding_fraction': .02,
            'layout': 'Panel dimensions match projected extent; 0.22-inch panel gutter; compact headers and footers',
            'map_style_source_sha256': sha256_file(root/'src/pipeline/reporting_figures.py'),
            'context_geometries_sha256': hashlib.sha256(''.join(sorted(map_style.context)).encode()).hexdigest(),
            'processed_polygons_sha256': hashlib.sha256(b''.join(areas.geometry.to_wkb())).hexdigest(),
            'reference_files_sha256': {name: sha256_file(root/name) for name in REFERENCES},
            'geospatial_tabular_file_inventory': inventory, 'script_sha256': sha256_file(Path(__file__)),
            'output': output.relative_to(root).as_posix(), 'output_sha256': sha256_file(output)}
        report = root / 'outputs/tables/reporting/random_vs_loao_validation_schematic.json'
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + '\n')
        print(f'Inspected {len(inventory)} geospatial/tabular project files and all seven reference files.')
        print('Used processed polygons: PostgreSQL v3_spatial.analysis_areas (11 areas, EPSG:25832).')
        print('Used existing reporting basemap and official neighbouring municipalities: v3_spatial.map_context_municipalities.')
        print(f'Used real final coordinates: PostgreSQL v3_analysis.dataset_records ({len(points):,} listings).')
        print(f'Used saved assignments: PostgreSQL v3_analysis.outer_assignments; random_5/{args.random_fold}, geographic_11/{args.test_area}.')
        print('Cross-checks: splits_metadata.json, fold_summary.csv, final analysis_area_counts.csv, upstream cv_area_counts.csv.')
        print(f'Saved PNG: {output}\nSaved provenance: {report}')
    except Exception as error:
        print(f'DIAGNOSTIC: {type(error).__name__}: {error}\n'
              f'Looked under {root} (raw, processed, outputs and archives) and the project PostgreSQL tables '
              'v3_spatial.analysis_areas, v3_analysis.dataset_records and v3_analysis.outer_assignments. '
              'No synthetic boundaries, coordinates or fold assignments were substituted.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
