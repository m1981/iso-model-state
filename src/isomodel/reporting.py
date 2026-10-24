"""Czytelny raport wykonania; źródłem są faktyczne kroki wykonawcy.

Trace: WIT1.
"""


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(result):
    lines = ["# WIT1 — raport wykonania", "",
             "**SYMULACJA.** Cytaty i decyzje są demonstracyjne. Stan `accepted` dotyczy wyłącznie instancji testowej; nie jest odbiorem E2 ani tego repozytorium.", "",
             f"Wynik odtworzenia: **{result['outcome']}**. Liczba zapisanych kroków: **{len(result['steps'])}**.", "",
             "`checks_ok(e)` i `tests_ok` są jawnymi założeniami wejściowymi. Wykonawca nie uruchamia testów rzeczywistego produktu.", "",
             "## Tożsamość wejść i wykonawcy", "",
             f"- Model: v{result['model_version']}; SHA-256 danych: `{result['model_sha256']}`.",
             f"- Scenariusz SHA-256: `{result['scenario_sha256']}`."]
    for key, value in result.get("provenance", {}).items():
        lines.append(f"- {key}: `{value}`.")
    lines += ["", "## Przebieg", "",
              "Warunki są rozwinięte w kolejnej tabeli. Pełne stany przed i po, dowody oraz dane wejściowe znajdują się w wygenerowanym `trace.json`.", "",
              "| Krok | Aktor | Przejście | Cel | Stan przed → po | Ocena warunku | Wynik |",
              "|---|---|---|---|---|---|---|"]
    guards = {}
    for step in result["steps"]:
        event = step["event"]
        before, after = step["before"], step["after"]
        item = event.get("item")
        if item is not None:
            prior, following = before["items"][item], after["items"][item]
            target = item
        else:
            prior = before["releases"][before["current_release"]]
            following = after["releases"][after["current_release"]]
            target = f"wydanie {before['current_release']}"
        verdict = {True: "spełniony", False: "niespełniony", None: "nie oceniono"}[step["guard_result"]]
        values = [step["step"], event.get("actor"), event.get("transition"), target,
                  f"{prior['state']} → {following['state']}", verdict, step["outcome"]]
        lines.append("| " + " | ".join(_cell(value) for value in values) + " |")
        if "guard" in step:
            guards[event["transition"]] = step["guard"]
        if "reason" in step:
            lines += ["", f"Przyczyna zatrzymania: {_cell(step['reason'])}", ""]
    lines += ["", "## Warunki odczytane z YAML", "", "| Przejście | Warunek |", "|---|---|"]
    for ident, guard in guards.items():
        lines.append(f"| {ident} | `{_cell(guard)}` |")
    lines += ["", "## Dowody demonstracyjne", "", "| Krok | Odwołanie | Cytat |", "|---|---|---|"]
    for step in result["steps"]:
        evidence = step["event"].get("evidence")
        if evidence:
            reference = evidence.get("decision", evidence.get("reference", "protokół testowy"))
            lines.append(f"| {step['step']} | {_cell(reference)} | {_cell(evidence.get('quote', ''))} |")
    probes = result.get("gate_probes", [])
    if probes:
        lines += ["", "## Próby obejścia bramek i wybrane mutanty", "",
                  "Każdą próbę rozpoczyna odtworzenie poprawnego prefiksu. Model bazowy musi odmówić, a pojedyncza celowa zmiana reguły dopuścić ten sam krok. To potwierdza czułość wyroczni, nie pełne pokrycie mutacyjne E2.", "",
                  "| Mutant | Właściwość | Poprawny model: odmowa | Po uszkodzeniu reguły | Wykryty |", "|---|---|---|---|---|"]
        for probe in probes:
            lines.append("| " + " | ".join(_cell(probe[k]) for k in ["id", "property", "baseline_code", "mutant_outcome", "detected"]) + " |")
    state = result["final_state"]
    release = state["releases"][state["current_release"]]
    lines += ["", "## Stan końcowy", "",
              f"Bieżące wydanie: {release['number']}, `{release['state']}`. `next_release_required = {str(state['next_release_required']).lower()}`.", "",
              "| Element | Stan | Wersja | Suspect |", "|---|---|---|---|"]
    for ident, item in state["items"].items():
        lines.append(f"| {ident} | {item['state']} | {item['version']} | {str(item['suspect']).lower()} |")
    lines += ["", "## Granice wyniku", "",
              "Wykonano podaną ścieżkę WIT1 w E2. Nie wygenerowano świadka przez TLC, nie udowodniono wszystkich G/S/L i nie zakończono E2. Obsługa pytań, zmian i kolejnych wydań pozostaje przed nami. Weryfikacja roli R w symulacji nie jest niezależnym przeglądem implementacji.", ""]
    return "\n".join(lines)
