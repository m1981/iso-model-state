# iso-model-state

Projekt rozwija i sprawdza sposób współpracy operatora z agentem: zachowanie kontekstu, kontrolę zatwierdzeń i skutków zmian. [Przyjęta karta celu i zakresu](docs/KARTA-CELU-I-ZAKRESU.md) określa korzyści i pierwsze zastosowanie na jednym rzeczywistym projekcie. Podstawą techniczną jest model stanów produktów pracy według ISO/IEC 29110-5-1-2 (profil Basic), wraz z dowodami poprawności.

Nową sesję z agentem zaczynaj treścią `PROMPT-STARTOWY.md`.

## Wiążące (normatywne)

| Plik | Zawartość |
|---|---|
| `PROMPT-STARTOWY.md` | Wejście do sesji: co czytać, zasady stałe (bez stanu prac) |
| `docs/KARTA-CELU-I-ZAKRESU.md` | Przyjęty cel użytkowy, zakres pierwszego zastosowania i kryteria sukcesu (DEC-PRO-007) |
| `PLAN.md` | Cel, Definition of Done, etapy E0–E5, narzędzia, ryzyka |
| `model/process.yaml` | **Model**: aktorzy, typy produktów, stany, przejścia, warunki, skutki, instancja testowa |
| `docs/WLASCIWOSCI.md` | Właściwości do udowodnienia: struktura, bezpieczeństwo, żywotność, sprawiedliwość, ścieżki świadkowie |
| `docs/INTERPRETACJE.md` | Rejestr interpretacji normy (INT): jak rozstrzygamy jej luki i sprzeczności |
| `docs/STAN.md` | Punkt wznowienia i decyzje DEC-PRO-nnn |
| `docs/WSPOLPRACA.md` | Kontrakt współpracy użytkownika i agenta |

## Informacyjne (niewiążące)

`informative/`: zapis sesji z motywacjami decyzji, wskazanie pełnego tekstu normy i jej niespójności, przegląd vcs-lite, szablon projektu. Przy sprzeczności rozstrzygają pliki wiążące (`informative/README.md`).

Identyfikatory tego repozytorium mają prefiks `PRO`.

## Uruchomienie sprawdzeń E2 i E3

`uv run --locked pytest -q` instaluje zależności z `uv.lock` w lokalnym `.venv` i uruchamia testy. Wymagany Python 3.12+. Kolejne uruchomienia z dostępną pamięcią pakietów mogą użyć `--offline`. Pełny zestaw obejmuje teraz rzeczywiste TLC: wymaga lokalnego JAR i Javy według [instrukcji E3.1](tla/README.md); brak narzędzia nie pomija testów.

Po korekcie DEC-PRO-006 usunięto wykazane wcześniej luki G3/G6: mutant G3 usuwa wszystkie wyjścia z `deferred`, a każde przejście ma adnotacje ISO, łącznie obejmujące 14 efektów PM/SI. Przyjęte uzasadnienie korekty zachowano w `model/proposals/e2-structure.yaml`; testy czytają model wiążący. Przyrost WIT1 dodaje wykonanie ścieżki, testy bramek i wybrane mutanty. Zielony wynik obecnego zestawu nie oznacza zakończenia E2; aktualny wynik jest w `docs/STAN.md`.

`src/isomodel/` wczytuje model i wykonuje przyjęte przejścia, w tym uwagi W03/W05. Korpus ma świadków 28/28 przejść; niezależne wyrocznie S1–S15 badają WIT i generowane sekwencje Hypothesis. Projekcja grafu G1/G3 nie dowodzi całej osiągalności ani braku zakleszczeń. Pełne dowody czasowe pozostają w E3.

**Model v0.7 wdraża DEC-PRO-010.** Późna blokada zatrzymuje odbiór, T10 zachowuje budżet odrzuceń, pusty zakres respektuje globalne bramki, a wpływ zmiany spoza zakresu unieważnia gotowość. [Raport E2](docs/E2-RAPORT.md) zawiera odtwarzalne wyniki i granice badania; **E2 v0.7 odebrano przez DEC-PRO-012**. E3.1–E3.3 wykonane: [lokalne T03](docs/E3-01-RAPORT.md), [wielokrokowy wycinek T01–T03](docs/E3-02-RAPORT.md), [tworzenie i linie bazowe PLAN–REQ](docs/E3-03-RAPORT.md). E3 jako etap pozostaje w toku. [Przyjęty pakiet zmian](model/proposals/e2-hardening.md).

