# Scientific thesis proposal

## Urban accessibility and Airbnb asking prices

Within-city prediction, geographic generalization and cross-city transfer across Copenhagen, Oslo and Stockholm.

Programme: MSc Social Data Science, University of Copenhagen. Updated: **14 October 2026**. Status: **reconciled with the completed study**, not a new preregistration or authorization to refit models. Copenhagen denotes Copenhagen–Frederiksberg.

## Abstract

This thesis compares straight-line and walking-network accessibility in Airbnb nightly asking-price modelling across three Scandinavian capitals. It uses the preserved Inside Airbnb batch dated 30 June 2026, a common OpenStreetMap timestamp, matched destination categories and four models: M0=X, ME=X+E, MW=X+W and MEW=X+E+W. X contains dwelling, host, amenity, source-native population-density and civic-centrality controls; income and residential prices are excluded. Separate within-city models predict observed native-currency log nightly price. Neighbourhood holdouts test geographic generalization, while six source-only directional transfers predict city-relative log price. OLS supplies a predictive baseline and complementary complete-case adjusted associations; XGBoost measures nonlinear predictive information. The harmonized empirical rerun is complete. Accessibility improves primary XGBoost point errors in Copenhagen and Stockholm but produces small adverse changes in Oslo, with geographically heterogeneous gains and direction-dependent transfer. These are observational findings, not causal accessibility effects or a demonstration of universal network superiority. Later document and figure revisions preserve the completed fitted results.

## 1. Research problem and contribution

### Accessibility measurement

Straight-line proximity does not capture the restrictions imposed by waterways, rail infrastructure, pedestrian permissions or disconnected streets. Walking-network accessibility expresses a different travel concept, while requiring additional source qualification, routing and computation. The thesis asks whether these differences change measured accessibility and predictive information under comparable destinations and evaluation tasks, rather than assuming the more complex representation must perform better. The supplied literature motivates this comparison through accessibility measurement and Airbnb price modelling (Geurs and van Wee, 2004; Wang and Nicolau, 2017; Gibbs et al., 2018; Gyódi and Nawaro, 2021; Türk et al., 2021).

### Geographic generalization and transfer

Random validation and geographically separated holdouts answer different questions. The primary task predicts eligible listings in a neighbourhood absent from training. Random folds are a benchmark, and fixed spatial-block designs show sensitivity to geographic separation. The six cross-city experiments ask whether relationships learned in one capital distinguish relatively expensive and cheap listings in another, without target fitting or calibration. Spatial-validation and hedonic-transfer literature supplies the motivation (Roberts et al., 2017; Valavi et al., 2019; McArthur et al., 2012).

### Bounded contribution and study status

The contribution is a matched E/W measurement comparison, separation of replacement from incremental network information, paired within-city evaluation, explicit geographic heterogeneity, and six directional relative-price transfers. It does not establish an exhaustive literature-wide novelty claim or represent every Nordic city. Earlier Copenhagen results were observed before the harmonized design and remain historical evidence. They are not the final estimates below. The all-city rerun was completed under the active design; subsequent reporting changes do not require another fit. Neither the design nor later missingness decisions are retrospectively described as preregistered.

## 2. Four research questions

| Question | Required and completed evidence |
| --- | --- |
| RQ1. How do matched Euclidean and walking-network accessibility measures differ within and across the three capitals? | Nearest-category distance distributions, reachable food/social and culture/tourism counts, matched-universe qualification and network QA. |
| RQ2. How much predictive information does accessibility add within each city, including replacement and incremental network information? | OLS/XGBoost M0, ME, MW and MEW on common rows/folds; all five paired contrasts; complementary complete-case association and held-out contribution summaries. |
| RQ3. How robust are accessibility gains in geographically unseen neighbourhoods, and how consistent are those gains across cities? | Primary neighbourhood holdouts, random and six fixed block designs, full neighbourhood error distributions, geographic buffers and registered robustness. |
| RQ4. To what extent do relative-price relationships transfer between cities, and does accessibility improve that transfer? | Six source-only directions, common target rows, relative-price metrics, paired transfer contrasts and reversal diagnostics. |

