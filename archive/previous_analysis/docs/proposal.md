> **Live A02 reconciliation — 11 October 2026.** Active design:
> `v4_accessibility_only_20261011`. The canonical executable registry and
> separate new-design configuration now implement X/E/W without housing.
> Historical configurations, source ledgers and receipts remain immutable.
> Full empirical readiness remains BLOCKED by A03–A07 and genuine city inputs;
> no acquisition, routes, sample/fold creation or fitting occurred in A02.
> V3 results and housing feasibility were already known; supervisor approval
> is not recorded. [A02 implementation audit](pipeline_scope_audit_A02_20261011.md)
> records the actual implementation and tests; the [A01 audit](current_state_audit_20261011.md)
> retains its original checkpoint evidence and input-version discrepancies.
>
> **Baseline reconciliation resolved under A02:** the instruction to remove
> only housing-derived active dependencies retains categorical `property_type`
> from the actual frozen v3 baseline, alongside the 17 numeric/amenity/context
> controls. This explicitly supersedes the supplied revision's prose exclusion;
> the supplied bundle itself remains unchanged. See [model_contract.md](model_contract.md).

# Scientific Thesis Proposal
## Urban accessibility and Airbnb asking prices
### A matched comparison of Copenhagen–Frederiksberg, Oslo and Stockholm

**Version 4 revised · Accessibility-only amendment · 11 October 2026**

MSc Social Data Science · University of Copenhagen

**Design ID:** `v4_accessibility_only_20261011`
**Repository branch:** `v4` — continue the existing branch; do not restart from main.

**Status.** Researcher-requested revision for supervisor review. This document supersedes the active housing-inclusive v4 design, not its historical records. The Copenhagen v3 results and subsequent data-feasibility findings are already known. New-city conditional price estimates have not been established in the supplied audit reports. This is not retrospective preregistration or a claim that v4 estimation is complete.

## Abstract

This thesis examines whether pedestrian-network accessibility provides useful information beyond straight-line accessibility when modelling Airbnb advertised nightly prices. It extends the existing Copenhagen–Frederiksberg study to Oslo and Stockholm, retaining one matched Inside Airbnb observation batch per city, the same eligible dwelling segment, comparable destination definitions and separate city models. Euclidean proximity and cumulative opportunities are compared with walking-network travel times and opportunities using identical destination universes. Ordinary least squares provides conditional association estimates and a predictive baseline; XGBoost evaluates nonlinear predictive information. Geographically withheld evaluation is the principal prediction task, while random validation measures performance for spatially interspersed listings. Paired out-of-fold comparisons distinguish replacing Euclidean measures with network measures from adding network information to an existing Euclidean model. Common spatial-block checks assess sensitivity to differences in administrative geography. The contribution is a reproducible three-case assessment of accessibility measurement and spatial generalisation, including evidence when network complexity brings small or unstable gains. Residential property prices, property-portal acquisition, housing-value subgroup analysis and causal gentrification questions are removed from the active design. Existing housing-acquisition evidence is retained as a documented, discontinued feasibility investigation.

**Keywords:** Airbnb; accessibility measurement; walking networks; hedonic modelling; spatial validation; Scandinavian capitals.

<!-- PAGE -->
# 1. Research problem and literature

## 1.1 Why compare accessibility representations?

Accessibility concerns both the distribution of opportunities and the impedance of reaching them. A short straight-line distance does not necessarily imply a short pedestrian route. Network construction can represent crossings and connected routes, but it also introduces data requirements, modelling assumptions and computational costs. Geurs and van Wee’s review provides the conceptual basis for comparing measures suited to a specific purpose rather than assuming that more complex measures are always superior [R2; L1, P03.E08–E15].

The empirical question is whether this added measurement detail improves Airbnb asking-price prediction beyond dwelling, host and neighbourhood controls. Hedonic theory frames prices as related to bundles of characteristics [R1]. Airbnb studies examine location and professionalisation alongside dwelling attributes [R3], while Gyódi and Nawaro use richer attraction and restaurant accessibility measures in European cities [R4]. Their measures and evaluation design should not be described as a walking-network benchmark or as geographically held-out prediction [L1, P08.E08–E15].

