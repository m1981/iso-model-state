# <projekt> — specyfikacja

Reżim: NEED → DEC → REQ → (DES, AT, VER) → test → kod. Każda decyzja ma źródło: cytat użytkownika z datą albo „decyzja agenta” do podważenia. Statusy elementów są stanami modelu procesu (`draft`, `verified`, `approved`, `baselined`, `deferred`, `superseded`, `withdrawn`); `draft` i `verified` oznaczają, że użytkownik jeszcze tego nie zatwierdził.

Produkt pracy ISO/IEC 29110: Requirements specification (WP.13); decyzje i rejestr pytań pełnią rolę Change request (WP.03) i Meeting record (WP.07).

## Zasady prowadzenia

- **ID:** `NEED`, `DEC`, `REQ`, `UC`, `VER`, `Q`, `OBS` z prefiksem `<PRJ>` i numerem trzycyfrowym. Numery nie są używane ponownie.
- **Kolejność:** wiersze w tabelach rosnąco po ID.
- **Statusy elementu:** `draft` → `verified` → `approved (DEC-…)` → `baselined (<tag>)`; poza tym `deferred (DEC-…)`, `superseded by … (DEC-…)`, `withdrawn (DEC-…)`. Elementów nie usuwamy. Element z flagą `suspect` czeka na przegląd po zmianie zależności.
- **Cytat:** dosłowny, z datą, z literówkami użytkownika.
- **Niejednoznaczna odpowiedź:** nie tworzy DEC. Agent zapisuje pytanie ponownie (Q) i pyta prościej.

## Zarządzanie zmianą (PM.02.02–03, PM.03.03–04)

Decyzja, która zmienia coś zaakceptowanego, ma w kolumnie „Zmienia” pełną listę ID. W tej samej edycji agent:

1. oznacza zmienione elementy statusem `superseded` albo przywraca je do `draft` z dopiskiem `(changed DEC-…)`, a ich zależne oznacza jako `suspect`;
2. przegląda: REQ, UC (także scenariusze alternatywne), AT w `ACCEPTANCE.feature`, DES (także tabelę modułów, ograniczenia wejściowe, ryzyka, kolejność realizacji), VER, kroki `MANUAL.md`, `ui-reference/`, wiedzę techniczną w `DESIGN.md`;
3. dopisuje w wierszu DEC „Przejrzane: …” z listą zaktualizowanych ID;
4. uruchamia sprawdzanie powiązań (VER-<PRJ>-900).

Zmiana jest gotowa dopiero po punkcie 4. Dopóki nie jest, sprawa jest otwarta w `STAN.md`.

## Potrzeby

| ID | Potrzeba | Źródło |
|---|---|---|
| NEED-<PRJ>-001 | | Użytkownik <data>: „…” |

## Poza zakresem (OUT)

- <pozycja>, DEC-<PRJ>-…

## Język domeny

| Termin | Znaczenie |
|---|---|
| | |

## Decyzje

| ID | Decyzja | Źródło | Zmienia | Przejrzane |
|---|---|---|---|---|
| DEC-<PRJ>-001 | Karta projektu zatwierdzona. | Użytkownik <data>: „…” | — | — |

## Wymagania funkcjonalne

| ID | Wymaganie | Status | Powiązania |
|---|---|---|---|
| REQ-<PRJ>-001 | | draft | NEED-…, DEC-…, UC-… |

Każde wymaganie jest jednoznaczne, weryfikowalne i ma co najmniej jeden AT albo VER oraz DES (wyjątek: „bez DES: <powód>”).

## Wymagania jakościowe

| ID | Wymaganie | Miara i metoda | Status |
|---|---|---|---|
| REQ-<PRJ>-100 | | <liczba, warunki pomiaru, narzędzie> | |

Rozważ charakterystyki ISO/IEC 25010 (wydajność, użyteczność, niezawodność, bezpieczeństwo, utrzymywalność, przenośność) i każdą odrzuconą zapisz w OUT.

## Przypadki użycia

Wspólne: **aktor**, **granica systemu**, **gwarancja minimalna**.

### UC-<PRJ>-01 — <nazwa>

**Wyzwalacz:** … **Sukces:** …

1. …

| Krok | Warunek | Reakcja |
|---|---|---|
| 1a | | |

## Weryfikacja

| ID | Co weryfikuje (REQ) | Metoda | Scenariusze |
|---|---|---|---|
| VER-<PRJ>-001 | | test automatyczny / pomiar / przegląd / ręcznie (`MANUAL.md` krok n) | AT-… |
| VER-<PRJ>-900 | REQ-<PRJ>-200–209 | `tests/test_traceability.py` | — |

## Śledzenie powiązań

| ID | Reguła |
|---|---|
| REQ-<PRJ>-200 | Każde ID ma dokładnie jedną definicję (wiersz tabeli, nagłówek UC, tag `@AT_<PRJ>_nnn`). |
| REQ-<PRJ>-201 | Odwołania pełnym ID; zakres tylko jako `X-001–005` z półpauzą. |
| REQ-<PRJ>-202 | W przód: każde REQ ma AT albo VER oraz DES (albo „bez DES: …”). |
| REQ-<PRJ>-203 | Wstecz z dokumentów: AT, VER i DES wskazują REQ lub DEC. |
| REQ-<PRJ>-204 | Wstecz z testów: nazwa testu zaczyna się od pokrywanego ID. |
| REQ-<PRJ>-205 | Każdy AT `@confirmed` ma test; brak testu oblewa sprawdzenie. |
| REQ-<PRJ>-206 | Każdy moduł kodu ma w docstringu linię `Trace: …` z istniejącymi ID. |
| REQ-<PRJ>-207 | Generator tworzy `TRACE.md`; plik nie jest edytowany ręcznie. |
| REQ-<PRJ>-208 | Element ze statusem `superseded` lub `withdrawn` nie jest wskazywany przez żaden AT `@confirmed`, aktywny DES ani linię `Trace:`. |
| REQ-<PRJ>-209 | Każde ID z kolumny „Zmienia” decyzji występuje w jej kolumnie „Przejrzane”. |

## Obserwacje

| ID | Obserwacja | Dowód (polecenie, wersje, data) |
|---|---|---|
| OBS-<PRJ>-001 | | |

## Rejestr pytań

| ID | Pytanie (z rekomendacją agenta) | Status | Co od niego zależy |
|---|---|---|---|
| Q-<PRJ>-001 | | open / asked / resolved <data>: DEC-… / deferred to <etap> | |
