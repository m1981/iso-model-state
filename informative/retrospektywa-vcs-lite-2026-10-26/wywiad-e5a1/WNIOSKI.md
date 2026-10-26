# Wnioski z rozmowy o współpracy w vcs_lite

Data: 2026-10-26. Materiał informacyjny. Autor syntezy i weryfikacji: agent prowadzący iso-model-state. Rozmówca: Claude wznowiony z sesji wskazanej przez użytkownika.

**Najważniejszy wniosek:** doświadczenia vcs_lite uzasadniają sprawdzenie trzech rzeczy na granicy między rozmową a modelem: wiernego odczytania zgody, zrozumiałego następnego kroku i wiarygodności dowodów testowych. Wywiad nie dostarczył podstaw do dodawania kolejnych bramek ani zmiany przyjętych reguł v0.7. Pokazał też, że krytyczna wypowiedź autora może być błędna: zarzut „cichej zmiany” REQ-VCS-017 został obalony przez propozycję i odpowiedź użytkownika.

## Zakres rozmowy i źródła

Użytkownik wskazał sesję `e5a1e620-442a-4613-9606-6bffe6dfbe04`. Wywiad przeprowadzono na jej odgałęzieniu `d412a546-fc3a-4db6-90bb-237cda269c8b`, bez narzędzi wykonawczych i MCP. Pięć etapów uzgodnionego planu zrealizowano w czterech wymianach: pierwsza łączyła rekonstrukcję i mechanizmy; następne obejmowały próbę podważenia, recenzję naszego modelu oraz korekty i rekomendacje. Cel i szczegóły iso-model-state pokazano dopiero w trzeciej wymianie.

Wznowienie wybrało wcześniejszą gałąź historii, kończącą pracę projektową na propozycji diffu Markdown Q-VCS-051. Zweryfikowano to przez łańcuch `parentUuid`: zawiera tę propozycję, lecz nie późniejszą retrospektywę i prompt wznowienia. Rozmówca znał więc węższy zakres niż cały plik JSONL. Dokument PLAN.md w katalogu nadrzędnym wymienia inną sesję (`26cc4e83-…`); pozostawiono go bez zmian. Ten zapis dotyczy wyłącznie sesji wskazanej w bieżącym poleceniu.

Rozmówca jest uczestnikiem oceniającym własną pracę, nie niezależnym audytorem. Prowadzący osobno sprawdził 14 wiadomości i wyników narzędzi, cztery commity oraz historyczną konwencję współpracy. Nie odtwarzano działania vcs_lite ani jego testów; wyniki historycznych uruchomień są zapisami z sesji. Nie oceniano treści zrzutów na nowo. Nie wykonano formalnego E4 ani nowych eksperymentów użytkowych.

- [Rozmowa 1 — doświadczenia i mechanizmy](RUNDA-1.md)
- [Rozmowa 2 — granice relacji i próby podważenia](RUNDA-2.md)
- [Rozmowa 3 — recenzja naszego modelu](RUNDA-3.md)
- [Rozmowa 4 — korekty i rekomendacje](RUNDA-4.md)
- [Dowody źródłowe](DOWODY.json): identyfikatory S01–S14, dokładne cytaty, UUID, czas UTC, pozycja w lokalnym JSONL i hashe commitów.
- [Pochodzenie zapisu](PROWENIENCJA.json): sesje, model rozmówcy, konfiguracja narzędzi i hashe pytań oraz odpowiedzi. Pełnej historii źródłowej ani ukrytego rozumowania nie skopiowano do dostawy.

## Co pomagało i co przeszkadzało

