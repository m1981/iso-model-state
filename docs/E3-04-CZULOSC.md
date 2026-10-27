# E3.4 — niezależne przypadki i oczekiwane błędy mutantów

2026-10-27. Autor zamrożonej wyroczni przygotował osobno [impact_cases.py](../tests/fixtures/e3/impact_cases.py): **60 pełnych kontekstów A/I/R i 34 mutanty z ręcznie określonym złym następstwem**. To gotowe dane badania czułości, nie deklaracja wykrycia mutantów. Autor tych danych nie uruchomił E2 ani translatora; osobny autor integracji zgłosił dwie korekty DSL opisane poniżej. Pliki wyroczni Python/TLA i jej dokumentu pozostały identyczne z zamrożeniem opisanym w [E3-04-WYROCZNIA](E3-04-WYROCZNIA.md).

## Pochodzenie i interfejs

Jedynymi importami nowego modułu są `deepcopy` i funkcje niezależnej wyroczni `impact_oracle`. Autor buduje pełny przedstan z literalnego `initial_state()`, wybranych checkpointów ręcznego świadka i wskazanych kroków referencji. Dla przypadków oczekiwany legalny wynik wylicza zamrożona wyrocznia. Dla mutantów zły wynik jest osobną ręczną zmianą pełnego przedstanu lub kopii poprawnego oczekiwania. Kandydat nie bierze udziału w żadnym z tych obliczeń.

`cases()` zwraca świeżą listę rekordów `id, before, command, expected, note`. Expected ma `None` dla odmowy albo pełny rekord `world, records`. Dwa przypadki A02 z brakującym/nieznanym pytaniem dodatkowo mają `input_error=True`: tutaj `expected=None` oznacza brak następstwa po błędzie wejścia. Uprząż ma oczekiwać błędu walidacji i nie zaliczać go jako guard=false ani jako semantycznego kontrprzykładu TLC.

`mutants(model)` zwraca 34 rekordy `id, model, case, wrong_expected, expected_violation` oraz opcjonalne metadane. Każdy model jest głęboką kopią wejścia; każdy case zawiera własny pełny przedstan. Wszystkie wrong_expected są pełnymi wynikami `world, records`, odmiennymi od referencji. Piętnaście ma `expected_violation=Availability` — mutant wykonuje krok zabroniony w bazie. Dziewiętnaście ma `Successor` — krok jest legalny w bazie, lecz mutant zmienia jego rezultat. Nazwane kontrole szczegółowe i monitory należy dodatkowo sprawdzić; ogólna nierówność nie dowodzi sama czułości kontroli pola lub historii.

Przypadki zachowują wszystkie osiem ID i stałą topologię bazową. Warianty izolacyjne są opisane jako wstrzyknięte. Dwanaście kontekstów R ma pełny świat, odpowiedni scope, a przy accepted pełny snapshot rekordów produktów bez pola `id` oraz acceptance `{number: 1, quote: SIM_QUOTE}`. Stany te są oczekiwanymi kontekstami, nie sfabrykowanymi śladami wykonania: osiągalne warianty R autor badania musi potwierdzić osobnymi prefiksami E2 zgodnie z mapowaniem.

## Pokrycie przypadków

| Grupa | Rozdzielone próby |
|---|---|
| A01 | state, kind, resolution, about, about_version, requested_transition, consumed — siedem pojedynczych zmian poprawnej zgody. |
| A02 | Aktor A/R przy poprawnej zgodzie; osobno brak i nieznane ID pytania jako błędy wejścia. |
| A03 | P02 approved, rejected, T05 po rejected, niejednoznaczność i brak dowodu. Pełne DEC w legalnych wynikach. |
| A04 | consumed=true przy nadal pasującej wersji. |
| A05 | Dwa open o różnym age: starsze dozwolone, młodsze odmówione; dodatkowo q1=asked i q2 najstarsze open izolują limit jednego asked. |
| I01 | Pełny wpływ r1, ponowne oznaczenie c1 przez a1, pełny nowy rekord T12(a1,q1). |
| I02 | Osobno zależność draft i dojrzała suspect, legalny przegląd, brak evidence oraz końcowy legalny przegląd c1. |
| I03 | Legalny T13 szkicu; dozwolone T01 z dojrzałymi suspect zależnościami; aktor U/R; baselined; własne suspect; bezpośrednia zależność draft; osobna izolacja własnej flagi przy dojrzałych zależnościach. |
| I04 | Własne suspect=true oraz rejections=2 przed legalnym T05: nowa wersja, oba resety. |
| R01/R02 | r1 w scope przy ready/reviewed/accepted; pending po accepted blokuje następne T11. |
| R03 | r1 poza scope, jego zależni w scope, wszystkie trzy stany wydania; observer ma działać bez helpera źródła. |
| R04 | Liść a2 w/poza scope, wszystkie trzy stany; w zakresie izoluje helper, poza zakresem nie ma wpływu. |

## Izolacja priorytetu pending po recenzji

