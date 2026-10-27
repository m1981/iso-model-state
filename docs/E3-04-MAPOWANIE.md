# E3.4 — przygotowanie badania wpływu zmiany

2026-10-27. Polecenie U: „wykonaj Dalej zgodnie ze sztuka”, w odpowiedzi na przygotowanie zakresu scenariusza i oczekiwanych wyników **przed rozszerzeniem generatora**. Podstawa: E3.3 w `3195a84`, model v0.7, DEC-PRO-008/009/010. Status: specyfikacja badania i sprawdzenie przygotowania w E2; wynik niezależnego przeglądu w [recenzji](reviews/E3-04-PRZYGOTOWANIE-2026-10-27.md). Nie wykonano TLC E3.4 ani odbioru E3. Nie zmieniamy modelu, interpretacji, właściwości ani kolejności E3–E5.

## 1. Rezultat dla operatora

Po zatwierdzonej zmianie wymagania operator otrzymuje kompletną listę zależnych produktów do przeglądu, a agent może uporządkować tę listę legalną ścieżką. Samo „pytanie rozstrzygnięte” nie wystarcza do zmiany. Stara zgoda nie uprawnia do dowolnej następnej operacji. Przegląd bez wpływu wymaga dojrzałych i przejrzanych zależności.

Przykład objaśniający: aplikacja do zadań już pozwala oznaczać wykonanie. Operator proponuje także cofanie oznaczenia. r1 to wymaganie, a1 to scenariusz akceptacyjny, d1 to projekt, c1 to kod. Przyjmujemy dla przykładu, że projekt i kod już umożliwiają oba kierunki zmiany statusu, ale wymaganie i test akceptacyjny wymagają uzupełnienia. To jawne założenie oceny treści, którego automat nie dowodzi.

Oczekiwany wynik: r1 i a1 mają wersję 2 oraz nową linię bazową; d1 i c1 zachowują wersję 1 po T11; żaden produkt nie ma suspect. p1, r2, a2 i rezerwowe r3 zachowują całe rekordy. Nie otrzymujemy w tym przyroście działającej aplikacji ani oceny prawdziwości jej testów.

## 2. Zakres i reprezentacja stanu

| Warstwa | Ustalony zakres |
|---|---|
| Katalog | Pełne osiem rekordów z test_instance; stałe ID, typy, depends_on i predecessor. Akcje produktów wybieramy na r1, d1, a1, c1. p1/r2/a2/r3 pozostają w ramie, również przy sprawdzaniu propagacji. |
| Główne nowe przejścia | T05 otwarcie zmiany, T11 przegląd bez wpływu, T12 zgłoszenie zmiany, T13 naprawa szkicu. Powrót do dojrzałości przez T01/T02/T04. |
| Pytania w wycinku | P01 i P02 dla pytań change; q0 istnieje na wejściu, q1/q2 mogą powstać przez T12. Uwzględniamy approved i rejected oraz unambiguous_answer=true/false. P00 służy do jawnego prefiksu przygotowania q0, nie jest akcją eksplorowanego wycinka. |
| Globalny stan | items, questions, releases, current_release, next_release_required w całości. Nie wolno odtwarzać pytań z początkowej migawki po każdym kroku, jakby zużycie zgody było zewnętrznym wejściem. |
| Wynik kroku | Pełny następnik oraz records. P02 wytwarza demonstracyjny DEC z wynikiem i powiązaniem; jest to wyjście kroku, nie dodatkowy trwały rejestr w modelu. T11 wymaga evidence, lecz obecny E2 nie wytwarza osobnego records dla tego wpisu. |
| Wydanie | Główny graf: jedno wydanie in_preparation. Osobne próby jednego kroku obejmują ready/reviewed/accepted oraz zmianę spoza zakresu. W06 i ponowny odbiór pozostają poza E3.4. |

Zależni r1 to dokładnie **{d1,a1,c1}**; c1 jest pośredni i osiągalny dwiema drogami. Zależni a1 to {c1}. Żaden z p1/r2/a2/r3 nie należy do tych zbiorów. Generator wylicza domknięcie z danych grafu, a wyrocznia ma niezależnie zapisane oczekiwania. Stała topologia pozwala specjalizować domknięcie, lecz nie na podstawie produkcyjnego `_dependents`. Próba kontrolna zmienionego grafu musi wykazać, że domknięcie nie jest zaszyte po ID.

