# Related Work Deep Read: Role-Aware Example Use

2026-11-03 · Tanjamul


## What sir asked for

Sir approved the topic on 3 November 2026 and asked for four things. This doc answers each one.

| Request | Where it is answered |
| --- | --- |
| Read the related papers fully: their method, data and what they actually did, not only the abstract | Paper notes, comparison table |
| Make the examples real-world and striking, not easy synthetic data | Making the benchmark real-world |
| Existing datasets cover parts of the problem; merge them with our own | Datasets we can merge |
| Try layer-level experiments on open models (last layer, weights, adding or removing layers, neurons) | Layer-level experiments |

## Paper notes

We read ten papers in full, including method sections and appendices. None tests whether a model uses a user's example according to its role. Two findings change our plan: the strategic-analogy result we cited holds only in one condition, and plain SFT overfits transfer data.

### 1. Do as I Say, Not as I Do (Camassa and Shiller, 2026)

[arXiv 2605.20382](https://arxiv.org/abs/2605.20382). Poster at the Sci-FM workshop, COLM 2026, not a main-track paper.

- **What they did.** A user instruction ("answer with X") is placed before N hard-coded assistant turns that show a competing pattern. N runs from 1 to 50. They find the N at which models stop following the instruction.
- **Data.** Templates only: 13 conditions, about 200 questions per topic, pattern turns pre-generated once with Claude Haiku 4.5. No human-written or real-user data. No data link in the paper.
- **Models.** 13 models: 4 closed (Claude Opus 4.6, Sonnet 4.6, Gemini 2.5 Flash, GPT-5.2) and 9 open (Llama 3.1/3.3 70B, Qwen3 30B and 235B, Gemma-3 12B/27B, OLMo 3.1 32B, Hermes-4 70B, Kimi K2).
- **Results.** Mean instruction-following is 27% on fixed-output tasks and 43% on task-based ones. GPT-5.2, Gemini and Qwen3 235B drop below 50% after one pattern turn. Llama 3.3 70B stays at 99%. A hint that the turns are hard-coded raises task-based following from 43% to 54%.
- **Layer analysis.** None. The authors leave the mechanism to future work.
- **Weak spots.** Artificial setting (their word). Borderline p-values (0.034 to 0.096) for the main explanation. The arXiv abstract reports a self-prediction result that is not in the body.
- **For us.** Their examples are always wrong to follow. In our benchmark some examples must be followed, some partly used, some rejected. That is the gap.

### 2. Mitigating Copy Bias in ICL through Neuron Pruning (Ali, Wolf and Titov)

[Findings of EACL 2026](https://aclanthology.org/2026.findings-eacl.13/), pages 230–251.

- **What they did.** A "copying error" is a wrong answer that equals a label shown in the prompt. They find the MLP neurons that push the model toward copying and switch them off.
- **Method.** Integrated Gradients (20 steps) on a synthetic vowel-counting task scores each neuron in one MLP layer. The top 1–10% of that layer are zeroed. Block and rate are picked on a validation split. No retraining.
- **Data.** 18 short ICL tasks (lowercase, antonyms, country–capital and similar), plus SST-2, SST-5 and one BBH task for Llama-2/3.
- **Models.** Small: GPT-2, BLOOM up to 1.1B, OPT up to 2.7B, Mamba up to 370M.
- **Results.** Largest gains on 1–2 shot algorithmic tasks, for example OPT-1.3B lowercase 2-shot from 0.24 to 0.83. Knowledge tasks change by about 0.02 or less. Random pruning of the same size gives little gain.
- **Weak spots.** No limitations section, no variance, no code link, several unclear table values. Chosen layers are not reported.
- **For us.** This is the clearest template for sir's neuron idea: find units tied to copying source details, ablate them, and measure whether leakage falls without hurting useful transfer.

### 3. LLMs Get Lost in Multi-Turn Conversation (Laban et al., Microsoft and Salesforce)

[arXiv 2505.06120](https://arxiv.org/abs/2505.06120), May 2025. A later paper cites it as ICLR 2026; we did not confirm this.

- **What they did.** They split fully specified instructions into "shards" and reveal one per turn through a GPT-4o-mini user simulator.
- **Data.** Six tasks from existing benchmarks: HumanEval/LiveCodeBench, Spider, BFCL, GSM8K, ToTTo, Summary of a Haystack. Shards written by GPT-4o, then edited by two authors. The text says 600 instructions; per-task counts add to 627. Released on [GitHub](https://github.com/microsoft/lost_in_conversation).
- **Models.** 15, closed and open, including GPT-4.1, o3, Gemini 2.5 Pro, Claude 3.7 Sonnet, Llama-3.1-8B and DeepSeek-R1.
- **Results.** Average score falls 39% from single-turn to sharded. Best-case ability drops 16%, but unreliability rises 112%. Restating all shards at the end recovers part of the loss (GPT-4o 59.1 to 76.6).
- **Layer analysis.** None. No training.
- **For us.** Their single-turn "concat" control is the model for our information-equivalent single-turn variant. Their tasks give us target problems with automatic checks.

### 4. LLMs Get Lost in Evolving User Intent (Tack, Laban and Neville, Microsoft)

[arXiv 2607.20734](https://arxiv.org/abs/2607.20734), July 2026.

- **What they did.** They turn a verified single-turn task into a 7-turn conversation where the user reveals arguments, corrects a wrong value, or switches to a related task.
- **Data.** 450 items from GSM8K, BIRD-SQL, BrowseComp+ and SWE-Bench Verified. Built and checked by GPT 5.1. Turns are rule-rendered text, not real users.
- **Results.** GPT 5.5 on GSM8K falls from 99.0 to 80.5. Function switches hurt most. A short GRPO run on Qwen3-4B lifts the evolving score from 64.0 to 76.0.
- **Weak spots.** One run per item, no confidence intervals. The same GPT 5.1 builds, checks and is evaluated.
- **For us.** Their framework keeps the original task's verifier. We can do the same: take a checkable task and add an example with a role, so scoring stays automatic.

### 5. Can LLMs Help Improve Analogical Reasoning for Strategic Decisions? (Puranam, Sen and Workiewicz)

[arXiv 2505.00603](https://arxiv.org/abs/2505.00603), May 2025. INSEAD, ISB and ESSEC; no venue stated.

- **What they did.** A classic Gick and Holyoak design with a matching twist: two source stories (radiation therapy; dolphins and survivorship bias) and two business problems (a factory supply problem; an HR pilot that failed after roll-out). Each problem has one right source story.
- **Data.** Two hand-written stories and two problems. 199 business students and 60 GPT-4 runs (September 2024). Correct transfer was coded by hand against causal diagrams.
- **Results.** Without a hint, GPT-4 never named either story as its source (precision and recall 0), though the text says it used some analogy in 14 of 15 HR runs. The paper is not consistent on this point. With a hint, recall was 1.00 but precision about 0.50: it applied both stories to both problems. Humans were cautious: precision 0.67–0.75, recall 0.26–0.39.
- **Weak spots.** Only two items, 15 runs per cell, one model.
- **For us.** Our proposal said GPT-4 shows "high recall, low precision". That holds only in the hint condition, and we should say so. The design itself is what sir asked for: realistic business cases where the surface-similar example is the wrong one.

### 6. Relevant or Random (Qin et al.)

[Findings of ACL 2025](https://aclanthology.org/2025.findings-acl.1230), pages 23993–24010.

- **What they did.** In analogical prompting the model writes its own solved examples before answering. They compare relevant self-written examples with irrelevant ones (random math, random biology).
- **Data.** GSM8K and MATH (500 items each, 3 seeds), five BBH tasks, plus CSQA, MBPP and GPQA. Examples are model-generated.
- **Models.** Mainly GPT-3.5; GSM8K also on GPT-4o-mini, Llama-2-70B, Llama-3/3.1-8B, Qwen2.5-14B.
- **Results.** On GSM8K, random biology examples score 75.3 and relevant ones 71.5. On BBH relevant examples win (63.2 vs 61.9). Correct examples matter more than relevant ones: wrong-answer versions fall to about 51.
- **Weak spots.** MATH gaps are smaller than the seed spread (±3 to ±5). No significance tests.
- **For us.** Their examples are aids the model writes for itself. Ours come from the user and carry intent. Use as contrast only.

### 7. AnaloBench (Ye et al., Johns Hopkins)

[EMNLP 2024](https://aclanthology.org/2024.emnlp-main.725), pages 13060–13082. Data on [GitHub](https://github.com/JHU-CLSP/AnaloBench).

- **What they did.** Given a story, find the analogous one among 4 candidates (T1) or among a bank of 200 (T2).
- **Data.** 340 human-written one-sentence stories in 47 clusters (about 7 per cluster), seeded from idioms and metaphors. GPT-4 expanded each to 10 and 30 sentences.
- **Results.** T1 accuracy at 1 / 10 / 30 sentences: GPT-4 89.1 / 66.5 / 60.7; humans 96.0 / 72.5 / 73.3. Scale helps short stories only. On T2, models are near random for longer stories.
- **For us.** Good source of hand-written analogy pairs. They test finding an analogy, not using it on a task under constraints.

### 8. ARN: Analogical Reasoning on Narratives (Sourati et al.)

[arXiv 2310.00996](https://arxiv.org/abs/2310.00996); the paper thanks TACL reviewers, but arXiv lists no journal reference.

- **What they did.** Given a story, pick the analogous one over a distractor that looks similar on the surface.
- **Data.** Crowd-written proverb stories from ePiC. 1,096 triples. Far analogies are human-written; near analogies are GPT-3.5 drafts edited by hand. Two assistants checked 120 items (kappa 0.865). The data link is a bit.ly short link that did not load for us.
- **Results.** Average accuracy: humans 96.0, GPT-4 68.1, GPT-3.5 60.3. When the true analogy is far and the distractor is near, GPT-4 scores 29.1, below the 50% chance level.
- **For us.** The closest data to our counter-example role: a surface-similar story that must not be followed. It needs requirement-role and constraint annotation added.

### 9. ReTRE (Li et al., Soochow University and others)

[ACL 2026](https://aclanthology.org/2026.acl-long.2048/), pages 44257–44268.

- **What they did.** Rewrite a math or science problem so its solution stays the same, along two axes: new domain (knowledge domain, near or far) and new format (table or diagram).
- **Data.** MATH500 (306 variant sets built) and 103 GPQA problems. A six-agent generate-and-validate pipeline builds the variants.
- **Results.** Gemini-3-pro on MATH500 falls from 93.1% to 84.9% on far-domain rewrites. Full SFT on Qwen3-VL-8B reaches 100% in-distribution but drops to 47.1% on near-domain rewrites, below the untrained model (64.4%). GSPO, an RL method, reaches 74.2%.
- **For us.** A direct warning for our method: plain SFT on transfer data can memorise. We should add an RL baseline beside SFT and DPO, and test on held-out families.

### 10. ARCANA (Chen, Wang and Wang, USTC)

[arXiv 2610.29271](https://arxiv.org/abs/2610.29271), October 2026. Data on [GitHub](https://github.com/density-11/arcana-test).

- **What they did.** 200 hand-designed grid puzzles whose rule comes from a real object or law (buoyancy, Kepler's second law, fireworks).
- **Results.** Humans 69.0% on average. GPT 5.2 51.2%, Gemini 3 Pro 43.1%, Claude Opus 4.5 8.6%.
- **Weak spots.** One author designed the tasks and graded all answers.
- **For us.** Far analogy from real-world sources, but in grids. Useful for related work; not reusable as our data.

## Comparison

Only one paper looks inside the model, and none uses real user examples. Our two open slots are the role of the example and a layer-level account of why models copy surface details.

| Paper | Data | Real users? | Example roles | Training | Inside the model | What it leaves for us |
| --- | --- | --- | --- | --- | --- | --- |
| Do as I Say | Templates, LLM-made pattern turns | No | Reject only | No | No | Accept, partly use, reject |
| Copy Bias | 18 short ICL tasks | No | Copy vs not | No (pruning) | Yes: MLP neurons | Larger models, richer tasks |
| Lost in Multi-Turn | 6 existing benchmarks, sharded | Simulated | None | No | No | Examples as a variable |
| Evolving Intent | 4 existing benchmarks, rule-rendered | Simulated | None | Small GRPO run | No | Examples as a variable |
| Strategic analogy | 2 hand-written stories, 2 cases | Human subjects | Right vs wrong source | No | No | Scale beyond 2 items |
| Relevant or Random | Model-written examples | No | Relevant vs random | No | No | User-given examples |
| AnaloBench | 340 human-written stories | No | Find analogy | No | No | Use it on a task |
| ARN | Crowd stories (ePiC) | No | Analogy vs distractor | No | No | Constraints, requirement role |
| ReTRE | MATH500, GPQA rewrites | No | None | SFT vs GSPO | No | User-given examples |
| ARCANA | 200 hand-made grids | No | Far analogy | No | No | Text tasks |

## Datasets we can merge

Sir is right that parts exist. No dataset has all three roles with constraints, so we merge parts and add our own role labels and gold specifications. Super-NaturalInstructions is the best find: every task already ships with positive and negative examples written by people.

| Dataset | What we take | Size | Real-world? | Roles it covers | Licence |
| --- | --- | --- | --- | --- | --- |
| [WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M) | Real user turns that give an example | about 1M chats | Yes, real users | All three, after labelling | ODC-BY (changed from ImpACT on 2024-06-26) |
| [LMSYS-Chat-1M](https://huggingface.co/datasets/lmsys/lmsys-chat-1m) | Backup source of real turns | 1M chats | Yes | All three, after labelling | Gated agreement |
| [Super-NaturalInstructions](https://arxiv.org/abs/2204.07705) | Task definitions with positive and negative examples and the reason each is right or wrong | 1,616 tasks | Human-written | Requirement, counter-example | Apache-2.0 repo; source datasets vary |
| [Lost in Conversation](https://github.com/microsoft/lost_in_conversation) | Target tasks with automatic checks | 600 instructions | From benchmarks | None (targets only) | To check |
| [AnaloBench](https://github.com/JHU-CLSP/AnaloBench) | Hand-written analogy pairs, short and long | 340 stories, 47 clusters | Human-written | Analogy | To check |
| [ARN](https://arxiv.org/abs/2310.00996) | Analogy plus surface-similar distractor | 1,096 triples | Crowd-written stories | Analogy, counter-example | Unknown; data link did not load |
| [ParallelPARC](https://aclanthology.org/2024.naacl-long.329) | Paragraph analogies with hard distractors | Gold and silver sets | Science process paragraphs | Analogy, counter-example | To check |
| [Strategic analogy cases](https://arxiv.org/abs/2505.00603) | Business problems with a right and a wrong source story | 2 stories, 2 problems | Realistic business cases | Analogy, counter-example | CC BY 4.0 (paper) |
| IFEval, FollowBench | Constraints a program can check | Hundreds of prompts | Templates | Requirement | To check |

StoryAnalogy (24K pairs) is too short to use: pairs are about 2 sentences. Stack Exchange questions where a user writes "like this, but" are another real source to check.

## Making the benchmark real-world

Every seed starts from a real situation: a real user turn, a documented business case, or a real code task. We then write controlled variants of it. Templates are used only for the variant structure, never for the story.

**Where seeds come from**

1. Real user turns mined from WildChat, rewritten so no user text is released.
2. Documented cases where an analogy misled people. The strategic-analogy paper lists two: Kodak treating digital images like film, and Blockbuster treating Netflix like its own DVD model.
3. Positive and negative examples from Super-NaturalInstructions, which people wrote to show what to do and what not to do.
4. Real code and data tasks with tests (Lost in Conversation, Stack Exchange), where a user shows an existing function and says "like this".

**Example seeds**

| Domain | User's task | Example given | Role | Must transfer | Must not transfer |
| --- | --- | --- | --- | --- | --- |
| Operations | Priority scheme for a university help desk | Hospital triage | Analogy | Urgent cases first | Staffing, budget, fixed time limits |
| Business | Pricing for a drone-as-a-service firm | Printer-and-ink pricing | Counter-example | Nothing; the causal structure differs | Profit from consumables |
| Business | Same drone firm | Rolls-Royce "power by the hour" | Analogy | Charge by usage, keep ownership | Jet-engine specifics |
| HR | Why a voluntary pilot's 23% gain vanished after roll-out | Shipwreck survivors and dolphins | Analogy | Self-selection bias | Sailors, islands |
| Code | New CSV parser | An existing parser function | Requirement | Signature, error handling | Its hard-coded file path |

The drone and HR rows come from the strategic-analogy paper. The same target task appears with different examples, so only the role changes.

**Rules against easy data**

- The role is often implied, not announced. Real users rarely write "this is an analogy". About half the variants state the role; the rest leave it to context.
- Every counter-example looks similar on the surface. ARN shows this is where models fail: GPT-4 scores 29.1% when the distractor is near and the analogy is far.
- Long contexts are included. AnaloBench shows GPT-4 falls from 89.1% to 60.7% as stories grow from 1 to 30 sentences.
- Two annotators rate each seed for realism on a 1–5 scale. We keep seeds rated 4 or above.
- We compare our seeds with a WildChat sample on length, domain and how the example is phrased, and report the gap.

## Layer-level experiments

We will run sir's idea in three steps: find the layers where source details take over, switch those parts off without training, then train only those layers. Our benchmark adds what earlier layer studies lacked. It scores useful transfer as well as copying, so we can see whether an intervention kills both.

| Technique | What it changes | Question it answers | Prior evidence | We run it? |
| --- | --- | --- | --- | --- |
| Logit lens per layer | Nothing; reads each layer's guess | At which layer does a source detail replace the right answer? | [Halawi et al., ICLR 2024](https://arxiv.org/abs/2307.09476): middle layers hold the right answer, late layers overwrite it with copied false demonstrations | Yes |
| Linear probes per layer | Nothing; trains a small classifier on hidden states | Does a layer encode the example's role? | Standard probing; needs lexical controls | Yes |
| Activation patching | Swaps one layer's activations between two variants | Which layers and heads carry the role? | [Function vectors, ICLR 2024](https://arxiv.org/abs/2310.15213): a few middle-layer heads carry the task shown in context | Yes |
| Head or neuron ablation | Zeroes a few heads or MLP neurons | Does removing "copy" units cut detail leakage? | Halawi: ablating 5 heads (about 1%) cuts the false-demo gap by 38.9% on 14 datasets. [Copy Bias](https://aclanthology.org/2026.findings-eacl.13/): pruning MLP neurons | Yes |
| Last-layer retraining | Retrains only the final layer(s) | Is fixing the last layers enough? | [DFR, ICLR 2023](https://arxiv.org/abs/2204.02937): retraining only the last layer removes reliance on spurious features | Yes, as a method baseline |
| LoRA only in chosen layers | Trains adapters only where patching points | Does targeted training beat LoRA everywhere? | Our own ablation | Yes |
| Layer removal | Drops whole late layers | Does copying live in the deepest layers? | [Gromov et al., ICLR 2025](https://arxiv.org/abs/2403.17887): many deep layers can be removed with small QA loss | Exploratory |
| Added module | A small scope-gating head beside the model | Does an explicit take/drop/keep signal help? | None; our idea | Optional |

**Order of work**

1. **Diagnose (no training).** On matched pairs (same content, different role), run the logit lens, probes and patching. Output: the layers where role is encoded and where source details enter the answer.
2. **Intervene (no training).** Ablate the heads or neurons found in step 1. Report leakage, appropriate transfer and joint success. Copy Bias and Halawi report only accuracy, so this is new.
3. **Train.** Compare retraining the last k blocks, LoRA in the chosen layers, and LoRA everywhere, with the same data and compute.

**Compute.** Internal analysis needs full-precision weights; 4-bit models distort activations. An 8B model in bf16 needs about 16GB for weights alone, so step 1 runs on 3–4B models (Qwen2.5-3B, Llama-3.2-3B) on our own GPUs. We repeat the main result on one 8B model on a rented A100. Tools: TransformerLens or nnsight.

## What changes in our plan

The topic holds: no paper we read tests role-dependent use of a user's example. Seven parts of the proposal change.

1. **Motivation.** The GPT-4 "high recall, low precision" result holds only when GPT-4 is told to use a story. Without that hint it named no source story at all. We will state both conditions and note the paper's own inconsistency.
2. **Venues.** Do as I Say is a COLM 2026 workshop poster. Copy Bias is confirmed as Findings of EACL 2026, and Relevant or Random as Findings of ACL 2025.
3. **Data.** Seeds start from real situations, with the sources and rules above. Super-NaturalInstructions and ParallelPARC join the building blocks.
4. **WildChat licence.** It is ODC-BY, changed from ImpACT on 26 June 2024, so the licence risk is lower. Privacy rules stay: no raw user text released.
5. **Baselines.** Add an RL baseline (GRPO) next to SFT and DPO. ReTRE shows SFT can reach 100% in-distribution and still fall below the untrained model on rewrites.
6. **Layer analysis.** It moves from optional to a core part, in the three steps above. The pilot's third week adds a logit-lens run on a 3B model.
7. **Related work.** Add Halawi et al. (false induction heads) and function vectors, since they are the closest layer-level work.

**Still open**

- [ ] ARN's data link (a bit.ly short link) did not load. Ask the authors or find a mirror.
- [ ] Licences for Lost in Conversation, AnaloBench, ParallelPARC and ePiC.
- [ ] Whether Lost in Multi-Turn appeared at ICLR 2026.

## Sources

Papers read in full:

- [Do as I Say, Not as I Do: Instruction-Induction Conflict in LLMs](https://arxiv.org/abs/2605.20382)
- [Mitigating Copy Bias in In-Context Learning through Neuron Pruning](https://aclanthology.org/2026.findings-eacl.13/)
- [LLMs Get Lost in Multi-Turn Conversation](https://arxiv.org/abs/2505.06120)
- [LLMs Get Lost in Evolving User Intent](https://arxiv.org/abs/2607.20734)
- [Can LLMs Help Improve Analogical Reasoning for Strategic Decisions?](https://arxiv.org/abs/2505.00603)
- [Relevant or Random: Can LLMs Truly Perform Analogical Reasoning?](https://aclanthology.org/2025.findings-acl.1230)
- [AnaloBench](https://aclanthology.org/2024.emnlp-main.725)
- [ARN: Analogical Reasoning on Narratives](https://arxiv.org/abs/2310.00996)
- [ReTRE](https://aclanthology.org/2026.acl-long.2048/)
- [ARCANA](https://arxiv.org/abs/2610.29271)

Layer-level work (abstracts and venue pages only):

- [Overthinking the Truth: Understanding how Language Models Process False Demonstrations](https://arxiv.org/abs/2307.09476)
- [Function Vectors in Large Language Models](https://arxiv.org/abs/2310.15213)
- [Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations](https://arxiv.org/abs/2204.02937)
- [The Unreasonable Ineffectiveness of the Deeper Layers](https://arxiv.org/abs/2403.17887)

Datasets:

- [WildChat-1M dataset card](https://huggingface.co/datasets/allenai/WildChat-1M)
- [LMSYS-Chat-1M](https://huggingface.co/datasets/lmsys/lmsys-chat-1m)
- [Super-NaturalInstructions](https://arxiv.org/abs/2204.07705)
- [Lost in Conversation code and data](https://github.com/microsoft/lost_in_conversation)
- [AnaloBench code and data](https://github.com/JHU-CLSP/AnaloBench)
- [ParallelPARC](https://aclanthology.org/2024.naacl-long.329)
- [ePiC](https://aclanthology.org/2022.acl-long.276)
- [ARCANA data](https://github.com/density-11/arcana-test)
