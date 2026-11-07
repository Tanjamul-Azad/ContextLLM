# Research Proposal: Role-Aware Selective Transfer in Large Language Models

7 November 2026

**Md. Tanzamul Azad (0112230863)**, United International University. **Target venue:** ACL or EMNLP main track.

## Abstract

Users often explain what they want through an example. The example plays a role: it may show an idea to borrow, a part to follow exactly, or a pattern to avoid. We propose to study whether large language models use a user's example according to its role, to locate the internal mechanism behind the errors, and to correct them with targeted training. A pilot with six models found that models often carry over details they should leave behind, or ignore parts they were asked to keep. Open models failed on 40–47% of prompts and frontier models on 17–30%. We will build a human-validated benchmark, test the mechanism causally, and evaluate a scope-supervised fine-tuning method against strong baselines.

## 1. Background and motivation

Suppose a user asks for a priority scheme for a university IT help desk, with at most three levels, and cites hospital triage. The principle "urgent cases first" should transfer; the colour codes and minute-based times should not. If the user instead says the faculty already uses those colour codes, the colour names become required. The correct answer therefore depends on the example's role, which the prompt states or implies.

Related work studies parts of this problem. Ali et al. (2026) prune neurons to reduce copying from demonstrations. Halawi et al. (2024) find late layers that copy false demonstrations. Camassa and Shiller (2026) show instructions losing to in-context patterns. AnaloBench (Ye et al., 2024) tests whether models can identify analogies. In all of these, copying is either always wrong or never required. No work tests whether models adapt what they transfer to the role of a user-supplied example, where copying is sometimes required and sometimes harmful.

## 2. Research questions

**Main research question.** When a user gives an example, do large language models use it according to the role the user intends, and if not, why do they fail and can training correct it?

The question breaks into three parts, one for each stage of the study:

1. **Behaviour.** When only the role of an example changes, do models change what they transfer accordingly, while keeping the user's own constraints?
2. **Mechanism.** Which internal components carry the example's role and drive the transfer of source details?
3. **Correction.** Does training that supervises transfer scope improve role-correct transfer on unseen tasks, beyond prompting and standard fine-tuning?

## 3. Preliminary results

The pilot used 10 seeds (6 planning tasks with JSON answers, 4 code tasks with unit tests), each in three roles, giving 130 automatically scored prompts per model.

| Model | Failure, plain wording | Failure, explicit wording |
| --- | --- | --- |
| Qwen2.5-3B | 47% | 33% |
| Qwen2.5-7B (4-bit) | 40% | 30% |
| Llama-3.1-8B (4-bit) | 43% | 27% |
| GPT-4.1-mini | 23% | 7% |
| GPT-5.4-mini | 17% | 0% |
| GPT-5.4 | 30% | 3% |

Explicit instructions largely fix frontier models but not open ones, so the hard case is inferring the role from context. A logit-lens reading of Qwen2.5-3B shows the roles' predictions diverging around layers 23–28 of 36; causal tests are still to come. These results are provisional: the seeds have not yet been validated by independent annotators.

**Why not simply ask explicitly?** The explicit condition works as an oracle: the user states which parts to take and which to leave, which is the very judgement the model is meant to make. Real users rarely do this. In our samples of WildChat and OASST2, people give the example and leave the role implied, and under that realistic condition frontier models still fail 17–30% of the time. Open models, which are widely deployed for cost and privacy reasons, fail 27–33% of the time even when told explicitly. Agents that reuse retrieved documents or earlier code face the same problem with no one to state the scope. The pilot examples were also short and fairly direct; whether longer contexts and weaker cues raise frontier failure rates will be tested in the validation week.

