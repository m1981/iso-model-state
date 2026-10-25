"""Nowe sekwencje zdarzeń z Hypothesis, z historią od initial.

Trace: S1–S15. Prefiksy dają dostęp do późnych etapów, a kolejne kroki są
dobierane na nowo. Żaden wynik wyroczni nie służy filtrowaniu generatora.
Trzy osobne instancje zakresu zachowują granice YAML; nie jest to badanie
wyczerpujące ani zmiana świadków podstawowej instancji.
"""

from copy import deepcopy
from pathlib import Path

from hypothesis import event, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from isomodel import load_model
from isomodel.execution import (ExplorationBoundary, InputError, StepRejected,
                                execute_step, initial_state)
from isomodel.exploration import (classify_candidates, exploration_candidates,
                                  exploration_inputs, reachability_scenarios,
                                  simulation_evidence)
from isomodel.safety import safety_violations


MODEL = load_model(Path(__file__).resolve().parents[1] / "model/process.yaml")
SCENARIOS = reachability_scenarios()


def external_change_events():
    return [
        {"transition": "P00", "actor": "A", "question": "external-change",
         "attributes": {"kind": "change", "about": "p1",
                        "requested_transition": "T05", "blocking": True}},
        {"transition": "P01", "actor": "A", "question": "external-change"},
        {"transition": "P02", "actor": "U", "question": "external-change",
         "inputs": {"unambiguous_answer": True, "resolution": "approved"},
         "evidence": simulation_evidence()},
        {"transition": "T05", "actor": "U", "item": "p1",
         "question": "external-change"},
    ]


# Prefiksy alternatywnego zakresu obejmują wpływ spoza scope na każdy etap
# wydania. Każdy krok nadal wykonuje publiczny interpreter od initial.
EXTERNAL_SCENARIOS = [
    {"events": SCENARIOS[0]["events"][:count] + external_change_events()
     + ([{"transition": "W06", "actor": "A"}] if count == 29 else [])}
    for count in (27, 28, 29)
]
EMPTY_SCENARIOS = [SCENARIOS[0], {"events": SCENARIOS[0]["events"][-3:]}]


class ProcessSequences(RuleBasedStateMachine):
    scope_variant = "default"
    scenarios = SCENARIOS

    @initialize(data=st.data())
    def start_at_reachable_prefix(self, data):
        self.model = deepcopy(MODEL)
        if self.scope_variant == "without_p1":
            self.model["test_instance"]["release_scope"].remove("p1")
        elif self.scope_variant == "empty":
            self.model["test_instance"]["release_scope"] = []
        self.state = initial_state(self.model)
        self.inputs = exploration_inputs(self.model)
        self.steps = []
        event("scope=" + self.scope_variant)
        scenario = data.draw(st.sampled_from(self.scenarios), label="prefix_scenario")
        count = data.draw(st.one_of(st.just(0), st.just(len(scenario["events"])),
            st.integers(0, len(scenario["events"]))), label="prefix_length")
        for candidate in scenario["events"][:count]:
            self.apply(candidate)
        assert len(self.steps) == count
        self.initial_prefix_length = count
        self.generated_steps = 0

    def apply(self, candidate):
        before = deepcopy((self.model, self.state, candidate, self.inputs))
        try:
            step = execute_step(self.model, self.state, candidate, self.inputs)
        except ExplorationBoundary:
            event("outcome=boundary")
            assert (self.model, self.state, candidate, self.inputs) == before
            return
        except (StepRejected, InputError) as error:
            event("outcome=" + (error.code if isinstance(error, StepRejected) else "input"))
            assert (self.model, self.state, candidate, self.inputs) == before
            return
        assert (self.model, self.state, candidate, self.inputs) == before
        step["step"] = len(self.steps) + 1
        self.steps.append(step)
        self.state = deepcopy(step["after"])
        event("applied=" + candidate["transition"])

    @rule(data=st.data())
    def choose_enabled_step(self, data):
        outcomes = classify_candidates(self.model, self.state)
        if outcomes["boundary"]:
            event("frontier_has_boundary")
        if not outcomes["applied"]:
            # To opis skończonego generatora, nie dowód zakleszczenia procesu.
            event("no_enabled_candidate_within_bounds")
            return
        candidate = data.draw(st.sampled_from([step["event"] for step in outcomes["applied"]]),
                              label="enabled_event")
        self.apply(candidate)
        self.generated_steps += 1

    @rule(data=st.data(), mutation=st.sampled_from(["none", "actor", "evidence", "checks", "answer"]))
    def attempt_step_and_check_atomic_refusal(self, data, mutation):
        candidates = exploration_candidates(self.model, self.state)
        candidate = deepcopy(data.draw(st.sampled_from(candidates), label="attempt_event"))
        if mutation == "actor":
            candidate["actor"] = data.draw(st.sampled_from(["A", "U", "R"]))
        elif mutation == "evidence":
            candidate.pop("evidence", None)
        elif mutation == "checks":
            candidate["inputs"] = {"tests_ok": False,
                                   "checks_ok": {ident: False for ident in self.state["items"]}}
        elif mutation == "answer":
            candidate["inputs"] = {"unambiguous_answer": False}
        self.apply(candidate)
        self.generated_steps += 1

    @invariant()
    def all_observed_steps_satisfy_independent_safety(self):
        violations = safety_violations(self.model, self.steps)
        assert violations == [], {"violations": violations,
                                  "events": [step["event"] for step in self.steps]}

    def teardown(self):
        event(f"generated_steps={self.generated_steps}")


TestProcessSequences = ProcessSequences.TestCase
TestProcessSequences.settings = settings(max_examples=24, stateful_step_count=25,
                                        deadline=None, derandomize=True)


class ExternalScopeSequences(ProcessSequences):
    scope_variant = "without_p1"
    scenarios = [SCENARIOS[0], *EXTERNAL_SCENARIOS]


class EmptyScopeSequences(ProcessSequences):
    scope_variant = "empty"
    scenarios = EMPTY_SCENARIOS


TestExternalScopeSequences = ExternalScopeSequences.TestCase
TestExternalScopeSequences.settings = TestProcessSequences.settings
TestEmptyScopeSequences = EmptyScopeSequences.TestCase
TestEmptyScopeSequences.settings = TestProcessSequences.settings