| Mechanizm używany w vcs_lite | Potwierdzone użycie lub zdarzenie | Korzyść i granica wniosku |
|---|---|---|
| Dokumenty zamiaru i ograniczona lista spraw wymagających decyzji | Historyczne WSPOLPRACA.md w `fdc5da9` oddziela decyzje operatora od szczegółów rozstrzyganych przez agenta; nakazuje utrzymać punkt wznowienia | Daje podstawę samodzielności. Sam zapis nie dowodzi przestrzegania ani niższego kosztu pracy. |
| Konkretna propozycja i krótka odpowiedź użytkownika | Odmowa w S03; propozycja rozszerzenia REQ-VCS-017, zgoda zbiorcza i wykonanie w S04–S06 | Zgoda staje się czytelna razem z propozycją. Sam cytat „D1 tak” bez kontekstu jest za słaby do ustalenia zakresu. |
| Jeden temat i rejestr spraw otwartych | Użytkownik zażądał obu zasad, S01–S02; później nadal pytał „Co to za kroki 5-9”, S10 | Zwięzłość nie zastępuje samowystarczalnej instrukcji. Nie zmierzono poprawy komunikacji po zmianie zasad. |
| Test przed poprawką i kontrola przyczyny niepowodzenia | Test krótkiej listy początkowo przechodził; autor poprawił asercje, S07. Narzędzie pokazuje najpierw pass, potem `assert 10.0 == 0`, S08–S09 | W tym epizodzie sprawdzenie testu ujawniło jego słabość. Nie dowodzi jakości wszystkich testów ani skuteczności samej procedury TDD. |
| Automatyczne śledzenie powiązań | W S11 zgłoszono brak testu AT-VCS-038; kod test_traceability sprawdza ID, odwołania i obecność testów | Chroni strukturę dokumentów i kodu. Nie ocenia, czy treść wymagania oddaje zamiar użytkownika. |
| Weryfikacja zachowania przez operatora | S10 łączy „gitignore perfect” z pytaniem o dalsze kroki; merge doprowadził do DEC-VCS-065 i commitu `243ba6e` | Użytkownik oceniał działanie, a także korygował proces. Nie wolno całej korzyści przypisać automatom i testom. |
| Logi testów i badanie stanu przeznaczonego do commita | S12 opisuje testy poszczególnych commitów oraz utratę szczegółów błędu przez filtrowanie wyjścia; `767cbf0` rzeczywiście łączy kilka funkcji | Zapis dowodu ma znaczenie. Niezweryfikowana przyczyna niestabilności pozostaje niewiadomą, a deklaracja „zignoruj” w S13 nie wyjaśnia błędu. |

Relacja agenta o użyteczności makiet, przykładów i szybkich odpowiedzi operatora jest wiarygodnym kierunkiem dalszego badania, lecz nie pomiarem przewagi tej metody. Mała skala, wcześniejsza specyfikacja i aktywny użytkownik są alternatywnymi wyjaśnieniami sprawnego przebiegu.

## Co skorygowano podczas wywiadu

| Twierdzenie rozmówcy | Wynik sprawdzenia |
|---|---|
| Widzi „pełną historię” | Zawężone do wznowionej gałęzi. Późniejsze wpisy istnieją w pliku, ale nie są jej przodkami. Nie traktujemy nieobecnych zdarzeń jako zapomnienia agenta. |
| REQ-VCS-017 zmieniono po zgodzie wyłącznie na etapy, bez wcześniejszej zapowiedzi zmiany wymagania | **Obalone.** S04 wprost zapowiada zmianę tego wymagania przed zgodą S05. Rozmówca wycofał zarzut. To przypadek poprawnej zgody kontekstowej, który przyszły adapter powinien zachować. |
| „Nikt nie przejrzał zależnych” | Nieudowodnione. Rozmówca wskazał brak znanego mu zapisu; nie przeprowadzono pełnego audytu wszystkich zależności. |
| Każda późniejsza zmiana zależnego kodu bez nowej zgody narusza S11 | **Wycofane jako zbyt szerokie.** S11 dotyczy T05/T07; potrzebne jest uzasadnione mapowanie konkretnej zmiany na element i operację. |
| Pewnych interakcji Tk „nie da się” testować automatycznie | Zawężone do braku pokrycia w ówczesnym zestawie. Rozmówca nie sprawdził wszystkich alternatywnych metod. |

