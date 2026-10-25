# E2 — raport sprawdzeń modelu v0.6

**Status: wymaga decyzji o korekcie modelu; E2 nie jest odebrane.** Zielone testy diagnostyczne potwierdzają istnienie znanych luk. Nie są dowodem ich usunięcia z obowiązującego modelu.

## Tożsamość badania

- Model v0.6, SHA-256: `ec342e2d04d8200de32d2bbba963ecd4fc45014405b99653134f15e110ff4680`.
- Kod i dane sprawdzeń SHA-256: `23dd7e08998b28b4840ce7d3c8a97ae61e600533ed22c80e412a8c0ed9e12abf`; Python `3.14.7`.
- Pełne scenariusze, wyniki i hashe plików: odtwarzany `evidence.json`. Polecenie: `.venv/bin/python scripts/run_e2.py --output artifacts/e2`. Kod wyjścia 1 oznacza znaną blokadę odbioru; 2 oznacza błąd przygotowania raportu.

## Struktura i wykonalność

| Właściwość | Model bazowy | Mutant wykryty | Zakres |
|---|---|---|---|
| G0 | True | True | struktura/adnotacje |
| G1 | True | True | graph_projection |
| G2 | True | True | witness_per_transition_and_T04_per_type_not_exhaustive |
| G3 | True | True | graph_projection |
| G4 | True | True | struktura/adnotacje |
| G5 | raport | nie dotyczy | report_not_test |
| G6 | True | True | struktura/adnotacje |

**28/28 przejść** ma jawny, wykonany świadek od stanu początkowego. Brakujące: []. G2 wymaga dodatkowo T04 dla wszystkich pięciu typów; brakujące zastosowania: []. Mutant G2 sprawdzono na stanie CODE osiągniętym modelem bazowym; odrzucenia wcześniejszego DES nie zaliczamy jako próby CODE. Ta sama wyrocznia pokrycia zgłasza również brak T04:CODE w korpusie wykonanym zmienionym modelem.

| Przejście | Scenariusz | Liczba kroków prefiksu |
|---|---|---|
| P00 | WIT4 | 1 |
| P01 | WIT4 | 2 |
| P02 | WIT4 | 7 |
| P03 | WIT4 | 5 |
| P04 | WIT4 | 10 |
| P05 | WIT4 | 11 |
| T00 | WIT1 | 1 |
| T01 | WIT1 | 2 |
| T02 | WIT1 | 3 |
| T03 | WIT2 | 7 |
| T04 | WIT1 | 4 |
| T05 | WIT5 | 33 |
| T06 | WIT3 | 46 |
| T07 | WIT3 | 32 |
| T08 | E2-EXITS | 4 |
| T09 | E2-EXITS | 2 |
| T10 | E2-EXITS | 3 |
| T11 | WIT3 | 51 |
| T12 | WIT3 | 38 |
| T13 | WIT3 | 48 |
| T14 | WIT3 | 42 |
| W01 | WIT1 | 27 |
| W02 | WIT1 | 28 |
| W03 | E2-REVIEW-REJECTIONS | 28 |
| W04 | WIT1 | 29 |
| W05 | E2-REVIEW-REJECTIONS | 35 |
| W06 | WIT5 | 34 |
| W07 | WIT3 | 37 |

## Bezpieczeństwo i czułość wyroczni

Niezależny moduł safety.py nie importuje wykonawcy, parsera ani jego helperów. S2/S3/S8 sprawdzają całą historię wersji i wydania; nie przyjmują wstrzykniętego prefiksu jako dowodu. Poniżej mutant jest przypisany wyłącznie do właściwości, której naruszenie wyrocznia rzeczywiście zgłosiła.

