# Generated findings and interpretation

Read with the [publication research handover](research_report_publication.md). All numerical values below are extracted from verified authoritative SQL summaries by `python -m src.reporting.study_findings`; no previous analysis value or result prose is substituted.

## RQ1: representation changes measurement

| city | concept | unit | euclidean_median | walking_median |
| --- | --- | --- | --- | --- |
| copenhagen | station | km | 0.404388 | 0.637527 |
| copenhagen | bus | km | 0.129573 | 0.218617 |
| copenhagen | food | 10-minute opportunities | 84.000000 | 47.000000 |
| copenhagen | culture | 10-minute opportunities | 6.000000 | 3.000000 |
| oslo | station | km | 0.668309 | 0.896561 |
| oslo | bus | km | 0.137144 | 0.218729 |
| oslo | food | 10-minute opportunities | 63.000000 | 35.000000 |
| oslo | culture | 10-minute opportunities | 8.000000 | 4.000000 |
| stockholm | station | km | 0.388101 | 0.640361 |
| stockholm | bus | km | 0.123360 | 0.216729 |
| stockholm | food | 10-minute opportunities | 51.000000 | 28.000000 |
| stockholm | culture | 10-minute opportunities | 4.000000 | 2.000000 |

Network travel generally lengthens nearest-category distances and reduces the median locally reachable opportunities relative to matched straight-line measures. The table describes the analytical sample, not all destinations or listings in a city. Nearest destinations can differ between representations, so these differences are not same-destination circuity. The map and full distributions provide the spatial and distributional detail.

## RQ2: incremental within-city prediction

| city | estimator | model | delta_rmse | percentage_change | stability_low | stability_high |
| --- | --- | --- | --- | --- | --- | --- |
| copenhagen | OLS | ME | -0.008731 | -2.606035 | -0.019692 | 0.001516 |
| copenhagen | OLS | MW | -0.006318 | -1.885778 | -0.015758 | 0.002396 |
| copenhagen | OLS | MEW | -0.007596 | -2.267202 | -0.017976 | 0.002327 |
| copenhagen | XGBoost | ME | -0.009018 | -2.658144 | -0.016745 | -0.001492 |
| copenhagen | XGBoost | MW | -0.009465 | -2.789890 | -0.022469 | 0.001358 |
| copenhagen | XGBoost | MEW | -0.010669 | -3.144927 | -0.021869 | -0.000223 |
| oslo | OLS | ME | 0.000157 | 0.043628 | -0.001729 | 0.002794 |
| oslo | OLS | MW | 0.000779 | 0.217276 | -0.000776 | 0.003461 |
| oslo | OLS | MEW | 0.000639 | 0.178028 | -0.001175 | 0.003326 |
| oslo | XGBoost | ME | 0.000679 | 0.194344 | -0.003069 | 0.004772 |
| oslo | XGBoost | MW | 0.000879 | 0.251548 | -0.002979 | 0.005006 |
| oslo | XGBoost | MEW | 0.002358 | 0.674853 | -0.000962 | 0.006384 |
| stockholm | OLS | ME | -0.025118 | -5.722668 | -0.034614 | -0.010542 |
| stockholm | OLS | MW | -0.024645 | -5.614934 | -0.032770 | -0.010931 |
| stockholm | OLS | MEW | -0.026466 | -6.029937 | -0.035391 | -0.011908 |
| stockholm | XGBoost | ME | -0.017091 | -4.206129 | -0.028548 | 0.001864 |
| stockholm | XGBoost | MW | -0.019894 | -4.895905 | -0.032410 | -0.000879 |
| stockholm | XGBoost | MEW | -0.018586 | -4.573968 | -0.031086 | 0.001189 |

Negative changes favour the accessibility model. The neighbourhood results show improvements in Copenhagen and Stockholm, with small adverse changes in Oslo. Walking is not universally superior to Euclidean accessibility, and adding both representations does not always beat either alone. The reported stability ranges describe geographic composition sensitivity; their signs do not establish causal effects or statistical equivalence.

## RQ3: gains depend on geographic separation

