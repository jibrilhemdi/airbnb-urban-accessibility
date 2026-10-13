# Association eligibility amendment — 13 October 2026

The researcher explicitly changed the union X+E+W predictor-missingness
eligibility limit from **5% to 10%**, uniformly for Copenhagen, Oslo and
Stockholm. Missingness strictly greater than 10% blocks association inference;
10% itself passes. This decision was made **after observing** Stockholm's
147 missing bedrooms among 2,495 prediction rows (5.891783567%). It is a
post-observation methodological amendment, not an originally frozen or
preregistered threshold. Ten percent is a researcher-design choice, not a
universal statistical standard.

The motivation is to permit complete-case association inference below the
chosen limit. Stockholm still has exactly 2,348 genuinely complete cases;
the 147 original bedroom blanks remain missing. There is no inferential
imputation, reconstruction, beds substitution, zero-bedroom assumption,
Stockholm-only exception or removal of bedrooms.

The required union, observed outcome, four model definitions, HC3 baseline,
9,999-replication restricted Webb WCR11/CRV1 procedure, rank/condition/VIF
checks, 8-neighbour/499-permutation Moran specification, registered spatial
trigger and area fixed-effect rules remain unchanged. Association and its
dependent checks are freshly rerun for all three cities on the verified,
previously frozen common complete cases. Adjusted observational associations
remain noncausal.

This amendment affects association eligibility only. Prediction samples,
folds, accessibility, context, price benchmarks, fitted predictive models,
all six transfers and their SHAP outputs are preserved. Broad historical
configuration hashes include the old gate as incidental metadata; the
dependency audit compares the complete design except this single eligibility
key and verifies the exact fitted code, inputs, predictions and model bytes.
No completed predictive or transfer fit is repeated.

The [exact instruction](../../archive/research_request/association_amendment.txt)
and [pre-amendment checkpoint](../../archive/before_association_amendment/manifest.json)
preserve the evidence. Earlier 5% audits and execution-log entries remain
historical records of what actually happened. Repository cleanup relocates
preserved evidence into one archive with verified original bytes; it does not
rename persisted source, migration or database identities.
