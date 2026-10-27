# E3.4 — zgoda na zmianę i jej wpływ

2026-10-27. **E3.4 wykonane; nie stanowi odbioru E3.** Polecenie użytkownika „wykonaj zgodnie z powyzszym” uruchomiło wykonanie przygotowanego [mapowania](E3-04-MAPOWANIE.md). Przygotowanie pozostaje historycznym pakietem; nie nadpisano jego wyników.

## Co daje wynik

Na przykładzie aplikacji do zadań zmiana wymagania r1 otwiera jego nową wersję i oznacza powiązane projekt d1, test a1 oraz kod c1 do ponownego sprawdzenia. Zgoda dotyczy konkretnego produktu, wersji i operacji, jest jednorazowa. Przegląd może potwierdzić aktualność projektu, ale zmieniany test wymaga własnej zgody i ponownej weryfikacji. Kod można oczyścić z flagi dopiero po uporządkowaniu zależności.

Badanie porównuje pełny stan, dostępność kroków i wyjścia decyzji dwóch implementacji — generowanej z YAML TLA+ i istniejącego wykonawcy E2 — z osobną wyrocznią. Pozwala sprawdzić, czy przyszłe narzędzie poprawnie rozpozna zgodę i pokaże konsekwencje zmiany. Nie ocenia trafności merytorycznej wymagania ani jakości testu.

## Zakres i niezależność

- Pełny katalog ośmiu produktów, cztery aktywne r1/d1/a1/c1; T01/T02/T04/T05/T11/T12/T13/P01/P02; głębokość 16. Wszystkie trzy role, obie odpowiedzi i reprezentowane kombinacje checks/evidence/unambiguous. q0 istnieje, q1/q2 powstają w badaniu; q3 jest reprezentantem próby przekroczenia granicy trzech pytań.
- Jawny 29-krokowy prefiks E2 przygotowuje stan wejściowy i historię par ID/wersja. TLC rozpoczyna się w tym stanie, nie w Init pełnego procesu. Świadek ma 13 dalszych kroków i 14 pełnych punktów kontrolnych, łącznie 42 kroki z prefiksem.
- [Osobna wyrocznia](E3-04-WYROCZNIA.md) została zamrożona przed integracją. Nie importuje E2 ani translatora. Osobny autor przygotował [60 przypadków i 34 mutanty](E3-04-CZULOSC.md); integrator wykonał je, a recenzent odtworzył wynik niezależnie.
- Trzy kontrole danych: przemianowanie dziewięciu operacji i ich referencji, zmiana zależności a1 na r2, inna początkowa wersja z dopasowaną zgodą i historią. Macierz R bada ready/reviewed/accepted, źródło w/poza zakresem oraz liść a2. Dwanaście jej kontekstów jest odtwarzanych rzeczywistymi prefiksami E2; wstrzyknięte izolacje w A/I są jawnie oznaczone.
- Dwa dodatkowe konteksty historyczne z a1.predecessor=a2 służą wyłącznie izolacji błędnego powiązania pytania/DEC. Nie twierdzimy, że są osiągalne w głównym grafie. Oddzielny moduł TLC zachowuje ich stałą ramę.

## Wyniki i DoD

Niezależne odtworzenie recenzenta zakończyło wszystkie **79 przebiegów TLC**: 42 poprawne przebiegi oraz 37 oczekiwanych naruszeń nazwanych niezmienników (34 wykrycia mutantów + trzy odizolowane monitory). Bez błędów narzędzia i timeoutów. Autor powtórzył komplet z tym samym wynikiem. Pełna regresja: **514 testów passed**, skrypt spójności: **413 kontroli OK**. [Niezależna recenzja](reviews/E3-04-WYKONANIE-2026-10-27.md) zamyka W01–W03.

