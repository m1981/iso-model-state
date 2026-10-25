"""Następca, jawna naprawa grafu i zakresu; przypadki dodatnie i próby obejścia.

Trace: DEC-PRO-009, WIT3, S1, S4, S5, S6, S7a, S10, S12, S13.
"""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

from isomodel import load_model
from isomodel.execution import execute_step, initial_state, replay, InputError, StepRejected, ExplorationBoundary

ROOT = Path(__file__).resolve().parents[1]


def scenario(name='wit3'):
    return json.loads((ROOT / f'tests/fixtures/{name}/scenario.json').read_text())


def prefix(model, count):
    data = scenario()
    state = initial_state(model)
    for event in data['events'][:count]:
        state = execute_step(model, state, event, data['inputs'])['after']
    return state


def transition(model, ident):
    return next(t for kind in ('item', 'question', 'release')
                for t in model[f'{kind}_transitions'] if t['id'] == ident)


def attempt(model, state, index):
    data = scenario()
    return execute_step(model, state, data['events'][index - 1], data['inputs'])


def test_initial_dependencies_are_independent_values_and_reserve_is_not_created(model):
    state = initial_state(model)
    assert len(state['items']) == 8
    assert state['items']['r3']['depends_on'] == ['p1']
    assert state['items']['r3']['state'] == 'none'
    assert state['items']['r3']['predecessor'] == 'none'
    assert state['items']['r3']['version'] == 0
    assert 'r3' not in state['releases'][1]['scope']
    state['items']['r3']['depends_on'].clear()
    assert model['test_instance']['items']['r3']['depends_on'] == ['p1']
    assert initial_state(model)['items']['r3']['depends_on'] == ['p1']


def test_wit3_reaches_acceptance_with_exact_impact_and_repaired_links(model):
    data = scenario()
    original = deepcopy((model, data))
    result = replay(model, data)
    assert result['outcome'] == 'completed', result['steps'][-1]
    assert len(result['steps']) == 54
    before = result['steps'][27]['after']
    changed = result['steps'][31]['after']
    assert {i for i, e in changed['items'].items() if e['suspect']} == {'a1', 'd1', 'c1'}
    assert changed['items']['r1']['state'] == 'superseded'
    assert changed['releases'][1]['state'] == 'in_preparation'
    for step in result['steps'][28:]:
        for ident in ('p1', 'r2', 'a2'):
            assert step['after']['items'][ident] == before['items'][ident]
        assert step['after']['current_release'] == 1
        assert not step['after']['next_release_required']
    final = result['final_state']
    assert final['releases'][1]['state'] == 'accepted'
    assert set(final['releases'][1]['scope']) == {'p1','r1','r2','r3','a1','a2','d1','c1'}
    assert final['items']['r3']['predecessor'] == 'r1'
    for ident in ('a1', 'd1'):
        assert final['items'][ident]['depends_on'] == ['r3']
        assert final['items'][ident]['version'] == 2
    assert final['items']['c1']['depends_on'] == before['items']['c1']['depends_on']
    assert final['items']['c1']['version'] == 1
    for ident, item in final['items'].items():
        assert item['state'] == ('superseded' if ident == 'r1' else 'baselined')
        assert not item['suspect']
    for q in final['questions'].values():
        assert (q['state'], q['resolution'], q['consumed']) == ('resolved','approved',True)
    assert len(final['questions']) == len(result['records']) == 2
    assert result['steps'][-2]['event'] == dict(transition='W02', actor='R')
    assert final['releases'][1]['snapshot']['a1']['depends_on'] == ['r3']
    assert final['releases'][1]['snapshot']['r3']['predecessor'] == 'r1'
    assert (model, data) == original and result == replay(model, data)


@pytest.mark.parametrize('name', ['wit1','wit2','wit4','wit5'])
def test_old_scenarios_leave_reserve_untouched(model, name):
    result = replay(model, scenario(name))
    assert result['outcome'] == 'completed', result['steps'][-1]
    assert result['final_state']['items']['r3'] == initial_state(model)['items']['r3']
    for release in result['final_state']['releases'].values():
        assert 'r3' not in release['scope']
        assert release['snapshot'] is None or 'r3' not in release['snapshot']


