# Pilot results (4 November 2026)

**Verdict: go, with two gaps to close this week.** All three models fail on 40–47% of plain prompts, and stating the relation outright does not fix it. In two of three models the role clearly changes what gets copied. Inside the model, the roles split at layers 23–28 of 36. The gaps: the seeds have not yet been checked by a second annotator (E2), and 10 seeds is a small set.

All numbers below come from files in [results/](results/). Every raw prompt and answer is saved, so any number can be traced back.

## Verdict per experiment

| # | Question | Result | Pass mark | Verdict |
| --- | --- | --- | --- | --- |
| E1 | Do real chats contain the problem? | WildChat: about 2,160 real example-giving turns (hand-checked rate 0.29% of unique turns). OASST2: about 100 | 300+ | Pass, but almost all are "follow this format"; real counter-examples are rare |
| E2 | Do two people agree on the gold answer? | Not run: needs two human annotators | 80%+ agreement | Pending: [data/E2_annotation_sheet.csv](data/E2_annotation_sheet.csv) |
| E3 | Is reused data contaminated? | GSM8K on Qwen2.5-3B: 0% recited word for word; originals scored above their paraphrases in only 17% of pairs | Flag if >5% recited | Not flagged |
| E4 | Do models fail? | Plain wording: 47% / 40% / 47% fail (Qwen-3B / Qwen-7B / Llama-8B). Explicit wording: 33% / 30% / 27% | 25%+ fail, and explicit halves it | Failure is real; explicit wording helps but does not halve it |
| E5 | Does the role matter? | Copy-rate gap, requirement minus counter: 60 [30, 90], 30 [-10, 70], 50 [20, 80] points | 15+ points, interval above 0 | Pass for Qwen-3B and Llama-8B; not for Qwen-7B |
| E6 | Is it more than multi-turn drift? | Single-turn failure 40–47%; multi-turn 40–43% | Failure appears in single-turn | Pass |
| E7 | Is there a layer signal? | The roles split at layers 23–28 of 36 in all 5 probes; the final answer was role-correct in 2 of 5 | Clear split in 3 of 5 | Pass |

Intervals are 95% bootstrap over seeds.

## What was run

| Item | Detail |
| --- | --- |
| Seeds | 10 tasks: 6 planning tasks (JSON answer) and 4 code tasks (Python function with tests). Each is built on a real case: hospital triage, Rolls-Royce "Power by the Hour", Toyota andon, Abraham Wald's bombers, airline boarding, tabloid headlines, Gmail address rules, a GitHub pager. See [src/seeds.py](src/seeds.py) |
| Conditions per seed | 3 roles × 2 wordings (plain, explicit) × 2 turn structures (single, multi) + 1 no-example baseline = 13 prompts |
| Models | Qwen2.5-3B-Instruct (bf16), Qwen2.5-7B-Instruct (4-bit), Llama-3.1-8B-Instruct (4-bit), all on one RTX 4060 (8GB) |
| Decoding | Greedy, at most 512 new tokens, so reruns give the same answers |
| Scoring | Fully automatic: JSON checks and Python tests. [tests/validate_checks.py](tests/validate_checks.py) shows that correct answers pass and copied answers get caught |
| Total | 390 scored answers, 5 layer probes, 60 contamination items, 30,000 sampled chats |

## One real example

**Input** (seed P1, role analogy, explicit wording). The user asks for an IT help-desk priority scheme with at most 3 levels and times in hours. They show hospital triage (Red, Orange, Yellow, Green, Blue; times in minutes) and add: *"Take only the principle that more urgent tickets get a faster response. Do not reuse the colour names, minute-based times or clinical roles."*

**Qwen2.5-3B answered:**

```json
{"levels": [{"name": "Red", "response_hours": 1}, {"name": "Orange", "response_hours": 2}, {"name": "Yellow", "response_hours": 3}]}
```

**Score:** target rules kept, urgency order kept, but **leaked** the colour names it was told not to use, so joint success = fail. Llama-3.1-8B on the same prompt answered "Critical, High, Low" and passed.

This is the failure the project is about: the model takes the example's surface details along with its idea.

## E4–E6: behaviour

![Joint success by role](results/behaviour/figures/joint_by_role.png)

![Copy rate by role](results/behaviour/figures/copy_rate_by_role.png)

