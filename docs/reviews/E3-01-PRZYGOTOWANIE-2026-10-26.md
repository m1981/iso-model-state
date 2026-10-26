# Niezależny przegląd przygotowania E3.1 — 2026-10-26

**Wniosek: brak otwartych ustaleń blokujących przedstawienie przygotowania E3.1 i propozycji narzędzia użytkownikowi.** Zakres jest właściwy dla pierwszego testu translacji jednej reguły. Zgłoszoną lukę czułości na pola `from` i `to` zamknięto w specyfikacji podczas przeglądu. To ocena planu; nie potwierdza wykonania przyrostu, gotowości generatora ani spełnienia S/L. Recenzent nie odbiera E3.1 lub E3 za użytkownika.

## Przedmiot i niezależność

Osobny przebieg recenzenta oceniał dokument na podstawie instrukcji repozytorium i dokumentów zamiaru, bez historii tworzenia propozycji. Przeczytano `PROMPT-STARTOWY.md`, `WSPOLPRACA.md`, `STAN.md`, kartę celu, `PLAN.md`, model v0.7, właściwości, interpretacje i regułę pierwszeństwa `informative/`. Pomocniczo sprawdzono wykonanie kroku i granice istniejącego interpretera oraz wcześniejszy raport E2. Końcowy dokument odczytano ponownie po korekcie autora.

- Oceniany plik: [E3-PRZYROST-01.md](../E3-PRZYROST-01.md).
- SHA-256 jego bajtów: `cd75b740d9f400179507efd6961d093dd8224e357fba67295de16789e459944a`.
- Podstawa semantyczna: `model/process.yaml`, v0.7 / DEC-PRO-010; SHA-256 bajtów pliku: `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07`. To hash pliku, nie kanonicznych danych modelu stosowany w raportach E2.
- DEC-PRO-012 i bieżące dokumenty stanu zapisują odbiór E2 oraz przygotowanie E3. Recenzja nie ustanawia tej decyzji ani nie powtarza audytu E2.

Recenzent utworzył wyłącznie niniejszy raport. Nie zmieniał modelu, kodu, testów, planu ani rejestru decyzji; nie wykonywał commitu.

## Kryteria i ocena

| Kryterium | Ocena przygotowania |
|---|---|
| Powiązanie z celem użytkowym | Sprawdzenie translacji ogranicza ryzyko obejścia roli U i budżetu odrzuceń wskutek błędu generatora. Jest uzasadnionym krokiem technicznym przed dalszym E3. Nie jest jeszcze pomiarem użyteczności ani kosztu procesu na rzeczywistym projekcie. |
| Zgodność z T03 v0.7 | Dla lokalnej relacji warunek to aktor U, stan verified i licznik poniżej MAX_REJECTIONS. Skutek to draft i inkrementacja dokładnie o 1. Pozostałe pola objęte rzutem mają pozostać identyczne. Nie dodano resetu wersji ani licznika z T10. |
| Jeden model jako źródło | Kontrakt wymaga odczytu `from/to/actor/guard/effects` i parametru, a ID służy wyborowi. Zmiana ID oraz kontrolowane zmiany danych mają sprawdzić ten wymóg. Nieobsługiwana składnia ma zatrzymać generowanie. |
| Niezależność wyroczni | Ręcznie ustalone wyniki są właściwą podstawą. Dodatkowe porównanie z interpreterem pomaga wykrywać rozbieżności, ale nie zastępuje wyroczni i przeglądu translacji. |
| Przypadek poprawny i odmowy | Wartości 0 i 1 sprawdzają dozwoloną inkrementację, 2 sprawdza granicę; aktorzy A/R oraz stany draft/approved sprawdzają istotne odmowy. Jest to wystarczający początek dla tego wycinka, bez deklaracji wyczerpania wszystkich stanów procesu. |
| Mutanty | Usunięcie guard, zmiana aktora na A i usunięcie inkrementacji badają trzy odrębne błędy. Mutant ma rzeczywiście wykonać odmienną relację; błąd narzędzia nie jest wykryciem semantycznym. |
| Granica licznika | Dopuszczenie wartości 3 po usunięciu guard zapobiega ukryciu naruszenia przez dziedzinę stanu. W implementacji nie wolno ponownie narzucić ograniczenia `0..MAX_REJECTIONS` jako warunku odcinającego ten następnik. |
| Dostępność i stutter | Wymagana jest ocena dostępności i całego zbioru następników akcji. Sam brak naruszeń nie wystarczy: relacja stale wyłączona musi oblać przypadki pozytywne. Samopętla stutter nie może zastąpić T03 ani zamaskować jego odmowy. |
| Syntetyczne stany | Dokument jawnie określa je jako stany jednostkowego testu relacji. Nie są świadkami od Init, testem pełnej pętli odrzucania ani historycznym dowodem S15. |
| Granice pełnego E3 | Pozostają S/L, sprawiedliwość, osiągalność, świadkowie i uzasadnienie granic całej instancji. L1 jest jawnie rozpoznane jako CTL `AG EF done`; plan nie zastępuje go własnością LTL. |
| TDD i odtwarzalność | Kolejność RED/GREEN/REFACTOR, zakaz zaliczenia pominiętych testów TLC, surowe logi, hashe, wersje i limity wykonania tworzą właściwy kontrakt przyszłego dowodu. Żaden z tych wyników nie jest obecnie deklarowany jako wykonany. |

