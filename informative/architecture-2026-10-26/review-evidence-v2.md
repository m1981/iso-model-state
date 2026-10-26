# Niezależny przegląd kontraktu API — wiedza dowodowa przy odbiorze

Data: 2026-10-26. Recenzent: osobny przebieg agenta R. Przedmiot: [process-api-contract-evidence-v2.md](process-api-contract-evidence-v2.md), **SHA-256 bajtów `b55837a80b4d7b6e2861d01c2e9d09e867af10c64912096b32f1bfa8ee0d9af9`**.

**Werdykt: R04 zamknięte na poziomie specyfikacji. Nie znalazłem otwartych ustaleń blokujących przedstawienie rewizji 2 jako propozycji kierunku architektonicznego. Nie stwierdziłem regresji zamknięć R01–R03 ani sprzeczności z v0.7.** To techniczny wynik przeglądu dokumentu, nie potwierdzenie działania API, wykonania AC41–AC54, odbioru E2 ani przyjęcia AX01–AX06.

## Zakres i metoda

Przeczytano instrukcję startową i kontrakt współpracy, STAN, kartę celu, PLAN, model/process.yaml, właściwości, interpretacje oraz regułę pierwszeństwa informative/. Oceniono całą rewizję 2, porównano ją z pierwszym kontraktem i z kryteriami zamknięcia R01–R03 w historycznej recenzji. Przegląd polegał na poszukiwaniu przeciwnych przebiegów: pominięcia wyniku, błędnej stosowalności, wyścigu callback–W04, starego widoku, awarii pomiędzy zapisami, retry, zmiany próby zadania i późnej wiedzy po odbiorze. Nie przyjęto jako dowodu samej deklaracji autora, że luka została zamknięta.

W toku przeglądu autor doprecyzował §6 i AC43, obejmując rewizją także klasyfikację, uzupełnienie logu/metadanych i konflikt. Niniejszy werdykt dotyczy wyłącznie końcowych bajtów wskazanych powyżej, zawierających to doprecyzowanie. Recenzent nie zmieniał kontraktu.

Niezależnie uruchomiono istniejącą projekcję scenariusza i trzy próby odmowy opisane w §12. Nie tworzono implementacji API ani sztucznego symulatora nowych reguł adaptera. Nie wykonywano ponownie pełnej regresji E2: zmieniany przedmiot jest propozycją dokumentu, a nowej semantyki dowodów wykonawca E2 nie zawiera. Nie sprawdzano ponownie źródeł zewnętrznych OWASP/RFC ani pełnej zgodności z ISO; wnioski opierają się na lokalnym kontrakcie i dokumentach wiążących.

## R04 — wynik znany przed W04, ale niepodpięty

**Problem:** dla tego samego materiału istnieje pass, następuje W02, następnie runner dostarcza fail trwale przyjęty do magazynu usługi. Agent nie podpina go do procesu i przedstawia W04 wyłącznie z pozytywnymi evidence_refs. Historyczny kontrakt nie określał dostatecznie, czy W04 musi uwzględnić wynik poza aktywnymi powiązaniami. Jest to luka specyfikacji adaptera, nie wykazany exploit działającego serwisu ani błąd symulatora v0.7. To nowe R04 nie zmienia historycznego zamknięcia R01–R03.

**Przebieg po korekcie:**

1. Zaufany intake sprawdza przydział runnera. Atomowo utrwala kopertę wyniku, odwołanie do bajtów i evidence_revision, zanim potwierdzi odbiór. W tym punkcie fail staje się znany, niezależnie od powiązania, klasyfikacji i odczytu przez A (§6.1 pkt 1).
2. W04 ocenia rejestr projektu, a evidence_refs nadawcy nie filtruje tego rejestru. Stosowalność obejmuje materiał i odpowiedni element zakresu; odrębny material_digest nie zależy od listy wyników zamrożonej przy W01 (§6, §6.1 pkt 2).
3. Stary DecisionView lub wcześniej wydany confirmation_id nie przechodzi kontroli evidence_revision. Po odświeżeniu applicable fail nadal blokuje. Nieklasyfikowany wynik lub brak logu blokuje jako unresolved. Sam nowszy pass nie usuwa fail (§6.1 pkt 3 i 6).
4. Intake i W04 mają wspólny serializowany porządek zapisu. Gdy przyjęcie fail poprzedza odbiór, W04 nie może utrwalić accepted na wcześniejszej ocenie. Warunek dotyczy finalnej transakcji, nie tylko wcześniejszego odczytu (§6.1 pkt 5).
5. Odmowa nie wykonuje W05 ani nie zmienia reviewed. W05 pozostaje dostępne dla U bez pozytywnej oceny dowodów; poprawa przebiega przez istniejące bramki modelu (§6.1 pkt 6 i 8).

W analizowanym kontrprzykładzie wynik jest zatem zablokowany niezależnie od działania A. AC41, AC44 i AC54 opisują trzy istotne odmiany: stary ekran, wybór tylko pozytywnych referencji i brak wyniku w zamrożonym pakiecie W01. **Kryterium zamknięcia R04 jest spełnione w treści kontraktu.**

