"""Zestawienie rzeczywiście wykonanych świadków i niezależnych wyroczni E2.

Trace: G0–G6, S1–S13. Raport skończonego badania, nie dowód TLC.
"""
from copy import deepcopy
import json
from pathlib import Path

from .execution import execute_step, initial_state, replay, StepRejected
from .loader import ModelError, validate_model
from .graph import unreachable_states, dead_ends, completeness_matrix, iso_coverage
from .safety import safety_violations
from .probes import gate_probes

SAFETY_IDS = ['S1','S2','S3','S4','S5','S6','S7a','S7b','S8','S9','S10','S11','S12','S13']


def _mutate(model, case):
    mutant=deepcopy(model)
    if 'model_path' in case:
        node=mutant
        for key in case['model_path'][:-1]:
            node=node[key]
        node[case['model_path'][-1]]=deepcopy(case['replacement'])
    else:
        definition=next(t for kind in ('item','question','release') for t in mutant[kind+'_transitions']
                        if t['id']==case['attempt']['transition'])
        definition[case['field']]=deepcopy(case['replacement'])
    return mutant


def safety_evidence(model, root):
    """Każdy mutant ma osiągalny prefiks; błędy wykonania nie są zabiciem."""
    root=Path(root)
    witnesses=[]; mutations=[]
    for name in ('wit1','wit2','wit3','wit4','wit5'):
        data=json.loads((root/f'tests/fixtures/{name}/scenario.json').read_text())
        result=replay(model,data)
        if result['outcome']!='completed':
            raise ValueError(f'{name}: niewykonany świadek: {result["steps"][-1]}')
        witnesses.append(dict(id=name.upper(), steps=len(result['steps']), violations=safety_violations(model,result['steps'])))
        cases=json.loads((root/f'mutants/{name}_gates.json').read_text())
        gates=gate_probes(model,data,cases)
        for case,gate in zip(cases,gates,strict=True):
            state=initial_state(model);steps=[]
            for event in data['events'][:case['prefix_steps']]+case.get('setup_events',[]):
                step=execute_step(model,state,event,data['inputs']);steps.append(step);state=step['after']
            base_violations=safety_violations(model,steps)
            baseline_steps=steps[:]
            try:
                baseline_steps.append(execute_step(model,state,case['attempt'],data['inputs']))
            except StepRejected:
                pass
            baseline_violations=safety_violations(model,baseline_steps)
            mutant=_mutate(model,case)
            applied=False; failure=None;violations=[]
            try:
                mutated_step=execute_step(mutant,state,case['attempt'],data['inputs'])
                applied=True
                violations=safety_violations(model,steps+[mutated_step])
            except ModelError as error:
                failure=f'{type(error).__name__}: {error}'
            expected=[p for p in case['property'].split('/') if p in SAFETY_IDS]
            detected={v['property'] for v in violations}
            killed=[p for p in expected if p in detected and applied and not base_violations and not baseline_violations]
            mutations.append(dict(scenario=name.upper(),id=case['id'],gate_detected=gate['detected'],
                expected_safety=expected,mutant_applied=applied,oracle_detected=killed,
                baseline_violations=base_violations+baseline_violations,violations=violations,error=failure))
    covered={p:[m['id'] for m in mutations if p in m['oracle_detected']] for p in SAFETY_IDS}
    return dict(witnesses=witnesses,mutations=mutations,properties=covered,
                missing=[p for p,ids in covered.items() if not ids],exhaustive=False)


def structural_evidence(model):
    """Kontrole struktury; G1/G3 z grafu są tylko projekcjami bez warunków."""
    validate_model(model)
    results={}
    for prop,kind,field,value in [('G0','item','from',['misspelled_state']),('G4','item','to',['draft','verified'])]:
        mutant=deepcopy(model);mutant[kind+'_transitions'][0][field]=value
        try:
            validate_model(mutant)
        except ModelError:
            results[prop]={'baseline':True,'mutant_detected':True}
        else:
            results[prop]={'baseline':True,'mutant_detected':False}
    for prop,removed,check in [('G1',{'T02'},unreachable_states),('G3',{'T07','T08','T10'},dead_ends)]:
        mutant=deepcopy(model)
        mutant['item_transitions']=[t for t in mutant['item_transitions'] if t['id'] not in removed]
        results[prop]={'baseline':all(not check(model,k) for k in ('item','question','release')),
                       'mutant_detected':bool(check(mutant,'item')),'scope':'graph_projection'}
    mutant=deepcopy(model);mutant['release_transitions']=[t for t in mutant['release_transitions'] if t['id']!='W04']
    iso=iso_coverage(model)
    results['G6']={'baseline':not iso['missing_outcomes'] and not iso['missing_transition_iso'],
                   'mutant_detected':'PM.O2' in iso_coverage(mutant)['missing_outcomes'],'coverage':iso}
    results['G5']={'kind':'report_not_test','pairs':{k:len(completeness_matrix(model,k)) for k in ('item','question','release')}}
    return results
