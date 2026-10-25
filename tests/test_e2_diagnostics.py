"""Znane luki są odtwarzane jawnie, a nie maskowane jako pełne E2."""
import importlib.util
from pathlib import Path
from copy import deepcopy

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('e2_hardening',ROOT/'model/proposals/e2_hardening_diagnostics.py')
diag=importlib.util.module_from_spec(spec);spec.loader.exec_module(diag)


def test_known_model_gaps_and_proposed_copy_have_explicit_outcomes(model):
    original=deepcopy(model)
    report=diag.diagnostics(model)
    assert model==original and report['status']=='requires_decision'
    late,rejections,external=report['cases']
    assert late['baseline']['release']=='accepted' and late['baseline']['open_blocking']==['late']
    assert late['proposed']['last_code']=='guard' and late['proposed']['release']=='reviewed'
    assert rejections['baseline']['rejection_events']=={'p1@1':3}
    assert rejections['proposed']['rejection_events']=={'p1@1':2} and rejections['proposed']['last_code']=='guard'
    assert external['alternative_scope']
    assert {'S7a','S7b'} <= {v['property'] for v in external['baseline']['violations']}
    assert external['proposed']['violations']==[] and external['proposed']['release']=='in_preparation'
    assert report['empty_scope']['runtime_code']=='unsupported'
    assert [v['baseline'] for v in report['empty_scope']['predicate_only']]==[True,True,True]
    assert [v['proposed'] for v in report['empty_scope']['predicate_only']]==[True,False,False]