### Granice

- Modelowe max_questions=3, max_version=3, max_releases=2 pozostają bez zmian; w głównym wycinku nie powstaje nowe wydanie. q0/q1/q2 są identyfikatorami instancji, nie dodatkowymi regułami procesu.
- Głębokość głównego grafu: **16 wykonanych kroków od punktu wejścia**. Obejmuje świadka 13 kroków. Nie twierdzimy, że obejmuje każdą ścieżkę zamknięcia wszystkich możliwych pytań.
- Ograniczenie głębokości, wyczerpanie puli pytań lub przekroczenie wersji to **granica badania**, nie odmowa biznesowa i nie zakleszczenie. Raport pokazuje liczbę i rodzaj odcięć. Następnik musi być oceniony przed odcięciem; ograniczenie nie może ukryć naruszenia mutanta. Osobna próba graniczna sprawdzi czwarty wniosek i wersję ponad limit.
- Nie ograniczamy komend wyrocznią ani tylko do działań oczekiwanych na ścieżce. W każdym odwiedzonym stanie badamy wszystkie reprezentowane wybory właściwe dla kontraktu danej operacji. Nie narzucamy „najwyżej jednego T12 na produkt”, bo takiej reguły nie ma w modelu.
- Zachowujemy CHECK_DEADLOCK FALSE wyłącznie dla wycinka. Brak dowodu L1/L3/L5, F, pełnego WIT3, zastępowania T07/T14/W07 i wszystkich skutków T06–T10.

## 3. Punkt wejścia i jego pochodzenie

Prefiks od rzeczywistego Init tworzy i bazuje siedem produktów w kolejności p1,r1,r2,d1,a1,a2,c1. Dla PLAN/REQ/AT: T00,T01,T02,T04; dla DES/CODE: T00,T01,T04. To **26 kroków**. Dowody i checks są demonstracyjne, z simulation=true.

Następnie P00 zgłasza q0: change/about=r1/requested_transition=T05/blocking=true, P01 je zadaje, P02 zatwierdza z cytatem demonstracyjnym. To kolejne **3 kroki**. Punkt wejścia ma siedem baselined/v1/rejections=0/suspect=false, r3=none/v0; q0 resolved/approved/about_version=1/consumed=false/age=1. Wydanie 1 pozostaje in_preparation, bez migawki i protokołu, pending=false.

Autor wyroczni ma zapisać pełne oczekiwanie punktu wejścia niezależnie od execute_step. Wykonanie prefiksu E2 potwierdza spójność tej drogi z interpreterem. Główny graf TLC zaczyna się dopiero w tym punkcie: **nie nazywamy go pełnym dowodem TLC od Init procesu**. Prefiks, jego DEC i hashe należy zachować jako osobny dowód przygotowania.

## 4. Ręczny świadek zmiany — oczekiwania przed kodem

W tabeli „baza” oznacza baselined. Wersja zmienia się tylko przez T05. Wszystkie niewymienione pola i rekordy pozostają bez zmian.

| Krok wycinka | Zdarzenie | Oczekiwana zmiana |
|---:|---|---|
| 0 | punkt wejścia po prefiksie | r1/d1/a1/c1 baza v1; q0 approved, niezużyte |
| 1 | U: T05(r1,q0) | r1=draft v2, rejections=0, suspect=false; q0.consumed=true; dokładnie d1/a1/c1 suspect=true |
| 2 | A: T01(r1), checks=true | r1=verified v2 |
| 3 | U: T02(r1), dowód | r1=approved v2 |
| 4 | U: T04(r1), dowód | r1=baza v2 |
| 5 | A: T11(d1), dowód przeglądu | tylko d1.suspect=false; d1 nadal baza v1, c1 nadal suspect |
| 6 | A: T12(a1,q1) | a1 bez zmiany; nowy q1 open/change/about=a1/about_version=1/requested_transition=T05/blocking=true/resolution=none/consumed=false/age=2 |
| 7 | A: P01(q1) | q1=asked; powiązanie zachowane |
| 8 | U: P02(q1), approved, jednoznacznie, dowód | q1=resolved/approved; dokładnie jeden DEC z powiązaniem a1 v1/T05; consumed nadal false |
| 9 | U: T05(a1,q1) | a1=draft v2/rejections=0/suspect=false; q1.consumed=true; c1 pozostaje suspect |
| 10 | A: T01(a1), checks=true | a1=verified v2 |
| 11 | U: T02(a1), dowód | a1=approved v2 |
| 12 | U: T04(a1), dowód | a1=baza v2 |
| 13 | A: T11(c1), dowód przeglądu | tylko c1.suspect=false; c1 nadal baza v1 |

