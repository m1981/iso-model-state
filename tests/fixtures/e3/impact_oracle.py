"""Niezależna wyrocznia E3.4, zapisana z modelu v0.7 i mapowania.

Nie importuje E2, translatora ani ich helperów i nie odczytuje preflight.
None oznacza odmowę procesu, ValueError niepoprawną komendę. Granice
eksploracji nie są warunkami tej relacji. Funkcje nie zmieniają wejścia.
"""

from copy import deepcopy
import json


TRANSITION_IDS = ("T01", "T02", "T04", "T05", "T11", "T12", "T13", "P01", "P02")
APPROVAL_TYPES = frozenset({"PLAN", "REQ", "AT"})
MATURE = frozenset({"approved", "baselined"})
ACTIVE_ITEMS = ("r1", "d1", "a1", "c1")
COMMAND_FIELDS = frozenset({"operation", "item", "question", "actor", "checks", "evidence", "unambiguous", "resolution"})
EVIDENCE = {"simulation": True, "decision": "SIM_DEC", "reference": "SIM_REF", "quote": "SIM_QUOTE"}
MAX_DEPTH = 16


def _transition_ids(transition_ids):
    if (not isinstance(transition_ids, tuple) or len(transition_ids) != 9
            or len(set(transition_ids)) != 9
            or any(not isinstance(t, str) or not t for t in transition_ids)):
        raise ValueError("Wymagane dziewięć różnych identyfikatorów operacji")
    return transition_ids


def initial_state(transition_ids=TRANSITION_IDS):
    """Pełne literalne oczekiwanie po 29 krokach prefiksu; nie wykonuje prefiksu."""
    change_id = _transition_ids(transition_ids)[3]
    return {
        "items": {
            "p1": {"id": "p1", "type": "PLAN", "depends_on": [], "predecessor": "none", "version": 1, "rejections": 0, "suspect": False, "state": "baselined"},
            "r1": {"id": "r1", "type": "REQ", "depends_on": ["p1"], "predecessor": "none", "version": 1, "rejections": 0, "suspect": False, "state": "baselined"},
            "r2": {"id": "r2", "type": "REQ", "depends_on": ["p1"], "predecessor": "none", "version": 1, "rejections": 0, "suspect": False, "state": "baselined"},
            "d1": {"id": "d1", "type": "DES", "depends_on": ["r1"], "predecessor": "none", "version": 1, "rejections": 0, "suspect": False, "state": "baselined"},
            "a1": {"id": "a1", "type": "AT", "depends_on": ["r1"], "predecessor": "none", "version": 1, "rejections": 0, "suspect": False, "state": "baselined"},
            "a2": {"id": "a2", "type": "AT", "depends_on": ["r2"], "predecessor": "none", "version": 1, "rejections": 0, "suspect": False, "state": "baselined"},
            "c1": {"id": "c1", "type": "CODE", "depends_on": ["a1", "d1"], "predecessor": "none", "version": 1, "rejections": 0, "suspect": False, "state": "baselined"},
            "r3": {"id": "r3", "type": "REQ", "depends_on": ["p1"], "predecessor": "none", "version": 0, "rejections": 0, "suspect": False, "state": "none"},
        },
        "questions": {
            "q0": {"id": "q0", "state": "resolved", "blocking": True, "age": 1,
                   "kind": "change", "about": "r1", "about_version": 1,
                   "requested_transition": change_id, "resolution": "approved", "consumed": False},
        },
        "releases": {1: {"number": 1, "state": "in_preparation",
                         "scope": ["a1", "a2", "c1", "d1", "p1", "r1", "r2"],
                         "snapshot": None, "acceptance": None}},
        "current_release": 1,
        "next_release_required": False,
    }


