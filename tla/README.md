# Badanie E3.1

To test translacji lokalnej relacji T03 z YAML, oparty na syntetycznych próbkach. Nie jest pełnym modelem procesu, dowodem S/L ani CLI do prowadzenia projektu. Zakres: [mapowanie](../docs/E3-01-MAPOWANIE.md), wynik: [raport](../docs/E3-01-RAPORT.md).

## Przygotowanie

Python i zależności zgodnie z głównym README. Narzędzia Java/TLC wymagają zgody na środowisko; dla tej sesji udzielono jej w DEC-PRO-013. Nie potrzeba instalatora systemowego ani zmiany PATH/JAVA_HOME.

Przypięcie: [tools/tla-toolchain.json](../tools/tla-toolchain.json). Pobranie w nowym środowisku jest osobnym, jawnym działaniem:

```sh
mkdir -p artifacts/tools/tla/1.7.4
curl --fail --location https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar --output artifacts/tools/tla/1.7.4/tla2tools.jar
shasum -a 256 artifacts/tools/tla/1.7.4/tla2tools.jar
```

Oczekiwany SHA-256: `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`. Przy pierwszym pobraniu sprawdzono też SHA-1 wydawcy: `bee4a54f3ee3d4afc347c3240ec2d9e93b075104`. Runner odmawia użycia innych bajtów. Kontrola sumy nie jest niezależnym audytem dostawcy.

Domyślna Java pochodzi z lokalnego PyCharm; inną istniejącą Javę podaje się przez `--java /pełna/ścieżka/bin/java`, a lokalizację przypiętego JAR przez `--jar /pełna/ścieżka/tla2tools.jar`. Sprawdzono JBR 21.0.10+7-b1163.110. Wersja runtime trafia do każdego wyniku. TLC korzysta z lokalnego portu RMI: ograniczony sandbox może odmówić uruchomienia. Taka odmowa to błąd środowiska, nie naruszenie modelu.

## Odtworzenie

Z katalogu głównego repozytorium:

```sh
.venv/bin/python scripts/run_e3.py --help
.venv/bin/python scripts/run_e3.py --output artifacts/e3-01/reproduction
```

Runner wykonuje dwa testy narzędzia, bazową regułę, pięć kontrolowanych wariantów danych, trzy mutanty oraz trzy osobne świadki skutków mutantów. YAML pozostaje niezmieniony. Limit pojedynczego TLC: 60 s, jeden worker. Nie pobiera zależności automatycznie.

| Kod wyjścia | Znaczenie | Następny krok |
|---|---|---|
| 0 | Wszystkie oczekiwania badania spełnione | Odczytać zakres i ograniczenia; nie oznacza odbioru E3 |
| 1 | Rozbieżność semantyczna lub niekompletny oczekiwany wynik | Sprawdzić próbę i wyrocznię w evidence.json |
| 2 | Błąd narzędzia/wejścia | Sprawdzić komunikat, JAR/Java, log i konfigurację |
| 3 | Limit czasu | Badanie nieukończone; bez wniosku o poprawności |

Wyniki: `report.md`, `evidence.json`, moduły `.tla` i `.cfg`, przypadki, pełne logi, dump odwiedzonych stanów i wynik każdego procesu w osobnym katalogu `run-*`. Oczekiwania w JSON są wyrocznią, a nie odczytem dump. Przy ponawianiu badania używać nowego katalogu `--output`, aby zachować spójny wcześniejszy komplet modułów i dowodów. Lokalny `artifacts/` jest ignorowany przez Git; zapisane dowody dostawy znajdują się w `tla/e3-01/`.

Pełny `pytest -q` obejmuje TLC i wymaga tego środowiska; brak narzędzia kończy się błędem, nie pominięciem testów. W obecnej konfiguracji testy integracyjne używają domyślnej ścieżki Javy/JAR z tej maszyny. Sam runner przyjmuje jawne ścieżki na innej maszynie.

## Granice

Tylko T03 jest przedmiotem tego rzutu; pozostałe T00–T02, T04–T14, P00–P05 i W01–W07 nie są wygenerowane jako akcje procesu. Dopuszczenie lokalnych konstrukcji składni nie oznacza walidacji innych przejść. Brak następcy jest oczekiwaną odmową albo końcem jednego kroku, więc test ma `CHECK_DEADLOCK FALSE`. Nie przenosić tego ustawienia do dowodu braku zakleszczeń.

Do dalszego E3 pozostają pełna relacja procesu, osiągalność, własności S/L, sprawiedliwość, mutanty czasowe i OBS. L1 (`AG EF done`) wymaga osobnego rozwiązania dla CTL. Nie zastępujemy go milcząco własnością LTL.

## Badanie wielokrokowe E3.2

E3.2 rozszerza translator o T01/T02, stałe zależności, metadane typu oraz jawne wejścia checks/evidence. [Raport i granice](../docs/E3-02-RAPORT.md), [mapowanie](../docs/E3-02-MAPOWANIE.md), [wyrocznia](../docs/E3-02-WYROCZNIA.md).

```sh
.venv/bin/python scripts/run_e3_loop.py --help
.venv/bin/python scripts/run_e3_loop.py --output artifacts/e3-02/reproduction
```

Używa tego samego toolchainu i kodów 0/1/2/3 co E3.1. Katalog wyjściowy musi być nowy albo pusty. Runner wykonuje 31 uruchomień TLC, każde z limitem do 60 s; nie edytować źródeł w czasie badania. Hash wejść jest kontrolowany przed i po wykonaniu; zmiana unieważnia wynik. Nowy katalog zachowuje poprzedni komplet dowodów. Ustawienia `--java` i `--jar` działają tak jak wyżej; automatyczne pobieranie nie występuje.

