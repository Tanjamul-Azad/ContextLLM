"""E3: contamination checks, shown on GSM8K (a public test set that our target tasks reuse).

1. Guided completion (Golchin and Surdeanu, ICLR 2024): give the first half of a test question
   with the dataset name, and without it; measure how close the model's completion is to the real second half.
2. Min-K% Prob (Shi et al., ICLR 2024): score original questions and paraphrases of the same
   questions; memorised text scores higher. Our own seed texts are the fresh reference.

Usage: python -I src/contamination.py [MODEL_KEY] [N]
Writes results/contamination/<model>/summary.json and items.csv.
"""
import csv
import json
import os
import random
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch  # noqa: E402

from run_behaviour import MODELS, ROOT, generate, load  # noqa: E402
from seeds import SEEDS  # noqa: E402

VIEWER = "https://datasets-server.huggingface.co/rows?dataset=openai/gsm8k&config=main&split=test&offset={o}&length=100"


def fetch_gsm8k(n, seed=3):
    random.seed(seed)
    off = random.choice(range(0, 1300 - 100))
    for _ in range(5):
        try:
            with urllib.request.urlopen(VIEWER.format(o=off), timeout=60) as r:
                rows = [x["row"]["question"] for x in json.load(r)["rows"]]
            return rows[:n], off
        except Exception:
            time.sleep(10)
    raise RuntimeError("could not fetch GSM8K rows")


def lcs(a, b):
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[-1]))
        prev = cur
    return prev[-1]


def rouge_l(pred, ref):
    p, r = pred.lower().split(), ref.lower().split()
    if not p or not r:
        return 0.0
    l = lcs(p, r)
    if l == 0:
        return 0.0
    prec, rec = l / len(p), l / len(r)
    return 2 * prec * rec / (prec + rec)


@torch.no_grad()
def min_k(tok, model, text, k=0.2):
    ids = tok(text, return_tensors="pt").input_ids.to(model.device)
    logits = model(ids).logits[0, :-1].float()
    lp = torch.log_softmax(logits, -1).gather(1, ids[0, 1:, None])[:, 0]
    n = max(1, int(len(lp) * k))
    return lp.sort().values[:n].mean().item()


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5-3b"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    out_dir = os.path.join(ROOT, "results", "contamination", key)
    os.makedirs(out_dir, exist_ok=True)
    qs, off = fetch_gsm8k(n)
    tok, model = load(key)

    halves = []
    for q in qs:
        w = q.split()
        cut = len(w) // 2
        halves.append((" ".join(w[:cut]), " ".join(w[cut:])))
    guided = [[{"role": "user", "content": "You are given the first part of a question from the test split of the GSM8K dataset. "
                "Finish the question exactly as it appears in the dataset. Reply with the rest of the question only.\n\n"
                f"First part: {h}"}] for h, _ in halves]
    general = [[{"role": "user", "content": "Finish this question. Reply with the rest of the question only.\n\n"
                 f"First part: {h}"}] for h, _ in halves]
    para = [[{"role": "user", "content": "Rewrite this math word problem with different names, objects and wording, "
              "but keep every number and the same answer. Reply with the rewritten problem only.\n\n" + q}] for q in qs]

    def gen_all(batches, max_new):
        out = []
        for i in range(0, len(batches), 8):
            out += generate(tok, model, batches[i:i + 8], max_new_tokens=max_new)
        return out

    g_out = gen_all(guided, 80)
    n_out = gen_all(general, 80)
    p_out = gen_all(para, 200)

    rows = []
    for q, (h, rest), go, no, po in zip(qs, halves, g_out, n_out, p_out):
        rows.append({
            "rouge_guided": round(rouge_l(go, rest), 3),
            "rouge_general": round(rouge_l(no, rest), 3),
            "mink_original": round(min_k(tok, model, q), 3),
            "mink_paraphrase": round(min_k(tok, model, po.strip()), 3),
        })
    fresh = [round(min_k(tok, model, f"{s['task']} {s['rules']}"), 3) for s in SEEDS]

    def mean(xs):
        return round(sum(xs) / len(xs), 3)

    wins = sum(r["mink_original"] > r["mink_paraphrase"] for r in rows)
    summary = {
        "model": MODELS[key],
        "dataset": f"openai/gsm8k test, {len(qs)} questions from offset {off}",
        "guided_completion": {
            "mean_rouge_l_guided": mean([r["rouge_guided"] for r in rows]),
            "mean_rouge_l_general": mean([r["rouge_general"] for r in rows]),
            "share_near_verbatim_guided(>=0.75)": round(sum(r["rouge_guided"] >= 0.75 for r in rows) / len(rows), 3),
            "share_near_verbatim_general(>=0.75)": round(sum(r["rouge_general"] >= 0.75 for r in rows) / len(rows), 3),
        },
        "min_k_prob(k=20%)": {
            "mean_original": mean([r["mink_original"] for r in rows]),
            "mean_paraphrase": mean([r["mink_paraphrase"] for r in rows]),
            "share_original_scores_higher_than_its_paraphrase": round(wins / len(rows), 3),
            "mean_our_fresh_seed_texts": mean(fresh),
        },
        "rule": "Flag the source if more than 5% of items come back near word for word, or if originals score clearly higher than paraphrases.",
    }
    gc = summary["guided_completion"]
    summary["flag_source"] = gc["share_near_verbatim_guided(>=0.75)"] > 0.05 or summary["min_k_prob(k=20%)"]["share_original_scores_higher_than_its_paraphrase"] > 0.7
    with open(os.path.join(out_dir, "items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
