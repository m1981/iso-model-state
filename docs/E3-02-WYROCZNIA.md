# E3.2 — niezależna wyrocznia pętli

2026-10-27. Osobny autor wyroczni, bez udziału w generatorze E3.2.
Artefakt: `tests/fixtures/e3/loop_oracle.py`, importowalny samodzielnie przez
`importlib.util.spec_from_file_location`. Jedyny import to `copy.deepcopy`.

Podstawa reguł: T01–T03 z wiążącego `model/process.yaml`; podstawa próbek:
`item_types`, `item_variables`, `test_instance` oraz `E3-02-MAPOWANIE.md`.
`execution.py` odczytano dla kształtu pełnego rekordu i kontraktu demonstracyjnego
dowodu. Nie użyto `execute_step`, `initial_state`, `compile_expression`,
translatora ani odczytu kandydackiego YAML do obliczenia oczekiwań.

## Kontrakt

- `contexts()` zwraca osiem świeżych kontekstów. Każdy ma `id`, pełny `item`,
  listę pełnych rekordów bezpośrednich `dependencies`, `budget=2` i logiczne
  `requires_approval`. Stan początkowy jest syntetyczny: draft, rejections=0.
- `domain(context, depth=8)` zwraca iloczyn trzech stanów
  draft/verified/approved i liczników 0..depth, zachowując całą ramę rekordu.
  `depth` jest całkowite w 0..8. Wyrocznia obsługuje zewnętrzną dziedzinę 0..8,
  niezależną od budżetu 2; dzięki temu licznik 3 nie zostaje odcięty.
- `oracle_step(context, before, operation, actor, checks, evidence)` zwraca
  pełny oczekiwany następnik albo `None` dla niedostępnej akcji. Operacje 1/2/3
  odpowiadają regułom specyfikacji, niezależnie od ID w kopii YAML. Aktor to
  A/R/U; dwa ostatnie argumenty są rzeczywistymi bool. `evidence=False` oznacza
  brak dowodu, `True` poprawny demonstracyjny dowód. Nie obejmuje to badania
  prawdziwości cytatu.
- Nieznane pola, brak danych, zmiana ramy `before`, stan poza wycinkiem lub
  licznik poza 0..8 powodują `ValueError`, nawet gdy akcja miałaby być odmówiona
  z innego powodu. Funkcje nie zmieniają argumentów i zwracają kopie.
- Wariant budżetu lub metadanych typu otrzymuje oddzielny kontekst z jawnie
  podmienionym `budget` albo `requires_approval`; nie wylicza się tych wartości
  z badanej kopii modelu.

Pełna rama globalna pozostaje obowiązkiem uprzęży. Moduł określa pełny rekord
zmienianego elementu i stałe dane zależności. Nie deklaruje, że samodzielnie
sprawdził wydania, pytania lub pozostałe elementy.

## Ręczne wyprowadzenie

T01 wymaga draft, aktora A, braku suspect, checks=true i dojrzałości każdej
bezpośredniej zależności: approved lub baselined. Pusta lista spełnia warunek.
Zmienia wyłącznie state na verified; nie zeruje rejections. Evidence nie jest
bramką tej reguły.

T02 wymaga verified, aktora U, requires_approval=true, braku suspect i dowodu.
Zmienia wyłącznie state na approved. Checks i dojrzałość zależności nie są
oddzielnymi bramkami T02. Wstrzyknięty verified z niedojrzałą zależnością może
zatem zostać zatwierdzony; nie twierdzimy, że taki stan jest bazowo osiągalny.

T03 wymaga verified, aktora U i rejections < budget. Zmienia state na draft
i zwiększa rejections o dokładnie jeden. Nie ma bramek suspect, checks,
requires_approval ani evidence. Wszystkie pozostałe pola pozostają bez zmian.

Ręczne liczby dostępnych akcji dla całej dziedziny (27 rekordów × 36 wejść):

| Kontekst | T01 | T02 | T03 | Razem |
|---|---:|---:|---:|---:|
| req_approved | 18 | 18 | 8 | 44 |
| req_baselined | 18 | 18 | 8 | 44 |
| req_draft | 0 | 18 | 8 | 26 |
| req_suspect | 0 | 0 | 8 | 8 |
| plan_empty | 18 | 18 | 8 | 44 |
| des_no_approval | 18 | 0 | 8 | 26 |
| code_good | 18 | 0 | 8 | 26 |
| code_mixed | 0 | 0 | 8 | 8 |

18 dla T01 to 9 liczników × 2 wartości evidence. 18 dla T02 to 9 liczników ×
2 wartości checks. 8 dla T03 to 2 dozwolone liczniki × 2 wartości checks ×
2 wartości evidence. Są to liczby dla szerokiej dziedziny, nie liczby krawędzi
grafu osiągalnego. W `code_mixed` pierwsza zależność jest approved, a druga
draft: pominięcie drugiej zależności musi zostać ujawnione.

## Świadek i sprawdzenie własne

`witness()` zapisuje osobno ręcznie wyprowadzone pełne rekordy i wejścia:

| Krok | Operacja | Aktor | checks | evidence | Stan po | rejections |
|---:|---|---|---|---|---|---:|
| 0 | inicjalizacja | — | — | — | draft | 0 |
| 1 | T01 | A | true | false | verified | 0 |
| 2 | T03 | U | false | false | draft | 1 |
| 3 | T01 | A | true | false | verified | 1 |
| 4 | T03 | U | false | false | draft | 2 |
| 5 | T01 | A | true | false | verified | 2 |
| 6 | T02 | U | false | true | approved | 2 |

Przez cały świadek: r1, REQ, depends_on=[p1], predecessor=none, version=2,
suspect=false; p1 jest approved. Trzecie T03 po kroku 5 jest niedostępne,
ale T02 jest dostępne. Oczekiwane rekordy świadka nie powstają przez
`oracle_step` ani wykonawcę produkcyjną.

Wykonano kontrolę własną samodzielnym importem modułu: 7776 decyzji porównano
z powyższymi ręcznymi licznościami; sześć następników wyroczni porównano z
niezależnie zapisanym świadkiem. Sprawdzono zachowanie wersji 2, odmowę trzeciego
odrzucenia, oddzielny budget=1, requires_approval=true dla DES, niezmienianie
argumentów oraz `ValueError` dla zmienionej ramy i niepoprawnych typów wejść.
Wynik: PASS. To kontrola spójności artefaktu wyroczni, nie walidacja translatora,
wykonawcy ani dowód TLC.
