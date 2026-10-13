"""Dependency-aware research stages; exports are generated from authoritative SQL."""
from __future__ import annotations

import json
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT
from src.pipeline.protocol import canonical_hash
from src.study.geography import prepare
from src.study.samples import reference_sample, listing_controls
from src.study.sources import get_engine, historical_inputs, write_once
from src.study.specification import CITIES
from src.study.store import commit_package, dependencies, read_package, setup

GEOGRAPHY_SELECTION = PROJECT_ROOT/'config/study/geography_selection.json'
REFERENCE_SELECTION = PROJECT_ROOT/'config/study/reference_selection.json'
CONTEXT_SELECTION = PROJECT_ROOT/'config/study/context_selection.json'


def freeze_geography():
    if GEOGRAPHY_SELECTION.exists() or REFERENCE_SELECTION.exists():
        raise ValueError('Selections already frozen; audit rather than overwrite')
    sources = json.loads((PROJECT_ROOT/'config/study/neighbourhood_sources.json').read_text())
    engine = get_engine()
    selected, references = {}, {}
    try:
        setup(engine)
        for city in CITIES:
            with engine.begin() as conn:
                rows, mask, source = historical_inputs(conn, city)
                summary, assignments, raw, grouped = prepare(rows, mask, city, sources[city])
                summary['listing_source'] = source
                geometries = [('mask', mask, {'role':'accepted_study_mask'})]
                geometries += [('raw:'+a['raw_label'],a['geom'],{'raw_label':a['raw_label'],'group':a['group']}) for a in raw]
                geometries += [('group:'+a['group'],a['geom'],{'group':a['group'],'raw_components':a['raw_components']}) for a in grouped]
                identity = commit_package(conn,city=city,family='geography',summary=summary,
                                          records={'assignment':assignments},geometries=geometries,
                                          deps=dependencies({'listing_source':source,'neighbourhood_source':sources[city]}))
                reference, records = reference_sample(rows)
                reference.update(city=city,currency=source['currency'],listing_source=source)
                ref_id = commit_package(conn,city=city,family='reference',summary=reference,
                                        records={'reference_sample':records},deps=dependencies({'listing_source':source}))
                selected[city] = {'run_id':identity,'summary_sha256':canonical_hash(summary)}
                references[city] = {'run_id':ref_id,'summary_sha256':canonical_hash(reference)}
            print(city,summary['status'],source['counts']['inside_boundary_positive_price'],flush=True)
        write_once(GEOGRAPHY_SELECTION,(json.dumps(selected,indent=2)+'\n').encode())
        write_once(REFERENCE_SELECTION,(json.dumps(references,indent=2)+'\n').encode())
    finally:
        engine.dispose()
    return audit_geography(export=True)