13 kroków wycinka, **42 kroki razem z prefiksem**. To przygotowany świadek E3.4, nie nowa definicja WIT ani zmiana zaakceptowanych świadków. Końcowy stan nie jest odbiorem wydania.

### Odmowy w naturalnych punktach tej ścieżki

- Po 1: T11(d1) nie może usunąć flagi, bo r1 jest draft. T13(a1) nie może zmienić baselined w szkic.
- Po 4: ponowne T05(r1,q0) ma być odmówione; r1 jest znowu w stanie dopuszczającym T05, lecz zgoda dotyczy starej wersji i jest zużyta. Odmowa bez zmiany jakiegokolwiek pola.
- Po 5: T11(c1) nadal odmówione, mimo że d1 jest dojrzałe i przejrzane — a1 pozostaje suspect.
- Po 9: T01(c1) nie daje obejścia przeglądu; osobny kontekst c1=draft/suspect=true izoluje właśnie bramkę suspect, bez maskowania przez from.
- Po 12: T11(c1) bez dowodu odmówione; z dowodem dozwolone. Sama obecność poprawnie uformowanego dowodu nie dowodzi prawdziwości oceny „bez wpływu”.

Odmowy nie zwiększają licznika wykonanych kroków i nie zużywają zgody.

## 5. Przypadki uzupełniające i izolacja warunków

| ID | Próba | Oczekiwanie |
|---|---|---|
| A01 | Osobno zmienić jeden składnik poprawnej zgody q0: state=asked, kind=general, resolution=rejected, about=r2, about_version=2, requested_transition=T07, consumed=true | Każda próba T05(r1) odmówiona. Warianty izolacyjne są oznaczone jako wstrzyknięte stany; nie udajemy ich osiągalności. |
| A02 | Brak/nieznane ID pytania, niewłaściwy aktor A/R | Jawny błąd wejścia albo odmowa roli; pełny brak skutków. Nie utożsamiać błędu wejścia z guard=false. |
| A03 | P02(q1) z rejected; następnie próba T05(a1,q1) | DEC zapisuje odmowę; T05 odmówione. P02 z unambiguous_answer=false nie rozstrzyga pytania ani nie tworzy DEC. P03 pozostaje poza wycinkiem. |
| A04 | Izolacja consumed=true przy nadal pasującej wersji | Odmowa z powodu zużycia. Naturalny ponowny T05 ma też złą wersję i sam nie dowodzi czułości warunku consumed. |
| A05 | Dwa otwarte wnioski q1/q2 z różnym age | P01 wybiera starszy; drugi nie może być asked równocześnie. Nie jest to dowód pełnego FIFO/priorities lub L2; oba wnioski są blocking/change. |
| I01 | T05(r1), następnie T05(a1) | Domknięcie r1={d1,a1,c1}, a1={c1}; powtórne oznaczenie już podejrzanego c1 jest idempotentne. Reszta rekordów identyczna. |
| I02 | T11 przy zależności draft albo osobno dojrzałej, lecz suspect | Obie odmowy; osobny pozytywny przypadek i dowód wymagany. T11 nie zmienia stanu, wersji, licznika ani cudzych flag. |
| I03 | Wariant prefiksu zostawia c1 w draft v1; T05(r1), T13(c1) przez A | T13 czyści tylko flagę szkicu, bez nowej wersji i zgody. Przy d1/a1 nadal baselined T01(c1) jest **dozwolone**, choć mają suspect: T01 nie sprawdza flag zależności. Osobno T12(a1), P01/P02 approved i T05(a1) dają bezpośrednią zależność draft; wówczas po T13(c1) T01(c1) jest odmówione. Nie utożsamiamy T13 z bardziej rygorystycznym T11 i nie zmieniamy modelu. |
| I04 | T05 przy rejections=2 i suspect=true | Wersja +1, rejections=0, własne suspect=false; to nowy budżet wersji. Nie jest to pełny dowód S15. |
| R01 | T05 w zakresie przy ready i reviewed | Atomowo in_preparation. Pozostałe pola wydania zachowane. |
| R02 | T05 w zakresie przy accepted | Odebrany rekord identyczny bajtowo/strukturalnie; next_release_required=true. Następne T11 jest blokowane przez priorytet W06. Nie wykonujemy W06 w E3.4. |
| R03 | Osobna instancja bez r1 w scope, ale z d1/a1/c1; T05(r1), ready/reviewed/accepted | Obserwator reaguje na nowe suspect w zakresie, mimo że bezpośredni helper dla r1 nie działa. Te same rezultaty jak R01/R02. |
| R04 | Zmiana liścia a2 w zakresie oraz wariant zakresu bez a2 | Brak nowych zależnych: izoluje helper od obserwatora. W zakresie cofa ready/reviewed; poza zakresem i bez nowego suspect wydanie pozostaje identyczne. To osobna próba, a2 nie staje się aktywne w głównym grafie. |

