"""Create the fixed candidate budget before any model fitting."""
import itertools,json
import numpy as np
from src.ingestion.common import PROJECT_ROOT,write_json,sha256_file
from src.pipeline.protocol import DESIGN,canonical_hash
SPACE={'max_depth':[2,3,4,5,6],'n_estimators':[180,250,350,500,700],'learning_rate':[.02,.04,.06,.10],
       'min_child_weight':[3,5,7,10,15],'subsample':[.70,.85,1.00],'colsample_bytree':[.70,.85,1.00],
       'reg_alpha':[0,.1,.5,1.0],'reg_lambda':[5,15,25,50]}
PATH=PROJECT_ROOT/'config/xgboost_candidates.json'
def generate():
    keys=list(SPACE);grid=list(itertools.product(*(SPACE[k] for k in keys)))
    indices=np.random.default_rng(DESIGN['candidate_seed']).choice(len(grid),size=DESIGN['candidate_count'],replace=False)
    candidates=[dict(zip(keys,grid[int(i)])) for i in indices]
    return {'version':'xgboost_candidates_v3','seed':DESIGN['candidate_seed'],'search_space':SPACE,'candidates':candidates,'candidates_sha256':canonical_hash(candidates)}
def build():
    expected=generate()
    if PATH.exists() and json.loads(PATH.read_text())!=expected:raise RuntimeError('Fixed XGBoost candidate list changed unexpectedly')
    if not PATH.exists():write_json(PATH,expected)
    write_json(PROJECT_ROOT/'outputs/tables/validation/xgboost_candidates.json',expected)
    return expected
def load_candidates():
    actual=json.loads(PATH.read_text())
    if actual!=generate():raise RuntimeError('Candidate freeze mismatch')
    return actual
if __name__=='__main__':print(json.dumps(build(),indent=2))
