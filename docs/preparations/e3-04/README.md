# E3.4 — sprawdzenie przygotowania istniejącym E2

2026-10-27. Ten pakiet sprawdza wykonalność scenariusza z [mapowania](../../E3-04-MAPOWANIE.md). **Nie jest implementacją generatora E3.4, niezależną wyrocznią przyszłego generatora ani wynikiem TLC.** [Recenzja przygotowania](../../reviews/E3-04-PRZYGOTOWANIE-2026-10-27.md) rozdziela własne próby R i wyniki autora.

## Wejścia i wykonany wynik

- `scenario.json`: 26 kroków do siedmiu linii bazowych, 3 kroki zgłoszenia/zatwierdzenia q0, 13 kroków zmiany i przeglądu — razem 42.
- `expected-checkpoints.json`: 14 pełnych ręcznie określonych stanów i wyjść records, od kroku 29 do 42. Oczekiwania nie powstały przez zapis wyniku execute_step. Zapis przygotował autor scenariusza; niezależne autorstwo wyroczni formalnej dopiero nastąpi.
- `refusals.json`: pięć odmów, z punktem ścieżki, zdarzeniem i oczekiwanym kodem.
- `check_preparation.py`: wywołuje istniejący replay/execute_step, porównuje punkty kontrolne, sprawdza odmowy i brak mutacji. Dodatkowo wykonuje oba warianty I03 z osiągalnego prefiksu, w którym c1 jest jeszcze szkicem.

Wynik: **42 kroki wykonane, 14 pełnych punktów zgodnych, 5 odmów bez zmiany stanu, oba I03 zgodne**. r1/a1 kończą w baselined v2, d1/c1 w baselined v1, suspect=false; p1/r2/a2/r3 nie zmieniają rekordów w 13 krokach wycinka. q0/q1 są zużytymi pozytywnymi zgodami. Wydanie nadal in_preparation, bez odbioru.

W I03 po T05(r1) i T13(c1), T01(c1) jest dozwolone przy d1/a1 nadal baselined, choć mają suspect. Po dodatkowej zatwierdzonej zmianie a1 do draft, T13(c1) nie wystarcza i T01(c1) jest odmówione. Model sprawdza w T01 stany bezpośrednich zależności; nie sprawdza ich suspect. T11 ma bardziej rygorystyczny warunek. Wstępne błędne oczekiwanie odmowy pierwszego wariantu poprawiono podczas przeglądu, bez zmiany modelu.

Pierwsze porównanie records wykryło `kind=DEC` w oczekiwaniu autora; istniejący kontrakt E2 używa `kind=decision`. Poprawiono reprezentację oczekiwania. Nie nazywamy tego naprawą procesu ani RED/GREEN generatora. Pozostała macierz i mutanty opisane w mapowaniu są planem późniejszego wykonania E3.4.

## Odtworzenie

Z katalogu głównego repozytorium, przy istniejącym środowisku E2:

```sh
.venv/bin/python docs/preparations/e3-04/check_preparation.py --output artifacts/e3-04/preparation-reproduction
```

Katalog musi być nowy albo pusty. Komenda nie zmienia źródeł, nie wymaga TLC i nie pobiera zależności. Kod 0 oznacza zgodność tego przygotowania; błędne wejścia lub niespełnione oczekiwanie kończą się błędem. Powstaje `summary.json` oraz `evidence.json.gz` zawierający pełne stany przed/po, rekordy DEC i oba odtworzone warianty I03. Skrypt sprawdza hashe wejść przed i po wykonaniu.

## Zachowane dowody

`author-evidence.json.gz` i `reviewer-evidence.json.gz` zachowują pełne wyniki dwóch odtworzeń. Odpowiednie `*-summary.json` podają 21 hashy źródeł oraz sumy kompresji i rozpakowanych bajtów. [Manifest](manifest.json) obejmuje pliki wejściowe i dowodowe; ścieżki oryginałów są zapisane dla identyfikacji, do odczytu wystarczają pliki repozytorium.

```sh
gzip -dc docs/preparations/e3-04/author-evidence.json.gz
```

Wspólny hash źródeł przygotowania: `26e63b7d4d94dac480dafef5f2f1a6d01ef4f93fe6f9192529c0e84b4b736929`. Kontrola spójności modelu: **413 OK**, log `consistency.log`. Historyczne 449 testów i 27 prób TLC dotyczą dostawy E3.3; nie ponawiano ich dla samej dokumentacji i pomocniczego preflight bez zmian implementacji modelu.

Następne działanie A: niezależny autor pełnej wyroczni E3.4, potem RED → GREEN generatora zgodnie z mapowaniem. Odbiór całego E3 pozostaje po zakończeniu pozostałego zakresu planu.