| Sprawdzenie | Wynik |
|---|---|
| Baza | 19 797 stanów, 38 340 dozwolonych krawędzi; identyczny pełny zbiór stanów TLC/Python, brak różnic z wyrocznią |
| Przemianowane operacje | 19 797 stanów, 38 340 krawędzi; zgodność |
| Zależność a1 → r2 | 4 565 stanów, 8 500 krawędzi; zgodność |
| Początkowa wersja 2 | 19 797 stanów, 38 340 krawędzi; zgodność |
| Macierz A/I/R | 58 prób semantycznych + dwa błędy wejścia; pełne stany/records i odmowy zgodne |
| Konteksty wydań | 12 prefiksów E2; trzy jawne pending_release i trzy pary izolujące priorytet W06 |
| Mutanty | 34/34 wykryte właściwą kontrolą, każdy ma osobny rzeczywiście wykonany zły następnik zgodny z niezależnym oczekiwaniem |
| Monitory | Consumed, VerifiedHistory i ApprovedHistory wykrywają własne usterki; pełne kontrprzykłady potwierdzone przez E2 |
| Świadek | 29 kroków prefiksu + 13 kroków wycinka; 14 pełnych checkpointów i wyjścia records |
| Granice | W bazie 13 006 krawędzi przekracza limit pytań; 586 stanów kończy się na głębokości 16. Osobne próby czwartego pytania i wersji 4 |

Krawędzie są dozwolonymi komendami rozwijanych węzłów; kilka komend może dawać ten sam następnik. Liczba 13 006 dotyczy krawędzi, a 586 stanów — nie sumujemy ich jako liczby niezależnych przypadków. W grafie wersji 2 nie osiągnięto przekroczenia wersji; czułość tej granicy daje jawna osobna próba.

## TDD i znalezione błędy implementacji

Pierwszy test nowego przejścia był rzeczywiście czerwony z powodu braku modułu translatora (`red-collection.log`), po implementacji przeszedł. Recenzent następnie wykazał milczące przyjmowanie zmienionych opisów semantyki pytań i wydań. Dodano testy, które rzeczywiście dały 20 niepowodzeń; translator teraz odmawia nieobsługiwanej semantyki. Logi RED i GREEN są zachowane. Kolejna uwaga R wykazała przyjmowanie zapisów do technicznego question.id, których E2 nie obsługuje; trzy rzeczywiście czerwone testy potwierdziły lukę przed poprawką.

R wykazał też maskowanie trzech odmów T11 po odbiorze przez inne warunki. Zachowano ich jawny powód pending_release, a niezależny autor dodał trzy odmowy T01 i trzy legalne kontrole po wyłączeniu wyłącznie pending. Dzięki temu blokada W06 jest rozstrzygającym warunkiem. Nie zmieniono modelu procesu, jego właściwości, interpretacji ani istniejącego wykonawcy E2.

Podczas integracji dwa wyrażenia mutantów używały ID produktu jak literału DSL; nie były legalne w interpreterze. Nie liczono błędu narzędzia jako wykrycia błędu procesu. Autor danych zastąpił te próby legalnymi odwołaniami do istniejących pól rekordu i jawnie wstrzykniętą historią. Poprawiono również techniczną podmianę algorytmu domknięcia, tak aby zwracała rekordy produktów zgodnie z kontraktem E2. To korekty uprzęży, nie reguł v0.7.

Pierwsze odtworzenie R w sandboxie zatrzymał błąd lokalnego RMI; ponowienie w zatwierdzonym środowisku przeszło. Pierwszy końcowy przebieg autora miał jeden błąd SANY: brak standardowego modułu Sequences we wspólnym katalogu tymczasowym. Podejrzenie kolizji plików tymczasowych podczas równoległych JVM jest hipotezą, nie wynikiem dowodu. Pełny przebieg autora z własnym java.io.tmpdir zakończył się poprawnie; logi nieudanych prób są zachowane jako błędy narzędzia, bez zaliczania ich do wykryć mutantów.

## Granice i sposób interpretacji

`evidence=True` reprezentuje konkretny poprawny dowód demonstracyjny SIM_DEC/SIM_REF/SIM_QUOTE, a false jego brak. Nie dowodzi to autentyczności podpisu ani realnego commita. Translator odmawia tekstów spoza Latin-1 zamiast je przekształcać; ślady badania używają ASCII. Zmienione opisy semantyki, nieznane pola i nieobsługiwany DSL muszą być jawną odmową translacji.

Granice są terminalnym wynikiem badania, nie odmową procesu. Po dopuszczonym kroku zapisywany jest pełny następnik, records i historia; kontrole nadal sprawdzają ten stan. Oryginalny E2 zgłasza `ExplorationBoundary`. Aby zobaczyć następnik, uprząż powtarza krok na osobnej kopii modelu ze zwiększonymi wyłącznie bounds; zachowuje oryginalny wyjątek i potwierdza niezmienność wejścia. Główna eksploracja nadal używa przyjętych granic. Oddzielne próby obejmują czwartą wersję oraz czwarte pytanie.

