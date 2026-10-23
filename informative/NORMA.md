# Norma ISO/IEC 29110-5-1-2 — gdzie jest i jak jej używać

Migawka: 2026-10-23. Dokument informacyjny (`informative/README.md`).

## Pełny tekst

- Zdalnie: https://github.com/m1981/iso-29110-5-1/tree/main/chapters
- Lokalnie u użytkownika: `/Users/michal/PycharmProjects/iso-29110-5-1` (rozdziały w `chapters/`)

Pliki rozdziałów (transkrypcja PDF do Markdown, z oznaczeniami stron i transkrypcją etykiet figur):

| Plik | Zawartość |
|---|---|
| `00-introduction.md` | seria 29110, profile, figura 1 |
| `03-terms-and-definitions.md` | definicje 3.1–3.53 |
| `04-naming-diagramming-and-definitions-conventions.md` | notacja zadań, produktów, stanów |
| `05-overview.md` | warunki wejścia (5.2), procesy PM i SI, linie bazowe i powiązania |
| `06-project-management-pm-process.md` | PM.O1–O7, PM.01–PM.04, tabele zadań 1–4 |
| `07-software-implementation-si-process.md` | SI.O1–O7, SI.01–SI.06, tabele zadań 5–10 |
| `08-description-of-roles.md` | role (Tabela 11) |
| `09-description-of-work-products.md` | stany (Tabela 12), produkty pracy WP.01–WP.23 (Tabele 13–35) |
| `annex-a…` – `annex-e…` | dodatki A (wsparcie), B (testy), C (dostępność), D (bezpieczeństwo), E (pakiety wdrożeniowe) |

Zasady korzystania:
- Agent czyta rozdział, gdy potrzebuje dokładnego brzmienia zadania, efektu albo produktu; nie kopiuje treści normy do tego repozytorium (prawa autorskie ISO), tylko odwołuje się do numerów (PM.02.03, WP.13, Tabela 12).
- Transkrypcja może mieć błędy konwersji: przy wątpliwości porównać z PDF.
- Ten przewodnik (29110-5-1-2) używa „should”. Wymagania zgodności są w ISO/IEC 29110-4-1, ocena w 29110-3. Tych części nie mamy.
- Darmowe pakiety wdrożeniowe (Aneks E) to warstwa „jak”: szablony, listy kontrolne, przykłady.

## Niespójności wykryte w normie (2026-10-23)

Podstawa rejestru `docs/INTERPRETACJE.md`. Numeracja według normy.

### Stany produktów pracy

Tabela 12 definiuje znaczenie stanów, ale nie przejścia ani aktorów. Listy „applicable states” w opisach produktów przeczą stanom w tabelach zadań:

| Produkt | Stany w opisie produktu | Stany w zadaniach |
|---|---|---|
| Acceptance record (WP.01) | initiated, signed („signed” nie ma w Tabeli 12) | approved (PM.04.01) |
| Project plan (WP.10) | validated, accepted, updated, reviewed („accepted” nie ma w Tabeli 12) | initiated, approved |
| Requirements specification (WP.13) | verified, validated, baselined | initiated, approved; SI.03.08 wymaga [validated], którego nic nie wytwarza |
| Change request (WP.03) | initiated, evaluated, accepted, rejected | approved or rejected (PM.02.03) |
| Meeting / Verification / Validation record | approved / initiated, approved | published |
| Progress status record (WP.09) | published | evaluated (PM.03.01) |
| Software (WP.14), Software components (WP.15) | tested, unit tested (brak w Tabeli 12) | implemented, verified |
| Software product (WP.17) | delivered, accepted | baselined, verified |

### Identyfikatory

- Aneks D: WP.07SM, WP.09SM, WP.12SM, WP.15SM wskazują produkty, które w rozdziale 9 mają numery WP.08, WP.10, WP.13, WP.16.
- Aneks B zapowiada numerację „WP.CXX”, używa WP.T01; Aneks C używa WP.D.01.
- Aneks D: nierozwiązane numery zadań `PM.01.XSA`, `PM.1.XSA`, `SI.01.nSA`.
- Aneks A: `SLM.01.01` w działaniu SS.01; po `PCM.01.01` następuje `PCM.02.02`.
- `SI.3.8.TT1` (format niezgodny); rola „PJ” (Aneks B); rola TES spoza wykazu 4.3; skrót ST znaczy support team (Aneks A) i security task (Aneks D).

### Odsyłacze i treść

- PM.01.01 odsyła warunki wejścia do rozdziału 6 (są w 5.2).
- PM.02.02 każe negocjować zmianę w PM.02.04 (to PM.02.05).
- PM.01.13: walidacja zapisywana w „verification record”, choć wynikiem jest validation record.
- SI.02.07 i SI.03.05: zdublowane uwagi o zadaniach warunkowych.
- Nazwy: „Product operation guide” (figura 4) / „guideline” (tekst); „Product assembly” / „Product delivery” (Tabela 37) / „Software product delivery” (Aneks C).

### Diagramy

Pokazują główne przepływy, nie wszystkie: na figurze 4 brak Implementation environment (wynik SI.01.02) i Agreement (wejście SI.02.02). Norma sama zaznacza, że notacja nie narzuca cyklu życia, a tabele służą prezentacji.

### Czego norma nie definiuje

Przejść między stanami, aktorów przejść, warunków bramek, limitu pętli „popraw, aż zatwierdzi”, reakcji na odrzucenie i na odpowiedź niejednoznaczną, losu elementów zależnych po zmianie, sytuacji, gdy klient i kierownik projektu to jedna osoba. Dlatego „jednego właściwego” wdrożenia nie ma: jedna musi być nasza zapisana interpretacja.
