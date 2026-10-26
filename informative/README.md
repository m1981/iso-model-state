# informative/ — materiały informacyjne (niewiążące)

Ten folder jest **informacyjny** w sensie norm ISO: wyjaśnia, uzasadnia i przechowuje materiał źródłowy, ale niczego nie wymaga. Tak samo norma oznacza swoje aneksy „(informative)” w odróżnieniu od treści normatywnej.

## Reguła pierwszeństwa

1. Wiążące (normatywne) są wyłącznie: `docs/KARTA-CELU-I-ZAKRESU.md` (DEC-PRO-007), `PLAN.md`, `model/process.yaml`, `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `docs/WSPOLPRACA.md`, `docs/STAN.md` i decyzje DEC-PRO-nnn zapisane w `docs/STAN.md`.
2. Gdy cokolwiek w `informative/` przeczy dokumentom wiążącym, **rozstrzygają dokumenty wiążące**. Sprzeczność agent zgłasza jako sprawę do poprawienia (w `informative/`), a nie jako powód do zmiany modelu.
3. Treść z `informative/` staje się wiążąca tylko przez decyzję DEC-PRO-nnn, która przenosi ją do dokumentu wiążącego.
4. Programy sprawdzające (E2–E5) nie czytają `informative/`: identyfikatory w tym folderze nie są definicjami ani odwołaniami.
5. Pliki są migawką z daty w nagłówku; nie aktualizujemy ich wstecz, tylko dopisujemy nowe.

## Zawartość

| Plik | Co to jest | Data |
|---|---|---|
| `SESJA-2026-10-23.md` | Zapis sesji założycielskiej: przebieg, decyzje i ich motywacje, wnioski, techniki weryfikacji | 2026-10-23 |
| `NORMA.md` | Gdzie jest pełny tekst ISO/IEC 29110-5-1-2 i jak z niego korzystać; wykryte w normie niespójności | 2026-10-23 |
| `PRZEGLAD-VCS-LITE.md` | Przegląd projektu vcs-lite względem normy: niespójności, luki, co działa | 2026-10-23 |
| `szablon-projektu/` | Szablon dokumentów dla nowych projektów (wejście do etapu E5) | 2026-10-23 |
| `WIZUALIZACJA-2026-10-24.md`, `visuals-v0.4/` | Przewodnik po modelu v0.4, trzy diagramy i mapowanie tematów dziewięciu pakietów Aneksu E | 2026-10-24 |
| `ROADMAPA-2026-10-24.md` | Propozycja dostaw w ramach E2–E5 i konkretny zakres pierwszego wykonywalnego WIT1 | 2026-10-24 |
| `KARTA-CELU-I-ZAKRESU-2026-10-24.md` | Historyczna propozycja; przyjęta treść jest w [docs/KARTA-CELU-I-ZAKRESU.md](../docs/KARTA-CELU-I-ZAKRESU.md), DEC-PRO-007 | 2026-10-24 |
| `retrospektywa-vcs-lite-2026-10-26/wywiad-e5a1/WNIOSKI.md` | [Zweryfikowane wnioski z wywiadu z agentem vcs_lite](retrospektywa-vcs-lite-2026-10-26/wywiad-e5a1/WNIOSKI.md), cztery wymiany, dowody i trzy projekty eksperymentów; bez zmiany modelu | 2026-10-26 |
| `retrospektywa-vcs-lite-2026-10-26/wywiad-8f641/STATUS.md` | [Drugi wywiad — stan i kontynuacja](retrospektywa-vcs-lite-2026-10-26/wywiad-8f641/STATUS.md): trzy rundy i zweryfikowane ustalenia wstępne; czwarta niewysłana, limit 5h = 100%; oryginał nienaruszony | 2026-10-26 |
