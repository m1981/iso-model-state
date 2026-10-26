# Niezależny przegląd kontraktu API procesu

Data: 2026-10-26. Recenzent: osobny przebieg agenta R, bez historii tworzenia dokumentu. Przedmiot: [process-api-contract.md](process-api-contract.md). Baza repozytorium: `2061c52`. **Status po ponownej weryfikacji: R01–R03 zamknięte; brak otwartych ustaleń blokujących przedstawienie kontraktu operatorowi do decyzji o kierunku.** Oceniony końcowy SHA-256: `316081b451820af018db4fd7ded87e0dbd37f3dbfe0c512dd9af040faa6ddd93`. To przegląd projektu dokumentu, nie odbiór E2, architektury ani systemu przez operatora.

Poniższe pierwotne ustalenia zachowano jako historię przeglądu wersji SHA-256 `7c9e4eba6fba66b83bec2e161fb9c8c4a05d84527c0c2f681de4d4bc7149c6c9`. Ich status rozstrzyga końcowa sekcja „Ponowna weryfikacja”. Pierwszy wynik obejmował dwa ustalenia blokujące i jedno wymagane doprecyzowanie.

## Pierwszy wynik — zapis historyczny

Kierunek architektury odpowiada celowi użytkowemu: oddziela pracę A od decyzji U, zamraża przedmiot zgody i odbioru oraz nie utożsamia deklaracji agenta z dowodem runnera. Główny ślad zachowuje aktorów i warunki v0.7. Nie znalazłem zmiany modelu ani przypisania T05/T04 agentowi. Kontrakt uczciwie określa nowe zobowiązania AX01–AX06 i nie przypisuje im dowodów E2.

Przed przedstawieniem dokumentu jako kompletnego kontraktu opisanego scenariusza należy zamknąć R01–R02 i doprecyzować R03. Nie są to wykazane podatności istniejącej implementacji: API jeszcze nie istnieje. Są to miejsca, w których dwie implementacje zgodne z różnymi fragmentami opisu mogłyby zachować się inaczej, także nie osiągnąć opisanego poprawnego wyniku.

## Zakres i metoda

Przeczytano PROMPT-STARTOWY.md, docs/WSPOLPRACA.md, docs/STAN.md, kartę celu, PLAN.md, model/process.yaml, docs/WLASCIWOSCI.md, docs/INTERPRETACJE.md, regułę pierwszeństwa informative/ i cały kontrakt. Sprawdzono także miejsca adapterowania dowodów w istniejącym wykonawcy symulatora. Analiza objęła ślad poprawny, odmowę, próbę podszycia się pod U/R, nieaktualne dowody, konkurencję, retry oraz awarie Git.

Nie uruchamiano testów integracyjnych nieistniejącego API ani ponownej regresji E2, nie wykonywano wywiadów, nie uruchamiano Claude, nie zmieniano implementacji, modelu ani innych dokumentów. Recenzja nie weryfikuje na nowo zewnętrznych źródeł technicznych przytoczonych przez autora; ustalenia wynikają z porównania lokalnego kontraktu z wiążącymi dokumentami.

## Ustalenia i kryteria zamknięcia

### R01 — blokujące: rezerwacja T04 nie określa własnej ścieżki finalizacji i rewizji

**Miejsce:** §6 (każda przyjęta transakcja zwiększa process_revision), §7 (każda mutacja ma rewizję i przechodzi wspólną procedurę), §8 pkt 1, 3–4 oraz wiersz „Mutacja równoległa podczas rezerwacji”.

Przyjęcie T04 zapisuje zlecenie i rezerwuje mutacje projektu. Finalizacja ma sprawdzić oczekiwaną rewizję, lecz nie wskazano, czy jest to rewizja wejściowego polecenia, po zapisaniu T02, po przyjęciu zlecenia, czy po zapisie potwierdzenia. Sam zapis zlecenia jest przyjętą transakcją. Nie określono też transportu potwierdzenia Git ani wyjątku, który pozwala właścicielowi rezerwacji finalizować ją mimo zakazu mutacji. Endpoint evidence opisuje wynik runnera, nie poświadczenie Git. Czytanie opisu dosłownie może zablokować również poprawne potwierdzenie lub odrzucić je wskutek własnego zwiększenia rewizji.

