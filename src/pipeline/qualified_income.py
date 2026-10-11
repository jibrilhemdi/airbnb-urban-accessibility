"""Frozen qualified income decision; strict source validation and SQL adoption."""
from __future__ import annotations
import json
from decimal import Decimal
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT, sha256_file, read_manifest, write_json
from src.pipeline.protocol import AREA_NAMES, canonical_hash
from src.pipeline.investigate_income_harmonisation import candidates, diagnostics, decile_mean
from src.pipeline.storage import export

CONFIG_PATH=PROJECT_ROOT/'config/qualified_income_decision.json'
TRANSFORMATION='(d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8 + d9 + d10) / 10'
QUALIFICATION=('Pragmatically harmonised equivalised disposable income; exact table-specific '
    'weighting, finite-count/tie handling, eligibility, variable version, income-treatment and '
    'KKIND5 raw price-basis details cannot be proven identical. Equal weighting follows '
    'the conceptual ten equal person groups; no model-dependent weights are used.')
METHODS_TEXT=("Area income is operationalised as 2024 equivalised disposable income derived from decile means. "
    "Copenhagen city-district values use Copenhagen Municipality's KKIND5, while Frederiksberg uses Statistics "
    "Denmark's nominal IFOR35. Both sources represent closely aligned equivalised-disposable-income concepts "
    "and use ten person-based decile groups, but some table-specific processing details cannot be proven identical. "
    "The measure is therefore treated as pragmatically harmonised. All primary models include the measure, "
    "and a prespecified no-income robustness analysis tests whether substantive accessibility conclusions "
    "depend on this cross-source context variable.")

def source_rows():
    manifest={e['local_path']:e for e in read_manifest()['files']}
    selected=[r for r in candidates() if r['analysis_area'] and
              (r['source_table']=='KKIND5' or r.get('price_unit_code')=='006')]
    rows=[]
    for r in selected:
        e=manifest[r['source_path']]
        rows.append({**{k:r[k] for k in ['analysis_area','analysis_area_name','source_table','source_geography',
             'year','price_basis','deciles','source_path','source_checksum']},
            'source_institution':'Copenhagen Municipality' if r['source_table']=='KKIND5' else 'Statistics Denmark',
            'source_url':e['source_url'],'acquired_at_utc':e['downloaded_at_utc'],
            'geographic_extent':e['geographic_extent'],'unit':'DKK',
            'transformation':TRANSFORMATION,'equiv_disposable_income_2024':str(decile_mean(r['deciles'])),
            'harmonisation_status':'qualified','qualification':QUALIFICATION,
            'eligible_person_count':None})
    if len(rows)!=11 or {r['analysis_area'] for r in rows}!=set(AREA_NAMES):
        raise RuntimeError('Qualified income requires the eleven official peer areas')
    return sorted(rows,key=lambda r:r['analysis_area'])

def validate(design):
    decision=design['income_harmonisation']
    if decision.get('status')!='qualified_accepted':
        raise RuntimeError('Income decision '+str(decision.get('status'))+' is not qualified_accepted: '+decision.get('reason',''))
    if sha256_file(CONFIG_PATH)!=decision.get('decision_sha256'):
        raise RuntimeError('Frozen qualified income decision changed')
    frozen=json.loads(CONFIG_PATH.read_text())
    if frozen['year']!=2024 or frozen['transformation']!=TRANSFORMATION or frozen['harmonisation_status']!='qualified':
        raise RuntimeError('Income year, transformation or qualification changed')
    if frozen['qualification']!=QUALIFICATION or frozen['methods_text']!=METHODS_TEXT:
        raise RuntimeError('Income qualification is absent or changed')
    for path,digest in frozen['source_sha256'].items():
        if not (PROJECT_ROOT/path).is_file() or sha256_file(PROJECT_ROOT/path)!=digest:
            raise RuntimeError('Income source or selection missing/changed: '+path)
    # Parsers validate actual CSV years, deciles, source labels and official crosswalk.
    rows=source_rows()
    if rows!=frozen['expected_records']:
        raise RuntimeError('Actual deciles, transformation or provenance differ from frozen income decision')
    robustness=design.get('no_income_robustness',{})
    if robustness!=frozen['no_income_robustness'] or not robustness.get('enabled') or not robustness.get('mandatory'):
        raise RuntimeError('Mandatory no-income robustness is absent/changed')
    from src.pipeline.model_specification import FEATURES, NO_INCOME_FEATURES
    for name,cols in FEATURES.items():
        if NO_INCOME_FEATURES[name+'_no_income']!=tuple(c for c in cols if c!='income_100k_dkk'):
            raise RuntimeError('No-income models must omit only income')
    if design['candidate_count']!=30 or design['inner_folds']!=4:
        raise RuntimeError('Frozen income robustness tuning budget changed')
    return {'status':'qualified_accepted','harmonisation_status':'qualified','year':2024,
        'analysis_areas':11,'decile_cells':110,'missing_decile_cells':0,
        'transformation':TRANSFORMATION,'decision_sha256':sha256_file(CONFIG_PATH),
        'source_records_sha256':canonical_hash(rows),'qualification':QUALIFICATION,
        'no_income_robustness':robustness}

