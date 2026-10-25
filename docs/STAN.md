# Stan prac

Nadpisywany na końcu każdej sesji. Zaktualizowano: 2026-10-25. Model v0.5 i WIT5 wykonane; ostatnia regresja: 197 testów. Przygotowano propozycję WIT3 i odtworzono kontrprzykład S4 w T11. Model i wykonawca pozostają bez zmian; propozycja czeka na decyzję. E2 nadal trwa.

## Gdzie jesteśmy

- **Etap:** E2 w toku. Model v0.3 przyjęty przez DEC-PRO-005; korekta v0.4 przyjęta przez DEC-PRO-006, a v0.5 przez DEC-PRO-008. Karta celu i reguła zgody są przyjęte; nie ma oczekującej decyzji w tych sprawach.
- **Ostatnio zrobione:**
  - na polecenie „wykonaj rzeteleni Dalej” przygotowano propozycję następcy, jawnej aktualizacji powiązań i zakresu wydania: `model/proposals/wit3-replacement.md`; plan zdarzeń `wit3-outline.json`, status proposed_not_executable;
  - diagnostyka `model/proposals/wit3_diagnostics.py` odtworzyła 32-krokowy początek zastępowania: r1 superseded, a1/d1/c1 suspect, wydanie in_preparation, p1/r2/a2 bez zmian; wykazała brak r3 w katalogu i blokadę pozornego przeglądu a1;
  - osobny, osiągalny 30-krokowy kontrprzykład S4: WIT1 do reviewed → T06(d1) → T11(c1) zostawia c1 baselined bez suspect przy d1 draft. Proponowane wzmocnienie T11 blokuje ten przypadek na kopii w pamięci. Wynik zapisano w `model/proposals/wit3-diagnostics.json`; nie zastosowano korekty w wiążącym modelu;
  - DEC-PRO-008: wynik approved/rejected, powiązanie zgody z elementem, wersją i T05/T07, atomowe consumed; pytania general pozostają zgodne z WIT4;
  - WIT5: 40 kroków, a2 zmienia się z v1 na v2, dwa odebrane wydania; cały rekord wydania 1 jest identyczny po każdym późniejszym kroku;
  - dodano 46 przypadków testowych (197 łącznie); 10 mutantów WIT5 wykrytych (26 wybranych mutantów w raportach wykonania) i osobny test mutanta usuwającego warunek consumed;
  - odtworzono WIT1/WIT2/WIT4/WIT5 na v0.5; zapisane raporty w examples/, pełne odtwarzalne ślady JSON w ignorowanym artifacts/;
  - zapisano DEC-PRO-007 z cytatem „d1 tak”: karta celu i zakresu jest dokumentem zamiaru w `docs/KARTA-CELU-I-ZAKRESU.md`; plan E2–E5 i DoD zachowano;
  - wcześniejszą propozycję `model/proposals/change-authorization.md` zastosowano przez DEC-PRO-008; zachowano ją jako uzasadnienie modelu v0.5;
  - na prośbę „napisz do pliku karte celu i zekresu” zapisano `informative/KARTA-CELU-I-ZAKRESU-2026-10-24.md`: propozycję celu użytkowego, zakresu pierwszego zastosowania, rezultatów, kryteriów sukcesu i związku z E2–E5;
  - wykonano następny przyrost WIT2/WIT4 na polecenie użytkownika „commit i wykonaj nastepny przyrost”; WIT1 był już zapisany i wypchnięty jako 2b830e0;
  - WIT2: 33 kroki, dwa odrzucenia r1 w wersji 1, blokada trzeciego odrzucenia w osobnej próbie, następnie zatwierdzenie i odbiór wydania testowego;
  - WIT4: 13 kroków P00–P05, zachowanie FIFO i pierwszeństwa blokujących, odpowiedź niejednoznaczna bez DEC, trzy rozstrzygnięcia z demonstracyjnymi DEC, odłożenie i wznowienie;
  - przy zakończeniu przyrostu WIT2/WIT4 przechodziło 151 testów, 9 nowych mutantów wykrytych (łącznie 16 wybranych mutantów wykonania); instrukcja i raporty: `examples/questions/README.md`, `wit2-report.md`, `wit4-report.md`;
  - wykonano WIT1 na przyjętym modelu v0.4: 7 elementów, 29 kroków, wydanie 1 accepted z odrębną migawką i protokołem demonstracyjnym;
  - dodano interpreter wyrażeń, atomowy wykonawca, odtworzenie scenariusza i raport; odrzucony krok nie zmienia stanu;
  - przyrost WIT1 miał 108 testów i siedem wykrytych mutantów bramek; pozostaje zielony w obecnym zestawie;
  - instrukcja i zapisany raport: `examples/wit1/README.md`, `examples/wit1/report.md`; pełny ślad lokalny: `artifacts/wit1/trace.json` (odtwarzalny, pomijany przez Git);
  - zastosowano korektę adnotacji ISO: wszystkie przejścia mają iso, a jawne powiązania obejmują 14 efektów PM/SI;
  - zastąpiono nieskutecznego mutanta G3: aktywny usuwa T07/T08/T10; poprzedni zachowano jako superseded;
  - wcześniejszy przyrost strukturalny miał 31 testów, w tym dwa uprzednio czerwone kryteria G3/G6; są częścią obecnego zestawu;
  - na prośbę użytkownika przygotowano informacyjny przewodnik, trzy diagramy SVG/PNG i mapowanie wsparcia dziewięciu pakietów Aneksu E: `informative/WIZUALIZACJA-2026-10-24.md`;
  - diagramy generuje `scripts/render_process.py` z YAML przez dostępny Graphviz; nie jest to symulator.
