"""Wykonanie instancji symulacyjnej; bez zapisu do repozytorium.

Trace: WIT1, WIT2, WIT4, WIT5, S11, S1, S2, S3, S4, S7a, S7b, S8, S9, S10, L2, L4.
"""

from copy import deepcopy
import hashlib
import json
import re

from .dependencies import acyclic_dependencies, dependency_types_ok
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
            value = variable["initial"]
            if value == "test_instance.items[e.id].depends_on":
                value = definition["depends_on"]
            values[name] = deepcopy(value)
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


def _context(model, state, item, inputs, newly_suspect=(), question=None, transition=None, local=None, bindings=None):
    release = state["releases"][state["current_release"]]
    environment = {s: s for kind in ("item", "question", "release") for s in model[f"{kind}_states"]}
    environment.update(model["parameters"])
    environment.update({v: v for var in model["question_variables"].values() for v in var.get("values", [])})
    environment.update({t["id"]: t["id"] for kind in ("item", "question", "release") for t in model[f"{kind}_transitions"]})
    environment["transition"] = {"id": transition}
    environment.update({k: state[k] for k in model["release_control_variables"]})
    environment.update({"none": "none", "release": release, "blocking_first": "blocking_first",
                        "all_items": list(state["items"].values()),
                        "all_questions": list(state["questions"].values()),
                        "newly_suspect": newly_suspect})
    for name in ("tests_ok", "unambiguous_answer"):
        if name in inputs:
            environment[name] = boolean(inputs[name])
    if item is not None:
        environment.update(item)
        environment["e"] = item
    if question is not None:
        if item is None:
            environment.update(question)
        environment["q"] = question
    environment.update(local or {})
    # Rekordy argumentów odczytujemy z bieżącej kopii, nie ze stanu wejściowego.
    environment.update({name: state["items"][value["id"]] if isinstance(value, dict) else value
                        for name, value in (bindings or {}).items()})

    def checks_ok(element):
        checks = inputs.get("checks_ok", {})
        if not isinstance(checks, dict) or element["id"] not in checks:
            raise InputError(f"Brak checks_ok dla {element['id']}")
        return boolean(checks[element["id"]])

    def snapshot(scope):
        keys = {"type", "depends_on"} | set(model["item_variables"])
        return {ident: {key: deepcopy(state["items"][ident][key]) for key in sorted(keys)} for ident in scope}

    def select_question(question_state, priority, newest=False):
        if priority != "blocking_first":
            raise UnsupportedSemantics(f"Nieobsługiwana kolejność pytań: {priority}")
        candidates = [q for q in state["questions"].values() if q["state"] == question_state]
        # Age jest kolejnością zgłoszenia, nie czasem spędzonym w stanie open.
        return min(candidates, key=lambda q: (not q["blocking"], -q["age"] if newest else q["age"]), default=None)

    def authorized_change(q, element):
        expression = model["question_semantics"]["authorized_change"]
        if "authorized_change" in expression:
            raise UnsupportedSemantics("Rekurencyjna definicja zgody")
        return evaluate(compile_expression(expression, model), environment | {"q": q, "e": element}, functions)

    def answer_resolution(q):
        answer = inputs.get("resolution")
        if q["kind"] == "general":
            if answer is not None and answer != "answered":
                raise InputError("Pytanie general dopuszcza tylko answered")
            return "answered"
        if q["kind"] != "change" or answer not in ("approved", "rejected"):
            raise InputError("Pytanie change wymaga wyniku approved albo rejected")
        return answer

    def lookup_item(ident):
        if ident == "none":
            return {"id": "none", "state": "none", "type": "none", "depends_on": [],
                    "predecessor": "none", "suspect": False}
        if not isinstance(ident, str) or ident not in state["items"]:
            raise InputError("Nieznane ID elementu")
        return state["items"][ident]

    functions = {
        "item": lookup_item,
        "predecessor": lambda element: lookup_item(element["predecessor"]),
        "dependency_types_ok": lambda element, ids: dependency_types_ok(model, state, element, ids),
        "acyclic_dependencies": lambda element, ids: acyclic_dependencies(state, element, ids),
        "authorized_change": authorized_change,
        "answer_resolution": answer_resolution,
        "copy": deepcopy,
        "dependents": lambda element: _dependents(state, element),
        "deps": lambda element: [state["items"][ident] for ident in element["depends_on"]],
        "type": lambda element: model["item_types"][element["type"]],
        "in_scope": lambda element: element["id"] in release["scope"],
        "checks_ok": checks_ok,
        "snapshot": snapshot,
        "count": lambda question_state: sum(q["state"] == question_state for q in state["questions"].values()),
        "oldest": select_question,
        "newest": lambda question_state, priority: select_question(question_state, priority, newest=True),
    }
    return environment, functions


