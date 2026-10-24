"""Projekcja grafu i audyt jawnych adnotacji, bez wykonywania guard/effects.

Trace: G1, G3, G5, G6, S10.
"""

import networkx as nx


def state_graph(model, kind):
    """Graf jednego rekordu; pomija warunki oraz tworzenie innej instancji."""
    graph = nx.MultiDiGraph()
    graph.add_nodes_from(model[f"{kind}_states"])
    graph.add_node(model[f"{kind}_variables"]["state"]["initial"])
    for transition in model[f"{kind}_transitions"]:
        if transition.get("target") == "new_release":
            continue
        for source in transition["from"]:
            destination = source if transition["to"] == "=" else transition["to"]
            graph.add_edge(source, destination, transition=transition["id"])
    return graph


def unreachable_states(model, kind):
    """Warunek konieczny G1; osiągalność w tej projekcji nie dowodzi G1."""
    initial = model[f"{kind}_variables"]["state"]["initial"]
    reachable = nx.descendants(state_graph(model, kind), initial) | {initial}
    return set(model[f"{kind}_states"]) - reachable


def dead_ends(model, kind):
    """Warunek konieczny G3; wychodzące łuki mogą mieć niespełnialne warunki."""
    graph = state_graph(model, kind)
    return {name for name, state in model[f"{kind}_states"].items() if not state["final"] and graph.out_degree(name) == 0}


def completeness_matrix(model, kind):
    """Raport G5: from jawnie wyklucza pozostałe pary; guard nadal obowiązuje."""
    states = set(model[f"{kind}_states"]) | {model[f"{kind}_variables"]["state"]["initial"]}
    matrix = {}
    for state in sorted(states):
        for transition in model[f"{kind}_transitions"]:
            result = "forbidden_by_source"
            if state in transition["from"]:
                target = "new" if transition.get("target") == "new_release" else "current"
                result = f"{target}_instance_if_guard"
            matrix[(state, transition["id"])] = result
    return matrix


def iso_coverage(model):
    """Audyt G6: zadanie ISO nie jest automatycznie adnotacją efektu procesu."""
    required = {f"{process}.O{number}" for process in ("PM", "SI") for number in range(1, 8)}
    covered = {}
    missing_transition_iso = []
    for kind in ("item", "question", "release"):
        for transition in model[f"{kind}_transitions"]:
            references = transition.get("iso", [])
            if not references:
                missing_transition_iso.append(transition["id"])
            for reference in sorted(set(references) & required):
                covered.setdefault(reference, []).append(transition["id"])
    return {
        "covered": covered,
        "missing_outcomes": sorted(required - covered.keys()),
        "missing_transition_iso": missing_transition_iso,
    }
