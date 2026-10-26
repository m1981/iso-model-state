# Plan krytycznej rozmowy z agentem vcs_lite

Data: 2026-10-26. Materiał niewiążący, przygotowany na prośbę użytkownika o wywiad z agentem sesji `26cc4e83-dd37-43be-b408-24a8bec22906`. Badamy, co rzeczywiście pomagało we współpracy i które doświadczenia mogą sprawdzić lub podważyć założenia iso-model-state. To wywiad z uczestnikiem, nie niezależny audyt jego pracy ani formalne odtworzenie historii E4.

## Pytanie badawcze

Które mechanizmy współpracy operatora z agentem pomagają zachować zamiar, kontrolować zmiany i uzyskać działający produkt przy akceptowalnym nakładzie pracy? Które są zbędne, zawodne albo działają wyłącznie dzięki interwencji użytkownika?

Pozytywna ocena projektu przez użytkownika jest punktem wyjścia do badania, nie dowodem skuteczności procesu. Alternatywne wyjaśnienia to m.in. niewielki zakres, szybki feedback, doświadczenie operatora, istniejący kod i wspólny wzorzec interfejsu.

## Przebieg rozmowy

| Runda | Pytania i ćwiczenia | Oczekiwany wynik |
|---|---|---|
| 1. Rekonstrukcja bez prezentowania naszego rozwiązania | Co widzisz z własnej historii, a co tylko ze streszczenia? Odtwórz 4–6 epizodów: pomocna reguła, pomyłka, korekta zamiaru, zmiana po akceptacji, wznowienie, odbiór. Co faktycznie robiłeś, a co tylko deklarowały dokumenty? | Epizody ze śladami oraz lista używanych mechanizmów i kosztów |
| 2. Krytyczna ocena iso-model-state | Dopiero teraz przedstawimy cel użytkowy, automat produktów/pytań/wydań, zakres E2 i plan E3–E5. Które reguły odpowiadają epizodom? Czego model nie widzi? Gdzie formalizacja doda pracę lub zatrzyma poprawne działanie? | Powiązania doświadczenie → reguła → korzyść lub luka; najmocniejszy zarzut wobec podejścia |
| 3. Próby podważenia wniosków | Na wybranych epizodach: usuń jeden mechanizm; zastosuj nasz model krok po kroku; rozpatrz wariant odmowy/niejednoznacznej zgody; odróżnij poprawne testy od potwierdzonego zamiaru. Jaki minimalny eksperyment odróżni korzyść od samej dyscypliny dokumentacyjnej? | Maksymalnie trzy hipotezy przeniesienia z kryterium sukcesu, kosztem i warunkiem odrzucenia |

Po każdej rundzie prowadzący sprawdza wskazane cytaty, dokumenty lub zdarzenia w udostępnionym zapisie. Dopytuje o luki, sprzeczności i brakujące przykłady, zamiast wysyłać z góry całą ankietę. Nie przedstawia naszej interpretacji jako odpowiedzi uczestnika.

## Instrukcja dla rozmówcy

„Bądź krytycznym świadkiem i recenzentem. Nie chodzi o chwalenie siebie ani naszego projektu. Nie wymuszamy krytyki dla samej krytyki. Każdy wniosek oprzyj na konkretnym epizodzie z tej sesji. Odróżnij widoczny zapis, streszczenie po kompakcji, interpretację i hipotezę. Nie wymyślaj brakujących ID, cytatów, pomiarów ani motywacji użytkownika. Wskaż własne błędy i przykłady, które przeczą Twojej rekomendacji.”

## Ćwiczenia i sposób oceny

1. **Próba usunięcia reguły:** wybierz mechanizm uznany za pomocny; wskaż obserwację potwierdzającą użycie, prawdopodobny skutek jego braku i inne możliwe wyjaśnienie. Skutek hipotetyczny nie jest obserwacją.
2. **Próba rozróżnienia zamiaru:** dla konkretnej korekty użytkownika określ, czy zawiodła zgoda, rozumienie wymagania, realizacja czy weryfikacja. Sprawdź, czy nasz automat w ogóle rozróżnia te przyczyny.
3. **Próba wznowienia:** na znanym epizodzie utraty kontekstu wskaż minimalne zapisy potrzebne do odzyskania zamiaru, zakresu zgody i następnego kroku. To projekt przyszłego eksperymentu; sam wywiad nie udowadnia skutecznego wznowienia przez nowego agenta.
4. **Próba proporcjonalności:** pokaż małą i dużą zmianę z tej sesji. Określ, które zapisy i bramki były potrzebne w obu, a które były kosztem bez potwierdzonej korzyści. Nie szacuj czasu bez danych.

Dla każdego wniosku zapisujemy: epizod/źródło → mechanizm → obserwowalny wynik → interpretacja i alternatywy → koszt → związek z modelem → proponowany test → warunek obalenia. Pewność dotyczy osobno faktu użycia mechanizmu i przypisywanego mu wpływu na wynik.

## Prezentacja naszego projektu w rundzie drugiej

Cel: lekki sposób współpracy jednego operatora, agenta i recenzenta, który zachowuje kontekst, pilnuje zatwierdzeń i pokazuje wpływ zmian. ISO/IEC 29110 inspiruje dobór reguł; nie deklarujemy certyfikacji ani pełnej zgodności.

Model v0.7 w YAML opisuje dojrzałość produktów, pytania i kolejne wydania. Zgoda na zmianę wiąże element, wersję i operację oraz jest zużywana atomowo. Zmiany oznaczają produkty zależne jako suspect. Odebrany rekord jest niezmienny; kolejna zmiana prowadzi do następnego wydania. Odbiór wymaga przeglądu i braku blokad. Zasady komunikacji oddzielają samodzielność agenta od decyzji operatora.

E2 ma wykonawcę w Pythonie, skończone symulacje WIT1–WIT5, niezależne wyrocznie, testy generowane i mutanty. Zielone testy nie dowodzą trafności wymagań, użyteczności ani małego kosztu procesu. E3 ma sprawdzać własności formalne przez TLC, E4 odtworzyć historię rzeczywistego projektu, E5 włączyć rozwiązanie do szablonu. Odbiór E2 nadal czeka na użytkownika.

Pytanie do recenzenta: co w tym podejściu odpowiada rzeczywistym potrzebom z Twojej sesji, co tylko pozornie chroni operatora, a co wymaga doświadczenia z użyciem przed dalszą rozbudową?

## Granice i zakończenie

Rozmowa używa kopii wskazanej sesji, bez zapisywania do oryginalnej historii i bez narzędzi wykonawczych rozmówcy. Odczyt źródeł przez prowadzącego jest ograniczony do tej sesji i właściwych materiałów vcs_lite. Nie modyfikujemy vcs_lite. Nie kopiujemy całej historii do repozytorium; utrwalamy pytania, odpowiedzi i niezbędne odniesienia.

Kończymy po trzech rundach, gdy mamy sprawdzone epizody, krytykę modelu i maksymalnie trzy mierzalne hipotezy. Braki dowodów pozostają jawne. Wywiad nie zmienia zaakceptowanych reguł, nie odbiera E2 i nie zastępuje E3/E4. Ewentualna zmiana modelu lub kolejności etapów wymaga osobnej propozycji do decyzji.
