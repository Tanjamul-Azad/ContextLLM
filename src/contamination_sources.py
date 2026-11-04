"""Contamination checks on the other public sources the benchmark plans to reuse.

Same two checks as src/contamination.py (GSM8K):
1. Guided completion (Golchin and Surdeanu, ICLR 2024): first half of an item with the dataset
   name (guided) and without it (general); ROUGE-L of the completion against the real second half.
2. Min-K% Prob, k=20% (Shi et al., ICLR 2024): original text versus a model-written paraphrase.

Flag rule (docs/paper-protocol.md, section 3): flag the source if more than 5% of items are
recalled near word for word (guided ROUGE-L >= 0.75), or if originals score higher than their
paraphrases in more than 70% of pairs.

Rows are fetched at run time from the Hugging Face dataset-viewer API. Only item ids, offsets
and scores are written; no dataset text is stored.

Usage: python -I src/contamination_sources.py [MODEL_KEY] [N] [SOURCE ...]
Writes results/contamination/<model>/sources/<source>/summary.json and items.csv.
"""
import csv
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contamination import min_k, rouge_l  # noqa: E402  (imports _compat before transformers)
from run_behaviour import MODELS, ROOT, generate, load  # noqa: E402
from seeds import SEEDS  # noqa: E402

API = "https://datasets-server.huggingface.co"
SEED = 7


def get_json(path, params, tries=6):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    err = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = json.load(r)
            time.sleep(2.5)
            return data
        except Exception as e:  # network errors, 5xx, rate limits
            err = e
            time.sleep(3 + 5 * i)
    raise RuntimeError(f"fetch failed: {url}: {err}")


def rows(dataset, config, split, offset, length):
    d = get_json("rows", {"dataset": dataset, "config": config, "split": split, "offset": offset, "length": length})
    return d["num_rows_total"], [(x["row_idx"], x["row"]) for x in d["rows"]]


def n_words(t):
    return len(t.split())


# ---- source loaders: each returns (description, [(item_id, text)]) ----

def load_natinst(n):
    ds, cfg, sp = "jayelm/natural-instructions", "default", "test"
    total, _ = rows(ds, cfg, sp, 0, 1)
    rng = random.Random(SEED)
    seen, items = set(), []
    # the test split is ordered by task; sample offsets until n distinct task definitions are collected
    for _ in range(4 * n):
        if len(items) >= n:
            break
        off = rng.randrange(total - 20)
        _, rs = rows(ds, cfg, sp, off, 20)
        for idx, r in rs:
            t = r["task_name"]
            if t in seen:
                continue
            seen.add(t)
            d = r["definition"].strip()
            if n_words(d) >= 16:
                items.append((f"{t}|row{idx}", d))
            break
    return f"{ds} ({cfg}/{sp}), task definitions, {len(items)} distinct tasks", "Super-NaturalInstructions", items


def load_humaneval(n):
    ds, cfg, sp = "openai/openai_humaneval", "openai_humaneval", "test"
    total, rs = rows(ds, cfg, sp, 0, 100)
    _, rs2 = rows(ds, cfg, sp, 100, 100)
    rs += rs2
    rng = random.Random(SEED)
    pick = sorted(rng.sample(range(len(rs)), min(n, len(rs))))
    items = [(rs[i][1]["task_id"], rs[i][1]["prompt"].strip()) for i in pick]
    return f"{ds} ({sp}), function prompts (signature + docstring), {len(items)} of {total}", "HumanEval", items


