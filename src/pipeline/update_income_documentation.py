"""Add a truthful, reversible income-review addendum to the two V3 documents."""
from __future__ import annotations

import shutil
from pathlib import Path
from zipfile import ZipFile

from lxml import etree

from src.ingestion.common import PROJECT_ROOT, sha256_file, write_json

NAMES=('airbnb_urban_accessibility_end_to_end_research_plan_v3.docx',
       'airbnb_urban_accessibility_scientific_thesis_proposal_v3.docx')
from src.pipeline.qualified_income import METHODS_TEXT, QUALIFICATION, TRANSFORMATION
PARAGRAPHS=(
    'Version 3 income protocol amendment — accepted 4 October 2026',
    'This explicit protocol decision supersedes earlier pending income prerequisites and municipal-only source proposals. Income remains a core M0 predictor; ME, MW and MEW inherit it. Frederiksberg remains one of eleven peer analysis areas, without a special dummy or CTX model family.',
    METHODS_TEXT,
    'The transparent variable is equiv_disposable_income_2024 (DKK), with income_100k_dkk = equiv_disposable_income_2024 / 100000 for modelling. Both sources use 2024 and the frozen transformation '+TRANSFORMATION+'. IFOR35 selects nominal current prices (006); KKIND5 raw price basis remains not_confirmed. Metadata harmonisation_status = qualified; preflight decision = qualified_accepted. '+QUALIFICATION,
    'Supportive QA compares Copenhagen published municipality totals: KKIND5 340620.1 DKK and IFOR35 340949.1 DKK; signed difference -329 DKK, absolute difference 329 DKK, relative difference -0.0964953%. Tenth-decile difference is -3376 DKK. This does not prove exact equivalence or reconstruct a population-weighted district total. Missing income-eligible counts remain missing.',
    'Mandatory M0_no_income, ME_no_income, MW_no_income and MEW_no_income omit only income. They use the same frozen sample, saved random-five and geographic-eleven outer folds and training-only inner-four folds, preprocessing, thirty XGBoost candidates and tuning budget. Report OLS accessibility coefficients, RMSE, MAE, R-squared, paired delta-RMSE and per-area geographic results. Prespecified direction/ranking and coefficient-magnitude sensitivity flags are frozen in config/qualified_income_decision.json before model fitting.',
    'The active eleven-row income table is authoritative in PostgreSQL v3_features.qualified_area_income and records source institution, table, year, price basis, ten decile means, formula, final value, source SHA-256 and qualification. Preflight checks actual immutable sources, selections, deciles, year, common transformation, provenance and mandatory robustness. Earlier KKIND3/INDKP106, KKIND5/IFOR35 and municipal investigations remain archived. No renewed municipal-source search or message is authorised by this amendment.',
    'Limitations: qualified cross-source comparability leaves some table-specific processing and KKIND5 raw price-basis details unresolved. The mandatory no-income analysis assesses whether accessibility conclusions depend on that control. This limitation is stated here and in Methods/Data; results must not assert perfectly identical definitions.',
)


def update():
    root=PROJECT_ROOT/'docs/design'
    baseline=root/'income_review_baseline'
    baseline.mkdir(parents=True,exist_ok=True)
    results=[]
    w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    for name in NAMES:
        path=root/name;original=baseline/name
        if not original.exists():
            shutil.copy2(path,original)
        with ZipFile(original) as source:
            document=etree.fromstring(source.read('word/document.xml'))
            body=document.find(w+'body')
            if body is None:
                raise RuntimeError('No Word body in '+name)
            section=body.find(w+'sectPr')
            for i,content in enumerate(PARAGRAPHS):
                p=etree.Element(w+'p')
                if i==0:
                    properties=etree.SubElement(p,w+'pPr')
                    style=etree.SubElement(properties,w+'pStyle');style.set(w+'val','Heading2')
                run=etree.SubElement(p,w+'r');text=etree.SubElement(run,w+'t');text.text=content
                if section is None: body.append(p)
                else: body.insert(body.index(section),p)
            payload=etree.tostring(document,xml_declaration=True,encoding='UTF-8',standalone=True)
            temporary=path.with_suffix('.docx.tmp')
            with ZipFile(temporary,'w') as target:
                for item in source.infolist():
                    target.writestr(item,payload if item.filename=='word/document.xml' else source.read(item.filename))
        temporary.replace(path)
        with ZipFile(original) as before,ZipFile(path) as after:
            if before.namelist()!=after.namelist():raise RuntimeError('DOCX member set changed')
            for member in before.namelist():
                if member!='word/document.xml' and before.read(member)!=after.read(member):
                    raise RuntimeError('Unexpected supporting-document part modification: '+member)
            texts=etree.fromstring(after.read('word/document.xml')).findall('.//'+w+'t')
            if sum(t.text==PARAGRAPHS[0] for t in texts)!=1:raise RuntimeError('Duplicate income addendum')
        results.append({'document':path.relative_to(PROJECT_ROOT).as_posix(),'sha256':sha256_file(path),
                        'baseline':original.relative_to(PROJECT_ROOT).as_posix(),'baseline_sha256':sha256_file(original),
                        'change':'Current qualified income amendment; historical addenda archived; every other DOCX member unchanged'})
    write_json(PROJECT_ROOT/'outputs/tables/reproducibility/income_document_updates.json',
               {'version':'income_document_review_v3','status':'qualified_accepted','documents':results})
    return results


if __name__=='__main__':
    update()