def _dependents(state, element):
    reached = {element["id"]}
    pending = [element["id"]]
    while pending:
        dependency = pending.pop()
        for ident, candidate in state["items"].items():
            if ident not in reached and dependency in candidate["depends_on"]:
                reached.add(ident)
                pending.append(ident)
    return [candidate for ident, candidate in state["items"].items() if ident in reached and ident != element["id"]]


def _compile_effect(text, kind, model):
    if text == "invalidate_release(e)" and kind == "item":
        expected = "jeśli in_scope(e) i release.state in {ready, reviewed}: release.state := in_preparation; jeśli in_scope(e) i release.state = accepted: next_release_required := true, bez zmiany odebranego rekordu"
        if model["helper_effects"].get(text) != expected:
            raise UnsupportedSemantics("Nieobsługiwana definicja invalidate_release")
        return ("invalidate", None), None
    if text.startswith(("forall d in dependents(e): ", "forall d in pre_dependents(e): ")) and kind == "item":
        match = re.fullmatch(r"forall d in (dependents|pre_dependents)\(e\): d\.([a-z_]+) := (.+)", text)
        if not match or match[2] not in model["item_variables"] or match[2] == "state":
            raise UnsupportedSemantics("Nieobsługiwany skutek dla zależnych")
        return (match[1], match[2]), compile_expression(match[3], model)
    if text.startswith("create question(") and text.endswith(")") and kind == "item":
        fields = {}
        for entry in text[len("create question("):-1].split(","):
            match = re.fullmatch(r"\s*([a-z_]+) = (.+)", entry)
            if not match or match[1] not in model["question_variables"] or match[1] in fields:
                raise UnsupportedSemantics("Nieznane/powtórzone pole tworzonego pytania")
            fields[match[1]] = compile_expression(match[2], model)
        return ("create_question", None), fields
    history = re.fullmatch(r"releases\[(.+)\] := (.+)", text)
    if history and kind == "release":
        return ("history", compile_expression(history[1], model)), compile_expression(history[2], model)

    if text == "record DEC with user quote" and kind == "question":
        return ("record", "decision"), None
    match = re.fullmatch(r"([a-z_]+(?:\.[a-z_]+)?)\s*:=\s*(.+)", text)
    if match is None:
        raise UnsupportedSemantics(f"Nieobsługiwany skutek: {text}")
    target, expression = match.groups()
    if target.startswith("q.") and kind in {"item", "question"} and target[2:] in model["question_variables"] and target != "q.state":
        path = ("question", target[2:])
    elif kind == "release" and target == "n":
        path = ("local", "n")
    elif kind == "release" and target in {"current_release", "next_release_required"}:
        path = ("control", target)
    elif kind == "item" and target in model["item_variables"] and target != "state":
        path = ("item", target)
    elif kind == "question" and target in model["question_variables"] and target != "state":
        path = ("question", target)
    elif kind == "release" and target in {"release.snapshot", "release.acceptance", "release.state", "release.scope"}:
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
    elif description == "wpis w kolumnie Przejrzane decyzji, która wywołała zmianę; decyzja agenta do podważenia":
        fields |= {"decision", "reference"}
    elif description == "wpis agenta: element, stara i nowa zależność oraz odwołanie do przeglądu":
        fields |= {"decision", "reference"}
    elif description is not None:
        raise UnsupportedSemantics(f"Nieobsługiwany rodzaj dowodu: {description}")
    if any("record acceptance with release.number and user quote" in effect for effect in transition["effects"]):
        fields.add("quote")
    if "record DEC with user quote" in transition["effects"]:
        fields |= {"decision", "quote"}
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


