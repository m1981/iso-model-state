# E3.3 — niezależna wyrocznia katalogu

2026-10-27. Osobny autor przygotował `tests/fixtures/e3/catalog_oracle.py`
na podstawie `docs/E3-03-MAPOWANIE.md`, T00–T04, `item_types`,
`item_variables` i całej `test_instance` modelu v0.7. Odczytano
`execution.initial_state` dla kształtu rekordu oraz dokumentację predykatów
zależności. Nie importowano ani nie wywoływano wykonawcy, translatora ani
produkcyjnych predykatów. Moduł nie czyta YAML; jedyny import to `deepcopy`.

## Kontrakt i niezależne dane

`initial_items()` zwraca świeży słownik wszystkich ośmiu pełnych rekordów.
Każdy ma id, type, depends_on, predecessor, version, rejections, suspect,
state. Wszystkie zaczynają z state=none, version=0, rejections=0,
suspect=false, predecessor=none. Zbiory zależności są listami bez duplikatów;
c1 ma znormalizowane depends_on=[a1,d1]. Pozostałe krawędzie zapisano ręcznie:
r1/r2/r3→p1, d1/a1→r1, a2→r2; p1 nie ma zależności.

`step(items, command, *, budget=2, initial_version=1)` zwraca pełny nowy
katalog albo `None` dla niedostępnego przejścia. Dokładne pola komendy:
operation=0..4, item=p1/r1, actor=A/R/U, checks=bool, evidence=bool.
Daje to 120 komend. Nie ma pola predecessor: T00 używa wyłącznie domyślnego
argumentu none. Próba przekazania dodatkowego pola, także predecessor=none,
jest błędem kontraktu, a nie milczącym pominięciem argumentu.

Niepoprawny kształt katalogu, rekordu lub komendy, nieznane identyfikatory,
duplikaty krawędzi i niepoprawne typy skalarne powodują `ValueError`.
Złe zestawy typów zależności oraz cykle pozostają dopuszczalnymi danymi prób
negatywnych; odmowę wykonuje reguła T00. Licznik nie jest ograniczony budżetem
ani głębokością: mutant może ujawnić przekroczenie, a wyrocznia go nie odcina.
Wersje i liczniki muszą być nieujemnymi liczbami całkowitymi. Funkcje nie
zmieniają argumentów; każdy zwracany katalog zawiera niezależne listy i rekordy.

`budget` i `initial_version` ustala autor kontroli. Wariant budget=1 oraz
wariant initial_version=2 mają jawne oczekiwania niezależne od kandydata.
Nazwa `initial_version` oznacza wersję ustawianą przez T00: rzeczywisty Init
nadal ma version=0. Zmienione stany wejściowe nie są deklarowane jako osiągalne
od bazowego Init.

## Ręcznie wyprowadzone reguły

- T00: none, aktor A, poprawny zbiór typów bezpośrednich zależności i cały graf
  acykliczny. Nie wymaga dojrzałości zależności, checks ani evidence. Zmienia
  state=draft, version=initial_version, predecessor=none; zachowuje resztę.
- T01: draft, aktor A, brak suspect, checks=true i wszystkie aktualne
  bezpośrednie zależności approved/baselined. Zmienia tylko state=verified.
- T02: verified, aktor U, typ wymagający zatwierdzenia, brak suspect i dowód.
  Zmienia tylko state=approved. Checks oraz dojrzałość zależności nie są bramką.
- T03: verified, aktor U i rejections < budget. Zmienia state=draft i zwiększa
  rejections o jeden. Nie wymaga checks, evidence ani braku suspect.
- T04: approved/verified, aktor U, brak suspect, approved albo typ bez wymogu
  zatwierdzenia, wszystkie zależności baselined i dowód. Dla bazowych PLAN/REQ
  oznacza to koniecznie approved. Zmienia tylko state=baselined.

Dowód true reprezentuje poprawny demonstracyjny rekord, false jego brak.
Wyrocznia nie uwierzytelnia cytatów ani nie zastępuje kontroli pól dowodu
wykonywanej przez uprząż. Zależności każdej decyzji czytane są z bieżącego
katalogu. Pusty zbiór spełnia oba warunki dojrzałości.

