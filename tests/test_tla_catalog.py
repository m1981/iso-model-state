"""E3.3: badanie pełnego katalogu z dwiema aktywnymi pozycjami."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from isomodel.tla_catalog import render_catalog, validate_command
from isomodel.tla_projection import ProjectionError


@pytest.mark.parametrize('field,value', [('evidence','false'), ('checks',1), ('operation',True), ('item','r2'), ('actor','unknown'), ('predecessor','p1')])
def test_invalid_catalog_command_refused(model, field, value):
    command = dict(operation=0, item='r1', actor='A', checks=True, evidence=False)
    command[field] = value
    with pytest.raises(ProjectionError):
        validate_command(model, command)


@pytest.mark.parametrize('fault', ['topology_effect', 'unknown_guard', 'argument_default', 'unknown_evidence'])
def test_unsupported_catalog_semantics_refused(model, fault):
    from run_e3_catalog import load_oracle
    oracle = load_oracle(); seed = oracle.initial_items()
    t = model['item_transitions'][0]
    if fault == 'topology_effect': t['effects'].append('depends_on := {}')
    elif fault == 'unknown_guard': t['guard'] = 'false and in_scope(e)'
    elif fault == 'argument_default': t['arguments']['predecessor']['default'] = 'p1'
    else: model['item_transitions'][4]['evidence'] = 'unknown'
    with pytest.raises(ProjectionError):
        render_catalog(model, seed, oracle.tla_oracle())


def test_catalog_command_reproduces_all_evidence(tmp_path):
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/run_e3_catalog.py'), '--output', str(tmp_path)],
                       cwd=ROOT, capture_output=True, text=True, timeout=600)
    assert p.returncode == 0, p.stdout + p.stderr
    r = json.loads((tmp_path / 'evidence.json').read_text())
    assert r['status'] == 'checks_passed_not_stage_acceptance'
    assert r['baseline']['same_state_set'] and r['baseline']['matched']
    assert len(r['controls']) == 3 and all(p['matched'] for p in r['controls'])
    assert len(r['negative_contexts']) == 2 and all(p['matched'] for p in r['negative_contexts'])
    assert len(r['monitors']) == 2 and all(p['matched'] for p in r['monitors'])
    assert len(r['mutants']) == 8 and all(p['matched'] and p['witness']['matched'] for p in r['mutants'])
    assert r['witness']['matched'] and r['witness']['tlc']['distinct_states'] == 9
    assert all(p['matched'] for p in r['refusals']) and len(r['refusals']) == 2
    assert r['witness']['expected'][-1]['p1']['state'] == 'baselined'
    assert r['witness']['expected'][-1]['r1']['state'] == 'baselined'


def test_help_and_missing_tool(tmp_path):
    script = ROOT / 'scripts/run_e3_catalog.py'
    p = subprocess.run([sys.executable,str(script),'--help'],capture_output=True,text=True)
    assert p.returncode == 0 and '--java' in p.stdout
    p = subprocess.run([sys.executable,str(script),'--jar',str(tmp_path/'missing'),'--output',str(tmp_path/'out')],capture_output=True,text=True)
    assert p.returncode == 2 and 'JAR' in p.stderr


@pytest.mark.parametrize('fault', ['missing_arguments','missing_default'])
def test_create_binding_must_be_declared(model,fault):
    from run_e3_catalog import load_oracle
    oracle=load_oracle()
    if fault=='missing_arguments': del model['item_transitions'][0]['arguments']
    else: del model['item_transitions'][0]['arguments']['predecessor']['default']
    with pytest.raises(ProjectionError):
        render_catalog(model,oracle.initial_items(),oracle.tla_oracle())


def test_baseline_evidence_rejects_malformed_records(model):
    from run_e3_catalog import load_oracle
    from isomodel.execution import initial_state,execute_step,StepRejected
    state=initial_state(model);state['items']=load_oracle().witness()['expected'][4]
    good=dict(simulation=True,reference='SIM',quote='Demonstracja')
    bad=[good|{'simulation':1},good|{'extra':True},good|{'reference':''},good|{'quote':''}]
    bad += [{k:v for k,v in good.items() if k!='reference'}, {k:v for k,v in good.items() if k!='quote'}]
    for evidence in bad:
        with pytest.raises(StepRejected) as error:
            execute_step(model,state,dict(transition='T04',item='p1',actor='U',evidence=evidence),{})
        assert error.value.code=='evidence'


def test_history_does_not_infer_approval_from_a_mutated_create(model,tmp_path):
    from argparse import Namespace
    from run_e3_catalog import load_oracle,run_module
    oracle=load_oracle();model['item_transitions'][0]['to']='approved'
    module,cfg=render_catalog(model,oracle.initial_items(),oracle.tla_oracle())
    cfg='\n'.join(line for line in cfg.splitlines() if not line.startswith('INVARIANT ') or line=='INVARIANT ApprovedHistory')+'\n'
    result=run_module((module,cfg),tmp_path,Namespace(java='/Applications/PyCharm.app/Contents/jbr/Contents/Home/bin/java',jar=ROOT/'artifacts/tools/tla/1.7.4/tla2tools.jar',timeout=60))
    assert result['status']=='invariant_violation' and result['invariant']=='ApprovedHistory',result
