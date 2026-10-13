# Findings by research question

Copenhagen includes Frederiksberg. All values below come from the final-run registered tables; no historical numeric result is substituted.

## RQ1

### 1. Evidence used

[accessibility descriptive statistics](../outputs/tables/thesis/accessibility_descriptive_statistics.md); [nearest access divergence](../outputs/metrics/thesis/nearest_access_divergence.md); nearest relationships, opportunities and suppressed spatial maps.

### 2. Headline result

Network and straight-line representations differ despite matched destination universes: walking nearest-category distances are longer and median reachable opportunities are fewer in these three samples.

### 3. Important quantitative results

| City | Concept | Euclidean median | Walking median | Unit |
| --- | --- | --- | --- | --- |
| Copenhagen | station | 0.4044 | 0.6375 | km |
| Copenhagen | bus | 0.1296 | 0.2186 | km |
| Oslo | station | 0.6683 | 0.8966 | km |
| Oslo | bus | 0.1371 | 0.2187 | km |
| Stockholm | station | 0.3881 | 0.6404 | km |
| Stockholm | bus | 0.1234 | 0.2167 | km |

| City | Concept | Euclidean median | Walking median | Unit |
| --- | --- | --- | --- | --- |
| Copenhagen | food | 84.0000 | 47.0000 | destinations |
| Copenhagen | culture | 6.0000 | 3.0000 | destinations |
| Oslo | food | 63.0000 | 35.0000 | destinations |
| Oslo | culture | 8.0000 | 4.0000 | destinations |
| Stockholm | food | 51.0000 | 28.0000 | destinations |
| Stockholm | culture | 4.0000 | 2.0000 | destinations |

### 4. City heterogeneity

Distance distributions, food/culture opportunity levels and within-city spatial variation differ. Absolute counts also reflect different destination universes and source completeness.

### 5. Robustness

Frozen15/20-minute, speed4/5.4 km/h, continuous decay and boundary-exclusion results are accounted for in the robustness registry; they do not redefine the primary10-minute/833 m comparison.

### 6. Interpretation

Representations change the measured proximity/reachability concept. Nearest Euclidean and network destinations may differ, so distance excess is not same-destination route circuity.

### 7. What cannot be claimed

No causal price effect, perfect OSM completeness, exact official neighbourhood equivalence or same-object route-circuity claim.

### 8. Recommended figures/tables

Main: nearest-access relationships and opportunity comparison; T3. Appendix: nearest distance excess and accessibility maps.

## RQ2

### 1. Evidence used

[primary predictive performance](../outputs/tables/thesis/primary_predictive_performance.md); [paired model contrasts](../outputs/tables/thesis/paired_model_contrasts.md); [association results](../outputs/tables/thesis/association_results.md); existing heldout contributions.

### 2. Headline result

Primary accessibility models lower XGBoost point RMSE in Copenhagen and Stockholm but produce small adverse point changes in Oslo. Representation replacement and add-on are distinct; walking is not universally superior.

### 3. Important quantitative results

| City | Model | ΔRMSE | % RMSE change | Stability low | Stability high |
| --- | --- | --- | --- | --- | --- |
| Copenhagen | ME | -0.009018 | -2.658144 | -0.016745 | -0.001492 |
| Copenhagen | MW | -0.009465 | -2.789890 | -0.022469 | 0.001358 |
| Copenhagen | MEW | -0.010669 | -3.144927 | -0.021869 | -0.000223 |
| Oslo | ME | 0.000679 | 0.194344 | -0.003069 | 0.004772 |
| Oslo | MW | 0.000879 | 0.251548 | -0.002979 | 0.005006 |
| Oslo | MEW | 0.002358 | 0.674853 | -0.000962 | 0.006384 |
| Stockholm | ME | -0.017091 | -4.206129 | -0.028548 | 0.001864 |
| Stockholm | MW | -0.019894 | -4.895905 | -0.032410 | -0.000879 |
| Stockholm | MEW | -0.018586 | -4.573968 | -0.031086 | 0.001189 |

