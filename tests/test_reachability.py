"""Świadkowie G2 od initial; jawne granice generatora.

Trace: G2, S1–S13.
"""

from copy import deepcopy

import pytest

from isomodel.execution import StepRejected, execute_step, initial_state, replay
from isomodel.exploration import (classify_candidates, exploration_inputs,
                                  generator_coverage_report,
                                  reachability_report, reachability_scenarios,
                                  reachability_witnesses)
from isomodel.safety import safety_violations


def test_every_declared_transition_has_executable_reachable_witness(model):
    report = reachability_report(model)
    assert report["missing"] == [], report
    assert len(report["covered"]) == 28
    assert all(run["outcome"] == "completed" for run in report["runs"]), report["runs"]
    assert report["bounds"] == model["test_instance"]["bounds"]
    assert report["exhaustive"] is False
    for ident, scenario in report["witnesses"].items():
        result = replay(model, scenario)
        assert result["outcome"] == "completed"
        assert result["steps"][0]["before"] == initial_state(model)
        assert result["steps"][-1]["event"]["transition"] == ident
        assert safety_violations(model, result["steps"]) == [], ident


def test_all_reachability_corpus_steps_satisfy_independent_safety_oracles(model):
    for scenario in reachability_scenarios():
        result = replay(model, scenario)
        assert result["outcome"] == "completed", result["steps"][-1]
        assert safety_violations(model, result["steps"]) == [], scenario["id"]


def test_reachability_report_does_not_claim_failed_path_is_a_witness(model):
    changed = deepcopy(model)
    next(t for t in changed["release_transitions"] if t["id"] == "W05")["guard"] = "false"
    report = reachability_report(changed)
    assert "W05" in report["missing"]
    assert "W05" not in report["witnesses"]
    assert any(run["outcome"] == "rejected" for run in report["runs"])


def test_baseline_reachability_covers_each_type_and_detects_g2_mutant(model):
    report = reachability_report(model)
    expected = {f"T04:{kind}" for kind in model["item_types"]}
    assert expected <= set(report["covered_applications"])
    for application in expected:
        result = replay(model, report["application_witnesses"][application])
        assert result["outcome"] == "completed"
        assert result["steps"][-1]["event"]["transition"] == "T04"
    changed = deepcopy(model)
    baseline = next(t for t in changed["item_transitions"] if t["id"] == "T04")
    baseline["guard"] = baseline["guard"].replace(
        "(state = approved or not type(e).requires_approval)", "state = approved")
    assert baseline["guard"] != next(t for t in model["item_transitions"] if t["id"] == "T04")["guard"]
    mutant = replay(changed, report["application_witnesses"]["T04:CODE"])
    assert mutant["outcome"] == "rejected"
    # Osobna osiągalna próba kończy się dokładnie na CODE; wcześniejsze DES
    # bazujemy modelem bazowym, aby nie zaliczyć odmowy DES jako wykrycia CODE.
    scenario = report["application_witnesses"]["T04:CODE"]
    prefix = dict(scenario, events=scenario["events"][:-1])
    state = replay(model, prefix)["final_state"]
    with pytest.raises(StepRejected, match="guard"):
        execute_step(changed, state, scenario["events"][-1], scenario["inputs"])


def test_dynamic_generator_can_execute_every_transition_at_reachable_sources(model):
    report = generator_coverage_report(model)
    expected = {t["id"] for kind in ("item", "question", "release") for t in model[f"{kind}_transitions"]}
    assert set(report["covered"]) == expected, report
    assert report["source_states"] == 28
    assert report["counts"]["applied"] > 28
    assert report["counts"]["rejected"] > 0
    assert report["counts"]["input_error"] == 0
    assert report["exhaustive"] is False


def test_question_limit_is_reported_as_boundary_with_other_steps_available(model):
    state = initial_state(model)
    inputs = exploration_inputs(model)
    for index in range(model["test_instance"]["bounds"]["max_questions"]):
        state = execute_step(model, state, {"transition": "P00", "actor": "A",
            "question": f"q{index}", "attributes": {"blocking": False}}, inputs)["after"]
    before = deepcopy(state)
    outcomes = classify_candidates(model, state)
    assert outcomes["boundary"]
    assert any(step["event"]["transition"] == "P01" for step in outcomes["applied"])
    assert state == before
    assert "deadlock" not in outcomes


def test_release_limit_is_separate_from_guard_rejection_and_atomic(model):
    witness = reachability_witnesses(model)["W06"]
    # Osiągalny stan po W06; domykamy drugie wydanie i zgłaszamy trzecią zmianę.
    scenario = next(s for s in reachability_scenarios() if s["id"] == "WIT5")
    result = replay(model, scenario)
    assert result["outcome"] == "completed"
    state = execute_step(model, result["final_state"],
        {"transition": "T06", "actor": "U", "item": "d1"}, scenario["inputs"])["after"]
    before = deepcopy(state)
    outcomes = classify_candidates(model, state)
    assert [e["transition"] for e in outcomes["boundary"]] == ["W06"]
    assert outcomes["applied"] == []
    assert state == before
    assert witness["events"][-1]["transition"] == "W06"


def test_version_limit_is_reported_without_mutation(model):
    result = replay(model, next(s for s in reachability_scenarios() if s["id"] == "WIT1"))
    state = result["final_state"]
    inputs = exploration_inputs(model)
    for version in range(1, model["test_instance"]["bounds"]["max_version"]):
        state = execute_step(model, state, {"transition": "T06", "actor": "U", "item": "d1"}, inputs)["after"]
        if state["next_release_required"]:
            state = execute_step(model, state, {"transition": "W06", "actor": "A"}, inputs)["after"]
        state = execute_step(model, state, {"transition": "T01", "actor": "A", "item": "d1"}, inputs)["after"]
    before = deepcopy(state)
    outcomes = classify_candidates(model, state)
    assert any(e["transition"] == "T06" and e["item"] == "d1" for e in outcomes["boundary"])
    assert state == before
