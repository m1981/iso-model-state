"""Wczytywanie i błędy słownika modelu.

Trace: G0, G4.
"""

from copy import deepcopy

import pytest
import yaml
from hypothesis import given, strategies as st

from isomodel import ModelError, load_model, validate_model


def test_G0_loads_authoritative_model(model):
    assert model["model"] == "iso29110-basic-process"
    assert model["status"] == "approved"
    assert model["test_instance"]["bounds"]["max_releases"] == 2


def test_G0_rejects_duplicate_yaml_key(tmp_path):
    path = tmp_path / "duplicate.yaml"
    path.write_text("version: 0.3\nversion: 0.4\n")
    with pytest.raises(ModelError, match="Powtórzony klucz"):
        load_model(path)


def test_G0_rejects_non_mapping_yaml(tmp_path):
    path = tmp_path / "list.yaml"
    path.write_text("- element\n")
    with pytest.raises(ModelError, match="mapą"):
        load_model(path)


@pytest.mark.parametrize("field,value", [("actor", "UNKNOWN"), ("from", ["unknown_state"]), ("to", "unknown_state")])
def test_G0_rejects_unknown_transition_reference(model, field, value):
    model["item_transitions"][0][field] = value
    with pytest.raises(ModelError, match="G0"):
        validate_model(model)


def test_G0_rejects_unknown_guard_state(model):
    model["item_transitions"][1]["guard"] = "state in {approved, typo}"
    with pytest.raises(ModelError, match="G0"):
        validate_model(model)


def test_G0_rejects_unknown_dependency(model):
    model["test_instance"]["items"]["r1"]["depends_on"] = ["missing"]
    with pytest.raises(ModelError, match="G0"):
        validate_model(model)


def test_G0_rejects_missing_section(model):
    del model["release_control_variables"]
    with pytest.raises(ModelError, match="G0"):
        validate_model(model)


def test_G0_rejects_unknown_top_level_section(model):
    model["release_transitons"] = []
    with pytest.raises(ModelError, match="G0"):
        validate_model(model)


def test_G4_rejects_multiple_targets(model):
    model["item_transitions"][3]["to"] = ["draft", "approved"]
    with pytest.raises(ModelError, match="G4"):
        validate_model(model)


def test_G4_rejects_duplicate_transition_id(model):
    model["item_transitions"].append(deepcopy(model["item_transitions"][0]))
    with pytest.raises(ModelError, match="G4"):
        validate_model(model)


def test_G0_round_trip_does_not_depend_on_yaml_key_order(model, tmp_path):
    path = tmp_path / "sorted.yaml"
    path.write_text(yaml.safe_dump(model, sort_keys=True, allow_unicode=True))
    assert load_model(path) == model


@given(name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=15))
def test_G0_duplicate_keys_never_silently_overwrite(name, tmp_path_factory):
    path = tmp_path_factory.getbasetemp() / "generated.yaml"
    path.write_text(f"{name}: 1\n{name}: 2\n")
    with pytest.raises(ModelError, match="Powtórzony klucz"):
        load_model(path)
