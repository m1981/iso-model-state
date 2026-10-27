# E3.3 — utworzenie produktów i dynamiczna dojrzałość zależności

2026-10-27. U: „super przyklad, wykonaj e3.3 jak planowales”. Kontynuacja po 1585449, w reżimie PLAN: niezależny przegląd mapowania, osobny autor wyroczni, TDD, TLC, niezależne odtworzenie. Bez zmian modelu v0.7, właściwości, kolejności E3–E5 i bez odbioru całego E3. Toolchain zgodnie z DEC-PRO-013.

## Cel użytkowy i instancja

Przykład objaśniający: plan lokalnej aplikacji do zadań oraz wymaganie trwałego oznaczania zadania jako wykonanego. To etykiety dla p1 (PLAN) i r1 (REQ), a nie działająca aplikacja. Badanie sprawdza procedurę, nie prawdziwość wyników testów zapisu na dysku.

Badamy przejścia T00–T04 na p1 i r1, w obu kolejnościach i wszystkich przeplotach, przy wszystkich A/R/U, checks=true/false i evidence=true/false. Katalog zachowuje **wszystkie osiem rekordów z initial_state modelu**. Pozostałe sześć produktów nie wykonuje akcji i ma niezmienną ramę; pytania i wydanie pozostają w rzeczywistym stanie początkowym. Init podstawowego badania jest rzutem rzeczywistego Init, a każdy poprawny krok sprawdzamy również istniejącym interpreterem na pełnym stanie. Nie oznacza to eksploracji wszystkich przejść ani świadków pełnego procesu.

Dynamiczne są stany produktów, wersja ustawiana przez T00 i liczniki odrzuceń. Topologia depends_on nie zmienia się: r1 wskazuje p1; nie obejmujemy T14 ani propagacji zmian. Zależności T01/T04 czytane są z **bieżącego katalogu**, nie migawki początku próby.

## Rzut i translacja

Zmienna items zawiera pełne rekordy o ośmiu polach; katalog jest funkcją ID → rekord. Każda akcja zmienia dokładnie jeden rekord. From/to/actor/guard/effects/evidence pochodzą z YAML, a ID tylko wybiera definicję. Zachować kontrole i historię E3.1/E3.2.

T00 w tym przyroście tworzy nowy produkt: predecessor jest niepodanym argumentem z domyślnym none. Odmienna deklaracja arguments, brak default lub nieobsługiwane przypisanie są czytelną odmową. Zastąpienie produktu z niepustym predecessor pozostaje poza E3.3; nie wolno takiego wejścia milcząco zamienić na none. Mimo ograniczenia wejść całe wyrażenie guard, łącznie z gałęzią poprzednika i lookup none, podlega kompilacji. Nieobsługiwane konstrukcje są odrzucane również w nieaktywnej gałęzi.

dependency_types_ok sprawdza typy bezpośrednich zależności w katalogu. acyclic_dependencies sprawdza cały graf katalogu, także zamrożone produkty. Ponieważ dozwolone skutki nie zmieniają żadnej krawędzi, acykliczność może być obliczona raz z danych początkowych i używana jako stała specjalizacji. Nie jest stałym true: osobne próby niepoprawnych typów oraz cyklu muszą ją podważyć. Typy i zależności pochodzą z modelu/instancji, bez wywoływania produkcyjnego predykatu E2 do obliczania wyniku translatora. Każde późniejsze dopuszczenie zmiany topologii wymaga przeglądu tego założenia.

T04 wymaga dojrzałości wszystkich zależności do baselined oraz właściwego stanu produktu i roli U. Evidence=true reprezentuje poprawny demonstracyjny rekord zawierający simulation=true oraz niepuste decision/reference/quote; false oznacza brak pola. T02 wymaga decision i quote, T04 reference i quote. To tylko reprezentanci wejść; nie uwierzytelniają cytatu. Osobne odmowy sprawdzą niepoprawny typ bool, brak pól wymaganych dla danego przejścia i nieznane pola. Nie zmieniać kontraktu E2 dla pól nadmiarowych.

## Uprząż i niezależność oczekiwań

