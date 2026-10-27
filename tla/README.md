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
