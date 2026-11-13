"""WP0.4 backbone competence screen: one model, no-example gate items plus oracle items.

Items per model
  (a) v1 draft cards (data/seeds_v1_draft/): condition no_example (10 items) and condition oracle (68 variants);
  (b) pilot seeds (src/seeds.py): condition no_example, role none (10 items).
The gate is the 20 no_example items. Oracle items are supplementary.

Outputs (results/backbone_screen/<model>/): generations.jsonl, scored.jsonl, meta.json.
Resumable: items already in generations.jsonl are skipped. Greedy decoding, max_new_tokens=1024.
Code answers are executed by the existing checker (checks.run_py_test). It is NOT sandboxed (it only
blocks a regex list of dangerous calls and uses a temp dir and a 30 s timeout).

Usage:
  python -I scripts/backbone_screen.py MODEL_KEY [--limit N] [--rescore]
Development-stage, exploratory results on unreviewed draft items.
"""
import argparse
import datetime
import hashlib
import glob
import json
import os
import platform
import sys
import time
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

FAMILY_MAP = {"planning": "decision", "decision": "decision", "code": "code"}
MAX_NEW_TOKENS = 1024


def build_items():
    """Return list of dicts: item, source, family, task, condition, variant, role, cue, fit, messages."""
    from checks_v1 import score_v1  # noqa: F401  (import check only)
    from prompts import build
    from run_validation import conditions, load_cards
    from seeds import SEEDS

    items = []
    for card in load_cards(dev=True):
        for item, cond, variant, msgs in conditions(card):
            if cond not in ("no_example", "oracle"):
                continue
            items.append({"item": f"v1|{item}", "source": "v1_cards", "family": FAMILY_MAP[card["family"]],
                          "task": card["id"], "condition": cond,
                          "variant": variant["id"] if variant else "none",
                          "role": variant["role"] if variant else "none",
                          "cue": variant["cue"] if variant else "-", "fit": variant["fit"] if variant else "-",
                          "messages": msgs})
    for s in SEEDS:
        items.append({"item": f"pilot|{s['id']}|none", "source": "pilot_seeds", "family": FAMILY_MAP[s["family"]],
                      "task": s["id"], "condition": "no_example", "variant": "none", "role": "none", "cue": "-",
                      "fit": "-", "messages": build(s, None, "-", "single")})
    return items


def score_item(g):
    """Score one stored generation; returns dict with score fields plus the list of failed checks."""
    from checks import score
    from run_validation import NO_EXAMPLE_VARIANT, load_cards
    from checks_v1 import score_v1
    from seeds import SEEDS

    if g["source"] == "pilot_seeds":
        seed = next(s for s in SEEDS if s["id"] == g["task"])
        r = score(g["output"], seed, None)
        failed = [{"kind": "constraint", "check": f"{seed['constraints'][i][0]}#{i}", "note": c[1]}
                  for i, c in enumerate(r["detail"]["constraints"]) if c[0] != "True"]
    else:
        card = next(c for c in load_cards(dev=True) if c["id"] == g["task"])
        variant = next((v for v in card["variants"] if v["id"] == g["variant"]), None) or NO_EXAMPLE_VARIANT
        r = score_v1(g["output"], card, variant)
        failed = []
        for kind, key in (("constraint", "constraints"), ("transfer", "transfer"), ("leakage", "leakage")):
            for cid, passed, note in r["detail"][key]:
                if not passed:
                    failed.append({"kind": kind, "check": cid, "note": str(note)[:120]})
    out = {k: g[k] for k in ("item", "source", "family", "task", "condition", "variant", "role", "cue", "fit")}
    out.update({"format_ok": r["format_ok"], "constraint_ok": r["constraint_ok"], "transfer_ok": r.get("transfer_ok"),
                "leak": r.get("leak"), "joint": r["joint"], "failed_checks": failed,
                # odd number of code fences = answer cut off by the 1024-token limit (proxy; token count is not stored)
                "truncated_likely": g["output"].count("```") % 2 == 1,
                "messages": g["messages"], "output": g["output"]})
    return out


def cards_hash():
    h = hashlib.sha256()
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "seeds_v1_draft", "*.json"))):
        h.update(open(p, "rb").read())
    h.update(open(os.path.join(ROOT, "src", "seeds.py"), "rb").read())
    return h.hexdigest()[:16]


def resolved_revision(repo):
    from huggingface_hub import try_to_load_from_cache
    p = try_to_load_from_cache(repo, "config.json")
    if isinstance(p, str):
        parts = p.replace("\\", "/").split("/")
        if "snapshots" in parts:
            return parts[parts.index("snapshots") + 1]
    return None


