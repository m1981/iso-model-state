# Stan prac

Nadpisywany na końcu każdej sesji. Zaktualizowano: 2026-10-24, model v0.4, rozróżnienie WIT1, eksperymentów i pilotażu oraz propozycja izolacji pracy eksperymentalnej.

## Gdzie jesteśmy

- **Etap:** E2 w toku. Model v0.3 przyjęty przez DEC-PRO-005; korekta v0.4 przyjęta przez DEC-PRO-006. Nie ma oczekującej decyzji o G3/G6.
- **Ostatnio zrobione:**
  - zastosowano korektę adnotacji ISO: wszystkie przejścia mają iso, a jawne powiązania obejmują 14 efektów PM/SI;
  - zastąpiono nieskutecznego mutanta G3: aktywny usuwa T07/T08/T10; poprzedni zachowano jako superseded;
  - 31 testów przechodzi, w tym dwa uprzednio czerwone kryteria G3/G6; testy korekty sprawdzają teraz model wiążący;
  - na prośbę użytkownika przygotowano informacyjny przewodnik, trzy diagramy SVG/PNG i mapowanie wsparcia dziewięciu pakietów Aneksu E: `informative/WIZUALIZACJA-2026-10-24.md`;
  - diagramy generuje `scripts/render_process.py` z YAML przez dostępny Graphviz; nie jest to symulator.
- **Następny krok:** rozpocząć wykonywalny WIT1 w ramach zaakceptowanego E2: czerwone testy scenariusza i bramek, potem wykonawca potrzebnych warunków/skutków oraz raport 29 kroków. Zakres opisany w informative/ROADMAPA-2026-10-24.md. Dalsze G/S, mutanty i dowody pozostają w planie; nie uznawać E2 za zakończone.

## Bramka E1

Przyjęta przez DEC-PRO-005. Korekta G3/G6 zatwierdzona przez DEC-PRO-006 nie zmienia zachowania przejść ani polityki wydań. G6 sprawdza śledzenie powiązań, nie pełną zgodność procesu z normą.

## Decyzje

| ID | Decyzja | Źródło | Zmienia | Przejrzane |
|---|---|---|---|---|
| DEC-PRO-001 | DoD 1–10 i stos narzędzi (YAML, pytest z Hypothesis, TLA+ z TLC, odtworzenie historii vcs-lite). | Użytkownik 2026-10-23: „d1 tak” | — | — |
| DEC-PRO-002 | Kody, identyfikatory, atrybuty i kod źródłowy po angielsku w terminologii normy; proza, opisy i cytaty po polsku. | Użytkownik 2026-10-23: „d1 tak wykonaj rzetelenie i push” | `model/process.yaml` (v0.1 → v0.2), `docs/WSPOLPRACA.md`, szablon projektu. | `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `README.md`. |
| DEC-PRO-003 | Wariant A: odebrane wydanie jest niezmienne; odbiór dotyczy stanu z chwili podpisu, jak tag v1.0. Zmiany po odbiorze należą do następnego wydania. W06 tworzy nowy rekord, nie cofa starego. Odrzucone B: zakaz zmian po odbiorze blokuje projekt; C: cofanie accepted do in_preparation fałszuje protokół odbioru. | Użytkownik 2026-10-24: „d1 a” (cytat wskazany przez użytkownika do zapisu). | `model/process.yaml` (v0.2 → v0.3): `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7` → `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7`, `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo T00–T13, P00–P05, W01–W06, G0–G6, S1–S10, F1–F3, L1–L5, WIT1–WIT5, `README.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`, lista kontrolna w `informative/szablon-projektu/docs/SPEC.md` i materiały informacyjne. |
| DEC-PRO-004 | Wznowienie odłożonego elementu przez T10 także zmienia kompletność zakresu. T10 wywołuje invalidate_release: przy ready/reviewed wraca do in_preparation, przy accepted wymusza W06 bez zmiany odebranego rekordu. Rozszerza listę wyzwalaczy z DEC-PRO-003 o T10. | Użytkownik 2026-10-24: „Tak, uwzględnij T10” | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo `invalidate_release`, `S7b`, `S10`, `L1`, `L5`, T09 i bramki U. |
| DEC-PRO-005 | Przyjęcie modelu v0.3 i właściwości jako podstawy E2; zatwierdzenie INT-001–INT-016 i opisów WIT1–WIT5. Nie stanowi dowodu G/S/L ani odbioru całego projektu. | Użytkownik 2026-10-24: „przyjmuje” | `model/process.yaml`: status; `docs/WLASCIWOSCI.md`: status; `docs/INTERPRETACJE.md`: status INT-001–INT-016; `PLAN.md`: stan etapów; `docs/STAN.md`: zamknięcie bramki E1; `PROMPT-STARTOWY.md`: gałąź pobierana ze stanu prac. | `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `docs/STAN.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`; treść modelu i właściwości bez zmiany. |
| DEC-PRO-006 | Przyjąć korektę G3/G6 jako model v0.4: uzupełnić jawne adnotacje ISO bez zmiany zachowania procesu; mutant G3 usuwa T07/T08/T10. G6 jest indeksem powiązań, nie dowodem realizacji wszystkich składowych efektów normy. | Użytkownik 2026-10-24: „d1 tak.” | `model/process.yaml`: wersja i iso; `model/proposals/e2-structure.yaml`: status zastosowania; `docs/WLASCIWOSCI.md`: G3/G6; `docs/INTERPRETACJE.md`: odniesienie do decyzji; `mutants/g3_missing_resume.yaml`, `mutants/g3_missing_deferred_exits.yaml`: zastąpienie mutanta; `tests/test_model_contract.py`, `tests/test_structure_proposal.py`: kryteria przyjętej korekty; `scripts/check_model.py`; `README.md`; `docs/STAN.md`. | `model/process.yaml`, `model/proposals/e2-structure.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `mutants/g3_missing_resume.yaml`, `mutants/g3_missing_deferred_exits.yaml`, `tests/test_model_contract.py`, `tests/test_structure_proposal.py`, `scripts/check_model.py`, `README.md`, `docs/STAN.md`; ponadto G0–G6, S1–S10, L1–L5, WIT1–WIT5 i PLAN.md; nie zmieniono from/to/actor/guard/effects. |

