#!/usr/bin/env python3
"""Uruchom WIT1 i zapisz odtwarzalny raport symulacji.

Trace: WIT1, S1, S2, S3, S4, S7a, S7b, S8.
"""

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from isomodel import ModelError, load_model
from isomodel.execution import StepRejected, execute_step, fingerprint, initial_state, replay
from isomodel.reporting import render_markdown


def gate_probes(model, scenario, cases):
    results = []
    for case in cases:
        state = initial_state(model)
        for event in scenario["events"][:case["prefix_steps"]] + case.get("setup_events", []):
            state = execute_step(model, state, event, scenario["inputs"])["after"]
        baseline_code = "applied"
        try:
            execute_step(model, state, case["attempt"], scenario["inputs"])
        except StepRejected as error:
            baseline_code = error.code
        mutant = deepcopy(model)
        definition = next(t for kind in ("item", "release") for t in mutant[f"{kind}_transitions"]
                          if t["id"] == case["attempt"]["transition"])
        definition[case["field"]] = case["replacement"]
        try:
            execute_step(mutant, state, case["attempt"], scenario["inputs"])
            mutant_outcome = "applied"
        except StepRejected:
            mutant_outcome = "rejected"
        results.append({"id": case["id"], "property": case["property"], "baseline_code": baseline_code,
                        "mutant_outcome": mutant_outcome,
                        "detected": baseline_code == case["expected_code"] and mutant_outcome == "applied"})
    return results


def main():
    parser = argparse.ArgumentParser(description="WIT1 — wyłącznie symulacja, bez decyzji w rzeczywistym projekcie")
    parser.add_argument("--output", type=Path, help="Katalog dla report.md i trace.json; bez opcji raport trafia na stdout")
    args = parser.parse_args()
    try:
        model = load_model(ROOT / "model/process.yaml")
        scenario = json.loads((ROOT / "tests/fixtures/wit1/scenario.json").read_text())
        cases = json.loads((ROOT / "mutants/wit1_gates.json").read_text())
        result = replay(model, scenario)
        if result["outcome"] == "completed":
            result["gate_probes"] = gate_probes(model, scenario, cases)
        source_files = sorted((ROOT / "src/isomodel").glob("*.py")) + [Path(__file__).resolve()]
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
            print(f"WIT1: {result['outcome']}; {len(result['steps'])} kroków; raport: {args.output / 'report.md'}")
        if result["outcome"] != "completed" or not all(p["detected"] for p in result.get("gate_probes", [])):
            return 1
        return 0
    except (ModelError, OSError, ValueError) as error:
        print(f"Nie wykonano WIT1: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