| Właściwość | Wykryte mutanty z istniejących prób WIT |
|---|---|
| S1 | wit1_author_baseline, wit2_author_rejection, s1_agent_includes_scope |
| S2 | wit1_skip_approval |
| S3 | wit1_skip_verification |
| S4 | wit1_unready_dependency, s4_premature_no_impact_review |
| S5 | s5_missing_relink_propagation |
| S6 | s6_review_ignores_retired_dependency |
| S7a | wit1_incomplete_ready, s7a_retirement_keeps_reviewed, s7a_t10_keeps_readiness |
| S7b | wit1_incomplete_acceptance |
| S8 | wit1_skip_review |
| S9 | wit4_two_asked |
| S10 | s10_modifies_accepted_scope, s10_w06_rewrites_accepted |
| S11 | s11_rejection_as_consent, s11_wrong_item, s11_wrong_operation, s11_stale_unused_consent, s11_missing_consumption, s11_p03_changes_binding |
| S12 | s12_active_predecessor, s12_wrong_predecessor_type, s12_relink_without_opening, s12_relink_outside_scope, s12_wrong_successor, s12_immature_successor, s12_missing_relink, s12_rewrites_lineage |
| S13 | s1_agent_includes_scope, s13_drops_predecessor_from_scope, s13_includes_immature_successor, s10_modifies_accepted_scope |

W pięciu WIT: 0 naruszeń S1–S13. Wykryto 43/43 mutantów prób bramek. Pokrycie właściwości S wykonanymi mutantami niezależnej wyroczni: 14/14; brakujące: []. Próby reguł kolejki lub strażnika T11 mogą nie naruszać żadnej formuły S — nie przypisujemy im sztucznie takiego wyniku.

## Generowanie sekwencji

`tests/test_stateful.py`: RuleBasedStateMachine, max_examples=24, stateful_step_count=25, derandomize=True. Początek to osiągalny prefiks; dalsze kroki są generowane na nowo. Sprawdzane są S1–S13, odmowy i atomowość. Nie filtrujemy wyników wyroczni. Wyniki pytest są zapisane w STAN, a nie wnioskowane z samego generatora.

Oddzielny deterministyczny przegląd kandydatów w 28 źródłach świadków pokrywa 28 przejść: {'applied': 1063, 'rejected': 766, 'boundary': 24, 'input_error': 0}. To liczby prób kandydatów, nie liczba wszystkich stanów ani kroków Hypothesis. Granice pytań, wersji i wydań są wynikiem boundary, nie dowodem zakleszczenia.

## Otwarte blokady

| ID | Dowód | Proponowana korekta |
|---|---|---|
| A1 | Późne pytanie blocking po W02 nie blokuje W04 | Warunek braku blokad przy odbiorze, nowe S14 |
| A2 | T09/T10 pozwala trzeci raz odrzucić tę samą wersję | Zachowanie licznika przez T10, nowe S15 i doprecyzowanie L4 |
| A5 | Pusty scope unsupported; literalny guard W01 pomija globalne bramki | Nawias wokół forall i obsługa pustego zakresu po przyjęciu reguły |
| A6/A7 | Zmiana poza zakresem może naruszyć S7a/S7b wewnątrz niego | Obserwator nowych suspect cofa ready/reviewed; alternatywna instancja |

Dokładna propozycja i wyniki próby na kopii: `model/proposals/e2-hardening.md`, `e2-hardening-diagnostics.json`. Audyt bazowego modelu: `docs/reviews/E2-AUDYT-2026-10-26.md`. W03/W05 zostały uzupełnione w wykonawcy bez zmiany reguł; wskazane cztery korekty wymagają zgody.

## Granice wyniku

- E2 nie jest odebrane; wymagane rozstrzygnięcie propozycji v0.7 i ponowna weryfikacja.
- Świadkowie i generator nie wyczerpują przestrzeni stanów.
- G1/G3 w grafie są projekcjami, nie dowodem globalnej osiągalności ani braku zakleszczeń.
- Hypothesis uruchamia pytest; ten raport nie udaje ponownego uruchomienia testów.
- Pusty scope pozostaje unsupported; diagnoza jego guard jest oddzielną próbą predykatu.
- Nie wykonano TLC, dowodów żywotności ani oceny rzeczywistego projektu.
