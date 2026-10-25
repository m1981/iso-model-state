# WIT4 — raport wykonania

**SYMULACJA.** Cytaty i decyzje są demonstracyjne. Stan `accepted` dotyczy wyłącznie instancji testowej; nie jest odbiorem E2 ani tego repozytorium.

Wynik odtworzenia: **completed**. Liczba zapisanych kroków: **13**.

Wyniki kontroli i jednoznaczność odpowiedzi są danymi wejściowymi tych kroków, które ich wymagają. Wykonawca nie uruchamia testów rzeczywistego produktu ani nie klasyfikuje treści odpowiedzi.

## Tożsamość wejść i wykonawcy

- Model: v0.6; SHA-256 danych: `ec342e2d04d8200de32d2bbba963ecd4fc45014405b99653134f15e110ff4680`.
- Scenariusz SHA-256: `be7b118fa3c78f0685c6a4cc47998eaf420ba0261b67c5c86ad83b30dad89bb1`.
- python: `3.14.7`.
- source_sha256: `e87b1bec0b3669f5801e91bc96f371125e14b84bedbf223a1400df419ff4c66a`.
- uv_lock_sha256: `027a3da0a1f3fbd763d5b9b7c8a8a71229b35202efe60d3d97e4e60f4ce9897a`.
- mutants_sha256: `47ffaef89a6e7970279663bfa75dc729a6a4b12df62653315892b095c4470955`.

## Przebieg

Warunki są rozwinięte w kolejnej tabeli. Pełne stany przed i po, dowody oraz dane wejściowe znajdują się w wygenerowanym `trace.json`.

| Krok | Aktor | Przejście | Cel | Stan przed → po | Ocena warunku | Wynik | Nowe DEC pytań |
|---|---|---|---|---|---|---|---|
| 1 | A | P00 | q1 | none → open | spełniony | applied | 0 |
| 2 | A | P01 | q1 | open → asked | spełniony | applied | 0 |
| 3 | R | P00 | q2 | none → open | spełniony | applied | 0 |
| 4 | U | P00 | q3 | none → open | spełniony | applied | 0 |
| 5 | U | P03 | q1 | asked → open | spełniony | applied | 0 |
| 6 | A | P01 | q1 | open → asked | spełniony | applied | 0 |
| 7 | U | P02 | q1 | asked → resolved | spełniony | applied | 1 |
| 8 | A | P01 | q2 | open → asked | spełniony | applied | 0 |
| 9 | U | P02 | q2 | asked → resolved | spełniony | applied | 1 |
| 10 | U | P04 | q3 | open → deferred | spełniony | applied | 0 |
| 11 | A | P05 | q3 | deferred → open | spełniony | applied | 0 |
| 12 | A | P01 | q3 | open → asked | spełniony | applied | 0 |
| 13 | U | P02 | q3 | asked → resolved | spełniony | applied | 1 |

## Warunki odczytane z YAML

| Przejście | Warunek |
|---|---|
| P00 | `true` |
| P01 | `count(asked) = 0 and q = oldest(open, blocking_first)` |
| P03 | `true` |
| P02 | `unambiguous_answer` |
| P04 | `not blocking` |
| P05 | `true` |

## Dowody demonstracyjne

| Krok | ID decyzji | Odwołanie | Cytat |
|---|---|---|---|
| 5 | — | odpowiedź testowa | Nie wiem, doprecyzuj — odpowiedź demonstracyjna. |
| 7 | SIM-DEC-q1 | — | Rozstrzygam q1 — cytat demonstracyjny. |
| 9 | SIM-DEC-q2 | — | Rozstrzygam q2 — cytat demonstracyjny. |
| 13 | SIM-DEC-q3 | — | Rozstrzygam q3 — cytat demonstracyjny. |

## Próby obejścia bramek i wybrane mutanty

Każdą próbę rozpoczyna odtworzenie poprawnego prefiksu. Model bazowy spełnia oczekiwanie, a pojedyncza celowa zmiana reguły je narusza: dopuszcza zabroniony krok, zmienia kolejność lub zapis decyzji. To potwierdza czułość wyroczni, nie pełne pokrycie mutacyjne E2 ani dowód żywotności.

| Mutant | Właściwość | Model bazowy | Po uszkodzeniu reguły | Wykryty |
|---|---|---|---|---|
| wit4_two_asked | S9 | guard | applied | True |
| wit4_lifo | L2 | guard | applied | True |
| wit4_ambiguous_resolution | WIT4 | guard | applied | True |
| wit4_defer_blocking | WIT4 | guard | applied | True |
| wit4_lost_age | WIT4 | preserved=True | preserved=False | True |
| wit4_ambiguous_decision | WIT4 | records=0 | records=1 | True |
| wit4_missing_decision | WIT4 | records=1 | records=0 | True |

## Stan końcowy

Bieżące wydanie: 1, `in_preparation`. `next_release_required = false`.

Zakres bieżącego wydania: p1, r1, r2, d1, a1, a2, c1.

| Element | Stan | Wersja | Suspect | Odrzucenia | Zależy od | Poprzednik | W zakresie |
|---|---|---|---|---|---|---|---|
| p1 | none | 0 | false | 0 | — | none | True |
| r1 | none | 0 | false | 0 | p1 | none | True |
| r2 | none | 0 | false | 0 | p1 | none | True |
| d1 | none | 0 | false | 0 | r1 | none | True |
| a1 | none | 0 | false | 0 | r1 | none | True |
| a2 | none | 0 | false | 0 | r2 | none | True |
| c1 | none | 0 | false | 0 | d1, a1 | none | True |
| r3 | none | 0 | false | 0 | p1 | none | False |

## Pytania

| ID | Stan | Blokujące | Kolejność zgłoszenia |
|---|---|---|---|
| q1 | resolved | true | 1 |
| q2 | resolved | true | 2 |
| q3 | resolved | false | 3 |

| Pytanie | Rodzaj | Element / wersja | Operacja | Rozstrzygnięcie | Wykorzystana |
|---|---|---|---|---|---|
| q1 | general | none / none | none | answered | False |
| q2 | general | none / none | none | answered | False |
| q3 | general | none / none | none | answered | False |

## Utworzone decyzje demonstracyjne

Zapisy pochodzą ze skutku `record DEC with user quote`; kolumna «Nowe DEC pytań» pokazuje, w którym kroku powstały. Cytat przy P03 jest dowodem odpowiedzi niejednoznacznej, bez utworzenia DEC. Cytowane zatwierdzenia produktów i protokół odbioru mają osobne dowody.

| Krok | ID | Pytanie | Cytat |
|---|---|---|---|
| 7 | SIM-DEC-q1 | q1 | Rozstrzygam q1 — cytat demonstracyjny. |
| 9 | SIM-DEC-q2 | q2 | Rozstrzygam q2 — cytat demonstracyjny. |
| 13 | SIM-DEC-q3 | q3 | Rozstrzygam q3 — cytat demonstracyjny. |

## Granice wyniku

Wykonano podaną ścieżkę WIT4 w E2. Nie wygenerowano świadka przez TLC, nie udowodniono wszystkich G/S/L i nie zakończono E2. Pozostają pełne pokrycie reguł i zastosowanie na rzeczywistym projekcie. Weryfikacja roli R w symulacji nie jest niezależnym przeglądem implementacji.
