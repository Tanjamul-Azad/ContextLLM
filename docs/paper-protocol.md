# Paper protocol: role-aware example use

**Status: DRAFT, not frozen.** It is frozen when Tanjamul and sir sign the checklist at the end. After that, every experiment follows this file. Any change goes in the deviation log first, with a reason and an approval.

Target: EMNLP 2027 main track (ARR cycle, date to confirm). The pilot ([RESULTS.md](../RESULTS.md)) only showed the pipeline works and the effect exists; none of its seeds or numbers go into the paper.

## 1. Claims

The paper makes three claims. Each has one deciding experiment.

| # | Claim | Deciding experiment | Supported if |
| --- | --- | --- | --- |
| C1 | LLMs, open and frontier, often fail to use a user's example according to its role: they leak incidental details, miss the needed relation, or drop the user's constraints | Behavioural study on the full benchmark (section 5) | H1 and H2 hold |
| C2 | Inside the model, the example's role is resolved in late layers, and a small set of components drives the copying of source details | Mechanism study (section 6) | H3 and H4 hold |
| C3 | Training aimed at those layers improves role-correct transfer on unseen task families, beyond prompting, SFT, DPO and GRPO | Method study (section 7) | H5 holds |

If C3 fails, the paper becomes a benchmark-and-analysis paper built on C1 and C2. That fallback is decided now, not after seeing results.

## 2. Hypotheses and pass marks (fixed before any paper run)

| # | Hypothesis | Test | Pass mark |
| --- | --- | --- | --- |
| H1 | Models fail often | Joint-success failure on plain, single-turn items, per model | ≥ 25% failure for at least 4 of 6 models, including at least one frontier model |
| H2 | The role matters | Copy-rate gap: requirement minus counter-example, same content | ≥ 15 points, 95% seed-bootstrap interval above 0, in at least 4 of 6 models |
| H3 | The role is resolved in late layers | Activation patching between matched role pairs | Patching one contiguous block of ≤ 25% of layers restores ≥ 50% of the role effect |
| H4 | A few components drive copying | Ablating the top-k heads or neurons chosen on dev, evaluated on test | Leakage falls by ≥ 30% relative, appropriate transfer falls by ≤ 5 points, and both beat the random-ablation control (p < 0.05) |
| H5 | Targeted training works | Joint success on held-out task families | Beats the best baseline by ≥ 5 points, interval above 0, averaged over 3 training seeds |

Multiple comparisons: Holm correction across H1–H5's primary tests.

## 3. Benchmark specification

**Unit.** A seed is one target task, one source example and a gold specification. Variants of a seed never cross splits.

**Size.** 150 seeds, about 1,500 variants. At least 40 seeds per task family.

**Task families.**

1. Decisions and plans with a JSON answer (schemes, policies, pricing, evaluations).
2. Code and data tasks with unit tests.

**Variation axes.** Every seed covers all meaningful cells.

| Axis | Levels |
| --- | --- |
| Role | analogy, requirement, counter-example |
| Target fit | the relation fits fully, partly, or would be wrong to apply |
| Role cue | stated ("don't do it like this") or implied (only context shows the role) |
| Turns | single-turn, information-equivalent multi-turn |
| Incidental-detail control | same role and relation, different incidental details |

**Every seed must meet all of these (checked by script or annotator):**

- [ ] Built on a real, citable case or a real user request (source recorded in the seed).
- [ ] The source example is at least 8 sentences long. A long variant of 20 or more sentences exists for 30% of seeds.
- [ ] The example contains at least 3 incidental details that must not transfer.
- [ ] A counter-example shares at least 3 surface features with the target task, so it looks applicable.
- [ ] The gold specification lists what must transfer, what must not, and the target rules, each with an automatic check.
- [ ] Realism rated 4 or 5 out of 5 by both annotators.
- [ ] Implied-cue variants make up half of all variants.

**Sources and quotas.** No source may supply more than 40% of seeds.

| Source | Used for |
| --- | --- |
| Real WildChat / OASST2 requests (paraphrased) | Requirement seeds, phrasing of examples |
| Documented real cases (business, engineering, science, policy) | Analogy and counter-example seeds |
| Super-NaturalInstructions positive and negative examples | Requirement and counter-example seeds |
| AnaloBench, ParallelPARC, ARN | Analogy pairs and surface-similar distractors |
| Lost in Conversation tasks | Target tasks with checkers |
| Fresh seeds written after the models' cutoffs | At least one third of the test split |