The attached draft combined geographic generalization with within-city modelling and labelled transfer RQ3. The completed project separates geographic generalization as RQ3 and labels transfer RQ4. No directional hypothesis requires walking to outperform Euclidean accessibility.

## 3. Data, population and actual samples

All cities use detailed June 2026 Inside Airbnb files. Eligible dwellings have room type Entire home/apt and one of six conventional categories: Entire rental unit, Entire condo, Entire home, Entire loft, Entire townhouse or Entire villa. There is no primary review/activity threshold. The outcome is the original observed positive nightly asking price; missing prices are excluded, never filled or replaced by quote values.

| City | Raw listings | Conventional entire dwellings | Positive-price reference N | Prediction N | Association N | Holdout groups |
| --- | --- | --- | --- | --- | --- | --- |
| Copenhagen | 23144 | 21080 | 12508 | 12408 | 12285 | 11 |
| Oslo | 13391 | 11776 | 8557 | 8529 | 8152 | 17 |
| Stockholm | 4806 | 3834 | 2510 | 2495 | 2348 | 11 |

The reference sample is defined before accessibility or model-feature exclusions. It is not the final prediction sample. Final prediction rows have observed outcomes, qualified unique geography, qualified context and common matched accessibility support. Missing listing predictors remain explicit and are handled by training-only predictive preprocessing. The inferential sample is genuinely complete on the union X+E+W.

### Operational geography

Accepted municipal masks define membership using covers in EPSG:4326. Provider polygons define validation groups; they are not certified current administrative districts. Copenhagen normalizes the five documented spelling/encoding variants while preserving all 11 source groups. Oslo retains 15 borough labels plus Sentrum and Marka. Stockholm preserves 14 raw labels and groups them into 11 units: Hägersten-Liljeholmens plus Älvsjö become Hägersten-Älvsjö; Norrmalms plus Östermalms become Norra innerstaden; Spånga-Tensta plus the recorded Rinkeby-Tensta label become Järva. The historical polygon audit supports a likely provider naming error, not an invented geographic identity. Raw strings, geometries and grouping rationale remain separate evidence.

### Source-native population density

Density uses official population divided by its compatible native official area in km², then natural log. It does not divide official counts by provider holdout-polygon areas merely because labels correspond.

| City | Population and denominator actually used | Qualification |
| --- | --- | --- |
| Copenhagen–Frederiksberg | Copenhagen 2026Q3 population and native official district gross areas; Frederiksberg 2026Q3 population and accepted municipal gross area. | Population reference is one day after the listing batch; water and boundary-vintage caveats remain. |
| Oslo | Official 1 January 2026 population and gross native 17-unit official polygons. | Native density polygons differ from provider validation polygons; citywide and unlocated totals are not redistributed. |
| Stockholm | Official 31 December 2025 borough population and the published 31 December 2024 gross land-plus-water area table, converted from hectares. | Rounded areas and historical 2003/1997 derivation are disclosed; published 11-unit name correspondence does not establish exact provider/current polygon identity. |

Stockholm's primary density is not a RegSO-to-provider aggregation. RegSO geometry is used separately for cartographic context. Registered Stockholm density sensitivities use same-year population and land-only denominators; Copenhagen/Oslo alternatives are explicitly not applicable. No completed no-density predictive run is claimed. Area fixed-effect association models absorb area-constant density.

### Civic centrality and map references

The model control is projected Euclidean distance to each frozen OSM City Hall/town-hall anchor from the common historical snapshot. Metric CRSs are EPSG:25832, EPSG:25833 and EPSG:3006 for Copenhagen, Oslo and Stockholm. The displayed Copenhagen City Hall Square star is a separate public cartographic reference; Oslo/Stockholm stars show the verified City Hall points. Surrounding municipalities and stars do not redefine samples or centrality features.

