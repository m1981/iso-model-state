# Stan prac

Nadpisywany na końcu każdej sesji. Zaktualizowano: 2026-10-24, model v0.3.

## Gdzie jesteśmy

- **Etap:** E1, model v0.3 czeka na przegląd użytkownika (bramka). DEC-PRO-003 i DEC-PRO-004 zatwierdzają opisane zmiany, nie cały etap E1.
- **Ostatnio zrobione:**
  - DEC-PRO-003: numerowane wydania, migawka i protokół w W04, niezmienność odebranego rekordu, W06 otwierające następne wydanie, granica dwóch wydań;
  - DEC-PRO-004: T10 dołączone do unieważniania gotowości przed odbiorem i wyzwalania W06 po odbiorze;
  - S7 zastąpione przez S7a i S7b, dodane S10 i mutanty; `done`, L1, L5 i S8 uwzględniają tożsamość wydania; dodane WIT5 i przypadek T10;
  - INT-017 z odniesieniami do Tabeli 12, SI.06.05–SI.06.06, PM.04.01–PM.04.02 oraz informacyjnego Aneksu A (A.1–A.2, A.9.4);
  - odtwarzalny skrypt `scripts/check_model.py` do sprawdzenia spójności danych i odwołań E1; nie jest implementacją symulatora E2.
- **Następny krok:** bramka E1 dla v0.3. Po akceptacji E2: najpierw testy oblewające z właściwego powodu, potem wczytanie modelu, graf i sprawdzenia bezpieczeństwa.

## Decyzja czekająca na użytkownika

D1. Przyjąć model v0.3 jako podstawę E2: DES i CODE bez osobnego zatwierdzania użytkownika, ale do podważenia (INT-013); `MAX_REJECTIONS = 2` (INT-011); T04 zawsze wykonuje U; odebrane wydanie jest niezmienne, a T05–T10 w zakresie lub pojawienie się `suspect` w zakresie po odbiorze wymusza W06 (INT-017). Dlaczego: model i właściwości uwzględniają rozstrzygniętą politykę kolejnych wydań. Co, jeśli nie: pozostajemy w E1 i korygujemy wskazane uwagi. Zmienia: status modelu i właściwości z oczekujących na zatwierdzone jako podstawa E2; nie oznacza dowodu G/S/L ani odbioru całego projektu. Najszybszy przegląd: WIT1–WIT5, S7a, S7b, S10, następnie T00–T13 i W01–W06.

## Decyzje

