# WIT5 — zgoda na zmianę i kolejne wydanie

Reguły przyjęte w v0.5 przez DEC-PRO-008; raport odtworzony na v0.6. Rezerwowe r3 pozostaje none poza zakresem. Scenariusz symulacyjny na siedmiu elementach; wszystkie cytaty, decyzje, tagi i odbiory są demonstracyjne. Nie zmieniają decyzji ani odbiorów tego repozytorium.

## Uruchomienie i wynik

```sh
uv run --locked --offline python scripts/run_scenario.py --scenario WIT5 --output artifacts/wit5
```

Polecenie zapisuje `report.md` i `trace.json`. Dane: `tests/fixtures/wit5/scenario.json`; wybrane mutanty: `mutants/wit5_gates.json`. Raport z bieżącej weryfikacji jest w [report.md](report.md).

| Kroki | Co się dzieje |
|---|---|
| 1–29 | WIT1: utworzenie produktów, weryfikacje, zatwierdzenia, linie bazowe, przegląd R i odbiór wydania 1 |
| 30–32 | P00/P01/P02: pytanie change o T05 dla a2 w wersji 1; wynik approved i cytat |
| 33 | T05: użycie wskazanej zgody, a2 przechodzi do draft w wersji 2; wymagane następne wydanie |
| 34 | W06: nowy rekord wydania 2, kopia zakresu, bez migawki i protokołu |
| 35–40 | Weryfikacja, zatwierdzenie i linia bazowa a2 v2; gotowość, przegląd R i odbiór wydania 2 |

Wyrocznia testowa porównuje cały rekord wydania 1 po każdym późniejszym kroku (stan, numer, zakres, migawkę i protokół). Oba wydania są accepted, ale migawki zawierają różne wersje a2. Zgoda pozostaje resolved/approved i ma consumed=true.

## Co wykrywają sprawdzenia

Dziesięć mutantów w raporcie korzysta wyłącznie z osiągniętych prefiksów i dodatkowych zdarzeń: odmowa jako zgoda, inny element, inna operacja, stara niewykorzystana zgoda, brak oznaczenia wykorzystania, nadpisanie odebranego rekordu przez W06, nieuprawniony aktor W06, brak unieważnienia gotowości przez T10, zmiana powiązania w P03 i W06 bez nowej zmiany.

Dodatkowe testy obejmują actor U dla T05/T07, atomowość błędu po oznaczeniu zgody, granice wersji/pytań/wydań, T12, przechodnie suspect, zmianę spoza zakresu, T10 przed i po odbiorze oraz zmianę identyfikatorów przejść bez zmiany działania. Hypothesis porównuje kombinacje warunków zgody z osobną wyrocznią logiczną. Izolowane testy pól zgody i mutanta usuwającego warunek consumed wstrzykują stan; nie są świadkami jego osiągalności. Próba powtórnego użycia zgody po rzeczywistym ponownym baselined jest osobnym testem.

Pierwszy czerwony przebieg: zatrzymano po trzech błędach, bo stary wykonawca odrzucał nowe atrybuty pytania change. Po implementacji wykonano regresję WIT1/WIT2/WIT4 i nowe przypadki; aktualne liczby są w `docs/STAN.md`.

## Decyzje implementacyjne i ograniczenia

- `resolution` jest jawnym wejściem odpowiedzi, a nie wynikiem analizy języka naturalnego. P02 zachowuje cytat i powiązanie w dzienniku dowodów. Zgoda uprawnia do operacji otwarcia zmiany lub zastąpienia; nie podpisuje treści przyszłej poprawki.
- Predykat authorized_change jest wyrażeniem w YAML, czytanym przez wykonawcę. Skutki i nowe rekordy wydań także są czytane z YAML. Wykonawca nie wybiera zachowania według ID przejścia.
- Inicjalizacja pytań i funkcja answer_resolution mają implementację opisaną w question_semantics. Helper invalidate_release obsługuje dokładnie obecną definicję tekstową i odrzuca inną; nie jest ogólnym interpreterem zdań po polsku. Pozostaje to ograniczeniem obecnego wykonawcy.
- Nowe pytanie T12 otrzymuje jawne ID ze zdarzenia, jak P00; wersję bierze ze stanu elementu. Zapis consumed, zmiany produktów, flagi i nowe wydania są zatwierdzane razem dopiero po wykonaniu całego kroku i kontroli granic.
- Limity to granice badania, nie zakazy procesu. Błąd przy przekroczeniu limitu pozostawia stan i zgodę bez zmian.
- To wykonanie zadanej ścieżki E2, bez dowodu TLC, pełnej maszyny stanów Hypothesis i odbioru E2. WIT3 ma [osobne wykonanie](../wit3/README.md). Pełne pokrycie G/S/L, obsługa ustaleń W03/W05 i adapter do rzeczywistego repozytorium pozostają przed nami. Pusty zakres wydania nadal jest jawnie nieobsługiwany.
