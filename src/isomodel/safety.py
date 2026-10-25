"""Niezależne wyrocznie S1–S13 dla pełnej historii symulacji v0.6.

Źródło reguł: docs/WLASCIWOSCI.md i model/process.yaml (DEC-PRO-009).
Nie interpretujemy guard/effects ani nie importujemy wykonawcy i jego pomocników.
To sprawdzenie skończonego śladu, nie dowód osiągalności wszystkich stanów.
"""

from copy import deepcopy


USER_GATES = frozenset({"T02", "T03", "T04", "T05", "T06", "T07", "T08", "T09", "T10",
                        "P02", "P03", "P04", "W04", "W05", "W07"})
MATURE = frozenset({"verified", "approved", "baselined"})
INACTIVE = frozenset({"deferred", "superseded", "withdrawn"})
QUESTION_FRAME = ("kind", "about", "about_version", "requested_transition", "blocking", "age", "consumed")


def _initial(model):
    """Odtworzenie deklarowanych danych początkowych bez kodu wykonawcy."""
    items = {}
    for ident, definition in model["test_instance"]["items"].items():
        item = deepcopy(definition) | {"id": ident}
        for field, specification in model["item_variables"].items():
            value = specification["initial"]
            if field == "depends_on":
                value = definition["depends_on"]
            item[field] = deepcopy(value)
        items[ident] = item
    release = {field: deepcopy(specification["initial"])
               for field, specification in model["release_variables"].items()}
    release["scope"] = deepcopy(model["test_instance"]["release_scope"])
    for field in ("snapshot", "acceptance"):
        if release[field] == "none":
            release[field] = None
    return {"items": items, "questions": {}, "releases": {1: release},
            "current_release": 1, "next_release_required": False}


def _dependents(items, source):
    """Domknięcie relacji odwrotnej, wyliczone z grafu przed krokiem."""
    reached = {source}
    while True:
        enlarged = reached | {ident for ident, item in items.items()
                              if reached.intersection(item["depends_on"])}
        if enlarged == reached:
            return reached - {source}
        reached = enlarged


def _valid_graph(model, items, ident, dependencies):
    if len(dependencies) != len(set(dependencies)) or any(d not in items for d in dependencies):
        return False
    required = set(model["item_types"][items[ident]["type"]]["depends_on"])
    if {items[d]["type"] for d in dependencies} != required:
        return False
    # Usuwanie wierzchołków bez zależności (niezależna kontrola acykliczności).
    graph = {key: set(dependencies if key == ident else item["depends_on"])
             for key, item in items.items()}
    if any(not edges <= graph.keys() for edges in graph.values()):
        return False
    while graph:
        leaves = {key for key, edges in graph.items() if not edges}
        if not leaves:
            return False
        graph = {key: edges - leaves for key, edges in graph.items() if key not in leaves}
    return True


def _complete(state, scope):
    return all(ident in state["items"] and
               (state["items"][ident]["state"] in INACTIVE or
                (state["items"][ident]["state"] == "baselined" and
                 not state["items"][ident]["suspect"])) for ident in scope)


