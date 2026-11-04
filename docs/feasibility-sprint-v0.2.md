# One-week feasibility sprint - reviewed revision

Date: 5 November 2026. Window: 5-11 November; supervisor review can follow on 12 November. Status: DRAFT FOR REVIEW. This supersedes proposed future work only after review; it does not change the old pilot's pass rules or reinterpret it as pre-registered.

## Topic statement

We investigate whether an LLM uses a user-supplied example according to its communicative role: transferring an appropriate relation, following a specified part, or avoiding a specified failure while preserving the target task's active constraints. We construct provenance-tracked, human-validated matched examples and study behavioural and causal responses to role, incidental-detail and relational changes. We test whether an intervention or training method improves appropriate transfer without damaging legitimate copying or task performance. Target venue: ACL/EMNLP main conference; novelty and acceptance are not established by this sprint.

## Starting evidence, not final conclusions

The saved pilot contains ten seeds and 390 scored outputs across three models. Its results are useful for debugging, but E2 human annotation is pending, E4's old rule is false for all three models, at least one gold/check mismatch is confirmed, and five logit-lens traces are not causal localization. Read `../results/audit_2026-11-05/README.md` and the paired JSON audit before quoting any percentages.

The WildChat candidate and first-pass label files suggest relevant examples can be found, mostly format/style requirements. Human provenance, retrieval recall and population prevalence are not established. Neither finding few natural analogies nor finding a keyword hit settles whether a high-quality controlled benchmark can be constructed.

## Scope for this week

- Two task families: constrained planning and machine-checkable data/code tasks.
- Approximately 20-30 NEW independent seeds, roughly 100-150 valid constructed variants; context versions are extra evaluations, not new independent seeds.
- Existing ten seeds remain exploratory development material. Preserve old outputs, hashes, scorer versions and old gates.
- Start with the already available small-model pipeline. Use a second model family after data/check validity. A paid API or 14B model is not a feasibility dependency.
- Hardware observed directly on 5 November with `nvidia-smi`: RTX 4060, 8,188 MiB total VRAM (6,888 MiB free at that instant). This is a hardware inventory, not a measured guarantee that training/patching will fit. Runtime and peak memory still need a short trial.
- No full-dataset mining, all-source contamination certification, full GRPO run or five-domain benchmark is promised in seven days.

## Day plan

| Date | Work | Concrete deliverable / dependency |
| --- | --- | --- |
| Thu 5 Nov | Audit existing scores/gates; establish source registry, role/scope definitions, verifier contract and representative human review | Existing-pilot audit, seed-card v0.1, issues list. Audit completed this review; human review pending |
| Fri 6 Nov | Retrieve a bounded candidate sample with contexts; annotate hits and some misses; inspect NaturalInstructions and a licensed analogy source | Source IDs/revisions and licence decisions; human-labeled inclusion decisions; report actual reviewed yield without extrapolating a corpus count |
| Sat 7 Nov | Construct first new seeds in two domains; independent review of prompt entitlements and scope; validate alternative good/bad outputs | Valid seed cards; disagreement log; no hidden lexical bans or stricter-than-prompt thresholds |
| Sun 8 Nov | Reach 20-30 acceptable seed families if feasible; dedup/provenance grouping; lock a new evaluation manifest and planned contrasts before running it | 100-150 valid variants or documented shortfall; immutable manifest; grouped development/held-out allocation; agreed practical effect thresholds |
| Mon 9 Nov | Run behaviour on new accepted cards: direct, principle-then-constraint prompt, no-example, oracle-scope controls and matched role/detail changes | Raw prompts/outputs with exact model revisions and scorer versions; format, task, leakage and useful-transfer errors separately |
| Tue 10 Nov | Full-layer coarse scan on development pairs; controlled patching of a small candidate set with random-location controls; short training feasibility run if time permits | Exploratory intervention effect, collateral-cost measures, GPU-memory/runtime record. No causal result is acceptable as a finding; diagnose why |
| Wed 11 Nov | Held-out check of selected intervention only after selection rule is recorded; seed-cluster uncertainty; dataset/cost synthesis | One-page GO / REVISE / NO-GO decision for sir, open limitations, required resources and next-stage scope |

If independent reviewers are unavailable, label this dependency unmet. Continue source/validator work, but do not replace human labels with AI judgments presented as human agreement.

