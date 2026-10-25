"""Odtworzenie luk przed propozycją WIT3; nie jest implementacją WIT3.

Trace: WIT3, S4, S6, S7a. Czyta zatwierdzony v0.5, nie zapisuje modelu.
Korekta T11 jest sprawdzana wyłącznie na oznaczonej kopii w pamięci.
"""
from copy import deepcopy
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))

from isomodel import load_model
from isomodel.execution import execute_step, fingerprint, initial_state, StepRejected, InputError


def main():
    model = load_model(ROOT / 'model/process.yaml')
    if model['version'] != 0.5:
        raise SystemExit('Diagnostyka dotyczy v0.5; po zmianie modelu użyj bazowego commitu e5fc842.')
    data = json.loads((ROOT / 'tests/fixtures/wit1/scenario.json').read_text())
    state = initial_state(model)
    for event in data['events'][:28]:
        state = execute_step(model, state, event, data['inputs'])['after']
    assert state['releases'][1]['state'] == 'reviewed'
    original = deepcopy((model, state))
    events = [
        dict(transition='P00', actor='A', question='q1',
             attributes=dict(kind='change', about='r1', requested_transition='T07', blocking=True)),
        dict(transition='P01', actor='A', question='q1'),
        dict(transition='P02', actor='U', question='q1',
             inputs=dict(unambiguous_answer=True, resolution='approved'),
             evidence=dict(simulation=True, decision='SIM-WIT3-REPLACE', quote='Zgoda testowa na zastąpienie r1 v1.')),
        dict(transition='T07', actor='U', item='r1', question='q1'),
    ]
    replaced = state
    for event in events:
        replaced = execute_step(model, replaced, event, data['inputs'])['after']
    affected = sorted(i for i, value in replaced['items'].items() if value['suspect'])
    assert affected == ['a1', 'c1', 'd1']
    assert replaced['releases'][1]['state'] == 'in_preparation'
    for ident in ('p1', 'r2', 'a2'):
        assert replaced['items'][ident] == state['items'][ident]
    denied = {}
    for label, attempt in [
        ('review_a1_with_superseded_dependency', dict(transition='T11', actor='A', item='a1')),
        ('ready_with_unresolved_impact', dict(transition='W01', actor='A')),
        ('create_undeclared_successor', dict(transition='T00', actor='A', item='r3')),
    ]:
        try:
            execute_step(model, replaced, attempt, data['inputs'])
        except (StepRejected, InputError) as error:
            denied[label] = error.code if isinstance(error, StepRejected) else 'input'
        else:
            raise AssertionError(f'Nieoczekiwane dopuszczenie: {label}')
    assert denied == dict(review_a1_with_superseded_dependency='guard',
                          ready_with_unresolved_impact='guard', create_undeclared_successor='input')

    # Osiągalny kontrprzykład S4, bez wstrzykiwania stanu: 28 kroków + T06 + T11.
    opened = execute_step(model, state, dict(transition='T06', actor='U', item='d1'), {})['after']
    review = dict(transition='T11', actor='A', item='c1',
                  evidence=dict(simulation=True, decision='SIM-WIT3-REVIEW', reference='SIM-Przejrzane-c1'))
    unsafe = execute_step(model, opened, review, {})['after']
    assert unsafe['items']['c1']['state'] == 'baselined' and not unsafe['items']['c1']['suspect']
    assert unsafe['items']['d1']['state'] == 'draft'

    candidate = deepcopy(model)
    fixed_guard = 'suspect and forall d in deps(e): d.state in {approved, baselined} and not d.suspect'
    next(t for t in candidate['item_transitions'] if t['id'] == 'T11')['guard'] = fixed_guard
    try:
        execute_step(candidate, opened, review, {})
    except StepRejected as error:
        assert error.code == 'guard'
    else:
        raise AssertionError('Proponowany T11 nie blokuje kontrprzykładu')
    assert (model, state) == original
    print(json.dumps({
        'purpose': 'diagnosis_only_not_WIT3_completion', 'model_version': model['version'],
        'base_commit': 'e5fc842b9447e53550aac73f229879bff9d2a850',
        'python': platform.python_version(),
        'model_sha256': fingerprint(model), 'fixture_sha256': fingerprint(data),
        'supersede_prefix_steps': 32, 'suffix_events': events,
        'affected': affected, 'release_after_supersede': replaced['releases'][1]['state'],
        'unchanged': ['p1', 'r2', 'a2'], 'denied': denied,
        'S4_counterexample': {'steps': 30, 'suffix': [dict(transition='T06', actor='U', item='d1'), review],
                              'c1': unsafe['items']['c1'], 'd1': unsafe['items']['d1']},
        'candidate_T11_guard': fixed_guard, 'candidate_blocks_counterexample': True,
        'production_model_unchanged': True,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