@pytest.mark.parametrize('predecessor,code', [('missing','input'), ('r2','guard'), ('d1','guard'), ('r3','guard')])
def test_create_rejects_invalid_predecessor_without_partial_creation(model, predecessor, code):
    state = prefix(model,32)
    before = deepcopy(state)
    event = dict(scenario()['events'][32], predecessor=predecessor)
    with pytest.raises((InputError, StepRejected)) as raised:
        execute_step(model,state,event,{})
    assert ('input' if isinstance(raised.value,InputError) else raised.value.code) == code
    assert state == before


def test_create_rejects_withdrawn_predecessor_and_reuse_of_id(model):
    state = prefix(model,32)
    state['items']['r1']['state'] = 'withdrawn'  # Kontrola lokalnego warunku.
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,state,33)
    state = prefix(model,33)
    with pytest.raises(StepRejected,match='state'):
        attempt(model,state,33)


@pytest.mark.parametrize('field,value', [('state','draft'),('suspect',True),('predecessor','r2'),('predecessor','none')])
def test_scope_inclusion_requires_mature_successor(model,field,value):
    state = prefix(model,36)
    state['items']['r3'][field] = value  # Lokalna wyrocznia, nie świadek osiągalności.
    before = deepcopy(state)
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,state,37)
    assert state == before


@pytest.mark.parametrize('actor', ['A','R'])
def test_scope_inclusion_requires_user(model,actor):
    state = prefix(model,36)
    event = dict(scenario()['events'][36],actor=actor)
    with pytest.raises(StepRejected,match='actor'):
        execute_step(model,state,event,{})


@pytest.mark.parametrize('release_state', ['ready','reviewed','accepted'])
def test_scope_inclusion_cannot_modify_frozen_release_states(model,release_state):
    state = prefix(model,36)
    state['releases'][1]['state'] = release_state  # Izolacja from; nie twierdzimy osiągalności.
    before = deepcopy(state)
    with pytest.raises(StepRejected,match='state'):
        attempt(model,state,37)
    assert state == before


def test_scope_keeps_predecessor_and_requires_evidence_and_dependencies_in_scope(model):
    state = prefix(model,36)
    event = deepcopy(scenario()['events'][36])
    event.pop('evidence')
    with pytest.raises(StepRejected,match='evidence'):
        execute_step(model,state,event,{})
    state['releases'][1]['scope'].remove('p1')
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,state,37)
    state = prefix(model,37)
    assert {'r1','r3'} <= set(state['releases'][1]['scope'])
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,state,37)


@pytest.mark.parametrize('state_name', ['verified','approved','baselined'])
def test_relink_requires_open_draft(model,state_name):
    state = prefix(model,41)
    state['items']['a1']['state'] = state_name
    with pytest.raises(StepRejected,match='state'):
        attempt(model,state,42)


@pytest.mark.parametrize('field,value', [('state','draft'),('suspect',True),('predecessor','r2')])
def test_relink_requires_correct_and_mature_successor(model,field,value):
    state = prefix(model,41)
    state['items']['r3'][field] = value
    before = deepcopy(state)
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,state,42)
    assert state == before


def test_relink_requires_scope_and_preserves_version_flags_and_other_edges(model):
    state = prefix(model,41)
    before = deepcopy(state)
    without_scope = deepcopy(state)
    without_scope['releases'][1]['scope'].remove('r3')
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,without_scope,42)
    # Dodatkowe dozwolone powiązanie tego samego typu nie może zniknąć.
    state['items']['a1']['depends_on'].append('r2')
    state['items']['c1']['suspect'] = False
    after = attempt(model,state,42)['after']
    assert set(after['items']['a1']['depends_on']) == {'r2','r3'}
    assert after['items']['a1']['version'] == before['items']['a1']['version'] == 2
    assert after['items']['a1']['suspect'] == before['items']['a1']['suspect']
    assert after['items']['c1']['suspect']
    assert state['items']['a1']['depends_on'] == ['r1','r2']


@pytest.mark.parametrize('old,new', [('missing','r3'),('r1','missing'),('r1','r1'),('r1','a1'),('r2','r3')])
def test_relink_bad_ids_and_edges_are_atomic(model,old,new):
    state = prefix(model,41)
    before = deepcopy(state)
    event = dict(scenario()['events'][41],old_dependency=old,new_dependency=new)
    with pytest.raises((InputError,StepRejected)):
        execute_step(model,state,event,{})
    assert state == before


