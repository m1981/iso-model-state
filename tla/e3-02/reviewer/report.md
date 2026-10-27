# E3.2 — wynik badania

Wynik: **checks_passed_not_stage_acceptance**.

Hash wejść: `3b527c6de498bd4a4da3c77a45fb7a4b4432e1375eab5f3dbeb2c1f6f2d8126e`.

| Próba | TLC | Stany | Oczekiwanie spełnione |
|---|---|---:|---|
| req_approved | passed | 9 | True |
| req_baselined | passed | 9 | True |
| req_draft | passed | 1 | True |
| req_suspect | passed | 1 | True |
| plan_empty | passed | 9 | True |
| des_no_approval | passed | 6 | True |
| code_good | passed | 6 | True |
| code_mixed | passed | 1 | True |
| renamed | passed | 9 | True |
| limit | passed | 6 | True |
| approval_metadata | passed | 9 | True |
| dependency | Availability | — | True |
| checks | Availability | — | True |
| suspect | Availability | — | True |
| verification | Availability | — | True |
| actor | Availability | 2 | True |
| evidence | Availability | 2 | True |
| budget | Availability | 8 | True |
| reset | Successor | 5 | True |
| verification | VerifiedHistory | 3 | True |
| budget | HistoryBudget | 10 | True |
| reset | CounterHistory | 5 | True |

Świadek zatwierdzenia po dwóch odrzuceniach: True

Granice: syntetyczne Init, jeden zmieniany rekord, stałe zależności i wersja, do 8 akcji.
CHECK_DEADLOCK FALSE dotyczy tylko tego wycinka. Brak dowodu pełnych S/L/F, osiągalności od Init procesu, braku zakleszczeń i odbioru E3.
Każdy mutant ma osobny wykonany świadek; pełne dane, wyniki porównania grafów, logi i dump w evidence.json.