## Próby podważenia i wynik

| Próba lub granica | Wynik przeglądu |
|---|---|
| Fail dotyczy tych samych bajtów, lecz ma inny identyfikator pakietu lub próby | Nie wolno uznać go za obcy tylko z tego powodu. §6.1 pkt 2–3 i AC44/54 wymagają oceny materiału, zależności, kryterium i środowiska. Material_digest oddziela przedmiot od listy dowodów. |
| Fail dotyczy jednego elementu większego wydania | §6.1 pkt 2 jawnie wymaga uwzględnienia odpowiedniego elementu zakresu; sama nierówność skrótów całych pakietów nie uzasadnia wykluczenia. AC54 utrwala ten przypadek. |
| Fail jest rzeczywiście obcego materiału | Może być inapplicable wyłącznie według przypiętej polityki i z uzasadnieniem. Nie ma globalnego zakazu odbioru po jakimkolwiek fail w projekcie. Przy braku rozstrzygnięcia obowiązuje blokada, nie domniemanie nieistotności (AC45/46). |
| Zmiana metadanych, klasyfikacji lub dostępności logu po wyświetleniu U | Końcowy §6 obejmuje każdą taką zmianę evidence_revision i wspólnym porządkiem zapisu. Stary ekran traci ważność także bez nowego callbacku. Kolejne oceny nie nadpisują historycznych dowodów ani AcceptanceCheck (AC43). |
| W04 zdążyło odczytać pass, a intake dopisuje fail przed finalnym zapisem | Wymagana serializacja lub równoważna kontrola z ponowną walidacją wyklucza zatwierdzenie starszej wiedzy. Sam snapshot bazy jest wprost niewystarczający (AC42). |
| Fail zapisuje się przed potwierdzeniem callbacku, po czym serwis przestaje działać | Już przyjęta koperta uczestniczy w bramce; utrata odpowiedzi nie usuwa wiedzy. Retry jest idempotentne. Awaria przed atomowym zapisem nie może dać potwierdzenia sukcesu (AC47). |
| Runner odpowiada na wcześniejszą próbę, podczas rezerwacji T04 lub po zmianie statusu zadania | Poprawnie przypisanego wyniku nie odrzuca się z powodu starej rewizji/próby. Jego przyjęcie zwiększa evidence_revision, pozostawiając process_revision bez zmian. Reguła nie znosi oddzielnego fencing finalizacji Git (AC48 i §8). |
| Ten sam callback_id przynosi inną treść | Oryginał zostaje, powstaje nierozstrzygnięte ustalenie integralności, rośnie rewizja wiedzy; konflikt jest blokujący dla właściwego materiału. Identyczny retry nie tworzy kolejnego wyniku (AC53). |
| Wcześniejszy pass oraz nowe wymagane zlecenie running, expired lub error | Wcześniejszy sukces nie zastępuje nierozstrzygniętego wymaganego zadania. Required określa polityka serwera. Utworzenie i zmiany stanu istotnego zadania podlegają rewizji i temu samemu porządkowi (AC49). |
| Niewymagane zadanie jest jeszcze w toku | Kontrakt jawnie nie wymaga czekania. Jeśli wynik już przyjęto i jest applicable fail, blokuje niezależnie od required. To ograniczenie obietnicy przyszłej wiedzy, nie luka pomijania wiedzy znanej. |
| W04 zapisuje się przed intake fail | Stary odbiór i AcceptanceCheck pozostają identyczne. Transakcja intake zapisuje EvidenceFinding dla dotkniętych odbiorów; nieukończona klasyfikacja daje unresolved. Autorytatywny odczyt nie zależy od opóźnionej projekcji ani powiadomienia (AC50). |
| Odpowiedź skutecznego W04 zginęła, potem nadszedł fail i retry | Zwrócenie pierwotnego sukcesu oznacza wynik historycznego polecenia, nie ponowną pozytywną ocenę. GET process pokazuje późne ustalenie. Odmowa W04 również pozostaje trwała pod starym command_id; nowa próba wymaga nowego ID (AC51/52). |
| U próbuje wymusić W04 mimo fail albo A ponawia test do uzyskania pass | Brak takiego odstępstwa w tym wycinku. Nowy numer wydania, ponowienie testu i nowszy pass nie kasują negatywnego dowodu dla tego samego materiału (§6.1 pkt 3). |

## Zgodność z v0.7 i brak regresji R01–R03

Nowa bramka jest jawnie oznaczona jako AX03/AX04/AX06 i zawężenie adaptera. Nie jest dopisana do guard W04 ani przedstawiona jako wynik S14: S14 dotyczy pytań blocking, a model nie zna rejestru wyników runnera. Callback nie przejmuje roli U/R i nie wykonuje sam P00, W05 lub W06. Późne ustalenie nie cofa accepted; zachowano S10. W06 nadal wymaga legalnej zmiany modelowej i pozostaje przejściem A. W05 z właściwym przedmiotem i rewizją nie wymaga pozytywnego AcceptanceCheck.

