# Wywiad — runda 3

Data: 2026-10-26. Zapis pytania i widocznej odpowiedzi bez zmian treści. Relacja uczestnika wymaga weryfikacji; korekty w kolejnych rundach i [ustaleniach wstępnych](WNIOSKI-WSTEPNE.md).

## Pytanie

RUNDA 3 — recenzja naszego rozwiązania, po rekonstrukcji Twojego doświadczenia.
Najpierw korekta: DEC-VCS-096 stwierdza wyłącznie spełnienie punktu „przez tydzień zastępuje PyCharm” (odczytanie agenta, do podważenia). SPEC DoD v1 ma także wszystkie @confirmed automatyczne, pomiar VER-006 i brak blokujących pytań. Źródłowa wiadomość 1f11a96a-1444-4ccb-abc6-13715d772983 mówi o PUNKCIE DoD. Wycofaj wniosek „formalny projekt zamknięty / cały DoD spełniony”: przedstawione dowody tego nie uzasadniają. Nie twierdzimy też odwrotnie, że odbioru na pewno nie było.
Brak użycia punktu wznowienia później w tej samej sesji nie dowodzi jego rytualności: służy następnej sesji. Zmiana chwili nadania @confirmed nie dowodzi sama zmiany definicji znacznika. Rozróżniaj sprzeczność, ryzyko i niewiedzę. Potwierdzam fa90b77 z czerwoną kontrolą brakujących AT-061–063 oraz DEC122 jako późniejsze przyjęcie odstępstwa H48.

NASZ PROJEKT iso-model-state:
Cel: lekki sposób pracy jednego operatora z agentem i niezależnym recenzentem; zachowanie kontekstu, kontrola zgód i wpływu zmian, mały koszt utrzymania. ISO/IEC 29110 inspiruje dobór reguł; nie deklarujemy certyfikacji. Model v0.7 w YAML opisuje produkty PLAN/REQ/DES/CODE/TEST, pytania oraz wydania. PLAN/REQ/TEST wymagają zatwierdzenia U; DES/CODE nie mają tego samego obowiązku, lecz utworzenie linii bazowej to bramka U. R to osobny przebieg bez historii tworzenia.
Reguły: zmiana zatwierdzonego/bazowego produktu przez T05 wymaga pozytywnej, niewykorzystanej zgody powiązanej z ID, wersją i konkretną operacją; zgoda zużywana atomowo przy otwarciu zmiany, NIE zatwierdza automatycznie treści przyszłej poprawki. T06 daje U podważenie DES/CODE. Wpływ zmiany oznacza zależnych suspect; agent może po udokumentowanym przeglądzie stwierdzić brak wpływu T11. Zastąpienie wymaga jawnej naprawy powiązań i zakresu. Odbiór W04 wymaga reviewed przez R i braku pytań blokujących; utrwala niezmienny rekord wydania i migawkę. Zmiana po odbiorze wymusza nowe wydanie W06.
Pytania general rozstrzygnięte jako answered, change jako approved/rejected. Jedno asked naraz; blocking mają priorytet. Dwa odrzucenia na jedną wersję (MAX_REJECTIONS=2), T10 nie resetuje budżetu. tests_ok/checks_ok to wejścia zewnętrzne: model NIE dowodzi jakości testu ani zgodności wymagania z zamiarem. Nie interpretuje języka naturalnego; zdarzenia i wyniki dostarcza otoczenie.
E2: interpreter Python, pięć zadanych ścieżek WIT, generowane sekwencje Hypothesis, niezależne wyrocznie i celowo zepsute modele. 389 testów; 48/48 prób mutantów; to skończone sprawdzenia. E2 czeka na odbiór użytkownika. E3 planuje formalizację TLA+/TLC w granicach instancji, E4 odtworzenie historii vcs-lite, E5 włączenie do szablonu i osobno uzgodniony pilotaż. Kryteria użytkowe obejmują poprawne wznowienie, zakres zgód, wpływ zmiany, wiarygodny odbiór, zrozumiałość raportu i akceptowalny koszt. Nie znamy jeszcze kosztu użytkowego.

Poniżej pełna karta celu oraz przyjęte właściwości, żebyś nie oceniał wyłącznie reklamowego skrótu:

--- KARTA ---
# Karta celu i zakresu projektu iso-model-state

Data przyjęcia: 2026-10-24. Status: **przyjęta — DEC-PRO-007**, odpowiedź użytkownika: „d1 tak”. Karta jest dokumentem zamiaru i określa cel użytkowy. Obowiązujące etapy E2–E5 i DoD pozostają w [PLAN.md](../PLAN.md).

## Cel użytkowy

**Opracować i sprawdzić na jednym rzeczywistym projekcie lekki sposób współpracy operatora z agentem, który zachowuje kontekst, pilnuje zatwierdzeń i pokazuje skutki zmian.**