| city | estimator | added | reference | delta_rmse | stability_low | stability_high |
| --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | OLS | MW | ME | 0.002413 | 0.000542 | 0.004102 |
| Copenhagen | OLS | MEW | ME | 0.001135 | 0.000626 | 0.001749 |
| Copenhagen | XGBoost | MW | ME | -0.000447 | -0.006876 | 0.005589 |
| Copenhagen | XGBoost | MEW | ME | -0.001651 | -0.005452 | 0.001356 |
| Oslo | OLS | MW | ME | 0.000623 | -0.000556 | 0.001638 |
| Oslo | OLS | MEW | ME | 0.000482 | -0.000336 | 0.001402 |
| Oslo | XGBoost | MW | ME | 0.000200 | -0.001102 | 0.001566 |
| Oslo | XGBoost | MEW | ME | 0.001679 | 0.000845 | 0.002656 |
| Stockholm | OLS | MW | ME | 0.000473 | -0.002092 | 0.003241 |
| Stockholm | OLS | MEW | ME | -0.001349 | -0.002712 | 0.000250 |
| Stockholm | XGBoost | MW | ME | -0.002803 | -0.006942 | 0.001032 |
| Stockholm | XGBoost | MEW | ME | -0.001495 | -0.004739 | 0.001791 |

### 4. City heterogeneity

The direction and magnitude vary by city and estimator. Complementary complete-case OLS associations describe adjustments conditional on X/E/W, not the heldout predictive estimand.

### 5. Robustness

Frozen paired ranges describe neighbourhood-composition stability, not independent-sample confidence intervals. Reputation/tail/sample variants and geographic designs qualify the primary point pattern.

### 6. Interpretation

Incremental prediction concerns information under the specified evaluation. HC3 and9,999 restricted Webb results are separately reported; SHAP allocation among correlated features is descriptive.

### 7. What cannot be claimed

No causal coefficients, universal network superiority, significance from citywide point differences alone or statistical equivalence from overlapping intervals. The10% association eligibility change was post-observation.

### 8. Recommended figures/tables

Main: model performance and all five paired contrasts; T4/T5. Appendix: complete-case coefficient figure/full T6 and frozen heldout feature contributions.

## RQ3

### 1. Evidence used

[validation comparison](../outputs/tables/thesis/validation_comparison.md); [neighbourhood performance](../outputs/metrics/thesis/neighbourhood_performance.md); [robustness registry](../outputs/tables/thesis/robustness_registry.md).

### 2. Headline result

Geographic holdouts increase baseline error relative to random CV in these primary tasks, and accessibility gains vary across heldout neighbourhoods and geometric configurations.

### 3. Important quantitative results

| City | Estimator | Primary M0 RMSE | Random M0 RMSE | MW improves geometric variants | Geometric variants |
| --- | --- | --- | --- | --- | --- |
| Copenhagen | OLS | 0.335021 | 0.325305 | 6 | 6 |
| Copenhagen | XGBoost | 0.339247 | 0.310875 | 5 | 6 |
| Oslo | OLS | 0.358725 | 0.355792 | 3 | 6 |
| Oslo | XGBoost | 0.349470 | 0.338318 | 0 | 6 |
| Stockholm | OLS | 0.438915 | 0.415671 | 6 | 6 |
| Stockholm | XGBoost | 0.406336 | 0.366871 | 2 | 6 |

### 4. City heterogeneity

The geometric sign counts are descriptive comparisons of six correlated fixed configurations. They do not turn a neighbourhood gain into universal geographically unseen improvement.

### 5. Robustness

All registered statuses remain explicit. Within-variant paired changes are comparable within each row; absolute errors across sample-changing variants are not a model-selection ranking.

### 6. Interpretation

Validation geography changes the prediction task. Few groups, uneven fold sizes, overlapping training data and residual spatial dependence qualify stability and generalization statements.

### 7. What cannot be claimed

No independent replication across grids, universal superiority, spatially independent errors or generalization to all Nordic cities.

### 8. Recommended figures/tables

Main: strategy comparison and heldout-neighbourhood variation; T7. Appendix: robustness contrasts/full T10 and spatial diagnostics.

## RQ4

### 1. Evidence used

[transfer performance](../outputs/tables/thesis/transfer_performance.md); [transfer contrasts](../outputs/tables/thesis/transfer_contrasts.md); [directional transfer asymmetry](../outputs/metrics/thesis/directional_transfer_asymmetry.md); suppressed frozen-prediction diagnostics.