`.venv/bin/python scripts/run_e2.py --output artifacts/e2` odtwarza raport i pełne dane. Kod wyjścia **0** oznacza powodzenie sprawdzeń, **1** niepowodzenie sprawdzeń, **2** błąd przygotowania raportu. Skrypt nie odczytuje decyzji odbioru; generowany status awaiting_acceptance nie zastępuje DEC-PRO-012 i bieżącego STAN.md. Testy diagnostyczne są zielone, gdy prawidłowo odtwarzają znaną lukę — nie są dowodem jej naprawy.

Starszy skrypt spójności E1: `uv run --locked python scripts/check_model.py`. Wynik tego skryptu nie zastępuje testów E2 ani dowodów E3. Bieżące decyzje i punkt wznowienia: `docs/STAN.md`.

## Lokalne sprawdzenie T03 w TLC — E3.1

`.venv/bin/python scripts/run_e3.py --output artifacts/e3-01/reproduction` odtwarza bazową regułę, pięć kontroli danych, trzy mutanty i ich wykonane świadki. Kod 0 oznacza spełnienie oczekiwań badania, nie odbiór E3. [Instrukcja i setup](tla/README.md) · [Raport](docs/E3-01-RAPORT.md) · [Archiwum dowodów](tla/e3-01/manifest.json). Wynik dotyczy syntetycznej relacji jednego kroku; nie dowodzi pełnych S/L ani osiągalności.

## Wielokrokowy wycinek T01–T03 — E3.2

`.venv/bin/python scripts/run_e3_loop.py --output artifacts/e3-02/reproduction` bada osiem kontekstów do głębokości 8 oraz kontrole danych, mutanty i monitory historii. Pokazuje zatwierdzenie po dwóch odrzuceniach i blokadę trzeciego; porównuje zbiory odwiedzonych stanów z Pythonem i niezależną wyrocznią. [Raport](docs/E3-02-RAPORT.md) · [Niezależna recenzja](docs/reviews/E3-02-WYKONANIE-2026-10-27.md) · [Archiwum obu przebiegów](tla/e3-02/manifest.json). Syntetyczny Init i stałe zależności ograniczają zakres wyniku; nie jest to dowód całego procesu.

## Tworzenie produktów i linie bazowe — E3.3

`.venv/bin/python scripts/run_e3_catalog.py --output artifacts/e3-03/reproduction` bada T00–T04 na planie i wymaganiu, od rzeczywistego Init. Zależności czyta z bieżącego katalogu: wymaganie można przygotować wcześniej, lecz zweryfikować dopiero po zatwierdzeniu planu, a ustalić jego linię bazową po linii bazowej planu. [Raport](docs/E3-03-RAPORT.md) · [Niezależna recenzja](docs/reviews/E3-03-WYKONANIE-2026-10-27.md) · [Manifest dowodów](tla/e3-03/manifest.json). Dwa aktywne produkty, stała topologia i 16 kroków ograniczają wynik; to nadal część E3.

## Przygotowanie badania wpływu zmiany — E3.4

[Zakres i oczekiwania](docs/E3-04-MAPOWANIE.md) · [Scenariusz i odtworzenie przygotowania](docs/preparations/e3-04/README.md) · [Niezależny przegląd](docs/reviews/E3-04-PRZYGOTOWANIE-2026-10-27.md). Istniejący E2 wykonał 42 kroki zmiany wymagania i testu oraz przeglądu projektu i kodu; sprawdzono 14 pełnych punktów kontrolnych i 5 odmów. To przygotowanie następnego badania, bez nowego generatora i TLC E3.4.

## Wykonywalny WIT1

