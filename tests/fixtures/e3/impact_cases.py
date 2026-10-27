"""Niezależne przypadki i ręczne złe następstwa mutantów E3.4.

Importuje wyłącznie zamrożoną wyrocznię sibling oraz standardowe copy.
Nie importuje, nie uruchamia i nie odczytuje E2 ani translatora.
"""

from copy import deepcopy

from impact_oracle import command, initial_state, step, witness


def _case(ident, before, cmd, note, *, input_error=False):
    result = None if input_error else step(before, cmd)
    out = {"id": ident, "before": deepcopy(before), "command": deepcopy(cmd),
           "expected": result, "note": note}
    if input_error:
        out["input_error"] = True
    return out


def _release_case(item, inside, state):
    world = initial_state()
    world["questions"]["q0"]["about"] = item
    release = world["releases"][1]
    if not inside:
        release["scope"].remove(item)
    release["state"] = state
    if state == "accepted":
        release["snapshot"] = {
            i: {k: deepcopy(v) for k, v in world["items"][i].items() if k != "id"}
            for i in release["scope"]
        }
        release["acceptance"] = {"number": 1, "quote": "SIM_QUOTE"}
    return world


def cases():
    """Pełne konteksty A/I/R; każdy ma nową kopię świata i komendy.

    Wszystkie warianty zachowują osiem ID i bazową topologię. Stany
    izolacyjne są jawnie oznaczone; R są pełnymi stanami oczekiwanymi,
    których osiągalność należy osobno potwierdzić prefiksem E2.
    """
    out = []
    base = initial_state()
    checkpoints = witness()["expected"]
    for field, value in (
        ("state", "asked"), ("kind", "general"), ("resolution", "rejected"),
        ("about", "r2"), ("about_version", 2),
        ("requested_transition", "T07"), ("consumed", True),
    ):
        before = deepcopy(base)
        before["questions"]["q0"][field] = value
        out.append(_case("A01_" + field, before, command(3, "r1", "q0"),
                         "Wstrzyknięta izolacja jednego składnika zgody: " + field))
    for actor in ("A", "R"):
        out.append(_case("A02_actor_" + actor, base, command(3, "r1", "q0", actor=actor),
                         "Odmowa roli T05 przy poprawnej zgodzie."))
    for q in ("none", "missing"):
        out.append(_case("A02_question_" + q, base, command(3, "r1", q),
                         "Błąd wejścia ValueError; expected=None oznacza brak następstwa, NIE guard=false.",
                         input_error=True))
    asked = checkpoints[7]
    out.append(_case("A03_approved", asked, command(8, question="q1"), "Pozytywne P02 z pełnym DEC."))
    rejected = _case("A03_rejected", asked, command(8, question="q1", resolution="rejected"),
                     "P02 zapisuje odmowny wynik w pytaniu i DEC.")
    out.append(rejected)
    out.append(_case("A03_rejected_change", rejected["expected"]["world"], command(3, "a1", "q1"),
                     "Odmowna odpowiedź nie uprawnia do T05."))
    out.append(_case("A03_ambiguous", asked, command(8, question="q1", unambiguous=False),
                     "Brak jednoznaczności nie zmienia świata ani nie tworzy DEC."))
    out.append(_case("A03_no_evidence", asked, command(8, question="q1", evidence=False),
                     "Brak dowodu P02 jest odmową, bez records."))
    linked_answer = deepcopy(asked)
    linked_answer["items"]["a1"]["predecessor"] = "a2"
    linked_answer["items"]["a2"]["state"] = "superseded"
    out.append(_case("A03_approved_predecessor", linked_answer, command(8, question="q1"),
                     "Wstrzyknięta historia a1.predecessor=a2, a2=superseded; nie twierdzimy osiągalności. "
                     "Kontekst wiązania DEC przez legalną referencję, bez zmiany depends_on."))
    consumed = deepcopy(base)
    consumed["questions"]["q0"]["consumed"] = True
    out.append(_case("A04_consumed", consumed, command(3, "r1", "q0"),
                     "Zużycie izolowane przy nadal pasującej wersji 1."))
    queued = step(checkpoints[6], command(5, "a1", "q2"))["world"]
    out.append(_case("A05_oldest", queued, command(7, question="q1"),
                     "Dwa otwarte blocking/change: q1 age2 przed q2 age3."))
    out.append(_case("A05_younger", queued, command(7, question="q2"), "Odmowa młodszego q2."))
    already_asked = step(queued, command(7, question="q1"))["world"]
    out.append(_case("A05_asked_limit", already_asked, command(7, question="q2"),
                     "q2 jest najstarszym open, lecz q1 jest już asked; izolacja count(asked)."))
    out.append(_case("I01_r1", base, command(3, "r1", "q0"),
                     "Dokładne domknięcie d1/a1/c1; rama p1/r2/a2/r3."))
    out.append(_case("I01_a1", checkpoints[8], command(3, "a1", "q1"),
                     "Zależny c1 już suspect: ponowne oznaczenie idempotentne."))
    out.append(_case("I01_raise_a1", checkpoints[5], command(5, "a1", "q1"),
                     "T12 tworzy pełny rekord powiązany z a1 v1, age2."))
    linked_request = deepcopy(checkpoints[5])
    linked_request["items"]["a1"]["predecessor"] = "a2"
    linked_request["items"]["a2"]["state"] = "superseded"
    out.append(_case("I01_raise_a1_predecessor", linked_request, command(5, "a1", "q1"),
                     "Wstrzyknięta historia a1.predecessor=a2, a2=superseded; nie twierdzimy osiągalności. "
                     "Kontekst błędnego about przez legalny predecessor, bez zmiany depends_on."))
    out.append(_case("I02_immature", checkpoints[1], command(4, "d1"),
                     "r1=draft/suspect=false izoluje dojrzałość zależności T11."))
    out.append(_case("I02_suspect_dependency", checkpoints[5], command(4, "c1"),
                     "d1/a1 baselined, tylko a1 nadal suspect; izolacja flagi zależności."))
    out.append(_case("I02_positive", checkpoints[4], command(4, "d1"),
                     "T11 czyści wyłącznie d1.suspect przy dojrzałym r1."))
    out.append(_case("I02_no_evidence", checkpoints[12], command(4, "c1", evidence=False),
                     "Wszystkie zależności dojrzałe i przejrzane; brakuje wyłącznie dowodu."))
    out.append(_case("I02_final_positive", checkpoints[12], command(4, "c1"), "Legalne końcowe T11(c1)."))
    draft = deepcopy(checkpoints[1])
    draft["items"]["c1"]["state"] = "draft"
    out.append(_case("I03_fix", draft, command(6, "c1"),
                     "Wariant prefiksu c1=draft v1; po zmianie r1 T13 czyści tylko flagę."))
    fixed = step(draft, command(6, "c1"))["world"]
    out.append(_case("I03_verify_mature_suspect_dependencies", fixed, command(0, "c1"),
                     "T01 dozwolone: d1/a1 baselined choć suspect; T01 nie bada ich flag."))
    for actor in ("U", "R"):
        out.append(_case("I03_actor_" + actor, draft, command(6, "c1", actor=actor),
                         "Nieuprawniony aktor T13 przy poprawnym szkicu."))
    out.append(_case("I03_baselined", checkpoints[1], command(6, "a1"),
                     "T13 nie otwiera szkicu z baselined."))
    direct_draft = deepcopy(checkpoints[9])
    direct_draft["items"]["c1"]["state"] = "draft"
    out.append(_case("I03_verify_own_suspect", direct_draft, command(0, "c1"),
                     "Własne suspect blokuje weryfikację szkicu."))
    direct_draft = step(direct_draft, command(6, "c1"))["world"]
    out.append(_case("I03_verify_immature_dependency", direct_draft, command(0, "c1"),
                     "Po T13 własna flaga false, lecz a1=draft blokuje T01."))
    own_suspect = deepcopy(fixed)
    own_suspect["items"]["c1"]["suspect"] = True
    out.append(_case("I03_verify_own_suspect_isolated", own_suspect, command(0, "c1"),
                     "Wstrzyknięta izolacja: szkic i dojrzałe zależności; tylko własne suspect blokuje T01."))
    reset = deepcopy(base)
    reset["items"]["r1"].update(rejections=2, suspect=True)
    out.append(_case("I04_reset", reset, command(3, "r1", "q0"),
                     "Wstrzyknięta izolacja licznika 2 i własnej flagi; nowa wersja resetuje oba."))
    for item in ("r1", "a2"):
        for inside in (True, False):
            for state in ("ready", "reviewed", "accepted"):
                group = ("R01" if state != "accepted" else "R02") if item == "r1" and inside else "R03" if item == "r1" else "R04"
                ident = f"{group}_{item}_{'in' if inside else 'out'}_{state}"
                before = _release_case(item, inside, state)
                case = _case(ident, before, command(3, item, "q0"),
                             "Pełny oczekiwany kontekst wydania; osiągalność potwierdza osobny prefiks E2. "
                             + ("Liść izoluje helper." if item == "a2" else "Źródło poza scope izoluje obserwator." if not inside else "Zmiana źródła w zakresie."))
                out.append(case)
                if state == "accepted" and (inside or item == "r1"):
                    out.append(_case(ident + "_pending", case["expected"]["world"], command(4, "d1"),
                                     "Pending blokuje T11 jako następną operację; W06 poza wycinkiem."))
                    out.append(_case(ident + "_pending_verify", case["expected"]["world"], command(0, item),
                                     "Izolacja priorytetu: zmieniony produkt jest draft/suspect=false, "
                                     "jego zależności dojrzałe, checks=true; T01 odmawia wyłącznie przez pending."))
                    unblocked = deepcopy(case["expected"]["world"])
                    unblocked["next_release_required"] = False
                    out.append(_case(ident + "_pending_verify_isolated", unblocked, command(0, item),
                                     "Wstrzyknięta kontrola izolacji: identyczny świat z pending=false "
                                     "dopuszcza T01; nie twierdzimy osiągalności tego wyłączenia bez W06."))
    return out