def load_spider(n):
    ds, cfg, sp = "xlangai/spider", "spider", "validation"
    total, _ = rows(ds, cfg, sp, 0, 1)
    allr = []
    for off in range(0, total, 100):
        allr += rows(ds, cfg, sp, off, 100)[1]
    # questions are short; keep the longer ones so each half carries some content
    pool = [(i, r) for i, r in allr if n_words(r["question"]) >= 12]
    seen, uniq = set(), []
    for i, r in pool:
        if r["question"] not in seen:
            seen.add(r["question"])
            uniq.append((i, r))
    rng = random.Random(SEED)
    pick = sorted(rng.sample(range(len(uniq)), min(n, len(uniq))), key=lambda j: uniq[j][0])
    items = [(f"{uniq[j][1]['db_id']}|row{uniq[j][0]}", uniq[j][1]["question"].strip()) for j in pick]
    return (f"{ds} ({sp}), questions with >= 12 words ({len(uniq)} eligible of {total}), {len(items)} sampled",
            "Spider", items)


def load_analobench(n):
    ds, cfg, sp = "jhu-clsp/AnaloBench", "T1S10-Full", "train"
    total, _ = rows(ds, cfg, sp, 0, 1)
    rng = random.Random(SEED)
    seen, items = set(), []
    for _ in range(3 * n):
        if len(items) >= n:
            break
        off = rng.randrange(total - 10)
        _, rs = rows(ds, cfg, sp, off, 10)
        for idx, r in rs:
            # the gold (most analogous) story among options A-D
            opts = re.split(r"\n(?=[A-D]\. )", r["Options"].strip())
            gold = [o[3:].strip() for o in opts if o.startswith(r["Label"].strip() + ". ")]
            if not gold or gold[0] in seen or n_words(gold[0]) < 30:
                continue
            seen.add(gold[0])
            items.append((f"{cfg}|row{idx}|opt{r['Label'].strip()}", gold[0]))
            break
    return f"{ds} ({cfg}/{sp}), gold 10-sentence stories, {len(items)} distinct", "AnaloBench", items


def load_parallelparc(n):
    raise LookupError("ParallelPARC is not on the Hugging Face Hub (Hub search for 'ParallelPARC', "
                      "'parallelparc', 'parallel_parc', 'Parallel-PARC' returned no datasets on 2026-11-05)")


SOURCES = {
    "natural_instructions": (load_natinst, "task definition"),
    "humaneval": (load_humaneval, "Python function prompt"),
    "spider": (load_spider, "question"),
    "analobench": (load_analobench, "story"),
    "parallelparc": (load_parallelparc, "text"),
}


