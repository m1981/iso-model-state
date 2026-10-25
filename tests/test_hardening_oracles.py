"""Niezależne wyrocznie v0.7 na wykonanych śladach i mutantach.

Trace: S14, S15, DEC-PRO-010. Skończone przykłady, nie dowód formalny.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel.execution import replay
from isomodel.safety import safety_violations


ROOT = Path(__file__).resolve().parents[1]


def witness():
    return json.loads((ROOT / "tests/fixtures/wit1/scenario.json").read_text())


def transition(model, ident):
    return next(t for kind in ("item", "question", "release")
                for t in model[f"{kind}_transitions"] if t["id"] == ident)


def event(ident, item="p1"):
    return {"transition": ident, "actor": "A" if ident in {"T00", "T01"} else "U", "item": item}


def rejection_cycles(item="p1", count=2):
    return [event(ident, item) for _ in range(count) for ident in ("T01", "T03")]


def run(model, events):
    return replay(model, dict(witness(), events=events))


def findings(model, result):
    return safety_violations(model, [s for s in result["steps"] if s["outcome"] == "applied"])


def executed_mutant(model, mutant, events):
    baseline = run(model, events)
    assert baseline["outcome"] in {"completed", "rejected"}, baseline
    assert findings(model, baseline) == []
    result = run(mutant, events)
    assert result["outcome"] == "completed", result["steps"][-1]
    return result


@pytest.mark.parametrize("asked", [False, True])
def test_s14_detects_executed_acceptance_with_late_blocker(model, asked):
    data = witness()
    events = data["events"][:28] + [
        {"transition": "P00", "actor": "R", "question": "late", "attributes": {"blocking": True}}]
    if asked:
        events.append({"transition": "P01", "actor": "A", "question": "late"})
    events.append(data["events"][-1])
    mutant = deepcopy(model)
    transition(mutant, "W04")["guard"] = "true"
    result = executed_mutant(model, mutant, events)
    assert {v["property"] for v in findings(model, result)} == {"S14"}
    assert findings(model, result)[0]["step"] == len(events)


@pytest.mark.parametrize("state", ["open", "asked", "resolved", "deferred"])
@pytest.mark.parametrize("blocking", [False, True])
def test_s14_acceptance_question_states(model, state, blocking):
    data = witness()
    events = data["events"][:28] + [
        {"transition": "P00", "actor": "R", "question": "late", "attributes": {"blocking": blocking}}]
    if state != "open":
        events.append({"transition": "P01", "actor": "A", "question": "late"})
    if state == "resolved":
        events.append({"transition": "P02", "actor": "U", "question": "late",
                       "inputs": {"unambiguous_answer": True, "resolution": "answered"},
                       "evidence": {"simulation": True, "decision": "SIM-LATE", "quote": "Odpowiedź testowa."}})
    elif state == "deferred":
        events.append({"transition": "P04", "actor": "U", "question": "late"})
    events.append(data["events"][-1])
    result = run(model, events)
    assert result["outcome"] == ("rejected" if blocking and state != "resolved" else "completed")
    if blocking and state == "deferred":
        # P04 nie pozwala odłożyć pytania blokującego; W04 nie jest osiągnięte.
        assert result["steps"][-1]["event"]["transition"] == "P04"
    assert findings(model, result) == []


def test_s14_question_created_after_acceptance_is_not_retroactive(model):
    events = witness()["events"] + [
        {"transition": "P00", "actor": "R", "question": "later", "attributes": {"blocking": True}},
        {"transition": "P01", "actor": "A", "question": "later"}]
    result = run(model, events)
    assert result["outcome"] == "completed"
    assert findings(model, result) == []


def test_s15_detects_t10_reset_and_third_historical_rejection(model):
    events = [event("T00")] + rejection_cycles() + [event("T09"), event("T10")] + rejection_cycles(count=1)
    mutant = deepcopy(model)
    transition(mutant, "T10")["effects"].insert(0, "rejections := 0")
    result = executed_mutant(model, mutant, events)
    assert result["final_state"]["items"]["p1"]["rejections"] == 1
    assert {(v["property"], v["step"]) for v in findings(model, result)} == {("S15", 7), ("S15", 9)}


def test_s15_counts_events_even_when_integer_counter_never_increases(model):
    mutant = deepcopy(model)
    transition(mutant, "T03")["effects"] = []
    events = [event("T00")] + rejection_cycles(count=3)
    result = executed_mutant(model, mutant, events)
    assert all(s["after"]["items"]["p1"]["rejections"] == 0 for s in result["steps"])
    assert any(v["property"] == "S15" and v["step"] == 7 for v in findings(model, result))


@pytest.mark.parametrize("operation", ["T09", "T10"])
def test_s15_reset_requires_an_authorized_new_version(model, operation):
    mutant = deepcopy(model)
    transition(mutant, operation)["effects"].insert(0, "rejections := 0")
    events = [event("T00")] + rejection_cycles(count=1) + [event("T09")]
    if operation == "T10":
        events.append(event("T10"))
    result = executed_mutant(model, mutant, events)
    assert any(v["property"] == "S15" and v["step"] == len(events) for v in findings(model, result))


def test_s15_t10_preserves_nonzero_counter_exactly(model):
    mutant = deepcopy(model)
    transition(mutant, "T10")["effects"].insert(0, "rejections := rejections + 1")
    events = [event("T00")] + rejection_cycles(count=1) + [event("T09"), event("T10")]
    result = executed_mutant(model, mutant, events)
    assert any(v["property"] == "S15" and v["step"] == 5 for v in findings(model, result))


def test_s15_t10_cannot_open_another_version_to_evade_history(model):
    mutant = deepcopy(model)
    transition(mutant, "T10")["effects"].insert(0, "version := version + 1")
    events = [event("T00")] + rejection_cycles(count=1) + [event("T09"), event("T10")]
    result = executed_mutant(model, mutant, events)
    assert any(v["property"] == "S15" and v["step"] == 5 for v in findings(model, result))


def test_s15_same_version_number_on_other_item_has_own_budget(model):
    events = ([event("T00")] + rejection_cycles() + witness()["events"][1:4]
              + [event("T00", "r1")] + rejection_cycles("r1"))
    result = run(model, events)
    assert result["outcome"] == "completed", result["steps"][-1]
    assert sum(s["event"]["transition"] == "T03" for s in result["steps"]) == 4
    assert findings(model, result) == []


def test_s15_uses_declared_limit_in_alternative_instance(model):
    instance = deepcopy(model)
    instance["parameters"]["MAX_REJECTIONS"] = 1
    mutant = deepcopy(instance)
    transition(mutant, "T03")["effects"] = []
    result = executed_mutant(instance, mutant, [event("T00")] + rejection_cycles())
    assert any(v["property"] == "S15" and v["step"] == 5 for v in findings(instance, result))


def new_version_events(operation):
    item = "p1" if operation == "T05" else "d1"
    prefix = [] if item == "p1" else witness()["events"][:20]
    events = prefix + [event("T00", item)] + rejection_cycles(item) + [event("T01", item)]
    if operation == "T05":
        events += [
            {"transition": "P00", "actor": "A", "question": "change", "attributes": {
                "kind": "change", "about": item, "requested_transition": "T05", "blocking": True}},
            {"transition": "P01", "actor": "A", "question": "change"},
            {"transition": "P02", "actor": "U", "question": "change",
             "inputs": {"unambiguous_answer": True, "resolution": "approved"},
             "evidence": {"simulation": True, "decision": "SIM-V2", "quote": "Zgoda testowa na nową wersję."}},
            dict(event("T05", item), question="change")]
    else:
        events.append(event("T06", item))
    return events + rejection_cycles(item)


@pytest.mark.parametrize("operation", ["T05", "T06"])
def test_s15_new_versions_have_separate_rejection_budgets(model, operation):
    result = run(model, new_version_events(operation))
    assert result["outcome"] == "completed", result["steps"][-1]
    counts = {}
    for step in result["steps"]:
        if step["event"]["transition"] == "T03":
            ident = step["event"]["item"]
            key = (ident, step["before"]["items"][ident]["version"])
            counts[key] = counts.get(key, 0) + 1
    assert sorted(counts.values()) == [2, 2]
    assert findings(model, result) == []


@pytest.mark.parametrize("operation", ["T05", "T06"])
def test_s15_new_version_operation_cannot_reset_same_version(model, operation):
    mutant = deepcopy(model)
    transition(mutant, operation)["effects"].remove("version := version + 1")
    events = new_version_events(operation)[:-4]
    result = executed_mutant(model, mutant, events)
    assert any(v["property"] == "S15" and v["step"] == len(events) for v in findings(model, result))
