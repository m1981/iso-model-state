"""Odtwarzalna komenda przyrostu, raport i jawne błędy środowiska."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/run_e3.py'


def test_research_command_reproduces_evidence(tmp_path):
    before = (ROOT / 'model/process.yaml').read_bytes()
    p = subprocess.run([sys.executable, str(SCRIPT), '--output', str(tmp_path)], cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert p.returncode == 0, p.stdout + p.stderr
    evidence = json.loads((tmp_path / 'evidence.json').read_text())
    assert evidence['status'] == 'checks_passed_not_stage_acceptance'
    assert len(evidence['probes']) == 9
    assert all(p['matched_expectation'] for p in evidence['probes'])
    assert [p['tlc']['invariant'] for p in evidence['probes'] if p['kind'] == 'mutant'] == ['Availability', 'Availability', 'Successor']
    assert all(p['executed_witness']['tlc']['distinct_states'] == 2 for p in evidence['probes'] if p['kind'] == 'mutant')
    assert evidence['smoke']['good']['status'] == 'passed'
    assert evidence['smoke']['violation']['invariant'] == 'WithinLimit'
    assert (tmp_path / 'report.md').is_file()
    assert (ROOT / 'model/process.yaml').read_bytes() == before


def test_help_and_missing_dependency_have_useful_contract(tmp_path):
    help_result = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True)
    assert help_result.returncode == 0 and '--java' in help_result.stdout and '--jar' in help_result.stdout
    p = subprocess.run([sys.executable, str(SCRIPT), '--jar', str(tmp_path / 'absent.jar'), '--output', str(tmp_path / 'out')], capture_output=True, text=True)
    assert p.returncode == 2
    assert 'JAR' in p.stderr and 'docs/E3-01-MAPOWANIE.md' in p.stderr
    assert not (tmp_path / 'out/evidence.json').exists()