**Annotation (E2 at scale).** Two annotators label every seed independently: what must transfer, what must not, and realism. Seeds are kept only when both agree on the transfer scope. Agreement is reported as Cohen's kappa, with kappa ≥ 0.6 required overall.

**Splits.** By seed: 50% train, 15% dev, 35% test. Two task sub-families (named before data collection) are held out of training entirely. A hidden test split of 30 seeds is run only on paid APIs with a no-training data policy.

**Contamination.** Every reused source goes through guided completion, Min-K% Prob and original-versus-rewrite before entering test. A source is flagged at more than 5% near-verbatim recall. Flagged items are rewritten and retested, or moved to train. Test files carry a canary string.

## 4. Models (versions pinned on the run date)

| Role in paper | Models |
| --- | --- |
| Behaviour, open | Qwen2.5-3B, Qwen2.5-7B, Llama-3.1-8B, Llama-3.3-70B (Groq) |
| Behaviour, frontier | Gemini 2.5 Flash; one OpenAI model (GPT-4.1-mini, or GPT-4.1 if budget allows) |
| Mechanism | Qwen2.5-3B (bf16) and a second, non-gated 3–4B model from another family |
| Method | Qwen2.5-3B, then Qwen2.5-7B or Llama-3.1-8B with QLoRA |

Decoding: greedy for main results. A robustness subset of 300 items is also run with 3 samples at temperature 0.7.

## 5. Behavioural study

- **Metrics.** Primary: joint success. Secondary: appropriate transfer, detail leakage, constraint retention, copy-rate gap by role.
- **Baselines inside the study.** A no-example version of every task, and a relation-stated version.
- **Statistics.** Seed-level bootstrap, 10,000 resamples. Paired permutation tests for within-seed comparisons. Effect sizes are always reported with intervals.
- **Error analysis.** 100 failed answers, sampled at random and labelled by type.

## 6. Mechanism study

1. **Logit lens and tuned lens** on matched role pairs (dev split).
2. **Linear probes** for role on every layer, with lexical controls: the same role words in a neutral context.
3. **Activation patching**, by layer and then by head, between pairs that differ only in role.
4. **Ablation** of the top-k components chosen on dev, evaluated on test, with k ∈ {1, 5, 10, 1% of the layer}.
5. **Controls, all required.**
   - Random ablation of the same size, 5 draws.
   - Random ablation within the same layers.
   - General-ability check on 200 GSM8K and 200 MMLU items, to show nothing else broke.
6. **Report** leakage, appropriate transfer and joint success. Removing copying while also removing useful transfer counts as a failure, not a success.

## 7. Method study

- **Proposed method.** A specification-conditioned consistency objective with three parts (task supervision, transfer-scope supervision, paired consistency), applied with LoRA only in the layers found in section 6.
- **Baselines, same data and the same tuning budget.**
  - Prompting.
  - SFT.
  - DPO.
  - GRPO with the automatic checkers as reward.
  - Retraining only the last layers.
  - LoRA in all layers.
- **Tuning budget.** Each method gets the same grid of 8 configurations on dev. The best is chosen on dev only.
- **Evaluation.** Test split and the held-out families, with 3 training seeds. Also report general-ability drift on the same 400 items as in section 6.
- **Ablations.** Remove each objective part in turn, and compare targeted layers against random layers of the same count.

## 8. Reporting rules

- Every number in the paper traces to a file in `results/` and a logged command.
- Post-hoc analyses are labelled as post hoc.
- Hand-picked examples are labelled, and a random example is shown beside each one.
- Limitations are written before the results section.

## 9. Deviation log

| Date | Section | Change | Reason | Approved by |
| --- | --- | --- | --- | --- |
| | | | | |

## 10. Freeze checklist

- [ ] Claims and hypotheses (sections 1–2) agreed with sir.
- [ ] Pass marks agreed with sir.
- [ ] Seed rules (section 3) agreed.
- [ ] Two held-out task sub-families named.
- [ ] Model list and API budget confirmed.
- [ ] Second annotator confirmed.
- [ ] Signed: Tanjamul Azad, date ____
- [ ] Signed: supervisor, date ____
