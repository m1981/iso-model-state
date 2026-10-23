# <projekt> — karta projektu

Umowa i plan projektu w jednym dokumencie (ISO/IEC 29110-5-1-2: Agreement WP.02, Project plan WP.10). Agent proponuje treść, użytkownik zatwierdza. Zgoda na kartę: `DEC-<PRJ>-001`. Każda późniejsza zmiana karty to decyzja (DEC) z listą kontrolną zmiany (`SPEC.md`).

Status: draft | approved (`DEC-<PRJ>-…`, data) | baselined (<tag>)

## 1. Produkt i cel (PM.01.12)

| Pole | Treść |
|---|---|
| Nazwa robocza | <projekt> |
| Prefiks ID | `<PRJ>` |
| Jedno zdanie | <co to jest i dla kogo> |
| Problem, który rozwiązuje | <cytat użytkownika> |
| Kryterium sukcesu | <mierzalne, np. „przez tydzień zastępuje X w czynności Y”> |
| Język | proza, opisy i cytaty: <polski>; kody, identyfikatory, atrybuty i kod źródłowy: angielski w terminologii ISO/IEC 29110 (`WSPOLPRACA.md`) |

## 2. Zakres

- **W zakresie wersji 1:** odnośniki do NEED w `SPEC.md`.
- **Poza zakresem (OUT):** w `SPEC.md`, sekcja OUT, każda pozycja z DEC.

## 3. Cykl wytwarzania (PM.01.01)

<np. przyrostowy: etapy po 1–3 sesje, każdy kończy się działającym produktem i przeglądem.> Specyfikacja przed kodem, TDD.

## 4. Role (PM.01.06)

| Rola ISO 29110 | Kto | Uwagi |
|---|---|---|
| Klient (CUS) | użytkownik | zatwierdza wymagania, zmiany i odbiór |
| Kierownik projektu (PJM) | użytkownik | zatwierdza plan i kolejność prac |
| Lider techniczny (TL) | agent | środowisko, wersjonowanie, wydania |
| Analityk (AN), projektant (DES), programista (PR) | agent | |
| Weryfikator niezależny | osobny przebieg agenta | bez wiedzy o procesie tworzenia (SI.O7, uwaga 2) |
| Tester ręczny | użytkownik | kroki `MANUAL.md` wymagające ekranu, sprzętu, prawdziwych danych |

## 5. Dostarczane produkty i instrukcje dostawy (PM.01.02, SI.06)

| Produkt | Dostarczany? | Postać |
|---|---|---|
| Kod i testy | tak | repozytorium, tag `v<x.y.z>` |
| Specyfikacja, projekt, macierz powiązań | tak | `docs/` w tym samym tagu |
| Instrukcja użytkownika (WP.18) | tak / nie | <np. sekcja w README> |
| Instrukcja instalacji i uruchomienia (WP.08) | tak / nie | |
| Dokumentacja utrzymaniowa (WP.06) | tak / nie | <np. DESIGN.md + „Wiedza techniczna”> |

Sposób instalacji u użytkownika: <polecenie>. Sposób przywrócenia poprzedniej wersji: <polecenie>.

## 6. Plan etapów (PM.01.03–07)

| Etap | Wynik | Kryterium zakończenia | Status |
|---|---|---|---|
| E0 | Karta, SPEC, DESIGN zatwierdzone; sprawdzanie powiązań działa | `DEC-<PRJ>-…` | |
| E1 | <pierwszy pionowy przekrój funkcji> | AT … przechodzą, przegląd etapu, odbiór | |
| E2 | | | |

Pracochłonności nie szacujemy (decyzja przy zatwierdzeniu karty); jeśli trzeba, dopisz kolumnę „Szacunek sesji”.

## 7. Ryzyka (PM.01.09, PM.03)

Rejestr żyje tutaj; przegląd na końcu każdego etapu.

