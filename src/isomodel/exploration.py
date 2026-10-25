"""Skończone próby wykonania; świadkowie osiągalności nie są dowodem zupełności.

Trace: G2, S1–S13. Generator dobiera zdarzenia, nie ocenia bezpieczeństwa.
"""

from copy import deepcopy
import json
from pathlib import Path

from .execution import ExplorationBoundary, InputError, StepRejected, execute_step, initial_state, replay


FIXTURES = Path(__file__).resolve().parents[2] / "tests/fixtures"


def exploration_inputs(model):
    return {"checks_ok": {ident: True for ident in model["test_instance"]["items"]},
            "tests_ok": True}


def simulation_evidence():
    return {"simulation": True, "decision": "SIM-E2", "reference": "SIM-E2-review",
            "quote": "Dowód demonstracyjny E2; nie jest decyzją operatora."}


def reachability_scenarios():
    """Jawne ślady testowe od initial; nie wstrzykujemy stanów pośrednich."""
    paths = [FIXTURES / f"wit{number}/scenario.json" for number in range(1, 6)]
    paths += sorted((FIXTURES / "e2").glob("reachability-*.json"))
    return [json.loads(path.read_text()) for path in paths]


def reachability_report(model):
    """Raport tylko dostarczonego korpusu; brak świadka nie dowodzi martwoty."""
    witnesses = {}
    application_witnesses = {}
    runs = []
    for scenario in reachability_scenarios():
        result = replay(model, scenario)
        for index, step in enumerate(result["steps"]):
            if step["outcome"] == "applied":
                ident = step["event"]["transition"]
                candidate = deepcopy(scenario)
                candidate["events"] = candidate["events"][:index + 1]
                if ident not in witnesses or len(candidate["events"]) < len(witnesses[ident]["events"]):
                    witnesses[ident] = candidate
                if step["kind"] == "item":
                    item_type = step["before"]["items"][step["event"]["item"]]["type"]
                    application = f"{ident}:{item_type}"
                    if application not in application_witnesses or len(candidate["events"]) < len(application_witnesses[application]["events"]):
                        application_witnesses[application] = candidate
        last = result["steps"][-1]
        runs.append({"scenario": scenario["id"], "outcome": result["outcome"],
                     "steps": len(result["steps"]), "boundary": last.get("code") == "boundary",
                     "failure": None if result["outcome"] == "completed" else last})
    declared = {t["id"] for kind in ("item", "question", "release") for t in model[f"{kind}_transitions"]}
    return {"witnesses": witnesses, "covered": sorted(witnesses),
            "application_witnesses": application_witnesses,
            "covered_applications": sorted(application_witnesses),
            "missing": sorted(declared - witnesses.keys()), "runs": runs,
            "bounds": deepcopy(model["test_instance"]["bounds"]), "exhaustive": False}


def reachability_witnesses(model):
    return reachability_report(model)["witnesses"]