Timeout i fencing są dobrym kierunkiem, lecz samo zdanie „limit zwalnia blokadę” nie określa zachowania po restarcie usługi ani arbitrażu finalizacja–wygaśnięcie. Jest to luka kontraktu podstawowej ścieżki T04, a nie zastrzeżenie do jawnego braku bezwarunkowej żywotności przy niedostępnej usłudze.

**Kryterium zamknięcia:**

- Podać jawny kanał/operację potwierdzenia Git z nadawcą, powiązaniem z operation_id i numerem próby oraz odpowiedzią na duplikat.
- Rozdzielić rewizję, na której U wyraził polecenie, od rewizji/warunku finalizacji przechowywanego przez usługę. Opisać, czy i kiedy zapis zlecenia oraz dowodu zwiększa process_revision. Finalizacja nie może tracić prawa do wykonania wskutek własnych technicznych zapisów.
- Wymienić operacje dopuszczone przy rezerwacji: co najmniej jej własne potwierdzenie, zakończenie i wygaśnięcie; pozostałe mutacje otrzymują określoną odmowę. Dla wygaśnięcia i finalizacji wskazać jeden atomowy warunek rozstrzygający konkurencję.
- Zapisać trwały termin ważności i regułę odzyskania po restarcie; retry klienta lub aktywność wykonawcy nie mogą bez końca przedłużać rezerwacji bez jawnej reguły. Po odzyskaniu dostępności usługi wygasła rezerwacja przestaje blokować projekt.
- Dodać GWT dla prawidłowej finalizacji bez konfliktu z własnymi zapisami, restartu z wygasłą rezerwacją oraz wyścigu callback–timeout. Spóźniony wynik nadal może być śladem skutku zewnętrznego, bez T04.

### R02 — blokujące: katalog operacji nie zamyka ścieżki potwierdzeń U i T04

**Miejsce:** §6 rekordy Proposal/OperatorDecision, §7 tabela operacji, §5 kroki 5 i 9, §8.

Jedyny opisany POST proposals tworzy propozycję T05 dla elementu i wersji bazowej. POST operator-confirmations przyjmuje identyfikator wyświetlonej propozycji, lecz ma obsługiwać również T02+zlecenie T04 dla nowej treści. Nie podano, skąd pochodzi odrębny przedmiot tego potwierdzenia. Podobnie nie określono, jak potwierdzenie W04 wiąże sesję U z numerem wydania, manifestem i recenzją, skoro nie jest ono obsługiwanym pakietem. Ogólne /commands może wykonywać pojedyncze przejścia, ale jego opis „applied albo odmowa” nie wyjaśnia przekazania T04 do procedury pending z §8 ani zastosowania wyzwania U do pojedynczych poleceń.

Nie twierdzę, że autor zezwolił na obejście §8: ten paragraf wyraźnie wymaga potwierdzonego Git. Brakuje jednak jednoznacznej reguły dispatch i danych pozwalających wykonać deklarowany scenariusz przez opisane operacje. Jawne wyłączenie pełnego API wszystkich przejść nie obejmuje braku operacji koniecznych dla własnego głównego scenariusza.

**Kryterium zamknięcia:**

- Wprowadzić albo opisać istniejący, niezmienny przedmiot potwierdzenia dla każdego działania U w scenariuszu: P02/T05 — pytanie, cel i operacja; T02/T04 — element, wersja, manifest i jawne polecenia; W04/W05 — numer wydania, aktualny manifest i właściwy przegląd. Może to być ogólny rekord żądania potwierdzenia generowany przez serwer; nie wymaga osobnego endpointu na każdą operację.
- Wskazać, jak powstaje ekran/wyzwanie U i którędy przechodzą pojedyncze polecenia; te same kontrole treści i autoryzacji obowiązują każdą ścieżkę wejściową.
- Jawnie stwierdzić, że każde żądanie T04, również przez /commands, trafia do tej samej procedury z §8 i samo uwierzytelnienie U oraz evidence_refs nie pozwala zastosować T04 bez potwierdzonego skutku. Określić pending w odpowiedzi tego wejścia.
- Określić zamkniętą listę operacji obsługiwanych w tym wariancie; pozostałe odrzucać jako nieobsługiwane mimo ich istnienia w modelu. Macierz ról nie powinna sugerować kompletnego API wyłączonego w §10.
- Dodać GWT dla T04 przez ogólny endpoint, zamiany manifestu nowej treści przed T02/T04 oraz próby użycia potwierdzenia odbioru dla innego numeru wydania/manifestu.

