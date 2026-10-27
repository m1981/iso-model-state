#!/usr/bin/env python3
"""E3.2: odtwarzalne ograniczone badanie wielu kroków, bez odbioru etapu."""
import argparse
from collections import deque
from copy import deepcopy
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from isomodel import load_model
from isomodel.execution import StepRejected, execute_step, initial_state, fingerprint
from isomodel.tla_loop import render_loop, render_path, parse_dump, validate_context, validate_command
from isomodel.tlc import ToolchainError, run_tlc, toolchain_info

TRANSITIONS = ('T01', 'T02', 'T03')


def load_oracle():
    spec = importlib.util.spec_from_file_location('loop_oracle', ROOT / 'tests/fixtures/e3/loop_oracle.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def commands():
    return [dict(operation=o, actor=a, checks=c, evidence=e)
            for o, a, c, e in product((1, 2, 3), ('A', 'R', 'U'), (False, True), (False, True))]


def state_key(state):
    # depends_on jest zbiorem w modelu; kolejność listy Pythona nie jest stanem.
    normalized = deepcopy(state)
    normalized['item']['depends_on'] = sorted(normalized['item']['depends_on'])
    return fingerprint(normalized)


def oracle_table(context):
    oracle = load_oracle(); states = oracle.domain(context); cs = commands()
    targets = []
    for state in states:
        row = []
        for c in cs:
            after = oracle.oracle_step(context, state, **c)
            row.append(0 if after is None else states.index(after) + 1)
        targets.append(row)
    return dict(states=states, targets=targets, commands=cs)


def global_state(model, context, item):
    state = initial_state(model)
    for d in context['dependencies']:
        state['items'][d['id']] = deepcopy(d)
    state['items'][item['id']] = deepcopy(item)
    return state


def actual_step(model, context, before, command, transitions):
    validate_context(model, context)
    validate_command(model, command)
    state = global_state(model, context, before)
    frozen = deepcopy(state)
    event = {'transition': transitions[command['operation'] - 1], 'actor': command['actor'], 'item': before['id']}
    if command['evidence']:
        event['evidence'] = {'simulation': True, 'decision': 'DEC-SIM-LOOP', 'quote': 'Demonstracyjna zgoda w badaniu E3.2'}
    try:
        result = execute_step(model, state, event, {'checks_ok': {before['id']: command['checks']}})
    except StepRejected:
        assert state == frozen
        return None
    assert state == frozen
    after = deepcopy(result['after']); item = after['items'][before['id']]
    after['items'][before['id']] = deepcopy(before)
    if after != frozen:
        raise ValueError('Naruszenie globalnej ramy: kontekst wymaga rozszerzenia mapowania.')
    return item


def python_graph(model, context, transitions=TRANSITIONS):
    oracle = load_oracle()
    init = dict(item=deepcopy(context['item']), depth=0, used=0, seen=False, ok=True)
    reached = {fingerprint(init): init}; pending = deque([init]); differences = []; edges = 0
    while pending:
        before = pending.popleft()
        if before['depth'] == 8:
            continue
        for c in commands():
            expected = oracle.oracle_step(context, before['item'], **c)
            after = actual_step(model, context, before['item'], c, transitions)
            if after != expected:
                differences.append({'before': before, 'command': c, 'expected': expected, 'actual': after})
            if after is None:
                continue
            edges += 1
            node = dict(item=after, depth=before['depth'] + 1,
                        used=before['used'] + (c['operation'] == 3),
                        seen=before['seen'] or after['state'] == 'verified', ok=after == expected)
            ident = fingerprint(node)
            if ident not in reached:
                reached[ident] = node; pending.append(node)
    return {'states': list(reached.values()), 'allowed_input_edges': edges, 'differences': differences}


def run_module(module_config, directory, args):
    directory.mkdir(parents=True, exist_ok=True)
    module, cfg = directory / 'Loop.tla', directory / 'Loop.cfg'
    module.write_text(module_config[0]); cfg.write_text(module_config[1])
    return run_tlc(module, cfg, directory / 'runs', java=args.java, jar=args.jar, timeout=args.timeout)


def graph_probe(model, context, directory, args, transitions=TRANSITIONS, violation=None):
    table = oracle_table(context)
    result = run_module(render_loop(model, context, transitions=transitions, **table), directory, args)
    py = python_graph(model, context, transitions)
    matched = result['status'] == ('invariant_violation' if violation else 'passed')
    same = False
    if violation:
        matched &= result['invariant'] == violation and bool(py['differences'])
    elif result['status'] == 'passed':
        observed = parse_dump(Path(result['states_file']).read_text())
        same = {state_key(s) for s in observed} == {state_key(s) for s in py['states']}
        matched &= same and not py['differences'] and len(observed) == result['distinct_states']
    return {'id': context['id'], 'context': context, 'transitions': transitions, 'model_sha256': fingerprint(model),
            'tlc': result, 'python': py, 'matched': bool(matched), 'same_state_set': same}


def path_probe(model, context, inputs, expected, directory, args):
    result = run_module(render_path(model, context, inputs, expected), directory, args)
    py = [deepcopy(context['item'])]
    for c in inputs:
        after = actual_step(model, context, py[-1], c, TRANSITIONS)
        if after is None:
            break
        py.append(after)
    matched = result['status'] == 'passed' and py == expected and result.get('distinct_states') == len(expected)
    if result['status'] == 'passed':
        observed = sorted(parse_dump(Path(result['states_file']).read_text()), key=lambda s: s['depth'])
        matched &= [state_key(s) for s in observed] == [state_key(dict(depth=i, item=s)) for i, s in enumerate(expected)]
    return {'tlc': result, 'inputs': inputs, 'expected': expected, 'python': py, 'matched': bool(matched)}


def mutant_cases(model, contexts):
    by_id = {c['id']: c for c in contexts}
    for name in ('dependency', 'checks', 'suspect', 'verification', 'actor', 'evidence', 'budget', 'reset'):
        m = deepcopy(model)
        ts = {t['id']: t for t in m['item_transitions']}
        c = deepcopy(by_id['req_approved'])
        inputs = [dict(operation=1, actor='A', checks=True, evidence=False)]
        pairs = [('draft', 0), ('verified', 0)]
        violation = 'Availability'
        if name == 'dependency':
            c = deepcopy(by_id['code_mixed'])
            ts['T01']['guard'] = 'not suspect and checks_ok(e)'
        elif name == 'checks':
            ts['T01']['guard'] = 'not suspect and forall d in deps(e): d.state in {approved, baselined}'
            inputs[0]['checks'] = False
        elif name == 'suspect':
            c = deepcopy(by_id['req_suspect'])
            ts['T01']['guard'] = 'checks_ok(e) and forall d in deps(e): d.state in {approved, baselined}'
        elif name == 'verification':
            ts['T02']['from'] = ['draft']
            inputs = [dict(operation=2, actor='U', checks=False, evidence=True)]
            pairs = [('draft', 0), ('approved', 0)]
        elif name in ('actor', 'evidence'):
            if name == 'actor': ts['T02']['actor'] = 'A'
            else: del ts['T02']['evidence']
            inputs.append(dict(operation=2, actor='A' if name == 'actor' else 'U', checks=False, evidence=name == 'actor'))
            pairs.append(('approved', 0))
        elif name == 'budget':
            ts['T03']['guard'] = 'true'
            inputs = [dict(operation=o, actor='A' if o == 1 else 'U', checks=o == 1, evidence=False) for o in (1,3,1,3,1,3)]
            pairs = [('draft',0), ('verified',0), ('draft',1), ('verified',1), ('draft',2), ('verified',2), ('draft',3)]
        else:
            ts['T01']['effects'] = ['rejections := 0']; violation = 'Successor'
            inputs += [dict(operation=3, actor='U', checks=False, evidence=False), dict(operation=1, actor='A', checks=True, evidence=False)]
            pairs += [('draft',1), ('verified',0)]
        expected = [deepcopy(c['item']) | {'state': s, 'rejections': n} for s, n in pairs]
        yield name, m, c, violation, inputs, expected


def history_probes(model, contexts, out, args):
    # Sprawdzamy każdy monitor osobno: wcześniejsza wyrocznia nie może go maskować.
    names = {'budget': 'HistoryBudget', 'reset': 'CounterHistory', 'verification': 'VerifiedHistory'}
    results = []
    for name, m, c, _, _, _ in mutant_cases(model, contexts):
        if name not in names:
            continue
        monitor = names[name]
        module, cfg = render_loop(m, c, **oracle_table(c))
        cfg = '\n'.join(line for line in cfg.splitlines() if not line.startswith('INVARIANT ') or line == 'INVARIANT ' + monitor) + '\n'
        result = run_module((module, cfg), out / monitor, args)
        results.append({'id': name, 'monitor': monitor, 'model_sha256': fingerprint(m), 'tlc': result,
                        'matched': result['status'] == 'invariant_violation' and result['invariant'] == monitor})
    return results


def source_manifest():
    paths = [ROOT / 'model/process.yaml', ROOT / 'docs/E3-02-MAPOWANIE.md', ROOT / 'docs/E3-02-WYROCZNIA.md',
             ROOT / 'tools/tla-toolchain.json', Path(__file__).resolve(), ROOT / 'tests/fixtures/e3/loop_oracle.py',
             ROOT / 'tests/test_tla_loop.py', ROOT / 'pyproject.toml', ROOT / 'uv.lock',
             *sorted((ROOT / 'src/isomodel').glob('*.py'))]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def verify_sources(before):
    if source_manifest() != before:
        raise ValueError('Zmieniono źródła podczas badania; wynik nie może zostać przypisany do tej wersji. Powtórz w nowym katalogu po zakończeniu edycji.')


def build(args):
    sources = source_manifest()
    info = toolchain_info(args.java, args.jar)
    out = Path(args.output).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Katalog wyniku musi być nowy albo pusty; zachowaj wcześniejsze dowody.')
    out.mkdir(parents=True, exist_ok=True)
    model = load_model(ROOT / 'model/process.yaml'); oracle = load_oracle(); cs = oracle.contexts()
    baseline = [graph_probe(model, c, out / c['id'], args) for c in cs]
    controls = []
    for kind in ('renamed', 'limit', 'approval_metadata'):
        m, c = deepcopy(model), deepcopy(cs[0]); transitions = TRANSITIONS
        if kind == 'renamed':
            transitions = ('RENAMED_VERIFY', 'RENAMED_APPROVE', 'RENAMED_REJECT')
            for old, new in zip(TRANSITIONS, transitions):
                next(t for t in m['item_transitions'] if t['id'] == old)['id'] = new
        elif kind == 'limit':
            m['parameters']['MAX_REJECTIONS'] = c['budget'] = 1
        else:
            c = deepcopy(next(c for c in cs if c['id'] == 'des_no_approval'))
            m['item_types']['DES']['requires_approval'] = c['requires_approval'] = True
        p = graph_probe(m, c, out / 'controls' / kind, args, transitions); p['id'] = kind; controls.append(p)
    mutants = []
    for name, m, c, violation, inputs, expected in mutant_cases(model, cs):
        p = graph_probe(m, c, out / 'mutants' / name, args, violation=violation)
        p['id'] = name; p['expected_violation'] = violation
        p['witness'] = path_probe(m, c, inputs, expected, out / 'mutants' / name / 'witness', args)
        p['matched'] &= p['witness']['matched']; mutants.append(p)
    w = oracle.witness(); context = next(c for c in cs if c['id'] == w['context_id'])
    witness = path_probe(model, context, w['inputs'], w['expected'], out / 'acceptance_witness', args)
    history = history_probes(model, cs, out / 'history', args)
    verify_sources(sources)
    matched = all(p['matched'] for p in baseline + controls + mutants + history + [witness])
    return {'status': 'checks_passed_not_stage_acceptance' if matched else 'verification_failed',
            'scope': 'synthetic_fixed_context_T01_T02_T03_depth_8', 'toolchain': info, 'source_files': sources,
            'source_sha256': fingerprint(sources), 'model_sha256': fingerprint(model),
            'contexts': baseline, 'controls': controls, 'mutants': mutants, 'history_probes': history, 'acceptance_witness': witness}


def render(r):
    lines = ['# E3.2 — wynik badania', '', f'Wynik: **{r["status"]}**.', '',
             f'Hash wejść: `{r["source_sha256"]}`.', '',
             '| Próba | TLC | Stany | Oczekiwanie spełnione |', '|---|---|---:|---|']
    for p in r['contexts'] + r['controls'] + r['mutants'] + r['history_probes']:
        t = p['tlc']; lines.append(f'| {p["id"]} | {t["invariant"] or t["status"]} | {t.get("distinct_states") or "—"} | {p["matched"]} |')
    lines += ['', 'Świadek zatwierdzenia po dwóch odrzuceniach: ' + str(r['acceptance_witness']['matched']),
              '', 'Granice: syntetyczne Init, jeden zmieniany rekord, stałe zależności i wersja, do 8 akcji.',
              'CHECK_DEADLOCK FALSE dotyczy tylko tego wycinka. Brak dowodu pełnych S/L/F, osiągalności od Init procesu, braku zakleszczeń i odbioru E3.',
              'Każdy mutant ma osobny wykonany świadek; pełne dane, wyniki porównania grafów, logi i dump w evidence.json.', '']
    return '\n'.join(lines)


def main():
    pin = json.loads((ROOT / 'tools/tla-toolchain.json').read_text())
    parser = argparse.ArgumentParser(description='E3.2: do 8 kroków T01–T03. Kody: 0 OK, 1 rozbieżność, 2 błąd wejścia/narzędzia, 3 timeout. Wynik nie jest odbiorem E3.')
    parser.add_argument('--output', default='artifacts/e3-02/run', help='Nowy lub pusty katalog dowodów')
    parser.add_argument('--java', default=pin['java_default'], help='Istniejący plik wykonywalny Java')
    parser.add_argument('--jar', default=str(ROOT / pin['jar_default']), help='Przypięty JAR TLC; bez pobierania')
    parser.add_argument('--timeout', type=float, default=60, help='Limit pojedynczego TLC: 0 < t <= 60 s')
    args = parser.parse_args()
    try:
        r = build(args); out = Path(args.output)
        (out / 'evidence.json').write_text(json.dumps(r, ensure_ascii=False, indent=2) + '\n')
        (out / 'report.md').write_text(render(r))
    except (ValueError, OSError) as error:
        print(f'E3.2: {error}', file=sys.stderr); return 2
    results = [p['tlc'] for p in r['contexts'] + r['controls'] + r['mutants'] + r['history_probes']]
    results += [p['witness']['tlc'] for p in r['mutants']] + [r['acceptance_witness']['tlc']]
    statuses = {p['status'] for p in results}
    print(f'E3.2: {r["status"]}; raport {out / "report.md"}. Bez odbioru E3.')
    return 2 if 'tool_error' in statuses else 3 if 'timeout' in statuses else 0 if r['status'] == 'checks_passed_not_stage_acceptance' else 1


if __name__ == '__main__':
    raise SystemExit(main())
