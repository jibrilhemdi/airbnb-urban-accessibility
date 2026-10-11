"""Build core context for the same eleven peer areas; retain source limitations."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.db.connection import get_engine
from src.pipeline.protocol import AREA_NAMES,DESIGN,verify_income_evidence
from src.pipeline.storage import export,json_records
from src.pipeline.qualified_income import verify_sql

# Source readers are shared with context ingestion, not a separate model family.
def build(engine,require_harmonised=True):
    if require_harmonised: verify_income_evidence()
    with engine.connect() as conn:
        areas=pd.read_sql(text('SELECT area_id AS analysis_area,area_name AS analysis_area_name,source_file_id AS boundary_source_file_id,'
            'ST_Area(geom_25832)/1000000 AS area_km2,ST_SRID(geom_25832) AS crs_epsg '
            'FROM v3_spatial.analysis_areas ORDER BY area_id'),conn)
        city=pd.read_sql(text("SELECT district_code,measure_code,reference_period,value,source_file_id FROM v3_clean.copenhagen_district_context_measures"),conn)
        national=pd.read_sql(text("SELECT municipality_code,measure_code,reference_period,value,source_file_id FROM v3_clean.municipality_context_measures"),conn)
        verify_sql(conn)
        incomes={r['analysis_area']:r for r in conn.execute(text('SELECT analysis_area,equiv_disposable_income_2024,source_file_id,record FROM v3_features.qualified_area_income')).mappings()}
    if set(areas.analysis_area)!=set(AREA_NAMES) or len(areas)!=11: raise RuntimeError('Eleven peer area polygons required')
    rows=[]
    for area in areas.to_dict('records'):
        is_city=area['analysis_area'].startswith('cph_')
        source=city.loc[city.district_code=='10'+area['analysis_area'][-2:]] if is_city else national.loc[national.municipality_code=='147']
        pop_key='district_population' if is_city else 'total_population'
        pop=source.loc[(source.measure_code==pop_key)&(source.reference_period=='2026Q3')]
        if len(pop)!=1 or area['crs_epsg']!=25832 or area['area_km2']<=0: raise RuntimeError('Ambiguous context source/geometry')
        p=pop.iloc[0];i=incomes[area['analysis_area']]
        status='qualified'
        row={**area,'population_count':int(p.value),'population_period':p.reference_period,
            'log_population_density':float(np.log(float(p.value)/area['area_km2'])),
            'equiv_disposable_income_2024':str(i['equiv_disposable_income_2024']),
            'income_100k_dkk':float(i['equiv_disposable_income_2024'])/100000,'income_period':'2024',
            'population_source_file_id':int(p.source_file_id),'income_source_file_id':int(i['source_file_id']),
            'income_harmonisation_status':status,'context_version':'area_context_v3',
            'provenance':json.dumps({'income_evidence':DESIGN['income_harmonisation'],'income_source_record':i['record'],
                'density_definition':'population / gross assignment-polygon area; water inclusion and statistical boundary vintage unverified',
                'population_note':'City total differs from national municipality total; no rescaling'})}
        if not np.isfinite(row['log_population_density']) or row['income_100k_dkk']<=0: raise RuntimeError('Invalid context values')
        rows.append(row)
    frame=pd.DataFrame(rows)
    with engine.begin() as conn:
        existing=conn.scalar(text('SELECT count(*) FROM v3_features.area_context'))
        if existing: raise RuntimeError('Context already persisted; explicitly version changes instead of overwriting')
        columns=list(rows[0]);values=','.join('CAST(:provenance AS jsonb)' if c=='provenance' else ':'+c for c in columns)
        conn.execute(text('INSERT INTO v3_features.area_context('+','.join(columns)+') VALUES('+values+')'),rows)
    export('area_context','analysis_area_context.csv',frame)
    return {'analysis_areas':len(frame),'income_harmonisation_status':status}
def main():
    engine=get_engine()
    try: print(json.dumps(build(engine),indent=2))
    finally:engine.dispose()
if __name__=='__main__':main()
