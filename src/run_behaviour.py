"""E4-E6: generate answers for every condition and score them.

Usage: python -I src/run_behaviour.py MODEL_KEY [--limit N]
Writes results/behaviour/<model>/generations.jsonl and scored.jsonl.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _compat  # noqa: E402,F401
import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from checks import score  # noqa: E402
from prompts import all_conditions  # noqa: E402

MODELS = {
    "qwen2.5-3b": "Qwen/Qwen2.5-3B-Instruct",
    "qwen2.5-7b-4bit": "unsloth/Qwen2.5-7B-Instruct-bnb-4bit",
    "llama3.1-8b-4bit": "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit",
}
QUANTIZE_ON_LOAD = set()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(key):
    name = MODELS[key]
    tok = AutoTokenizer.from_pretrained(name)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    kw = {"device_map": "cuda"}
    if key in QUANTIZE_ON_LOAD:
        from transformers import BitsAndBytesConfig
        kw["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                                       bnb_4bit_compute_dtype=torch.bfloat16)
    elif "bnb-4bit" not in name:
        kw["dtype"] = torch.bfloat16
    model = AutoModelForCausalLM.from_pretrained(name, **kw)
    model.eval()
    return tok, model


@torch.no_grad()
def generate(tok, model, batch, max_new_tokens=512):
    texts = [tok.apply_chat_template(m, tokenize=False, add_generation_prompt=True) for m in batch]
    enc = tok(texts, return_tensors="pt", padding=True).to(model.device)
    out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False, temperature=None, top_p=None, top_k=None,
                         pad_token_id=tok.pad_token_id or tok.eos_token_id)
    return [tok.decode(o[enc["input_ids"].shape[1]:], skip_special_tokens=True) for o in out]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--batch", type=int, default=8)
    a = ap.parse_args()

    out_dir = os.path.join(ROOT, "results", "behaviour", a.model)
    os.makedirs(out_dir, exist_ok=True)
    gen_path = os.path.join(out_dir, "generations.jsonl")
    done = set()
    if os.path.exists(gen_path):
        with open(gen_path, encoding="utf-8") as f:
            done = {json.loads(line)["item"] for line in f}

    items = [c for c in all_conditions() if c[0] not in done]
    if a.limit:
        items = items[: a.limit]
    print(f"{len(done)} done, {len(items)} to run", flush=True)

    tok, model = load(a.model)
    t0 = time.time()
    with open(gen_path, "a", encoding="utf-8") as f:
        for i in range(0, len(items), a.batch):
            chunk = items[i: i + a.batch]
            outs = generate(tok, model, [c[5] for c in chunk])
            for (item, seed, role, w, t, msgs), o in zip(chunk, outs):
                f.write(json.dumps({"item": item, "model": a.model, "seed": seed["id"], "family": seed["family"],
                                    "role": role or "none", "wording": w, "turns": t, "messages": msgs,
                                    "output": o}, ensure_ascii=False) + "\n")
            f.flush()
            print(f"{min(i + a.batch, len(items))}/{len(items)}  {time.time() - t0:.0f}s", flush=True)

    rescore(a.model)


def rescore(model_key):
    from seeds import SEEDS
    by_id = {s["id"]: s for s in SEEDS}
    out_dir = os.path.join(ROOT, "results", "behaviour", model_key)
    rows = []
    with open(os.path.join(out_dir, "generations.jsonl"), encoding="utf-8") as f:
        for line in f:
            g = json.loads(line)
            role = None if g["role"] == "none" else g["role"]
            s = score(g["output"], by_id[g["seed"]], role)
            rows.append({k: g[k] for k in ("item", "model", "seed", "family", "role", "wording", "turns")} | s)
    with open(os.path.join(out_dir, "scored.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"scored {len(rows)} answers -> {out_dir}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--rescore":
        rescore(sys.argv[2])
    else:
        main()