Türk et al. explicitly include Copenhagen in a multi-city study relating Airbnb prices to transport and destination proximity. The supplied literature audit records Cartesian proximity measures rather than computed pedestrian paths and does not identify spatially held-out predictive validation [R5; L1, P09.E08–E15]. Consequently, adding cities alone is not a sufficient novelty claim. The contribution is the controlled combination of matched destinations, network versus Euclidean representations, equal model budgets and evaluation in unseen parts of each city.

## 1.2 Why validation is part of the question

Spatial prediction depends on the setting in which predictions will be used. Random folds evaluate another interspersed listing; geographic holdouts evaluate listings in an area absent from training. These are different tasks, not a contest in which random validation is always invalid. Roberts et al. explain both dependence-related optimism and the possibility that blocking induces additional extrapolation [R6; L1, P14.E11–E15]. Valavi et al. motivate explicit fold geometry and sensitivity to separation choices [R7].

## 1.3 What the scope revision changes

The housing investigation found usable source material but unresolved annual-statistic, access and geographic requirements across the cities [A3–A4]. The researcher has therefore chosen not to make residential prices a condition of the thesis. This removes H from models, samples, folds, questions and the critical path. It does not remove population density, income or centrality from the inherited baseline by implication. No asking-price proxy, rent variable or housing-derived substitute is introduced.

<!-- PAGE -->
# 2. Comparative rationale and existing evidence

## 2.1 Why Copenhagen–Frederiksberg, Oslo and Stockholm?

The cases are selected Scandinavian capitals with a shared regional context and meaningful local differences. Haandrikman et al. provide a comparative precedent including all three cities; Andersen et al. show why Nordic urban and housing institutions should not be treated as identical [R8–R9]. These references justify a coherent comparative setting, not a claim that this thesis measures segregation or housing-policy effects.

The practical rationale is a common Airbnb provider and a matched 30 June 2026 batch already acquired in the project. City selection is not based on which model performs best. The same feature definitions will be applied to each city, while local networks, destinations and sample composition remain empirical differences to document. Any explanation involving barriers or urban form will be grounded in measured route/coverage diagnostics rather than an assumed ranking of the cities.

This is analytical comparison of three selected cases, not a representative sample of Nordic cities. Country, city, institutions and many other characteristics vary together. Separate city estimates cannot identify the causal effect of national policy. “Selected Scandinavian capitals” is the appropriate scope; Helsinki and Reykjavík are not implied to be covered.

## 2.2 V3 evidence already observed

The supplied Copenhagen–Frederiksberg v3 outputs report 12,412 prediction observations and 11 peer analysis areas. Geographic XGBoost log-price RMSE is 0.332357 for M0, 0.324049 for ME, 0.324482 for MW and 0.322703 for MEW. The reported MW-minus-ME difference is +0.000433, with an area-resampling stability interval spanning zero [P1–P2]. These are existing reported estimates, not rerun results. They motivate checking whether the pattern persists in other cities; they do not establish equivalence or network superiority.

## 2.3 Current acquisition state

| City | Positive-price eligible dwellings inside operational municipal mask | Qualification still needed |
|---|---:|---|
| Copenhagen–Frederiksberg | 12,508 | V4 analysis-area/context and common-feature checks |
| Oslo | 8,557 | Municipal boundary vintage; analysis areas and context |
| Stockholm | 2,510 | Analysis-area/context qualification; retain municipal-mask amendment |

Counts come from A1 and the superseding Stockholm amendment A2. They are acquisition counts, not final prediction or OLS samples. Stockholm’s 127 RegSO components form its accepted operational municipal mask; they are not automatically 127 validation areas. Oslo’s geographic count is provisional with respect to boundary vintage. Removing H does not resolve either city’s remaining analysis-geography decisions.

<!-- PAGE -->
# 3. Aim, questions and analytical structure

## 3.1 Aim

Evaluate whether and when walking-network accessibility improves the modelling and geographically held-out prediction of Airbnb asking prices relative to matched Euclidean accessibility, across three selected Scandinavian capitals.