Maksymalnie 16 wykonanych kroków. Dwie drogi none→draft→verified→approved→baselined wymagają po cztery kroki, a po dwa odrzucenia każdego produktu dodają łącznie osiem. Limit pozwala więc przejść także najdłuższą bazową drogę tego wycinka. Nie ogranicza licznika do MAX_REJECTIONS — mutant może przekroczyć budżet. CHECK_DEADLOCK FALSE wyłącza traktowanie końca wycinka jako zakleszczenia całego procesu; nie dowodzimy L1/L5 ani sprawiedliwości.

Osobny autor przygotowuje referencyjne reguły w Pythonie i tekst ExpectedAction w TLA+, niezależnie od generatora i execute_step. Oczekiwania mają własne dane bazowe i jawne odrębne wartości kontrolowanych wariantów, nie są wyliczane z kandydata YAML. Tablicowe powielanie wszystkich możliwych par katalogów nie jest wymagane. TLA ExpectedAction służy wyłącznie do oceny kroku, nigdy do ograniczania Next.

Kontrole: dostępność wszystkich 120 komend (2 produkty × 5 operacji × 3 aktorów × 2 checks × 2 evidence), cały następnik katalogu, rama globalna w Pythonie, zgodność rzeczywistych zbiorów stanów dump TLC i Pythona. Dodatkowe lokalne monitory: liczba odrzuceń dla każdego produktu zgodna z licznikiem i budżetem; approved/baselined tylko po odpowiedniej weryfikacji i zatwierdzeniu w wersji 1. Kontrole kroków i historii obowiązują także po kroku 16; dostępność przed tą granicą. Podstawą S2 dla baselined jest wcześniejszy approved przy requires_approval=true, nie sama nazwa stanu.

## Świadek i czułość

Wykonany świadek ośmiu kroków: T00(r1), T00(p1), T01(p1), T02(p1), T01(r1), T02(r1), T04(p1), T04(r1). Pokazuje legalne przygotowanie wymagania przed dojrzałością planu oraz dojście obu do baselined. Osobno sprawdzić odmowę T01(r1) po pierwszych dwóch krokach i odmowę T04(r1) przed T04(p1). Odmowy są próbami, nie wykonanymi akcjami procesu.

Kontrole odczytu danych: przemianowanie T00–T04, limit=1, zmiana inicjalizacji wersji w kopii danych (z odrębnym oczekiwaniem). Mutanty: brak ustawienia version=1 przez T00; T00 aktora U; pominięcie kontroli typów zależności albo acykliczności; usunięcie wymogu approved w guard T04; pominięcie dojrzałości zależności w T04; T04 aktora A; usunięcie evidence T04. Każdy musi naruszyć nazwaną wyrocznię i mieć osobny wykonany świadek błędnego skutku. Mutanty T00 typów/cyklu zaczynają od jawnie oznaczonych błędnych instancji testowych, nie osiągalnych stanów bazowego procesu. Regresja zachowuje mutanty i monitory T01–T03 z E3.2.

## DoD i decyzje agenta

Gotowość dostawy: mapowanie przejrzane przed kodem, niezależna wyrocznia, rzeczywiste RED/GREEN, wykonane bazowe grafy/kontrole/mutanty/świadki, właściwa regresja, odtwarzalne polecenie, przypięte i niezmienione podczas przebiegu źródła, surowe dowody i niezależny przegląd bez otwartych ustaleń blokujących. Wynik techniczny nie odbiera E3.

E3-DA11 (A, 2026-10-27): pełny katalog przy dwóch aktywnych produktach zachowuje sens globalnej acykliczności i ramy, jednocześnie pozwalając badać przeploty bez udawania pełnego procesu.
E3-DA12 (A, 2026-10-27): bezpośrednia niezależna relacja ExpectedAction zamiast ogromnej tablicy par katalogów; oczekiwanie nie wyznacza dozwolonych następników.

Właściciel A: wykonanie E3.3 i punkt wznowienia. R: przegląd mapowania i osobne odtworzenie wyniku. U: przyszły odbiór E3 lub rozstrzygnięcie nowej luki zaakceptowanych reguł. Obecnie nie ma nowej decyzji do podpisu.