| city | estimator | model | primary_delta_rmse | random_delta_rmse | improving_geometric_variants | geometric_variants | geometric_delta_min | geometric_delta_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| copenhagen | OLS | ME | -0.008731 | -0.005372 | 6 | 6 | -0.006531 | -0.004387 |
| copenhagen | OLS | MW | -0.006318 | -0.004085 | 6 | 6 | -0.004593 | -0.003559 |
| copenhagen | OLS | MEW | -0.007596 | -0.005262 | 6 | 6 | -0.006005 | -0.004208 |
| copenhagen | XGBoost | ME | -0.009018 | -0.001861 | 4 | 6 | -0.001608 | 0.000664 |
| copenhagen | XGBoost | MW | -0.009465 | -0.002095 | 5 | 6 | -0.002169 | 0.000748 |
| copenhagen | XGBoost | MEW | -0.010669 | 0.000070 | 5 | 6 | -0.002361 | 0.001313 |
| oslo | OLS | ME | 0.000157 | -0.000925 | 3 | 6 | -0.000879 | 0.000702 |
| oslo | OLS | MW | 0.000779 | -0.000572 | 3 | 6 | -0.000503 | 0.001626 |
| oslo | OLS | MEW | 0.000639 | -0.000978 | 2 | 6 | -0.000683 | 0.001632 |
| oslo | XGBoost | ME | 0.000679 | -0.001228 | 1 | 6 | -0.000630 | 0.003558 |
| oslo | XGBoost | MW | 0.000879 | -0.000004 | 0 | 6 | 0.000096 | 0.003026 |
| oslo | XGBoost | MEW | 0.002358 | -0.000302 | 0 | 6 | 0.000779 | 0.004275 |
| stockholm | OLS | ME | -0.025118 | -0.009273 | 6 | 6 | -0.011286 | -0.009433 |
| stockholm | OLS | MW | -0.024645 | -0.009022 | 6 | 6 | -0.011665 | -0.009317 |
| stockholm | OLS | MEW | -0.026466 | -0.009401 | 6 | 6 | -0.011879 | -0.010098 |
| stockholm | XGBoost | ME | -0.017091 | 0.004165 | 0 | 6 | 0.001219 | 0.005093 |
| stockholm | XGBoost | MW | -0.019894 | -0.000583 | 2 | 6 | -0.002412 | 0.004468 |
| stockholm | XGBoost | MEW | -0.018586 | 0.002088 | 0 | 6 | 0.001750 | 0.007520 |

Neighbourhood and geometric validation answer different generalization questions. The following sign counts are descriptive comparisons across correlated fixed designs; they are not independent replications or pooled significance tests. A gain in primary neighbourhood validation can reverse when the held-out units change. Random validation remains a benchmark and does not certify geographically unseen performance. Different error levels across cities also reflect their outcome distributions and sample supports.

For XGBoost walking versus baseline in Copenhagen, the neighbourhood ΔRMSE is -0.009465; random ΔRMSE is -0.002095; walking lowers error in 5 of the 6 registered geometric variants.

For XGBoost walking versus baseline in Oslo, the neighbourhood ΔRMSE is +0.000879; random ΔRMSE is -0.000004; walking lowers error in 0 of the 6 registered geometric variants.

For XGBoost walking versus baseline in Stockholm, the neighbourhood ΔRMSE is -0.019894; random ΔRMSE is -0.000583; walking lowers error in 2 of the 6 registered geometric variants.

## RQ4: relative pricing relationships transfer unevenly

