#!/usr/bin/env python3
"""Odtwarzalny raport E2; kod 1 przy nieudanych sprawdzeniach, 2 przy błędzie.

Trace: G0–G6, S1–S15, E2. Nie uruchamia TLC ani nie odbiera etapu.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
from copy import deepcopy
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from isomodel import load_model
from isomodel.execution import fingerprint, replay, execute_step
from isomodel.evidence import safety_evidence, structural_evidence
from isomodel.exploration import reachability_report, generator_coverage_report


def build_report():
    model=load_model(ROOT/'model/process.yaml')
    reach=reachability_report(model)
    safety=safety_evidence(model,ROOT)
    structure=structural_evidence(model)
    mutant=deepcopy(model)
    definition=next(t for t in mutant['item_transitions'] if t['id']=='T04')
    definition['guard']=definition['guard'].replace('(state = approved or not type(e).requires_approval)','state = approved')
    witness=reach['application_witnesses']['T04:CODE']
    baseline=replay(model,dict(witness,events=witness['events'][:-1]))
    from isomodel.execution import StepRejected
    try:
        execute_step(mutant,baseline['final_state'],witness['events'][-1],witness['inputs'])
        killed=False
    except StepRejected as error:
        killed=error.code=='guard'
    required_applications={f'T04:{kind}' for kind in model['item_types']}
    missing_applications=sorted(required_applications-set(reach['covered_applications']))
    mutant_reach=reachability_report(mutant)
    structure['G2']={'baseline':not reach['missing'] and not missing_applications,
        'required_applications':sorted(required_applications),'missing_applications':missing_applications,
        'mutant_detected':killed and 'T04:CODE' not in mutant_reach['covered_applications'],
        'mutant':'T04 wymaga approved również dla CODE','tested_application':'T04:CODE',
        'scope':'witness_per_transition_and_T04_per_type_not_exhaustive'}
    sources=sorted({*ROOT.glob('src/isomodel/*.py'),*ROOT.glob('scripts/*.py'),*ROOT.glob('tests/**/*.py'),
                    *ROOT.glob('tests/fixtures/**/*.json'),*ROOT.glob('mutants/*'),
                    *ROOT.glob('model/proposals/e2*'),ROOT/'model/process.yaml',ROOT/'uv.lock'})
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.is_file()}
    checks_passed=(not reach['missing'] and all(run['outcome']=='completed' for run in reach['runs'])
        and not safety['missing'] and all(not w['violations'] for w in safety['witnesses'])
        and all(m['gate_detected'] and m['mutant_applied'] and not m['baseline_violations'] for m in safety['mutations'])
        and all(e['baseline'] and e['mutant_detected'] for p,e in structure.items() if p!='G5'))
    return dict(status='checks_passed_awaiting_acceptance' if checks_passed else 'verification_failed',checks_passed=checks_passed,model_version=model['version'],model_sha256=fingerprint(model),
        python=platform.python_version(),source_sha256=fingerprint(hashes),source_files=hashes,
        structure=structure,reachability=reach,generator=generator_coverage_report(model),safety=safety,
        limitations=['E2 nie jest odebrane; odbiór użytkownika pozostaje osobną decyzją.',
            'Świadkowie i generator nie wyczerpują przestrzeni stanów.',
            'G1/G3 w grafie są projekcjami, nie dowodem globalnej osiągalności ani braku zakleszczeń.',
            'Hypothesis uruchamia pytest; ten raport nie udaje ponownego uruchomienia testów.',
            'Nie wykonano TLC, dowodów żywotności ani oceny rzeczywistego projektu.'])


def render(report):
    r=report;reach=r['reachability'];safety=r['safety'];gen=r['generator']
    status='sprawdzenia zakończone pomyślnie; oczekuje odbioru użytkownika' if r['checks_passed'] else 'niepowodzenie sprawdzeń — zbadać szczegóły evidence.json'
    lines=[f"# E2 — raport sprawdzeń modelu v{r['model_version']}",'',
        f'**Status: {status}; E2 nie jest odebrane.** DEC-PRO-010 wdrożono w obowiązującym modelu. Regresje dawnych luk sprawdzają odmowę modelu bazowego oraz wykonanie naruszające reguły po celowej mutacji.','',
        '## Tożsamość badania','',f"- Model v{r['model_version']}, SHA-256: `{r['model_sha256']}`.",
        f"- Kod i dane sprawdzeń SHA-256: `{r['source_sha256']}`; Python `{r['python']}`.",
        '- Pełne scenariusze, wyniki i hashe plików: odtwarzany `evidence.json`. Polecenie: `.venv/bin/python scripts/run_e2.py --output artifacts/e2`. Kod wyjścia 0 oznacza powodzenie sprawdzeń (bez odbioru E2), 1 niepowodzenie sprawdzeń, 2 błąd przygotowania raportu.','',
        '## Struktura i wykonalność','', '| Właściwość | Model bazowy | Mutant wykryty | Zakres |','|---|---|---|---|']
    for p in ('G0','G1','G2','G3','G4','G5','G6'):
        e=r['structure'][p]
        lines.append(f"| {p} | {e.get('baseline','raport')} | {e.get('mutant_detected','nie dotyczy')} | {e.get('scope',e.get('kind','struktura/adnotacje'))} |")
    lines += ['',f"**{len(reach['covered'])}/28 przejść** ma jawny, wykonany świadek od stanu początkowego. Brakujące: {reach['missing']}. G2 wymaga dodatkowo T04 dla wszystkich pięciu typów; brakujące zastosowania: {r['structure']['G2']['missing_applications']}. Mutant G2 sprawdzono na stanie CODE osiągniętym modelem bazowym; odrzucenia wcześniejszego DES nie zaliczamy jako próby CODE. Ta sama wyrocznia pokrycia zgłasza również brak T04:CODE w korpusie wykonanym zmienionym modelem.",'',
        '| Przejście | Scenariusz | Liczba kroków prefiksu |','|---|---|---|']
    for ident,data in sorted(reach['witnesses'].items()):
        lines.append(f"| {ident} | {data['id']} | {len(data['events'])} |")
    lines += ['','## Bezpieczeństwo i czułość wyroczni','',
        'Niezależny moduł safety.py nie importuje wykonawcy, parsera ani jego helperów. S2/S3/S8/S15 sprawdzają całą historię wersji i wydania; nie przyjmują wstrzykniętego prefiksu jako dowodu. Poniżej mutant jest przypisany wyłącznie do właściwości, której naruszenie wyrocznia rzeczywiście zgłosiła.','',
        '| Właściwość | Wykryte mutanty WIT i regresji DEC-PRO-010 |','|---|---|']
    for prop,ids in safety['properties'].items():
        lines.append(f"| {prop} | {', '.join(ids) or 'BRAK'} |")
    lines += ['',f"W pięciu WIT: {sum(len(w['violations']) for w in safety['witnesses'])} naruszeń S1–S15. Wykryto {sum(m['gate_detected'] for m in safety['mutations'])}/{len(safety['mutations'])} mutantów prób bramek. Pokrycie właściwości S wykonanymi mutantami niezależnej wyroczni: {len(safety['properties'])-len(safety['missing'])}/{len(safety['properties'])}; brakujące: {safety['missing']}. Próby reguł kolejki lub strażnika T11 mogą nie naruszać żadnej formuły S — nie przypisujemy im sztucznie takiego wyniku.",'',
        '## Generowanie sekwencji','',
        '`tests/test_stateful.py`: RuleBasedStateMachine dla zakresu bazowego, bez p1 i pustego; każda max_examples=24, stateful_step_count=25, derandomize=True. Początek to osiągalny prefiks; dalsze kroki są generowane na nowo. Sprawdzane są S1–S15, odmowy i atomowość. Nie filtrujemy wyników wyroczni. Wyniki pytest są zapisane w STAN, a nie wnioskowane z samego generatora.','',
        f"Oddzielny deterministyczny przegląd kandydatów w {gen['source_states']} źródłach świadków pokrywa {len(gen['covered'])} przejść: {gen['counts']}. To liczby prób kandydatów, nie liczba wszystkich stanów ani kroków Hypothesis. Granice pytań, wersji i wydań są wynikiem boundary, nie dowodem zakleszczenia.",'',
        '## Regresje zaakceptowanej korekty v0.7','',
        '| Przypadek | Obowiązujący model | Mutant |', '|---|---|---|',
        '| Pytanie blocking po W02 | W04 odmawia; rozstrzygnięcie pozwala na odbiór | Brak guard W04 wykrywany przez S14 |',
        '| T09/T10 po dwóch odrzuceniach wersji | T10 zachowuje licznik; trzecie T03 odmawia | Reset licznika wykrywany przez S15 |',
        '| Zmiana p1 poza zakresem wydania | Nowe suspect w zakresie cofa ready/reviewed | Usunięcie obserwatora narusza S7a/S7b |',
        '| Pusty zakres | W01 wymaga tests_ok i braku blokad; pełny odbiór możliwy | Stary guard przepuszcza osobno brak testów i blokadę |','',
        'Pięć dodatkowych prób ma pełne ślady bazowe i mutantów w evidence.json oraz jawny zakres instancji. tests/test_readiness_matrix.py sprawdza 32 kombinacje zakresu, tests_ok, blocking i stanów pytań; cztery blocking/deferred odmawiają P04 i następnie W01 w zachowanym asked. Testy obejmują też rozwiązanie późnego pytania, dwa budżety różnych wersji i zachowanie odebranego wydania przy wpływie spoza zakresu. Dawny mutant T07(r1) bez invalidate_release jest teraz maskowany poprawnie przez nowy obserwator; zastąpiono go próbą T07(a2) bez zależnych produktów. To kontrola reguły T07, nie S7a. S7a nadal ma własne naruszające mutanty.','',
        'Historyczne kontrprzykłady v0.6 i proponowana wtedy kopia: model/proposals/e2-hardening-diagnostics.json. Ich skrypt uruchamiać na commicie de94da9; bieżące regresje nie wykonują historycznego skryptu. Decyzja i lista wpływu: DEC-PRO-010 w docs/STAN.md. Niezależny końcowy przegląd: docs/reviews/E2-V07-PRZEGLAD-2026-10-26.md.','',
        '## Granice wyniku','']
    lines += ['- '+s for s in r['limitations']]
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description='Raport E2 bez odbioru etapu')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        result=build_report(); markdown=render(result)
        if args.output:
            args.output.mkdir(parents=True,exist_ok=True)
            (args.output/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            (args.output/'report.md').write_text(markdown)
            print(f"E2: {result['status']}; raport: {args.output/'report.md'}")
        else: print(markdown,end='')
        return 0 if result['checks_passed'] else 1
    except (ValueError,OSError,KeyError) as error:
        print(f'Nie przygotowano raportu E2: {error}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
