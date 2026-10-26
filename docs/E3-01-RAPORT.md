# E3.1 — wynik lokalnego sprawdzenia T03

2026-10-27. **Sprawdzenia przyrostu zakończone powodzeniem; E3 jako etap pozostaje w toku.** Podstawa: DEC-PRO-012/013, model v0.7. Wykonano rzeczywiste TLC, porównanie z interpreterem Python i niezależnymi oczekiwaniami. Reguły procesu nie zostały zmienione.

## Co wnosi wynik

Generator odczytuje z YAML rolę, stan wejściowy, limit i skutek odrzucenia, a nie tylko nazwę T03. Dla ośmiu jawnych próbek wynik jest zgodny z oczekiwaniami. Jest to sprawdzony początek tłumaczenia do TLA+, na którym można rozwijać badanie wielokrokowe. Nie daje jeszcze kontroli rzeczywistego repozytorium ani dowodu całego procesu.

## Przedmiot i odtworzenie

- Model: kanoniczny SHA-256 `ecca43e1402ee476502943caa16556d5609021b8894f3a702e26ca2da3cf21a6`; bajty YAML `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07` — identyczne z odebraną v0.7.
- Wejścia tego wykonania: SHA-256 `3f60b5d51f058464fe356cafcd44d10d2982b6a085fe4e71f4401927fba33547`. Manifest obejmuje model, kod, zależności, testy, próbki, mapowanie i smoke. Szczegóły: [evidence.json](../tla/e3-01/evidence.json).
- Narzędzie: release TLA+ tools **1.7.4**, log TLC2 **2.19 / rev 5a47802**; JAR SHA-256 `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`. JBR 21.0.10+7-b1163.110. Jeden worker, fp=0, seed=1, limit 60 s na przebieg.
- Polecenie: `.venv/bin/python scripts/run_e3.py --output artifacts/e3-01/reproduction`. [Instrukcja środowiska, kodów i ograniczeń](../tla/README.md).
- Pełne logi, moduły, konfiguracje i dump zachowano w repo. [Manifest archiwum](../tla/e3-01/manifest.json) wiąże oryginalne lokalne ścieżki zapisane w evidence.json z przenośnymi kopiami i ich sumami. Odtworzenie tworzy nowe ścieżki/czasy, więc nie oczekujemy identycznych bajtów całego raportu.

## Wykonane kontrole

| Próba | Wynik TLC | Odrębne stany | Znaczenie |
|---|---|---:|---|
| Reguła bazowa | passed | 11 | 8 wejść, 3 dopuszczone następniki; dostępność i cały rekord zgodne |
| Zmiana ID | passed | 11 | Zachowanie pochodzi z definicji, nie nazwy T03 |
| Limit = 1 | passed | 9 | Odczyt zmienionego parametru |
| from = approved | passed | 9 | Odczyt stanu wejściowego |
| to = deferred | passed | 11 | Odczyt stanu docelowego |
| to = „=” | passed | 11 | Zachowanie stanu przy wykonanym skutku |
| Brak limitu (mutant) | Availability naruszone | TLC nie podał statystyki | Niepoprawna dostępność przy liczniku 2 |
| Aktor A (mutant) | Availability naruszone | TLC nie podał statystyki | Rozbieżność uprawnienia |
| Brak inkrementacji (mutant) | Successor naruszone | 9 | Niepoprawny następnik |

Dwa naruszenia Availability występują podczas sprawdzania Init. Nie przedstawiamy ich jako wykonanych kroków. **Każdy mutant ma dodatkowy wykonany świadek z dwoma stanami**: licznik 2 → 3, aktor A wykonujący odrzucenie, licznik 0 pozostający 0 po odrzuceniu. Cały następnik sprawdzają TLC i Python. Te dodatkowe oczekiwania opisują celowo uszkodzoną kopię, nie przyjętą regułę procesu.