def command(operation, item="none", question="none", actor=None,
            checks=True, evidence=True, unambiguous=True, resolution="approved"):
    """Pełny rekord komendy do uprzęży; prawdziwe wejścia pozostają jawne."""
    if actor is None:
        actor = ("A", "U", "U", "U", "A", "A", "A", "A", "U")[operation]
    return dict(operation=operation, item=item, question=question, actor=actor,
                checks=checks, evidence=evidence, unambiguous=unambiguous,
                resolution=resolution)


def dependents(world, item):
    """Dla każdego kandydata szukamy źródła w jego przodkach, bez E2.

    Algorytm czyta cały aktualny katalog; nie wykorzystuje list r1/d1/a1/c1
    ani stanu dojrzałości wierzchołka. seen zapewnia zakończenie także dla
    syntetycznej topologii z cyklem (legalna instancja pozostaje acykliczna).
    """
    items = world["items"]
    if item not in items:
        raise ValueError("Nieznany element")
    result = set()
    for candidate, record in items.items():
        pending, seen = list(record["depends_on"]), set()
        while pending:
            parent = pending.pop()
            if parent == item:
                result.add(candidate)
                break
            if parent not in seen:
                seen.add(parent)
                pending.extend(items[parent]["depends_on"])
    return result


def _validate_command(world, c):
    if not isinstance(c, dict) or set(c) != COMMAND_FIELDS:
        raise ValueError("Niepełne lub dodatkowe pola komendy")
    if type(c["operation"]) is not int or c["operation"] not in range(9):
        raise ValueError("Nieznana rola operacji")
    if c["actor"] not in ("A", "R", "U"):
        raise ValueError("Nieznany aktor")
    for field in ("checks", "evidence", "unambiguous"):
        if type(c[field]) is not bool:
            raise ValueError("Flagi komendy muszą być boolean")
    if c["resolution"] not in ("approved", "rejected"):
        raise ValueError("Nieznany wynik odpowiedzi")
    if not isinstance(c["item"], str) or not isinstance(c["question"], str):
        raise ValueError("Identyfikatory muszą być tekstem")
    op, qid = c["operation"], c["question"]
    if op < 7:
        if c["item"] not in world["items"]:
            raise ValueError("Nieznany element")
    elif c["item"] != "none":
        raise ValueError("Operacja pytania nie przyjmuje elementu")
    if op in (3, 7, 8):
        if qid not in world["questions"]:
            raise ValueError("Nieznane pytanie")
    elif op == 5:
        if not qid or qid == "none" or qid in world["questions"]:
            raise ValueError("T12 wymaga nowego identyfikatora pytania")
    elif qid != "none":
        raise ValueError("Operacja nie przyjmuje pytania")


