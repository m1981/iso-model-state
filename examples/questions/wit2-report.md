# WIT2 — raport wykonania

**SYMULACJA.** Cytaty i decyzje są demonstracyjne. Stan `accepted` dotyczy wyłącznie instancji testowej; nie jest odbiorem E2 ani tego repozytorium.

Wynik odtworzenia: **completed**. Liczba zapisanych kroków: **33**.

Wyniki kontroli i jednoznaczność odpowiedzi są danymi wejściowymi tych kroków, które ich wymagają. Wykonawca nie uruchamia testów rzeczywistego produktu ani nie klasyfikuje treści odpowiedzi.

## Tożsamość wejść i wykonawcy

- Model: v0.6; SHA-256 danych: `ec342e2d04d8200de32d2bbba963ecd4fc45014405b99653134f15e110ff4680`.
- Scenariusz SHA-256: `0bb62c523052950649dcb6b10f565d561cc1759f2a4a606f53bee0bb76c560c1`.
- python: `3.14.7`.
- source_sha256: `78a67819591e32053962691f764a53c40ae3eee09920c83c64b5cb0d7897f27d`.
- uv_lock_sha256: `027a3da0a1f3fbd763d5b9b7c8a8a71229b35202efe60d3d97e4e60f4ce9897a`.
- mutants_sha256: `25e094a4d18f8d782fb0365b972fa4ab5f0f4a654375de142f4740e3211dfddf`.

## Przebieg

Warunki są rozwinięte w kolejnej tabeli. Pełne stany przed i po, dowody oraz dane wejściowe znajdują się w wygenerowanym `trace.json`.

| Krok | Aktor | Przejście | Cel | Stan przed → po | Ocena warunku | Wynik | Nowe DEC pytań |
|---|---|---|---|---|---|---|---|
| 1 | A | T00 | p1 | none → draft | spełniony | applied | 0 |
| 2 | A | T01 | p1 | draft → verified | spełniony | applied | 0 |
| 3 | U | T02 | p1 | verified → approved | spełniony | applied | 0 |
| 4 | U | T04 | p1 | approved → baselined | spełniony | applied | 0 |
| 5 | A | T00 | r1 | none → draft | spełniony | applied | 0 |
| 6 | A | T01 | r1 | draft → verified | spełniony | applied | 0 |
| 7 | U | T03 | r1 | verified → draft | spełniony | applied | 0 |
| 8 | A | T01 | r1 | draft → verified | spełniony | applied | 0 |
| 9 | U | T03 | r1 | verified → draft | spełniony | applied | 0 |
| 10 | A | T01 | r1 | draft → verified | spełniony | applied | 0 |
| 11 | U | T02 | r1 | verified → approved | spełniony | applied | 0 |
| 12 | U | T04 | r1 | approved → baselined | spełniony | applied | 0 |
| 13 | A | T00 | r2 | none → draft | spełniony | applied | 0 |
| 14 | A | T01 | r2 | draft → verified | spełniony | applied | 0 |
| 15 | U | T02 | r2 | verified → approved | spełniony | applied | 0 |
| 16 | U | T04 | r2 | approved → baselined | spełniony | applied | 0 |
| 17 | A | T00 | a1 | none → draft | spełniony | applied | 0 |
| 18 | A | T01 | a1 | draft → verified | spełniony | applied | 0 |
| 19 | U | T02 | a1 | verified → approved | spełniony | applied | 0 |
| 20 | U | T04 | a1 | approved → baselined | spełniony | applied | 0 |
| 21 | A | T00 | a2 | none → draft | spełniony | applied | 0 |
| 22 | A | T01 | a2 | draft → verified | spełniony | applied | 0 |
| 23 | U | T02 | a2 | verified → approved | spełniony | applied | 0 |
| 24 | U | T04 | a2 | approved → baselined | spełniony | applied | 0 |
| 25 | A | T00 | d1 | none → draft | spełniony | applied | 0 |
| 26 | A | T01 | d1 | draft → verified | spełniony | applied | 0 |
| 27 | U | T04 | d1 | verified → baselined | spełniony | applied | 0 |
| 28 | A | T00 | c1 | none → draft | spełniony | applied | 0 |
| 29 | A | T01 | c1 | draft → verified | spełniony | applied | 0 |
| 30 | U | T04 | c1 | verified → baselined | spełniony | applied | 0 |
| 31 | A | W01 | wydanie 1 | in_preparation → ready | spełniony | applied | 0 |
| 32 | R | W02 | wydanie 1 | ready → reviewed | spełniony | applied | 0 |
| 33 | U | W04 | wydanie 1 | reviewed → accepted | spełniony | applied | 0 |

