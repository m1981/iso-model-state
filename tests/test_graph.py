"""Projekcja strukturalna grafu, bez założenia wykonalności warunków.

Trace: G1, G3, G5, G6, S10.
"""

import pytest
import yaml

from isomodel.graph import completeness_matrix, dead_ends, iso_coverage, state_graph, unreachable_states
from conftest import ROOT


@pytest.mark.parametrize("kind", ["item", "question", "release"])
def test_G1_no_structurally_unreachable_state_in_base_model(model, kind):
    assert unreachable_states(model, kind) == set()


def test_G1_detects_missing_approval_transition(model):
    mutant = yaml.safe_load((ROOT / "mutants/g1_missing_approval.yaml").read_text())
    model["item_transitions"] = [t for t in model["item_transitions"] if t["id"] not in mutant["remove_transitions"]]
    assert unreachable_states(model, "item") == {"approved"}


@pytest.mark.parametrize("kind", ["item", "question", "release"])
def test_G3_no_structural_dead_end_in_base_model(model, kind):
    assert dead_ends(model, kind) == set()


def test_G3_detects_removal_of_all_exits_from_deferred(model):
    model["item_transitions"] = [t for t in model["item_transitions"] if t["id"] not in {"T07", "T08", "T10"}]
    assert dead_ends(model, "item") == {"deferred"}


def test_S10_next_release_is_not_edge_out_of_accepted_record(model):
    graph = state_graph(model, "release")
    assert graph.out_degree("accepted") == 0
    assert not any(data["transition"] == "W06" for *_, data in graph.edges(data=True))


def test_G5_reports_every_pair_without_claiming_guard_satisfiability(model):
    matrix = completeness_matrix(model, "release")
    assert len(matrix) == len(model["release_states"]) * len(model["release_transitions"])
    assert matrix[("accepted", "W06")] == "new_instance_if_guard"
    assert matrix[("ready", "W04")] == "forbidden_by_source"
    assert matrix[("reviewed", "W04")] == "current_instance_if_guard"


def test_G6_reports_missing_annotations_without_inventing_task_outcome_mapping(model):
    for kind in ("item", "question", "release"):
        for transition in model[f"{kind}_transitions"]:
            if "iso" in transition:
                transition["iso"] = [ref for ref in transition["iso"] if ".O" not in ref or ref == "SI.O7"]
            if transition["id"] in {"P03", "P05"}:
                transition.pop("iso", None)
    report = iso_coverage(model)
    assert report["covered"] == {"SI.O7": ["W02", "W03"]}
    assert report["missing_transition_iso"] == ["P03", "P05"]
    assert "PM.O2" in report["missing_outcomes"]


def test_G6_reads_outcomes_from_input_model(model):
    model["release_transitions"][3]["iso"].append("PM.O2")
    assert iso_coverage(model)["covered"]["PM.O2"] == ["W04"]
