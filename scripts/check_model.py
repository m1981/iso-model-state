"""Sprawdzenie spójności danych E1; nie jest symulatorem ani dowodem G/S/L.

Uruchomienie: uv run --with pyyaml python scripts/check_model.py
Trace: DEC-PRO-003, G0 (część strukturalna).
"""

import re
from pathlib import Path

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    """Odrzuca powtórzone klucze zamiast cicho nadpisywać ich wartości."""


def construct_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"Powtórzony klucz YAML: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
)


def main():
    root = Path(__file__).resolve().parents[1]
    model = yaml.load((root / "model/process.yaml").read_text(), Loader=UniqueKeyLoader)
    errors = []
    checks = 0

    def check(condition, message):
        nonlocal checks
        checks += 1
        if not condition:
            errors.append(message)

    transitions = {}
    actors = set(model["actors"])
    all_states = set().union(*(model[f"{kind}_states"] for kind in ("item", "question", "release")))
    for kind in ("item", "question", "release"):
        states = set(model[f"{kind}_states"])
        for transition in model[f"{kind}_transitions"]:
            ident = transition["id"]
            check(ident not in transitions, f"Powtórzone ID: {ident}")
            transitions[ident] = transition
            check(isinstance(transition["from"], list), f"{ident}: from nie jest listą")
            check(set(transition["from"]) <= states | {"none"}, f"{ident}: nieznany stan źródłowy")
            check(isinstance(transition["to"], str) and transition["to"] in states | {"="}, f"{ident}: błędny cel")
            assigned = transition["actor"]
            assigned = assigned if isinstance(assigned, list) else [assigned]
            check(set(assigned) <= actors, f"{ident}: nieznany aktor")
            check(isinstance(transition["guard"], str), f"{ident}: warunek nie jest tekstem")
            check(isinstance(transition["effects"], list), f"{ident}: skutki nie są listą")
            for state_set in re.findall(r"\{([a-z_, ]+)\}", transition["guard"]):
                check(set(re.split(r",\s*", state_set.strip())) <= all_states, f"{ident}: nieznane stany w warunku")
            check(transition.get("target", "current_release") in {"current_release", "new_release"}, f"{ident}: nieznany rodzaj celu")
            check(transition.get("target") != "new_release" or ident == "W06", f"{ident}: nieoczekiwane tworzenie wydania")

    for name, state in model["item_states"].items():
        check(bool(state.get("iso")), f"Stan {name}: brak mapowania ISO")
    for name, item_type in model["item_types"].items():
        check(set(item_type["depends_on"]) <= model["item_types"].keys(), f"Typ {name}: nieznane zależności")
    items = model["test_instance"]["items"]
    for ident, item in items.items():
        check(item["type"] in model["item_types"], f"{ident}: nieznany typ")
        check(set(item["depends_on"]) <= items.keys(), f"{ident}: nieznane zależności")
        if item["type"] in model["item_types"] and set(item["depends_on"]) <= items.keys():
            dependency_types = {items[dep]["type"] for dep in item["depends_on"]}
            check(dependency_types == set(model["item_types"][item["type"]]["depends_on"]), f"{ident}: zależności nie odpowiadają typowi")
    for ident in items:
        pending = list(items[ident]["depends_on"])
        seen = set()
        while pending:
            dependency = pending.pop()
            if dependency not in seen and dependency in items:
                seen.add(dependency)
                pending.extend(items[dependency]["depends_on"])
        check(ident not in seen, f"{ident}: cykl zależności")
    check(set(model["test_instance"]["release_scope"]) <= items.keys(), "Zakres zawiera nieznane elementy")

    for kind in ("item", "question", "release"):
        state_variable = model[f"{kind}_variables"]["state"]
        check(state_variable["type"] == f"{kind}_states", f"{kind}: błędny typ zmiennej state")
        check(state_variable["initial"] in set(model[f"{kind}_states"]) | {"none"}, f"{kind}: błędny stan początkowy")
    variables = model["release_variables"]
    control = model["release_control_variables"]
    check(set(variables) == {"number", "state", "scope", "snapshot", "acceptance"}, "Niezgodny słownik pól wydania")
    check(set(control) == {"releases", "current_release", "next_release_required"}, "Niezgodny słownik sterowania wydaniami")
    check(variables["number"]["initial"] == control["current_release"]["initial"] == 1, "Błędny początkowy numer wydania")
    check(control["next_release_required"]["initial"] is False, "Znacznik oczekującej zmiany nie jest początkowo false")
    check(variables["snapshot"]["initial"] == variables["acceptance"]["initial"] == "none", "Pierwsze wydanie nie może mieć odbioru")
    check(model["release_states"]["accepted"]["final"] is True, "accepted nie jest końcowe")
    next_release = transitions["W06"]
    check(next_release["from"] == ["accepted"] and next_release["to"] == "in_preparation", "W06: błędne stany")
    check(next_release.get("target") == "new_release" and next_release["actor"] == "A", "W06: błędny cel lub aktor")
    check(next_release["guard"] == "next_release_required", "W06: brak warunku oczekującej zmiany")
    check(next_release.get("interpretation") == "INT-017", "W06: brak INT-017")
    for number in range(5, 11):
        ident = f"T{number:02}"
        check("invalidate_release(e)" in transitions[ident]["effects"], f"{ident}: brak obsługi zmiany wydania")
    check("current_release := n + 1" in next_release["effects"], "W06: brak zwiększenia numeru wydania")
    check("next_release_required := false" in next_release["effects"], "W06: brak skasowania znacznika")
    check(any(effect.startswith("releases[n + 1] :=") for effect in next_release["effects"]), "W06: brak nowego rekordu")
    check("snapshot(release.scope)" in " ".join(transitions["W04"]["effects"]), "W04: brak zapisu migawki")
    check(model["post_step_effects"][0]["id"] == "detect_post_acceptance_change", "Brak obserwatora suspect po odbiorze")
    check(model["test_instance"]["bounds"]["max_releases"] == 2, "WIT5 wymaga granicy dwóch wydań")
    for name, value in model["test_instance"]["bounds"].items():
        check(isinstance(value, int) and value > 0, f"Niepoprawna granica {name}")

    properties = (root / "docs/WLASCIWOSCI.md").read_text()
    interpretations = (root / "docs/INTERPRETACJE.md").read_text()
    state = (root / "docs/STAN.md").read_text()
    plan = (root / "PLAN.md").read_text()
    property_ids = re.findall(r"^\| ((?:G|S|L|F)\d+[ab]?|WIT\d+) \|", properties, re.M)
    check(len(property_ids) == len(set(property_ids)), "Powtórzone ID właściwości lub świadków")
    for ident in ("S7a", "S7b", "S10", "WIT5"):
        check(ident in property_ids, f"Brak definicji {ident}")
    check("S7" not in property_ids, "Stare S7 nadal jest aktywną definicją")
    for ident in ("S7a", "S7b", "S10"):
        row = next((line for line in properties.splitlines() if line.startswith(f"| {ident} |")), "")
        check(len(row.split("|")) == 6 and bool(row.split("|")[-2].strip()), f"{ident}: brak mutanta")
    interpretation_ids = set(re.findall(r"^\| (INT-\d+) \|", interpretations, re.M))
    for path in ("model/process.yaml", "docs/WLASCIWOSCI.md", "docs/INTERPRETACJE.md", "docs/STAN.md"):
        refs = set(re.findall(r"\bINT-\d+\b", (root / path).read_text()))
        check(refs <= interpretation_ids, f"{path}: nieznana interpretacja {refs - interpretation_ids}")
    check("WIT1–WIT5" in plan and "S7a" in plan and "S7b" in plan, "Plan nie uwzględnia zmienionych właściwości")
    for ident, quote in (("DEC-PRO-003", "„d1 a”"), ("DEC-PRO-004", "„Tak, uwzględnij T10”")):
        decision = next((line for line in state.splitlines() if line.startswith(f"| {ident} |")), "")
        cells = [cell.strip() for cell in decision.split("|")[1:-1]]
        check(len(cells) == 5, f"{ident}: brak kolumn Zmienia i Przejrzane")
        if len(cells) == 5:
            check("2026-10-24" in cells[2] and quote in cells[2], f"{ident}: błędna data lub cytat")
            changed = set(re.findall(r"`([^`]+)`", cells[3]))
            reviewed = set(re.findall(r"`([^`]+)`", cells[4]))
            check(bool(changed) and changed <= reviewed, f"{ident}: nieprzejrzane elementy zmiany: {changed - reviewed}")

    if errors:
        raise SystemExit("NIESPÓJNOŚĆ:\n- " + "\n- ".join(errors))
    print(f"OK: {checks} sprawdzeń spójności, {len(transitions)} przejść, {len(items)} elementów, 2 wydania.")
    print("Zakres: struktura YAML, odwołania i zapis DEC-PRO-003/004. Bez symulacji i dowodu właściwości G/S/L (E2/E3).")


if __name__ == "__main__":
    main()
