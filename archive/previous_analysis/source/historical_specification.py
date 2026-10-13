"""Read-only V4 model definitions, separate from the frozen V3 pipeline."""
from __future__ import annotations

import json
from pathlib import Path

DEFINITION_VERSION = "v4_housing_standard_20261011"
CONFIG_PATH = Path(__file__).resolve().parents[2] / "config/v4/research_design.json"
PRIMARY_BLOCKS = {
    "M0": ["X", "H"], "ME": ["X", "H", "E"],
    "MW": ["X", "H", "W"], "MEW": ["X", "H", "E", "W"],
}


def validate_definition(design: dict) -> None:
    if design.get("version") != "research_design_v4" or design.get("definition_version") != DEFINITION_VERSION:
        raise ValueError("Require the explicit V4 definition version; V3 labels are not V4 models")
    models = design["primary_models"]
    if set(models) != set(PRIMARY_BLOCKS):
        raise ValueError("Exactly M0, ME, MW and MEW are primary")
    blocks = design["blocks"]
    if set(blocks) != {"X", "H", "E", "W"} or blocks["H"] != ["housing_context_midrank"]:
        raise ValueError("Require the frozen X/H/E/W blocks and single H feature")
    union = [feature for block in blocks.values() for feature in block]
    if len(union) != len(set(union)):
        raise ValueError("Feature blocks must be disjoint; include H exactly once")
    for name, expected in PRIMARY_BLOCKS.items():
        if models[name] != {"definition_id": DEFINITION_VERSION + ":" + name, "blocks": expected}:
            raise ValueError("Primary model definition/version mismatch: " + name)
    if design["automatic_no_housing_fallback"] or not design["housing"]["required"]:
        raise ValueError("Housing is mandatory; a no-H fallback is forbidden")
    if design["cities"]["missing_qualified_housing_action"] != "BLOCKED":
        raise ValueError("Unqualified H must block the city")
    if design["housing"]["formula"] != "H=(midrank-0.5)/G_ref" or design["housing"]["rerank_with_airbnb_sample_or_folds"]:
        raise ValueError("H requires the frozen external-area midrank")
    sensitivity = design["no_income_sensitivity"]
    if not sensitivity["mandatory"] or not sensitivity["retain_housing"] or sensitivity["omit_only"] != ["income_100k_dkk"]:
        raise ValueError("Mandatory no-income sensitivity omits only income, retaining H")
    if design["incremental_benefit_of_housing_estimand_authorized"]:
        raise ValueError("Adding-H estimand needs a separately authorized no-H sensitivity")


def load_design(path: Path = CONFIG_PATH) -> dict:
    design = json.loads(path.read_text(encoding="utf-8"))
    validate_definition(design)
    return design


def model_definition(name: str, *, scenario: str = "primary", design: dict | None = None) -> dict:
    """Return versioned feature metadata only; never fit or provision anything."""
    design = load_design() if design is None else design
    validate_definition(design)
    if name not in PRIMARY_BLOCKS or scenario not in {"primary", "no_income", "log_native_housing"}:
        raise ValueError("Unknown V4 model or prespecified sensitivity")
    model = design["primary_models"][name]
    features = [feature for block in model["blocks"] for feature in design["blocks"][block]]
    identity = model["definition_id"]
    if scenario == "no_income":
        features.remove("income_100k_dkk")
        identity = design["no_income_sensitivity"]["definition_ids"][name]
    elif scenario == "log_native_housing":
        features[features.index("housing_context_midrank")] = "log_housing_price_m2_native"
        identity = DEFINITION_VERSION + ":log_native_housing:" + name
    return {"definition_id": identity, "model": name, "scenario": scenario, "features": tuple(features)}
