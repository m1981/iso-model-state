# <projekt> — procedury ręczne

Kroki, których nie da się zautomatyzować (ekran, sprzęt, prawdziwe konto, odczucie użytkownika). Produkty pracy ISO/IEC 29110: Test procedures (WP.19) i Validation record (WP.22).

Zasady:
- Agent przygotowuje środowisko i dane, uruchamia program i mówi dokładnie, co kliknąć i co ma być widać.
- Wynik zapisuje agent, ale **potwierdza użytkownik**: cytat z datą. Brak cytatu = krok niepotwierdzony.
- Pominięcie kroku wymaga decyzji (DEC). Agent nie odhacza kroków na podstawie „pracy w sesji”.
- Krok działający na prawdziwych danych lub zewnętrznych usługach jest na liście eskalacji.

## Kroki

| Krok | Weryfikuje | Przygotowanie | Działanie | Oczekiwany wynik | Wynik i potwierdzenie |
|---|---|---|---|---|---|
| 1 | REQ-<PRJ>-…, VER-… | | | | <data>, użytkownik: „…” |