| source_city | target_city | estimator | model | delta_rmse | percentage_change | stability_low | stability_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| copenhagen | oslo | OLS | ME | -0.006072 | -1.607660 | -0.015335 | -0.001201 |
| copenhagen | oslo | OLS | MW | -0.003329 | -0.881479 | -0.010301 | 0.000893 |
| copenhagen | oslo | OLS | MEW | -0.006153 | -1.628974 | -0.015525 | -0.001443 |
| copenhagen | stockholm | OLS | ME | -0.013710 | -3.071486 | -0.030711 | -0.005641 |
| copenhagen | stockholm | OLS | MW | -0.012176 | -2.727733 | -0.026284 | -0.005114 |
| copenhagen | stockholm | OLS | MEW | -0.013774 | -3.085775 | -0.031592 | -0.005508 |
| copenhagen | oslo | XGBoost | ME | 0.001143 | 0.313744 | -0.003250 | 0.006101 |
| copenhagen | oslo | XGBoost | MW | 0.005433 | 1.491388 | -0.000148 | 0.011631 |
| copenhagen | oslo | XGBoost | MEW | 0.002346 | 0.643891 | -0.003013 | 0.008204 |
| copenhagen | stockholm | XGBoost | ME | -0.014972 | -3.493182 | -0.022602 | -0.009878 |
| copenhagen | stockholm | XGBoost | MW | -0.011255 | -2.625985 | -0.017778 | -0.005244 |
| copenhagen | stockholm | XGBoost | MEW | -0.015052 | -3.511806 | -0.021739 | -0.009958 |
| oslo | copenhagen | OLS | ME | -0.001802 | -0.531135 | -0.007178 | 0.002950 |
| oslo | copenhagen | OLS | MW | -0.000708 | -0.208831 | -0.004040 | 0.002292 |
| oslo | copenhagen | OLS | MEW | -0.001355 | -0.399293 | -0.006642 | 0.003152 |
| oslo | stockholm | OLS | ME | -0.004205 | -0.962178 | -0.006872 | -0.001623 |
| oslo | stockholm | OLS | MW | -0.001318 | -0.301596 | -0.002683 | 0.000843 |
| oslo | stockholm | OLS | MEW | -0.004516 | -1.033227 | -0.006929 | -0.002205 |
| oslo | copenhagen | XGBoost | ME | 0.001183 | 0.352506 | -0.002540 | 0.004941 |
| oslo | copenhagen | XGBoost | MW | 0.001844 | 0.549610 | -0.003008 | 0.007172 |
| oslo | copenhagen | XGBoost | MEW | 0.003469 | 1.033774 | -0.004136 | 0.011190 |
| oslo | stockholm | XGBoost | ME | -0.001548 | -0.363394 | -0.006628 | 0.004561 |
| oslo | stockholm | XGBoost | MW | 0.001033 | 0.242456 | -0.004971 | 0.006097 |
| oslo | stockholm | XGBoost | MEW | -0.000174 | -0.040815 | -0.006048 | 0.008077 |
| stockholm | copenhagen | OLS | ME | -0.011056 | -3.125750 | -0.020428 | -0.000314 |
| stockholm | copenhagen | OLS | MW | -0.010533 | -2.977808 | -0.020500 | 0.000807 |
| stockholm | copenhagen | OLS | MEW | -0.009072 | -2.564591 | -0.018906 | 0.002500 |
| stockholm | oslo | OLS | ME | 0.012547 | 3.198408 | 0.001992 | 0.023917 |
| stockholm | oslo | OLS | MW | 0.005351 | 1.364139 | -0.003820 | 0.013104 |
| stockholm | oslo | OLS | MEW | 0.013397 | 3.415048 | 0.002379 | 0.024008 |
| stockholm | copenhagen | XGBoost | ME | -0.008812 | -2.507187 | -0.019549 | 0.005118 |
| stockholm | copenhagen | XGBoost | MW | -0.005351 | -1.522466 | -0.016349 | 0.008373 |
| stockholm | copenhagen | XGBoost | MEW | -0.005486 | -1.560967 | -0.016338 | 0.008621 |
| stockholm | oslo | XGBoost | ME | -0.003341 | -0.870677 | -0.014296 | 0.006581 |
| stockholm | oslo | XGBoost | MW | -0.002119 | -0.552387 | -0.012413 | 0.006356 |
| stockholm | oslo | XGBoost | MEW | -0.004496 | -1.171703 | -0.017690 | 0.006534 |

These tests remove citywide price-level differences using an observed target benchmark. They evaluate relative pricing transfer and do not demonstrate absolute-price deployment in a truly unseen city. Reversing a direction changes both the fitted source relationship and the target distribution; asymmetric errors and bias are expected to require substantive interpretation rather than an assumption of interchangeability. No target correction was applied.

OLS ME lowers relative-price RMSE versus M0 in 5 of 6 directions. This count summarizes heterogeneous patterns and is not an independent-direction significance test.

OLS MW lowers relative-price RMSE versus M0 in 5 of 6 directions. This count summarizes heterogeneous patterns and is not an independent-direction significance test.

OLS MEW lowers relative-price RMSE versus M0 in 5 of 6 directions. This count summarizes heterogeneous patterns and is not an independent-direction significance test.

XGBoost ME lowers relative-price RMSE versus M0 in 4 of 6 directions. This count summarizes heterogeneous patterns and is not an independent-direction significance test.

XGBoost MW lowers relative-price RMSE versus M0 in 3 of 6 directions. This count summarizes heterogeneous patterns and is not an independent-direction significance test.

XGBoost MEW lowers relative-price RMSE versus M0 in 4 of 6 directions. This count summarizes heterogeneous patterns and is not an independent-direction significance test.

## Inferential limitation

Fresh complete-case association coefficients and registered spatial-error/area fixed-effect checks completed in all three cities. The researcher raised the uniform eligibility limit from 5% to 10% after observing Stockholm’s missingness; this is a disclosed post-observation amendment, not preregistration or a universal standard. Stockholm uses the same 2,348 genuinely complete cases; no inferential imputation was used. Predictions and all six transfers were preserved after dependency checks. All outcomes remain original observed asking prices.

## Complete-case association execution

| city | status | prediction_n | association_n | missing_fraction | association_missing_limit |
| --- | --- | --- | --- | --- | --- |
| copenhagen | COMPLETE_ASSOCIATION | 12408 | 12285 | 0.009913 | 0.100000 |
| oslo | COMPLETE_ASSOCIATION | 8529 | 8152 | 0.044202 | 0.100000 |
| stockholm | COMPLETE_ASSOCIATION | 2495 | 2348 | 0.058918 | 0.100000 |

Complete-case selection can still bias adjusted observational associations. HC3 and wild-cluster inference do not correct that selection. See the [dated amendment](association_missingness_amendment_20261013.md) and generated coefficient tables.