- **Następny krok:** użytkownik rozstrzyga gotową propozycję `model/proposals/wit3-replacement.md`. Po zgodzie agent zapisuje nową DEC, aktualizuje model/właściwości i wdraża WIT3 według planu 54 kroków, z czerwonymi testami, mutantami i regresją. Nie ma zgody na v0.6 ani DEC-PRO-009; „wykonaj rzeteleni Dalej” dotyczyło przygotowania propozycji. Dalsze prace E2 i E3–E5 pozostają w planie.

## Bramka E1

Przyjęta przez DEC-PRO-005. Korekta G3/G6 zatwierdzona przez DEC-PRO-006 nie zmienia zachowania przejść ani polityki wydań. G6 sprawdza śledzenie powiązań, nie pełną zgodność procesu z normą.

## Przyjęta karta celu użytkowego

- DEC-PRO-007 przyjmuje cel użytkowy: sprawdzić na jednym rzeczywistym projekcie lekki sposób współpracy operatora z agentem, zachowujący kontekst, zatwierdzenia i kontrolę skutków zmian. Dokument wiążący: docs/KARTA-CELU-I-ZAKRESU.md.
- Karta rozdziela poprawność reguł od użyteczności narzędzia. Określa zakres jednego repozytorium i zespołu operator–agent–przegląd, trzy przypadki użycia, pięć grup rezultatów i kryteria sukcesu, w tym pomiar kosztu utrzymania procesu. Konkretny pilotaż i dopuszczalny narzut wymagają uzgodnienia przed rozpoczęciem.
- Plan E2–E5, E3/TLC i dotychczasowy DoD zachowano. Akceptacja celu nie udziela dostępu do historii vcs-lite ani nie odbiera żadnego etapu. Historyczna propozycja w informative/ pozostaje bez zmian; indeks wskazuje nowy dokument wiążący.
- Włączono kartę do PLAN.md, listy dokumentów zamiaru, kolejności czytania w PROMPT-STARTOWY.md, README i reguły pierwszeństwa informative/. Ze skopiowanej karty usunięto wyłącznie nieaktualny status propozycji i punkt wznowienia; jej zakres i kryteria zachowano.

## WIT3 — propozycja gotowa do decyzji

- Rekomendacja: nowe ID r3 z niezmiennym predecessor=r1; jawne przepięcie zależności T14 tylko w draft; włączenie następcy do zakresu przez nowe W07 aktora U; przegląd T11 dopiero przy zależnościach approved/baselined bez suspect. T07 i zgody z DEC-PRO-008 zachowane.
- Propozycja zawiera warunki i skutki, zakres ośmiu ID (początkowo siedem w wydaniu), plan 54 kroków, diagram, wyrocznie i mutanty, propozycje S12/S13 oraz listę wpływu. T14 nie zwiększa ponownie wersji otwartej przez T05/T06; nie kasuje sam suspect. W07 dodaje r3, zachowuje stare r1 i nie dotyka accepted.
- Wykonano wyłącznie diagnostykę bieżącego v0.5 i próbę korekty T11 na kopii w pamięci. Nie wykonano pełnego WIT3 i nie ma dowodu v0.6. Kontrprzykład S4 jest znanym otwartym problemem; wcześniejsze 197 zielonych testów nie było dowodem całej właściwości.
- Przejrzano lokalny tekst PM.02.02–PM.02.03, SI.03.04–SI.03.05, SI.04.06. Format danych i reguły to rekomendowana polityka projektu, nie wymóg takiego schematu narzucony przez normę.
- Powód bramki: zmiana przyjętego modelu i uzupełnienie jego luki (§2.1 i §2.3 WSPOLPRACA). Właściciel decyzji: użytkownik; właściciel wdrożenia po zgodzie: agent. Zakres dostarczenia tej sesji zamyka się na gotowej propozycji, diagnostyce i punkcie wznowienia.

## Zgoda na konkretną zmianę — wdrożona przez DEC-PRO-008

