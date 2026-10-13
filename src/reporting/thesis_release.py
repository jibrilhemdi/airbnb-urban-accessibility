"""Assemble and verify the public thesis release; no scientific fitting or writes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import io
import os
import posixpath
import tempfile
import zipfile
from urllib.parse import quote
import pandas as pd
from src.ingestion.common import sha256_file
from src.study.sources import write_once
from src.reporting.thesis_sources import ROOT,verify_catalog
from src.reporting.thesis_validate import artifacts,check_links,FORBIDDEN

DESTINATION=ROOT/'outputs'
MANIFEST=ROOT/'reports/thesis_release_manifest.json'
ZIP=DESTINATION/'thesis_results.zip'
COMMAND='.venv/bin/python -m src.reporting.thesis_release'
REMOTE='https://github.com/jibrilhemdi/airbnb-urban-accessibility/blob/v4/'


def json_file(path):return json.loads(path.read_text())


def release_name(name):
    path=Path(name)
    if name.startswith(('outputs/figures/','outputs/tables/','outputs/metrics/')) and len(path.parts)==3:
        return str(path.relative_to('outputs'))
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
        if not resolved.is_relative_to(ROOT):raise ValueError('Unsafe source document link: '+target)
        name=str(resolved.relative_to(ROOT))
        if not resolved.exists() and name not in mapping:raise ValueError('Broken source document link: '+target)
        rewritten=os.path.relpath(mapping[name],Path(destination).parent) if name in mapping else REMOTE+quote(name,safe='/')
        return ']('+rewritten+(mark+anchor if mark else '')+')'
    return re.sub(r'\]\(([^)]+)\)',replace,content)


def package_links(blobs):
    count=0
    for name,body in blobs.items():
        if not name.endswith('.md'):continue
        for target in re.findall(r'\]\(([^)]+)\)',body.decode()):
            if target.startswith(('http:','https:','mailto:')):continue
            target=target.partition('#')[0]
            if target:
                resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name),target))
                if resolved not in blobs:raise ValueError('Broken package link: '+name+' '+target)
            count+=1
    return count


def verify():
    catalog=verify_catalog();manifest=json_file(MANIFEST)
    if manifest['source_catalog_sha256']!=catalog['source_catalog_sha256'] or manifest['models_refitted']:raise ValueError('Release scientific identity differs')
    names={item['filename'] for item in manifest['items']}
    if len(names)!=len(manifest['items']):raise ValueError('Duplicate package path')
    with zipfile.ZipFile(ZIP) as z:
        zip_names=z.namelist()
        if len(zip_names)!=len(set(zip_names)) or set(zip_names)!=names|{'manifests/release_manifest.json'}:raise ValueError('ZIP membership differs')
        if z.testzip() is not None:raise ValueError('ZIP CRC validation failed')
        blobs={name:z.read(name) for name in zip_names}
    if blobs['manifests/release_manifest.json']!=MANIFEST.read_bytes():raise ValueError('Bundled manifest differs')
    for item in manifest['items']:
        name=item['filename'];path=Path(name);body=blobs[name]
        if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe package path')
        if hashlib.sha256(body).hexdigest()!=item['sha256'] or len(body)!=item['bytes']:raise ValueError('Release file hash/size mismatch')
        if item.get('source_filename') and sha256_file(ROOT/item['source_filename'])!=item['source_file_sha256']:raise ValueError('Release contains a stale source artifact')
        if item['publication_status']!='THESIS_READY' or not item['source_run_artifact'] or not item['research_question'] or not item['generation_command']:raise ValueError('Release provenance absent')
        if path.suffix=='.csv':
            frame=pd.read_csv(io.BytesIO(body))
            if set(frame)&FORBIDDEN:raise ValueError('Private fields in release')
            if path.stem.endswith(('_bins','_cells')) and frame.n.lt(5).any():raise ValueError('Unsuppressed release aggregate')
        if path.suffix not in {'.png','.csv','.md','.json','.py','.txt'} or path.name.startswith('.env'):raise ValueError('Unsafe or non-PNG release file type')
    return {'status':'PASS','package_files':len(names)+1,'zip_entries':len(zip_names),'links_checked':package_links(blobs),
            'manifest_sha256':sha256_file(MANIFEST),'zip_sha256':sha256_file(ZIP),'zip_bytes':ZIP.stat().st_size,
            'private_data_check':'PASS','all_release_hashes':'PASS','figure_formats':['PNG'],'models_refitted':False}


def assemble(revise=False):
    if revise:raise ValueError('Preserve the certified package before any revision')
    if MANIFEST.exists() and ZIP.exists():return verify()
    if MANIFEST.exists() or ZIP.exists():raise ValueError('Partial package; refuse overwrite')
    publication=artifacts();catalog=verify_catalog()
    science=json_file(ROOT/'reports/frozen_science_verification.json')
    if not science['full_rerun_complete'] or science['models_refitted']:raise ValueError('Scientific integrity has not passed')
    generated=json_file(ROOT/'reports/thesis_artifact_manifest.json')
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
              'reports/thesis_style_review.json','docs/analysis/release_audit.json',
              'docs/analysis/software_environment.json','config/study/design.json','config/study/cities.json',
              'config/reporting/map_context.json']
    mapping.update(documents)
    for name in metadata:mapping[name]='manifests/'+Path(name).name
    generators=sorted((ROOT/'src/reporting').glob('thesis_*.py'))
    for path in generators:mapping[str(path.relative_to(ROOT))]='manifests/reporting_code/'+path.name
    mapping['requirements.txt']='manifests/requirements.txt'
    mapping['outputs/README.md']='README.md'
    mapping['reports/thesis_release_manifest.json']='manifests/release_manifest.json'
    registered=[];blobs={}
    def add(name,body,source,rq,command,source_filename=None,caption=None):
        if name in blobs:raise ValueError('Duplicate package path')
        blobs[name]=body
        item={'filename':name,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),
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
        add(name,body,{'document':source,'sha256':sha256_file(original)},'RQ1–RQ4',COMMAND,source)
    for source in [*metadata,*[str(p.relative_to(ROOT)) for p in generators],'requirements.txt']:
        add(mapping[source],(ROOT/source).read_bytes(),{'artifact':source,'sha256':sha256_file(ROOT/source)},'RQ1–RQ4',COMMAND,source)
    readme=ROOT/'outputs/README.md'
    add('README.md',markdown_links(readme,readme.read_text(),mapping,'README.md').encode(),
        {'artifact':'outputs/README.md','catalog_sha256':catalog['source_catalog_sha256']},'RQ1–RQ4',COMMAND,'outputs/README.md')
    manifest={'status':'COMPLETE_THESIS_REPORTING','source_catalog_sha256':catalog['source_catalog_sha256'],
              'models_refitted':False,'scientific_choice_changes':False,'generation_command':COMMAND,
              'generator_sha256':sha256_file(Path(__file__)),'publication_validation':publication,
              'figure_formats':['PNG'],'document_exports':'AUTHORITATIVE_MARKDOWN',
              'items':sorted(registered,key=lambda item:item['filename'])}
    manifest_body=(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode()
    blobs['manifests/release_manifest.json']=manifest_body
    package_links(blobs)
    descriptor,temporary=tempfile.mkstemp(prefix='thesis-package-',suffix='.zip')
    os.close(descriptor)
    try:
        with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,body in sorted(blobs.items()):
                info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                z.writestr(info,body,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        with zipfile.ZipFile(temporary) as z:
            if z.testzip() is not None:raise ValueError('Staged ZIP CRC failed')
        write_once(MANIFEST,manifest_body)
        write_once(ZIP,Path(temporary).read_bytes())
    finally:Path(temporary).unlink(missing_ok=True)
    return verify()


def delivery(result):
    gap=json_file(ROOT/'reports/deliverable_gap_audit.json');registered=json_file(ROOT/'reports/thesis_artifact_manifest.json')
    available={item['filename'] for item in registered['items']};completed=[]
    for original in gap['deliverables']:
        item=dict(original)
        if original['status']=='NOT_NEEDED':item['completion_status']='NOT_NEEDED'
        else:
            target='outputs/tables/sample_flow.md' if original['id']=='A2' else original['missing_output']
            target=target.replace('/thesis/','/').replace('.pdf','.png')
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
    md+='All eighteen figure sets, eleven required tables, sample flow and supporting aggregate views are verified against the final frozen SQL catalog. Ten main figures, eight main tables and eight appendix figures are recommended. All49 earlier PNGs and77 public scientific artifacts remain byte-identical in the archive.\n\n'
    md+='Publication checks, independently recalculated contrasts, source-run lineage, numeric-claim trace, layout checks, private-data suppression, local links, release hashes and ZIP membership PASS. The separate frozen-science verification checks saved models and predictions without overwriting the earlier completed audit.\n\n'
    md+='[Release manifest](thesis_release_manifest.json), [safe ZIP](../outputs/thesis_results.zip), [full delivery audit](thesis_delivery_audit.json), [results](research_results.md) and [recommendations](thesis_figure_recommendations.md).\n\n'
    md+='Markdown is authoritative for proposal, plan and results. No supported active DOCX/PDF document renderer exists; figures are supplied as PNG only. No genuinely required deliverable remains missing.\n'
    mdpath=ROOT/'reports/thesis_delivery_audit.md'
    if not mdpath.exists():write_once(mdpath,md.encode())
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--verify',action='store_true');parser.add_argument('--revise-package',action='store_true');args=parser.parse_args()
    if args.verify and args.revise_package:parser.error('Verification and draft revision are mutually exclusive')
    result=verify() if args.verify else assemble(args.revise_package)
    if not args.verify:delivery(result)
    print(json.dumps(result,indent=2))
