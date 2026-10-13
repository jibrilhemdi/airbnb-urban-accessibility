# Income harmonisation — unresolved prerequisite

The full Version 3 primary rerun is blocked. Core income is required, but the frozen sources do not establish an identical denominator for Copenhagen KKIND3 and Frederiksberg INDKP106.

The preserved [context audit](../archive/legacy_v2/reports/postcompletion_01_context_audit.md) explicitly states that the income field was not fully harmonised. KKIND3's selected mean refers to persons with the selected income type; INDKP106's selected mean refers to persons in the selected total group. Both use 2024 DKK/person and broad disposable-income concepts. Matching units/year and plausible values do not demonstrate denominator equivalence. The audit's population-weighted comparison is not an income-denominator harmonisation method.

Official source pages checked on 4 October 2026 corroborate the broad table concepts but do not resolve that denominator issue: [Copenhagen income tables](https://kk.statistikbank.dk/statbank5a/SelectTable/omrade0.asp?PLanguage=0&ShowNews=OFF&SubjectCode=305), [INDKP106](https://www.statbank.dk/statbank55/SelectVarVal/Define.asp?MainTable=INDKP106&PLanguage=0). Lack of equivalence evidence is an inference from the documented selections, not a newly proven numerical discrepancy.

A scientifically defensible resolution is authoritative documentation demonstrating equivalent eligible populations/definitions, or a compatible income source/validated transformation with its own provenance and freeze. The current code requires evidence paths and SHA-256 values and retains original source IDs. It does not turn the earlier comparability flag off merely to run M0. If the original source values need transformation, that transformation must also be implemented and frozen before modelling.

Using the existing mixed-definition means would require an explicit protocol amendment and clear qualification; it is not silently performed. Dropping income, restricting the primary analysis to Copenhagen, or substituting the archived separate context-model family would depart from the user's eleven-area core specification. No such fallback has been executed.

Core inferential missingness is another conditional guard: if more than 5% of the common sample lacks any inferential predictor, the OLS component stops pending an exact multiple-imputation/pooling implementation. That condition has not been assessed on a rebuilt V3 sample, because the primary data build is still blocked by income evidence.
