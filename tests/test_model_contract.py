"""Kryteria odbioru modelu: nie ukrywamy czerwonych wyników przez xfail.

Trace: G3, G6, DoD 6, DoD 8.
"""

import yaml

from isomodel.graph import dead_ends, iso_coverage
from conftest import ROOT


def test_G3_specified_mutant_must_have_dead_end(model):
    mutant = yaml.safe_load((ROOT / "mutants/g3_missing_deferred_exits.yaml").read_text())
    model["item_transitions"] = [t for t in model["item_transitions"] if t["id"] not in mutant["remove_transitions"]]
    assert "deferred" in dead_ends(model, "item"), "Mutant G3 powinien usunąć wszystkie wyjścia z deferred"


def test_G6_model_must_cover_all_outcomes_and_annotate_each_transition(model):
    report = iso_coverage(model)
    assert not report["missing_outcomes"] and not report["missing_transition_iso"], report
