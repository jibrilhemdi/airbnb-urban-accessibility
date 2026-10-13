# Version 3 research results

Run `research_v3_20261004T111510Z`; analytical dataset N = 12,412; 11 peer analysis areas.

Core M0 contains property, prespecified amenities, host/rental variables, area density, harmonised income and City Hall centrality. Rail and bus enter separately in the Euclidean and walking blocks.

The baseline assumes 5.0 km/h and a 10-minute network budget with an 833 m rounded Euclidean analogue. Threshold, speed and continuous-decay checks are distinct prespecified sensitivities.

Random CV assesses another spatially interspersed listing in the same market; geographic CV assesses an analysis area absent from training.

OLS coefficients are conditional associations. HC3 intervals and area wild-cluster bootstrap-t inference are both reported. Held-out SHAP explains predictions; no causal interpretation.

## Model Performance

    n      model    r2_log        scheme  mae_log  rmse_log feature_set  fold_r2_log_q25  fold_r2_log_q75  fold_mae_log_q25  fold_mae_log_q75  fold_rmse_log_q25  fold_rmse_log_q75  fold_r2_log_median  fold_mae_log_median  fold_rmse_log_median
12412        OLS  0.437680 geographic_11 0.245673  0.331702          M0         0.349911         0.452231          0.233016          0.252636           0.310156           0.346287            0.391573             0.242574              0.333181
12412        OLS  0.453677 geographic_11 0.242085  0.326950          ME         0.381087         0.454199          0.233246          0.248040           0.311126           0.339948            0.400667             0.236026              0.325823
12412        OLS  0.451789 geographic_11 0.242765  0.327515         MEW         0.376892         0.454977          0.233328          0.248637           0.311356           0.339930            0.392797             0.237420              0.326070
12412        OLS  0.448579 geographic_11 0.243570  0.328472          MW         0.371111         0.457225          0.234798          0.251605           0.311897           0.342003            0.387216             0.238316              0.327483
12412    XGBoost  0.435457 geographic_11 0.244541  0.332357          M0         0.320699         0.473112          0.227705          0.262775           0.303113           0.346960            0.415768             0.236195              0.322928
12412    XGBoost  0.463329 geographic_11 0.238406  0.324049          ME         0.377997         0.476906          0.226363          0.251040           0.296105           0.336503            0.411975             0.235380              0.321721
12412    XGBoost  0.467780 geographic_11 0.237798  0.322703         MEW         0.386124         0.476971          0.230350          0.248945           0.296969           0.334658            0.406736             0.235258              0.323646
12412    XGBoost  0.461893 geographic_11 0.238680  0.324482          MW         0.372952         0.480237          0.229467          0.249809           0.296287           0.337053            0.397790             0.234357              0.323267
12412 train_mean -0.036823 geographic_11 0.346650  0.450411        none        -0.150800        -0.002537          0.320986          0.391486           0.422071           0.482765           -0.137022             0.365796              0.455893
12412        OLS  0.475628      random_5 0.236136  0.320315          M0         0.472904         0.480645          0.234888          0.237813           0.320178           0.322716            0.476285             0.235129              0.322477
12412        OLS  0.483328      random_5 0.234352  0.317954          ME         0.482138         0.487511          0.232497          0.236367           0.317290           0.320338            0.485689             0.234476              0.320191
12412        OLS  0.483720      random_5 0.234338  0.317833         MEW         0.481830         0.487109          0.232198          0.236439           0.316852           0.320541            0.486861             0.234603              0.320015
12412        OLS  0.482050      random_5 0.234680  0.318347          MW         0.481295         0.485146          0.232415          0.236860           0.317458           0.321345            0.484282             0.234701              0.320848
12412    XGBoost  0.506418      random_5 0.229107  0.310768          M0         0.498880         0.515315          0.226262          0.232050           0.307189           0.313048            0.501935             0.228661              0.312389
12412    XGBoost  0.514953      random_5 0.226973  0.308069          ME         0.501535         0.528798          0.225339          0.227504           0.303710           0.311560            0.511548             0.227335              0.308521
12412    XGBoost  0.514347      random_5 0.227129  0.308262         MEW         0.502484         0.529282          0.225991          0.227505           0.304465           0.311264            0.507536             0.226935              0.307888
12412    XGBoost  0.513097      random_5 0.227201  0.308658          MW         0.502032         0.527299          0.225482          0.228490           0.303343           0.313690            0.506209             0.228222              0.309154
12412 train_mean -0.000365      random_5 0.340225  0.442421        none        -0.001259        -0.000442          0.337003          0.344183           0.441853           0.447590           -0.000528             0.340195              0.442708

