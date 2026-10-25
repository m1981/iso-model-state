"""Zgoda na konkretną operację i niezmienność kolejnych odbiorów.

Trace: DEC-PRO-008, WIT5, S7a, S10, S11.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from isomodel import load_model
from isomodel.execution import execute_step, initial_state, replay, StepRejected, InputError, ExplorationBoundary

ROOT = Path(__file__).resolve().parents[1]


def scenario():
    return json.loads((ROOT / 'tests/fixtures/wit5/scenario.json').read_text())


def prefix(model, count=32):
    data = scenario()
    state = initial_state(model)
    for event in data['events'][:count]:
        state = execute_step(model, state, event, data['inputs'])['after']
    return state


def transition(model, ident):
    return next(t for kind in ('item', 'question', 'release') for t in model[f'{kind}_transitions'] if t['id'] == ident)


def change(item='a2', question='q1', operation='T05'):
    return dict(transition=operation, actor='U', item=item, question=question)


def test_wit5_two_acceptances_keep_first_record_identical(model):
    data = scenario()
    original = deepcopy((model, data))
    result = replay(model, data)
    assert result['outcome'] == 'completed', result['steps'][-1]
    assert len(result['steps']) == 40
    first = result['steps'][28]['after']['releases'][1]
    for step in result['steps'][29:]:
        assert step['after']['releases'][1] == first
    final = result['final_state']
    assert final['current_release'] == 2 and final['next_release_required'] is False
    assert [r['state'] for r in final['releases'].values()] == ['accepted', 'accepted']
    assert final['releases'][1]['snapshot']['a2']['version'] == 1
    assert final['releases'][2]['snapshot']['a2']['version'] == 2
    assert final['questions']['q1']['consumed'] is True
    record = result['records'][0]
    assert {k: record[k] for k in ('about','about_version','requested_transition','resolution')} == dict(about='a2', about_version=1, requested_transition='T05', resolution='approved')
    assert (model, data) == original and replay(model, data) == result
    final['releases'][2]['scope'].clear()
    assert len(final['releases'][1]['scope']) == 7


@pytest.mark.parametrize('field,value', [('state','asked'),('kind','general'),('resolution','rejected'),('about','r1'),('about_version',2),('requested_transition','T07'),('consumed',True)])
def test_each_authorization_condition_blocks_independently(model, field, value):
    state = prefix(model)
    state['questions']['q1'][field] = value  # Wstrzyknięcie bada predykat, nie osiągalność.
    before = deepcopy(state)
    with pytest.raises(StepRejected, match='guard'):
        execute_step(model, state, change(), {})
    assert state == before


@pytest.mark.parametrize('resolution', ['approved','rejected'])
def test_answer_preserves_binding_and_quote_and_distinguishes_outcome(model, resolution):
    state = prefix(model, 31)
    event = scenario()['events'][31]
    event['inputs']['resolution'] = resolution
    step = execute_step(model, state, event, {})
    after = step['after']['questions']['q1']
    assert after == dict(state['questions']['q1'], state='resolved', resolution=resolution)
    assert step['records'][0]['resolution'] == resolution
    if resolution == 'approved':
        execute_step(model, step['after'], change(), {})
    else:
        with pytest.raises(StepRejected, match='guard'):
            execute_step(model, step['after'], change(), {})


@pytest.mark.parametrize('resolution', [None, 'answered', 'yes', True])
def test_change_answer_requires_explicit_valid_resolution(model, resolution):
    state = prefix(model, 31)
    before = deepcopy(state)
    event = scenario()['events'][31]
    if resolution is None:
        del event['inputs']['resolution']
    else:
        event['inputs']['resolution'] = resolution
    with pytest.raises(InputError):
        execute_step(model, state, event, {})
    assert state == before


def test_ambiguous_change_answer_does_not_create_decision_or_grant_permission(model):
    state = prefix(model, 31)
    event = dict(transition='P03',actor='U',question='q1')
    step = execute_step(model,state,event,{})
    assert step['records'] == []
    assert step['after']['questions']['q1'] == dict(state['questions']['q1'],state='open')
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,step['after'],change(),{})


@pytest.mark.parametrize('attributes', [
    dict(kind='change', about='missing', requested_transition='T05', blocking=True),
    dict(kind='change', about='a2', requested_transition='T08', blocking=True),
    dict(kind='change', about='a2', requested_transition='T05', blocking=False),
    dict(kind='change', about='a2', requested_transition='T05', blocking=True, about_version=99),
    dict(kind='general', about='a2', blocking=True),
])
def test_invalid_binding_is_rejected_at_creation(model, attributes):
    state = prefix(model,29)
    before = deepcopy(state)
    with pytest.raises(InputError):
        execute_step(model,state,dict(transition='P00',actor='A',question='q1',attributes=attributes),{})
    assert state == before


def test_change_question_cannot_target_uncreated_item(model):
    with pytest.raises(InputError):
        execute_step(model,initial_state(model),scenario()['events'][29],{})


def test_error_after_consumption_rolls_back_permission_item_and_release(model):
    state=prefix(model)
    before=deepcopy(state)
    transition(model,'T05')['effects'].append('version := tests_ok + 1')
    with pytest.raises(InputError):
        execute_step(model,state,change(),dict(tests_ok=True))
    assert state == before and not state['questions']['q1']['consumed']


def test_version_bound_does_not_consume_permission(model):
    state=prefix(model)
    model['test_instance']['bounds']['max_version']=1
    before=deepcopy(state)
    with pytest.raises(ExplorationBoundary):
        execute_step(model,state,change(),{})
    assert state == before


def test_w06_priority_and_bounds_keep_accepted_record(model):
    state=prefix(model,33)
    before=deepcopy(state)
    with pytest.raises(StepRejected,match='pending_release'):
        execute_step(model,state,dict(transition='T01',actor='A',item='a2'),scenario()['inputs'])
    model['test_instance']['bounds']['max_releases']=1
    with pytest.raises(ExplorationBoundary):
        execute_step(model,state,dict(transition='W06',actor='A'),{})
    assert state == before


def test_next_release_requires_new_change_not_just_old_acceptance(model):
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,prefix(model,29),dict(transition='W06',actor='A'),{})


@pytest.mark.parametrize('count,expected',[(27,'in_preparation'),(28,'in_preparation'),(29,'accepted')])
def test_change_invalidates_readiness_but_preserves_acceptance(model,count,expected):
    state=prefix(model,count)
    for event in scenario()['events'][29:33]:
        state=execute_step(model,state,event,{})['after']
    assert state['releases'][1]['state']==expected
    assert state['next_release_required'] is (count==29)


def test_transitive_dependents_suspect_and_t12_opens_bound_request(model):
    state=prefix(model,29)
    events=deepcopy(scenario()['events'][29:32])
    events[0]['attributes']['about']='r1'
    for event in events:
        state=execute_step(model,state,event,{})['after']
    state=execute_step(model,state,change(item='r1'),{})['after']
    assert {i for i,v in state['items'].items() if v['suspect']} == {'a1','d1','c1'}
    state=execute_step(model,state,dict(transition='W06',actor='A'),{})['after']
    after=execute_step(model,state,dict(transition='T12',actor='A',item='a1',question='q2'),{})['after']
    q=after['questions']['q2']
    assert (q['state'],q['kind'],q['about'],q['about_version'],q['requested_transition'],q['resolution'],q['consumed']) == ('open','change','a1',1,'T05','none',False)
    assert after['items']==state['items'] and after['releases']==state['releases']


def test_model_authorization_expression_is_used(model):
    state=prefix(model)
    model['question_semantics']['authorized_change']='false'
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,state,change(),{})


@given(resolution=st.sampled_from(['approved','rejected','none','answered']),
       target=st.sampled_from(['a2','r1']), version=st.integers(min_value=1,max_value=3),
       operation=st.sampled_from(['T05','T07']), consumed=st.booleans())
def test_generated_authorization_matches_independent_oracle(resolution,target,version,operation,consumed):
    model=load_model(ROOT/'model/process.yaml')
    state=prefix(model)
    state['questions']['q1'].update(resolution=resolution,about=target,about_version=version,requested_transition=operation,consumed=consumed)
    expected=resolution=='approved' and target=='a2' and version==1 and operation=='T05' and not consumed
    try:
        result=execute_step(model,state,change(),{})
    except StepRejected:
        assert not expected
    else:
        assert expected and result['after']['questions']['q1']['consumed']


def test_supersede_requires_its_own_permission_and_marks_consumption(model):
    state=prefix(model,29)
    events=deepcopy(scenario()['events'][29:32])
    events[0]['attributes']['requested_transition']='T07'
    for event in events:
        state=execute_step(model,state,event,{})['after']
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,state,change(),{})
    after=execute_step(model,state,change(operation='T07'),{})['after']
    assert after['items']['a2']['state']=='superseded'
    assert after['items']['a2']['version']==1 and after['questions']['q1']['consumed']
    assert after['releases']==state['releases']


def test_consumption_guard_mutant_is_detected_independently_of_version(model):
    state=prefix(model)
    # Kontrolowane wstrzyknięcie izoluje warunek consumed od zmiany wersji i stanu.
    state['questions']['q1']['consumed']=True
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,state,change(),{})
    model['question_semantics']['authorized_change']=model['question_semantics']['authorized_change'].replace(' and not q.consumed','')
    assert execute_step(model,state,change(),{})['after']['items']['a2']['version']==2


def test_old_consent_cannot_be_reused_after_real_second_baseline(model):
    state=prefix(model,37)
    before=deepcopy(state)
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,state,change(),{})
    assert state==before


@pytest.mark.parametrize('operation',['T05','T07'])
@pytest.mark.parametrize('actor',['A','R'])
def test_authorized_change_still_requires_user_actor(model,operation,actor):
    state=prefix(model)
    event=change(operation=operation)
    event['actor']=actor
    with pytest.raises(StepRejected,match='actor'):
        execute_step(model,state,event,{})


def test_t12_question_bound_is_atomic_and_existing_id_is_not_overwritten(model):
    state=prefix(model,29)
    state['items']['a1']['suspect']=True  # Kontrola lokalnej semantyki T12.
    event=dict(transition='T12',actor='A',item='a1',question='q1')
    state=execute_step(model,state,event,{})['after']
    before=deepcopy(state)
    with pytest.raises(InputError):
        execute_step(model,state,event,{})
    model['test_instance']['bounds']['max_questions']=1
    event['question']='q2'
    with pytest.raises(ExplorationBoundary):
        execute_step(model,state,event,{})
    assert state==before


def test_out_of_scope_change_triggers_new_release_through_suspect(model):
    state=prefix(model,29)
    state['releases'][1]['scope'].remove('d1')  # Kontrolowany zakres przed zdarzeniem.
    before=deepcopy(state['releases'][1])
    after=execute_step(model,state,dict(transition='T06',actor='U',item='d1'),{})['after']
    assert after['items']['c1']['suspect'] and after['next_release_required']
    assert after['releases'][1]==before


@pytest.mark.parametrize('phase',['ready','reviewed','accepted'])
def test_resume_deferred_item_invalidates_current_release(model,phase):
    data=scenario()
    state=prefix(model,17)
    state=execute_step(model,state,dict(transition='T09',actor='U',item='a2'),{})['after']
    end={'ready':27,'reviewed':28,'accepted':29}[phase]
    for event in data['events'][20:end]:
        state=execute_step(model,state,event,data['inputs'])['after']
    old=deepcopy(state['releases'][1])
    after=execute_step(model,state,dict(transition='T10',actor='U',item='a2'),{})['after']
    assert after['items']['a2']['state']=='draft'
    if phase=='accepted':
        assert after['releases'][1]==old and after['next_release_required']
    else:
        assert after['releases'][1]['state']=='in_preparation' and not after['next_release_required']


def test_renaming_transition_ids_preserves_behavior_when_references_are_updated(model):
    data=scenario()
    mapping={'T05':'CHANGE_RENAMED','T07':'SUPERSEDE_RENAMED','W06':'NEXT_RENAMED'}
    for kind in ('item','question','release'):
        for t in model[f'{kind}_transitions']:
            t['id']=mapping.get(t['id'],t['id'])
            t['effects']=[effect.replace('requested_transition = T05','requested_transition = CHANGE_RENAMED') for effect in t['effects']]
    model['question_semantics']['change_operations']=[mapping.get(i,i) for i in model['question_semantics']['change_operations']]
    for event in data['events']:
        event['transition']=mapping.get(event['transition'],event['transition'])
        if 'requested_transition' in event.get('attributes',{}):
            event['attributes']['requested_transition']=mapping[event['attributes']['requested_transition']]
    result=replay(model,data)
    assert result['outcome']=='completed' and result['final_state']['current_release']==2
