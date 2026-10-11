"""One spatial-error association sensitivity, conditional on residual diagnostics."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from libpysal.weights import KNN
from spreg import GM_Error_Het
from src.pipeline.model_specification import FEATURES,build_preprocessor,BASE_NUMERIC,CATEGORICAL
from src.pipeline.storage import persist,export,load_artifact
from src.pipeline.build_analysis_dataset import load_dataset

def area_fixed_effects(frame):
    rows=[]
    # Context is constant within area and is absorbed by area effects. Omitting
    # its separate slopes is a declared identification requirement, not selection.
    for fs in FEATURES:
        cols=[c for c in FEATURES[fs] if c not in ['log_population_density','income_100k_dkk']]
        complete=frame.dropna(subset=cols+['log_price'])
        numeric=[c for c in cols if c not in CATEGORICAL]
        dummies=pd.get_dummies(complete[['property_type','analysis_area']],drop_first=True,dtype=float)
        X=sm.add_constant(np.column_stack([complete[numeric].to_numpy(float),dummies.to_numpy(float)]),has_constant='add')
        names=['Intercept',*numeric,*dummies.columns]
        if np.linalg.matrix_rank(X)!=X.shape[1]:raise RuntimeError('Area fixed-effects design not identified')
        fit=sm.OLS(complete.log_price.to_numpy(float),X).fit(cov_type='HC3');ci=fit.conf_int()
        rows.extend({'feature_set':fs,'term':name,'coefficient':float(fit.params[i]),'hc3_se':float(fit.bse[i]),'hc3_ci_low':float(ci[i,0]),'hc3_ci_high':float(ci[i,1]),'n':len(complete),
            'scope':'within-analysis-area conditional association; context absorbed'} for i,name in enumerate(names))
    return pd.DataFrame(rows)

def run(engine,run_id):
    with engine.connect() as conn:
        diagnostics=load_artifact(conn,run_id,'primary_models','spatial_moran');frame=load_dataset(conn)
    selected=diagnostics.loc[(diagnostics.variable=='residual')&(diagnostics.model=='OLS')&(diagnostics.feature_set=='MW')]
    justified=bool(len(selected) and ((selected.moran_i.abs()>.05)&(selected.permutation_p_two_sided<.05)).any())
    metadata={'status':'run' if justified else 'not_justified_by_prespecified_diagnostic','diagnostic_rule':'absolute Moran I > .05 and permutation p < .05 in OLS MW geographic residuals','crs_epsg':25832}
    if justified:
        complete=frame.dropna(subset=list(FEATURES['MW']));prep=build_preprocessor('MW');X=prep.fit_transform(complete)
        w=KNN.from_array(complete[['metric_x','metric_y']].to_numpy(float),k=8);w.transform='R'
        fit=GM_Error_Het(complete.log_price.to_numpy(float).reshape(-1,1),np.asarray(X,float),w=w,name_x=list(prep.get_feature_names_out()),name_y='log_price')
        rows=pd.DataFrame([{'term':name,'coefficient':float(beta),'standard_error':float(se),'n':len(complete),'scope':'spatial-error conditional association robustness'}
            for name,beta,se in zip(fit.name_x,np.asarray(fit.betas).ravel(),np.asarray(fit.std_err).ravel())])
        with engine.begin() as conn:persist(conn,run_id,'robustness','spatial_error_coefficients',rows)
        export('robustness','spatial_error_coefficients.csv',rows)
    with engine.begin() as conn:persist(conn,run_id,'robustness','spatial_error_metadata',[metadata])
    export('robustness','spatial_error_metadata.csv',pd.DataFrame([metadata]));return metadata
