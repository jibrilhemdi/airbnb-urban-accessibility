"""Reproducible claims audit from primary geographic paired-error uncertainty."""
import pandas as pd
from src.pipeline.storage import load_artifact,export

def run(engine,run_id):
    with engine.connect() as conn:table=load_artifact(conn,run_id,'primary_models','incremental_performance')
    if table.empty:raise RuntimeError('Current incremental results missing')
    table=table.loc[table.scheme=='geographic_11'].copy()
    table['interpretation']=['consistent lower held-out RMSE across area resamples' if h<0 else 'consistent higher held-out RMSE across area resamples' if l>0 else 'direction varies across area resamples' for l,h in zip(table.delta_rmse_bootstrap_low,table.delta_rmse_bootstrap_high)]
    table['causal_claim_supported']=False
    export('reporting','claims_audit.csv',table);return {'claims':len(table),'bootstrap_replications':2000}