Operator ma zachować kontrolę nad zamiarem i ważnymi decyzjami, a agent samodzielnie wykonywać pracę w uzgodnionych granicach. Dokumenty i narzędzia mają ograniczać ręczne pilnowanie spójności projektu. Norma ISO/IEC 29110 jest podstawą doboru reguł; model i testy służą sprawdzeniu ich działania.

## Problemy i oczekiwane korzyści

| Problem w pracy | Oczekiwany rezultat dla operatora |
|---|---|
| Po przerwie albo zmianie agenta trzeba odtwarzać ustalenia | Wiadomo, co obowiązuje, co jest otwarte i jaki jest następny krok |
| Propozycja, decyzja i wykonanie mieszają się ze sobą | Można odróżnić pomysł od zatwierdzonego wymagania i wskazać źródło zgody |
| Zmiana wymagania pozostawia nieaktualne dokumenty, testy lub kod | Widoczna jest lista zależnych elementów wymagających przeglądu |
| Po kolejnych zmianach nie wiadomo, co zostało odebrane | Odbiór wskazuje konkretną, niezmienną migawkę wydania |
| Każdy projekt wymaga ponownego ustalania sposobu pracy | Sprawdzony zestaw zasad, dokumentów i poleceń można zastosować ponownie |

## Zakres pierwszego zastosowania

Jeden operator, agent wykonujący, niezależny przegląd i jedno repozytorium. Operator ustala zamiar, granice i podejmuje wymagane decyzje; agent przygotowuje propozycje, wykonuje pracę, weryfikuje ją i utrzymuje zapisy.

Przećwiczymy trzy sytuacje:

1. Zwykła realizacja: od ustalenia zakresu i wymagań do przeglądu oraz odbioru.
2. Odrzucenie propozycji lub niejednoznaczna odpowiedź: poprawa, kolejka pytań i rozstrzygnięcie bez domyślania się zgody.
3. Zmiana zaakceptowanego elementu: ocena wpływu na zależności, wymagane zatwierdzenia i następne wydanie z zachowaniem wcześniejszego odbioru.

`vcs-lite` jest wskazanym w obecnym planie projektem do odtworzenia historii. Dostęp do tej historii pozostaje do uzgodnienia. Proponowany pilotaż bieżącej pracy obejmie jeden uzgodniony przypadek; jego wybór i granice ustalimy przed rozpoczęciem.

Poza pierwszym zastosowaniem są: zarządzanie wieloma zespołami, rozbudowany interfejs graficzny, certyfikacja lub pełny audyt zgodności z normą oraz przewidywanie czasu, kosztu i produktywności. Obecna symulacja bada dopuszczalne przebiegi procesu.

## Co ma powstać

- **Zasady współpracy:** odpowiedzialności operatora i agenta, bramki decyzji oraz sposób obsługi zmian.
- **Minimalny zestaw zapisów:** cel i zakres, wymagania, decyzje, powiązania, punkt wznowienia i odbiór; zakres dokumentacji dopasowany do przypadku użycia.
- **Program sprawdzający:** raport naruszeń z konkretnymi elementami i dowodami, możliwy do użycia na wybranym repozytorium.
- **Sprawdzony przykład:** odtwarzalny przebieg oraz instrukcja zastosowania w kolejnym projekcie.
- **Ocena użyteczności:** wykryte problemy, fałszywe alarmy i nakład pracy na utrzymanie procesu.

## Kryteria sukcesu użytkowego

| Kryterium | Jak je sprawdzimy |
|---|---|
| Można wznowić pracę bez ponownego opowiadania historii | Nowy przebieg agenta poprawnie wskazuje obowiązujący zakres, ostatnie decyzje, otwarte sprawy i następny krok na podstawie repozytorium |
| Zgody są przypisane do właściwych działań | W przygotowanych przypadkach kontrolnych wykrywane są próby pominięcia wymaganej zgody; poprawne przebiegi przechodzą |
| Zmiana ma widoczny wpływ | Dla wybranej zmiany raport wskazuje uzgodniony zbiór zależnych elementów; przegląd potwierdza kompletność tej listy |
| Historia odbiorów jest wiarygodna | Zmiana po odbiorze prowadzi do kolejnego wydania, a wcześniejszy zakres, migawka i protokół pozostają identyczne |
| Narzędzie pomaga podjąć działanie | Operator potrafi na podstawie raportu ustalić, co wymaga poprawy, przeglądu lub decyzji |
| Koszt procesu jest akceptowalny | W pilotażu mierzymy czas przygotowania decyzji i utrzymania zapisów oraz liczbę fałszywych alarmów; porównujemy z dotychczasową pracą. Dopuszczalny narzut ustalamy przed pilotażem |

Powyższe kryteria uzupełniają ocenę korzyści. Obowiązujący DoD techniczny, w tym dowody w podanych granicach, pozostaje w PLAN.md.

## Jak kierować dalszymi pracami

