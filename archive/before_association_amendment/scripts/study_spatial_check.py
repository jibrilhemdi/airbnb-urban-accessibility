"""Independent PostGIS check of private operational assignments; emits counts only."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sqlalchemy import text
from src.study.sources import get_engine
from src.study.specification import load_design


def verify():
    _,cities=load_design()
    selected=json.loads((ROOT/'config/study/geography_selection.json').read_text())
    engine=get_engine();results={}
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
            for city,config in cities.items():
                old=config['historical_listing_selection']
                query=text("""
                WITH points AS (
                 SELECT record->>'listing_id' AS id,
                  ST_SetSRID(ST_MakePoint((record->>'longitude')::float8,(record->>'latitude')::float8),4326) AS geom
                 FROM v4_raw.listing_audit
                 WHERE version=:version AND run_id=:old_run AND city=:old_city AND snapshot='2026-06-30'
                ), checked AS (
                 SELECT r.record, m.geom AS mask, p.geom AS point, h.groups
                 FROM study.records r JOIN points p ON p.id=r.record->>'listing_id'
                 JOIN study.geometries m ON m.run_id=r.run_id AND m.city=r.city AND m.family=r.family AND m.geometry_key='mask'
                 CROSS JOIN LATERAL (
                  SELECT COALESCE(jsonb_agg(g.properties->>'group' ORDER BY g.properties->>'group'),'[]'::jsonb) AS groups
                  FROM study.geometries g WHERE g.run_id=r.run_id AND g.city=r.city AND g.family=r.family
                   AND g.geometry_key LIKE 'group:%' AND ST_Covers(m.geom,p.geom) AND ST_Covers(g.geom,p.geom)
                 ) h
                 WHERE r.run_id=:run AND r.city=:city AND r.family='geography' AND r.artifact='assignment'
                )
                SELECT count(*) AS rows,
                 count(*) FILTER(WHERE groups<>record->'group_hits') AS inconsistent_group_hits,
                 count(*) FILTER(WHERE ST_Covers(mask,point)<>(record->>'inside_mask')::boolean) AS inconsistent_mask
                FROM checked
                """)
                row=conn.execute(query,{'version':old['source_version'],'old_run':old['run_id'],'old_city':old['city'],
                                        'run':selected[city]['run_id'],'city':city}).mappings().one()
                results[city]=dict(row)
                if row['rows']<=0 or row['inconsistent_group_hits'] or row['inconsistent_mask']:
                    raise ValueError('Independent spatial check failed: '+city)
    finally:engine.dispose()
    return results


if __name__=='__main__':print(json.dumps(verify(),indent=2))
