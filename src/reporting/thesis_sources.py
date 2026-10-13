"""Read-only access to explicitly pinned final research packages for reporting."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import text
from shapely.geometry import shape
from src.ingestion.common import PROJECT_ROOT,sha256_file
from src.pipeline.protocol import canonical_hash
from src.pipeline.storage import json_records
from src.study.sources import get_engine,write_once
from src.study.specification import load_design,CITIES,MODELS
from src.study.store import read_package
from src.study.sample_freeze import records
from src.reporting.study_results import predictions
from src.study.archive import preserved_path

ROOT=PROJECT_ROOT
CATALOG=ROOT/'reports/frozen_reporting_sources.json'
SCHEMES=['neighbourhood','random']+[f'blocks_{size}m_origin_{origin}' for size in [1000,1500,2000] for origin in ['0_0','0p5_0p5']]
LABELS={'copenhagen':'Copenhagen','oslo':'Oslo','stockholm':'Stockholm'}


def capture():
    """Pin selectors and all existing immutable SQL identities before generation."""
    paths=['config/study/design.json','config/study/cities.json']
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'config/study').glob('*selection.json'))]
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'config/study').glob('results_*.json'))]
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'runs').rglob('*selection.json'))]
    paths += ['runs/transfer/selection.json']
    file_pins={p:sha256_file(ROOT/p) for p in sorted(set(paths))}
    engine=get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            packages=[dict(r) for r in conn.execute(text('SELECT run_id,city,family,summary_sha256,dependencies_sha256 FROM study.checkpoints ORDER BY run_id')).mappings()]
    finally:engine.dispose()
    existing=json.loads((ROOT/'docs/analysis/final_artifact_inventory.json').read_text())
    result={'purpose':'Reporting only; no fitted model or frozen analytical dependency may change',
            'design_id':'three_city_accessibility_transfer','files':file_pins,'sql_packages':packages,
            'sql_packages_sha256':canonical_hash(packages),'previous_public_artifacts':existing,
            'source_catalog_sha256':canonical_hash({'files':file_pins,'packages':packages}),
            'allowed_scientific_reconstruction':False,'models_refitted':False}
    write_once(CATALOG,(json.dumps(result,indent=2)+'\n').encode())
    return result


def verify_catalog():
    catalog=json.loads(CATALOG.read_text())
    for path,expected in catalog['files'].items():
        if sha256_file(ROOT/path)!=expected:raise ValueError('Frozen reporting selector/design changed: '+path)
    for item in catalog['previous_public_artifacts']:
        if sha256_file(preserved_path(item['path'],item['sha256']))!=item['sha256']:raise ValueError('Pre-existing completed public artifact changed')
    return catalog


def chosen(conn,name,family='reporting'):
    pointer=json.loads((ROOT/'config/study'/(name+'.json')).read_text());summaries={};refs=[]
    for city in CITIES:
        item=pointer[city];summary,deps=read_package(conn,item['run_id'],city,family)
        if canonical_hash(summary)!=item['summary_sha256']:raise ValueError('Selected final summary hash differs')
        if deps['design']['design_id']!='three_city_accessibility_transfer':raise ValueError('Historical scientific result forbidden')
        expected=load_design()[0]['models']
        if deps['design']['models']!=expected:raise ValueError('Different scientific model registry')
        summaries[city]=summary
        refs.append({'run_id':item['run_id'],'city':city,'family':family,'summary_sha256':item['summary_sha256'],
                     'selector':'config/study/'+name+'.json'})
    return summaries,refs


def load():
    """Never fit or write SQL; private rows remain in memory for safe aggregation."""
    catalog=verify_catalog();design,cities=load_design();engine=get_engine();data={'design':design,'cities':cities,'sources':{},'frames':{},'geometries':{},'primary_predictions':{},'transfer_predictions':{}}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            packages=[dict(r) for r in conn.execute(text('SELECT run_id,city,family,summary_sha256,dependencies_sha256 FROM study.checkpoints ORDER BY run_id')).mappings()]
            if canonical_hash(packages)!=catalog['sql_packages_sha256']:raise ValueError('Scientific SQL identity changed during reporting')
            roles={'sample':('sample_selection','sample'),'geography':('geography_selection','geography'),
                   'reference':('reference_selection','reference'),'association':('association_selection','reporting'),
                   'spatial':('spatial_diagnostic_selection','reporting'),'robustness':('robustness_results_selection','reporting'),
                   'interpretation':('interpretation_selection','reporting')}
            for role,(name,family) in roles.items():data[role],data['sources'][role]=chosen(conn,name,family)
            data['validation']={}
            for scheme in SCHEMES:
                data['validation'][scheme],data['sources'][scheme]=chosen(conn,'results_'+scheme)
            data['transfer'],data['sources']['transfer']=chosen(conn,'results_transfer')
            from src.reporting.thesis_cartography import load_layers
            data['cartographic_context'],cartographic_source=load_layers(conn)
            data['sources']['cartographic_context']=[cartographic_source]
            sample=json.loads((ROOT/'config/study/sample_selection.json').read_text());geo=json.loads((ROOT/'config/study/geography_selection.json').read_text())
            assoc=json.loads((ROOT/'config/study/association_selection.json').read_text());interp=json.loads((ROOT/'config/study/interpretation_selection.json').read_text())
            data['coefficients']=[];data['contributions']=[];data['fold_metrics']=[];data['fold_sources']=[];data['transfer_sources']=[]
            for city in CITIES:
                frame=pd.DataFrame(records(conn,sample,city,'sample','prediction_sample'))
                if canonical_hash(json_records(frame))!=data['sample'][city]['record_sha256']:raise ValueError('Frozen sample differs')
                if len(frame)!=data['sample'][city]['prediction_n'] or frame.log_price.isna().any():raise ValueError('Invalid observed outcome/sample')
                data['frames'][city]=frame
                geometries=conn.execute(text("SELECT geometry_key,properties,ST_AsGeoJSON(geom,15) AS geometry FROM study.geometries WHERE run_id=:run AND (geometry_key='mask' OR geometry_key LIKE 'group:%') ORDER BY geometry_key"),{'run':geo[city]['run_id']}).mappings().all()
                data['geometries'][city]=[{'key':r['geometry_key'],'properties':r['properties'],'geometry':shape(json.loads(r['geometry']))} for r in geometries]
                if sum(g['key'].startswith('group:') for g in data['geometries'][city])!=cities[city]['operational_count']:raise ValueError('Wrong validation polygons')
                data['coefficients'].extend({'city':city,**r} for r in records(conn,assoc,city,'reporting','association_coefficients'))
                data['contributions'].extend(records(conn,interp,city,'reporting','contribution_summary'))
                selected=json.loads((ROOT/'runs'/city/'within_city_neighbourhood_selection.json').read_text());parts=[]
                for item in selected:
                    summary,private=predictions(conn,item['run_id'],city,'within_city')
                    if canonical_hash(summary)!=item['summary_sha256'] or summary['scheme']!='neighbourhood' or summary['historical_fit_reused']:raise ValueError('Wrong final fold')
                    parts.append(private);data['fold_metrics'].extend({'city':city,**r} for r in summary['metrics'])
                    data['fold_sources'].append({'run_id':item['run_id'],'city':city,'family':'within_city','summary_sha256':item['summary_sha256'],'artifact':'predictions; metrics'})
                data['primary_predictions'][city]=pd.concat(parts,ignore_index=True)
                primary=data['validation']['neighbourhood'][city]
                for score in primary['performance']:
                    part=data['primary_predictions'][city].loc[lambda p:(p.estimator==score['estimator'])&(p.model==score['model'])]
                    if len(part)!=len(frame) or part.listing_id.duplicated().any():raise ValueError('Incomplete common heldout ladder')
                    recalculated=float(np.sqrt(np.mean((part.log_price-part.prediction)**2)))
                    if not np.isclose(recalculated,score['rmse'],rtol=1e-12,atol=1e-12):raise ValueError('Final RMSE does not reproduce')
                if data['association'][city]['status']!='COMPLETE_ASSOCIATION' or data['association'][city]['association_missing_limit']!=.10:raise ValueError('Incomplete/amendment-mismatched inference')
            transfers=json.loads((ROOT/'runs/transfer/selection.json').read_text())
            for item in transfers:
                summary,private=predictions(conn,item['run_id'],item['city'],'transfer')
                if canonical_hash(summary)!=item['summary_sha256'] or any(summary[k] for k in ['target_fit','target_tuning','target_intercept_recalibration']):raise ValueError('Transfer provenance/leakage failure')
                key=(item['city'],item['target_city'],item['estimator'],item['model']);data['transfer_predictions'][key]=private
                if not np.isclose(float(np.sqrt(np.mean((private.relative_log_price-private.prediction)**2))),summary['metrics']['rmse'],rtol=1e-12,atol=1e-12):raise ValueError('Transfer RMSE does not reproduce')
                data['transfer_sources'].append({'run_id':item['run_id'],'city':item['city'],'target_city':item['target_city'],'family':'transfer','summary_sha256':item['summary_sha256'],'artifact':'predictions; metrics'})
            if len(data['transfer_predictions'])!=48:raise ValueError('Incomplete six-direction transfer ladder')
    finally:engine.dispose()
    data['catalog']=catalog
    return data
