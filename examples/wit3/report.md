# WIT3 — raport wykonania

**SYMULACJA.** Cytaty i decyzje są demonstracyjne. Stan `accepted` dotyczy wyłącznie instancji testowej; nie jest odbiorem E2 ani tego repozytorium.

Wynik odtworzenia: **completed**. Liczba zapisanych kroków: **54**.

Wyniki kontroli i jednoznaczność odpowiedzi są danymi wejściowymi tych kroków, które ich wymagają. Wykonawca nie uruchamia testów rzeczywistego produktu ani nie klasyfikuje treści odpowiedzi.

## Tożsamość wejść i wykonawcy

- Model: v0.6; SHA-256 danych: `ec342e2d04d8200de32d2bbba963ecd4fc45014405b99653134f15e110ff4680`.
- Scenariusz SHA-256: `3d39b6ac75da0cdf766b635f2c6fc2ba073ec09d1d944e24d1ee6ada06ec4340`.
- python: `3.14.7`.
- source_sha256: `78a67819591e32053962691f764a53c40ae3eee09920c83c64b5cb0d7897f27d`.
- uv_lock_sha256: `027a3da0a1f3fbd763d5b9b7c8a8a71229b35202efe60d3d97e4e60f4ce9897a`.
- mutants_sha256: `486e0def874e3a9eca739b646047946d15c8ad8a113c66b3828a985708235377`.

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
| 7 | U | T02 | r1 | verified → approved | spełniony | applied | 0 |
| 8 | U | T04 | r1 | approved → baselined | spełniony | applied | 0 |
| 9 | A | T00 | r2 | none → draft | spełniony | applied | 0 |
| 10 | A | T01 | r2 | draft → verified | spełniony | applied | 0 |
| 11 | U | T02 | r2 | verified → approved | spełniony | applied | 0 |
| 12 | U | T04 | r2 | approved → baselined | spełniony | applied | 0 |
| 13 | A | T00 | a1 | none → draft | spełniony | applied | 0 |
| 14 | A | T01 | a1 | draft → verified | spełniony | applied | 0 |
| 15 | U | T02 | a1 | verified → approved | spełniony | applied | 0 |
| 16 | U | T04 | a1 | approved → baselined | spełniony | applied | 0 |
| 17 | A | T00 | a2 | none → draft | spełniony | applied | 0 |
| 18 | A | T01 | a2 | draft → verified | spełniony | applied | 0 |
| 19 | U | T02 | a2 | verified → approved | spełniony | applied | 0 |
| 20 | U | T04 | a2 | approved → baselined | spełniony | applied | 0 |
| 21 | A | T00 | d1 | none → draft | spełniony | applied | 0 |
| 22 | A | T01 | d1 | draft → verified | spełniony | applied | 0 |
| 23 | U | T04 | d1 | verified → baselined | spełniony | applied | 0 |
| 24 | A | T00 | c1 | none → draft | spełniony | applied | 0 |
| 25 | A | T01 | c1 | draft → verified | spełniony | applied | 0 |
| 26 | U | T04 | c1 | verified → baselined | spełniony | applied | 0 |
| 27 | A | W01 | wydanie 1 | in_preparation → ready | spełniony | applied | 0 |
| 28 | R | W02 | wydanie 1 | ready → reviewed | spełniony | applied | 0 |
| 29 | A | P00 | q1 | none → open | spełniony | applied | 0 |
| 30 | A | P01 | q1 | open → asked | spełniony | applied | 0 |
| 31 | U | P02 | q1 | asked → resolved | spełniony | applied | 1 |
| 32 | U | T07 | r1 (pytanie q1) | baselined → superseded | spełniony | applied | 0 |
| 33 | A | T00 | r3 | none → draft | spełniony | applied | 0 |
| 34 | A | T01 | r3 | draft → verified | spełniony | applied | 0 |
| 35 | U | T02 | r3 | verified → approved | spełniony | applied | 0 |
| 36 | U | T04 | r3 | approved → baselined | spełniony | applied | 0 |
| 37 | U | W07 | wydanie 1 (element r3) | in_preparation → in_preparation | spełniony | applied | 0 |
| 38 | A | T12 | a1 (pytanie q2) | baselined → baselined | spełniony | applied | 0 |
| 39 | A | P01 | q2 | open → asked | spełniony | applied | 0 |
| 40 | U | P02 | q2 | asked → resolved | spełniony | applied | 1 |
| 41 | U | T05 | a1 (pytanie q2) | baselined → draft | spełniony | applied | 0 |
| 42 | A | T14 | a1 | draft → draft | spełniony | applied | 0 |
| 43 | A | T01 | a1 | draft → verified | spełniony | applied | 0 |
| 44 | U | T02 | a1 | verified → approved | spełniony | applied | 0 |
| 45 | U | T04 | a1 | approved → baselined | spełniony | applied | 0 |
| 46 | U | T06 | d1 | baselined → draft | spełniony | applied | 0 |
| 47 | A | T14 | d1 | draft → draft | spełniony | applied | 0 |
| 48 | A | T13 | d1 | draft → draft | spełniony | applied | 0 |
| 49 | A | T01 | d1 | draft → verified | spełniony | applied | 0 |
| 50 | U | T04 | d1 | verified → baselined | spełniony | applied | 0 |
| 51 | A | T11 | c1 | baselined → baselined | spełniony | applied | 0 |
| 52 | A | W01 | wydanie 1 | in_preparation → ready | spełniony | applied | 0 |
| 53 | R | W02 | wydanie 1 | ready → reviewed | spełniony | applied | 0 |
| 54 | U | W04 | wydanie 1 | reviewed → accepted | spełniony | applied | 0 |

