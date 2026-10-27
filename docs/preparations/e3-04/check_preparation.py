#!/usr/bin/env python3
"""Odtwórz sprawdzenie przygotowania E3.4 istniejącym E2; bez generatora/TLC."""
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from isomodel import load_model
from isomodel.execution import execute_step, replay, StepRejected, fingerprint


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True))


def sources():
    paths = [ROOT/'model/process.yaml', Path(__file__), *(HERE/name for name in ('scenario.json','expected-checkpoints.json','refusals.json')),
             *sorted((ROOT/'src/isomodel').glob('*.py'))]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify():
    before_sources = sources()
    model = load_model(ROOT/'model/process.yaml')
    scenario = json.loads((HERE/'scenario.json').read_text())
    expected = json.loads((HERE/'expected-checkpoints.json').read_text())['checkpoints']
    refusals = json.loads((HERE/'refusals.json').read_text())
    trace = replay(model, scenario)
    assert trace['outcome'] == 'completed' and len(trace['steps']) == 42, trace['outcome']
    for checkpoint in expected:
        step = trace['steps'][checkpoint['after_step']-1]
        assert canonical(step['after']) == checkpoint['state'], checkpoint['after_step']
        assert canonical(step['records']) == checkpoint['records'], checkpoint['after_step']
    observed = []
    for probe in refusals:
        state = deepcopy(trace['steps'][probe['after_step']-1]['after']); frozen = deepcopy(state)
        try:
            execute_step(model, state, probe['event'], scenario['inputs'])
        except StepRejected as error:
            assert error.code == probe['expected_code'], (probe, error.code)
            observed.append(probe | {'observed_code': error.code, 'unchanged': state == frozen})
        else:
            raise AssertionError(('Próba nie została odmówiona', probe))
        assert state == frozen
    # I03 ma własny osiągalny prefiks: c1 utworzone, jeszcze nieweryfikowane.
    draft_scenario = deepcopy(scenario)
    draft_scenario['events'] = scenario['events'][:24] + scenario['events'][26:30]
    draft_trace = replay(model, draft_scenario)
    assert draft_trace['outcome'] == 'completed' and len(draft_trace['steps']) == 28
    draft = draft_trace['final_state']
    assert draft['items']['c1']['state'] == 'draft' and draft['items']['c1']['suspect']
    fix = {'transition':'T13', 'actor':'A', 'item':'c1'}
    verify_code = {'transition':'T01', 'actor':'A', 'item':'c1'}
    fixed = execute_step(model, draft, fix, scenario['inputs'])
    allowed = execute_step(model, fixed['after'], verify_code, scenario['inputs'])
    assert allowed['after']['items']['c1']['state'] == 'verified'
    assert all(allowed['after']['items'][i]['state'] == 'baselined' and allowed['after']['items'][i]['suspect'] for i in ('d1','a1'))
    alternative = deepcopy(draft); alternative_steps = []
    for event in scenario['events'][34:38]:  # T12/P01/P02/T05 dla a1.
        result = execute_step(model, alternative, event, scenario['inputs'])
        alternative_steps.append(result); alternative = result['after']
    fixed_alternative = execute_step(model, alternative, fix, scenario['inputs'])
    frozen = deepcopy(fixed_alternative['after'])
    try:
        execute_step(model, fixed_alternative['after'], verify_code, scenario['inputs'])
    except StepRejected as error:
        assert error.code == 'guard'
        blocked = {'event': verify_code, 'code': error.code, 'before': frozen, 'after': deepcopy(frozen)}
    else:
        raise AssertionError('T01(c1) nie odrzuciło bezpośredniej zależności draft')
    assert fixed_alternative['after'] == frozen
    assert sources() == before_sources, 'Źródła zmieniły się podczas sprawdzenia'
    return {'status':'preparation_checked_not_e34_verification', 'source_files':before_sources,
            'source_sha256':fingerprint(before_sources), 'model_sha256':trace['model_sha256'],
            'steps':42, 'full_checkpoints':len(expected), 'refusals':observed,
            'i03':{'mature_but_suspect_dependencies':'applied', 'draft_dependency':'guard'},
            'trace':trace, 'i03_traces':{'prefix':draft_trace,'fixed':fixed,'allowed':allowed,
                                      'alternative':alternative_steps,'fixed_alternative':fixed_alternative,'blocked':blocked}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Nowy lub pusty katalog; nie nadpisuje dowodów')
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('Wybierz nowy albo pusty katalog wyniku')
    result = verify()
    args.output.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(result, ensure_ascii=False, indent=2).encode()+b'\n'
    archive = gzip.compress(raw, mtime=0)
    (args.output/'evidence.json.gz').write_bytes(archive)
    summary = {k:v for k,v in result.items() if k not in ('trace','i03_traces')}
    summary['archive_sha256'] = hashlib.sha256(archive).hexdigest()
    summary['uncompressed_sha256'] = hashlib.sha256(raw).hexdigest()
    (args.output/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print('OK: 42 kroki, 14 pełnych punktów kontrolnych, 5 odmów, oba warianty I03. To przygotowanie, bez TLC E3.4.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
