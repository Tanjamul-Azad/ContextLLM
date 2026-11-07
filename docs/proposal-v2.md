# Role-Aware Example Use in LLMs: Research Proposal v2

7 November 2026 · Tanjamul Azad

**Working title:** "That Was Just an Example": Learning Role-Aware Selective Transfer in LLMs. **Area:** NLP, instruction following, analogical transfer, mechanistic interpretability. **Target:** ACL or EMNLP main track; submission timing follows validated results.

## Summary

When a user gives an LLM an example, the example has a role. It may show an idea to borrow (analogy), a part to follow exactly (requirement), or something to avoid (counter-example). A good answer takes only the part the role allows and keeps the user's own rules. We study whether models do this, where inside the model it goes wrong, and whether targeted training fixes it.

**What we have so far.** A pilot on 10 seeds and 6 models, 780 scored answers in all, suggests the problem is real. On plain prompts, open models (3B to 8B) fail 40–47% of the time and frontier GPT models 17–30%. Spelling out what to take helps frontier models (0–7% failure) but not open ones (27–33%). These numbers are provisional: the pilot seeds were not human-validated, and an audit found checker errors that we have since corrected.

**What we ask for.** Approval of a one-week validation step (7–12 November), and decisions on the open design questions in the final section, so the full protocol can be frozen.

## 1. Problem and research questions

A user asks for a ticket-priority scheme for a university IT help desk, with at most three levels, and cites hospital triage. The principle "urgent cases first" should transfer; the hospital's colour codes and minute-based times should not. If the user instead says the faculty already uses those colour codes, the colour names become required. The same example therefore calls for different answers depending on its role, and the correct answer is fixed by the prompt, not by the example alone.

- **RQ1.** When only the role of an example changes, do LLMs change what they transfer accordingly, while keeping the target constraints?
- **RQ2.** Which internal components carry the role and drive the transfer of source details? We locate them on development data and test them causally on held-out data.
- **RQ3.** Does training that supervises transfer scope improve role-correct transfer on unseen tasks, beyond prompting and ordinary fine-tuning?

## 2. Related work and novelty

