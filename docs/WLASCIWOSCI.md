# Właściwości modelu i Definition of Done

Właściwości, które model `model/process.yaml` musi spełniać. Każda ma: zapis formalny, narzędzie, które ją sprawdza, i **mutanta**: celowo zepsuty model, na którym musi paść (DoD 6). Status `approved`: przyjęte jako podstawa E2 przez DEC-PRO-005 (2026-10-24). Korekta G3/G6 przyjęta przez DEC-PRO-006. DEC-PRO-008 (2026-10-25) przyjmuje regułę zgody i S11. Spełnienie właściwości wymaga jeszcze testów i dowodów.

Notacja: `G` zawsze, `F` kiedyś, `X` w następnym kroku, `O` kiedyś w przeszłości (LTL z przeszłością); `AG`, `EF`, `EX` z CTL. `e` to dowolny element, `q` dowolne pytanie, `rel` rekord wydania o ustalonym numerze `n`. `current ≡ releases[current_release]`; `pre` i `post` oznaczają stan przed i po kroku. Identyfikatory jak w modelu (DEC-PRO-002).

Predykaty pomocnicze:
- `USER_GATES = {T02, T03, T04, T05, T06, T07, T08, T09, T10, P02, P03, P04, W04, W05}`
- `complete(scope) ≡ forall e in scope: e.state in {baselined, deferred, superseded, withdrawn} and (e.state = baselined => not e.suspect)`; predykat odnosi się do produktów roboczych w danej chwili.
- `done ≡ not next_release_required and (current.state = accepted or forall e: e.state in {superseded, withdrawn})`. Odbiór wcześniejszego wydania nie kończy pracy nad nowszym; oczekujące W06 również wyklucza `done`.
- `scope_change ≡ krok T05–T10 na elemencie bieżącego zakresu lub pojawienie się suspect na elemencie tego zakresu`; identyczne zdarzenia wyzwalają W06 po odbiorze (DEC-PRO-003, DEC-PRO-004).
- `inactive(e) ≡ e.state in {deferred, superseded, withdrawn}`

Semantyka wielu wydań (DEC-PRO-003, INT-017): W04 utrwala własną kopię zakresu, migawkę elementów i protokół z numerem wydania. Późniejsze przejścia T dotyczą produktów roboczych. W06 tworzy nowy rekord, zwiększa `current_release` i nie zmienia starego rekordu. Znacznik `next_release_required` leży poza odebranym rekordem; gdy jest ustawiony, następnym przejściem musi być W06. Przejście to jest krokiem A, więc podlega F1. `accepted` pozostaje końcowe dla każdego numeru wydania.

## Definition of Done (pełna treść)

| DoD | Kryterium | Dowód zakończenia |
|---|---|---|
| 1 | Zamknięty słownik: każdy typ, stan, zmienna, przejście, aktor i warunek jest w `process.yaml`; każdy stan wskazuje stan Tabeli 12 normy albo INT | test G0 przechodzi |
| 2 | Struktura: G1–G6 | testy pytest przechodzą |
| 3 | Bezpieczeństwo: S1–S11, z S7a i S7b zamiast S7 | Hypothesis (E2) i TLC (E3) bez naruszeń |
| 4 | Żywotność: L1–L5 przy założeniach F1–F3 | TLC z warunkami sprawiedliwości bez naruszeń |
| 5 | Dowód w granicach `test_instance` z uzasadnieniem granic | OBS: wersja TLC, liczba stanów, czas |
| 6 | Każda właściwość ma mutanta, na którym pada | raport mutacji: 100% zabitych |
| 7 | Ścieżki świadkowie WIT1–WIT5 wygenerowane i przejrzane przez użytkownika | DEC z cytatem |
| 8 | Powiązania z ISO: każde przejście ma pole `iso`; każdy efekt PM.O1–O7, SI.O1–O7 pokryty przez co najmniej jedno przejście | test G6 |
| 9 | Sprawdzenia i dowody czytają ten sam `process.yaml`; odtworzenie historii vcs-lite wykrywa DEC-VCS-096 i Beyond Compare po DEC-VCS-102 | test odtworzenia |
| 10 | Niezależny przegląd i podpis użytkownika | protokół odbioru |