`uv run --locked --offline python scripts/run_wit1.py --output artifacts/wit1` wykonuje 29 kroków na siedmiu elementach i zapisuje raport Markdown oraz pełny ślad JSON. Osiągnięte `accepted` i wszystkie cytaty dotyczą wyłącznie symulacji. Skrypt sprawdza też siedem prób obejścia bramek i odpowiadające im mutanty.

[Instrukcja, zakres i ograniczenia](examples/wit1/README.md) · [Raport wykonanego przebiegu](examples/wit1/report.md). Nie jest to dowód TLC ani odbiór E2.

## Odrzucenia i pytania — WIT2/WIT4

`uv run --locked --offline python scripts/run_scenario.py --scenario WIT2 --output artifacts/wit2` wykonuje 33 kroki: dwa odrzucenia r1, zatwierdzenie trzeciej propozycji i odbiór. Osobna próba potwierdza blokadę trzeciego odrzucenia.

`uv run --locked --offline python scripts/run_scenario.py --scenario WIT4 --output artifacts/wit4` wykonuje 13 kroków kolejki pytań: odpowiedź niejednoznaczną bez DEC, zachowanie FIFO, rozstrzygnięcia, odłożenie i wznowienie. Powstają trzy demonstracyjne DEC. Reguła blocking_first zachowuje pierwszeństwo pytań blokujących.

[Instrukcja i granice](examples/questions/README.md) · [Raport WIT2](examples/questions/wit2-report.md) · [Raport WIT4](examples/questions/wit4-report.md). Przyrost dodaje dziewięć wykrytych mutantów; pełne G/S/L nadal wymagają dalszych prac.

## Zmiana po odbiorze — WIT5

`uv run --locked --offline python scripts/run_scenario.py --scenario WIT5 --output artifacts/wit5` wykonuje 40 kroków: odbiór wydania 1, zgodę na zmianę a2 v1, otwarcie wydania 2 i jego odbiór. Cały rekord wcześniejszego odbioru pozostaje identyczny. Dziesięć wybranych mutantów sprawdza m.in. odmowę potraktowaną jak zgoda, niepasujący element/wersję/operację, brak zapisu wykorzystania zgody i zmianę historycznego odbioru.

[Instrukcja i granice](examples/wit5/README.md) · [Raport WIT5](examples/wit5/report.md). Ten przebieg jest częścią dostawy E2 odebranej przez DEC-PRO-012; sam nie zastępuje dowodów E3.

## Zastąpienie wymagania i naprawa powiązań — WIT3

`uv run --locked --offline python scripts/run_scenario.py --scenario WIT3 --output artifacts/wit3` wykonuje **54 kroki**: zastąpienie r1, utworzenie r3, jawne włączenie do zakresu przez U, naprawę a1/d1 i przegląd c1, ponowny przegląd R oraz odbiór. Siedemnaście mutantów potwierdza czułość wybranych kontroli. Test uzupełniający sprawdza również zastąpienie po odbiorze: 56 kroków, dwa wydania, pierwszy rekord bez zmian.

[Instrukcja i diagram przed/po](examples/wit3/README.md) · [Raport wykonania](examples/wit3/report.md) · [Przyjęte uzasadnienie DEC-PRO-009](model/proposals/wit3-replacement.md).

Katalog ma osiem ID, ale początkowy zakres nadal siedem. Rezerwowe r3 pozostaje nieutworzone i poza zakresem w WIT1/WIT2/WIT4/WIT5. Zidentyfikowany kontrprzykład S4 jest zablokowany przez wzmocniony T11; nie jest to dowód całego S4 ani zakończenie E2.

## Wizualizacja procesu i pakiety wdrożeniowe

[Przewodnik po modelu v0.4 i wsparciu pakietów Aneksu E](informative/WIZUALIZACJA-2026-10-24.md) zawiera diagramy zależności produktów, życia elementu i kolejnych wydań oraz tabelę zakresu wsparcia dziewięciu pakietów. Materiał jest informacyjny.

Diagramy SVG/PNG generuje `uv run --locked python scripts/render_process.py` z bieżącego YAML, przy użyciu zainstalowanego Graphviz (`dot`). Diagramy nie są interaktywnym symulatorem ani dowodem poprawności procesu.
