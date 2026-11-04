"""E1: do real conversations contain example-giving turns, and in which role?

1. Sample random pages of WildChat-1M through the Hugging Face dataset viewer.
2. Keep English, drop repeated turns and long pasted text.
3. Keyword prefilter, then a local model labels each candidate turn.

Raw user text never enters the repository: it is written to local_only/ (git-ignored)
for hand-checking. The repository keeps only hashes, lengths and labels.

Usage: python -I src/wildchat_mine.py [PAGES] [MODEL_KEY]
"""
import csv
import json
import os
import random
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_behaviour import ROOT, generate, load  # noqa: E402

BASE = "https://datasets-server.huggingface.co"
DS = "allenai/WildChat-1M"
N_ROWS = 837989
MAX_LEN = 1500

PREFILTER = re.compile(
    r"\b(for example|for instance|e\.g\.|like this|like that|similar to|in the same way|the same (format|style|way|structure)|"
    r"just like|inspired by|analog(y|ous)|follow (this|the|that) (format|template|example|style)|here is an example|"
    r"(don'?t|do not) (do it|write it|make it) like|not like (this|that|the previous|before)|unlike (this|that|the)|"
    r"exactly like|same as (this|that|the)|as an example)\b", re.I)

LABEL_PROMPT = """You label one message a user sent to a chatbot.

Question 1: Does the user give a concrete example (text, code, a case, a story, a format) that should shape the answer? Quoting a document only to be summarised or translated does not count.
Question 2: If yes, what is the example's role?
- requirement: the answer must follow or copy something in the example (format, names, style, exact values)
- analogy: the answer should borrow the idea or structure of the example, not its details
- counter-example: the answer must avoid what the example does
Question 3: Does the example come from a different domain than the user's task (for example a hospital case for an IT problem)?

Message:
<<<
{msg}
>>>

Reply with JSON only: {{"gives_example": true or false, "role": "requirement" or "analogy" or "counter-example" or "none", "different_domain": true or false}}"""


def wildchat_turns(r):
    if r.get("language") != "English":
        return []
    return [(r["conversation_hash"], i, t.get("content")) for i, t in enumerate(r["conversation"]) if t.get("role") == "user"]


def oasst_turns(r):
    if r.get("role") != "prompter" or r.get("lang") != "en" or r.get("deleted"):
        return []
    return [(r["message_id"], 0, r.get("text"))]


SOURCES = {
    "wildchat": {"name": "allenai/WildChat-1M", "n_rows": 837989, "turns": wildchat_turns},
    "oasst": {"name": "OpenAssistant/oasst2", "n_rows": 128575, "turns": oasst_turns},
}


def get(url):
    for _ in range(5):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.load(r)
        except Exception:
            time.sleep(15)
    return None


def main():
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    key = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5-3b"
    source = sys.argv[3] if len(sys.argv) > 3 else "wildchat"
    out_dir = os.path.join(ROOT, "results", f"E1_{source}")
    local = os.path.join(ROOT, "local_only")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(local, exist_ok=True)

    random.seed(2026)
    src = SOURCES[source]
    offsets = sorted(random.sample(range(0, src["n_rows"] - 100), pages))
    seen, stats = set(), {"source": src["name"], "pages_requested": pages, "pages_fetched": 0, "rows": 0,
                          "english_user_turns": 0, "unique_english_user_turns": 0, "short_turns": 0, "prefilter_hits": 0}
    cands = []
    for off in offsets:
        d = get(f"{BASE}/rows?dataset={src['name']}&config=default&split=train&offset={off}&length=100")
        time.sleep(2.5)
        if d is None:
            continue
        stats["pages_fetched"] += 1
        for row in d["rows"]:
            stats["rows"] += 1
            for h, ti, x in src["turns"](row["row"]):
                stats["english_user_turns"] += 1
                x = (x or "").strip()
                k = x[:200]
                if not x or k in seen:
                    continue
                seen.add(k)
                stats["unique_english_user_turns"] += 1
                if len(x) > MAX_LEN:
                    continue
                stats["short_turns"] += 1
                if PREFILTER.search(x):
                    stats["prefilter_hits"] += 1
                    cands.append({"hash": h, "turn": ti, "chars": len(x), "text": x})
        print(f"page {stats['pages_fetched']}/{pages}  candidates {len(cands)}", flush=True)

    tok, model = load(key)
    labels = []
    for i in range(0, len(cands), 8):
        batch = cands[i:i + 8]
        outs = generate(tok, model, [[{"role": "user", "content": LABEL_PROMPT.format(msg=c["text"])}] for c in batch], max_new_tokens=60)
        for c, o in zip(batch, outs):
            m = re.search(r"\{.*\}", o, re.S)
            try:
                lab = json.loads(m.group(0)) if m else {}
            except json.JSONDecodeError:
                lab = {}
            labels.append({"hash": c["hash"], "turn": c["turn"], "chars": c["chars"],
                           "gives_example": bool(lab.get("gives_example", False)),
                           "role": lab.get("role", "parse_error") if lab else "parse_error",
                           "different_domain": bool(lab.get("different_domain", False))})

    pos = [x for x in labels if x["gives_example"] and x["role"] in ("requirement", "analogy", "counter-example")]
    by_role = {r: sum(1 for x in pos if x["role"] == r) for r in ("requirement", "analogy", "counter-example")}
    unique_per_row = stats["unique_english_user_turns"] / max(1, stats["rows"])
    rate = len(pos) / max(1, stats["unique_english_user_turns"])
    summary = {
        "sample": stats,
        "model_labelled_examples": len(pos),
        "by_role": by_role,
        "cross_domain": sum(1 for x in pos if x["different_domain"]),
        "rate_per_unique_english_turn": round(rate, 4),
        "estimate_full_dataset": int(rate * unique_per_row * src["n_rows"]),
        "note": "Labels come from a 3B model and are not yet hand-checked. The keyword prefilter misses many cases, so counts are a lower bound.",
    }
    with open(os.path.join(out_dir, "labels.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(labels[0].keys()) if labels else ["hash"])
        w.writeheader()
        w.writerows(labels)
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    # Hand-check sheet with raw text stays out of the repository.
    with open(os.path.join(local, f"E1_{source}_handcheck.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["hash", "turn", "model_role", "model_gives_example", "your_role", "text"])
        for c, lab in zip(cands, labels):
            w.writerow([c["hash"], c["turn"], lab["role"], lab["gives_example"], "", c["text"]])
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
