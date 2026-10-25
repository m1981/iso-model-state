"""Niezależne wyrocznie: świadkowie, błędne historie i wykonywane mutanty.

Trace: S1–S13, WIT1–WIT5. Mutant musi wykonać krok; błąd parsera nie wystarcza.
"""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel.execution import replay
from isomodel.safety import safety_violations


ROOT = Path(__file__).resolve().parents[1]


def scenario(name="wit1"):
    return json.loads((ROOT / f"tests/fixtures/{name}/scenario.json").read_text())


def transition(model, ident):
    return next(t for kind in ("item", "question", "release")
                for t in model[f"{kind}_transitions"] if t["id"] == ident)


@pytest.mark.parametrize("name", ["wit1", "wit2", "wit3", "wit4", "wit5"])
def test_safety_witnesses(model, name):
    result = replay(model, scenario(name))
    assert result["outcome"] == "completed"
    untouched = deepcopy((model, result))
    assert safety_violations(model, result["steps"]) == []
    assert (model, result) == untouched


def test_safety_requires_complete_contiguous_applied_history(model):
    steps = replay(model, scenario())["steps"]
    for invalid in (steps[1:], steps[:3] + steps[4:]):
        with pytest.raises(ValueError, match="ciągły"):
            safety_violations(model, invalid)
    steps[0]["outcome"] = "rejected"
    with pytest.raises(ValueError, match="applied"):
        safety_violations(model, steps[:1])
    assert safety_violations(model, []) == []


SAFETY_PROPERTIES = ("S1", "S2", "S3", "S4", "S5", "S6", "S7a", "S7b", "S8",
                     "S9", "S10", "S11", "S12", "S13")


def mutant_case(model, property_id):
    """Jeden błąd modelu, pełna historia, niezależna oczekiwana właściwość."""
    data = scenario()
    events = data["events"]
    mutant = deepcopy(model)
    if property_id == "S1":
        transition(mutant, "T04")["actor"] = "A"
        events[:] = events[:4]
        events[-1]["actor"] = "A"
    elif property_id == "S2":
        transition(mutant, "T04")["guard"] = "not suspect"
        events[:] = events[:2] + [events[3]]
    elif property_id == "S3":
        transition(mutant, "T02")["from"] = ["draft"]
        events[:] = events[:1] + [events[2]]
    elif property_id == "S4":
        transition(mutant, "T01")["guard"] = "not suspect and checks_ok(e)"
        events[:] = events[4:6]
    elif property_id in {"S5", "S6", "S12", "S13"}:
        data = scenario("wit3")
        if property_id == "S5":
            t = transition(mutant, "T07")
            t["effects"] = [e for e in t["effects"] if not e.startswith("forall d")]
            data["events"] = data["events"][:32]
        elif property_id == "S6":
            transition(mutant, "T11")["guard"] = "suspect"
            data["events"] = data["events"][:32] + [{"transition": "T11", "actor": "A", "item": "a1",
                "evidence": {"simulation": True, "decision": "SIM-NO-IMPACT", "reference": "SIM-REVIEW"}}]
        elif property_id == "S12":
            transition(mutant, "T14")["effects"][0] = "depends_on := depends_on"
            data["events"] = data["events"][:42]
        else:
            transition(mutant, "W07")["effects"] = ["release.scope := {e.id}"]
            data["events"] = data["events"][:37]
    elif property_id == "S7a":
        t = transition(mutant, "T05")
        t["effects"].remove("invalidate_release(e)")
        data["events"] = events[:28] + scenario("wit5")["events"][29:33]
    elif property_id == "S7b":
        transition(mutant, "W04")["effects"][0] = "release.snapshot := snapshot(release.scope minus release.scope)"
    elif property_id == "S8":
        transition(mutant, "W04")["from"] = ["ready"]
        data["events"] = events[:27] + [events[28]]
    elif property_id == "S9":
        transition(mutant, "P01")["guard"] = "true"
        data["events"] = [
            {"transition": "P00", "actor": "A", "question": "q1", "attributes": {"blocking": False}},
            {"transition": "P00", "actor": "A", "question": "q2", "attributes": {"blocking": False}},
            {"transition": "P01", "actor": "A", "question": "q1"},
            {"transition": "P01", "actor": "A", "question": "q2"},
        ]
    elif property_id == "S10":
        transition(mutant, "W06")["effects"].insert(0, "release.state := in_preparation")
        data = scenario("wit5")
        data["events"] = data["events"][:34]
    elif property_id == "S11":
        transition(mutant, "T05")["effects"].remove("q.consumed := true")
        data = scenario("wit5")
        data["events"] = data["events"][:33]
    return mutant, data


@pytest.mark.parametrize("property_id", SAFETY_PROPERTIES)
def test_executed_mutant_violates_independent_oracle(model, property_id):
    mutant, data = mutant_case(model, property_id)
    baseline = replay(model, data)
    baseline_applied = [s for s in baseline["steps"] if s["outcome"] == "applied"]
    assert safety_violations(model, baseline_applied) == []
    result = replay(mutant, data)
    assert result["outcome"] == "completed", result["steps"][-1]
    findings = safety_violations(model, result["steps"])
    assert any(f["property"] == property_id and f["step"] == len(result["steps"])
               for f in findings), findings