## 4. Accessibility and the model ladder

The analytical OSM snapshot is **2026-06-30T23:59:59Z** in every city. Destinations, inherited category rules, deduplication, directed pedestrian permissions, connectors and the 2 km extraction-buffer policy are frozen and audited. The directed graph is built by the project pipeline; OSMnx is a literature reference, not a claim about the implemented software dependency.

| Block | Euclidean E | Walking-network W |
| --- | --- | --- |
| Rail | Straight-line km to the nearest qualifying station in the matched category universe. | Minimum directed walking minutes to any qualifying station, including origin and destination connectors. |
| Bus | Straight-line km to the nearest consolidated bus destination. | Minimum directed walking minutes within the same consolidated bus universe. |
| Food/social | Count within 833 m, transformed with log(1+count). | Count reachable in 10 minutes at 5 km/h, transformed with log(1+count). |
| Culture/tourism | Count within 833 m, transformed with log(1+count). | Count reachable in 10 minutes at 5 km/h, transformed with log(1+count). |

The universe is matched, but the closest Euclidean and walking destination can differ. Their nearest-category distance excess is therefore not same-destination route circuity. An observed finite zero opportunity count remains zero; a route/source failure remains missing. The thesis does not claim a completed same-object route-ratio or destination-disagreement analysis without saved, qualified paired identities.

| Model | Features | Main comparison |
| --- | --- | --- |
| M0 | X | Baseline prediction. |
| ME | X+E | Euclidean information beyond X. |
| MW | X+W | Walking information beyond X, and replacement of E. |
| MEW | X+E+W | Combined information and W added beyond E. |

X has the exact frozen common listing/dwelling, host, eight amenity, density and centrality registry. Property type remains a listing control, not a residential-price measure. Source amenities use exact observed JSON values; absent or malformed source information is not silently treated as zero. The detailed variable dictionary is in [the data dictionary](../analysis/data_dictionary.md).

## 5. Two prediction outcomes

Within-city Y is log(price_nightly) in the city's original currency. Separate city models use paired rows and folds, with no currency conversion or city-level outcome centring.

Transfer alone uses y_relative = log(price_nightly) − μ_city, where μ_city is mean log price in the frozen positive-price reference population before feature filtering. All models and outgoing/incoming directions use the same city benchmark.

| City | Reference N | Mean log price | Geometric mean asking price | Currency |
| --- | --- | --- | --- | --- |
| Copenhagen | 12508 | 7.505578 | 1818.156240 | DKK |
| Oslo | 8557 | 7.624645 | 2048.053064 | NOK |
| Stockholm | 2510 | 7.711207 | 2233.235220 | SEK |

The centring is invariant to multiplying every native price by a currency-conversion constant. Each source-city pipeline is fitted and tuned using source data only, then applied unchanged to the two other cities. Target prices determine the frozen target reference and evaluation, not tuning, encoder levels, imputers, intercepts or recalibration. This evaluates relative-price structural transfer, not zero-shot absolute-price deployment. There is no pooled two-city source fit or learned city weighting.

## 6. Estimation, validation and uncertainty

Primary evaluation leaves out one operational neighbourhood. Every outer test group has at least 15 final observations and complementary training support at least 500. The 15 threshold was an explicit support-inspection feasibility decision before final fitting, not a universal statistical standard. The earlier 30 threshold remains a diagnostic. Five-fold random validation is a benchmark; five-fold 1, 1.5 and 2 km grids at zero and half-grid origins provide six separate robustness designs.

Predictive OLS and XGBoost share comparisons, observations and outcomes. XGBoost uses the preserved 30-candidate search with four geography-aware inner folds. Imputation, indicators, category encoding and any other learned preprocessing are fitted inside the relevant training split; inner preprocessing is refitted per inner fold. Source-only transfer follows the same leakage discipline. No outer-test early stopping or result-guided feature/category/threshold selection is allowed.