## Struktura (G) — analiza grafu, E2

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| G0 | Słownik zamknięty | każdy stan użyty w `from` i `to` jest zdefiniowany; każdy aktor istnieje; każdy stan elementu ma `iso`; zbiory stanów w `guard` istnieją | stan `approved` przemianowany tylko w jednym przejściu |
| G1 | Osiągalność | każdy stan osiągalny ze stanu początkowego: `none` dla elementów i pytań, `in_preparation` dla wydania; W06 tworzy nowy rekord, nie wychodzi z końcowego stanu starego | usunięte T02 → `approved` nieosiągalny dla REQ |
| G2 | Brak martwych przejść | każde przejście jest możliwe w jakimś osiągalnym stanie systemu (warunek spełnialny) | `guard` T04 wymaga `state = approved` także dla CODE |
| G3 | Brak ślepych stanów | każdy stan niekońcowy ma przejście wyjściowe | usunięte T07, T08 i T10 → `deferred` bez wyjścia (DEC-PRO-006) |
| G4 | Determinizm | z danego stanu dane przejście prowadzi do dokładnie jednego stanu; cel W06 to jednoznacznie nowy rekord numer `current_release + 1` | T03 z dwoma stanami docelowymi |
| G5 | Kompletność | dla każdej pary (stan, przejście) przejście jest zdefiniowane albo jawnie niedozwolone | — (raport, nie test) |
| G6 | Pokrycie ISO | każdy efekt PM.O1–O7, SI.O1–O7 wskazany przez co najmniej jedno przejście | usunięte W04 → PM.O2 (odbiór) niepokryty |

G6 sprawdza jawne powiązania zapisane w polach `iso`, w tym PM.O1–PM.O7 i SI.O1–SI.O7 (DEC-PRO-006). Nie dowodzi realizacji wszystkich składowych efektu ISO. Dla przejścia wielotypowego adnotacja dotyczy właściwego zastosowania, np. PM.O1 dla T02 na PLAN. Uzasadnienia przyjętych adnotacji: `model/proposals/e2-structure.yaml`; źródłem danych testów pozostaje `model/process.yaml`.

## Bezpieczeństwo (S) — Hypothesis w E2, TLC w E3

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| S1 | **Bramki użytkownika.** Tylko U wykonuje przejścia z `USER_GATES` | dla każdego kroku: `transition in USER_GATES => actor = U` | T04 z aktorem A (agent sam tworzy linię bazową) |
| S2 | **Brak obejścia zatwierdzenia.** Element wymagający zatwierdzenia nie jest bazowy bez zatwierdzenia w tej wersji | `G(e.state = baselined and type(e).requires_approval => O(e.state = approved and e.version unchanged))` | T04 dopuszcza `from: verified` dla REQ |
| S3 | **Brak obejścia weryfikacji.** Zatwierdzony lub bazowy tylko po weryfikacji w tej wersji | `G(e.state in {approved, baselined} => O(e.state = verified))` | T02 z `from: [draft]` |
| S4 | **Budowanie na zatwierdzonym** | `G(e.state in {verified, approved, baselined} => (e.suspect or forall d in deps(e): d.state in {approved, baselined}))` | T01 bez warunku na zależności |
| S5 | **Zmiana oznacza zależne** | po T05–T08 na `e`: `forall d in dependents(e): d.suspect or inactive(d)` | skutek „oznacz zależne” usunięty z T07 (sprawa Beyond Compare) |
| S6 | **Nic aktywnego nie wskazuje wycofanego** (REQ-208 szablonu) | `G(e.state in {verified, approved, baselined} and not e.suspect => forall d in deps(e): d.state not in {superseded, withdrawn})` | T11 bez warunku na wycofane zależności |
| S7a | **Kompletność wydania gotowego i przejrzanego** | `G(current.state in {ready, reviewed} => complete(current.scope))` | `invalidate_release` usunięte ze skutków T05: zmiana elementu wydania `reviewed` pozostawia niekompletne wydanie w tym stanie |
| S7b | **Kompletność w chwili odbioru** (właściwość kroku) | dla każdego kroku W04: `complete(pre.current.scope)` oraz `post.releases[pre.current_release].snapshot = snapshot(pre.current.scope)` | W04 z `from: [in_preparation]` zamiast `[reviewed]` pozwala odebrać zakres zawierający `draft` |
| S8 | **Niezależność weryfikacji wydania.** Odbiór tylko po przeglądzie R tego samego wydania | dla każdego istniejącego numeru `n`: `G(releases[n].state = accepted => O(releases[n].state = reviewed))` | W04 z `from: [ready]` |
| S9 | **Jedna decyzja naraz** | `G(count(q.state = asked) <= 1)` | P01 bez warunku `count(asked) = 0` |
| S10 | **Niezmienność odebranego wydania.** Nie zmieniają się stan, numer, zakres, migawka ani protokół | dla każdego kroku i numeru `n` istniejącego w `pre`: `pre.releases[n].state = accepted => (n in post.releases and post.releases[n] = pre.releases[n])` | W06 nadpisuje odebrany rekord stanem `in_preparation` zamiast utworzyć rekord `n + 1`; wariant mutanta: migawka współdzieli zmienne elementy i zmienia się po T05 |
| S11 | **Zgoda na konkretną operację** | każdy krok T05/T07: `pre.authorized_change(q,e)` oraz `post.q.consumed = true`; P01–P05 zachowują powiązanie kind/about/about_version/requested_transition i consumed | usunięcie kolejno wymogu approved, zgodności elementu, wersji, operacji, niewykorzystania lub skutku consumed=true; P03 zmienia powiązanie |