## Warunki odczytane z YAML

| Przejście | Warunek |
|---|---|
| T00 | `dependency_types_ok(e, e.depends_on) and acyclic_dependencies(e, e.depends_on) and (proposed_predecessor = none or (item(proposed_predecessor).state = superseded and item(proposed_predecessor).type = e.type and not item(proposed_predecessor).id = e.id))` |
| T01 | `not suspect and checks_ok(e) and forall d in deps(e): d.state in {approved, baselined}` |
| T02 | `type(e).requires_approval and not suspect` |
| T04 | `not suspect and (state = approved or not type(e).requires_approval) and forall d in deps(e): d.state = baselined` |
| W01 | `forall e: in_scope(e) => (e.state in {baselined, deferred, superseded, withdrawn} and (e.state = baselined => not e.suspect)) and tests_ok and not exists q: q.blocking and q.state in {open, asked}` |
| W02 | `true` |
| P00 | `true` |
| P01 | `count(asked) = 0 and q = oldest(open, blocking_first)` |
| P02 | `unambiguous_answer` |
| T07 | `authorized_change(q,e)` |
| W07 | `not in_scope(e) and e.state = baselined and not e.suspect and not e.predecessor = none and predecessor(e).state = superseded and in_scope(predecessor(e)) and forall d in deps(e): in_scope(d)` |
| T12 | `suspect` |
| T05 | `authorized_change(q,e)` |
| T14 | `release.state = in_preparation and old_dependency.id in e.depends_on and old_dependency.state = superseded and new_dependency.predecessor = old_dependency.id and new_dependency.state = baselined and not new_dependency.suspect and not old_dependency.id = new_dependency.id and new_dependency.id not in e.depends_on and not new_dependency.id = e.id and dependency_types_ok(e, (e.depends_on minus {old_dependency.id}) union {new_dependency.id}) and acyclic_dependencies(e, (e.depends_on minus {old_dependency.id}) union {new_dependency.id}) and (in_scope(e) => in_scope(new_dependency))` |
| T06 | `not type(e).requires_approval` |
| T13 | `suspect` |
| T11 | `suspect and forall d in deps(e): d.state in {approved, baselined} and not d.suspect` |
| W04 | `true` |

## Zmiany powiązań i zakresu

Porównanie rzeczywistych stanów przed i po kroku. `predecessor` zapisuje historię następstwa; nie jest zależnością produktu.

