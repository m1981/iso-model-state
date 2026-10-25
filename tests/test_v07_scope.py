"""DEC-PRO-010: wpływ spoza zakresu i atomowość obserwatorów, S7a/S10.

Wszystkie stany osiągamy od inicjalizacji alternatywnej instancji modelu.
Kontrolowana zmiana obserwatora bada wyłącznie atomowość błędu wykonania.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel.execution import InputError, StepRejected, execute_step, initial_state
from isomodel.exploration import exploration_inputs, simulation_evidence
from isomodel.safety import safety_violations


WIT1 = json.loads((Path(__file__).parent / "fixtures/wit1/scenario.json").read_text())


def external_change_prefix(model, release_state):
    model["test_instance"]["release_scope"].remove("p1")
    state = initial_state(model)
    inputs = exploration_inputs(model)
    events = deepcopy(WIT1["events"][:{"ready": 27, "reviewed": 28, "accepted": 29}[release_state]])
    events += [
        {"transition": "P00", "actor": "A", "question": "change-p1",
         "attributes": {"kind": "change", "about": "p1",
                        "requested_transition": "T05", "blocking": True}},
        {"transition": "P01", "actor": "A", "question": "change-p1"},
        {"transition": "P02", "actor": "U", "question": "change-p1",
         "inputs": {"unambiguous_answer": True, "resolution": "approved"},
         "evidence": simulation_evidence()},
    ]
    steps = []
    for candidate in events:
        step = execute_step(model, state, candidate, inputs)
        steps.append(step)
        state = step["after"]
    assert state["releases"][1]["state"] == release_state
    assert "p1" not in state["releases"][1]["scope"]
    assert safety_violations(model, steps) == []
    return state, inputs, steps


@pytest.mark.parametrize("release_state", ["ready", "reviewed", "accepted"])
def test_external_change_invalidates_only_unsigned_release(model, release_state):
    state, inputs, steps = external_change_prefix(model, release_state)
    candidate = {"transition": "T05", "actor": "U", "item": "p1", "question": "change-p1"}
    original = deepcopy((model, state, candidate, inputs))
    step = execute_step(model, state, candidate, inputs)
    assert (model, state, candidate, inputs) == original
    steps.append(step)
    after = step["after"]
    assert after["questions"]["change-p1"]["consumed"] is True
    assert after["items"]["p1"]["state"] == "draft"
    assert after["items"]["p1"]["version"] == 2
    for ident in state["releases"][1]["scope"]:
        assert state["items"][ident]["suspect"] is False
        assert after["items"][ident]["suspect"] is True

    if release_state == "accepted":
        assert after["releases"] == state["releases"]
        assert after["next_release_required"] is True
        frozen = deepcopy(after)
        with pytest.raises(StepRejected, match="pending_release"):
            execute_step(model, after, {"transition": "T01", "actor": "A", "item": "p1"}, inputs)
        assert after == frozen
        next_release = execute_step(model, after, {"transition": "W06", "actor": "A"}, inputs)
        steps.append(next_release)
        assert next_release["after"]["current_release"] == 2
        assert next_release["after"]["releases"][1] == state["releases"][1]
        assert next_release["after"]["releases"][2]["scope"] == state["releases"][1]["scope"]
        assert next_release["after"]["next_release_required"] is False
    else:
        assert after["releases"][1] == state["releases"][1] | {"state": "in_preparation"}
        assert after["next_release_required"] is False
    assert safety_violations(model, steps) == []


@pytest.mark.parametrize("release_state", ["ready", "reviewed", "accepted"])
def test_observer_failure_rolls_back_external_change_and_consumed_consent(model, release_state):
    state, inputs, steps = external_change_prefix(model, release_state)
    # Ten efekt zawodzi dopiero po skutkach T05 i obu obserwatorach modelu.
    model["post_step_effects"].append({"id": "failing-observer", "guard": "true",
                                       "effects": ["next_release_required := checks_ok(e)"]})
    inputs["checks_ok"].pop("p1")
    candidate = {"transition": "T05", "actor": "U", "item": "p1", "question": "change-p1"}
    original = deepcopy((model, state, candidate, inputs, steps))
    with pytest.raises(InputError, match="Brak checks_ok dla p1"):
        execute_step(model, state, candidate, inputs)
    assert (model, state, candidate, inputs, steps) == original
    assert state["questions"]["change-p1"]["consumed"] is False
    assert safety_violations(model, steps) == []
