"""Kill test 2: is the example's role readable inside the model, and does patching it in repair failures?

Development cards only (data/seeds_v1_draft). Qwen2.5-3B in bf16 by default.

Steps
  collect : hidden state at the last prompt token, every layer, for every variant; greedy answer + score.
  probe   : per-layer logistic probe trained on stated-cue variants, tested on implied-cue variants,
            grouped by seed (leave-one-seed-out). Bag-of-words baseline trained and tested the same way.
  type    : each failing implied variant whose stated twin succeeds -> execution failure (probe reads the right
            role) or inference failure. Failures where the stated twin also fails are task failures, not counted.
  patch   : for each failing implied variant, copy the layer-L last-token state from the stated variant of the
            same seed, role and fit; regenerate and rescore. Controls: same patch from a different role of the
            same seed, and a random direction with the same norm as the real patch.

Usage:
  python -I src/role_probe_patch.py collect [--cards D01,C02]
  python -I src/role_probe_patch.py probe
  python -I src/role_probe_patch.py patch --layers 16,20,24,26,28 [--max-new 400] [--limit N]
  python -I src/role_probe_patch.py report
Outputs: results/probe_patch_dev/<model>/. Pass/fail rules: docs/goal-and-kill-tests.md section 3.
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _compat  # noqa: E402,F401
import torch  # noqa: E402

from checks_v1 import score_v1  # noqa: E402
from seed_lint_v1 import build_messages  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = {"qwen2.5-3b": "Qwen/Qwen2.5-3B-Instruct"}
ROLES = ["analogy", "requirement", "counter"]


def out_dir(model):
    d = os.path.join(ROOT, "results", "probe_patch_dev", model)
    os.makedirs(d, exist_ok=True)
    return d


def load_cards(only=None):
    cards = []
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "seeds_v1_draft", "*.json"))):
        c = json.load(open(p, encoding="utf-8"))
        if not only or any(c["id"].startswith(o) for o in only):
            cards.append(c)
    return cards


def load_model(key):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODELS[key])
    model = AutoModelForCausalLM.from_pretrained(MODELS[key], dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    return tok, model


def encode(tok, msgs, device):
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return tok(text, return_tensors="pt").to(device)


@torch.no_grad()
def last_token_states(model, enc):
    out = model(**enc, output_hidden_states=True)
    # hidden_states[0] is the embedding output; [i] is the output of block i-1.
    return torch.stack([h[0, -1, :].float().cpu() for h in out.hidden_states]).numpy()


@torch.no_grad()
def generate(model, tok, enc, max_new):
    o = model.generate(**enc, max_new_tokens=max_new, do_sample=False, temperature=None, top_p=None, top_k=None,
                       pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return tok.decode(o[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)


class Patch:
    """Replace the last-prompt-token output of block `layer` with `vec` on the prompt pass only."""

    def __init__(self, model, layer, vec):
        self.vec = vec
        self.h = model.model.layers[layer].register_forward_hook(self.hook)

    def hook(self, module, args, output):
        hs = output[0] if isinstance(output, tuple) else output
        if hs.shape[1] > 1:  # prompt pass; later steps see one token at a time
            hs[:, -1, :] = self.vec.to(hs.dtype).to(hs.device)
        return output

    def remove(self):
        self.h.remove()


def cmd_collect(a):
    tok, model = load_model(a.model)
    d = out_dir(a.model)
    rows, states = [], []
    for card in load_cards([c for c in a.cards.split(",") if c]):
        for v in card["variants"]:
            enc = encode(tok, build_messages(card, v, "single"), model.device)
            states.append(last_token_states(model, enc))
            ans = generate(model, tok, enc, a.max_new)
            s = score_v1(ans, card, v)
            rows.append({"card": card["id"], "variant": v["id"], "role": v["role"], "cue": v["cue"], "fit": v["fit"],
                         "text": v["text"], "output": ans, "joint": s["joint"], "format_ok": s["format_ok"]})
            print(card["id"], v["id"], "joint" if s["joint"] else "FAIL", flush=True)
    np.save(os.path.join(d, "states.npy"), np.stack(states))
    with open(os.path.join(d, "items.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"saved {len(rows)} items, states {np.stack(states).shape}")


def _load_collected(model):
    d = out_dir(model)
    items = [json.loads(line) for line in open(os.path.join(d, "items.jsonl"), encoding="utf-8")]
    return items, np.load(os.path.join(d, "states.npy"))


def _fit_predict(Xtr, ytr, Xte):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.1))
    clf.fit(Xtr, ytr)
    return clf.predict(Xte)


def probe_predictions(items, states, layer):
    """Leave-one-seed-out: train on stated variants of the other seeds, predict implied variants of the held-out seed."""
    y = np.array([ROLES.index(r["role"]) for r in items])
    preds = {}
    for card in sorted({r["card"] for r in items}):
        tr = [i for i, r in enumerate(items) if r["card"] != card and r["cue"] == "stated"]
        te = [i for i, r in enumerate(items) if r["card"] == card and r["cue"] == "implied"]
        if not te or len(set(y[tr])) < 3:
            continue
        for i, p in zip(te, _fit_predict(states[tr, layer, :], y[tr], states[te, layer, :])):
            preds[i] = int(p)
    return preds


def bow_predictions(items):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    y = np.array([ROLES.index(r["role"]) for r in items])
    preds = {}
    for card in sorted({r["card"] for r in items}):
        tr = [i for i, r in enumerate(items) if r["card"] != card and r["cue"] == "stated"]
        te = [i for i, r in enumerate(items) if r["card"] == card and r["cue"] == "implied"]
        if not te or len(set(y[tr])) < 3:
            continue
        vec = CountVectorizer(lowercase=True).fit([items[i]["text"] for i in tr])
        clf = LogisticRegression(max_iter=2000).fit(vec.transform([items[i]["text"] for i in tr]), y[tr])
        for i, p in zip(te, clf.predict(vec.transform([items[i]["text"] for i in te]))):
            preds[i] = int(p)
    return preds


def cmd_probe(a):
    items, states = _load_collected(a.model)
    y = [ROLES.index(r["role"]) for r in items]
    acc = {}
    for layer in range(states.shape[1]):
        p = probe_predictions(items, states, layer)
        acc[layer] = round(float(np.mean([p[i] == y[i] for i in p])), 3) if p else None
    bow = bow_predictions(items)
    bow_acc = round(float(np.mean([bow[i] == y[i] for i in bow])), 3) if bow else None
    best = max((l for l in acc if acc[l] is not None), key=lambda l: acc[l])
    best_preds = probe_predictions(items, states, best)
    typing = {"execution": 0, "inference": 0}
    for i, r in enumerate(items):
        twin_ok = any(s["card"] == r["card"] and s["role"] == r["role"] and s["fit"] == r["fit"]
                      and s["cue"] == "stated" and s["joint"] for s in items)
        if r["cue"] == "implied" and not r["joint"] and twin_ok and i in best_preds:
            typing["execution" if best_preds[i] == y[i] else "inference"] += 1
    res = {"probe_acc_implied_by_layer": acc, "best_layer": best, "best_acc": acc[best], "bow_acc_implied": bow_acc,
           "chance": round(1 / 3, 3), "n_implied": len(bow), "failure_typing_at_best_layer": typing,
           "note": "hidden_states index 0 = embeddings; index i = output of block i-1"}
    json.dump(res, open(os.path.join(out_dir(a.model), "probe.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


def cmd_patch(a):
    items, states = _load_collected(a.model)
    tok, model = load_model(a.model)
    cards = {c["id"]: c for c in load_cards()}
    layers = [int(x) for x in a.layers.split(",")]
    targets = [i for i, r in enumerate(items) if r["cue"] == "implied" and not r["joint"]]
    if a.limit:
        targets = targets[: a.limit]
    rng = np.random.default_rng(0)
    path = os.path.join(out_dir(a.model), "patch.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        for i in targets:
            r = items[i]
            card = cards[r["card"]]
            variant = next(v for v in card["variants"] if v["id"] == r["variant"])
            same = [j for j, s in enumerate(items) if s["card"] == r["card"] and s["role"] == r["role"]
                    and s["fit"] == r["fit"] and s["cue"] == "stated"]
            other = [j for j, s in enumerate(items) if s["card"] == r["card"] and s["role"] != r["role"]
                     and s["fit"] == r["fit"] and s["cue"] == "stated"]
            # Only role-related failures: the stated twin must succeed, so the task itself is solvable for this model.
            same = [j for j in same if items[j]["joint"]]
            if not same:
                continue
            enc = encode(tok, build_messages(card, variant, "single"), model.device)
            for layer in layers:
                hs_idx = layer + 1  # output of block `layer`
                real = states[same[0], hs_idx]
                own = states[i, hs_idx]
                noise = rng.standard_normal(own.shape)
                noise = own + noise / np.linalg.norm(noise) * np.linalg.norm(real - own)
                runs = {"same_role": real, "random_dir": noise}
                if other:
                    runs["other_role"] = states[other[0], hs_idx]
                for kind, vec in runs.items():
                    p = Patch(model, layer, torch.tensor(vec))
                    try:
                        ans = generate(model, tok, enc, a.max_new)
                    finally:
                        p.remove()
                    s = score_v1(ans, card, variant)
                    f.write(json.dumps({"target": i, "card": r["card"], "variant": r["variant"], "layer": layer,
                                        "patch": kind, "repaired": bool(s["joint"]), "output": ans}, ensure_ascii=False) + "\n")
                    f.flush()
                    print(r["card"], r["variant"], layer, kind, "REPAIRED" if s["joint"] else "-", flush=True)


def cmd_report(a):
    d = out_dir(a.model)
    res = {}
    if os.path.exists(os.path.join(d, "probe.json")):
        res["probe"] = json.load(open(os.path.join(d, "probe.json")))
    if os.path.exists(os.path.join(d, "patch.jsonl")):
        rows = [json.loads(line) for line in open(os.path.join(d, "patch.jsonl"), encoding="utf-8")]
        rate = {}
        for r in rows:
            k = f"layer{r['layer']}/{r['patch']}"
            rate.setdefault(k, []).append(r["repaired"])
        res["patch_repair_rate"] = {k: {"n": len(v), "rate": round(sum(v) / len(v), 3)} for k, v in sorted(rate.items())}
    items, _ = _load_collected(a.model)
    imp = [r for r in items if r["cue"] == "implied"]
    res["behaviour"] = {"n_items": len(items), "implied_failure": round(sum(not r["joint"] for r in imp) / max(1, len(imp)), 3)}
    pr = res.get("probe", {})
    best_patch = max((v["rate"] - max(res["patch_repair_rate"].get(k.replace("same_role", c), {"rate": 0})["rate"]
                                       for c in ("other_role", "random_dir"))
                      for k, v in res.get("patch_repair_rate", {}).items() if k.endswith("same_role")), default=None)
    best_rate = max((v["rate"] for k, v in res.get("patch_repair_rate", {}).items() if k.endswith("same_role")), default=None)
    res["gate"] = {
        "probe_pass": bool(pr and pr["best_acc"] >= 0.70 and pr["bow_acc_implied"] is not None
                           and pr["best_acc"] - pr["bow_acc_implied"] >= 0.15),
        "patch_pass": bool(best_rate is not None and best_rate >= 0.25 and best_patch is not None and best_patch >= 0.15),
        "rule": "docs/goal-and-kill-tests.md section 3",
    }
    json.dump(res, open(os.path.join(d, "report.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["collect", "probe", "patch", "report"])
    ap.add_argument("--model", default="qwen2.5-3b", choices=list(MODELS))
    ap.add_argument("--cards", default="")
    ap.add_argument("--layers", default="16,20,24,26,28")
    ap.add_argument("--max-new", type=int, default=1024)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    {"collect": cmd_collect, "probe": cmd_probe, "patch": cmd_patch, "report": cmd_report}[a.step](a)


if __name__ == "__main__":
    main()
