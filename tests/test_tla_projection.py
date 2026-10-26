"""Niezależne oczekiwania lokalnego T03; rzeczywiste TLC, nie test tekstu generatora."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel import load_model
from isomodel.execution import StepRejected, execute_step, initial_state
from isomodel.tla_projection import ProjectionError, render_probe
from isomodel.tlc import run_tlc

ROOT = Path(__file__).resolve().parents[1]
JAVA = Path('/Applications/PyCharm.app/Contents/jbr/Contents/Home/bin/java')
JAR = ROOT / 'artifacts/tools/tla/1.7.4/tla2tools.jar'


def inputs():
    return load_model(ROOT / 'model/process.yaml'), json.loads((ROOT / 'tests/fixtures/e3/t03_cases.json').read_text())['cases']


def definition(model):
    return next(t for t in model['item_transitions'] if t['id'] == 'T03')


def check_python(model, cases, transition='T03'):
    for case in cases:
        state = initial_state(model)
        state['items']['r1'] = deepcopy(case['before'])
        frozen = deepcopy(state)
        try:
            result = execute_step(model, state, {'transition': transition, 'actor': case['actor'], 'item': 'r1'}, {})
        except StepRejected:
            assert not case['enabled'], case['id']
        else:
            assert case['enabled'], case['id']
            assert result['after']['items']['r1'] == case['after']
            restored = deepcopy(result['after'])
            restored['items']['r1'] = frozen['items']['r1']
            assert restored == frozen
        assert state == frozen


def run(model, cases, tmp_path, transition='T03'):
    tmp_path.mkdir(parents=True, exist_ok=True)
    module, config = render_probe(model, transition, cases)
    (tmp_path / 'Projection.tla').write_text(module)
    (tmp_path / 'Projection.cfg').write_text(config)
    return run_tlc(tmp_path / 'Projection.tla', tmp_path / 'Projection.cfg', tmp_path / 'result', java=JAVA, jar=JAR)


def test_baseline_relation_and_complete_frame(tmp_path):
    model, cases = inputs()
    check_python(model, cases)
    result = run(model, cases, tmp_path)
    assert result['status'] == 'passed', result
    assert result['distinct_states'] == len(cases) + sum(c['enabled'] for c in cases)
    assert Path(result['states_file']).stat().st_size > 0


@pytest.mark.parametrize('variant', ['renamed', 'limit', 'from', 'to', 'same_state'])
def test_controlled_data_changes_reach_tlc(variant, tmp_path):
    model, cases = inputs()
    t = definition(model)
    transition = 'T03'
    if variant == 'renamed':
        t['id'] = transition = 'T_RENAMED'
    elif variant == 'limit':
        model['parameters']['MAX_REJECTIONS'] = 1
        for c in cases:
            if c['before']['rejections'] == 1:
                c.update(enabled=False, after=None)
    elif variant == 'from':
        t['from'] = ['approved']
        for c in cases:
            c.update(enabled=False, after=None)
        c = next(c for c in cases if c['id'] == 'approved_refused')
        c.update(enabled=True, after=c['before'] | {'state': 'draft', 'rejections': 1})
    elif variant == 'to':
        t['to'] = 'deferred'
        for c in cases:
            if c['enabled']:
                c['after']['state'] = 'deferred'
    else:
        t['to'] = '='
        for c in cases:
            if c['enabled']:
                c['after']['state'] = c['before']['state']
    check_python(model, cases, transition)
    assert run(model, cases, tmp_path, transition)['status'] == 'passed'


@pytest.mark.parametrize('variant,oracle', [('guard', 'Availability'), ('actor', 'Availability'), ('effect', 'Successor')])
def test_semantic_mutants_violate_named_oracle(variant, oracle, tmp_path):
    model, cases = inputs()
    t = definition(model)
    if variant == 'guard':
        t['guard'] = 'true'
        c = next(c for c in cases if c['id'] == 'budget_exhausted')
        state = initial_state(model)
        state['items']['r1'] = deepcopy(c['before'])
        assert execute_step(model, state, {'transition': 'T03', 'actor': 'U', 'item': 'r1'}, {})['after']['items']['r1']['rejections'] == 3
    elif variant == 'actor':
        t['actor'] = 'A'
    else:
        t['effects'] = []
    result = run(model, cases, tmp_path)
    assert result['status'] == 'invariant_violation', result
    assert result['invariant'] == oracle
    assert result['returncode'] == 12
    # Osobno wykonany następnik mutanta, nie tylko błąd dostępności w Init.
    ident = {'guard': 'budget_exhausted', 'actor': 'author_refused', 'effect': 'first_rejection'}[variant]
    witness = deepcopy(next(c for c in cases if c['id'] == ident))
    count = {'guard': 3, 'actor': 1, 'effect': 0}[variant]
    witness.update(enabled=True, after=witness['before'] | {'state': 'draft', 'rejections': count})
    witness_result = run(model, [witness], tmp_path / 'witness')
    assert witness_result['status'] == 'passed'
    assert witness_result['distinct_states'] == 2


@pytest.mark.parametrize('field,value', [('guard', 'false and checks_ok(e)'), ('effects', ['invalidate_release(e)']), ('effects', ['state := draft']), ('effects', ['rejections := mystery']), ('target', 'new_release'), ('evidence', 'DEC'), ('arguments', {'x': {}})])
def test_unsupported_semantics_refuses_even_when_disabled(field, value):
    model, cases = inputs()
    t = definition(model)
    t['guard'] = 'false'
    t[field] = value
    with pytest.raises(ProjectionError):
        render_probe(model, 'T03', cases)


def test_unknown_item_field_not_silently_discarded():
    model, cases = inputs()
    cases[0]['before']['unknown'] = 1
    with pytest.raises(ProjectionError):
        render_probe(model, 'T03', cases)


def test_malformed_dependency_is_readable_projection_error():
    model, cases = inputs()
    cases[0]['before']['depends_on'] = [{'id': 'p1'}]
    with pytest.raises(ProjectionError, match='depends_on'):
        render_probe(model, 'T03', cases)
