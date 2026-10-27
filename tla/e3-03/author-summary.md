# E3.3 — wykonanie

Wynik: **checks_passed_not_stage_acceptance**.
Hash źródeł: `e16b2d1a2e35289be0e4ea630b0360ab4a88a0f35912b37f0bf0c49593854eb9`.

| Próba | TLC | Stany | Oczekiwanie spełnione |
|---|---|---:|---|
| baseline | passed | 83 | True |
| renamed | passed | 83 | True |
| limit | passed | 42 | True |
| created_version | passed | 83 | True |
| dependency_types | passed | 13 | True |
| acyclic | passed | 1 | True |
| create_version | Successor | 2 | True |
| create_actor | Availability | — | True |
| dependency_types | Availability | — | True |
| acyclic | Availability | — | True |
| approval | Availability | 4 | True |
| baseline_dependency | Availability | 19 | True |
| baseline_actor | Availability | 6 | True |
| baseline_evidence | Availability | 6 | True |
| CreatedVersion | CreatedVersion | 2 | True |
| ApprovedHistory | ApprovedHistory | 8 | True |

Świadek ośmiu kroków: True; dwie odmowy: True.
Zakres: pełny katalog, aktywne p1/r1, tylko T00–T04 i predecessor=none, stała topologia, do 16 kroków.
To nie dowód całego procesu, żywotności ani odbiór E3. CHECK_DEADLOCK FALSE dotyczy końca wycinka.
