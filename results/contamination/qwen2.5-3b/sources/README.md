# Contamination checks on reused public sources (Qwen2.5-3B-Instruct)

Script: `src/contamination_sources.py` (run 2026-11-05, 02:25 to 02:44, about 19 minutes on one RTX 4060; log in `results/logs/contamination_sources.log`).
Same two checks as the GSM8K run in `results/contamination/qwen2.5-3b/summary.json`:

- Guided completion (Golchin and Surdeanu, ICLR 2024): the model gets the first half of an item, with the dataset name (guided) or without it (general). Near-verbatim = ROUGE-L >= 0.75 against the real second half.
- Min-K% Prob, k = 20% (Shi et al., ICLR 2024): each original is scored against a paraphrase written by the same model. The column gives the share of pairs where the original scores higher.

Flag rule (protocol section 3): flag if guided near-verbatim share > 5%, or originals beat paraphrases in > 70% of pairs.

| Source | Items used | n | Near-verbatim guided / general | Mean ROUGE-L guided / general | Min-K% original > paraphrase | Flagged |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Super-NaturalInstructions | task definitions, `jayelm/natural-instructions` test split, 50 distinct tasks | 50 | 0.00 / 0.00 | 0.188 / 0.193 | 0.70 | no (at the threshold) |
| HumanEval | function prompts, `openai/openai_humaneval` test | 50 | 0.00 / 0.00 | 0.157 / 0.171 | 0.40 | no |
| Spider | questions with >= 12 words, `xlangai/spider` validation | 50 | 0.00 / 0.00 | 0.133 / 0.096 | 0.36 | no |
| AnaloBench | gold stories, `jhu-clsp/AnaloBench` config T1S10-Full | 50 | 0.00 / 0.00 | 0.145 / 0.150 | 0.36 | no |
| ParallelPARC | - | 0 | - | - | - | not tested |
| GSM8K (earlier run, for reference) | test questions | 60 | 0.00 / 0.017 | 0.278 / 0.305 | 0.17 | no |

Per-item scores are in `<source>/items.csv`. These files hold item ids (task name, row index or task id) and scores only, with no dataset text. Run status is in `run_status.json`.

## Notes

- Super-NaturalInstructions is borderline. Originals beat paraphrases in exactly 70% of pairs, and the mean Min-K% gap is the largest of the four sources (-5.97 vs -7.03). Strictly, the rule (> 70%) does not flag it. These task definitions are widely used in instruction tuning (Flan, Tulu and others), so exposure is plausible. Treat reused definitions as at risk: rewrite them before they enter test, or recheck them with more items and a second model.
- ParallelPARC was skipped. On 2026-11-05 a Hub search for "ParallelPARC", "parallelparc", "parallel_parc" and "Parallel-PARC" returned no datasets. It was not fetched from any other host.
- `Muennighoff/natural-instructions` was not usable because the dataset viewer still reported it as processing. The public mirror `jayelm/natural-instructions` was used instead. Super-NI was tested only on its task definitions, not on positive or negative example text.
- Spider questions are short (median about 15 words), so each half is only 6 to 10 words and ROUGE-L is noisy. The Spider row covers the questions only, not the SQL.
- The originals of every source score higher (less surprising) than our own seed texts (-9.42), except Spider (-10.13). That comparison mixes text types and is not evidence on its own.

## Limitations

- Only one small model was tested (Qwen2.5-3B-Instruct, greedy decoding). Larger or other models may memorise more.
- A negative result does not prove an item was absent from training data. Guided completion misses items the model saw but cannot reproduce. Min-K% against self-written paraphrases is weak when paraphrases are themselves fluent, high-probability text.
- 50 items per source give a wide interval. A 0% near-verbatim share is consistent with a true rate of a few percent.
- These checks cover the public source texts only. They do not certify new items we build from those sources.
