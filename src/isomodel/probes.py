"""Próby czułości wybranych wyroczni na mutanty modelu w pamięci.

To narzędzie sprawdzające; nie definiuje reguł procesu ani pełnego pokrycia.
Trace: WIT1, WIT2, WIT4, S1, S2, S3, S4, S7a, S7b, S8, S9, L2, L4.
"""

from copy import deepcopy

from .execution import StepRejected, execute_step, initial_state


def _at_path(state, path):
    for key in path:
        state = state[key]
    return state


def _observe(model, state, case, inputs):
    try:
        step = execute_step(model, state, case["attempt"], inputs)
    except StepRejected as error:
        return error.code, error.code == case.get("expected_code"), False
    if "expected_records" in case:
        count = len(step["records"])
        return f"records={count}", count == case["expected_records"], True
    if "preserve_path" in case:
        path = case["preserve_path"]
        actual = _at_path(step["after"], path)
        return f"{'.'.join(path)}={actual}", actual == _at_path(state, path), True
    return "applied", False, True


def gate_probes(model, scenario, cases):
    results = []
    for case in cases:
        state = initial_state(model)
        for event in scenario["events"][:case["prefix_steps"]] + case.get("setup_events", []):
            state = execute_step(model, state, event, scenario["inputs"])["after"]
        baseline, baseline_matches, _ = _observe(model, state, case, scenario["inputs"])
        mutant = deepcopy(model)
        definition = next(t for kind in ("item", "question", "release") for t in mutant[f"{kind}_transitions"]
                          if t["id"] == case["attempt"]["transition"])
        definition[case["field"]] = deepcopy(case["replacement"])
        observation, mutant_matches, applied = _observe(mutant, state, case, scenario["inputs"])
        results.append({"id": case["id"], "property": case["property"], "baseline_code": baseline,
                        "mutant_outcome": observation,
                        "detected": baseline_matches and applied and not mutant_matches})
    return results
