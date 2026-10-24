"""Wczytywanie wiążących danych modelu.

Trace: G0, G4.
"""

from .loader import ModelError, load_model, validate_model

__all__ = ["ModelError", "load_model", "validate_model"]
