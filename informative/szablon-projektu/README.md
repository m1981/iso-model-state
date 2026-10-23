# Szablon projektu: użytkownik i agent LLM

Generyczny zestaw dokumentów dla nowego projektu tworzonego przez jednego użytkownika z agentem LLM. Szablon wyrósł z praktyki projektu vcs-lite i jest zmapowany na produkty pracy ISO/IEC 29110-5-1-2 (profil Basic dla bardzo małych podmiotów, VSE).

## Jak zacząć

1. Skopiuj zawartość szablonu do repozytorium nowego projektu.
2. Zamień `<PRJ>` na krótki prefiks projektu (np. `VCS`) i `<projekt>` na nazwę.
3. Wypełnij z agentem `docs/KARTA-PROJEKTU.md` (umowa i plan). Zgoda na kartę to pierwsza decyzja: `DEC-<PRJ>-001`.
4. Wpisz ścieżkę projektu w `PROMPT-STARTOWY.md` i rozpoczynaj nim każdą sesję.

## Pliki

| Plik | Rola | Produkt pracy ISO 29110 | Kto zmienia |
|---|---|---|---|
| `PROMPT-STARTOWY.md` | Wejście do sesji: co czytać i w jakiej kolejności. **Bez stanu prac.** | — | Użytkownik, rzadko |
| `docs/WSPOLPRACA.md` | Kontrakt komunikacji (BLUF, decyzje do podpisu, lista eskalacji). | — (sposób prowadzenia przeglądów, PM.O4) | Użytkownik |
| `docs/KARTA-PROJEKTU.md` | Umowa, plan, role, ryzyka, wersjonowanie, instrukcje dostawy, kryteria odbioru. | Agreement (WP.02), Project plan (WP.10) | Agent proponuje, użytkownik zatwierdza |
| `docs/SPEC.md` | Potrzeby, decyzje z cytatami, wymagania, przypadki użycia, weryfikacja, rejestr pytań. | Requirements specification (WP.13), Change request (WP.03), Meeting record (WP.07) | Agent; zmiany zamiaru tylko po DEC |
| `docs/DESIGN.md` | Architektura, decyzje projektowe, środowisko, wiedza techniczna. | Software design (WP.16), Implementation environment (WP.05), Maintenance documentation (WP.06, część) | Agent |
| `docs/ui-reference/` | Wiążący wzorzec wyglądu (makiety HTML, zrzuty, tabela wartości). | Software design (WP.16), część interfejsu | Agent; akceptuje użytkownik |
| `docs/ACCEPTANCE.feature` | Scenariusze akceptacyjne (Gherkin jako dokumentacja). | Test cases (WP.19) | Agent |
| `docs/MANUAL.md` | Procedury ręczne i zapis ich wyników. | Test procedures (WP.19), Validation record (WP.22) | Agent pisze, użytkownik potwierdza |
| `docs/TRACE.md` | Macierz powiązań, **generowana** przez test. | Traceability record (WP.21) | Generator |
| `docs/STAN.md` | Punkt wznowienia: stan, ostatni przebieg testów, sprawy otwarte, rejestr korekt. **Nadpisywany**, historia jest w git. | Progress status record (WP.09), Correction register (WP.04), Test report (WP.20, skrót) | Agent na końcu sesji |
| `docs/ODBIOR.md` | Protokół odbioru każdego wydania. | Acceptance record (WP.01) | Agent przygotowuje, użytkownik podpisuje cytatem |
| `docs/RETROSPEKTYWA.md` | Lekcje i wynikające z nich zmiany procesu. | — (doskonalenie procesu) | Agent i użytkownik |

## Cykl sesji

1. **Start**: agent czyta pliki z `PROMPT-STARTOWY.md` i podaje w BLUF rozumienie zadania. Pytania zadaje tylko z listy eskalacji (`WSPOLPRACA.md`).
2. **Praca**: decyzja (DEC z cytatem) → REQ, DES, AT → test oblewający z właściwego powodu → kod → weryfikacja.
3. **Koniec**: agent nadpisuje `STAN.md` i zapisuje przebieg testów. Commit robi użytkownik albo agent na polecenie, według `KARTA-PROJEKTU.md` §8.

## Mapa ISO/IEC 29110-5-1-2 na praktykę

| Działanie ISO | Jak realizuje szablon |
|---|---|
| PM.01 Planowanie | `KARTA-PROJEKTU.md`, zatwierdzona decyzją `DEC-<PRJ>-001` (PM.01.14) |
| PM.02 Wykonanie planu | `STAN.md` (stan postępu), DEC z cytatami (zapis uzgodnień), rejestr pytań i lista kontrolna zmiany (`SPEC.md`), kopia i test odtworzenia (`KARTA` §8) |
| PM.03 Ocena i kontrola | Przegląd na końcu etapu: plan etapów i ryzyka w `KARTA`, korekty w `STAN.md` |
| PM.04 Zamknięcie | `ODBIOR.md` z podpisem użytkownika |
| SI.01 Inicjacja | Prompt startowy, środowisko w `DESIGN.md` |
| SI.02 Wymagania | `SPEC.md` z regułami śledzenia; walidacja przez akceptację użytkownika (DEC) |
| SI.03 Projekt | `DESIGN.md`, `ui-reference/`, `ACCEPTANCE.feature` |
| SI.04 Konstrukcja | TDD, nazwy testów od ID, linia `Trace:` w modułach |
| SI.05 Integracja i testy | Pełny przebieg testów z logiem, `MANUAL.md`, `TRACE.md` |
| SI.06 Złożenie produktu | Instrukcje dostawy (`KARTA` §5), wydanie z tagiem, `ODBIOR.md` |

### Świadome uproszczenia dla zespołu „człowiek i agent”

- **Podpis** to cytat wypowiedzi użytkownika z datą, zapisany przy decyzji albo w protokole odbioru.
- **Role ISO** łączą się w dwie osoby (`KARTA` §4). Klient i kierownik projektu to użytkownik; analityk, projektant, programista i lider techniczny to agent.
- **Niezależność weryfikacji** (SI.O7, uwaga 2) zapewnia osobny przebieg agenta, który nie widział procesu tworzenia: przegląd na końcu etapu, przed odbiorem.
- **Szacunki pracochłonności i kosztu** (PM.01.04, PM.01.08) są opcjonalne. Zamiast nich etapy mają kryteria zakończenia, a ryzyka właściciela.

### Dodatki normy (warunkowe)

O każdym dodatku decyduje się w `KARTA` §11, z uzasadnieniem: A (wsparcie po dostawie), B (rozszerzone testy), C (dostępność), D (bezpieczeństwo). Decyzja „nie dotyczy” też jest zapisywana.
