"""E3.2: kryteria realnego badania wielokrokowego, przed implementacją."""
from copy import deepcopy
import sys
from pathlib import Path

import pytest

from isomodel.tla_projection import ProjectionError, compile_action
from isomodel.tla_loop import render_loop, parse_dump

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def test_context_required_for_global_guard(model):
    with pytest.raises(ProjectionError):
        compile_action(model, 'T01')


@pytest.mark.parametrize('change', ['unknown_evidence', 'global_effect', 'unknown_guard'])
def test_unsupported_loop_semantics_rejected(model, change):
    from run_e3_loop import load_oracle, oracle_table
    context = load_oracle().contexts()[0]
    if change == 'unknown_evidence':
        model['item_transitions'][2]['evidence'] = 'unknown evidence'
    elif change == 'global_effect':
        model['item_transitions'][1]['effects'] = ['invalidate_release(e)']
    else:
        model['item_transitions'][1]['guard'] = 'false and in_scope(e)'
    with pytest.raises(ProjectionError):
        render_loop(model, context, **oracle_table(context))


def test_dump_parser_refuses_incomplete_or_unknown_data():
    with pytest.raises(ValueError):
        parse_dump('State 1:\n/\\ depth = 0\n')


def test_bounded_graphs_mutants_and_executed_paths(tmp_path):
    # Osobne wykonanie komendy także obejmuje generator i rzeczywiste TLC.
    import json
    import subprocess
    import sys
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/run_e3_loop.py'), '--output', str(tmp_path)],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, p.stdout + p.stderr
    result = json.loads((tmp_path / 'evidence.json').read_text())
    assert result['status'] == 'checks_passed_not_stage_acceptance'
    assert len(result['contexts']) == 8
    assert all(p['matched'] and p['same_state_set'] for p in result['contexts'])
    assert len(result['controls']) == 3 and all(p['matched'] for p in result['controls'])
    assert len(result['mutants']) == 8
    assert all(p['matched'] and p['witness']['matched'] for p in result['mutants'])
    witness = result['acceptance_witness']
    assert witness['matched'] and witness['tlc']['distinct_states'] == 7
    assert witness['expected'][-1]['state'] == 'approved'
    assert witness['expected'][-1]['rejections'] == 2


def test_oracle_independence_and_model_immutability(model):
    from run_e3_loop import load_oracle, oracle_table
    oracle = load_oracle()
    c = oracle.contexts()[0]
    original = deepcopy(model)
    table = oracle_table(c)
    module, cfg = render_loop(model, c, **table)
    assert model == original
    assert 'CONSTRAINT' not in cfg
    assert 'Expected' not in module.split('RawAction')[0]  # reguły przed tablicą wyroczni


def test_missing_tool_and_help(tmp_path):
    import subprocess
    import sys
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/run_e3_loop.py'), '--help'], capture_output=True, text=True)
    assert p.returncode == 0 and '--java' in p.stdout
    p = subprocess.run([sys.executable, str(ROOT / 'scripts/run_e3_loop.py'), '--jar', str(tmp_path / 'missing'), '--output', str(tmp_path / 'out')], capture_output=True, text=True)
    assert p.returncode == 2 and 'JAR' in p.stderr
    assert not (tmp_path / 'out/evidence.json').exists()


def test_history_monitors_have_their_own_counterexamples(model, tmp_path):
    from argparse import Namespace
    from run_e3_loop import history_probes, load_oracle
    result = history_probes(model, load_oracle().contexts(), tmp_path,
                           Namespace(java='/Applications/PyCharm.app/Contents/jbr/Contents/Home/bin/java',
                                     jar=ROOT / 'artifacts/tools/tla/1.7.4/tla2tools.jar', timeout=60))
    assert {p['tlc']['invariant'] for p in result} == {'HistoryBudget', 'CounterHistory', 'VerifiedHistory'}
    assert all(p['matched'] for p in result)


@pytest.mark.parametrize('fault', ['missing_dependencies', 'bool_budget', 'text_evidence', 'text_checks', 'bool_operation'])
def test_invalid_context_and_commands_are_refused_before_execution(model, fault):
    from run_e3_loop import load_oracle, oracle_table, actual_step
    c = load_oracle().contexts()[0]
    table = oracle_table(c)
    if fault == 'missing_dependencies':
        del c['dependencies']
    elif fault == 'bool_budget':
        c['budget'] = True
    else:
        cmd = dict(operation=2, actor='U', checks=True, evidence=True)
        cmd[{'text_evidence': 'evidence', 'text_checks': 'checks', 'bool_operation': 'operation'}[fault]] = True if fault == 'bool_operation' else 'false'
        with pytest.raises(ProjectionError):
            actual_step(model, c, c['item'] | {'state': 'verified'}, cmd, ('T01','T02','T03'))
        table['commands'][0] = cmd
    with pytest.raises(ProjectionError):
        render_loop(model, c, **table)


def test_evidence_abstraction_does_not_represent_malformed_records(model):
    from run_e3_loop import load_oracle, global_state
    from isomodel.execution import execute_step, StepRejected
    c = load_oracle().contexts()[0]
    for transition, actor, state in [('T01','A','draft'), ('T02','U','verified')]:
        before = global_state(model, c, c['item'] | {'state': state})
        malformed = [{'simulation':False,'decision':'SIM','quote':'x'},
                     {'simulation':True,'decision':'SIM','quote':'x','extra':True}]
        # T01 nie wymaga quote; pusty cytat jest błędem dopiero dla T02.
        if transition == 'T02':
            malformed.append({'simulation':True,'decision':'SIM','quote':''})
        for bad in malformed:
            with pytest.raises(StepRejected) as error:
                execute_step(model, before, dict(transition=transition, actor=actor, item='r1', evidence=bad), {'checks_ok':{'r1':True}})
            assert error.value.code == 'evidence'


def test_changed_sources_invalidate_run(monkeypatch):
    import run_e3_loop as runner
    monkeypatch.setattr(runner, 'source_manifest', lambda: {'source': 'changed'}, raising=False)
    with pytest.raises(ValueError, match='źród'):
        runner.verify_sources({'source': 'before'})