| ID | Decyzja | Źródło | Zmienia | Przejrzane |
|---|---|---|---|---|
| DEC-PRO-001 | DoD 1–10 i stos narzędzi (YAML, pytest z Hypothesis, TLA+ z TLC, odtworzenie historii vcs-lite). | Użytkownik 2026-10-23: „d1 tak” | — | — |
| DEC-PRO-002 | Kody, identyfikatory, atrybuty i kod źródłowy po angielsku w terminologii normy; proza, opisy i cytaty po polsku. | Użytkownik 2026-10-23: „d1 tak wykonaj rzetelenie i push” | `model/process.yaml` (v0.1 → v0.2), `docs/WSPOLPRACA.md`, szablon projektu. | `docs/WLASCIWOSCI.md`, `docs/INTERPRETACJE.md`, `PLAN.md`, `README.md`. |
| DEC-PRO-003 | Wariant A: odebrane wydanie jest niezmienne; odbiór dotyczy stanu z chwili podpisu, jak tag v1.0. Zmiany po odbiorze należą do następnego wydania. W06 tworzy nowy rekord, nie cofa starego. Odrzucone B: zakaz zmian po odbiorze blokuje projekt; C: cofanie accepted do in_preparation fałszuje protokół odbioru. | Użytkownik 2026-10-24: „d1 a” (cytat wskazany przez użytkownika do zapisu). | `model/process.yaml` (v0.2 → v0.3): `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7` → `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `release_variables`, `release_control_variables`, `release_semantics`, `W04`, `W06`, `invalidate_release`, `detect_post_acceptance_change`, `test_instance.bounds`; `docs/WLASCIWOSCI.md`: `S7`, `S7a`, `S7b`, `S10`, `done`, `G1`, `G4`, `S8`, `L1`, `L5`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-012`, `INT-017`; `PLAN.md`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo T00–T13, P00–P05, W01–W06, G0–G6, S1–S10, F1–F3, L1–L5, WIT1–WIT5, `README.md`, `PROMPT-STARTOWY.md`, `docs/WSPOLPRACA.md`, lista kontrolna w `informative/szablon-projektu/docs/SPEC.md` i materiały informacyjne. |
| DEC-PRO-004 | Wznowienie odłożonego elementu przez T10 także zmienia kompletność zakresu. T10 wywołuje invalidate_release: przy ready/reviewed wraca do in_preparation, przy accepted wymusza W06 bez zmiany odebranego rekordu. Rozszerza listę wyzwalaczy z DEC-PRO-003 o T10. | Użytkownik 2026-10-24: „Tak, uwzględnij T10” | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`. | `model/process.yaml`: `T10`, `W06`; `docs/WLASCIWOSCI.md`: `scope_change`, `S7a`, `WIT5`; `docs/INTERPRETACJE.md`: `INT-017`; `docs/STAN.md`; `scripts/check_model.py`; dodatkowo `invalidate_release`, `S7b`, `S10`, `L1`, `L5`, T09 i bramki U. |

## Weryfikacja i lista kontrolna zmiany

- Zmienione definicje i ich zależne zaktualizowano w jednej zmianie. S7 jest wycofaną definicją zastąpioną przez S7a i S7b; wzmianki historyczne pozostają jawnie oznaczone.
- Lista kontrolna ze specyfikacji szablonu zastosowana do istniejących artefaktów tego repozytorium: model, właściwości, scenariusze WIT, interpretacje, plan i ryzyka. Osobnych REQ/UC/DES/AT/VER, kodu produktu ani instrukcji UI w tym projekcie jeszcze nie ma; odpowiedniki w `informative/szablon-projektu/` są niewiążącą migawką do E5, nie definicjami obecnego modelu.
- Polecenie: `uv run --offline --with pyyaml python scripts/check_model.py` (PyYAML 6.0.3). Wynik: **330 sprawdzeń spójności OK**, 26 przejść, 7 elementów, granica 2 wydań; `git diff --check` bez błędów.
- Trzy próby na tymczasowych błędnych plikach potwierdziły diagnostykę skryptu: nieznany aktor W06, brak `invalidate_release` w T10 i powtórzony klucz YAML są odrzucane z właściwego powodu. To sprawdzenie narzędzia E1, nie raport mutantów właściwości z DoD 6.
- Zakres skryptu: unikalność kluczy YAML i ID, stany, aktorzy, zbiory stanów w warunkach, typy i zależności instancji, inicjalizacja i cel W06, definicje właściwości i interpretacji, obecność mutantów S7a/S7b/S10 oraz „Zmienia” ⊆ „Przejrzane” dla nowych decyzji.
- WIT5 i wariant T10 przejrzane ręcznie względem warunków i skutków. Generowanie świadków, wykonanie mutantów, dowody G/S/L i niezależny odbiór nie są jeszcze wykonane; pozostają w E2–E5.

## Repozytorium

- Użytkownik scalił poprzednią gałąź `e1-model` do `main` (merge PR #1, `eceaf0e`). Drzewa plików po scaleniu i poprzedniego `e1-model` są identyczne.
- Model v0.3 powstaje na `e1-model`; commit i push są zlecone przez użytkownika. Scalenie tej zmiany do `main` wymaga osobnej zgody.

## Sprawy otwarte

| Sprawa | Właściciel | Następny krok |
|---|---|---|
| Przegląd modelu v0.3 w E1 (D1 wyżej) | użytkownik | akceptacja albo uwagi; DEC-PRO-003/004 nie zastępują tej bramki |
| Weryfikacja G/S/L i mutantów, w tym S7a/S7b/S10 oraz granicy wydań | agent | po bramce E1 wykonać E2, a następnie E3; skrypt spójności nie jest dowodem |
| Historyczny opis pojedynczego wydania w informative/ | agent | przy E5 uwzględnić INT-017 w nowym materiale; nie przepisywać migawek sesji 2026-10-23 |
| REQ-210 (wycofane pojęcia) i REQ-211 (rejestr decyzji agenta) dla szablonu | użytkownik | decyzja; opis w `informative/SESJA-2026-10-23.md` §5 |
| Instalacja Javy i TLA+ (E3) | użytkownik | zgoda przed E3 |
| Dostęp do historii vcs-lite (E4) | użytkownik | zgoda przed E4 |
| Porządki w vcs-lite według `informative/PRZEGLAD-VCS-LITE.md` | użytkownik | decyzja, czy i kiedy |

## Decyzje agenta w tej sesji (do podważenia)

- Odebrane rekordy trzymamy w `releases`, a wskaźnik `current_release` i znacznik `next_release_required` poza nimi; dzięki temu samo odnotowanie zmiany nie narusza S10.
- Migawka kopiuje wartości pól elementów i zależności, a protokół zawiera numer wydania; nie przechowujemy zmiennych referencji do produktów roboczych.
- W06 jest następnym przejściem po ustawieniu znacznika i kopiuje zakres do nowego rekordu. To techniczne wykonanie uzgodnionej polityki; nie zastępuje zgód U na elementy ani odbioru.
- `max_releases` ogranicza eksplorację, nie dopuszczalność zmian w rzeczywistym procesie. Wyjście poza granicę musi być jawnie raportowane w E3.
- Przejrzane wcześniejsze decyzje agenta pozostają: warunek T11 chroniący przed wycofaną zależnością; blokujące pytanie w T12; dopuszczenie nieaktywnych elementów w W01; terminologia angielska; niewiążący charakter informative/.
