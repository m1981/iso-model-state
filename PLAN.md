# Plan: model stanów procesu (ISO/IEC 29110-5-1-2)

## Cel

Cel użytkowy przyjęty przez DEC-PRO-007 (2026-10-24, „d1 tak”): **opracować i sprawdzić na jednym rzeczywistym projekcie lekki sposób współpracy operatora z agentem, który zachowuje kontekst, pilnuje zatwierdzeń i pokazuje skutki zmian**. Zakres pierwszego zastosowania, rezultaty i kryteria korzyści określa [karta celu i zakresu](docs/KARTA-CELU-I-ZAKRESU.md). Przyjęcie karty zachowuje poniższy DoD oraz plan E2–E5.

Cel techniczny wspierający ten zamiar:

Jeden, sprawdzalny model stanów produktów pracy dla zespołu „użytkownik i agent LLM”. Model ma być wolny od zakleszczeń, uwięzienia w pętlach, zagłodzenia i obejść bramek. Jest jednym źródłem dla dowodów (TLA+), testów (pytest) i programu sprawdzającego repozytoria projektów.

Zgoda: DEC-PRO-001, 2026-10-23, użytkownik: „d1 tak” na DoD 1–10 i stos narzędzi.

## Definition of Done (skrót; pełna treść w `docs/WLASCIWOSCI.md`)

1. Zamknięty słownik w `model/process.yaml`; każdy stan z Tabeli 12 normy albo z INT.
2. Struktura: osiągalność, wykonalność przejść, brak ślepych stanów, determinizm, kompletność.
3. Bezpieczeństwo: S1–S15 (S7 zastąpione przez S7a i S7b), w tym brak obejść bramek użytkownika i niezmienność odebranych wydań (DEC-PRO-003), zgoda na konkretną zmianę (DEC-PRO-008) i kontrola powiązań/zakresu (DEC-PRO-009), brak blokad przy odbiorze i budżet odrzuceń wersji (DEC-PRO-010).
4. Żywotność: L1–L5 przy jawnych założeniach sprawiedliwości F1–F3.
5. Dowód TLC w podanych granicach; wynik jako OBS.
6. Test mutacyjny: każda właściwość pada na co najmniej jednym celowo zepsutym modelu.
7. Ścieżki świadkowie WIT1–WIT5 przejrzane przez użytkownika.
8. Powiązania: każdy stan i przejście → zadanie lub efekt ISO albo INT; każdy efekt PM.O1–O7, SI.O1–O7 pokryty.
9. Zgodność: sprawdzenia czytają ten sam plik modelu; odtworzenie historii vcs-lite wykrywa znane naruszenia.
10. Niezależny przegląd i podpis użytkownika.

## Etapy

| Etap | Wynik (artefakty) | Bramka | DoD |
|---|---|---|---|
| **E0** Plan | `PLAN.md`, `README.md`, `docs/STAN.md`, `docs/WSPOLPRACA.md` | — | — |
| **E1** Model jako dane | `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md` | **przegląd użytkownika**: stany, przejścia, aktorzy, właściwości | 1, 3, 4 (treść), 7 (opis), 8 |
| **E2** Sprawdzenia w Pythonie | `src/isomodel/` (wczytanie, graf), `tests/` (struktura, niezmienniki przez Hypothesis), `mutants/` | testy zielone, każdy mutant zabity | 2, 3, 6 |
| **E3** Dowody TLA+ | `tla/Process.tla`, `tla/MC.cfg`, generator z YAML, `docs/OBS.md` | TLC: brak naruszeń; mutanty czasowe zabite | 4, 5, 6, 7 |
| **E4** Odtworzenie historii | `replay/` z historią vcs-lite jako ciągiem zdarzeń | wykryte DEC-VCS-096 i Beyond Compare po DEC-VCS-102 | 9 |
| **E5** Włączenie do szablonu | `PROCES.md` i program sprawdzający w szablonie projektu, przegląd niezależny, `docs/ODBIOR.md` | podpis użytkownika | 10 |

Kolejność jest ścisła: bez zgody na E1 nie piszemy kodu, bo kod i dowody wywodzą się z modelu.

Stan etapów: E1 przyjęty jako podstawa E2 przez DEC-PRO-005 (2026-10-24); E2: dostawa v0.7 zweryfikowana, niezależny przegląd bez otwartych blokad; oczekuje osobnego odbioru użytkownika (docs/E2-RAPORT.md i docs/reviews/E2-V07-PRZEGLAD-2026-10-26.md). Akceptacja modelu nie jest potwierdzeniem spełnienia właściwości G/S/L.

## Narzędzia

| Narzędzie | Etap | Uwagi |
|---|---|---|
| Python 3.12+, PyYAML, networkx, pytest, Hypothesis | E2, E4 | zależności deweloperskie |
| Java 17+, TLA+ tools (TLC) | E3 | instalacja środowiska wymaga zgody (lista eskalacji) |

## Ryzyka

| ID | Ryzyko | Środek zaradczy |
|---|---|---|
| RSK-PRO-001 | Model poprawny, ale nie wyraża zamiaru użytkownika | ścieżki świadkowie (DoD 7) przed dowodami |
| RSK-PRO-002 | Właściwość spełniona w pusty sposób | test mutacyjny (DoD 6) |
| RSK-PRO-003 | Model i program sprawdzający się rozjadą | oba czytają `model/process.yaml` (DoD 9) |
| RSK-PRO-004 | Działania poza modelem (ręczna edycja plików) | odtwarzanie historii w E4, kontrola repozytorium w E5 |
| RSK-PRO-005 | Wybuch przestrzeni stanów w TLC | mała instancja (`test_instance`), hipoteza małego zakresu |
