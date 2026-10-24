# Stan prac

Nadpisywany na końcu każdej sesji. Zaktualizowano: 2026-10-24, akceptacja E1 i pierwszy przebieg E2.

## Gdzie jesteśmy

- **Etap:** E2 rozpoczęty; bramka E1 przyjęta przez DEC-PRO-005. Model v0.3 ma status approved jako podstawa testów i implementacji.
- **Ostatnio zrobione:**
  - DEC-PRO-005: użytkownik przyjął v0.3 i przejście do E2; status modelu, właściwości i interpretacji zaktualizowany;
  - pierwszy przyrost E2: wczytywanie YAML, część walidacji G0/G4, projekcja grafu G1/G3, macierz G5 i audyt adnotacji G6;
  - 29 testów przechodzi, 2 kryteria modelu nie przechodzą (G3 i G6); propozycja korekty przygotowana i sprawdzona na kopii danych;
  - DEC-PRO-003: numerowane wydania, migawka i protokół w W04, niezmienność odebranego rekordu, W06 otwierające następne wydanie, granica dwóch wydań;
  - DEC-PRO-004: T10 dołączone do unieważniania gotowości przed odbiorem i wyzwalania W06 po odbiorze;
  - S7 zastąpione przez S7a i S7b, dodane S10 i mutanty; `done`, L1, L5 i S8 uwzględniają tożsamość wydania; dodane WIT5 i przypadek T10;
  - INT-017 z odniesieniami do Tabeli 12, SI.06.05–SI.06.06, PM.04.01–PM.04.02 oraz informacyjnego Aneksu A (A.1–A.2, A.9.4);
  - odtwarzalny skrypt `scripts/check_model.py` do sprawdzenia spójności danych i odwołań E1; nie jest implementacją symulatora E2.
- **Następny krok:** decyzja o korekcie G3/G6 poniżej; po zgodzie zastosować propozycję jako v0.4 z nową DEC i kontynuować E2. Nie uznawać E2 za zakończone.

## Bramka E1

Zamknięta przez DEC-PRO-005: użytkownik przyjął model v0.3 i przejście do E2.

## Decyzje

