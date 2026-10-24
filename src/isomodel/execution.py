"""Wykonanie instancji symulacyjnej; bez zapisu do repozytorium.

Trace: WIT1, S1, S2, S3, S4, S7a, S7b, S8, S10.
"""

from copy import deepcopy
import hashlib
import json
import re

from .expressions import InputError, UnsupportedSemantics, boolean, compile_expression, evaluate
from .loader import ModelError, validate_model


class StepRejected(ModelError):
    """Krok niedozwolony przez model albo brak dowodu."""

    def __init__(self, code, message, guard_result=None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.guard_result = guard_result


class ExplorationBoundary(ModelError):
    """Wyjście poza granice badania; nie zakleszczenie procesu."""


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def initial_state(model):
    validate_model(model)
    items = {}
    for ident, definition in model["test_instance"]["items"].items():
        values = {}
        for name, variable in model["item_variables"].items():
            if "initial" not in variable:
                raise UnsupportedSemantics(f"Brak inicjalizacji: item.{name}")
            values[name] = deepcopy(variable["initial"])
        items[ident] = deepcopy(definition) | values | {"id": ident}
    release = {}
    for name, variable in model["release_variables"].items():
        value = variable.get("initial")
        if value == "test_instance.release_scope":
            value = model["test_instance"]["release_scope"]
        elif value == "none":
            value = None
        elif isinstance(value, str) and value not in model["release_states"]:
            raise UnsupportedSemantics(f"Nieobsługiwana inicjalizacja release.{name}: {value}")
        release[name] = deepcopy(value)
    controls = model["release_control_variables"]
    if controls["releases"]["initial"] != "{1: initial release_variables}":
        raise UnsupportedSemantics("Nieobsługiwana inicjalizacja historii wydań")
    if release["number"] != 1 or controls["current_release"]["initial"] != 1:
        raise UnsupportedSemantics("Inicjalizacja historii wymaga zgodnego numeru 1")
    state = {"items": items, "questions": {}, "releases": {1: release}}
    for name, variable in controls.items():
        if name != "releases":
            state[name] = deepcopy(variable["initial"])
    return state


def _context(model, state, item, inputs, newly_suspect=()):
    release = state["releases"][state["current_release"]]
    environment = {s: s for kind in ("item", "question", "release") for s in model[f"{kind}_states"]}
    environment.update(model["parameters"])
    environment.update({k: state[k] for k in model["release_control_variables"]})
    environment.update({"none": "none", "release": release,
                        "all_items": list(state["items"].values()),
                        "all_questions": list(state["questions"].values()),
                        "newly_suspect": newly_suspect})
    if "tests_ok" in inputs:
        environment["tests_ok"] = boolean(inputs["tests_ok"])
    if item is not None:
        environment.update(item)
        environment["e"] = item

    def checks_ok(element):
        checks = inputs.get("checks_ok", {})
        if not isinstance(checks, dict) or element["id"] not in checks:
            raise InputError(f"Brak checks_ok dla {element['id']}")
        return boolean(checks[element["id"]])

    def snapshot(scope):
        keys = {"type", "depends_on"} | set(model["item_variables"])
        return {ident: {key: deepcopy(state["items"][ident][key]) for key in sorted(keys)} for ident in scope}

    functions = {
        "deps": lambda element: [state["items"][ident] for ident in element["depends_on"]],
        "type": lambda element: model["item_types"][element["type"]],
        "in_scope": lambda element: element["id"] in release["scope"],
        "checks_ok": checks_ok,
        "snapshot": snapshot,
    }
    return environment, functions


def _compile_effect(text, kind, model):
    match = re.fullmatch(r"([a-z_]+(?:\.[a-z_]+)?)\s*:=\s*(.+)", text)
    if match is None:
        raise UnsupportedSemantics(f"Nieobsługiwany skutek: {text}")
    target, expression = match.groups()
    if kind == "item" and target in model["item_variables"] and target != "state":
        path = ("item", target)
    elif kind == "release" and target in {"release.snapshot", "release.acceptance"}:
        path = ("release", target.split(".")[1])
    elif kind == "observer" and target == "next_release_required":
        path = ("control", target)
    else:
        raise UnsupportedSemantics(f"Nieobsługiwany cel przypisania: {target}")
    if expression == "record acceptance with release.number and user quote":
        if path != ("release", "acceptance"):
            raise UnsupportedSemantics("Protokół poza polem acceptance")
        return path, None
    return path, compile_expression(expression, model)


def _evidence_requirements(transition):
    description = transition.get("evidence")
    fields = set()
    if description == "DEC z cytatem użytkownika":
        fields |= {"decision", "quote"}
    elif description == "commit lub tag na polecenie użytkownika":
        fields |= {"reference", "quote"}
    elif description is not None:
        raise UnsupportedSemantics(f"Nieobsługiwany rodzaj dowodu: {description}")
    if any("record acceptance with release.number and user quote" in effect for effect in transition["effects"]):
        fields.add("quote")
    return fields


def _check_evidence(event, fields):
    evidence = event.get("evidence")
    if not fields and evidence is None:
        return
    if not isinstance(evidence, dict) or evidence.get("simulation") is not True:
        raise StepRejected("evidence", "Wymagany jawny dowód demonstracyjny (simulation: true)", True)
    if set(evidence) - {"simulation", "decision", "reference", "quote"}:
        raise StepRejected("evidence", "Nieznane pola dowodu", True)
    for field in fields:
        if not isinstance(evidence.get(field), str) or not evidence[field].strip():
            raise StepRejected("evidence", f"Brak {field}", True)


def _apply_effects(effects, model, state, item, inputs, event, newly_suspect=()):
    for (kind, field), expression in effects:
        release = state["releases"][state["current_release"]]
        if expression is None:
            value = {"number": release["number"], "quote": event["evidence"]["quote"]}
        else:
            value = evaluate(expression, *_context(model, state, item, inputs, newly_suspect))
        target = {"item": item, "release": release, "control": state}[kind]
        target[field] = deepcopy(value)


def _check_bounds(model, state):
    bounds = model["test_instance"]["bounds"]
    if any(item["version"] > bounds["max_version"] for item in state["items"].values()):
        raise ExplorationBoundary("Przekroczono max_version")
    if len(state["releases"]) > bounds["max_releases"] or len(state["questions"]) > bounds["max_questions"]:
        raise ExplorationBoundary("Przekroczono granicę liczby wydań lub pytań")


def execute_step(model, state, event, inputs):
    """Czysta operacja: zwraca kopie przed/po; błąd nie zmienia argumentów.

    Czyta from/to/actor/guard/effects, bez dyspozytora po ID przejść.
    Stan wejściowy w testach warunków może być wstrzyknięty: to nie dowód
    jego osiągalności. Odtwarzanie scenariusza zawsze zaczyna od initial_state.
    """
    if not isinstance(event, dict) or set(event) - {"transition", "actor", "item", "evidence"}:
        raise InputError("Niepoprawne lub nieznane pola zdarzenia")
    if not isinstance(inputs, dict) or set(inputs) - {"checks_ok", "tests_ok"}:
        raise InputError("Niepoprawne lub nieznane dane wejściowe")
    matches = [(kind, t) for kind in ("item", "question", "release")
               for t in model[f"{kind}_transitions"] if t["id"] == event.get("transition")]
    if len(matches) != 1:
        raise InputError("Nieznane lub niejednoznaczne przejście")
    kind, transition = matches[0]
    if kind == "question" or transition.get("target") == "new_release":
        raise UnsupportedSemantics("Pytania i otwieranie kolejnych wydań są poza przyrostem WIT1")
    # Wstępna kompilacja CAŁEGO kroku przed oceną warunku i zapisem.
    guard = compile_expression(transition["guard"], model)
    effects = [_compile_effect(text, kind, model) for text in transition["effects"]]
    fields = _evidence_requirements(transition)
    observers = [(compile_expression(o["guard"], model),
                  [_compile_effect(text, "observer", model) for text in o["effects"]])
                 for o in model["post_step_effects"]]
    actors = transition["actor"]
    if event.get("actor") not in ([actors] if isinstance(actors, str) else actors):
        raise StepRejected("actor", "Aktor nie jest uprawniony do tego przejścia")
    if state["next_release_required"]:
        raise StepRejected("pending_release", "Najpierw wymagane otwarcie następnego wydania")
    if not state["releases"][state["current_release"]]["scope"]:
        raise UnsupportedSemantics("Pusty zakres wydania jest poza przyrostem WIT1")
    if kind == "item":
        if event.get("item") not in state["items"]:
            raise InputError("Brak lub nieznany element")
        item = state["items"][event["item"]]
        subject = item
    else:
        if "item" in event:
            raise InputError("Przejście wydania nie przyjmuje elementu")
        item = None
        subject = state["releases"][state["current_release"]]
    if subject["state"] not in transition["from"]:
        raise StepRejected("state", f"Przejście niedozwolone ze stanu {subject['state']}")
    if not boolean(evaluate(guard, *_context(model, state, item, inputs))):
        raise StepRejected("guard", "Warunek przejścia niespełniony", False)
    _check_evidence(event, fields)
    candidate = deepcopy(state)
    target_item = candidate["items"][event["item"]] if kind == "item" else None
    target = target_item if kind == "item" else candidate["releases"][candidate["current_release"]]
    if transition["to"] != "=":
        target["state"] = transition["to"]
    _apply_effects(effects, model, candidate, target_item, inputs, event)
    newly_suspect = [item for ident, item in candidate["items"].items()
                     if item["suspect"] and not state["items"][ident]["suspect"]]
    for observer_guard, observer_effects in observers:
        if boolean(evaluate(observer_guard, *_context(model, candidate, target_item, inputs, newly_suspect))):
            _apply_effects(observer_effects, model, candidate, target_item, inputs, event, newly_suspect)
    _check_bounds(model, candidate)
    return {"event": deepcopy(event), "kind": kind, "guard": transition["guard"],
            "guard_result": True, "outcome": "applied", "before": deepcopy(state), "after": candidate}


def replay(model, scenario):
    """Wykonuje tylko symulacje, zatrzymuje się na pierwszym błędzie/odmowie."""
    if not isinstance(scenario, dict) or scenario.get("simulation") is not True:
        raise InputError("Wymagany scenariusz symulacyjny (simulation: true)")
    if set(scenario) - {"id", "simulation", "description", "inputs", "events"}:
        raise InputError("Nieznane pola scenariusza")
    if not isinstance(scenario.get("events"), list) or not scenario["events"]:
        raise InputError("Scenariusz wymaga niepustej listy zdarzeń")
    state = initial_state(model)
    result = {"scenario": scenario.get("id"), "simulation": True, "model_version": model["version"],
              "model_sha256": fingerprint(model), "scenario_sha256": fingerprint(scenario),
              "inputs": deepcopy(scenario.get("inputs", {})), "steps": [], "outcome": "completed"}
    for index, event in enumerate(scenario["events"], 1):
        try:
            record = execute_step(model, state, event, scenario.get("inputs", {}))
        except ModelError as error:
            rejected = isinstance(error, StepRejected)
            code = error.code if rejected else (
                "unsupported" if isinstance(error, UnsupportedSemantics) else
                "boundary" if isinstance(error, ExplorationBoundary) else "input")
            record = {"event": deepcopy(event), "before": deepcopy(state), "after": deepcopy(state),
                      "outcome": "rejected" if rejected else "error", "code": code, "reason": str(error),
                      "guard_result": error.guard_result if rejected else None}
            result["outcome"] = record["outcome"]
        record["step"] = index
        result["steps"].append(record)
        state = deepcopy(record["after"])
        if record["outcome"] != "applied":
            break
    result["final_state"] = deepcopy(state)
    return result
