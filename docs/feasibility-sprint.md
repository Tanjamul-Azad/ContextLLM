# One-Week Feasibility Sprint: Role-Aware Example Use

2026-11-04 · Tanjamul


Sir gave one week to show the topic can work. By 2026-11-12 we decide go or no-go and, on go, fix the topic.

## Fixed-topic statement

This is the paragraph we commit to if the week ends in go. Sir has already approved the method; the week tests the data.

> **Topic.** We study whether LLMs use a user-supplied example according to its role: borrow its idea (analogy), follow it exactly (requirement), or avoid it (counter-example). We build a benchmark from real situations and merged public data, with checks against data contamination. We then locate where inside the model source details override the user's task (layer scanning, activation patching), switch those parts off and measure again, and fix the failure with training aimed at those layers. Target: EMNLP 2027 main track.

The week answers three questions before we sign this:

1. Do real conversations contain enough example-giving turns of each role?
2. Can we build 20–30 good seeds in a week, with a clear gold answer?
3. Do current models actually fail on them, and does the failure depend on the role?

## The week, day by day

Data comes first, as sir asked: four of the seven days are about the dataset. Each day ends with one output we can show.

| Day | Work | Output | Status |
| --- | --- | --- | --- |
| 1 · Thu 5 Nov | Mine WildChat at scale: keyword filter on all English turns, then an LLM classifier on about 2,000 candidates; label 200 by hand | Real counts per role; precision of the filter; 30 paraphrased real cases | Not started |
| 2 · Fri 6 Nov | Audit the public sources: download, check licence, count usable items per role (Super-NaturalInstructions, AnaloBench, ARN, ParallelPARC, Lost in Conversation) | Filled source table with real counts | Not started |
| 3 · Sat 7 Nov | Seed format and annotation guide; write 10 seeds from real sources; a second person labels them | Guide v1; agreement on what must and must not transfer | Not started |
| 4 · Sun 8 Nov | Write 10–20 more seeds (20–30 total); build role variants; write program checks | Pilot set of 100–150 variants | Not started |
| 5 · Mon 9 Nov | Contamination checks on every reused source (below) with two open models | Table: source, contaminated or not, action taken | Not started |
| 6 · Tue 10 Nov | Behavioural test: a 3B and an 8B open model plus one API model; plain vs relation-stated prompt; single vs multi-turn. Logit lens on 5 matched pairs | First failure rates by role; first layer plot | Not started |
| 7 · Wed 11 Nov | Fill the go / no-go table; write a one-page result for sir | Go with the fixed-topic statement, or the fallback plan | Not started |

## WildChat check: is the right kind of conversation there?

Partly. Real users do give examples, but mostly "do it in this format" and "in this style". Cross-domain analogies and counter-examples were almost absent in our sample. So WildChat can show the problem is real and give realistic phrasing, but it cannot be the main source of seeds.

**What we did (4 November).** We pulled 40 random pages of 100 conversations from [WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M) (837,989 conversations in total), kept English, removed repeated turns, and searched user turns with keyword patterns for each role. Then we read every match under 1,200 characters by hand. This is a quick sample, not the full mining planned for day 1. Script: [scripts/wildchat_probe.py](../scripts/wildchat_probe.py).

| Step | Count |
| --- | --- |
| Conversations sampled | 4,000 |
| English conversations | 2,492 |
| Unique English user turns | 3,893 |
| Turns matching any role pattern | 127 |
| Matches under 1,200 characters (read by hand) | 32 |
| Real example-giving turns among those 32 | about 12 |

About 0.3% of unique turns are clear cases, so the full English set may hold a few thousand. Keyword search misses many, so this is a lower bound.

**What the real cases look like** (paraphrased; we never copy user text)

| Type of case | How often in the sample | Role it fits | Usable for us? |
| --- | --- | --- | --- |
| "Make names like this one", "write a sentence like this" | Most common | Requirement (copy the pattern) | Yes |
| "The input file looks like this" | Common | Requirement (format) | Yes, for code tasks |
| "Write quotes similar to this", "a version inspired by that song" | Several | Analogy of style | Yes, but shallow |
| "Your earlier example was better, do it that way" | A few, in multi-turn chats | Requirement, plus a sign of the failure | Yes, valuable |
| "What else behaves the same way as Python lists?" | One | Conceptual analogy | Rare |
| A surface-similar example the user rejects | None seen | Counter-example | Not from WildChat |

**Most matches were noise:** pasted documents that happen to contain "for example", jailbreak prompts, and the same role-play prompt repeated many times. Any mining must remove repeats and long pasted text first.

**What this means for the dataset**

- Requirement-role seeds can start from real WildChat turns.
- Analogy and counter-example seeds need curated sources: business cases, ARN distractors, Super-NaturalInstructions negative examples.
- WildChat's main job is to measure how often the problem happens and how real users phrase examples. That answers a reviewer who asks whether the problem is artificial.

## How we build and merge the dataset

We never use a public item as it is. Each one is rewritten into our seed format, so every source ends up with the same fields and the same checks. This also lowers contamination, since the final text is new.

*[Diagram, in the online version only: Six sources become one seed format, then pass checks before the benchmark. WildChat turns, Super-NaturalInstructions, AnaloBench/ParallelPARC, ARN distractors, business cases and Lost in Conversation tasks all feed "Rewrite into a seed" (target task + constraints, source example + role, transfer scope + gold), then Role variants (3 roles × fit × turns) → Quality checks (2 annotators + programs) → Contamination check (drop or rewrite flagged) → Benchmark (split by seed, not variant).]*

Every source feeds the same seed card. A seed only enters the benchmark after the quality and contamination checks.

