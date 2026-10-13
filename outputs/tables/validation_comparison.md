# Validation Comparison

Spatial-block cells show the range over all six fixed configurations, not a pooled score. Full CSV retains every configuration and model.

| city | estimator | validation | M0 | ME | MW | MEW |
| --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | OLS | Random | 0.3253 | 0.3199 | 0.3212 | 0.3200 |
| Copenhagen | OLS | Neighbourhood | 0.3350 | 0.3263 | 0.3287 | 0.3274 |
| Copenhagen | OLS | Spatial blocks: six-design range | 0.3265–0.3306 | 0.3213–0.3246 | 0.3226–0.3265 | 0.3219–0.3255 |
| Copenhagen | XGBoost | Random | 0.3109 | 0.3090 | 0.3088 | 0.3109 |
| Copenhagen | XGBoost | Neighbourhood | 0.3392 | 0.3302 | 0.3298 | 0.3286 |
| Copenhagen | XGBoost | Spatial blocks: six-design range | 0.3145–0.3202 | 0.3151–0.3204 | 0.3148–0.3190 | 0.3156–0.3196 |
| Oslo | OLS | Random | 0.3558 | 0.3549 | 0.3552 | 0.3548 |
| Oslo | OLS | Neighbourhood | 0.3587 | 0.3589 | 0.3595 | 0.3594 |
| Oslo | OLS | Spatial blocks: six-design range | 0.3566–0.3592 | 0.3562–0.3592 | 0.3565–0.3595 | 0.3564–0.3598 |
| Oslo | XGBoost | Random | 0.3383 | 0.3371 | 0.3383 | 0.3380 |
| Oslo | XGBoost | Neighbourhood | 0.3495 | 0.3501 | 0.3503 | 0.3518 |
| Oslo | XGBoost | Spatial blocks: six-design range | 0.3423–0.3495 | 0.3429–0.3489 | 0.3446–0.3496 | 0.3437–0.3503 |
| Stockholm | OLS | Random | 0.4157 | 0.4064 | 0.4066 | 0.4063 |
| Stockholm | OLS | Neighbourhood | 0.4389 | 0.4138 | 0.4143 | 0.4124 |
| Stockholm | OLS | Spatial blocks: six-design range | 0.4168–0.4228 | 0.4071–0.4124 | 0.4075–0.4121 | 0.4067–0.4118 |
| Stockholm | XGBoost | Random | 0.3669 | 0.3710 | 0.3663 | 0.3690 |
| Stockholm | XGBoost | Neighbourhood | 0.4063 | 0.3892 | 0.3864 | 0.3878 |
| Stockholm | XGBoost | Spatial blocks: six-design range | 0.3729–0.3787 | 0.3765–0.3825 | 0.3759–0.3831 | 0.3755–0.3861 |