R01–R04 mają pełne, jawne stany wejściowe. Warianty osiągalne przygotowujemy prefiksem E2 (P02 przed W01, następnie W02/W04 według potrzeby). Wstrzyknięte przypadki izolujące wyraźnie oznaczamy. Osobne próby R badają jeden krok i kontrolę priorytetu, nie cały cykl wydań. Ani helper, ani obserwator nie mogą maskować nieskuteczności testu drugiego mechanizmu.

## 6. Kontrakt translacji, wejść i wyroczni

1. From/to/actor/guard/effects/evidence czytamy z YAML. Rozwijamy authorized_change z question_semantics, a nie przepisujemy jedną stałą decyzję allow. Przemianowanie ID obejmie też odwołania requested_transition i change_operations; oczekiwanie odpowiada roli operacji, nie starej nazwie T05.
2. Akcja jest atomowa: konsumowanie zgody, nowa wersja, reset, propagacja, helper i obserwatory należą do jednego następstwa. nowo_suspect wyznacza różnica flag po skutkach przejścia względem pre. Pełne post_step_effects mają być odczytane; nie wolno milcząco ignorować ich zmian. Nieobsługiwana semantyka/helper/observer prowadzi do jawnej odmowy translacji także w nieaktywnej gałęzi.
3. Każdy krok porównujemy z niezależną relacją ExpectedEnabled/ExpectedStep oraz interpreterem Python. Oczekiwanie nie ogranicza Next. Porównujemy pełne stany i wyjścia records, a nie tylko suspect. Dopuszczalne są dwa niezależne algorytmy grafowe; żaden nie wylicza referencji przez kod kandydata.
4. Autor wyroczni nie implementuje generatora. Otrzymuje model, tę specyfikację i literalne oczekiwania scenariusza. Przygotuje niezależny pełny punkt wejścia, następstwa świadka, reguły referencyjne oraz odmowy. Wynik ręcznego sprawdzenia E2 w przygotowaniu nie staje się automatycznie wyrocznią.
5. Domeny komend są jawne per operacja: wszystkie A/R/U; wszystkie cztery aktywne produkty dla każdej operacji produktu; T05 wybiera istniejące q0/q1/q2; T12 każde dostępne nowe q1/q2; P01/P02 każde istniejące pytanie. T01 oba checks, T02/T04/T11 oba evidence, P02 oba resolution i unambiguous_answer oraz evidence. Kombinacje niedozwolone semantycznie pozostają próbami odmów. Dodatkowe i błędnie typowane pola oraz nieznane ID badamy osobno jako wejścia niepoprawne.
6. Dowód true to jawny demonstracyjny rekord, false brak pola. T02/P02 wymagają decision+quote, T04 reference+quote, T11 decision+reference. Walidujemy wymagane pola i nieznane pola zgodnie z E2; nie dopisujemy uwierzytelniania cytatu lub merytorycznej kontroli referencji. T05 korzysta z pytania, nie z nowego dowodu zastępującego q.
7. Monitory weryfikacji i zatwierdzenia muszą śledzić **(ID, version)** oraz faktyczną operację. Wpis T01/T02 wersji 1 nie spełnia obowiązku wersji 2. Historia początkowa wynika z jawnego prefiksu, nie ze zgadywania na podstawie samego stanu baselined.
8. Porównanie pełnych zbiorów stanów TLC i Pythona obejmuje globalny stan i monitory. Różnice reprezentacji (zbiory, None) muszą być zdefiniowane jawnie i nie usuwać istotnych pól. Raport osobno wykazuje dostępność, skutki, monitory, odcięcia granic i wykonane świadki mutantów.