Recenzent wykrył, że trzy dotychczasowe odmowy R z sufiksem `_pending` próbują T11(d1), którego własne warunki również są niespełnione. Same te odmowy nie wykazują czułości kontroli priorytetu. Zachowano wszystkie 54 wcześniejsze przypadki i 34 mutanty oraz dodano sześć prób: dla każdego z trzech kontekstów accepted/pending T01 na właśnie zmienionym r1 albo a2 odmawia, a identyczna kopia z `next_release_required=false` dopuszcza T01.

Nowe przypadki mają sufiksy `_pending_verify` oraz `_pending_verify_isolated`. Zmieniony produkt jest draft, ma suspect=false, dojrzałe bezpośrednie zależności i checks=true, więc odmowy nie maskują from, rola ani guard T01. Wyłączenie pending w kontroli pozytywnej jest jawnie wstrzykniętym stanem izolacyjnym; nie twierdzimy, że proces pozwala pominąć W06. Niezależna referencja potwierdziła trzy odmowy i trzy legalne pełne następstwa, bez wykonywania E2 ani translatora. Poprzednie wyniki badania dotyczą wcześniejszego hasha i nie zastępują wykonania nowych prób na kandydacie.

## Mutanty i izolacja kontroli

| Mutanty | Przypadek | Oczekiwany błędny wynik |
|---|---|---|
| `authorization_without_*` (7) | Odpowiedni A01 | T05 mimo dokładnie jednego niezgodnego składnika; pełna zmiana r1 i zużycie pytania. |
| `change_wrong_actor` | A02_actor_A | Autor wykonuje operację U. |
| `change_without_consumption` | I01_r1 | Zmieniony produkt, q0.consumed nadal false; sprawdzane natychmiast, bez maskowania przez późniejszą wersję. |
| `change_without_version` | I01_r1 | Nowy draft nadal v1. |
| `change_without_rejection_reset` | I04_reset | Nowa wersja zachowuje rejections=2. |
| `change_without_own_flag_reset` | I04_reset | Nowa wersja zachowuje własne suspect. |
| `change_without_propagation` | I01_r1 | Żaden zależny nie dostaje flagi. |
| `change_direct_only` | I01_r1 | d1/a1 dostają flagę, pośredni c1 pominięty. |
| `change_whole_catalog` | I01_r1 | Flagi dostają wszystkie produkty poza źródłem, także p1/r2/a2/r3. Własne r1.suspect pozostaje false, aby nie maskować błędu ramy. |
| `review_without_maturity` | I02_immature | T11 czyści flagę mimo r1=draft/suspect=false. |
| `review_without_dependency_flag` | I02_suspect_dependency | T11(c1) mimo dojrzałego, nadal podejrzanego a1. |
| `review_without_evidence` | I02_no_evidence | T11 bez dowodu przy spełnionych pozostałych warunkach. |
| `request_wrong_about` | I01_raise_a1_predecessor | Nowy wniosek wskazuje historyczne a2 zamiast bieżącego a1. |
| `request_wrong_operation` | I01_raise_a1 | Nowy wniosek wskazuje T07. |
| `request_wrong_version` | I01_raise_a1 | Przed utworzeniem pytania mutant zwiększa wersję a1; pytanie ma v2 zamiast wersji 1 sprzed T12. |
| `request_without_question` | I01_raise_a1 | T12 niczego nie tworzy. |
| `fix_baselined` | I03_baselined | T13 otwiera draft z baselined bez zgody. |
| `fix_wrong_actor` | I03_actor_U | T13 wykonuje U. |
| `fix_changes_version` | I03_fix | T13 zwiększa wersję szkicu do 2. |
| `change_without_helper` | R04_a2_in_ready | Liść zmienia się, wydanie zostaje ready; brak zależnych nie pozwala observerowi zamaskować usuniętego helpera. |
| `without_observer_before_acceptance` | R03_r1_out_ready | Nowe suspect w scope, wydanie pozostaje ready; źródło poza scope wyłącza helper. |
| `without_observer_after_acceptance` | R03_r1_out_accepted | Odebrany rekord zachowany, ale brak pending mimo nowych flag w scope. |
| `observer_overwrites_accepted` | R03_r1_out_accepted | Observer zmienia odebrany rekord na in_preparation zamiast ustawić pending. |
| `change_to_approved_history` | I01_r1 | Nowa v2 pozostaje approved; stara historia v1 nie może wystarczyć. |
| `ask_without_single_pending` | A05_asked_limit | q1 i q2 równocześnie asked. |
| `resolve_without_unambiguous` | A03_ambiguous | Niejednoznaczne P02 rozstrzyga i tworzy DEC. |
| `resolve_wrong_resolution` | A03_approved | Pytanie i DEC zapisują rejected zamiast approved. |
| `resolve_wrong_dec_binding` | A03_approved_predecessor | P02 zmienia about na historyczne a2 przed zapisem DEC; records musi ujawnić błędne powiązanie. |

## Trzy odrębne rodzaje kontroli