## Weryfikacja i lista kontrolna zmiany

- `uv run --locked --offline pytest -q`: **31 passed**; bez xfail i pomijania testów. G3/G6 poprawiono według przyjętej propozycji, nie wyłączono kryteriów.
- `uv run --locked --offline python scripts/check_model.py`: **336 sprawdzeń spójności OK**; obejmuje także cytat i „Zmienia” ⊆ „Przejrzane” dla DEC-PRO-005/006. `git diff --check` bez błędów.
- Zachowanie: porównanie z poprzednim commitem potwierdza identyczne from/to/actor/guard/effects i pozostałe reguły; w modelu zmieniono tylko wersję i adnotacje iso.
- Diagramy wygenerowano i obejrzano jako PNG; wersje SVG służą do powiększania i publikacji. Przewodnik jest migawką informacyjną, nie nowym źródłem reguł.
- Przejrzano model, właściwości, interpretacje, testy, mutanty, uzasadnienie adnotacji, README, plan i stan. Zaktualizowane definicje oraz odwołania są w tej samej zmianie. Stary mutant jest jawnie zastąpiony.
- Przeczytano lokalny Aneks E. Ocena wsparcia jest mapowaniem tematów a–i na model, nie audytem pełnej zawartości osobno publikowanych pakietów. Żaden pakiet nie jest uznany za w pełni wdrożony.
- Wcześniejszy czerwony przebieg E2: 29 passed, 2 failed (G3/G6). TDD walidatora: powtórzony klucz YAML, nieznana zależność i wielokrotny cel dawały DID NOT RAISE ModelError, po implementacji przechodzą.

## Zakres obecnej implementacji

- Wczytywanie YAML, część walidacji G0/G4, projekcja grafów G1/G3, macierz G5 i audyt adnotacji G6 są zaimplementowane.
- Projekcje grafów ignorują guard/effects; dodatni wynik jest tylko warunkiem koniecznym osiągalności i braku ślepych stanów.
- Obecne Hypothesis bada odrzucanie powtórzonych kluczy YAML; testy bezpieczeństwa S1–S10 przez maszynę stanów są jeszcze przed nami.
- G2, interpretacja warunków/skutków, pełna mutacja, wygenerowane świadki i dowody TLA+ nie są wykonane. Ręcznie opisano WIT1–WIT5, w tym zmianę po odbiorze i przypadek T10.
- Zależności: PyYAML 6.0.3, networkx 3.6.1, pytest 9.1.1, Hypothesis 6.151.10 w pyproject.toml/uv.lock; lokalne .venv. Wizualizacja korzysta z już zainstalowanego Graphviz, bez nowych zależności Pythona.

## Ocena używalności — na pytanie użytkownika

- Klasyfikacja: dokumentacja zarządzania tym projektem; specyfikacja projektowanego procesu; prototyp narzędzi analizy modelu; materiały wdrożeniowe i edukacyjne. To różne poziomy gotowości, nie jeden gotowy produkt.
- Używalne obecnie: kontrakt współpracy i rejestr decyzji w pracy ręcznej, model i diagramy do przeglądu reguł, skrypty do analizy samego modelu, szablon jako punkt startowy do adaptacji.
- Brak gotowości do automatycznego sprawdzania rzeczywistego projektu: nie ma wykonania guard/effects, trwałej instancji projektu i zdarzeń, adaptera do dokumentów/historii repozytorium ani raportu naruszeń dla użytkownika projektu. Pełne testy zachowania i dowody pozostają przed nami.
- Szablon odwołuje się do tests/test_traceability.py i generowanego TRACE.md, lecz nie dostarcza tego programu; wymaga dopracowania i pilotażu przed uznaniem za gotowy pakiet wdrożeniowy.
- Perspektywa PO: brakuje demonstracji pełnego przypadku użycia z wynikiem dla użytkownika. Perspektywa PM: plan i bramki istnieją, ale E2 trwa, a E3–E5 nie są dostarczone. Perspektywa developera: działa część biblioteki walidacji i analizy grafów, nie pełny silnik procesu.
- Skorygowane uzasadnienie sprawdzianów: wycofanie/zastąpienie REQ wybrano heurystycznie na podstawie znanego ryzyka, bez wykazania największego kosztu lub przekrojowości. Pierwszą demonstracją powinien być WIT1; WIT5 i WIT3 uzupełniają go o kolejne wydania i wpływ zmian. Demonstracja na przykładzie w E2 nie zastępuje odtworzenia rzeczywistego projektu w E4/E5.
- To ocena i rekomendacja, bez zmiany modelu, kolejności etapów, DoD ani rozszerzenia zakresu o interfejs graficzny. Nie zapisano nowej decyzji użytkownika.

