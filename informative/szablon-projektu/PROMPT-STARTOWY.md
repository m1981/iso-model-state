Kontynuujemy projekt <projekt> (<jedno zdanie: co to jest>) w <ścieżka do repozytorium>.

Ten plik mówi tylko, co przeczytać i jakie zasady obowiązują. Nie zawiera stanu prac: stan jest wyłącznie w docs/STAN.md. Jeśli coś tutaj przeczy docs/STAN.md albo docs/SPEC.md, rozstrzygają te dokumenty, a niezgodność zgłoś jako sprawę z listy eskalacji.

Zanim cokolwiek zrobisz, przeczytaj w tej kolejności:
1. docs/WSPOLPRACA.md: kontrakt współpracy. Ma pierwszeństwo nad pozostałymi zasadami.
2. docs/STAN.md: punkt wznowienia, ostatni przebieg testów, sprawy otwarte, rejestr korekt.
3. docs/KARTA-PROJEKTU.md: umowa, plan etapów, role, ryzyka, wersjonowanie, instrukcje dostawy.
4. docs/SPEC.md: decyzje (DEC), wymagania (REQ), przypadki użycia, weryfikacja (VER), rejestr pytań.
5. docs/DESIGN.md: projekt (DES), środowisko, wiedza techniczna (pułapki).
6. docs/ui-reference/: wiążący wzorzec wyglądu (jeśli projekt ma interfejs).
7. docs/ACCEPTANCE.feature, docs/MANUAL.md, docs/TRACE.md (generowany).
8. docs/RETROSPEKTYWA.md: czego unikać.

Zasady stałe (szczegóły w dokumentach powyżej):
- Język komunikacji i dokumentów: według KARTA-PROJEKTU.md §1.
- Specyfikacja przed kodem: decyzja (DEC z cytatem użytkownika) → REQ, DES, AT → test, który oblewa z właściwego powodu → kod.
- Każda zmiana czegoś zaakceptowanego przechodzi listę kontrolną zmiany (SPEC.md, „Zarządzanie zmianą”) w tej samej edycji.
- Commity, pushe i wydania według KARTA-PROJEKTU.md §8.
- Testy: polecenie i miejsce logu według DESIGN.md, „Środowisko”. Czytaj pełny log, nie ucinaj treści błędów filtrem.
- Wiedzę techniczną zdobytą w sesji (pułapki, obejścia) zapisuj w DESIGN.md, „Wiedza techniczna”, a nie w tym pliku.
- Na końcu sesji nadpisz docs/STAN.md.
