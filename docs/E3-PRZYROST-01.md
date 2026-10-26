# E3.1 — przygotowanie pierwszego przyrostu TLA+

Data: 2026-10-26. Status: **przygotowanie po odbiorze E2, bez implementacji i wykonania TLC**. Podstawa: DEC-PRO-012, model v0.7 / DEC-PRO-010. Jest to dobór środków w ramach E3, nie zmiana semantyki ani rozszerzenie DoD. [Plan](../PLAN.md), [właściwości](WLASCIWOSCI.md), [stan i decyzje](STAN.md).

## Wynik dla użytkownika i granica przyrostu

Pierwszy przyrost ma dostarczyć odtwarzalny dowód, że generator przenosi do TLA+ mały fragment reguł YAML bez ukrytego uproszczenia: uprawnienie U, stan wejściowy, warunek limitu i skutek odrzucenia T03. Dzięki temu dalsze badanie procesu będzie oparte na sprawdzonym tłumaczeniu, a nie drugim, ręcznie napisanym modelu.

Wybrano T03, ponieważ obejmuje kontrolę aktora i granicę liczbową z rzeczywistym skutkiem, a pozostaje wystarczająco małe do ręcznego sprawdzenia. To test lokalnej relacji przejścia; nie dowód całego S1/S15, pętli T01–T03, osiągalności, braku zakleszczeń ani L1–L5. W tym przyroście nie dodajemy API, CLI użytkowego ani nowych reguł modelu.

## Kontrakt pierwszego sprawdzenia

- Wejście generatora: wiążący YAML, wybrane przejście oraz jawna instancja testowa. `from`, `to`, `actor`, `guard`, `effects` i parametr MAX_REJECTIONS pochodzą z danych. ID służy wyborowi, nie zastępuje definicji reguły; test zmiany ID musi zachować zachowanie.
- Dla tego wycinka translator obsługuje wymagane porównanie, dodawanie, przypisanie oraz kontrolę stanu i aktora. Nieznana składnia lub nieobsługiwany skutek wybranego przejścia powoduje czytelną odmowę generowania. Nie wolno pomijać go lub traktować jak true. Raport jawnie wymienia przejścia poza wycinkiem; nie nazywamy wyniku pełnym modelem v0.7.
- Test rozdziela wejściowe polecenie (aktor) od stanu produktu. Ocenia dostępność akcji i cały rzut stanu po akcji, w tym brak zmian pozostałych objętych rzutem pól. Nie używa stutter jako dowodu wykonania T03.
- Przygotowane przypadki początkowe są **syntetycznymi stanami testu jednostkowego**. Nie przedstawiamy ich jako świadków osiągalności od Init pełnego procesu. Wszystkie wyłączenia globalnych mechanizmów modelu i odwzorowanie stanu na rzut muszą być zapisane przed implementacją oraz sprawdzone przez R.

| Przypadek dla modelu bazowego | Oczekiwany wynik niezależnej wyroczni |
|---|---|
| verified, U, rejections=0 lub 1 przy MAX_REJECTIONS=2 | Akcja dostępna; draft, licznik zwiększony dokładnie o 1; pozostałe pola rzutu bez zmian. |
| verified, U, rejections=2 | Brak następcy przez T03; brak skutku. |
| verified, A albo R, licznik poniżej limitu | Brak następcy przez T03. |
| draft albo approved, U, licznik poniżej limitu | Brak następcy przez T03. |
| Ten sam fragment z przemianowanym ID | Te same wyniki; generator nie przełącza zachowania według napisu T03. |
| Parametr limitu zmieniony wyłącznie w kopii testowej | Generator odczytuje nowy limit; przypadki graniczne dostosowane do niego. Wiążący model bez zmiany. |
| `from=[approved]` wyłącznie w kopii testowej | U poniżej limitu: approved dopuszczone, verified odmówione. Wykrywa zaszyty stan wejściowy, którego nie ujawnia samo przemianowanie ID. |
| `to=deferred` wyłącznie w kopii testowej | Poprawna akcja kończy się w deferred, z inkrementacją i bez pozostałych zmian rzutu. Wykrywa zaszyty stan docelowy. |

## Kolejność TDD i wymagane dowody

1. **Kontrakt i wyrocznia:** przygotować powyższe przypadki, dokładny rzut oraz niezależnie zapisane oczekiwania. R sprawdza zakres i wyłączenia przed rozszerzeniem generatora. Można współdzielić parser składni YAML, lecz oczekiwany wynik nie może być wyliczony przez ten sam translator, który jest badany.
2. **RED:** uruchomić testy interfejsu generatora i wykonania relacji. Zapisać faktyczny brak implementacji, a później oczekiwane rozbieżności zachowania. Brak JAR/Javy jest błędem środowiska, a nie dowodem czułości testu procesu. Nie zgłaszać GREEN, jeśli testy TLC są pominięte.
3. **GREEN:** zaimplementować najmniejszy translator tego wycinka. TLC ma rzeczywiście zbadać dostępność i następniki akcji, a Python porównać wynik z niezależnymi oczekiwaniami oraz lokalnym wykonaniem istniejącego interpretera. Sam poprawny tekst TLA+ lub identyczność dwóch implementacji nie wystarcza.
4. **Mutacja:** w kopiach danych usunąć guard limitu, zmienić aktora na A i usunąć inkrementację. Każda zmiana musi dotrzeć do wygenerowanego modelu i ujawnić oczekiwany błędny wynik. Osobne próby zmiany from/to z tabeli sprawdzają czułość translatora na te pola; są testami odczytu danych, nie nowymi regułami obowiązującego procesu. Dla usuniętego guard dopuszczamy licznik 3 w przestrzeni badania, aby ograniczenie instancji nie ukryło naruszenia. W modelu bazowym wyrocznia musi przejść. Błąd parsera, kompilacji, timeout lub brak narzędzia nie są wykryciem mutanta semantycznego.
5. **REFACTOR i regresja:** uporządkować kod z zachowaniem testów wycinka i odpowiedniej regresji E2; utrwalić komendę, wersje, hashe wejść/narzędzi, wynik, liczbę zbadanych stanów i surowy log. Limit czasu pierwszych uruchomień: 60 s na przypadek, jeden worker; przekroczenie daje wynik nieukończony, nie sukces.
6. **Recenzja wyniku:** osobny R odtwarza model bazowy i mutanty, porównuje regułę YAML z relacją TLA+ i sprawdza, czy testy wykazały wykonanie akcji. Zamknięcie E3.1 nie jest odbiorem całego E3.