## 7. Właściwości i plan czułości

Nowe kontrole mają charakter lokalny lub krokowy; nie deklarujemy zamknięcia całych S ani L. Planowane kontrole:

| Kontrola | Powiązanie | Celowy mutant / izolacja |
|---|---|---|
| zgoda i rola | S1/S11 | każdy z siedmiu składników authorized_change usunięty osobno; T05 aktora A; odpowiednie A01/A02/A04 |
| atomowe zużycie | S11 | pominięte q.consumed=true; kontrola post natychmiast po zmianie, niezależna od późniejszej złej wersji |
| wersja/reset | T05, część S15 | osobno brak version+1, brak resetu rejections, brak czyszczenia własnego suspect; I04 |
| pełny wpływ i rama | część S5 | brak propagacji, tylko bezpośredni zależni, oznaczenie całego katalogu; I01 plus rama r2/a2 |
| bezpieczny przegląd | S4, T11/INT-012 | pominięta dojrzałość zależności, pominięte not suspect, brak evidence; I02 oraz odmowa po 5 |
| wniosek o konkretną zmianę | T12/S11 | osobno błędne about, about_version, requested_transition lub brak nowego pytania; kontrola pełnego rekordu |
| granica szkicu | T13 | dopuszczenie baselined, nieuprawniony aktor, zmiana wersji przy czyszczeniu flagi; I03 |
| globalny wpływ | część S7a/S10 | brak helpera izolowany na liściu; brak odpowiedniego obserwatora izolowany zmianą spoza scope; nadpisanie accepted; R01–R04 |
| historia właściwej wersji | S2/S3 w wycinku | otwarcie v2 bez powrotu do draft i próba wykorzystania historii v1; oddzielny monitor, nie tylko ogólna równość następników |
| rozstrzygnięcie i powiązanie | P01/P02, część S9/S11 | P01 bez count(asked)=0; P02 z pominiętym warunkiem jednoznaczności lub złym resolution/DEC; A03/A05 |

Każdy mutant ma naruszyć nazwaną kontrolę i otrzymać wykonany świadek błędnego skutku; czułość monitorów badać też osobno. Jeżeli konstrukcja zmienionego modelu jest poza obsługiwaną semantyką, odmowa generatora jest testem granicy, **nie zabiciem mutanta**. Brak narzędzia, błąd składni, timeout i przekroczenie granicy nie są dowodami poprawności ani kontrprzykładami semantycznymi.

Kontrole danych: przemianowane ID operacji z naprawionymi referencjami; inna legalna krawędź (np. a1 wskazuje r2, oczekiwani zależni r1={d1,c1}); jawnie inna wersja wejściowa wraz z pasującą zgodą; osobna instancja zakresu R03. To kopie danych badań, bez edycji modelu v0.7.

## 8. Wykonanie i DoD

