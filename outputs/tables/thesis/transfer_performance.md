# Transfer Performance

Relative-price RMSE on all six source-only directions; no target fitting/recalibration; diagonal not tested. Full CSV retains MAE, R², Pearson and Spearman.

| source_city | target_city | estimator | M0 | ME | MW | MEW |
| --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | Oslo | OLS | 0.3777 | 0.3716 | 0.3744 | 0.3716 |
| Copenhagen | Oslo | XGBoost | 0.3643 | 0.3654 | 0.3697 | 0.3666 |
| Copenhagen | Stockholm | OLS | 0.4464 | 0.4327 | 0.4342 | 0.4326 |
| Copenhagen | Stockholm | XGBoost | 0.4286 | 0.4136 | 0.4174 | 0.4136 |
| Oslo | Copenhagen | OLS | 0.3392 | 0.3374 | 0.3385 | 0.3379 |
| Oslo | Copenhagen | XGBoost | 0.3356 | 0.3368 | 0.3374 | 0.3391 |
| Oslo | Stockholm | OLS | 0.4371 | 0.4329 | 0.4358 | 0.4326 |
| Oslo | Stockholm | XGBoost | 0.4260 | 0.4244 | 0.4270 | 0.4258 |
| Stockholm | Copenhagen | OLS | 0.3537 | 0.3427 | 0.3432 | 0.3447 |
| Stockholm | Copenhagen | XGBoost | 0.3515 | 0.3427 | 0.3461 | 0.3460 |
| Stockholm | Oslo | OLS | 0.3923 | 0.4048 | 0.3976 | 0.4057 |
| Stockholm | Oslo | XGBoost | 0.3837 | 0.3804 | 0.3816 | 0.3792 |
