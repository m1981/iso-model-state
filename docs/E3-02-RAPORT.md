# E3.2 — wielokrokowa weryfikacja, zatwierdzenie i odrzucenie

2026-10-27. **Sprawdzenia przyrostu zakończone powodzeniem; etap E3 pozostaje w toku.** Kontynuacja na polecenie „wykonaj dalej w rezimie”, po E3.1 w 790b822. Model v0.7, właściwości i wykonawca E2 nie zmieniły się. Narzędzie pozostaje lokalne, przypięte zgodnie z DEC-PRO-013.

## Wynik praktyczny

Badanie potwierdza w opisanym wycinku, że ponowna weryfikacja zachowuje licznik odrzuceń. Po dwóch odrzuceniach trzecie jest blokowane, a poprawną propozycję nadal można zatwierdzić. Zatwierdzenie wymaga wcześniejszej weryfikacji, uprawnionego aktora U i demonstracyjnego dowodu decyzji. Rozwijamy w ten sposób sprawdzony translator, potrzebny do późniejszego badania całego procesu.

Oto **wykonany w Pythonie i TLC** świadek dla r1, wersji 2, przy stałej zależności p1 w approved:

| Krok | Akcja | Stan po kroku | Licznik odrzuceń |
|---:|---|---|---:|
| 0 | syntetyczny stan wejściowy | draft | 0 |
| 1 | T01, A | verified | 0 |
| 2 | T03, U | draft | 1 |
| 3 | T01, A | verified | 1 |
| 4 | T03, U | draft | 2 |
| 5 | T01, A | verified | 2 |
| 6 | T02, U, dowód decyzji | approved | 2 |

Wszystkie pozostałe pola produktu i globalna rama są zachowane. Oczekiwania siedmiu pełnych rekordów zapisał osobny autor, bez użycia wykonawcy ani translatora do ich wyliczenia. To świadek lokalny, nie WIT2 od Init całego procesu ani odbiór wydania.

## Zakres i metoda

[Mapowanie](E3-02-MAPOWANIE.md) oceniono [przed kodem](reviews/E3-02-MAPOWANIE-2026-10-27.md). [Niezależna wyrocznia](E3-02-WYROCZNIA.md) określa osiem kontekstów, 27 rekordów domeny i 36 kombinacji wejść. Jawne tablice wyroczni nie ograniczają Next. TLC bada dostępność każdej akcji oraz wszystkich następców w odwiedzonych stanach do ośmiu kroków; na końcowej głębokości nadal sprawdzane są następnik i historia.

Checks i evidence są wejściami kroku. Evidence=false oznacza brak pola, true poprawny demonstracyjny rekord, a nie domysł zgody. Wadliwe rekordy są odrębnymi odmowami wejścia. Pusty nadmiarowy quote przy T01 nie jest błędem E2; T01 go nie wymaga. T02 wymaga niepustego quote. Nie zmienialiśmy tych reguł, aby dopasować testy.

| Kontekst bazowy | Odrębne stany TLC | Wynik i znaczenie |
|---|---:|---|
| REQ, zależność approved | 9 | zgodny graf weryfikacji, odrzucenia i zatwierdzenia |
| REQ, zależność baselined | 9 | zgodny graf |
| REQ, zależność draft | 1 | weryfikacja niedostępna |
| REQ z suspect | 1 | weryfikacja niedostępna |
| PLAN bez zależności | 9 | poprawny sens pustego forall |
| DES bez wymogu zatwierdzenia | 6 | T02 niedostępne dla tego typu |
| CODE, obie zależności dojrzałe | 6 | T01 dostępne, T02 niedostępne |
| CODE, druga zależność draft | 1 | dojrzałość pierwszej zależności nie wystarcza |

Każdy bazowy graf i trzy kontrole danych mają **ten sam zbiór pełnych stanów pomocniczych i produktów w dump TLC i Pythonie**, po normalizacji zbioru depends_on. Porównano też każdą badaną komendę z niezależną wyrocznią. Kontrole danych: przemianowanie trzech ID (9 stanów), limit=1 (6), wymóg zatwierdzenia DES w kopii metadanych (9).

Wynik jednego stanu lub koniec w verified nie oznacza zakleszczenia procesu. Dla DES/CODE dalszą drogę daje m.in. T04, który pozostaje poza tym wycinkiem.

## Czułość i historia

Osiem mutantów jest wykrytych przez nazwaną wyrocznię: pominięcie zależności, checks albo suspect w T01; T02 dopuszczone z draft; T02 aktora A; usunięty wymóg dowodu; usunięty limit T03; reset licznika przez T01. Pierwszych siedem narusza Availability, reset — Successor. **Każdy ma również osobny wykonany świadek błędnego skutku**, z porównaniem pełnego dump i Pythonem; sama odmowa translatora nie jest wynikiem pozytywnym mutacji.

Trzy dodatkowe konfiguracje włączają pojedynczy monitor historii, aby wcześniejsza kontrola nie maskowała jego nieskuteczności:

