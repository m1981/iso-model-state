# Runda 4 — przygotowana, niewysłana

Wstrzymana po kontroli limitu 5h. Brak odpowiedzi rozmówcy; poniższe korekty są stanowiskiem prowadzącego, nie uzgodnionym wynikiem rundy.

RUNDA 4 — końcowe korekty i maksymalnie trzy rekomendacje do sprawdzenia.
Dziękuję za wycofanie wniosków o całym DoD, rytualności punktu wznowienia i zmianie definicji @confirmed. Źródła potwierdzają: @confirmed oznacza potwierdzoną potrzebę, nie przejście testu (ACCEPTANCE.feature w 5744bc0); czerwony wynik 1 failed, 642 passed, AT061–063; commit fa90b77 wprost deklaruje te braki; foldery dodaje c49f161 po pytaniu użytkownika. Kolejność H48: wiadomość 1423ea2d… przyznaje już wykonane odstępstwo i pyta, 2f75a780… odpowiada „d1 dziala cudnie”, DEC122 zapisuje zmianę.
Korekty Twojego mapowania:
- checks_ok elementu i tests_ok wydania to RÓŻNE wejścia. Samo checks_ok=false nie dowodzi blokady W01 przez tests_ok. Trzeba określić zakres kontroli i wierne mapowanie wyniku, nie dopisywać automatycznej konwersji.
- Nie wolno rozbić rzeczywiście jednocześnie zadanych D1/D2/D3 na fikcyjne sekwencyjne P01/P02, aby dopasować historię do S9. Zachowujemy historię; niezgodność konwencji wymaga uczciwego raportu i ewentualnej osobnej decyzji, nie obejścia.
- T11 to udokumentowane usunięcie suspect po spełnieniu warunków, nie ogólna zgoda na dowolną zmianę DES/CODE. T05 może wymagać zgody także na bazowy DES/CODE; T06 nie zastępuje T05. Sama etykieta refaktoryzacji nie zwalnia z obowiązujących bramek.
- Odwołanie REQ037→H48 nie jest z definicji nieaktualne po DEC122: trzeba sprawdzić wersję/treść referenta i regułę pierwszeństwa. Nie udowodniliśmy pełnego naruszenia spójności. Nie każde znaczenie potrzebuje nowego ID — wersja pod tym samym ID jest normalna.
- Nie każda niedokładnie mapowalna akceptacja daje S1. Zgoda użytkownika może obejmować konkretny pakiet; ustalenie jej zakresu to praca na źródłach. Brak osobnego podpisu pod każdym scenariuszem nie dowodzi jego braku.

Dopiero teraz porównanie z pierwszą sesją (wcześniejsza gałąź, do Q051): podobne osie pytań; konkretne wyniki to odmowa D1, pozytywna zgoda kontekstowa na zmianę REQ017 (rozmówca błędnie zarzucił brak zgody, wycofał po źródłach), pytanie „co to za kroki5–9”, test przewijania zielony przed poprawką, poprawione asercje potem rzeczywiście czerwone. Wnioski prowadzącego: sprawdzić odczyt zgód, samowystarczalny następny krok oraz wiarygodne dowody testowe. To nie wyniki wykonanych eksperymentów i nie dowód przyczynowej przewagi procesu. Sesje tego samego projektu nie są niezależnymi replikacjami.

ZADANIA:
1. Jawnie przyjmij lub uzasadnij odrzucenie powyższych korekt; wycofaj niepodparte diagnozy naruszeń modelu.
2. Zaproponuj MAKSYMALNIE 3 małe eksperymenty o najwyższej wartości: dla każdego hipoteza, konkretne dane z sesji, wariant kontrolny, wynik obalający, koszt do ZMIERZENIA i granica wniosku. Uwzględnij nowe dane: brak przygotowanego folderu demo, czerwona kontrola bez egzekucji, ryzykowna powłoka. Nie odtwarzaj niebezpiecznych poleceń; ewentualna próba wykonawcy tylko na syntetycznych ścieżkach bez realnych mutacji. Nie zmieniaj zakresu E2–E5 i nie ogłaszaj wykonania eksperymentu.
3. Co druga sesja potwierdza, co dodaje, a czego nadal nie rozstrzyga względem pierwszej? Jakie reguły należy zachować zamiast zwiększać biurokrację?
4. Jedno zdanie najsilniejszego falsyfikowalnego zarzutu wobec naszej propozycji i jedno praktyczne zalecenie dla operatora+agenta.
Do około 1000 słów; bez pochwał na zamówienie, bez ponownego opisu całej historii.
