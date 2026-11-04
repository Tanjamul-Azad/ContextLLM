"""Summarise E4-E6 from results/behaviour/<model>/scored.jsonl.

Usage: python -I src/analyze.py
Writes results/behaviour/summary.json, summary.md, per_seed.csv and figures.
"""
import csv
import json
import os
import random
import sys
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEH = os.path.join(ROOT, "results", "behaviour")
ROLES = ["analogy", "requirement", "counter"]
B = 5000


def load():
    data = {}
    for m in sorted(os.listdir(BEH)):
        p = os.path.join(BEH, m, "scored.jsonl")
        if os.path.isfile(p):
            with open(p, encoding="utf-8") as f:
                data[m] = [json.loads(x) for x in f]
    return data


def rate(rows, key, val=True):
    rows = [r for r in rows if r[key] is not None]
    return sum(r[key] == val for r in rows) / len(rows) if rows else float("nan")


def boot(rows, stat, seed=0):
    """95% CI by resampling seeds (variants of one seed are not independent)."""
    by = defaultdict(list)
    for r in rows:
        by[r["seed"]].append(r)
    seeds = sorted(by)
    rnd = random.Random(seed)
    vals = []
    for _ in range(B):
        pick = [rnd.choice(seeds) for _ in seeds]
        sample = [r for s in pick for r in by[s]]
        v = stat(sample)
        if v == v:
            vals.append(v)
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def sel(rows, **kw):
    return [r for r in rows if all(r[k] == v for k, v in kw.items())]


def pct(x):
    return f"{100 * x:.0f}%" if x == x else "n/a"


def ci(c):
    return f"[{100 * c[0]:.0f}, {100 * c[1]:.0f}]"


def analyse(model, rows):
    ex = [r for r in rows if r["role"] != "none"]
    base = sel(rows, role="none")
    out = {"model": model, "n_answers": len(rows), "n_seeds": len({r["seed"] for r in rows})}

    # condition table
    table = []
    for role in ROLES:
        for w in ("plain", "explicit"):
            for t in ("single", "multi"):
                g = sel(ex, role=role, wording=w, turns=t)
                table.append({"role": role, "wording": w, "turns": t, "n": len(g),
                              "format_ok": rate(g, "format_ok"), "constraint_ok": rate(g, "constraint_ok"),
                              "transfer_ok": rate(g, "transfer_ok"), "leak": rate(g, "leak"),
                              "joint": rate(g, "joint"), "copied_marker": rate(g, "marker")})
    out["conditions"] = table
    out["baseline_no_example"] = {"n": len(base), "format_ok": rate(base, "format_ok"), "constraint_ok": rate(base, "constraint_ok")}
    with_ex_single = sel(ex, turns="single", wording="plain")
    out["constraint_ok_with_example_plain_single"] = rate(with_ex_single, "constraint_ok")

    # E4: do models fail, and does stating the relation help?
    plain = sel(ex, wording="plain", turns="single")
    expl = sel(ex, wording="explicit", turns="single")
    f_plain = 1 - rate(plain, "joint")
    f_expl = 1 - rate(expl, "joint")
    out["E4"] = {
        "failure_plain": f_plain, "failure_plain_ci": boot(plain, lambda s: 1 - rate(s, "joint")),
        "failure_explicit": f_expl, "failure_explicit_ci": boot(expl, lambda s: 1 - rate(s, "joint")),
        "failure_by_role_plain": {r: 1 - rate(sel(plain, role=r), "joint") for r in ROLES},
        "leak_plain": rate(plain, "leak"), "missed_transfer_plain": 1 - rate(plain, "transfer_ok"),
        "constraint_broken_plain": 1 - rate(plain, "constraint_ok"),
        "pass": f_plain >= 0.25 and f_expl <= f_plain / 2,
        "rule": "failure (plain) >= 25% and explicit wording halves it",
    }

    # E5: does the role change what the model copies?
    def role_gap(s):
        return rate(sel(s, role="requirement"), "marker") - rate(sel(s, role="counter"), "marker")

    gap = role_gap(plain)
    gap_ci = boot(plain, role_gap)
    out["E5"] = {
        "copied_marker_plain": {r: rate(sel(plain, role=r), "marker") for r in ROLES},
        "role_gap_requirement_minus_counter": gap, "role_gap_ci": gap_ci,
        "joint_by_role_plain": {r: rate(sel(plain, role=r), "joint") for r in ROLES},
        "pass": gap >= 0.15 and gap_ci[0] > 0,
        "rule": "copy rate (requirement) minus copy rate (counter-example) >= 15 points, CI above 0",
    }

    # E6: single-turn vs multi-turn (plain wording)
    multi = sel(ex, wording="plain", turns="multi")
    f_multi = 1 - rate(multi, "joint")
    out["E6"] = {"failure_single": f_plain, "failure_multi": f_multi,
                 "multi_ci": boot(multi, lambda s: 1 - rate(s, "joint")),
                 "pass": f_plain >= 0.25, "rule": "the failure also appears in single-turn (>= 25%)"}

    # per seed
    out["per_seed"] = []
    for s in sorted({r["seed"] for r in rows}):
        rec = {"seed": s}
        for role in ROLES:
            g = sel(plain, seed=s, role=role)
            rec[f"{role}_joint"] = g[0]["joint"] if g else None
            rec[f"{role}_marker"] = g[0]["marker"] if g else None
        out["per_seed"].append(rec)
    return out


