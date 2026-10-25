# Korekta potrzebna do odbioru E2 — propozycja v0.7

Data przyjęcia: 2026-10-26. Status: **applied — DEC-PRO-010**, cytat użytkownika „d1 tak”. Pakiet wdrożono jako v0.7. Poniżej zachowano historyczną treść propozycji i diagnostyki v0.6; źródłem reguł jest model/process.yaml. Aktualne wyniki są w docs/E2-RAPORT.md. Przyjęcie korekty nie odbiera E2.

## Jedna rekomendacja

Przyjąć jako v0.7 cztery korekty poniżej wraz z właściwościami bezpieczeństwa S14/S15, zachowując kolejność E2–E5 i cały DoD. Następnie zastosować pakiet do modelu, dokończyć sprawdzenia oraz ponowić niezależny przegląd przed osobną bramką odbioru E2. Przyjęcie propozycji nie jest odbiorem E2.

| Problem i dowód | Proponowana reguła | Efekt dla operatora |
|---|---|---|
| Po W02 można zgłosić P00(blocking=true), a W04 nadal odbiera wydanie. Ślad 30 kroków na stałej instancji. Obecne S1–S13 nie zabraniają tego wprost | W04 wymaga braku pytań blocking w open/asked. Nie cofamy samego reviewed; po rozstrzygnięciu pytania odbiór znów jest dostępny | Późno zgłoszona blokada nie ginie przed podpisem |
| Dwa T03, potem T09/T10 zerują licznik bez nowej wersji. Trzecie odrzucenie tej samej wersji jest możliwe po 9 krokach | T10 zachowuje rejections. Zerowanie pozostaje przy otwarciu nowej wersji przez T05/T06 | Limit poprawek nie daje się obejść odłożeniem pracy |
| W01 wiąże tests_ok i pytania wewnątrz implikacji forall. Dla pustego scope predykat jest true mimo testów false albo pytania blokującego. Wykonawca dotąd odmawia całej obsługi pustego scope | Nawias ogranicza forall do kompletności produktów; tests_ok i brak pytań są globalne. Usunąć ograniczenie wykonawcy dla pustego scope po przyjęciu jednoznacznej reguły | Pusta dostawa też wymaga przejścia bramek. Przy poprawnych testach i bez blokad pozostaje dopuszczalna — nie ustanawiamy nowego zakazu pustych wydań |
| W dozwolonej alternatywnej instancji, gdy p1 leży poza scope, T05(p1) oznacza elementy zakresu suspect, lecz wydanie pozostaje reviewed i może zostać odebrane: S7a/S7b. To nie kontrprzykład stałego zakresu v0.6 | Nowy obserwator po kroku cofa ready/reviewed do in_preparation, jeżeli nowy suspect pojawił się w zakresie, niezależnie od położenia zmienionego źródła | Ocena gotowości uwzględnia również wpływ zmian spoza dostawy |

Ostatnia korekta nie zmienia odbiorów historycznych: istniejący obserwator po accepted nadal wymusza W06, a odebrany rekord pozostaje identyczny. Nie zmieniamy zakresu, helpera invalidate_release ani polityki następstwa.

## Dokładny zapis

[Propozycja YAML](e2-hardening.yaml) zawiera docelowe guard/effects i nowy obserwator. Jest osobnym plikiem danych eksperymentu; zwykły wykonawca ładuje wyłącznie obowiązujący model. W implementacji dodano już możliwość wykonania przypisania `release.state` z obserwatora, aby zbadać proponowaną kopię; v0.6 nie zawiera takiego obserwatora.

Nowe właściwości proponowane do zatwierdzenia:

- **S14 — brak blokady przy odbiorze:** dla każdego W04 w stanie przed krokiem nie istnieje pytanie `blocking and state in {open, asked}`. Mutant: W04 guard=true, osiągalny późny blocker po W02. Stan reviewed sam w sobie nie musi oznaczać braku pytań.
- **S15 — budżet odrzuceń wersji:** dla każdej pary (ID, wersja) liczba wykonanych T03 w całej historii nie przekracza MAX_REJECTIONS. Dodatkowo T10 nie zeruje licznika tej wersji; T05/T06 otwierają nową wersję. Mutant: przywrócone `rejections := 0` w T10. L4 zachowuje cel ograniczenia cyklu poprawek i odwołuje się do S15; sam warunek wartości bieżącego licznika jest niewystarczający.