Każdy kolejny przyrost powinien wskazywać: **problem operatora → regułę procesu → sprawdzalny przypadek → dowód działania → koszt obsługi**. Pozwala to oceniać wartość pracy technicznej i utrzymywać zakres.

| Obecny etap | Jego znaczenie dla celu użytkowego |
|---|---|
| E2 — wykonanie i testy modelu | Sprawdza, czy reguły poprawnie obsługują sytuacje, z którymi spotka się operator |
| E3 — dowody w granicach instancji | Ogranicza ryzyko obejść i zakleszczeń niewidocznych w pojedynczych przykładach |
| E4 — odtworzenie historii projektu | Sprawdza, czy model rozpoznaje znane problemy i poprawne przebiegi rzeczywistej pracy |
| E5 — zastosowanie w szablonie | Dostarcza sposób użycia; proponowany ograniczony pilotaż pozwoli ocenić użyteczność i nakład pracy |

Bieżący stan realizacji i następny krok są w [STAN.md](STAN.md). Przyjęcie karty nie oznacza osiągnięcia jej celów ani odbioru etapu. Ewentualna zmiana zakresu lub kolejności E2–E5 wymaga osobnej decyzji.

--- WŁAŚCIWOŚCI ---
# Właściwości modelu i Definition of Done

Właściwości, które model `model/process.yaml` musi spełniać. Każda ma: zapis formalny, narzędzie, które ją sprawdza, i **mutanta**: celowo zepsuty model, na którym musi paść (DoD 6). Status `approved`: przyjęte jako podstawa E2 przez DEC-PRO-005 (2026-10-24). Korekta G3/G6 przyjęta przez DEC-PRO-006. DEC-PRO-008 (2026-10-25) przyjmuje regułę zgody i S11. DEC-PRO-009 (2026-10-25) przyjmuje v0.6, korektę T11 i S12/S13. DEC-PRO-010 (2026-10-26) przyjmuje v0.7, S14/S15 i doprecyzowanie L4. Spełnienie właściwości wymaga testów i dowodów.

Notacja: `G` zawsze, `F` kiedyś, `X` w następnym kroku, `O` kiedyś w przeszłości (LTL z przeszłością); `AG`, `EF`, `EX` z CTL. `e` to dowolny element, `q` dowolne pytanie, `rel` rekord wydania o ustalonym numerze `n`. `current ≡ releases[current_release]`; `pre` i `post` oznaczają stan przed i po kroku. Identyfikatory jak w modelu (DEC-PRO-002).

Predykaty pomocnicze:
- `USER_GATES = {T02, T03, T04, T05, T06, T07, T08, T09, T10, P02, P03, P04, W04, W05, W07}`
- `complete(scope) ≡ forall e in scope: e.state in {baselined, deferred, superseded, withdrawn} and (e.state = baselined => not e.suspect)`; predykat odnosi się do produktów roboczych w danej chwili.
- `done ≡ not next_release_required and (current.state = accepted or forall e: e.state in {superseded, withdrawn})`. Odbiór wcześniejszego wydania nie kończy pracy nad nowszym; oczekujące W06 również wyklucza `done`.
- `scope_change ≡ krok T05–T10 lub T14 na elemencie bieżącego zakresu, W07 lub pojawienie się suspect na elemencie tego zakresu`. T14/W07 wymagają in_preparation; wyzwalacze W06 po odbiorze pozostają zgodne z DEC-PRO-003/004.
- `inactive(e) ≡ e.state in {deferred, superseded, withdrawn}`

Semantyka wielu wydań (DEC-PRO-003, INT-017): W04 utrwala własną kopię zakresu, migawkę elementów i protokół z numerem wydania. Późniejsze przejścia T dotyczą produktów roboczych. W06 tworzy nowy rekord, zwiększa `current_release` i nie zmienia starego rekordu. Znacznik `next_release_required` leży poza odebranym rekordem; gdy jest ustawiony, następnym przejściem musi być W06. Przejście to jest krokiem A, więc podlega F1. `accepted` pozostaje końcowe dla każdego numeru wydania.

## Definition of Done (pełna treść)

