"""E3.4 — pełny krok otwarcia zmiany i odmowy bez skutków."""
from copy import deepcopy
from pathlib import Path
import json

from isomodel.tla_impact import render_probes
from isomodel.tlc import run_tlc

ROOT = Path(__file__).resolve().parents[1]


def test_change_requires_matching_unused_consent(model,tmp_path):
    seed=json.loads((ROOT/'docs/preparations/e3-04/expected-checkpoints.json').read_text())['checkpoints'][0]['state']
    seed['releases']={int(k):v for k,v in seed['releases'].items()}
    command=dict(operation=3,item='r1',question='q0',actor='U',checks=True,evidence=True,unambiguous=True,resolution='approved')
    expected=deepcopy(seed);expected['items']['r1'].update(state='draft',version=2,rejections=0,suspect=False)
    expected['questions']['q0']['consumed']=True
    for ident in ('d1','a1','c1'):expected['items'][ident]['suspect']=True
    cases=[dict(before=seed,command=command,expected=dict(world=expected,records=[]))]
    for field,value in [('state','asked'),('kind','general'),('resolution','rejected'),('about','r2'),('about_version',2),('requested_transition','T07'),('consumed',True)]:
        before=deepcopy(seed);before['questions']['q0'][field]=value
        cases.append(dict(before=before,command=command,expected=None))
    module,cfg=render_probes(model,cases)
    (tmp_path/'Impact.tla').write_text(module);(tmp_path/'Impact.cfg').write_text(cfg)
    pin=json.loads((ROOT/'tools/tla-toolchain.json').read_text())
    r=run_tlc(tmp_path/'Impact.tla',tmp_path/'Impact.cfg',tmp_path/'runs',java=pin['java_default'],jar=ROOT/pin['jar_default'],timeout=60)
    assert r['status']=='passed',r


def test_bound_candidate_is_observed_without_consuming_original(model):
    import sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from run_e3_impact import actual,load_oracle,event_for
    from isomodel.execution import execute_step,ExplorationBoundary
    from isomodel.tla_impact_graph import command,boundary
    import pytest
    world=load_oracle().initial_state();world['items']['r1']['version']=3;world['questions']['q0']['about_version']=3
    frozen=deepcopy(world);c=command(3,'r1','q0');event,inputs=event_for(c)
    with pytest.raises(ExplorationBoundary):execute_step(model,world,event,inputs)
    result=actual(model,world,c)
    assert world==frozen and not world['questions']['q0']['consumed']
    assert result['world']['items']['r1']['version']==4 and result['world']['questions']['q0']['consumed']
    assert boundary(result['world'],model['test_instance']['bounds'])=='version'


def test_history_is_specific_to_new_version(model,tmp_path):
    import sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from run_e3_impact import load_oracle,run_module
    from isomodel.tla_impact_graph import render_graph
    from argparse import Namespace
    oracle=load_oracle();t=next(t for t in model['item_transitions'] if t['id']=='T05');t['to']='approved'
    pin=json.loads((ROOT/'tools/tla-toolchain.json').read_text())
    args=Namespace(java=pin['java_default'],jar=ROOT/pin['jar_default'],timeout=60)
    for name in ('VerifiedHistory','ApprovedHistory'):
        result=run_module(render_graph(model,oracle.initial_state(),oracle.tla_oracle(),invariants=(name,)),tmp_path/name,args)
        assert result['status']=='invariant_violation' and result['invariant']==name,result


def test_compilation_cache_preserves_full_results(model):
    import sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from run_e3_impact import load_oracle,actual,event_for,executor,canonical
    from isomodel.execution import execute_step
    oracle=load_oracle();w=oracle.witness();engine=executor(model)
    for state,c,expected,records in zip(w['expected'],w['commands'],w['expected'][1:],w['records']):
        event,inputs=event_for(c);plain=execute_step(model,state,event,inputs)
        cached=actual(model,state,c,engine=engine)
        assert canonical(cached)==canonical(dict(world=plain['after'],records=plain['records']))==canonical(dict(world=expected,records=records))


def test_evidence_representative_matches_e2_field_requirements(model):
    import sys
    import pytest
    sys.path.insert(0,str(ROOT/'scripts'))
    from run_e3_impact import load_cases,event_for
    from isomodel.execution import execute_step,StepRejected
    cases={c['id']:c for c in load_cases().cases()}
    for ident,required in [('I02_positive',('decision','reference')),('A03_approved',('decision','quote'))]:
        case=cases[ident];event,inputs=event_for(case['command']);before=deepcopy(case['before'])
        for field in required:
            wrong=deepcopy(event);wrong['evidence'].pop(field)
            with pytest.raises(StepRejected,match='Brak '+field):execute_step(model,before,wrong,inputs)
            assert before==case['before']
        for change in ({'simulation':1},{'extra':'unknown'}):
            wrong=deepcopy(event);wrong['evidence'].update(change)
            with pytest.raises(StepRejected):execute_step(model,before,wrong,inputs)
            assert before==case['before']
        optional='quote' if ident.startswith('I02') else 'reference'
        event['evidence'].pop(optional)
        assert execute_step(model,before,event,inputs)['after']==case['expected']['world']


def test_impact_full_runner(tmp_path):
    import subprocess
    import sys
    out=tmp_path/'complete'
    process=subprocess.run([sys.executable,str(ROOT/'scripts/run_e3_impact.py'),'--output',str(out)],cwd=ROOT,capture_output=True,text=True,timeout=600)
    assert process.returncode==0,process.stdout+process.stderr
    r=json.loads((out/'evidence.json').read_text())
    assert r['status']=='checks_passed_not_stage_acceptance'
    assert r['baseline']['matched'] and r['baseline']['same_state_set']
    assert r['baseline']['python']['distinct_states']==19797
    assert len(r['controls'])==3 and all(c['matched'] for c in r['controls'])
    assert r['matrix']['case_count']==58 and r['matrix']['matched']
    assert len(r['invalid_inputs'])==2 and all(c['matched'] for c in r['invalid_inputs'])
    assert len(r['release_prefixes'])==12 and all(c['matched'] for c in r['release_prefixes'])
    assert len(r['pending_refusals'])==3 and all(c['matched'] for c in r['pending_refusals'])
    assert len(r['mutants'])==34 and all(c['matched'] for c in r['mutants'])
    assert len(r['monitors'])==3 and all(c['matched'] and c['counterexample_confirmed'] for c in r['monitors'])
    assert len(r['boundaries']['original_limit_probes'])==2
    assert all(c['matched'] for c in r['boundaries']['original_limit_probes'])
    assert r['witness']['matched'] and len(r['witness']['expected'])==14
    assert r['source_files'] and (out/'report.md').is_file()


def test_runner_does_not_count_tool_failure_as_counterexample():
    import sys
    sys.path.insert(0,str(ROOT/'scripts'))
    from run_e3_impact import exit_code
    for status,code in [('tool_error',2),('timeout',3),('invariant_violation',1)]:
        assert exit_code(dict(status='verification_failed',probe=dict(status=status,toolchain={})))==code
