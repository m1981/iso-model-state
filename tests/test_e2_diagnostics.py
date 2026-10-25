"""Regresje dawnych luk na obowiązującym modelu, a nie proponowanej kopii."""
from copy import deepcopy
from pathlib import Path

import pytest

from isomodel.hardening import hardening_evidence
from isomodel.execution import replay
from isomodel.safety import safety_violations

ROOT = Path(__file__).resolve().parents[1]


def test_approved_hardening_blocks_all_counterexamples(model):
    original = deepcopy(model)
    cases = hardening_evidence(model, ROOT)
    assert model == original
    assert len(cases) == 5
    for case in cases:
        assert case['gate_detected'], case['id']
        assert not case['baseline_violations']
        assert case['mutant_applied']
    assert cases[0]['oracle_detected'] == ['S14']
    assert cases[1]['oracle_detected'] == ['S15']
    assert cases[2]['oracle_detected'] == ['S7a', 'S7b']


@pytest.mark.parametrize('tests_ok,blocking,expected', [
    (True, False, 'completed'), (False, False, 'rejected'),
    (True, True, 'rejected'), (False, True, 'rejected')])
def test_empty_scope_full_execution_respects_global_gates(model, tests_ok, blocking, expected):
    model['test_instance']['release_scope'] = []
    events = ([dict(transition='P00', actor='R', question='late', attributes={'blocking':True})]
              if blocking else [])
    events += [dict(transition='W01', actor='A'), dict(transition='W02', actor='R'),
               dict(transition='W04', actor='U', evidence={'simulation':True,'quote':'Odbiór testowy.'})]
    result = replay(model, dict(id='empty', simulation=True, inputs={'tests_ok':tests_ok}, events=events))
    assert result['outcome'] == expected, result['steps'][-1]
    assert safety_violations(model, [s for s in result['steps'] if s['outcome']=='applied']) == []
    if expected == 'completed':
        assert result['final_state']['releases'][1]['state'] == 'accepted'
    else:
        assert result['steps'][-1]['code'] == 'guard'
        assert result['final_state']['releases'][1]['state'] == 'in_preparation'
