# E3.3 — tworzenie produktów i dynamiczna dojrzałość zależności

2026-10-27. **Przyrost wykonany i sprawdzony; E3 pozostaje w toku.** Polecenie U: „super przyklad, wykonaj e3.3 jak planowales”, po E3.2 w `1585449`. Model v0.7, właściwości, interpretacje i wykonawca E2 bez zmian.

## Co zyskujemy

Badanie obejmuje teraz utworzenie produktów i dojście do linii bazowej od rzeczywistego stanu początkowego. Plan i wymaganie rozwijają się razem; kontrola dojrzałości zależności korzysta z ich bieżących stanów. Operator może pozwolić agentowi wcześniej przygotować wymaganie, a proces nadal blokuje przedwczesną weryfikację i linię bazową.

Przykład to **plan lokalnej aplikacji do zadań** (p1) i **wymaganie zachowania statusu zadania po ponownym uruchomieniu** (r1). To znaczenie produktów użytych w badaniu procesu, a nie implementacja takiej aplikacji lub test jej zapisu na dysku.

| Krok | Operacja | Plan p1 | Wymaganie r1 |
|---:|---|---|---|
| 0 | rzeczywisty Init | none | none |
| 1 | A tworzy wymaganie, T00 | none | draft |
| 2 | A tworzy plan, T00 | draft | draft |
| — | próba T01(r1): **odmowa**, plan niezatwierdzony | draft | draft |
| 3 | A weryfikuje plan, T01 | verified | draft |
| 4 | U zatwierdza plan, T02 | approved | draft |
| 5 | A weryfikuje wymaganie, T01 | approved | verified |
| 6 | U zatwierdza wymaganie, T02 | approved | approved |
| — | próba T04(r1): **odmowa**, plan bez linii bazowej | approved | approved |
| 7 | U ustanawia linię bazową planu, T04 | baselined | approved |
| 8 | U ustanawia linię bazową wymagania, T04 | baselined | baselined |

Osiem kroków wykonano w Pythonie i TLC, porównując wszystkie dziewięć pełnych katalogów z literalnymi oczekiwaniami osobnego autora. Dwie odmowy to osobne próby; nie doliczamy ich do wykonanych kroków. T02 i T04 otrzymują demonstracyjne dowody. Symulacja nie uwierzytelnia rzeczywistej decyzji użytkownika.

## Zakres i wyniki

[Mapowanie](E3-03-MAPOWANIE.md) oceniono [przed implementacją](reviews/E3-03-MAPOWANIE-2026-10-27.md). Osobny autor przygotował [niezależną wyrocznię](E3-03-WYROCZNIA.md), bez użycia translatora ani wykonawcy do wyliczania oczekiwań. Jej relacja sprawdza kandydacki następnik; nie ogranicza Next.

Pełny katalog zawiera osiem produktów, aktywne są p1 i r1. Badamy T00–T04 i 120 komend na stan: dwie pozycje, pięć operacji, trzy role, dwa warianty checks i dwa evidence. Głębokość 16 obejmuje obie pełne drogi z dwoma odrzuceniami każdego produktu. T00 używa wyłącznie domyślnego predecessor=none. Sześć pozostałych produktów i topologia pozostają niezmienne. Python dodatkowo sprawdza zachowanie całej ramy globalnej, w tym wydań i pytań.

| Próba bez mutacji reguł | Odrębne stany TLC | Wynik |
|---|---:|---|
| bazowa | 83 | zgodność zbiorów stanów TLC/Python i wyroczni |
| przemianowane ID T00–T04 | 83 | zachowanie odczytywane z danych |
| budżet odrzuceń = 1 | 42 | zgodność z odrębnym oczekiwaniem |
| T00 ustawia wersję 2 | 83 | zgodność z odrębnym oczekiwaniem |
| brak wymaganej zależności r1 | 13 | T00(r1) blokowane, plan może się rozwijać |
| cykl w zamrożonej części katalogu | 1 | tworzenie obu aktywnych produktów blokowane |

Bazowy graf ma **298 etykietowanych dozwolonych krawędzi**, 83 stany i maksymalną głębokość 16. Porównanie zbiorów uwzględnia także historię i liczniki uprzęży, a nie tylko liczbę stanów. W sześciu powyższych próbach nie ma rozbieżności z niezależną wyrocznią. Błędne grafy są celowymi instancjami kontrolnymi, nie stanami osiągniętymi w bazowym procesie.

## Czułość na błędy

Osiem mutantów: brak ustawienia wersji przez T00, nieuprawniony aktor T00, pominięte typy zależności, pominięta acykliczność, pominięte zatwierdzenie przed T04, pominięta dojrzałość zależności T04, nieuprawniony aktor T04 i brak wymogu dowodu T04. **Wszystkie osiem wykryto nazwaną właściwością i odtworzono osobnym wykonanym świadkiem błędnego skutku.** Brak wersji narusza Successor, pozostałe Availability.

Acykliczność translator wylicza własnym DFS po wszystkich ośmiu rekordach; wyrocznia używa niezależnego usuwania wierzchołków bez zależności. Stała jest poprawna tylko dzięki niezmiennej topologii. Cykl a1↔c1 w części nieaktywnej potwierdza, że kontrola nie ignoruje tej części katalogu. Translator odmawia nieobsługiwanych zmian topologii.