| DoD | Kryterium | Dowód zakończenia |
|---|---|---|
| 1 | Zamknięty słownik: każdy typ, stan, zmienna, przejście, aktor i warunek jest w `process.yaml`; każdy stan wskazuje stan Tabeli 12 normy albo INT | test G0 przechodzi |
| 2 | Struktura: G1–G6 | testy pytest przechodzą |
| 3 | Bezpieczeństwo: S1–S15, z S7a i S7b zamiast S7 | Hypothesis (E2) i TLC (E3) bez naruszeń |
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
| S5 | **Zmiana oznacza zależne** | po T05–T08 oraz T14 na `e` (zależni w grafie `pre`): `forall d in dependents(e): d.suspect or inactive(d)` | skutek „oznacz zależne” usunięty z T07 (sprawa Beyond Compare) |
| S6 | **Nic aktywnego nie wskazuje wycofanego** (REQ-208 szablonu) | `G(e.state in {verified, approved, baselined} and not e.suspect => forall d in deps(e): d.state not in {superseded, withdrawn})` | T11 z guard=suspect pomija kontrolę zależności i kasuje flagę mimo superseded r1 |
| S7a | **Kompletność wydania gotowego i przejrzanego** | `G(current.state in {ready, reviewed} => complete(current.scope))` | `invalidate_release` usunięte ze skutków T05: zmiana elementu wydania `reviewed` pozostawia niekompletne wydanie w tym stanie |
| S7b | **Kompletność w chwili odbioru** (właściwość kroku) | dla każdego kroku W04: `complete(pre.current.scope)` oraz `post.releases[pre.current_release].snapshot = snapshot(pre.current.scope)` | W04 z `from: [in_preparation]` zamiast `[reviewed]` pozwala odebrać zakres zawierający `draft` |
| S8 | **Niezależność weryfikacji wydania.** Odbiór tylko po przeglądzie R tego samego wydania | dla każdego istniejącego numeru `n`: `G(releases[n].state = accepted => O(releases[n].state = reviewed))` | W04 z `from: [ready]` |
| S9 | **Jedna decyzja naraz** | `G(count(q.state = asked) <= 1)` | P01 bez warunku `count(asked) = 0` |
| S10 | **Niezmienność odebranego wydania.** Nie zmieniają się stan, numer, zakres, migawka ani protokół | dla każdego kroku i numeru `n` istniejącego w `pre`: `pre.releases[n].state = accepted => (n in post.releases and post.releases[n] = pre.releases[n])` | W06 nadpisuje odebrany rekord stanem `in_preparation` zamiast utworzyć rekord `n + 1`; wariant mutanta: migawka współdzieli zmienne elementy i zmienia się po T05 |
| S11 | **Zgoda na konkretną operację** | każdy krok T05/T07: `pre.authorized_change(q,e)` oraz `post.q.consumed = true`; P01–P05 zachowują powiązanie kind/about/about_version/requested_transition i consumed | usunięcie kolejno wymogu approved, zgodności elementu, wersji, operacji, niewykorzystania lub skutku consumed=true; P03 zmienia powiązanie |
| S12 | **Kontrolowana zmiana powiązań** | poza inicjalizacją zmiana depends_on tylko w T14 na draft i zgodnie z guard: dokładnie jedna krawędź do wskazanego następcy, poprawne typy, bez cyklu/duplikatu; zależni z pre oznaczeni. predecessor zapisywany tylko w T00 zgodnie z guard i potem niezmienny | T14 dopuszcza baselined, usuwa niewskazane krawędzie lub propagację; T00 pomija kontrolę poprzednika; T14 nadpisuje predecessor |
| S13 | **Kontrolowane rozszerzenie zakresu** | zmiana scope istniejącego rekordu tylko w W07 przez U z in_preparation: post.scope = pre.scope union {e.id}, pozostałe pola rekordu bez zmian, spełniony guard W07. W06 tworzy nowy rekord; accepted chroni S10 | W07 aktora A, z reviewed/accepted, usuwa poprzednika z zakresu albo pomija dojrzałość następcy |
| S14 | **Brak blokad przy odbiorze** | dla każdego W04: `not exists q in pre.questions: q.blocking and q.state in {open, asked}`; późniejsze pytania nie zmieniają odebranego rekordu | W04 z guard=true dopuszcza blocker zgłoszony po W02 |
| S15 | **Budżet odrzuceń wersji** | dla każdej pary (ID, version) liczba wykonanych T03 w historii <= MAX_REJECTIONS; T10 zachowuje rejections, a T05/T06 zerują licznik przy nowej wersji | T10 zeruje rejections bez zmiany version, pozwalając na trzecie T03 tej samej wersji |

S14/S15 przyjęto przez DEC-PRO-010. W01 obejmuje globalne tests_ok i brak pytań również dla pustego scope. Nowy suspect w zakresie cofa ready/reviewed do in_preparation także po zmianie spoza scope; accepted nadal chroni S10 i obowiązkowe W06. Alternatywne zakresy są osobnymi instancjami badania, nie modyfikacją świadków podstawowej instancji.

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
| L4 | **Ograniczona liczba poprawek** | `G(e.rejections <= MAX_REJECTIONS)` oraz historyczny budżet S15 dla każdej wersji; brak nieskończonej pętli T01↔T03 w jednej wersji, także przez T09/T10 | warunek `rejections < MAX_REJECTIONS` usunięty z T03; T10 zeruje licznik tej samej wersji |
| L5 | **Postęp kolejnych wydań**, a po ustaniu zmian trwały odbiór najnowszego | dla każdego numeru `n`: `G(releases[n].state = ready => F(releases[n].state in {accepted, in_preparation}))` i `G(next_release_required and current_release = n => F(current_release = n + 1))`; ponadto `(FG not scope_change) => FG(current.state = accepted and not next_release_required)` przy F1–F3 | usunięte W06 (brak postępu po odbiorze); usunięte W02 i W03 (brak zakończenia przeglądu) |

