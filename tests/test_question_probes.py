"""Wybrane mutanty i atomowość zapisu decyzji symulacyjnej.

Trace: WIT2, WIT4, S9, L2, L4.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel.execution import replay
from isomodel.probes import gate_probes

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name,count", [("wit2", 2), ("wit4", 7)])
def test_new_probe_sets_detect_every_selected_mutant(model, name, count):
    data = json.loads((ROOT / f"tests/fixtures/{name}/scenario.json").read_text())
    cases = json.loads((ROOT / f"mutants/{name}_gates.json").read_text())
    original = deepcopy((model, data, cases))
    result = gate_probes(model, data, cases)
    assert len(result) == count and all(case["detected"] for case in result), result
    assert (model, data, cases) == original


def test_runtime_error_after_record_creation_does_not_commit_record_or_question(model):
    data = json.loads((ROOT / "tests/fixtures/wit4/scenario.json").read_text())
    transition = next(t for t in model["question_transitions"] if t["id"] == "P02")
    transition["effects"].append("age := unambiguous_answer + 1")  # bool nie jest int.
    result = replay(model, data)
    assert result["outcome"] == "error" and result["steps"][-1]["code"] == "input"
    assert len(result["steps"]) == 7
    assert result["records"] == [] and result["steps"][-1]["records"] == []
    assert result["steps"][-1]["before"] == result["final_state"]
    assert result["final_state"]["questions"]["q1"]["state"] == "asked"


def test_decision_records_do_not_alias_event_or_other_reports(model):
    data = json.loads((ROOT / "tests/fixtures/wit4/scenario.json").read_text())
    result = replay(model, data)
    result["records"][0]["quote"] = "zmieniony raport"
    assert result["steps"][6]["records"][0]["quote"] == data["events"][6]["evidence"]["quote"]
    assert replay(model, data)["records"][0]["quote"] != "zmieniony raport"