## Ustalenie zgłoszone i zamknięte

**R-E3-01 — czułość na `from` i `to`.** Pierwotne przypadki mogły przejść również dla generatora z zaszytym `from=verified` i `to=draft`. Zmiana ID, parametru, aktora, guard i skutku nie sprawdzała odczytu tych dwóch pól, choć dokument obejmował je kontraktem.

Autor dodał dwie odrębne kopie testowe: `from=[approved]` ma dopuścić approved i odmówić verified; `to=deferred` ma wytworzyć deferred z zachowaną inkrementacją i ramą pozostałych pól. Ponowny odczyt potwierdził te oczekiwania i rozróżnienie testu odczytu danych od zmiany obowiązującej reguły. **Ustalenie zamknięte na poziomie przygotowania.** Jego wykonanie pozostaje do wykazania w TDD.

## Co musi zostać skonkretyzowane przed implementacją

To zadania już wskazanego kroku 1, nie dodatkowe wymagania pełnego E3 i nie wykonane dowody:

1. Zapisać dokładny rzut stanu, dziedziny oraz sposób przeniesienia syntetycznej próbki do istniejącego interpretera. Przegląd ma sprawdzić ramę wszystkich pól rzutu, a nie tylko stan i licznik.
2. Nazwać globalne mechanizmy pozostające poza lokalną relacją. W szczególności interpreter odmawia T03 przy `next_release_required=true`; porównanie lokalne wymaga odpowiedniego kontekstu, np. tej flagi ustawionej na false. T03 nie tworzy `newly_suspect`, więc oba obecne obserwatory nie powinny zmieniać wyniku. Tych warunków nie wolno domyślnie przenosić na pełny model.
3. Skonkretyzować odczyt wyników TLC tak, aby sprawdzał rzeczywistą akcję, cały zbiór następników i odmowę; brak następcy przez T03 jest poprawnym wynikiem lokalnym, nie diagnozą zakleszczenia procesu.
4. Dla mutantów zachować bazową wyrocznię reguły i pokazać konkretną rozbieżność. Dla zmian parametru oraz `from/to` użyć osobno zapisanych oczekiwań odpowiadających zmienionym danym. Nie uzyskiwać oczekiwań przez badany translator.

Po konkretyzacji rzut i wyłączenia wymagają przewidzianego w planie przeglądu R przed rozszerzeniem generatora. Niniejsza recenzja nie zatwierdza nieistniejącego jeszcze mapowania.

## Ocena lokalnego narzędzia

Propozycja przypina jeden JAR i używa istniejącego runtime bez globalnej rekonfiguracji. `.gitignore` obejmuje `artifacts/`. Recenzent wykonał wyłącznie odczyt wersji `/Applications/PyCharm.app/Contents/jbr/Contents/Home/bin/java -version`; potwierdzono build `21.0.10+7-b1163.110`.

Odczytana [oficjalna strona v1.7.4](https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4) oznacza wydanie jako Latest i publikuje dla JAR SHA-1 `bee4a54f3ee3d4afc347c3240ec2d9e93b075104`, zgodny z propozycją. [Dokumentacja projektu](https://github.com/tlaplus/tlaplus/blob/master/USE.md) potwierdza uruchamianie SANY/TLC z JAR przez Javę. Nie daje to jeszcze dowodu zgodności konkretnego pliku z lokalnym runtime; plan słusznie wymaga próby poprawnego modelu i celowego naruszenia po uzyskaniu narzędzia.

Recenzent nie pobrał JAR, nie instalował zależności, nie uruchomił SANY/TLC i nie zmieniał środowiska. Nie odtwarzał pełnego poszukiwania JAR w lokalizacjach autora; API GitHub nie było dostępne przez użyte narzędzie przeglądania, więc szczegółowe pola asset ID/rozmiar/digest pozostają zapisem sprawdzenia autora. Kontrola SHA-1 wydawcy i zapis własnego SHA-256 pozwalają sprawdzić zgodność i przypiąć bajty, lecz nie są niezależnym uwierzytelnieniem wydawcy; dokument tego nie obiecuje.

## Granice wyniku

Przeprowadzono przegląd dokumentów, reguły YAML, istotnego kontekstu interpretera oraz propozycji środowiska. Nie uruchamiano testów generatora ani ponownie regresji E2, ponieważ ta dostawa jest przygotowaniem, a model i kod pozostają bez zmian. Nie wykazano jeszcze żadnego kontrprzykładu TLC, liczby zbadanych stanów, osiągalności lub żywotności. Właścicielem wykonania przygotowanych sprawdzeń jest A; decyzja o środowisku i późniejsze odbiory należą do U zgodnie z obowiązującym kontraktem.
