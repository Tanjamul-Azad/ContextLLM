# “That Was Just an Example”: Learning Role-Aware Selective Transfer in LLMs

2026-11-04 · Tanjamul


Sir approved this topic on 3 November 2026. This version adds his feedback: real-world data, merged datasets and experiments inside the model's layers. A one-week feasibility sprint (5–11 November) decides go or no-go on 12 November. Target: EMNLP 2027 main track.

## At a glance

People often explain what they want through an example. Sometimes the example should be followed exactly, sometimes only its idea should be borrowed, and sometimes it shows what to avoid. We test whether LLMs can tell these apart, find where inside the model the wrong parts get copied, and train the model to fix it.

*[Diagram, in the online version only: Build real test cases, find where models fail, look inside, then fix it. Four steps: Real-world tests (one task, one example used in three roles; about 150 real seeds) → Where models fail (do they copy the wrong details or drop earlier constraints?) → Inside the model (which layers carry the role and which copy source details?) → Targeted training (train where it fails; compare with SFT, DPO and GRPO). A band under steps 1–3: One-week sprint, 5 to 11 Nov: steps 1 to 3 on 20 to 30 seeds, then go / no-go.]*

The one-week sprint runs the first three steps on a small set. We build the full study only if models really fail and the failure depends on the example's role.

**Key terms**

| Term | Plain meaning |
| --- | --- |
| Example role | Why the user gave the example: to borrow its idea (analogy), follow it exactly (requirement), or avoid it (counter-example) |
| Transfer scope | Which parts of the example should carry over to the user's task, and which should stay behind |
| Detail leakage | The answer copies a part of the example that should have stayed behind |
| Constraint retention | The answer still keeps the user's earlier rules, such as budget or format |
| Joint success | One answer gets all of the above right at once; our main score |
| Logit lens, activation patching | Ways to read the model layer by layer and test which parts cause a behaviour |

## Research question

When a user gives an LLM an example, can the model tell what the example is for, take only the part that is meant to transfer, and still keep the user's earlier requirements?

The same example can play different roles:

- **Analogy**: "solve mine the way this one works" (transfer the relation, not the details).
- **Requirement**: "follow this exactly" (some details are mandatory).
- **Counter-example**: "don't do it like this" (reject the pattern).

We will measure this with controlled variants of the same example, then test whether training improves it on unseen tasks.

**Example.** A user asks for a priority scheme for a university help desk and cites hospital triage. The principle "urgent cases first" should transfer. The hospital's staffing, budget and fixed time limits should not.

**Research questions**

- **RQ1.** When the same example is given for a different purpose, does the model change its behaviour appropriately?
- **RQ2.** Does it apply the needed relation, drop irrelevant source details, and keep the target constraints that still apply?
- **RQ3.** Where inside the model do source details replace the right answer, and which layers encode the example's role?
- **RQ4.** Does training aimed at those layers beat ordinary fine-tuning, preference training, RL and strong prompting on unseen tasks?

## Motivation

Users often explain a need through an example from another context. In our own use of chat assistants, the model then treats the example's incidental details as new requirements, keeps coming back to the example, and drops constraints stated earlier. We will check how often this happens in real user conversations, not only in our own.

People explain things to assistants and agents through examples all the time. If the model cannot separate what the example illustrates from what it happens to contain, the answer looks relevant but solves the wrong problem.

