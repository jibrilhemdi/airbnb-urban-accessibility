"""Single V3 conceptual ladder for association and predictive evaluation."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
AMENITIES=('amenity_wifi','amenity_dishwasher','amenity_washer','amenity_dryer','amenity_workspace','amenity_free_parking','amenity_private_balcony','amenity_self_checkin')
CATEGORICAL=('property_type',)
BASE_NUMERIC=('accommodates','bedrooms','bathrooms_effective','log1p_minimum_nights','superhost','log1p_host_listings_count',*AMENITIES,
              'log_population_density','income_100k_dkk','distance_centre_euclidean_km')
E_NUMERIC=('nearest_station_euclidean_km','nearest_bus_euclidean_km','log1p_food_e','log1p_culture_e')
W_NUMERIC=('nearest_station_walking_minutes','nearest_bus_walking_minutes','log1p_food_w','log1p_culture_w')
FEATURES={'M0':BASE_NUMERIC+CATEGORICAL,'ME':BASE_NUMERIC+E_NUMERIC+CATEGORICAL,'MW':BASE_NUMERIC+W_NUMERIC+CATEGORICAL,'MEW':BASE_NUMERIC+E_NUMERIC+W_NUMERIC+CATEGORICAL}
NO_INCOME_FEATURES={name+'_no_income':tuple(c for c in cols if c!='income_100k_dkk') for name,cols in FEATURES.items()}
ALL_FEATURES={**FEATURES,**NO_INCOME_FEATURES}
def prepare_features(frame):
    result=frame.copy()
    for source,target in [('nearest_station_euclidean_m','nearest_station_euclidean_km'),('nearest_bus_euclidean_m','nearest_bus_euclidean_km')]:
        result[target]=pd.to_numeric(result[source],errors='raise')/1000
    for source,target in [('food_social_833m','log1p_food_e'),('cultural_tourist_833m','log1p_culture_e'),('food_social_w_10','log1p_food_w'),('cultural_tourist_w_10','log1p_culture_w')]:
        value=pd.to_numeric(result[source],errors='raise')
        if (value.dropna()<0).any():raise RuntimeError('Negative opportunity value')
        result[target]=np.log1p(value)
    for col in set(BASE_NUMERIC+E_NUMERIC+W_NUMERIC):result[col]=pd.to_numeric(result[col],errors='raise').astype(float)
    if result.log_price.isna().any() or not np.isfinite(result.log_price).all():raise RuntimeError('Outcome is missing/nonfinite; never impute')
    if (result.price_nightly<=0).any() or not np.allclose(result.log_price,np.log(result.price_nightly.astype(float))):raise RuntimeError('Invalid observed outcome')
    return result

def build_preprocessor(feature_set,extra_features=()):
    columns=ALL_FEATURES[feature_set]+tuple(extra_features)
    cats=[c for c in columns if c in CATEGORICAL or c=='analysis_area']
    nums=[c for c in columns if c not in cats]
    return ColumnTransformer([('numeric',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),nums),
        ('category',OneHotEncoder(drop='first',handle_unknown='ignore',sparse_output=False),cats)],
        remainder='drop',verbose_feature_names_out=False)