| ID | Ryzyko | Skutek | Środek zaradczy | Właściciel | Status |
|---|---|---|---|---|---|
| RSK-<PRJ>-001 | Wiedza projektu ginie między sesjami agenta | powtarzanie pytań, sprzeczne decyzje | `STAN.md` nadpisywany co sesję, DEC z cytatami | agent | otwarte |
| RSK-<PRJ>-002 | Agent weryfikuje własną pracę | przeoczone błędy | niezależny przegląd na końcu etapu | agent | otwarte |
| RSK-<PRJ>-003 | Długo niezatwierdzona praca w repo | utrata pracy, brak linii bazowej | commit na koniec każdego etapu (§8) | użytkownik | otwarte |

Przyjęcie ryzyka bez środka zaradczego wymaga decyzji użytkownika (lista eskalacji).

## 8. Wersjonowanie, linie bazowe i kopie (PM.01.10, PM.01.15, PM.02.06–07)

- **Repozytorium:** <ścieżka, zdalne repo>.
- **Kto commituje:** <użytkownik / agent na polecenie>. **Kto pushuje:** <…>.
- **Kolejność commitów:** najpierw specyfikacja (DEC, REQ, AT), potem kod z testami i `TRACE.md`.
- **Przed commitem:** testy na samym stanie indeksu; do commita tylko wskazane pliki.
- **Linie bazowe (baselines):**
  - wymagań: commit z zatwierdzoną kartą i SPEC, tag `spec-<etap>`;
  - produktu: tag wydania `v<x.y.z>` po odbiorze (`ODBIOR.md`).
- **Kopia zapasowa:** <np. zdalne repo + kopia maszyny>. **Test odtworzenia:** raz na etap, `git clone` do pustego katalogu i pełny przebieg testów; wynik w `STAN.md`.
- **Pliki, których agent nie rusza bez pytania:** <lista>.

## 9. Kryteria odbioru (Definition of Done)

- Wszystkie AT `@confirmed` z danego zakresu przechodzą; brak AT `@confirmed` bez testu.
- Wymagania jakościowe zmierzone, wynik zapisany jako OBS z datą i wersjami.
- Kroki `MANUAL.md` dla zakresu potwierdzone przez użytkownika albo jawnie pominięte decyzją.
- Rejestr pytań bez pytań blokujących.
- Niezależny przegląd wykonany, uwagi zamknięte albo przyjęte decyzją.
- Protokół w `ODBIOR.md` podpisany cytatem użytkownika.

## 10. Lista kontrolna niezależnego przeglądu (SI.O7)

Agent przeglądający dostaje tylko `docs/` i kod, bez historii rozmowy, i sprawdza:
1. Czy każdy DEC ze słowem „zmienia” lub „zastępuje” ma odbicie we wszystkich wskazanych REQ, DES, AT, UC, VER i w `MANUAL.md`?
2. Czy żaden dokument nie opisuje zachowania wycofanego decyzją?
3. Czy liczby i zakresy (liczba testów, zakresy ID, liczba kroków) zgadzają się z rzeczywistością?
4. Czy każde REQ jest weryfikowalne i ma AT albo VER?
5. Czy ryzyka i rejestr pytań są aktualne?
Wynik: lista uwag w `STAN.md`, „Rejestr korekt”.

## 11. Dodatki ISO/IEC 29110-5-1-2 (warunkowe)

| Dodatek | Dotyczy? | Uzasadnienie (DEC) |
|---|---|---|
| A. Wsparcie po dostawie | tak / nie | <np. „narzędzie własne, zgłoszenia jako Q w SPEC”> |
| B. Rozszerzone testy (plan testów, raport incydentów) | tak / nie | |
| C. Dostępność | tak / nie | |
| D. Bezpieczeństwo | tak / nie | <np. „produkt otwiera pliki z sieci / wykonuje polecenia / przetwarza dane osobowe” → tak> |

Przy D = tak: wymagania bezpieczeństwa jako REQ-<PRJ>-3nn, zagrożenia w rejestrze ryzyk.
