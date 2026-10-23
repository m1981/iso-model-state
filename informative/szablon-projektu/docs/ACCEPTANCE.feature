# language: en
# Scenariusze akceptacyjne <projekt>. Dokumentacja wykonywana przez zwykłe testy
# nazwane ID scenariusza (test_at_<prj>_nnn_…), bez generatora kroków.
#
# Statusy:
#   @proposal    propozycja agenta, bez decyzji użytkownika
#   @confirmed   potwierdzona potrzeba; musi mieć test (REQ-<PRJ>-205)
#   @dormant     potwierdzona, ale nie obowiązuje w tej wersji (podaj DEC)
#   @superseded  zastąpiona; podaj DEC i nowy AT; test usunięty albo przemianowany
#
# Każdy scenariusz ma tagi: ID, status, UC, REQ, VER, a przy zmianie także DEC.

@<prj>
Feature: <jedno zdanie o produkcie>
  <Kto> chce <czego>, żeby <po co>.

  Background:
    Given <wspólne przygotowanie, np. dane testowe w katalogu tymczasowym>

  @AT_<PRJ>_001 @proposal @UC_<PRJ>_01 @REQ_<PRJ>_001 @VER_<PRJ>_001
  Scenario: <obserwowalny wynik z punktu widzenia użytkownika>
    Given <stan początkowy>
    When <działanie użytkownika>
    Then <obserwowalny wynik>
