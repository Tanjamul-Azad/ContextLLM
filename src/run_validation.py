"""Kill test 1: run v1 seed cards under four conditions and score them.

Conditions per variant: no_example, plain, scope_inference, oracle.
Only cards whose human review is complete count as validated. Use --dev to run on
draft cards; those outputs go to results/validation_dev/ and are never evidence.

Usage:
  python -I src/run_validation.py qwen2.5-3b --dev [--cards D01,C02] [--limit N]
  python -I src/run_validation.py gpt-5.4-mini --dev
  python -I src/run_validation.py MODEL --summarize-only --dev
Pass/fail rules: docs/goal-and-kill-tests.md section 2.
"""
import argparse
import glob
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checks_v1 import score_v1  # noqa: E402
from seed_lint_v1 import build_messages  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL = {"qwen2.5-3b", "qwen2.5-7b-4bit", "llama3.1-8b-4bit"}
API = {"gpt-4.1-mini", "gpt-5.4-mini", "gpt-5.4"}

SCOPE_INFERENCE = ("Before you answer, work out from my message which parts of the example I want you to use, "
                   "which parts I want you to leave out, and which of my own rules must still hold. "
                   "Then give only the final answer in the format I asked for.")


def validated(card):
    """A card counts only when both annotators rated realism >= 4, agreed on scope,
    and every ambiguous implied check has an adjudication."""
    hr = card.get("human_review") or {}
    real = hr.get("realism") or {}
    agree = hr.get("scope_agreement") or {}
    ok_real = all(isinstance(real.get(k), (int, float)) and real.get(k) >= 4 for k in ("annotator_1", "annotator_2"))
    ok_agree = all(agree.get(k) is True for k in ("annotator_1", "annotator_2"))
    ambiguous = {(v["id"], c["id"]) for v in card["variants"]
                 for c in v["must_transfer"] + v["must_not_transfer"]
                 if (c.get("basis") or {}).get("ambiguity") == "ambiguous"}
    adjudicated = {(a.get("variant"), a.get("check")) for a in hr.get("adjudications", [])}
    return ok_real and ok_agree and ambiguous <= adjudicated


def load_cards(dev, only=None):
    cards = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "seeds_v1_draft", "*.json"))):
        card = json.load(open(path, encoding="utf-8"))
        if only and not any(card["id"].startswith(o) for o in only):
            continue
        if dev or validated(card):
            cards.append(card)
    return cards


def oracle_text(variant):
    use = "; ".join(c["what"] for c in variant["must_transfer"])
    avoid = "; ".join(c["what"] for c in variant["must_not_transfer"])
    return f"What to take from the example: {use}. What not to take: {avoid}."


def conditions(card):
    """Yield (item_id, condition, variant_or_None, messages)."""
    yield f"{card['id']}|none", "no_example", None, build_messages(card, None)
    for v in card["variants"]:
        base = build_messages(card, v, "single")
        yield f"{card['id']}|{v['id']}|plain", "plain", v, base
        msgs = [dict(m) for m in base]
        msgs[-1]["content"] += "\n\n" + SCOPE_INFERENCE
        yield f"{card['id']}|{v['id']}|scope_inference", "scope_inference", v, msgs
        msgs = [dict(m) for m in base]
        msgs[-1]["content"] += "\n\n" + oracle_text(v)
        yield f"{card['id']}|{v['id']}|oracle", "oracle", v, msgs


NO_EXAMPLE_VARIANT = {"id": "none", "role": "none", "cue": "-", "fit": "-", "must_transfer": [], "must_not_transfer": []}


def score_item(output, card, variant):
    s = score_v1(output, card, variant or NO_EXAMPLE_VARIANT)
    s.pop("detail", None)
    return s


def bootstrap_ci(rows, n=2000, seed=0):
    """95% interval of the failure rate, resampling seeds (cards)."""
    by_seed = {}
    for r in rows:
        by_seed.setdefault(r["card"], []).append(0 if r["joint"] else 1)
    keys = list(by_seed)
    if not keys:
        return None
    rng = random.Random(seed)
    stats = []
    for _ in range(n):
        vals = [x for k in (rng.choice(keys) for _ in keys) for x in by_seed[k]]
        stats.append(sum(vals) / len(vals))
    stats.sort()
    return round(stats[int(0.025 * n)], 3), round(stats[int(0.975 * n)], 3)