| Research question | Required evidence |
|---|---|
| RQ1. How do Euclidean and walking-network representations differ across the cities? | Matched distance/time and opportunity comparisons; route, destination and coverage audits |
| RQ2. What predictive information does each representation add, and does combining them help? | Paired M0/ME/MW/MEW comparisons within each city on identical observations and folds |
| RQ3. How stable are these comparisons across cities and validation settings? | Administrative-area and random validation; common geometric-block checks; relative gains and support diagnostics |

The former housing RQ4 is withdrawn. It is not replaced with a new mandatory moderator, residential outcome or data-intensive mechanism study.

## 3.2 Conceptual blocks

The outcome is the natural logarithm of the original positive observed advertised nightly price. X contains the inherited property, amenity, host/rental and neighbourhood controls. E describes straight-line access; W describes walking-network access to the same destinations. OLS estimates conditional associations, while predictive OLS and XGBoost are assessed on held-out observations.

| Model | Conceptual definition | Interpretation |
|---|---|---|
| M0 | X | Baseline without transport/opportunity blocks |
| ME | X + E | Euclidean accessibility added |
| MW | X + W | Walking accessibility added |
| MEW | X + E + W | Both representations added |

No residential-price H appears in any primary model or required sensitivity. “M0” is version-qualified in all stored results because its housing-inclusive v4 meaning was different. The new definition restores the v3 conceptual ladder but does not imply identical samples or fitted estimates.

## 3.3 Expectations and interpretation

Both access representations may help relative to M0, but network superiority and its city ranking are not assumed. MW versus ME addresses replacement; MEW versus ME addresses additional information. A positive replacement loss and a negative add-on loss can coexist. Small or inconsistent differences will be reported without selecting a preferred city, radius or model after examining the results. Route-circuity and opportunity-disagreement summaries may aid interpretation, but do not establish why a city-level performance difference occurred.

<!-- PAGE -->
# 4. Data, controls and measurement

## 4.1 Sample and observation period

Use the acquired 30 June 2026 Inside Airbnb batch in all three cities. Retain `Entire home/apt` listings in the six v3 categories: Entire rental unit, Entire condo, Entire home, Entire loft, Entire townhouse and Entire villa. Require an observed positive price and valid geographic/feature support. Do not impute price or introduce a primary minimum-review or activity restriction [P1; A1].

The source’s original price is the outcome candidate. Batch, actual scraping, requested stay and returned stay are distinct. A1 reports varied requested stay dates and unverified returned dates; the matched batch must not be described as one identical travel-date quote across all cities. Literal currency formatting is checked against source metadata rather than interpreted automatically as US dollars. Models use native DKK, NOK and SEK separately. Missing-price listings remain in the acquisition/selection audit.

## 4.2 Baseline controls

X retains accommodates, bedrooms, source-derived effective bathrooms, log1p minimum nights, superhost, log1p host listings, eight prespecified amenity indicators, log population density, qualified income and projected distance to a documented central civic anchor. Amenities are Wi-Fi, dishwasher, washer, dryer, workspace, free parking, private balcony and self check-in. Area identifiers and municipality flags are not primary predictors [P1].

Copenhagen’s accepted 2024 equivalised-disposable-income construction is preserved. New-city income needs a conceptually defensible source/crosswalk and an explicit record of reference year, population and equivalence-scale differences. The mandatory no-income sensitivity remains. A common no-income comparative baseline is available only through a recorded pre-fit decision if harmonisation fails; local income-augmented results would then be labelled supplementary. Housing-data failure alone is not a reason to drop income.

## 4.3 Matched accessibility

E contains nearest eligible rail and consolidated bus distances in kilometres, plus log1p food/social and cultural/tourist opportunities within 833 metres. W contains nearest walking times and matching opportunities within 10 minutes. The inherited speed is exactly 5 km/h; route costs include origin and destination connectors. The 833-metre radius is the documented rounded analogue, not an independently optimized threshold [P1; R10].

All representations use the same eligible destination sets and consolidation policy within each city. Pedestrian restrictions, crossings and network topology must be respected. A consistent OSM extraction policy and city-appropriate metric CRS are required. OSM observation date, source coverage and routing assumptions are recorded; walking access to a stop is not timetable-based transit accessibility.

<!-- PAGE -->
# 5. Estimation and spatial evaluation

## 5.1 Common samples and preprocessing

