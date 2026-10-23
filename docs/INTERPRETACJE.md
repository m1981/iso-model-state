# Rejestr interpretacji normy

Gdzie ISO/IEC 29110-5-1-2 jest niejednoznaczna lub sama sobie przeczy, tutaj zapisujemy jedno rozstrzygnięcie. Każde INT jest propozycją agenta do bramki E1; po akceptacji wskazuje DEC. Odwołania do normy według jej numeracji; tekst normy streszczony, nie cytowany.

| ID | Problem w normie | Rozstrzygnięcie | Gdzie w modelu |
|---|---|---|---|
| INT-001 | Tabela 12 definiuje znaczenie stanów, ale nie przejścia między nimi ani aktorów. | Siedem stanów elementu (nazwy angielskie, możliwie wprost z Tabeli 12), przejścia T00–T13 z aktorem i warunkiem. Każdy stan wskazuje stany Tabeli 12, które obejmuje. | `item_states`, `item_transitions` |
| INT-002 | Listy „applicable states” produktów (Tabele 13–35) przeczą stanom używanym w tabelach zadań, np. Project plan: accepted wobec approved; Requirements specification bez approved. | Obowiązują stany modelu; słowa normy „approved”, „validated”, „accepted” i „reviewed” mapujemy na `approved`. | `item_states.approved.iso` |
| INT-003 | Stan „signed” (Acceptance record, Tabela 13) nie jest zdefiniowany w Tabeli 12; zadanie PM.04.01 używa „approved”. | Podpis = przejście W04 z cytatem użytkownika; stan wydania `accepted`. | W04 |
| INT-004 | „Published” i „Evaluated” używane dla zapisów (meeting, verification, validation record, progress status record) to nie etapy dojrzałości produktu, tylko fakt zapisu. | Zapisy nie mają własnego automatu; są skutkami przejść (DEC, wpis Przejrzane, protokół odbioru). | `effects`, `evidence` |
| INT-005 | SI.03.08 wymaga Requirements specification [validated], którego żadne zadanie nie wytwarza (SI.02.05 daje [approved]). | Walidacja = zatwierdzenie przez użytkownika (T02). Wejście SI.03.08 to `approved`. | T02 |
| INT-006 | „Tested”, „unit tested” (Tabele 26–27) nie występują w Tabeli 12. | Dla CODE `verified` oznacza: testy przechodzą. | `item_types.CODE` |
| INT-007 | Weryfikacja i walidacja w zadaniach mieszają role (np. PM.01.13 opisuje walidację, ale zapis nazywa weryfikacją). | Weryfikacja wobec specyfikacji: agent (T01) i recenzent (W02). Walidacja wobec zamiaru: użytkownik (T02, W04). | T01, T02, W02, W04 |
| INT-008 | Change request: „accepted” (Tabela 15) wobec „approved or rejected” (PM.02.03); brak opisu, co dzieje się z elementami zależnymi. | Wniosek o zmianę = pytanie Q; rozstrzygnięcie P02. Zmiana elementu: T05/T07/T08 z oznaczeniem zależnych jako podejrzane. | P00–P05, T05–T08 |
| INT-009 | Norma zakłada osobne osoby: klient i kierownik projektu (np. negocjacja zmiany między nimi w PM.02.05). | Jedna osoba (U). Zatwierdzenia klienta i kierownika to jedno przejście U. | `actors.U` |
| INT-010 | „Popraw, aż zatwierdzi” (SI.02.04, SI.02.05 i inne) nie określa reakcji na odpowiedź niejednoznaczną ani liczby iteracji. | Odpowiedź niejednoznaczna nie tworzy DEC (P03); liczba odrzuceń ograniczona (INT-011). | P03, T03 |
| INT-011 | Brak limitu pętli poprawek. | Najwyżej `MAX_REJECTIONS` odrzuceń jednej wersji; potem tylko zatwierdzenie, odłożenie, zastąpienie albo wycofanie. | T03, L4 |
| INT-012 | Norma każe aktualizować rekord powiązań (SI.03.04, SI.04.06), ale nie mówi, co dzieje się z elementami zależnymi po zmianie. | Flaga `suspect` (jak „suspect links” w narzędziach zarządzania wymaganiami); blokuje weryfikację, zatwierdzenie, linię bazową i wydanie do czasu przeglądu. | T05–T08, T11–T13, S5–S7 |
| INT-013 | Norma wymaga zatwierdzenia projektu przez projektanta (SI.03.05), nie przez klienta. | DES i CODE nie wymagają zatwierdzenia użytkownika; są decyzjami agenta, które użytkownik może podważyć (T06) i odbiera razem z wydaniem. | `item_types`, T06 |
| INT-014 | Niezależność weryfikacji (SI.O7, uwaga 2) bez wskazania, kto i kiedy. | Recenzent R: osobny przebieg agenta przed odbiorem każdego wydania. | `actors.R`, W02–W03 |
| INT-015 | Numeracja produktów w Aneksie D (WP.07SM, WP.09SM, WP.12SM, WP.15SM) nie zgadza się z rozdziałem 9; Aneksy B i C mają własne, sprzeczne schematy (WP.CXX wobec WP.T01, WP.D.01 w Aneksie C). | Obowiązuje numeracja rozdziału 9 (WP.01–WP.23); aneksy przy decyzji o nich w karcie projektu. | `item_types.iso_wp` |
| INT-016 | Błędne odsyłacze: PM.01.01 → „Clause 6” (powinno 5.2); PM.02.02 → PM.02.04 (powinno PM.02.05). | Odwołujemy się do treści, nie do błędnego odsyłacza. | — |
