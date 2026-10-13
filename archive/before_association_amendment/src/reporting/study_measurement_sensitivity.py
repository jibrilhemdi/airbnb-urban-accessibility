"""Frozen speed and all-reachable continuous-decay measures from original sources."""
from __future__ import annotations
from collections import defaultdict
import gc
import json
import math
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
import networkx as nx
import pandas as pd
from src.ingestion.common import PROJECT_ROOT
from src.pipeline.protocol import canonical_hash
from src.study.sources import get_engine,write_once
from src.study.specification import CITIES,load_design
from src.study.sample_freeze import records
from src.study.accessibility import elements,complete_geometry,pedestrian_graph,destinations
from src.study.store import commit_package,dependencies


def run():
    design,cities=load_design();source=json.loads((PROJECT_ROOT/'config/study/osm_sources.json').read_text())
    selected=json.loads((PROJECT_ROOT/'config/study/sample_selection.json').read_text());engine=get_engine();pointers={}
    try:
        for city in CITIES:
            with engine.connect() as conn:
                conn.exec_driver_sql('SET TRANSACTION READ ONLY');frame=pd.DataFrame(records(conn,selected,city,'sample','prediction_sample'))
            dst,_=destinations(complete_geometry(city,elements(source[city]['osm_destinations'])),cities[city]['metric_crs'])
            graph,metric,_=pedestrian_graph(elements(source[city]['osm_network']),cities[city]['metric_crs'])
            ids=list(metric);lookup={node:i for i,node in enumerate(ids)};node_xy=np.array([metric[node] for node in ids]);tree=cKDTree(node_xy)
            origins=frame[['metric_x','metric_y']].to_numpy(float);osnap,oi=tree.query(origins)
            destination_xy=np.array([[d['x'],d['y']] for d in dst]);dsnap,di=tree.query(destination_xy)
            grouped=defaultdict(list)
            for i,d in enumerate(dst):
                if d['category'] in {'food_social','cultural_tourist'}:grouped[d['category']].append(i)
            features=[{'listing_id':str(key)} for key in frame.listing_id]
            by_node=defaultdict(list)
            for j,d in enumerate(dst):
                if d['category'] in grouped:by_node[ids[int(di[j])]].append((d['category'],float(dsnap[j])))
            all_origins=defaultdict(list)
            for i,index in enumerate(oi):all_origins[ids[int(index)]].append(i)
            for node,members in all_origins.items():
                reached=nx.single_source_dijkstra_path_length(graph,node,cutoff=900-min(float(osnap[i]) for i in members),weight='length_m')
                arrived=defaultdict(list)
                for other,length in reached.items():
                    for category,connector in by_node.get(other,[]):arrived[category].append(length+connector)
                for i in members:
                    for speed,radius in [(4.,667),(5.4,900)]:
                        code='4p0' if speed==4 else '5p4';limit=speed*1000/6
                        for category,prefix in [('food_social','food'),('cultural_tourist','culture')]:
                            direct=np.linalg.norm(destination_xy[grouped[category]]-origins[i],axis=1)
                            features[i][prefix+'_e_speed_'+code]=int(np.sum(direct<=radius))
                            features[i][prefix+'_w_speed_'+code]=int(np.sum(np.asarray(arrived[category])+osnap[i]<=limit))
            print(city,'speed measures completed',flush=True)
            edge_row=[];edge_col=[];edge_data=[]
            for u,v,data in graph.edges(data=True):edge_row.append(lookup[v]);edge_col.append(lookup[u]);edge_data.append(data['length_m'])
            reverse=csr_matrix((edge_data,(edge_row,edge_col)),shape=(len(ids),len(ids)))
            del graph,edge_row,edge_col,edge_data;gc.collect()
            rate=math.log(2)/(5000/6)
            for category,prefix in [('food_social','food'),('cultural_tourist','culture')]:
                selected_dst=grouped[category];values=np.zeros(len(frame))
                # Every reachable destination is included. Source-node batches
                # bound memory, without a distance/time truncation.
                for start in range(0,len(selected_dst),8):
                    positions=selected_dst[start:start+8]
                    distances=dijkstra(reverse,directed=True,indices=di[positions],limit=np.inf)
                    route=distances[:,oi]+np.asarray(dsnap)[positions,None]+np.asarray(osnap)[None,:]
                    values+=np.exp(-rate*route).sum(axis=0)
                    if start%400==0:print(city,prefix,'decay destinations',start,'of',len(selected_dst),flush=True)
                for start in range(0,len(frame),200):
                    points=origins[start:start+200]
                    direct=np.linalg.norm(points[:,None,:]-destination_xy[selected_dst][None,:,:],axis=2)
                    decay=np.exp(-rate*direct).sum(axis=1)
                    for offset,value in enumerate(decay):
                        i=start+offset;features[i][prefix+'_e_decay']=float(value);features[i][prefix+'_w_decay']=float(values[i])
            summary={'city':city,'status':'MEASUREMENT_VARIANTS_RECOMPUTED','n':len(frame),'metric_crs':cities[city]['metric_crs'],
                     'speed_kmh':[4.,5.4],'decay_half_life_minutes':10,'decay_arbitrary_cutoff':False,
                     'finite_frozen_destination_universe':True,'record_sha256':canonical_hash(features)}
            with engine.begin() as conn:
                identity=commit_package(conn,city=city,family='accessibility',summary=summary,records={'measurement_variants':features},
                                        deps=dependencies({'sample':selected[city],'source':source[city],'measurement_code':'src/reporting/study_measurement_sensitivity.py'}))
            pointers[city]={'run_id':identity,'summary_sha256':canonical_hash(summary)}
            del reverse,metric,node_xy,dst,features;gc.collect()
            print(city,'measurement variants stored',flush=True)
        write_once(PROJECT_ROOT/'config/study/measurement_variant_selection.json',(json.dumps(pointers,indent=2)+'\n').encode())
    finally:engine.dispose()
    return pointers


if __name__=='__main__':run()
