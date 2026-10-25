"""Wczytywanie YAML i walidacja słownika; bez interpretacji guard/effects.

Trace: G0, G4.
"""

from pathlib import Path
import re

import yaml


class ModelError(ValueError):
    """Niepoprawne lub nieobsługiwane dane modelu."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Nie pozwala, aby YAML cicho nadpisał wcześniejszą definicję."""


def _construct_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, (str, int, float, bool, type(None))):
            raise ModelError("G0: klucz YAML musi być skalarem")
        if key in result:
            raise ModelError(f"G0: Powtórzony klucz YAML: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


KINDS = ("item", "question", "release")
SECTIONS = {
    "model", "version", "status", "notation", "parameters", "actors", "item_types",
    "release_control_variables", "release_semantics", "question_semantics", "helper_effects", "post_step_effects", "test_instance",
} | {f"{kind}_{suffix}" for kind in KINDS for suffix in ("states", "variables", "transitions")}


def _require(condition, message):
    if not condition:
        raise ModelError(message)


def load_model(path):
    try:
        data = yaml.load(Path(path).read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except yaml.YAMLError as error:
        raise ModelError(f"G0: niepoprawny YAML: {error}") from error
    return validate_model(data)


def validate_model(data):
    _require(isinstance(data, dict), "G0: model musi być mapą")
    _require(set(data) == SECTIONS, f"G0: brakujące sekcje {SECTIONS - data.keys()}, nieznane {data.keys() - SECTIONS}")
    for section in SECTIONS - {"model", "version", "status", "post_step_effects", *(f"{kind}_transitions" for kind in KINDS)}:
        _require(isinstance(data[section], dict), f"G0: {section} musi być mapą")
    actors = data["actors"]
    all_states = set().union(*(data[f"{kind}_states"] for kind in KINDS))
    identifiers = set()
    for kind in KINDS:
        states = data[f"{kind}_states"]
        _require(bool(states), f"G0: brak stanów {kind}")
        for name, definition in states.items():
            _require(isinstance(definition, dict) and type(definition.get("final")) is bool, f"G0: {kind}.{name}: brak flagi final")
            if kind == "item":
                _require(isinstance(definition.get("iso"), list) and bool(definition["iso"]), f"G0: {name}: brak stanów ISO")
        state_variable = data[f"{kind}_variables"].get("state", {})
        _require(isinstance(state_variable, dict), f"G0: {kind}.state: błędna zmienna")
        _require(state_variable.get("type") == f"{kind}_states", f"G0: {kind}.state: błędny typ")
        _require(state_variable.get("initial") in set(states) | {"none"}, f"G0: {kind}.state: nieznany stan początkowy")
        transitions = data[f"{kind}_transitions"]
        _require(isinstance(transitions, list), f"G0: przejścia {kind} muszą być listą")
        for transition in transitions:
            _require(isinstance(transition, dict), "G0: przejście musi być mapą")
            required = {"id", "name", "from", "to", "actor", "guard", "effects"}
            _require(required <= transition.keys(), "G0: niepełna definicja przejścia")
            allowed = required | {"iso", "description", "evidence", "interpretation", "target", "arguments"}
            _require(transition.keys() <= allowed, f"G0: nieznane pola przejścia {transition.keys() - allowed}")
            arguments = transition.get("arguments", {})
            _require(isinstance(arguments, dict), "G0: arguments musi być mapą")
            bindings = set()
            for name, argument in arguments.items():
                _require(isinstance(name, str) and name.isidentifier(), "G0: błędna nazwa argumentu")
                _require(name not in {"transition", "actor", "question", "attributes", "evidence", "inputs"}, "G0: zastrzeżona nazwa argumentu")
                _require(isinstance(argument, dict) and {"bind", "type"} <= argument.keys()
                         and argument.keys() <= {"bind", "type", "default"}, "G0: niepełny lub nieznany argument")
                binding = argument["bind"]
                _require(isinstance(binding, str) and binding.isidentifier() and binding not in bindings,
                         "G0: niepoprawne lub powtórzone wiązanie argumentu")
                bindings.add(binding)
                _require(argument["type"] in {"item", "optional_item_id"}, "G0: nieznany typ argumentu")
                _require("default" not in argument or argument["type"] == "optional_item_id" and argument["default"] == "none",
                         "G0: błędna wartość domyślna argumentu")
            ident = transition["id"]
            _require(isinstance(ident, str), "G0: ID musi być tekstem")
            _require(ident not in identifiers, f"G4: powtórzone ID {ident}")
            identifiers.add(ident)
            sources = transition["from"]
            _require(isinstance(sources, list) and bool(sources) and all(isinstance(s, str) for s in sources), f"G0: {ident}: błędne from")
            _require(set(sources) <= set(states) | {"none"}, f"G0: {ident}: nieznany stan źródłowy")
            destination = transition["to"]
            _require(isinstance(destination, str), f"G4: {ident}: cel nie jest pojedynczym stanem")
            _require(destination in set(states) | {"="}, f"G0: {ident}: nieznany stan docelowy")
            assigned = transition["actor"]
            assigned = [assigned] if isinstance(assigned, str) else assigned
            _require(isinstance(assigned, list) and bool(assigned) and all(isinstance(a, str) for a in assigned), f"G0: {ident}: błędny aktor")
            _require(set(assigned) <= actors.keys(), f"G0: {ident}: nieznany aktor")
            _require(isinstance(transition["guard"], str), f"G0: {ident}: warunek musi być tekstem")
            _require(isinstance(transition["effects"], list) and all(isinstance(e, str) for e in transition["effects"]), f"G0: {ident}: skutki muszą być listą tekstów")
            for group in re.findall(r"\{([a-z_, ]+)\}", transition["guard"]):
                _require(set(re.split(r",\s*", group.strip())) <= all_states, f"G0: {ident}: nieznany stan w warunku")
            target = transition.get("target", "current_release")
            _require(target in {"current_release", "new_release"}, f"G0: {ident}: nieznany rodzaj celu")
            _require(target != "new_release" or kind == "release", f"G0: {ident}: nowe wydanie poza automatem wydań")
            if "iso" in transition:
                _require(isinstance(transition["iso"], list) and all(isinstance(ref, str) for ref in transition["iso"]), f"G0: {ident}: błędne odwołania ISO")
    items = data["test_instance"].get("items")
    _require(isinstance(items, dict) and bool(items), "G0: brak elementów instancji")
    for ident, item in items.items():
        _require(isinstance(item, dict) and isinstance(item.get("type"), str) and item["type"] in data["item_types"], f"G0: {ident}: nieznany typ")
        dependencies = item.get("depends_on")
        _require(isinstance(dependencies, list) and all(isinstance(dep, str) for dep in dependencies), f"G0: {ident}: błędne zależności")
        _require(set(dependencies) <= items.keys(), f"G0: {ident}: nieznana zależność")
    scope = data["test_instance"].get("release_scope")
    _require(isinstance(scope, list) and all(isinstance(i, str) for i in scope) and set(scope) <= items.keys(), "G0: nieznany element zakresu")
    return data
