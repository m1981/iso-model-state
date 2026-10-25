# E2 — raport sprawdzeń modelu v0.7

**Status: sprawdzenia zakończone pomyślnie; oczekuje odbioru użytkownika; E2 nie jest odebrane.** DEC-PRO-010 wdrożono w obowiązującym modelu. Regresje dawnych luk sprawdzają odmowę modelu bazowego oraz wykonanie naruszające reguły po celowej mutacji.

## Tożsamość badania

- Model v0.7, SHA-256: `ecca43e1402ee476502943caa16556d5609021b8894f3a702e26ca2da3cf21a6`.
- Kod i dane sprawdzeń SHA-256: `12cf8f7e37d731706f060293f69f5221c26b90950d199f922ab6ae09b8b0bed0`; Python `3.14.7`.
- Pełne scenariusze, wyniki i hashe plików: odtwarzany `evidence.json`. Polecenie: `.venv/bin/python scripts/run_e2.py --output artifacts/e2`. Kod wyjścia 0 oznacza powodzenie sprawdzeń (bez odbioru E2), 1 niepowodzenie sprawdzeń, 2 błąd przygotowania raportu.

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

Niezależny moduł safety.py nie importuje wykonawcy, parsera ani jego helperów. S2/S3/S8/S15 sprawdzają całą historię wersji i wydania; nie przyjmują wstrzykniętego prefiksu jako dowodu. Poniżej mutant jest przypisany wyłącznie do właściwości, której naruszenie wyrocznia rzeczywiście zgłosiła.

| Właściwość | Wykryte mutanty WIT i regresji DEC-PRO-010 |
|---|---|
| S1 | wit1_author_baseline, wit2_author_rejection, s1_agent_includes_scope |
| S2 | wit1_skip_approval |
| S3 | wit1_skip_verification |
| S4 | wit1_unready_dependency, s4_premature_no_impact_review |
| S5 | s5_missing_relink_propagation |
| S6 | s6_review_ignores_retired_dependency |
| S7a | wit1_incomplete_ready, s7a_t10_keeps_readiness, external_scope_change |
| S7b | wit1_incomplete_acceptance, external_scope_change |
| S8 | wit1_skip_review |
| S9 | wit4_two_asked |
| S10 | s10_modifies_accepted_scope, s10_w06_rewrites_accepted |
| S11 | s11_rejection_as_consent, s11_wrong_item, s11_wrong_operation, s11_stale_unused_consent, s11_missing_consumption, s11_p03_changes_binding |
| S12 | s12_active_predecessor, s12_wrong_predecessor_type, s12_relink_without_opening, s12_relink_outside_scope, s12_wrong_successor, s12_immature_successor, s12_missing_relink, s12_rewrites_lineage |
| S13 | s1_agent_includes_scope, s13_drops_predecessor_from_scope, s13_includes_immature_successor, s10_modifies_accepted_scope |
| S14 | late_blocker |
| S15 | rejection_budget |

W pięciu WIT: 0 naruszeń S1–S15. Wykryto 48/48 mutantów prób bramek. Pokrycie właściwości S wykonanymi mutantami niezależnej wyroczni: 16/16; brakujące: []. Próby reguł kolejki lub strażnika T11 mogą nie naruszać żadnej formuły S — nie przypisujemy im sztucznie takiego wyniku.

## Generowanie sekwencji

`tests/test_stateful.py`: RuleBasedStateMachine dla zakresu bazowego, bez p1 i pustego; każda max_examples=24, stateful_step_count=25, derandomize=True. Początek to osiągalny prefiks; dalsze kroki są generowane na nowo. Sprawdzane są S1–S15, odmowy i atomowość. Nie filtrujemy wyników wyroczni. Wyniki pytest są zapisane w STAN, a nie wnioskowane z samego generatora.

Oddzielny deterministyczny przegląd kandydatów w 28 źródłach świadków pokrywa 28 przejść: {'applied': 1063, 'rejected': 766, 'boundary': 24, 'input_error': 0}. To liczby prób kandydatów, nie liczba wszystkich stanów ani kroków Hypothesis. Granice pytań, wersji i wydań są wynikiem boundary, nie dowodem zakleszczenia.

## Regresje zaakceptowanej korekty v0.7

| Przypadek | Obowiązujący model | Mutant |
|---|---|---|
| Pytanie blocking po W02 | W04 odmawia; rozstrzygnięcie pozwala na odbiór | Brak guard W04 wykrywany przez S14 |
| T09/T10 po dwóch odrzuceniach wersji | T10 zachowuje licznik; trzecie T03 odmawia | Reset licznika wykrywany przez S15 |
| Zmiana p1 poza zakresem wydania | Nowe suspect w zakresie cofa ready/reviewed | Usunięcie obserwatora narusza S7a/S7b |
| Pusty zakres | W01 wymaga tests_ok i braku blokad; pełny odbiór możliwy | Stary guard przepuszcza osobno brak testów i blokadę |

Pięć dodatkowych prób ma pełne ślady bazowe i mutantów w evidence.json oraz jawny zakres instancji. tests/test_readiness_matrix.py sprawdza 32 kombinacje zakresu, tests_ok, blocking i stanów pytań; cztery blocking/deferred odmawiają P04 i następnie W01 w zachowanym asked. Testy obejmują też rozwiązanie późnego pytania, dwa budżety różnych wersji i zachowanie odebranego wydania przy wpływie spoza zakresu. Dawny mutant T07(r1) bez invalidate_release jest teraz maskowany poprawnie przez nowy obserwator; zastąpiono go próbą T07(a2) bez zależnych produktów. To kontrola reguły T07, nie S7a. S7a nadal ma własne naruszające mutanty.

Historyczne kontrprzykłady v0.6 i proponowana wtedy kopia: model/proposals/e2-hardening-diagnostics.json. Ich skrypt uruchamiać na commicie de94da9; bieżące regresje nie wykonują historycznego skryptu. Decyzja i lista wpływu: DEC-PRO-010 w docs/STAN.md. Niezależny końcowy przegląd: docs/reviews/E2-V07-PRZEGLAD-2026-10-26.md.

## Granice wyniku

- E2 nie jest odebrane; odbiór użytkownika pozostaje osobną decyzją.
- Świadkowie i generator nie wyczerpują przestrzeni stanów.
- G1/G3 w grafie są projekcjami, nie dowodem globalnej osiągalności ani braku zakleszczeń.
- Hypothesis uruchamia pytest; ten raport nie udaje ponownego uruchomienia testów.
- Nie wykonano TLC, dowodów żywotności ani oceny rzeczywistego projektu.