- HistoryBudget: mutant bez limitu osiąga trzeci krok T03 tej samej wersji.
- CounterHistory: reset w T01 rozbiega licznik produktu z rzeczywistą historią odrzuceń.
- VerifiedHistory: zatwierdzenie z draft zachodzi bez wcześniejszego verified.

Łącznie badanie obejmuje **31 rzeczywistych uruchomień TLC**: 8 kontekstów, 3 kontrole danych, 8 mutantów, 8 ich świadków, 1 świadek bazowy i 3 osobne monitory. Osobny recenzent odtworzył cały komplet na tych samych źródłach.

## TDD, regresja i ustalenia

Zachowane [logi TDD](../tla/e3-02/tdd/):

1. RED: brak modułu `tla_loop`; po minimalnej implementacji 7 testów jednostkowych przechodzi.
2. Pierwsza integracja: 1 failed, 7 passed. TLC miało poprawny wynik, lecz porównanie Pythonowe traktowało kolejność listy depends_on jako istotną. Poprawka normalizuje wyłącznie zbiór zależności. Następnie E3.2 wraz z testami translatora E3.1: 26 passed.
3. Monitory historii: RED brak funkcji; GREEN trzy właściwe kontrprzykłady w TLC.
4. Recenzent wykazał brak ścisłych odmów na granicy danych. Testy odtwarzają brak dependencies, budget=true oraz tekstowe evidence/checks i logiczne operation. Po walidacji kończą się czytelną odmową przed wygenerowaniem modelu lub wykonaniem kroku. Dodatkowo źródła są hashowane przed badaniem i sprawdzane po nim; zmiana unieważnia raport. RED zachowano. Jeden test niepoprawnie wymagał niepustego nadmiarowego quote przy T01; skorygowano oczekiwanie do istniejącego E2, bez zmiany wykonawcy. Końcowo 14 testów jednostkowych przechodzi.
5. Pełna regresja: **433 passed**, bez pominięcia TLC. Kontrola spójności: **413 OK**. Logi końcowe zapisano w archiwum.

[Recenzja wykonania](reviews/E3-02-WYKONANIE-2026-10-27.md) zawiera niezależne odtworzenie, kontrolę wyroczni i zamknięcie ustaleń; nie jest odbiorem E3 przez użytkownika.

## Tożsamość dowodu i odtworzenie

- Model — SHA-256 bajtów: `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07`; kanonicznie `ecca43e1402ee476502943caa16556d5609021b8894f3a702e26ca2da3cf21a6`.
- Końcowe 24 pliki wejściowe: `3b527c6de498bd4a4da3c77a45fb7a4b4432e1375eab5f3dbeb2c1f6f2d8126e`; jednakowy hash autora i recenzenta.
- TLA+ tools release 1.7.4, JAR SHA-256 `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`, JBR 21.0.10+7-b1163.110; jeden worker, fp=0, seed=1, limit 60 s na pojedyncze TLC.
- Polecenie: `.venv/bin/python scripts/run_e3_loop.py --output artifacts/e3-02/reproduction`. Katalog musi być nowy albo pusty. `--help`, `--java`, `--jar`, `--timeout`; kody 0/1/2/3: spełnione oczekiwania/rozbieżność/błąd/timeout. Zero nie oznacza odbioru etapu.
- [Manifest archiwum](../tla/e3-02/manifest.json) wskazuje surowe moduły, konfiguracje, logi i dump obu autorstw oraz [evidence autora](../tla/e3-02/author/evidence.json) i [evidence recenzenta](../tla/e3-02/reviewer/evidence.json). Oryginalne ścieżki i komendy pozostają w danych; manifest prowadzi do przenośnych kopii. Nie normalizowano bajtów logów/dump.

Historyczne dowody E3.1 pozostają niezmienione. Ich manifest odpowiada ówczesnej implementacji, nie nowemu rozszerzeniu translatora. Pełny wynik E3.2 nie jest odbiorem E2 ani ponownym podpisem użytkownika.

## Granice i następny krok

To eksploracja ograniczonego wycinka przy stałych zależnościach i niezmiennej wersji, z syntetycznego Init. Nie dowodzi osiągalności z Init procesu, całych S1/S3/S4/S15/L4, sprawiedliwości, braku zakleszczeń, pełnego L1 w CTL ani użyteczności CLI. CHECK_DEADLOCK FALSE dotyczy oczekiwanych końców tego testu. TLC stosuje fingerprinty stanów; nie jest to dowód dedukcyjny.

E3-DA09 (A, 2026-10-27): trzy monitory badamy dodatkowo osobno, ponieważ wcześniejsza wyrocznia mogłaby ukryć ich stałe true. E3-DA10 (A, 2026-10-27): porównujemy rzeczywiste zbiory stanów, z zachowaniem zbiorowego sensu zależności, oraz zachowujemy oba niezależne komplety dowodów.

Właściciel A: przygotowanie E3.3 — mapowanie tworzenia produktu i linii bazowej (T00/T04) oraz dynamicznych zależności między produktami; najpierw uzasadnić instancję i rzut, potem przegląd i TDD. To kolejny krok do całego modelu, nie nowy projekt API. Pełne E3 nadal wymaga pozostałych przejść, S/L przy F, mutantów czasowych, OBS i odbioru U.
