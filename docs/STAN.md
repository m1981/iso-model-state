# Stan prac

Nadpisywany na końcu każdej sesji. Zaktualizowano: 2026-10-23, koniec sesji założycielskiej.

## Gdzie jesteśmy

- **Etap:** E1, czeka na przegląd użytkownika (bramka).
- **Ostatnio zrobione:**
  - model v0.2 z angielskimi identyfikatorami (DEC-PRO-002); spójność sprawdzona skryptem (stany, aktorzy, zbiory stanów w warunkach, typy w instancji, unikalność 25 ID przejść);
  - `PROMPT-STARTOWY.md` do przekazania sesji;
  - folder `informative/` (niewiążący): zapis sesji z motywacjami, wskazanie pełnej normy i jej niespójności, przegląd vcs-lite, szablon projektu.
- **Następny krok:** zapytać użytkownika o bramkę E1 (decyzja niżej). Po akceptacji E2: wczytanie modelu i sprawdzenia grafowe G0–G6 w pytest.

## Decyzja czekająca na użytkownika

D1. Przyjąć model v0.2 jako podstawę E2, w szczególności: DES i CODE bez zatwierdzenia użytkownika, ale do podważenia (INT-013); `MAX_REJECTIONS = 2`, potem eskalacja (INT-011); linię bazową (T04) wyzwala zawsze użytkownik. Na tych decyzjach opierają się S1, S2 i L4. Najszybszy przegląd: ścieżki WIT1–WIT4 w `docs/WLASCIWOSCI.md`, potem T00–T13.

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
| Przegląd modelu E1 (D1 wyżej) | użytkownik | akceptacja albo uwagi |
| REQ-210 (wycofane pojęcia) i REQ-211 (rejestr decyzji agenta) dla szablonu | użytkownik | decyzja; opis w `informative/SESJA-2026-10-23.md` §5 |
| Instalacja Javy i TLA+ (E3) | użytkownik | zgoda przed E3 |
| Dostęp do historii vcs-lite (E4) | użytkownik | zgoda przed E4 |
| Porządki w vcs-lite według `informative/PRZEGLAD-VCS-LITE.md` | użytkownik | decyzja, czy i kiedy |

## Decyzje agenta w tej sesji (do podważenia)

- T11 dostał warunek: przegląd „bez wpływu” niemożliwy, gdy zależność została wycofana lub zastąpiona. Bez tego aktywny AT mógłby wskazywać wycofane REQ (S6), jak w sprawie Beyond Compare.
- T12 przy zgłoszeniu zmiany tworzy pytanie blokujące, żeby wydanie nie przeszło z niezałatwionym zgłoszeniem.
- W01: elementy odłożone, zastąpione i wycofane wypadają z zakresu wydania; inaczej jeden odłożony element blokowałby wydanie na zawsze (L1).
- Nazwy w v0.2: `KARTA` → `PLAN` (WP.02 i WP.10), `KOD` → `CODE`, ścieżki świadkowie ŚW → WIT.
- Materiały niewiążące w `informative/` z regułą pierwszeństwa; programy sprawdzające nie czytają tego folderu.