### R03 — wymagane doprecyzowanie: manifest z wersjami zależności a przegląd T11

**Miejsce:** §5 krok 6, §6 ArtifactManifest i reguły niezmienności, §9 AC13–14.

ArtifactManifest zawiera wersje zależności i po T01 jest zamrożony. W scenariuszu a1/d1/c1 zachowują wersje i treści po zmianie r1 v1→v2. Nie określono, czy zapisane wersje zależności oznaczają historyczny kontekst weryfikacji, czy aktualny kontekst użycia elementu. Pierwsza interpretacja jest poprawna, ale wymaga osobnego odwołania do aktualnego przeglądu T11. Druga wymuszałaby zmianę zamrożonego manifestu albo uniemożliwiała użycie niezmienionej treści w kolejnym wydaniu.

Kontrakt mówi o odświeżeniu zapisu oceny wpływu, ale nie podaje minimalnego rekordu i jego relacji do decyzji wywołującej zmianę. Model wymaga dla T11 wpisu „Przejrzane” tej decyzji. Nie należy zastępować go samym wynikiem runnera ani bezprzedmiotowym komentarzem A.

**Kryterium zamknięcia:** odróżnić niezmienną treść/historyczny kontekst od nowego rekordu oceny wpływu A. Rekord powinien wskazywać oceniany element i manifest, przyczynę/DEC zmiany, oceniane aktualne wersje i manifesty zależności oraz wniosek. Manifest bieżącego wydania ma wskazywać właściwy kontekst oceny; poprzedni manifest i odbiór pozostają identyczne. Dodać GWT: po T11 dla a1 treść i stary manifest identyczne, nowa ocena dotyczy r1 v2, ocena dla r1 v1 nie usuwa bieżącego suspect. Nie wymaga to dodatkowej zgody U ani zmiany guard T11.

## Kontrole zakończone bez ustalenia blokującego

| Obszar | Wynik |
|---|---|
| T05 i P02 | Oddzielne zdarzenia U; jawny pakiet P02+T05 może być atomowy. P02 bez T05 nie deleguje wykonania A. Approved/rejected, element, wersja, operacja i consumed zachowane. |
| T04 | Aktor pozostaje U, także przy technicznym wykonawcy Git. Po opóźnieniu T04 wcześniejsze T02 pozostaje ważnym zatwierdzeniem; to jawnie opisane częściowe wykonanie pakietu, nie udawany rollback. Domknięcia wymagają R01–R02. |
| S9 i P01 | Zachowane jedno asked oraz kolejka modelu. Grupowanie P02+T05 nie oznacza dwóch pytań asked; T02/T04 nie są kolejnymi pytaniami P01. |
| T11 | Poprawna kolejność a1/d1 przed c1 i dojrzałe zależności bez suspect. Brak wpływu jest hipotezą scenariusza, nie automatycznym prawem skasowania suspect przy rzeczywistej zmianie treści. R03 dotyczy wyłącznie reprezentacji dowodu. |
| W04/W06 | W04 ponownie sprawdza blokery; W06 jest następnym przejściem modelowym A po zmianie accepted. Stary rekord odbioru nie jest cofany. |
| Granice zaufania | Oddzielne poświadczenia i brak bezpośredniego zapisu A/R do stanu, ról, magazynów i chronionych referencji. Jawnie wyłączono gwarancję przy dostępie A do sesji U lub systemowych uprawnień usługi. |
| Kto poświadcza | U poświadcza zgodę, importer tożsamość bajtów, runner wykonanie planu, R swoją ocenę, Git skutek zewnętrzny, silnik dopuszczalność przejścia. Żaden z tych zapisów nie dowodzi sam merytorycznej poprawności całości. |
| Weryfikacja | Zaufany plan, izolacja testów bez sekretów, odrębne checks_ok/tests_ok, odrzucanie brakujących i niepasujących dowodów. Wadliwa asercja pozostaje jawnym ryzykiem merytorycznym. |
| Idempotencja | Trwała tożsamość polecenia, porównanie payloadu, kontrola nadawcy i projektu oraz retry przed sprawdzaniem starej rewizji są właściwe. Stan, zdarzenia i wynik zapisują się atomowo; późniejsze testy powinny objąć jednoczesny retry tego samego ID. |
| Częściowa awaria Git | Brak udawanej transakcji DB+Git, warunkowy tag, jawne osierocone skutki, brak automatycznego usuwania, ponowna kontrola uprawnienia U i odrzucenie spóźnionej finalizacji. Nie ma podstaw, by żądać dodatkowej publikacji lub zmiany main. |
| Koszt U | Rachunek poprawny dla założeń scenariusza: 3 świadome czynności, 5 przejść U — P02, T05, T02, T04, W04. Nie jest to pomiar czasu, a wpływ na zależne produkty, odmowa i konflikty zwiększają koszt. |

