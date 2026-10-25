# WIT2/WIT4 — odrzucenia i pytania

Przyrost E2 z 2026-10-24 na przyjętym modelu v0.4. Nie zmienia modelu ani nie stanowi odbioru E2. Korzysta z tego samego wykonawcy co WIT1.

## Uruchomienie i raporty

```sh
uv run --locked --offline python scripts/run_scenario.py --scenario WIT2 --output artifacts/wit2
uv run --locked --offline python scripts/run_scenario.py --scenario WIT4 --output artifacts/wit4
uv run --locked --offline pytest -q
```

Polecenia wymagają środowiska z zależnościami z `uv.lock`. W każdym katalogu powstają `report.md` i pełny `trace.json`, z SHA-256 wejść i kodu. Katalog `artifacts/` nie trafia do Git. Zapisane raporty do przeglądu: [WIT2](wit2-report.md), [WIT4](wit4-report.md). Dotychczasowe polecenie `scripts/run_wit1.py` nadal działa; jest wejściem do wspólnego runnera.

## WIT2: limit odrzuceń

WIT1 rozszerzono o dwa cykle T03(U) → T01(A) na r1. Po nich trzecia propozycja ma `rejections = 2`, `version = 1`. U zatwierdza ją przez T02, tworzy linię bazową T04, a pozostały przebieg dochodzi do odbioru. Łącznie **33 kroki**.

Osobna próba z tego samego osiągalnego prefiksu wykazuje, że trzecie T03 zostaje odrzucone bez zmiany stanu. Zmiana MAX_REJECTIONS na 1 w teście przesuwa blokadę na drugie odrzucenie — limit nie jest zaszyty w wykonawcy. Mutant z guard=true dopuszcza licznik 3 i narusza wyrocznię. Sprawdzono też rolę U przy odrzuceniu.

WIT2 wybiera zatwierdzenie po osiągnięciu limitu. Alternatywne wycofanie/odłożenie produktu oraz skutki zmian na zależnościach nie są implementowane w tym przyroście; wymagają helperów i dalszych scenariuszy. Nie oznacza to usunięcia tych możliwości z modelu.

## WIT4: niejednoznaczność i kolejka

1. Zgłoszenie blokującego q1 i zadanie go użytkownikowi.
2. Podczas oczekiwania zgłoszenie blokującego q2 oraz nieblokującego q3.
3. Niejednoznaczna odpowiedź na q1: P03 wraca do open bez DEC i bez zmiany age.
4. q1 zostaje zadane ponownie przed q2; jednoznaczna odpowiedź P02 tworzy demonstracyjny zapis decyzji.
5. Zadanie i rozstrzygnięcie q2.
6. Odłożenie q3, wznowienie przez A, zadanie i rozstrzygnięcie.

Łącznie **13 kroków**, trzy pytania resolved i trzy DEC utworzone wyłącznie przez P02. Wydanie pozostaje in_preparation; ten scenariusz sprawdza kolejkę, nie wytwarzanie produktów. Testy obejmują także wznowienie przez U oraz odłożenie nieblokującego pytania już zadanego.

Pierwszeństwo blokujących wynika z `blocking_first`. Ponowne zadanie starszego pytania przed nowszymi dotyczy tej samej klasy priorytetu. Osobny test potwierdza, że nowe pytanie blokujące ma pierwszeństwo przed starszym nieblokującym także po P03. Nie zmieniamy P01 na bezwzględne FIFO.

## Format zdarzeń i decyzje implementacyjne agenta

Zgłoszenie:

```json
{"transition": "P00", "actor": "A", "question": "q1", "attributes": {"blocking": true}}
```

Rozstrzygnięcie:

```json
{"transition": "P02", "actor": "U", "question": "q1", "inputs": {"unambiguous_answer": true}, "evidence": {"simulation": true, "decision": "SIM-DEC-q1", "quote": "Zgoda testowa"}}
```

- `state` jest inicjalizowany z question_variables; blocking musi być jawnym bool. `age` otrzymuje kolejny numer zgłoszenia, począwszy od 1. To reprezentacja istniejącej kolejności FIFO, nie czas zegarowy ani nowa polityka. P03/P04/P05 pozostawiają age bez zmiany zgodnie z zasadą frame. Operator scenariusza nie nadaje age ręcznie.
- ID pytania jest metadanymi instancji. Próba ponownego utworzenia tego samego ID lub nadpisania jego atrybutów jest odrzucana. Zamknięte pytania pozostają w historii; przekroczenie max_questions jest granicą badania, bez częściowego utworzenia rekordu.
- `count`, `oldest` i `blocking_first` interpretują notację P01. `newest` służy do wykonania mutanta LIFO; nie jest używane przez przyjęty model. Nie ma dyspozytora zachowania według P00/P01 itd.; test zmienia wszystkie ID pytań i nadal wykonuje WIT4.
- `unambiguous_answer` jest jawnym wejściem kroku P02. Dane zdarzenia nakładają się na bazowe inputs tylko dla tego zdarzenia. Nie są kopiowane do następnego kroku. Brak wartości lub tekst zamiast bool to błąd wejścia; false uniemożliwia P02. Wykonawca nie rozpoznaje sensu naturalnej wypowiedzi. P03 jest jawnym zdarzeniem wybranym przez autora scenariusza.
- Skutek `record DEC with user quote` tworzy zapis w `step.records`; odtworzenie zbiera je w `result.records` z numerami kroków. To dziennik dowodów wykonania, nie nowa zmienna procesu ani dodatkowy automat (INT-004). Rekord zawiera ID demonstracyjne, ID pytania, cytat i simulation=true. Nie trafia do docs/STAN.md ani do rzeczywistych decyzji projektu.
- Stan i dowody powstają atomowo na kopiach. Test wymusza błąd po przygotowaniu DEC i potwierdza, że ani DEC, ani resolved nie zostają zatwierdzone. Wyniki nie współdzielą zmiennych struktur z wejściami ani innymi raportami.
- Model v0.5 (DEC-PRO-008) dodaje kind/about i powiązanie zgody. Dotychczasowe pytania WIT4 mają kind=general; P02 zapisuje resolution=answered. Pytania change i wynik approved/rejected sprawdza [WIT5](../wit5/README.md).

## Weryfikacja i zakres dowodu

Pierwszy przebieg nowych kryteriów: 27 failed, 7 passed. WIT2 korzystał już z obsługiwanych wyrażeń T03; czerwone przypadki WIT4 wskazywały brak zdarzeń i wykonania pytań. Dodano następnie testy atomowości, raportów i dodatkowych przypadków kolejki. Aktualny wynik pełnego zestawu jest w docs/STAN.md.

Dziewięć nowych mutantów: dwa WIT2 i siedem WIT4. Obejmują limit i rolę przy odrzucaniu, dwa jednoczesne asked, LIFO, rozstrzygnięcie niejednoznacznej odpowiedzi, odłożenie blokującego pytania, utratę age, nieuprawnione utworzenie DEC przez P03 oraz brak DEC po P02. Łącznie z WIT1 jest 16 wybranych mutantów wykonania; nie jest to pełne pokrycie mutacyjne E2.

Hypothesis sprawdza kolejność obsługi przy kombinacjach blocking dla maksymalnie trzech pytań. To sprawdzenia skończonych przebiegów i warunków S9/L4; nie dowód żywotności L2 pod F1/F2. WIT5 jest wykonany w kolejnym przyroście. Pełna maszyna stanów, WIT3, pozostałe mutanty i TLC pozostają w planie. Ograniczenie pustego zakresu wydania z WIT1 pozostaje jawne.
