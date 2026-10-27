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

Stan etapów: E1 przyjęty jako podstawa E2 przez DEC-PRO-005 (2026-10-24); E2: dostawa v0.7 odebrana przez użytkownika — DEC-PRO-012 (2026-10-26, „d1 tak”), na podstawie docs/E2-RAPORT.md i docs/reviews/E2-V07-PRZEGLAD-2026-10-26.md. E3: wykonane E3.1–E3.4. Najnowsze E3.4 bada zgodę na zmianę, wpływ na zależne produkty i wydania: 514 testów passed, 413 kontroli spójności, 79 przebiegów TLC odtworzonych niezależnie, 34 mutanty z pełnymi świadkami. [Wynik i granice](docs/E3-04-RAPORT.md), [instrukcja](tla/README.md). Zgoda na narzędzie: DEC-PRO-013. E3 pozostaje w toku: dalej mapowanie pozostałych przejść T06–T10/T14 oraz W/P, pełna relacja, S/L przy F, jawna metoda CTL L1 i OBS. Odbiór całego E3 pozostaje przyszłą bramką; poprawny wycinek nie dowodzi wszystkich G/S/L.

## Kierunek narzędzia i sposób kolejnych przyrostów

DEC-PRO-011 (2026-10-26): dalszy rozwój API jest odłożony do wniosków z E4. Powrót do bramki E2 wykonano; odbiór zapisała DEC-PRO-012. Dalej E3–E5 w dotychczasowej kolejności. Kontrakt API i recenzje zachowujemy jako materiał do późniejszego wykorzystania; nie są przyjętym zakresem wdrożenia.

Użytkownik akceptuje przyszłe narzędzie **CLI z jawnym kontraktem i pomocnymi dla agenta komunikatami pomocy i błędów**. Nie jest to jeszcze wybór komend ani zgoda na rozpoczęcie implementacji CLI. Kontrakt przed implementacją określi wejścia, wyniki, kody zakończenia i skutki poleceń; pomoc poda przykłady, a błąd wskaże przyczynę, przedmiot i dozwolony następny krok. CLI samo nie zapewnia izolacji uprawnień ani ochrony przed obejściem procesu.

Sposób wykonania dobrany przez agenta na prośbę użytkownika: dla każdego przyrostu najpierw wskazujemy korzyść dla operatora, obowiązującą regułę i obserwowalny wynik. Potem **RED → GREEN → REFACTOR**: test zachowania nie przechodzi z oczekiwanego powodu, minimalna implementacja go spełnia, a porządkowanie zachowuje wynik i właściwą regresję. Zapisujemy faktycznie wykonane sprawdzenia. Dla samego zapisu decyzji nie tworzymy sztucznych czerwonych testów.

| Krok | Wykonanie i dowód | Udział recenzenta |
|---|---|---|
| Bramka E2 | Przedstawić istniejący raport i ograniczenia, sprawdzić aktualność dowodów; odbiór należy do U. Nie dopisywać kodu tylko po to, by ponownie zamknąć gotowy etap. | Wykorzystać zakończony niezależny przegląd v0.7; ponowić go dopiero przy zmianie przedmiotu lub nowym istotnym ustaleniu. |
| E3 po odbiorze E2 | Najpierw mały test zgodności generowanego przejścia z YAML i oczekiwanym skutkiem, potem generator i kolejne przejścia. Niezależne oczekiwania oraz porównanie z Pythonem; zgodność dwóch implementacji sama nie dowodzi poprawności. Następnie sprawdzenia TLC w jawnych granicach, S i L przy F oraz wykonane mutanty czasowe. Brak naruszeń w modelu bazowym i rzeczywisty kontrprzykład mutanta to odrębne dowody; błąd składni, brak narzędzia lub timeout nie są takim kontrprzykładem. | Przed rozszerzeniem generatora osobny R ocenia mapowanie, granice i założenia, a przed bramką E3 niezależnie odtwarza wyniki i sprawdza, czy właściwości nie zachodzą w pusty sposób. |
| E4 | Najpierw zweryfikowane epizody rzeczywistej historii i niezależnie określone oczekiwane oceny; następnie czerwone testy adaptera, implementacja i porównanie wyników. Osobno przypadki poprawne, naruszenia i brak wystarczających danych. | R sprawdza źródła i etykiety przypadków, żeby wyrocznia nie wynikała z kodu ani niepotwierdzonego zarzutu. |
| E5 / przyszłe CLI | Najpierw kontrakt wybranych poleceń i testy wywołania procesu: poprawny przypadek, odmowa, błędne wejście, pomoc, kod zakończenia i skutki. Potem minimalny CLI na sprawdzonym rdzeniu. Osobny agent próbuje wykonać zadanie, dysponując wyłącznie kontraktem i pomocą; poprawiamy komunikaty na podstawie obserwowanych pomyłek. | R sprawdza zgodność zachowania z kontraktem, czytelność następnego kroku i granice uprawnień; wyniku próby użycia nie utożsamiamy z pełnym dowodem bezpieczeństwa. |

Przyrost jest gotowy do przedstawienia, gdy ma wynik użytkowy, sprawdzony przypadek poprawny i istotne odmowy, właściwą regresję, jawne ograniczenia i zamknięte ustalenia wymaganej recenzji. Nowa luka w zaakceptowanej regule wraca do U przed jej zmianą; recenzent nie akceptuje etapu za operatora. Dla E3 pierwszym działaniem po odbiorze E2 jest odczyt dostępności narzędzi i przygotowanie zakresu pierwszego przyrostu; instalacja pozostaje osobną sprawą zgodnie z poniższą tabelą.

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
