# Właściwości modelu i Definition of Done

Właściwości, które model `model/process.yaml` musi spełniać. Każda ma: zapis formalny, narzędzie, które ją sprawdza, i **mutanta**: celowo zepsuty model, na którym musi paść (DoD 6). Status `verified` (czeka na zatwierdzenie w bramce E1).

Notacja: `G` zawsze, `F` kiedyś, `X` w następnym kroku, `O` kiedyś w przeszłości (LTL z przeszłością); `AG`, `EF`, `EX` z CTL. `e` to dowolny element, `q` dowolne pytanie, `rel` wydanie. Identyfikatory jak w modelu (DEC-PRO-002).

Predykaty pomocnicze:
- `USER_GATES = {T02, T03, T04, T05, T06, T07, T08, T09, T10, P02, P03, P04, W04, W05}`
- `done ≡ rel.state = accepted or forall e: e.state in {superseded, withdrawn}`
- `inactive(e) ≡ e.state in {deferred, superseded, withdrawn}`

## Definition of Done (pełna treść)

| DoD | Kryterium | Dowód zakończenia |
|---|---|---|
| 1 | Zamknięty słownik: każdy typ, stan, zmienna, przejście, aktor i warunek jest w `process.yaml`; każdy stan wskazuje stan Tabeli 12 normy albo INT | test G0 przechodzi |
| 2 | Struktura: G1–G6 | testy pytest przechodzą |
| 3 | Bezpieczeństwo: S1–S9 | Hypothesis (E2) i TLC (E3) bez naruszeń |
| 4 | Żywotność: L1–L5 przy założeniach F1–F3 | TLC z warunkami sprawiedliwości bez naruszeń |
| 5 | Dowód w granicach `test_instance` z uzasadnieniem granic | OBS: wersja TLC, liczba stanów, czas |
| 6 | Każda właściwość ma mutanta, na którym pada | raport mutacji: 100% zabitych |
| 7 | Ścieżki świadkowie WIT1–WIT4 wygenerowane i przejrzane przez użytkownika | DEC z cytatem |
| 8 | Powiązania z ISO: każde przejście ma pole `iso`; każdy efekt PM.O1–O7, SI.O1–O7 pokryty przez co najmniej jedno przejście | test G6 |
| 9 | Sprawdzenia i dowody czytają ten sam `process.yaml`; odtworzenie historii vcs-lite wykrywa DEC-VCS-096 i Beyond Compare po DEC-VCS-102 | test odtworzenia |
| 10 | Niezależny przegląd i podpis użytkownika | protokół odbioru |

## Struktura (G) — analiza grafu, E2

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| G0 | Słownik zamknięty | każdy stan użyty w `from` i `to` jest zdefiniowany; każdy aktor istnieje; każdy stan elementu ma `iso`; zbiory stanów w `guard` istnieją | stan `approved` przemianowany tylko w jednym przejściu |
| G1 | Osiągalność | każdy stan osiągalny ze stanu `none` | usunięte T02 → `approved` nieosiągalny dla REQ |
| G2 | Brak martwych przejść | każde przejście jest możliwe w jakimś osiągalnym stanie systemu (warunek spełnialny) | `guard` T04 wymaga `state = approved` także dla CODE |
| G3 | Brak ślepych stanów | każdy stan niekońcowy ma przejście wyjściowe | usunięte T10 → `deferred` bez wyjścia |
| G4 | Determinizm | z danego stanu dane przejście prowadzi do dokładnie jednego stanu | T03 z dwoma stanami docelowymi |
| G5 | Kompletność | dla każdej pary (stan, przejście) przejście jest zdefiniowane albo jawnie niedozwolone | — (raport, nie test) |
| G6 | Pokrycie ISO | każdy efekt PM.O1–O7, SI.O1–O7 wskazany przez co najmniej jedno przejście | usunięte W04 → PM.O2 (odbiór) niepokryty |