## Incremental Performance

    n added   model        scheme  delta_mae reference  delta_rmse  bootstrap_seed  area_delta_mae_q25  area_delta_mae_q75  area_delta_rmse_q25  area_delta_rmse_q75  area_delta_mae_median  area_delta_rmse_median  bootstrap_replications  delta_mae_bootstrap_low  delta_mae_bootstrap_high  delta_rmse_bootstrap_low  delta_rmse_bootstrap_high  bootstrap_fraction_mae_improved  bootstrap_fraction_rmse_improved
12412    ME     OLS geographic_11  -0.003588        M0   -0.004752      20261004.0           -0.007976            0.004300            -0.007719             0.001948              -0.001279               -0.002028                  2000.0                -0.009658                  0.001160                 -0.009485                  -0.000385                           0.9270                            0.9845
12412    MW     OLS geographic_11  -0.002104        M0   -0.003230      20261004.0           -0.005945            0.001214            -0.004649            -0.000105              -0.001909               -0.001803                  2000.0                -0.006119                  0.001631                 -0.006889                   0.000480                           0.8725                            0.9590
12412   MEW     OLS geographic_11  -0.002908        M0   -0.004188      20261004.0           -0.005760            0.003303            -0.006368             0.000843              -0.001121               -0.002209                  2000.0                -0.008586                  0.001573                 -0.008549                  -0.000046                           0.8950                            0.9760
12412    MW     OLS geographic_11   0.001484        ME    0.001522      20261004.0           -0.000322            0.002156            -0.000052             0.001737               0.000482                0.000502                  2000.0                -0.000005                  0.003650                  0.000301                   0.003313                           0.0260                            0.0020
12412    ME XGBoost geographic_11  -0.006135        M0   -0.008308      20261004.0           -0.010639            0.003526            -0.011303             0.003822              -0.007191               -0.010245                  2000.0                -0.013111                  0.000673                 -0.015544                  -0.000979                           0.9625                            0.9865
12412    MW XGBoost geographic_11  -0.005860        M0   -0.007875      20261004.0           -0.015041           -0.000781            -0.013956             0.000635              -0.004526               -0.005428                  2000.0                -0.011946                 -0.000192                 -0.015494                  -0.000704                           0.9780                            0.9885
12412   MEW XGBoost geographic_11  -0.006743        M0   -0.009655      20261004.0           -0.014172            0.000041            -0.014307             0.001225              -0.004829               -0.006687                  2000.0                -0.014517                  0.000845                 -0.019071                  -0.000287                           0.9575                            0.9800
12412    MW XGBoost geographic_11   0.000275        ME    0.000433      20261004.0           -0.003702            0.003327            -0.003462             0.003401              -0.001431               -0.001142                  2000.0                -0.002992                  0.003017                 -0.002448                   0.003633                           0.4490                            0.4235
12412    ME     OLS      random_5  -0.001783        M0   -0.002361             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN
12412    MW     OLS      random_5  -0.001456        M0   -0.001968             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN
12412   MEW     OLS      random_5  -0.001798        M0   -0.002481             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN
12412    MW     OLS      random_5   0.000327        ME    0.000393             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN
12412    ME XGBoost      random_5  -0.002134        M0   -0.002699             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN
12412    MW XGBoost      random_5  -0.001907        M0   -0.002110             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN
12412   MEW XGBoost      random_5  -0.001978        M0   -0.002506             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN
12412    MW XGBoost      random_5   0.000227        ME    0.000589             NaN                 NaN                 NaN                  NaN                  NaN                    NaN                     NaN                     NaN                      NaN                       NaN                       NaN                        NaN                              NaN                               NaN

## Ols Ladder

    n         aic         bic  adjusted_r2 feature_set  condition_number
12289 6869.450606 7040.029183     0.476936          M0        378.240744
12289 6681.014829 6881.259244     0.485063          ME        428.903162
12289 6711.212554 6911.456969     0.483796          MW        522.077692
12289 6669.317291 6899.227546     0.485720         MEW        561.914633

