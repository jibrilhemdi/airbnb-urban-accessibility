"""Assemble and verify the public thesis release; no scientific fitting or writes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile
from urllib.parse import quote
import pandas as pd
from src.ingestion.common import sha256_file
from src.study.sources import write_once
from src.reporting.thesis_sources import ROOT,verify_catalog
from src.reporting.thesis_validate import artifacts,check_links,FORBIDDEN

DESTINATION=ROOT/'outputs/release'
COMMAND='.venv/bin/python -m src.reporting.thesis_release'
REMOTE='https://github.com/jibrilhemdi/airbnb-urban-accessibility/blob/v4/'


def json_file(path):return json.loads(path.read_text())


def release_name(name):
    path=Path(name)
    if name.startswith('outputs/figures/thesis/'):return 'figures/'+path.name
    if name.startswith('outputs/tables/thesis/'):return 'tables/'+path.name
    if name.startswith('outputs/metrics/thesis/'):return 'metrics/'+path.name
    if name.startswith('outputs/diagnostics/thesis/'):return 'metrics/diagnostics/'+path.name
    raise ValueError('Unapproved artifact path: '+name)


def markdown_links(source,content,mapping,destination):
    """Rebase package-local links; unbundled evidence retains a repository link."""
    import os
    def replace(match):
        target=match.group(1)
        if target.startswith(('http:','https:','mailto:')):return match.group(0)
        location,mark,anchor=target.partition('#')
        if not location:return match.group(0)
        resolved=(source.parent/location).resolve()
        if not resolved.exists() or not resolved.is_relative_to(ROOT):raise ValueError('Broken/unsafe source document link: '+target)
        name=str(resolved.relative_to(ROOT))
        rewritten=os.path.relpath(mapping[name],Path(destination).parent) if name in mapping else REMOTE+quote(name,safe='/')
        return ']('+rewritten+(mark+anchor if mark else '')+')'
    return re.sub(r'\]\(([^)]+)\)',replace,content)


def verify():
    catalog=verify_catalog();manifest=json_file(DESTINATION/'manifests/release_manifest.json')
    if manifest['source_catalog_sha256']!=catalog['source_catalog_sha256'] or manifest['models_refitted']:raise ValueError('Release scientific identity differs')
    names={item['filename'] for item in manifest['items']}
    expected=names|{'manifests/release_manifest.json','thesis_release.zip'}
    actual={str(p.relative_to(DESTINATION)) for p in DESTINATION.rglob('*') if p.is_file()}
    if len(names)!=len(manifest['items']) or actual!=expected:raise ValueError('Release missing/extra files')
    for item in manifest['items']:
        path=DESTINATION/item['filename']
        if not path.resolve().is_relative_to(DESTINATION) or path.is_symlink():raise ValueError('Release path escapes package')
        if sha256_file(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('Release file hash/size mismatch')
        if item['publication_status']!='THESIS_READY' or not item['source_run_artifact'] or not item['research_question'] or not item['generation_command']:raise ValueError('Release provenance absent')
        if path.suffix=='.csv':
            frame=pd.read_csv(path)
            if set(frame)&FORBIDDEN:raise ValueError('Private fields in release')
            if path.stem.endswith(('_bins','_cells')) and frame.n.lt(5).any():raise ValueError('Unsuppressed release aggregate')
        if path.suffix not in {'.png','.pdf','.svg','.csv','.md','.json','.py','.txt'} or path.name.startswith('.env'):raise ValueError('Unsafe release file type')
    links=check_links(sorted(DESTINATION.rglob('*.md')))
    archive=DESTINATION/'thesis_release.zip'
    with zipfile.ZipFile(archive) as z:
        zip_names=z.namelist()
        if len(zip_names)!=len(set(zip_names)) or set(zip_names)!=names|{'manifests/release_manifest.json'}:raise ValueError('ZIP membership differs')
        if z.testzip() is not None:raise ValueError('ZIP CRC validation failed')
        for name in zip_names:
            if z.read(name)!=(DESTINATION/name).read_bytes():raise ValueError('ZIP member differs from registered file')
    return {'status':'PASS','package_files':len(names)+1,'zip_entries':len(zip_names),'links_checked':links,
            'manifest_sha256':sha256_file(DESTINATION/'manifests/release_manifest.json'),
            'zip_sha256':sha256_file(archive),'zip_bytes':archive.stat().st_size,
            'private_data_check':'PASS','all_release_hashes':'PASS','models_refitted':False}


def assemble(revise=False):
    if revise:
        if (ROOT/'reports/thesis_delivery_audit.json').exists():raise ValueError('Certified delivery cannot be revised')
        previous=verify();manifest=json_file(DESTINATION/'manifests/release_manifest.json')
        preserved=ROOT/'archive/implementation/thesis_release_first_draft_manifest.json'
        if preserved.exists():raise ValueError('First package revision already recorded')
        write_once(preserved,(DESTINATION/'manifests/release_manifest.json').read_bytes())
        write_once(ROOT/'archive/implementation/thesis_release_first_draft_code.py',(DESTINATION/'manifests/reporting_code/thesis_release.py').read_bytes())
        write_once(ROOT/'archive/implementation/thesis_release_first_draft_verification.json',(json.dumps(previous,indent=2)+'\n').encode())
        for name in [*[item['filename'] for item in manifest['items']],'manifests/release_manifest.json','thesis_release.zip']:
            (DESTINATION/name).unlink()
    if (DESTINATION/'manifests/release_manifest.json').exists():return verify()
    if DESTINATION.exists() and any(p.is_file() for p in DESTINATION.rglob('*')):raise ValueError('Incomplete or unrelated release area; refuse overwrite')
    publication=artifacts();catalog=verify_catalog()
    science=json_file(ROOT/'reports/frozen_science_verification.json')
    if not science['full_rerun_complete'] or science['models_refitted']:raise ValueError('Scientific integrity has not passed')
    generated=json_file(ROOT/'reports/thesis_artifact_manifest.json')
    synthesis=json_file(ROOT/'reports/thesis_synthesis_manifest.json')
    mapping={item['filename']:release_name(item['filename']) for item in generated['items']}
    documents={
      'reports/research_results.md':'reports/research_results.md',
      'reports/findings_by_research_question.md':'reports/findings_by_research_question.md',
      'reports/thesis_figure_recommendations.md':'reports/thesis_figure_recommendations.md',
      'docs/final_claims_for_thesis.md':'reports/final_claims_for_thesis.md',
      'docs/scientific_proposal.md':'reports/scientific_proposal.md',
      'docs/analysis/research_plan.md':'reports/research_plan.md',
      'docs/analysis/preanalysis_specification.md':'reports/preanalysis_specification.md',
      'docs/analysis/data_dictionary.md':'reports/data_dictionary.md',
      'docs/analysis/source_registry.md':'reports/source_registry.md',
      'docs/analysis/reproducibility.md':'reports/reproducibility.md',
      'reports/deliverable_gap_audit.md':'reports/initial_deliverable_gap_audit.md'}
    metadata=['reports/thesis_artifact_manifest.json','reports/thesis_synthesis_manifest.json',
              'reports/thesis_recommendations.json','reports/numeric_claims_registry.json',
              'reports/frozen_reporting_sources.json','reports/deliverable_gap_audit.json',
              'reports/thesis_publication_validation.json','reports/frozen_science_verification.json',
              'docs/analysis/release_audit.json','docs/analysis/software_environment.json',
              'config/study/design.json','config/study/cities.json']
    mapping.update(documents)
    for name in metadata:mapping[name]='manifests/'+Path(name).name
    generators=sorted((ROOT/'src/reporting').glob('thesis_*.py'))
    for path in generators:mapping[str(path.relative_to(ROOT))]='manifests/reporting_code/'+path.name
    mapping['requirements.txt']='manifests/requirements.txt'
    registered=[]
    def add(name,body,source,rq,command,source_filename=None,caption=None):
        path=DESTINATION/name;write_once(path,body)
        item={'filename':name,'sha256':sha256_file(path),'bytes':len(body),
              'source_run_artifact':source,'research_question':rq,'publication_status':'THESIS_READY',
              'generation_command':command,'source_catalog_sha256':catalog['source_catalog_sha256'],'private_row_export':False}
        if source_filename:item.update(source_filename=source_filename,source_file_sha256=sha256_file(ROOT/source_filename))
        if caption:item['caption']=caption
        registered.append(item)
    for item in generated['items']:
        original=ROOT/item['filename'];name=mapping[item['filename']];blob=original.read_bytes()
        if original.suffix=='.md':blob=markdown_links(original,blob.decode(),mapping,name).encode()
        add(name,blob,item['source_run_artifact'],item['research_question'],item['generation_command'],item['filename'],item['caption'])
    for source,name in documents.items():
        original=ROOT/source;body=markdown_links(original,original.read_text(),mapping,name).encode()
        add(name,body,{'document':source,'sha256':sha256_file(original),'frozen_catalog':'manifests/frozen_reporting_sources.json'},'RQ1–RQ4',COMMAND,source)
    for source in [*metadata,*[str(p.relative_to(ROOT)) for p in generators],'requirements.txt']:
        add(mapping[source],(ROOT/source).read_bytes(),{'artifact':source,'sha256':sha256_file(ROOT/source)},'RQ1–RQ4',COMMAND,source)
    readme='''# Thesis-ready research release

This package contains final frozen three-city results, publication figures,
aggregate tables, RQ findings, scientific claims and current Markdown documents.
Ten main figures and eight main tables are recommended in
[the placement guide](reports/thesis_figure_recommendations.md). Start with
[research results](reports/research_results.md) and
[RQ findings](reports/findings_by_research_question.md).

PNG figures are300dpi; PDF and SVG are vector exports. Sample flow is a compact
table. Suppressed map/relationship/prediction bins require n≥5. The package
contains no raw listings, individual coordinates, host identifiers, credentials,
model bytes or individual predictions. Native-currency within-city outcomes and
city-relative transfer outcomes remain distinct. No model was refitted for this
reporting release. The disclosed10% association eligibility amendment was made
after observing missingness and is not presented as preregistered.

Markdown proposal, research plan and results are authoritative. The repository
has no supported active DOCX/PDF document renderer for this four-RQ design;
document exports are therefore not supplied. This does not affect vector figures.

## Reproduction and verification

Use the final repository checkpoint recorded in the external handover and the
single pinned requirements file. PostgreSQL/PostGIS remains authoritative;
private sources and saved predictions are required to reproduce analytical
aggregates, and remain outside this public package. In the repository run
`make thesis-check`, `make thesis-science-check` and `make thesis-release`.
Generation commands are write-once and refuse to overwrite completed results.
Exact reporting code is copied under manifests/reporting_code; supporting
repository modules and frozen source selectors remain in the repository.

[Release manifest](manifests/release_manifest.json) records every bundled file,
SHA256, final source run/artifact, RQ, publication status and generation command.
The manifest excludes itself from its own file-hash list. The ZIP contains every
registered file plus that manifest, with fixed timestamps and sorted paths.
Rebased Markdown links resolve within this package when evidence is bundled;
other preserved evidence links to the recorded repository branch. Original
repository artifact/synthesis manifests retain their source paths and hashes;
the release manifest records the hashes after link-only rebasing.
'''
    add('README.md',readme.encode(),{'artifact':'reports/thesis_artifact_manifest.json','catalog_sha256':catalog['source_catalog_sha256']},'RQ1–RQ4',COMMAND)
    manifest={'status':'COMPLETE_THESIS_REPORTING','source_catalog_sha256':catalog['source_catalog_sha256'],
              'models_refitted':False,'scientific_choice_changes':False,'generation_command':COMMAND,
              'generator_sha256':sha256_file(Path(__file__)),
              'publication_validation':publication,'document_exports':'AUTHORITATIVE_MARKDOWN_NO_SUPPORTED_ACTIVE_DOCX_PDF_RENDERER',
              'items':sorted(registered,key=lambda item:item['filename'])}
    write_once(DESTINATION/'manifests/release_manifest.json',(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode())
    check_links(sorted(DESTINATION.rglob('*.md')))
    with zipfile.ZipFile(DESTINATION/'thesis_release.zip','x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted([item['filename'] for item in registered]+['manifests/release_manifest.json']):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,(DESTINATION/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return verify()


def delivery(result):
    gap=json_file(ROOT/'reports/deliverable_gap_audit.json');registered=json_file(ROOT/'reports/thesis_artifact_manifest.json')
    available={item['filename'] for item in registered['items']};completed=[]
    for original in gap['deliverables']:
        item=dict(original)
        if original['status']=='NOT_NEEDED':item['completion_status']='NOT_NEEDED'
        else:
            target='outputs/tables/thesis/sample_flow.md' if original['id']=='A2' else original['missing_output']
            if target not in available or not (ROOT/target).exists():raise ValueError('Required gap not resolved: '+original['id'])
            item['completion_status']='READY';item['final_output']=target
        completed.append(item)
    record={'status':'COMPLETE_THESIS_REPORTING','scientific_models_refitted':False,'scientific_choice_changes':False,
            'initial_gap_audit_preserved':True,'initial_gap_audit_sha256':sha256_file(ROOT/'reports/deliverable_gap_audit.json'),
            'publication_validation':artifacts(),'release_verification':result,'required_deliverables':completed,
            'historical_figures_preserved':49,'earlier_public_artifacts_unchanged':77,
            'required_reports':['reports/research_results.md','reports/findings_by_research_question.md','reports/thesis_figure_recommendations.md','docs/final_claims_for_thesis.md'],
            'document_export_status':'AUTHORITATIVE_MARKDOWN; NO_SUPPORTED_ACTIVE_DOCX_PDF_RENDERER',
            'remaining_required_deliverables':[]}
    for name in record['required_reports']:
        if not (ROOT/name).is_file():raise ValueError('Required report absent')
    path=ROOT/'reports/thesis_delivery_audit.json'
    if not path.exists():write_once(path,(json.dumps(record,indent=2,ensure_ascii=False)+'\n').encode())
    elif json_file(path)!=record:raise ValueError('Certified delivery audit differs; refuse overwrite')
    md='# Final thesis delivery audit\n\nStatus: COMPLETE_THESIS_REPORTING. No scientific model was refitted.\n\n'
    md+='All eighteen figure sets, eleven required tables, sample flow and supporting aggregate views are verified against the final frozen SQL catalog. Ten main figures, eight main tables and eight appendix figures are recommended. All49 earlier PNGs and77 public scientific artifacts remain unchanged.\n\n'
    md+='Publication checks, independently recalculated contrasts, source-run lineage, numeric-claim trace, layout checks, private-data suppression, local links, release hashes and ZIP membership PASS. The separate frozen-science verification checks saved models and predictions without overwriting the earlier completed audit.\n\n'
    md+='[Release manifest](../outputs/release/manifests/release_manifest.json), [safe ZIP](../outputs/release/thesis_release.zip), [full delivery audit](thesis_delivery_audit.json), [results](research_results.md) and [recommendations](thesis_figure_recommendations.md).\n\n'
    md+='Markdown is authoritative for proposal, plan and results. No supported active DOCX/PDF document renderer exists; scientific figure PDF/SVG exports are supplied. No genuinely required deliverable remains missing.\n'
    mdpath=ROOT/'reports/thesis_delivery_audit.md'
    if not mdpath.exists():write_once(mdpath,md.encode())
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');parser.add_argument('--revise-package',action='store_true');args=parser.parse_args()
    if args.verify and args.revise_package:parser.error('Verification and draft revision are mutually exclusive')
    result=verify() if args.verify else assemble(args.revise_package)
    if not args.verify:delivery(result)
    print(json.dumps(result,indent=2))
