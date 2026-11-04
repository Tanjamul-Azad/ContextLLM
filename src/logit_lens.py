"""E7: logit-lens layer scan.

At the first token where the answer must either copy the example's marker or not,
we read every layer's guess (final norm + LM head on that layer's hidden state)
and compare log-probability of the "copy" tokens with the "alternative" tokens.

Usage: python -I src/logit_lens.py [MODEL_KEY]
Writes results/logit_lens/<model>/layer_scan.csv, summary.json and one plot per seed.
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from prompts import ROLES, build  # noqa: E402
from run_behaviour import MODELS, ROOT, load  # noqa: E402
from seeds import SEEDS  # noqa: E402

# seed id -> (answer prefix the model continues from, copy words, alternative words)
PROBES = {
    "P1_helpdesk_triage": ('{"levels": [{"name": "',
                           ["Red", "Orange", "Yellow", "Green", "Blue"],
                           ["Critical", "Urgent", "High", "Priority", "Level", "Emergency", "Immediate", "Standard", "Low", "P"]),
    "P2_drone_pricing": ('{"charges": [{"name": "',
                         ["Power"],
                         ["Base", "Seasonal", "Season", "Per", "Inspection", "Flight", "Hour", "Hourly", "Subscription", "Monthly", "Basic", "Standard", "Field", "Acre"]),
    "P6_exam_hall_boarding": ('{"groups": [{"name": "',
                              ["Zone"],
                              ["Group", "Row", "Back", "Rear", "Far", "Batch", "Wave", "First", "Rows", "Block", "Section"]),
    "C1_window_sum": ("```python\ndef max_window_sum(nums, k",
                      ["="],
                      [")", "):", ":"]),
    "C2_retry_backoff": ("```python\ndef retry_call(fn, attempts, sleep):\n    delay = ",
                         ["1"],
                         ["0"]),
}


def first_ids(tok, words):
    ids = set()
    for w in words:
        t = tok.encode(w, add_special_tokens=False)
        if t:
            ids.add(t[0])
    return sorted(ids)


@torch.no_grad()
def scan(tok, model, messages, prefix, copy_ids, alt_ids):
    text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True) + prefix
    enc = tok(text, return_tensors="pt").to(model.device)
    out = model(**enc, output_hidden_states=True)
    hs = out.hidden_states
    norm = model.model.norm
    head = model.lm_head
    final = out.logits[0, -1].float()
    rows = []
    n = len(hs)
    for layer in range(n):
        h = hs[layer][0, -1]
        logits = head(norm(h)).float() if layer < n - 1 else None
        if layer == n - 1:
            # HF already applies the final norm to the last hidden state; check against the real logits.
            cand = head(h).float()
            logits = cand if torch.allclose(cand, final, atol=1e-2, rtol=1e-2) else head(norm(h)).float()
        lp = torch.log_softmax(logits, -1)
        c = torch.logsumexp(lp[copy_ids], 0).item()
        a = torch.logsumexp(lp[alt_ids], 0).item()
        rows.append({"layer": layer, "copy_logp": c, "alt_logp": a, "diff": c - a,
                     "top_token": tok.decode([int(lp.argmax())])})
    return rows


def separation_layer(req, cnt, gap=1.0):
    """First layer from which requirement minus counter stays above `gap` nats to the end."""
    d = [r["diff"] - c["diff"] for r, c in zip(req, cnt)]
    for i in range(len(d)):
        if all(x > gap for x in d[i:]):
            return i
    return None


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5-3b"
    out_dir = os.path.join(ROOT, "results", "logit_lens", key)
    os.makedirs(out_dir, exist_ok=True)
    tok, model = load(key)
    by_id = {s["id"]: s for s in SEEDS}
    all_rows, summary = [], {"model": MODELS[key], "probes": {}}
    for sid, (prefix, copy_w, alt_w) in PROBES.items():
        seed = by_id[sid]
        copy_ids, alt_ids = first_ids(tok, copy_w), first_ids(tok, alt_w)
        alt_ids = [i for i in alt_ids if i not in copy_ids]
        curves = {}
        for role in ROLES:
            msgs = build(seed, role, "plain", "single")
            rows = scan(tok, model, msgs, prefix, copy_ids, alt_ids)
            curves[role] = rows
            for r in rows:
                all_rows.append({"seed": sid, "role": role, **r})
        sep = separation_layer(curves["requirement"], curves["counter"])
        n_layers = len(curves["requirement"]) - 1
        summary["probes"][sid] = {
            "final_diff": {r: round(curves[r][-1]["diff"], 2) for r in ROLES},
            "final_top_token": {r: curves[r][-1]["top_token"] for r in ROLES},
            "separation_layer": sep,
            "n_layers": n_layers,
            "role_correct_at_output": curves["requirement"][-1]["diff"] > 0 > curves["counter"][-1]["diff"],
        }
        plt.figure(figsize=(7, 3.6))
        for role, colour in zip(ROLES, ["#4C78A8", "#54A24B", "#E45756"]):
            plt.plot([r["layer"] for r in curves[role]], [r["diff"] for r in curves[role]], label=role, color=colour, lw=2)
        plt.axhline(0, color="#888", lw=0.8)
        if sep is not None:
            plt.axvline(sep, color="#888", ls="--", lw=0.8)
        plt.xlabel("layer")
        plt.ylabel("log p(copy) - log p(alternative)")
        plt.title(f"{sid}: does the layer lean towards copying the example?")
        plt.legend(frameon=False)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"{sid}.png"), dpi=130)
        plt.close()
        print(sid, summary["probes"][sid], flush=True)

    with open(os.path.join(out_dir, "layer_scan.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        w.writeheader()
        w.writerows(all_rows)
    n_ok = sum(1 for p in summary["probes"].values() if p["separation_layer"] is not None)
    summary["probes_with_clear_separation"] = f"{n_ok} of {len(PROBES)}"
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
