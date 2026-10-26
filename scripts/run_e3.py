#!/usr/bin/env python3
"""Odtwarzalny przyrost E3.1: lokalna relacja, nie odbiór E3 ani pełny dowód."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from isomodel import load_model
from isomodel.execution import StepRejected, execute_step, initial_state, fingerprint
from isomodel.tla_projection import ProjectionError, render_probe
from isomodel.tlc import ToolchainError, run_tlc, toolchain_info


def variants(model, cases):
    """Jawne kopie kontrolne i niezależne oczekiwania; brak zmian pliku modelu."""
    yield 'baseline', 'baseline', model, cases, 'T03', None
    for name in ('renamed', 'limit', 'from', 'to', 'same_state', 'guard', 'actor', 'effect'):
        m, cs = deepcopy(model), deepcopy(cases)
        t = next(t for t in m['item_transitions'] if t['id'] == 'T03')
        ident, oracle = 'T03', None
        if name == 'renamed':
            t['id'] = ident = 'T_RENAMED'
        elif name == 'limit':
            m['parameters']['MAX_REJECTIONS'] = 1
            for c in cs:
                if c['before']['rejections'] == 1:
                    c.update(enabled=False, after=None)
        elif name == 'from':
            t['from'] = ['approved']
            for c in cs:
                c.update(enabled=False, after=None)
            c = next(c for c in cs if c['id'] == 'approved_refused')
            c.update(enabled=True, after=c['before'] | {'state': 'draft', 'rejections': 1})
        elif name in ('to', 'same_state'):
            t['to'] = 'deferred' if name == 'to' else '='
            for c in cs:
                if c['enabled']:
                    c['after']['state'] = 'deferred' if name == 'to' else c['before']['state']
        elif name == 'guard':
            t['guard'], oracle = 'true', 'Availability'
        elif name == 'actor':
            t['actor'], oracle = 'A', 'Availability'
        else:
            t['effects'], oracle = [], 'Successor'
        yield name, 'mutant' if oracle else 'data_control', m, cs, ident, oracle


def python_observations(model, cases, transition):
    results = []
    for c in cases:
        before = initial_state(model)
        before['items']['r1'] = deepcopy(c['before'])
        try:
            step = execute_step(model, before, {'transition': transition, 'actor': c['actor'], 'item': 'r1'}, {})
        except StepRejected as error:
            results.append({'case': c['id'], 'enabled': False, 'after': None, 'reason': error.code,
                            'matches_oracle': not c['enabled']})
        else:
            after = deepcopy(step['after'])
            item = after['items']['r1']
            after['items']['r1'] = deepcopy(before['items']['r1'])
            results.append({'case': c['id'], 'enabled': True, 'after': item,
                            'global_frame_preserved': after == before,
                            'matches_oracle': c['enabled'] and item == c['after'] and after == before})
    return results


def run_projection(model, cases, transition, directory, args):
    directory.mkdir(parents=True, exist_ok=True)
    text, config = render_probe(model, transition, cases)
    module, cfg = directory / 'Projection.tla', directory / 'Projection.cfg'
    module.write_text(text); cfg.write_text(config)
    (directory / 'cases.json').write_text(json.dumps(cases, ensure_ascii=False, indent=2) + '\n')
    return run_tlc(module, cfg, directory / 'runs', java=args.java, jar=args.jar, timeout=args.timeout)


def build(args):
    info = toolchain_info(args.java, args.jar)  # przed utworzeniem raportu przy braku narzędzia
    output = Path(args.output).resolve(); output.mkdir(parents=True, exist_ok=True)
    model = load_model(ROOT / 'model/process.yaml')
    fixture = ROOT / 'tests/fixtures/e3/t03_cases.json'
    cases = json.loads(fixture.read_text())['cases']
    smoke = {name: run_tlc(ROOT / 'tla/smoke/Smoke.tla', ROOT / f'tla/smoke/{cfg}.cfg', output / 'smoke' / name,
                          java=args.java, jar=args.jar, timeout=args.timeout)
             for name, cfg in [('good', 'Good'), ('violation', 'Violation')]}
    probes = []
    for name, kind, m, cs, transition, oracle in variants(model, cases):
        result = run_projection(m, cs, transition, output / name, args)
        observed = python_observations(m, cs, transition)
        matched = result['status'] == ('invariant_violation' if oracle else 'passed')
        matched &= result['invariant'] == oracle
        if not oracle:
            matched &= all(o['matches_oracle'] for o in observed)
            matched &= result.get('distinct_states') == len(cs) + sum(c['enabled'] for c in cs)
        else:
            matched &= any(not o['matches_oracle'] for o in observed)
        probe = {'id': name, 'kind': kind, 'model_sha256': fingerprint(m), 'transition': transition,
                 'expected_oracle_violation': oracle, 'cases': cs, 'python': observed, 'tlc': result,
                 'matched_expectation': matched}
        if oracle:
            ident = {'guard': 'budget_exhausted', 'actor': 'author_refused', 'effect': 'first_rejection'}[name]
            witness = deepcopy(next(c for c in cs if c['id'] == ident))
            count = {'guard': 3, 'actor': 1, 'effect': 0}[name]
            witness.update(enabled=True, after=witness['before'] | {'state': 'draft', 'rejections': count})
            wresult = run_projection(m, [witness], transition, output / name / 'witness', args)
            wp = python_observations(m, [witness], transition)
            probe['executed_witness'] = {'case': witness, 'python': wp, 'tlc': wresult}
            probe['matched_expectation'] &= wresult['status'] == 'passed' and wresult.get('distinct_states') == 2 and all(o['matches_oracle'] for o in wp)
        probes.append(probe)
    smoke_ok = smoke['good']['status'] == 'passed' and smoke['good'].get('distinct_states') == 2 and smoke['violation']['status'] == 'invariant_violation' and smoke['violation']['invariant'] == 'WithinLimit'
    checks_passed = smoke_ok and all(p['matched_expectation'] for p in probes)
    paths = [ROOT / 'model/process.yaml', fixture, ROOT / 'tools/tla-toolchain.json', Path(__file__).resolve(),
             ROOT / 'docs/E3-01-MAPOWANIE.md', ROOT / 'pyproject.toml', ROOT / 'uv.lock',
             *sorted((ROOT / 'src/isomodel').glob('*.py')),
             *sorted((ROOT / 'tla/smoke').glob('*')),
             *(ROOT / 'tests' / name for name in ('test_tla_projection.py', 'test_tlc.py', 'test_e3_runner.py', 'conftest.py'))]
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return {'status': 'checks_passed_not_stage_acceptance' if checks_passed else 'verification_failed',
            'scope': 'synthetic_local_T03_relation_one_step_not_full_process', 'toolchain': info,
            'model_sha256': fingerprint(model), 'source_files': sources, 'source_sha256': fingerprint(sources),
            'smoke': smoke, 'probes': probes,
            'limitations': ['Nie dowodzi osiągalności próbek, całych S1/S15, żywotności, sprawiedliwości ani braku zakleszczeń.',
                            'CHECK_DEADLOCK FALSE dotyczy wyłącznie lokalnego testu relacji.',
                            'Oczekiwania są danymi wyroczni; wynik TLC sprawdza ich zgodność, dump zachowuje odwiedzone stany.',
                            'TLC używa fingerprintów stanów; wynik nie jest dowodem dedukcyjnym.',
                            'E3.1 nie jest odbiorem E3 ani narzędziem do kontroli rzeczywistego repozytorium.']}


def render(report):
    lines = ['# E3.1 — wykonanie lokalnej relacji T03', '', f'Wynik: **{report["status"]}**.', '',
             f'Model SHA-256: `{report["model_sha256"]}`; wejścia badania: `{report["source_sha256"]}`.',
             f'TLC release {report["toolchain"]["release"]}, JAR SHA-256 `{report["toolchain"]["jar_sha256"]}`.', '',
             '| Próba | TLC | Wyrocznia naruszona | Stany odrębne | Oczekiwanie spełnione |', '|---|---|---|---|---|']
    for p in report['probes']:
        r = p['tlc']
        lines.append(f'| {p["id"]} | {r["status"]} | {r["invariant"] or "—"} | {r.get("distinct_states", "—")} | {p["matched_expectation"]} |')
    lines += ['', 'Osobne próby świadków mutantów sprawdzają: utrata limitu daje licznik 3, zmiana roli dopuszcza A, brak inkrementacji zachowuje licznik 0. Każdy świadek musi mieć dokładnie 2 stany i zgodność z Pythonem; wykonane wyniki w evidence.json.', '', '## Granice wyniku', '']
    lines.extend('- ' + limit for limit in report['limitations'])
    lines += ['', 'Odtworzenie: `.venv/bin/python scripts/run_e3.py --output artifacts/e3-01/reproduction`.',
              'Źródła, konfiguracje, pełne logi, dump i wyniki procesu są wskazane w evidence.json. Brak automatycznego pobierania narzędzia.', '']
    return '\n'.join(lines)


def main():
    pin = json.loads((ROOT / 'tools/tla-toolchain.json').read_text())
    parser = argparse.ArgumentParser(description='E3.1: lokalne sprawdzenie T03, bez odbioru etapu. Kody: 0 sprawdzenia OK, 1 rozbieżność, 2 błąd narzędzia/wejścia, 3 timeout.')
    parser.add_argument('--output', default='artifacts/e3-01/run', help='Katalog raportu, modułów i surowych logów')
    parser.add_argument('--java', default=pin['java_default'], help='Pełna ścieżka do istniejącej Javy')
    parser.add_argument('--jar', default=str(ROOT / pin['jar_default']), help='JAR zgodny z tools/tla-toolchain.json; runner nie pobiera plików')
    parser.add_argument('--timeout', type=float, default=60, help='Limit 0 < t <= 60 sekund dla pojedynczego TLC')
    args = parser.parse_args()
    try:
        report = build(args)
        out = Path(args.output)
        (out / 'evidence.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        (out / 'report.md').write_text(render(report))
    except (ToolchainError, ProjectionError, ValueError, OSError) as error:
        print(f'E3.1: {error}', file=sys.stderr)
        return 2
    results = list(report['smoke'].values()) + [p['tlc'] for p in report['probes']] + [p['executed_witness']['tlc'] for p in report['probes'] if 'executed_witness' in p]
    statuses = {r['status'] for r in results}
    print(f'E3.1: {report["status"]}; raport {Path(args.output) / "report.md"}. Nie jest to odbiór E3.')
    return 2 if 'tool_error' in statuses else 3 if 'timeout' in statuses else 0 if report['status'] == 'checks_passed_not_stage_acceptance' else 1


if __name__ == '__main__':
    raise SystemExit(main())
