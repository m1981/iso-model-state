"""Nowe sekwencje zdarzeń z Hypothesis, z historią od initial.

Trace: S1–S13. Prefiksy dają dostęp do późnych etapów, a kolejne kroki są
dobierane na nowo. Żaden wynik wyroczni nie służy filtrowaniu generatora.
"""

from copy import deepcopy
from pathlib import Path

from hypothesis import event, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from isomodel import load_model
from isomodel.execution import (ExplorationBoundary, InputError, StepRejected,
                                execute_step, initial_state)
from isomodel.exploration import (classify_candidates, exploration_candidates,
                                  exploration_inputs, reachability_scenarios)
from isomodel.safety import safety_violations


MODEL = load_model(Path(__file__).resolve().parents[1] / "model/process.yaml")
SCENARIOS = reachability_scenarios()


class ProcessSequences(RuleBasedStateMachine):
    @initialize(data=st.data())
    def start_at_reachable_prefix(self, data):
        self.model = deepcopy(MODEL)
        self.state = initial_state(self.model)
        self.inputs = exploration_inputs(self.model)
        self.steps = []
        scenario = data.draw(st.sampled_from(SCENARIOS), label="prefix_scenario")
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
