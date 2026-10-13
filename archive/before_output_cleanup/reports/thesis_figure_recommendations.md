# Thesis figure and table recommendations

Ten main figures and eight main tables; eight further figures belong in appendices. Full feature definitions, all-model association coefficients, robustness registry, source support and aggregate diagnostics remain appendix/supplement tables. Landscape figures are explicitly marked in the artifact manifest. Use PDF/SVG in the thesis and PNG for review.

| Placement | Kind | RQ | Artifact | Reason | Takeaway | Thesis section |

| --- | --- | --- | --- | --- | --- | --- |

| MAIN | figure | Design | [study_areas](../outputs/figures/thesis/study_areas.pdf) | Show the actual provider validation geography across all cities | Operational neighbourhoods are the geographic holdouts | Methods: study design |

| MAIN | figure | RQ1 | [nearest_access_relationship](../outputs/figures/thesis/nearest_access_relationship.pdf) | Reveal paired measurement relationships rather than isolated averages | Nearest network distances exceed straight-line distances; destinations can differ | Results: accessibility measurement |

| MAIN | figure | RQ1 | [opportunity_comparison](../outputs/figures/thesis/opportunity_comparison.pdf) | Show both food/social and culture/tourism reachability | Matched walking opportunities are lower than straight-line opportunities | Results: accessibility measurement |

| MAIN | figure | RQ2 | [primary_model_performance](../outputs/figures/thesis/primary_model_performance.pdf) | Establish all four pooled model results with fold variation | Accessibility gains depend on city and estimator | Results: within-city prediction |

| MAIN | figure | RQ2 | [paired_accessibility_contrasts](../outputs/figures/thesis/paired_accessibility_contrasts.pdf) | Put baseline gain, replacement and add-on on one clear scale | MW−ME and MEW−ME answer different comparisons | Results: accessibility contributions |

| MAIN | figure | RQ3 | [validation_strategy_comparison](../outputs/figures/thesis/validation_strategy_comparison.pdf) | Compare geographically unseen evaluation with random CV | Changing holdout geometry changes error and model ordering | Results: geographic generalization |

| MAIN | figure | RQ3 | [neighbourhood_performance_variation](../outputs/figures/thesis/neighbourhood_performance_variation.pdf) | Prevent citywide means from hiding local heterogeneity | Every heldout neighbourhood contributes an observed paired score | Results: spatial heterogeneity |

| MAIN | figure | RQ4 | [transfer_performance](../outputs/figures/thesis/transfer_performance.pdf) | Cover six directions and all model ladders in one landscape figure | Source/target combinations have heterogeneous relative-price errors | Results: cross-city transfer |

| MAIN | figure | RQ4 | [transfer_network_comparison](../outputs/figures/thesis/transfer_network_comparison.pdf) | Expose network replacement and add-on directly | Walking is not universally better than Euclidean transfer | Results: transfer accessibility contributions |

| MAIN | figure | RQ4 | [directional_transfer_asymmetry](../outputs/figures/thesis/directional_transfer_asymmetry.pdf) | Make direction reversal explicit | Different source/target tasks are not interchangeable | Results: transfer asymmetry |

| MAIN | table | Design | [city_sample_summary](../outputs/tables/thesis/city_sample_summary.md) | Compact factual basis for the associated RQ; full precision stays in CSV | Generated from explicitly pinned final SQL/results; definitions, selection limits and source identities remain unchanged. | Methods: samples |

| MAIN | table | RQ1 | [accessibility_descriptive_statistics](../outputs/tables/thesis/accessibility_descriptive_statistics.md) | Compact factual basis for the associated RQ; full precision stays in CSV | Generated from explicitly pinned final SQL/results; definitions, selection limits and source identities remain unchanged. | Results: RQ1 |

| MAIN | table | RQ2 | [primary_predictive_performance](../outputs/tables/thesis/primary_predictive_performance.md) | Compact factual basis for the associated RQ; full precision stays in CSV | Primary neighbourhood OOF RMSE by city/estimator/model; full CSV also retains MAE, R² and correlation. Four models share rows/folds. | Results: RQ2 |

| MAIN | table | RQ2 | [paired_model_contrasts](../outputs/tables/thesis/paired_model_contrasts.md) | Compact factual basis for the associated RQ; full precision stays in CSV | Candidate minus reference; negative improves. Existing95% geographic-composition stability ranges, not independent-sample confidence intervals; crossing zero is not equivalence. | Results: RQ2 |

