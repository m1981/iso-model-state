"""Sprawdzenie propozycji na kopii danych, bez zmiany zaakceptowanego modelu.

Trace: G3, G6.
"""

from copy import deepcopy

import yaml

from isomodel import validate_model
from isomodel.graph import dead_ends, iso_coverage
from conftest import ROOT


def proposed_model(model):
    proposal = yaml.safe_load((ROOT / "model/proposals/e2-structure.yaml").read_text())
    result = deepcopy(model)
    for kind in ("item", "question", "release"):
        for transition in result[f"{kind}_transitions"]:
            for reference in proposal["add_iso"].get(transition["id"], []):
                if reference not in transition.setdefault("iso", []):
                    transition["iso"].append(reference)
    return validate_model(result)


def test_G6_proposed_annotations_close_structural_gaps_without_changing_behavior(model):
    result = proposed_model(model)
    report = iso_coverage(result)
    assert not report["missing_outcomes"]
    assert not report["missing_transition_iso"]
    for kind in ("item", "question", "release"):
        for original, proposed in zip(model[f"{kind}_transitions"], result[f"{kind}_transitions"], strict=True):
            assert {k: v for k, v in original.items() if k != "iso"} == {k: v for k, v in proposed.items() if k != "iso"}


def test_G6_removing_acceptance_from_proposal_loses_PM_O2(model):
    result = proposed_model(model)
    result["release_transitions"] = [t for t in result["release_transitions"] if t["id"] != "W04"]
    assert iso_coverage(result)["missing_outcomes"] == ["PM.O2"]


def test_G3_proposed_mutant_removes_all_exits(model):
    proposal = yaml.safe_load((ROOT / "model/proposals/e2-structure.yaml").read_text())
    candidate = yaml.safe_load((ROOT / "mutants/g3_missing_deferred_exits.candidate.yaml").read_text())
    assert proposal["g3_mutant"]["after"] == candidate["remove_transitions"]
    model["item_transitions"] = [t for t in model["item_transitions"] if t["id"] not in candidate["remove_transitions"]]
    assert dead_ends(model, "item") == {"deferred"}
