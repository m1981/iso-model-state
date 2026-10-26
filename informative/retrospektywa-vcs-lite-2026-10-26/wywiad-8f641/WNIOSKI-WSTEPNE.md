# Ustalenia po trzech rundach — wywiad nieukończony

2026-10-26. Materiał informacyjny prowadzącego iso-model-state. To weryfikacja relacji uczestnika i wstępne porównanie, nie końcowy wynik wywiadu ani formalne odtworzenie historii E4.

**Druga sesja dostarczyła nowych przykładów rozbieżności między zapisaną zasadą a wykonaniem. Nie dowiodła przewagi naszego modelu.** Czwarta runda z korektami i projektami eksperymentów pozostaje niewysłana: kontrola `/usage` wykazała 100% wykorzystania okna 5h. Nie wolno przedstawiać jej pytań jako odpowiedzi ani uzgodnionych rekomendacji.

## Materiał i ograniczenia

Zrealizowano rekonstrukcję doświadczeń, próbę podważenia relacji oraz recenzję naszego modelu: [runda 1](RUNDA-1.md), [runda 2](RUNDA-2.md), [runda 3](RUNDA-3.md). Pierwsze pytanie jest identyczne z pierwszym wywiadem; dalsze pytania zachowują te same osie, lecz odnoszą się do innych epizodów. Model pokazano dopiero w trzeciej rundzie. Wyników pierwszego wywiadu jeszcze nie przekazano rozmówcy — są w [niewysłanej rundzie 4](RUNDA-4-PYTANIE.md).

Rozmowa odbywa się wyłącznie w odgałęzieniu `3407bcbe-95ac-493e-bae1-d257b62e3f85`. Hash źródłowej sesji jest niezmieniony; [PROWENIENCJA.json](PROWENIENCJA.json) zawiera konfigurację bez narzędzi/MCP oraz hashe pytań i odpowiedzi. Pełne źródło i surowe odpowiedzi pozostają lokalnie w ignorowanym artifacts, bez publikowania ukrytego rozumowania.

Rozmówca zna wcześniejszą część pracy poprzez kompakcję, a późniejszą poprzez historię po niej. Prowadzący sprawdził osobno 14 zapisów wiadomości/wyników, pięć commitów i trzy historyczne wersje dokumentów: [DOWODY.json](DOWODY.json). S05 jest zapisem wiadomości użytkownika dostarczonej w toku pracy, w rekordzie `api-request-blob` bez własnego UUID i czasu; identyfikuje go linia oraz hash źródła. S01 poprzedza kompakcję. Zapis wyników testów nie jest ich ponownym wykonaniem. Nie odtwarzano niebezpiecznego polecenia ani działania GUI.

## Co potwierdzono

| Zdarzenie | Dowód | Znaczenie i granica |
|---|---|---|
| Użytkownik jednocześnie zgodził się na D1, odmówił D2 i usunął menu z propozycji | S02 | Samo „tak” nie wystarcza do ustalenia zakresu. Potrzebne są propozycja, pełna odpowiedź i późniejsze doprecyzowanie. Nie wykonano mapowania na zdarzenia modelu. |
| Agent zaimplementował datę w szczegółach zamiast podpowiedzi H48, następnie zapytał i otrzymał akceptację | S03–S04, DEC-VCS-122 | Kolejność wykonanie → pytanie jest potwierdzona. Nie utożsamiamy jej automatycznie z naruszeniem S11: potrzebne jest ustalenie modelowych produktów, stanów i wersji. |
| Użytkownik ustanowił commitowanie po logicznym przyroście | S05–S07, instrukcja w `5744bc0` | To istotna stała instrukcja, którą punkt wznowienia powinien zachować. Commit nie jest odbiorem wydania. |
| Kontrola wykryła brak testów AT-061–063, a następnie powstał commit `fa90b77` | S08–S10, treść commita | Wykrywanie nie oznacza egzekwowania bramki. Commit jawnie przyznaje brak testów kolejnej funkcji. Nie dowodzi to wydania niepoprawnego produktu ani obowiązku blokowania każdego pośredniego commita. |
| Użytkownik nie znalazł folderu do próby; później poprawiono generator demo | S11, `c49f161` | Instrukcja próby musi mieć spełnione warunki wejściowe. Samo wskazanie numeru testu tego nie zapewnia. |
| Po odesłaniu do kroków 18 i 19 użytkownik zapytał o ich znaczenie | S12–S14 | Powtórzenie problemu samowystarczalności instrukcji z pierwszej sesji. Nie jest to pomiar częstości ani przyczyn. |
| Historyczne polecenie testowania indeksu próbowało zapisywać pliki pod `/` | S06 | Wynik pokazuje odmowy zapisu. Nie dowodzi braku wszystkich skutków ubocznych; nie przeprowadzono audytu całego systemu. To problem wykonawcy, którego abstrakcyjny model produktów nie kontroluje. |