## Spatial Moran

 k     n     seed   model        scheme  moran_i  crs_epsg  variable  expected_i feature_set  permutations  directed_edges  permutation_mean  permutation_p_two_sided
 8 12412 20261004    none   descriptive 0.246885     25832 log_price   -0.000081        none           499           99296         -0.000259                    0.002
 8 12412 20261004     OLS geographic_11 0.121091     25832  residual   -0.000081          M0           499           99296          0.000300                    0.002
 8 12412 20261004     OLS geographic_11 0.105791     25832  residual   -0.000081          MW           499           99296          0.000265                    0.002
 8 12412 20261004 XGBoost geographic_11 0.132829     25832  residual   -0.000081          M0           499           99296          0.000312                    0.002
 8 12412 20261004 XGBoost geographic_11 0.101915     25832  residual   -0.000081          MW           499           99296          0.000320                    0.002

## Methods/Data: area income

Area income is operationalised as 2024 equivalised disposable income derived from decile means. Copenhagen city-district values use Copenhagen Municipality's KKIND5, while Frederiksberg uses Statistics Denmark's nominal IFOR35. Both sources represent closely aligned equivalised-disposable-income concepts and use ten person-based decile groups, but some table-specific processing details cannot be proven identical. The measure is therefore treated as pragmatically harmonised. All primary models include the measure, and a prespecified no-income robustness analysis tests whether substantive accessibility conclusions depend on this cross-source context variable.

## Income robustness

Accessibility conclusions materially change under the prespecified flags: YES — review the flagged coefficient directions and/or paired error/ranking reversals.

                                         kind                            term   model        scheme comparison feature_set  material_change magnitude_sensitivity_flag
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS geographic_11      ME/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS geographic_11      MW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS geographic_11     MEW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS geographic_11      MW/ME        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost geographic_11      ME/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost geographic_11      MW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost geographic_11     MEW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost geographic_11      MW/ME        None             True                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS      random_5      ME/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS      random_5      MW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS      random_5     MEW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None     OLS      random_5      MW/ME        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost      random_5      ME/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost      random_5      MW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost      random_5     MEW/M0        None            False                       None
 pooled_delta_rmse_direction_or_MW_ME_ranking                            None XGBoost      random_5      MW/ME        None            False                       None
ols_accessibility_direction_with_wild_support    nearest_station_euclidean_km    None          None       None          ME            False                       True
ols_accessibility_direction_with_wild_support        nearest_bus_euclidean_km    None          None       None          ME            False                      False
ols_accessibility_direction_with_wild_support                    log1p_food_e    None          None       None          ME            False                       True
ols_accessibility_direction_with_wild_support                 log1p_culture_e    None          None       None          ME            False                       True
ols_accessibility_direction_with_wild_support nearest_station_walking_minutes    None          None       None          MW            False                      False
ols_accessibility_direction_with_wild_support     nearest_bus_walking_minutes    None          None       None          MW            False                      False
ols_accessibility_direction_with_wild_support                    log1p_food_w    None          None       None          MW            False                       True
ols_accessibility_direction_with_wild_support                 log1p_culture_w    None          None       None          MW            False                       True
ols_accessibility_direction_with_wild_support    nearest_station_euclidean_km    None          None       None         MEW            False                       True
ols_accessibility_direction_with_wild_support        nearest_bus_euclidean_km    None          None       None         MEW            False                      False
ols_accessibility_direction_with_wild_support                    log1p_food_e    None          None       None         MEW            False                       True
ols_accessibility_direction_with_wild_support                 log1p_culture_e    None          None       None         MEW            False                       True
ols_accessibility_direction_with_wild_support nearest_station_walking_minutes    None          None       None         MEW            False                       True
ols_accessibility_direction_with_wild_support     nearest_bus_walking_minutes    None          None       None         MEW            False                       True
ols_accessibility_direction_with_wild_support                    log1p_food_w    None          None       None         MEW            False                       True
ols_accessibility_direction_with_wild_support                 log1p_culture_w    None          None       None         MEW            False                       True

RMSE, MAE, R² and paired ΔRMSE changes and all eleven geographic area results are in the accompanying income comparison tables.

## Limitations

Income has qualified cross-source comparability; exact table processing and KKIND5 raw price basis remain unresolved. The mandatory no-income sensitivity quantifies dependence on this control.