Nie potwierdzono naruszenia przy nadaniu statusu REQ-VCS-030. Pozostaje pytanie, czy wszystkie szczegóły mieściły się w zaakceptowanej propozycji. Nie uznajemy braku osobnego podpisu pod każdym późniejszym zdaniem za automatyczny dowód braku upoważnienia.

## Ocena naszego modelu

Najmocniejszy argument za modelem: pozwala jawnie oddzielić zgodę na określoną zmianę od wykonania oraz wymusić przegląd jej zależności. Zwykłe sprawdzenie istniejących ID nie opisuje historii zgód i wersji. To potencjalna przewaga do zmierzenia, nie już udowodniona korzyść użytkowa.

Najmocniejszy zarzut: model otrzymuje zdarzenia i wyniki z zewnątrz. Może poprawnie sprawdzić błędnie odczytaną zgodę lub bezwartościowy zielony wynik. Sytuacje te nie są nowo odkrytym błędem automatu: granice są już jawne w modelu i karcie celu. Wymagają dobrego sposobu pozyskania danych oraz zrozumiałego raportu.

Odpowiedzi zbiorcze stanowią osobną kwestię mapowania na S9. **Nie wolno zapisać historycznych D1/D2 jako sekwencji pojedynczych pytań tylko po to, żeby uzyskać zielony wynik.** Trzeba zachować treść i kolejność rzeczywistych zdarzeń, ustalić znaczenie modelowego pytania, a ewentualną zmianę reguły przedstawić użytkownikowi. Ta sesja nie rozstrzyga też zasadności MAX_REJECTIONS=2 ani optymalnej wielkości modelowego elementu TEST.

## Trzy rekomendowane sprawdzenia

Poniższe projekty są syntezą prowadzącego po krytycznej ocenie propozycji rozmówcy. Nie zostały wykonane; nie zmieniają planu E2–E5 ani przyjętych reguł. Porównania wymagają tych samych danych wejściowych dla obu wariantów. Nie traktujemy niepodpartego pomiarem szacunku „około godziny” jako ustalonego kosztu.

### R1 Zgoda zachowuje swój kontekst

**Cel:** agent nie myli odmowy ze zgodą i nie pyta ponownie o działanie już zatwierdzone.

Zestaw kontrolny: propozycja i odmowa z DEC-VCS-070; S04–S06 ze zgodą zbiorczą; wyraźna zgoda, odpowiedź niejednoznaczna i odpowiedź odnosząca się do wcześniejszej wersji propozycji. Dodatkowe warianty celowo zmienione oznaczyć jako syntetyczne. Wzorzec wskazuje wynik decyzji, zakres, operację, wersję jeśli można ją ustalić i źródło; nieznanej wersji nie dopisywać z domysłu.

Porównać A: odczyt z dokumentów i pełnych par propozycja–odpowiedź; B: ten sam materiał z ustrukturyzowanym powiązaniem do zdarzeń modelu. Oceniać na nieużytych wcześniej wariantach. Prowadzący przygotowuje wzorzec; do użytkownika trafiają tylko rzeczywiste niejednoznaczności zamiaru.

Miary: fałszywe zgody, przeoczone odmowy, błędny zakres, niepotrzebne ponowne pytania, poprawnie zgłoszone niewiadome i koszt przygotowania. Na kontrolnym zestawie wymagamy zera fałszywych zgód; choć jeden przypadek oznacza niegotowość wariantu B. Brak poprawy względem A podważa korzyść dodanej warstwy. Ewentualna zmiana S9 lub polityki zatwierdzania wymaga decyzji użytkownika.

### R2 Wznowienie jest zrozumiałe dla człowieka i nowego agenta

**Cel:** po przerwie wiadomo co obowiązuje, co jest otwarte, kto działa i co konkretnie ma zrobić.