S7 v0.2 jest zastąpione przez S7a i S7b (DEC-PRO-003). S7b ocenia produkty w chwili podpisu; S10 chroni wynik tego podpisu także wtedy, gdy produkty robocze zostały już zmienione. Nie wymagamy, aby dzisiejszy stan produktów nadal odpowiadał każdej historycznej dostawie.

## Żywotność (L) — TLC z warunkami sprawiedliwości, E3

Żywotność zależy od tego, że ludzie i agent w końcu działają. Bez tych założeń żadna żywotność nie jest prawdziwa: użytkownik może nigdy nie odpowiedzieć. Zapisujemy je jawnie.

| ID | Założenie sprawiedliwości |
|---|---|
| F1 | Słaba sprawiedliwość dla A i R: przejście agenta stale możliwe w końcu zachodzi. |
| F2 | Silna sprawiedliwość dla P02: pytanie zadawane nieskończenie często w końcu dostaje odpowiedź jednoznaczną (użytkownik nie odpowiada niejednoznacznie bez końca). |
| F3 | Użytkownik w końcu wybiera jedną z dostępnych mu akcji wobec elementu `verified` i wydania `reviewed` (nie zostawia ich na zawsze). |

| ID | Właściwość | Formalnie | Mutant |
|---|---|---|---|
| L1 | **Możliwość zakończenia bieżącej pracy** (brak zakleszczeń i uwięzienia, również po wcześniejszym odbiorze) | `AG EF done`, z definicją `done` uwzględniającą najnowsze wydanie i oczekujące W06 | usunięte W06: po zmianie odebranego elementu `next_release_required` pozostaje ustawione i nie ma ścieżki do `done` |
| L2 | **Brak zagłodzenia pytań** | `G(q.state = open => F(q.state in {resolved, deferred}))` przy F1, F2 | P01 wybiera najnowsze pytanie zamiast najstarszego (LIFO) |
| L3 | **Podejrzenia znikają** | `G(e.suspect => F(not e.suspect or inactive(e)))` przy F1, F3 | T12 bez utworzenia pytania (zgłoszenie znika w próżni) |
| L4 | **Ograniczona liczba poprawek** | `G(e.rejections <= MAX_REJECTIONS)` i brak nieskończonej pętli T01↔T03 w jednej wersji | warunek `rejections < MAX_REJECTIONS` usunięty z T03 |
| L5 | **Postęp kolejnych wydań**, a po ustaniu zmian trwały odbiór najnowszego | dla każdego numeru `n`: `G(releases[n].state = ready => F(releases[n].state in {accepted, in_preparation}))` i `G(next_release_required and current_release = n => F(current_release = n + 1))`; ponadto `(FG not scope_change) => FG(current.state = accepted and not next_release_required)` przy F1–F3 | usunięte W06 (brak postępu po odbiorze); usunięte W02 i W03 (brak zakończenia przeglądu) |

W L5 numer `n` jest ustalony w chwili sprawdzania zobowiązania; przegląd lub odbiór innego numeru go nie spełnia. Ostatnia formuła wyklucza pozorne spełnienie przez historyczny odbiór wydania 1, gdy wydanie 2 nadal czeka. Są to wymagania do sprawdzenia w E3, nie deklaracja dowodu pod F1–F3.

## Ścieżki świadkowie (DoD 7)

Narzędzie wygeneruje je w E3 jako konkretne ciągi kroków na `test_instance`. Użytkownik sprawdza, czy tak ma wyglądać praca. Poniżej opis zamiaru; WIT5 ma dodatkowo ręcznie rozpisany przebieg do przeglądu E1.

