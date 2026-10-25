# WIT5 — raport wykonania

**SYMULACJA.** Cytaty i decyzje są demonstracyjne. Stan `accepted` dotyczy wyłącznie instancji testowej; nie jest odbiorem E2 ani tego repozytorium.

Wynik odtworzenia: **completed**. Liczba zapisanych kroków: **40**.

Wyniki kontroli i jednoznaczność odpowiedzi są danymi wejściowymi tych kroków, które ich wymagają. Wykonawca nie uruchamia testów rzeczywistego produktu ani nie klasyfikuje treści odpowiedzi.

## Tożsamość wejść i wykonawcy

- Model: v0.6; SHA-256 danych: `ec342e2d04d8200de32d2bbba963ecd4fc45014405b99653134f15e110ff4680`.
- Scenariusz SHA-256: `759626cbf24169a4033f3d3282a23693062b01bc73bcdf644fc8691eb43b2085`.
- python: `3.14.7`.
- source_sha256: `e87b1bec0b3669f5801e91bc96f371125e14b84bedbf223a1400df419ff4c66a`.
- uv_lock_sha256: `027a3da0a1f3fbd763d5b9b7c8a8a71229b35202efe60d3d97e4e60f4ce9897a`.
- mutants_sha256: `1dc1bf7f5c34ac420d9514a3c14d90f33f17c367687c0d3ce31a963c09e7368f`.

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
| 29 | U | W04 | wydanie 1 | reviewed → accepted | spełniony | applied | 0 |
| 30 | A | P00 | q1 | none → open | spełniony | applied | 0 |
| 31 | A | P01 | q1 | open → asked | spełniony | applied | 0 |
| 32 | U | P02 | q1 | asked → resolved | spełniony | applied | 1 |
| 33 | U | T05 | a2 (pytanie q1) | baselined → draft | spełniony | applied | 0 |
| 34 | A | W06 | wydanie 1 → nowe 2 | accepted → in_preparation | spełniony | applied | 0 |
| 35 | A | T01 | a2 | draft → verified | spełniony | applied | 0 |
| 36 | U | T02 | a2 | verified → approved | spełniony | applied | 0 |
| 37 | U | T04 | a2 | approved → baselined | spełniony | applied | 0 |
| 38 | A | W01 | wydanie 2 | in_preparation → ready | spełniony | applied | 0 |
| 39 | R | W02 | wydanie 2 | ready → reviewed | spełniony | applied | 0 |
| 40 | U | W04 | wydanie 2 | reviewed → accepted | spełniony | applied | 0 |

## Warunki odczytane z YAML

| Przejście | Warunek |
|---|---|
| T00 | `dependency_types_ok(e, e.depends_on) and acyclic_dependencies(e, e.depends_on) and (proposed_predecessor = none or (item(proposed_predecessor).state = superseded and item(proposed_predecessor).type = e.type and not item(proposed_predecessor).id = e.id))` |
| T01 | `not suspect and checks_ok(e) and forall d in deps(e): d.state in {approved, baselined}` |
| T02 | `type(e).requires_approval and not suspect` |
| T04 | `not suspect and (state = approved or not type(e).requires_approval) and forall d in deps(e): d.state = baselined` |
| W01 | `forall e: in_scope(e) => (e.state in {baselined, deferred, superseded, withdrawn} and (e.state = baselined => not e.suspect)) and tests_ok and not exists q: q.blocking and q.state in {open, asked}` |
| W02 | `true` |
| W04 | `true` |
| P00 | `true` |
| P01 | `count(asked) = 0 and q = oldest(open, blocking_first)` |
| P02 | `unambiguous_answer` |
| T05 | `authorized_change(q,e)` |
| W06 | `next_release_required` |

## Zmiany powiązań i zakresu

Porównanie rzeczywistych stanów przed i po kroku. `predecessor` zapisuje historię następstwa; nie jest zależnością produktu.

| Krok | Cel | Pole | Przed | Po |
|---|---|---|---|---|
| 34 | wydanie 2 | scope | None | ['p1', 'r1', 'r2', 'd1', 'a1', 'a2', 'c1'] |

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
| 29 | — | protokół testowy | Odbieram wydanie testowe 1 — cytat demonstracyjny. |
| 32 | SIM-DEC-CHANGE-A2 | — | Zgoda testowa na otwarcie zmiany a2 w wersji 1 przez T05. |
| 36 | SIM-DEC-A2-V2 | — | Zatwierdzam testowe a2 w wersji 2. |
| 37 | — | SIM-TAG-A2-V2 | Zapisz linię bazową testowego a2 w wersji 2. |
| 40 | — | protokół testowy | Odbieram testowe wydanie 2. |

