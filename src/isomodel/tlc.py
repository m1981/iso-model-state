"""Przypięty runner TLC; awaria, timeout i kontrprzykład to różne wyniki.

Trace: E3.1; nie implementuje reguł procesu ani nie pobiera zależności.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]


class ToolchainError(ValueError):
    """Narzędzie nie jest dostępne albo nie odpowiada przypiętym bajtom."""


def toolchain_info(java, jar):
    pin = json.loads((ROOT / 'tools/tla-toolchain.json').read_text())
    java, jar = Path(java).resolve(), Path(jar).resolve()
    if not jar.is_file():
        raise ToolchainError(f'Brak JAR: {jar}. Udostępnij TLC {pin["version"]} według docs/E3-01-MAPOWANIE.md; runner nie pobiera plików.')
    digest = hashlib.sha256(jar.read_bytes()).hexdigest()
    if digest != pin['sha256']:
        raise ToolchainError(f'Niezgodny SHA-256 JAR: {jar}. Oczekiwano {pin["sha256"]}; sprawdź źródło pliku, nie zmieniaj przypięcia automatycznie.')
    try:
        result = subprocess.run([str(java), '-version'], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ToolchainError(f'Java niedostępna: {java}. Podaj działającą Javę przez --java: {error}') from error
    if result.returncode:
        raise ToolchainError(f'Java nie uruchamia się: {java}. Sprawdź --java; {result.stderr.strip()}')
    return {'java': str(java), 'java_version': (result.stdout + result.stderr).strip(),
            'jar': str(jar), 'jar_sha256': digest, 'release': pin['version']}


def classify_output(returncode, output):
    blocks = [(int(code), int(level), text) for code, level, text in re.findall(
        r'@!@!@STARTMSG (\d+):(\d+) @!@!@\s*(.*?)@!@!@ENDMSG \1 @!@!@', output, re.S)]
    codes = {code for code, _, _ in blocks}
    stats = next((re.search(r'([\d,]+) states generated, ([\d,]+) distinct states found, ([\d,]+) states left', text)
                  for code, _, text in blocks if code == 2199), None)
    invariant = next((re.search(r'Invariant (\w+) is violated', text)
                      for code, _, text in blocks if code in {2107, 2110}), None)
    result = {'status': 'tool_error', 'returncode': returncode, 'message_codes': sorted(codes),
              'invariant': None, 'generated_states': None, 'distinct_states': None, 'queue_remaining': None}
    if stats:
        result.update(zip(('generated_states', 'distinct_states', 'queue_remaining'),
                          (int(x.replace(',', '')) for x in stats.groups())))
    if returncode == 0 and 2193 in codes and 2186 in codes and stats and result['queue_remaining'] == 0 and not any(level == 1 for _, level, _ in blocks):
        result['status'] = 'passed'
    elif returncode == 12 and invariant and 2186 in codes:
        result.update(status='invariant_violation', invariant=invariant[1])
    else:
        result['reason'] = 'Brak potwierdzonego zakończenia TLC lub błąd narzędzia; sprawdź log, konfigurację i uprawnienia środowiska.'
    return result


def run_tlc(module, config, output_dir, *, java, jar, timeout=60):
    if not 0 < timeout <= 60:
        raise ValueError('Limit TLC musi być dodatni i nie większy niż 60 s dla E3.1.')
    info = toolchain_info(java, jar)
    module, config = Path(module).resolve(), Path(config).resolve()
    if not module.is_file() or not config.is_file():
        raise ToolchainError('Brak modułu TLA+ lub konfiguracji CFG; najpierw wygeneruj oba pliki.')
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix='run-', dir=output_dir))
    log_file, dump_prefix = run_dir / 'tlc.log', run_dir / 'visited'
    states_file = run_dir / 'visited.dump'  # TLC 1.7.4 dopisuje rozszerzenie.
    command = [info['java'], '-XX:+UseParallelGC', '-Xmx256m', '-cp', info['jar'], 'tlc2.TLC',
               '-tool', '-workers', '1', '-fp', '0', '-seed', '1', '-config', str(config),
               '-metadir', str(run_dir / 'states'), '-dump', str(dump_prefix), module.name]
    start = time.monotonic()
    try:
        process = subprocess.run(command, cwd=module.parent, capture_output=True, text=True, timeout=timeout)
        output = process.stdout + process.stderr
        result = classify_output(process.returncode, output)
    except subprocess.TimeoutExpired as error:
        def decode(value):
            return value.decode(errors='replace') if isinstance(value, bytes) else value or ''
        output = decode(error.stdout) + decode(error.stderr)
        result = {'status': 'timeout', 'returncode': None, 'invariant': None,
                  'reason': 'Przekroczono limit czasu; badanie nieukończone, bez wniosku o poprawności.'}
    except OSError as error:
        output = str(error)
        result = {'status': 'tool_error', 'returncode': None, 'invariant': None, 'reason': str(error)}
    log_file.write_text(output)
    if result['status'] == 'passed' and (not states_file.is_file() or not states_file.stat().st_size):
        result.update(status='tool_error', reason='Brak dump stanów po deklarowanym sukcesie TLC; sprawdź kompletność dowodu.')
    result.update(toolchain=info, command=command, cwd=str(module.parent), elapsed_seconds=time.monotonic() - start,
                  module_sha256=hashlib.sha256(module.read_bytes()).hexdigest(), config_sha256=hashlib.sha256(config.read_bytes()).hexdigest(),
                  log_file=str(log_file), log_sha256=hashlib.sha256(log_file.read_bytes()).hexdigest(), states_file=str(states_file))
    (run_dir / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result
