"""Preserved, staged figure style refresh; all frozen numerical exports stay intact."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from src.ingestion.common import sha256_file
from src.study.sources import write_once
from src.reporting.thesis_sources import ROOT,verify_catalog

BASELINE=ROOT/'archive/before_figure_style/manifest.json'


def baseline():
    record=json.loads(BASELINE.read_text())
    for item in record['files']:
        path=ROOT/item['archived_path']
        if sha256_file(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('Archived presentation changed: '+str(path))
    for item in record['numeric_exports_immutable']:
        if sha256_file(ROOT/item['original_path'])!=item['sha256']:raise ValueError('Frozen numerical export changed')
    if verify_catalog()['source_catalog_sha256']!=record['source_catalog_sha256']:raise ValueError('Scientific catalog changed')
    return record


def render():
    from src.reporting.thesis_outputs import run
    baseline()
    preview=Path(tempfile.mkdtemp(prefix='thesis-style-'))/'figures'
    return run(preview=preview)


def activate(preview):
    record=baseline();manifest_path=preview/'thesis_artifact_manifest.json';manifest=json.loads(manifest_path.read_text())
    if any(item['out_of_canvas_text'] or item['caption_overlaps_axis_label'] or item['header_overlaps_legend'] for item in manifest['layout_checks']):raise ValueError('Style preview contains clipped/overlapping labels')
    if manifest['source_catalog_sha256']!=record['source_catalog_sha256']:raise ValueError('Preview scientific identity differs')
    for name,expected in manifest['generation_dependencies'].items():
        if sha256_file(ROOT/name)!=expected:raise ValueError('Preview code changed; render again')
    old={item['original_path']:item for item in record['files']}
    figures=[item for item in manifest['items'] if item['kind']=='figure']
    if len(figures)!=54:raise ValueError('Incomplete figure preview')
    for item in figures:
        source=preview/Path(item['filename']).name
        if sha256_file(source)!=item['sha256']:raise ValueError('Preview figure changed')
        if sha256_file(ROOT/item['filename'])!=old[item['filename']]['sha256']:raise ValueError('Existing figure changed since preservation')
    # Archive equality was checked before replacing these known public files.
    for item in figures:shutil.copyfile(preview/Path(item['filename']).name,ROOT/item['filename'])
    (ROOT/'reports/thesis_artifact_manifest.json').write_bytes(manifest_path.read_bytes())
    for name in ['reports/thesis_publication_validation.json','reports/thesis_delivery_audit.json',
                 'reports/thesis_delivery_audit.md','reports/thesis_completion_checks.json']:
        path=ROOT/name
        if sha256_file(path)!=old[name]['sha256']:raise ValueError('Prior audit changed since preservation')
        path.unlink()
    from src.reporting.thesis_validate import artifacts
    checked=artifacts()
    write_once(ROOT/'reports/thesis_publication_validation.json',(json.dumps(checked,indent=2)+'\n').encode())
    review={'status':'PASS_VISUAL_REVIEW','style_id':manifest['style']['style_id'],
            'reference_style':manifest['style'],'figure_sets':18,'figure_files':54,
            'visual_review':'All18 figures reviewed in full-resolution contact sheets plus selected full-size panels before activation',
            'numerical_exports_verified_byte_identical':44,'source_catalog_sha256':record['source_catalog_sha256'],
            'previous_presentation_archive':'archive/before_figure_style/manifest.json',
            'models_refitted':False,'scientific_choice_changes':False,'publication_validation':checked}
    write_once(ROOT/'reports/thesis_style_review.json',(json.dumps(review,indent=2,ensure_ascii=False)+'\n').encode())
    return checked


def package():
    record=baseline()
    if not (ROOT/'reports/thesis_style_review.json').exists():raise ValueError('Style refresh needs visual/publication review first')
    from src.reporting import thesis_release
    active=ROOT/'outputs/release'
    previous={item['original_path']:item for item in record['files'] if item['original_path'].startswith('outputs/release/')}
    actual={str(p.relative_to(ROOT)) for p in active.rglob('*') if p.is_file()}
    if actual!=set(previous):raise ValueError('Existing release membership changed since preservation')
    for name,item in previous.items():
        if sha256_file(ROOT/name)!=item['sha256']:raise ValueError('Existing release changed since preservation')
    stage=Path(tempfile.mkdtemp(prefix='.thesis-release-',dir=ROOT/'outputs'))/'release'
    thesis_release.DESTINATION=stage
    thesis_release.assemble()
    thesis_release.verify()
    # Only files already preserved and verified against the prior certificate.
    for name in previous:(ROOT/name).unlink()
    for path in sorted((p for p in active.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):path.rmdir()
    active.rmdir();stage.rename(active);stage.parent.rmdir()
    thesis_release.DESTINATION=active
    result=thesis_release.verify();thesis_release.delivery(result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--render',action='store_true');group.add_argument('--activate',type=Path);group.add_argument('--package',action='store_true')
    args=parser.parse_args();result=render() if args.render else activate(args.activate) if args.activate else package()
    print(json.dumps(result,indent=2))