Osobno włączone monitory CreatedVersion i ApprovedHistory ujawniają właściwe kontrprzykłady, nawet gdy ogólna wyrocznia jest wyłączona. Test regresyjny dodatkowo podmienia cel T00 na approved i sprawdza, że samo nadanie nazwy stanu nie fałszuje historii zatwierdzenia. Historię aktualizuje rzeczywista operacja T01/T02 i jej wynik. Ograniczona wersja tego wycinka nie obejmuje późniejszych zmian wersji produktu.

**27 uruchomień TLC na pełne odtworzenie**: baza 1, kontrole danych 3, błędne konteksty 2, mutanty 8, ich świadki 8, monitory 2, świadek bazowy 1, odmowy 2. [Niezależny recenzent](reviews/E3-03-WYKONANIE-2026-10-27.md) odtworzył ten sam komplet.

## TDD i poprawki z recenzji

1. RED: brak modułu tla_catalog. Po implementacji sprawdzenia jednostkowe przechodziły; pierwszy przebieg ujawnił też jeszcze niedostarczony plik dokumentacji wyroczni. To brak kompletu wejść, nie naruszenie reguły procesu.
2. R wskazał, że pierwotny monitor zapamiętywał sam nowy stan zamiast operacji. Najpierw wystąpił błąd składni wcięcia kwantyfikatora Next. Po jego poprawieniu uzyskano **semantyczny RED**: TLC przepuszczał celowo błędne T00→approved, a test oczekiwał naruszenia ApprovedHistory. Dodanie kontroli numeru operacji w TLC i Pythonie dało GREEN. Zachowano oba logi i rozróżniono ich znaczenie.
3. Uzupełniono odmowy brakującego wiązania T00 oraz niepoprawnych dowodów T04: bool jako liczba, brak reference/quote, puste wymagane pola i nieznane pole. Zgodnie z E2 pola wymagane zależą od przejścia; nie dodawano nowych reguł modelu.
4. Pierwsze pełne odtworzenie dało poprawny graf i mutanty, ale dwie odmowy miały **błąd narzędzia**: TLC nie dopuszcza stałej Next=FALSE jako akcji. Zastąpiono ją relacją akcji z UNCHANGED i FALSE, nadal bez następników. Ponowiono cały komplet oraz regresję; błędnego przebiegu nie zaliczono jako dowodu odmowy.
5. Końcowo **449 testów passed**, **413 kontroli spójności OK**. Niezależna recenzja nie pozostawia otwartych ustaleń blokujących. Logi i oba poprawne odtworzenia są zachowane.

## Tożsamość i odtworzenie

- SHA-256 modelu (bajty): `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07`; kanonicznie `ecca43e1402ee476502943caa16556d5609021b8894f3a702e26ca2da3cf21a6`.
- Hash 25 plików źródłowych: `e16b2d1a2e35289be0e4ea630b0360ab4a88a0f35912b37f0bf0c49593854eb9`. Sprawdzony przed i po badaniu, wspólny dla autora i recenzenta.
- TLA+ tools release 1.7.4, TLC 2.19, JAR `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`, JBR 21.0.10+7-b1163.110. Jeden worker, fp=0, seed=1, do 60 s na pojedyncze TLC.
- Polecenie: `.venv/bin/python scripts/run_e3_catalog.py --output artifacts/e3-03/reproduction`. Nowy lub pusty katalog; `--help`, `--java`, `--jar`, `--timeout`. Kody 0/1/2/3: oczekiwania spełnione/rozbieżność/błąd/timeout. Instrukcja w [tla/README.md](../tla/README.md).
- [Manifest](../tla/e3-03/manifest.json) wiąże archiwa autora i recenzenta z oryginalnymi ścieżkami i sumami każdego pliku. Surowe bajty modułów, konfiguracji, logów, dump oraz wyników JSON są zachowane w tar.gz. Podsumowania można czytać bez rozpakowania. Logi TDD i regresji są w [tdd](../tla/e3-03/tdd/). Archiwa E3.1 i E3.2 pozostają historycznymi dowodami swoich wersji.

E3-DA13 (A, 2026-10-27): surowe dowody zachowujemy w dwóch archiwach tar.gz z manifestem bajtów, aby nie powiększać przeglądu kodu o dziesiątki tysięcy wygenerowanych linii; pomijamy wyłącznie robocze pliki TLC states/. E3-DA14 (A, 2026-10-27): monitor historii wymaga wykonania właściwej operacji, ponieważ sama nazwa stanu może zostać nadana przez błędne przejście.

## Granice i punkt wznowienia

Wynik obejmuje tylko opisany wycinek z rzeczywistego Init. Nie obejmuje zmiany krawędzi ani poprzednika, propagacji suspect, pytań, odbiorów wydań, całych S/L przy F, braku zakleszczeń ani dowodu L1 w CTL. CHECK_DEADLOCK FALSE odpowiada końcom tego badania. TLC używa fingerprintów; to badanie skończonej instancji, nie dowód dedukcyjny ani pomiar skuteczności współpracy w projekcie.

Właściciel A: następnie przygotować mapowanie wpływu zmiany produktu na zależne produkty, z wyraźnym ujęciem wersji, suspect i zgody na zmianę, przed kolejnym rozszerzeniem generatora. Pozostałe zobowiązania E3: pełna relacja przejść, S/L przy F, mutanty czasowe, metoda CTL dla L1, OBS i niezależny przegląd całego etapu. Właściciel U: przyszły odbiór E3 po tej dostawie zbiorczej. E4 odtworzy rzeczywistą historię; API/CLI pozostaje odłożone zgodnie z DEC-PRO-011.
