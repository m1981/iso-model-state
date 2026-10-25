"""Predykaty grafu roboczego; polityka użycia pozostaje w guard modelu.

Trace: G0, S12, WIT3.
"""


def _valid_ids(items, dependencies):
    return (isinstance(dependencies, (list, set))
            and all(isinstance(i, str) and i in items for i in dependencies)
            and len(dependencies) == len(set(dependencies)))


def dependency_types_ok(model, state, element, dependencies):
    items = state["items"]
    if not _valid_ids(items, dependencies) or element["type"] not in model["item_types"]:
        return False
    return {items[i]["type"] for i in dependencies} == set(model["item_types"][element["type"]]["depends_on"])


def acyclic_dependencies(state, element, dependencies):
    """Sprawdza cały graf z podmienionymi krawędziami e, bez zmiany stanu."""
    items = state["items"]
    graph = {i: dependencies if i == element["id"] else value["depends_on"] for i, value in items.items()}
    if not all(_valid_ids(items, edges) for edges in graph.values()):
        return False
    visited, visiting = set(), set()

    def visit(ident):
        if ident in visiting:
            return False
        if ident in visited:
            return True
        visiting.add(ident)
        for dependency in graph[ident]:
            if not visit(dependency):
                return False
        visiting.remove(ident)
        visited.add(ident)
        return True

    return all(visit(ident) for ident in graph)
