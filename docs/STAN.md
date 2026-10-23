# Stan prac

Nadpisywany na końcu każdej sesji. Zaktualizowano: 2026-10-23.

## Gdzie jesteśmy

- **Etap:** E1, czeka na przegląd użytkownika (bramka).
- **Ostatnio zrobione:** plan (`PLAN.md`), model v0.1 (`model/process.yaml`), właściwości G/S/L (`docs/WLASCIWOSCI.md`), interpretacje INT-001–016.
- **Następny krok:** po akceptacji E1 — E2: wczytanie modelu i sprawdzenia grafowe G0–G6 w pytest.

## Decyzje

| ID | Decyzja | Źródło |
|---|---|---|
| DEC-PRO-001 | DoD 1–10 i stos narzędzi (YAML, pytest z Hypothesis, TLA+ z TLC, odtworzenie historii vcs-lite). | Użytkownik 2026-10-23: „d1 tak” |

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
- W01: elementy odłożone, zastąpione i wycofane wypadają z zakresu wydania. Bez tego jeden odłożony element blokowałby wydanie na zawsze (zakleszczenie, L1).
