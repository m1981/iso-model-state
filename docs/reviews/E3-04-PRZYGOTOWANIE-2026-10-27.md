# Niezależny przegląd przygotowania E3.4 — 2026-10-27

**Wniosek: brak otwartych ustaleń blokujących przygotowanie E3.4.** Po poprawieniu I03 mapowanie jest zgodne z modelem v0.7; ręczny świadek jest wykonalny istniejącym E2. Ten przegląd nie jest dowodem TLC E3.4, realizacją jego macierzy mutantów ani odbiorem E3. Następna dostawa zaczyna się od niezależnej wyroczni i RED przed rozszerzeniem generatora.

## Przedmiot i niezależność

R pracował w osobnym przebiegu, bez historii tworzenia mapowania, na bazie `3195a84c20303e87790a0c77ec17d2d33504ab1f`. Przeczytał PROMPT-STARTOWY, kontrakt współpracy, stan i decyzje DEC-PRO-008/009/010, kartę celu, PLAN, model, właściwości, interpretacje i regułę pierwszeństwa informative. Przedmiotem jest [mapowanie E3.4](../E3-04-MAPOWANIE.md), jego 42-krokowy świadek i rozdzielenie przygotowania od przyszłego wykonania. Uwzględniono wykonawcę E2 oraz zaakceptowaną w PLAN metodę osobnej recenzji przed rozszerzeniem generatora.

R utworzył wyłącznie ten raport jako dokument źródłowy oraz odtworzył preflight autora do osobnego katalogu wyników `artifacts/e3-04/preparation-reviewer`. Nie implementował wyroczni, translatora ani testów, nie zmieniał modelu i nie wykonywał commitu. Własne próby były lokalnymi wywołaniami istniejącego `execute_step`/`replay` w pamięci, z demonstracyjnymi dowodami. Nie kontaktowały się z usługami ani rzeczywistymi danymi projektu.

| Oceniony przedmiot | SHA-256 bajtów |
|---|---|
| Mapowanie E3.4, po korekcie I03 i zapisie wyniku przygotowania | `c1c13010e6a6c8ad28e203b70460ba8f3bd509c03c78704559a9ce095fe32148` |
| Model v0.7 | `2d329822e239555c1642d0a5a20aae0eb28fee17a6f2ff13968e48d7f428fc07` |
| Wykonawca E2 | `0180a0a4f80577709e44413a1db492cfce25e1b55d211b5c710354e1082fb197` |
| scenario.json | `4c90d18b6209617b1b9cb1a514c3a958c89997f00279e2d7af76d69fd609ea22` |
| expected-checkpoints.json | `89a4a5517bbab803d8b1beff192406fa90d82105830ff1494702543f3d66fac1` |
| refusals.json | `3f6d62cc530aeedccc3402fd021889595009d8fde3d08838233c9fa739f2ca4d` |
| check_preparation.py | `14dc6fe09377c69ff8d57ea2a21266f7dc565c5979024d2b5532d89e02df8163` |

## Zamknięte ustalenie R-E3-04-01

Pierwotny I03 sugerował odmowę T01(c1) po pozostawieniu c1 w draft, zmianie r1 i T13(c1). To nie jest wynik tej ścieżki w v0.7: bezpośrednie zależności c1, czyli d1/a1, pozostają baselined, choć suspect=true. T01 sprawdza ich dojrzałość, lecz nie flagi suspect zależności. Po skasowaniu własnej flagi przez T13, T01(c1) jest dozwolone.

R zgłosił problem autorowi i wykonał niezależną próbę: prefiks WIT3 bez T01/T04(c1), następnie P00/P01/P02 z approved na r1/T05, T05(r1), T13(c1), T01(c1). Wszystkie kroki zostały zastosowane; wynik c1 to verified/v1/suspect=false, d1/a1 pozostają baselined/v1/suspect=true, r1 jest draft/v2. Pierwsza próba uruchomienia nie miała PYTHONPATH i zakończyła się ModuleNotFoundError; wynik semantyczny pochodzi dopiero z poprawnego uruchomienia `PYTHONPATH=src .venv/bin/python`.

