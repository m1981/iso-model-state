# Propozycja powiązania zgody ze zmianą produktu

Status: **applied**, DEC-PRO-008, 2026-10-25, cytat „D1 tak.”; zastosowanie w modelu v0.5. Poniżej zachowano treść propozycji z 2026-10-24 jako uzasadnienie. Źródłem obowiązujących reguł jest model/process.yaml. DEC-PRO-007 dotyczy wyłącznie celu użytkowego.

## Korzyść i rekomendacja

Operator ma wiedzieć, na co wyraził zgodę, a program ma uniemożliwić wykorzystanie tej odpowiedzi do innego działania. Rekomendacja: **pozytywna zgoda dotycząca zmiany wskazuje element, jego wersję i operację; można ją wykorzystać w jednym skutecznie wykonanym kroku**.

Przykład pytania: „Otworzyć zmianę a2 w wersji 1 przez T05?”. Odpowiedź „tak” pozwala wykonać tę operację raz. Odpowiedź „nie” rozstrzyga pytanie, ale nie otwiera zmiany. Zmiana r1, zastąpienie a2 przez T07 albo ponowne wykorzystanie tej zgody są odrębnymi działaniami.

## Luka w obecnym modelu

- T12 używa kind/about, których nie ma w question_variables.
- Warunek resolved_question(e) w T05/T07 sprawdza jedynie istnienie rozstrzygniętego pytania dotyczącego elementu. P02 nie zapisuje rozróżnienia między zgodą a odmową. Jednoznaczna odpowiedź nie musi być zgodą.
- Nie ma powiązania z wersją, rodzajem operacji ani znacznika wykorzystania zgody. Bez doprecyzowania stary zapis może zostać potraktowany jako uprawnienie do kolejnej czynności.

## Proponowane dane i reguły

Dotychczasowe state, blocking i age pozostają. Do question_variables dochodzą:

| Pole | Wartości i znaczenie |
|---|---|
| kind | general albo change; domyślnie general dla dotychczasowych pytań WIT4 |
| about | ID istniejącego elementu dla change; none dla general |
| about_version | Wersja elementu zapisana podczas zgłoszenia change; none dla general |
| requested_transition | T05 lub T07 dla change; none dla general |
| resolution | none przed odpowiedzią; approved albo rejected dla change; answered dla rozstrzygniętego general |
| consumed | Początkowo false; true po skutecznym użyciu zgody przez T05 lub T07 |

**P00:** dla change wymagane są about, requested_transition i blocking=true; wskazany element musi istnieć (state różne od none). Wersję pobiera model z elementu podczas zgłoszenia. Dla general nie przyjmujemy powiązania z produktem ani operacji. Zapis celu i wersji nie zmienia się podczas P01–P05. age i blocking zachowują dotychczasową semantykę.

**T12:** tworzy pytanie change dotyczące e, z about_version równym bieżącej wersji e, requested_transition=T05, blocking=true, resolution=none i consumed=false. Zgłoszenie zastąpienia przez T07 odbywa się przez P00 z jawnym rodzajem operacji. T12 nie przyznaje zgody.

**P02:** nadal wymaga U, stanu asked i jednoznacznej odpowiedzi. Dla change wymagany jest jawny wynik approved lub rejected, zapisany razem z cytatem. Dla general wynik to answered. Stan pytania staje się resolved w każdym z tych trzech przypadków. Rekord DEC zawiera również powiązanie z elementem, wersją, operacją i wynikiem rozstrzygnięcia, jeśli pytanie dotyczy zmiany.

**P03:** pozostawia resolution=none i consumed=false, wraca do open, bez DEC i zmiany age. P04/P05 nie zmieniają powiązania, wersji ani wyniku. Pytania change są blokujące, więc nie można ich odłożyć przez P04; można je rozstrzygnąć odmową przez P02.

**T05 i T07:** zdarzenie wskazuje konkretne pytanie q. Warunek resolved_question(e) zastępuje authorized_change(q,e), oceniany w stanie przed krokiem:

```text
q.state = resolved
and q.kind = change
and q.resolution = approved
and q.about = e.id
and q.about_version = e.version
and q.requested_transition = transition.id
and not q.consumed
```

