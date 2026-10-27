"""Niezależna, skończona wyrocznia badawcza wycinka E3.2 T01--T03.

Autor wyroczni przepisał reguły z T01--T03, item_types i test_instance
w process.yaml, w granicach określonych w E3-02-MAPOWANIE.md.
Moduł nie importuje kodu produkcyjnego, kandydata modelu, translatora ani wykonawcy.
``None`` oznacza niedostępną akcję; ``ValueError`` — wyjście poza kontrakt.
Moduł nie stwierdza osiągalności od Init całego procesu.
"""

from copy import deepcopy


MAX_DEPTH = 8
STATES = ("draft", "verified", "approved")
RECORD_FIELDS = {
    "id", "type", "depends_on", "predecessor", "version", "rejections",
    "suspect", "state",
}
CONTEXT_FIELDS = {"id", "item", "dependencies", "budget", "requires_approval"}


def _item(ident, kind, dependencies, state="draft", version=1, suspect=False):
    return {
        "id": ident, "type": kind, "depends_on": list(dependencies),
        "predecessor": "none", "version": version, "rejections": 0,
        "suspect": suspect, "state": state,
    }


def contexts():
    """Osiem jawnych próbek syntetycznych, każda zaczyna od draft/rejections=0."""
    result = []
    for label, dependency_state, suspect in (
        ("req_approved", "approved", False),
        ("req_baselined", "baselined", False),
        ("req_draft", "draft", False),
        ("req_suspect", "approved", True),
    ):
        result.append({
            "id": label,
            "item": _item("r1", "REQ", ["p1"], version=2, suspect=suspect),
            "dependencies": [_item("p1", "PLAN", [], state=dependency_state)],
            "budget": 2, "requires_approval": True,
        })
    result.append({
        "id": "plan_empty", "item": _item("p1", "PLAN", []),
        "dependencies": [], "budget": 2, "requires_approval": True,
    })
    result.append({
        "id": "des_no_approval", "item": _item("d1", "DES", ["r1"]),
        "dependencies": [_item("r1", "REQ", ["p1"], state="approved")],
        "budget": 2, "requires_approval": False,
    })
    for label, second_state in (("code_good", "baselined"), ("code_mixed", "draft")):
        result.append({
            "id": label, "item": _item("c1", "CODE", ["d1", "a1"], version=2),
            "dependencies": [
                _item("d1", "DES", ["r1"], state="approved"),
                _item("a1", "AT", ["r1"], state=second_state),
            ],
            "budget": 2, "requires_approval": False,
        })
    return result


def _validate_record(record):
    if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
        raise ValueError("Oczekiwano jednego pełnego rekordu elementu ze znanymi polami")
    if (not isinstance(record["id"], str) or not record["id"]
            or record["type"] not in ("PLAN", "REQ", "AT", "DES", "CODE")
            or not isinstance(record["predecessor"], str) or not record["predecessor"]):
        raise ValueError("Niepoprawny identyfikator, typ lub poprzednik elementu")
    if (type(record["version"]) is not int or record["version"] not in (1, 2)
            or type(record["rejections"]) is not int or record["rejections"] < 0
            or type(record["suspect"]) is not bool):
        raise ValueError("Niepoprawna wersja elementu, licznik odrzuceń lub flaga suspect")
    deps = record["depends_on"]
    if (not isinstance(deps, list) or any(not isinstance(d, str) or not d for d in deps)
            or len(deps) != len(set(deps))):
        raise ValueError("depends_on musi być listą różnych identyfikatorów elementów")
    if record["state"] not in (
        "draft", "verified", "approved", "baselined", "deferred", "superseded", "withdrawn",
    ):
        raise ValueError("Nieznany stan elementu")


def _validate_context(context):
    if not isinstance(context, dict) or set(context) != CONTEXT_FIELDS:
        raise ValueError("Oczekiwano pełnego kontekstu E3.2 ze znanymi polami")
    if not isinstance(context["id"], str) or not context["id"]:
        raise ValueError("Kontekst wymaga niepustego identyfikatora")
    if type(context["budget"]) is not int or context["budget"] < 0:
        raise ValueError("budget musi być nieujemną liczbą całkowitą")
    if type(context["requires_approval"]) is not bool:
        raise ValueError("requires_approval musi być wartością logiczną")
    _validate_record(context["item"])
    if context["item"]["state"] != "draft" or context["item"]["rejections"] != 0:
        raise ValueError("Syntetyczny element początkowy musi mieć stan draft i zerowy licznik odrzuceń")
    if not isinstance(context["dependencies"], list):
        raise ValueError("dependencies musi zawierać pełne rekordy bezpośrednich zależności")
    for dependency in context["dependencies"]:
        _validate_record(dependency)
    identifiers = [d["id"] for d in context["dependencies"]]
    if (len(set(identifiers)) != len(identifiers)
            or set(identifiers) != set(context["item"]["depends_on"])):
        raise ValueError("Rekordy zależności muszą dokładnie odpowiadać depends_on")


