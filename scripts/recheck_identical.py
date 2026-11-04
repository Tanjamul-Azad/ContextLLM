"""Regenerate the first N saved answers for a model and count how many come out identical.

Use after changing the environment (for example a torchvision fix) to show results do not move.
Usage: python -I scripts/recheck_identical.py MODEL_KEY [N]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import run_behaviour as rb  # noqa: E402

key = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 16
with open(os.path.join(ROOT, "results", "behaviour", key, "generations.jsonl"), encoding="utf-8") as f:
    gens = [json.loads(line) for line in f][:n]
tok, model = rb.load(key)
same = 0
for i in range(0, n, 8):
    outs = rb.generate(tok, model, [g["messages"] for g in gens[i:i + 8]])
    same += sum(o == g["output"] for o, g in zip(outs, gens[i:i + 8]))
print(f"{key}: {same} of {n} answers identical to the saved run")