def step(world, c, transition_ids=TRANSITION_IDS):
    """Pełna relacja referencyjna; brak obcinania wersji, pytań i głębokości."""
    transition_ids = _transition_ids(transition_ids)
    _validate_command(world, c)
    op, ident, qid = c["operation"], c["item"], c["question"]
    if world["next_release_required"]:
        return None
    if c["actor"] != ("A", "U", "U", "U", "A", "A", "A", "A", "U")[op]:
        return None
    items, questions = world["items"], world["questions"]
    if op < 7:
        e = items[ident]
        state = e["state"]
        deps = [items[d] for d in e["depends_on"]]
        if op == 0:
            enabled = state == "draft" and not e["suspect"] and c["checks"] and all(d["state"] in MATURE for d in deps)
        elif op == 1:
            enabled = state == "verified" and e["type"] in APPROVAL_TYPES and not e["suspect"] and c["evidence"]
        elif op == 2:
            enabled = state in {"approved", "verified"} and not e["suspect"] and (state == "approved" or e["type"] not in APPROVAL_TYPES) and all(d["state"] == "baselined" for d in deps) and c["evidence"]
        elif op == 3:
            q = questions[qid]
            enabled = (state in {"verified", "approved", "baselined"}
                       and q["state"] == "resolved" and q["kind"] == "change"
                       and q["resolution"] == "approved" and q["about"] == ident
                       and q["about_version"] == e["version"]
                       and q["requested_transition"] == transition_ids[3] and not q["consumed"])
        elif op == 4:
            enabled = state in {"draft", "verified", "approved", "baselined"} and e["suspect"] and c["evidence"] and all(d["state"] in MATURE and not d["suspect"] for d in deps)
        elif op == 5:
            enabled = state in {"verified", "approved", "baselined"} and e["suspect"]
        else:
            enabled = state == "draft" and e["suspect"]
    else:
        q = questions[qid]
        if op == 7:
            opened = [p for p in questions.values() if p["state"] == "open"]
            oldest = min(opened, key=lambda p: (not p["blocking"], p["age"]), default=None)
            enabled = q["state"] == "open" and not any(p["state"] == "asked" for p in questions.values()) and q == oldest
        else:
            enabled = q["state"] == "asked" and c["unambiguous"] and c["evidence"]
    if not enabled:
        return None
    out = deepcopy(world)
    records = []
    if op in (0, 1, 2):
        out["items"][ident]["state"] = ("verified", "approved", "baselined")[op]
    elif op == 3:
        out["items"][ident].update(state="draft", version=e["version"] + 1, rejections=0, suspect=False)
        out["questions"][qid]["consumed"] = True
        for affected in dependents(world, ident):
            out["items"][affected]["suspect"] = True
        release = out["releases"][out["current_release"]]
        if ident in release["scope"]:
            if release["state"] in {"ready", "reviewed"}:
                release["state"] = "in_preparation"
            elif release["state"] == "accepted":
                out["next_release_required"] = True
    elif op in (4, 6):
        out["items"][ident]["suspect"] = False
    elif op == 5:
        out["questions"][qid] = {
            "id": qid, "state": "open", "blocking": True,
            "age": max((p["age"] for p in questions.values()), default=0) + 1,
            "kind": "change", "about": ident, "about_version": e["version"],
            "requested_transition": transition_ids[3], "resolution": "none", "consumed": False,
        }
    elif op == 7:
        out["questions"][qid]["state"] = "asked"
    else:
        resolution = c["resolution"] if q["kind"] == "change" else "answered"
        out["questions"][qid].update(state="resolved", resolution=resolution)
        records = [{"kind": "decision", "id": "SIM_DEC", "question": qid,
                    "quote": "SIM_QUOTE", "simulation": True, "resolution": resolution,
                    "about": q["about"], "about_version": q["about_version"],
                    "requested_transition": q["requested_transition"]}]
    # Dwa obserwatory są atomową częścią każdego kroku, po helperze.
    release = out["releases"][out["current_release"]]
    newly_in_scope = any(out["items"][i]["suspect"] and not items[i]["suspect"] for i in release["scope"])
    if newly_in_scope:
        if release["state"] == "accepted":
            out["next_release_required"] = True
        elif release["state"] in {"ready", "reviewed"}:
            release["state"] = "in_preparation"
    return {"world": out, "records": records}


def prefix_events(transition_ids=TRANSITION_IDS):
    """29 jawnych zdarzeń E2 od Init; dane scenariusza, nie wynik E2."""
    ids = _transition_ids(transition_ids)
    events = []
    for ident in ("p1", "r1", "r2", "d1", "a1", "a2", "c1"):
        events.append(dict(transition="T00", actor="A", item=ident))
        events.append(dict(transition=ids[0], actor="A", item=ident,
                           inputs={"checks_ok": {ident: True}}))
        if ident not in {"d1", "c1"}:
            events.append(dict(transition=ids[1], actor="U", item=ident, evidence=deepcopy(EVIDENCE)))
        events.append(dict(transition=ids[2], actor="U", item=ident, evidence=deepcopy(EVIDENCE)))
    events.extend([
        dict(transition="P00", actor="A", question="q0", attributes={"kind": "change", "about": "r1", "requested_transition": ids[3], "blocking": True}),
        dict(transition=ids[7], actor="A", question="q0"),
        dict(transition=ids[8], actor="U", question="q0", inputs={"unambiguous_answer": True, "resolution": "approved"}, evidence=deepcopy(EVIDENCE)),
    ])
    return events


