# WIT1 — raport wykonania

**SYMULACJA.** Cytaty i decyzje są demonstracyjne. Stan `accepted` dotyczy wyłącznie instancji testowej; nie jest odbiorem E2 ani tego repozytorium.

Wynik odtworzenia: **completed**. Liczba zapisanych kroków: **29**.

`checks_ok(e)` i `tests_ok` są jawnymi założeniami wejściowymi. Wykonawca nie uruchamia testów rzeczywistego produktu.

## Tożsamość wejść i wykonawcy

- Model: v0.4; SHA-256 danych: `2c207324149fcb51d5586526823466202f7a8c0fa3d20d5ce205c7125bb86242`.
- Scenariusz SHA-256: `29d2bce8024c668cca35abaeeb687541c008de3c49d7421ba204f3485f12ba6a`.
- python: `3.14.7`.
- source_sha256: `b247be9799eb570a19dee067686b96a538541b89ff44b592ac7845570cc0932b`.
- uv_lock_sha256: `027a3da0a1f3fbd763d5b9b7c8a8a71229b35202efe60d3d97e4e60f4ce9897a`.
- mutants_sha256: `232de804651920c1405c6ddca0bd771c7f9a240554eb75c35b973ea1c32bb5c9`.

## Przebieg

Warunki są rozwinięte w kolejnej tabeli. Pełne stany przed i po, dowody oraz dane wejściowe znajdują się w wygenerowanym `trace.json`.

| Krok | Aktor | Przejście | Cel | Stan przed → po | Ocena warunku | Wynik |
|---|---|---|---|---|---|---|
| 1 | A | T00 | p1 | none → draft | spełniony | applied |
| 2 | A | T01 | p1 | draft → verified | spełniony | applied |
| 3 | U | T02 | p1 | verified → approved | spełniony | applied |
| 4 | U | T04 | p1 | approved → baselined | spełniony | applied |
| 5 | A | T00 | r1 | none → draft | spełniony | applied |
| 6 | A | T01 | r1 | draft → verified | spełniony | applied |
| 7 | U | T02 | r1 | verified → approved | spełniony | applied |
| 8 | U | T04 | r1 | approved → baselined | spełniony | applied |
| 9 | A | T00 | r2 | none → draft | spełniony | applied |
| 10 | A | T01 | r2 | draft → verified | spełniony | applied |
| 11 | U | T02 | r2 | verified → approved | spełniony | applied |
| 12 | U | T04 | r2 | approved → baselined | spełniony | applied |
| 13 | A | T00 | a1 | none → draft | spełniony | applied |
| 14 | A | T01 | a1 | draft → verified | spełniony | applied |
| 15 | U | T02 | a1 | verified → approved | spełniony | applied |
| 16 | U | T04 | a1 | approved → baselined | spełniony | applied |
| 17 | A | T00 | a2 | none → draft | spełniony | applied |
| 18 | A | T01 | a2 | draft → verified | spełniony | applied |
| 19 | U | T02 | a2 | verified → approved | spełniony | applied |
| 20 | U | T04 | a2 | approved → baselined | spełniony | applied |
| 21 | A | T00 | d1 | none → draft | spełniony | applied |
| 22 | A | T01 | d1 | draft → verified | spełniony | applied |
| 23 | U | T04 | d1 | verified → baselined | spełniony | applied |
| 24 | A | T00 | c1 | none → draft | spełniony | applied |
| 25 | A | T01 | c1 | draft → verified | spełniony | applied |
| 26 | U | T04 | c1 | verified → baselined | spełniony | applied |
| 27 | A | W01 | wydanie 1 | in_preparation → ready | spełniony | applied |
| 28 | R | W02 | wydanie 1 | ready → reviewed | spełniony | applied |
| 29 | U | W04 | wydanie 1 | reviewed → accepted | spełniony | applied |

## Warunki odczytane z YAML