**Code and data.** The code, the 130 prompts, all 780 model answers and their scores are on [GitHub](https://github.com/Tanjamul-Azad/ContextLLM). A browsable copy with spreadsheets and Colab notebooks is in a [Google Drive folder](https://drive.google.com/drive/folders/1PDY9RPmH4ioq-y9gHqcQZVryrqk3Xnwm).

## 4. Proposed methodology

### 4.1 Dataset

The basic unit is a seed: a target task, a source example, the relation that may carry over, and the user's constraints. Each seed is written in several variants that change only the example's role, how clearly that role is signalled, or how well the example fits the task. For every variant the gold answer lists what must be used, what may be used and what must not be used, each tied to the wording of the prompt. This lets us separate a harmful transfer from a harmless optional one. Tasks come from two families where answers can be checked automatically: planning problems with a JSON answer, and code tasks with unit tests.

The test set (120–200 seeds) will be written fresh or adapted from documented real cases, and each seed will be checked by two annotators working independently. Training data will come mainly from existing resources converted to the same format. Super-NaturalInstructions provides positive and negative examples with explanations for over 1,600 tasks; AnaloBench and ARN provide analogies and misleading look-alikes. No source used in training will appear in the test set, and whole task families are held out to test generalisation. Because public data may have been seen by the models, we run contamination diagnostics on every reused source.

### 4.2 Mechanism study

On development data we compare matched prompts that differ only in the example's role, using the logit lens and probing to find where the role becomes visible. We then test those locations causally on held-out data with activation patching, and ablate the components that drive harmful copying. An ablation counts as a success only if harmful transfer drops while useful transfer and general ability are preserved, compared against random ablations of the same size.

### 4.3 Training method

We fine-tune with LoRA using an objective with three parts: producing a valid answer, predicting the transfer scope, and staying consistent across paired variants, so that the answer changes when the role changes but not when only incidental details do. Gold scope is used only in training; at test time the model must infer it from the prompt. If the mechanism study locates the role in specific layers, we also train only those layers.

### 4.4 Baselines and evaluation

Every method is compared on the same test seeds, and every trained method gets the same data and the same tuning budget.

| Comparison | Purpose |
| --- | --- |
| No example | Shows whether a failure comes from the example or from the task itself |
| Plain prompt | The realistic condition: the role is stated or implied as a user would |
| Scope-inference prompt | A strong prompting baseline: the model is asked to work out what to take before answering |
| Explicit scope (oracle) | Upper bound: the gold scope is given; reported as a diagnostic, not as a competitor |
| Supervised fine-tuning | Standard training on the same data without scope supervision |
| LoRA on all or random layers | Tests whether choosing layers from the mechanism study matters |
| Random ablation | Control for the mechanism study: removing as many random components |

The main measure is joint success: the answer uses what it must, avoids what it must not, and keeps the user's constraints. We also report harmful transfer, missed transfer and broken constraints separately, and keep format errors apart from content errors. Results use seed-level bootstrap intervals and paired tests, because variants of one seed are related. Generalisation is measured on held-out task families, and general ability (for example GSM8K and MMLU) is checked after every intervention or training run. Trained methods are averaged over three random seeds.

## 5. Expected contributions

1. A benchmark in which the same example appears in different roles, with a gold answer grounded in the prompt, validated by independent annotators.
2. A causal account of how models decide what to take from an example, covering both useful and harmful transfer.
3. A training method that improves role-correct transfer on unseen task families.

If the training method does not beat the baselines, the first two contributions still stand as a benchmark and analysis paper.

I would be grateful for your feedback on the scope, and for guidance on the annotator arrangement and compute support.

## References

- Ali, A., Wolf, L. and Titov, I. (2026). [Mitigating Copy Bias in In-Context Learning through Neuron Pruning](https://aclanthology.org/2026.findings-eacl.13/). Findings of EACL.
- Camassa, C. and Shiller, D. (2026). [Do as I Say, Not as I Do: Instruction-Induction Conflict in LLMs](https://arxiv.org/abs/2605.20382). Sci-FM Workshop, COLM.
- Halawi, D., Denain, J.-S. and Steinhardt, J. (2024). [Overthinking the Truth: Understanding how Language Models Process False Demonstrations](https://arxiv.org/abs/2307.09476). ICLR.
- Sourati, Z., Ilievski, F., Sommerauer, P. and Jiang, Y. (2023). [ARN: Analogical Reasoning on Narratives](https://arxiv.org/abs/2310.00996). arXiv.
- Wang, Y. et al. (2022). [Super-NaturalInstructions: Generalization via Declarative Instructions on 1600+ NLP Tasks](https://arxiv.org/abs/2204.07705). EMNLP.
- Ye, X. et al. (2024). [AnaloBench: Benchmarking the Identification of Abstract and Long-context Analogies](https://aclanthology.org/2024.emnlp-main.725/). EMNLP.
- Zhang, F. and Nanda, N. (2024). [Towards Best Practices of Activation Patching in Language Models](https://proceedings.iclr.cc/paper_files/paper/2024/hash/06a52a54c8ee03cd86771136bc91eb1f-Abstract-Conference.html). ICLR.
