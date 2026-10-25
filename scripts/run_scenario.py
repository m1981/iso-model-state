#!/usr/bin/env python3
"""Uruchom WIT1/WIT2/WIT4/WIT5 i zapisz odtwarzalny raport symulacji.

Trace: WIT1, WIT2, WIT4, WIT5, S11, S1, S9, L2, L4.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from isomodel import ModelError, load_model
from isomodel.execution import fingerprint, replay
from isomodel.probes import gate_probes
from isomodel.reporting import render_markdown


def main():
    parser = argparse.ArgumentParser(description="WIT — wyłącznie symulacja, bez decyzji w rzeczywistym projekcie")
    parser.add_argument("--scenario", type=str.upper, choices=["WIT1", "WIT2", "WIT4", "WIT5"], default="WIT1")
    parser.add_argument("--output", type=Path, help="Katalog dla report.md i trace.json; bez opcji raport trafia na stdout")
    args = parser.parse_args()
    name = args.scenario.lower()
    try:
        model = load_model(ROOT / "model/process.yaml")
        scenario = json.loads((ROOT / f"tests/fixtures/{name}/scenario.json").read_text())
        cases = json.loads((ROOT / f"mutants/{name}_gates.json").read_text())
        result = replay(model, scenario)
        if result["outcome"] == "completed":
            result["gate_probes"] = gate_probes(model, scenario, cases)
        source_files = sorted((ROOT / "src/isomodel").glob("*.py")) + sorted((ROOT / "scripts").glob("run_*.py"))
        result["provenance"] = {
            "python": platform.python_version(),
            "source_sha256": fingerprint({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}),
            "uv_lock_sha256": hashlib.sha256((ROOT / "uv.lock").read_bytes()).hexdigest(),
            "mutants_sha256": fingerprint(cases),
        }
        report = render_markdown(result)
        if args.output is None:
            print(report, end="")
        else:
            args.output.mkdir(parents=True, exist_ok=True)
            (args.output / "trace.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (args.output / "report.md").write_text(report, encoding="utf-8")
            print(f"{args.scenario}: {result['outcome']}; {len(result['steps'])} kroków; raport: {args.output / 'report.md'}")
        if result["outcome"] != "completed" or not all(p["detected"] for p in result.get("gate_probes", [])):
            return 1
        return 0
    except (ModelError, OSError, ValueError) as error:
        print(f"Nie wykonano {args.scenario}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
