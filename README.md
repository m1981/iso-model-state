# iso-model-state

Model stanów produktów pracy według ISO/IEC 29110-5-1-2 (profil Basic) dla projektów prowadzonych przez użytkownika z agentem LLM, wraz z dowodami poprawności.

Nową sesję z agentem zaczynaj treścią `PROMPT-STARTOWY.md`.

## Wiążące (normatywne)

| Plik | Zawartość |
|---|---|
| `PROMPT-STARTOWY.md` | Wejście do sesji: co czytać, zasady stałe (bez stanu prac) |
| `PLAN.md` | Cel, Definition of Done, etapy E0–E5, narzędzia, ryzyka |
| `model/process.yaml` | **Model**: aktorzy, typy produktów, stany, przejścia, warunki, skutki, instancja testowa |
| `docs/WLASCIWOSCI.md` | Właściwości do udowodnienia: struktura, bezpieczeństwo, żywotność, sprawiedliwość, ścieżki świadkowie |
| `docs/INTERPRETACJE.md` | Rejestr interpretacji normy (INT): jak rozstrzygamy jej luki i sprzeczności |
| `docs/STAN.md` | Punkt wznowienia i decyzje DEC-PRO-nnn |
| `docs/WSPOLPRACA.md` | Kontrakt współpracy użytkownika i agenta |

## Informacyjne (niewiążące)

`informative/`: zapis sesji z motywacjami decyzji, wskazanie pełnego tekstu normy i jej niespójności, przegląd vcs-lite, szablon projektu. Przy sprzeczności rozstrzygają pliki wiążące (`informative/README.md`).

Identyfikatory tego repozytorium mają prefiks `PRO`.