## Roadmapa i gotowość do WIT1

- Na pytanie użytkownika przygotowano `informative/ROADMAPA-2026-10-24.md`: propozycję kolejności dostaw w ramach istniejących E2–E5, bez zmiany PLAN.md, modelu i DoD.
- Gotowość: można rozpocząć implementację WIT1 na obecnym modelu i środowisku; nie ma jeszcze wykonywalnej ścieżki ani silnika procesu. Nie zidentyfikowano nowej decyzji biznesowej blokującej rozpoczęcie tego przyrostu.
- Najbliższy wynik: 7 elementów, 29 kroków T00/T01/T02/T04/W01/W02/W04, jedno wydanie accepted z migawką; jawne dane checks_ok/tests_ok i dowody demonstracyjne; raport kroków oraz odrzucania prób obejścia bramek. Liczba kroków jest wyprowadzona ręcznie, nie pochodzi z wykonania symulatora.
- Proponowana kolejność implementacji w E2: WIT1 → WIT2/WIT4 (pytania potrzebne do T05) → WIT5 → WIT3 → pełne sprawdzenia i mutanty. Następnie E3 (TLC), E4 (historia), E5 (pakiet wdrożeniowy).
- E2 wykonuje podaną ścieżkę jako test integracyjny; formalne generowanie i przegląd świadków pozostają w E3. Każde rozszerzenie lub zmiana przyjętej semantyki wraca do decyzji użytkownika.
- Nie podano terminów ani twierdzenia o najdroższym przyroście: brak pomiarów. Oszacowania należy uzupełnić po pierwszym wykonawcy WIT1 i rozpoznaniu semantyki.
- Podczas przygotowania roadmapy zmieniono wyłącznie dokumentację planowania i punkt wznowienia; nie uruchamiano ponownie testów niezmienionego kodu. Nie zapisano nowej DEC.

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
- To wyjaśnienie i rekomendacja, bez nowej DEC, zmiany semantyki v0.4, planu ani rozpoczęcia pilotażu. Następny krok pozostaje WIT1. W tej sesji zmieniono tylko punkt wznowienia; testy kodu nie były ponawiane.

## Repozytorium

- Użytkownik scalił poprzednią gałąź e1-model do main (PR #1, eceaf0e). Model v0.3 opublikowano na e1-model w 7e4856d; akceptację E1 i pierwszy przyrost E2 na e2-checks w c38a4b7.
- Bieżąca gałąź: `e2-checks`; korekta v0.4 i przewodnik są przekazywane na tej gałęzi. Scalenie do main wymaga osobnej zgody użytkownika.

## Sprawy otwarte

| Sprawa | Właściciel | Następny krok |
|---|---|---|
| Pozostała implementacja E2: G2, warunki/skutki, bezpieczeństwo i mutanty | agent | kontynuować od przyjętego modelu v0.4; odbiór E2 dopiero po spełnieniu kryteriów |
| Historyczne materiały informative/ | agent | przy E5 uwzględnić INT-017 w nowym materiale; nie przepisywać migawek sesji 2026-10-23 |
| REQ-210 i REQ-211 dla szablonu | użytkownik | decyzja; opis w informative/SESJA-2026-10-23.md §5 |
| Instalacja Javy i TLA+ (E3) | użytkownik | zgoda przed E3 |
| Dostęp do historii vcs-lite (E4) | użytkownik | zgoda przed E4 |
| Porządki w vcs-lite | użytkownik | decyzja, czy i kiedy |

## Decyzje agenta do podważenia

- Wizualizacja jest dokumentacją w repozytorium, a nie nową aplikacją ani rozszerzeniem zakresu E2. Grafy korzystają z modelu; ocena wsparcia pakietów jest jawnie interpretacją autora.
- Uzasadnienie korekty pozostaje w model/proposals/e2-structure.yaml ze statusem applied i DEC-PRO-006; źródłem zachowania jest nadal wyłącznie model/process.yaml.
- Pozostają wcześniejsze rozstrzygnięcia: oddzielny znacznik oczekującej zmiany, kopiowanie migawki, priorytet W06, granice eksploracji odrębne od zasad procesu, zabezpieczenie T11, pytanie blokujące w T12 i nieuwzględnianie nieaktywnych elementów w dostawie.
