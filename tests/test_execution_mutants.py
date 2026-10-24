"""Czułość wybranych wyroczni WIT1 na uszkodzenie danych modelu.

Nie jest to pełne pokrycie mutacyjne E2.
Trace: WIT1, S1, S2, S3, S4, S7a, S7b, S8.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel.execution import StepRejected, execute_step, initial_state


FIXTURES = Path(__file__).parent / "fixtures/wit1"
MUTANTS = json.loads((FIXTURES.parents[2] / "mutants/wit1_gates.json").read_text())


@pytest.mark.parametrize("case", MUTANTS, ids=lambda c: c["id"])
def test_guard_oracle_detects_mutant(model, case):
    scenario = json.loads((FIXTURES / "scenario.json").read_text())
    state = initial_state(model)
    for event in scenario["events"][:case["prefix_steps"]]:
        state = execute_step(model, state, event, scenario["inputs"])["after"]
    for event in case.get("setup_events", []):
        state = execute_step(model, state, event, scenario["inputs"])["after"]
    event = deepcopy(case["attempt"])
    with pytest.raises(StepRejected, match=case["expected_code"]):
        execute_step(model, state, event, scenario["inputs"])
    mutant = deepcopy(model)
    transition = next(t for kind in ("item", "release") for t in mutant[f"{kind}_transitions"]
                      if t["id"] == event["transition"])
    transition[case["field"]] = case["replacement"]
    # Wyrocznia oczekuje odmowy; mutant przyjmuje ten sam krok, więc ją narusza.
    assert execute_step(mutant, state, event, scenario["inputs"])["outcome"] == "applied"
