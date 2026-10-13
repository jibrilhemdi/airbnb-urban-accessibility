"""Render/check two research DOCX copies from canonical Markdown, never run analysis."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from lxml import etree
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
ARCHIVE=ROOT/'archive/before_research_documents'
MANIFEST=ROOT/'reports/research_document_manifest.json'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}
DOCS=[('docs/design/scientific_proposal.md','docs/design/scientific_proposal.docx','scientific_proposal.docx'),
      ('docs/design/end_to_end_research_plan.md','docs/design/end_to_end_research_plan.docx','end_to_end_research_plan.docx')]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def plain(value):
    value=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',value)
    return value.replace('**','').replace('`','').replace('\\|','|')


def blocks(markdown):
    """The document subset: headings, paragraphs, lists and pipe tables."""
    lines=markdown.splitlines();result=[];index=0
    while index<len(lines):
        line=lines[index].strip()
        if not line:index+=1;continue
        if line.startswith('|'):
            rows=[]
            while index<len(lines) and lines[index].strip().startswith('|'):
                cells=[cell.strip() for cell in lines[index].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-{3,}:?',c) for c in cells):rows.append(cells)
                index+=1
            if len({len(row) for row in rows})!=1:raise ValueError('Malformed Markdown table')
            result.append(('table',rows));continue
        heading=re.match(r'^(#{1,6})\s+(.*)$',line)
        if heading:result.append(('heading',(len(heading[1]),heading[2])));index+=1;continue
        if re.match(r'^(?:[-*]|\d+\.)\s+',line):result.append(('list',line));index+=1;continue
        paragraph=[line];index+=1
        while index<len(lines) and lines[index].strip() and not re.match(r'^(?:#|\||[-*]\s|\d+\.\s)',lines[index].strip()):
            paragraph.append(lines[index].strip());index+=1
        result.append(('paragraph',' '.join(paragraph)))
    return result


def el(name,**attrs):return etree.Element('{'+W+'}'+name,{'{'+W+'}'+k:str(v) for k,v in attrs.items()})


def inline(parent,value,*,bold=False,small=False):
    value=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',value)
    for token in re.split(r'(\*\*.*?\*\*|`.*?`)',value):
        if not token:continue
        emphasis=token.startswith('**') and token.endswith('**')
        text=token[2:-2] if emphasis else token.strip('`') if token.startswith('`') else token
        run=el('r');props=el('rPr')
        if emphasis or bold:props.append(el('b'))
        if small:props.extend([el('sz',val=18),el('szCs',val=18)])
        if len(props):run.append(props)
        t=el('t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text
        run.append(t);parent.append(run)


def paragraph(text,style=None,*,small=False,bold=False):
    p=el('p')
    if style:
        props=el('pPr');props.append(el('pStyle',val=style));p.append(props)
    inline(p,text,small=small,bold=bold);return p


def table(rows,width):
    tbl=el('tbl');props=el('tblPr');props.append(el('tblStyle',val='TableGrid'))
    props.append(el('tblW',w=width,type='dxa'));props.append(el('tblLayout',type='fixed'))
    margins=el('tblCellMar')
    for side in ['top','left','bottom','right']:margins.append(el(side,w=70,type='dxa'))
    props.append(margins);tbl.append(props)
    count=len(rows[0]);column=int(width/count);grid=el('tblGrid')
    for _ in range(count):grid.append(el('gridCol',w=column))
    tbl.append(grid)
    for index,row in enumerate(rows):
        tr=el('tr');tr_props=el('trPr');tr_props.append(el('cantSplit'))
        if index==0:tr_props.append(el('tblHeader'))
        tr.append(tr_props)
        for value in row:
            cell=el('tc');cell_props=el('tcPr');cell_props.append(el('tcW',w=column,type='dxa'))
            if index==0:cell_props.append(el('shd',fill='E7EEF1'))
            cell.append(cell_props);cell.append(paragraph(value,small=True,bold=index==0));tr.append(cell)
        tbl.append(tr)
    return tbl


def source_content(path):
    parsed=blocks(path.read_text());expected=[]
    for kind,value in parsed:
        if kind=='table':expected.extend(plain(c) for row in value for c in row)
        else:expected.append(plain(value[1] if kind=='heading' else value))
    return parsed,expected


def verify_numerical_tables():
    """Reproduce document tables from the checksum-pinned final exports."""
    from src.reporting.thesis_tables import markdown
    samples=pd.read_csv(ROOT/'outputs/tables/city_sample_summary.csv')
    counts=samples[['city','raw_listings','eligible_conventional_dwellings','reference_n','prediction_n','association_n','operational_neighbourhoods']].copy()
    counts.columns=['City','Raw listings','Conventional entire dwellings','Positive-price reference N','Prediction N','Association N','Holdout groups']
    references=samples[['city','reference_n','reference_mean_log_price','reference_geometric_mean_native_price','currency']].copy()
    references.columns=['City','Reference N','Mean log price','Geometric mean asking price','Currency']
    performance=pd.read_csv(ROOT/'outputs/tables/primary_predictive_performance.csv')
    scores=performance.loc[performance.estimator.eq('XGBoost')].pivot(index='city',columns='model',values='rmse').reindex(['Copenhagen','Oslo','Stockholm'])[['M0','ME','MW','MEW']].reset_index()
    scores.columns=['City','M0','ME','MW','MEW']
    generated=[blocks(markdown(frame,precision=precision))[0][1] for frame,precision in [(counts,0),(references,6),(scores,6)]]
    for source,indices in [('docs/design/scientific_proposal.md',[1,5,6]),('docs/design/end_to_end_research_plan.md',[2,4,5])]:
        tables=[value for kind,value in blocks((ROOT/source).read_text()) if kind=='table']
        for index,expected in zip(indices,generated,strict=True):
            if tables[index]!=expected:raise ValueError('Document numerical table differs from final results: '+source)
    names=['outputs/tables/city_sample_summary.csv','outputs/tables/primary_predictive_performance.csv']
    return {'tables_independently_reproduced':6,'sources':{name:digest(ROOT/name) for name in names},'status':'PASS'}


def generate(source,destination,template):
    if destination.exists():raise ValueError('Preserve an existing Word copy before regeneration: '+str(destination))
    parsed,_=source_content(source)
    with ZipFile(template) as original:
        doc=etree.fromstring(original.read('word/document.xml'));body=doc.find('w:body',NS)
        if body is None:raise ValueError('DOCX has no body')
        section=deepcopy(body.find('w:sectPr',NS))
        for child in list(body):body.remove(child)
        size=section.find('w:pgSz',NS);margin=section.find('w:pgMar',NS)
        width=int(size.get('{'+W+'}w'))-int(margin.get('{'+W+'}left'))-int(margin.get('{'+W+'}right'))
        for kind,value in parsed:
            if kind=='table':body.append(table(value,width))
            elif kind=='heading':
                level,text=value;body.append(paragraph(text,'Title' if level==1 else 'Heading'+str(min(level-1,3))))
            else:body.append(paragraph(value,'ListParagraph' if kind=='list' else 'Normal'))
        body.append(section)
        data={'word/document.xml':etree.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)}
        core=etree.fromstring(original.read('docProps/core.xml'))
        metadata={'{http://purl.org/dc/elements/1.1/}title':plain(parsed[0][1][1]),
                  '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy':'Thesis research document exporter',
                  '{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}revision':'2',
                  '{http://purl.org/dc/terms/}modified':datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')}
        for name,value in metadata.items():
            node=core.find(name)
            if node is None:node=etree.SubElement(core,name)
            node.text=value
        data['docProps/core.xml']=etree.tostring(core,xml_declaration=True,encoding='UTF-8',standalone=True)
        # Keep original fonts, styles, margins, headers, page numbers and relationships.
        with ZipFile(destination,'x',compression=ZIP_DEFLATED,compresslevel=9) as output:
            for name in original.namelist():
                item=ZipInfo(name,date_time=(2026,10,14,0,0,0));item.compress_type=ZIP_DEFLATED
                output.writestr(item,data.get(name,original.read(name)))


def check_pair(source,destination,template):
    parsed,expected=source_content(source)
    with ZipFile(template) as previous,ZipFile(destination) as document:
        if set(previous.namelist())!=set(document.namelist()) or document.testzip():raise ValueError('DOCX package membership/CRC failed')
        for name in previous.namelist():
            if name not in {'word/document.xml','docProps/core.xml'} and previous.read(name)!=document.read(name):raise ValueError('Unexpected template change: '+name)
        for name in document.namelist():
            if name.endswith('.xml') or name.endswith('.rels'):etree.fromstring(document.read(name))
        root=etree.fromstring(document.read('word/document.xml'))
        actual=[''.join(p.xpath('.//w:t/text()',namespaces=NS)) for p in root.xpath('./w:body//w:p',namespaces=NS)]
        if actual!=expected:raise ValueError('Word content differs from canonical Markdown: '+str(destination))
        tables=root.xpath('./w:body/w:tbl',namespaces=NS)
        if len(tables)!=sum(k=='table' for k,_ in parsed):raise ValueError('Table count differs')
        if not all(t.xpath('./w:tr[1]/w:trPr/w:tblHeader',namespaces=NS) for t in tables):raise ValueError('Table headers will not repeat')
        return {'markdown':str(source.relative_to(ROOT)),'markdown_sha256':digest(source),
                'docx':str(destination.relative_to(ROOT)),'docx_sha256':digest(destination),
                'template':str(template.relative_to(ROOT)),'template_sha256':digest(template),
                'text_and_tables_match':'PASS','paragraphs':len(actual),'tables':len(tables),
                'package_XML_CRC':'PASS','template_styles_headers_footers_preserved':True}


def run(check=False):
    archive=json.loads((ARCHIVE/'manifest.json').read_text())
    for item in [*archive['files'],*archive['attached_inputs']]:
        if digest(ROOT/item['archived_path'])!=item['sha256']:raise ValueError('Original document/input changed')
    for name,expected in archive['frozen_output_hashes'].items():
        if digest(ROOT/name)!=expected:raise ValueError('Scientific output changed')
    numerical=verify_numerical_tables()
    results=[]
    for md,word,name in DOCS:
        source=ROOT/md;destination=ROOT/word;template=ARCHIVE/'attachments'/name
        if not check:generate(source,destination,template)
        results.append(check_pair(source,destination,template))
    record={'status':'PASS','updated_date':'2026-10-14','canonical_format':'Markdown',
            'export_scope':'Scientific proposal and research plan DOCX only; no PDF/results-report renderer',
            'generation_command':'.venv/bin/python scripts/update_research_documents.py',
            'generator_sha256':digest(Path(__file__)),'documents':results,
            'numerical_table_verification':numerical,
            'attached_document_instructions_executed':False,'models_refitted':False,
            'frozen_scientific_outputs_unchanged':len(archive['frozen_output_hashes']),
            'preservation_manifest':'archive/before_research_documents/manifest.json',
            'pending_user_output_deletions_preserved':archive['pending_user_deletions_preserved']}
    if check:
        if json.loads(MANIFEST.read_text())!=record:raise ValueError('Document generation manifest differs')
    else:
        with MANIFEST.open('x') as handle:handle.write(json.dumps(record,indent=2)+'\n')
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    print(json.dumps(run(parser.parse_args().check),indent=2))