Construct one prediction sample per city with common accessibility support for all four models. There is no housing-qualified subsample, price-area join or residential-transaction-count gate. M0 uses the same rows as MEW even when it needs fewer features. A separate common OLS association sample follows the inherited complete-case rule: at most 5% of candidate observations missing any required predictor. Above that level, inferential OLS pauses pending an explicit validated treatment; predictive modelling need not be falsely labelled complete-case inference [P1].

All learned imputations, encodings and scaling are estimated inside training partitions. Missing outcomes are never filled. Entirely missing required training predictors fail rather than receive an invented statistic. Missingness and exclusions are reported by city and area.

## 5.2 Validation tasks

The primary task is an unseen official analysis area within the same city. Preserve Copenhagen’s 11-area leave-one-area-out design where the new source/feature checks support it. Qualify official borough/district polygons in Oslo and Stockholm and freeze any geometry/count-based grouping before model evaluation. Sparse-area treatment cannot depend on prices or prediction errors. A proposed extension applies the inherited minimum of 500 training and 30 test observations to new-city primary folds; it is a feasibility safeguard, not a power guarantee.

Random five-fold validation remains a different, interspersed-listing benchmark. A common 1.5-kilometre, five-fold geometric-block check at zero and half-block-shifted origins is required across cities. Administrative areas differ in scale and composition, so cross-city conclusions cannot rely on their labels alone. No fold is defined by discontinued housing-price geography. Ordinary external area statistics may be available in both train and test settings; they are not target encoding.

## 5.3 Models and tuning

Fit predictive OLS and XGBoost using the same conceptual feature blocks. Recover the exact 30-candidate v3 XGBoost list and preserve the four spatial inner folds based on 1-kilometre blocks. Freeze outer/inner membership and candidates before fitting. No outer-test early stopping, performance-based category choice or smaller search budget for a difficult city is allowed. Held-out TreeSHAP, where available, explains tuned predictions rather than causal effects [P1].

Primary summaries report geographic RMSE, MAE and R² in log price, paired losses, fold distributions and support diagnostics. The training-mean benchmark is separate from the four substantive models. Separate city estimators and relative within-city gains avoid pooling currencies or letting Copenhagen’s larger sample dominate a single pooled score.

<!-- PAGE -->
# 6. Comparisons, uncertainty and robustness

## 6.1 Prespecified comparisons

Retain ME–M0, MW–M0, MEW–M0 and MW–ME. Explicitly add MEW–ME to the revised reporting protocol: it directly tests the extra information in W after E is known. This is a documented reporting/design addition relative to the v3 frozen comparison list, not a retrospectively preregistered v3 contrast.

Define Delta RMSE as the added model’s RMSE minus the reference model’s RMSE; negative values favour the added model. Also report proportional reductions and equal-area summaries. Resample matched held-out geographic groups 2,000 times and recompute paired pooled losses. These ranges describe stability to area composition; overlapping training sets and residual dependence prevent treating them as definitive independent-sample confidence intervals. Crossing zero is not evidence of equivalence [P1].

Cross-city synthesis reports all three estimates, their actual sample/fold sizes and their geometric-check results. No regression of a country effect on three city estimates or causal explanation from three cases is proposed.

## 6.2 Association and spatial diagnostics

OLS coefficients are conditional associations. Retain HC3 intervals and the validated restricted WCR11 wild-cluster bootstrap-t sensitivity with Webb weights, CRV1 studentisation and 9,999 replications. WCR11 is the procedure label, not an instruction to manufacture 11 clusters in every city. Use each city’s valid analysis areas and state small-cluster limitations. VIFs, rank and condition numbers diagnose collinearity without selecting predictors by significance [P1].

Use eight-neighbour Moran diagnostics with 499 permutations for log price and selected geographic out-of-fold residuals. The inherited trigger permits one spatial-error association sensitivity where OLS MW residual |I| exceeds 0.05 and p is below 0.05. No new SAR/SDM/GWR family or causal model is introduced.

## 6.3 Bounded robustness programme

Retain the inherited no-income, apartment/condo-only, reviewed-listing, training-only price-trimming and reputation sensitivities. Measurement checks preserve matched 15/20-minute opportunities, 4.0/5.4 km/h speeds and continuous decay with a 10-minute half-life. Spatial checks retain the v3 block/buffer programme, with the common 1.5-kilometre comparison prioritized for cross-city interpretation. A 150-metre boundary-near diagnostic is retained because coordinates are anonymized [D1; A2].

