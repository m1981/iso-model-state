# Stan prac

Nadpisywany na końcu każdej sesji. Zaktualizowano: 2026-10-23.

## Gdzie jesteśmy

- **Etap:** E1, czeka na przegląd użytkownika (bramka).
- **Ostatnio zrobione:** model v0.2 z angielskimi identyfikatorami (DEC-PRO-002); właściwości (`docs/WLASCIWOSCI.md`) i interpretacje (`docs/INTERPRETACJE.md`) zaktualizowane do nowych nazw; spójność modelu sprawdzona skryptem (stany, aktorzy, zbiory stanów w warunkach, typy w instancji, unikalność 25 ID przejść).
- **Następny krok:** po akceptacji E1 — E2: wczytanie modelu i sprawdzenia grafowe G0–G6 w pytest.

## Decyzje

| ID | Decyzja | Źródło |
|---|---|---|
| DEC-PRO-001 | DoD 1–10 i stos narzędzi (YAML, pytest z Hypothesis, TLA+ z TLC, odtworzenie historii vcs-lite). | Użytkownik 2026-10-23: „d1 tak” |
| DEC-PRO-002 | Kody, identyfikatory, atrybuty i kod źródłowy po angielsku w terminologii normy; proza, opisy i cytaty po polsku. Zmienia: `model/process.yaml` (v0.1 → v0.2), `docs/WSPOLPRACA.md`, szablon projektu. Przejrzane: `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `README.md`. | Użytkownik 2026-10-23: „d1 tak wykonaj rzetelenie i push” |

## Repozytorium

- Praca na gałęzi `e1-model`; `main` bez zmian do zgody użytkownika.

## Sprawy otwarte

| Sprawa | Właściciel | Następny krok |
|---|---|---|
| Przegląd modelu E1 | użytkownik | akceptacja albo uwagi |
| Instalacja Javy i TLA+ (E3) | użytkownik | zgoda przed E3 |
| Dostęp do historii vcs-lite (E4) | użytkownik | zgoda przed E4 |

## Wykryte przy pisaniu modelu (decyzje agenta)

- T11 dostał warunek: przegląd „bez wpływu” niemożliwy, gdy zależność została wycofana lub zastąpiona. Bez tego agent mógłby zostawić aktywny AT wskazujący wycofane REQ (S6). To dokładnie sprawa Beyond Compare.
- T12 przy zgłoszeniu zmiany tworzy pytanie blokujące (`blocking = true`), żeby wydanie nie przeszło z niezałatwionym zgłoszeniem.
- Nazwy w modelu v0.2: typ `KARTA` → `PLAN` (umowa i plan, WP.02 i WP.10), `KOD` → `CODE`, ścieżki świadkowie ŚW → WIT.
- W01: elementy odłożone, zastąpione i wycofane wypadają z zakresu wydania. Bez tego jeden odłożony element blokowałby wydanie na zawsze (zakleszczenie, L1).
