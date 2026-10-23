# Właściwości modelu i Definition of Done

Właściwości, które model `model/process.yaml` musi spełniać. Każda ma: zapis formalny, narzędzie, które ją sprawdza, i **mutanta**: celowo zepsuty model, na którym musi paść (DoD 6). Status `PROPOZYCJA` do bramki E1.

Notacja: `G` zawsze, `F` kiedyś, `X` w następnym kroku, `O` kiedyś w przeszłości (LTL z przeszłością); `AG`, `EF`, `EX` z CTL. `e` to dowolny element, `q` dowolne pytanie, `w` wydanie.

## Definition of Done (pełna treść)

| DoD | Kryterium | Dowód zakończenia |
|---|---|---|
| 1 | Zamknięty słownik: każdy typ, stan, zmienna, przejście, aktor i warunek jest w `process.yaml`; każdy stan wskazuje stan Tabeli 12 normy albo INT | test G0 przechodzi |
| 2 | Struktura: G1–G5 | testy pytest przechodzą |
| 3 | Bezpieczeństwo: S1–S9 | Hypothesis (E2) i TLC (E3) bez naruszeń |
| 4 | Żywotność: L1–L5 przy założeniach F1–F3 | TLC z warunkami sprawiedliwości bez naruszeń |
| 5 | Dowód w granicach `instancja_testowa` z uzasadnieniem granic | OBS: wersja TLC, liczba stanów, czas |
| 6 | Każda właściwość ma mutanta, na którym pada | raport mutacji: 100% zabitych |
| 7 | Ścieżki świadkowie ŚW1–ŚW4 wygenerowane i przejrzane przez użytkownika | DEC z cytatem |
| 8 | Powiązania z ISO: każde przejście ma pole `iso`; każdy efekt PM.O1–O7, SI.O1–O7 pokryty przez co najmniej jedno przejście | test G6 |
| 9 | Sprawdzenia i dowody czytają ten sam `process.yaml`; odtworzenie historii vcs-lite wykrywa DEC-VCS-096 i Beyond Compare po DEC-VCS-102 | test odtworzenia |
| 10 | Niezależny przegląd i podpis użytkownika | protokół odbioru |

## Struktura (G) — analiza grafu, E2

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| G0 | Słownik zamknięty | każdy stan użyty w `z` i `do` jest zdefiniowany; każdy aktor istnieje; każdy stan ma `iso` | stan `zatwierdzony` przemianowany tylko w jednym przejściu |
| G1 | Osiągalność | każdy stan osiągalny ze stanu `brak` | usunięte T02 → `zatwierdzony` nieosiągalny dla REQ |
| G2 | Brak martwych przejść | każde przejście jest możliwe w jakimś osiągalnym stanie systemu (warunek spełnialny) | warunek T04 wymaga `stan = zatwierdzony` dla KOD |
| G3 | Brak ślepych stanów | każdy stan niekońcowy ma przejście wyjściowe | usunięte T10 → `odlozony` bez wyjścia |
| G4 | Determinizm | z danego stanu jedno zdarzenie prowadzi do co najwyżej jednego stanu | T03 z dwoma stanami docelowymi |
| G5 | Kompletność | dla każdej pary (stan, przejście) albo przejście jest zdefiniowane, albo jawnie niedozwolone | — (raport, nie test) |
| G6 | Pokrycie ISO | każdy efekt PM.O1–O7, SI.O1–O7 wskazany przez co najmniej jedno przejście | usunięte W04 → PM.O2 (odbiór) niepokryty |

## Bezpieczeństwo (S) — Hypothesis w E2, TLC w E3

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| S1 | **Bramki użytkownika.** Tylko U wykonuje T02–T10, P02–P04 i W04–W05 | dla każdego kroku: `przejscie in BRAMKI_U => aktor = U` | T04 z aktorem A (agent sam tworzy linię bazową) |
| S2 | **Brak obejścia zatwierdzenia.** Element wymagający zatwierdzenia nie jest bazowy bez zatwierdzenia w tej wersji | `G(e.stan = bazowy and typ(e).wymaga_zatwierdzenia => O(e.stan = zatwierdzony and wersja niezmieniona))` | T04 dopuszcza `z: zweryfikowany` dla REQ |
| S3 | **Brak obejścia weryfikacji.** Zatwierdzony lub bazowy tylko po weryfikacji w tej wersji | `G(e.stan in {zatwierdzony, bazowy} => O(e.stan = zweryfikowany))` | T02 z `z: [szkic]` |
| S4 | **Budowanie na zatwierdzonym.** Element zweryfikowany ma zatwierdzone lub bazowe zależności albo jest podejrzany | `G(e.stan in {zweryfikowany, zatwierdzony, bazowy} => (e.podejrzany or forall z in zal(e): z.stan in {zatwierdzony, bazowy}))` | T01 bez warunku na zależności |
| S5 | **Zmiana oznacza zależne.** Po T05–T08 na `e` każdy aktywny zależny jest podejrzany albo przejrzany | `G(X(e zmieniony) => X(forall d in zalezne(e): d.podejrzany or d nieaktywny))` | skutek „oznacz zależne” usunięty z T07 (sprawa Beyond Compare) |
| S6 | **Nic aktywnego nie wskazuje wycofanego** (REQ-208 szablonu) | `G(e.stan in {zweryfikowany, zatwierdzony, bazowy} and not e.podejrzany => forall z in zal(e): z.stan not in {zastapiony, wycofany})` | T11 bez warunku na wycofane zależności |
| S7 | **Odbiór tylko kompletnego wydania** | `G(w.stan in {gotowe, przejrzane, odebrane} => forall e in zakres: e.stan in {bazowy, odlozony, zastapiony, wycofany} and (e.stan = bazowy => not e.podejrzany))` | `uniewaznij_wydanie` usunięte ze skutków T05 (zmiana po przeglądzie) |
| S8 | **Niezależność weryfikacji wydania.** Odbiór tylko po przeglądzie R | `G(w.stan = odebrane => O(w.stan = przejrzane))` | W04 z `z: [gotowe]` |
| S9 | **Jedna decyzja naraz** | `G(liczba(q.stan = zadane) <= 1)` | P01 bez warunku `liczba(zadane) = 0` |

