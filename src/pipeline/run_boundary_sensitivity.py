"""Boundary-adjacency sensitivity using frozen buffered geographic holdouts.

The matched full extraction universe is retained in every comparison. This
module routes the already prespecified buffer variants to the common evaluator.
"""
from src.pipeline.build_analysis_dataset import load_dataset
from src.pipeline.build_validation_splits import saved_outer
from src.pipeline.run_primary_models import evaluate_cv

def run(engine,run_id):
    with engine.connect() as conn:
        frame=load_dataset(conn);outer=saved_outer(conn,frame)
    buffered={name:folds for name,folds in outer.items() if name.startswith('buffered_area_')}
    if len(buffered)!=2:raise RuntimeError('Both frozen buffer geometries are required')
    return evaluate_cv(frame,buffered,engine,run_id,family='robustness',shap=False)
