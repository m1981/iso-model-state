"""Pełne uruchomienie przykładu i izolacja zapisów symulacji.

Trace: WIT1.
"""

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_command_creates_repeatable_report_without_changing_project(tmp_path):
    protected = [*ROOT.glob("*.md"), *ROOT.glob("docs/*.md"), *ROOT.glob("model/**/*.yaml")]
    before = {str(path): path.read_bytes() for path in protected}
    outputs = []
    for name in ("first", "second"):
        destination = tmp_path / name
        process = subprocess.run(
            [sys.executable, str(ROOT / "scripts/run_wit1.py"), "--output", str(destination)],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert process.returncode == 0, process.stdout + process.stderr
        trace = json.loads((destination / "trace.json").read_text())
        report = (destination / "report.md").read_text()
        assert trace["simulation"] is True
        assert trace["outcome"] == "completed" and len(trace["steps"]) == 29
        assert trace["final_state"]["releases"]["1"]["state"] == "accepted"
        assert len(trace["gate_probes"]) == 7 and all(p["detected"] for p in trace["gate_probes"])
        assert "SYMULACJA" in report and "W04" in report and "S7b" in report
        assert len(trace["provenance"]["source_sha256"]) == 64
        assert set(p.name for p in destination.iterdir()) == {"report.md", "trace.json"}
        outputs.append((trace, report))
    assert outputs[0] == outputs[1]
    assert before == {str(path): path.read_bytes() for path in protected}