**Mutanty danych modelu** zmieniają rozpoznawalne from/to/actor/guard/effects/evidence lub predykat autoryzacji i globalne obserwatory. Nie zmieniają prozy ani nazw operacji. Używają istniejącego DSL, np. `predecessor(e).id`. Jeżeli kandydat nie obsługuje takiej semantyki, jego jawna odmowa translacji jest wynikiem kontroli granicy, a nie zabiciem mutanta.

Pierwsze warianty dwóch błędnych powiązań używały `item(r2).id`; integrator ustalił, że ID produktu nie jest literałem DSL i interpreter odmawia takiej semantyki. Nie zaliczono tego jako wykrycia mutanta. Autor danych zastąpił je odwołaniami do istniejącej wartości rekordu: T12 używa `predecessor(e).id`, P02 przed DEC używa `about := item(q.about).predecessor`. Dwa dedykowane konteksty mają wstrzyknięte `a1.predecessor=a2` i `a2.state=superseded`; oba produkty są AT/v1. To syntetyczna historia do izolacji pola, bez twierdzenia osiągalności i bez zmiany grafu depends_on. Poprawny wynik nadal wskazuje a1, ręczny błędny wynik wskazuje a2. Pierwotne zwykłe przypadki I01_raise_a1 i A03_approved pozostają w macierzy.

**Mutanty algorytmiczne** mają `special=direct` albo `special=all` i pozostawiają model bez zmian. Uprząż ma świadomie podmienić implementację domknięcia w kandydacie. Direct oznacza tylko produkty mające źródło bezpośrednio w depends_on; all oznacza wszystkie ID poza źródłem. Nie są to nielegalne wyrażenia YAML ani zmiana wyroczni.

**Próba kontraktu wykonawcy** `request_without_question` ma `special=noquestion`. Po usunięciu create normalne zdarzenie E2 z argumentem question staje się niepoprawne. Aby uzyskać rzeczywiście wykonany świadek brakującego skutku, uprząż musi świadomie usunąć question z tego jednego zdarzenia kandydata, zachowując oryginalną komendę referencyjną i jawnie raportując różnicę kontraktu. Sam InputError normalnego zdarzenia nie jest semantycznym wykryciem mutanta.

`request_wrong_version` ma dodatkowe `fieldcheckwanted=question_version`. Zmiana samego about_version w argumencie create jest normalizowana/walidowana przez kontrakt tworzenia; zamiast liczyć błąd wejścia jako sukces, mutant legalnie zwiększa wersję przed create. Ogólna nierówność produktów może go wykryć, ale zaliczenie kontroli powiązania wymaga osobnego sprawdzenia q.about_version wobec wersji produktu **sprzed** T12. Analogicznie `resolve_wrong_dec_binding` wymaga osobnej asercji pola DEC przez `fieldcheckwanted=decision_binding`; sam błąd zmienionego pytania nie wystarcza do deklaracji czułości records.

`change_to_approved_history` ma `monitorwanted=version_history`. Wykrycie różnicy pełnego następnika to osobny wynik od wykazania, że monitor nie przyjmuje wpisów T01/T02 wersji 1 jako historii wersji 2. Kontrole muszą zostać uruchomione na rzeczywiście wykonanym złym kroku.

## Samokontrola i zamrożenie

Autor lokalnie sprawdził unikalność 60 ID przypadków i 34 ID mutantów, kompletność pełnych złych wyników, ich odmienność od referencji, podział 15 Availability/19 Successor, brak mutacji wejściowego modelu oraz powtarzalność budowania przypadków. Po korekcie dwóch powiązań sprawdził też zachowanie wstrzykniętej ramy historycznej w before, expected i wrong_expected. To sprawdzenie konstrukcji danych; E2/TLC kandydata, świadki mutantów i niezależna recenzja pozostają pracą integracyjną. Nie wytworzono ani nie zapisano fikcyjnego śladu tych wykonań.

| Źródło | SHA-256 bajtów |
|---|---|
| tests/fixtures/e3/impact_cases.py | `90754b7ead4ed55d037b33273276772bbd4f5faf27e87409214772804e92e325` |
| tests/fixtures/e3/impact_oracle.py — bez zmian | `098854ff9f416aa302e2e1e347a0e19ef88c0b1d9487597ae4db25d04f758652` |
| docs/E3-04-WYROCZNIA.md — bez zmian | `864aa7ec5844d848a0594d1dfd7e2b639516e2e5702336bd7003aff2ea05df9e` |

Decyzja autora: izolujemy ramę allclosure bez ustawiania własnej flagi źródła i osobno klasyfikujemy mutanty algorytmiczne oraz zmieniony kontrakt noquestion, ponieważ zwykła nierówność lub odmowa wejścia mogłaby zamaskować nieskuteczną kontrolę. Zmienia: nowe dane czułości i opis metody; nie zmienia modelu, zamrożonej wyroczni ani zakresu E3.4. Przejrzane: mapowanie §5/7 i przekazane ustalenia integracyjne.
