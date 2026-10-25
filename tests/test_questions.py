"""Odrzucenia, jedna decyzja, FIFO i jawne dowody odpowiedzi.

Trace: WIT2, WIT4, S1, S9, L2, L4.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from isomodel import load_model
from isomodel.execution import (
    ExplorationBoundary, InputError, StepRejected, UnsupportedSemantics,
    execute_step, initial_state, replay,
)

ROOT = Path(__file__).resolve().parents[1]


def scenario(name):
    return json.loads((ROOT / f"tests/fixtures/{name}/scenario.json").read_text())


def prefix(model, data, count):
    result = replay(model, dict(data, events=data["events"][:count]))
    assert result["outcome"] == "completed", result["steps"][-1]
    return result["final_state"]


def question(transition, ident, actor="A", **kwargs):
    return dict(transition=transition, actor=actor, question=ident, **kwargs)


def raise_question(ident, blocking=True, actor="A"):
    return question("P00", ident, actor, attributes={"blocking": blocking})


def resolve(ident, answer=True, actor="U"):
    return question("P02", ident, actor, inputs={"unambiguous_answer": answer},
                    evidence={"simulation": True, "decision": f"SIM-DEC-{ident}", "quote": "Zgoda testowa"})


def definition(model, ident):
    return next(t for kind in ("item", "question") for t in model[f"{kind}_transitions"] if t["id"] == ident)


def test_wit2_two_rejections_then_approval_and_acceptance(model):
    data = scenario("wit2")
    result = replay(model, data)
    assert result["outcome"] == "completed"
    assert len(result["steps"]) == 33
    assert [s["after"]["items"]["r1"]["rejections"] for s in result["steps"][5:11]] == [0, 1, 1, 2, 2, 2]
    assert all(s["after"]["items"]["r1"]["version"] == 1 for s in result["steps"][4:])
    state = result["final_state"]
    assert state["items"]["r1"]["state"] == "baselined"
    assert state["releases"][1]["state"] == "accepted"
    assert state["releases"][1]["snapshot"]["r1"]["rejections"] == 2
    before = prefix(model, data, 10)
    original = deepcopy(before)
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, before, {"transition": "T03", "actor": "U", "item": "r1"}, data["inputs"])
    assert before == original


def test_rejection_limit_comes_from_yaml_and_mutant_is_observable(model):
    data = scenario("wit2")
    model["parameters"]["MAX_REJECTIONS"] = 1
    result = replay(model, data)
    assert result["outcome"] == "rejected" and len(result["steps"]) == 9
    assert result["final_state"]["items"]["r1"]["rejections"] == 1
    model["parameters"]["MAX_REJECTIONS"] = 2
    before = prefix(model, data, 10)
    definition(model, "T03")["guard"] = "true"
    after = execute_step(model, before, {"transition": "T03", "actor": "U", "item": "r1"}, data["inputs"])["after"]
    assert after["items"]["r1"]["rejections"] == 3  # Naruszenie wyroczni L4.


def test_wit4_preserves_fifo_and_only_resolutions_create_records(model):
    data = scenario("wit4")
    original = deepcopy((model, data))
    result = replay(model, data)
    assert result["outcome"] == "completed" and len(result["steps"]) == 13
    assert [s["event"]["question"] for s in result["steps"] if s["event"]["transition"] == "P01"] == ["q1", "q1", "q2", "q3"]
    ambiguous = result["steps"][4]
    assert ambiguous["records"] == []
    assert ambiguous["after"]["questions"]["q1"] == dict(ambiguous["before"]["questions"]["q1"], state="open")
    assert [r["question"] for r in result["records"]] == ["q1", "q2", "q3"]
    assert [r["step"] for r in result["records"]] == [7, 9, 13]
    assert all(r["simulation"] is True and r["kind"] == "decision" for r in result["records"])
    assert [q["age"] for q in result["final_state"]["questions"].values()] == [1, 2, 3]
    assert all(q["state"] == "resolved" for q in result["final_state"]["questions"].values())
    for step in result["steps"]:
        assert sum(q["state"] == "asked" for q in step["after"]["questions"].values()) <= 1
    assert result == replay(model, data)
    assert (model, data) == original


@pytest.mark.parametrize("actor", ["A", "R", "U"])
def test_question_creation_initializes_declared_variables(model, actor):
    state = initial_state(model)
    step = execute_step(model, state, raise_question("q1", False, actor), {})
    assert state["questions"] == {}
    assert step["after"]["questions"]["q1"] == {
        "id": "q1", "state": "open", "blocking": False, "age": 1,
        "kind": "general", "about": "none", "about_version": "none",
        "requested_transition": "none", "resolution": "none", "consumed": False}
    assert step["records"] == []


@pytest.mark.parametrize("attributes", [{}, {"blocking": "false"}, {"blocking": 0}, {"blocking": True, "age": 99}, {"blocking": True, "kind": "change"}])
def test_invalid_creation_data_is_not_silently_accepted(model, attributes):
    state = initial_state(model)
    with pytest.raises((InputError, UnsupportedSemantics)):
        execute_step(model, state, question("P00", "q1", attributes=attributes), {})
    assert state == initial_state(model)


def test_fifo_with_blocking_priority_and_nonblocking_fallback(model):
    state = initial_state(model)
    for ident, blocking in [("old", False), ("first", True), ("second", True)]:
        state = execute_step(model, state, raise_question(ident, blocking), {})["after"]
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P01", "old"), {})
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P01", "second"), {})
    for ident in ("first", "second", "old"):
        state = execute_step(model, state, question("P01", ident), {})["after"]
        state = execute_step(model, state, resolve(ident), {})["after"]


def test_fifo_uses_creation_order_not_question_identifier(model):
    state = initial_state(model)
    for ident in ("z-last-alphabetically", "a-first-alphabetically"):
        state = execute_step(model, state, raise_question(ident), {})["after"]
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P01", "a-first-alphabetically"), {})
    execute_step(model, state, question("P01", "z-last-alphabetically"), {})


def test_new_blocking_question_keeps_priority_after_ambiguous_answer(model):
    state = initial_state(model)
    for attempt in (raise_question("old", False), question("P01", "old"),
                    raise_question("new", True), question("P03", "old", "U")):
        state = execute_step(model, state, attempt, {})["after"]
    assert state["questions"]["old"]["age"] == 1
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P01", "old"), {})
    execute_step(model, state, question("P01", "new"), {})


def test_deferring_asked_nonblocking_question_frees_slot_and_keeps_age(model):
    state = initial_state(model)
    for attempt in (raise_question("q1", False), question("P01", "q1"),
                    raise_question("q2", False), question("P04", "q1", "U"),
                    question("P01", "q2"), question("P05", "q1", "U")):
        state = execute_step(model, state, attempt, {})["after"]
    assert state["questions"]["q1"]["age"] == 1
    assert state["questions"]["q2"]["state"] == "asked"
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P01", "q1"), {})
    state = execute_step(model, state, resolve("q2"), {})["after"]
    execute_step(model, state, question("P01", "q1"), {})


def test_second_asked_is_denied_and_count_mutant_exposes_violation(model):
    state = prefix(model, scenario("wit4"), 4)
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P01", "q2"), {})
    definition(model, "P01")["guard"] = "q = oldest(open, blocking_first)"
    after = execute_step(model, state, question("P01", "q2"), {})["after"]
    assert sum(q["state"] == "asked" for q in after["questions"].values()) == 2


def test_fifo_oracle_detects_lifo_mutant(model):
    state = prefix(model, scenario("wit4"), 5)
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P01", "q2"), {})
    definition(model, "P01")["guard"] = "count(asked) = 0 and q = newest(open, blocking_first)"
    execute_step(model, state, question("P01", "q2"), {})


@pytest.mark.parametrize("value", [False, None, "true", 1])
def test_resolve_requires_explicit_unambiguous_boolean(model, value):
    state = prefix(model, scenario("wit4"), 2)
    original = deepcopy(state)
    with pytest.raises((StepRejected, InputError)):
        execute_step(model, state, resolve("q1", value), {})
    assert state == original


def test_answer_does_not_leak_to_next_event(model):
    data = scenario("wit4")
    data["events"][8].pop("inputs")
    result = replay(model, data)
    assert result["outcome"] == "error" and result["steps"][-1]["code"] == "input"
    assert len(result["records"]) == 1
    assert result["final_state"]["questions"]["q2"]["state"] == "asked"


@pytest.mark.parametrize("missing", ["quote", "decision", "simulation"])
def test_question_decision_requires_evidence(model, missing):
    state = prefix(model, scenario("wit4"), 2)
    attempt = resolve("q1")
    attempt["evidence"].pop(missing)
    with pytest.raises(StepRejected, match="evidence"):
        execute_step(model, state, attempt, {})


@pytest.mark.parametrize("transition,actor,count,ident", [
    ("P01", "U", 1, "q1"), ("P02", "A", 2, "q1"),
    ("P03", "R", 2, "q1"), ("P04", "A", 4, "q3"), ("P05", "R", 10, "q3"),
])
def test_question_roles_are_enforced(model, transition, actor, count, ident):
    state = prefix(model, scenario("wit4"), count)
    attempt = resolve(ident, actor=actor) if transition == "P02" else question(transition, ident, actor)
    with pytest.raises(StepRejected, match="actor"):
        execute_step(model, state, attempt, {})


def test_blocking_question_cannot_be_deferred(model):
    state = prefix(model, scenario("wit4"), 2)
    with pytest.raises(StepRejected, match="guard"):
        execute_step(model, state, question("P04", "q1", "U"), {})


@pytest.mark.parametrize("actor", ["U", "A"])
def test_resumption_preserves_age_and_does_not_create_decision(model, actor):
    state = prefix(model, scenario("wit4"), 10)
    step = execute_step(model, state, question("P05", "q3", actor), {})
    assert step["after"]["questions"]["q3"] == dict(state["questions"]["q3"], state="open")
    assert step["records"] == []


def test_duplicate_and_resolved_question_cannot_be_recreated(model):
    data = scenario("wit4")
    for count in (1, 7):
        state = prefix(model, data, count)
        with pytest.raises((StepRejected, InputError)):
            execute_step(model, state, raise_question("q1"), {})


def test_question_bound_does_not_partially_create_record(model):
    state = prefix(model, scenario("wit4"), 4)
    original = deepcopy(state)
    with pytest.raises(ExplorationBoundary):
        execute_step(model, state, raise_question("q4"), {})
    assert state == original


def test_question_rules_are_not_dispatched_by_ids(model):
    data = scenario("wit4")
    mapping = {t["id"]: f"QUESTION_{i}" for i, t in enumerate(model["question_transitions"])}
    for t in model["question_transitions"]:
        t["id"] = mapping[t["id"]]
    for event in data["events"]:
        event["transition"] = mapping[event["transition"]]
    result = replay(model, data)
    assert result["outcome"] == "completed" and len(result["records"]) == 3


@given(flags=st.lists(st.booleans(), min_size=1, max_size=3))
def test_generated_queue_order_matches_priority_then_creation(flags):
    model = load_model(ROOT / "model/process.yaml")
    state = initial_state(model)
    for i, flag in enumerate(flags):
        state = execute_step(model, state, raise_question(f"q{i}", flag), {})["after"]
    expected = sorted(range(len(flags)), key=lambda i: (not flags[i], i))
    for i in expected:
        state = execute_step(model, state, question("P01", f"q{i}"), {})["after"]
        state = execute_step(model, state, resolve(f"q{i}"), {})["after"]
    assert all(q["state"] == "resolved" for q in state["questions"].values())