| ID | Decyzja | Źródło | Zmienia | Przejrzane |
|---|---|---|---|---|
| DEC-PRO-001 | DoD 1–10 i stos narzędzi (YAML, pytest z Hypothesis, TLA+ z TLC, odtworzenie historii vcs-lite). | Użytkownik 2026-10-23: „d1 tak” | — | — |
| DEC-PRO-002 | Kody, identyfikatory, atrybuty i kod źródłowy po angielsku w terminologii normy; proza, opisy i cytaty po polsku. | Użytkownik 2026-10-23: „d1 tak wykonaj rzetelenie i push” | `model/process.yaml` (v0.1 → v0.2), `docs/WSPOLPRACA.md`, szablon projektu. | `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `README.md`. |
| DEC-PRO-003 | Wariant A: odebrane wydanie jest niezmienne; odbiór dotyczy stanu z chwili podpisu, jak tag v1.0. Zmiany po odbiorze należą do następnego wydania. W06 tworzy nowy rekord, nie cofa starego. Odrzucone B: zakaz zmian po odbiorze blokuje projekt; C: cofanie accepted do in_preparation fałszuje protokół odbioru. | Użytkownik 2026-10-24: „d1 a” (cytat wskazany przez użytkownika do zapisu). | `model/process.yaml` (v0.2 → v0.3): `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7` → `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7`, `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo T00–T13, P00–P05, W01–W06, G0–G6, S1–S10, F1–F3, L1–L5, WIT1–WIT5, `README.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`, lista kontrolna w `informative/szablon-projektu/docs/SPEC.md` i materiały informacyjne. |
| DEC-PRO-004 | Wznowienie odłożonego elementu przez T10 także zmienia kompletność zakresu. T10 wywołuje invalidate_release: przy ready/reviewed wraca do in_preparation, przy accepted wymusza W06 bez zmiany odebranego rekordu. Rozszerza listę wyzwalaczy z DEC-PRO-003 o T10. | Użytkownik 2026-10-24: „Tak, uwzględnij T10” | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo `invalidate_release`, `S7b`, `S10`, `L1`, `L5`, T09 i bramki U. |
| DEC-PRO-005 | Przyjęcie modelu v0.3 i właściwości jako podstawy E2; zatwierdzenie INT-001–INT-016 i opisów WIT1–WIT5. Nie stanowi dowodu G/S/L ani odbioru całego projektu. | Użytkownik 2026-10-24: „przyjmuje” | `model/process.yaml`: status; `docs/WLASCIWOSCI.md`: status; `docs/INTERPRETACJE.md`: status INT-001–INT-016; `PLAN.md`: stan etapów; `docs/STAN.md`: zamknięcie bramki E1; `PROMPT-STARTOWY.md`: gałąź pobierana ze stanu prac. | `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `docs/STAN.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`; treść modelu i właściwości bez zmiany. |

## Decyzja czekająca na użytkownika — korekta G3/G6

D1. Zastosować propozycję `model/proposals/e2-structure.yaml`: uzupełnić adnotacje ISO bez zmiany zachowania procesu i zastąpić nieskutecznego mutanta G3 usunięciem T07, T08 i T10. Dlaczego: obecny mutant G3 nie psuje właściwości, a G6 nie ma jawnych odwołań dla 13 z 14 wymaganych efektów. Co, jeśli nie: pozostają dwa czerwone kryteria modelu i E2 nie może przejść odbioru. Zmienia: `model/process.yaml` (adnotacje iso, v0.3 → v0.4), G3 (mutant) i doprecyzowanie granic G6 w `docs/WLASCIWOSCI.md`; rejestr INT/DEC i powiązane testy. Przejrzane: T00–T13, P00–P05, W01–W06, G3/G6, DoD 6/8, źródło ISO rozdziały 6.2, 7.2, PM.01.09–PM.01.11, PM.02.05, PM.03.03–PM.03.04.

Propozycja jest niewiążąca do decyzji. Nie zmienia from/to/actor/guard/effects ani polityki wydań. G6 jest indeksem śledzenia powiązań, nie dowodem wykonania każdej składowej efektu ISO; ograniczenia i uzasadnienie każdego powiązania zapisano w propozycji.

### Wyniki pierwszego przyrostu E2

- `uv run --locked pytest -q`: **29 passed, 2 failed**. Nie ma ukrytych xfail ani pominiętych testów.
- G3: usunięcie tylko T10 zostawia wyjścia `deferred → superseded` (T07) i `deferred → withdrawn` (T08, bezwarunkowe). Dlatego mutant z dokumentu przeżywa. Kandydat usuwający T07/T08/T10 jest wykrywany.
- G6: jawnie wskazane jest tylko SI.O7 (W02/W03). Brakuje PM.O1–PM.O7 i SI.O1–SI.O6; P03/P05 nie mają pola iso. Odwołania do zadań ISO nie mają w danych mapowania na efekty, więc program nie dopowiada takiego mapowania.
- Kopia z proponowanymi adnotacjami ma wszystkie 14 efektów i iso w każdym przejściu. Usunięcie W04 z tej kopii gubi PM.O2, zgodnie z mutantem G6. Wszystkie pola zachowania przejść pozostają identyczne.
- TDD: przed walidacją testy powtórzonego klucza YAML, nieznanej zależności i wielokrotnego celu przejścia zakończyły się `DID NOT RAISE ModelError` (3 failed, 1 passed); po implementacji przechodzą. Wstępny błąd importu brakującego modułu nie jest liczony jako dowód właściwego czerwonego testu.
- Projekcje grafowe ignorują guard/effects: ich pozytywny wynik jest tylko warunkiem koniecznym G1/G3. G2, wykonanie warunków i skutków, właściwości bezpieczeństwa przez Hypothesis i pełna mutacja nie są jeszcze zrealizowane. Hipoteza o bezpieczeństwie modelu nie została potwierdzona.
- Zależności zgodne z DEC-PRO-001: PyYAML 6.0.3, networkx 3.6.1, pytest 9.1.1, Hypothesis 6.151.10, zapisane w pyproject.toml i uv.lock; instalacja lokalna w .venv.

## Weryfikacja i lista kontrolna zmiany

- Zmienione definicje i ich zależne zaktualizowano w jednej zmianie. S7 jest wycofaną definicją zastąpioną przez S7a i S7b; wzmianki historyczne pozostają jawnie oznaczone.
- Lista kontrolna ze specyfikacji szablonu zastosowana do istniejących artefaktów tego repozytorium: model, właściwości, scenariusze WIT, interpretacje, plan i ryzyka. Osobnych REQ/UC/DES/AT/VER, kodu produktu ani instrukcji UI w tym projekcie jeszcze nie ma; odpowiedniki w `informative/szablon-projektu/` są niewiążącą migawką do E5, nie definicjami obecnego modelu.
- Polecenie: `uv run --offline --with pyyaml python scripts/check_model.py` (PyYAML 6.0.3). Wynik: **330 sprawdzeń spójności OK**, 26 przejść, 7 elementów, granica 2 wydań; `git diff --check` bez błędów.
- Trzy próby na tymczasowych błędnych plikach potwierdziły diagnostykę skryptu: nieznany aktor W06, brak `invalidate_release` w T10 i powtórzony klucz YAML są odrzucane z właściwego powodu. To sprawdzenie narzędzia E1, nie raport mutantów właściwości z DoD 6.
- Zakres skryptu: unikalność kluczy YAML i ID, stany, aktorzy, zbiory stanów w warunkach, typy i zależności instancji, inicjalizacja i cel W06, definicje właściwości i interpretacji, obecność mutantów S7a/S7b/S10 oraz „Zmienia” ⊆ „Przejrzane” dla nowych decyzji.
- WIT5 i wariant T10 przejrzane ręcznie względem warunków i skutków. Generowanie świadków, wykonanie mutantów, dowody G/S/L i niezależny odbiór nie są jeszcze wykonane; pozostają w E2–E5.

## Repozytorium

- Użytkownik scalił poprzednią gałąź `e1-model` do `main` (merge PR #1, `eceaf0e`). Drzewa plików po scaleniu i poprzedniego `e1-model` są identyczne.
- Model v0.3 opublikowany na `e1-model` w commicie `7e4856d`; praca E2 na gałęzi `e2-checks`. Scalenie tej zmiany do `main` wymaga osobnej zgody.

## Sprawy otwarte

| Sprawa | Właściciel | Następny krok |
|---|---|---|
| Korekta G3/G6 (D1 wyżej) | użytkownik | zatwierdzić albo zgłosić uwagi do gotowej propozycji |
| Pozostała implementacja E2: G2, warunki/skutki, bezpieczeństwo i mutanty | agent | kontynuować po rozstrzygnięciu korekty; potem E3 |
| Historyczny opis pojedynczego wydania w informative/ | agent | przy E5 uwzględnić INT-017 w nowym materiale; nie przepisywać migawek sesji 2026-10-23 |
| REQ-210 (wycofane pojęcia) i REQ-211 (rejestr decyzji agenta) dla szablonu | użytkownik | decyzja; opis w `informative/SESJA-2026-10-23.md` §5 |
| Instalacja Javy i TLA+ (E3) | użytkownik | zgoda przed E3 |
| Dostęp do historii vcs-lite (E4) | użytkownik | zgoda przed E4 |
| Porządki w vcs-lite według `informative/PRZEGLAD-VCS-LITE.md` | użytkownik | decyzja, czy i kiedy |

## Decyzje agenta w tej sesji (do podważenia)

- Dwa testy kontraktu modelu pozostają jawnie czerwone; testy działania diagnostyki są osobne. Nie zmieniam zatwierdzonych kryteriów, żeby uzyskać zielony wynik.
- Adnotacji efektów ISO nie wywodzę po cichu z numeru zadania; gotowa propozycja mapowania jest osobnym, niewiążącym plikiem YAML.
- Funkcje grafowe na tym etapie mają jawnie ograniczony zakres; wykonalność przejść wymaga dalszej implementacji.

- Odebrane rekordy trzymamy w `releases`, a wskaźnik `current_release` i znacznik `next_release_required` poza nimi; dzięki temu samo odnotowanie zmiany nie narusza S10.
- Migawka kopiuje wartości pól elementów i zależności, a protokół zawiera numer wydania; nie przechowujemy zmiennych referencji do produktów roboczych.
- W06 jest następnym przejściem po ustawieniu znacznika i kopiuje zakres do nowego rekordu. To techniczne wykonanie uzgodnionej polityki; nie zastępuje zgód U na elementy ani odbioru.
- `max_releases` ogranicza eksplorację, nie dopuszczalność zmian w rzeczywistym procesie. Wyjście poza granicę musi być jawnie raportowane w E3.
- Przejrzane wcześniejsze decyzje agenta pozostają: warunek T11 chroniący przed wycofaną zależnością; blokujące pytanie w T12; dopuszczenie nieaktywnych elementów w W01; terminologia angielska; niewiążący charakter informative/.