def read_meta(path):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", type=int, default=8,
                    help="generation batch size (greedy, left padding; recorded in meta.json)")
    ap.add_argument("--rescore", action="store_true", help="only rescore stored generations")
    a = ap.parse_args()

    from run_behaviour import MODELS, TEMPLATE_KW
    if a.model not in MODELS:
        sys.exit(f"unknown model key {a.model}; choose from {sorted(MODELS)}")
    out_dir = os.path.join(ROOT, "results", "backbone_screen", a.model)
    os.makedirs(out_dir, exist_ok=True)
    gen_path = os.path.join(out_dir, "generations.jsonl")
    meta_path = os.path.join(out_dir, "meta.json")
    meta = read_meta(meta_path)

    items = build_items()
    if not a.rescore:
        done = set()
        if os.path.exists(gen_path):
            done = {json.loads(line)["item"] for line in open(gen_path, encoding="utf-8")}
        todo = [x for x in items if x["item"] not in done]
        if a.limit:
            todo = todo[: a.limit]
        print(f"{a.model}: {len(items)} items, {len(done)} done, {len(todo)} to run", flush=True)
        if todo:
            import torch
            from run_behaviour import generate, load
            t0 = time.time()
            repo = MODELS[a.model]
            meta.update({"model_key": a.model, "hf_repo": repo, "date": datetime.date.today().isoformat(),
                         "decoding": {"do_sample": False, "max_new_tokens": MAX_NEW_TOKENS, "batch_size": a.batch,
                                      "chat_template_kwargs": TEMPLATE_KW.get(a.model, {})},
                         "library_versions": {"python": platform.python_version(), "torch": torch.__version__,
                                              "transformers": __import__("transformers").__version__,
                                              "bitsandbytes": __import__("bitsandbytes").__version__},
                         "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                         "items_hash": cards_hash(), "n_items": len(items)})
            try:
                tok, model = load(a.model)
            except BaseException as e:  # noqa: BLE001  record any load failure
                meta["load_error"] = f"{type(e).__name__}: {e}"[:2000]
                meta["load_traceback"] = traceback.format_exc()[-3000:]
                json.dump(meta, open(meta_path, "w", encoding="utf-8"), indent=1)
                print("LOAD FAILED:", meta["load_error"], flush=True)
                sys.exit(2)
            meta.pop("load_error", None)
            meta.pop("load_traceback", None)
            qc = getattr(model.config, "quantization_config", None)
            if qc is not None and not isinstance(qc, dict):
                qc = qc.to_dict()
            meta["revision"] = resolved_revision(repo)
            meta["quantisation"] = ({"method": qc.get("quant_method"), "bits": 4 if qc.get("load_in_4bit") else None,
                                     "type": qc.get("bnb_4bit_quant_type"),
                                     "compute_dtype": qc.get("bnb_4bit_compute_dtype"),
                                     "double_quant": qc.get("bnb_4bit_use_double_quant"),
                                     "prequantised": True} if qc else "none")
            meta["dtype"] = str(next(model.parameters()).dtype)
            meta["n_parameters_loaded"] = sum(p.numel() for p in model.parameters())
            meta["vram_after_load_gb"] = round(torch.cuda.memory_allocated() / 1e9, 2)
            with open(gen_path, "a", encoding="utf-8") as f:
                for i in range(0, len(todo), a.batch):
                    chunk = todo[i: i + a.batch]
                    outs = generate(tok, model, [c["messages"] for c in chunk], max_new_tokens=MAX_NEW_TOKENS,
                                    template_kw=TEMPLATE_KW.get(a.model))
                    for it, out in zip(chunk, outs):
                        f.write(json.dumps(dict(it, output=out), ensure_ascii=False) + "\n")
                    f.flush()
                    print(f"{min(i + a.batch, len(todo))}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)
            meta["wall_time_s"] = round(meta.get("wall_time_s", 0) + time.time() - t0, 1)
            meta["peak_vram_gb"] = round(torch.cuda.max_memory_allocated() / 1e9, 2)
            json.dump(meta, open(meta_path, "w", encoding="utf-8"), indent=1)

    gens = [json.loads(line) for line in open(gen_path, encoding="utf-8")] if os.path.exists(gen_path) else []
    with open(os.path.join(out_dir, "scored.jsonl"), "w", encoding="utf-8") as f:
        for g in gens:
            f.write(json.dumps(score_item(g), ensure_ascii=False) + "\n")
    print(f"scored {len(gens)} generations -> {out_dir}", flush=True)


if __name__ == "__main__":
    main()