| Krok | Cel | Pole | Przed | Po |
|---|---|---|---|---|
| 33 | r3 | predecessor | none | r1 |
| 37 | wydanie 1 | scope | ['p1', 'r1', 'r2', 'd1', 'a1', 'a2', 'c1'] | ['a1', 'a2', 'c1', 'd1', 'p1', 'r1', 'r2', 'r3'] |
| 42 | a1 | depends_on | ['r1'] | ['r3'] |
| 47 | d1 | depends_on | ['r1'] | ['r3'] |

## Dowody demonstracyjne

| Krok | ID decyzji | Odwołanie | Cytat |
|---|---|---|---|
| 3 | SIM-DEC-p1 | — | Zatwierdzam p1 — cytat demonstracyjny. |
| 4 | — | SIM-TAG-p1-v1 | Utwórz linię bazową p1 — polecenie demonstracyjne. |
| 7 | SIM-DEC-r1 | — | Zatwierdzam r1 — cytat demonstracyjny. |
| 8 | — | SIM-TAG-r1-v1 | Utwórz linię bazową r1 — polecenie demonstracyjne. |
| 11 | SIM-DEC-r2 | — | Zatwierdzam r2 — cytat demonstracyjny. |
| 12 | — | SIM-TAG-r2-v1 | Utwórz linię bazową r2 — polecenie demonstracyjne. |
| 15 | SIM-DEC-a1 | — | Zatwierdzam a1 — cytat demonstracyjny. |
| 16 | — | SIM-TAG-a1-v1 | Utwórz linię bazową a1 — polecenie demonstracyjne. |
| 19 | SIM-DEC-a2 | — | Zatwierdzam a2 — cytat demonstracyjny. |
| 20 | — | SIM-TAG-a2-v1 | Utwórz linię bazową a2 — polecenie demonstracyjne. |
| 23 | — | SIM-TAG-d1-v1 | Utwórz linię bazową d1 — polecenie demonstracyjne. |
| 26 | — | SIM-TAG-c1-v1 | Utwórz linię bazową c1 — polecenie demonstracyjne. |
| 31 | SIM-DEC-q1 | — | Zgoda testowa na zastąpienie r1 v1 przez T07. |
| 35 | SIM-APPROVE-r3 | — | Zatwierdzam testowe r3. |
| 36 | — | SIM-BASELINE-r3 | Zapisz linię bazową testowego r3. |
| 37 | SIM-INCLUDE-R3 | — | Włączam r3 jako następcę r1 do zakresu testowego wydania 1; r1 pozostaje w historii. |
| 40 | SIM-DEC-q2 | — | Zgoda testowa na otwarcie zmiany a1 v1 przez T05. |
| 42 | SIM-AGENT-RELINK-a1 | SIM-Przejrzane: a1, r1 -> r3 |  |
| 44 | SIM-APPROVE-a1 | — | Zatwierdzam testowe a1. |
| 45 | — | SIM-BASELINE-a1 | Zapisz linię bazową testowego a1. |
| 47 | SIM-AGENT-RELINK-d1 | SIM-Przejrzane: d1, r1 -> r3 |  |
| 50 | — | SIM-BASELINE-d1 | Zapisz linię bazową testowego d1. |
| 51 | SIM-AGENT-NO-IMPACT-C1 | SIM-Przejrzane: c1, a1 v2, d1 v2; zachowanie kodu bez zmiany |  |
| 54 | — | protokół testowy | Odbieram testowe wydanie 1 po zastąpieniu wymagania i ponownym przeglądzie. |

## Próby obejścia bramek i wybrane mutanty

Każdą próbę rozpoczyna odtworzenie poprawnego prefiksu. Model bazowy spełnia oczekiwanie, a pojedyncza celowa zmiana reguły je narusza: dopuszcza zabroniony krok, zmienia kolejność lub zapis decyzji. To potwierdza czułość wyroczni, nie pełne pokrycie mutacyjne E2 ani dowód żywotności.

