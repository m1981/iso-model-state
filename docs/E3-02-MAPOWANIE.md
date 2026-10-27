# E3.2 — kontrakt wielokrokowego wycinka T01–T03

2026-10-27. Polecenie U: „wykonaj dalej w rezimie”. Kontynuacja E3 po 790b822, zgodnie z PLAN i DEC-PRO-013, bez zmiany modelu v0.7, kolejności etapów ani odbioru E3. Rola A: inżynier weryfikacji formalnej i automatyzacji testów. Metoda: przegląd mapowania → niezależne oczekiwania → RED/GREEN → TLC → niezależne odtworzenie.

## Korzyść i granice

Operator potrzebuje wiedzieć, czy po poprawce nadal obowiązują bramki zatwierdzenia i budżet odrzuceń. E3.1 badało pojedyncze T03. E3.2 bada wszystkie wybory T01/T02/T03 w ograniczonym wielokrokowym wycinku, także zakończenie przez T02 po dwóch odrzuceniach. Nie jest pełnym dowodem S1/S3/S4/S15/L4: brak T00, T04–T14, pytań, wydań, zmian wersji i założeń sprawiedliwości. Zakończenie w approved nie oznacza done całego projektu.

Każda instancja zaczyna się od jawnej syntetycznej próbki draft, version=1 lub 2, rejections=0. Nie nazywamy tego osiągalnością od Init procesu. Zmieniany jest jeden pełny rekord item (jak E3.1). Pozostałe rekordy zależności są stałe. W Pythonie punkt odniesienia to initial_state z podmienionymi rekordami próbki/zależności; wydanie 1 in_preparation, brak pytań i next_release_required=false. Po każdym kroku porównujemy również całą globalną ramę. Przy T01–T03 żaden obserwator nie zmienia tego kontekstu.

## Relacja i wejścia

Wybrane ID służą tylko odnalezieniu trzech definicji. From/to/actor/guard/effects pochodzą z YAML. Rozszerzenie parsera TLA+ obejmuje dokładnie potrzebne konstrukcje: checks_ok(e), type(e).requires_approval, forall d in deps(e), d.state, zbiory stanów i przynależność. Dane zależności i requires_approval są jawne; nie zastępujemy całego guard stałym true. Pusty zbiór zależności spełnia forall. Inne konstrukcje są odrzucane także pod fałszywym guard.

T02 deklaruje evidence „DEC z cytatem użytkownika”. Akcja dostaje bool evidence_ok, odpowiadający istnieniu poprawnego demonstracyjnego dowodu (simulation=true, niepuste decision i quote, brak nieznanych pól). Nie analizuje prawdziwości ani autorstwa cytatu. Porównanie Pythonowe używa konkretnych rekordów dowodu, w tym odmowy braku dowodu. Zmiana nieznanego opisu evidence powoduje odmowę generatora; usunięcie evidence w kopii mutanta usuwa tę bramkę. evidence_ok=false oznacza wyłącznie brak pola evidence, nie dowolny wadliwy rekord: ten interpreter odrzuca także dla T01/T03. Niepoprawne rekordy pozostają osobnymi testami odmowy adaptera. Brak evidence w T01/T03 nie nakłada obowiązku dostarczenia dowodu; do porównania wolno przesłać także poprawny nadmiarowy dowód demonstracyjny.

Aktor, checks_ok oraz evidence_ok są wejściami każdego kroku, nie trwałymi zmiennymi produktu. Graf rozpatruje A/R/U i oba bool dla każdego wejścia przy każdym z trzech przejść. Nie wykonuje akcji środowiskowej zmieniającej zależności, suspect czy typ. Warianty kontekstu są osobnymi badaniami: REQ z PLAN approved/baselined/draft, REQ suspect, PLAN bez zależności, DES bez wymogu zatwierdzenia oraz CODE z dwiema dobrymi zależnościami lub jedną niedojrzałą. Próba mieszana zabezpiecza przed pominięciem jednej zależności.

## Uprząż, wyrocznie i niepustość

