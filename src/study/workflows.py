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