def verify_sql(conn,rows=None):
    expected=rows if rows is not None else source_rows()
    actual=conn.execute(text('SELECT record FROM v3_features.qualified_area_income ORDER BY analysis_area')).scalars().all()
    if actual!=expected:
        raise RuntimeError('Authoritative SQL income table differs from frozen source-derived eleven records')
    columns=conn.execute(text('SELECT i.analysis_area,i.reference_year,i.equiv_disposable_income_2024,'
        'i.harmonisation_status,trim(s.file_hash_sha256) AS source_checksum,s.relative_path '
        'FROM v3_features.qualified_area_income i JOIN meta.source_files s USING(source_file_id) ORDER BY i.analysis_area')).mappings().all()
    if len(columns)!=11:raise RuntimeError('Income SQL source registrations are incomplete')
    for c,r in zip(columns,expected,strict=True):
        if (c['analysis_area']!=r['analysis_area'] or c['reference_year']!=2024 or
            str(c['equiv_disposable_income_2024'])!=r['equiv_disposable_income_2024'] or
            c['harmonisation_status']!='qualified' or c['source_checksum']!=r['source_checksum'] or
            c['relative_path']!=r['source_path']):
            raise RuntimeError('Income SQL value, source registration or qualification differs from frozen record')
    return {'qualified_income_rows':len(actual),'records_sha256':canonical_hash(actual)}

def adopt():
    from src.pipeline.protocol import DESIGN
    from src.db.connection import get_engine
    from src.db.migrations import migrate
    result=validate(DESIGN);rows=source_rows();engine=get_engine()
    try:
        applied=migrate(engine)
        with engine.begin() as conn:
            existing=conn.scalar(text('SELECT count(*) FROM v3_features.qualified_area_income'))
            if existing:verify_sql(conn,rows)
            else:
                conn.execute(text('INSERT INTO v3_features.qualified_area_income '
                    '(analysis_area,reference_year,equiv_disposable_income_2024,harmonisation_status,source_file_id,record) '
                    'VALUES(:area,2024,:income,\'qualified\',:source,CAST(:record AS jsonb))'),
                    [dict(area=r['analysis_area'],income=r['equiv_disposable_income_2024'],
                        source=conn.scalar(text('SELECT source_file_id FROM meta.source_files WHERE file_hash_sha256=:sha'),
                                           {'sha':r['source_checksum']}),record=json.dumps(r)) for r in rows])
            verify_sql(conn,rows)
        with engine.connect() as conn:
            table=pd.read_sql(text('SELECT record FROM v3_features.qualified_area_income ORDER BY analysis_area'),conn)
            records=table.record.tolist()
        frame=pd.DataFrame(records);frame['deciles']=frame.deciles.map(json.dumps)
        export('area_context','qualified_area_income_2024.csv',frame)
        export('data','qualified_income_source_inventory.csv',frame)
        qa=diagnostics(candidates());qa.update(status='supportive_qa_only',scope='published municipality totals; no proof of exact equivalence')
        write_json(PROJECT_ROOT/'outputs/tables/area_context/qualified_income_qa.json',qa)
        write_json(PROJECT_ROOT/'outputs/tables/reproducibility/qualified_income_metadata.json',
            {**result,'applied_migrations':applied,'authority':'v3_features.qualified_area_income',
             'source_sha256':json.loads(CONFIG_PATH.read_text())['source_sha256'],
             'qualification_document':'reports/income_harmonisation_status.md',
             'source_code_sha256':sha256_file(Path(__file__)),'crs':'No spatial operation; official crosswalk EPSG:4326',
             'prior_investigations_preserved':True,'primary_models_fitted_by_income_adoption':False})
        lines=['# Version 3 qualified income protocol amendment','',METHODS_TEXT,'',
            'Accepted by explicit user decision on 4 October 2026. Preflight status: `qualified_accepted`; record metadata: `qualified`.','',
            '## Frozen source table','',frame[['analysis_area','analysis_area_name','source_table','equiv_disposable_income_2024']].to_string(index=False),'',
            'Each of the eleven areas has all ten observed decile means. Common transformation: `'+TRANSFORMATION+'`. '
            'Values are annual DKK; the model uses `income_100k_dkk = equiv_disposable_income_2024 / 100000`.','',
            'KKIND5 raw price basis remains `not_confirmed`; IFOR35 uses nominal current prices (`006`). '+QUALIFICATION,'',
            '## Supportive QA','',
            'Copenhagen published totals: KKIND5 340,620.1 DKK, nominal IFOR35 340,949.1 DKK; '
            'City minus national −329 DKK (absolute 329 DKK; −0.0964953%). Tenth-decile discrepancy: −3,376 DKK. '
            'This small aggregate difference supports the practical decision but does not prove exact equivalence. '
            'Eligible district/decile counts and a weighted district reconstruction remain NULL.','',
            '## Mandatory robustness and provenance','',
            'M0_no_income, ME_no_income, MW_no_income and MEW_no_income omit only income. They use the identical frozen '
            'sample, saved random-5/geographic-11 outer and four inner folds, training-only preprocessing, thirty '
            'XGBoost candidates and tuning budgets. Outputs compare OLS accessibility coefficients, RMSE, MAE, R², '
            'paired ΔRMSE and per-area geographic performance. Prespecified material-change flags are documented in '
            '`config/qualified_income_decision.json`; they never select the primary model.','',
            'The source table is authoritative in PostgreSQL `v3_features.qualified_area_income`; aggregate CSVs are exports. '
            'Every record retains institution/table/year/basis/deciles/transformation/value/source URL/acquisition/extent/SHA/qualification. '
            'Raw files and all earlier source investigations remain intact in `archive/income_investigations` and '
            '`reports/income_harmonisation_previous_sources.md`. The municipal investigation is historical evidence; '
            'it is not reopened and the unsent contact draft remains unsent. No CTX family or Frederiksberg dummy is added.','',
            '## Limitations','',
            'Qualified cross-source comparability leaves unresolved processing and price-basis details. '
            'The mandatory no-income analysis measures dependence of accessibility conclusions on that context control.','']
        (PROJECT_ROOT/'reports/income_harmonisation_status.md').write_text('\n'.join(lines))
        return result
    finally:engine.dispose()

if __name__=='__main__':print(json.dumps(adopt(),indent=2))
