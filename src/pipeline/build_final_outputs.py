"""Publication exports generated exclusively from the current V3 database run."""
from __future__ import annotations
import pandas as pd
from sqlalchemy import text
from src.ingestion.common import PROJECT_ROOT,write_json
from src.pipeline.output_paths import output_file
from src.pipeline.model_specification import FEATURES
from src.pipeline.storage import load_artifact,export
from src.pipeline.build_analysis_dataset import load_dataset

def run(engine,run_id):
    with engine.connect() as conn:
        run=conn.execute(text('SELECT metadata FROM v3_analysis.runs WHERE run_id=:run'),{'run':run_id}).scalar_one()
        frame=load_dataset(conn)
        tables={name:load_artifact(conn,run_id,'primary_models',name) for name in ['ols_coefficients','ols_ladder','model_performance','fold_performance','incremental_performance','incremental_by_analysis_area','spatial_moran','aggregate_shap']}
        tables['robustness_summary']=load_artifact(conn,run_id,'robustness','model_performance')
        for name in ['accessibility_coefficient_comparison','performance_comparison','incremental_comparison',
            'geographic_area_performance_comparison','geographic_area_incremental_comparison','conclusion_flags']:
            tables['income_'+name]=load_artifact(conn,run_id,'income_robustness',name)
    if any(t.empty for t in tables.values()):raise RuntimeError('Incomplete current results; publication export refuses partial/legacy substitutions')
    from src.pipeline.protocol import DESIGN
    from src.pipeline.build_tuning_candidates import load_candidates
    definitions=pd.DataFrame([{'measure':'rail Euclidean','unit':'km','role':'core ME/MEW'}, {'measure':'bus Euclidean','unit':'km','role':'core ME/MEW'},
        {'measure':'rail walking','unit':'minutes at 5.0 km/h','role':'core MW/MEW'}, {'measure':'bus walking','unit':'minutes at 5.0 km/h','role':'core MW/MEW'},
        {'measure':'food/social and cultural/tourist opportunities','unit':'log(1 + count); 10 network min / 833 Euclidean m','role':'primary matched opportunities'},
        {'measure':'threshold sensitivity','unit':'15/20 min at 5 km/h; 1250/1667 m','role':'robustness'},
        {'measure':'speed sensitivity','unit':'10 min at 4.0/5.4 km/h; 667/900 m','role':'robustness'},
        {'measure':'continuous decay','unit':'log(1 + sum(exp(-ln(2)*minutes/10)))','role':'robustness; full frozen destination universe'}])
    tables['accessibility_definitions']=definitions
    with engine.connect() as conn:tables['analysis_area_context']=pd.read_sql(text('SELECT analysis_area,analysis_area_name,population_count,population_period,area_km2,log_population_density,equiv_disposable_income_2024,income_100k_dkk,income_period,income_harmonisation_status,crs_epsg FROM v3_features.area_context ORDER BY analysis_area'),conn)
    tables['sample_construction']=pd.DataFrame(run['component_results']['frozen_analysis_dataset_and_dictionary']['sample_construction'])
    paths=[]
    for name,table in tables.items():paths.append(export('reporting',name+'.csv',table).relative_to(PROJECT_ROOT).as_posix())
    descriptions=frame[list(FEATURES['MEW'])+['log_price']].select_dtypes(include='number').describe().T.reset_index(names='variable')
    export('reporting','descriptive_statistics.csv',descriptions)
    from src.pipeline.reporting_figures import run as render_figures
    figure_manifest=render_figures(engine,run_id,frame,tables)
    paths.extend(path for figure in figure_manifest['figures'] for path in figure['paths'])
    report=['# Version 3 research results','',f'Run `{run_id}`; analytical dataset N = {len(frame):,}; 11 peer analysis areas.','',
        'Core M0 contains property, prespecified amenities, host/rental variables, area density, harmonised income and City Hall centrality. Rail and bus enter separately in the Euclidean and walking blocks.','',
        'The baseline assumes 5.0 km/h and a 10-minute network budget with an 833 m rounded Euclidean analogue. Threshold, speed and continuous-decay checks are distinct prespecified sensitivities.','',
        'Random CV assesses another spatially interspersed listing in the same market; geographic CV assesses an analysis area absent from training.','',
        'OLS coefficients are conditional associations. HC3 intervals and area wild-cluster bootstrap-t inference are both reported. Held-out SHAP explains predictions; no causal interpretation.','']
    for name in ['model_performance','incremental_performance','ols_ladder','spatial_moran']:
        report.extend([f'## {name.replace("_"," ").title()}','',tables[name].to_string(index=False),''])
    from src.pipeline.qualified_income import METHODS_TEXT
    report.extend(['## Methods/Data: area income','',METHODS_TEXT,'',
        '## Income robustness','',
        'Accessibility conclusions materially change under the prespecified flags: '+
        ('YES — review the flagged coefficient directions and/or paired error/ranking reversals.'
         if tables['income_conclusion_flags'].material_change.any() else
         'No material direction/ranking reversal was flagged under the prespecified rules; magnitude sensitivity remains reported.'),'',
        tables['income_conclusion_flags'].to_string(index=False),'',
        'RMSE, MAE, R² and paired ΔRMSE changes and all eleven geographic area results are in the accompanying income comparison tables.','',
        '## Limitations','',
        'Income has qualified cross-source comparability; exact table processing and KKIND5 raw price basis remain unresolved. '
        'The mandatory no-income sensitivity quantifies dependence on this control.',''])
    (PROJECT_ROOT/'reports').mkdir(exist_ok=True);(PROJECT_ROOT/'reports/research_results_v3.md').write_text('\n'.join(report))
    write_json(PROJECT_ROOT/'outputs/tables/reporting/output_manifest.json',{'run_id':run_id,'outputs':paths,'source':'v3_analysis artifacts','publication_row_level_coordinates':False})
    return {'publication_outputs':len(paths)}