def _apply_effects(effects, model, state, item, inputs, event, newly_suspect=(), question=None, records=None, bindings=None, pre_state=None):
    local = {}
    for (kind, field), expression in effects:
        context = _context(model, state, item, inputs, newly_suspect, question, event["transition"], local, bindings)
        release = state["releases"][state["current_release"]]
        if kind == "record":
            evidence = event["evidence"]
            entry = {"kind": field, "id": evidence["decision"], "question": question["id"],
                     "quote": evidence["quote"], "simulation": True}
            entry.update({key: deepcopy(question[key]) for key in ("resolution", "about", "about_version", "requested_transition")})
            records.append(entry)
            continue
        if kind == "invalidate":
            if item["id"] in release["scope"]:
                if release["state"] in {"ready", "reviewed"}:
                    release["state"] = "in_preparation"
                elif release["state"] == "accepted":
                    state["next_release_required"] = True
            continue
        if kind in {"dependents", "pre_dependents"}:
            source = pre_state if kind == "pre_dependents" else state
            if source is None:
                raise UnsupportedSemantics("Brak stanu przed krokiem dla pre_dependents")
            for dependent in _dependents(source, item):
                state["items"][dependent["id"]][field] = deepcopy(evaluate(expression, *context))
            continue
        if kind == "create_question":
            values = {key: evaluate(value, *context) for key, value in expression.items()}
            ident = event.get("question")
            if not isinstance(ident, str) or not ident.strip() or ident in state["questions"]:
                raise InputError("Tworzenie pytania wymaga nowego, niepustego ID")
            attributes = {key: value for key, value in values.items() if key in {"kind", "about", "requested_transition", "blocking"}}
            created = _question_subject(model, state, {"question": ident, "attributes": attributes},
                                        {"from": [model["question_variables"]["state"]["initial"]]})
            # Pozostałe pola tworzone przez skutek muszą zgadzać się z inicjalizacją.
            if any(created[key] != value for key, value in values.items()):
                raise InputError("Niespójna inicjalizacja pytania przez skutek")
            created["state"] = "open"
            state["questions"][ident] = created
            continue
        if expression is None:
            value = {"number": release["number"], "quote": event["evidence"]["quote"]}
        else:
            value = evaluate(expression, *context)
        if kind == "history":
            index = evaluate(field, *context)
            if type(index) is not int or index < 1 or index in state["releases"]:
                raise InputError("Nowy rekord wymaga wolnego dodatniego numeru")
            if not isinstance(value, dict) or set(value) != set(model["release_variables"]) or value["number"] != index:
                raise InputError("Niekompletny lub niespójny rekord wydania")
            value = {k: None if v == "none" else v for k, v in value.items()}
            state["releases"][index] = deepcopy(value)
            continue
        target = {"item": item, "question": question, "release": release, "control": state, "local": local}[kind]
        if target is None:
            raise InputError("Skutek wymaga wskazania pytania lub elementu")
        target[field] = deepcopy(value)


