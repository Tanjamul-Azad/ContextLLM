# Fixed goal and kill tests

13 November 2026. Written before either test is run, so the result cannot move the goalposts. Changing anything here later needs a dated entry in the deviation log at the bottom.

## 1. The goal

**Paper goal.** A main-track ACL or EMNLP paper (EMNLP 2027 target) whose core is a validated benchmark of role-dependent example use, plus a causal explanation of the failure. A training method is added only if it clears its gate.

**One-sentence claim we are testing (not yet a result).** When a user gives an example, models do not adjust what they take from it to its role; for open models the failure lies mainly in inferring the role, for frontier models mainly in acting on a role they have inferred.

**What is new, after the 13 November novelty check.** The evaluation object: one example under three roles, a prompt-grounded licence (MUST / MAY / MUST NOT), and scoring of both over-transfer and under-transfer against the user's own constraints. The "knows but does not use" framing alone is not new (Li et al. 2026, arXiv 2608.12321; Lu et al., EMNLP Findings 2024). The mechanism part counts as new only if it separates role-inference failure from licence-execution failure.

**What stays fixed:** the research question, the two task families (decision tasks with JSON answers, code tasks with unit tests), the three roles, the gold-scope format, joint success as the primary measure, and the tier plan in `artifacts/strengthening-plan-2026-11-13.md` Section 7.

## 2. Kill test 1: does the failure survive validation?

**Question.** On human-validated prompts, do models still fail often enough to matter, under realistic wording, after a practical prompting fix?

**Setup.** `src/run_validation.py`. Four conditions per variant: no example, plain (the variant as written), scope-inference prompt (the model is told to decide what to take before answering), oracle (the gold MUST / MUST NOT items are stated). At least one open model (Qwen2.5-7B, 4-bit) and one frontier model (GPT-5.4-mini). Only cards whose human review is complete count; runs on draft cards are labelled DEV and are never evidence.

**Pass (all three):**
1. Plain-condition failure on implied-cue variants is at least 20% for the open model or at least 10% for the frontier model, with a seed-level 95% bootstrap interval whose lower end is above 5%.
2. The scope-inference prompt leaves at least half of that failure in place (otherwise the problem is solved by a prompt and the paper weakens to a prompting note).
3. In the no-example condition, the task itself succeeds at least 80% of the time (otherwise failures reflect task difficulty, not example use).

**Fail →** the problem is too easy or prompt-solvable. Stop and redesign seeds (longer contexts, weaker cues) before any further work; do not move to the mechanism.

## 3. Kill test 2: can the failure be located inside the model?

**Question.** In plain prompts, can the example's role be read from the model's hidden states, and does inserting the role-correct state repair a failing answer?

**Setup.** `src/role_probe_patch.py`, Qwen2.5-3B in bf16, development cards only (never test items).
- **Probe with a lexical control.** Train a per-layer role probe on stated-cue variants and test it on implied-cue variants, grouped by seed so no seed is in both. Implied prompts do not contain the role words, so a probe that transfers is reading something beyond the cue words. A bag-of-words classifier trained and tested the same way is the lexical baseline.
- **Failure typing.** Only failures where the stated twin (same seed, role and fit) succeeds count, so task difficulty is excluded. For each such failing implied variant: if the probe reads the right role, it is an execution failure; if not, an inference failure.
- **Patching.** For each such failing implied variant, copy the last-prompt-token hidden state at layer L from the stated variant of the same seed, role and fit, then regenerate and rescore. Controls: the same patch taken from a different role of the same seed, and a random direction of the same norm.

**Pass (Tier B stays open) when both hold:**
1. Probe accuracy on implied variants is at least 70% at some layer (chance is 33%) and at least 15 points above the bag-of-words baseline.
2. Patching repairs at least 25% of failing variants at the best layer, at least 15 points more than each control.

**Partial →** the probe passes but patching does not: report failure typing only; Tier B becomes exploratory.
**Fail →** the paper targets Tier A (benchmark plus behaviour), and the mechanism is reported as a negative result.

**Limits we accept now.** One position (the last prompt token), one model, 10 draft cards. A pass justifies the full study; it is not evidence for the paper. All layers selected here are fixed before any held-out run.

## 4. Order

1. Kill test 2 can start now on the draft cards (development use is allowed).
2. Kill test 1 counts only after the E2 human review marks cards as validated; a DEV run on drafts checks the pipeline.
3. Both results, pass or fail, are written into `RESULTS.md` and this file's log, then the tier is chosen.

## Deviation log

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-13 | Kill test 1 open model changed from Qwen2.5-3B to Qwen2.5-7B, before any counted run | Dev smoke test: Qwen2.5-3B fails the v1 tasks even with no example (C01, D01), so it cannot pass the task-solvable check; failures would reflect model weakness, not example use |