Dwa mutanty direct/all celowo podmieniają algorytm domknięcia w kandydacie; nie są mutacjami YAML. Archiwum zawiera podmienioną linię oraz hashe modułów przed/po. Usunięcie create w T12 sprawdzane jest dodatkowo zdarzeniem bez argumentu question: zwykłe zdarzenie z tym argumentem ma osobno zachowany InputError, którego nie zaliczamy jako semantycznego wykrycia. Wersja pytania i powiązanie DEC mają osobne kontrole pól. Dwa monitory historii oraz monitor zużycia zgody uruchamiane są osobno bez ogólnego Successor, żeby nierówność stanu nie maskowała ich nieskuteczności. Pełny kontrprzykład z logu TLC jest parsowany i porównywany z rzeczywistym wykonaniem E2 mutanta, a osobne asercje potwierdzają r1/v2 bez odpowiedniej historii v2 albo niezużyte q0 po T05.

Wycinek nie dowodzi wszystkich S/L/F, osiągalności pełnego procesu ani braku zakleszczeń; CHECK_DEADLOCK FALSE dotyczy końców badanego wycinka. L1 w CTL pozostaje osobnym zadaniem. Pełny cykl wydania, pozostałe operacje, temporalne mutanty i OBS należą do dalszego E3. API/CLI użytkowe nadal czekają na E4/E5.

## Dowody dostawy

[Manifest](../tla/e3-04/manifest.json) przypina **30 źródeł**, SHA-256 zestawu `1557a8bf09ff358895958e38893308c93818320e22b9c3db6c1e8714b0ad5706`. Archiwa author.tar.gz i reviewer.tar.gz zachowują pełne moduły, konfiguracje, logi, dump i JSON bez przepisywania bajtów; pominięto tylko roboczy katalog TLC states. Osobny tool-errors.tar.gz zachowuje raporty błędnych prób i pierwszy rzeczywisty błąd każdego rodzaju. Obok są logi TDD, pełnej regresji i spójności. Mapowanie, wyrocznia oraz model mają zachowane hashe; wersja procesu pozostaje v0.7.

## Odtworzenie i decyzje agenta

`.venv/bin/python scripts/run_e3_impact.py --output artifacts/e3-04/reproduction` wymaga nowego/pustego katalogu i przypiętych narzędzi z [instrukcji](../tla/README.md). Źródła nie mogą zmienić się w czasie przebiegu. Kody 0/1/2/3 oznaczają spełnienie oczekiwań/rozbieżność/błąd narzędzia lub wejścia/timeout. `--baseline-only` jest wyłącznie pomiarem bazy i nie wykonuje DoD. Dowody demonstracyjne nie są decyzjami użytkownika.

- **E3-DA19**, A, 2026-10-27: stan terminalny po przekroczeniu bounds oraz odrębny odczyt kandydata E2 na kopii z większymi samymi limitami, bo odcięcie przed krokiem ukryłoby złe skutki. Zmienia: nowa uprząż; przejrzane: mapowanie §6, wykonawca E2, uwaga R o granicy.
- **E3-DA20**, A, 2026-10-27: cache tylko kompilacji AST w izolowanej instancji niezmienionego E2, bo wielokrotne parsowanie identycznych reguł dominuje czas badania. Zmienia: nowy runner; przejrzane: semantyka guard/effects, porównanie 13 pełnych kroków z wykonaniem bez cache.
- **E3-DA21**, A, 2026-10-27: oddzielamy mutanty danych, algorytmu i kontraktu wejścia oraz kontrolujemy konkretne pola i monitory osobno, bo ogólna nierówność mogłaby maskować niewrażliwość właściwego sprawdzenia. Zmienia: nowa macierz/uprząż; przejrzane: zamrożona wyrocznia, mapowanie §5/7, uzgodnienia z R.

Właściciel A: kompletna dostawa i punkt wznowienia; R: niezależny przegląd; U: przyszły odbiór całego E3 lub zmiana zaakceptowanego zamiaru. Brak nowego pytania do U na etapie wykonania.