@pytest.mark.parametrize('damage', ['duplicate','cycle','type'])
def test_relink_structural_validation_on_injected_graph(model,damage):
    state = prefix(model,41)
    if damage == 'duplicate':
        state['items']['a1']['depends_on'].append('r3')
    elif damage == 'cycle':
        state['items']['r3']['depends_on'] = ['a1']
    else:
        state['items']['r3']['type'] = 'DES'
    before = deepcopy(state)
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,state,42)
    assert state == before


def test_review_no_impact_blocks_reachable_S4_counterexample(model):
    state = prefix(model,28)
    opened = execute_step(model,state,dict(transition='T06',actor='U',item='d1'),{})['after']
    review = scenario()['events'][50]
    with pytest.raises(StepRejected,match='guard'):
        execute_step(model,opened,review,{})
    # Powrót do starego warunku musi ujawnić rzeczywiste naruszenie S4.
    transition(model,'T11')['guard'] = 'suspect and forall d in deps(e): d.state not in {superseded, withdrawn}'
    after = execute_step(model,opened,review,{})['after']
    assert after['items']['d1']['state']=='draft'
    assert after['items']['c1']['state']=='baselined' and not after['items']['c1']['suspect']


def test_review_no_impact_waits_for_dependency_review_even_if_baselined(model):
    state = prefix(model,32)
    with pytest.raises(StepRejected,match='guard'):
        attempt(model,state,51)
    state = prefix(model,50)
    assert attempt(model,state,51)['after']['items']['c1']['suspect'] is False


@pytest.mark.parametrize('index,field', [(33,'version'),(37,'current_release'),(42,'version')])
def test_runtime_failure_after_write_rolls_back_everything(model,index,field):
    state = prefix(model,index-1)
    before = deepcopy(state)
    ident = scenario()['events'][index-1]['transition']
    transition(model,ident)['effects'].append(f'{field} := tests_ok + 1')
    with pytest.raises(InputError):
        attempt(model,state,index)
    assert state == before


def test_version_boundary_does_not_partially_create_successor(model):
    state = prefix(model,32)
    before = deepcopy(state)
    transition(model,'T00')['effects'].append('version := 4')
    with pytest.raises(ExplorationBoundary):
        attempt(model,state,33)
    assert state == before


def test_declared_arguments_cannot_be_used_to_edit_other_transitions(model):
    state = prefix(model,41)
    with pytest.raises(InputError):
        execute_step(model,state,dict(transition='T13',actor='A',item='a1',predecessor='r2'),{})
    for missing in ('old_dependency','new_dependency'):
        event = deepcopy(scenario()['events'][41])
        event.pop(missing)
        with pytest.raises(InputError):
            execute_step(model,state,event,{})


def test_replacement_rules_are_not_dispatched_by_ids(model):
    data = scenario()
    mapping = {'T00':'NEW_ITEM','T14':'RELINK','W07':'INCLUDE','T11':'REVIEW'}
    for kind in ('item','question','release'):
        for t in model[f'{kind}_transitions']:
            t['id'] = mapping.get(t['id'],t['id'])
    for event in data['events']:
        event['transition'] = mapping.get(event['transition'],event['transition'])
    result = replay(model,data)
    assert result['outcome']=='completed',result['steps'][-1]


@given(maturity=st.sampled_from(['none','draft','verified','approved','baselined','superseded','withdrawn']),
       suspect=st.booleans(), owner=st.sampled_from(['A','U','R']))
def test_generated_dependency_review_matches_separate_oracle(maturity,suspect,owner):
    model = load_model(ROOT/'model/process.yaml')
    state = prefix(model,50)
    state['items']['d1'].update(state=maturity,suspect=suspect)
    event = dict(scenario()['events'][50],actor=owner)
    expected = owner=='A' and maturity in {'approved','baselined'} and not suspect
    try:
        result = execute_step(model,state,event,{})
    except StepRejected:
        assert not expected
    else:
        assert expected and not result['after']['items']['c1']['suspect']