@pytest.mark.parametrize("property_id,skip", [("S2", 35), ("S3", 34)])
def test_old_version_evidence_does_not_authorize_new_version(model, property_id, skip):
    # Stara wersja a2 jest zweryfikowana i zatwierdzona. Wersja 2 omija jeden etap.
    data = scenario("wit5")
    mutant = deepcopy(model)
    if property_id == "S2":
        transition(mutant, "T04")["guard"] = "not suspect"
        data["events"] = data["events"][:skip] + [data["events"][36]]
    else:
        transition(mutant, "T02")["from"] = ["draft", "verified"]
        data["events"] = data["events"][:skip] + [data["events"][35]]
    result = replay(mutant, data)
    assert result["outcome"] == "completed", result["steps"][-1]
    assert property_id in {v["property"] for v in safety_violations(model, result["steps"])}


def test_old_release_review_does_not_authorize_new_release(model):
    data = scenario("wit5")
    data["events"] = data["events"][:38] + [data["events"][39]]
    mutant = deepcopy(model)
    transition(mutant, "W04")["from"] = ["ready", "reviewed"]
    result = replay(mutant, data)
    assert result["outcome"] == "completed"
    findings = safety_violations(model, result["steps"])
    assert findings == [{"property": "S8", "step": 39,
                         "detail": "Wydanie 2: brak wcześniejszego przeglądu R"}]


def test_review_by_author_is_not_independent(model):
    data = scenario()
    data["events"][27]["actor"] = "A"
    mutant = deepcopy(model)
    transition(mutant, "W02")["actor"] = "A"
    result = replay(mutant, data)
    assert result["outcome"] == "completed"
    assert {v["property"] for v in safety_violations(model, result["steps"])} == {"S8"}


@pytest.mark.parametrize("field,value", [("kind", "general"), ("about", "none"),
    ("about_version", "2"), ("requested_transition", "T05"), ("consumed", "true"),
    ("blocking", "false"), ("age", "2")])
def test_question_frame_preserves_every_authorization_field(model, field, value):
    data = scenario("wit3")
    data["events"] = data["events"][:30] + [{"transition": "P03", "actor": "U", "question": "q1"}]
    mutant = deepcopy(model)
    transition(mutant, "P03")["effects"] = [f"{field} := {value}"]
    result = replay(mutant, data)
    assert result["outcome"] == "completed", result["steps"][-1]
    assert {v["property"] for v in safety_violations(model, result["steps"])} == {"S11"}


@pytest.mark.parametrize("field,value", [("state", "baselined"), ("version", 99), ("suspect", True),
    ("depends_on", ["p1"]), ("predecessor", "p1")])
def test_snapshot_is_exact_not_only_a_version_map(model, field, value):
    steps = replay(model, scenario())["steps"]
    # Jednostkowy test wyroczni na uszkodzeniu wyniku; nie świadek osiągalności.
    snapshot = steps[-1]["after"]["releases"][1]["snapshot"]
    if snapshot["p1"][field] == value:
        value = "corrupted"
    snapshot["p1"][field] = value
    assert "S7b" in {v["property"] for v in safety_violations(model, steps)}


@pytest.mark.parametrize("field,value", [("state", "asked"), ("kind", "general"),
    ("resolution", "rejected"), ("about", "r2"), ("about_version", 2),
    ("requested_transition", "T07"), ("consumed", True)])
def test_authorization_checks_each_conjunct_independently(model, field, value):
    data = scenario("wit5")
    data["events"] = data["events"][:33]
    steps = replay(model, data)["steps"]
    # Jednostkowy test czytnika historii, bez twierdzenia o osiągalności
    # spreparowanej zgody. Mutanty wykonania są sprawdzane osobno powyżej.
    steps[-2]["after"]["questions"]["q1"][field] = value
    steps[-1]["before"]["questions"]["q1"][field] = value
    findings = safety_violations(model, steps)
    assert any(v["property"] == "S11" and v["step"] == 33 for v in findings)


def test_safety_module_does_not_import_execution_helpers():
    import ast
    source = (ROOT / "src/isomodel/safety.py").read_text()
    imports = [node for node in ast.walk(ast.parse(source)) if isinstance(node, (ast.Import, ast.ImportFrom))]
    assert len(imports) == 1
    assert imports[0].module == "copy"


def test_s7b_also_rejects_incomplete_products_at_acceptance(model):
    data = scenario()
    data["events"] = data["events"][:1] + [data["events"][-1]]
    mutant = deepcopy(model)
    transition(mutant, "W04")["from"] = ["in_preparation"]
    result = replay(mutant, data)
    assert result["outcome"] == "completed"
    assert "S7b" in {v["property"] for v in safety_violations(model, result["steps"])}