W L5 numer `n` jest ustalony w chwili sprawdzania zobowiązania; przegląd lub odbiór innego numeru go nie spełnia. Ostatnia formuła wyklucza pozorne spełnienie przez historyczny odbiór wydania 1, gdy wydanie 2 nadal czeka. Są to wymagania do sprawdzenia w E3, nie deklaracja dowodu pod F1–F3.

## Ścieżki świadkowie (DoD 7)

Narzędzie wygeneruje je w E3 jako konkretne ciągi kroków na `test_instance`. Użytkownik sprawdza, czy tak ma wyglądać praca. Poniżej opis zamiaru; WIT5 ma dodatkowo ręcznie rozpisany przebieg do przeglądu E1.

| ID | Scenariusz | Musi pokazać |
|---|---|---|
| WIT1 | Przebieg bez przeszkód | p1 → r1, r2 → a1, a2, d1 → c1 → wydanie `accepted`; każde zatwierdzenie i linia bazowa jako krok U |
| WIT2 | Odrzucenie i eskalacja | r1 odrzucone 2 razy; przy trzeciej propozycji U musi zatwierdzić, wycofać albo odłożyć |
| WIT3 | Zmiana w trakcie pracy | wydanie reviewed; zgoda i T07(r1); a1/d1/c1 suspect; wydanie in_preparation; T00–T04 tworzą r3 z predecessor=r1, U włącza r3 przez W07; zmiana a1/d1 do draft i T14(r1→r3); ponowne weryfikacje, T11(c1) po naprawie zależnych, W01/W02/W04 tego samego wydania |
| WIT4 | Odpowiedź niejednoznaczna | pytanie `asked`, odpowiedź niejednoznaczna, pytanie wraca do kolejki jako najstarsze i jest zadane ponownie przed nowszymi |
| WIT5 | Zmiana po odbiorze | wydanie 1 `accepted`; U udziela zgody na a2 v1 / T05 i wykonuje T05; znacznik wymusza W06 wykonywane przez A; wydanie 2 przechodzi weryfikację, przegląd R i odbiór U; wydanie 1 pozostaje identyczne |

### WIT5 — przebieg do przeglądu E1

1. WIT1 kończy się W04 dla wydania 1: zakres to siedem ID z `test_instance.release_scope`, a wszystkie elementy zakresu są `baselined`; migawka zawiera a2 w wersji 1.
2. P00 → P01 → P02: użytkownik udziela zgody approved na T05 dla a2 w wersji 1; pytanie ma kind=change i blocking=true. T05 wskazuje to pytanie, sprawdza authorized_change i atomowo oznacza consumed=true (S11). T05 na a2 ustawia `draft`, wersję 2 oraz `next_release_required = true`. Rekord wydania 1 nadal ma stan `accepted` i niezmienioną migawkę a2 w wersji 1; `done = false`.
3. Następnym krokiem jest W06 (A): powstaje rekord wydania 2 z kopią zakresu, stanem `in_preparation`, bez migawki i protokołu; znacznik zostaje skasowany. T05 nie zmieniło r2, od którego zależy a2; r2 nadal jest `baselined`.
4. T01(a2), T02(a2), T04(a2): a2 w wersji 2 zostaje zweryfikowane, zatwierdzone i włączone do linii bazowej. Przy przechodzących testach W01 → W02(R) → W04(U) kończą wydanie 2.
5. Oba rekordy mają `accepted`, lecz osobne migawki: a2 w wersji 1 i a2 w wersji 2. `current_release = 2`, `done = true`. Przebieg mieści się w limitach: 2 wydania, 2 wersje a2 i 1 pytanie o zmianę.

Przypadek uzupełniający dla W06: zmiana elementu spoza zakresu, która ustawia `suspect` na elemencie zakresu, również ustawia znacznik przez `detect_post_acceptance_change`. Samo istnienie starszego `accepted` nie otwiera kolejnych wydań bez nowego zdarzenia.

Przypadek wznowienia (DEC-PRO-004): a2 jest `deferred` podczas W01. Jeśli U wykona T10 przy wydaniu `ready` lub `reviewed`, a2 wraca do `draft`, a wydanie do `in_preparation` (S7a). Jeśli najpierw nastąpi W04, późniejsze T10 ustawia znacznik i wymusza W06; migawka wydania 1 nadal zawiera a2 jako `deferred` (S7b, S10). Usunięcie `invalidate_release` z T10 jest dodatkowym mutantem S7a.

## Znane ograniczenia modelu