- Źródłem reguł jest model/process.yaml v0.5; uzasadnienie zachowano w model/proposals/change-authorization.md. Instrukcja i wynik: examples/wit5/README.md oraz report.md.
- P00/T12 tworzą pytanie change związane z elementem, wersją i operacją. P02 zapisuje approved/rejected; pytania general mają answered. T05/T07 wymagają wskazanej, pasującej, pozytywnej i niewykorzystanej zgody. Stan consumed zmienia się atomowo z produktem; błąd lub granica badania nie zużywają zgody.
- Nie ma kolejnego pytania o wykonanie już zatwierdzonej operacji. T06/T08–T10 zachowują dotychczasowe bramki U. Zgoda dotyczy operacji otwarcia zmiany lub zastąpienia, nie treści przyszłej poprawki.
- WIT5 wykonuje zmianę po odbiorze, obowiązkowe W06 i odbiór wydania 2, zachowując identyczny rekord wydania 1. Sprawdzono także T10 przed/po odbiorze oraz wpływ zmiany spoza zakresu przez suspect.
- Pochodzenie luki: przegląd reguł i przygotowanie WIT5 ujawniły, że resolved nie rozróżnia zgody i odmowy oraz brakuje powiązania. Nie wykrył jej zakończony przebieg WIT1/WIT2/WIT4. Nowe testy i mutanty potwierdzają skutki usunięcia zabezpieczeń oraz działanie korekty.

## Decyzje

| ID | Decyzja | Źródło | Zmienia | Przejrzane |
|---|---|---|---|---|
| DEC-PRO-001 | DoD 1–10 i stos narzędzi (YAML, pytest z Hypothesis, TLA+ z TLC, odtworzenie historii vcs-lite). | Użytkownik 2026-10-23: „d1 tak” | — | — |
| DEC-PRO-002 | Kody, identyfikatory, atrybuty i kod źródłowy po angielsku w terminologii normy; proza, opisy i cytaty po polsku. | Użytkownik 2026-10-23: „d1 tak wykonaj rzetelenie i push” | `model/process.yaml` (v0.1 → v0.2), `docs/WSPOLPRACA.md`, szablon projektu. | `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `README.md`. |
| DEC-PRO-003 | Wariant A: odebrane wydanie jest niezmienne; odbiór dotyczy stanu z chwili podpisu, jak tag v1.0. Zmiany po odbiorze należą do następnego wydania. W06 tworzy nowy rekord, nie cofa starego. Odrzucone B: zakaz zmian po odbiorze blokuje projekt; C: cofanie accepted do in_preparation fałszuje protokół odbioru. | Użytkownik 2026-10-24: „d1 a” (cytat wskazany przez użytkownika do zapisu). | `model/process.yaml` (v0.2 → v0.3): `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7` → `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7`, `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo T00–T13, P00–P05, W01–W06, G0–G6, S1–S10, F1–F3, L1–L5, WIT1–WIT5, `README.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`, lista kontrolna w `informative/szablon-projektu/docs/SPEC.md` i materiały informacyjne. |
| DEC-PRO-004 | Wznowienie odłożonego elementu przez T10 także zmienia kompletność zakresu. T10 wywołuje invalidate_release: przy ready/reviewed wraca do in_preparation, przy accepted wymusza W06 bez zmiany odebranego rekordu. Rozszerza listę wyzwalaczy z DEC-PRO-003 o T10. | Użytkownik 2026-10-24: „Tak, uwzględnij T10” | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo `invalidate_release`, `S7b`, `S10`, `L1`, `L5`, T09 i bramki U. |
| DEC-PRO-005 | Przyjęcie modelu v0.3 i właściwości jako podstawy E2; zatwierdzenie INT-001–INT-016 i opisów WIT1–WIT5. Nie stanowi dowodu G/S/L ani odbioru całego projektu. | Użytkownik 2026-10-24: „przyjmuje” | `model/process.yaml`: status; `docs/WLASCIWOSCI.md`: status; `docs/INTERPRETACJE.md`: status INT-001–INT-016; `PLAN.md`: stan etapów; `docs/STAN.md`: zamknięcie bramki E1; `PROMPT-STARTOWY.md`: gałąź pobierana ze stanu prac. | `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `docs/STAN.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`; treść modelu i właściwości bez zmiany. |
| DEC-PRO-006 | Przyjąć korektę G3/G6 jako model v0.4: uzupełnić jawne adnotacje ISO bez zmiany zachowania procesu; mutant G3 usuwa T07/T08/T10. G6 jest indeksem powiązań, nie dowodem realizacji wszystkich składowych efektów normy. | Użytkownik 2026-10-24: „d1 tak.” | `model/process.yaml`: wersja i iso; `model/proposals/e2-structure.yaml`: status zastosowania; `docs/WLASCIWOSCI.md`: G3/G6; `docs/INTERPRETACJE.md`: odniesienie do decyzji; `mutants/g3_missing_resume.yaml`, `mutants/g3_missing_deferred_exits.yaml`: zastąpienie mutanta; `tests/test_model_contract.py`, `tests/test_structure_proposal.py`: kryteria przyjętej korekty; `scripts/check_model.py`; `README.md`; `docs/STAN.md`. | `model/process.yaml`, `model/proposals/e2-structure.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `mutants/g3_missing_resume.yaml`, `mutants/g3_missing_deferred_exits.yaml`, `tests/test_model_contract.py`, `tests/test_structure_proposal.py`, `scripts/check_model.py`, `README.md`, `docs/STAN.md`; ponadto G0–G6, S1–S10, L1–L5, WIT1–WIT5 i PLAN.md; nie zmieniono from/to/actor/guard/effects. |
| DEC-PRO-007 | Przyjąć zapisaną kartę celu i zakresu jako cel użytkowy projektu i włączyć ją do dokumentów zamiaru, z zachowaniem obecnego planu E2–E5 oraz DoD. Nie stanowi akceptacji propozycji zmiany pytań ani odbioru etapu. | Użytkownik 2026-10-24: „d1 tak” — odpowiedź na D1 o przyjęciu karty celu i zakresu. | `docs/KARTA-CELU-I-ZAKRESU.md`, `PLAN.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`, `README.md`, `informative/README.md`, `docs/STAN.md`, `scripts/check_model.py`; cel użytkowy i status karty. | `docs/KARTA-CELU-I-ZAKRESU.md`, `PLAN.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`, `README.md`, `informative/README.md`, `docs/STAN.md`, `scripts/check_model.py`, `informative/KARTA-CELU-I-ZAKRESU-2026-10-24.md`, `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`; DoD i kolejność E2–E5 zachowane. |
| DEC-PRO-008 | Przyjąć regułę zgody na konkretny element, wersję i operację T05/T07; rozróżnić zgodę od odmowy i atomowo oznaczać wykorzystanie zgody. Wdrożyć model v0.5, testy i WIT5; bez odbioru E2. | Użytkownik 2026-10-25: „D1 tak.” — odpowiedź na propozycję powiązania zgody z konkretną zmianą. | `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `model/proposals/change-authorization.md`, `docs/STAN.md`, `src/isomodel/loader.py`, `src/isomodel/execution.py`, `src/isomodel/expressions.py`, `src/isomodel/reporting.py`, `src/isomodel/probes.py`, `scripts/check_model.py`, `scripts/run_scenario.py`, `tests/`, `mutants/`, `examples/`, `README.md` | `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `model/proposals/change-authorization.md`, `docs/STAN.md`, `src/isomodel/loader.py`, `src/isomodel/execution.py`, `src/isomodel/expressions.py`, `src/isomodel/reporting.py`, `src/isomodel/probes.py`, `scripts/check_model.py`, `scripts/run_scenario.py`, `tests/`, `mutants/`, `examples/`, `README.md`; ponadto WIT1/WIT2/WIT4, S1–S11, L1–L5, INT-008/017 i karta celu. |

