"""E4-E6 on OpenAI API models. Same prompts and scoring as run_behaviour.py.

The key is read from local_only/.env (git-ignored) and never printed.
Usage: python -I src/run_api.py MODEL [--limit N]
Writes results/behaviour/<model>/generations.jsonl, usage.jsonl and scored.jsonl.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prompts import all_conditions  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Pinned snapshots, so reruns hit the same model.
PINNED = {"gpt-4.1-mini": "gpt-4.1-mini-2025-04-14", "gpt-5.4-mini": "gpt-5.4-mini-2026-03-17", "gpt-5.4": "gpt-5.4-2026-03-05"}
REASONING = {"gpt-5.4-mini", "gpt-5.4"}


def api_key():
    with open(os.path.join(ROOT, "local_only", ".env"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("OPENAI_API_KEY missing in local_only/.env")


def call(model, messages, key):
    body = {"model": PINNED[model], "messages": messages}
    if model in REASONING:
        body.update({"reasoning_effort": "low", "max_completion_tokens": 4000})
    else:
        body.update({"temperature": 0, "max_tokens": 1024})
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503):
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {e.code}: {e.read()[:300]}")
        except Exception:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("API failed after retries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=list(PINNED))
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    key = api_key()
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
    tin = tout = treason = 0
    with open(gen_path, "a", encoding="utf-8") as gf, open(os.path.join(out_dir, "usage.jsonl"), "a", encoding="utf-8") as uf:
        for n, (item, seed, role, w, t, msgs) in enumerate(items, 1):
            out, use = call(a.model, msgs, key)
            gf.write(json.dumps({"item": item, "model": a.model, "snapshot": PINNED[a.model], "seed": seed["id"],
                                 "family": seed["family"], "role": role or "none", "wording": w, "turns": t,
                                 "messages": msgs, "output": out}, ensure_ascii=False) + "\n")
            uf.write(json.dumps({"item": item, **use}) + "\n")
            gf.flush()
            tin += use.get("prompt_tokens", 0)
            tout += use.get("completion_tokens", 0)
            treason += (use.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
            if n % 10 == 0 or n == len(items):
                print(f"{n}/{len(items)}  input {tin}  output {tout} (reasoning {treason})", flush=True)
    from run_behaviour import rescore
    rescore(a.model)


if __name__ == "__main__":
    main()