| Mutant | Właściwość | Model bazowy | Po uszkodzeniu reguły | Wykryty |
|---|---|---|---|---|
| s12_active_predecessor | S12 | guard | applied | True |
| s12_wrong_predecessor_type | S12 | guard | applied | True |
| s12_relink_without_opening | S12 | state | applied | True |
| s12_relink_outside_scope | S12 | guard | applied | True |
| s12_wrong_successor | S12 | guard | applied | True |
| s12_immature_successor | S12 | guard | applied | True |
| s12_missing_relink | S12 | value=['r3'] | value=['r1'] | True |
| s5_missing_relink_propagation | S5 | value=True | value=False | True |
| s12_rewrites_lineage | S12 | value=none | value=r1 | True |
| s4_premature_no_impact_review | S4 | guard | applied | True |
| t11_ignores_suspect_dependency | WIT3/T11 | guard | applied | True |
| s1_agent_includes_scope | S1/S13 | actor | applied | True |
| s13_drops_predecessor_from_scope | S13 | value=['a1', 'a2', 'c1', 'd1', 'p1', 'r1', 'r2', 'r3'] | value=['a1', 'a2', 'c1', 'd1', 'p1', 'r2', 'r3'] | True |
| s13_includes_immature_successor | S13 | guard | applied | True |
| s10_modifies_accepted_scope | S10/S13 | state | applied | True |
| s7a_retirement_keeps_reviewed | S7a | value=in_preparation | value=reviewed | True |
| s6_review_ignores_retired_dependency | S6 | guard | applied | True |

## Stan końcowy

Bieżące wydanie: 1, `accepted`. `next_release_required = false`.

Zakres bieżącego wydania: a1, a2, c1, d1, p1, r1, r2, r3.

| Element | Stan | Wersja | Suspect | Odrzucenia | Zależy od | Poprzednik | W zakresie |
|---|---|---|---|---|---|---|---|
| p1 | baselined | 1 | false | 0 | — | none | True |
| r1 | superseded | 1 | false | 0 | p1 | none | True |
| r2 | baselined | 1 | false | 0 | p1 | none | True |
| d1 | baselined | 2 | false | 0 | r3 | none | True |
| a1 | baselined | 2 | false | 0 | r3 | none | True |
| a2 | baselined | 1 | false | 0 | r2 | none | True |
| c1 | baselined | 1 | false | 0 | d1, a1 | none | True |
| r3 | baselined | 1 | false | 0 | p1 | r1 | True |

## Pytania

| ID | Stan | Blokujące | Kolejność zgłoszenia |
|---|---|---|---|
| q1 | resolved | true | 1 |
| q2 | resolved | true | 2 |

| Pytanie | Rodzaj | Element / wersja | Operacja | Rozstrzygnięcie | Wykorzystana |
|---|---|---|---|---|---|
| q1 | change | r1 / 1 | T07 | approved | True |
| q2 | change | a1 / 1 | T05 | approved | True |

## Utworzone decyzje demonstracyjne

Zapisy pochodzą ze skutku `record DEC with user quote`; kolumna «Nowe DEC pytań» pokazuje, w którym kroku powstały. Cytat przy P03 jest dowodem odpowiedzi niejednoznacznej, bez utworzenia DEC. Cytowane zatwierdzenia produktów i protokół odbioru mają osobne dowody.

| Krok | ID | Pytanie | Cytat |
|---|---|---|---|
| 31 | SIM-DEC-q1 | q1 | Zgoda testowa na zastąpienie r1 v1 przez T07. |
| 40 | SIM-DEC-q2 | q2 | Zgoda testowa na otwarcie zmiany a1 v1 przez T05. |

## Granice wyniku

Wykonano podaną ścieżkę WIT3 w E2. Nie wygenerowano świadka przez TLC, nie udowodniono wszystkich G/S/L i nie zakończono E2. Pozostają pełne pokrycie reguł i zastosowanie na rzeczywistym projekcie. Weryfikacja roli R w symulacji nie jest niezależnym przeglądem implementacji.
