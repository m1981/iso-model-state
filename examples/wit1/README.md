# WIT1 — wykonywalny przykład w E2

To demonstracja i test integracyjny na sztucznej instancji, pierwotnie dla modelu v0.4; zapisany raport odtworzono na v0.5. Nie jest formalnym świadkiem wygenerowanym przez TLC ani odbiorem projektu. Opis procesu pozostaje w `model/process.yaml` i `docs/WLASCIWOSCI.md`.

## Uruchomienie

Z katalogu repozytorium:

```sh
uv run --locked --offline python scripts/run_wit1.py --output artifacts/wit1
```

Wymaga istniejącego środowiska/zależności z `uv.lock`; przy pierwszym przygotowaniu środowiska można pominąć `--offline`. Bez `--output` skrypt wypisuje raport na standardowe wyjście.

- `artifacts/wit1/report.md`: czytelny przebieg 29 kroków, warunki, cytaty demonstracyjne, końcowe stany i siedem prób obejścia bramek.
- `artifacts/wit1/trace.json`: pełne kopie stanów przed i po każdym kroku, zdarzenia, założenia wejściowe, identyfikatory SHA-256 modelu, scenariusza, kodu, mutantów i pliku zależności.
- [report.md](report.md): zapisana migawka raportu wykonania z 2026-10-24. Można odtworzyć ją powyższym poleceniem; po zmianie kodu lub wejść porównać identyfikatory.

Kod wyjścia: 0 — scenariusz wykonany i wszystkie siedem prób mutacyjnych wykryte; 1 — odmowa kroku, błąd wykonania zapisany w raporcie lub niewykryty mutant; 2 — błąd wczytania, zapisu lub przygotowania sprawdzeń. Kod 0 nie oznacza spełnienia całego DoD.

Testy:

```sh
uv run --locked --offline pytest -q
uv run --locked --offline python scripts/check_model.py
```

## Co jest wykonywane

Scenariusz jest zapisany w `tests/fixtures/wit1/scenario.json`. Kolejność:

1. p1, r1, r2, a1, a2: T00(A) → T01(A) → T02(U) → T04(U).
2. d1 i c1: T00(A) → T01(A) → T04(U).
3. W01(A) → W02(R) → W04(U).

Wynik: siedem elementów `baselined`, wersja 1, bez `suspect`; wydanie 1 `accepted` z własną migawką oraz demonstracyjnym cytatem. Przy weryfikacji i bazowaniu zależności mają wymaganą dojrzałość. Każde T02/T04/W04 jest osobnym zdarzeniem U.

`checks_ok(e)` i `tests_ok` są jawnie zadane w scenariuszu zgodnie z abstrakcją modelu. Brak wartości lub tekst zamiast bool to błąd wejścia; false uniemożliwia właściwe przejście. Wykonawca nie weryfikuje treści prawdziwego PLAN/REQ/CODE ani nie uruchamia ich testów.

## Decyzje implementacyjne agenta

