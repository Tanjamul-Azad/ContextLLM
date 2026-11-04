# How to read the results folder

| Folder / file | Experiment | What is inside |
| --- | --- | --- |
| `behaviour/<model>/generations.jsonl` | E4–E6 | Every prompt sent and every raw answer, one JSON per line |
| `behaviour/<model>/scored.jsonl` | E4–E6 | The automatic scores for each answer, with the reason for every failed check |
| `behaviour/summary.md` | E4–E6 | Tables per model and condition, pass / fail per rule |
| `behaviour/per_seed.csv` | E4–E6 | Joint success and copied pattern per seed and role |
| `behaviour/figures/` | E4–E5 | Joint success by role; copy rate by role |
| `logit_lens/<model>/` | E7 | Per-layer scan (`layer_scan.csv`), one plot per probe, `summary.json` |
| `contamination/<model>/` | E3 | Guided-completion and Min-K% scores on GSM8K |
| `E1_wildchat/` | E1 | Labels for candidate turns (hashes only, no user text) and counts |
| `logs/run_all.log` | all | Start and end time of every step |
| `overview.json` | all | Every headline number in one file |

## Score fields in `scored.jsonl`

| Field | Meaning |
| --- | --- |
| `format_ok` | The answer could be parsed (JSON object, or Python code that defines the function) |
| `constraint_ok` | Every target rule holds (for example at most 3 levels, tests pass) |
| `transfer_ok` | The answer does what the example's role asks: borrows the idea, copies the required part, or avoids the rejected pattern |
| `leak` | The answer copies an incidental detail it should have left behind |
| `joint` | All of the above at once: our main score |
| `marker` | The answer copies the example's distinctive pattern. Right for a requirement, wrong for a counter-example |
| `detail` | For each check: pass or fail, and what the check saw |

A `role` of `none` is the baseline with no example at all.
