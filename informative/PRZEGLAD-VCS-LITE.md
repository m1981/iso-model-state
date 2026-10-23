# Przegląd materiałów vcs-lite względem ISO/IEC 29110-5-1-2

Przegląd 2026-10-23 dokumentów: `PROMPT-STARTOWY.md`, `WSPOLPRACA.md`, `SPEC.md`, `DESIGN.md`, `ACCEPTANCE.feature`. Wnioski trafiły do szablonu; ta lista służy też jako zadania porządkowe dla samego vcs-lite.

## A. Niespójności (dokumenty sobie przeczą)

| # | Niespójność | Dowód | Skutek | Poprawka w szablonie |
|---|---|---|---|---|
| A1 | Prompt startowy ma nieaktualny stan. | Prompt: „czeka krok 16” i „podpis Q-VCS-055”; SPEC: krok 16 potwierdzony, DEC-VCS-109 podpisana. Prompt: „DEC-VCS-001–097”; SPEC kończy się na DEC-VCS-109. | Agent zaczyna sesję od zadań już zrobionych. | Stan tylko w `STAN.md`; prompt bez stanu. |
| A2 | Usunięcie Beyond Compare (DEC-VCS-102) nie objęło reszty dokumentów. | REQ-VCS-023, REQ-VCS-031 („Porównaj źródło” w BC), UC-VCS-03, DES-VCS-036–039, ryzyka w DESIGN, AT-VCS-004, 025–029, 039, prompt („tool (Beyond Compare)”) dalej opisują BC. | Testy i specyfikacja opisują produkt, którego już nie ma; śledzenie powiązań tego nie wykrywa. | Lista kontrolna zmiany, kolumny „Zmienia” i „Przejrzane”, reguły REQ-<PRJ>-208–209. |
| A3 | REQ-VCS-007 jest jednocześnie „uśpione” i „przestaje być uśpione”. | Status w tabeli REQ: „Uśpione w v1, DEC-VCS-044”; DEC-VCS-105: „przestaje być uśpione”. AT-VCS-007 nadal `@dormant`. | Nie wiadomo, czy wymaganie obowiązuje. | Jak A2. |
| A4 | Zasada „bez zewnętrznych zależności” obowiązuje i nie obowiązuje. | DESIGN, „Ograniczenia wejściowe”, wiersz 1; DEC-VCS-079 dopuszcza `markdown-it-py`. | Agent może odrzucić poprawne rozwiązanie albo przyjąć złe. | `DESIGN`, „Środowisko”: lista zależności, każda z DEC. |
| A5 | Tabela modułów opisuje widżety, których nie ma. | `DiffView` (wycofany DES-VCS-025); `FileTree` i `RepoList` jako `ttk.Treeview` (DES-VCS-023, 024), choć DEC-VCS-047 i DES-VCS-045 mówią o `tk.Canvas`. | Mylący opis architektury dla przeglądu i utrzymania. | Tabela modułów = stan obecny; sekcja „Wycofane”. |
| A6 | VER-VCS-013 mówi o 13 krokach ręcznych, a kroków jest 16. | VER-VCS-013 vs Punkt wznowienia. | Drobne, ale pokazuje, że liczby w tekście się starzeją. | Liczby zmienne tylko w `STAN.md`. |
| A7 | Kontrakt współpracy w vcs-lite stawia decyzje na drugim miejscu wiadomości i pozwala na 3 decyzje przy zasadzie „jeden temat”. | `WSPOLPRACA.md` vcs-lite, pkt 3, 4 i 6. | Sprzeczne instrukcje dla agenta. | Nowy `WSPOLPRACA.md`: decyzja na dole, domyślnie jedna. |
| A8 | Kolejność wierszy w rejestrach. | DEC-VCS-017 i Q-VCS-013 stoją na końcu tabel. | Trudniej znaleźć i porównać. | „Zasady prowadzenia” w `SPEC`. |

## B. Luki względem ISO/IEC 29110-5-1-2

| # | Luka | Wymaganie normy | Propozycja |
|---|---|---|---|
| B1 | Brak planu projektu: etapów, harmonogramu, instrukcji dostawy, strategii wersjonowania. | PM.01, WP.10; PM.O1, PM.O6 | `KARTA-PROJEKTU.md` §3–§8. |
| B2 | Brak rejestru ryzyk; ryzyka przyjmowane mimochodem (niestabilny test zignorowany, DEC-VCS-077). | PM.01.09, PM.O5, PM.03.01 | `KARTA` §7; przyjęcie ryzyka na liście eskalacji. |
| B3 | Odbiór zastąpiony „odczytaniem agenta” (DEC-VCS-096); kroki ręczne odhaczone bez potwierdzenia. | PM.04.01, WP.01 (podpis klienta) | `ODBIOR.md`; `MANUAL.md` tylko z cytatem. |
| B4 | Brak linii bazowych: specyfikacja i kod niezatwierdzone przez wiele etapów. | PM.O6, PM.01.10, SI.02.08, SI.06.05 | Tagi `spec-<etap>` i `v<x.y.z>`, commit na koniec etapu. |
| B5 | Brak kopii zapasowej i testu odtworzenia. | PM.02.06–07 | `KARTA` §8. |
| B6 | Weryfikacja niezależna nie istnieje; agent sprawdza własną pracę. | SI.O7, uwaga 2 | Niezależny przegląd z listą kontrolną (`KARTA` §10). |
| B7 | Brak decyzji o dokumentacji użytkownika, instalacji i utrzymania. | SI.02.06, SI.05.07, SI.06.02 (warunkowe, zależne od instrukcji dostawy) | `KARTA` §5. |
| B8 | Brak rejestru korekt i raportu z testów per wydanie. | PM.03.02 (WP.04), SI.05.04 (WP.20) | `STAN.md`: przebieg testów, rejestr korekt. |
| B9 | Brak jawnej decyzji o dodatku D (bezpieczeństwo), choć produkt generuje HTML z treści plików, otwiera pliki w przeglądarce i uruchamia gita. Zabezpieczenia (CSP, HTML jako tekst) powstały doraźnie. | Annex D | `KARTA` §11: decyzja o każdym dodatku z uzasadnieniem. |

## C. Słabe punkty śledzenia powiązań

- Sprawdzanie wykrywa brakujące i nieistniejące ID, ale **nie wykrywa treści sprzecznej z decyzją** (A2, A3). Szablon dodaje reguły REQ-<PRJ>-208 (nic aktywnego nie wskazuje elementu wycofanego) i REQ-<PRJ>-209 (każde ID z „Zmienia” jest „Przejrzane”).
- „Decyzje agenta” są rozproszone w tekście DES i DEC bez znacznika, który da się wyszukać. Szablon: stały zwrot „decyzja agenta: …, bo …” przy elemencie, którego dotyczy.

## D. Co działa dobrze i zostało w szablonie bez zmian

- Cytat użytkownika z datą jako dowód decyzji (lepszy ślad niż typowy „meeting record”).
- Specyfikacja przed kodem, test oblewający z właściwego powodu, nazwy testów od ID, `Trace:` w modułach, generowany `TRACE.md`.
- OBS z poleceniem, wersjami i datą jako dowód pomiaru.
- Makieta HTML przed kodem i wiążący wzorzec wyglądu.
- Lista eskalacji (CCIR) i decyzje do podpisu z rekomendacją.