def audit_geography(export=False):
    selected = json.loads(GEOGRAPHY_SELECTION.read_text())
    references = json.loads(REFERENCE_SELECTION.read_text())
    sources = json.loads((PROJECT_ROOT/'config/study/neighbourhood_sources.json').read_text())
    result = {}
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                rows, mask, source = historical_inputs(conn, city)
                actual, assignments, _, _ = prepare(rows,mask,city,sources[city])
                actual['listing_source'] = source
                prior,_ = read_package(conn,selected[city]['run_id'],city,'geography')
                if actual != prior or canonical_hash(actual) != selected[city]['summary_sha256']:
                    raise ValueError('Geography source/recomputation changed: '+city)
                stored = conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city "
                                           "AND family='geography' AND artifact='assignment' ORDER BY record_key::integer"),
                                      {'run':selected[city]['run_id'],'city':city}).scalars().all()
                if stored != assignments:
                    raise ValueError('Private assignment roundtrip mismatch: '+city)
                reference, records = reference_sample(rows)
                reference.update(city=city,currency=source['currency'],listing_source=source)
                stored_ref,_ = read_package(conn,references[city]['run_id'],city,'reference')
                if reference != stored_ref or canonical_hash(reference) != references[city]['summary_sha256']:
                    raise ValueError('Frozen reference benchmark differs: '+city)
                stored_rows = conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city "
                                                "AND family='reference' ORDER BY record_key::integer"),
                                          {'run':references[city]['run_id'],'city':city}).scalars().all()
                if stored_rows != records:
                    raise ValueError('Private reference sample differs')
                result[city] = {'geography':actual,'reference':reference,'private_assignment_roundtrip':'PASS',
                                'reference_roundtrip':'PASS','geography_run_id':selected[city]['run_id'],
                                'reference_run_id':references[city]['run_id']}
    finally:
        engine.dispose()
    if export:
        write_once(PROJECT_ROOT/'docs/analysis/geography_audit.json',(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode())
    return result


def freeze_context():
    from src.study.context import build_context
    if CONTEXT_SELECTION.exists():raise ValueError('Context selection already frozen; audit rather than overwrite')
    audit_geography()
    sources=json.loads((PROJECT_ROOT/'config/study/neighbourhood_sources.json').read_text())
    engine=get_engine();selected={}
    try:
        for city in CITIES:
            with engine.begin() as conn:
                rows,mask,listing=historical_inputs(conn,city)
                _,assignments,_,_=prepare(rows,mask,city,sources[city])
                summary,context=build_context(conn,city,rows,assignments,mask)
                identity=commit_package(conn,city=city,family='context',summary=summary,records={'context':context},
                                        deps=dependencies({'listing_source':listing,'geography':json.loads(GEOGRAPHY_SELECTION.read_text())[city],
                                                           'source_native_density':summary['density_units'],'civic_anchor':summary['civic_anchor']}))
                selected[city]={'run_id':identity,'summary_sha256':canonical_hash(summary)}
            print(city,summary['status'],summary['eligible_context_missing_n'],flush=True)
        write_once(CONTEXT_SELECTION,(json.dumps(selected,indent=2)+'\n').encode())
    finally:engine.dispose()
    return audit_context(export=True)


def audit_context(export=False):
    from src.study.context import build_context
    sources=json.loads((PROJECT_ROOT/'config/study/neighbourhood_sources.json').read_text())
    selected=json.loads(CONTEXT_SELECTION.read_text());engine=get_engine();result={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city in CITIES:
                rows,mask,_=historical_inputs(conn,city)
                _,assignments,_,_=prepare(rows,mask,city,sources[city])
                summary,records=build_context(conn,city,rows,assignments,mask)
                prior,_=read_package(conn,selected[city]['run_id'],city,'context')
                stored=conn.execute(text("SELECT record FROM study.records WHERE run_id=:run AND city=:city "
                                         "AND family='context' AND artifact='context' ORDER BY record_key::integer"),
                                    {'run':selected[city]['run_id'],'city':city}).scalars().all()
                if summary!=prior or canonical_hash(summary)!=selected[city]['summary_sha256'] or records!=stored:
                    raise ValueError('Context source/private-child roundtrip differs: '+city)
                result[city]=summary
    finally:engine.dispose()
    if export:write_once(PROJECT_ROOT/'docs/analysis/context_audit.json',(json.dumps(result,indent=2,ensure_ascii=False)+'\n').encode())
    return result


def freeze_accessibility():
    from src.study.accessibility import elements,complete_geometry,pedestrian_graph,destinations,measurements
    from src.study.specification import load_design
    import gc
    target=PROJECT_ROOT/'config/study/accessibility_selection.json'
    if target.exists():raise ValueError('Accessibility already frozen; refuse replacement')
    sources=json.loads((PROJECT_ROOT/'config/study/osm_sources.json').read_text())
    design,cities=load_design();engine=get_engine();selected={};public={}
    try:
        for city in CITIES:
            with engine.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY')
                rows,_,listing=historical_inputs(conn,city)
            eligible=[r for r in rows if r['dwelling_eligible'] and r['positive_price'] and r['inside_boundary']]
            del rows
            dst,dst_qa=destinations(complete_geometry(city,elements(sources[city]['osm_destinations'])),cities[city]['metric_crs'])
            print(city,'destinations qualified',dst_qa['canonical_counts'],flush=True)
            document=elements(sources[city]['osm_network'])
            graph,metric,graph_qa=pedestrian_graph(document,cities[city]['metric_crs'])
            del document;gc.collect()
            print(city,'graph qualified',graph_qa['nodes'],graph_qa['arcs'],flush=True)
            extent=sources[city]['osm_network'][0]['geographic_extent']
            bbox=extent.get('full_extent',extent.get('bbox_south_west_north_east'))
            features,measurement_qa=measurements(graph,metric,dst,eligible,bbox,cities[city]['metric_crs'])
            del graph,metric;gc.collect()
            summary={'city':city,'status':'FEATURES_RECOMPUTED_PENDING_SAMPLE_FOLD_QA','source_snapshot':design['accessibility']['preferred_osm_timestamp'],
                     'listing_source':listing,'graph':graph_qa,'destinations':dst_qa,'measurements':measurement_qa,
                     'destination_universe_sha256':canonical_hash(dst),'records_sha256':canonical_hash(features),
                     'feature_n':len(features),'historical_features_reused':False,'empirical_models_fitted':False}
            with engine.begin() as conn:
                identity=commit_package(conn,city=city,family='accessibility',summary=summary,
                                        records={'features':features,'destinations':dst},deps=dependencies({'osm_sources':sources[city],
                                          'destination_geometry':json.loads((PROJECT_ROOT/'config/study/destination_geometry_sources.json').read_text())[city],
                                          'listing_source':listing}))
            selected[city]={'run_id':identity,'summary_sha256':canonical_hash(summary)};public[city]=summary
            print(city,'fresh matched features stored',len(features),measurement_qa['counts'],flush=True)
            del features,dst,eligible;gc.collect()
        write_once(target,(json.dumps(selected,indent=2)+'\n').encode())
        write_once(PROJECT_ROOT/'docs/analysis/accessibility_audit.json',(json.dumps(public,indent=2,ensure_ascii=False)+'\n').encode())
    finally:engine.dispose()
    return public
