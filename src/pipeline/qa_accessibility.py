"""Aggregate V3 coverage, matched destinations, routing and snapping QA."""
import pandas as pd
from sqlalchemy import text
from src.pipeline.storage import export

def run(engine):
    with engine.connect() as conn:
        coverage=pd.read_sql(text("SELECT s.analysis_area,count(*) FILTER(WHERE l.primary_sample_candidate) AS primary_candidates,"
            "count(*) FILTER(WHERE l.primary_sample_candidate AND w.nearest_station_walking_minutes IS NULL) AS rail_unreachable,"
            "count(*) FILTER(WHERE l.primary_sample_candidate AND b.nearest_bus_walking_minutes IS NULL) AS bus_unreachable,"
            "count(*) FILTER(WHERE l.primary_sample_candidate AND NOT e.count_coverage_complete) AS count_edge_incomplete,"
            "count(*) FILTER(WHERE l.primary_sample_candidate AND NOT w.nearest_station_coverage_complete) AS rail_edge_incomplete,"
            "count(*) FILTER(WHERE l.primary_sample_candidate AND NOT b.walking_coverage_complete) AS bus_edge_incomplete,"
            "percentile_cont(.5) WITHIN GROUP(ORDER BY w.listing_snap_distance_m) AS median_listing_snap_m,"
            "count(*) FILTER(WHERE w.listing_snap_distance_m>100) AS large_listing_snap_n,"
            "count(*) FILTER(WHERE w.listing_snap_distance_m>250) AS severe_listing_snap_n "
            "FROM v3_clean.airbnb_listings l LEFT JOIN v3_features.listing_spatial_base s USING(snapshot_date,listing_id) "
            "LEFT JOIN v3_features.euclidean_accessibility e USING(snapshot_date,listing_id) LEFT JOIN v3_features.walking_accessibility w USING(snapshot_date,listing_id) "
            "LEFT JOIN v3_features.bus_accessibility b USING(snapshot_date,listing_id) GROUP BY s.analysis_area ORDER BY s.analysis_area"),conn)
        listing_n=conn.scalar(text('SELECT count(*) FROM v3_clean.airbnb_listings'))
        for relation in ['v3_features.euclidean_accessibility','v3_features.walking_accessibility','v3_features.bus_accessibility']:
            if conn.scalar(text('SELECT count(*) FROM '+relation))!=listing_n:raise RuntimeError('Listing feature cardinality mismatch: '+relation)
        mismatched=conn.scalar(text("WITH universe AS (SELECT destination_key,'poi'::text kind FROM v3_spatial.osm_pois UNION ALL SELECT station_key,'station' FROM v3_spatial.transit_stations) "
            "SELECT count(*) FROM universe u FULL JOIN v3_spatial.walking_destination_snaps s ON s.destination_key=u.destination_key AND s.destination_kind=u.kind "
            "WHERE u.destination_key IS NULL OR s.destination_key IS NULL"))
        if mismatched:raise RuntimeError('Euclidean and network destination sets differ')
        bus_mismatch=conn.scalar(text('SELECT count(*) FROM v3_spatial.canonical_bus_stops b FULL JOIN v3_spatial.bus_destination_snaps s USING(bus_stop_key) WHERE b.bus_stop_key IS NULL OR s.bus_stop_key IS NULL'))
        if bus_mismatch:raise RuntimeError('Euclidean and walking bus destination sets differ')
        violations=conn.scalar(text('SELECT count(*) FROM v3_features.walking_accessibility w JOIN v3_features.euclidean_accessibility e USING(snapshot_date,listing_id) '
            'JOIN v3_features.bus_accessibility b USING(snapshot_date,listing_id) WHERE w.nearest_station_network_distance_m+.1<e.nearest_station_distance_m '
            'OR b.bus_walking_distance_m+.1<b.nearest_bus_euclidean_m OR w.walking_speed_kmh<>5 OR b.walking_speed_kmh<>5 OR e.distance_crs_epsg<>25832'))
        if violations:raise RuntimeError('Distance lower-bound, speed or CRS QA failed')
        snaps=pd.read_sql(text("SELECT category,count(*) AS destinations,percentile_cont(.5) WITHIN GROUP(ORDER BY snap_distance_m) AS median_snap_m,"
            "count(*) FILTER(WHERE snap_distance_m>100) AS large_snap_n,count(*) FILTER(WHERE snap_distance_m>250) AS severe_snap_n "
            "FROM (SELECT category,snap_distance_m FROM v3_spatial.walking_destination_snaps UNION ALL SELECT 'bus',snap_distance_m FROM v3_spatial.bus_destination_snaps) a GROUP BY category"),conn)
        spatial_coverage=pd.read_sql(text("WITH d AS (SELECT category,geom_25832 FROM v3_spatial.osm_pois UNION ALL SELECT 'rail',geom_25832 FROM v3_spatial.transit_stations UNION ALL SELECT 'bus',geom_25832 FROM v3_spatial.canonical_bus_stops) "
            "SELECT a.area_id AS analysis_area,d.category,count(*) AS destinations FROM v3_spatial.analysis_areas a JOIN d ON ST_Covers(a.geom_25832,d.geom_25832) GROUP BY a.area_id,d.category ORDER BY a.area_id,d.category"),conn)
        # Check the network lower-bound count against the exact unrounded
        # Euclidean budget, keeping the rounded-radius publication feature intact.
        rows=conn.execute(text('SELECT l.listing_id,ST_X(l.geom_25832)x,ST_Y(l.geom_25832)y,w.food_social_w_10,w.cultural_tourist_w_10 '
            'FROM v3_clean.airbnb_listings l JOIN v3_features.walking_accessibility w USING(snapshot_date,listing_id) '
            'WHERE l.primary_sample_candidate AND w.routing_status=\'ok\' ORDER BY l.listing_id LIMIT 20')).mappings().all()
        for row in rows:
            counts=dict(conn.execute(text('SELECT category,count(*) FROM v3_spatial.osm_pois WHERE ST_DWithin(geom_25832,ST_SetSRID(ST_MakePoint(:x,:y),25832),5000.0/6) GROUP BY category'),row).all())
            for cat in ['food_social','cultural_tourist']:
                if row[cat+'_w_10']>counts.get(cat,0):raise RuntimeError('Independent exact-budget opportunity lower-bound failed')
    coverage['crs_epsg']=25832;snaps['crs_epsg']=25832;spatial_coverage['crs_epsg']=25832
    export('accessibility','destinations_by_analysis_area.csv',spatial_coverage)
    export('accessibility','coverage_by_analysis_area.csv',coverage);export('accessibility','destination_snap_qa.csv',snaps)
    return {'listing_n':listing_n,'matched_destination_sets':True,'distance_lower_bound_violations':violations,'independent_spotchecks':len(rows),'walking_speed_kmh':5.,'crs_epsg':25832}
