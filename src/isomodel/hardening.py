"""Wykonane regresje DEC-PRO-010 ze śladami bazowymi i mutantami.

Trace: S7a/S7b, S14/S15, W01. Alternatywne zakresy są jawne.
"""
from copy import deepcopy
import json
from pathlib import Path

from .execution import replay
from .safety import safety_violations


def hardening_evidence(model, root):
    cases = json.loads((Path(root) / 'mutants/e2_hardening.json').read_text())
    results = []
    for case in cases:
        instance = deepcopy(model)
        if case['alternative_scope'] == 'empty':
            instance['test_instance']['release_scope'] = []
        elif case['alternative_scope']:
            instance['test_instance']['release_scope'].remove('p1')
        baseline = replay(instance, case['scenario'])
        applied = [s for s in baseline['steps'] if s['outcome'] == 'applied']
        baseline_violations = safety_violations(instance, applied)
        mutant = deepcopy(instance)
        mutation = case['mutation']
        if 'remove_observer' in mutation:
            mutant['post_step_effects'] = [o for o in mutant['post_step_effects']
                                         if o['id'] != mutation['remove_observer']]
        else:
            target = next(t for kind in ('item', 'release') for t in mutant[kind + '_transitions']
                          if t['id'] == mutation['transition'])
            target[mutation['field']] = deepcopy(mutation['replacement'])
        trial = replay(mutant, case['scenario'])
        violations = safety_violations(instance, [s for s in trial['steps'] if s['outcome'] == 'applied'])
        expected = [] if case['property'] == 'W01' else case['property'].split('/')
        found = {v['property'] for v in violations}
        baseline_ok = (baseline['outcome'] == 'rejected'
                       and baseline['steps'][-1].get('code') == case['expected_code']
                       and not baseline_violations)
        mutant_applied = trial['outcome'] == 'completed'
        # W01 to kontrola globalnej bramki gotowości, nie nowa formuła S.
        gate_detected = baseline_ok and mutant_applied and set(expected) <= found
        results.append(dict(id=case['id'], scenario=case['scenario']['id'],
            release_scope=instance['test_instance']['release_scope'],
            gate_detected=gate_detected, mutant_applied=mutant_applied,
            baseline_violations=baseline_violations, expected_safety=expected,
            oracle_detected=[p for p in expected if p in found and gate_detected],
            violations=violations, baseline=baseline, mutant=trial))
    return results
