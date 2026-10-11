"""Audit the matched rail/bus/opportunity universe and extraction boundary."""
import pandas as pd
from sqlalchemy import text
from src.pipeline.storage import export

def run(engine):
    with engine.connect() as conn:
        table=pd.read_sql(text("WITH study AS (SELECT geom_25832 FROM v3_spatial.study_area WHERE area_kind='official_study_area'), "
            "destinations AS (SELECT destination_key AS key,category,geom_25832 FROM v3_spatial.osm_pois UNION ALL "
            "SELECT station_key,'rail',geom_25832 FROM v3_spatial.transit_stations UNION ALL "
            "SELECT bus_stop_key,'bus',geom_25832 FROM v3_spatial.canonical_bus_stops) "
            "SELECT category,count(*) AS destinations,count(*) FILTER(WHERE ST_Covers(study.geom_25832,d.geom_25832)) AS within_study_area,"
            "count(*) FILTER(WHERE NOT ST_Covers(study.geom_25832,d.geom_25832)) AS outside_study_area "
            "FROM destinations d CROSS JOIN study GROUP BY category ORDER BY category"),conn)
    if set(table.category)!= {'food_social','cultural_tourist','rail','bus'}:raise RuntimeError('Destination family missing')
    table['crs_epsg']=25832;table['definition']='full frozen extract used for both Euclidean and network measures'
    export('accessibility','destination_boundary_audit.csv',table);return {'families':len(table),'destinations':int(table.destinations.sum())}
