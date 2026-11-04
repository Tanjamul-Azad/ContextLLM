# ContextLLM: Role-Aware Example Use in LLMs

Tanjamul Azad · United International University

When a user gives an LLM an example, the example can play different roles:

- **Analogy**: borrow its idea, not its details.
- **Requirement**: follow it exactly in some respect.
- **Counter-example**: avoid what it does.

This project tests whether models use an example according to its role, finds where inside the model the wrong parts get copied, and trains the model to fix it. Target venue: EMNLP 2027.

**Start here:** [RESULTS.md](RESULTS.md) has every pilot result in one page, with the go / no-go verdict for each experiment.

## Repository map

| Path | What it holds |
| --- | --- |
| [docs/proposal.md](docs/proposal.md) | Research proposal (updated with sir's feedback) |
| [docs/feasibility-sprint.md](docs/feasibility-sprint.md) | One-week go / no-go plan (5–11 Nov 2026) and pass marks |
| [docs/related-work-deep-read.md](docs/related-work-deep-read.md) | Full reading of the 10 closest papers |
| [docs/compute-plan.md](docs/compute-plan.md) | GPU and credit plan |
| [src/seeds.py](src/seeds.py) | Pilot seeds: 10 tasks × 3 roles, with automatic checks |
| [src/checks.py](src/checks.py) | Scoring: format, target rules, transfer, leakage, copied pattern |
| [src/prompts.py](src/prompts.py) | Builds every condition (role × wording × single/multi-turn) |
| [src/run_behaviour.py](src/run_behaviour.py) | E4–E6: generate and score answers |
| [src/analyze.py](src/analyze.py) | Metrics, seed-level bootstrap intervals, figures |
| [src/logit_lens.py](src/logit_lens.py) | E7: layer scan |
| [src/contamination.py](src/contamination.py) | E3: guided completion and Min-K% Prob |
| [src/wildchat_mine.py](src/wildchat_mine.py) | E1: example-giving turns in real WildChat conversations |
| [data/seeds.json](data/seeds.json) | The seeds in readable form |
| [data/E2_annotation_sheet.csv](data/E2_annotation_sheet.csv) | Sheet for the two-annotator agreement check (E2) |
| [results/](results/) | Every raw answer, score, summary and figure |
| [tests/validate_checks.py](tests/validate_checks.py) | Proves the checks pass correct answers and catch copied ones |

## How to run

```bash
pip install -r requirements.txt
python -I tests/validate_checks.py      # checks are correct: 0 problems expected
bash scripts/run_all.sh                 # all experiments, about 1–2 hours on an RTX 4060 (8GB)
python -I src/analyze.py                # rebuild summaries from saved answers
```

Each step's start, end and output is logged in `results/logs/run_all.log`. Generation is greedy (no sampling), so a rerun gives the same answers.

## Data policy

Raw WildChat user text is never committed. It stays in `local_only/` (git-ignored) for hand-checking; the repository keeps only conversation hashes, lengths and labels. WildChat is released under ODC-BY.

## Environment notes

- Tested with torch 2.6.0+cu124, torchvision 0.21.0+cu124, transformers 5.5.0, bitsandbytes 0.49.2, Python 3.13, Windows, RTX 4060 (8GB).
- torchvision must match torch. A mismatched one (we had 0.26 with torch 2.6) breaks `transformers` imports; [src/_compat.py](src/_compat.py) then blocks it, which does not change any text result. After installing the matching version, all three models reproduced 16 of 16 saved answers exactly (`python -I scripts/recheck_identical.py <model>`).
- Loading the 4-bit 7B/8B models can crash on Windows after a long session (access violation while memory-mapping the weights). A restart fixed it.