def domain(context, depth=MAX_DEPTH):
    """Pełne ramy × trzy stany × 0..depth; bez filtrowania po osiągalności.

    Głębokość można zmniejszyć dla mniejszego testu. Jawna zewnętrzna dziedzina
    wyroczni pozostaje 0..8, także dla liczników zabronionych przez bazowy budżet.
    """
    _validate_context(context)
    if type(depth) is not int or not 0 <= depth <= MAX_DEPTH:
        raise ValueError("Głębokość E3.2 musi być liczbą całkowitą w zakresie 0..8")
    return [deepcopy(context["item"]) | {"state": state, "rejections": count}
            for state in STATES for count in range(depth + 1)]


def oracle_step(context, before, operation, actor, checks, evidence):
    """Zwraca pełny oczekiwany element po dozwolonym kroku albo None.

    Operacje 1/2/3 oznaczają reguły specyfikacji niezależnie od ID w YAML.
    Dowód jest nieobecny (False) albo poprawnym rekordem demonstracyjnym (True).
    Zależności i wymóg zatwierdzenia są jawnymi, stałymi danymi kontekstu.
    """
    _validate_context(context)
    _validate_record(before)
    if (before["state"] not in STATES or before["rejections"] > MAX_DEPTH
            or any(before[key] != context["item"][key]
                   for key in RECORD_FIELDS - {"state", "rejections"})):
        raise ValueError("Element jest poza jawną dziedziną wyroczni albo ma nieznaną ramę")
    if type(operation) is not int or operation not in (1, 2, 3):
        raise ValueError("operation musi być liczbą całkowitą 1, 2 lub 3")
    if not isinstance(actor, str) or actor not in ("A", "R", "U"):
        raise ValueError("actor musi mieć wartość A, R lub U")
    if type(checks) is not bool or type(evidence) is not bool:
        raise ValueError("checks i evidence muszą być wartościami logicznymi")

    if operation == 1:
        if (before["state"] != "draft" or actor != "A" or before["suspect"]
                or not checks
                or any(d["state"] not in ("approved", "baselined")
                       for d in context["dependencies"])):
            return None
        return deepcopy(before) | {"state": "verified"}
    if operation == 2:
        if (before["state"] != "verified" or actor != "U" or before["suspect"]
                or not context["requires_approval"] or not evidence):
            return None
        return deepcopy(before) | {"state": "approved"}
    # T03 nie ma bramek checks, suspect, zależności, zatwierdzania typu ani dowodu.
    if (before["state"] != "verified" or actor != "U"
            or before["rejections"] >= context["budget"]):
        return None
    return deepcopy(before) | {"state": "draft", "rejections": before["rejections"] + 1}


def witness():
    """Ręcznie wyprowadzony świadek sześciu kroków i siedem pełnych oczekiwanych rekordów.

    Żaden oczekiwany rekord nie powstaje przez wywołanie oracle_step ani wykonawcy.
    ``expected[0]`` jest początkowy; kolejne rekordy odpowiadają kolejnym wejściom.
    """
    frame = {
        "id": "r1", "type": "REQ", "depends_on": ["p1"],
        "predecessor": "none", "version": 2, "suspect": False,
    }
    return {
        "context_id": "req_approved",
        "inputs": [
            {"operation": 1, "actor": "A", "checks": True, "evidence": False},
            {"operation": 3, "actor": "U", "checks": False, "evidence": False},
            {"operation": 1, "actor": "A", "checks": True, "evidence": False},
            {"operation": 3, "actor": "U", "checks": False, "evidence": False},
            {"operation": 1, "actor": "A", "checks": True, "evidence": False},
            {"operation": 2, "actor": "U", "checks": False, "evidence": True},
        ],
        "expected": [deepcopy(frame) | {"state": state, "rejections": count}
                     for state, count in (
                         ("draft", 0), ("verified", 0), ("draft", 1),
                         ("verified", 1), ("draft", 2), ("verified", 2),
                         ("approved", 2),
                     )],
    }