def split_half(text):
    """Cut at the middle whitespace token, keeping the original formatting of each half."""
    spans = [m.start() for m in re.finditer(r"\S+", text)]
    cut = spans[len(spans) // 2]
    return text[:cut].rstrip(), text[cut:].strip()


def para_prompt(kind, text):
    if kind == "Python function prompt":
        return ("Rewrite this Python function stub: rename the function and its arguments, reword the docstring, "
                "and change the example values, but keep the same task. Reply with the rewritten stub only.\n\n" + text)
    return (f"Rewrite this {kind} with different wording and different names or examples, keeping the same meaning. "
            f"Reply with the rewritten {kind} only.\n\n" + text)


def run_source(name, tok, model, n, base, fresh_mean):
    loader, kind = SOURCES[name]
    desc, ds_name, items = loader(n)
    if len(items) < 10:
        raise RuntimeError(f"only {len(items)} usable items")
    halves = [split_half(t) for _, t in items]
    guided = [[{"role": "user", "content": f"You are given the first part of a {kind} from the {ds_name} dataset. "
                f"Finish it exactly as it appears in the dataset. Reply with the rest of the {kind} only.\n\n"
                f"First part: {h}"}] for h, _ in halves]
    general = [[{"role": "user", "content": f"Finish this {kind}. Reply with the rest of the {kind} only.\n\n"
                 f"First part: {h}"}] for h, _ in halves]
    para = [[{"role": "user", "content": para_prompt(kind, t)}] for _, t in items]

    rest_tok = max(len(tok(r).input_ids) for _, r in halves)
    full_tok = max(len(tok(t).input_ids) for _, t in items)
    max_comp = min(512, int(1.3 * rest_tok) + 16)
    max_para = min(768, int(1.5 * full_tok) + 32)

    def gen_all(batches, max_new):
        out = []
        for i in range(0, len(batches), 8):
            out += generate(tok, model, batches[i:i + 8], max_new_tokens=max_new)
        return out

    g_out = gen_all(guided, max_comp)
    n_out = gen_all(general, max_comp)
    p_out = gen_all(para, max_para)

    recs = []
    for (iid, t), (_, rest), go, no, po in zip(items, halves, g_out, n_out, p_out):
        recs.append({
            "item_id": iid,
            "n_words": n_words(t),
            "rouge_guided": round(rouge_l(go, rest), 3),
            "rouge_general": round(rouge_l(no, rest), 3),
            "mink_original": round(min_k(tok, model, t), 3),
            "mink_paraphrase": round(min_k(tok, model, po.strip()), 3),
        })

    def mean(xs):
        return round(sum(xs) / len(xs), 3)

    m = len(recs)
    wins = sum(r["mink_original"] > r["mink_paraphrase"] for r in recs)
    s = {
        "model": MODELS[base],
        "source": name,
        "dataset": desc,
        "n": m,
        "item_sampling_seed": SEED,
        "max_new_tokens": {"completion": max_comp, "paraphrase": max_para},
        "guided_completion": {
            "mean_rouge_l_guided": mean([r["rouge_guided"] for r in recs]),
            "mean_rouge_l_general": mean([r["rouge_general"] for r in recs]),
            "share_near_verbatim_guided(>=0.75)": round(sum(r["rouge_guided"] >= 0.75 for r in recs) / m, 3),
            "share_near_verbatim_general(>=0.75)": round(sum(r["rouge_general"] >= 0.75 for r in recs) / m, 3),
        },
        "min_k_prob(k=20%)": {
            "mean_original": mean([r["mink_original"] for r in recs]),
            "mean_paraphrase": mean([r["mink_paraphrase"] for r in recs]),
            "share_original_scores_higher_than_its_paraphrase": round(wins / m, 3),
            "mean_our_fresh_seed_texts": fresh_mean,
        },
        "rule": "Flag if guided near-verbatim share (ROUGE-L >= 0.75) > 0.05, or original > paraphrase in > 70% of pairs.",
    }
    gc, mk = s["guided_completion"], s["min_k_prob(k=20%)"]
    s["flag_reasons"] = [r for r, c in [
        ("near-verbatim recall > 5%", gc["share_near_verbatim_guided(>=0.75)"] > 0.05),
        ("originals beat paraphrases in > 70% of pairs", mk["share_original_scores_higher_than_its_paraphrase"] > 0.7),
    ] if c]
    s["flag_source"] = bool(s["flag_reasons"])
    out = os.path.join(base_dir(base), name)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "items.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    with open(os.path.join(out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, indent=1)
    return s


def base_dir(key):
    return os.path.join(ROOT, "results", "contamination", key, "sources")


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5-3b"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    names = sys.argv[3:] or list(SOURCES)
    os.makedirs(base_dir(key), exist_ok=True)
    tok, model = load(key)
    fresh = [min_k(tok, model, f"{s['task']} {s['rules']}") for s in SEEDS]
    fresh_mean = round(sum(fresh) / len(fresh), 3)
    status = {}
    for name in names:
        t0 = time.time()
        try:
            s = run_source(name, tok, model, n, key, fresh_mean)
            status[name] = {"status": "ok", "n": s["n"], "flag_source": s["flag_source"],
                            "seconds": round(time.time() - t0)}
            print(name, json.dumps(s, indent=1), flush=True)
        except Exception as e:
            status[name] = {"status": "skipped", "reason": str(e), "seconds": round(time.time() - t0)}
            print(name, "SKIPPED:", e, flush=True)
    with open(os.path.join(base_dir(key), "run_status.json"), "w", encoding="utf-8") as f:
        json.dump(status, f, indent=1)
    print(json.dumps(status, indent=1))


if __name__ == "__main__":
    main()
