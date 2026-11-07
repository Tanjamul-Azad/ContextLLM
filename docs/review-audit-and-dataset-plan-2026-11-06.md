# Review audit and proposed dataset plan

Date: 6 November 2026. Status: proposed amendments, NOT a frozen protocol.
This audit does not certify novelty, citation validity, contamination freedom,
model performance or venue acceptance. Existing protocol, seed cards, results and
v1 reviews have not been modified. No API calls or model experiments were run.

## Verified local state

- 10 draft seed cards, 68 variants: 28 analogy, 20 requirement, 20 counter-example.
- Fit coverage: 58 full, 6 partial, 4 wrong. This is not a balanced final design.
- 95 author-flagged ambiguous checks in both cards and current Part 2 (not 113).
- Both v1 Part 1 files have 204 empty answer fields; no completed local review.
- All 10 cards still have reference verification pending. This does not establish
  that references are false; existence AND support for used facts need checking.
- Original exporter omits all 10 variant-specific rules_add entries and output
  format, although build_messages includes them for the model. Such reviews do
  not validate the full evaluated prompt.
- v1 has no MAY USE, evidence or prior-exposure fields. Both Part 2 reviewers
  would enter answers in a shared table.
- Six saved generation files contain 130 unique items each: 780 outputs total.
  These are saved old-pilot outputs, not validated performance on the new seeds.
  RESULTS.md still contains obsolete statements such as 390 outputs and no API
  model, alongside newer frontier results. Do not use it unchanged in a report.
- local_only/.env is currently ignored by Git and is not tracked. Its contents
  were not read. Ignoring a file is not a guarantee against every future upload.

## Repair delivered

scripts/prepare_review_v1_1.py writes data/human_review/v1_1_draft/ without
overwriting old reviews. Each reviewer receives all 68 complete prompts in a
different order, with stable item codes, evidence and scope fields. Exact prompt
equality with build_messages was checked for every item in both packs. Separate
Part 2 files contain the 95 flagged checks. No gold labels or outputs in Part 1.
Both reviewers must submit Part 1 before either opens Part 2. Related variants
remain correlated and can cue reviewers; record this limitation. Realism is now
rated per full prompt, not averaged over incompatible variants.

## Amendments needed before protocol freeze

1. Human validity first: distinguish optional detail use, harmful transfer,
   explicit prohibition and genuine ambiguity. Not-needed does not imply banned.
   Unnecessary helper functions, harmless names and discussion of rejected details
   must not automatically count as behavioral leakage. Validate semantic errors
   as well as term matching; test paraphrases, negations and alternative solutions.
2. Report pre-adjudication agreement on defined units. Role labels permit nominal
   agreement measures. Free-text MUST/MAY/MUST NOT answers need a defined atomic
   alignment/coding stage, not direct kappa. Do not count agreement after discussion
   as independent agreement. Report rejected and ambiguous items too.
3. C2/H3 must allow early, middle, late or distributed mechanisms. Scan on dev;
   lock selected components before test. Patching design, token alignment and
   random/matched-layer controls need validation. Read-out is not causal evidence.
4. Requirement-minus-counter copying is a role sensitivity check, not proof of
   failure: an ideal model can have a large positive gap. Use prompt-grounded
   violations, preserved task ability and paired controls to establish the failure.
5. Original/rewrite comparisons, recall and Min-K are diagnostics, not certificates.
   Rewriting does not certify uncontaminated data. Fresh authoring reduces known
   exposure but does not prove every underlying relation is absent from training.
6. Keep a no-example control and a relation/scope-explicit control. Also test a
   practical prompting baseline that infers the scope without being given gold.
   Explicit gold instructions change the available information; distinguish this
   diagnostic oracle from a deployable baseline.
7. Calibrate difficulty, length and coverage rather than imposing eight sentences,
   three forbidden details or every role/fit combination regardless of semantics.
   An inferred role must remain inferable to humans. Do not manufacture difficulty
   through missing information or contradictions.
8. Budget experiments. SFT, the proposed objective, prompting and equal-parameter
   random/all-layer LoRA are a practical initial comparison. DPO/GRPO are not
   universally mandatory; add when relevant to the claim and compute-feasible.
   Statistical comparison families and primary metrics need an explicit plan;
   a blanket Holm correction across heterogeneous H1-H5 is insufficient detail.
9. Replace 'effect exists' with provisional evidence until gold and scorers are
   independently validated. Preserve raw outputs and scorer version history.

## Realistic collection plan (proposal for supervisor review)