def _question_subject(model, state, event, transition):
    ident = event.get("question")
    if not isinstance(ident, str) or not ident.strip():
        raise InputError("Brak lub niepoprawne ID pytania")
    ages = []
    for q in state["questions"].values():
        if type(q.get("age")) is not int or q["age"] < 1 or type(q.get("blocking")) is not bool:
            raise InputError("Pytania wymagają dodatniego age i logicznego blocking")
        ages.append(q["age"])
    if len(set(ages)) != len(ages):
        raise InputError("Kolejność zgłoszenia pytań musi być jednoznaczna")
    if ident in state["questions"]:
        if "attributes" in event:
            raise InputError("Nie można nadpisać atrybutów istniejącego pytania")
        return state["questions"][ident]
    initial = model["question_variables"]["state"]["initial"]
    if initial not in transition["from"]:
        raise InputError("Nieznane pytanie; wymagane wcześniejsze zgłoszenie")
    attributes = event.get("attributes", {})
    if not isinstance(attributes, dict) or set(attributes) - {"blocking", "kind", "about", "requested_transition"}:
        raise InputError("Nieznane atrybuty nowego pytania")
    result = {"id": ident}
    for name, variable in model["question_variables"].items():
        if "initial" in variable:
            result[name] = deepcopy(variable["initial"])
        elif name == "age":
            result[name] = max(ages, default=0) + 1
        elif name == "blocking":
            if name not in attributes:
                raise InputError("Zgłoszenie pytania wymaga blocking")
            result[name] = boolean(attributes[name])
        else:
            raise UnsupportedSemantics(f"Brak inicjalizacji pytania: {name}")
    result["kind"] = attributes.get("kind", result["kind"])
    if result["kind"] not in model["question_variables"]["kind"]["values"]:
        raise InputError("Nieznany rodzaj pytania")
    if result["kind"] == "change":
        about = attributes.get("about")
        operation = attributes.get("requested_transition")
        if not isinstance(about, str) or about not in state["items"] or state["items"][about]["state"] == "none":
            raise InputError("Wniosek o zmianę wymaga istniejącego elementu")
        if operation not in model["question_semantics"]["change_operations"] or result["blocking"] is not True:
            raise InputError("Wniosek o zmianę wymaga obsługiwanej operacji i blocking=true")
        result.update(about=about, about_version=state["items"][about]["version"], requested_transition=operation)
    elif "about" in attributes or "requested_transition" in attributes:
        raise InputError("Pytanie general nie przyjmuje powiązania")
    return result


def _check_bounds(model, state):
    bounds = model["test_instance"]["bounds"]
    if any(item["version"] > bounds["max_version"] for item in state["items"].values()):
        raise ExplorationBoundary("Przekroczono max_version")
    if len(state["releases"]) > bounds["max_releases"] or len(state["questions"]) > bounds["max_questions"]:
        raise ExplorationBoundary("Przekroczono granicę liczby wydań lub pytań")


def _bind_arguments(transition, event, state):
    bindings = {}
    for field, definition in transition.get("arguments", {}).items():
        if field not in event and "default" not in definition:
            raise InputError(f"Brak argumentu: {field}")
        value = event.get(field, definition.get("default"))
        if not isinstance(value, str) or (value not in state["items"] and not (
                definition["type"] == "optional_item_id" and value == "none")):
            raise InputError(f"Niepoprawny argument: {field}")
        bindings[definition["bind"]] = state["items"][value] if definition["type"] == "item" else value
    return bindings


