"""Threshold, fixed-budget speed and full frozen-destination exponential decay."""
from __future__ import annotations
import json
from bisect import bisect_right
from collections import defaultdict
import networkx as nx
import numpy as np
import pandas as pd
from scipy.sparse.csgraph import dijkstra
from sqlalchemy import text
from src.db.connection import get_engine
from src.pipeline.build_bus_walking_accessibility import persisted_graph
from src.pipeline.protocol import DECAY_LAMBDA,METRES_PER_MINUTE
from src.pipeline.storage import export
VARIANTS=[('threshold_15',5.,15.,1250),('threshold_20',5.,20.,1667),('speed_4',4.,10.,667),('speed_5_4',5.4,10.,900),('continuous_decay',5.,None,None)]

def calculate(graph,listing_snaps,poi_snaps,poi_xy):
    """Unreachable destinations have t=infinity and contribute zero to decay.

    No finite routing cutoff is used for decay. The universe is the full frozen
    extracted destination set, not a claim about destinations absent from OSM.
    Exact speed*time distances define network budgets; rounded integer radii
    define the declared Euclidean analogues (rounding discrepancy <=0.333 m).
    """
    node_ids=np.array(sorted(graph.nodes),dtype=np.int64)
    sparse=nx.to_scipy_sparse_array(graph,nodelist=node_ids,weight='length_m',format='csr')
    # scipy csgraph expects 32-bit sparse index arrays in this environment.
    sparse.indices=sparse.indices.astype(np.int32);sparse.indptr=sparse.indptr.astype(np.int32)
    if not len(listing_snaps) or not len(poi_snaps):raise RuntimeError('Opportunity origins/destinations missing')
    dest_nodes=np.array([r['snapped_node_id'] for r in poi_snaps],np.int64)
    if not np.isin(dest_nodes,node_ids).all():raise RuntimeError('Destination snap missing from graph')
    dest_idx=np.searchsorted(node_ids,np.array([r['snapped_node_id'] for r in poi_snaps],np.int64))
    dest_connector=np.array([r['snap_distance_m'] for r in poi_snaps],float)
    cat=np.array([r['category'] for r in poi_snaps]);categories=['food_social','cultural_tourist']
    grouped=defaultdict(list)
    for row in listing_snaps:
        if pd.notna(row['snapped_node_id']):grouped[int(row['snapped_node_id'])].append(row)
    results=[]
    for count,(node,origins) in enumerate(grouped.items(),1):
        paths=dijkstra(sparse,directed=True,indices=int(np.searchsorted(node_ids,node)))
        arrivals=paths[dest_idx]+dest_connector
        sorted_arrivals={c:np.sort(arrivals[cat==c]) for c in categories}
        network_decay={c:float(np.exp(-DECAY_LAMBDA*arrivals[cat==c]/METRES_PER_MINUTE).sum()) for c in categories}
        for listing in origins:
            connector=listing['snap_distance_m'];distances=np.hypot(poi_xy[:,0]-listing['x'],poi_xy[:,1]-listing['y'])
            for name,speed,budget,radius in VARIANTS:
                for c in categories:
                    if budget is None:
                        e=float(np.exp(-DECAY_LAMBDA*distances[cat==c]/METRES_PER_MINUTE).sum())
                        w=network_decay[c]*np.exp(-DECAY_LAMBDA*connector/METRES_PER_MINUTE)
                    else:
                        e=int(np.sum(distances[cat==c]<=radius));w=bisect_right(sorted_arrivals[c],speed*1000/60*budget-connector)
                    results.append({'snapshot':str(listing['snapshot_date'])[:10],'id':int(listing['listing_id']),'definition':name,'category':c,
                        'euclidean_value':e,'walking_value':float(w),'speed':speed,'budget':budget,'radius':radius,'decay':DECAY_LAMBDA if budget is None else None})
        if count%250==0:print(f'Opportunity variants: {count}/{len(grouped)} origin nodes',flush=True)
    return results

def build(engine):
    with engine.connect() as conn:
        network,nodes,graph=persisted_graph(conn)
        listings=pd.read_sql(text('SELECT l.snapshot_date,l.listing_id,ST_X(l.geom_25832)x,ST_Y(l.geom_25832)y,s.snapped_node_id,s.snap_distance_m '
            'FROM v3_analysis.dataset_records d JOIN v3_clean.airbnb_listings l USING(snapshot_date,listing_id) '
            'JOIN v3_features.walking_listing_snaps s USING(snapshot_date,listing_id) WHERE s.network_id=:network ORDER BY l.snapshot_date,l.listing_id'),conn,params={'network':network})
        pois=pd.read_sql(text("SELECT s.*,ST_X(p.geom_25832)x,ST_Y(p.geom_25832)y FROM v3_spatial.walking_destination_snaps s JOIN v3_spatial.osm_pois p USING(destination_key) WHERE s.network_id=:network AND s.destination_kind='poi' ORDER BY s.destination_key"),conn,params={'network':network})
        if conn.scalar(text('SELECT count(*) FROM v3_features.opportunity_variants')):raise RuntimeError('Opportunity variants already persisted; freeze must not be overwritten')
    rows=calculate(graph,listings.to_dict('records'),pois.to_dict('records'),pois[['x','y']].to_numpy(float))
    with engine.begin() as conn:
        conn.execute(text('INSERT INTO v3_features.opportunity_variants(snapshot_date,listing_id,definition,category,euclidean_value,walking_value,walking_speed_kmh,time_budget_minutes,matched_euclidean_radius_m,decay_lambda) '
            'VALUES(:snapshot,:id,:definition,:category,:euclidean_value,:walking_value,:speed,:budget,:radius,:decay)'),rows)
    summary=pd.DataFrame(rows).groupby(['definition','category']).agg(n=('id','size'),euclidean_mean=('euclidean_value','mean'),walking_mean=('walking_value','mean')).reset_index()
    export('accessibility','opportunity_variant_summary.csv',summary)
    return {'records':len(rows),'network_id':network,'decay_lambda':DECAY_LAMBDA,'network_cutoff':'none','crs_epsg':25832,'destination_universe':'all frozen extracted canonical POIs'}
if __name__=='__main__':
    engine=get_engine()
    try:print(json.dumps(build(engine),indent=2))
    finally:engine.dispose()