def summarize(out_dir, model):
    rows = [json.loads(line) for line in open(os.path.join(out_dir, "scored.jsonl"), encoding="utf-8")]
    summ = {"model": model, "n": len(rows), "cards": sorted({r["card"] for r in rows}), "conditions": {}}
    for cond in ("no_example", "plain", "scope_inference", "oracle"):
        for cue in ("all", "implied", "stated"):
            sub = [r for r in rows if r["condition"] == cond and (cue == "all" or r["cue"] == cue)]
            if not sub or (cond == "no_example" and cue != "all"):
                continue
            fail = sum(0 if r["joint"] else 1 for r in sub) / len(sub)
            summ["conditions"][f"{cond}/{cue}"] = {"n": len(sub), "failure": round(fail, 3), "ci95": bootstrap_ci(sub)}
    c = summ["conditions"]
    plain = c.get("plain/implied", {}).get("failure")
    scope = c.get("scope_inference/implied", {}).get("failure")
    noex = c.get("no_example/all", {}).get("failure")
    summ["gate_inputs"] = {"plain_implied_failure": plain, "plain_implied_ci95": c.get("plain/implied", {}).get("ci95"),
                           "share_left_by_scope_prompt": round(scope / plain, 3) if plain else None,
                           "no_example_success": round(1 - noex, 3) if noex is not None else None}
    json.dump(summ, open(os.path.join(out_dir, "summary.json"), "w"), indent=1)
    print(json.dumps(summ, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(LOCAL | API))
    ap.add_argument("--dev", action="store_true", help="allow draft cards; outputs are DEV only")
    ap.add_argument("--cards", default="", help="comma-separated id prefixes")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--summarize-only", action="store_true")
    a = ap.parse_args()

    out_dir = os.path.join(ROOT, "results", "validation_dev" if a.dev else "validation", a.model)
    os.makedirs(out_dir, exist_ok=True)
    if a.summarize_only:
        return summarize(out_dir, a.model)

    cards = load_cards(a.dev, [c for c in a.cards.split(",") if c])
    if not cards:
        sys.exit("No validated cards yet. Finish the E2 review, or use --dev for a pipeline check.")
    items = [(card, *rest) for card in cards for rest in conditions(card)]
    gen_path = os.path.join(out_dir, "generations.jsonl")
    done = set()
    if os.path.exists(gen_path):
        done = {json.loads(line)["item"] for line in open(gen_path, encoding="utf-8")}
    todo = [x for x in items if x[1] not in done]
    if a.limit:
        todo = todo[: a.limit]
    print(f"{len(cards)} cards, {len(items)} items, {len(done)} done, {len(todo)} to run", flush=True)

    if a.model in LOCAL:
        from run_behaviour import generate, load
        tok, model = load(a.model)
        run = lambda msgs: generate(tok, model, [msgs], max_new_tokens=1024)[0]  # noqa: E731
    else:
        from run_api import api_key, call
        key = api_key()
        run = lambda msgs: call(a.model, msgs, key)[0]  # noqa: E731

    with open(gen_path, "a", encoding="utf-8") as f:
        for n, (card, item, cond, variant, msgs) in enumerate(todo, 1):
            out = run(msgs)
            f.write(json.dumps({"item": item, "card": card["id"], "condition": cond,
                                "variant": variant["id"] if variant else "none",
                                "role": variant["role"] if variant else "none",
                                "cue": variant["cue"] if variant else "-", "fit": variant["fit"] if variant else "-",
                                "dev": a.dev, "messages": msgs, "output": out}, ensure_ascii=False) + "\n")
            f.flush()
            if n % 10 == 0 or n == len(todo):
                print(f"{n}/{len(todo)}", flush=True)

    by_card = {c["id"]: c for c in load_cards(True)}
    with open(os.path.join(out_dir, "scored.jsonl"), "w", encoding="utf-8") as f:
        for line in open(gen_path, encoding="utf-8"):
            g = json.loads(line)
            card = by_card[g["card"]]
            variant = next((v for v in card["variants"] if v["id"] == g["variant"]), None)
            s = score_item(g["output"], card, variant)
            f.write(json.dumps({k: g[k] for k in ("item", "card", "condition", "variant", "role", "cue", "fit", "dev")} | s) + "\n")
    summarize(out_dir, a.model)


if __name__ == "__main__":
    main()