Update, 5 November 2026: the user confirmed that two human reviewers can give time this week. Availability is confirmed; independent annotations and agreement are still pending. Start with the eight-case legacy calibration pack at `../data/human_review/calibration_v0.1/README.md`, then apply the corrected guide to new seeds. Availability confirmation does not freeze or approve this protocol.

## Decision contract

Set practical effect thresholds and budgets on 8 November before the new held-out evaluations; record who agreed and when. The checklist below defines evidence requirements, not retroactive numerical passes for the saved pilot.

Suggested project decision thresholds for review now (not literature standards): at least 20 acceptable NEW seed families across two domains, independent review by two humans, at least 85% agreement on atomic scope/constraint labels before adjudication, and a separate record of unresolved/removed cards. For behaviour, use a provisional 15-percentage-point practically meaningful role/scope error rate and a 10-point residual gap to the oracle-scope control under the strongest prompt, after separating formatting and unrelated task errors. Report paired seed-level intervals; a wide interval yields REVISE/collect-more, not a confident pass. The oracle control estimates task solvability and is not itself a deployed solution. Candidate thresholds may be changed during review only before new held-out results, with a rationale; historical E4 remains failed under its original rule.

The mechanistic feasibility threshold is a working patching experiment on at least 8 development pairs plus random-location and collateral controls, followed by a small untouched check. It is NOT a requirement to manufacture a successful neuron-off result, and it is NOT enough for a final causal claim. Decide on main-stage investment according to whether the data, evidence and remaining mechanistic risk are acceptable to the supervisor.

| Gate | Required evidence | Decision if missing |
| --- | --- | --- |
| D: Data validity | Two humans can identify the intended role/scope and accept the answer contract; disagreements/adjudication are documented; enough valid new seed families are constructible within the available effort | REVISE data/rubric. If reliable scope cannot be defined, NO-GO for this formulation |
| B: Specific behavioural gap | Repeated useful-transfer or forbidden-import errors on otherwise solvable tasks; paired role/detail controls and oracle-scope results distinguish these from formatting/general task difficulty; report both model families without requiring every model to fail | REVISE task/model choice or NO-GO if no practically meaningful residual problem |
| C: Causal path | At least a credible matched-pair intervention prototype and measured controls/collateral effects, or a precise reason why the mechanistic route remains unresolved | If sir requires a mechanistic paper, cannot claim full GO for that route; a training-only pivot requires an explicit scope amendment |
| F: Feasible execution | Bounded data/annotation effort and a measured runnable intervention/training step; minimal main-paper baselines and budget specified | Reduce a pre-declared scope or NO-GO if the required study cannot fit resources |

Strong prompting closing the behavioural gap is evidence about solution cost, not automatic proof the entire research area is empty. It can remove the proposed training contribution unless robust generalization or efficiency advantages remain.

GO means the next-stage research investment is justified. It does not mean novelty is proven, the main mechanism is known, or a main-conference paper is secured. Unresolved annotation or causal requirements yield REVISE rather than an unsupported GO.

## Layer analysis: investigate, do not assume

Use all layers in a coarse development scan; select candidates with a recorded criterion and then refine. The old layer 23-28 observation is model-/prefix-/token-set-specific. Do not freeze layers 23-36 as the universal failure location.

Patching uses matched inputs and compatible token positions. Test restoring task-relevant decisions, not just increasing a selected token's logit. Compare random locations and same-budget interventions; check general task correctness and legitimate requirement copying. Zeroing a head/neuron can suppress all copying, including correct copying. Also consider mean/replacement controls rather than treating zero ablation as the only valid intervention.

Reserve new seeds for confirmation; do not use the same five diagnostic items to choose and validate a mechanism. A negative patching result does not establish no mechanism exists.

## What is frozen after a GO review

Only after this week's result review: main research questions, data inclusion/gold rules, provenance split, primary metrics/contrasts, model snapshots/budgets, selection/confirmation separation and amendment procedure. Layer numbers, a successful ablation and a winning loss are not preordained conclusions.

Use `paper-protocol.md` as the main-stage draft. Record any approved scope amendment before running the changed confirmatory test. Exploration is allowed within its declared lane and is reported as exploration. New hypotheses after observing test outcomes need new held-out confirmation.