The independent unit is a seed: target task + source example + intended relation
+ target constraints + evidence-grounded transfer scope. A paraphrase, role flip
or detail substitution is a variant, not another independent seed.

Phase 1: now to 12 November, 20-30 reviewed development seeds total if staffing
permits. Start with the current 10 after repair; add 10-20 genuinely distinct
seeds. Failure to reach this by the date yields REVISE, not automatic freeze.

Phase 2: after feasibility, expand in batches of 20 to an initial 120-200 accepted
benchmark seeds across 2-3 well-defined domains. Use roughly 4-6 meaningful core
variants, with fit/length/multi-turn/detail diagnostics on selected subsets.
Numbers are planning targets, not a claim of statistical power or acceptance.
Choose final held-out counts using pilot variance and the minimum useful effect.

Phase 3: a separate training pool, provisionally 200-500 seed groups if collection
and compute permit, with controlled augmentation and learning curves at several
sizes. Never describe many variants of a few templates as diverse training data.
Benchmark seeds alone do not establish sufficient data for a training contribution.

Each contributor first submits 10 candidate seeds with source, exact excerpt or
original-authoring declaration, adaptation notes, license/consent status, task,
relation, constraints and scope evidence. Time this batch before assigning 100.
After calibration, batches of 20 are reviewed. '100 per person' is a candidate
collection target, not a promise of 100 accepted independent seeds. Prefer distinct
relation/domain coverage over names-and-numbers substitutions. Authors do not
serve as independent blind reviewers of their own seeds. With only two people,
use a separate author/proposer or disclose author-plus-reviewer validation; AI
drafts also need independent human review, and prompt/gold exposure is recorded.

Record drafting time, review time per reviewer, adjudication time and acceptance
rate. For accepted-seed target N and observed acceptance fraction a, plan roughly
N/a candidate seeds. Compute hours from measured times, not an assumed 2-3 hours.

Sources can be original human scenarios, verified real requests, documented-case
adaptations or AI-assisted drafts. Label the origin honestly. A fictional scenario
does not need an invented real-world citation; external factual claims do need
support. Start with English for controlled scope unless the team explicitly chooses
Bangla; multilingual expansion is a separately validated study.

Pipeline: collect candidates -> verify provenance and relevance -> blind scope
review -> adjudicate/revise -> validate checkers against valid and invalid answers
-> cluster source/template/near-duplicate groups -> allocate splits -> augment
within splits -> lock confirmatory test -> evaluate once analysis is fixed.
Maintain provenance/parent IDs through every merge. Never randomly split variants.
For relation-generalization claims, hold out relations too, not just stories.
AI generation for training may see training material only, not held-out examples.

Keep a small separately analysed natural or human-authored validation slice to
test whether findings extend beyond controlled templates. Do not infer real-world
prevalence from balanced constructed examples or keyword-filtered chat samples.

## Decision week

- 6-7 November: corrected pack, timed calibration, references/checker review,
  explicit agreement schema; independent answers before discussion.
- 8-9 November: validate current seeds; add independent candidates; record rejected
  items and uncertainty. Lock a small untouched feasibility set before model runs.
- 10 November: one local and one capable API model on validated prompts; compare
  no-example, original, practical scope-inference prompting and explicit oracle.
  Set an API spend cap before running. Saved older results are not confirmation.
- 11 November: small dev-only patching prototype and controls, compute/memory
  measurement; a training smoke test if possible, not a claimed method win.
- 12 November: GO / REVISE / NO-GO with supervisor. Freeze only if data validity,
  residual reproducible failure, literature distinction and resource feasibility
  are supported. A calendar date cannot determine scientific readiness.

Freeze claims/questions, exclusion rules, splits, primary metrics, analysis,
baseline budget and stopping criteria. Do not freeze a desired result. Amendments
remain possible through an explicit dated log; already inspected data become
development evidence and are not repurposed as untouched confirmation.

## Checked methodological sources

- Artstein & Poesio, Computational Linguistics 2008, inter-coder agreement:
  https://aclanthology.org/J08-4004/
- Zhang & Nanda, ICLR 2024, sensitivity of activation patching to metrics and
  corruption choices:
  https://proceedings.iclr.cc/paper_files/paper/2024/hash/06a52a54c8ee03cd86771136bc91eb1f-Abstract-Conference.html
- Sun et al., ICML 2025, limitations of benchmark contamination mitigation:
  https://proceedings.mlr.press/v267/sun25t.html

These support methodology; this audit is not an exhaustive related-work search.
