"""Odtwarzalne luki v0.6 i eksperyment na proponowanej kopii, bez zmiany modelu.

Trace: S7a/S7b, L4, W01, W04. Nie stanowi przyjęcia propozycji v0.7.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from isomodel import load_model
from isomodel.execution import replay, initial_state, fingerprint, _context
from isomodel.expressions import compile_expression, evaluate
from isomodel.safety import safety_violations


def proposed_copy(model):
    candidate=deepcopy(model)
    proposal=yaml.safe_load((ROOT/'model/proposals/e2-hardening.yaml').read_text())
    for kind in ('item','release'):
        for ident,fields in proposal[kind+'_transitions'].items():
            target=next(t for t in candidate[kind+'_transitions'] if t['id']==ident)
            target.update(deepcopy(fields))
    candidate['post_step_effects']+=deepcopy(proposal['append_post_step_effects'])
    return candidate


def scenarios(model):
    wit=json.loads((ROOT/'tests/fixtures/wit1/scenario.json').read_text())
    events=wit['events']
    late=events[:28]+[dict(transition='P00',actor='R',question='late',attributes={'blocking':True}),events[28]]
    reject=[dict(transition='T00',actor='A',item='p1')]
    reject += [dict(transition='T01',actor='A',item='p1'),dict(transition='T03',actor='U',item='p1')]*2
    reject += [dict(transition='T09',actor='U',item='p1'),dict(transition='T10',actor='U',item='p1')]
    reject += [dict(transition='T01',actor='A',item='p1'),dict(transition='T03',actor='U',item='p1')]
    change=events[:28]+[
        dict(transition='P00',actor='A',question='q1',attributes=dict(kind='change',about='p1',requested_transition='T05',blocking=True)),
        dict(transition='P01',actor='A',question='q1'),
        dict(transition='P02',actor='U',question='q1',inputs=dict(unambiguous_answer=True,resolution='approved'),
             evidence=dict(simulation=True,decision='SIM-E2',quote='Zgoda testowa na T05 p1 v1.')),
        dict(transition='T05',actor='U',item='p1',question='q1'),events[28]]
    result=[]
    for ident,ev,alternative in [('late_blocker',late,False),('rejection_budget',reject,False),('external_scope_change',change,True)]:
        instance=deepcopy(model)
        if alternative: instance['test_instance']['release_scope'].remove('p1')
        result.append((instance,dict(wit,id=ident,events=ev),alternative))
    return result


def observations(model, result):
    state=result['final_state'];release=state['releases'][state['current_release']]
    steps=[s for s in result['steps'] if s['outcome']=='applied']
    counts={}
    for step in steps:
        e=step['event']
        if e['transition']=='T03':
            key=f"{e['item']}@{step['before']['items'][e['item']]['version']}"
            counts[key]=counts.get(key,0)+1
    return dict(outcome=result['outcome'],steps=len(result['steps']),last_code=result['steps'][-1].get('code'),
        release=release['state'],open_blocking=[q['id'] for q in state['questions'].values() if q['blocking'] and q['state'] in {'open','asked'}],
        rejection_events=counts,violations=safety_violations(model,steps))


def diagnostics(model=None):
    model=load_model(ROOT/'model/process.yaml') if model is None else model
    if model['version']!=0.6: raise ValueError('Diagnostyka historyczna wymaga v0.6')
    original=deepcopy(model);out=[]
    for instance,data,alternative in scenarios(model):
        baseline=replay(instance,data)
        proposed=proposed_copy(instance)
        trial=replay(proposed,data)
        out.append(dict(id=data['id'],alternative_scope=alternative,scenario=data,
            baseline=observations(instance,baseline),proposed=observations(instance,trial)))
    # Pusty zakres: wykonawca v0.6 jawnie go nie obsługuje. Oddzielnie badamy
    # dokładne drzewo wyrażenia; nie przedstawiamy go jako wykonanego wydania.
    empty=deepcopy(model);empty['test_instance']['release_scope']=[]
    state=initial_state(empty)
    unsupported=replay(empty,dict(id='empty_scope',simulation=True,inputs={'tests_ok':True},events=[dict(transition='W01',actor='A')]))
    predicate=[]
    for tests_ok,blocking in [(True,False),(False,False),(True,True)]:
        pre=deepcopy(state)
        if blocking:
            pre['questions']['q1']={'state':'open','blocking':True}
        values=[]
        for candidate in (empty,proposed_copy(empty)):
            rule=next(t for t in candidate['release_transitions'] if t['id']=='W01')
            values.append(evaluate(compile_expression(rule['guard'],candidate),*_context(candidate,pre,None,{'tests_ok':tests_ok})))
        predicate.append(dict(tests_ok=tests_ok,blocking=blocking,baseline=values[0],proposed=values[1]))
    assert model==original
    return dict(model_version=model['version'],model_sha256=fingerprint(model),status='requires_decision',
        cases=out,empty_scope=dict(runtime_outcome=unsupported['outcome'],runtime_code=unsupported['steps'][-1]['code'],
                                 predicate_only=predicate),
        limitations=['Propozycja nie zmienia obowiązującego modelu.',
          'Pusty zakres sprawdzono na predykacie; wykonawca nadal zwraca unsupported.',
          'Alternatywny zakres nie jest świadkiem stałej test_instance v0.6.'])


if __name__=='__main__':
    print(json.dumps(diagnostics(),ensure_ascii=False,indent=2))
