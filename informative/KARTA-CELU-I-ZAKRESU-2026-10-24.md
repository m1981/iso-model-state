# Karta celu i zakresu projektu iso-model-state

Data: 2026-10-24. Status: **propozycja do przeglądu**, zapisana na prośbę użytkownika. Karta opisuje cel użytkowy; obowiązujące etapy i DoD pozostają w [PLAN.md](../PLAN.md). Przyjęcie zmian celu, zakresu lub planu wymaga osobnej decyzji.

## Cel użytkowy

**Opracować i sprawdzić na jednym rzeczywistym projekcie lekki sposób współpracy operatora z agentem, który zachowuje kontekst, pilnuje zatwierdzeń i pokazuje skutki zmian.**

Operator ma zachować kontrolę nad zamiarem i ważnymi decyzjami, a agent samodzielnie wykonywać pracę w uzgodnionych granicach. Dokumenty i narzędzia mają ograniczać ręczne pilnowanie spójności projektu. Norma ISO/IEC 29110 jest podstawą doboru reguł; model i testy służą sprawdzeniu ich działania.

## Problemy i oczekiwane korzyści

| Problem w pracy | Oczekiwany rezultat dla operatora |
|---|---|
| Po przerwie albo zmianie agenta trzeba odtwarzać ustalenia | Wiadomo, co obowiązuje, co jest otwarte i jaki jest następny krok |
| Propozycja, decyzja i wykonanie mieszają się ze sobą | Można odróżnić pomysł od zatwierdzonego wymagania i wskazać źródło zgody |
| Zmiana wymagania pozostawia nieaktualne dokumenty, testy lub kod | Widoczna jest lista zależnych elementów wymagających przeglądu |
| Po kolejnych zmianach nie wiadomo, co zostało odebrane | Odbiór wskazuje konkretną, niezmienną migawkę wydania |
| Każdy projekt wymaga ponownego ustalania sposobu pracy | Sprawdzony zestaw zasad, dokumentów i poleceń można zastosować ponownie |

## Zakres pierwszego zastosowania

Jeden operator, agent wykonujący, niezależny przegląd i jedno repozytorium. Operator ustala zamiar, granice i podejmuje wymagane decyzje; agent przygotowuje propozycje, wykonuje pracę, weryfikuje ją i utrzymuje zapisy.

Przećwiczymy trzy sytuacje:

1. Zwykła realizacja: od ustalenia zakresu i wymagań do przeglądu oraz odbioru.
2. Odrzucenie propozycji lub niejednoznaczna odpowiedź: poprawa, kolejka pytań i rozstrzygnięcie bez domyślania się zgody.
3. Zmiana zaakceptowanego elementu: ocena wpływu na zależności, wymagane zatwierdzenia i następne wydanie z zachowaniem wcześniejszego odbioru.

`vcs-lite` jest wskazanym w obecnym planie projektem do odtworzenia historii. Dostęp do tej historii pozostaje do uzgodnienia. Proponowany pilotaż bieżącej pracy obejmie jeden uzgodniony przypadek; jego wybór i granice ustalimy przed rozpoczęciem.

Poza pierwszym zastosowaniem są: zarządzanie wieloma zespołami, rozbudowany interfejs graficzny, certyfikacja lub pełny audyt zgodności z normą oraz przewidywanie czasu, kosztu i produktywności. Obecna symulacja bada dopuszczalne przebiegi procesu.

## Co ma powstać

- **Zasady współpracy:** odpowiedzialności operatora i agenta, bramki decyzji oraz sposób obsługi zmian.
- **Minimalny zestaw zapisów:** cel i zakres, wymagania, decyzje, powiązania, punkt wznowienia i odbiór; zakres dokumentacji dopasowany do przypadku użycia.
- **Program sprawdzający:** raport naruszeń z konkretnymi elementami i dowodami, możliwy do użycia na wybranym repozytorium.
- **Sprawdzony przykład:** odtwarzalny przebieg oraz instrukcja zastosowania w kolejnym projekcie.
- **Ocena użyteczności:** wykryte problemy, fałszywe alarmy i nakład pracy na utrzymanie procesu.

## Proponowane kryteria sukcesu użytkowego

| Kryterium | Jak je sprawdzimy |
|---|---|
| Można wznowić pracę bez ponownego opowiadania historii | Nowy przebieg agenta poprawnie wskazuje obowiązujący zakres, ostatnie decyzje, otwarte sprawy i następny krok na podstawie repozytorium |
| Zgody są przypisane do właściwych działań | W przygotowanych przypadkach kontrolnych wykrywane są próby pominięcia wymaganej zgody; poprawne przebiegi przechodzą |
| Zmiana ma widoczny wpływ | Dla wybranej zmiany raport wskazuje uzgodniony zbiór zależnych elementów; przegląd potwierdza kompletność tej listy |
| Historia odbiorów jest wiarygodna | Zmiana po odbiorze prowadzi do kolejnego wydania, a wcześniejszy zakres, migawka i protokół pozostają identyczne |
| Narzędzie pomaga podjąć działanie | Operator potrafi na podstawie raportu ustalić, co wymaga poprawy, przeglądu lub decyzji |
| Koszt procesu jest akceptowalny | W pilotażu mierzymy czas przygotowania decyzji i utrzymania zapisów oraz liczbę fałszywych alarmów; porównujemy z dotychczasową pracą. Dopuszczalny narzut ustalamy przed pilotażem |

Powyższe kryteria uzupełniają ocenę korzyści. Obowiązujący DoD techniczny, w tym dowody w podanych granicach, pozostaje w PLAN.md.

## Jak kierować dalszymi pracami

Każdy kolejny przyrost powinien wskazywać: **problem operatora → regułę procesu → sprawdzalny przypadek → dowód działania → koszt obsługi**. Pozwala to oceniać wartość pracy technicznej i utrzymywać zakres.

| Obecny etap | Jego znaczenie dla celu użytkowego |
|---|---|
| E2 — wykonanie i testy modelu | Sprawdza, czy reguły poprawnie obsługują sytuacje, z którymi spotka się operator |
| E3 — dowody w granicach instancji | Ogranicza ryzyko obejść i zakleszczeń niewidocznych w pojedynczych przykładach |
| E4 — odtworzenie historii projektu | Sprawdza, czy model rozpoznaje znane problemy i poprawne przebiegi rzeczywistej pracy |
| E5 — zastosowanie w szablonie | Dostarcza sposób użycia; proponowany ograniczony pilotaż pozwoli ocenić użyteczność i nakład pracy |

Mamy przyjęty model v0.4 oraz wykonywalne WIT1/WIT2/WIT4 na sztucznych danych. E2 trwa. Narzędzie do automatycznej kontroli rzeczywistego repozytorium i potwierdzenie korzyści użytkowych pozostają do dostarczenia.

Najbliższym krokiem organizacyjnym jest przegląd tej karty. Dotychczasowy następny krok techniczny to doprecyzowanie powiązania pytania ze zmienianym elementem przed WIT5. WIT5 ma wykazać kontrolę zgody na zmianę i niezmienność wcześniejszego odbioru. Ewentualną zmianę zakresu lub kolejności E2–E5 należy wyraźnie zatwierdzić; zapisanie karty nie zmienia planu.
