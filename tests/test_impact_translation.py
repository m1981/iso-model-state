"""Granice odmowy translatora E3.4; testy nie stanowią niezależnej wyroczni."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from isomodel.tla_impact import IDS, prelude, render_probes, validate_command, value_literal
from isomodel.tla_projection import ProjectionError


@pytest.fixture
def world():
    root=Path(__file__).resolve().parents[1]
    state=json.loads((root/'docs/preparations/e3-04/expected-checkpoints.json').read_text())['checkpoints'][0]['state']
    state['releases']={int(k):v for k,v in state['releases'].items()}
    return state


def command():
    return dict(operation=3,item='r1',question='q0',actor='U',checks=True,evidence=True,unambiguous=True,resolution='approved')


@pytest.mark.parametrize('field,value', [('operation',True),('operation',9),('item',[]),('actor',[]),('actor','X'),('checks',1),('evidence','false'),('unambiguous',0),('resolution','answered'),('question','none')])
def test_command_type_and_shape_refusals(model,world,field,value):
    c=command(); c[field]=value
    with pytest.raises(ProjectionError): validate_command(model,c,world)


def test_unknown_and_extra_inputs(model,world):
    for changes in ({'surprise':True},{'item':'missing'},{'question':'missing'}):
        with pytest.raises(ProjectionError): validate_command(model,command()|changes,world)


def test_inactive_unknown_helper_fails_closed(model,world):
    model['helper_effects']['invalidate_release(e)']='if false: arbitrary prose'
    with pytest.raises(ProjectionError,match='helper'): prelude(model,world)


def test_inactive_observer_unknown_effect_fails_closed(model,world):
    model['post_step_effects'].append(dict(id='unreachable',guard='false',effects=['unknown prose']))
    with pytest.raises(ProjectionError,match='skutek'): prelude(model,world)


def test_empty_quantifier_unknown_body_fails_closed(model,world):
    model['item_transitions'][1]['guard']='forall d in deps(e): unknown_fn(d)'
    with pytest.raises(ProjectionError): prelude(model,world)


@pytest.mark.parametrize('effect',['depends_on := depends_on','predecessor := none','state := draft','q.state := resolved'])
def test_topology_and_state_effects_refused(model,world,effect):
    next(t for t in model['item_transitions'] if t['id']=='T05')['effects'].append(effect)
    with pytest.raises(ProjectionError): prelude(model,world)


def test_cycle_refused(model,world):
    world['items']['p1']['depends_on']=['r1']
    with pytest.raises(ProjectionError,match='Cykl'): prelude(model,world)


def test_probe_topologies_cannot_be_mixed(model,world):
    altered=deepcopy(world);altered['items']['a1']['depends_on']=['r2']
    cases=[dict(before=w,command=command(),expected=None) for w in (world,altered)]
    with pytest.raises(ProjectionError,match='topologi'): render_probes(model,cases)


def test_literal_preserves_sequence_and_set_distinction():
    assert value_literal(['a','b'])=='<<"a", "b">>'
    assert value_literal(['a','b'],'scope')=='{"a", "b"}'
    assert value_literal([])=='<<>>'
    assert value_literal({})=='[emptyKey \\in {} |-> 0]'
    assert value_literal({1:None})=='((1 :> "__null__"))'
    assert value_literal('a "quote" \\ line\nnext')=='"a \\"quote\\" \\\\ line\\nnext"'


def test_model_mutations_are_translated_without_id_dispatch(model,world):
    t=next(t for t in model['item_transitions'] if t['id']=='T05')
    t.update(actor='A',to='verified',guard='true',effects=['version := version + 1'])
    text=prelude(model,world)
    assert 'Enabled3(w,c)' in text and 'THEN' in text
    assert 'Result3(w,c) == LET s0 == [w EXCEPT !.items[c.item].state = "verified"]' in text


def test_raw_results_are_not_bound_by_exploration_limits(model,world):
    model['test_instance']['bounds'].update(max_version=1,max_questions=1)
    text=prelude(model,world)
    assert 'max_version' not in text and 'max_questions' not in text


def test_non_latin1_evidence_is_explicitly_refused():
    with pytest.raises(ProjectionError,match='Latin-1'):
        value_literal('Zażółć')
    assert value_literal('a\b\\"\n\t\r\f') == '"a\b\\\\\\"\\n\\t\\r\\f"'


@pytest.mark.parametrize('section,field', [
    ('question_semantics','creation'),
    ('question_semantics','answer'),
    ('question_semantics','frame'),
    ('release_semantics','default_target'),
    ('release_semantics','new_release_target'),
    ('release_semantics','frame'),
    ('release_semantics','scope_copy'),
    ('release_semantics','pending_priority'),
    ('release_semantics','bounds'),
])
@pytest.mark.parametrize('inactive', [False, True])
def test_unrecognized_semantics_prose_refused(model,world,section,field,inactive):
    if inactive:
        world['questions']={}
        world['next_release_required']=True
    model[section][field]='Nieobsługiwana zmiana reguły, także w nieaktywnej gałęzi.'
    with pytest.raises(ProjectionError,match=section+'.'+field):
        prelude(model,world)


@pytest.mark.parametrize('field', ['unexpected','pending_priority'])
def test_release_semantics_shape_refused(model,world,field):
    if field=='unexpected': model['release_semantics'][field]='Nieznana reguła'
    else: del model['release_semantics'][field]
    with pytest.raises(ProjectionError,match='release_semantics'):
        prelude(model,world)


def test_renamed_semantics_prose_keeps_meaning(model,world):
    import re
    renamed={ident:'Renamed'+str(index) for index,ident in enumerate(IDS)}
    pattern=re.compile(r'\b('+'|'.join(IDS)+r')\b')
    def rewrite(value):
        if isinstance(value,str): return pattern.sub(lambda match:renamed[match[0]],value)
        if isinstance(value,list): return [rewrite(v) for v in value]
        if isinstance(value,dict): return {k:rewrite(v) for k,v in value.items()}
        return value
    changed=rewrite(model)
    seed=rewrite(world)
    text=prelude(changed,seed,tuple(renamed.values()))
    assert 'RawEnabled(w,c)' in text
    changed['question_semantics']['frame']+=' Nieznana dodatkowa reguła.'
    with pytest.raises(ProjectionError,match='question_semantics.frame'):
        prelude(changed,seed,tuple(renamed.values()))


@pytest.mark.parametrize('transition,effect', [
    ('T05','q.id := e.id'),
    ('P02','q.id := q.id'),
    ('P02','id := q.id'),
    ('T05','q.state := resolved'),
    ('P02','q.state := resolved'),
    ('P02','state := resolved'),
    ('T05','q.type := e.type'),
    ('T05','q.depends_on := e.depends_on'),
])
def test_question_effect_target_outside_model_variables_refused(model,world,transition,effect):
    kind='item' if transition.startswith('T') else 'question'
    definition=next(t for t in model[kind+'_transitions'] if t['id']==transition)
    definition['effects'].append(effect)
    definition['guard']='false'  # Cały skutek musi być sprawdzony także przy odmowie guard.
    with pytest.raises(ProjectionError):
        prelude(model,world)


@pytest.mark.parametrize('field,expression', [('id','e.id'),('type','e.type'),('depends_on','e.depends_on'),('predecessor','e.predecessor')])
def test_question_creation_field_outside_model_variables_refused(model,world,field,expression):
    definition=next(t for t in model['item_transitions'] if t['id']=='T12')
    definition['effects'][0]=definition['effects'][0][:-1]+f', {field} = {expression})'
    definition['guard']='false'
    with pytest.raises(ProjectionError):
        prelude(model,world)


def test_question_creation_initial_state_is_a_model_variable(model,world):
    definition=next(t for t in model['item_transitions'] if t['id']=='T12')
    definition['effects'][0]=definition['effects'][0][:-1]+', state = none)'
    # Stan początkowy jest legalnym polem inicjalizacji E2; id pochodzi ze zdarzenia.
    prelude(model,world)
