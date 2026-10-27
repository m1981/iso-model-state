# E3.3 — wykonanie

Wynik: **verification_failed**.
Hash źródeł: `d21725679483c50f764ad6d219404527e35ca2615a87afd51812e773a02f84ea`.

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

Świadek ośmiu kroków: True; dwie odmowy: False.
Zakres: pełny katalog, aktywne p1/r1, tylko T00–T04 i predecessor=none, stała topologia, do 16 kroków.
To nie dowód całego procesu, żywotności ani odbiór E3. CHECK_DEADLOCK FALSE dotyczy końca wycinka.
