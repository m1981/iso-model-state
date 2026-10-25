"""W03/W05: atomowe zgłoszenie uwag według reguły P00 w modelu.

Trace: G2, S9, W03, W05.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from isomodel import load_model
from isomodel.execution import execute_step, initial_state, InputError, StepRejected, ExplorationBoundary

ROOT = Path(__file__).resolve().parents[1]


def ready(model, reviewed=False):
    scenario=json.loads((ROOT/'tests/fixtures/wit1/scenario.json').read_text())
    state=initial_state(model)
    for event in scenario['events'][:28 if reviewed else 27]:
        state=execute_step(model,state,event,scenario['inputs'])['after']
    return state


def transition(model, ident):
    return next(t for kind in ('item','question','release') for t in model[kind+'_transitions'] if t['id']==ident)


@pytest.mark.parametrize('ident,actor,arguments', [('W03','R',{'findings':['q1','q2']}),('W05','U',{'question':'q1'})])
def test_release_findings_create_blocking_questions_atomically(model,ident,actor,arguments):
    state=ready(model,ident=='W05');before=deepcopy(state)
    step=execute_step(model,state,dict(transition=ident,actor=actor,**arguments),{})
    after=step['after']
    assert state==before and after['items']==before['items']
    assert after['releases'][1]['state']=='in_preparation'
    assert set(after['questions'])==set(arguments.get('findings',[arguments.get('question')]))
    for index,q in enumerate(after['questions'].values(),1):
        assert (q['state'],q['kind'],q['blocking'],q['age'])==('open','general',True,index)
    assert step['records']==[]
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,after,dict(transition='W01',actor='A'),{'tests_ok':True})


def test_review_empty_findings_is_literal_empty_iteration(model):
    state=ready(model)
    after=execute_step(model,state,dict(transition='W03',actor='R',findings=[]),{})['after']
    assert after['questions']=={} and after['releases'][1]['state']=='in_preparation'


@pytest.mark.parametrize('fields', [{},{'findings':None},{'findings':'q1'},{'findings':['q1','q1']},{'findings':['q1','']},{'findings':['q1',5]}])
def test_invalid_findings_never_leave_partial_release_or_question(model,fields):
    state=ready(model);before=deepcopy(state)
    with pytest.raises(InputError):
        execute_step(model,state,dict(transition='W03',actor='R',**fields),{})
    assert state==before


def test_question_limit_rolls_back_all_findings(model):
    state=ready(model);before=deepcopy(state)
    with pytest.raises(ExplorationBoundary):
        execute_step(model,state,dict(transition='W03',actor='R',findings=['q1','q2','q3','q4']),{})
    assert state==before


def test_findings_respect_existing_question_age_and_reject_reuse(model):
    state=ready(model)
    state=execute_step(model,state,dict(transition='P00',actor='A',question='old',attributes={'blocking':False}),{})['after']
    before=deepcopy(state)
    with pytest.raises(InputError):
        execute_step(model,state,dict(transition='W03',actor='R',findings=['new','old']),{})
    assert state==before
    after=execute_step(model,state,dict(transition='W03',actor='R',findings=['new']),{})['after']
    assert after['questions']['new']['age']==2
    assert after['questions']['old']==state['questions']['old']


def test_findings_execute_referenced_rule_from_yaml_not_hardcoded_p00(model):
    state=ready(model)
    transition(model,'P00')['guard']='false'
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,state,dict(transition='W03',actor='R',findings=['q1']),{})
    transition(model,'P00')['guard']='true'
    transition(model,'P00')['id']='RAISE_RENAMED'
    transition(model,'W03')['id']='FINDINGS_RENAMED'
    transition(model,'FINDINGS_RENAMED')['effects']=['for each finding: RAISE_RENAMED raise (blocking = true)']
    after=execute_step(model,state,dict(transition='FINDINGS_RENAMED',actor='R',findings=['q1']),{})['after']
    assert after['questions']['q1']['blocking'] is True


@pytest.mark.parametrize('transition_id', ['W01','W02','W04'])
def test_findings_field_is_not_accepted_by_unrelated_transition(model,transition_id):
    with pytest.raises(InputError):
        execute_step(model,ready(model),dict(transition=transition_id,actor='A',findings=[]),{})