| ID | Scenariusz | Musi pokazać |
|---|---|---|
| WIT1 | Przebieg bez przeszkód | p1 → r1, r2 → a1, a2, d1 → c1 → wydanie `accepted`; każde zatwierdzenie i linia bazowa jako krok U |
| WIT2 | Odrzucenie i eskalacja | r1 odrzucone 2 razy; przy trzeciej propozycji U musi zatwierdzić, wycofać albo odłożyć |
| WIT3 | Zmiana w trakcie pracy | wydanie `reviewed`; U zastępuje r1; a1, d1, c1 podejrzane; wydanie wraca do `in_preparation`; agent przegląda, zgłasza zmianę a1; dalej do odbioru |
| WIT4 | Odpowiedź niejednoznaczna | pytanie `asked`, odpowiedź niejednoznaczna, pytanie wraca do kolejki jako najstarsze i jest zadane ponownie przed nowszymi |
| WIT5 | Zmiana po odbiorze | wydanie 1 `accepted`; U udziela zgody na a2 v1 / T05 i wykonuje T05; znacznik wymusza W06 wykonywane przez A; wydanie 2 przechodzi weryfikację, przegląd R i odbiór U; wydanie 1 pozostaje identyczne |

### WIT5 — przebieg do przeglądu E1

1. WIT1 kończy się W04 dla wydania 1: zakres to siedem ID z `test_instance.release_scope`, a wszystkie elementy są `baselined`; migawka zawiera a2 w wersji 1.
2. P00 → P01 → P02: użytkownik udziela zgody approved na T05 dla a2 w wersji 1; pytanie ma kind=change i blocking=true. T05 wskazuje to pytanie, sprawdza authorized_change i atomowo oznacza consumed=true (S11). T05 na a2 ustawia `draft`, wersję 2 oraz `next_release_required = true`. Rekord wydania 1 nadal ma stan `accepted` i niezmienioną migawkę a2 w wersji 1; `done = false`.
3. Następnym krokiem jest W06 (A): powstaje rekord wydania 2 z kopią zakresu, stanem `in_preparation`, bez migawki i protokołu; znacznik zostaje skasowany. T05 nie zmieniło r2, od którego zależy a2; r2 nadal jest `baselined`.
4. T01(a2), T02(a2), T04(a2): a2 w wersji 2 zostaje zweryfikowane, zatwierdzone i włączone do linii bazowej. Przy przechodzących testach W01 → W02(R) → W04(U) kończą wydanie 2.
5. Oba rekordy mają `accepted`, lecz osobne migawki: a2 w wersji 1 i a2 w wersji 2. `current_release = 2`, `done = true`. Przebieg mieści się w limitach: 2 wydania, 2 wersje a2 i 1 pytanie o zmianę.

Przypadek uzupełniający dla W06: zmiana elementu spoza zakresu, która ustawia `suspect` na elemencie zakresu, również ustawia znacznik przez `detect_post_acceptance_change`. Samo istnienie starszego `accepted` nie otwiera kolejnych wydań bez nowego zdarzenia.

Przypadek wznowienia (DEC-PRO-004): a2 jest `deferred` podczas W01. Jeśli U wykona T10 przy wydaniu `ready` lub `reviewed`, a2 wraca do `draft`, a wydanie do `in_preparation` (S7a). Jeśli najpierw nastąpi W04, późniejsze T10 ustawia znacznik i wymusza W06; migawka wydania 1 nadal zawiera a2 jako `deferred` (S7b, S10). Usunięcie `invalidate_release` z T10 jest dodatkowym mutantem S7a.

## Znane ograniczenia modelu

- Model nie widzi działań poza nim (ręczna edycja pliku). Pokrywa to odtwarzanie historii w E4 i kontrola repozytorium w E5.
- Treść elementów jest abstrakcyjna: `checks_ok` i `tests_ok` są założone, nie modelowane.
- Granice instancji: 7 elementów, 3 pytania, 3 wersje, 2 wydania. Dwa wydania pozwalają sprawdzić oddzielenie migawki odbioru od dalszych zmian i WIT5. Nie jest to dowód dla dowolnej liczby wydań; uzasadnienie granic zostanie zapisane razem z wynikiem w E3.
- `max_releases` ogranicza badanie, nie proces. Przekroczenie granicy należy raportować jako wyjście poza badany zakres; nie wolno wyłączać W06 i przedstawiać sztucznego zakleszczenia jako błędu procesu ani ignorować niespełnionej żywotności na granicy.