- Model nie widzi działań poza nim (ręczna edycja pliku). Pokrywa to odtwarzanie historii w E4 i kontrola repozytorium w E5.
- Treść elementów jest abstrakcyjna: `checks_ok` i `tests_ok` są założone, nie modelowane.
- Granice instancji: 8 ID (początkowo 7 w zakresie), 3 pytania, 3 wersje, 2 wydania. Dwa wydania pozwalają sprawdzić oddzielenie migawki odbioru od dalszych zmian i WIT5. Nie jest to dowód dla dowolnej liczby wydań; uzasadnienie granic zostanie zapisane razem z wynikiem w E3.
- `max_releases` ogranicza badanie, nie proces. Przekroczenie granicy należy raportować jako wyjście poza badany zakres; nie wolno wyłączać W06 i przedstawiać sztucznego zakleszczenia jako błędu procesu ani ignorować niespełnionej żywotności na granicy.

## WIT3 — przyjęty przebieg v0.6

DEC-PRO-009: plan 54 kroków opisuje `model/proposals/wit3-replacement.md` §4. Siedem produktów jest gotowych przed zmianą, rezerwowe r3 ma none poza zakresem. Po T07 stare r1 pozostaje superseded; po W07 zakres obejmuje 8 ID. a1/d1 przechodzą do wersji 2 i wskazują r3 v1; c1 może pozostać w wersji 1 po udokumentowanym przeglądzie, dopiero gdy jego zależności są dojrzałe bez suspect. p1/r2/a2 pozostają identyczne. To założenie scenariusza dotyczące braku wpływu na kod, nie automatyczna ocena treści. Pełny świadek i jego przegląd w ramach DoD 7 pozostają w E3.

ZADANIA (te same osie oceny co w pierwszym wywiadzie, epizody z Twojej sesji):
1. Odtwórz cel w 2 zdaniach, najmocniejszy argument ZA i PRZECIW, zakotwiczone w epizodach. Nie oceniaj kodu, którego nie otrzymałeś.
2. Trzy ćwiczenia mapowania: (a) „Nie chce menu tylko kopiowanie do schowka. D1 tak D2 nie” i późniejsza stała instrukcja commitowania przyrostów; (b) przyjęte H48, implementacyjne odstępstwo tooltip→szczegóły, późniejsza DEC122; (c) wykryte brakujące AT-061–063, commit fa90b77, dalsza implementacja. Dla każdego co model odróżnia, dane wejściowe/bramki, co poza modelem. Nie utożsamiaj commit z odbiorem ani ID wymagania z wersją elementu; nie udawaj wykonanego replay. S11 nie obejmuje każdej edycji dowolnego pliku.
3. Do 3 luk/narzutów: błąd reguły, brak adaptera/wiarygodnych wejść, komunikacja. Czy incydent checkout-index z pustym katalogiem docelowym jest błędem abstrakcyjnej reguły, wykonawcy czy obu? Co uzasadnia MAX_REJECTIONS=2? Odróżnij kontrprzykład od obawy.
4. Mała zmiana vs zmiana znaczenia: gdzie wystarczy decyzja agenta, gdzie operator. Nie proponuj obchodzenia przyjętej zgody.
5. Jakie 3 informacje w raporcie pomogą użytkownikowi i jak zmierzyć wartość ponad same dokumenty/test powiązań?
Do około 1200 słów. Opinie oznacz jako opinie, bez pozorowanej przyczynowości i bez pochwał na zamówienie.


## Odpowiedź Claude

# Runda 3: recenzja iso-model-state

## Najpierw korekty mojej poprzedniej odpowiedzi

**DoD.**
- Wycofuję wniosek, że DoD v1 był w całości spełniony, a projekt formalnie zamknięty.
- [O] Znam tylko wpis „Tydzień próbny (DoD) zakończony, DEC-VCS-096”. Dotyczy on jednego punktu DoD.
- [B] Nie wiem, czy pozostałe punkty DoD były spełnione.

**Punkt wznowienia.**
- Wycofuję nazwanie go rytuałem. Brak odczytu w tej samej sesji tego nie dowodzi, bo służy następnej sesji.

**Znacznik `@confirmed`.**
- Wycofuję twierdzenie, że zmieniła się jego definicja.
- [I] Ustalone jest tylko tyle, że zmieniłem chwilę nadawania znacznika: razem z testem, a nie razem z potwierdzeniem potrzeby.
- [H] Grozi to rozjechaniem znaczenia. Sprzeczności nie wykazałem.

## 1. Cel, argument za i przeciw

**Cel w dwóch zdaniach.** Lekki, sprawdzalny sposób pracy jednego operatora z agentem i niezależnym recenzentem. Ma pilnować, że zmiany zatwierdzonych produktów mają konkretną zgodę, że wpływ zmian jest widoczny, a odbiór dotyczy niezmiennej migawki, i ma to robić przy małym koszcie utrzymania.