RMSE is the main error measure; MAE, R², Pearson and Spearman complement it. ΔRMSE equals candidate minus reference, so negative values favour the candidate. All five comparisons are retained: ME−M0, MW−M0, MEW−M0, MW−ME and MEW−ME. The 2,000 geographic-group paired resamples describe neighbourhood-composition stability conditional on existing predictions. They are not independent-replication confidence intervals and do not fully propagate source-model estimation uncertainty. Cross-city directions share models/targets and are not six independent significance-test replications.

### Complete-case inference and the observed amendment

Complementary OLS associations use the common complete-case sample, HC3 intervals, rank/condition/VIF checks and 9,999-replication restricted Webb wild-cluster bootstrap-t. Required-predictor missingness is 123/12,408 in Copenhagen (0.9913%), 377/8,529 in Oslo (4.4202%) and 147/2,495 in Stockholm (5.8918%). Oslo has 376 missing bedroom values plus one missing minimum-night value; the other two cities' missing required predictor is bedrooms.

The original 5% association eligibility threshold was changed to **10% uniformly after Stockholm's missingness was observed**. Complete cases remain 12,285/8,152/2,348; no outcome or inferential bedroom value is imputed. The amendment permits the specified inference but does not remove complete-case selection bias. It is explicitly not preregistered or a universal missingness rule. Eight-neighbour, 499-permutation Moran diagnostics triggered the registered spatial-error association sensitivity in all three cities; area fixed-effect association ladders were also completed.

## 7. Completed results and robustness

Primary geographically held-out XGBoost RMSE is:

| City | M0 | ME | MW | MEW |
| --- | --- | --- | --- | --- |
| Copenhagen | 0.339247 | 0.330229 | 0.329782 | 0.328578 |
| Oslo | 0.349470 | 0.350149 | 0.350349 | 0.351829 |
| Stockholm | 0.406336 | 0.389245 | 0.386442 | 0.387750 |

Accessibility lowers primary point RMSE in Copenhagen and Stockholm and gives small adverse point changes in Oslo. The walking replacement/add-on contrasts differ by city and estimator; interval crossing is not statistical equivalence. Geographic evaluation has higher M0 error than random evaluation in the observed primary tasks, but gains vary across neighbourhoods and block designs. Transfer is directional and does not establish universal network superiority. Exact all-model metrics and source lineage remain in [the results](../../reports/research_results.md).

The completed registry accounts for 75 city/check entries: 71 COMPLETE and four NOT_APPLICABLE native density alternatives. It covers random/geometric validation, former support, apartment/condo-only, reviewed-only, training-price tails, reputation, 15/20-minute opportunities, walking speeds 4/5.4 km/h, continuous decay, boundary-near exclusion, density definitions, 500/1,000 m training buffers and prescribed association sensitivities. Planned no-density, same-object circuity and optional median-centred transfer analyses in the supplied drafts are not represented as completed tests.

## 8. Limitations, thesis structure and reproducibility

Asking prices are not realized transactions. Missing-price exclusions, anonymized locations, official/provider footprint differences, density vintages and water shares, OSM completeness, complete-case selection and source/target sample-size differences remain material limits. Omitting income leaves socioeconomic context unmeasured. Observational coefficients and SHAP allocations among correlated E/W features are not causal amenity valuations, displacement effects or evidence of gentrification. Three selected capitals do not identify general Nordic/European effects.

The thesis structure follows data/methods, RQ1 measurement, RQ2 within-city prediction and associations, RQ3 geographic generalization, RQ4 transfer, robustness, discussion and conclusion. Final empirical stages are complete; thesis narrative and any supervisor-requested follow-up remain distinct tasks. Verified completed fits are preserved. A newly authorized change affecting science would require a separately logged decision and dependency-specific rerun, not an automatic refit triggered by an old draft.

