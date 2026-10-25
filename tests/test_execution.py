"""Kryteria WIT1 i blokad; niezależne oczekiwania wobec YAML.

Trace: WIT1, S1, S2, S3, S4, S7a, S7b, S8, S10.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest
from hypothesis import example, given, strategies as st

from isomodel.execution import (
    ExplorationBoundary, InputError, StepRejected, UnsupportedSemantics,
    execute_step, initial_state, replay,
)
from isomodel import load_model


FIXTURE = Path(__file__).parent / "fixtures/wit1/scenario.json"


@pytest.fixture
def scenario():
    return json.loads(FIXTURE.read_text())


def prefix(model, scenario, count):
    state = initial_state(model)
    for event in scenario["events"][:count]:
        state = execute_step(model, state, event, scenario["inputs"])["after"]
    return state


def event(transition, actor, item=None):
    result = {"transition": transition, "actor": actor,
              "evidence": {"simulation": True, "decision": "SIM-DEC-1",
                           "reference": "SIM-TAG-1", "quote": "Zgoda testowa"}}
    if item is not None:
        result["item"] = item
    return result


def transition(model, ident):
    return next(t for kind in ("item", "release", "question")
                for t in model[f"{kind}_transitions"] if t["id"] == ident)


def test_wit1_reaches_acceptance_with_exact_history(model, scenario):
    result = replay(model, scenario)
    assert result["outcome"] == "completed"
    assert len(result["steps"]) == 29
    state = result["final_state"]
    assert state["current_release"] == 1
    assert state["next_release_required"] is False
    assert state["questions"] == {}
    assert len(state["items"]) == 7
    for item in state["items"].values():
        assert (item["state"], item["version"], item["suspect"], item["rejections"]) == (
            "baselined", 1, False, 0)
    release = state["releases"][1]
    assert release["state"] == "accepted"
    assert set(release["snapshot"]) == set(model["test_instance"]["release_scope"])
    for ident, snapshot in release["snapshot"].items():
        assert snapshot == {k: v for k, v in state["items"][ident].items() if k != "id"}
    assert release["acceptance"] == {
        "number": 1, "quote": scenario["events"][-1]["evidence"]["quote"]}
    assert [s["event"]["transition"] for s in result["steps"]] == (
        ["T00", "T01", "T02", "T04"] * 5 + ["T00", "T01", "T04"] * 2
        + ["W01", "W02", "W04"])
    for previous, following in zip(result["steps"], result["steps"][1:]):
        assert previous["after"] == following["before"]
    for step in result["steps"]:
        assert step["outcome"] == "applied" and step["guard_result"] is True
        if step["event"]["transition"] in {"T02", "T04", "W04"}:
            assert step["event"]["actor"] == "U"
    assert result["steps"][-2]["event"]["actor"] == "R"


def test_replay_is_deterministic_and_does_not_mutate_inputs(model, scenario):
    original = deepcopy((model, scenario))
    first = replay(model, scenario)
    assert first == replay(model, scenario)
    assert (model, scenario) == original
    first["final_state"]["items"]["p1"]["version"] = 99
    first["final_state"]["items"]["r1"]["depends_on"].clear()
    first["final_state"]["releases"][1]["scope"].clear()
    assert first["steps"][-1]["after"]["items"]["p1"]["version"] == 1
    assert first["final_state"]["releases"][1]["snapshot"]["p1"]["version"] == 1
    assert first["final_state"]["releases"][1]["snapshot"]["r1"]["depends_on"] == ["p1"]
    assert len(first["steps"][-1]["after"]["releases"][1]["scope"]) == 7


@pytest.mark.parametrize("count,attempt,code", [
    (2, event("T02", "A", "p1"), "actor"),
    (3, event("T04", "A", "p1"), "actor"),
    (28, event("W04", "A"), "actor"),
    (27, event("W02", "A"), "actor"),
    (6, event("T04", "U", "r1"), "guard"),
    (5, event("T02", "U", "r1"), "state"),
    (26, event("W04", "U"), "state"),
    (27, event("W04", "U"), "state"),
    (25, event("W01", "A"), "guard"),
    (22, event("T02", "U", "d1"), "guard"),
    (29, event("W04", "U"), "state"),
])
def test_forbidden_steps_are_atomic(model, scenario, count, attempt, code):
    state = prefix(model, scenario, count)
    before = deepcopy(state)
    with pytest.raises(StepRejected, match=code):
        execute_step(model, state, attempt, scenario["inputs"])
    assert state == before


@pytest.mark.parametrize("dependency", ["d1", "a1"])
@pytest.mark.parametrize("dependency_state", ["none", "draft", "verified", "withdrawn", "superseded"])
def test_code_verification_requires_mature_dependencies(model, scenario, dependency, dependency_state):
    # Wstrzyknięty stan bada warunek; nie jest świadkiem osiągalności.
    state = prefix(model, scenario, 24)
    state["items"][dependency]["state"] = dependency_state
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, event("T01", "A", "c1"), scenario["inputs"])


def test_approved_dependency_allows_verification_but_not_baseline(model, scenario):
    state = prefix(model, scenario, 24)
    state["items"]["a1"]["state"] = "approved"
    state = execute_step(model, state, event("T01", "A", "c1"), scenario["inputs"])["after"]
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, event("T04", "U", "c1"), scenario["inputs"])


@pytest.mark.parametrize("count,ident", [(1, "T01"), (2, "T02"), (3, "T04")])
def test_suspect_blocks_item_gates(model, scenario, count, ident):
    state = prefix(model, scenario, count)
    state["items"]["p1"]["suspect"] = True
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, event(ident, "A" if ident == "T01" else "U", "p1"), scenario["inputs"])


@pytest.mark.parametrize("question_state,blocking,allowed", [
    ("open", True, False), ("asked", True, False), ("resolved", True, True),
    ("deferred", True, True), ("open", False, True),
])
def test_release_question_guard(model, scenario, question_state, blocking, allowed):
    state = prefix(model, scenario, 26)
    state["questions"]["q1"] = {"state": question_state, "blocking": blocking, "age": 1}
    if allowed:
        assert execute_step(model, state, event("W01", "A"), scenario["inputs"])["after"]["releases"][1]["state"] == "ready"
    else:
        with pytest.raises(StepRejected, match="guard"):
            execute_step(model, state, event("W01", "A"), scenario["inputs"])


@pytest.mark.parametrize("item_state,suspect,allowed", [
    ("baselined", True, False), ("draft", False, False), ("verified", False, False),
    ("approved", False, False), ("none", False, False),
    ("deferred", True, True), ("superseded", True, True), ("withdrawn", True, True),
])
def test_release_completeness_guard(model, scenario, item_state, suspect, allowed):
    state = prefix(model, scenario, 26)
    state["items"]["a2"].update(state=item_state, suspect=suspect)
    if allowed:
        execute_step(model, state, event("W01", "A"), scenario["inputs"])
    else:
        with pytest.raises(StepRejected, match="guard"):
            execute_step(model, state, event("W01", "A"), scenario["inputs"])


@pytest.mark.parametrize("count,key", [(1, "checks_ok"), (26, "tests_ok")])
def test_external_checks_cannot_be_assumed_true(model, scenario, count, key):
    inputs = deepcopy(scenario["inputs"])
    if key == "checks_ok":
        inputs[key]["p1"] = False
    else:
        inputs[key] = False
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, prefix(model, scenario, count), scenario["events"][count], inputs)


@pytest.mark.parametrize("count", [2, 3, 28])
def test_missing_or_non_simulated_evidence_is_rejected(model, scenario, count):
    state = prefix(model, scenario, count)
    attempt = deepcopy(scenario["events"][count])
    attempt.pop("evidence")
    with pytest.raises(StepRejected, match="evidence"):
        execute_step(model, state, attempt, scenario["inputs"])
    attempt["evidence"] = {"simulation": False, "quote": "zgoda"}
    with pytest.raises(StepRejected, match="evidence"):
        execute_step(model, state, attempt, scenario["inputs"])


def test_unknown_semantics_are_not_ignored_even_in_false_guard(model, scenario):
    state = initial_state(model)
    transition(model, "T00")["guard"] = "false and invented(e)"
    with pytest.raises(UnsupportedSemantics):
        execute_step(model, state, scenario["events"][0], scenario["inputs"])


def test_unknown_effect_cannot_partially_apply(model, scenario):
    state = initial_state(model)
    before = deepcopy(state)
    transition(model, "T00")["effects"].append("invented := true")
    with pytest.raises(UnsupportedSemantics):
        execute_step(model, state, scenario["events"][0], scenario["inputs"])
    assert state == before


def test_rules_and_initial_values_come_from_yaml_not_transition_ids(model, scenario):
    model["item_variables"]["rejections"]["initial"] = 1
    transition(model, "T00")["id"] = "CREATE_RENAMED"
    transition(model, "CREATE_RENAMED")["effects"] = ["version := 2"]
    for attempt in scenario["events"]:
        if attempt["transition"] == "T00":
            attempt["transition"] = "CREATE_RENAMED"
    result = replay(model, scenario)
    assert result["outcome"] == "completed"
    assert all(i["version"] == 2 and i["rejections"] == 1 for i in result["final_state"]["items"].values())


def test_replay_reports_denial_and_stops(model, scenario):
    scenario["events"][2]["actor"] = "A"
    result = replay(model, scenario)
    assert result["outcome"] == "rejected"
    assert len(result["steps"]) == 3
    denied = result["steps"][-1]
    assert denied["code"] == "actor"
    assert denied["before"] == denied["after"] == result["final_state"]


def test_evidence_denial_reports_already_evaluated_guard(model, scenario):
    scenario["events"][2].pop("evidence")
    result = replay(model, scenario)
    assert result["steps"][-1]["code"] == "evidence"
    assert result["steps"][-1]["guard_result"] is True


def test_change_without_question_is_reported_without_mutation(model, scenario):
    scenario["events"].append(event("T05", "U", "a2"))
    result = replay(model, scenario)
    assert result["outcome"] == "error"
    assert result["steps"][-1]["code"] == "input"
    assert result["steps"][-1]["before"] == result["final_state"]


@pytest.mark.parametrize("value", [None, "true", 1, [], {}])
def test_external_check_requires_actual_boolean(model, scenario, value):
    state = prefix(model, scenario, 1)
    scenario["inputs"]["checks_ok"]["p1"] = value
    with pytest.raises(InputError):
        execute_step(model, state, event("T01", "A", "p1"), scenario["inputs"])


def test_missing_input_and_typo_fail_explicitly(model, scenario):
    state = prefix(model, scenario, 1)
    with pytest.raises(InputError):
        execute_step(model, state, event("T01", "A", "p1"), {})
    with pytest.raises(InputError):
        execute_step(model, state, event("T01", "A", "p1"), {"check_ok": True})
    with pytest.raises(InputError):
        execute_step(model, state, {"transition": "TYPO", "actor": "A"}, {})


@pytest.mark.parametrize("count,field", [(2, "decision"), (2, "quote"), (3, "reference"), (3, "quote"), (28, "quote")])
def test_evidence_fields_are_nonempty(model, scenario, count, field):
    state = prefix(model, scenario, count)
    attempt = deepcopy(scenario["events"][count])
    attempt["evidence"][field] = "  "
    with pytest.raises(StepRejected, match="evidence"):
        execute_step(model, state, attempt, scenario["inputs"])


def test_pending_release_cannot_be_bypassed(model, scenario):
    state = prefix(model, scenario, 1)
    state["next_release_required"] = True
    with pytest.raises(StepRejected, match="pending_release"):
        execute_step(model, state, event("T01", "A", "p1"), scenario["inputs"])


def test_version_bound_is_not_reported_as_process_denial(model, scenario):
    transition(model, "T00")["effects"] = ["version := 4"]
    state = initial_state(model)
    with pytest.raises(ExplorationBoundary):
        execute_step(model, state, scenario["events"][0], scenario["inputs"])
    result = replay(model, scenario)
    assert result["outcome"] == "error" and result["steps"][0]["code"] == "boundary"
    assert result["final_state"] == state


def test_observer_is_executed_and_invalid_observer_fails_closed(model, scenario):
    # Kontrolowane wstrzyknięcie stanu/skutku bada obserwator, nie osiągalność.
    state = initial_state(model)
    state["releases"][1]["state"] = "accepted"
    transition(model, "T00")["effects"].append("suspect := true")
    after = execute_step(model, state, scenario["events"][0], scenario["inputs"])["after"]
    assert after["next_release_required"] is True
    assert after["releases"] == state["releases"]
    model["post_step_effects"][0]["guard"] = "false and unknown(e)"
    with pytest.raises(UnsupportedSemantics):
        execute_step(model, state, scenario["events"][0], scenario["inputs"])


def test_non_simulation_cannot_be_replayed(model, scenario):
    scenario["simulation"] = False
    with pytest.raises(InputError):
        replay(model, scenario)


def test_empty_release_scope_is_explicitly_outside_this_increment(model, scenario):
    state = prefix(model, scenario, 26)
    state["releases"][1]["scope"] = []
    with pytest.raises(UnsupportedSemantics, match="Pusty zakres"):
        execute_step(model, state, event("W01", "A"), scenario["inputs"])


def test_readiness_only_checks_items_in_scope(model, scenario):
    state = prefix(model, scenario, 26)
    state["releases"][1]["scope"].remove("a2")
    state["items"]["a2"].update(state="draft", suspect=True)
    execute_step(model, state, event("W01", "A"), scenario["inputs"])


@given(
    des=st.sampled_from(["none", "draft", "verified", "approved", "baselined", "deferred", "superseded", "withdrawn"]),
    acceptance_test=st.sampled_from(["none", "draft", "verified", "approved", "baselined", "deferred", "superseded", "withdrawn"]),
    suspect=st.booleans(), checks=st.booleans(), actor=st.sampled_from(["A", "U", "R"]),
)
@example(des="approved", acceptance_test="baselined", suspect=False, checks=True, actor="A")
@example(des="baselined", acceptance_test="approved", suspect=False, checks=True, actor="A")
def test_generated_code_verification_matches_independent_oracle(des, acceptance_test, suspect, checks, actor):
    model = load_model(FIXTURE.parents[3] / "model/process.yaml")
    state = initial_state(model)
    state["items"]["c1"].update(state="draft", version=1, suspect=suspect)
    state["items"]["d1"]["state"] = des
    state["items"]["a1"]["state"] = acceptance_test
    expected = actor == "A" and not suspect and checks and des in {"approved", "baselined"} and acceptance_test in {"approved", "baselined"}
    original = deepcopy(state)
    try:
        result = execute_step(model, state, event("T01", actor, "c1"), {"checks_ok": {"c1": checks}})
    except StepRejected:
        assert not expected
    else:
        assert expected and result["after"]["items"]["c1"]["state"] == "verified"
    assert state == original