Autor poprawił I03: zapisuje dozwolony wynik powyżej oraz osobny wariant z T12(a1), P01/P02 approved, T05(a1), po którym a1 jest draft i T01(c1) po T13 nie przechodzi. Ten drugi wynik wynika wprost z bezpośredniej zależności a1 i guard T01; oba warianty potwierdziło następnie odtworzenie preflight autora przez R. R ponownie przeczytał poprawkę i zamknął ustalenie. Nie wprowadzono silniejszego warunku do modelu ani nie utożsamiono T13 z T11.

## Ocena zakresu i warunków wykonania

| Kryterium | Ocena R |
|---|---|
| Korzyść użytkowa | Lista dokładnie d1/a1/c1 po zmianie r1 odpowiada celowi widocznego wpływu zmian. Ocena treści „d1/c1 bez wpływu” jest jawnym założeniem demonstracji; automat jej nie dowodzi. |
| Zgodność v0.7 | T05 wymaga siedmiu składników authorized_change, konsumuje zgodę, zmienia wersję, resetuje licznik i własną flagę, oznacza przechodnich zależnych. T11 wymaga dojrzałych zależności bez suspect i evidence. T12 tworzy powiązane pytanie, T13 dotyczy tylko szkicu. Skutki i odmowy głównego świadka odpowiadają tym regułom. |
| Punkt wejścia | 26 kroków produktów oraz P00/P01/P02 tworzą 29-krokowy prefiks. Główny graf rozpoczyna się po nim; nie jest dowodem TLC od Init procesu. Monitory muszą otrzymać rzeczywistą historię prefiksu według ID, wersji i operacji. |
| Pełna rama | Osiem produktów, pełne pytania i pełne sterowanie wydaniem są potrzebne, nawet przy czterech aktywnych produktach. Stała topologia dopuszcza specjalizację domknięcia wyliczonego z danych; kontrola a1→r2 ujawnia zaszycie oczekiwanych ID. |
| Głębokość i granice | 16 kroków obejmuje 13-krokowy świadek, lecz nie wszystkie sposoby uporządkowania pytań. Limity pytań, wersji i głębokości muszą pozostać granicami badania. Ocena następnika przed odcięciem oraz osobne próby poza granicą chronią przed ukryciem mutanta. CHECK_DEADLOCK FALSE i wyłączenie L/F są jawne. |
| Atomowość | Zużycie q, nowa wersja, propagacja, helper i obserwatory stanowią jeden krok. Nowe suspect należy wyliczyć jako różnicę flag pre/post. Błąd lub odmowa nie zmienia żadnego pola ani records. |
| DEC | P02 tworzy wynik kroku z resolution i powiązaniem element/wersja/operacja; nie jest to nowy trwały rejestr modelu. Niejednoznaczne P02 nie tworzy DEC. T11 wymaga evidence, ale nie generuje osobnego records w obecnym E2. |
| Globalny wpływ | R01–R04 poprawnie rozdzielają helper od obserwatora: liść izoluje helper, źródło poza scope z zależnymi w scope izoluje obserwator. Accepted pozostaje niezmienne, a pending blokuje T/P do W06. W06 pozostaje poza przyrostem. |
| Wyrocznia | Osobny autor ma zapisać pełne oczekiwania niezależnie od translatora, `_dependents` i wyników E2. Ręczne checkpointy przygotowania nie mogą automatycznie stać się przyszłą wyrocznią. Porównanie samych Python/TLC nie zastępuje tej niezależności. |
| Czułość | A01/A04 izolują wersję i consumed; pominięcie consumed w skutku bada się od razu, bez maskowania późniejszą złą wersją. Próby T11 rozdzielają dojrzałość i suspect zależności. Monitory historii wymagają własnych świadków czułości, poza ogólną różnicą następników. |
| Dostępność | ExpectedEnabled/ExpectedStep nie mogą ograniczać Next. Domeny obejmują wszystkich aktorów i reprezentowane kombinacje danych; nie wolno ograniczać T12 do jednego wniosku na produkt ani prób do ścieżki poprawnej. Niepoprawne wejście, guard=false i granica badania mają odrębne wyniki. |
| Status dowodów | Plan mutantów, porównanie pełnych grafów i TLC pozostają przyszłą pracą. Brak narzędzia, błędna składnia, timeout, nieobsługiwana semantyka lub odcięcie nie są zabiciem mutanta. |