Every registered check is labelled completed, infeasible, deferred or failed. Resource-driven deferral is a pre-fit amendment, not an unreported shortcut. Sensitivity sample changes are separated from feature changes, and adverse results are retained.

<!-- PAGE -->
# 7. Feasibility, ethics and expected contribution

## 7.1 What is ready and what remains

The project has acquired the three listing snapshots and a documented operational Stockholm municipal mask. It has also produced unsuccessful or partial housing-source work that remains valuable as a decision audit [A1–A4]. The revision retires housing acquisition, qualification, source-specific blockers and price-area folds from the active dependency chain. It preserves existing source bytes, receipts, database migrations, branch history and original failure statuses.

Work still required includes resolving or explicitly qualifying Oslo’s municipal boundary vintage; selecting new-city analysis areas; qualifying population/income/central anchors; auditing destination and network coverage; and freezing samples, folds and tuning. These are genuine accessibility-study requirements. Removing H is not permission to relabel unresolved geography as approved.

Implementation proceeds through twelve sequential Codex checkpoints on the existing v4 branch. The accompanying end-to-end plan specifies acceptance rules, model budget, amendment history, output provenance and restart-safe handover. Every checkpoint is committed and pushed to v4; no automatic merge to main is requested.

## 7.2 Limitations and responsible claims

A single batch cannot establish temporal stability, actual occupancy, realized revenue, residential housing effects or displacement. Observed nightly prices and their availability may select a nonrepresentative subset of eligible listings. Source coordinates are anonymized, so routing and administrative assignment are approximate; public outputs must not reveal listing locations [D1; A1–A2].

Destination coverage, OSM timing, gross-area density definitions, local income concepts and unequal administrative units can affect comparison. Results will therefore include source qualification, sample attrition, support and spatial-scale checks. Prediction does not demonstrate travellers’ actual routes, preferences or causal willingness to pay. Lower error is evidence about the specified prediction task, not the complete theoretical adequacy of an accessibility measure.

## 7.3 Contribution and thesis structure

The thesis will contribute a matched three-case measurement comparison, an explicit assessment of unseen-area prediction, and reproducible evidence about whether network detail adds useful information. A near-zero or unstable advantage remains a valid finding when uncertainty and measurement support are clear. The claim is methodological replication and comparative evaluation, not first use of Airbnb or first study of these cities.

The proposed chapters are: introduction and questions; literature and conceptual framework; cases/data; measurement and methods; within-city results; comparative results and robustness; discussion and conclusion. The housing feasibility decision belongs in the methods/amendment record, not an unfinished substantive housing chapter.

<!-- PAGE -->
# References

The supplied literature matrix remains the starting evidence audit. This revision uses its methodological qualifications, with selected publisher/author-institution records checked on 11 October 2026. Full original PDFs have not all been re-audited. References motivate methods and case selection; operational thresholds are project decisions.

[R1] Rosen, S. (1974). Hedonic prices and implicit markets: Product differentiation in pure competition. *Journal of Political Economy*, 82(1), 34–55. DOI: 10.1086/260169.

[R2] Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: Review and research directions. *Journal of Transport Geography*, 12(2), 127–140. DOI: 10.1016/j.jtrangeo.2003.10.005.

[R3] Deboosere, R., Kerrigan, D. J., Wachsmuth, D., & El-Geneidy, A. (2019). Location, location and professionalization: A multilevel hedonic analysis of Airbnb listing prices and revenue. *Regional Studies, Regional Science*, 6(1), 143–156. DOI: 10.1080/21681376.2019.1592699.

[R4] Gyódi, K., & Nawaro, Ł. (2021). Determinants of Airbnb prices in European cities: A spatial econometrics approach. *Tourism Management*, 86, 104319. DOI: 10.1016/j.tourman.2021.104319.

[R5] Türk, U., Östh, J., Kourtit, K., & Nijkamp, P. (2021). The path of least resistance explaining tourist mobility patterns in destination areas using Airbnb data. *Journal of Transport Geography*, 94, 103130. DOI: 10.1016/j.jtrangeo.2021.103130.

