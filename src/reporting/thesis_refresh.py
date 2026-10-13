"""Render and install presentation changes only after exact archive preservation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from src.ingestion.common import sha256_file
from src.study.sources import write_once
from src.reporting.thesis_sources import ROOT,verify_catalog
from src.study.archive import preserved_path

BASELINE=ROOT/'archive/before_output_cleanup/manifest.json'


def cleanup_baseline():
    record=json.loads(BASELINE.read_text())
    for item in record['files']:
        path=ROOT/item['archived_path']
        if sha256_file(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('Archived output changed: '+str(path))
    for item in record['numeric_exports_immutable']:
        if sha256_file(ROOT/item['current_path'])!=item['sha256']:raise ValueError('Frozen numerical export changed')
    if verify_catalog()['source_catalog_sha256']!=record['source_catalog_sha256']:raise ValueError('Scientific catalog changed')
    return record


def baseline():
    """Keep the original style checkpoint and its forty-four exports verifiable."""
    record=json.loads((ROOT/'archive/before_figure_style/manifest.json').read_text())
    for item in record['files']:
        if sha256_file(ROOT/item['archived_path'])!=item['sha256']:raise ValueError('Prior presentation changed')
    for item in record['numeric_exports_immutable']:
        if sha256_file(preserved_path(item['original_path'],item['sha256']))!=item['sha256']:raise ValueError('Prior numerical export changed')
    cleanup_baseline()
    return record


def render():
    from src.reporting.thesis_outputs import run
    cleanup_baseline()
    preview=Path(tempfile.mkdtemp(prefix='thesis-layout-'))/'figures'
    return run(preview=preview)


def activate(preview):
    previous=cleanup_baseline();manifest_path=preview/'thesis_artifact_manifest.json';manifest=json.loads(manifest_path.read_text())
    for check in manifest['layout_checks']:
        if check['out_of_canvas_text'] or check['caption_overlaps_axis_label'] or check['header_overlaps_legend'] or check['data_text_outside_axes'] or check['plotted_values_outside_axes']:
            raise ValueError('Preview contains clipped/overlapping labels: '+check['figure'])
        if any(not panel['square'] for panel in check['map_panels']):raise ValueError('Map panel is not square')
    if manifest['source_catalog_sha256']!=previous['source_catalog_sha256']:raise ValueError('Preview scientific identity differs')
    for name,expected in manifest['generation_dependencies'].items():
        if sha256_file(ROOT/name)!=expected:raise ValueError('Preview code changed; render again')
    figures=[item for item in manifest['items'] if item['kind']=='figure']
    if len(figures)!=18 or any(Path(item['filename']).suffix!='.png' for item in figures):raise ValueError('Expected eighteen PNG figures only')
    for item in figures:
        source=preview/Path(item['filename']).name;dest=ROOT/item['filename']
        if sha256_file(source)!=item['sha256']:raise ValueError('Preview figure changed')
        if dest.exists():raise ValueError('Active figure exists; preserve before replacing')
    for item in figures:shutil.copyfile(preview/Path(item['filename']).name,ROOT/item['filename'])
    old={item['original_path']:item for item in previous['files']}
    def remove_preserved(name):
        path=ROOT/name
        if path.exists():
            if name not in old or sha256_file(path)!=old[name]['sha256']:raise ValueError('Existing audit changed: '+name)
            path.unlink()
    remove_preserved('reports/thesis_artifact_manifest.json')
    write_once(ROOT/'reports/thesis_artifact_manifest.json',manifest_path.read_bytes())
    for name in ['reports/thesis_publication_validation.json','reports/thesis_style_review.json',
                 'reports/thesis_delivery_audit.json','reports/thesis_delivery_audit.md','reports/thesis_completion_checks.json']:
        remove_preserved(name)
    return {'installed_PNG_figures':18,'numerical_exports_verified_byte_identical':44,'models_refitted':False}


def package():
    cleanup_baseline()
    if not (ROOT/'reports/thesis_style_review.json').exists():raise ValueError('Visual/publication review required first')
    from src.reporting.thesis_release import assemble,delivery
    result=assemble();delivery(result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--render',action='store_true');group.add_argument('--activate',type=Path);group.add_argument('--package',action='store_true')
    args=parser.parse_args();result=render() if args.render else activate(args.activate) if args.activate else package()
    print(json.dumps(result,indent=2))
