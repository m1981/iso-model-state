"""Kontrola rozróżnienia kontrprzykładu od awarii narzędzia."""
from pathlib import Path
import pytest
from isomodel.tlc import classify_output, run_tlc, ToolchainError

ROOT = Path(__file__).resolve().parents[1]
JAVA = Path('/Applications/PyCharm.app/Contents/jbr/Contents/Home/bin/java')
JAR = ROOT / 'artifacts/tools/tla/1.7.4/tla2tools.jar'


def test_real_tool_accepts_and_finds_counterexample(tmp_path):
    module = ROOT / 'tla/smoke/Smoke.tla'
    good = run_tlc(module, module.with_name('Good.cfg'), tmp_path / 'good', java=JAVA, jar=JAR)
    bad = run_tlc(module, module.with_name('Violation.cfg'), tmp_path / 'bad', java=JAVA, jar=JAR)
    assert good['status'] == 'passed' and good['distinct_states'] == 2
    assert bad['status'] == 'invariant_violation' and bad['invariant'] == 'WithinLimit'


@pytest.mark.parametrize('code,output', [(0, ''), (12, 'syntax error'), (255, 'exception'), (0, 'Model checking completed. No error has been found.')])
def test_unconfirmed_or_failed_run_is_not_success_or_mutant(code, output):
    assert classify_output(code, output)['status'] == 'tool_error'


def test_missing_or_modified_jar_is_explicit_error(tmp_path):
    for path in [tmp_path / 'missing.jar', tmp_path / 'changed.jar']:
        if path.name == 'changed.jar':
            path.write_bytes(b'not the pinned tool')
        with pytest.raises(ToolchainError, match='JAR|SHA'):
            run_tlc(ROOT / 'tla/smoke/Smoke.tla', ROOT / 'tla/smoke/Good.cfg', tmp_path / 'result', java=JAVA, jar=path)


def test_actual_timeout_is_not_success(tmp_path):
    result = run_tlc(ROOT / 'tla/smoke/Smoke.tla', ROOT / 'tla/smoke/Good.cfg', tmp_path / 'timeout', java=JAVA, jar=JAR, timeout=0.001)
    assert result['status'] == 'timeout'


def test_invalid_spec_is_tool_error(tmp_path):
    module = tmp_path / 'Invalid.tla'
    module.write_text('---- MODULE Invalid ----\nInit == syntax !!!\n====\n')
    config = tmp_path / 'Invalid.cfg'
    config.write_text('INIT Init\nNEXT Next\n')
    result = run_tlc(module, config, tmp_path / 'invalid', java=JAVA, jar=JAR)
    assert result['status'] == 'tool_error'
