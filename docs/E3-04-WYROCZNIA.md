# Niezależna wyrocznia E3.4

2026-10-27. Autor wyroczni pracował w osobnym przebiegu na podstawie modelu v0.7, dokumentów zamiaru, [mapowania](E3-04-MAPOWANIE.md) i [przeglądu przygotowania](reviews/E3-04-PRZYGOTOWANIE-2026-10-27.md). Bazowy commit przekazany autorowi: `f728940`. Wynikiem są wyłącznie ten dokument oraz [impact_oracle.py](../tests/fixtures/e3/impact_oracle.py). Autor nie implementował translatora, nie uruchamiał E2 do wyznaczania oczekiwań, nie edytował modelu i nie wykonywał commitu.

## Źródła i niezależność

Reguły zapisano ręcznie z T01/T02/T04/T05/T11/T12/T13/P01/P02 oraz question/release semantics. Pełny punkt wejścia pochodzi z tabeli prefiksu i literalnej instancji modelu. Tabela 13 kroków jest ręcznym oczekiwaniem z mapowania: funkcja `witness()` rozwija jej jawne zmiany w 14 pełnych stanów przez kopiowanie. Nie wywołuje `step()`. Żadne oczekiwanie nie jest odczytem `expected-checkpoints.json` ani innego wyniku preflight.

Przeczytano strukturę rekordów E2, w tym kształt DEC i reprezentację wartości początkowych. Wyrocznia nie importuje żadnego modułu `isomodel`, parsera YAML, predykatów wykonawcy ani kodu translacji. Jedynymi importami są standardowe `copy` i `json`. Nie odczytuje plików podczas wykonywania relacji. To niezależność implementacji od kandydata, nie dowód nieomylności interpretacji wspólnego modelu.

Python wyszukuje dla każdego produktu źródło zmiany w jego przodkach. Referencja TLA+ poszerza zbiór zależnych najwyżej tyle razy, ile jest produktów. Oba algorytmy czytają cały bieżący graf; żaden nie ma tabeli zależnych zaszytej po ID ani nie używa produkcyjnego `_dependents`. Referencja nie enumeruje wszystkich ścieżek długości osiem. Odmienne algorytmy ograniczają ryzyko wspólnego błędu implementacyjnego; ich zgodność nie zastępuje ręcznego oczekiwania r1→{d1,a1,c1}, a1→{c1} i kontroli zmienionej krawędzi.

## Kontrakt dla uprzęży

| Funkcja | Wynik |
|---|---|
| `initial_state(transition_ids=TRANSITION_IDS)` | Nowa kopia pełnego świata po 29 krokach prefiksu. Osiem produktów, q0 resolved/approved/r1/v1/T05/age1/consumed=false, wydanie 1 in_preparation. |
| `command(...)` | Pełny rekord reprezentowanej komendy; domyślny aktor wynika z roli operacji. |
| `step(world, command, transition_ids=...)` | `None` dla odmowy procesu albo `{'world': full_successor, 'records': list}`. Nie zmienia wejścia. `ValueError` dla niepoprawnego kontraktu komendy. |
| `dependents(world, item)` | Zbiór wszystkich przechodnich zależnych z aktualnego pełnego katalogu. |
| `prefix_events(...)` | 29 jawnych zdarzeń w schemacie E2: 26 operacji produktów i P00/P01/P02. To scenariusz do wykonania, nie twierdzenie, że został wykonany. |
| `prefix_history(...)` | 19 wpisów T01/T02/T04 z identyfikatorem, rolą operacji, produktem i wersją 1, pochodzących z jawnego prefiksu. |
| `prefix_records(...)` | 29 oczekiwanych list records, ostatnia z jednym DEC q0/r1/v1/T05. |
| `witness(...)` | `commands`: 13 komend; `expected`: 14 pełnych światów; `records`: 13 list wyjść. |
| `tla_oracle(...)` | Samodzielne definicje `RefEnabled(w,c)` i `RefResult(w,c)`, z pomocnikami `Ref*`. Wymaga modułów `Naturals`, `Sequences`, `FiniteSets`. |

Kolejność ról operacji 0–8: T01, T02, T04, T05, T11, T12, T13, P01, P02. Pełne pola komendy to `operation`, `item`, `question`, `actor`, `checks`, `evidence`, `unambiguous`, `resolution`; brak celu oznacza tekst `none`. Aktor należy do A/R/U, trzy flagi są rzeczywistym bool, resolution to approved/rejected. Nieznane ID, zbędne pole, brak pola, błędny typ, brak/nieznane pytanie dla T05/P01/P02 i ponownie użyty identyfikator T12 są błędami wejścia, nie odmowami guard. Pozostałe flagi wypełniają rekord komendy także wtedy, gdy dana operacja ich nie używa. `RefEnabled` ma kontrakt poprawnych komend uprzęży; nie zastępuje walidatora niepoprawnych wejść.

`transition_ids` jest krotką dziewięciu różnych nazw w tej samej kolejności ról. Nazwa roli T05 trafia do zgody, tworzonego pytania, DEC i oczekiwania prefiksu. Dzięki temu kontrola przemianowanych operacji nie wymaga przepisania semantyki referencji.

W Pythonie releases ma klucz liczbowy 1, snapshot/acceptance mają `None`, a zależności i scope są deterministycznymi listami. W TLA+ zależności/scope są zbiorami, releases funkcją z domeną liczbową, questions funkcją o domenie istniejących pytań, w tym pustej. `None` przy serializacji odpowiada tekstowi `__null__`; modelowe `none` pozostaje osobną wartością tekstową. Records jest listą w Pythonie i sekwencją TLA+. Porównanie nie może usuwać żadnego pola świata ani DEC.