## Próby obejścia bramek i wybrane mutanty

Każdą próbę rozpoczyna odtworzenie poprawnego prefiksu. Model bazowy spełnia oczekiwanie, a pojedyncza celowa zmiana reguły je narusza: dopuszcza zabroniony krok, zmienia kolejność lub zapis decyzji. To potwierdza czułość wyroczni, nie pełne pokrycie mutacyjne E2 ani dowód żywotności.

| Mutant | Właściwość | Model bazowy | Po uszkodzeniu reguły | Wykryty |
|---|---|---|---|---|
| s11_rejection_as_consent | S11 | guard | applied | True |
| s11_wrong_item | S11 | guard | applied | True |
| s11_wrong_operation | S11 | guard | applied | True |
| s11_stale_unused_consent | S11 | guard | applied | True |
| s11_missing_consumption | S11 | value=True | value=False | True |
| s10_w06_rewrites_accepted | S10 | preserved=True | preserved=False | True |
| w06_wrong_actor | WIT5 | actor | applied | True |
| s7a_t10_keeps_readiness | S7a | value=in_preparation | value=ready | True |
| s11_p03_changes_binding | S11 | preserved=True | preserved=False | True |
| w06_without_change | WIT5 | guard | applied | True |

## Stan końcowy

Bieżące wydanie: 2, `accepted`. `next_release_required = false`.

Zakres bieżącego wydania: p1, r1, r2, d1, a1, a2, c1.

| Element | Stan | Wersja | Suspect | Odrzucenia | Zależy od | Poprzednik | W zakresie |
|---|---|---|---|---|---|---|---|
| p1 | baselined | 1 | false | 0 | — | none | True |
| r1 | baselined | 1 | false | 0 | p1 | none | True |
| r2 | baselined | 1 | false | 0 | p1 | none | True |
| d1 | baselined | 1 | false | 0 | r1 | none | True |
| a1 | baselined | 1 | false | 0 | r1 | none | True |
| a2 | baselined | 2 | false | 0 | r2 | none | True |
| c1 | baselined | 1 | false | 0 | d1, a1 | none | True |
| r3 | none | 0 | false | 0 | p1 | none | False |

## Historia wydań

Niezmienność całych odebranych rekordów we wszystkich krokach śladu: **True**.

| Numer | Stan | Wersje w migawce |
|---|---|---|
| 1 | accepted | p1@1, r1@1, r2@1, d1@1, a1@1, a2@1, c1@1 |
| 2 | accepted | p1@1, r1@1, r2@1, d1@1, a1@1, a2@2, c1@1 |

## Pytania

| ID | Stan | Blokujące | Kolejność zgłoszenia |
|---|---|---|---|
| q1 | resolved | true | 1 |

| Pytanie | Rodzaj | Element / wersja | Operacja | Rozstrzygnięcie | Wykorzystana |
|---|---|---|---|---|---|
| q1 | change | a2 / 1 | T05 | approved | True |

## Utworzone decyzje demonstracyjne

Zapisy pochodzą ze skutku `record DEC with user quote`; kolumna «Nowe DEC pytań» pokazuje, w którym kroku powstały. Cytat przy P03 jest dowodem odpowiedzi niejednoznacznej, bez utworzenia DEC. Cytowane zatwierdzenia produktów i protokół odbioru mają osobne dowody.

| Krok | ID | Pytanie | Cytat |
|---|---|---|---|
| 32 | SIM-DEC-CHANGE-A2 | q1 | Zgoda testowa na otwarcie zmiany a2 w wersji 1 przez T05. |

## Granice wyniku

Wykonano podaną ścieżkę WIT5 w E2. Nie wygenerowano świadka przez TLC, nie udowodniono wszystkich G/S/L i nie zakończono E2. Pozostają pełne pokrycie reguł i zastosowanie na rzeczywistym projekcie. Weryfikacja roli R w symulacji nie jest niezależnym przeglądem implementacji.