Smoke narzędzia: poprawny model ma dwa stany i kod 0; naruszony `WithinLimit` ma kod 12 oraz kontrprzykład 0 → 1. Osobne testy obejmują błędną specyfikację, brak/zmieniony JAR, rzeczywisty timeout, niepotwierdzony komunikat sukcesu oraz odmowę nieobsługiwanej semantyki także pod fałszywym guard. Błąd środowiska nigdy nie jest wykryciem mutanta.

## TDD i regresja

Zachowane [logi przebiegów](../tla/e3-01/tdd/):

1. RED translatora/runnera TLC: dwa błędy kolekcji z powodu brakujących modułów; hashe ówczesnych testów i fixture zapisano przed kodem. To dowód braku implementacji, nie test czułości semantycznej.
2. Pierwsze wykonanie: 24 passed, 1 failed — TLC dopisuje `.dump`, a runner wskazywał niewłaściwą ścieżkę stanów. Po poprawce: 25 passed.
3. RED komendy badania: dwa testy nie przechodzą z powodu braku `run_e3.py`. Po implementacji i dodaniu osobnych świadków: 27 passed.
4. Uzupełnienie walidacji: nowy test niepoprawnego typu depends_on najpierw wykazał surowy TypeError, a po poprawce kolejności kontroli przechodzi z czytelnym ProjectionError. Recenzent niezależnie wykonał wszystkie **28 nowych testów**.
5. Regresja całego repo przed tą poprawką: **416 passed**; końcowa regresja po poprawce: **417 passed**, bez pominięcia TLC. Kontrola spójności: **413 OK**. Dotychczasowe testy i wykonawca E2 pozostają bez zmian.

Pierwsza próba smoke w sandboxie zakończyła się odmową lokalnego portu RMI. Powtórzono ją poza sandboxem w zatwierdzonym zakresie. Nie traktowano tego jako czerwonego testu reguły. Przyrost nie instaluje Javy i nie zmienia globalnej konfiguracji.

## Recenzja i ograniczenia

Mapowanie oceniono przed implementacją: [raport R](reviews/E3-01-MAPOWANIE-2026-10-26.md). Uwagę o `state := ...` rozstrzygnięto zgodnie z interpreterem: stan zmienia `to`, takie przypisanie w effects jest odrzucane. Wykonanie ocenia osobny R: [recenzja końcowa](reviews/E3-01-WYKONANIE-2026-10-27.md); nie jest to podpis użytkownika pod etapem.

Próbki są syntetyczne. Badanie nie dowodzi ich osiągalności, całych S1/S15, żywotności, sprawiedliwości ani braku zakleszczeń. `CHECK_DEADLOCK FALSE` dotyczy tylko testu jednego kroku. TLC stosuje fingerprinty stanów; nie jest to dowód dedukcyjny. Pozostałe przejścia procesu są poza rzutem (lista w instrukcji). Zgodność z Pythonem jest dodatkową kontrolą, nie źródłem oczekiwań. Historyczny wynik i odbiór E2 zachowano; rozszerzony zbiorczy hash źródeł nie jest hashem dawnej dostawy E2.

## Następny przyrost i decyzje agenta

- E3-DA05, 2026-10-27: obok naruszeń dostępności zapisano osobne wykonane świadki mutantów, aby wykazać ich skutki mimo zatrzymania TLC w Init.
- E3-DA06, 2026-10-27: zarchiwizowano surowe dowody z manifestem, ponieważ ignorowany artifacts nie przetrwa świeżego klonu; JAR pozostaje lokalny i przypięty sumą.
- Właściciel A: przygotować E3.2 — mapowanie i wyrocznie wielokrokowej pętli przygotowanie → weryfikacja → odrzucenie (T01–T03), z jawnie określonym kontekstem globalnym. Najpierw przegląd zakresu, potem TDD; nie rozszerzać po cichu do całego modelu.
- Właściciel A: późniejsze E3 obejmie pozostałe przejścia, S/L przy F, mutanty czasowe i OBS; osobno ustalić realizację CTL dla L1. API pozostaje odłożone do wniosków E4.