### 2. Headline result

Relative-price transfer depends on source/target direction, estimator and representation. Accessibility helps in some directions and hurts in others; source-only transfer is not interchangeable across cities.

### 3. Important quantitative results

| Estimator | Model | Improving directions | Directions |
| --- | --- | --- | --- |
| OLS | ME | 5 | 6 |
| OLS | MW | 5 | 6 |
| OLS | MEW | 5 | 6 |
| XGBoost | ME | 4 | 6 |
| XGBoost | MW | 3 | 6 |
| XGBoost | MEW | 4 | 6 |

| first_city | second_city | estimator | model | forward_rmse | reverse_rmse | forward_minus_reverse_rmse |
| --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | Oslo | OLS | M0 | 0.377704 | 0.339232 | 0.038473 |
| Copenhagen | Oslo | OLS | ME | 0.371632 | 0.337430 | 0.034202 |
| Copenhagen | Oslo | OLS | MW | 0.374375 | 0.338523 | 0.035852 |
| Copenhagen | Oslo | OLS | MEW | 0.371552 | 0.337877 | 0.033675 |
| Copenhagen | Oslo | XGBoost | M0 | 0.364294 | 0.335600 | 0.028693 |
| Copenhagen | Oslo | XGBoost | ME | 0.365437 | 0.336783 | 0.028653 |
| Copenhagen | Oslo | XGBoost | MW | 0.369727 | 0.337445 | 0.032282 |
| Copenhagen | Oslo | XGBoost | MEW | 0.366639 | 0.339070 | 0.027570 |
| Copenhagen | Stockholm | OLS | M0 | 0.446377 | 0.353722 | 0.092655 |
| Copenhagen | Stockholm | OLS | ME | 0.432667 | 0.342665 | 0.090001 |
| Copenhagen | Stockholm | OLS | MW | 0.434201 | 0.343189 | 0.091013 |
| Copenhagen | Stockholm | OLS | MEW | 0.432603 | 0.344650 | 0.087953 |
| Copenhagen | Stockholm | XGBoost | M0 | 0.428611 | 0.351472 | 0.077138 |
| Copenhagen | Stockholm | XGBoost | ME | 0.413639 | 0.342660 | 0.070978 |
| Copenhagen | Stockholm | XGBoost | MW | 0.417356 | 0.346121 | 0.071234 |
| Copenhagen | Stockholm | XGBoost | MEW | 0.413559 | 0.345986 | 0.067573 |
| Oslo | Stockholm | OLS | M0 | 0.437073 | 0.392293 | 0.044780 |
| Oslo | Stockholm | OLS | ME | 0.432868 | 0.404841 | 0.028027 |
| Oslo | Stockholm | OLS | MW | 0.435755 | 0.397645 | 0.038110 |
| Oslo | Stockholm | OLS | MEW | 0.432557 | 0.405690 | 0.026867 |
| Oslo | Stockholm | XGBoost | M0 | 0.425962 | 0.383695 | 0.042267 |
| Oslo | Stockholm | XGBoost | ME | 0.424414 | 0.380354 | 0.044060 |
| Oslo | Stockholm | XGBoost | MW | 0.426995 | 0.381576 | 0.045419 |
| Oslo | Stockholm | XGBoost | MEW | 0.425788 | 0.379199 | 0.046589 |

### 4. City heterogeneity

Each direction changes source covariate support and target distribution/sample size. Price centring removes citywide mean levels but not dispersion or conditional relationships.

### 5. Robustness

All four models use identical target rows within each direction. Existing target-neighbourhood composition ranges are preserved; the identical source pipeline serves its two outgoing targets.

### 6. Interpretation

These experiments evaluate structural relative-price transfer with an observed target benchmark; no target fitting, tuning, recalibration or pooled-source model is used.

### 7. What cannot be claimed

No zero-shot absolute-price deployment or pseudo-independent six-direction significance test. Prediction diagnostic slopes and bins never alter model parameters.

### 8. Recommended figures/tables

Main: performance matrices, network replacement/add-on and reversal asymmetry; T8/T9. Appendix: baseline-gain matrices and saved-prediction diagnostic panels.
