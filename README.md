# iso-model-state

Projekt rozwija i sprawdza sposób współpracy operatora z agentem: zachowanie kontekstu, kontrolę zatwierdzeń i skutków zmian. [Przyjęta karta celu i zakresu](docs/KARTA-CELU-I-ZAKRESU.md) określa korzyści i pierwsze zastosowanie na jednym rzeczywistym projekcie. Podstawą techniczną jest model stanów produktów pracy według ISO/IEC 29110-5-1-2 (profil Basic), wraz z dowodami poprawności.

Nową sesję z agentem zaczynaj treścią `PROMPT-STARTOWY.md`.

## Wiążące (normatywne)

| Plik | Zawartość |
|---|---|
| `PROMPT-STARTOWY.md` | Wejście do sesji: co czytać, zasady stałe (bez stanu prac) |
| `docs/KARTA-CELU-I-ZAKRESU.md` | Przyjęty cel użytkowy, zakres pierwszego zastosowania i kryteria sukcesu (DEC-PRO-007) |
| `PLAN.md` | Cel, Definition of Done, etapy E0–E5, narzędzia, ryzyka |
| `model/process.yaml` | **Model**: aktorzy, typy produktów, stany, przejścia, warunki, skutki, instancja testowa |
| `docs/WLASCIWOSCI.md` | Właściwości do udowodnienia: struktura, bezpieczeństwo, żywotność, sprawiedliwość, ścieżki świadkowie |
| `docs/INTERPRETACJE.md` | Rejestr interpretacji normy (INT): jak rozstrzygamy jej luki i sprzeczności |
| `docs/STAN.md` | Punkt wznowienia i decyzje DEC-PRO-nnn |
| `docs/WSPOLPRACA.md` | Kontrakt współpracy użytkownika i agenta |

## Informacyjne (niewiążące)

`informative/`: zapis sesji z motywacjami decyzji, wskazanie pełnego tekstu normy i jej niespójności, przegląd vcs-lite, szablon projektu. Przy sprzeczności rozstrzygają pliki wiążące (`informative/README.md`).

Identyfikatory tego repozytorium mają prefiks `PRO`.

## Uruchomienie sprawdzeń E2

`uv run --locked pytest -q` instaluje zależności z `uv.lock` w lokalnym `.venv` i uruchamia testy. Wymagany Python 3.12+. Kolejne uruchomienia z dostępną pamięcią pakietów mogą użyć `--offline`.

Po korekcie DEC-PRO-006 usunięto wykazane wcześniej luki G3/G6: mutant G3 usuwa wszystkie wyjścia z `deferred`, a każde przejście ma adnotacje ISO, łącznie obejmujące 14 efektów PM/SI. Przyjęte uzasadnienie korekty zachowano w `model/proposals/e2-structure.yaml`; testy czytają model wiążący. Przyrost WIT1 dodaje wykonanie ścieżki, testy bramek i wybrane mutanty. Zielony wynik obecnego zestawu nie oznacza zakończenia E2; aktualny wynik jest w `docs/STAN.md`.

`src/isomodel/` wczytuje model, sprawdza część strukturalną G0/G4, buduje projekcję grafu dla G1/G3, raport G5 i audyt adnotacji G6. Projekcja pomija warunki przejść, więc nie dowodzi osiągalności ani braku zakleszczeń całego systemu. Wykonawca interpretuje warunki i skutki potrzebne WIT1/WIT2/WIT4. Pełne G2, pozostała semantyka, maszyna stanów Hypothesis oraz pełny raport mutacji pozostają do wykonania w E2. Hypothesis sprawdza obecnie powtórzone klucze YAML, kombinacje wejść weryfikacji CODE oraz kolejność pytań przy różnych priorytetach.

Starszy skrypt spójności E1: `uv run --locked python scripts/check_model.py`. Wynik tego skryptu nie zastępuje testów E2 ani dowodów E3. Bieżące decyzje i punkt wznowienia: `docs/STAN.md`.

## Wykonywalny WIT1

`uv run --locked --offline python scripts/run_wit1.py --output artifacts/wit1` wykonuje 29 kroków na siedmiu elementach i zapisuje raport Markdown oraz pełny ślad JSON. Osiągnięte `accepted` i wszystkie cytaty dotyczą wyłącznie symulacji. Skrypt sprawdza też siedem prób obejścia bramek i odpowiadające im mutanty.

[Instrukcja, zakres i ograniczenia](examples/wit1/README.md) · [Raport wykonanego przebiegu](examples/wit1/report.md). Nie jest to dowód TLC ani odbiór E2.

## Odrzucenia i pytania — WIT2/WIT4

`uv run --locked --offline python scripts/run_scenario.py --scenario WIT2 --output artifacts/wit2` wykonuje 33 kroki: dwa odrzucenia r1, zatwierdzenie trzeciej propozycji i odbiór. Osobna próba potwierdza blokadę trzeciego odrzucenia.

`uv run --locked --offline python scripts/run_scenario.py --scenario WIT4 --output artifacts/wit4` wykonuje 13 kroków kolejki pytań: odpowiedź niejednoznaczną bez DEC, zachowanie FIFO, rozstrzygnięcia, odłożenie i wznowienie. Powstają trzy demonstracyjne DEC. Reguła blocking_first zachowuje pierwszeństwo pytań blokujących.

[Instrukcja i granice](examples/questions/README.md) · [Raport WIT2](examples/questions/wit2-report.md) · [Raport WIT4](examples/questions/wit4-report.md). Przyrost dodaje dziewięć wykrytych mutantów; pełne G/S/L nadal wymagają dalszych prac.

## Wizualizacja procesu i pakiety wdrożeniowe

[Przewodnik po modelu v0.4 i wsparciu pakietów Aneksu E](informative/WIZUALIZACJA-2026-10-24.md) zawiera diagramy zależności produktów, życia elementu i kolejnych wydań oraz tabelę zakresu wsparcia dziewięciu pakietów. Materiał jest informacyjny.

Diagramy SVG/PNG generuje `uv run --locked python scripts/render_process.py` z bieżącego YAML, przy użyciu zainstalowanego Graphviz (`dot`). Diagramy nie są interaktywnym symulatorem ani dowodem poprawności procesu.