Głębokość badania: 8 wykonanych akcji. Brak stutter jako zastępczej akcji. Stan pomocniczy: depth, liczba wykonanych odrzuceń, informacja o wcześniejszej weryfikacji i wynik porównania ostatniego następnika z niezależną wyrocznią. Nie ograniczamy dziedziny rejections do MAX_REJECTIONS; mutant może ujawnić 3. Głębokość ogranicza badanie również dla mutanta bez limitu. Jawna dziedzina wyroczni obejmuje draft/verified/approved i liczniki 0..8, więc także wszystkie osiągalne liczniki 3+ badanych mutantów. Nie jest constraintem Next. Brak następcy to koniec wycinka/odmowa albo granica badania, nie dowód zakleszczenia procesu; CHECK_DEADLOCK FALSE jest jawne.

Oczekiwania przygotowuje osobny autor na podstawie reguł, bez używania translatora ani execute_step do ich wyliczenia. Mała referencyjna funkcja jest wyrocznią testową, nie źródłem reguł produkcyjnych. Generator otrzymuje jej jawne tablice (dostępność i cały oczekiwany rekord) dla skończonego zbioru stanów testowych i wejść. Next nigdy nie jest ograniczony wyrocznią; błędny następnik ma być osiągalny i naruszyć kontrolę.

Kontrole:

1. Dostępność każdej akcji dla wszystkich wejść, w każdym odwiedzonym stanie przed granicą, jest równa oczekiwaniu. Wyrocznia odmawia stanu poza swoją jawną dziedziną zamiast zgadywać.
2. Każdy wykonany następnik zachowuje cały oczekiwany rekord i ramę. Oczekiwanie nie jest obliczane przez translator.
3. Liczba odrzuceń w historii nie przekracza niezależnie podanego budżetu; licznik produktu odpowiada historii; approved jest poprzedzone verified w tej samej, niezmienianej wersji. Są to lokalne kontrole historii, nie pełne S/L.
4. Odtworzenie Pythonowe z tych samych wejść ma zgodny zbiór stanów/akcji z oczekiwaniami. Wynik i dump TLC muszą potwierdzić faktyczne kroki. Osobny świadek kończy się approved po sekwencji T01,T03,T01,T03,T01,T02; licznik 2 i wersja zachowane.

## Czułość i odmowy

Kontrole odczytu danych: zmiana ID trzech przejść, limit=1 i zmiana requires_approval typu (w kopiach, z odrębnymi oczekiwaniami). Regresja E3.1 zachowuje kontrole from/to. Mutanty mają bazowe oczekiwania: pominięcie zależności/checks/suspect w T01, T02 z draft, T02 aktora A, brak evidence T02, brak limitu T03, reset licznika przez T01. Dla każdego wymagane nazwane naruszenie wyroczni w TLC i osobno wykonany ciąg ujawniający błędny skutek; błąd narzędzia, odmowa translatora i timeout nie są wykryciem mutanta.

Nieobsługiwana semantyka, brak wymaganych danych kontekstu i niepoprawne typy wejść mają kończyć się czytelną odmową. Zachować istniejące zachowanie E3.1. Nie zmieniać wykonawcy E2, właściwości ani reguł YAML w celu dopasowania do translatora.

## DoD przyrostu i zapisy

Przyrost ma: zaakceptowane przez R mapowanie; niezależną wyrocznię; zachowane rzeczywiste RED/GREEN; wykonane kontrole bazowe, warianty i mutanty; odtwarzalną komendę z pinem TLC, limitami, kodami wyniku i hashem wejść; surowe dowody w Git; właściwą regresję; niezależne odtworzenie oraz zamknięte blokujące ustalenia. Sam sukces techniczny nie jest odbiorem E3.

E3-DA07 (A, 2026-10-27): ograniczenie do ośmiu kroków i stałych zależności pozwala zbadać trzecią próbę odrzucenia oraz zatwierdzenie po dwóch poprawkach bez pozorowania pełnej eksploracji procesu.
E3-DA08 (A, 2026-10-27): niezależny autor wyroczni i osobny końcowy recenzent, ponieważ zgodność dwóch implementacji tego samego założenia nie wystarcza jako dowód.

Właściciel A: wykonanie i raport E3.2. R: mapowanie i osobny przegląd wykonania. U: przyszły odbiór całego E3 lub rozstrzygnięcie nowej luki w przyjętych regułach; obecnie nie ma nowej decyzji do podpisu.