def exploration_candidates(model, state):
    """Dobór syntaktycznych zdarzeń zależny od stanu, bez kopiowania guardów.

    Obejmuje obie odpowiedzi change, niejednoznaczność, nowych poprzedników,
    przepięcia i pytania ponad limit. Ogranicza jedynie stan źródłowy oraz
    identyfikatory argumentów; dopuszczalność rozstrzyga wykonawca.
    """
    items = state["items"]
    questions = state["questions"]
    fresh = f"generated-{len(questions) + 1}"
    release = state["releases"][state["current_release"]]
    events = []

    def add(transition, **fields):
        actors = transition["actor"]
        for actor in [actors] if isinstance(actors, str) else actors:
            events.append({"transition": transition["id"], "actor": actor,
                           "evidence": simulation_evidence(), **fields})

    for transition in model["item_transitions"]:
        ident = transition["id"]
        for item, record in items.items():
            if record["state"] not in transition["from"]:
                continue
            if ident in {"T05", "T07"}:
                for question in questions:
                    add(transition, item=item, question=question)
            elif ident == "T12":
                add(transition, item=item, question=fresh)
            elif ident == "T14":
                for old in record["depends_on"]:
                    for new in items:
                        if new != old:
                            add(transition, item=item, old_dependency=old, new_dependency=new)
            elif ident == "T00":
                add(transition, item=item)
                for predecessor, previous in items.items():
                    if previous["state"] == "superseded":
                        add(transition, item=item, predecessor=predecessor)
            else:
                add(transition, item=item)

    for transition in model["question_transitions"]:
        if transition["id"] == "P00":
            for blocking in (False, True):
                add(transition, question=fresh, attributes={"blocking": blocking})
            for item, record in items.items():
                if record["state"] != "none":
                    for operation in model["question_semantics"]["change_operations"]:
                        add(transition, question=fresh, attributes={"kind": "change", "about": item,
                            "requested_transition": operation, "blocking": True})
        else:
            for question, record in questions.items():
                if record["state"] not in transition["from"]:
                    continue
                if transition["id"] == "P02":
                    for resolution in (["approved", "rejected"] if record["kind"] == "change" else ["answered"]):
                        add(transition, question=question,
                            inputs={"unambiguous_answer": True, "resolution": resolution})
                else:
                    add(transition, question=question)

    for transition in model["release_transitions"]:
        if release["state"] not in transition["from"]:
            continue
        if transition["id"] == "W03":
            for findings in ([], [fresh], [fresh, fresh + "-second"]):
                add(transition, findings=findings)
        elif transition["id"] == "W05":
            add(transition, question=fresh)
        elif transition["id"] == "W07":
            for item in items:
                add(transition, item=item)
        else:
            add(transition)
    return events


def classify_candidates(model, state):
    """Granica badania jest osobnym wynikiem, nigdy etykietą deadlock.

    Wynik dotyczy wyłącznie kandydatów generatora. Błędy semantyki nie są
    maskowane jako odmowy. Funkcja nie odrzuca kroków łamiących S1–S13.
    """
    result = {"applied": [], "rejected": [], "boundary": [], "input_error": []}
    inputs = exploration_inputs(model)
    for event in exploration_candidates(model, state):
        try:
            step = execute_step(model, state, event, inputs)
        except ExplorationBoundary:
            result["boundary"].append(event)
        except StepRejected:
            result["rejected"].append(event)
        except InputError:
            result["input_error"].append(event)
        else:
            result["applied"].append(step)
    return result


def generator_coverage_report(model):
    """Pokrycie generatora w stanach źródłowych jawnych świadków G2.

    Liczby dotyczą prób kandydatów, nie wszystkich stanów instancji ani
    losowych przebiegów Hypothesis. Świadkowie i generator są rozdzielone.
    """
    counts = {"applied": 0, "rejected": 0, "boundary": 0, "input_error": 0}
    covered = set()
    applications = set()
    boundary_transitions = set()
    witnesses = reachability_witnesses(model)
    for scenario in witnesses.values():
        if len(scenario["events"]) == 1:
            state = initial_state(model)
        else:
            result = replay(model, dict(scenario, events=scenario["events"][:-1]))
            if result["outcome"] != "completed":
                raise ValueError("Prefiks świadka nie jest wykonywalny")
            state = result["final_state"]
        outcomes = classify_candidates(model, state)
        for outcome, entries in outcomes.items():
            counts[outcome] += len(entries)
        for step in outcomes["applied"]:
            candidate = step["event"]
            covered.add(candidate["transition"])
            if step["kind"] == "item":
                applications.add(candidate["transition"] + ":" + state["items"][candidate["item"]]["type"])
        boundary_transitions.update(candidate["transition"] for candidate in outcomes["boundary"])
    return {"source_states": len(witnesses), "counts": counts,
            "covered": sorted(covered), "covered_applications": sorted(applications),
            "boundary_transitions": sorted(boundary_transitions),
            "bounds": deepcopy(model["test_instance"]["bounds"]), "exhaustive": False}
