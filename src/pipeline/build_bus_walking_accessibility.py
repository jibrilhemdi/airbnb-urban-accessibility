"""Core bus walking access to the same deduplicated destinations as Euclidean."""
from __future__ import annotations
import json
import networkx as nx
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sqlalchemy import text
from src.db.connection import get_engine
from src.spatial.walking_routing import station_distance_labels
from src.pipeline.protocol import METRES_PER_MINUTE
from src.pipeline.storage import export

def persisted_graph(conn):
    network=conn.execute(text('SELECT network_id,node_count FROM v3_spatial.walking_networks')).one()
    nodes=pd.read_sql(text('SELECT osm_node_id,component_id,ST_X(geom_25832)x,ST_Y(geom_25832)y FROM v3_spatial.walking_nodes WHERE network_id=:network ORDER BY osm_node_id'),conn,params={'network':network.network_id})
    edges=pd.read_sql(text('SELECT from_node_id,to_node_id,length_m,forward_allowed,reverse_allowed FROM v3_spatial.walking_edges WHERE network_id=:network'),conn,params={'network':network.network_id})
    if len(nodes)!=network.node_count:raise RuntimeError('Persisted walking graph incomplete')
    graph=nx.DiGraph();graph.add_nodes_from(nodes.osm_node_id)
    for u,v,d,f,r in edges.itertuples(index=False,name=None):
        for a,b,allowed in [(u,v,f),(v,u,r)]:
            if allowed and (not graph.has_edge(a,b) or d<graph[a][b]['length_m']):graph.add_edge(a,b,length_m=d)
    return network.network_id,nodes,graph

def run():
    engine=get_engine()
    try:
        with engine.connect() as conn:
            network,nodes,graph=persisted_graph(conn)
            stops=pd.read_sql(text('SELECT bus_stop_key,ST_X(geom_25832)x,ST_Y(geom_25832)y FROM v3_spatial.canonical_bus_stops ORDER BY bus_stop_key'),conn)
            listings=pd.read_sql(text('SELECT s.*,e.source_edge_distance_m FROM v3_features.walking_listing_snaps s JOIN v3_features.euclidean_accessibility e USING(snapshot_date,listing_id) WHERE network_id=:network'),conn,params={'network':network})
        distances,idx=cKDTree(nodes[['x','y']].to_numpy()).query(stops[['x','y']].to_numpy())
        destinations=[{'destination_key':key,'snapped_node_id':int(nodes.iloc[i].osm_node_id),'snap_distance_m':float(d),
            'component_id':int(nodes.iloc[i].component_id)} for key,i,d in zip(stops.bus_stop_key,idx,distances)]
        best,keys=station_distance_labels(graph,destinations);dest_map={d['destination_key']:d for d in destinations};rows=[]
        for r in listings.to_dict('records'):
            node=r['snapped_node_id'];key=keys.get(int(node)) if pd.notna(node) else None
            distance=float(r['snap_distance_m']+best[int(node)]) if key else None
            rows.append(dict(snapshot=r['snapshot_date'],id=int(r['listing_id']),key=key,distance=distance,
                minutes=distance/METRES_PER_MINUTE if distance is not None else None,
                snap=dest_map[key]['snap_distance_m'] if key else None,
                coverage=distance<r['source_edge_distance_m'] if distance is not None else None,
                status='ok' if key else 'no_reachable_bus_stop',network=network))
        with engine.begin() as conn:
            conn.execute(text('INSERT INTO v3_spatial.bus_destination_snaps(network_id,bus_stop_key,snapped_node_id,snap_distance_m,component_id) '
                'VALUES(:network,:destination_key,:snapped_node_id,:snap_distance_m,:component_id)'),[{**r,'network':network} for r in destinations])
            conn.execute(text('UPDATE v3_features.bus_accessibility SET nearest_bus_walking_key=:key,bus_walking_distance_m=:distance,'
                'nearest_bus_walking_minutes=:minutes,destination_snap_m=:snap,walking_coverage_complete=:coverage,routing_status=:status,network_id=:network '
                'WHERE snapshot_date=:snapshot AND listing_id=:id'),rows)
        qa=pd.DataFrame([{'network_id':network,'bus_stops':len(stops),'snap_median_m':float(np.median(distances)),
            'snap_over_100m':int((distances>100).sum()),'snap_over_250m':int((distances>250).sum()),
            'unreachable_listings':sum(r['key'] is None for r in rows),'crs_epsg':25832,'walking_speed_kmh':5.0}])
        export('accessibility','bus_network_qa.csv',qa);return qa.to_dict('records')[0]
    finally:engine.dispose()
if __name__=='__main__':print(json.dumps(run(),indent=2))