| Przejście | Warunek |
|---|---|
| T00 | `true` |
| T01 | `not suspect and checks_ok(e) and forall d in deps(e): d.state in {approved, baselined}` |
| T02 | `type(e).requires_approval and not suspect` |
| T04 | `not suspect and (state = approved or not type(e).requires_approval) and forall d in deps(e): d.state = baselined` |
| W01 | `forall e: in_scope(e) => (e.state in {baselined, deferred, superseded, withdrawn} and (e.state = baselined => not e.suspect)) and tests_ok and not exists q: q.blocking and q.state in {open, asked}` |
| W02 | `true` |
| W04 | `true` |

## Dowody demonstracyjne

| Krok | Odwołanie | Cytat |
|---|---|---|
| 3 | SIM-DEC-p1 | Zatwierdzam p1 — cytat demonstracyjny. |
| 4 | SIM-TAG-p1-v1 | Utwórz linię bazową p1 — polecenie demonstracyjne. |
| 7 | SIM-DEC-r1 | Zatwierdzam r1 — cytat demonstracyjny. |
| 8 | SIM-TAG-r1-v1 | Utwórz linię bazową r1 — polecenie demonstracyjne. |
| 11 | SIM-DEC-r2 | Zatwierdzam r2 — cytat demonstracyjny. |
| 12 | SIM-TAG-r2-v1 | Utwórz linię bazową r2 — polecenie demonstracyjne. |
| 15 | SIM-DEC-a1 | Zatwierdzam a1 — cytat demonstracyjny. |
| 16 | SIM-TAG-a1-v1 | Utwórz linię bazową a1 — polecenie demonstracyjne. |
| 19 | SIM-DEC-a2 | Zatwierdzam a2 — cytat demonstracyjny. |
| 20 | SIM-TAG-a2-v1 | Utwórz linię bazową a2 — polecenie demonstracyjne. |
| 23 | SIM-TAG-d1-v1 | Utwórz linię bazową d1 — polecenie demonstracyjne. |
| 26 | SIM-TAG-c1-v1 | Utwórz linię bazową c1 — polecenie demonstracyjne. |
| 29 | protokół testowy | Odbieram wydanie testowe 1 — cytat demonstracyjny. |

## Próby obejścia bramek i wybrane mutanty

Każdą próbę rozpoczyna odtworzenie poprawnego prefiksu. Model bazowy musi odmówić, a pojedyncza celowa zmiana reguły dopuścić ten sam krok. To potwierdza czułość wyroczni, nie pełne pokrycie mutacyjne E2.

| Mutant | Właściwość | Poprawny model: odmowa | Po uszkodzeniu reguły | Wykryty |
|---|---|---|---|---|
| wit1_author_baseline | S1 | actor | applied | True |
| wit1_skip_approval | S2 | guard | applied | True |
| wit1_skip_verification | S3 | state | applied | True |
| wit1_unready_dependency | S4 | guard | applied | True |
| wit1_incomplete_ready | S7a | guard | applied | True |
| wit1_incomplete_acceptance | S7b | state | applied | True |
| wit1_skip_review | S8 | state | applied | True |

## Stan końcowy

Bieżące wydanie: 1, `accepted`. `next_release_required = false`.

| Element | Stan | Wersja | Suspect |
|---|---|---|---|
| p1 | baselined | 1 | false |
| r1 | baselined | 1 | false |
| r2 | baselined | 1 | false |
| d1 | baselined | 1 | false |
| a1 | baselined | 1 | false |
| a2 | baselined | 1 | false |
| c1 | baselined | 1 | false |

## Granice wyniku

Wykonano podaną ścieżkę WIT1 w E2. Nie wygenerowano świadka przez TLC, nie udowodniono wszystkich G/S/L i nie zakończono E2. Obsługa pytań, zmian i kolejnych wydań pozostaje przed nami. Weryfikacja roli R w symulacji nie jest niezależnym przeglądem implementacji.
