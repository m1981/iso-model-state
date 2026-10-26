# E3.1 — odwzorowanie lokalnej relacji przed implementacją

2026-10-26. Decyzja agenta E3-DA04 w ramach [przygotowania E3.1](E3-PRZYROST-01.md). Użytkownik polecił „wejdz w role. zgoda, dalej”, co obejmuje pobranie i lokalne użycie TLC oraz wykonanie przyrostu. Semantyka modelu v0.7 pozostaje bez zmiany.

## Rzut i kontekst

Rzut `item` zawiera cały rekord jednego produktu: `id`, `type`, `state`, `depends_on`, `predecessor`, `version`, `rejections`, `suspect`. `depends_on` jest zbiorem ID (kolejność listy wejściowej nie ma znaczenia); `predecessor=none` jest napisem modelu, nie NULL. Pozostałe pola: napisy dla ID/typów/stanów, liczby całkowite dla wersji/licznika i bool dla suspect. Wszystkie niewskazane w skutkach pola muszą być zachowane. Schemat wejściowy jest zamknięty; nieobsługiwane pole/typ lub nieobsługiwana konstrukcja wybranego przejścia powoduje odmowę generowania.

Do porównania z interpreterem tworzymy jego initial_state z YAML i podmieniamy cały rekord `r1` syntetyczną próbką o znanym ID i typie REQ. Inne produkty, pytania i wydania pozostają takie jak w initial_state: bieżące wydanie in_preparation, current_release=1, next_release_required=false, brak pytań. Każdy przypadek jest osobnym krokiem, nie kontynuacją historii. To celowo wstrzyknięte stany jednostkowe, nie dowód osiągalności.

T03 nie tworzy nowego suspect, nie ma skutków zależności, pytań, wydania ani dowodu U w definicji YAML. W tym kontekście oba post_step_effects nie zmieniają wyniku. Porównanie z Pythonem sprawdzi też identyczność całej reszty globalnego stanu. Wersja próbki mieści się w max_version. Licznik wyniku nie jest ograniczany dziedziną 0..MAX_REJECTIONS: mutant bez guard ma ujawnić 3, a nie zostać obcięty. Pełna bramka next_release_required, obserwatory, historia S15 i całe wydanie nie należą do wygenerowanej relacji. Gdy wybrane przejście wymaga innych mechanizmów, translator odmawia zamiast używać tego kontekstu milcząco.

## Translator i jego ograniczenia

Generator wybiera jedno przejście po ID; nie rozpoznaje jego nazwy jako instrukcji zachowania. Generuje predykat `LocalAction(before, after, actor)` z from/to/actor/guard/effects odczytanych z modelu. Warunek odnosi się do before. Najpierw stosowane jest to, potem skutki kolejno — zgodnie z interpreterem. Operacje w tym przyroście: literały bool/int, pola recordu, parametry int/bool, `<`, `=`, `+`, spójniki bool oraz lokalne przypisania do version/rejections/suspect. Stan zmienia wyłącznie pole to (wartość = zachowuje stan); skutek state := ... jest nieobsługiwany i odrzucany także pod fałszywym guard, zgodnie z istniejącym interpreterem. Nieobsługiwane wyrażenia, parametry, arguments, target, evidence lub skutki globalne są błędem, także pod fałszywym guard. Niezmienione pola zachowuje aktualizacja rekordu. Teksty danych są kodowane jako literały, nigdy wklejane jako kod TLA+.

Testy zmienionych danych obejmują również ID, limit, from i to. Osobne mutanty guard/actor/inkrementacji zachowują bazową wyrocznię i mają naruszyć jej oczekiwania. Kontrolowane zmiany from/to/limitu dostają osobne, ręcznie zapisane oczekiwania zgodne z tymi kopiami danych. W żadnym przypadku wiążący YAML nie jest nadpisywany.

## Uprząż TLC i niezależne oczekiwania

Moduł testowy ma trzy zmienne: numer przypadku `case_id`, `phase` (0 albo 1) i rekord `item`. Init wybiera przypadek i jego jawny stan wejściowy. Jedyną akcją Next jest:

- phase=0;
- wygenerowane LocalAction(item, item', aktor z przypadku);
- phase'=1 i niezmienione case_id.

W phase=1 nie ma kolejnej akcji. Nie dodajemy stutter jako zastępstwa akcji. Zestaw jest skończony przez długość jednego kroku i skończoną liczbę próbek, bez obcinania licznika po akcji. `CHECK_DEADLOCK FALSE` wyłącza jedynie traktowanie oczekiwanej odmowy/końca testu jako błędu; nie jest ustawieniem dowodu braku zakleszczeń całego procesu.

Dwie wyrocznie są niezależne od translatora i zapisane w przypadkach:

1. W phase=0: `ENABLED Next` jest dokładnie równe oczekiwanej dostępności. Relacja stale wyłączona obleje przypadek pozytywny; dodatkowa akcja obleje przypadek odmowy.
2. W phase=1: cały rekord item jest dokładnie równy oczekiwanemu następnikowi. TLC bada wszystkich osiągalnych następców; niewłaściwy dodatkowy następnik nie zostanie pominięty. Oczekiwanie nie jest wyliczane przez translator ani interpreter.

TLC zapisuje dump odwiedzonych stanów i pełny log. Raport rozróżnia expected successor (oczekiwanie z przypadku) od wyniku wykonanej kontroli tego oczekiwania. Nie udaje, że oczekiwania są danymi odczytanymi z dump. Dla udanego badania wymagane są poprawny kod zakończenia, komunikat sukcesu, zakończenie oraz statystyki; dla mutanta — rzeczywiste naruszenie właściwej wyroczni, a nie dowolny niezerowy kod.

## Toolchain, wynik i recenzja

TLC 1.7.4, jeden worker, maksymalnie 60 s na przebieg. JAR sprawdzony z SHA-1 wydawcy; SHA-256 pobranych bajtów `936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88`. Java wywoływana pełną ścieżką do JBR PyCharm lub jawnym parametrem; brak globalnej konfiguracji. Skrypt badawczy ma odróżniać sukces, naruszenie własności, błąd narzędzia i timeout; nie pobiera zależności automatycznie. Pomoc i błędy wskazują plik narzędzia, przyczynę i następny krok. To runner badania E3, nie produktowe CLI procesu.

Przed kodem R przegląda ten rzut i kontekst. Po GREEN inny przebieg R odtwarza wyniki i ocenia implementację. Zapis przygotowania i jego wcześniejsza recenzja pozostają historycznymi dokumentami.