Przy badaniu wyłącznie jednej akcji brak następcy może być poprawnym wynikiem odmowy, a nie zakleszczeniem pełnego procesu. Konfiguracja testu ma to rozróżniać jawnie. Testy żywotności i założenia F pozostają w późniejszych przyrostach. L1 używa CTL (`AG EF done`); przed jego realizacją trzeba osobno zaprojektować ocenę osiągalności zakończenia, bez cichego zastąpienia przez inną własność LTL.

## Środowisko: sprawdzone i proponowane

Sprawdzono lokalnie 2026-10-26:

- macOS arm64; systemowe `/usr/bin/java` i `/usr/bin/javac` są dostępne jako polecenia, ale `/usr/libexec/java_home -V` nie znalazło zarejestrowanego środowiska Java.
- Działa `/Applications/PyCharm.app/Contents/jbr/Contents/Home/bin/java -version`: OpenJDK/JBR **21.0.10+7-b1163.110**. Można uruchamiać je przez pełną ścieżkę, bez zmiany globalnego PATH/JAVA_HOME i bez instalacji nowej Javy. Aktualizacja PyCharm może zmienić to środowisko; każdy wynik musi zachować wersję użytego runtime.
- Nie znaleziono komendy tlc/tla2tools w PATH ani JAR narzędzi TLA+ w repozytorium, ~/.local, ~/.cache, /opt/homebrew i /usr/local. To wynik sprawdzenia tych lokalizacji, nie deklaracja przeszukania całego dysku.
- [Oficjalne API najnowszego stabilnego wydania](https://api.github.com/repos/tlaplus/tlaplus/releases/latest) wskazuje **v1.7.4**, prerelease=false. Wybrany plik: `tla2tools.jar`, asset ID 184694200, rozmiar 2 274 532 bajty. Metadane odczytano; pliku nie pobrano i TLC nie uruchomiono.

**Propozycja do zgody środowiskowej:** pobrać wyłącznie [tla2tools.jar v1.7.4](https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar) do ignorowanego `artifacts/tools/tla/1.7.4/`, sprawdzić zgodność z sumą wydawcy i zapisać SHA-256 pobranych bajtów; uruchamiać lokalnie przez istniejącą Javę PyCharm. Bez Toolbox GUI, instalatora systemowego i zmian globalnej konfiguracji. Nie przenosić później wersji automatycznie. Metadane GitHub nie podają SHA-256 (digest=null); [strona wydania](https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4) publikuje SHA-1 `bee4a54f3ee3d4afc347c3240ec2d9e93b075104`. Kontrola zgodności i przypięcie pobranych bajtów nie są niezależną weryfikacją dostawcy. Niezgodność sumy lub wersji zatrzymuje użycie pliku.

Po zgodzie najpierw test uruchomienia SANY/TLC oraz mały model poprawny i celowo naruszający niezmiennik. To kontrola narzędzia i rozpoznawania wyniku, przed testami właściwego generatora. Dokumentacja [uruchomienia narzędzi](https://github.com/tlaplus/tlaplus/blob/master/USE.md) opisuje użycie JAR z Java; faktyczną zgodność wybranej wersji z lokalnym runtime sprawdzimy wykonaniem.

## Decyzje agenta i następny krok

- E3-DA01, 2026-10-26: T03 jako pierwszy lokalny przypadek, bo pozwala sprawdzić rolę, stan, granicę i skutek bez udawania dowodu pełnego procesu.
- E3-DA02, 2026-10-26: użycie istniejącej Javy i przypiętego stabilnego JAR projektu, bo ogranicza zmianę środowiska; pobranie wymaga zgody według PLAN, tabela „Narzędzia”.
- E3-DA03, 2026-10-26: niezależna wyrocznia plus porównanie z interpreterem, bo sama zgodność dwóch implementacji może powielać wspólny błąd.
- Właściciel A: przygotowanie i recenzja specyfikacji przyrostu, następnie wykonanie TDD po udostępnieniu narzędzia. Właściciel U: zgoda na opisane pobranie i lokalne uruchamianie TLC. Nie wymaga się ponownej akceptacji istniejącego T03 ani ogólnej zgody na E3.

Raport niezależnego przeglądu przygotowania: [E3-01-PRZYGOTOWANIE](reviews/E3-01-PRZYGOTOWANIE-2026-10-26.md). Nie jest raportem wykonania przyrostu.