**Najmocniejszy argument ZA.**
- [O] W mojej sesji powtarzał się jeden wzorzec: zatwierdzony zapis zmieniał się później niejawnie albo zostawał nieaktualny.
  - H-48 przyjęte, potem odstępstwo w kodzie, potem DEC-VCS-122. REQ-VCS-037 nadal cytuje H-48.
  - REQ-VCS-035 zmieniło znaczenie pod tym samym ID.
- [O] Mój program śledzenia sprawdza tylko powiązania ID, więc niczego tu nie wykrył.
- [I] Właśnie to model rozróżnia: wersję elementu i zgodę na konkretną operację na tej wersji (S11). Do tego dochodzi oznaczanie zależnych jako `suspect` (S5).

**Najmocniejszy argument PRZECIW.**
- [O] Model nie interpretuje języka naturalnego, a wejścia (`tests_ok`, zdarzenia, zgody) dostarcza otoczenie.
- [O] W mojej sesji najtrudniejsze były właśnie te mapowania:
  - jedno „d1 tak” na 49 reguł;
  - „D1 tak” zinterpretowane przeze mnie po usunięciu menu.
- [I] Jeśli adapter zmapuje to źle, model formalnie potwierdzi zły przebieg.
- [O] Wiarygodność wejść jest poza dowodem.

## 2. Mapowanie trzech epizodów (bez wykonanego replay)

### (a) „Nie chce menu tylko kopiowanie do schowka. D1 tak D2 nie” oraz stała instrukcja commitowania

**Pierwsza wypowiedź to trzy zdarzenia w jednej:**
- odrzucenie mojej propozycji menu;
- odpowiedź na D1, którą trzeba było zinterpretować;
- odpowiedź „nie” na D2.

**Co model odróżnia.**
- REQ-VCS-035 wtedy jeszcze nie istniało. To pytanie ogólne przed utworzeniem REQ, a nie T05 na zatwierdzonym elemencie.
- Część „D1 tak” jest odpowiedzią na pytanie o już nieistniejący wariant.
- [I] Prawidłowo: osobne pytanie o nową interpretację, a nie domniemana zgoda. W sesji tak się stało w praktyce: zadałem D1 ponownie i dostałem „d1 tak”.

**Co jest poza modelem.**
- Rozbicie jednego zdania na zdarzenia. To robota adaptera.

**Instrukcja „rob commity po kazdym logicznym przyroscie”.**
- [O] To zmiana zasad pracy, a nie zmiana produktu REQ/DES/CODE.
- [I] Pasuje najwyżej do PLAN, czyli zasady procesu zatwierdzanej przez U. Tu U sam ją wydał.
- [O] Commit nie jest odbiorem (W04) ani linią bazową.
- [O] Model nie widzi commitów, chyba że adapter mapuje je na wersje CODE.

### (b) Przyjęte H-48, odstępstwo w kodzie, potem DEC-VCS-122

**Co by było w modelu.**
- H-48 to część zatwierdzonego REQ w pewnej wersji.
- Odstępstwo to CODE niezgodny z REQ.
- [O] Model tego nie wykryje, bo zgodność kodu z wymaganiem jest wejściem zewnętrznym.

**Prawidłowa ścieżka według modelu:**
1. Pytanie typu `change` o T05 na tym REQ w tej wersji.
2. Zgoda U.
3. T05 atomowo zużywa zgodę i daje nową wersję.
4. Zależni DES, TEST i CODE dostają `suspect`.
5. Przegląd i T11.

**Co faktycznie było.**
- [O] Kolejność była odwrotna: najpierw kod, potem D1, potem DEC-VCS-122.
- [O] DEC-VCS-122 nie zmieniło treści REQ-VCS-037.
- [I] Model pokazałby ten epizod tylko wtedy, gdyby adapter zarejestrował zmianę dokumentu wymagań. Ręczna edycja jest poza nim, co przyznaje „Znane ograniczenia”.

**Uwaga.**
- [O] Zgoda nie zatwierdza automatycznie treści poprawki.
- [I] U zatwierdzał tu fakt dokonany, a model tego nie zabrania.

### (c) Brakujące testy AT-VCS-061–063, commit `fa90b77`, dalsza praca

**Co model widzi.**
- Czerwona kontrola to `checks_ok = false`.
- [I] Wynika z właściwego braku nowych testów, a nie z dowodu złego testu.
- [O] W01 wymaga `tests_ok`, więc wydanie nie przeszłoby do `ready`. Pośredni commit niczego tu nie łamie.

**Możliwe ryzyko mapowania.**
- [O] TEST wymaga zatwierdzenia U.
- [O] Scenariusze AT-VCS-061–063 napisałem ja i oznaczyłem `@confirmed` na podstawie DEC-VCS-124. Ta decyzja przyjmowała funkcję, a nie tekst scenariuszy.
- [H] Jeśli adapter potraktuje `@confirmed` jako T02 na TEST, wyjdzie przejście U wykonane przez A, czyli naruszenie S1.
- [H] Jeśli potraktuje je jako szkic, model wymagałby osobnej zgody U na te testy.
- [B] Nie wiem, które mapowanie przyjmujecie.