def _decision(question, resolution):
    return {"kind": "decision", "id": "SIM_DEC", "question": question["id"],
            "quote": "SIM_QUOTE", "simulation": True, "resolution": resolution,
            "about": question["about"], "about_version": question["about_version"],
            "requested_transition": question["requested_transition"]}


def _wrong_change(case):
    """Ręczny skutek T05 z pominiętą bramką, bez odpytywania kandydata."""
    world = deepcopy(case["before"])
    c = case["command"]
    item, q = c["item"], c["question"]
    world["items"][item].update(state="draft", version=world["items"][item]["version"] + 1,
                               rejections=0, suspect=False)
    world["questions"][q]["consumed"] = True
    affected = {"r1": {"d1", "a1", "c1"}, "a1": {"c1"}, "a2": set()}[item]
    for ident in affected:
        world["items"][ident]["suspect"] = True
    return {"world": world, "records": []}


def mutants(model):
    """34 mutanty, każdy z własną kopią modelu, case i złym następnikiem.

    special=direct/all są mutacjami algorytmu domknięcia, nie YAML.
    special=noquestion wymaga świadomego usunięcia argumentu question
    w zdarzeniu E2; normalny kontrakt T12 wymaga tego argumentu.
    """
    by_id = {case["id"]: case for case in cases()}
    result = []

    def add(ident, case_id, transition=None, edits=None, *, wrong=None,
            violation="Successor", special=None, **metadata):
        candidate = deepcopy(model)
        if transition is not None:
            family = "question_transitions" if transition.startswith("P") else "item_transitions"
            definition = next(t for t in candidate[family] if t["id"] == transition)
            for key, value in (edits or {}).items():
                if value is None:
                    definition.pop(key, None)
                else:
                    definition[key] = deepcopy(value)
        case = deepcopy(by_id[case_id])
        entry = {"id": ident, "model": candidate, "case": case,
                 "wrong_expected": deepcopy(wrong if wrong is not None else case["expected"]),
                 "expected_violation": violation, **metadata}
        if special is not None:
            entry["special"] = special
        result.append(entry)
        return entry

    item_transitions = {t["id"]: t for t in model["item_transitions"]}
    question_transitions = {t["id"]: t for t in model["question_transitions"]}
    authorization_terms = (
        ("state", "q.state = resolved"), ("kind", "q.kind = change"),
        ("resolution", "q.resolution = approved"), ("about", "q.about = e.id"),
        ("about_version", "q.about_version = e.version"),
        ("requested_transition", "q.requested_transition = transition.id"),
        ("consumed", "not q.consumed"),
    )
    for field, removed in authorization_terms:
        case_id = "A01_" + field
        entry = add("authorization_without_" + field, case_id,
                    wrong=_wrong_change(by_id[case_id]), violation="Availability")
        entry["model"]["question_semantics"]["authorized_change"] = " and ".join(
            term for _, term in authorization_terms if term != removed)
    add("change_wrong_actor", "A02_actor_A", "T05", {"actor": "A"},
        wrong=_wrong_change(by_id["A02_actor_A"]), violation="Availability")

    for ident, effect, case_id, field, bad_value in (
        ("change_without_consumption", "q.consumed := true", "I01_r1", "consumed", False),
        ("change_without_version", "version := version + 1", "I01_r1", "version", 1),
        ("change_without_rejection_reset", "rejections := 0", "I04_reset", "rejections", 2),
        ("change_without_own_flag_reset", "suspect := false", "I04_reset", "suspect", True),
    ):
        wrong = deepcopy(by_id[case_id]["expected"])
        if field == "consumed":
            wrong["world"]["questions"]["q0"][field] = bad_value
        else:
            wrong["world"]["items"]["r1"][field] = bad_value
        add(ident, case_id, "T05", {"effects": [e for e in item_transitions["T05"]["effects"] if e != effect]}, wrong=wrong)
    propagation = "forall d in dependents(e): d.suspect := true"
    wrong = deepcopy(by_id["I01_r1"]["expected"])
    for item in ("d1", "a1", "c1"):
        wrong["world"]["items"][item]["suspect"] = False
    add("change_without_propagation", "I01_r1", "T05",
        {"effects": [e for e in item_transitions["T05"]["effects"] if e != propagation]}, wrong=wrong)
    wrong = deepcopy(by_id["I01_r1"]["expected"])
    wrong["world"]["items"]["c1"]["suspect"] = False
    add("change_direct_only", "I01_r1", wrong=wrong, special="direct")
    wrong = deepcopy(by_id["I01_r1"]["expected"])
    for ident, record in wrong["world"]["items"].items():
        if ident != "r1":
            record["suspect"] = True
    add("change_whole_catalog", "I01_r1", wrong=wrong, special="all")

    for ident, case_id, edits in (
        ("review_without_maturity", "I02_immature", {"guard": "suspect and forall d in deps(e): not d.suspect"}),
        ("review_without_dependency_flag", "I02_suspect_dependency", {"guard": "suspect and forall d in deps(e): d.state in {approved, baselined}"}),
        ("review_without_evidence", "I02_no_evidence", {"evidence": None}),
    ):
        case = by_id[case_id]
        wrong = {"world": deepcopy(case["before"]), "records": []}
        wrong["world"]["items"][case["command"]["item"]]["suspect"] = False
        add(ident, case_id, "T11", edits, wrong=wrong, violation="Availability")

    raise_case = by_id["I01_raise_a1"]
    creation = item_transitions["T12"]["effects"]
    linked_raise = by_id["I01_raise_a1_predecessor"]
    wrong = deepcopy(linked_raise["expected"])
    wrong["world"]["questions"]["q1"]["about"] = "a2"
    add("request_wrong_about", linked_raise["id"], "T12",
        {"effects": [e.replace("about = e.id", "about = predecessor(e).id") for e in creation]}, wrong=wrong)
    wrong = deepcopy(raise_case["expected"])
    wrong["world"]["questions"]["q1"]["requested_transition"] = "T07"
    add("request_wrong_operation", raise_case["id"], "T12",
        {"effects": [e.replace("requested_transition = T05", "requested_transition = T07") for e in creation]}, wrong=wrong)
    wrong = deepcopy(raise_case["expected"])
    wrong["world"]["items"]["a1"]["version"] = 2
    wrong["world"]["questions"]["q1"]["about_version"] = 2
    add("request_wrong_version", raise_case["id"], "T12",
        {"effects": ["version := version + 1"] + creation}, wrong=wrong,
        fieldcheckwanted="question_version")
    add("request_without_question", raise_case["id"], "T12", {"effects": []},
        wrong={"world": deepcopy(raise_case["before"]), "records": []}, special="noquestion")

    for ident, case_id, edits in (
        ("fix_baselined", "I03_baselined", {"from": ["draft", "baselined"]}),
        ("fix_wrong_actor", "I03_actor_U", {"actor": "U"}),
    ):
        case = by_id[case_id]
        wrong = {"world": deepcopy(case["before"]), "records": []}
        wrong["world"]["items"][case["command"]["item"]].update(state="draft", suspect=False)
        add(ident, case_id, "T13", edits, wrong=wrong, violation="Availability")
    wrong = deepcopy(by_id["I03_fix"]["expected"])
    wrong["world"]["items"]["c1"]["version"] = 2
    add("fix_changes_version", "I03_fix", "T13",
        {"effects": item_transitions["T13"]["effects"] + ["version := version + 1"]}, wrong=wrong)

    leaf_case = "R04_a2_in_ready"
    wrong = deepcopy(by_id[leaf_case]["expected"])
    wrong["world"]["releases"][1] = deepcopy(by_id[leaf_case]["before"]["releases"][1])
    add("change_without_helper", leaf_case, "T05",
        {"effects": [e for e in item_transitions["T05"]["effects"] if e != "invalidate_release(e)"]}, wrong=wrong)
    for ident, case_id, observer in (
        ("without_observer_before_acceptance", "R03_r1_out_ready", "detect_new_suspect_before_acceptance"),
        ("without_observer_after_acceptance", "R03_r1_out_accepted", "detect_post_acceptance_change"),
    ):
        wrong = deepcopy(by_id[case_id]["expected"])
        wrong["world"]["releases"] = deepcopy(by_id[case_id]["before"]["releases"])
        wrong["world"]["next_release_required"] = False
        entry = add(ident, case_id, wrong=wrong)
        entry["model"]["post_step_effects"] = [e for e in entry["model"]["post_step_effects"] if e["id"] != observer]
    case_id = "R03_r1_out_accepted"
    wrong = deepcopy(by_id[case_id]["expected"])
    wrong["world"]["releases"][1]["state"] = "in_preparation"
    wrong["world"]["next_release_required"] = False
    entry = add("observer_overwrites_accepted", case_id, wrong=wrong)
    observer = next(e for e in entry["model"]["post_step_effects"] if e["id"] == "detect_post_acceptance_change")
    observer["effects"] = ["release.state := in_preparation"]

    wrong = deepcopy(by_id["I01_r1"]["expected"])
    wrong["world"]["items"]["r1"]["state"] = "approved"
    add("change_to_approved_history", "I01_r1", "T05", {"to": "approved"}, wrong=wrong,
        monitorwanted="version_history")
    case_id = "A05_asked_limit"
    wrong = {"world": deepcopy(by_id[case_id]["before"]), "records": []}
    wrong["world"]["questions"]["q2"]["state"] = "asked"
    add("ask_without_single_pending", case_id, "P01", {"guard": "q = oldest(open, blocking_first)"},
        wrong=wrong, violation="Availability")
    case_id = "A03_ambiguous"
    wrong = {"world": deepcopy(by_id[case_id]["before"]), "records": []}
    q = wrong["world"]["questions"]["q1"]
    q.update(state="resolved", resolution="approved")
    wrong["records"] = [_decision(q, "approved")]
    add("resolve_without_unambiguous", case_id, "P02", {"guard": "true"}, wrong=wrong,
        violation="Availability")
    wrong = deepcopy(by_id["A03_approved"]["expected"])
    wrong["world"]["questions"]["q1"]["resolution"] = "rejected"
    wrong["records"][0]["resolution"] = "rejected"
    add("resolve_wrong_resolution", "A03_approved", "P02",
        {"effects": [e.replace("resolution := answer_resolution(q)", "resolution := rejected") for e in question_transitions["P02"]["effects"]]}, wrong=wrong)
    wrong = deepcopy(by_id["A03_approved_predecessor"]["expected"])
    wrong["world"]["questions"]["q1"]["about"] = "a2"
    wrong["records"][0]["about"] = "a2"
    effects = []
    for effect in question_transitions["P02"]["effects"]:
        if effect == "record DEC with user quote":
            effects.append("about := item(q.about).predecessor")
        effects.append(effect)
    add("resolve_wrong_dec_binding", "A03_approved_predecessor", "P02", {"effects": effects}, wrong=wrong,
        fieldcheckwanted="decision_binding")
    return result
