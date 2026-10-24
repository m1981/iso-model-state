"""Regresja zastosowania zaakceptowanej korekty DEC-PRO-006.

Trace: G3, G6.
"""

import yaml

from isomodel.graph import dead_ends, iso_coverage
from conftest import ROOT


def test_G6_accepted_annotations_are_in_authoritative_model(model):
    change = yaml.safe_load((ROOT / "model/proposals/e2-structure.yaml").read_text())
    assert change["status"] == "applied"
    assert change["decision"] == "DEC-PRO-006"
    transitions = {t["id"]: t for kind in ("item", "question", "release") for t in model[f"{kind}_transitions"]}
    for ident, references in change["add_iso"].items():
        assert set(references) <= set(transitions[ident]["iso"])


def test_G6_removing_acceptance_loses_PM_O2(model):
    model["release_transitions"] = [t for t in model["release_transitions"] if t["id"] != "W04"]
    assert iso_coverage(model)["missing_outcomes"] == ["PM.O2"]


def test_G3_accepted_mutant_removes_all_exits(model):
    change = yaml.safe_load((ROOT / "model/proposals/e2-structure.yaml").read_text())
    mutant = yaml.safe_load((ROOT / "mutants/g3_missing_deferred_exits.yaml").read_text())
    assert mutant["status"] == "active"
    assert change["g3_mutant"]["after"] == mutant["remove_transitions"]
    model["item_transitions"] = [t for t in model["item_transitions"] if t["id"] not in mutant["remove_transitions"]]
    assert dead_ends(model, "item") == {"deferred"}