| Work | What it studies | What it leaves open |
| --- | --- | --- |
| [Copy bias in ICL](https://aclanthology.org/2026.findings-eacl.13/) (Findings of EACL 2026) | Models copy labels from demonstrations; pruning a few MLP neurons reduces it | Copying is always wrong there; it never tests when copying is required |
| [Overthinking the Truth](https://arxiv.org/abs/2307.09476) (ICLR 2024) | Late layers overwrite correct answers with copied false demonstrations; ablating 5 heads helps | Demonstrations are false labels, not user examples with a role |
| [Do as I Say, Not as I Do](https://arxiv.org/abs/2605.20382) (COLM 2026 workshop) | Instructions lose to in-context pattern pressure | Examples are always to be resisted |
| [AnaloBench](https://aclanthology.org/2024.emnlp-main.725/) (EMNLP 2024), [ARN](https://arxiv.org/abs/2310.00996) | Finding analogies between stories | Identifying an analogy, not using one under constraints |
| [LLMs Get Lost in Multi-Turn Conversation](https://arxiv.org/abs/2505.06120) (2025) | Performance loss when instructions arrive over turns | The example's role is not a variable |
| [ReTRE](https://aclanthology.org/2026.acl-long.2048/) (ACL 2026) | Robustness to rewrites; SFT overfits, RL holds up | Transfer from the model's own knowledge, not from a user's example |

**Proposed novelty.** A benchmark in which the same example appears in different roles, with a prompt-grounded gold scope (must use, may use, must not use). A causal comparison of harmful and useful transfer inside the model. A training objective that supervises transfer scope. Neuron pruning alone is not claimed as new. A full-text novelty audit is part of the validation week.

## 3. Preliminary evidence (pilot, 4–5 November)

The pilot tested whether the effect exists and whether the pipeline works. It used 10 hand-written seeds (6 planning tasks with JSON answers, 4 code tasks with unit tests), each in 3 roles, with plain and explicit wording, single- and multi-turn, plus a no-example baseline: 130 prompts per model, scored automatically.

Failure rate, single-turn, 10 seeds × 3 roles per model (scorer v1.1):

| Model | Plain wording | Explicit wording |
| --- | --- | --- |
| Qwen2.5-3B | 47% | 33% |
| Qwen2.5-7B (4-bit) | 40% | 30% |
| Llama-3.1-8B (4-bit) | 43% | 27% |
| GPT-4.1-mini | 23% | 7% |
| GPT-5.4-mini | 17% | 0% |
| GPT-5.4 | 30% | 3% |

- **Open models are not rescued by prompting.** Explicit wording cuts their failure by 10–16 points only. This leaves room for a training method.
- **Frontier models fail mainly when the role is implied.** Their remaining problem is inferring the role from context, which sharpens the research question.
- **Typical failures** (read by hand): Qwen2.5-3B used the hospital colour names after being told not to; GPT-5.4 dropped a required plan name; GPT-4.1-mini pasted email-cleaning code onto usernames, which crashed.
- **Inside the model** (Qwen2.5-3B, logit lens, 5 probes): the roles' predictions separate around layers 23–28 of 36. This is a read-out that tells us where to look, not causal evidence.
- **Real conversations:** hand-checked samples of WildChat-1M and OASST2 show users mostly give "follow this format" examples; analogies and counter-examples are rare.
- **Contamination diagnostics** on GSM8K, Super-NaturalInstructions, HumanEval, Spider and AnaloBench flagged none (Qwen2.5-3B, 50–60 items each). These are diagnostics, not certificates of clean data.

**Limits.** Ten seeds give wide intervals. The seeds and gold checks were not independently reviewed. An audit found checks that were stricter than the prompt and a scorer that counted format errors as leakage; both were fixed and all answers rescored. The pilot is development evidence only and will not be reused as test data.

## 4. Study design

1. **Validated benchmark:** 120–200 seeds, two blind reviewers, MUST / MAY / MUST NOT scope.
2. **Behaviour study:** no example, plain, scope-inference prompt, oracle; open and frontier models.
3. **Mechanism:** scan layers on dev; patch and ablate on test, with random controls.
4. **Targeted training:** scope-consistency LoRA against prompting, SFT and all-layer LoRA.

A validation week (7–12 November, 20–30 seeds) ends in go, revise or stop. No behaviour, mechanism or training result is reported on data that has not passed human review.

## 5. Benchmark design

**Unit.** A seed is one target task, one source example, the relation that may transfer, the target constraints and a gold scope. Role changes, paraphrases and detail substitutions are variants of that seed; they are never counted as independent items and never split across train and test.

**Task families.** Planning and decision tasks with a structured (JSON) answer, and code or data-transformation tasks with unit tests.

**Variation axes.** Role (analogy, requirement, counter-example); target fit (the relation fits fully, partly or not at all); role cue (stated, or only inferable from context); single-turn, with an information-equivalent multi-turn subset. Combinations that make no sense are recorded as not applicable, with a reason.

**Gold scope.** Every item lists, with the prompt text that supports it:

| Field | Meaning |
| --- | --- |
| MUST USE | Relation or detail the answer is required to use |
| MAY USE | Allowed but optional; using it is not a failure |
| MUST NOT USE | Use breaks an explicit prohibition or a target constraint |
| Target constraints | Rules of the user's own task |

An optional detail that appears in an answer is not counted as leakage. Checkers are validated on correct alternative answers, paraphrased errors and negated mentions.

**Sources.** Original scenarios, documented real cases adapted with their provenance recorded, real user requests from WildChat and OASST2 (paraphrased, never released verbatim), and parts of public datasets (Super-NaturalInstructions, AnaloBench, ARN, Lost in Conversation). Fictional scenarios are labelled as fictional. AI-assisted drafts are labelled and reviewed like any other item.

**Annotation.** Two annotators review each seed blind and independently, then disagreements are adjudicated. We report agreement before adjudication: Cohen's kappa on role labels, and agreement on predefined atomic scope items for MUST / MAY / MUST NOT. Rejected and ambiguous items are reported. An author never serves as the blind reviewer of their own seed.

**Size.** 20–30 reviewed seeds in the validation week; then batches of 20 up to 120–200 accepted benchmark seeds, about 4–6 variants each. A separate training pool of 200–500 seed groups is planned only if the training study goes ahead. Final sizes follow the variance observed in the validation set.

**Splits and contamination.** Seeds are grouped by source, story and template before splitting; held-out task families or relations test generalisation. Controlled perturbations are logged separately from contamination. Recall and Min-K% Prob diagnostics are reported with their limits; rewriting is not treated as a guarantee of clean data ([Sun et al., ICML 2025](https://proceedings.mlr.press/v267/sun25t.html)). A hidden test split is run only through APIs with a no-training data policy.

## 6. Mechanism study

We make no prior claim about where the mechanism sits; it may be early, middle, late or distributed. Components are selected on development data only and locked before any test evaluation.

1. **Locate (dev).** Logit lens and probes with lexical controls on matched pairs that differ only in role.
2. **Test causally (held-out).** Activation patching by layer and by head on token-aligned pairs, with a check of how sensitive the result is to the patching metric ([Zhang and Nanda, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/06a52a54c8ee03cd86771136bc91eb1f-Abstract-Conference.html)).
3. **Intervene.** Ablate the selected heads or neurons and measure harmful transfer, useful transfer and joint success together. Removing useful transfer along with the harmful kind counts as a failure.
4. **Controls.** Random ablations of the same size, random components within the same layers, and a general-ability check on held-out items (for example GSM8K and MMLU).

Models: Qwen2.5-3B in bf16 on local hardware, a second 3–4B model from another family, and one 7–8B confirmation run on rented GPU time.

## 7. Method, baselines and evaluation

**Proposed objective.** LoRA fine-tuning with three terms: task supervision (a valid target answer), scope supervision (required, optional and prohibited transfer), and paired consistency (answers stay the same when only incidental details change, and change when the role or scope changes). Consistency is measured on gold-defined answer properties, not on wording. Gold scope is used in training only; at test time the model must infer the scope from the prompt. If the mechanism study locates the role causally, the same objective is also applied only in those layers.

**Baselines,** each with the same data and the same tuning budget: a practical scope-inference prompt (the model is asked to work out what to take, without being given the gold), SFT, and LoRA on random or all layers with an equal parameter count. A scope-explicit prompt that states the gold is reported as a diagnostic oracle, not as a baseline. DPO or GRPO are added only if the claim needs them and compute allows; ReTRE (ACL 2026) found that RL generalises better than SFT on transfer, so GRPO is the first candidate.

**Metrics.** Primary: joint success (required transfer achieved, target constraints kept, no prohibited transfer). Secondary: appropriate transfer, harmful transfer, constraint retention and role sensitivity. Format failures are reported separately. A large requirement-versus-counter-example copying gap is a sanity check, not evidence of failure.

**Statistics.** Seed-level bootstrap intervals and paired tests, because variants of one seed are correlated. Primary comparisons, test families and the correction method are fixed at protocol freeze. Training results are averaged over 3 seeds, with general-ability drift reported alongside.

## 8. Feasibility plan and timeline

**Validation week**

| Date | Work | Output |
| --- | --- | --- |
| 7–8 Nov | Timed, independent calibration on the revised review pack; reference and checker audit | Two reviewers' answers, time per item, ambiguity log |
| 8–9 Nov | Revise seeds; add new independent seeds; validate checkers | 20–30 reviewed development seeds |
| 10 Nov | One local and one frontier model on the validated prompts: no-example, plain, scope-inference prompt, oracle | Saved outputs, manual error audit, seed-level intervals |
| 11 Nov | Dev-only patching prototype with controls; training smoke test if time allows | Compute and memory record |
| 12 Nov | Supervisor review | Go, revise or stop |

**Go requires all four:** (1) annotators agree on role and scope well enough, at a workload we can sustain; (2) a reproducible failure remains on validated prompts after practical prompting, and is not explained by task inability or checker error; (3) a clear difference from the closest prior work; (4) the intervention and training pipeline runs within our resources. Numeric thresholds are fixed before the 10 November run. Incomplete evidence means revise, not go.

**After a go**

| Period | Work |
| --- | --- |
| Nov 2026 – Jan 2027 | Benchmark to 120–200 seeds; full behaviour study |
| Feb – Mar 2027 | Mechanism study; proposed objective against baselines |
| Apr – May 2027 | Held-out evaluation, ablations, writing; submission to the next suitable ARR cycle |

**Compute and budget.** Local RTX 4060 (8 GB) and RTX 5070 Ti (16 GB) cover the pilot, 3–4B mechanism work and QLoRA training. Final 7–8B runs need about 150–300 A100-hours. The pilot's three OpenAI models together cost under one US dollar; we propose a cap of USD 10 for the validation week.

## 9. Risks and decisions requested

| Risk | Response |
| --- | --- |
| Annotators cannot agree on scope | Redesign seeds and rules; report as revise, not go |
| Frontier models no longer fail once prompts are validated | Focus on inferred roles and open models; the paper becomes a benchmark and analysis contribution if training adds nothing |
| Overlap with copy-bias or instruction-conflict work | Centre the claim on role-dependent use, where copying is sometimes required |
| No clear causal mechanism | Report behaviour and training results; describe the mechanism findings as exploratory |
| Collection is slower than planned | Size targets follow measured acceptance rate and time per seed |

**Fallback topic:** hallucination detection from internal model signals, limited to one failure type.

**Decisions requested from the supervisor**

- [ ] Approval of the validation week and its go / revise / stop criteria
- [ ] The two task families, and the source and authoring policy
- [ ] Reviewer arrangement: who reviews the seeds written by whom
- [ ] Whether to add a Bangla and cross-lingual subset now or as a later study
- [ ] Compute support for the 7–8B runs, and the API budget
- [ ] Scope of the training contribution and its baselines

## References

- Ali, Wolf and Titov. [Mitigating Copy Bias in In-Context Learning through Neuron Pruning](https://aclanthology.org/2026.findings-eacl.13/). Findings of EACL 2026.
- Halawi, Denain and Steinhardt. [Overthinking the Truth: Understanding how Language Models Process False Demonstrations](https://arxiv.org/abs/2307.09476). ICLR 2024.
- Camassa and Shiller. [Do as I Say, Not as I Do: Instruction-Induction Conflict in LLMs](https://arxiv.org/abs/2605.20382). COLM 2026 workshop.
- Ye et al. [AnaloBench](https://aclanthology.org/2024.emnlp-main.725/). EMNLP 2024.
- Sourati et al. [ARN: Analogical Reasoning on Narratives](https://arxiv.org/abs/2310.00996). 2023.
- Laban et al. [LLMs Get Lost in Multi-Turn Conversation](https://arxiv.org/abs/2505.06120). 2025.
- Li et al. [ReTRE: Benchmarking LLM Transfer Robustness with Structure-Preserving Variants](https://aclanthology.org/2026.acl-long.2048/). ACL 2026.
- Zhang and Nanda. [Towards Best Practices of Activation Patching](https://proceedings.iclr.cc/paper_files/paper/2024/hash/06a52a54c8ee03cd86771136bc91eb1f-Abstract-Conference.html). ICLR 2024.
- Sun et al. [Contamination mitigation study](https://proceedings.mlr.press/v267/sun25t.html). ICML 2025.
- Artstein and Poesio. [Inter-Coder Agreement for Computational Linguistics](https://aclanthology.org/J08-4004/). Computational Linguistics 2008.
- Golchin and Surdeanu. [Time Travel in LLMs: Tracing Data Contamination](https://arxiv.org/abs/2308.08493). ICLR 2024.
- Shi et al. [Detecting Pretraining Data from Large Language Models](https://arxiv.org/abs/2310.16789). ICLR 2024.

Code, saved outputs and supporting documents: [github.com/Tanjamul-Azad/ContextLLM](https://github.com/Tanjamul-Azad/ContextLLM).