| Historyczne ustalenie | Kontrola w rewizji 2 |
|---|---|
| R01 — finalizacja T04 | §8 zachowuje osobne rewizje, wyjątek dla własnego callbacku/finalizatora, r/r+1/r+2, trwałe expires_at, odzyskanie bez callbacku i atomowy arbitraż timeout–finalizacja. Nowa wiedza runnera nie zmienia process_revision i nie powoduje konfliktu finalizacji z własnymi zapisami. |
| R02 — przedmiot i wejścia U | Zachowano DecisionView change/item/release, powiązanie tożsamości i poleceń, wspólny dyspozytor oraz pending dla każdego T04. W04 dodaje wymaganie aktualnej wiedzy na obu wejściach, także przy confirmation_id. Zamknięta lista 16 przejść nie została rozszerzona. |
| R03 — kontekst T11 | ArtifactManifest nadal zachowuje historyczne pochodzenie; AssessmentContext wiąże bieżące zależności, przyczynową DEC/zdarzenie i ocenę A. Material_digest nie pozwala zmienić treści przez T11 ani przenieść starego kontekstu na nowy. Nie dodano zatwierdzania T11 przez U. |

Niezależny przebieg projekcji w istniejącym środowisku dał **completed, 41 kroków, brak naruszeń safety_violations**. Osobne próby `agent_T05`, `rejected_consent` i `premature_T11` zakończyły się `rejected`. Wynik ten potwierdza wyłącznie projekcję na obecny model z założonymi checks_ok/tests_ok; nie sprawdza pełnego rejestru, intake, transakcji, runnera, interfejsu U ani Git.

SHA-256 model/process.yaml wynosi `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07`. Kontrola `git diff HEAD` była pusta dla modelu, właściwości, interpretacji, PLAN, karty celu oraz obu historycznych plików. STAN również nie miał zmian w chwili początkowej kontroli recenzenta; później autor zaktualizował w nim status tego zadania, bez zmiany semantyki modelu. Raport nie stwierdza niezmienności STAN w końcowej dostawie. Hash pierwszego kontraktu to `316081b451820af018db4fd7ded87e0dbd37f3dbfe0c512dd9af040faa6ddd93`, a historycznej recenzji `e4e95fd09141eb7874ed73a36d5e5fefb145a7f6f8bed434e3014d8a64b2a654`.

## Otwarte braki i ograniczenia dowodów

**Brak otwartych ustaleń wymagających korekty tej propozycji przed decyzją o kierunku.** Nie utożsamiam tego wyniku z gotowością do wdrożenia. Konkretna polityka stosowalności, wymaganych zleceń i zgodności środowisk oraz technologia serializacji pozostają zadaniami przyszłej implementacji. Wtedy trzeba wykazać zachowanie kontraktu, zwłaszcza brak pomijania wyników części zakresu i brak okna między intake a W04. Te szczegóły nie są przerzucone na operatora jako obowiązek technicznego przeglądu.

Granice zaakceptowane w ramach oceny dokumentu, a nie potwierdzone jako działające zabezpieczenia:

- „Znany” oznacza atomowo zarejestrowaną kopertę u zaufanej usługi. Sam plik stagingu bez koperty i wynik znajdujący się wyłącznie u runnera nie spełniają tej definicji. Nie można reklamować tej gwarancji jako objęcia dowolnych bajtów istniejących w jakimkolwiek magazynie. Przyjęcie wymagane w kontrprzykładzie R04 jest objęte ochroną już przed podpięciem do procesu.
- Bezwarunkowy postęp nie jest obiecany. Nierozstrzygnięty wymagany job lub autorytatywny fail może zablokować odbiór. Kontrakt jawnie nie zawiera uznaniowego anulowania fail i nie nakazuje oczekiwania na niewymagane zadania.
- Rewizja całego projektu może unieważniać widok U także po pozytywnym lub obcym wyniku. Koszt jest jawny; liczba trzech czynności z poprawnego scenariusza nie jest gwarantowana przy napływie nowej wiedzy ani zmierzona w pilotażu.
- AC41–AC54, podobnie jak AC01–AC40, są **specyfikacją przyszłych testów**, nie wynikiem ich wykonania. Nie ma tu dowodu działającej izolacji, uwierzytelnienia, serializacji ani retencji. Przegląd dokumentu i przebieg modelowy nie zastępują takich dowodów.

**Rekomendacja recenzenta:** przedstawić rewizję 2 wraz z tym raportem do decyzji o kierunku AX01–AX06. Techniczny przegląd R04 został wykonany; operator nie musi sam sprawdzać zamknięcia luki. Przyjęcie kierunku, umieszczenie implementacji w planie, zgoda na wdrożenie i odbiór E2 pozostają odrębnymi decyzjami.
