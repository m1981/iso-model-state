Kontynuujemy projekt iso-model-state: model stanów produktów pracy według ISO/IEC 29110-5-1-2 (profil Basic) dla pracy użytkownika z agentem LLM, z dowodami poprawności (pytest, Hypothesis, TLA+). Repozytorium: https://github.com/m1981/iso-model-state, gałąź robocza `e1-model`.

Ten plik mówi tylko, co przeczytać i jakie zasady obowiązują. Nie zawiera stanu prac: stan jest wyłącznie w docs/STAN.md.

Zanim cokolwiek zrobisz, przeczytaj w tej kolejności:
1. docs/WSPOLPRACA.md: kontrakt współpracy (BLUF, jedna decyzja na wiadomość, decyzja zawsze na samym dole, lista eskalacji). Ma pierwszeństwo nad pozostałymi zasadami.
2. docs/STAN.md: punkt wznowienia, decyzje DEC-PRO-nnn, sprawy otwarte.
3. PLAN.md: cel, DoD 1–10, etapy E0–E5, ryzyka.
4. model/process.yaml: model (wiążący).
5. docs/WLASCIWOSCI.md: właściwości G, S, L, założenia F, ścieżki świadkowie WIT.
6. docs/INTERPRETACJE.md: rozstrzygnięcia luk normy INT-nnn.
7. informative/README.md, potem według potrzeby: informative/SESJA-2026-10-23.md (motywacje decyzji), informative/NORMA.md, informative/PRZEGLAD-VCS-LITE.md, informative/szablon-projektu/.

Zasady stałe:
- informative/ jest niewiążący. Przy sprzeczności rozstrzygają dokumenty wiążące; sprzeczność zgłoś jako sprawę do poprawienia w informative/.
- Pełny tekst normy: https://github.com/m1981/iso-29110-5-1/tree/main/chapters (lokalnie u użytkownika /Users/michal/PycharmProjects/iso-29110-5-1). Czytaj rozdział, gdy potrzebujesz dokładnego brzmienia; nie kopiuj treści normy do repozytorium, odwołuj się do numerów (PM.02.03, WP.13, Tabela 12).
- Język (DEC-PRO-002): kody, identyfikatory, atrybuty i kod źródłowy po angielsku w terminologii normy; proza, opisy i cytaty po polsku.
- Kolejność pracy: model i właściwości → przegląd użytkownika (bramka) → testy, które oblewają z właściwego powodu → kod → dowody.
- Każda zmiana czegoś zaakceptowanego: decyzja z polami „Zmienia” i „Przejrzane”, w tej samej edycji.
- Pracujesz na gałęziach i je wypychasz; scalenie do main tylko za zgodą użytkownika.
- Na końcu sesji nadpisz docs/STAN.md.
