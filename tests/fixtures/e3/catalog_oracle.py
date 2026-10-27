"""Niezależna wyrocznia E3.3: pełny katalog i reguły T00--T04.

Dane i reguły przepisano ręcznie z zatwierdzonego modelu v0.7.
Nie odczytuje YAML, nie importuje translatora, wykonawcy ani predykatów E2.
None oznacza odmowę reguły; ValueError oznacza wejście poza kontraktem.
"""

from copy import deepcopy


RECORD_FIELDS = {
    "id", "type", "depends_on", "predecessor", "version", "rejections",
    "suspect", "state",
}
ITEM_IDS = {"p1", "r1", "r2", "d1", "a1", "a2", "c1", "r3"}
DEPENDENCY_TYPES = {
    "PLAN": frozenset(), "REQ": frozenset({"PLAN"}),
    "AT": frozenset({"REQ"}), "DES": frozenset({"REQ"}),
    "CODE": frozenset({"DES", "AT"}),
}
APPROVAL_TYPES = frozenset({"PLAN", "REQ", "AT"})
MAX_DEPTH = 16


def initial_items():
    """Osiem pełnych rekordów rzeczywistego Init; każde wywołanie daje kopię."""
    return {
        "p1": {"id": "p1", "type": "PLAN", "depends_on": [], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        "r1": {"id": "r1", "type": "REQ", "depends_on": ["p1"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        "r2": {"id": "r2", "type": "REQ", "depends_on": ["p1"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        "d1": {"id": "d1", "type": "DES", "depends_on": ["r1"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        "a1": {"id": "a1", "type": "AT", "depends_on": ["r1"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        "a2": {"id": "a2", "type": "AT", "depends_on": ["r2"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        "c1": {"id": "c1", "type": "CODE", "depends_on": ["a1", "d1"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        "r3": {"id": "r3", "type": "REQ", "depends_on": ["p1"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
    }


def _parameters(budget, initial_version):
    if type(budget) is not int or budget < 0:
        raise ValueError("budget musi być nieujemną liczbą całkowitą")
    if type(initial_version) is not int or initial_version < 1:
        raise ValueError("initial_version musi być dodatnią liczbą całkowitą skutku T00")


def _validate_items(items):
    if not isinstance(items, dict) or set(items) != ITEM_IDS:
        raise ValueError("Wymagany pełny katalog ośmiu elementów E3.3")
    for ident, record in items.items():
        if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
            raise ValueError("Wymagany pełny rekord o ośmiu polach")
        if (record["id"] != ident or record["type"] not in DEPENDENCY_TYPES
                or not isinstance(record["predecessor"], str)
                or record["predecessor"] not in ITEM_IDS | {"none"}):
            raise ValueError("Niepoprawne id, type lub predecessor")
        if (type(record["version"]) is not int or record["version"] < 0
                or type(record["rejections"]) is not int or record["rejections"] < 0
                or type(record["suspect"]) is not bool):
            raise ValueError("Niepoprawna wersja, licznik odrzuceń lub suspect")
        deps = record["depends_on"]
        if (not isinstance(deps, list) or any(type(d) is not str for d in deps)
                or len(deps) != len(set(deps)) or not set(deps) <= ITEM_IDS):
            raise ValueError("depends_on musi być listą różnych znanych identyfikatorów")
        if record["state"] not in {
            "none", "draft", "verified", "approved", "baselined",
            "deferred", "superseded", "withdrawn",
        }:
            raise ValueError("Nieznany stan elementu")


def acyclic(items):
    """Niezależna kontrola całego grafu przez usuwanie wierzchołków bez zależności.

    Zła topologia, nieznana krawędź lub duplikat daje False. Nie sprawdza typów.
    Żaden rekord ani lista wejściowa nie zostaje zmieniona.
    """
    if not isinstance(items, dict):
        return False
    graph = {}
    for ident, record in items.items():
        if not isinstance(record, dict):
            return False
        deps = record.get("depends_on")
        if (not isinstance(deps, list) or any(type(d) is not str for d in deps)
                or len(deps) != len(set(deps)) or not set(deps) <= items.keys()):
            return False
        graph[ident] = set(deps)
    while graph:
        leaves = {ident for ident, deps in graph.items() if not deps}
        if not leaves:
            return False
        graph = {ident: deps - leaves for ident, deps in graph.items() if ident not in leaves}
    return True


def step(items, command, *, budget=2, initial_version=1):
    """Pełny następnik katalogu albo None; operacje 0..4 niezależne od ID YAML.

    T00 ma wyłącznie domyślny argument predecessor=none. Dowód jest nieobecny
    albo poprawny demonstracyjny. Zależności czytane są z bieżącego items.
    Parametry kontrolne podaje autor testu, nigdy kandydacki model.
    """
    _parameters(budget, initial_version)
    _validate_items(items)
    if not isinstance(command, dict) or set(command) != {
        "operation", "item", "actor", "checks", "evidence",
    }:
        raise ValueError("Komenda wymaga dokładnie operation/item/actor/checks/evidence")
    if (type(command["operation"]) is not int or command["operation"] not in range(5)
            or command["item"] not in ("p1", "r1")
            or command["actor"] not in ("A", "R", "U")
            or type(command["checks"]) is not bool
            or type(command["evidence"]) is not bool):
        raise ValueError("Komenda poza dziedziną E3.3")
    operation, ident = command["operation"], command["item"]
    record = items[ident]
    dependencies = [items[d] for d in record["depends_on"]]
    actor = command["actor"]
    if operation == 0:
        allowed = (record["state"] == "none" and actor == "A"
                   and {d["type"] for d in dependencies} == DEPENDENCY_TYPES[record["type"]]
                   and acyclic(items))
        update = {"state": "draft", "version": initial_version, "predecessor": "none"}
    elif operation == 1:
        allowed = (record["state"] == "draft" and actor == "A"
                   and not record["suspect"] and command["checks"]
                   and all(d["state"] in {"approved", "baselined"} for d in dependencies))
        update = {"state": "verified"}
    elif operation == 2:
        allowed = (record["state"] == "verified" and actor == "U"
                   and record["type"] in APPROVAL_TYPES and not record["suspect"]
                   and command["evidence"])
        update = {"state": "approved"}
    elif operation == 3:
        allowed = (record["state"] == "verified" and actor == "U"
                   and record["rejections"] < budget)
        update = {"state": "draft", "rejections": record["rejections"] + 1}
    else:
        allowed = (record["state"] in {"approved", "verified"} and actor == "U"
                   and not record["suspect"]
                   and (record["state"] == "approved" or record["type"] not in APPROVAL_TYPES)
                   and all(d["state"] == "baselined" for d in dependencies)
                   and command["evidence"])
        update = {"state": "baselined"}
    if not allowed:
        return None
    result = deepcopy(items)
    result[ident].update(update)
    return result


def tla_oracle(budget=2, initial_version=1, *, graph_acyclic=True):
    """Samodzielna relacja oczekiwana; nie korzysta z Types ani akcji kandydata.

    graph_acyclic pochodzi z acyclic na niezależnie zadanej instancji referencyjnej.
    Stała jest poprawna tylko dla niezmiennej topologii tego wycinka.
    """
    _parameters(budget, initial_version)
    if type(graph_acyclic) is not bool:
        raise ValueError("graph_acyclic musi być wartością logiczną")
    return r'''
RefDependencyTypes == [kind \in {"PLAN", "REQ", "AT", "DES", "CODE"} |->
    CASE kind = "PLAN" -> {}
      [] kind = "REQ" -> {"PLAN"}
      [] kind = "AT" -> {"REQ"}
      [] kind = "DES" -> {"REQ"}
      [] kind = "CODE" -> {"DES", "AT"}]
RefApprovalTypes == {"PLAN", "REQ", "AT"}
RefAcyclic == @ACYCLIC@
RefBudget == @BUDGET@
RefInitialVersion == @VERSION@

RefTypeOK(before, record) ==
    /\ record.type \in DOMAIN RefDependencyTypes
    /\ record.depends_on \subseteq DOMAIN before
    /\ {before[d].type : d \in record.depends_on} = RefDependencyTypes[record.type]

ExpectedEnabled(before, command) ==
    LET record == before[command.item]
        mature == \A d \in record.depends_on : before[d].state \in {"approved", "baselined"}
        baseline == \A d \in record.depends_on : before[d].state = "baselined"
    IN CASE command.operation = 0 ->
                /\ record.state = "none"
                /\ command.actor = "A"
                /\ RefTypeOK(before, record)
                /\ RefAcyclic
         [] command.operation = 1 ->
                /\ record.state = "draft"
                /\ command.actor = "A"
                /\ ~record.suspect
                /\ command.checks
                /\ mature
         [] command.operation = 2 ->
                /\ record.state = "verified"
                /\ command.actor = "U"
                /\ record.type \in RefApprovalTypes
                /\ ~record.suspect
                /\ command.evidence
         [] command.operation = 3 ->
                /\ record.state = "verified"
                /\ command.actor = "U"
                /\ record.rejections < RefBudget
         [] command.operation = 4 ->
                /\ record.state \in {"approved", "verified"}
                /\ command.actor = "U"
                /\ ~record.suspect
                /\ (record.state = "approved" \/ record.type \notin RefApprovalTypes)
                /\ baseline
                /\ command.evidence
         [] OTHER -> FALSE

ExpectedAction(before, after, command) ==
    LET record == before[command.item]
        replacement == CASE command.operation = 0 ->
                               [record EXCEPT !.state = "draft", !.version = RefInitialVersion, !.predecessor = "none"]
                         [] command.operation = 1 -> [record EXCEPT !.state = "verified"]
                         [] command.operation = 2 -> [record EXCEPT !.state = "approved"]
                         [] command.operation = 3 ->
                               [record EXCEPT !.state = "draft", !.rejections = record.rejections + 1]
                         [] command.operation = 4 -> [record EXCEPT !.state = "baselined"]
                         [] OTHER -> record
    IN /\ ExpectedEnabled(before, command)
       /\ after = [before EXCEPT ![command.item] = replacement]
'''.replace("@ACYCLIC@", "TRUE" if graph_acyclic else "FALSE").replace(
        "@BUDGET@", str(budget)).replace("@VERSION@", str(initial_version))


def witness():
    """Osiem wejść i dziewięć ręcznie zapisanych pełnych katalogów.

    Oczekiwania nie są wyliczane przez step, initial_items ani dane kandydata.
    Odmowy są próbami po expected[after_index], nie wykonanymi krokami.
    """
    return {
        "inputs": [
            {"operation": 0, "item": "r1", "actor": "A", "checks": False, "evidence": False},
            {"operation": 0, "item": "p1", "actor": "A", "checks": False, "evidence": False},
            {"operation": 1, "item": "p1", "actor": "A", "checks": True, "evidence": False},
            {"operation": 2, "item": "p1", "actor": "U", "checks": False, "evidence": True},
            {"operation": 1, "item": "r1", "actor": "A", "checks": True, "evidence": False},
            {"operation": 2, "item": "r1", "actor": "U", "checks": False, "evidence": True},
            {"operation": 4, "item": "p1", "actor": "U", "checks": False, "evidence": True},
            {"operation": 4, "item": "r1", "actor": "U", "checks": False, "evidence": True},
        ],
        "refusals": [
            {"after_index": 2, "command": {"operation": 1, "item": "r1", "actor": "A", "checks": True, "evidence": False}},
            {"after_index": 6, "command": {"operation": 4, "item": "r1", "actor": "U", "checks": False, "evidence": True}},
        ],
        "expected": [
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'draft'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'draft'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'draft'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'verified'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'draft'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'approved'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'draft'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'approved'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'verified'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'approved'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'approved'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'baselined'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'approved'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
            {
                'p1': {'id': 'p1', 'type': 'PLAN', 'depends_on': [], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'baselined'},
                'r1': {'id': 'r1', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 1, 'rejections': 0, 'suspect': False, 'state': 'baselined'},
                'r2': {'id': 'r2', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'd1': {'id': 'd1', 'type': 'DES', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a1': {'id': 'a1', 'type': 'AT', 'depends_on': ['r1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'a2': {'id': 'a2', 'type': 'AT', 'depends_on': ['r2'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'c1': {'id': 'c1', 'type': 'CODE', 'depends_on': ['a1', 'd1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
                'r3': {'id': 'r3', 'type': 'REQ', 'depends_on': ['p1'], 'predecessor': 'none', 'version': 0, 'rejections': 0, 'suspect': False, 'state': 'none'},
            },
        ],
    }