Przy implementacji szczególnej uwagi wymaga granica porównania z E2: `execute_step` sprawdza limit na gotowym kandydacie, ale zgłasza ExplorationBoundary bez zwrócenia tego następnika. Przyszła uprząż nie może z samego wyjątku wywnioskować poprawności efektów kroku poza limitem. Sposób obserwacji takiego następstwa trzeba jawnie opisać i sprawdzić przed zaliczeniem prób granicznych; to realizacja już zapisanego wymagania mapowania, nie rozszerzenie zakresu.

## Rzeczywiście wykonane próby R

1. **Świadek:** ponowne wykonanie `docs/preparations/e3-04/scenario.json` przez istniejące `replay` zakończyło się completed, 42 krokami i dwoma demonstracyjnymi DEC (q0/r1/v1/T05 w kroku 29; q1/a1/v1/T05 w kroku 37). R sprawdził następstwa kroków 29–42 oraz niezależnie asercjami końcowe wersje r1/a1=2, d1/c1=1, baselined, brak suspect, identyczność p1/r2/a2/r3 i wydania wobec punktu wejścia, brak pending oraz zużycie obu zgód.
2. **Odmowy:** pięć prób z `refusals.json` wykonano na zapisanych stanach świadka. Po kroku 30 T11(d1) daje guard, T13(a1) daje state; po 33 ponowna zgoda q0 daje guard; po 34 T11(c1) daje guard; po 41 T11(c1) bez evidence daje evidence. Każda odmowa zachowała cały wejściowy stan.
3. **Globalny wpływ:** niezależny prefiks z pierwszych 26 kroków istniejącego WIT3, zgodą przez P00/P01/P02 przed W01 i następnie W01/W02/W04 według potrzeby. Dwanaście kombinacji r1/a2 × w/poza scope × ready/reviewed/accepted. Zmiana r1 w obu zakresach i a2 w zakresie cofa ready/reviewed do in_preparation; accepted pozostaje identyczne i ustawia pending. Zmiana liścia a2 poza scope zachowuje wydanie i pending=false. W trzech przypadkach accepted+pending kolejna próba T11 została odrzucona kodem pending_release. Zakresy alternatywne były kopiami danych instancji w pamięci.
4. **I03:** własna próba opisana przy R-E3-04-01. Nie wykonano mutacji modelu ani TLC; nie ponawiano pełnej regresji E2 dla dokumentacyjnego przygotowania.
5. **Odtworzenie preflight:** po przeczytaniu skryptu R uruchomił `.venv/bin/python docs/preparations/e3-04/check_preparation.py --output artifacts/e3-04/preparation-reviewer`. Wynik: 42 kroki, 14 pełnych checkpointów wraz z records, pięć odmów bez zmiany stanu i oba warianty I03. Skrypt sprawdza hashe źródeł przed i po próbie, zachowuje pełne ślady i odmowy w archiwum, a porównanie stanów normalizuje tylko serializację JSON. Podsumowania autora i recenzenta są identyczne. Zbiorczy fingerprint źródeł: `26e63b7d4d94dac480dafef5f2f1a6d01ef4f93fe6f9192529c0e84b4b736929`; SHA-256 `evidence.json.gz`: `35f5a0659239b53f39ebf4e661493f896e4320f9da5355fa86150d1c5efc21e3`. To odtworzenie pomocniczego preflight, nie niezależne autorstwo jego oczekiwań. Poprawkę ręcznego records.kind z DEC na decision ujawniono w mapowaniu; końcowe oczekiwanie zgadza się z istniejącym kontraktem E2.

Te próby potwierdzają wykonalność przygotowania i poprawność podanych lokalnych oczekiwań. Nie stanowią wyczerpującego badania przyszłego grafu E3.4 ani oceny całych S/L/F. Trwały preflight autora ma odrębne wyniki i pochodzenie; nie należy sumować jego kontroli z powyższymi jako liczby testów regresji.

## Dalsza odpowiedzialność

A zachowuje prefiks, pełne stany i wyniki przygotowania oraz aktualizuje punkt wznowienia. W przyszłym wykonaniu osobny autor wyroczni ustala oczekiwania, autor generatora realizuje RED/GREEN i badanie, a niezależny R odtwarza finalne wyniki oraz ocenia czułość i granice. U rozstrzyga nową lukę zaakceptowanych reguł lub odbiera cały E3 po jego ukończeniu; ten raport nie zastępuje żadnej z tych decyzji.
