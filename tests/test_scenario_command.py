"""Raporty nowych ścieżek, powtarzalność i brak zapisów decyzji w projekcie.

Trace: WIT2, WIT4.
"""

import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("name,steps,mutants,records", [("WIT3", 54, 17, 2), ("WIT2", 33, 2, 0), ("WIT4", 13, 7, 3), ("WIT5", 40, 10, 1)])
def test_new_scenario_command(tmp_path, name, steps, mutants, records):
    protected = [*ROOT.glob("*.md"), *ROOT.glob("docs/*.md"), *ROOT.glob("model/**/*.yaml")]
    before = {str(path): path.read_bytes() for path in protected}
    results = []
    for folder in ("first", "second"):
        output = tmp_path / folder
        process = subprocess.run([sys.executable, str(ROOT / "scripts/run_scenario.py"),
                                  "--scenario", name, "--output", str(output)],
                                 cwd=tmp_path, capture_output=True, text=True)
        assert process.returncode == 0, process.stderr + process.stdout
        data = json.loads((output / "trace.json").read_text())
        report = (output / "report.md").read_text()
        assert data["outcome"] == "completed" and len(data["steps"]) == steps
        assert len(data["gate_probes"]) == mutants and all(p["detected"] for p in data["gate_probes"])
        assert len(data["records"]) == records
        assert report.startswith(f"# {name}") and "SYMULACJA" in report
        if name == "WIT4":
            assert data["steps"][4]["records"] == []
            assert "Utworzone decyzje demonstracyjne" in report and "P03" in report
        if name == "WIT3":
            assert "| 37 | U | W07 | wydanie 1 (element r3) | in_preparation → in_preparation |" in report
            assert "Zmiany powiązań i zakresu" in report
            assert "| 42 | a1 | depends_on | ['r1'] | ['r3'] |" in report
            assert "SIM-Przejrzane: c1, a1 v2, d1 v2; zachowanie kodu bez zmiany" in report
        results.append((data, report))
    assert results[0] == results[1]
    assert before == {str(path): path.read_bytes() for path in protected}