## Warunki odczytane z YAML

| Przejście | Warunek |
|---|---|
| T00 | `dependency_types_ok(e, e.depends_on) and acyclic_dependencies(e, e.depends_on) and (proposed_predecessor = none or (item(proposed_predecessor).state = superseded and item(proposed_predecessor).type = e.type and not item(proposed_predecessor).id = e.id))` |
| T01 | `not suspect and checks_ok(e) and forall d in deps(e): d.state in {approved, baselined}` |
| T02 | `type(e).requires_approval and not suspect` |
| T04 | `not suspect and (state = approved or not type(e).requires_approval) and forall d in deps(e): d.state = baselined` |
| T03 | `rejections < MAX_REJECTIONS` |
| W01 | `forall e: in_scope(e) => (e.state in {baselined, deferred, superseded, withdrawn} and (e.state = baselined => not e.suspect)) and tests_ok and not exists q: q.blocking and q.state in {open, asked}` |
| W02 | `true` |
| W04 | `true` |

## Dowody demonstracyjne

| Krok | ID decyzji | Odwołanie | Cytat |
|---|---|---|---|
| 3 | SIM-DEC-p1 | — | Zatwierdzam p1 — cytat demonstracyjny. |
| 4 | — | SIM-TAG-p1-v1 | Utwórz linię bazową p1 — polecenie demonstracyjne. |
| 11 | SIM-DEC-r1 | — | Zatwierdzam r1 — cytat demonstracyjny. |
| 12 | — | SIM-TAG-r1-v1 | Utwórz linię bazową r1 — polecenie demonstracyjne. |
| 15 | SIM-DEC-r2 | — | Zatwierdzam r2 — cytat demonstracyjny. |
| 16 | — | SIM-TAG-r2-v1 | Utwórz linię bazową r2 — polecenie demonstracyjne. |
| 19 | SIM-DEC-a1 | — | Zatwierdzam a1 — cytat demonstracyjny. |
| 20 | — | SIM-TAG-a1-v1 | Utwórz linię bazową a1 — polecenie demonstracyjne. |
| 23 | SIM-DEC-a2 | — | Zatwierdzam a2 — cytat demonstracyjny. |
| 24 | — | SIM-TAG-a2-v1 | Utwórz linię bazową a2 — polecenie demonstracyjne. |
| 27 | — | SIM-TAG-d1-v1 | Utwórz linię bazową d1 — polecenie demonstracyjne. |
| 30 | — | SIM-TAG-c1-v1 | Utwórz linię bazową c1 — polecenie demonstracyjne. |
| 33 | — | protokół testowy | Odbieram wydanie testowe 1 — cytat demonstracyjny. |

## Próby obejścia bramek i wybrane mutanty

Każdą próbę rozpoczyna odtworzenie poprawnego prefiksu. Model bazowy spełnia oczekiwanie, a pojedyncza celowa zmiana reguły je narusza: dopuszcza zabroniony krok, zmienia kolejność lub zapis decyzji. To potwierdza czułość wyroczni, nie pełne pokrycie mutacyjne E2 ani dowód żywotności.

| Mutant | Właściwość | Model bazowy | Po uszkodzeniu reguły | Wykryty |
|---|---|---|---|---|
| wit2_third_rejection | L4 | guard | applied | True |
| wit2_author_rejection | S1 | actor | applied | True |

## Stan końcowy

Bieżące wydanie: 1, `accepted`. `next_release_required = false`.

Zakres bieżącego wydania: p1, r1, r2, d1, a1, a2, c1.

| Element | Stan | Wersja | Suspect | Odrzucenia | Zależy od | Poprzednik | W zakresie |
|---|---|---|---|---|---|---|---|
| p1 | baselined | 1 | false | 0 | — | none | True |
| r1 | baselined | 1 | false | 2 | p1 | none | True |
| r2 | baselined | 1 | false | 0 | p1 | none | True |
| d1 | baselined | 1 | false | 0 | r1 | none | True |
| a1 | baselined | 1 | false | 0 | r1 | none | True |
| a2 | baselined | 1 | false | 0 | r2 | none | True |
| c1 | baselined | 1 | false | 0 | d1, a1 | none | True |
| r3 | none | 0 | false | 0 | p1 | none | False |

## Granice wyniku

Wykonano podaną ścieżkę WIT2 w E2. Nie wygenerowano świadka przez TLC, nie udowodniono wszystkich G/S/L i nie zakończono E2. Pozostają pełne pokrycie reguł i zastosowanie na rzeczywistym projekcie. Weryfikacja roli R w symulacji nie jest niezależnym przeglądem implementacji.