## Pokrycie Given–When–Then

AC01–AC27 obejmują główne próby naruszenia ról, wiązania zgód, podmiany treści, nieaktualnych dowodów, niezależności R, blokad przy odbiorze i awarii integracji. Są prawidłowo oznaczone jako specyfikacja przyszłych testów.

Poza przypadkami potrzebnymi do zamknięcia R01–R03 warto dopisać przed implementacją:

- współbieżny identyczny command_id — dokładnie jeden skutek i jeden trwały wynik;
- niepowodzenie T05 w pakiecie P02+T05 — rollback również P02, bez DEC i consumed;
- P03 — brak DEC, zachowany wiek pytania i ponowne P01 według kolejki; osobno priorytet blocking przy pustym asked;
- W03/W05 — pytania blocking tworzą się atomowo ze zmianą stanu wydania;
- niepoprawny manifest/import — brak podpięcia częściowego artefaktu i brak wykonania kodu podczas odczytu;
- wynik runnera przypisany do cudzego zadania — odmowa mimo poprawnego uwierzytelnienia runnera.

To uzupełnienie pokrycia, nie żądanie wykonania nowych testów na etapie samej propozycji dokumentu.

## Jawne ograniczenia, których nie uznaję za luki

Wyłączenie pełnego API wszystkich przejść, parsera czatu, migracji, publikacji i administracji jest dopuszczalną granicą pierwszego kontraktu. Podobnie brak obietnicy wykrycia wszystkich błędów semantycznych oraz brak postępu przy nieobecności U lub niedostępności usługi. Nie wymagam zmiany tych założeń. Doprecyzowania R01–R03 dotyczą już zadeklarowanego scenariusza, a nie rozszerzenia zakresu.

Bez technicznego mapowania uprawnień na rzeczywiste środowisko nie można twierdzić, że izolacja działa. Kontrakt sam odkłada ten dowód przed implementację, więc na etapie kierunku architektonicznego jest to jawna przyszła praca, nie ukryte osiągnięcie.

## Czy obietnica braku ukrytych zmian modelu jest prawdziwa?

**Tak w zakresie sprawdzonego materiału.** Hash model/process.yaml wynosi `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07`, zgodnie z nagłówkiem kontraktu. `git diff HEAD` dla modelu, właściwości, interpretacji, PLAN i karty celu był pusty. Nie zmieniono aktorów, guard ani skutków v0.7. Dodatkowe kontrole adaptera, zewnętrzne dowody i rezerwacja ograniczają wykonanie API; autor jawnie oznaczył je jako nowe AX, nie część dowiedzionego modelu.

Zachowanie podstawowej semantyki musi pozostać warunkiem zamknięcia R01–R03. W szczególności poprawka T04 nie może przenieść aktora na A, a doprecyzowanie T11 nie może wymagać od U zatwierdzania każdego przeglądu „brak wpływu”. Nie przyjmuję ani nie odrzucam kierunku za operatora. Po korekcie dokumentu potrzebna jest ponowna weryfikacja wskazanych kryteriów przez R.

## Ponowna weryfikacja — 2026-10-26

Oceniono kontrakt SHA-256 `316081b451820af018db4fd7ded87e0dbd37f3dbfe0c512dd9af040faa6ddd93`, w tym poprawione §6–8, zamkniętą listę 16 przejść oraz AC28–AC40. Przegląd obejmował także uzupełnienia po wskazaniu brakujących szczegółów w pierwszej poprawce: trwałego terminu rezerwacji, odzyskania bez callbacku, powiązania oceny T11 z DEC oraz ogólnego przedmiotu OperatorDecision. Historyczne ustalenia powyżej pozostają bez usuwania lub przedstawiania ich jako niebyłych.