## Weryfikacja i lista kontrolna zmiany

- W sesji propozycji WIT3 uruchomiono diagnostykę na istniejącym wykonawcy i sprawdzono JSON planu (28 + 26 = 54 kroki, 2 pytania, 8 ID w proponowanej instancji). Ręcznie przejrzano warunki planowanych kroków, aktualizację powiązań i zakresu oraz listę wpływu. Pełnego WIT3 nie wykonano.
- Potwierdzono brak zmian w model/process.yaml, WLASCIWOSCI, INTERPRETACJE, PLAN, src/, tests/, mutants/, scripts/ i zależnościach. Nie ponawiano pełnej regresji niezmienionego wykonawcy; liczby poniżej dotyczą dostarczenia v0.5. Skrypt spójności i git diff --check sprawdzają dokumentację tej sesji.

- Końcowa regresja v0.5: `uv run --locked --offline pytest -q` — **197 passed w 7,77 s**, bez xfail i pominięć. Poprzednio 151; przyrost dodaje 46 przypadków, w tym Hypothesis, mutanty, testy polecenia i atomowości.
- `uv run --locked --offline python scripts/check_model.py` — **357 sprawdzeń spójności OK**, obejmuje DEC-PRO-008, datę, cytat, „Zmienia” ⊆ „Przejrzane”, pola zgody i S11. To kontrola strukturalna, nie dowód G/S/L.
- Pierwszy czerwony przebieg nowych testów zatrzymano po 3 błędach: brak obsługi atrybutów change w dotychczasowym wykonawcy. W pełnej regresji zaktualizowano cztery oczekiwania dotyczące starego interfejsu: trzy inicjalizacje pytań general i jeden brak obsługi T05, który obecnie zgłasza brak wskazanej zgody.
- Cztery polecenia run_scenario zakończone completed: WIT1 29, WIT2 33, WIT4 13 i WIT5 40 kroków. Wszystkie 26 wybranych mutantów raportów wykryte; raporty zawierają hashe modelu, scenariuszy, wykonawcy i uv.lock.
- Przegląd własny: model, właściwości S11/S10/S7a, INT-008, DoD, propozycja, inicjalizacja i atomowość pytań, interpretacja skutków, historia wydań, dowody i raporty. To nie niezależny przegląd końca E2. Kolejność E2–E5 i zależności środowiska zachowane.
- Przykłady są symulacjami; ich DEC i odbiory pozostają w danych wynikowych, bez aktualizacji rzeczywistych decyzji projektu. Pusty zakres i W03/W05 nadal jawnie nieobsługiwane.
- Historycznie: korekta G3/G6 miała czerwone wyniki 29 passed / 2 failed; przyrost WIT1 osiągnął 108 testów, WIT2/WIT4 151. Obecna regresja obejmuje wcześniejsze przypadki.

## Zakres obecnej implementacji

