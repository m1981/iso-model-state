"""Sprawdzenie spójności danych E1; nie jest symulatorem ani dowodem G/S/L.

Uruchomienie: uv run --locked python scripts/check_model.py
Trace: DEC-PRO-003–010, G0 (część strukturalna).
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
    observers = {effect["id"]: effect for effect in model["post_step_effects"]}
    check(len(observers) == len(model["post_step_effects"]), "Powtórzone ID obserwatora")
    accepted_observer = observers.get("detect_post_acceptance_change", {})
    check(accepted_observer.get("guard") == "release.state = accepted and exists e in newly_suspect: in_scope(e)"
          and accepted_observer.get("effects") == ["next_release_required := true"],
          "Obserwator suspect po odbiorze musi wymuszać W06 bez zmiany accepted")
    readiness_observer = observers.get("detect_new_suspect_before_acceptance", {})
    check(readiness_observer.get("guard") == "release.state in {ready, reviewed} and exists e in newly_suspect: in_scope(e)"
          and readiness_observer.get("effects") == ["release.state := in_preparation"],
          "DEC-PRO-010: brak cofnięcia gotowości po nowym suspect w zakresie")
    check(transitions["W04"]["guard"] == "not exists q: q.blocking and q.state in {open, asked}",
          "W04/S14: brak kontroli pytań blokujących przed odbiorem")
    check(transitions["W01"]["guard"] == (
        "(forall e: in_scope(e) => (e.state in {baselined, deferred, superseded, withdrawn} "
        "and (e.state = baselined => not e.suspect))) and tests_ok "
        "and not exists q: q.blocking and q.state in {open, asked}"),
        "W01: kompletność musi być w nawiasie, a testy i pytania globalne także dla pustego zakresu")
    check(transitions["T10"]["effects"] == ["invalidate_release(e)"],
          "T10/S15: wznowienie musi zachować licznik odrzuceń i wersję")
    for ident in ("T05", "T06"):
        check("version := version + 1" in transitions[ident]["effects"]
              and "rejections := 0" in transitions[ident]["effects"],
              f"{ident}/S15: nowa wersja musi rozpoczynać własny budżet odrzuceń")
    check({ident for ident, transition in transitions.items()
           if "rejections := 0" in transition["effects"]} == {"T05", "T06"},
          "S15: reset odrzuceń poza T05/T06")
    check(model["test_instance"]["bounds"]["max_releases"] == 2, "WIT5 wymaga granicy dwóch wydań")
    for name, value in model["test_instance"]["bounds"].items():
        check(isinstance(value, int) and value > 0, f"Niepoprawna granica {name}")

    properties = (root / "docs/WLASCIWOSCI.md").read_text()
    interpretations = (root / "docs/INTERPRETACJE.md").read_text()
    state = (root / "docs/STAN.md").read_text()
    plan = (root / "PLAN.md").read_text()
    property_ids = re.findall(r"^\| ((?:G|S|L|F)\d+[ab]?|WIT\d+) \|", properties, re.M)
    check(len(property_ids) == len(set(property_ids)), "Powtórzone ID właściwości lub świadków")
    for ident in ("S7a", "S7b", "S10", "S11", "S12", "S13", "S14", "S15", "WIT3", "WIT5"):
        check(ident in property_ids, f"Brak definicji {ident}")
    check("S7" not in property_ids, "Stare S7 nadal jest aktywną definicją")
    for ident in ("S7a", "S7b", "S10", "S11", "S12", "S13", "S14", "S15"):
        row = next((line for line in properties.splitlines() if line.startswith(f"| {ident} |")), "")
        check(len(row.split("|")) == 6 and bool(row.split("|")[-2].strip()), f"{ident}: brak mutanta")
    interpretation_ids = set(re.findall(r"^\| (INT-\d+) \|", interpretations, re.M))
    for path in ("model/process.yaml", "docs/WLASCIWOSCI.md", "docs/INTERPRETACJE.md", "docs/STAN.md"):
        refs = set(re.findall(r"\bINT-\d+\b", (root / path).read_text()))
        check(refs <= interpretation_ids, f"{path}: nieznana interpretacja {refs - interpretation_ids}")
    check("WIT1–WIT5" in plan and "S7a" in plan and "S7b" in plan and "S1–S15" in plan,
          "Plan nie uwzględnia zmienionych właściwości")
    l4 = next((line for line in properties.splitlines() if line.startswith("| L4 |")), "")
    check("S15" in l4, "L4: brak powiązania z historycznym budżetem odrzuceń S15")
    for ident, quote in (("DEC-PRO-003", "„d1 a”"), ("DEC-PRO-004", "„Tak, uwzględnij T10”"), ("DEC-PRO-005", "„przyjmuje”"), ("DEC-PRO-006", "„d1 tak.”"), ("DEC-PRO-007", "„d1 tak”"), ("DEC-PRO-008", "„D1 tak.”"), ("DEC-PRO-009", "„d1 tak”"), ("DEC-PRO-010", "„d1 tak”")):
        decision = next((line for line in state.splitlines() if line.startswith(f"| {ident} |")), "")
        cells = [cell.strip() for cell in decision.split("|")[1:-1]]
        check(len(cells) == 5, f"{ident}: brak kolumn Zmienia i Przejrzane")
        if len(cells) == 5:
            date = "2026-10-25" if ident in {"DEC-PRO-008", "DEC-PRO-009"} else "2026-10-24"
            if ident == "DEC-PRO-010":
                date = "2026-10-26"
            check(date in cells[2] and quote in cells[2], f"{ident}: błędna data lub cytat")
            changed = set(re.findall(r"`([^`]+)`", cells[3]))
            reviewed = set(re.findall(r"`([^`]+)`", cells[4]))
            check(bool(changed) and changed <= reviewed, f"{ident}: nieprzejrzane elementy zmiany: {changed - reviewed}")

    check(model["version"] == 0.7, "DEC-PRO-010: oczekiwany model v0.7")
    for name in ("kind", "about", "about_version", "requested_transition", "resolution", "consumed"):
        check(name in model["question_variables"], f"Brak pola zgody: {name}")
    for ident in ("T05", "T07"):
        check(transitions[ident]["guard"] == "authorized_change(q,e)", f"{ident}: brak konkretnej zgody")
        check("q.consumed := true" in transitions[ident]["effects"], f"{ident}: brak wykorzystania zgody")
    check("resolution := answer_resolution(q)" in transitions["P02"]["effects"], "P02: brak wyniku odpowiedzi")
    check(set(model["question_semantics"]["change_operations"]) == {"T05", "T07"}, "Niepoprawny zakres zgody")

    check("depends_on" in model["item_variables"] and "predecessor" in model["item_variables"], "Brak zmiennych powiązań")
    check("r3" in items and "r3" not in model["test_instance"]["release_scope"], "r3 musi być rezerwą poza początkowym zakresem")
    check(transitions["T14"]["from"] == ["draft"] and transitions["T14"]["actor"] == "A", "T14: błędny stan lub aktor")
    check(transitions["W07"]["from"] == ["in_preparation"] and transitions["W07"]["actor"] == "U" and transitions["W07"]["to"] == "=", "W07: błędna bramka zakresu")
    check(transitions["T11"]["guard"] == "suspect and forall d in deps(e): d.state in {approved, baselined} and not d.suspect", "T11: brak przeglądu dojrzałych zależności")
    for ident in ("T00", "T14", "W07"):
        check(bool(transitions[ident].get("arguments")), f"{ident}: brak deklaracji argumentów")
    check(transitions["T14"].get("interpretation") == transitions["W07"].get("interpretation") == "INT-018", "Brak interpretacji następstwa")

    if errors:
        raise SystemExit("NIESPÓJNOŚĆ:\n- " + "\n- ".join(errors))
    print(f"OK: {checks} sprawdzeń spójności, {len(transitions)} przejść, {len(items)} elementów, 2 wydania.")
    print("Zakres: struktura YAML, odwołania i zapis DEC-PRO-003–010. Bez symulacji i dowodu właściwości G/S/L (E2/E3).")


if __name__ == "__main__":
    main()