def safety_violations(model, steps):
    """Zwraca [{property, step, detail}] dla ciągłego śladu applied od początku.

    Niepełny prefiks, przerwana ciągłość lub kroki rejected/error powodują
    ValueError: nie są dowodem historycznych S2/S3/S8. Numery step w wyniku
    są pozycjami 1-based w przekazanym śladzie; pusta historia jest poprawna.
    Model dostarcza słownik typów i inicjalizację, lecz nie badane strażniki.
    """
    violations = []
    previous = _initial(model)
    approved, verified, reviewed = set(), set(), set()
    for index, step in enumerate(steps, 1):
        if step.get("outcome") != "applied":
            raise ValueError(f"Krok {index}: wymagany krok applied")
        pre, post, event = step["before"], step["after"], step["event"]
        if pre != previous:
            raise ValueError(f"Krok {index}: ślad musi być ciągły i zaczynać się w stanie początkowym")
        previous = post
        transition, actor = event["transition"], event["actor"]
        selected = event.get("item")
        items, after_items = pre["items"], post["items"]
        current = pre["releases"][pre["current_release"]]

        def check(condition, property_id, detail):
            if not condition:
                violations.append({"property": property_id, "step": index, "detail": detail})

        check(transition not in USER_GATES or actor == "U", "S1", f"{transition}: bramka wymaga U")
        for ident, item in after_items.items():
            if item["version"] != items[ident]["version"]:
                approved.discard(ident)
                verified.discard(ident)
            if item["state"] == "baselined" and model["item_types"][item["type"]]["requires_approval"]:
                check(ident in approved, "S2", f"{ident}: brak wcześniejszego approved tej wersji")
            if item["state"] in {"approved", "baselined"}:
                check(ident in verified, "S3", f"{ident}: brak wcześniejszego verified tej wersji")
            if item["state"] in MATURE and not item["suspect"]:
                dependencies = [after_items.get(d, {}) for d in item["depends_on"]]
                check(all(d.get("state") in {"approved", "baselined"} for d in dependencies),
                      "S4", f"{ident}: niedojrzała zależność bez suspect")
                check(all(d.get("state") not in {"superseded", "withdrawn"} for d in dependencies),
                      "S6", f"{ident}: nieaktywna zależność bez suspect")
            if item["state"] == "verified":
                verified.add(ident)
            if item["state"] == "approved":
                approved.add(ident)

        if transition in {"T05", "T06", "T07", "T08", "T14"}:
            for ident in sorted(_dependents(items, selected)):
                dependent = after_items[ident]
                check(dependent["suspect"] or dependent["state"] in INACTIVE,
                      "S5", f"{selected}: zależny {ident} nieoznaczony")

        release = post["releases"][post["current_release"]]
        if release["state"] in {"ready", "reviewed"}:
            check(_complete(post, release["scope"]), "S7a", "Niekompletny zakres ready/reviewed")
        if transition == "W04":
            check(_complete(pre, current["scope"]), "S7b", "Niekompletny zakres przed odbiorem")
            expected = {ident: {key: value for key, value in items[ident].items() if key != "id"}
                        for ident in current["scope"]}
            accepted = post["releases"].get(pre["current_release"], {})
            check(accepted.get("snapshot") == expected, "S7b", "Migawka różni się od produktów przed odbiorem")
        for number, record in post["releases"].items():
            if record["state"] == "accepted":
                check(number in reviewed, "S8", f"Wydanie {number}: brak wcześniejszego przeglądu R")
            before_record = pre["releases"].get(number, {})
            if record["state"] == "reviewed" and before_record.get("state") != "reviewed" and actor == "R":
                reviewed.add(number)
        check(sum(q["state"] == "asked" for q in post["questions"].values()) <= 1,
              "S9", "Więcej niż jedno pytanie asked")
        for number, record in pre["releases"].items():
            if record["state"] == "accepted":
                check(post["releases"].get(number) == record, "S10", f"Wydanie {number}: zmiana odebranego rekordu")

        if transition in {"T05", "T07"}:
            q = pre["questions"].get(event.get("question"), {})
            item = items[selected]
            authorized = (q.get("state") == "resolved" and q.get("kind") == "change" and
                          q.get("resolution") == "approved" and q.get("about") == selected and
                          q.get("about_version") == item["version"] and
                          q.get("requested_transition") == transition and q.get("consumed") is False)
            check(authorized, "S11", f"{transition}({selected}): brak konkretnej, niewykorzystanej zgody")
            after_q = post["questions"].get(event.get("question"), {})
            check(after_q.get("consumed") is True, "S11", "Operacja nie zużyła zgody")
        if transition in {"P01", "P02", "P03", "P04", "P05"}:
            for ident, q in pre["questions"].items():
                after_q = post["questions"].get(ident, {})
                check(all(q[field] == after_q.get(field) for field in QUESTION_FRAME),
                      "S11", f"{ident}: zmiana powiązania lub consumed przez {transition}")

        for ident, before_item in items.items():
            after_item = after_items[ident]
            if before_item["depends_on"] != after_item["depends_on"]:
                check(transition == "T14" and selected == ident, "S12", f"{ident}: zależności zmienione poza T14")
            if before_item["predecessor"] != after_item["predecessor"]:
                check(transition == "T00" and selected == ident and before_item["state"] == "none",
                      "S12", f"{ident}: zmiana historycznego poprzednika poza T00")
        if transition == "T00":
            item = items[selected]
            predecessor = event.get("predecessor", "none")
            old = items.get(predecessor, {})
            valid = (predecessor == "none" or (old.get("state") == "superseded" and
                     old.get("type") == item["type"] and predecessor != selected))
            check(item["state"] == "none" and valid and
                  after_items[selected]["predecessor"] == predecessor and
                  _valid_graph(model, items, selected, item["depends_on"]),
                  "S12", f"{selected}: niepoprawna inicjalizacja powiązań T00")
        if transition == "T14":
            item = items[selected]
            old_id, new_id = event.get("old_dependency"), event.get("new_dependency")
            old, new = items.get(old_id, {}), items.get(new_id, {})
            expected = (set(item["depends_on"]) - {old_id}) | {new_id}
            valid = (actor == "A" and item["state"] == "draft" and current["state"] == "in_preparation" and
                     old_id in item["depends_on"] and old.get("state") == "superseded" and
                     new.get("predecessor") == old_id and new.get("state") == "baselined" and
                     new.get("suspect") is False and old_id != new_id and new_id not in item["depends_on"] and
                     new_id != selected and _valid_graph(model, items, selected, expected) and
                     (selected not in current["scope"] or new_id in current["scope"]))
            actual = after_items[selected]
            check(valid and set(actual["depends_on"]) == expected and
                  len(actual["depends_on"]) == len(expected) and
                  all(actual[key] == item[key] for key in item if key != "depends_on"),
                  "S12", f"{selected}: T14 nie jest dozwoloną podmianą jednej krawędzi szkicu")
            check(all(after_items[d]["suspect"] for d in _dependents(items, selected)),
                  "S12", f"{selected}: brak propagacji T14")

        for number, record in pre["releases"].items():
            after_record = post["releases"].get(number)
            check(after_record is not None, "S13", f"Wydanie {number}: usunięto istniejący zakres")
            if after_record is not None and record["scope"] != after_record["scope"]:
                check(transition == "W07" and number == pre["current_release"],
                      "S13", f"Wydanie {number}: zakres zmieniony poza W07")
        if transition == "W07":
            item = items.get(selected, {})
            predecessor = items.get(item.get("predecessor"), {})
            expected = set(current["scope"]) | {selected}
            actual = post["releases"].get(pre["current_release"], {})
            valid = (actor == "U" and current["state"] == "in_preparation" and
                     selected not in current["scope"] and item.get("state") == "baselined" and
                     item.get("suspect") is False and item.get("predecessor") not in {None, "none"} and
                     predecessor.get("state") == "superseded" and
                     item.get("predecessor") in current["scope"] and
                     set(item.get("depends_on", [])) <= set(current["scope"]))
            check(valid and set(actual.get("scope", [])) == expected and
                  len(actual.get("scope", [])) == len(expected) and
                  all(actual.get(key) == value for key, value in current.items() if key != "scope"),
                  "S13", "W07 nie jest kontrolowanym rozszerzeniem zakresu")
        new_numbers = post["releases"].keys() - pre["releases"].keys()
        if new_numbers or transition == "W06":
            number = pre["current_release"] + 1
            check(transition == "W06" and new_numbers == {number} and
                  post["current_release"] == number and
                  post["releases"][number]["scope"] == current["scope"],
                  "S13", "Nowy rekord zakresu poza W06 albo bez kopii poprzedniego zakresu")
    return violations