[R6] Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography*, 40(8), 913–929. DOI: 10.1111/ecog.02881.

[R7] Valavi, R., Elith, J., Lahoz-Monfort, J. J., & Guillera-Arroita, G. (2019). blockCV: An R package for generating spatially or environmentally separated folds for k-fold cross-validation of species distribution models. *Methods in Ecology and Evolution*, 10(2), 225–232. DOI: 10.1111/2041-210X.13107.

[R8] Andersen, H. S., Andersson, R., Wessel, T., & Vilkama, K. (2016; online 2015). The impact of housing policies and housing markets on ethnic spatial segregation: Comparing the capital cities of four Nordic welfare states. *International Journal of Housing Policy*, 16(1), 1–30. DOI: 10.1080/14616718.2015.1110375.

[R9] Haandrikman, K., Costa, R., Malmberg, B., Rogne, A. F., & Sleutjes, B. (2023; online 2021). Socio-economic segregation in European cities: A comparative study of Brussels, Copenhagen, Amsterdam, Oslo and Stockholm. *Urban Geography*, 44(1), 1–36. DOI: 10.1080/02723638.2021.1959778.

[R10] Djurhuus, S., Hansen, H. S., Aadahl, M., & Glümer, C. (2016). Building a multimodal network and determining individual accessibility by public transportation. *Environment and Planning B: Planning and Design*, 43(1), 210–227. DOI: 10.1177/0265813515602594. Retained as the v3 convention’s cited rationale; no claim that 5 km/h is empirically universal.

<!-- PAGE -->
# Evidence and amendment register

| Key | Supplied source or verified route | Use and limitation |
|---|---|---|
| P1 | `thesis_results_v3.zip`: active pre-analysis specification, deviations and income dictionary | Governs inherited scientific definitions; active Markdown takes precedence over older DOCX prose |
| P2 | Same archive: primary-model tables and `reports/research_results_v3.md` | Existing Copenhagen results only; not re-estimated here |
| L1 | `Literature_Matrix_PDF_Audit_Evidence.csv` | 300 evidence rows / 20 papers; methodological qualifications retained |
| A1 | `listing_acquisition.md` | Listing counts, source periods, quote-field limitations and unresolved Oslo vintage |
| A2 | `stockholm_boundary_amendment_20261011.md` | Supersedes Stockholm municipal-mask blocker only; not analysis-area assignment |
| A3 | `housing_acquisition.md` | Records partial acquisition and unpassed housing gates, now outside active scope |
| A4 | `housing_access_requirements.md` | Unsent requests and access needs; no external contact authorized by this revision |
| D1 | Inside Airbnb, Data Assumptions | Provider limitations; checked 11 October 2026; complete route in companion registry |

**Supersession.** The original housing-inclusive v4 proposal/plan, housing-default prompt sequence and revised housing Prompt 5 are historical. Do not continue their Step 6 or remaining prompts. Use A01–A12 in the new playbook. The Git branch remains v4; the scientific design receives a new immutable ID.

**Preserved.** Completed v3 results, qualified Copenhagen income, all listing acquisitions, Stockholm’s boundary amendment, housing-source receipts and applied database migrations remain unchanged. No completed dataset is deleted to make the new design appear preregistered.

**Withdrawn requirements.** H and all residential price/rent proxies; housing-qualified samples; annual-sale-count and housing-coverage gates; housing-area folds; H subgroup/midrank analysis; property-portal extraction and provider-access requests. Historical blocked sources retain their original statuses, while the new design records these tasks as not required.

**New or clarified operational decisions.** Explicit MEW–ME reporting; new-city area/metric-CRS qualification; extension of minimum fold-support checks to new-city primary validation; and version-isolated execution with selective reuse. These decisions must be frozen before new conditional price fitting. Supervisor review status remains explicit.

**Package contents.** The matching research plan, revised pre-analysis specification, model contract, change log, provenance registry and twelve standalone prompts provide the implementation handover. They are documentation and instructions, not code already applied to the user’s repository.


Live document authority: [index](document_index.md), [contract](IMPLEMENTATION_CONTRACT.md), [step mapping](step_mapping_A01_A12.md).