| Model | Fail: analogy | Fail: requirement | Fail: counter | Copied pattern: requirement | Copied pattern: counter |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5-3B | 50% | 50% | 40% | 70% | 10% |
| Qwen2.5-7B (4-bit) | 40% | 60% | 20% | 50% | 20% |
| Llama-3.1-8B (4-bit) | 40% | 70% | 30% | 50% | 0% |

Plain wording, single-turn. Each cell is 10 answers, one per seed.

What this shows:

- **Models fail in all three roles, in different ways.** Under analogy they leak details. Under requirement they often fail to copy what was asked (only 50–70% did). Under counter-example they mostly avoid the pattern, but not always.
- **Explicit wording is not enough.** Telling the model exactly what to take and what to leave cuts failure by 10–20 points, not by half. Better prompting alone does not solve it, which leaves room for a training method.
- **The example also breaks the user's own rules.** For Llama, target rules hold in 90% of answers with no example but only 73% once an example is added.

Full tables: [results/behaviour/summary.md](results/behaviour/summary.md). Per seed: [results/behaviour/per_seed.csv](results/behaviour/per_seed.csv).

## E7: inside the model

![Layer scan, code seed](results/logit_lens/qwen2.5-3b/C1_window_sum.png)

At the token where the answer either copies the example or not (here: does `k` get the example's default of 7?), we read every layer's guess. Up to about layer 23 all three roles look the same. After that the requirement curve rises towards copying and the other two fall. So the role is only used in the last third of the network. The layer-level work (patching, switching off parts) should focus on layers 23–36.

| Probe | Layer where roles split | Role-correct at the output? |
| --- | --- | --- |
| P1 help-desk triage | 25 | No: copies "Red" even as a counter-example |
| P2 drone pricing | 28 | No |
| P6 exam-hall boarding | 23 | Yes |
| C1 window sum | 25 | Yes |
| C2 retry backoff | 28 | No |

Plots for all five: [results/logit_lens/qwen2.5-3b/](results/logit_lens/qwen2.5-3b/).

## E1: real conversations

| Source | Sampled | Keyword candidates | Real examples (hand-checked) | Roles found | Estimate, full dataset |
| --- | --- | --- | --- | --- | --- |
| WildChat-1M | 15,000 chats | 174 | 10 of a random 45 (22%) | 9 requirement, 1 analogy, 0 counter | about 2,160 |
| OASST2 | 15,000 messages | 40 | 12 of 40 (30%) | 8 requirement, 2 analogy, 2 counter | about 100 |

- Real users mostly give "do it in this format" examples. Cross-domain analogies and counter-examples are rare, and the counter-examples we did find reject the assistant's own earlier answer.
- This supports the plan: real chats measure how common the problem is and supply requirement seeds. Analogy and counter-example seeds must come from curated real cases.
- A 3B model is not a good labeller. It agreed with the hand labels on only 42% of turns and called most of them counter-examples. Full mining needs hand labels or a stronger labeller.
- The hand checks are a first pass and should be re-checked by a second person. Counts and labels: [results/E1_wildchat/](results/E1_wildchat/), [results/E1_oasst/](results/E1_oasst/). No user text is in the repository.

## E3: contamination

On 60 GSM8K test questions, Qwen2.5-3B did not recite any second half word for word (mean ROUGE-L 0.28 with the dataset name, 0.31 without). Min-K% Prob gave originals a higher score than paraphrases in only 17% of pairs. So there is no sign that this model memorised these items, and the check pipeline works. It still has to run on every source we reuse, and on each model. Details: [results/contamination/qwen2.5-3b/summary.json](results/contamination/qwen2.5-3b/summary.json).

## Limits of this pilot

- **Small set.** 10 seeds, so each role cell is 10 answers and the intervals are wide. The sprint target is 20–30 seeds.
- **No second annotator yet.** The seeds and gold checks were written by one person; E2 has not run.
- **Small models only.** The largest is 8B, and two of the models are 4-bit. No API model yet.
- **Leakage checks are word lists.** A model could leak an idea in other words and not be caught.
- **One prompt per condition.** Wording changes may move the numbers.

## Next steps

1. Run E2: two people fill [data/E2_annotation_sheet.csv](data/E2_annotation_sheet.csv) independently.
2. Grow to 20–30 seeds, mostly counter-example and analogy seeds from curated real cases.
3. Add one API model and a 14B open model.
4. Activation patching and head ablation on layers 23–36 of Qwen2.5-3B.