Skutek q.consumed := true jest atomowy z dotychczasowymi skutkami T05/T07. Przy odmowie wykonania, błędzie lub przekroczeniu granicy badania zgoda pozostaje niewykorzystana. resolved, resolution i cytat DEC pozostają w historii; wykorzystanie zgody nie zmienia wcześniejszego rozstrzygnięcia.

Pola powiązania przygotowuje agent przy pytaniu; operator widzi cel i proponowaną operację. Wykonanie wcześniej zatwierdzonego działania nie wymaga ponownego pytania o tę samą zgodę. Aktorem T05/T07 w modelu pozostaje U; P02 nie uruchamia tych przejść automatycznie.

## Zakres zmiany i sprawdzenia po przyjęciu

Zmiana obejmie question_variables, opis inicjalizacji pytań, notation, P00/P02/T12/T05/T07, interpretację INT-008, opis WIT5 oraz definicje właściwości i mutantów. Jawna sekcja question_semantics opisze niezmienność powiązania, wyniki rozstrzygnięcia i zużycie zgody; słownik loadera zostanie odpowiednio rozszerzony. WIT4 zachowa dotychczasowy przebieg jako pytania general.

Proponowana nowa właściwość S11: każdy krok T05/T07 ma w stanie przed krokiem zgodę spełniającą authorized_change, a w stanie po kroku wskazane pytanie ma consumed=true. Niezmienność powiązania przy P01–P05 zostanie sprawdzona osobno. Mutanty usuwają kolejno: wymóg approved, zgodność elementu, wersji i operacji, zapis consumed=true.

| Przypadek kontrolny | Oczekiwany wynik |
|---|---|
| approved dla a2 v1 i T05; U wykonuje T05 na a2 v1 | Krok dozwolony, a2 v2 draft, zgoda wykorzystana |
| Pytanie general, nierozstrzygnięte, odmowa albo odpowiedź niejednoznaczna | Brak uprawnienia do T05/T07 |
| Zgoda na a2 użyta dla r1 | Odmowa bez zmiany stanu |
| Zgoda na a2 v1 użyta po zmianie a2 do v2 | Odmowa; potrzebne nowe rozstrzygnięcie |
| Zgoda na T05 użyta do T07 | Odmowa |
| Ta sama zgoda użyta po raz drugi | Odmowa, także gdy sama wersja nie pozwala wykryć ponownego użycia |
| Błąd po rozpoczęciu wykonania skutków | Bez częściowej zmiany produktu ani zużycia zgody |

Po przyjęciu: aktualizacja modelu i dokumentów zależnych w jednej edycji, czerwone testy powyższych warunków, implementacja i regresja WIT1/WIT2/WIT4. Następnie WIT5: odbiór wydania 1 → zgoda na zmianę a2 v1 → T05 → W06 → odbiór wydania 2, z identycznym rekordem wcześniejszego odbioru. Znane kwestie pustego zakresu W01 i zastępowania zależności w WIT3 pozostają poza tą propozycją.

## Granice i alternatywa

To kontrola zgody na operację w modelu stanów, nie podpis treści dowolnej poprawki kodu. Model nadal abstrahuje treść produktów. T06, T08–T10 zachowują własne bramki U; nie dokładamy im obowiązkowego pytania o zmianę. Pytanie rozstrzygnięte odmową nie blokuje samo w sobie wydania, zgodnie z obecną regułą W01. Rozstrzygnięcia pytań nie zmieniają historycznych odbiorów.

Alternatywa minimalna: dodać wyłącznie kind/about. Usuwa lukę słownika, ale pozostawia ryzyko użycia odmowy lub starego rozstrzygnięcia jako zgody; nie rekomenduję jej do WIT5.

Przejrzane zależności propozycji: model/process.yaml (notation, question_variables, P00–P05, T05–T12, W01–W06), docs/WLASCIWOSCI.md (G0, S1, S7a/b, S9, S10, L1/L2/L4/L5, WIT2/WIT4/WIT5), docs/INTERPRETACJE.md (INT-004/008/010/017), PLAN.md, docs/KARTA-CELU-I-ZAKRESU.md, src/isomodel/loader.py, execution.py, expressions.py, reporting.py, probes.py, scripts/check_model.py i scenariusze WIT1/WIT2/WIT4. To lista wpływu do wdrożenia po osobnej decyzji, nie deklaracja ukończenia zmiany.