def change_events(item, question='q3'):
    return [
        dict(transition='P00', actor='A', question=question,
             attributes=dict(kind='change', about=item, requested_transition='T05', blocking=True)),
        dict(transition='P01', actor='A', question=question),
        dict(transition='P02', actor='U', question=question,
             inputs=dict(unambiguous_answer=True, resolution='approved'),
             evidence=dict(simulation=True, decision='SIM-'+question, quote=f'Zgoda testowa: T05 {item} v1.')),
        dict(transition='T05', actor='U', item=item, question=question),
    ]


def test_impact_follows_current_graph_and_lineage_is_not_a_dependency(model):
    # Osiągalny stan: a1 już wskazuje r3, d1 nadal r1, c1 zależy od obu.
    state = prefix(model,45)
    for event in change_events('r3'):
        state = execute_step(model,state,event,scenario()['inputs'])['after']
    assert state['items']['a1']['suspect'] and state['items']['c1']['suspect']
    assert state['items']['r1']['suspect'] is False
    assert state['items']['r1']['state'] == 'superseded'
    assert state['items']['r2']['suspect'] is False and state['items']['a2']['suspect'] is False
    # d1 był już suspect przed zmianą. Test nie przypisuje tego skutku nowemu r3.


def test_replacement_after_acceptance_preserves_entire_old_release(model):
    data = scenario()
    tail = deepcopy(data['events'][28:])
    tail.insert(4, dict(transition='W06',actor='A'))
    for event in tail:
        if event['transition'] in {'W07','W04'}:
            event['evidence']['quote'] = event['evidence']['quote'].replace('wydania 1','wydania 2')
    data['events'] = scenario('wit1')['events'] + tail
    result = replay(model,data)
    assert result['outcome'] == 'completed', result['steps'][-1]
    assert len(result['steps']) == 56
    accepted = result['steps'][28]['after']['releases'][1]
    for step in result['steps'][29:]:
        assert step['after']['releases'][1] == accepted
    final = result['final_state']
    assert final['current_release'] == 2 and not final['next_release_required']
    assert final['releases'][2]['state'] == 'accepted'
    assert 'r3' not in accepted['scope'] and accepted['snapshot']['a1']['depends_on'] == ['r1']
    assert set(final['releases'][2]['scope']) == set(accepted['scope']) | {'r3'}
    assert final['releases'][2]['snapshot']['a1']['depends_on'] == ['r3']


@pytest.mark.parametrize('field', ['decision','reference'])
def test_relink_requires_record_and_review_reference(model,field):
    state = prefix(model,41)
    before = deepcopy(state)
    event = deepcopy(scenario()['events'][41])
    event['evidence'].pop(field)
    with pytest.raises(StepRejected,match='evidence'):
        execute_step(model,state,event,{})
    assert state == before


def test_wit3_safety_oracles_hold_at_each_step(model):
    # Niezależne wyrocznie śladu: nie wywołują parsera guard ani helperów wykonawcy.
    result = replay(model,scenario())
    assert result['outcome']=='completed'
    for step in result['steps']:
        before,after,event = step['before'],step['after'],step['event']
        for ident,item in after['items'].items():
            if item['state'] in {'verified','approved','baselined'} and not item['suspect']:
                assert all(after['items'][d]['state'] in {'approved','baselined'} for d in item['depends_on'])
            old = before['items'][ident]
            if item['depends_on'] != old['depends_on']:
                assert event['transition']=='T14' and old['state']=='draft'
                assert set(item['depends_on']) == set(old['depends_on']) - {event['old_dependency']} | {event['new_dependency']}
                assert {k:v for k,v in item.items() if k!='depends_on'} == {k:v for k,v in old.items() if k!='depends_on'}
            if item['predecessor'] != old['predecessor']:
                assert event['transition']=='T00' and old['state']=='none'
                predecessor=before['items'][item['predecessor']]
                assert predecessor['state']=='superseded' and predecessor['type']==item['type']
        for n,release in before['releases'].items():
            updated=after['releases'][n]
            if release['state']=='accepted':
                assert updated==release
            if release['scope']!=updated['scope']:
                assert event['transition']=='W07' and event['actor']=='U' and release['state']=='in_preparation'
                assert set(updated['scope']) == set(release['scope']) | {event['item']}
                assert {k:v for k,v in updated.items() if k!='scope'} == {k:v for k,v in release.items() if k!='scope'}
