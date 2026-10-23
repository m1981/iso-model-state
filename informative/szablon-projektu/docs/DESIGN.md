# <projekt> — projekt techniczny

Realizuje `SPEC.md`. Każda decyzja projektowa (DES) wskazuje REQ lub DEC, które obsługuje. Produkty pracy ISO/IEC 29110: Software design (WP.16), Implementation environment (WP.05), część Maintenance documentation (WP.06).

Status: draft | verified | baselined (<tag>); DES nie wymaga zatwierdzenia, użytkownik może je podważyć

## Ograniczenia wejściowe

| Ograniczenie | Źródło |
|---|---|
| | DEC-…, REQ-… |

## Architektura

<diagram warstw / komponentów; kierunek zależności>

| Moduł | Odpowiedzialność | REQ |
|---|---|---|
| | | |

Tabela modułów opisuje **stan obecny**. Moduły wycofane przenoś do sekcji „Wycofane” na końcu, nie zostawiaj ich tutaj.

## Decyzje projektowe

Grupuj tematycznie; w każdej grupie wiersze rosnąco po ID.

### <temat>

| ID | Decyzja | REQ |
|---|---|---|
| DES-<PRJ>-001 | | |

## Interfejs użytkownika

Wiążący wzorzec: `ui-reference/`. Odstępstwa od wzorca tylko z tabeli „Przybliżenia” w `ui-reference/README.md`, każde z DEC.

## Środowisko (SI.01.02)

| Element | Wartość |
|---|---|
| Język i wersja | |
| Zarządzanie zależnościami | |
| Zależności czasu działania | <lista; każda z DEC> |
| Uruchomienie programu | `<polecenie>` |
| Pełny przebieg testów | `<polecenie> > <scratchpad>/log.txt 2>&1`; czytaj cały log |
| Środowisko do prób (dane demo) | `<polecenie>` |
| Liczba testów w ostatnim przebiegu | w `STAN.md` (tu nie wpisujemy, bo się starzeje) |

## Wiedza techniczna

Pułapki i obejścia zdobyte w pracy. Każdy wpis: co, dlaczego, jak sprawdzone (OBS lub data i wersja).

| ID | Wiedza | Dowód |
|---|---|---|
| KNW-<PRJ>-001 | | OBS-… |

## Testy

| ID | Decyzja | VER |
|---|---|---|
| DES-<PRJ>-9nn | Atrapy, konwencje nazw, pomiary, sprawdzanie powiązań. | |

## Kolejność realizacji

Odsyłacz do planu etapów: `KARTA-PROJEKTU.md` §6.

## Wycofane

| ID | Co było | Wycofane przez |
|---|---|---|
| | | DEC-… |