def prefix_history(transition_ids=TRANSITION_IDS):
    """Pochodzenie monitorów: rzeczywiste zaplanowane operacje prefiksu v1.

    Uprząż musi odtworzyć prefix_events przez E2 i dopiero potwierdzić tę
    historię; same rekordy baselined nie są dowodem wykonania T01/T02.
    """
    ids = _transition_ids(transition_ids)
    return [{"transition": event["transition"], "operation": ids.index(event["transition"]),
             "item": event["item"], "version": 1}
            for event in prefix_events(ids) if event["transition"] in ids[:3]]


def prefix_records(transition_ids=TRANSITION_IDS):
    """Ręcznie oczekiwane wyjścia 29 kroków prefiksu (jeden DEC)."""
    ids = _transition_ids(transition_ids)
    return [[] for _ in range(28)] + [[{
        "kind": "decision", "id": "SIM_DEC", "question": "q0", "quote": "SIM_QUOTE",
        "simulation": True, "resolution": "approved", "about": "r1", "about_version": 1,
        "requested_transition": ids[3],
    }]]


def witness(transition_ids=TRANSITION_IDS):
    """Ręczna tabela 13 kroków i 14 pełnych stanów, bez wywołania step.

    Delta w tabeli jest rozwijana wyłącznie przez kopiowanie poprzedniego
    pełnego oczekiwania; nie uruchamia reguł relacji ani kodu produkcyjnego.
    """
    ids = _transition_ids(transition_ids)
    commands = [
        command(3, "r1", "q0"), command(0, "r1"), command(1, "r1"), command(2, "r1"),
        command(4, "d1"), command(5, "a1", "q1"), command(7, question="q1"),
        command(8, question="q1"), command(3, "a1", "q1"), command(0, "a1"),
        command(1, "a1"), command(2, "a1"), command(4, "c1"),
    ]
    changes = [
        {"r1": {"state": "draft", "version": 2}, "d1": {"suspect": True}, "a1": {"suspect": True}, "c1": {"suspect": True}},
        {"r1": {"state": "verified"}}, {"r1": {"state": "approved"}}, {"r1": {"state": "baselined"}},
        {"d1": {"suspect": False}}, {}, {}, {},
        {"a1": {"state": "draft", "version": 2, "suspect": False}},
        {"a1": {"state": "verified"}}, {"a1": {"state": "approved"}}, {"a1": {"state": "baselined"}},
        {"c1": {"suspect": False}},
    ]
    expected = [initial_state(ids)]
    records = [[] for _ in commands]
    for n, delta in enumerate(changes, 1):
        world = deepcopy(expected[-1])
        for ident, fields in delta.items():
            world["items"][ident].update(fields)
        if n == 1:
            world["questions"]["q0"]["consumed"] = True
        elif n == 6:
            world["questions"]["q1"] = {"id": "q1", "state": "open", "blocking": True, "age": 2, "kind": "change", "about": "a1", "about_version": 1, "requested_transition": ids[3], "resolution": "none", "consumed": False}
        elif n == 7:
            world["questions"]["q1"]["state"] = "asked"
        elif n == 8:
            world["questions"]["q1"].update(state="resolved", resolution="approved")
            records[n - 1] = [{"kind": "decision", "id": "SIM_DEC", "question": "q1", "quote": "SIM_QUOTE", "simulation": True, "resolution": "approved", "about": "a1", "about_version": 1, "requested_transition": ids[3]}]
        elif n == 9:
            world["questions"]["q1"]["consumed"] = True
        expected.append(world)
    return {"commands": commands, "expected": expected, "records": records}