- Wczytywanie YAML, część walidacji G0/G4, projekcja grafów G1/G3, macierz G5 i audyt adnotacji G6 są zaimplementowane.
- Projekcje grafów ignorują guard/effects; dodatni wynik jest tylko warunkiem koniecznym osiągalności i braku ślepych stanów.
- Wykonawca interpretuje warunki i skutki WIT1/WIT2/WIT4/WIT5, w tym T05/T07, T12, unieważnienie gotowości, przechodnie suspect, W06 i obserwator zmiany po odbiorze. Osobne testy obejmują również T06 i T09/T10. Reguły są danymi z YAML; nie ma drugiej tabeli zachowania według ID. Nieobsługiwane reguły są jawnie raportowane, a odrzucone kroki oraz zapisy decyzji atomowe.
- Hypothesis bada odrzucanie powtórzonych kluczy YAML, kombinacje stanów zależności, aktorów, suspect i checks_ok dla T01(CODE) oraz kolejność pytań przy kombinacjach blocking. Hypothesis bada także kombinacje warunków zgody. Pełne S1–S11 przez maszynę stanów są jeszcze przed nami.
- Pełne G2, pozostała semantyka, pełna mutacja, świadki wygenerowane przez TLC i dowody TLA+ nie są wykonane. Opisano WIT1–WIT5; WIT1/WIT2/WIT4/WIT5 mają wykonanie deterministyczne w E2, bez zastępowania E3.
- Zależności: PyYAML 6.0.3, networkx 3.6.1, pytest 9.1.1, Hypothesis 6.151.10 w pyproject.toml/uv.lock; lokalne .venv. Wizualizacja korzysta z już zainstalowanego Graphviz, bez nowych zależności Pythona.

## Ocena używalności — na pytanie użytkownika

- Klasyfikacja: dokumentacja zarządzania tym projektem; specyfikacja projektowanego procesu; prototyp narzędzi analizy modelu; materiały wdrożeniowe i edukacyjne. To różne poziomy gotowości, nie jeden gotowy produkt.
- Używalne obecnie: kontrakt współpracy i rejestr decyzji w pracy ręcznej, model i diagramy do przeglądu reguł, skrypty do analizy samego modelu, szablon jako punkt startowy do adaptacji.
- Brak gotowości do automatycznego sprawdzania rzeczywistego projektu: jest wykonanie podzbioru guard/effects i czterech scenariuszy, lecz brakuje pełnej semantyki, obsługi trwałego stanu rzeczywistego projektu oraz adaptera do dokumentów/historii repozytorium. Raport WIT1 dotyczy sztucznej instancji; pełne testy zachowania i dowody pozostają przed nami.
- Szablon odwołuje się do tests/test_traceability.py i generowanego TRACE.md, lecz nie dostarcza tego programu; wymaga dopracowania i pilotażu przed uznaniem za gotowy pakiet wdrożeniowy.
- Perspektywa PO: WIT1 dostarcza pierwszą demonstrację od początku do odbioru na sztucznej instancji; użyteczność w rzeczywistym projekcie pozostaje do zbadania. Perspektywa PM: E2 trwa, E3–E5 nie są dostarczone. Perspektywa developera: działa biblioteka walidacji, analizy grafów i wykonawca podzbioru procesu, nie pełny silnik.
- Skorygowane uzasadnienie sprawdzianów: wycofanie/zastąpienie REQ wybrano heurystycznie na podstawie znanego ryzyka, bez wykazania największego kosztu lub przekrojowości. Pierwszą demonstracją powinien być WIT1; WIT5 i WIT3 uzupełniają go o kolejne wydania i wpływ zmian. Demonstracja na przykładzie w E2 nie zastępuje odtworzenia rzeczywistego projektu w E4/E5.
- To ocena i rekomendacja, bez zmiany modelu, kolejności etapów, DoD ani rozszerzenia zakresu o interfejs graficzny. Nie zapisano nowej decyzji użytkownika.

## Roadmapa i gotowość do WIT1

- Na pytanie użytkownika przygotowano `informative/ROADMAPA-2026-10-24.md`: propozycję kolejności dostaw w ramach istniejących E2–E5, bez zmiany PLAN.md, modelu i DoD.
- WIT1 wykonano na polecenie użytkownika: „wykonaj rzeteleni wit1”. Realizacja mieści się w zaakceptowanym E2, nie wymagała zmiany semantyki ani nowej DEC.
- Uzyskany wynik: 7 elementów, 29 kroków T00/T01/T02/T04/W01/W02/W04, jedno wydanie accepted z migawką; jawne dane checks_ok/tests_ok i dowody demonstracyjne; raport kroków oraz odrzucania prób obejścia bramek. Liczba kroków i stany zostały potwierdzone wykonaniem.
- Proponowana kolejność implementacji w E2: WIT1 → WIT2/WIT4 (pytania potrzebne do T05) → WIT5 → WIT3 → pełne sprawdzenia i mutanty. Następnie E3 (TLC), E4 (historia), E5 (pakiet wdrożeniowy).
- E2 wykonuje podaną ścieżkę jako test integracyjny; formalne generowanie i przegląd świadków pozostają w E3. Każde rozszerzenie lub zmiana przyjętej semantyki wraca do decyzji użytkownika.
- Nie podano terminów ani twierdzenia o najdroższym przyroście. WIT1 daje pierwszy pomiar wykonania sprawdzeń, nie wiarygodną estymację prac nad resztą semantyki i dowodami.
- Podczas przygotowania roadmapy zmieniono wyłącznie dokumentację planowania i punkt wznowienia; nie uruchamiano ponownie testów niezmienionego kodu. Nie zapisano nowej DEC.

