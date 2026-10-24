"""Czytelny raport wykonania; źródłem są faktyczne kroki wykonawcy.

Trace: WIT1, WIT2, WIT4.
"""


def _cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(result):
    lines = [f"# {_cell(result['scenario'])} — raport wykonania", "",
             "**SYMULACJA.** Cytaty i decyzje są demonstracyjne. Stan `accepted` dotyczy wyłącznie instancji testowej; nie jest odbiorem E2 ani tego repozytorium.", "",
             f"Wynik odtworzenia: **{result['outcome']}**. Liczba zapisanych kroków: **{len(result['steps'])}**.", "",
             "Wyniki kontroli i jednoznaczność odpowiedzi są danymi wejściowymi tych kroków, które ich wymagają. Wykonawca nie uruchamia testów rzeczywistego produktu ani nie klasyfikuje treści odpowiedzi.", "",
             "## Tożsamość wejść i wykonawcy", "",
             f"- Model: v{result['model_version']}; SHA-256 danych: `{result['model_sha256']}`.",
             f"- Scenariusz SHA-256: `{result['scenario_sha256']}`."]
    for key, value in result.get("provenance", {}).items():
        lines.append(f"- {key}: `{value}`.")
    lines += ["", "## Przebieg", "",
              "Warunki są rozwinięte w kolejnej tabeli. Pełne stany przed i po, dowody oraz dane wejściowe znajdują się w wygenerowanym `trace.json`.", "",
              "| Krok | Aktor | Przejście | Cel | Stan przed → po | Ocena warunku | Wynik | Nowe DEC pytań |",
              "|---|---|---|---|---|---|---|---|"]
    guards = {}
    for step in result["steps"]:
        event = step["event"]
        before, after = step["before"], step["after"]
        item = event.get("item")
        if "question" in event:
            ident = event["question"]
            prior = before["questions"].get(ident, {"state": "none"})
            following = after["questions"].get(ident, {"state": "none"})
            target = ident
        elif item is not None:
            prior, following = before["items"][item], after["items"][item]
            target = item
        else:
            prior = before["releases"][before["current_release"]]
            following = after["releases"][after["current_release"]]
            target = f"wydanie {before['current_release']}"
        verdict = {True: "spełniony", False: "niespełniony", None: "nie oceniono"}[step["guard_result"]]
        values = [step["step"], event.get("actor"), event.get("transition"), target,
                  f"{prior['state']} → {following['state']}", verdict, step["outcome"], len(step.get("records", []))]
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
            fallback = "odpowiedź testowa" if "question" in step["event"] else "protokół testowy"
            reference = evidence.get("decision", evidence.get("reference", fallback))
            lines.append(f"| {step['step']} | {_cell(reference)} | {_cell(evidence.get('quote', ''))} |")
    probes = result.get("gate_probes", [])
    if probes:
        lines += ["", "## Próby obejścia bramek i wybrane mutanty", "",
                  "Każdą próbę rozpoczyna odtworzenie poprawnego prefiksu. Model bazowy spełnia oczekiwanie, a pojedyncza celowa zmiana reguły je narusza: dopuszcza zabroniony krok, zmienia kolejność lub zapis decyzji. To potwierdza czułość wyroczni, nie pełne pokrycie mutacyjne E2 ani dowód żywotności.", "",
                  "| Mutant | Właściwość | Model bazowy | Po uszkodzeniu reguły | Wykryty |", "|---|---|---|---|---|"]
        for probe in probes:
            lines.append("| " + " | ".join(_cell(probe[k]) for k in ["id", "property", "baseline_code", "mutant_outcome", "detected"]) + " |")
    state = result["final_state"]
    release = state["releases"][state["current_release"]]
    lines += ["", "## Stan końcowy", "",
              f"Bieżące wydanie: {release['number']}, `{release['state']}`. `next_release_required = {str(state['next_release_required']).lower()}`.", "",
              "| Element | Stan | Wersja | Suspect | Odrzucenia |", "|---|---|---|---|---|"]
    for ident, item in state["items"].items():
        lines.append(f"| {ident} | {item['state']} | {item['version']} | {str(item['suspect']).lower()} | {item['rejections']} |")
    if state["questions"]:
        lines += ["", "## Pytania", "", "| ID | Stan | Blokujące | Kolejność zgłoszenia |", "|---|---|---|---|"]
        for ident, question in state["questions"].items():
            lines.append(f"| {_cell(ident)} | {question['state']} | {str(question['blocking']).lower()} | {question['age']} |")
        lines += ["", "## Utworzone decyzje demonstracyjne", "",
                  "Zapisy pochodzą ze skutku `record DEC with user quote`; kolumna «Nowe DEC pytań» pokazuje, w którym kroku powstały. Cytat przy P03 jest dowodem odpowiedzi niejednoznacznej, bez utworzenia DEC. Cytowane zatwierdzenia produktów i protokół odbioru mają osobne dowody.", "",
                  "| Krok | ID | Pytanie | Cytat |", "|---|---|---|---|"]
        for record in result.get("records", []):
            lines.append(f"| {record['step']} | {_cell(record['id'])} | {_cell(record['question'])} | {_cell(record['quote'])} |")
    lines += ["", "## Granice wyniku", "",
              f"Wykonano podaną ścieżkę {_cell(result['scenario'])} w E2. Nie wygenerowano świadka przez TLC, nie udowodniono wszystkich G/S/L i nie zakończono E2. Obsługa zmian produktów i kolejnych wydań pozostaje przed nami. Weryfikacja roli R w symulacji nie jest niezależnym przeglądem implementacji.", ""]
    return "\n".join(lines)