| MAIN | table | RQ3 | [validation_comparison](../outputs/tables/thesis/validation_comparison.md) | Compact factual basis for the associated RQ; full precision stays in CSV | Spatial-block cells show the range over all six fixed configurations, not a pooled score. Full CSV retains every configuration and model. | Results: RQ3 |

| MAIN | table | RQ4 | [transfer_performance](../outputs/tables/thesis/transfer_performance.md) | Compact factual basis for the associated RQ; full precision stays in CSV | Relative-price RMSE on all six source-only directions; no target fitting/recalibration; diagonal not tested. Full CSV retains MAE, R², Pearson and Spearman. | Results: RQ4 |

| MAIN | table | RQ4 | [transfer_contrasts](../outputs/tables/thesis/transfer_contrasts.md) | Compact factual basis for the associated RQ; full precision stays in CSV | All five paired contrasts for six directions/two estimators; negative improves. Frozen95% target-neighbourhood composition stability ranges. | Results: RQ4 |

| MAIN | table | All | [claims_and_limitations](../outputs/tables/thesis/claims_and_limitations.md) | Compact factual basis for the associated RQ; full precision stays in CSV | Generated from explicitly pinned final SQL/results; definitions, selection limits and source identities remain unchanged. | Results: All |

| APPENDIX | figure | RQ1 | [accessibility_spatial](../outputs/figures/thesis/accessibility_spatial.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | Mean nearest-rail walking minutes in500 m cells with at least five observations. Shared colour scale capped at pooled95th percentile for display; uncapped aggregate values remain in the accompanying table. Boundaries are the frozen provider geography. © OpenStreetMap contributors, ODbL; Inside Airbnb CC BY4.0. | Appendix: RQ1 |

| APPENDIX | figure | RQ1 | [nearest_access_divergence](../outputs/figures/thesis/nearest_access_divergence.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | Frozen nearest-category distance excess: median dots, interquartile thick bars and5th–95th percentile thin bars. These are distribution summaries, not confidence intervals or same-object route circuity. | Appendix: RQ1 |

| APPENDIX | figure | RQ2 | [association_accessibility](../outputs/figures/thesis/association_accessibility.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | Complete-case MEW adjusted observational associations, not causal effects or predictive importance. Rail/bus Euclidean predictors use km, walking uses minutes and opportunities use log(1+count); coefficient magnitudes across different units are not rankings. HC3 intervals shown;9,999-replication restricted Webb results are in the table. Uniform10% eligibility is a disclosed post-observation amendment. | Appendix: RQ2 |

| APPENDIX | figure | RQ2 | [heldout_feature_contributions](../outputs/figures/thesis/heldout_feature_contributions.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | Existing heldout XGBoost MEW contributions only; no new SHAP calculation or model fit. Ten encoded terms selected for display by across-city mean magnitude; this does not change the model. Unavailable encodings remain missing rather than zero. Each term’s actual support is in the table. Correlated E/W attribution is descriptive, not causal. | Appendix: RQ2 |

| APPENDIX | figure | RQ3 | [robustness_contrasts](../outputs/figures/thesis/robustness_contrasts.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | Every registered predictive family: paired MW−M0 point changes and frozen95% geographic-composition stability ranges. N/A denotes native density checks inapplicable to Copenhagen/Oslo; no value is filled. Samples and measurement definitions differ across rows, so this is not an absolute-score ranking or pass/fail test. | Appendix: RQ3 |

| APPENDIX | figure | RQ4 | [transfer_accessibility_gains](../outputs/figures/thesis/transfer_accessibility_gains.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | All six directional accessibility-versus-baseline point contrasts. Same target observations within every comparison; negative values favour accessibility. These correlated directional results are not pooled into an independent significance test. | Appendix: RQ4 |

| APPENDIX | figure | RQ4 | [transfer_prediction_diagnostics](../outputs/figures/thesis/transfer_prediction_diagnostics.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | Saved XGBoost MEW predictions versus actual relative log price in all six directions. Only aggregate rectangular bins with n≥5 are displayed; every target row remains in full metrics. Shared axes; diagonal is perfect relative prediction. No row export, target fitting, smoothing or recalibration. | Appendix: RQ4 |

| APPENDIX | figure | Appendix | [residual_spatial_diagnostics](../outputs/figures/thesis/residual_spatial_diagnostics.pdf) | Useful diagnostic/complementary evidence; avoids duplicating the main narrative | Frozen8-nearest-neighbour/499-permutation diagnostics for observed outcomes and primary OOF residuals. City metric CRSs retained. Material OLS MW residual dependence triggered the registered spatial-error association sensitivity in each city; prediction gains are not a claim of independent residuals. | Appendix: Appendix |
