"""Persist analytical artifacts in PostgreSQL; export aggregate tables separately."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.pipeline.output_paths import output_file

def json_records(frame):
    # Pandas writes NaN/NaT as explicit null, never as a numeric replacement.
    return json.loads(frame.to_json(orient='records',date_format='iso',double_precision=15))
def persist(conn,run_id,family,artifact,frame):
    records=json_records(frame) if isinstance(frame,pd.DataFrame) else frame
    conn.execute(text('DELETE FROM v3_analysis.artifacts WHERE run_id=:run AND family=:family AND artifact=:artifact'),
                 dict(run=run_id,family=family,artifact=artifact))
    if records:
        conn.execute(text('INSERT INTO v3_analysis.artifacts(run_id,family,artifact,record_key,record) '
            'VALUES(:run,:family,:artifact,:key,CAST(:record AS jsonb))'),
            [dict(run=run_id,family=family,artifact=artifact,key=str(i),record=json.dumps(record,allow_nan=False,default=str))
             for i,record in enumerate(records)])
def load_artifact(conn,run_id,family,artifact):
    records=conn.execute(text('SELECT record FROM v3_analysis.artifacts WHERE run_id=:run AND family=:family AND artifact=:artifact '
        'ORDER BY record_key::integer'),dict(run=run_id,family=family,artifact=artifact)).scalars().all()
    return pd.DataFrame(records)
def export(family,name,frame):
    path=output_file('tables',family,name);path.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(path,index=False)
    return path
