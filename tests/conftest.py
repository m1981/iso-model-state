"""Dane wiążącego modelu; materiały informative/ nie są wejściem testów.

Trace: G0, G1, G3, G4, G5, G6.
"""

from pathlib import Path

import pytest

from isomodel import load_model


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def model():
    return load_model(ROOT / "model/process.yaml")