| Source | What we take | How we change it | Role it feeds | Contamination risk |
| --- | --- | --- | --- | --- |
| WildChat turns | How real users phrase an example | Paraphrase; attach a new checkable target task | Requirement, some analogy | Low: chat logs, not a test set |
| Super-NaturalInstructions | Human-written positive and negative examples with reasons | Turn the negative example into a counter-example inside a new task | Requirement, counter-example | High: widely used for training |
| AnaloBench, ParallelPARC | Analogy pairs written or checked by people | Keep the relation; write a new target task with constraints | Analogy | Medium: public since 2024 |
| ARN | Surface-similar distractor stories | Use the distractor as the example that must not be followed | Counter-example | Medium |
| Business cases | Real cases where an analogy misled (Kodak, Blockbuster, survivorship bias) | Write the decision problem and constraints ourselves | Analogy, counter-example | Low for our new framing; the stories themselves are well known |
| Lost in Conversation tasks | Target tasks with automatic checks | Add an example with a role; keep the original checker | All three, as targets | High: built on GSM8K, HumanEval, Spider |

**Merge rules**

1. One seed = one target task + one source example. Its role variants share the same seed id and stay in the same split.
2. Each source covers at most 40% of seeds, so no single dataset's style dominates.
3. At least a third of test seeds are written fresh by us after the models' training cutoffs, as a clean control set.

## Data contamination

Contamination means a model saw our test items, or their source, during training. Then a good score may come from memory, not from reading the example's role. This matters most for the reused benchmarks (GSM8K, HumanEval and Spider inside Lost in Conversation, and Super-NaturalInstructions), which are public and widely trained on.

We handle it in two ways: we change every item so the final text is new, and we test for leftover memory before an item enters the benchmark.

| Check | What it catches | Models | Rule (our choice) |
| --- | --- | --- | --- |
| Guided completion ([Golchin and Surdeanu, ICLR 2024](https://arxiv.org/abs/2308.08493)): give the dataset name and the first half of an item, ask the model to finish it | Items the model can recite | API and open models | Flag a source if more than 5% of items come back near word for word |
| Min-K% Prob ([Shi et al., ICLR 2024](https://arxiv.org/abs/2310.16789)): average log-probability of the least likely tokens | Text the model trained on, without needing its training data | Open models only | Compare original items, our rewrites and fresh text; flag items that look like training text |
| Original vs rewrite | Memory helping on the original wording | All | If accuracy on the original is much higher than on our rewrite of the same item, treat that source as contaminated |
| Fresh control set | Anything the checks above miss | All | At least a third of test seeds written by us after the models' cutoffs; every main claim must also hold on this set |
| Generator kept apart | Bias when the same model writes and solves items | All | The model family that drafts variants is not used to report main results |

**When a source is flagged:** we keep its structure but rewrite the surface (names, numbers, domain), then test again. If it is still flagged, the source is used only for training, never for test.

**Protecting our own release.** Test files carry a canary string, as BIG-bench does, so future model builders can filter them. A canary does not stop all leaks, so we also keep a hidden test split.

## Go / no-go

We go if seeds can be built reliably, models fail, and the failure depends on the role. These thresholds are our proposal; we agree them with sir before day 6, so the result cannot be bent afterwards.

| Question | Go if | Stop if |
| --- | --- | --- |
| Real data exists | Full mining finds 300+ real example-giving turns, and curated sources give 100+ usable counter-examples | Under 100 real turns: WildChat is then used only to measure how common the problem is (not a stopper on its own) |
| Seeds can be built | 20+ seeds in the week; two annotators agree on what must transfer for 80%+ of seeds | Agreement under 60%: the roles are not well defined |
| Contamination is under control | Fresh seeds and rewritten seeds give results within 10 points | Large gap that rewriting does not close |
| Models really fail | 25%+ of answers leak a forbidden detail or miss the needed relation, and stating the relation outright halves this | Under 10% failure in every model |
| The role matters | Same content with a different role changes the failure rate by 15+ points, and the seed-level interval excludes zero | No role effect |
| Layer signal (helpful, not required) | The logit lens shows the answer flipping at clear layers in 3 of 5 pairs | Not a stopper |

**The three outcomes**

- **Go:** seeds can be built, models fail, and the role matters. We sign the fixed-topic statement on 12 November.
- **Revise:** data works but the effect is weak (between the two thresholds). We change the task families and run one more week.
- **No-go:** models do not fail, or the role makes no difference. We switch to the fallback topic (hallucination detection from internal model signals) and tell sir the same day.

## Sources

- [Proposal](proposal.md) and [Related Work Deep Read](related-work-deep-read.md)
- [WildChat-1M dataset card](https://huggingface.co/datasets/allenai/WildChat-1M), sampled through the Hugging Face dataset viewer on 4 November 2026
- [Time Travel in LLMs: Tracing Data Contamination in Large Language Models](https://arxiv.org/abs/2308.08493) (ICLR 2024)
- [Detecting Pretraining Data from Large Language Models](https://arxiv.org/abs/2310.16789) (ICLR 2024)
- [Super-NaturalInstructions](https://arxiv.org/abs/2204.07705)
- [AnaloBench](https://aclanthology.org/2024.emnlp-main.725), [ParallelPARC](https://aclanthology.org/2024.naacl-long.329), [ARN](https://arxiv.org/abs/2310.00996)
- [Lost in Conversation code and data](https://github.com/microsoft/lost_in_conversation)
- [Can LLMs Help Improve Analogical Reasoning for Strategic Decisions?](https://arxiv.org/abs/2505.00603)