def execute_step(model, state, event, inputs):
    """Czysta operacja: zwraca kopie przed/po; błąd nie zmienia argumentów.

    Czyta from/to/actor/guard/effects, bez dyspozytora po ID przejść.
    Stan wejściowy w testach warunków może być wstrzyknięty: to nie dowód
    jego osiągalności. Odtwarzanie scenariusza zawsze zaczyna od initial_state.
    """
    if not isinstance(event, dict):
        raise InputError("Niepoprawne lub nieznane pola zdarzenia")
    step_inputs = event.get("inputs", {})
    for values in (inputs, step_inputs):
        if not isinstance(values, dict) or set(values) - {"checks_ok", "tests_ok", "unambiguous_answer", "resolution"}:
            raise InputError("Niepoprawne lub nieznane dane wejściowe")
    inputs = inputs | step_inputs  # Dane odpowiedzi nie przechodzą do następnego zdarzenia.
    matches = [(kind, t) for kind in ("item", "question", "release")
               for t in model[f"{kind}_transitions"] if t["id"] == event.get("transition")]
    if len(matches) != 1:
        raise InputError("Nieznane lub niejednoznaczne przejście")
    kind, transition = matches[0]
    allowed_fields = {"transition", "actor", "item", "question", "attributes", "evidence", "inputs"} | set(transition.get("arguments", {}))
    if set(event) - allowed_fields:
        raise InputError("Nieznane pola zdarzenia dla tego przejścia")
    new_release = transition.get("target") == "new_release"
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
    if state["next_release_required"] and not new_release:
        raise StepRejected("pending_release", "Najpierw wymagane otwarcie następnego wydania")
    if not state["releases"][state["current_release"]]["scope"]:
        raise UnsupportedSemantics("Pusty zakres wydania jest poza przyrostem WIT1")
    creates_question = any(path[0] == "create_question" for path, _ in effects)
    uses_question = "authorized_change(" in transition["guard"] or any(path[0] == "question" for path, _ in effects)
    if kind != "question" and "attributes" in event:
        raise InputError("Atrybuty pytania poza zgłoszeniem P00")
    if kind != "question" and "question" in event and not (kind == "item" and (uses_question or creates_question)):
        raise InputError("Pytanie poza operacją korzystającą z pytania")
    bindings = _bind_arguments(transition, event, state)
    subject_question = None
    if kind == "question":
        if "item" in event:
            raise InputError("Przejście pytania nie przyjmuje elementu")
        subject_question = _question_subject(model, state, event, transition)
        item = None
        subject = subject_question
    elif kind == "item":
        if event.get("item") not in state["items"]:
            raise InputError("Brak lub nieznany element")
        item = state["items"][event["item"]]
        subject = item
        if uses_question:
            ident = event.get("question")
            if not isinstance(ident, str) or ident not in state["questions"]:
                raise InputError("Operacja wymaga wskazania istniejącej zgody")
            subject_question = state["questions"][ident]
    else:
        if "item" in event and "item" not in transition.get("arguments", {}):
            raise InputError("Przejście wydania nie przyjmuje elementu")
        item = bindings.get("e")
        subject = state["releases"][state["current_release"]]
    if subject["state"] not in transition["from"]:
        raise StepRejected("state", f"Przejście niedozwolone ze stanu {subject['state']}")
    if not boolean(evaluate(guard, *_context(model, state, item, inputs, question=subject_question, transition=transition["id"], bindings=bindings))):
        raise StepRejected("guard", "Warunek przejścia niespełniony", False)
    _check_evidence(event, fields)
    candidate = deepcopy(state)
    target_item = candidate["items"][item["id"]] if item is not None else None
    target_question = None
    if kind == "question":
        candidate["questions"][event["question"]] = deepcopy(subject_question)
        target_question = candidate["questions"][event["question"]]
    elif subject_question is not None:
        target_question = candidate["questions"][subject_question["id"]]
    target = {"item": target_item, "question": target_question,
              "release": candidate["releases"][candidate["current_release"]]}[kind]
    if transition["to"] != "=" and not new_release:
        target["state"] = transition["to"]
    records = []
    _apply_effects(effects, model, candidate, target_item, inputs, event, question=target_question, records=records, bindings=bindings, pre_state=state)
    newly_suspect = [item for ident, item in candidate["items"].items()
                     if item["suspect"] and not state["items"][ident]["suspect"]]
    for observer_guard, observer_effects in observers:
        if boolean(evaluate(observer_guard, *_context(model, candidate, target_item, inputs, newly_suspect, target_question))):
            _apply_effects(observer_effects, model, candidate, target_item, inputs, event, newly_suspect, target_question, records)
    _check_bounds(model, candidate)
    return {"event": deepcopy(event), "kind": kind, "guard": transition["guard"],
            "guard_result": True, "outcome": "applied", "before": deepcopy(state), "after": candidate,
            "inputs": deepcopy(inputs), "records": deepcopy(records)}


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
              "inputs": deepcopy(scenario.get("inputs", {})), "steps": [], "records": [], "outcome": "completed"}
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
                      "guard_result": error.guard_result if rejected else None, "records": []}
            result["outcome"] = record["outcome"]
        record["step"] = index
        result["steps"].append(record)
        result["records"].extend(dict(deepcopy(entry), step=index) for entry in record["records"])
        state = deepcopy(record["after"])
        if record["outcome"] != "applied":
            break
    result["final_state"] = deepcopy(state)
    return result