| Ustalenie | Stan | Podstawa zamknięcia |
|---|---|---|
| R01 | **Zamknięte w kontrakcie** | Osobne process_revision i operation_revision; zlecenie T04 nie zmienia rewizji procesu. T02 oraz zlecenie/rezerwacja powstają atomowo, finalizator zna r+1. Jawne git-result oraz wyjątki callback/finalizacja nie blokują się własną rezerwacją. Trwałe expires_at nie odnawia się przez retry/callback; odzyskiwanie po restarcie działa także bez dowodu. Timeout i finalizacja rozstrzygają własność atomowo. AC28/31/33 określają wymagane wyniki. |
| R02 | **Zamknięte w kontrakcie** | DecisionView rozróżnia change/item/release i wiąże tożsamość U, przedmiot, rewizję oraz polecenia. OperatorDecision odwołuje się do widoku i digest przedmiotu; proposal_digest jest wymagany tylko dla change. Wszystkie wejścia współdzielą dyspozytor i potwierdzenie U, a każde T04 prowadzi do pending z §8. Jawna lista 16 operacji odrzuca resztę jako OPERATION_NOT_SUPPORTED. AC29/30 wraz z AC08/09/17 określają granice potwierdzenia i niezmienności przedmiotu. |
| R03 | **Zamknięte w kontrakcie** | Niezmienny ArtifactManifest jest oddzielony od nowego AssessmentContext. Ocena wskazuje bieżące wersje i manifesty zależności, uwierzytelnionego autora, przyczynową DEC/zdarzenie oraz rationale. T11 sprawdza aktualny kontekst, a W01 odrzuca starą ocenę. AC32/34 zachowują historyczne bajty i dowody oraz odrzucają stary lub obcy kontekst. Nie dodano zatwierdzenia U dla T11. |

AC35–AC40 dodatkowo pokrywają sześć zaleceń dotyczących współbieżnego retry, rollbacku P02+T05, P03/kolejki, atomowości W03/W05, importu artefaktów oraz przydziału runnera. To nadal kryteria przyszłych testów integracyjnych, nie raport ich wykonania. Brak implementacji AX01–AX06 nie jest otwartym ustaleniem tego przeglądu: zadaniem było przygotowanie kompletnej propozycji do decyzji.

### Niezależne sprawdzenie projekcji modelowej

Recenzent sam wykonał `replay` na example-scenario.json z bieżącym model/process.yaml i uruchomił `safety_violations` na całym uzyskanym śladzie. Wynik: **completed, 41 kroków, 5 przejść U w 13 krokach scenariusza po 28-krokowym prefiksie, brak naruszeń S**. Kanoniczne hashe modelu `ecca43e1402ee476502943caa16556d5609021b8894f3a702e26ca2da3cf21a6` i scenariusza `a1ce942228899a7e0365cd7390b25a2eb3260151ea5323710e96c413641e193b` są zgodne z verification.json.

Przejrzano też jawne oznaczenie ograniczeń w example-scenario.json, verification.json i §12 kontraktu. Recenzent nie odtwarzał ponownie trzech negatywnych prób zapisanych przez autora w verification.json; niezależnie wykonana kontrola dotyczy pełnego śladu poprawnego i właściwości S. Projekcja przyjmuje checks_ok/tests_ok oraz brak wpływu merytorycznego jako dane, nie sprawdza uwierzytelnienia, bajtów, rezerwacji, Git ani runnera. Nie jest dowodem wykonania AC01–AC40.

Ponownie sprawdzono hash model/process.yaml: `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07`; dokumenty modelowe pozostają bez zmian względem HEAD. Rachunek 3 świadomych czynności i 5 przejść U jest zachowany. Zamknięta lista API jest jawnym wycinkiem v0.7, nie deklaracją pełnej żywotności ani obsługi wszystkich wyjść modelu; przygotowanie instancji i pełne tworzenie projektu pozostają wyraźnie poza tym kontraktem.

**Rekomendacja recenzenta:** przedstawić poprawiony kontrakt operatorowi do decyzji o kierunku architektonicznym. Nie ma otwartych ustaleń blokujących ten krok. Zgoda na implementację, umieszczenie jej w planie, dobór środowiska, pomiar kosztu oraz odbiór E2/systemu pozostają odrębnymi sprawami operatora.
