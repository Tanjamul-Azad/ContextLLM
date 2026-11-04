"""Export the seeds for reading (data/seeds.json) and the E2 annotation sheet (data/E2_annotation_sheet.csv).

E2 needs two people: each fills the 'annotator' columns without looking at the other's sheet.
Usage: python -I src/export_seeds.py
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import ROLES, role_text  # noqa: E402
from seeds import SEEDS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)

with open(os.path.join(ROOT, "data", "seeds.json"), "w", encoding="utf-8") as f:
    json.dump(SEEDS, f, indent=1, ensure_ascii=False, default=str)

with open(os.path.join(ROOT, "data", "E2_annotation_sheet.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seed", "role", "task", "rules", "what_the_user_says", "annotator: what MUST carry over",
                "annotator: what must NOT carry over", "annotator: is the right answer clear? (yes/no)", "notes"])
    for s in SEEDS:
        for r in ROLES:
            w.writerow([s["id"], r, s["task"], s["rules"], role_text(s, r, "plain"), "", "", "", ""])
print(f"wrote {len(SEEDS)} seeds and {len(SEEDS) * len(ROLES)} annotation rows")