def tla_oracle(transition_ids=TRANSITION_IDS):
    """Samodzielna relacja TLA+: wymaga EXTENDS Naturals, Sequences, FiniteSets.

    Zbiory depends_on/scope, funkcje items/questions/releases; brak Python
    None kodowany przez uprząż jako "__null__". Puste questions to funkcja
    pustej domeny. RefResult zwraca rekord world/records tylko dla legalnej
    komendy; poprawność wejść bada osobno Python, nie RefEnabled.
    """
    change_id = json.dumps(_transition_ids(transition_ids)[3])
    return r'''
RefMature == {"approved", "baselined"}
RefApprovalTypes == {"PLAN", "REQ", "AT"}
RECURSIVE RefReach(_, _, _)
RefReach(w, roots, n) ==
    IF n = 0 THEN roots
    ELSE LET previous == RefReach(w, roots, n - 1)
         IN previous \cup {i \in DOMAIN w.items :
             \E d \in w.items[i].depends_on : d \in previous}
RefDependents(w, i) ==
    {j \in DOMAIN w.items :
        \E d \in w.items[j].depends_on :
            d \in RefReach(w, {i}, Cardinality(DOMAIN w.items))}
RefMaxAge(w) ==
    LET ages == {w.questions[q].age : q \in DOMAIN w.questions} \cup {0}
    IN CHOOSE n \in ages : \A m \in ages : n >= m
RefOldest(w, q) ==
    /\ w.questions[q].state = "open"
    /\ \A p \in DOMAIN w.questions :
        w.questions[p].state = "open" =>
          /\ (w.questions[p].blocking => w.questions[q].blocking)
          /\ (w.questions[p].blocking = w.questions[q].blocking =>
                w.questions[q].age <= w.questions[p].age)
RefAuthorization(w, c) ==
    IF c.question \notin DOMAIN w.questions THEN FALSE
    ELSE LET q == w.questions[c.question]
             e == w.items[c.item]
         IN /\ q.state = "resolved"
            /\ q.kind = "change"
            /\ q.resolution = "approved"
            /\ q.about = c.item
            /\ q.about_version = e.version
            /\ q.requested_transition = __CHANGE_ID__
            /\ ~q.consumed
RefEnabled(w, c) ==
    IF w.next_release_required THEN FALSE
    ELSE IF c.operation < 7 THEN
      IF c.item \notin DOMAIN w.items THEN FALSE
      ELSE LET e == w.items[c.item]
               deps == e.depends_on
           IN CASE c.operation = 0 ->
                    /\ c.actor = "A" /\ e.state = "draft" /\ ~e.suspect /\ c.checks
                    /\ \A d \in deps : w.items[d].state \in RefMature
              [] c.operation = 1 ->
                    /\ c.actor = "U" /\ e.state = "verified" /\ ~e.suspect
                    /\ e.type \in RefApprovalTypes /\ c.evidence
              [] c.operation = 2 ->
                    /\ c.actor = "U" /\ e.state \in {"approved", "verified"}
                    /\ ~e.suspect /\ c.evidence
                    /\ (e.state = "approved" \/ e.type \notin RefApprovalTypes)
                    /\ \A d \in deps : w.items[d].state = "baselined"
              [] c.operation = 3 ->
                    /\ c.actor = "U" /\ e.state \in {"verified", "approved", "baselined"}
                    /\ RefAuthorization(w, c)
              [] c.operation = 4 ->
                    /\ c.actor = "A" /\ e.state \in {"draft", "verified", "approved", "baselined"}
                    /\ e.suspect /\ c.evidence
                    /\ \A d \in deps : w.items[d].state \in RefMature /\ ~w.items[d].suspect
              [] c.operation = 5 ->
                    /\ c.actor = "A" /\ e.state \in {"verified", "approved", "baselined"}
                    /\ e.suspect /\ c.question \notin DOMAIN w.questions /\ c.question # "none"
              [] c.operation = 6 -> c.actor = "A" /\ e.state = "draft" /\ e.suspect
              [] OTHER -> FALSE
    ELSE IF c.question \notin DOMAIN w.questions THEN FALSE
    ELSE CASE c.operation = 7 ->
                /\ c.actor = "A" /\ RefOldest(w, c.question)
                /\ \A q \in DOMAIN w.questions : w.questions[q].state # "asked"
         [] c.operation = 8 ->
                /\ c.actor = "U" /\ w.questions[c.question].state = "asked"
                /\ c.unambiguous /\ c.evidence
         [] OTHER -> FALSE
RefResolution(w, c) ==
    IF w.questions[c.question].kind = "change" THEN c.resolution ELSE "answered"
RefProductResult(w, c) ==
    CASE c.operation \in {0, 1, 2} ->
           [w EXCEPT !.items[c.item].state = <<"verified", "approved", "baselined">>[c.operation + 1]]
    [] c.operation = 3 ->
           LET affected == RefDependents(w, c.item)
               changed == [w.items[c.item] EXCEPT !.state = "draft", !.version = @ + 1,
                                                  !.rejections = 0, !.suspect = FALSE]
               updated == [i \in DOMAIN w.items |->
                 LET item == IF i = c.item THEN changed ELSE w.items[i]
                 IN IF i \in affected THEN [item EXCEPT !.suspect = TRUE] ELSE item]
           IN [w EXCEPT !.items = updated, !.questions[c.question].consumed = TRUE]
    [] c.operation \in {4, 6} -> [w EXCEPT !.items[c.item].suspect = FALSE]
    [] c.operation = 5 ->
           LET question == [id |-> c.question, state |-> "open", blocking |-> TRUE,
                            age |-> RefMaxAge(w) + 1, kind |-> "change", about |-> c.item,
                            about_version |-> w.items[c.item].version,
                            requested_transition |-> __CHANGE_ID__, resolution |-> "none", consumed |-> FALSE]
               questions == [q \in DOMAIN w.questions \cup {c.question} |->
                             IF q = c.question THEN question ELSE w.questions[q]]
           IN [w EXCEPT !.questions = questions]
    [] c.operation = 7 -> [w EXCEPT !.questions[c.question].state = "asked"]
    [] c.operation = 8 -> [w EXCEPT !.questions[c.question].state = "resolved",
                                   !.questions[c.question].resolution = RefResolution(w, c)]
RefHelper(w, c) ==
    LET n == w.current_release
        r == w.releases[n]
    IN IF c.operation = 3 /\ c.item \in r.scope THEN
          CASE r.state \in {"ready", "reviewed"} -> [w EXCEPT !.releases[n].state = "in_preparation"]
          [] r.state = "accepted" -> [w EXCEPT !.next_release_required = TRUE]
          [] OTHER -> w
       ELSE w
RefObserve(before, after) ==
    LET n == after.current_release
        r == after.releases[n]
        new == {i \in DOMAIN after.items : after.items[i].suspect /\ ~before.items[i].suspect}
    IN IF new \cap r.scope # {} THEN
          CASE r.state = "accepted" -> [after EXCEPT !.next_release_required = TRUE]
          [] r.state \in {"ready", "reviewed"} -> [after EXCEPT !.releases[n].state = "in_preparation"]
          [] OTHER -> after
       ELSE after
RefRecords(w, c) ==
    IF c.operation # 8 THEN <<>>
    ELSE LET q == w.questions[c.question]
         IN <<[kind |-> "decision", id |-> "SIM_DEC", question |-> c.question,
               quote |-> "SIM_QUOTE", simulation |-> TRUE, resolution |-> RefResolution(w, c),
               about |-> q.about, about_version |-> q.about_version,
               requested_transition |-> q.requested_transition]>>
RefResult(w, c) ==
    [world |-> RefObserve(w, RefHelper(RefProductResult(w, c), c)), records |-> RefRecords(w, c)]
'''.replace("__CHANGE_ID__", change_id)