- Biblioteka `src/isomodel/execution.py` jest czysta: przyjmuje model, stan, zdarzenie i dane, zwraca nowy stan. Nie korzysta z Git, sieci ani zapisów do plików. Pliki wynikowe zapisuje wyłącznie skrypt, do wskazanego katalogu.
- `from`, `to`, `actor`, `guard` i `effects` pochodzą z YAML. Brak tabeli zachowania wybieranej po T00/W04 itd. Test zmienia ID tworzenia i jego skutek w kopii modelu, sprawdzając, że wykonawca respektuje dane.
- Interpreter `expressions.py` rozpoznaje małą gramatykę, a nie wykonuje tekstu jako Python. Obsługuje nazwy i atrybuty, bool/int, zbiory, nawiasy, and/or/not, implikację, równość, przynależność, dodawanie, porównanie `<`, kwantyfikatory oraz funkcje potrzebne WIT1. Kwantyfikator wiąże wyrażenie do końca aktualnego nawiasu lub tekstu. Sprawdzane jest całe drzewo, również nieosiągnięte gałęzie i puste dziedziny.
- Cały krok jest kompilowany przed wykonaniem. Skutki i obserwator działają na kopii; wyjątek nie udostępnia częściowo zmienionego stanu. Pola niewymienione w skutkach pozostają bez zmian. Obserwator `detect_post_acceptance_change` również jest odczytywany z YAML.
- Początkowe wartości produktów i wydania pochodzą z deklaracji modelu. Migawka kopiuje wartości `type`, `depends_on` i wszystkich `item_variables`. Historia raportu, stan końcowy, model i wejściowy scenariusz nie współdzielą zmiennych struktur.
- Dowód T02 ma pola `decision`, `quote`; T04 — `reference`, `quote`; W04 — `quote`. Każdy dowód ma `simulation: true`. To format wejścia symulatora realizujący opisane w YAML dowody; nie nowy rodzaj zatwierdzenia. Odwołania `SIM-*` są demonstracyjne i nie tworzą rzeczywistych DEC ani tagów.
- Weryfikacja aktora R sprawdza rolę zdarzenia; nie uruchamia ani nie poświadcza rzeczywistego niezależnego przeglądu implementacji.
- Nieobsługiwane konstrukcje, helpery zmian i tworzenie kolejnego wydania kończą się jawnym `unsupported`. Pytania dodano w kolejnym [przyroście WIT2/WIT4](../questions/README.md). Wykonawca nie obsługuje pustego zakresu wydania. Przy niepustym zakresie W01 sprawdza zarówno kompletność, jak i globalne testy/pytania; przed poszerzeniem o pusty zakres trzeba ujednoznacznić wiązanie kwantyfikatora i globalnych członów W01. Nie zmieniono przyjętego YAML ani nie ustanowiono zakazu pustego zakresu w procesie.
- Przekroczenie granicy eksploracji jest raportowane osobno jako `boundary`, nie jako niedozwolone przejście lub zakleszczenie. Obsługa W06 i granicy wielu wydań wymaga dalszego przyrostu.

## Dowody i ich ograniczenia

- Test pełnego WIT1 sprawdza dokładną kolejność, aktorów, końcowe wartości, migawkę, protokół i ciągłość historii.
- Testy odmów sprawdzają role, pominięcie zatwierdzenia/weryfikacji/przeglądu, dojrzałość obu zależności CODE, flagi suspect, pytania, kompletność i dowody. Część testów wstrzykuje stan do izolowanego sprawdzenia warunku; nie są dowodami osiągalności tych stanów.
- Hypothesis generuje kombinacje stanów DES i AT, aktora, suspect oraz wyniku checks_ok dla T01(CODE), porównując wykonawcę z niezależnie zapisanym kryterium. To jeszcze nie pełna maszyna stanów S1–S10.
- Siedem mutantów w `mutants/wit1_gates.json` dotyczy wybranych przypadków S1, S2, S3, S4, S7a, S7b i S8. Poprawny model odrzuca próbę, mutant przyjmuje ten sam krok. Zmiany istnieją wyłącznie w kopii modelu w pamięci.
- Test polecenia uruchamia przykład dwukrotnie z innego katalogu, porównuje raporty i sprawdza niezmienność dokumentów oraz plików modelu.
- Rozdzielenie kopii migawki jest testowane; zmianę po odbiorze sprawdza także [WIT5](../wit5/README.md). WIT2/WIT4 mają osobne wykonanie w E2. WIT3, pełne G/S/L (w tym pełny dowód S10), mutacje wszystkich właściwości i dowód TLC pozostają w planie.

Początkowy przebieg TDD: 50 nieprzechodzących przypadków, z błędem `NotImplementedError` wykonawcy. Zapis wyniku końcowego i punkt wznowienia: `docs/STAN.md`.
