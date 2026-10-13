# Residual Spatial Diagnostics

Complete safe aggregate evidence; no individual source/prediction/location rows.

| city | metric_crs | k | n | seed | model | moran_i | crs_epsg | variable | estimator | expected_i | permutations | directed_edges | permutation_mean | permutation_p_two_sided |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | EPSG:25832 | 8 | 12408 | 20261004 | none | 0.2467 | 25832 | log_price | none | -0.0001 | 499 | 99264 | -0.0001 | 0.0020 |
| Copenhagen | EPSG:25832 | 8 | 12408 | 20261004 | M0 | 0.1409 | 25832 | oof_residual | OLS | -0.0001 | 499 | 99264 | 0.0001 | 0.0020 |
| Copenhagen | EPSG:25832 | 8 | 12408 | 20261004 | MW | 0.1091 | 25832 | oof_residual | OLS | -0.0001 | 499 | 99264 | 0.0002 | 0.0020 |
| Copenhagen | EPSG:25832 | 8 | 12408 | 20261004 | M0 | 0.1789 | 25832 | oof_residual | XGBoost | -0.0001 | 499 | 99264 | 0.0001 | 0.0020 |
| Copenhagen | EPSG:25832 | 8 | 12408 | 20261004 | MW | 0.1347 | 25832 | oof_residual | XGBoost | -0.0001 | 499 | 99264 | 0.0002 | 0.0020 |
| Oslo | EPSG:25833 | 8 | 8529 | 20261004 | none | 0.1934 | 25832 | log_price | none | -0.0001 | 499 | 68232 | 0.0000 | 0.0020 |
| Oslo | EPSG:25833 | 8 | 8529 | 20261004 | M0 | 0.1060 | 25832 | oof_residual | OLS | -0.0001 | 499 | 68232 | -0.0001 | 0.0020 |
| Oslo | EPSG:25833 | 8 | 8529 | 20261004 | MW | 0.1072 | 25832 | oof_residual | OLS | -0.0001 | 499 | 68232 | -0.0001 | 0.0020 |
| Oslo | EPSG:25833 | 8 | 8529 | 20261004 | M0 | 0.1142 | 25832 | oof_residual | XGBoost | -0.0001 | 499 | 68232 | 0.0001 | 0.0020 |
| Oslo | EPSG:25833 | 8 | 8529 | 20261004 | MW | 0.1098 | 25832 | oof_residual | XGBoost | -0.0001 | 499 | 68232 | 0.0001 | 0.0020 |
| Stockholm | EPSG:3006 | 8 | 2495 | 20261004 | none | 0.2076 | 25832 | log_price | none | -0.0004 | 499 | 19960 | -0.0004 | 0.0020 |
| Stockholm | EPSG:3006 | 8 | 2495 | 20261004 | M0 | 0.1818 | 25832 | oof_residual | OLS | -0.0004 | 499 | 19960 | -0.0015 | 0.0020 |
| Stockholm | EPSG:3006 | 8 | 2495 | 20261004 | MW | 0.0939 | 25832 | oof_residual | OLS | -0.0004 | 499 | 19960 | -0.0013 | 0.0020 |
| Stockholm | EPSG:3006 | 8 | 2495 | 20261004 | M0 | 0.2017 | 25832 | oof_residual | XGBoost | -0.0004 | 499 | 19960 | -0.0010 | 0.0020 |
| Stockholm | EPSG:3006 | 8 | 2495 | 20261004 | MW | 0.1110 | 25832 | oof_residual | XGBoost | -0.0004 | 499 | 19960 | -0.0011 | 0.0020 |