## Co trzeba skorygować w relacji

Rozmówca w rundzie 3 wycofał trzy zbyt dalekie wnioski: DEC096 nie dowodzi spełnienia całego DoD; brak odczytu punktu wznowienia w tej samej sesji nie dowodzi jego zbędności; zmiana chwili nadawania `@confirmed` nie dowodzi zmiany definicji znacznika. Historyczna definicja mówi o potwierdzonej potrzebie, a nie przejściu testu.

Pozostają korekty prowadzącego, **jeszcze nieprzedstawione rozmówcy**:

- `checks_ok` elementu i `tests_ok` wydania to różne wejścia. Czerwona kontrola nie jest sama przez się dowodem określonej blokady W01 bez ustalenia mapowania.
- Nie wolno zmieniać jednocześnie zadanych D1/D2/D3 w fikcyjną sekwencję, aby dopasować historię do S9. Niezgodność konwencji należy ujawnić.
- T11 usuwa `suspect` przy spełnieniu warunków, nie upoważnia do dowolnej zmiany. Refaktoryzacja nie zwalnia automatycznie z T05 na produkcie bazowym; T06 nie zastępuje zgody na T05.
- Odwołanie REQ037 do H48 nie jest automatycznie nieaktualne po DEC122. Trzeba sprawdzić treść, wersje i pierwszeństwo dokumentów. Nie wykazano pełnej sprzeczności.
- Brak osobnego podpisu pod każdym scenariuszem nie dowodzi braku zgody na pakiet. Nie wolno przypisać S1 wyłącznie na tej podstawie.

## Wstępne porównanie z pierwszym wywiadem

| Oś | Pierwsza sesja | Kontynuująca sesja | Wniosek prowadzącego |
|---|---|---|---|
| Zgoda i jej kontekst | Odmowa oraz prawidłowa zgoda na zmianę REQ017; błędny zarzut rozmówcy obalony | Mieszana odpowiedź D1/D2, odstępstwo H48, nowa stała instrukcja commitowania | Korpus do badania musi zawierać zgody, odmowy i poprawne upoważnienia; alarmowanie wszystkiego nie jest sukcesem. |
| Następny krok | „Co to za kroki 5–9” | „Co to są kroki 18 i 19” oraz brak folderu demo | Do projektu R2 warto włączyć sprawdzenie warunków wykonania instrukcji, nie tylko jej czytelności. |
| Dowody i wykonanie | Test zielony przed poprawką, potem poprawiona asercja | Czerwona kontrola bez blokady commita oraz wadliwa procedura powłoki | Trafność testu, zakres jego wyniku i egzekwowanie konkretnej bramki są odrębnymi zagadnieniami. |
| Ograniczenia wywiadu | Relacja wcześniejszej gałęzi, błędna samoocena zgody | Kompakcja i nadmierne wnioski o DoD | Samoocena agenta wymaga źródeł, także gdy jest samokrytyczna. |

To dwie części tego samego projektu, nie niezależne replikacje eksperymentu. Nie zmierzono czasu zaoszczędzonego, narzutu, przewagi automatu ani zasadności MAX_REJECTIONS=2. Dotychczasowe R1–R3 z [pierwszego wywiadu](../wywiad-e5a1/WNIOSKI.md) pozostają projektami sprawdzeń. Nie dodano nowych bramek i nie zmieniono modelu v0.7 ani kolejności E2–E5.

## Punkt wznowienia

Właściciel: agent iso-model-state. Po odzyskaniu dostępności najpierw ponownie odczytać `/usage`, potem wznowić wyłącznie fork i wysłać gotową rundę 4. Zakończyć weryfikację, porównanie i najwyżej trzy projekty eksperymentów. Do tego czasu wynik jest wstępny, E2 nadal czeka na osobną decyzję użytkownika. Szczegóły ograniczenia i odgałęzienia: [STATUS.md](STATUS.md).
