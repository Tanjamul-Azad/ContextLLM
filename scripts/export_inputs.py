"""Export the input data of the pilot behaviour runs as readable CSVs.

results/inputs/seeds.csv   one row per seed: task, user rules, source example, role wordings, checks
results/inputs/prompts.csv the exact 130 prompts every model received (same for all six models)
Usage: python -I scripts/export_inputs.py
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from prompts import all_conditions  # noqa: E402
from seeds import SEEDS  # noqa: E402

OUT = ROOT / "results" / "inputs"
OUT.mkdir(parents=True, exist_ok=True)

with open(OUT / "seeds.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed", "family", "based_on", "target_task", "user_rules", "answer_format", "source_example",
                "role_wordings", "rule_checks", "copy_marker"])
    for s in SEEDS:
        w.writerow([s["id"], s["family"], s["basis"], s["task"], s["rules"], s["format"], s["example"],
                    json.dumps(s["roles"], ensure_ascii=False, indent=1, default=str),
                    json.dumps(s["constraints"], default=str), json.dumps(s["marker"], default=str)])

n = 0
with open(OUT / "prompts.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["item", "seed", "family", "role", "wording", "turns", "prompt"])
    for item, seed, role, wording, turns, msgs in all_conditions():
        prompt = "\n\n".join(f"[{m['role']}] {m['content']}" for m in msgs)
        w.writerow([item, seed["id"], seed["family"], role or "none", wording, turns, prompt])
        n += 1
print(f"wrote {len(SEEDS)} seeds and {n} prompts to {OUT}")