## 3. Luki i narzuty

**Luka: wiarygodne wejścia i granulacja.**
- [O] S9 (jedno pytanie `asked` naraz) koliduje z obowiązującą w vcs-lite konwencją D1–D3 w jednej wiadomości.
- [O] Użytkownik w tej sesji wielokrotnie odpowiadał na trzy decyzje naraz („d1 tak, d2 tak, d3 tak”) bez widocznej szkody.
- [I] To nie kontrprzykład dla S9, tylko wymóg dla adaptera: albo pakiet pytań jako sekwencja, albo zmiana konwencji. Jest też obawa o narzut.

**Luka: zakres zgód.**
- [O] S11 obejmuje T05 i T07 na produktach.
- [O] Działania na zewnątrz są poza modelem: push, otwarcie pliku w aplikacji użytkownika, odczyty jego prawdziwych repo.
- [I] Te miały w sesji własne zasady: push tylko po „d1 tak”, zakaz zrzutów ekranu.

**Incydent `checkout-index` z pustym katalogiem docelowym.**
- [I] Przede wszystkim błąd wykonawcy:
  - zsh nie podzieliło listy plików;
  - łańcuch z `;` wykonał dalsze kroki po nieudanym `git add`;
  - nie sprawdziłem wyniku.
- [I] Częściowo luka reguły: „testuj indeks przed commitem” wymaga procedury powłoki, a reguła nie wskazuje bezpiecznego narzędzia.
- [O] Model abstrakcyjny tego w ogóle nie widzi. To nie błąd jego reguły, tylko granica zakresu.

**MAX_REJECTIONS=2.**
- [O] W widocznej części sesji nie ma przypadku dwóch odrzuceń tej samej wersji.
  - Menu odrzucono raz.
  - Wygląd grafu poprawiałem po akceptacji, czyli była to zmiana, a nie odrzucenie.
- [I] Nie mam więc kontrprzykładu. Jest tylko obawa, że dwa to mało przy wyglądzie UI, gdzie iteruje się na zrzutach.
- [B] Nie wiem, co uzasadnia tę wartość poza ograniczeniem żywotności (L4).

**Komunikacja.**
- [O] Odwołanie do „kroków 18 i 19” bez ich treści.
- [I] Raport oparty na ID grozi tym samym.

## 4. Mała zmiana a zmiana znaczenia

**Wystarcza decyzja agenta (opinia):**
- refaktoryzacja bez zmiany zachowania, np. wydzielenie `PageOpener`;
- szczegół w granicach zatwierdzonej treści DES/CODE, np. kolor toru 4–8 przy wzorcu pokazującym trzy.
- Warunek: zapis „decyzja agenta”, możliwość podważenia przez U (T06) i udokumentowany przegląd braku wpływu (T11).

**Potrzebny operator:**
- zmiana tego, co mówi zatwierdzony REQ lub TEST: zamiana na `https`, H-48, `@confirmed`;
- zmiana zakresu wydania, np. historia przeniesiona z v2 do v1;
- działanie zewnętrzne.

**Strefa szara (opinia).**
- Przykład: sygnał dźwiękowy przy braku zdalnego repo. To uzupełnienie luki w zatwierdzonym REQ.
- Nie obchodzi zgody, jeśli wejdzie jako jawna propozycja do tej wersji REQ, zatwierdzana razem z nim.

## 5. Raport: trzy informacje i pomiar wartości

**Trzy informacje (opinia):**
1. Zatwierdzone lub bazowe elementy zmienione od ostatniego odbioru, z informacją, czy każda zmiana ma zużytą, właściwą zgodę. Przykład: „REQ-VCS-037 v1 cytuje H-48 zmienione przez DEC-VCS-122, brak T05”.
2. Lista zależnych elementów `suspect` z jednym następnym działaniem dla każdego: przegląd, decyzja albo test.
3. Ostatnio odebrana migawka wobec stanu obecnego oraz otwarte pytania blokujące. Opisane treścią, nie samymi ID.

**Jak zmierzyć wartość ponad dokumenty i test powiązań:**
- W E4 przygotować z góry listę znanych epizodów vcs-lite:
  - H-48 i REQ-VCS-037;
  - REQ-VCS-035 pod tym samym ID;
  - `fa90b77`;
  - DEC-VCS-096;
  - Beyond Compare po DEC-VCS-102.
- Policzyć: ile z nich wykrywa raport, a ile istniejący `test_traceability.py`; ile jest fałszywych alarmów; czas operatora na każdą decyzję.
- Osobno: czy świeży agent z samego raportu poprawnie wskazuje zakres, otwarte sprawy i następny krok, w porównaniu z samymi dokumentami.