**Przygotowanie (bieżące polecenie):** kompletny ten dokument, sprawdzenie wykonalności świadka istniejącym E2 z zachowaniem prefiksu i wyniku, niezależny przegląd bez otwartych blokerów, aktualny punkt wznowienia. Brak nowych testów tylko dla dokumentacji i brak pozornego RED. Wykonanie świadka E2 nie zastępuje przyszłej wyroczni ani TLC.

W bieżącym przygotowaniu wykonano istniejącym E2 **42 kroki**, porównano **14 pełnych stanów i wyjść records** (punkt wejścia oraz 13 następników), potwierdzono **5 odmów bez mutacji** i oba warianty I03. Dane, polecenie oraz dowody: [pakiet przygotowania](preparations/e3-04/README.md). Pozostała macierz A/I/R i mutanty z §5/7 są planem przyszłego badania, nie deklaracją wykonania ich teraz przez autora.

Przegląd przygotowania ujawnił błędne oczekiwanie I03: T01 nie bada suspect zależności, a T13 nie ma warunków T11. Zapisano oba legalne rezultaty bez zmiany reguł. Pierwsze porównanie records w preflight wykryło też omyłkowe `kind=DEC` w ręcznym oczekiwaniu; skorygowano je do istniejącej reprezentacji `kind=decision`. To korekta oczekiwania i mapowania, nie nowa luka modelu ani deklaracja cyklu TDD generatora.

**Następne wykonanie E3.4:** osobny autor wyroczni → RED dla nowej translacji i granic → minimalna implementacja → GREEN → porządkowanie z regresją → graf i macierz prób TLC/Python → niezależne odtworzenie → dowody, raport, commit/push. Można implementować kolejno T05, T11/T13, T12/P01/P02 i globalne skutki; wszystkie należą do jednego opisanego przyrostu, a dostawa musi ujawnić części nieukończone.

DoD wykonania: wszystkie zadeklarowane przypadki i kontrole danych; pełny świadek i odmowy; czujne mutanty bez maskowania; zgodne stany i records; brak naruszeń w bazie; rozliczone granice; właściwa pełna regresja E2/E3.1–3; przypięte źródła i toolchain, surowe logi/dump; niezależny przegląd bez otwartych blokerów. Nowa luka zaakceptowanej reguły trafia do U przed zmianą. Odbiór całego E3 pozostaje osobną przyszłą decyzją.

Ryzyko kosztu: pełny katalog, pytania i przeploty zwiększą przestrzeń stanów. Nie deklarujemy liczby stanów ani czasu przed pomiarem. Najpierw mierzymy bazę na opisanej instancji; przekroczenie limitu TLC ma status nieukończony. Zmniejszenie zakresu dowodu wymaga jawnej korekty specyfikacji i recenzji, nie ukrytego przycięcia. Koszt obsługi rzeczywistego projektu i fałszywe alarmy zmierzymy dopiero w E4/E5.

## 9. Decyzje agenta i odpowiedzialności

- E3-DA15 (A, 2026-10-27): oddzielamy przygotowanie od wykonania generatora, bo bieżące „Dalej” dotyczyło dokładnego scenariusza i oczekiwań przed implementacją.
- E3-DA16 (A, 2026-10-27): pełny globalny stan i jawny prefiks, ponieważ odświeżanie pytania z fixture ukryłoby zużycie zgody, a syntetyczne zatwierdzenia bez pochodzenia osłabiłyby wniosek o historii wersji.
- E3-DA18 (A, 2026-10-27): preflight i dane przechowujemy w docs/preparations/e3-04, ponieważ sprawdzają wykonalność scenariusza istniejącym E2 i nie powinny udawać implementacji ani niezależnej wyroczni E3.4.
- E3-DA17 (A, 2026-10-27): główny graf in_preparation plus izolowane próby wpływu na wydanie, żeby zbadać skutki atomowego kroku bez przedwczesnego włączenia całego W06/odbioru.

A: przygotowanie oraz późniejsze wykonanie i dowody. R: niezależny przegląd granic, wyroczni i wyniku. U: rozstrzygnięcie nowej luki lub przyszły odbiór całego E3. Tematy T06–T10/T14, W/P poza wycinkiem, pełne S/L/F, CTL L1 i OBS pozostają w punkcie wznowienia, bez zmiany planu etapów.