S7a/S7b pozostają niezmienione; rozszerzamy ich przypadki o jawnie oznaczoną alternatywną instancję. Regułę W01 sprawdzimy dla niepustego i pustego zakresu, w kombinacjach tests_ok oraz open/asked/resolved/deferred i blocking.

## Co już sprawdzono, a co wymaga wdrożenia

Odtworzenie:

```sh
.venv/bin/python model/proposals/e2_hardening_diagnostics.py
.venv/bin/python -m pytest -q tests/test_e2_diagnostics.py
```

Diagnostyka odtwarza wszystkie trzy sekwencje na v0.6, a potem na zmienionej kopii w pamięci. Po korekcie: W04 zatrzymuje późną blokadę, trzecie T03 tej samej wersji jest odrzucone, a zmiana spoza zakresu cofa reviewed i blokuje odbiór niekompletnej dostawy. Dane i obserwacje są w [zapisie diagnostyki](e2-hardening-diagnostics.json).

Pusty zakres sprawdzono **wyłącznie na wyrażeniu guard**: obecny predykat daje true we wszystkich trzech próbach, proponowany daje true/false/false odpowiednio dla (testy OK, brak blokady), (testy nie przechodzą), (pytanie blokujące). Bieżący wykonawca nadal zwraca unsupported dla pustego zakresu. Pełna obsługa i test wykonania nastąpią po decyzji; nie przedstawiamy samej ewaluacji predykatu jako wykonanego wydania.

Nowe testy diagnostyczne są zielone, ponieważ potwierdzają istnienie znanych luk i działanie proponowanej kopii. Nie są dowodem bezpieczeństwa obowiązującego modelu. Raport E2 musi zachować status wymagający decyzji.

Niezależne źródło oceny: [audyt modelu](../../docs/reviews/E2-AUDYT-2026-10-26.md). Autor audytu nie miał historii implementacji, odtworzył bazę z Git i ocenił minimalność korekty. To nie odbiór etapu.

## Lista wpływu do zastosowania po zgodzie

- Model: v0.7, T10, W01, W04, nowy post_step_effect; opisy reguł wydań i licznika.
- Właściwości: S14/S15, doprecyzowanie L4 i granic instancji; pozostałe S i WIT bez osłabienia.
- Interpretacje: INT-011 (limit wersji), INT-012/017 (wpływ zmiany na gotowość), nowa interpretacja bramki pytań, jeśli potrzebna do jednoznacznego odwołania.
- PLAN: zakres bezpieczeństwa obejmuje nowe S; kolejność i kryteria etapów bez zmian.
- Wykonawca: usunięcie blokady pustego zakresu po ujednoznacznieniu W01, bez specjalnej obsługi ID W01.
- Dowody: niezależne S14/S15, mutanty, regresja 28 przejść, WIT1–WIT5, Hypothesis, przypadki alternatywnego zakresu, raport i ponowny przegląd.
- Rejestry: nowa DEC z cytatem użytkownika, polami „Zmienia” i „Przejrzane”, status applied tej propozycji i aktualizacja STAN.

Podstawa bramki: [WSPOLPRACA §2.1 i §2.3](../../docs/WSPOLPRACA.md): „zmiana czegoś, co użytkownik już zaakceptował” oraz „luka albo sprzeczność w dokumentach zamiaru”. Dlatego agent przygotowuje kompletną korektę i dowody, ale nie wdraża nowej polityki bez decyzji.

Jeśli propozycja zostanie odrzucona, v0.6 pozostaje obowiązujące, a E2 pozostaje otwarte z tymi ograniczeniami. Alternatywa: osobno rozstrzygnąć politykę każdej z czterech sytuacji; nie rekomendujemy przemilczania naruszeń.

Historyczną diagnostykę v0.6 odtwarzać na commicie `de94da9`. Bieżące wykonane regresje v0.7: `mutants/e2_hardening.json`, `src/isomodel/hardening.py`; aktualny [raport E2](../../docs/E2-RAPORT.md).
