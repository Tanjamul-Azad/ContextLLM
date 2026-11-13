"""WP0.4 summary: build results/backbone_screen/summary.json and summary.md (and update model_registry.json).

Gate: no-example success (joint = format ok and every task constraint satisfied) over the 20 no-example items,
95% bootstrap interval over tasks (10,000 resamples, seed 0). Eligible if success >= 0.80.
Oracle: joint success over the 68 v1 variants (format ok, constraints, must-transfer, no leakage).
Usage: python -I scripts/backbone_screen_summary.py
"""
import glob
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREEN = os.path.join(ROOT, "results", "backbone_screen")
THRESHOLD = 0.80
N_BOOT = 10000
# Sensitivity only (never the gate): tasks with a suspected task or checker defect found while reading failures.
FLAGGED = {
    "C02_typed_tsv_parser": "checker: the test header does 'import datetime' after the model code, which rebinds the name "
                            "and breaks correct solutions that use 'from datetime import datetime'",
    "D03_group_lending_lab": "task: the format template shows the placeholder 'group, individual or lab' and weaker models echo it",
    "D05_release_train_portal": "task: the format template shows the placeholder 'ship_without_it or delay_release' and models echo it",
}
# Nominal parameter counts in billions (from the model cards; the stored 4-bit tensors do not give a true count).
NOMINAL_B = {"qwen3-4b-2507-4bit": 4.0, "phi4-mini-4bit": 3.8, "gemma3-4b-4bit": 4.3, "llama3.2-3b-4bit": 3.2,
             "qwen3-8b-4bit": 8.2, "qwen2.5-3b": 3.1, "qwen2.5-7b-4bit": 7.6, "llama3.1-8b-4bit": 8.0}
ORDER = ["qwen3-4b-2507-4bit", "phi4-mini-4bit", "gemma3-4b-4bit", "llama3.2-3b-4bit", "qwen3-8b-4bit",
         "qwen2.5-3b", "qwen2.5-7b-4bit", "llama3.1-8b-4bit"]


def boot(values, seed=0):
    """Mean and 95% percentile interval, resampling tasks (each task is one no-example item)."""
    if not values:
        return None
    rng = random.Random(seed)
    n = len(values)
    stats = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(N_BOOT))
    return {"p": round(sum(values) / n, 3), "lo": round(stats[int(0.025 * N_BOOT)], 3),
            "hi": round(stats[int(0.975 * N_BOOT) - 1], 3), "k": int(sum(values)), "n": n}


def boot_clustered(rows, seed=0):
    """Oracle success: resample task cards (clusters of variants), 10,000 resamples."""
    by = {}
    for r in rows:
        by.setdefault(r["task"], []).append(1 if r["joint"] else 0)
    keys = list(by)
    if not keys:
        return None
    rng = random.Random(seed)
    stats = []
    for _ in range(N_BOOT):
        vals = [x for k in (keys[rng.randrange(len(keys))] for _ in keys) for x in by[k]]
        stats.append(sum(vals) / len(vals))
    stats.sort()
    allv = [x for k in keys for x in by[k]]
    return {"p": round(sum(allv) / len(allv), 3), "lo": round(stats[int(0.025 * N_BOOT)], 3),
            "hi": round(stats[int(0.975 * N_BOOT) - 1], 3), "k": sum(allv), "n": len(allv)}


def load_model(key):
    d = os.path.join(SCREEN, key)
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8")) if os.path.exists(os.path.join(d, "meta.json")) else {}
    sp = os.path.join(d, "scored.jsonl")
    rows = [json.loads(line) for line in open(sp, encoding="utf-8")] if os.path.exists(sp) else []
    return meta, rows


def fmt(ci, pct=True):
    if not ci:
        return "n/a"
    return f"{ci['p'] * 100:.0f}% [{ci['lo'] * 100:.0f}, {ci['hi'] * 100:.0f}] ({ci['k']}/{ci['n']})"