Dowód true reprezentuje jawny demonstracyjny rekord `simulation=True, decision=SIM_DEC, reference=SIM_REF, quote=SIM_QUOTE`. P02 zwraca kind=decision, id=SIM_DEC, question, quote, simulation, resolution, about, about_version i requested_transition. T11 wymaga dowodu, lecz nie tworzy dodatkowego records. Słownik evidence o złej strukturze pozostaje zadaniem walidacji uprzęży/E2 — wyrocznia komend reprezentuje tylko jego obecność/brak. P02 obsługuje również modelowe general→answered; eksplorowany wycinek tworzy tylko change.

## Reguły, historia i granice

Oczekiwanie T05 sprawdza osobno siedem składników zgody. Legalne następstwo zużywa ją, otwiera draft nowej wersji, zeruje rejections i własne suspect, oznacza pełne domknięcie zależnych, stosuje helper wydania i oba obserwatory. Observer oblicza nowo_suspect przez różnicę flag pre/post, a nie przez samą obecność suspect. Przy accepted zachowuje cały odebrany rekord i ustawia pending. Każda następna operacja wycinka jest wtedy odmówiona.

T11 wymaga dojrzałych bezpośrednich zależności bez suspect i dowodu. T13 usuwa własne suspect wyłącznie w draft. Zgodnie z poprawionym I03 T01 bada dojrzałość zależności, lecz nie ich suspect. T12 nie ma sztucznej zasady jednego wniosku na produkt; age to maksimum istniejących age plus jeden, z wartością 1 przy pustym rejestrze. P01 respektuje już asked, priorytet blocking i następnie wiek. Legalne stany utworzone przez proces mają unikalne age; nie ustanawiamy nowej reguły rozstrzygania sztucznie wstrzykniętych remisów.

Historia monitorów musi zostać potwierdzona odtworzeniem `prefix_events()` od rzeczywistego Init. `prefix_history()` jest oczekiwaną historią tych konkretnych operacji, nie syntetyczną historią odczytaną ze stanu baselined. Po otwarciu v2 poprzednie wpisy v1 pozostają historią v1 i nie spełniają obowiązku T01/T02 wersji 2. Autor wyroczni nie zapisuje fikcyjnego śladu wykonania.

Relacja nie ogranicza liczby pytań, wersji ani kroków. T12 może zwrócić czwarte pytanie, a T05 wersję 4. Uprząż ma najpierw porównać pełny następnik i records, a dopiero potem sklasyfikować przekroczenie max_questions/max_version lub głębokości 16. Wyrocznia nie ogranicza zbioru komend Next. Nie dowodzi pełnego procesu, L/F, zakleszczeń, odbioru wydania, pełnego WIT3 ani prawdziwości demonstracyjnych dowodów i oceny treści „bez wpływu”.

## Wykonana samokontrola autora wyroczni

1. Python porównał 13 wyników `step()` z niezależną ręczną tabelą 14 pełnych światów i records, sprawdził brak mutacji wejść, 29 zdarzeń prefiksu, 19 wpisów historii oraz pięć odmów w punktach świadka.
2. Osobne lokalne asercje objęły siedem składników zgody, aktorów A/R, pełny reset przy v3→v4, cztery pytania z age18/19/20, blokadę drugiego asked, rejected i brak jednoznaczności, 12 kombinacji liść/źródło z zależnymi × w/poza scope × ready/reviewed/accepted, pending, przemianowanie, pusty rejestr pytań oraz błędne typy komendy. To samokontrola, nie zaliczenie macierzy mutantów kandydata.
3. Samodzielny moduł TLC używający tylko referencji i ręcznej tabeli sprawdził 31 asercji: 13 enabled, 13 pełnych wyników i pięć odmów. TLC 2.19 z zatwierdzonego tla2tools.jar 1.7.4 zakończył bez błędu; techniczny graf miał jeden stan i pętlę. Pierwsze uruchomienie w sandboxie zatrzymał zakaz lokalnego portu RMI; dopiero ponowienie poza sandboxem na istniejącej zgodzie DEC-PRO-013 dało wynik semantyczny. To kontrola składni i skończonych oczekiwań wyroczni, nie główny graf E3.4 ani jego RED/GREEN.

Pełne badanie kandydata, zachowanie surowych dowodów, mutanty, porównanie grafów i niezależna recenzja należą do następnych kroków autora badania. Samokontrola wyroczni nie jest ich zamiennikiem.

## Zamrożenie przed integracją

| Źródło | SHA-256 bajtów |
|---|---|
| model/process.yaml | `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07` |
| docs/E3-04-MAPOWANIE.md | `c1c13010e6a6c8ad28e203b70460ba8f3bd509c03c78704559a9ce095fe32148` |
| docs/reviews/E3-04-PRZYGOTOWANIE-2026-10-27.md | `5468277b76df2f534433e8b9f477dfeb8ba604aacdf077a34623ef892e9ed61d` |
| tests/fixtures/e3/impact_oracle.py | `098854ff9f416aa302e2e1e347a0e19ef88c0b1d9487597ae4db25d04f758652` |

Decyzja autora wyroczni: pełne rekordy, osobne wyjścia DEC i dynamiczne pytania pozostają częścią referencji, ponieważ pominięcie ich pozwoliłoby ukryć zużycie zgody, błędne powiązanie albo zmianę odebranego wydania. Zmienia: nowe pliki wyroczni i opisu; nie zmienia zaakceptowanego modelu ani zakresu. Przejrzane: mapowanie §2–7, recenzja przygotowania oraz zapis I03.
