"""Versioned V4 model/scientific and document consistency; no research execution."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

from src.pipeline.model_specification import FEATURES as V3_FEATURES
from src.v4.specification import DEFINITION_VERSION, load_design, model_definition, validate_definition

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"M0": ["X", "H"], "ME": ["X", "H", "E"],
            "MW": ["X", "H", "W"], "MEW": ["X", "H", "E", "W"]}


class V4ModelDefinitionTests(unittest.TestCase):
    def setUp(self):
        self.design = load_design()

    def test_four_primary_models_inherit_x_e_w_with_h_exactly_once(self):
        self.assertEqual(set(self.design["primary_models"]), set(EXPECTED))
        for name, blocks in EXPECTED.items():
            model = model_definition(name, design=self.design)
            self.assertEqual(self.design["primary_models"][name]["blocks"], blocks)
            self.assertEqual(model["features"].count("housing_context_midrank"), 1)
            self.assertEqual(len(model["features"]), len(set(model["features"])))
            self.assertEqual(set(model["features"]) - {"housing_context_midrank"}, set(V3_FEATURES[name]))
            self.assertEqual(model["definition_id"], DEFINITION_VERSION + ":" + name)
            self.assertNotIn("housing_context_midrank", V3_FEATURES[name])

    def test_no_income_retains_h_and_omits_only_income(self):
        for name in EXPECTED:
            primary = model_definition(name, design=self.design)
            sensitivity = model_definition(name, scenario="no_income", design=self.design)
            self.assertEqual(sensitivity["features"], tuple(x for x in primary["features"] if x != "income_100k_dkk"))
            self.assertEqual(sensitivity["features"].count("housing_context_midrank"), 1)
            self.assertEqual(sensitivity["definition_id"], DEFINITION_VERSION + ":no_income:" + name)
        self.assertTrue(self.design["no_income_sensitivity"]["same_prediction_and_association_samples"])
        self.assertTrue(self.design["no_income_sensitivity"]["same_saved_outer_and_inner_folds"])

    def test_log_native_sensitivity_replaces_h_scale_only(self):
        for name in EXPECTED:
            primary = model_definition(name, design=self.design)
            sensitivity = model_definition(name, scenario="log_native_housing", design=self.design)
            self.assertEqual(sensitivity["features"], tuple("log_housing_price_m2_native" if x == "housing_context_midrank" else x for x in primary["features"]))
            self.assertEqual(sensitivity["features"].count("log_housing_price_m2_native"), 1)
        self.assertTrue(self.design["housing"]["sensitivity"]["same_prediction_sample_and_folds"])
        self.assertFalse(self.design["housing"]["sensitivity"]["additional_primary_models"])

    def test_v3_unversioned_extra_models_and_no_h_are_rejected(self):
        mutations = [
            lambda d: d.update(version="research_design_v3"),
            lambda d: d.update(definition_version="unversioned"),
            lambda d: d["primary_models"].update(M0_H=d["primary_models"]["M0"]),
            lambda d: d["primary_models"]["M0"].update(blocks=["X"]),
            lambda d: d["primary_models"]["MEW"].update(blocks=["X", "H", "H", "E", "W"]),
            lambda d: d["blocks"]["X"].append("housing_context_midrank"),
            lambda d: d.update(automatic_no_housing_fallback=True),
            lambda d: d["housing"].update(required=False),
            lambda d: d["cities"].update(missing_qualified_housing_action="omit_city"),
            lambda d: d["no_income_sensitivity"].update(retain_housing=False),
            lambda d: d["no_income_sensitivity"].update(mandatory=False),
            lambda d: d.update(incremental_benefit_of_housing_estimand_authorized=True),
            lambda d: d["housing"].update(rerank_with_airbnb_sample_or_folds=True),
        ]
        for index, mutate in enumerate(mutations):
            d = copy.deepcopy(self.design)
            mutate(d)
            with self.subTest(index=index), self.assertRaises(ValueError):
                validate_definition(d)
        for name, scenario in [("M0_H", "primary"), ("M0", "no_housing")]:
            with self.assertRaises(ValueError):
                model_definition(name, scenario=scenario, design=self.design)

    def test_comparison_priority_and_no_adding_h_estimand(self):
        self.assertEqual(self.design["comparisons"], [
            {"role": "primary", "added": "MEW", "reference": "ME"},
            {"role": "replacement", "added": "MW", "reference": "ME"},
            {"role": "additional", "added": "ME", "reference": "M0"},
            {"role": "additional", "added": "MW", "reference": "M0"},
            {"role": "additional", "added": "MEW", "reference": "M0"},
        ])
        self.assertFalse(self.design["incremental_benefit_of_housing_estimand_authorized"])

    def test_inherited_thresholds_candidates_income_and_qualification_unchanged(self):
        old = json.loads((ROOT / "config/research_design.json").read_text())
        inherited = self.design["inherited_safeguards"]
        for key, value in inherited.items():
            self.assertEqual(value, old[key], key)
        candidates = json.loads((ROOT / "config/xgboost_candidates.json").read_text())
        tuning = self.design["tuning"]
        for key in ["candidates", "candidates_sha256", "search_space"]:
            self.assertEqual(tuning[key], candidates[key], key)
        self.assertEqual(len(tuning["candidates"]), 30)
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in tuning["candidates"]}), 30)
        self.assertEqual(self.design["no_income_sensitivity"]["material_change_rules"], old["no_income_robustness"]["material_change_rules"])
        self.assertEqual(self.design["provenance"]["inherited_config_sha256"], hashlib.sha256((ROOT / "config/research_design.json").read_bytes()).hexdigest())
        self.assertEqual(tuning["inherited_candidate_file_sha256"], hashlib.sha256((ROOT / "config/xgboost_candidates.json").read_bytes()).hexdigest())

    def test_external_housing_reference_and_no_silent_missing_data(self):
        housing = self.design["housing"]
        self.assertEqual(housing["formula"], "H=(midrank-0.5)/G_ref")
        self.assertEqual(housing["preferred_reference_year"], 2025)
        self.assertEqual(housing["rank_method"], "average_ordinal_rank_of_ties")
        self.assertFalse(housing["rerank_with_airbnb_sample_or_folds"])
        self.assertFalse(housing["missing_housing_imputation_allowed"])
        self.assertTrue(housing["native_values_and_currency_preserved"])
        self.assertTrue(housing["alternate_period_or_measure_requires_explicit_amendment"])
        self.assertEqual(housing["qualification_status"], "BLOCKED_NOT_ASSESSED")
        for key in ["source", "acquisition_date", "geographic_extent", "source_sha256"]:
            self.assertIsNone(housing[key])
        self.assertEqual(self.design["cities"]["authorized_roster"], ["copenhagen_frederiksberg", "oslo", "stockholm"])
        self.assertEqual(self.design["cities"]["missing_qualified_housing_action"], "BLOCKED")
        self.assertTrue(self.design["cities"]["narrower_city_or_descriptive_only_scope_requires_explicit_amendment"])

    def test_samples_snapshot_and_interpretation_limits(self):
        self.assertEqual(self.design["snapshot"]["target_month"], "2026-06")
        self.assertTrue(self.design["snapshot"]["matched_between_cities"])
        self.assertEqual(self.design["cities"]["model_strategy"], "separate_city_models")
        self.assertEqual(self.design["engines"], ["OLS", "XGBoost"])
        samples = self.design["samples"]
        self.assertIn("one_housing_qualified_prediction_sample_per_city", samples["prediction"])
        self.assertIn("union_X_H_E_W", samples["ols_association"])
        self.assertTrue(samples["saved_outer_and_inner_folds_shared"])
        self.assertTrue(samples["shared_primary_outcome_observations"])
        self.assertTrue(self.design["provenance"]["v3_results_already_observed"])
        self.assertFalse(self.design["provenance"]["retrospective_preregistration_claim"])
        self.assertEqual(self.design["provenance"]["supervisor_approval"], "not_recorded")
        for key in ["imputation_allowed", "residential_price_outcome_model", "gentrification_score", "causal_housing_price_or_displacement_claims"]:
            self.assertFalse(self.design["outcome"][key])
        self.assertFalse(self.design["snapshot"]["temporal_airbnb_panel"])
        self.assertFalse(self.design["additional_inherited_safeguards"]["numeric_thresholds_are_power_guarantees"])
        self.assertFalse(self.design["execution_authorized_by_this_configuration"])


class V4DocumentConsistencyTests(unittest.TestCase):
    def test_active_markdown_definitions_match_machine_configuration(self):
        design = load_design()
        for relative in design["active_documents"]:
            text = (ROOT / relative).read_text()
            with self.subTest(path=relative):
                self.assertIn(DEFINITION_VERSION, text)
                self.assertIn("H=(midrank-0.5)/G_ref", text)
                self.assertIn("V3 results were already observed", text)
                self.assertIn("BLOCKED", text)
                self.assertNotRegex(text, r"\b(?:M0|ME|MW|MEW)_H\b")
                if Path(relative).name != "source_registry.md":
                    rows = re.findall(r"^\| (M0|ME|MW|MEW) \| ([XHEW +]+) \|$", text, re.M)
                    self.assertEqual(len(rows), 4)
                    self.assertEqual(dict(rows), {name: " + ".join(blocks) for name, blocks in EXPECTED.items()})
        for name in ["proposal.md", "research_plan.md", "preanalysis_specification.md"]:
            text = (ROOT / "docs/v4" / name).read_text()
            self.assertTrue(all(question in text for question in ["RQ1", "RQ2", "RQ3", "RQ4"]))
            self.assertIn("MEW versus ME", text)
            self.assertIn("MW versus ME", text)

    def test_dictionary_lists_every_actual_feature_and_model_versions(self):
        text = (ROOT / "docs/v4/data_dictionary.md").read_text()
        design = load_design()
        for block in design["blocks"].values():
            for feature in block:
                self.assertIn("`" + feature + "`", text)
        index = (ROOT / design["document_index"]).read_text()
        for relative in design["active_documents"]:
            self.assertIn(Path(relative).name, index)

    def test_active_links_resolve_and_docx_status_is_explicit(self):
        for path in (ROOT / "docs/v4").glob("*.md"):
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" not in target:
                    self.assertTrue((path.parent / target.split("#")[0]).exists(), (path, target))
        index = (ROOT / "docs/v4/document_index.md").read_text()
        self.assertIn("No existing active V4 DOCX file", index)
        self.assertIn("stale/superseded", index)
        self.assertIn("make income-docs", index)
        self.assertFalse([p for p in (ROOT / "docs").rglob("*.docx") if "v4" in p.as_posix().lower()])


if __name__ == "__main__":
    unittest.main()