## Historia przyrostu WIT1 — wynik i ówczesne ograniczenia

- TDD: pierwsze 50 testów było czerwonych (`NotImplementedError` wykonawcy). Następnie dodano interpreter, atomowe kroki, odtworzenie oraz kolejne testy wejść, obserwatora, granic, Hypothesis, mutantów i polecenia. Końcowy wynik całego repozytorium: 108 passed.
- `uv run --locked --offline python scripts/run_wit1.py --output artifacts/wit1`: completed, 29 kroków. Wszystkie elementy baselined w wersji 1, bez suspect; wydanie 1 accepted. Raport zawiera rzeczywiste stany, aktorów, warunki i cytaty demonstracyjne oraz SHA-256 danych i kodu. Kopia Markdown w examples/wit1/report.md została przeczytana i sprawdzona względem wyniku JSON.
- Siedem celowych uszkodzeń z mutants/wit1_gates.json wykryto: role, pominięcie zatwierdzenia/weryfikacji, niegotowa zależność, niekompletna gotowość/odbiór, pominięcie przeglądu R. To przypadki S1/S2/S3/S4/S7a/S7b/S8, nie 100% mutacji E2.
- W testach izolacji zmiana zwróconego stanu nie zmienia wcześniejszych kroków ani migawki; wejściowy model i scenariusz pozostają identyczne. Dwukrotne uruchomienie polecenia daje identyczne wyniki i nie zmienia dokumentów/modelu repozytorium. Dowody symulacyjne nie stają się rzeczywistymi DEC ani tagami.
- Decyzje agenta: mały interpreter bez eval, stan przekazywany jawnie i kopiowany, osobny format dowodów demonstracyjnych, pełny ślad JSON odtwarzany w ignorowanym artifacts/, raport Markdown w repozytorium. Uzasadnienia i format wejść: examples/wit1/README.md.
- W chwili dostarczenia WIT1 wykonawca nie obsługiwał helperów zmian, pytań, nowego wydania ani pustego zakresu. Pytania dodano w następnym przyroście opisanym poniżej. Dla pustego zakresu długie wiązanie kwantyfikatora w W01 może zmienić znaczenie globalnych testów/pytania; przypadek nadal jest jawnie unsupported. Przed poszerzeniem potrzebna jest analiza jednoznacznego zapisu W01. Instancja WIT1 ma niepusty zakres i nie wymaga zmiany modelu.
- Wstrzykiwane stany w części testów są testami warunków, nie świadkami osiągalności. checks_ok/tests_ok są założeniami. R jest rolą symulowanego zdarzenia, nie rzeczywistym niezależnym recenzentem tej implementacji. Przegląd niezależny i bramka użytkownika pozostają na koniec etapu E2.
- Lista kontrolna: przejrzano model, właściwości, roadmapę WIT1, kod, testy, scenariusz, mutanty, raport, README i stan prac. Nie zmieniono zaakceptowanej semantyki, planu ani zależności. Nie ogłoszono zakończenia E2 ani spełnienia DoD 7.

## Historia przyrostu WIT2/WIT4

