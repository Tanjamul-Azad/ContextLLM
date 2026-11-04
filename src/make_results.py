"""Collect every experiment's summary into results/overview.json and print a verdict table.

Usage: python -I src/make_results.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "results")


def load(*p):
    path = os.path.join(R, *p)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    beh = load("behaviour", "summary.json") or {}
    e1s = {src: load(f"E1_{src}", "summary.json") for src in ("wildchat", "oasst")}
    e3 = load("contamination", "qwen2.5-3b", "summary.json")
    e7 = load("logit_lens", "qwen2.5-3b", "summary.json")
    ov = {"models": list(beh)}

    ov["E1"] = {}
    for src, e1 in e1s.items():
        if e1 is None:
            continue
        est = e1.get("estimate_full_dataset", e1.get("estimate_full_english_set"))
        ov["E1"][src] = {"sample": e1["sample"], "labelled_examples_in_sample": e1["model_labelled_examples"],
                         "by_role": e1["by_role"], "cross_domain": e1["cross_domain"],
                         "estimate_full_dataset": est, "pass": est >= 300}
    ov["E2"] = {"status": "not run: needs two human annotators (data/E2_annotation_sheet.csv)"}
    ov["E3"] = None if e3 is None else {"flag_gsm8k": e3["flag_source"], "guided": e3["guided_completion"],
                                        "min_k": e3["min_k_prob(k=20%)"]}
    for k in ("E4", "E5", "E6"):
        ov[k] = {m: {"pass": beh[m][k]["pass"]} | {x: beh[m][k][x] for x in beh[m][k] if x not in ("pass", "rule")} for m in beh}
    if e7:
        n_sep = sum(1 for p in e7["probes"].values() if p["separation_layer"] is not None)
        ov["E7"] = {"probes_with_clear_separation": n_sep, "n_probes": len(e7["probes"]), "pass": n_sep >= 3,
                    "probes": e7["probes"]}
    with open(os.path.join(R, "overview.json"), "w", encoding="utf-8") as f:
        json.dump(ov, f, indent=1)
    print(json.dumps({k: (v if k in ("E1", "E2", "E7") else v) for k, v in ov.items()}, indent=1)[:6000])


if __name__ == "__main__":
    main()
