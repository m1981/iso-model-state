"""Trzy informacyjne widoki modelu; renderer nie wykonuje guard/effects.

Wymaga Graphviz (dot). Uruchomienie: uv run --locked python scripts/render_process.py
Trace: DEC-PRO-006, WIT1, WIT5. Źródło danych: model/process.yaml.
"""

import json
from pathlib import Path
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[1]


def quote(value):
    return json.dumps(str(value), ensure_ascii=False)


def node(ident, label, **attributes):
    attributes = {"label": label, **attributes}
    return f'{ident} [' + ", ".join(f"{key}={quote(value)}" for key, value in attributes.items()) + "];"


def edge(source, target, label="", **attributes):
    attributes = {"label": label, **attributes}
    return f'{source} -> {target} [' + ", ".join(f"{key}={quote(value)}" for key, value in attributes.items()) + "];"


def render(name, title, lines, output):
    source = "\n".join([
        "digraph process {",
        'graph [rankdir=LR, bgcolor="white", pad=0.35, nodesep=0.45, ranksep=0.7, fontname="Helvetica", fontsize=18, labelloc=t];',
        'node [shape=box, style="rounded,filled", fillcolor="#eaf1f8", color="#587491", fontname="Helvetica", fontsize=12, margin="0.18,0.12"];',
        'edge [fontname="Helvetica", fontsize=10, color="#587491", arrowsize=0.7];',
        f"label={quote(title)};", *lines, "}",
    ])
    for extension in ("svg", "png"):
        subprocess.run(["dot", f"-T{extension}", "-o", str(output / f"{name}.{extension}")], input=source, text=True, check=True)
    print(output / f"{name}.svg")


def main():
    model = yaml.safe_load((ROOT / "model/process.yaml").read_text())
    version = model["version"]
    output = ROOT / "informative" / f"visuals-v{version}"
    output.mkdir(exist_ok=True)
    transitions = {t["id"]: t for kind in ("item", "question", "release") for t in model[f"{kind}_transitions"]}

    names = {"PLAN": "Plan i umowa", "REQ": "Wymagania", "AT": "Scenariusze akceptacyjne", "DES": "Projekt rozwiązania", "CODE": "Kod"}
    lines = []
    for ident, item_type in model["item_types"].items():
        gate = "zatwierdzenie U" if item_type["requires_approval"] else "do podważenia przez U"
        lines.append(node(ident, f"{ident}\n{names[ident]}\n{gate}"))
        lines.extend(edge(dependency, ident) for dependency in item_type["depends_on"])
    render("dependencies", f"Model v{version} · zależności produktów\nStrzałka: podstawa → element zależny. U = użytkownik.", lines, output)

    names = {"none": "nie istnieje", "draft": "szkic", "verified": "zweryfikowany", "approved": "zatwierdzony", "baselined": "w linii bazowej"}
    lines = [node(ident, f"{ident}\n{label}", fillcolor="#dcf3e5" if ident == "baselined" else "#eaf1f8") for ident, label in names.items()]
    for ident in ("T00", "T01", "T02", "T03", "T04"):
        transition = transitions[ident]
        for source in transition["from"]:
            label = f'{ident} · {transition["actor"]}'
            if ident == "T02":
                label += "\nPLAN / REQ / AT"
            elif ident == "T03":
                label += f'\nmax {model["parameters"]["MAX_REJECTIONS"]} odrzucenia'
            elif ident == "T04" and source == "verified":
                label += "\nDES / CODE"
            lines.append(edge(source, transition["to"], label, tooltip=transition["guard"]))
    render("item-lifecycle", f"Model v{version} · główny przebieg elementu\nA = autor-agent, U = użytkownik. Zmiany i wycofanie opisano w przewodniku.", lines, output)

    names = {"in_preparation": "w przygotowaniu", "ready": "gotowe", "reviewed": "po przeglądzie", "accepted": "odebrane · niezmienne"}
    lines = ["subgraph cluster_current {", 'label="Wydanie n";', 'color="#c5d3df";']
    for ident, label in names.items():
        lines.append(node(ident, f"{ident}\n{label}", fillcolor="#dcf3e5" if ident == "accepted" else "#eaf1f8", peripheries=2 if ident == "accepted" else 1))
    for ident in ("W01", "W02", "W03", "W04", "W05"):
        transition = transitions[ident]
        lines.append(edge(transition["from"][0], transition["to"], f'{ident} · {transition["actor"]}', tooltip=transition["guard"]))
    lines.append("}")
    lines.append(node("working_change", "Zmiana produktów roboczych\nT05–T10 w zakresie\nlub nowe suspect w zakresie", fillcolor="#fff2d9"))
    lines.append(node("next_release", "Wydanie n + 1\nin_preparation\nnowy rekord", fillcolor="#dcf3e5"))
    lines.append(edge("accepted", "working_change", "późniejsze zdarzenie\nnie zmiana starego rekordu", style="dashed"))
    next_transition = transitions["W06"]
    if next_transition.get("target") != "new_release":
        raise ValueError("Widok wymaga W06 tworzącego nowy rekord")
    lines.append(edge("working_change", "next_release", f'W06 · {next_transition["actor"]}\nobowiązkowy następny krok', tooltip=next_transition["guard"]))
    render("releases", f"Model v{version} · odbiór i następne wydanie\nR = niezależny recenzent. Zielony rekord n pozostaje bez zmian.", lines, output)


if __name__ == "__main__":
    main()
