# <projekt> — protokoły odbioru

Produkt pracy ISO/IEC 29110: Acceptance record (WP.01), PM.04. Każdy etap kończący się wydaniem dostaje protokół. Agent przygotowuje, użytkownik podpisuje cytatem. **Agent nigdy nie uznaje odbioru za spełniony sam.**

## Odbiór <wersja / etap>, <data>

| Pole | Treść |
|---|---|
| Wersja i commit | `v<x.y.z>`, `<hash>` |
| Zakres | REQ-… (lista albo zakres), AT-… |
| Testy automatyczne | <n> przechodzi; log: <ścieżka> |
| Pomiary jakości | OBS-… |
| Kroki ręczne | `MANUAL.md` kroki … potwierdzone; pominięte: … (DEC-…) |
| Niezależny przegląd | <data>; uwagi: zamknięte / przyjęte (DEC-…) |
| Dostarczone produkty | według `KARTA` §5 |
| Sprawy otwarte przeniesione | Q-…, z etapem docelowym |
| Kryteria odbioru (`KARTA` §9) | spełnione / niespełnione: … |
| **Decyzja użytkownika** | <data>: „…” (`DEC-<PRJ>-…`) |