def plots(res):
    fig_dir = os.path.join(BEH, "figures")
    os.makedirs(fig_dir, exist_ok=True)
    models = list(res)
    # joint success by role, plain vs explicit
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 3.6), squeeze=False)
    for ax, m in zip(axes[0], models):
        c = res[m]["conditions"]
        for k, (w, col) in enumerate([("plain", "#4C78A8"), ("explicit", "#F58518")]):
            ys = [next(x["joint"] for x in c if x["role"] == r and x["wording"] == w and x["turns"] == "single") for r in ROLES]
            ax.bar([i + k * 0.38 for i in range(3)], [100 * y for y in ys], width=0.36, color=col, label=w)
        ax.set_xticks([i + 0.19 for i in range(3)], ROLES)
        ax.set_ylim(0, 100)
        ax.set_ylabel("joint success (%)")
        ax.set_title(m)
        ax.legend(frameon=False)
    fig.suptitle("Answers that get everything right, by example role (single-turn)")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, "joint_by_role.png"), dpi=130)
    plt.close(fig)
    # copy rate by role
    fig, axes = plt.subplots(1, len(models), figsize=(5.2 * len(models), 3.6), squeeze=False)
    for ax, m in zip(axes[0], models):
        cm = res[m]["E5"]["copied_marker_plain"]
        ax.bar(ROLES, [100 * cm[r] for r in ROLES], color=["#4C78A8", "#54A24B", "#E45756"])
        ax.set_ylim(0, 100)
        ax.set_ylabel("copied the example's pattern (%)")
        ax.set_title(m)
    fig.suptitle("Should copy: requirement. Should not: counter-example (plain, single-turn)")
    fig.tight_layout()
    fig.savefig(os.path.join(fig_dir, "copy_rate_by_role.png"), dpi=130)
    plt.close(fig)


def write_md(res):
    L = ["# Behaviour results (E4-E6)", "", "Generated by `src/analyze.py`. Intervals are 95% bootstrap over seeds.", ""]
    for m, r in res.items():
        e4, e5, e6 = r["E4"], r["E5"], r["E6"]
        L += [f"## {m}", "",
              f"{r['n_answers']} answers from {r['n_seeds']} seeds.", "",
              "| Experiment | Result | Rule | Pass? |", "| --- | --- | --- | --- |",
              f"| E4 failure, plain wording | {pct(e4['failure_plain'])} {ci(e4['failure_plain_ci'])} | {e4['rule']} | {'yes' if e4['pass'] else 'no'} |",
              f"| E4 failure, explicit wording | {pct(e4['failure_explicit'])} {ci(e4['failure_explicit_ci'])} | | |",
              f"| E5 copy rate: requirement minus counter | {pct(e5['role_gap_requirement_minus_counter'])} {ci(e5['role_gap_ci'])} | {e5['rule']} | {'yes' if e5['pass'] else 'no'} |",
              f"| E6 failure single-turn vs multi-turn | {pct(e6['failure_single'])} vs {pct(e6['failure_multi'])} | {e6['rule']} | {'yes' if e6['pass'] else 'no'} |",
              "",
              f"Where plain answers fail: leaked a detail {pct(e4['leak_plain'])}, missed the needed transfer {pct(e4['missed_transfer_plain'])}, broke a target rule {pct(e4['constraint_broken_plain'])}. "
              f"Without any example, target rules hold in {pct(r['baseline_no_example']['constraint_ok'])} of answers; with an example, {pct(r['constraint_ok_with_example_plain_single'])}.", "",
              "| Role | Joint success (plain) | Failure (plain) | Copied the pattern |", "| --- | --- | --- | --- |"]
        for role in ROLES:
            L.append(f"| {role} | {pct(e5['joint_by_role_plain'][role])} | {pct(e4['failure_by_role_plain'][role])} | {pct(e5['copied_marker_plain'][role])} |")
        L += ["", "| Role | Wording | Turns | n | Format | Rules kept | Transfer right | Leaked | Joint | Copied pattern |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for c in r["conditions"]:
            L.append(f"| {c['role']} | {c['wording']} | {c['turns']} | {c['n']} | {pct(c['format_ok'])} | {pct(c['constraint_ok'])} | "
                     f"{pct(c['transfer_ok'])} | {pct(c['leak'])} | {pct(c['joint'])} | {pct(c['copied_marker'])} |")
        L.append("")
    L += ["![joint](figures/joint_by_role.png)", "", "![copy](figures/copy_rate_by_role.png)", ""]
    with open(os.path.join(BEH, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    data = load()
    if not data:
        sys.exit("no scored results yet")
    res = {m: analyse(m, rows) for m, rows in data.items()}
    with open(os.path.join(BEH, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(BEH, "per_seed.csv"), "w", newline="", encoding="utf-8") as f:
        w = None
        for m, r in res.items():
            for rec in r["per_seed"]:
                rec = {"model": m, **rec}
                if w is None:
                    w = csv.DictWriter(f, fieldnames=list(rec))
                    w.writeheader()
                w.writerow(rec)
    plots(res)
    write_md(res)
    for m, r in res.items():
        print(m, "E4", pct(r["E4"]["failure_plain"]), "->", pct(r["E4"]["failure_explicit"]),
              "| E5 gap", pct(r["E5"]["role_gap_requirement_minus_counter"]), ci(r["E5"]["role_gap_ci"]),
              "| E6", pct(r["E6"]["failure_single"]), "vs", pct(r["E6"]["failure_multi"]))


if __name__ == "__main__":
    main()
