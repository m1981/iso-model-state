# iso-model-state

Model stanów produktów pracy według ISO/IEC 29110-5-1-2 (profil Basic) dla projektów prowadzonych przez użytkownika z agentem LLM, wraz z dowodami poprawności.

Nową sesję z agentem zaczynaj treścią `PROMPT-STARTOWY.md`.

## Wiążące (normatywne)

| Plik | Zawartość |
|---|---|
| `PROMPT-STARTOWY.md` | Wejście do sesji: co czytać, zasady stałe (bez stanu prac) |
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

Po korekcie DEC-PRO-006 model v0.4 ma **31 przechodzących testów**. Usunięto wykazane wcześniej luki G3/G6: mutant G3 usuwa wszystkie wyjścia z `deferred`, a każde przejście ma adnotacje ISO, łącznie obejmujące 14 efektów PM/SI. Przyjęte uzasadnienie korekty zachowano w `model/proposals/e2-structure.yaml`; testy czytają model wiążący. Zielony wynik obecnego zestawu nie oznacza zakończenia E2.

`src/isomodel/` wczytuje model, sprawdza część strukturalną G0/G4, buduje projekcję grafu dla G1/G3, raport G5 i audyt adnotacji G6. Projekcja pomija warunki przejść, więc nie dowodzi osiągalności ani braku zakleszczeń całego systemu. G2, interpretacja warunków i skutków, niezmienniki przez Hypothesis oraz pełny raport mutacji pozostają do wykonania w E2. Obecne użycie Hypothesis sprawdza jedynie odrzucanie powtórzonych kluczy YAML.

Starszy skrypt spójności E1: `uv run --locked python scripts/check_model.py`. Wynik tego skryptu nie zastępuje testów E2 ani dowodów E3. Bieżące decyzje i punkt wznowienia: `docs/STAN.md`.

## Wizualizacja procesu i pakiety wdrożeniowe

[Przewodnik po modelu v0.4 i wsparciu pakietów Aneksu E](informative/WIZUALIZACJA-2026-10-24.md) zawiera diagramy zależności produktów, życia elementu i kolejnych wydań oraz tabelę zakresu wsparcia dziewięciu pakietów. Materiał jest informacyjny.

Diagramy SVG/PNG generuje `uv run --locked python scripts/render_process.py` z bieżącego YAML, przy użyciu zainstalowanego Graphviz (`dot`). Diagramy nie są interaktywnym symulatorem ani dowodem poprawności procesu.