Three studies point the same way. In a test with business cases, GPT-4 named no source story when it was not told to use one. Once told, it applied both stories to both problems, so half its analogies were wrong (precision 0.50, recall 1.00) ([Puranam et al., 2025](https://arxiv.org/abs/2505.00603)). On story pairs, GPT-4 picks a surface-similar distractor over a true but distant analogy 71% of the time ([ARN](https://arxiv.org/abs/2310.00996)). In multi-turn chats, models lock into early assumptions and do not recover ([Laban et al., 2025](https://arxiv.org/abs/2505.06120)). None of these varies the role an example plays.

## Closest prior work

We found no paper that tests how the role of a user's example changes what a model should transfer. Each part of the problem has close neighbours.

| Work | Venue / status | What it covers | How we differ |
| --- | --- | --- | --- |
| [Do as I Say, Not as I Do](https://arxiv.org/abs/2605.20382) | Workshop poster, COLM 2026 | Models drop an explicit instruction as copied pattern turns grow (13 models, template data) | Their examples are always wrong to follow. Ours must be followed, partly used or rejected, by role. |
| [Mitigating Copy Bias in ICL](https://aclanthology.org/2026.findings-eacl.13/) | Findings of EACL 2026 | Models copy labels from demonstrations; pruning a few MLP neurons helps (models up to 2.7B) | We test larger models on richer tasks, and score useful transfer as well as copying. |
| [Overthinking the Truth](https://arxiv.org/abs/2307.09476) | ICLR 2024 | Late layers overwrite correct answers with copied false demonstrations; ablating 5 heads helps | We use the same tools on examples whose role varies. |
| [LLMs Get Lost in Evolving User Intent](https://arxiv.org/abs/2607.20734) | arXiv 2026 | Accuracy drops when users revise or switch intent (GPT 5.5 on GSM8K: 99.0 to 80.5) | We hold intent fixed and vary only the example's role. |
| [LLMs Get Lost in Multi-Turn Conversation](https://arxiv.org/abs/2505.06120) | arXiv 2025 | Scores fall 39% when an instruction arrives over several turns | We include single-turn versions with the same information, to separate role effects from drift. |
| [ReTRE](https://aclanthology.org/2026.acl-long.2048/) | ACL 2026 | Robustness to rewrites that keep the solution; SFT overfits, RL holds up | Transfer there is the model's own. Ours is from a user-supplied example. |
| [AnaloBench](https://aclanthology.org/2024.emnlp-main.725) and [ARN](https://arxiv.org/abs/2310.00996) | EMNLP 2024; arXiv | Finding an analogy among stories; surface-similar distractors fool GPT-4 | We test using an example on a task under constraints, not finding it. |
| [Relevant or Random](https://aclanthology.org/2025.findings-acl.1230) | Findings of ACL 2025 | Random model-written examples can match relevant ones | Their examples are model-written aids. Ours come from the user, with intent. |

Full notes on each paper (data, method, numbers, weak spots) are in the [deep-read doc](related-work-deep-read.md).

## Benchmark design

Each seed scenario pairs a source example with a target task, then varies the example's role and how well it fits the target.

Each seed contains:

| Component | Content |
| --- | --- |
| Target task | The user's actual problem |
| Target constraints | Budget, output format, resource limits or other conditions that apply |
| Source example | An example from another situation |
| Example role | Analogy, requirement or counter-example |
| Transfer scope | Which relations and details may transfer, and which may not |
| Gold specification | Required properties of an acceptable answer, and forbidden behaviour |
| Verification | A program check, or a human-validated rubric |

**Task families.** We start with two families where correctness can be checked: constraint-based planning (resources, priorities, time) and code or data transformation (unit tests, structured output). Writing and policy tasks are a later extension.

**Size.** About 150 independent seeds, giving roughly 900–1,500 meaningful variants. The final size depends on the sprint's annotation quality and resources. Generation may be LLM-assisted, but gold specifications and key samples are checked by people.

**Real-world seeds.** Sir asked that the examples be real and striking, not easy synthetic data. Every seed starts from a real situation: a real user turn, a documented business case, or a real code task. Templates shape only the variants, never the story. Five sample seeds:

| Domain | User's task | Example given | Role | Must transfer | Must not transfer |
| --- | --- | --- | --- | --- | --- |
| Operations | Priority scheme for a university help desk | Hospital triage | Analogy | Urgent cases first | Staffing, budget, fixed time limits |
| Business | Pricing for a drone-as-a-service firm | Printer-and-ink pricing | Counter-example | Nothing; the causal structure differs | Profit from consumables |
| Business | Same drone firm | Rolls-Royce "power by the hour" | Analogy | Charge by usage, keep ownership | Jet-engine specifics |
| HR | Why a voluntary pilot's 23% gain vanished after roll-out | Shipwreck survivors and dolphins | Analogy | Self-selection bias | Sailors, islands |
| Code | New CSV parser | An existing parser function | Requirement | Signature, error handling | Its hard-coded file path |

The drone and HR rows come from the business-case study by Puranam et al. The same task appears with different examples, so only the role changes.

**Rules against easy data**

- The role is often implied, not announced. Real users rarely write "this is an analogy". About half the variants state the role; the rest leave it to context.
- Every counter-example looks similar on the surface, since that is where models fail most (ARN).
- Long contexts are included. AnaloBench shows GPT-4 falls from 89.1% to 60.7% as stories grow from 1 to 30 sentences.
- Two annotators rate each seed for realism on a 1–5 scale. We keep seeds rated 4 or above.
- We compare our seeds with a WildChat sample on length, domain and phrasing, and report the gap.

**Building blocks.** No existing dataset tests example roles directly, so we merge parts of public datasets and add our own role labels and gold specifications:

- Target tasks with automatic checks from [Lost in Conversation](https://github.com/microsoft/lost_in_conversation): 600 code, math and function-calling instructions.
- Requirement and counter-example material from [Super-NaturalInstructions](https://arxiv.org/abs/2204.07705): 1,616 tasks, each with human-written positive and negative examples and the reason each is right or wrong.
- Analogy sources from [AnaloBench](https://github.com/JHU-CLSP/AnaloBench) (340 human-written stories in 47 clusters) and [ParallelPARC](https://aclanthology.org/2024.naacl-long.329) (paragraph analogies with hard distractors).
- Surface-similar distractors from [ARN](https://arxiv.org/abs/2310.00996) (1,096 story triples), which give natural counter-examples.
- Business cases with a right and a wrong source story from [Puranam et al.](https://arxiv.org/abs/2505.00603)
- Checkable constraints (format, length, keywords) in the style of IFEval and FollowBench.
- Instruction-retention results from [MultiChallenge](https://github.com/ekwinox117/multi-challenge) as an outside reference point.

**Real conversations.** We will mine [WildChat](https://arxiv.org/abs/2405.01470), a public set of about one million real ChatGPT conversations, for user turns that give an example ("for example", "like this", "similar to"). We label a sample by role and by whether the reply over-used the example. This gives three things: an estimate of how common the failure is, real material for writing seeds, and an answer to the question of whether the problem is artificial. We release only our labels and rewritten seeds, never raw user text. WildChat is released under ODC-BY.

**Variation axes**

- **Role** (3): analogy, requirement, counter-example.
- **Target fit**: the relation fits, fits only in part, or would be wrong to apply. Only meaningful role–fit combinations are kept.
- **Turn structure**: single-turn and information-equivalent multi-turn versions.

Partial transfer is not a separate role. Each instance is annotated with which relations and details may transfer and which may not. Cases where a requirement conflicts with an earlier constraint and the right answer is unclear go to a separate split.

**Useful transfer is required.** In some tasks the correct answer needs the example's relation. In others applying it is wrong. A model that ignores every example cannot score well.

**Metrics**

| Metric | What it checks |
| --- | --- |
| Joint success (primary) | One answer meets every required condition at once |
| Appropriate transfer | The allowed relation is used correctly |
| Detail leakage | A forbidden source detail appears in the answer |
| Constraint retention | Target requirements that still apply are kept |

Where a constraint can be checked by a program (numbers, code execution, structure), we check it that way. The rest uses a rubric-based LLM judge, validated against human labels on a held-out sample that was not used to write the rubric.

**Splits.** All variants of one seed stay in the same train/dev/test split. Relation or template families are also held out to test generalisation. Bootstrap confidence intervals are computed at seed level, since variants of one seed are not independent.

**Data contamination.** Reused benchmarks (GSM8K, HumanEval and Spider inside Lost in Conversation, and Super-NaturalInstructions) are public, so models may have seen them in training. Every item is rewritten into our seed format, so its final text is new. Before an item enters the test set we also run guided completion ([Golchin and Surdeanu, ICLR 2024](https://arxiv.org/abs/2308.08493)), Min-K% Prob ([Shi et al., ICLR 2024](https://arxiv.org/abs/2310.16789)) and an original-vs-rewrite comparison. At least a third of test seeds are written fresh after the models' cutoffs, and every main claim must hold on that set too. Test files carry a canary string, and a test split stays hidden.

## Inside the model

This part follows sir's suggestion to experiment on the model's layers. It answers one question: where inside the model does a source detail replace the right answer, and does fixing only that part work? Earlier layer studies measured only copying. Our benchmark also scores useful transfer, so we can see whether a fix removes both.

1. **Find the layers (no training).** On matched pairs (same content, different role) we read each layer's current guess with the logit lens, train small probes to see which layers encode the role, and swap activations between pairs (activation patching) to see which layers and heads cause the change. [Halawi et al. (ICLR 2024)](https://arxiv.org/abs/2307.09476) found that late layers overwrite correct answers with copied false demonstrations; we test whether the same happens with source details.
2. **Switch them off (no training).** We zero the few heads or MLP neurons found in step 1 and measure leakage, useful transfer and joint success. In Halawi et al., ablating 5 heads (about 1% of all heads) cut the false-demonstration gap by 38.9% on 14 datasets. [Copy Bias](https://aclanthology.org/2026.findings-eacl.13/) did the same with MLP neurons.
3. **Train only there.** We compare retraining only the last layers ([DFR, ICLR 2023](https://arxiv.org/abs/2204.02937)), LoRA in the layers from step 1, and LoRA everywhere, with the same data and compute.

Two extra checks are exploratory: removing whole late layers, which [Gromov et al. (ICLR 2025)](https://arxiv.org/abs/2403.17887) found often costs little, and a small added module that marks each part of the example as take, drop or keep-as-constraint.

**Models and tools.** Layer work needs full-precision weights, since 4-bit models distort activations. An 8B model in bf16 needs about 16GB for weights alone, so steps 1 and 2 run on 3–4B models (Qwen2.5-3B, Llama-3.2-3B) on our own GPUs. We repeat the main result on one 8B model on a rented A100. Tools: TransformerLens or nnsight.

## Method

We will train with a specification-conditioned consistency objective: the model's decisions should change exactly where the gold specification says they should, and stay fixed where it says they should not.

- Changing only incidental source details should not change the task-relevant decisions, unless the role makes that detail mandatory.
- Changing the role or the relevant relation should change the decisions that depend on it, and only those.

The objective targets task-relevant decisions and constraint satisfaction, not identical output text, because two roles can share a valid answer.

Training has three parts:

1. **Task supervision**: produce the correct target response.
2. **Transfer-scope supervision**: decide which source relations to use, which details to drop, and which target constraints to keep.
3. **Paired consistency training**: across related inputs, learn which changes are required and which must not happen.

**Baselines (same training data, similar compute)**

1. Prompting: "extract the relation, map it to the target, then check the original constraints".
2. Ordinary supervised fine-tuning (SFT).
3. Preference training (DPO on good and bad transfers).
4. RL with a verifier reward (GRPO). [ReTRE](https://aclanthology.org/2026.acl-long.2048/) found SFT reached 100% in-distribution but fell below the untrained model on rewrites, while RL held up, so RL is a needed baseline.
5. Retraining only the last layers.
6. The proposed objective, with LoRA in the layers found above and with LoRA everywhere.

If prompting closes most of the gap, the method must still show a gain in generalisation to held-out families, consistency, or inference cost. Otherwise the paper becomes a benchmark-and-analysis contribution.

We also report component ablations. The new part is the design of role-conditioned training pairs, not LoRA or contrastive learning themselves.

**Models.** 3–4B open models for the layer analysis and most ablations. 7–8B open models (Qwen or Llama) with LoRA/QLoRA for the main results. Frontier models are evaluated through their APIs only.

## One-week feasibility sprint (5–11 November)

Sir gave one week to decide whether this topic can carry a paper. The sprint runs seven experiments, each with a pass mark fixed before we see results. If they pass, we commit to the topic on 12 November. The day-by-day tracker is in the [Feasibility Sprint doc](feasibility-sprint.md).

**A first check is already done.** In a random sample of 4,000 WildChat conversations (4 November), users gave a real example in about 0.3% of unique English turns, mostly "in this format" or "in this style". We saw no counter-examples and no cross-domain analogies. So WildChat measures how common the problem is and supplies requirement seeds; analogy and counter-example seeds come from curated sources.

| Day | Work |
| --- | --- |
| 1 · Thu 5 Nov | Mine WildChat at scale; hand-label 200 turns |
| 2 · Fri 6 Nov | Audit public sources: licence and usable items per role |
| 3 · Sat 7 Nov | Seed format and annotation guide; 10 seeds; second annotator |
| 4 · Sun 8 Nov | 20–30 seeds, 100–150 role variants, program checks |
| 5 · Mon 9 Nov | Contamination checks |
| 6 · Tue 10 Nov | Model tests and first layer scan |
| 7 · Wed 11 Nov | Go / no-go table and a one-page result for sir |

**The seven experiments**

| # | Question | Setup | Pass if | Stop if |
| --- | --- | --- | --- | --- |
| E1 | Do real conversations contain the problem? | Keyword filter on all English WildChat turns; LLM classifier on about 2,000 candidates; 200 hand labels | 300+ real example-giving turns | Under 100: WildChat is used only to measure how common it is (not a stopper) |
| E2 | Can people agree on the gold answer? | Two annotators label what must and must not transfer on 20–30 seeds | Agreement on 80%+ of seeds | Under 60% |
| E3 | Is the reused data contaminated? | Guided completion, Min-K% Prob, and original vs rewrite, on 2 open models | Fresh and rewritten seeds within 10 points | A gap that rewriting does not close |
| E4 | Do models fail? | 3B and 8B open models plus one API model on 100–150 variants; plain example vs relation stated | 25%+ of answers leak a detail or miss the relation, and stating the relation halves this | Under 10% failure in every model |
| E5 | Does the role matter? | Same content, different role | Failure rate changes by 15+ points; the seed-level interval excludes zero | No role effect |
| E6 | Is it more than multi-turn drift? | Single-turn vs information-equivalent multi-turn | The failure also appears in single-turn | It appears only in multi-turn |
| E7 | Is there a layer signal? | Logit lens on 5 matched pairs, 3B model | The answer flips at clear layers in 3 of 5 pairs | Not a stopper |

Matched controls are built into E4–E6: same content with a different role, same role with different incidental details, the raw example vs a version that states the relation, and single- vs multi-turn. All model runs fit on our own 8GB and 16GB GPUs plus a small API budget.

**Outcome on 12 November**

- **Go** (E2, E4 and E5 pass): we commit to the topic statement below.
- **Revise** (data works, effect between the two marks): change the task families and run one more week.
- **No-go** (E4 or E5 fails): switch to the fallback topic and tell sir the same day.

**Topic statement we sign on go**

> We study whether LLMs use a user-supplied example according to its role: borrow its idea (analogy), follow it exactly (requirement), or avoid it (counter-example). We build a benchmark from real situations and merged public data, with checks against data contamination. We then locate where inside the model source details override the user's task (layer scanning, activation patching), switch those parts off and measure again, and fix the failure with training aimed at those layers. Target: EMNLP 2027 main track.

## Expected contributions

1. A benchmark built from real situations that tests whether models use an example according to its role.
2. A behavioural study that separates useful transfer, detail leakage and constraint failure.
3. A layer-level account of where source details take over, tested by ablation.
4. A training method aimed at those layers, whose gains hold on unseen tasks and examples.

## Risks and fallback

| Risk | Response |
| --- | --- |
| The failure is general instruction-following, not role understanding | Matched role-only controls test this directly. If roles make no difference, the topic is dropped after the sprint. |
| Prompting solves it | Report as benchmark and analysis; keep training only if it adds generalisation, consistency or cost benefits. |
| Overlap with Do as I Say or copy-bias work is judged too close | Centre the claim on useful transfer and role-dependent acceptance, which those works do not test. |
| SFT memorises the training tasks | Test on held-out families; compare with GRPO, which held up in ReTRE. |
| A layer fix also removes useful transfer | We score transfer and leakage separately, so this shows up directly. We report it as a finding. |
| Real-world seeds take long to write | Start from mined WildChat turns and Super-NaturalInstructions examples; the sprint measures time per seed. |
| Judge unreliability | Program checks where possible; human validation on a separate sample. |
| Privacy in real conversations | WildChat is ODC-BY; we release only labels and rewritten seeds, never raw user text. LMSYS-Chat-1M is a backup. |
| Compute limits | Layer work on 3–4B models on our own GPUs; 8B only for the final runs. |

**Fallback topic**: hallucination detection from internal model signals, limited to one failure type.

## Timeline

*[Roadmap figure, in the online version only. 1-week sprint (5 to 11 Nov 2026): 20–30 seeds, 2 domains; 7 experiments, E1 to E7; training + logit lens. Benchmark + study (mid Nov 2026 to Jan 2027): full real-world benchmark; judge validation; behavioural study. Layers + method (Feb – Mar 2027): layer analysis, ablation; objective vs baselines; held-out families. Writing (Apr – May 2027): paper draft; 8B replication; internal review. Gates: go / no-go on 12 Nov after the sprint; submit to ARR, EMNLP 2027 cycle, date TBC.]*

The layer analysis runs in the third phase, before the final training runs. The EMNLP 2027 deadline is not announced yet. ACL 2027 (ARR deadline 4 January 2027) is too soon for this plan.

## Requests

- [ ] Agreement on the sprint's pass marks before day 6 (10 November).
- [ ] Feedback on the three roles and the joint-success metric.
- [ ] GPU time for the final 8B runs and the 8B layer check: about 150–300 A100-hours (lab GPU or cloud credits). Our own 8GB and 16GB GPUs cover the sprint and the 3–4B work.
- [ ] One or two annotators for judge validation, if possible.

## Sources

- [Related Work Deep Read](related-work-deep-read.md): our full notes on each paper below
- [Do as I Say, Not as I Do: Instruction-Induction Conflict in LLMs](https://arxiv.org/abs/2605.20382)
- [Mitigating Copy Bias in In-Context Learning through Neuron Pruning](https://aclanthology.org/2026.findings-eacl.13/)
- [Overthinking the Truth: Understanding how Language Models Process False Demonstrations](https://arxiv.org/abs/2307.09476)
- [LLMs Get Lost in Evolving User Intent](https://arxiv.org/abs/2607.20734)
- [LLMs Get Lost in Multi-Turn Conversation](https://arxiv.org/abs/2505.06120)
- [ReTRE: Benchmarking LLM Transfer Robustness with Structure-Preserving Variants](https://aclanthology.org/2026.acl-long.2048/)
- [AnaloBench](https://aclanthology.org/2024.emnlp-main.725)
- [ARN: Analogical Reasoning on Narratives](https://arxiv.org/abs/2310.00996)
- [Relevant or Random: Can LLMs Truly Perform Analogical Reasoning?](https://aclanthology.org/2025.findings-acl.1230)
- [Can LLMs Help Improve Analogical Reasoning for Strategic Decisions?](https://arxiv.org/abs/2505.00603)
- [Function Vectors in Large Language Models](https://arxiv.org/abs/2310.15213)
- [Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations](https://arxiv.org/abs/2204.02937)
- [The Unreasonable Ineffectiveness of the Deeper Layers](https://arxiv.org/abs/2403.17887)
- [Super-NaturalInstructions](https://arxiv.org/abs/2204.07705)
- [ParallelPARC](https://aclanthology.org/2024.naacl-long.329)
- [Lost in Conversation code and data](https://github.com/microsoft/lost_in_conversation)
- [MultiChallenge](https://github.com/ekwinox117/multi-challenge)
- [WildChat: 1M ChatGPT Interaction Logs in the Wild](https://arxiv.org/abs/2405.01470) and its [dataset card](https://huggingface.co/datasets/allenai/WildChat-1M) (ODC-BY)
- [LMSYS-Chat-1M](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)
- [ACL 2027](https://2027.aclweb.org/) and [ACL Rolling Review](https://aclrollingreview.org)