## Żywotność (L) — TLC z warunkami sprawiedliwości, E3

Żywotność zależy od tego, że ludzie i agent w końcu działają. Bez tych założeń żadna żywotność nie jest prawdziwa: użytkownik może nigdy nie odpowiedzieć. Zapisujemy je jawnie.

| ID | Założenie sprawiedliwości |
|---|---|
| F1 | Słaba sprawiedliwość dla A i R: przejście agenta stale możliwe w końcu zachodzi. |
| F2 | Silna sprawiedliwość dla P02: pytanie zadawane nieskończenie często w końcu dostaje odpowiedź jednoznaczną (użytkownik nie odpowiada niejednoznacznie bez końca). |
| F3 | Użytkownik w końcu wybiera jedną z dostępnych mu akcji wobec elementu zweryfikowanego i wydania przejrzanego (nie zostawia ich na zawsze). |

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| L1 | **Możliwość zakończenia** (brak zakleszczeń i uwięzienia) | `AG EF koniec`, gdzie `koniec ≡ w.stan = odebrane or forall e: e.stan in {zastapiony, wycofany}` | T01 wymaga, by zależni byli zweryfikowani (cykl oczekiwania REQ ↔ AT) |
| L2 | **Brak zagłodzenia pytań** | `G(q.stan = otwarte and q nieodłożone => F(q.stan in {rozstrzygniete, odlozone}))` przy F1, F2 | P01 wybiera najnowsze pytanie zamiast najstarszego (LIFO) |
| L3 | **Podejrzenia znikają** | `G(e.podejrzany => F(not e.podejrzany or e nieaktywny))` przy F1, F3 | T12 bez utworzenia Q (zgłoszenie znika w próżni) |
| L4 | **Ograniczona liczba poprawek** | `G(e.poprawki <= N_POPRAWEK)` oraz brak nieskończonej pętli T01↔T03 w jednej wersji | warunek `poprawki < N_POPRAWEK` usunięty z T03 |
| L5 | **Wydanie dochodzi do odbioru**, jeśli użytkownik nie zmienia zakresu | `G(w.stan = gotowe => F(w.stan in {odebrane, w_przygotowaniu}))` i `(FG brak T05–T09) => F(w.stan = odebrane)` | W02 i W03 usunięte (recenzent nie może zakończyć przeglądu) |

## Ścieżki świadkowie (DoD 7)

Narzędzie wygeneruje je w E3 jako konkretne ciągi kroków na `instancja_testowa`. Użytkownik sprawdza, czy tak ma wyglądać praca.

| ID | Scenariusz | Musi pokazać |
|---|---|---|
| ŚW1 | Przebieg bez przeszkód | k1 → r1, r2 → a1, a2, d1 → c1 → wydanie odebrane; każde zatwierdzenie i linia bazowa jako krok U |
| ŚW2 | Odrzucenie i eskalacja | r1 odrzucone 2 razy; trzecia propozycja: U musi zatwierdzić, wycofać albo odłożyć |
| ŚW3 | Zmiana w trakcie pracy | wydanie przejrzane; U zastępuje r1; a1, d1, c1 podejrzane; wydanie wraca do przygotowania; agent przegląda, zgłasza zmianę a1; dalej do odbioru |
| ŚW4 | Pytanie niejednoznaczne | Q zadane, odpowiedź niejednoznaczna, Q wraca do kolejki jako najstarsze i jest zadane ponownie przed nowszymi |

## Znane ograniczenia modelu

- Model nie widzi działań poza nim (ręczna edycja pliku). Pokrywa to odtwarzanie historii w E4 i kontrola repozytorium w E5.
- Treść elementów jest abstrakcyjna: `sprawdzenia_ok` i `testy_ok` są założone, nie modelowane.
- Granice instancji: 7 elementów, 3 pytania, 3 wersje. Uzasadnienie (hipoteza małego zakresu) zostanie zapisane razem z wynikiem w E3.