- Początkowe kryteria: 27 failed, 7 passed. Istniejący interpreter wykonywał już T03, natomiast pytania kończyły się błędem wejścia/brakiem obsługi. Po implementacji i rozszerzeniu kryteriów cały zestaw ma 151 przechodzących testów.
- WIT2 rozszerza WIT1 o dwa odrzucenia r1 i ponowną weryfikację. Wersja pozostaje 1, licznik rośnie do 2; trzecie T03 jest blokowane, T02 pozostaje dostępne. Przebieg kończy się wydaniem accepted po 33 krokach. Alternatywne wycofanie/odłożenie produktu wymaga helperów, które pozostają poza tym przyrostem.
- WIT4 wykonuje 13 kroków na trzech pytaniach. P03 nie tworzy DEC ani nie zmienia age; starsze q1 wraca przed q2 w tej samej klasie priorytetu. P02 wymaga jawnego unambiguous_answer=true i dowodu. P04 nie pozwala odłożyć pytania blokującego; P05 dopuszcza U/A i zachowuje age. Wszystkie pytania kończą resolved; powstają dokładnie trzy DEC demonstracyjne. Wydanie pozostaje in_preparation.
- Decyzje agenta: ID pytania jako metadane instancji; age jako kolejny numer zgłoszenia; blocking jawnie podany w P00. Pola i stany pochodzą z question_variables. Nowe DEC są dziennikiem skutków step.records/result.records, nie nową zmienną procesu; odpowiada to INT-004. Dane odpowiedzi są nakładane tylko na bieżący krok, nie przenoszone automatycznie do następnego.
- Dowody: testy atomowości wymuszają błąd po przygotowaniu rekordu DEC i wykazują brak częściowego resolved/zapisu; testy poleceń potwierdzają identyczne raporty w dwóch wykonaniach oraz brak zmian dokumentów i modelu. Test zmiany wszystkich ID P wykazuje odczyt reguł z danych. Testy kolejki uwzględniają blocking_first, kolejność zgłoszenia niezależną od ID, P03 oraz odłożenie asked i wznowienie.
- Mutanty: 2 w mutants/wit2_gates.json i 7 w mutants/wit4_gates.json; wszystkie wykryte. Razem z WIT1: 16 wybranych mutantów wykonania. Obejmuje to skończone sprawdzenia S9/L4 i czułość na LIFO, nie dowód żywotności L2 ani pełne pokrycie E2.
- Polecenie wspólne: `uv run --locked --offline python scripts/run_scenario.py --scenario WIT2 --output artifacts/wit2` (analogicznie WIT4/WIT1). Dotychczasowe run_wit1.py zachowano jako wejście do wspólnego runnera. Instrukcja: examples/questions/README.md. Przeczytano wygenerowane raporty, sprawdzono liczbę kroków, nowe DEC i wyniki mutantów; kopie Markdown zapisano w examples/questions/. Pełny JSON jest odtwarzalny w artifacts/.
- W przyroście WIT2/WIT4 kind/about pozostawiono otwarte. Sprawę zamknął kolejny przyrost v0.5 / WIT5 przez DEC-PRO-008; pytania WIT4 są teraz general, a pytania o zmianę mają jawne powiązania.
- Przejrzano P00–P05, T03, S1/S9/L2/L4, INT-004/010/011, regułę frame, scenariusze, kod, testy, mutanty, raporty, instrukcje i punkt wznowienia. Nie zmieniono zaakceptowanej semantyki, planu ani zależności; nie zapisano nowej DEC i nie przedstawiono odbioru E2.

## Eksperymenty i pilotaż — wyjaśnienie na pytanie użytkownika

- WIT1 w E2 to test integracyjny wykonujący zadaną ścieżkę na sztucznej instancji. Pilotaż z rzeczywistym projektem ma inny cel: sprawdzenie użyteczności, kosztu obsługi i skutków narzędzia w pracy. Sam pozytywny WIT1 nie rozstrzyga tych kwestii.
- Sprawdzono lokalny tekst ISO/IEC 29110-5-1-2: §5 dopuszcza różne podejścia wytwórcze; PM.01.09 obejmuje ryzyka, PM.01.10 strategię wersjonowania i linie bazowe, PM.01.15 repozytorium, PM.02.02–03 ocenę i zatwierdzanie zmian, PM.03.04 zgodę na zmianę wymagań/planu. Nie wyprowadzamy z tego obowiązku konkretnego katalogu ani osobnego typu EXP w modelu.
- Źródło przykładu praktyki: NASA NPR 7120.7A §5.1.b–c rozróżnia PoC, prototyp w środowisku testowym oraz pilotaż dla ograniczonej grupy w środowisku produkcyjnym. To przykład zasad NASA, nie dodatkowe wymaganie dla naszego projektu: https://nodis3.gsfc.nasa.gov/displayDir.cfm?Internal_ID=N_PR_7120_007A_&page_name=Chapter5.
- Rekomendacja: rozdzielać cel artefaktu (produkt/test/przykład/eksperyment/dowód), jego dojrzałość oraz moc wiążącą. Zapisanie pliku w Git i pomyślna weryfikacja raportu nie oznaczają zatwierdzenia zawartych w nim zaleceń.
- Proponowana izolacja: osobny branch i opcjonalny worktree dla prób; osobne dane, katalogi wyników i środowisko wykonania. Worktree dzieli część metadanych Git i nie jest granicą uprawnień ani izolacją usług. Źródło: https://git-scm.com/docs/git-worktree. W przypadku agentów ograniczenia dostępu trzeba egzekwować uprawnieniami narzędzi, nie samą instrukcją w pliku.
- Proponowany przepływ wiedzy: pytanie i kryterium rozstrzygnięcia → wykonanie w określonym limicie → dowody i ograniczenia → przegląd → propozycja zmiany → decyzja w zakresie wymaganym kontraktem → aktualizacja specyfikacji/testów/kodu. Zachowywać także wyniki negatywne i nierozstrzygające; kod eksperymentu nie musi wejść do produktu.
- Minimalny zapis próby: ID, pytanie/hipoteza, bazowy commit i wersja modelu, wejście, polecenie i środowisko, kryterium wyniku, limit, wynik z dowodami, ograniczenia oraz odwołanie do dalszej decyzji. Operator ustala cel i granice; agent wykonuje i raportuje; niezależny przegląd ocenia dowody; operator rozstrzyga zmiany wymagające jego zgody. W ramach wcześniej udzielonego zakresu agent działa bez ponawiania pytań.
- Dla WIT1 rekomendowane są dane i testy w tests/ oraz wspólny wykonawca w src/isomodel; przykład powinien używać tego samego wykonawcy. Symulowane decyzje U i accepted muszą pozostać w instancji testowej, bez aktualizacji rzeczywistych DEC i protokołu odbioru projektu.
- Ewentualne metadane context_id/purpose/base_commit należą na początek do opisu uruchomienia. Nie są dziś polami wiążącego modelu. Jeżeli izolacja eksperymentów miałaby być dowodzoną właściwością procesu, potrzebna będzie osobna propozycja modelu, właściwości i mutantów, potem decyzja użytkownika.
- To wyjaśnienie i rekomendacja z sesji poprzedzającej wykonanie WIT1, bez nowej DEC, zmiany semantyki v0.4, planu ani rozpoczęcia pilotażu. W tamtej sesji zmieniono tylko punkt wznowienia; testy kodu nie były ponawiane. WIT1 wykonano później zgodnie z zapisem powyżej.