## Bezpieczeństwo (S) — Hypothesis w E2, TLC w E3

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| S1 | **Bramki użytkownika.** Tylko U wykonuje przejścia z `USER_GATES` | dla każdego kroku: `transition in USER_GATES => actor = U` | T04 z aktorem A (agent sam tworzy linię bazową) |
| S2 | **Brak obejścia zatwierdzenia.** Element wymagający zatwierdzenia nie jest bazowy bez zatwierdzenia w tej wersji | `G(e.state = baselined and type(e).requires_approval => O(e.state = approved and e.version unchanged))` | T04 dopuszcza `from: verified` dla REQ |
| S3 | **Brak obejścia weryfikacji.** Zatwierdzony lub bazowy tylko po weryfikacji w tej wersji | `G(e.state in {approved, baselined} => O(e.state = verified))` | T02 z `from: [draft]` |
| S4 | **Budowanie na zatwierdzonym** | `G(e.state in {verified, approved, baselined} => (e.suspect or forall d in deps(e): d.state in {approved, baselined}))` | T01 bez warunku na zależności |
| S5 | **Zmiana oznacza zależne** | po T05–T08 na `e`: `forall d in dependents(e): d.suspect or inactive(d)` | skutek „oznacz zależne” usunięty z T07 (sprawa Beyond Compare) |
| S6 | **Nic aktywnego nie wskazuje wycofanego** (REQ-208 szablonu) | `G(e.state in {verified, approved, baselined} and not e.suspect => forall d in deps(e): d.state not in {superseded, withdrawn})` | T11 bez warunku na wycofane zależności |
| S7 | **Odbiór tylko kompletnego wydania** | `G(rel.state in {ready, reviewed, accepted} => forall e in release_scope: e.state in {baselined, deferred, superseded, withdrawn} and (e.state = baselined => not e.suspect))` | `invalidate_release` usunięte ze skutków T05 (zmiana po przeglądzie) |
| S8 | **Niezależność weryfikacji wydania.** Odbiór tylko po przeglądzie R | `G(rel.state = accepted => O(rel.state = reviewed))` | W04 z `from: [ready]` |
| S9 | **Jedna decyzja naraz** | `G(count(q.state = asked) <= 1)` | P01 bez warunku `count(asked) = 0` |

## Żywotność (L) — TLC z warunkami sprawiedliwości, E3

Żywotność zależy od tego, że ludzie i agent w końcu działają. Bez tych założeń żadna żywotność nie jest prawdziwa: użytkownik może nigdy nie odpowiedzieć. Zapisujemy je jawnie.

| ID | Założenie sprawiedliwości |
|---|---|
| F1 | Słaba sprawiedliwość dla A i R: przejście agenta stale możliwe w końcu zachodzi. |
| F2 | Silna sprawiedliwość dla P02: pytanie zadawane nieskończenie często w końcu dostaje odpowiedź jednoznaczną (użytkownik nie odpowiada niejednoznacznie bez końca). |
| F3 | Użytkownik w końcu wybiera jedną z dostępnych mu akcji wobec elementu `verified` i wydania `reviewed` (nie zostawia ich na zawsze). |

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| L1 | **Możliwość zakończenia** (brak zakleszczeń i uwięzienia) | `AG EF done` | T01 wymaga, by zależni byli zweryfikowani (cykl oczekiwania REQ ↔ AT) |
| L2 | **Brak zagłodzenia pytań** | `G(q.state = open => F(q.state in {resolved, deferred}))` przy F1, F2 | P01 wybiera najnowsze pytanie zamiast najstarszego (LIFO) |
| L3 | **Podejrzenia znikają** | `G(e.suspect => F(not e.suspect or inactive(e)))` przy F1, F3 | T12 bez utworzenia pytania (zgłoszenie znika w próżni) |
| L4 | **Ograniczona liczba poprawek** | `G(e.rejections <= MAX_REJECTIONS)` i brak nieskończonej pętli T01↔T03 w jednej wersji | warunek `rejections < MAX_REJECTIONS` usunięty z T03 |
| L5 | **Wydanie dochodzi do odbioru**, jeśli użytkownik nie zmienia zakresu | `G(rel.state = ready => F(rel.state in {accepted, in_preparation}))` i `(FG no T05–T09) => F(rel.state = accepted)` | W02 i W03 usunięte (recenzent nie może zakończyć przeglądu) |

## Ścieżki świadkowie (DoD 7)

Narzędzie wygeneruje je w E3 jako konkretne ciągi kroków na `test_instance`. Użytkownik sprawdza, czy tak ma wyglądać praca.

| ID | Scenariusz | Musi pokazać |
|---|---|---|
| WIT1 | Przebieg bez przeszkód | p1 → r1, r2 → a1, a2, d1 → c1 → wydanie `accepted`; każde zatwierdzenie i linia bazowa jako krok U |
| WIT2 | Odrzucenie i eskalacja | r1 odrzucone 2 razy; przy trzeciej propozycji U musi zatwierdzić, wycofać albo odłożyć |
| WIT3 | Zmiana w trakcie pracy | wydanie `reviewed`; U zastępuje r1; a1, d1, c1 podejrzane; wydanie wraca do `in_preparation`; agent przegląda, zgłasza zmianę a1; dalej do odbioru |
| WIT4 | Odpowiedź niejednoznaczna | pytanie `asked`, odpowiedź niejednoznaczna, pytanie wraca do kolejki jako najstarsze i jest zadane ponownie przed nowszymi |

## Znane ograniczenia modelu

- Model nie widzi działań poza nim (ręczna edycja pliku). Pokrywa to odtwarzanie historii w E4 i kontrola repozytorium w E5.
- Treść elementów jest abstrakcyjna: `checks_ok` i `tests_ok` są założone, nie modelowane.
- Granice instancji: 7 elementów, 3 pytania, 3 wersje. Uzasadnienie (hipoteza małego zakresu) zostanie zapisane razem z wynikiem w E3.