Tabela referencyjna typów ma własne dane: PLAN→∅, REQ→{PLAN}, AT/DES→{REQ},
CODE→{DES,AT}; zatwierdzenia wymagają PLAN/REQ/AT. Nie pobiera tych danych
z modelu kandydata. `acyclic(items)` usuwa kolejno wierzchołki bez zależności;
pozostały niepusty graf bez takiego wierzchołka oznacza cykl. Bada również
sześć zamrożonych produktów. Niepoprawna krawędź albo duplikat daje false.

## Relacja TLA+

`tla_oracle(budget=2, initial_version=1, *, graph_acyclic=True)` zwraca
samodzielne definicje `ExpectedEnabled(before, command)` i
`ExpectedAction(before, after, command)`. Before/after są pełnymi funkcjami
ID→rekord, a depends_on zbiorami TLA+. Pomocnicze identyfikatory mają prefiks
Ref; własne `RefDependencyTypes` i `RefApprovalTypes` nie odwołują się do
kandydackiego Types. `RefTypeOK` czyta typy rekordów z bieżącego before.

Wynik acykliczności podaje się jako `graph_acyclic=acyclic(reference_items)`
dla niezależnie określonej instancji. Jest stałą tylko dlatego, że żadna
operacja tego wycinka nie zmienia topologii. Próba r1.depends_on=[] zachowuje
acykliczność, lecz T00(r1) narusza referencyjne typy. Próba
p1.depends_on=[r1] tworzy cykl p1↔r1, który blokuje również T00(r1).
Silniejsza izolowana próba cyklu w zamrożonej części to a1.depends_on=[c1]:
a1↔c1 blokuje T00 dla obu aktywnych produktów mimo poprawnych ich typów.

`ExpectedAction` wymaga dostępności i równości całego następnego katalogu
z `[before EXCEPT ![command.item] = replacement]`. Zastępuje pełny rekord
z zachowaniem wszystkich niewymienionych pól, więc sprawdza ramę ośmiu
produktów. Relacja służy do sprawdzania kandydata; nie może ograniczać jego
Next. Rama pytań i wydań pozostaje osobną odpowiedzialnością uprzęży Python.

## Ręczny świadek i samokontrola

`witness()` zawiera osiem inputs, dziewięć pełnych literalnych katalogów
expected oraz dwie refusals z polami after_index i command. Oczekiwania nie
powstają przez wywołanie step, initial_items ani wykonawcy.

| Indeks katalogu | Wykonana operacja | p1 | r1 |
|---:|---|---|---|
| 0 | Init | none, v0 | none, v0 |
| 1 | T00(r1) | none, v0 | draft, v1 |
| 2 | T00(p1) | draft, v1 | draft, v1 |
| 3 | T01(p1) | verified, v1 | draft, v1 |
| 4 | T02(p1) | approved, v1 | draft, v1 |
| 5 | T01(r1) | approved, v1 | verified, v1 |
| 6 | T02(r1) | approved, v1 | approved, v1 |
| 7 | T04(p1) | baselined, v1 | approved, v1 |
| 8 | T04(r1) | baselined, v1 | baselined, v1 |

T01(r1) po indeksie 2 jest odmówione, ponieważ p1 jest draft. T04(r1)
po indeksie 6 jest odmówione, ponieważ p1 jest approved, ale nie baselined.
Odmowy nie zmieniają numeracji wykonanych kroków. Sześć pozostałych produktów
zachowuje kompletne rekordy Init we wszystkich dziewięciu katalogach.

Samodzielny import i kontrola spójności Python: PASS. Sprawdzono osiem
następników względem literalnego świadka, obie odmowy, 120 komend i osiem
dostępnych komend w Init, niezmienianie argumentów, kontrolne budget=1
oraz skutek T00 version=2, zły zestaw typów, cykl aktywnych produktów i cykl
zamrożonej części, a także odrzucenie dodatkowego predecessor i boolów
podanych jako liczby. Niezależna enumeracja samej referencji daje 83 pełne
katalogi, 298 etykietowanych krawędzi i maksymalną głębokość 16.

Samokontrola tekstu TLA+ na przypiętym TLC także zakończyła się PASS:
jednostanowy moduł sprawdził osiem ExpectedAction dla literalnych katalogów
świadka i obie odmowy ExpectedEnabled. Nie używał translatora kandydata.

Te liczby i samokontrola dotyczą spójności wyroczni. Nie są dowodem zgodności
translatora ani wykonawcy, wynikiem TLC kandydata ani odbiorem E3.