Osiem kontekstów z syntetycznego Init, trzy reguły i głębokość 8 nie stanowią pełnej eksploracji procesu. W szczególności koniec w verified dla DES/CODE nie oznacza zakleszczenia: T04 jest poza wycinkiem. Brak dowodu to bool false reprezentujący nieobecne pole evidence; tekst `"false"` jest błędem wejścia. Wyniki w `tla/e3-02/` obejmują surowe dowody autora i niezależnego recenzenta, z przenośnym manifestem. Archiwum E3.1 pozostaje zapisem wcześniejszej wersji.

## Katalog PLAN–REQ — E3.3

[Raport](../docs/E3-03-RAPORT.md), [mapowanie](../docs/E3-03-MAPOWANIE.md), [niezależna wyrocznia](../docs/E3-03-WYROCZNIA.md). T00–T04 działają na pełnym ośmioelementowym katalogu, z dwoma aktywnymi produktami. Init pochodzi z modelu; dojrzałość zależności zmienia się w toku badania. Topologia i sześć pozostałych produktów są zamrożone, a T00 używa wyłącznie domyślnego predecessor=none.

```sh
.venv/bin/python scripts/run_e3_catalog.py --help
.venv/bin/python scripts/run_e3_catalog.py --output artifacts/e3-03/reproduction
```

Ten sam toolchain, limity i kody zakończenia co wyżej. Runner wykonuje 27 uruchomień TLC, porównuje pełne zbiory stanów z Pythonem i niezależną wyrocznią, zachowuje świadek ośmiu kroków oraz dwie osobne odmowy. Źródła muszą pozostać niezmienne podczas przebiegu. Katalog wyniku musi być nowy albo pusty.

Surowe dowody obu odtworzeń znajdują się w `e3-03/author.tar.gz` i `e3-03/reviewer.tar.gz`. [Manifest](e3-03/manifest.json) podaje SHA-256 każdego archiwum i każdego pliku wewnątrz oraz ścieżkę oryginalną. Archiwa zachowują bajty modułów, konfiguracji, logów, dump i wyników JSON; pomijają wyłącznie roboczy katalog TLC `states/`. Czytelne podsumowania są obok archiwów. Przykład odczytu bez rozpakowania:

```sh
tar -xOf tla/e3-03/author.tar.gz evidence.json
tar -xOf tla/e3-03/author.tar.gz baseline/Catalog.tla
```

Wynik nie dowodzi całego procesu, nie bada L przy F ani nie zamyka E3. Historyczne archiwa E3.1/E3.2 pozostają niezmienione.

## Zgoda i wpływ zmiany — E3.4

[Raport](../docs/E3-04-RAPORT.md), [mapowanie](../docs/E3-04-MAPOWANIE.md), [niezależna wyrocznia](../docs/E3-04-WYROCZNIA.md), [przypadki i czułość](../docs/E3-04-CZULOSC.md). Pełny stan katalogu, pytań i wydań; aktywne r1/d1/a1/c1. T05 i T11–T13, P01/P02 oraz powrót przez T01/T02/T04. TLC zaczyna od jawnego prefiksu 29 kroków E2, z historią ID/wersja; główny graf ma głębokość 16. Wydania bada osobna macierz kontekstów, bez generowania pełnego cyklu W.

```sh
.venv/bin/python scripts/run_e3_impact.py --help
.venv/bin/python scripts/run_e3_impact.py --output artifacts/e3-04/reproduction
```

Ten sam przypięty toolchain, nowy/pusty katalog, niezmienne źródła podczas badania i kody 0/1/2/3. Pełne badanie wykonuje 79 uruchomień TLC: cztery grafy, dwie grupy macierzy, granice, wykrycia i świadki 34 mutantów, trzy odizolowane monitory i pełny świadek. Pojedyncze TLC ma limit 60 s; cały runner wykonuje także porównania w Pythonie i trwa dłużej. `--baseline-only` mierzy wyłącznie bazę, nie realizuje DoD E3.4.

Granica eksploracji nie jest odmową procesu. Pełny następnik kroku przekraczającego limit nadal podlega kontroli, po czym nie jest rozwijany. Runner zachowuje oryginalne `ExplorationBoundary` E2 i osobny odczyt tego następnika na kopii z większymi samymi bounds. Kod 0 nie oznacza pełnego dowodu S/L/F ani odbioru etapu.

Dowody autora i niezależnego odtworzenia: `e3-04/author.tar.gz`, `e3-04/reviewer.tar.gz`; [manifest](e3-04/manifest.json) przechowuje hashe archiwów, każdego pliku wewnątrz i źródeł. Pominięty jest wyłącznie roboczy katalog TLC `states/`. Logi RED/GREEN i regresji są obok. Przykład odczytu:

```sh
tar -xOf tla/e3-04/author.tar.gz report.md
tar -xOf tla/e3-04/author.tar.gz baseline/Impact.tla
```

Przy równoległych niezależnych badaniach warto przydzielić każdemu procesowi własny istniejący katalog tymczasowy Javy przez `JAVA_TOOL_OPTIONS=-Djava.io.tmpdir=/bezwzgledna/sciezka`. W E3.4 pojedynczy przebieg zgłosił brak standardowego modułu Sequences we wspólnym katalogu; pełne ponowienie z izolacją przeszło. Przyczyna kolizji pozostaje hipotezą. Nieudane próby RMI i SANY zachowano w `e3-04/tool-errors.tar.gz`; nie są zaliczone jako kontrprzykłady modelu. Końcowy autor użył katalogu `artifacts/e3-04/author-isolated-tmp` z pełną ścieżką repozytorium; ustawienie jest widoczne w zapisanej wersji Javy i logach. Nie zmieniono globalnej konfiguracji Javy.