Na kilku zamrożonych punktach historii przygotować A: dotychczasowy zapis wznowienia; B: krótki zapis zawierający cel, stan, decyzje, otwarte sprawy z właścicielami i samowystarczalny pierwszy krok. Oba warianty muszą zawierać te same fakty. Wybrać punkty, dla których dokumenty i rzeczywisty stan da się zweryfikować; sam commit kodu nie wystarcza do odtworzenia stanu rozmowy.

Świeże przebiegi agenta bez historii odpowiadają na te same pytania. Osobno sprawdzić z użytkownikiem, czy instrukcja pozwala rozpocząć działanie bez pytania „co to za kroki?”. W porównaniu z jednym użytkownikiem użyć różnych, porównywalnych punktów i zmiennej kolejności, żeby ograniczyć efekt zapamiętania.

Miary: pominięte lub błędne obowiązujące decyzje, trafność następnego kroku, liczba doprecyzowań, czas odczytu i koszt utrzymania zapisu. Jeśli B nie poprawia trafności ani zrozumiałości albo zwiększa narzut bez korzyści, hipoteza przewagi nie jest potwierdzona. To badanie komunikacji i kryterium z karty celu; nie wymaga dodania stanów do modelu.

### R3 Wynik testu ma sprawdzalne pochodzenie

**Cel:** nie utożsamiać „test przeszedł” z dowodem, że sprawdza potrzebne zachowanie.

Dla epizodu krótkiej listy zestawić wadliwy test, poprawiony test, kod z błędem i poprawkę. Punktem wyjścia są S07–S09 i commit `b458136`. Jeśli wersji roboczego testu nie da się wiernie odtworzyć z zapisanych zmian, zaznaczyć rekonstrukcję zamiast przedstawiać ją jako oryginał. Dodać kontrolę pozytywną oraz test poprawnej zmiany porządkowej, który ma prawo przechodzić przed zmianą.

Porównać A: sam wynik pass/fail; B: wynik z identyfikacją kodu, testu, polecenia, pełnego logu i oceną przyczyny niepowodzenia. **Nie ustanawiać uniwersalnej zasady „każdy test musi oblać na rodzicu przez AssertionError”.** Brak nowego interfejsu może być prawidłową przyczyną niepowodzenia testu nowej funkcji, a zmiana porządkowa nie musi zmieniać wyniku. Niepowodzenie asercji samo w sobie również nie dowodzi trafności testu.

Miary: wykryte bezwartościowe sprawdzenia, fałszywe alarmy wobec poprawnych testów, odróżnienie błędu środowiska od zachowania i koszt oceny. Akceptacja wadliwego testu jako dowodu albo brak korzyści przy dodatkowych fałszywych alarmach podważa wariant B. To warstwa dowodowa. Zmiana znaczenia tests_ok albo dopuszczenie wyjątku dla niestabilnego testu wymagałoby osobnej decyzji; wywiad jej nie udziela.

## Co pozostaje bez rozstrzygnięcia

Nie zmierzono kosztu procesu ani czasu zaoszczędzonego przez reguły. Nie udowodniono przewagi automatu nad prostszym dziennikiem zdarzeń z kontrolą powiązań. Ta gałąź nie obejmuje DEC-VCS-096 ani DEC-VCS-102, więc nie zastępuje zaplanowanych przypadków E4. Opinie o bramkach, limitach odrzuceń i szczegółowości TEST są pytaniami do badania, nie podstawą do ich zmiany.

Odbiór E2 nadal należy do użytkownika. Wnioski można wykorzystać przy przygotowaniu danych i kryteriów E4/E5; ich wcześniejsze wykonanie wymagałoby jawnego uzgodnienia kolejności. Właściciel dalszego przygotowania: agent iso-model-state. Następny krok po odpowiednich bramkach: przygotować zestaw kontrolny R1 z zachowaniem oryginalnych propozycji i odpowiedzi, zanim powstanie adapter.
