"""DEC-PRO-010: W01 na osiągalnych stanach dwóch instancji zakresu.

Trace: W01, INT-019. Blocking/deferred jest nieosiągalne: P04 musi odmówić,
a próba W01 dotyczy wtedy zachowanego asked, bez wstrzyknięcia deferred.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel.execution import execute_step, initial_state, StepRejected
from isomodel.safety import safety_violations


@pytest.mark.parametrize('empty_scope', [False, True])
@pytest.mark.parametrize('tests_ok', [False, True])
@pytest.mark.parametrize('blocking', [False, True])
@pytest.mark.parametrize('question_state', ['open', 'asked', 'resolved', 'deferred'])
def test_readiness_global_gates_matrix(model, empty_scope, tests_ok, blocking, question_state):
    data = json.loads((Path(__file__).parent / 'fixtures/wit1/scenario.json').read_text())
    if empty_scope:
        model['test_instance']['release_scope'] = []
    inputs = data['inputs'] | {'tests_ok': tests_ok}
    state = initial_state(model)
    steps = []

    def apply(candidate):
        nonlocal state
        step = execute_step(model, state, candidate, inputs)
        steps.append(step)
        state = step['after']

    for candidate in ([] if empty_scope else data['events'][:26]):
        apply(candidate)
    apply(dict(transition='P00', actor='R', question='matrix', attributes={'blocking':blocking}))
    if question_state != 'open':
        apply(dict(transition='P01', actor='A', question='matrix'))
    if question_state == 'resolved':
        apply(dict(transition='P02', actor='U', question='matrix',
                   inputs={'unambiguous_answer':True, 'resolution':'answered'},
                   evidence={'simulation':True, 'decision':'SIM-MATRIX', 'quote':'Odpowiedź testowa.'}))
    if question_state == 'deferred':
        attempt = dict(transition='P04', actor='U', question='matrix')
        if blocking:
            before = deepcopy(state)
            with pytest.raises(StepRejected) as error:
                apply(attempt)
            assert error.value.code == 'guard'
            assert state == before
        else:
            apply(attempt)
    actual_question_state = 'asked' if blocking and question_state == 'deferred' else question_state
    assert state['questions']['matrix']['state'] == actual_question_state
    assert safety_violations(model, steps) == []
    expected_ready = tests_ok and not (blocking and actual_question_state in {'open','asked'})
    if expected_ready:
        for candidate in data['events'][-3:]:
            apply(candidate)
        assert state['releases'][1]['state'] == 'accepted'
    else:
        before = deepcopy(state)
        with pytest.raises(StepRejected) as error:
            apply(dict(transition='W01', actor='A'))
        assert error.value.code == 'guard'
        assert state == before
        assert state['releases'][1]['state'] == 'in_preparation'
    assert safety_violations(model, steps) == []
