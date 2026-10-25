"""Macierz E2 wiąże właściwości z rzeczywiście naruszającym je mutantem."""
from pathlib import Path
from isomodel.evidence import safety_evidence, structural_evidence, SAFETY_IDS

ROOT=Path(__file__).resolve().parents[1]


def test_each_safety_property_has_executed_mutant_and_clean_baseline(model):
    report=safety_evidence(model,ROOT)
    assert report['missing']==[],report
    assert len(report['mutations'])==43
    assert all(m['gate_detected'] and m['mutant_applied'] and not m['baseline_violations'] for m in report['mutations'])
    assert all(not w['violations'] for w in report['witnesses'])
    assert set(report['properties'])==set(SAFETY_IDS)
    assert report['exhaustive'] is False


def test_structural_report_distinguishes_projection_and_coverage(model):
    report=structural_evidence(model)
    for p in ('G0','G1','G3','G4','G6'):
        assert report[p]['baseline'] and report[p]['mutant_detected']
    assert report['G5']['kind']=='report_not_test'


def test_command_reports_model_decision_instead_of_false_green(tmp_path):
    import json
    import subprocess
    import sys
    run=subprocess.run([sys.executable,str(ROOT/'scripts/run_e2.py'),'--output',str(tmp_path)],cwd=tmp_path,capture_output=True,text=True)
    assert run.returncode==1,run.stdout+run.stderr
    report=json.loads((tmp_path/'evidence.json').read_text())
    assert report['status']=='requires_model_decision'
    assert len(report['reachability']['covered'])==28 and report['safety']['missing']==[]
    assert report['structure']['G2']['mutant_detected']
    assert 'E2 nie jest odebrane' in (tmp_path/'report.md').read_text()