## Repozytorium

- Użytkownik scalił poprzednią gałąź e1-model do main (PR #1, eceaf0e). Model v0.3 opublikowano na e1-model w 7e4856d; akceptację E1 i pierwszy przyrost E2 na e2-checks w c38a4b7.
- Bieżąca gałąź: `e2-checks`; WIT1 zapisano w 2b830e0, WIT2/WIT4 w 9bfebae, kartę celu w 360a90d. WIT5 i v0.5 zapisano i wypchnięto w e5fc842; obecna propozycja WIT3 jest przekazywana na tej samej gałęzi. Scalenie do main wymaga osobnej zgody użytkownika.

## Sprawy otwarte

| Sprawa | Właściciel | Następny krok |
|---|---|---|
| Pozostała implementacja E2: G2, warunki/skutki, bezpieczeństwo i mutanty | agent | kontynuować od przyjętego modelu v0.5; odbiór E2 dopiero po spełnieniu kryteriów |
| WIT3: następca, powiązania, zakres i korekta T11 | użytkownik | decyzja o gotowej propozycji model/proposals/wit3-replacement.md; potem agent wdraża v0.6 i WIT3 |
| Odtworzone naruszenie S4 przez T11 w v0.5 | agent | po decyzji wdrożyć opisane w propozycji wzmocnienie i test kontrprzykładu; do tego czasu jawnie zachować ograniczenie |
| Zakres kwantyfikatora W01 przy pustym zakresie wydania | agent | przed rozszerzeniem wykonawcy przeanalizować jednoznaczny zapis globalnych testów/pytania; ewentualną zmianę modelu przedstawić do decyzji; nie blokuje wykonanego WIT1 |
| Historyczne materiały informative/ | agent | przy E5 uwzględnić INT-017 w nowym materiale; nie przepisywać migawek sesji 2026-10-23 |
| REQ-210 i REQ-211 dla szablonu | użytkownik | decyzja; opis w informative/SESJA-2026-10-23.md §5 |
| Instalacja Javy i TLA+ (E3) | użytkownik | zgoda przed E3 |
| Dostęp do historii vcs-lite (E4) | użytkownik | zgoda przed E4 |
| Porządki w vcs-lite | użytkownik | decyzja, czy i kiedy |

## Decyzje agenta do podważenia

- 2026-10-25: diagnostykę i plan zdarzeń umieszczono obok propozycji, poza fixtures produkcyjnego runnera, aby przyszłe reguły nie stały się obowiązujące przez sam zapis pliku. Badanie T11 używa kopii w pamięci; baza v0.5 pozostaje niezmienna.
- 2026-10-25: do podpisu przygotowano jeden spójny pakiet WIT3, w tym konieczną korektę przeglądu T11; brak nowej DEC oznacza, że są to rekomendacje agenta, nie przyjęta polityka. Szczegóły wyboru ośmiu ID i jawnych operacji w propozycji.

- 2026-10-25: ID pytania tworzonego przez T12 jest wejściem zdarzenia, jak dla P00; wersja i powiązanie pochodzą ze stanu/modelu, aby scenariusze były deterministyczne bez własnej polityki numerowania w procesie.
- 2026-10-25: formalny predykat zgody i wyrażenia rekordów W06 są czytane z YAML; helper invalidate_release obsługuje wyłącznie obecną definicję tekstową i odrzuca zmienioną, aby nie wykonywać milcząco nieznanej semantyki. Pełny interpreter zdań nie należy do tego przyrostu.
- 2026-10-25: zachowano wszystkie wcześniejsze scenariusze i odświeżono ich raporty na v0.5; izolowane testy pól i consumed jawnie oznaczono jako wstrzyknięte stany, żeby nie mylić kontroli predykatu ze świadkiem osiągalności.

- Wizualizacja jest dokumentacją w repozytorium, a nie nową aplikacją ani rozszerzeniem zakresu E2. Grafy korzystają z modelu; ocena wsparcia pakietów jest jawnie interpretacją autora.
- Uzasadnienie korekty pozostaje w model/proposals/e2-structure.yaml ze statusem applied i DEC-PRO-006; źródłem zachowania jest nadal wyłącznie model/process.yaml.
- Pozostają wcześniejsze rozstrzygnięcia: oddzielny znacznik oczekującej zmiany, kopiowanie migawki, priorytet W06, granice eksploracji odrębne od zasad procesu, zabezpieczenie T11, pytanie blokujące w T12 i nieuwzględnianie nieaktywnych elementów w dostawie.