PostgreSQL/PostGIS remains authoritative. Current public outputs are 18 PNG figures and 22 CSV/Markdown table/aggregate views in the flat figures, tables and metrics folders. The map context is isolated in cartography and has no analytical role. Markdown is canonical; this update adds reproducible Word exports for the proposal and plan. It does not add PDF or results-report Word rendering. Attached originals and prior active documents are archived with checksums. See [the current plan](end_to_end_research_plan.md), [specification](../analysis/preanalysis_specification.md), [document comparison](../analysis/document_comparison.md) and [research claims](../final_claims_for_thesis.md).

## References retained from the supplied draft

The references below are retained from the attached proposal. This document reconciliation checks alignment with the project, not an exhaustive new literature search or verification of every bibliographic record.

Andersen, H. S., Andersson, R., Wessel, T., & Vilkama, K. (2016). The impact of housing policies and housing markets on ethnic spatial segregation: comparing the capital cities of four Nordic welfare states. International Journal of Housing Policy, 16(1), 1–30. https://doi.org/10.1080/14616718.2015.1110375

Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. Computers, Environment and Urban Systems, 65, 126–139. https://doi.org/10.1016/j.compenvurbsys.2017.05.004

Chica-Olmo, J., González-Morales, J. G., & Zafra-Gómez, J. L. (2020). Effects of location on Airbnb apartment pricing in Málaga. Tourism Management, 77, 103981. https://doi.org/10.1016/j.tourman.2019.103981

Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: review and research directions. Journal of Transport Geography, 12(2), 127–140. https://doi.org/10.1016/j.jtrangeo.2003.10.005

Gibbs, C., Guttentag, D., Gretzel, U., Morton, J., & Goodwill, A. (2018). Pricing in the sharing economy: a hedonic pricing model applied to Airbnb listings. Journal of Travel & Tourism Marketing, 35(1), 46–56. https://doi.org/10.1080/10548408.2017.1308292

Gyódi, K., & Nawaro, Ł. (2021). Determinants of Airbnb prices in European cities: a spatial econometrics approach. Tourism Management, 86, 104319. https://doi.org/10.1016/j.tourman.2021.104319

Haandrikman, K., Costa, R., Malmberg, B., Farner Rogne, A., & Sleutjes, B. (2023). Socio-economic segregation in European cities: a comparative study of Brussels, Copenhagen, Amsterdam, Oslo and Stockholm. Urban Geography, 44(1), 1–36. https://doi.org/10.1080/02723638.2021.1959778

McArthur, D. P., Osland, L., & Thorsen, I. (2012). Spatial transferability of hedonic house price functions. Regional Studies, 46(5), 597–610. https://doi.org/10.1080/00343404.2010.521147

Roberts, D. R., Bahn, V., Ciuti, S., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography, 40(8), 913–929. https://doi.org/10.1111/ecog.02881

Rosen, S. (1974). Hedonic prices and implicit markets: product differentiation in pure competition. Journal of Political Economy, 82(1), 34–55. https://doi.org/10.1086/260169

Türk, U., Östh, J., Kourtit, K., & Nijkamp, P. (2021). The path of least resistance: a spatial analysis of Airbnb pricing and urban amenities. Journal of Transport Geography, 94, 103130. https://doi.org/10.1016/j.jtrangeo.2021.103130

Valavi, R., Elith, J., Lahoz-Monfort, J. J., & Guillera-Arroita, G. (2019). blockCV: an R package for generating spatially or environmentally separated folds for k-fold cross-validation of species distribution models. Methods in Ecology and Evolution, 10(2), 225–232. https://doi.org/10.1111/2041-210X.13107

Wang, D., & Nicolau, J. L. (2017). Price determinants of sharing economy based accommodation rental: a study of listings from 33 cities on Airbnb.com. International Journal of Hospitality Management, 62, 120–131. https://doi.org/10.1016/j.ijhm.2016.12.007