def main():
    keys = [k for k in ORDER if os.path.isdir(os.path.join(SCREEN, k))]
    keys += sorted(os.path.basename(p) for p in glob.glob(os.path.join(SCREEN, "*")) if os.path.isdir(p)
                   and os.path.basename(p) not in keys)
    summary = {"status": "exploratory: development-stage results on unreviewed draft items", "threshold": THRESHOLD,
               "bootstrap": {"resamples": N_BOOT, "seed": 0, "unit": "task (no-example) / card (oracle)"}, "models": {}}
    task_fail = {}
    for key in keys:
        meta, rows = load_model(key)
        ent = {"hf_repo": meta.get("hf_repo"), "revision": meta.get("revision"), "load_error": meta.get("load_error")}
        gate = [r for r in rows if r["condition"] == "no_example"]
        orc = [r for r in rows if r["condition"] == "oracle"]
        if len(gate) < 20:
            ent["status"] = "not run" if not gate else f"incomplete ({len(gate)}/20 no-example items)"
            summary["models"][key] = ent
            continue
        j = lambda sub: [1 if r["joint"] else 0 for r in sub]  # noqa: E731
        ent["no_example"] = {"overall": boot(j(gate))}
        for fam in ("decision", "code"):
            ent["no_example"][fam] = boot(j([r for r in gate if r["family"] == fam]))
        for src in ("v1_cards", "pilot_seeds"):
            ent["no_example"][src] = boot(j([r for r in gate if r["source"] == src]))
        ent["no_example"]["truncated_likely"] = sum(1 for r in gate if r.get("truncated_likely"))
        ent["no_example"]["format_failure_rate"] = round(sum(1 for r in gate if not r["format_ok"]) / len(gate), 3)
        keep = [r for r in gate if r["task"] not in FLAGGED]
        ent["no_example_without_flagged"] = boot(j(keep))
        ent["eligible_80"] = ent["no_example"]["overall"]["p"] >= THRESHOLD
        if orc:
            ent["oracle"] = {"overall": boot_clustered(orc), "by_role": {}}
            for role in ("analogy", "requirement", "counter"):
                sub = [r for r in orc if r["role"] == role]
                ent["oracle"]["by_role"][role] = boot_clustered(sub)
            ent["oracle"]["format_failure_rate"] = round(sum(1 for r in orc if not r["format_ok"]) / len(orc), 3)
            ent["oracle"]["n_items"] = len(orc)
        ent["failed_no_example_tasks"] = [
            {"task": r["task"], "source": r["source"], "family": r["family"], "format_ok": r["format_ok"],
             "truncated_likely": r.get("truncated_likely", False),
             "failed_checks": [(c["check"] + ": " + " ".join(str(c["note"]).split())[-70:]) if c.get("note") else c["check"]
                              for c in r["failed_checks"]]}
            for r in gate if not r["joint"]]
        for r in gate:
            task_fail.setdefault((r["source"], r["task"], r["family"]), {})[key] = bool(not r["joint"])
        ent["status"] = "complete"
        ent["wall_time_s"] = meta.get("wall_time_s")
        summary["models"][key] = ent

    complete = [k for k, v in summary["models"].items() if v["status"] == "complete"]
    all_fail = [{"source": s, "task": t, "family": f} for (s, t, f), d in sorted(task_fail.items())
                if len(d) == len(complete) and complete and all(d.values())]
    most_fail = [{"source": s, "task": t, "failed_by": sum(d.values()), "of": len(d)} for (s, t, f), d in sorted(task_fail.items())
                 if d and sum(d.values()) >= max(2, len(d) - 1) and not all(d.values())]
    summary["flagged_tasks"] = FLAGGED
    summary["failed_by_every_model"] = all_fail
    summary["failed_by_all_but_one_model"] = most_fail
    json.dump(summary, open(os.path.join(SCREEN, "summary.json"), "w", encoding="utf-8"), indent=1)

    L = ["# WP0.4 backbone competence screen", "",
         "**Exploratory.** Development-stage results on unreviewed draft items (10 v1 draft cards, 10 pilot seeds). "
         "Not evidence for the paper; used only to choose backbones.", "",
         "Gate: a model is eligible if it solves at least 80% of the 20 no-example tasks (joint success: parseable answer and every "
         "task constraint satisfied). Greedy decoding, max 1024 new tokens. Intervals are 95% percentile bootstrap intervals "
         f"({N_BOOT:,} resamples over tasks; oracle: over cards). Oracle = the 68 v1 variants with the gold take / do-not-take "
         "statement in the prompt; joint success needs constraints, required transfer and no leakage. "
         "Code answers are executed by the existing checker, which is not sandboxed.", "",
         "| Model | HF repo @ revision | No-example success (overall) | Decision | Code | v1 cards | Pilot seeds | Format fail | Oracle joint | Eligible (80%) |",
         "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, v in summary["models"].items():
        if v["status"] != "complete":
            L.append(f"| {k} | {v.get('hf_repo')} | {v['status']} | | | | | | | {'load error' if v.get('load_error') else 'no'} |")
            continue
        n = v["no_example"]
        rev = (v.get("revision") or "?")[:8]
        L.append(f"| {k} | {v['hf_repo']} @ {rev} | {fmt(n['overall'])} | {fmt(n['decision'])} | {fmt(n['code'])} | "
                 f"{fmt(n['v1_cards'])} | {fmt(n['pilot_seeds'])} | {n['format_failure_rate'] * 100:.0f}% | "
                 f"{fmt(v['oracle']['overall']) if v.get('oracle') else 'n/a'} | {'yes' if v['eligible_80'] else 'no'} |")
    L += ["", "## Oracle joint success by role", "", "| Model | Analogy | Requirement | Counter-example | Oracle format failure |",
          "| --- | --- | --- | --- | --- |"]
    for k, v in summary["models"].items():
        if v.get("oracle"):
            b = v["oracle"]["by_role"]
            L.append(f"| {k} | {fmt(b['analogy'])} | {fmt(b['requirement'])} | {fmt(b['counter'])} | "
                     f"{v['oracle']['format_failure_rate'] * 100:.0f}% |")
    L += ["", "## Sensitivity: gate without the flagged tasks (not the gate)", "",
          "Excluded: " + "; ".join(f"`{k}` ({v})" for k, v in FLAGGED.items()) + ".", "",
          "| Model | No-example success on the remaining 17 tasks | Would pass 80% |", "| --- | --- | --- |"]
    for k, v in summary["models"].items():
        if v.get("no_example_without_flagged"):
            x = v["no_example_without_flagged"]
            L.append(f"| {k} | {fmt(x)} | {'yes' if x['p'] >= THRESHOLD else 'no'} |")
    L += ["", "## Tasks failed with no example", ""]
    if all_fail:
        L.append("**Failed by every complete model (possible task or checker problem, inspect before blaming the models):** "
                 + ", ".join(f"{x['task']} ({x['source']})" for x in all_fail))
    else:
        L.append("No task was failed by every complete model.")
    if most_fail:
        L.append("")
        L.append("Failed by all but one model: " + ", ".join(f"{x['task']} ({x['failed_by']}/{x['of']})" for x in most_fail))
    for k, v in summary["models"].items():
        if v["status"] != "complete":
            continue
        L += ["", f"### {k}", ""]
        if not v["failed_no_example_tasks"]:
            L.append("No failures.")
        for t in v["failed_no_example_tasks"]:
            why = ("unparseable answer" + (" (output cut off at the token limit)" if t.get("truncated_likely") else "")) if not t["format_ok"] else "; ".join(t["failed_checks"]) or "unknown"
            L.append(f"- `{t['task']}` ({t['source']}, {t['family']}): {why}")
    open(os.path.join(SCREEN, "summary.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")

    # model registry
    reg_path = os.path.join(ROOT, "results", "model_registry.json")
    reg = json.load(open(reg_path, encoding="utf-8")) if os.path.exists(reg_path) else {"models": {}}
    if "models" not in reg:
        reg = {"models": reg}
    for k, v in summary["models"].items():
        meta, _ = load_model(k)
        e = reg["models"].setdefault(k, {})
        e.update({"key": k, "hf_repo": v.get("hf_repo"), "revision": v.get("revision"),
                  "quantisation": meta.get("quantisation"), "dtype": meta.get("dtype"),
                  "parameters_billion_nominal": NOMINAL_B.get(k),
                  "backbone_screen": {"status": v["status"], "load_error": v.get("load_error"),
                                      "no_example_success": v.get("no_example", {}).get("overall"),
                                      "oracle_joint": (v.get("oracle") or {}).get("overall"),
                                      "eligible_80": v.get("eligible_80"), "exploratory": True,
                                      "details": "results/backbone_screen/summary.json"}})
    json.dump(reg, open(reg_path, "w", encoding="utf-8"), indent=1)
    print(open(os.path.join(SCREEN, "summary.md"), encoding="utf-8").read())


if __name__ == "__main__":
    main()
