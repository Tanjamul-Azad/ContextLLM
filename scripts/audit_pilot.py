"""Read-only audit of saved pilot outputs; never loads models or executes generated code.

Writes a new audit directory only. Old results and pass rules are preserved.
"""
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "audit_2026-11-05"


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    files = {}
    models = {}
    for directory in sorted((ROOT / "results" / "behaviour").iterdir()):
        scored_path = directory / "scored.jsonl"
        if not scored_path.is_file():
            continue
        generation_path = directory / "generations.jsonl"
        rows = read_jsonl(scored_path)
        generations = read_jsonl(generation_path)
        for path in (scored_path, generation_path):
            files[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        plain = [r for r in rows if r["role"] != "none" and r["wording"] == "plain" and r["turns"] == "single"]
        explicit = [r for r in rows if r["role"] != "none" and r["wording"] == "explicit" and r["turns"] == "single"]
        plain_fail = sum(not r["joint"] for r in plain)
        explicit_fail = sum(not r["joint"] for r in explicit)
        fp = plain_fail / len(plain)
        fe = explicit_fail / len(explicit)
        raw_ids = [r["item"] for r in generations]
        scored_ids = [r["item"] for r in rows]
        models[directory.name] = {
            "saved_answers": len(rows),
            "independent_seed_count": len({r["seed"] for r in rows}),
            "unique_scored_item_ids": len(set(scored_ids)),
            "raw_and_scored_ids_match": set(raw_ids) == set(scored_ids),
            "duplicate_raw_item_ids": len(raw_ids) - len(set(raw_ids)),
            "plain_single_n": len(plain), "plain_single_fail_n": plain_fail,
            "plain_single_failure_rate_as_scored": fp,
            "explicit_single_n": len(explicit), "explicit_single_fail_n": explicit_fail,
            "explicit_single_failure_rate_as_scored": fe,
            "plain_format_failure_n": sum(not r["format_ok"] for r in plain),
            "explicit_format_failure_n": sum(not r["format_ok"] for r in explicit),
            "old_E4_pass_rule_met": fp >= .25 and fe <= fp / 2,
            "interpretation": "Recomputed from saved scores, not independently re-generated; scoring validity remains unverified.",
        }
    handchecks = {}
    for source in ("wildchat", "oasst"):
        folder = ROOT / "results" / f"E1_{source}"
        with (folder / "handcheck_sample.csv").open(encoding="utf-8", newline="") as stream:
            sample = list(csv.DictReader(stream))
        positives = [r for r in sample if r["hand_gives_example"].lower() == "true"]
        handchecks[source] = {
            "rows_in_handcheck_file": len(sample),
            "positives_in_handcheck_file": len(positives),
            "positive_roles": {role: sum(r["hand_role"] == role for r in positives)
                               for role in ("analogy", "requirement", "counter-example")},
            "annotation_provenance": "File label names do not establish who annotated them; independent human verification is pending.",
            "population_prevalence_claim": "Not established: keyword-selected, length-filtered and deduplicated candidate sample; missed positives not audited.",
        }
    seeds = json.loads((ROOT / "data" / "seeds.json").read_text(encoding="utf-8"))
    p5 = next(s for s in seeds if s["id"] == "P5_newsletter_headlines")
    transfer_specs = [check for kind, check in p5["roles"]["analogy"]["checks"] if kind == "transfer"]
    report = {
        "audit_date": "2026-11-05", "models": models, "handcheck_files": handchecks,
        "confirmed_scoring_mismatch": {
            "seed": p5["id"], "prompt_rules": p5["rules"], "transfer_check": transfer_specs,
            "issue": "Prompt allows ten words; analogy checker requires at most eight. Nine/ten-word answers can be penalized without a matching instruction.",
        },
        "additional_design_issues": [
            "Plain P1 asks for inspiration but its gold bans colour names; that prohibition is only explicit in the explicit variant. Human adjudication is required.",
            "checks.score marks invalid format as leakage. Report format failure separately from source-detail import.",
            "E5 requirement-minus-counter marker gap is a role-response sanity check, not proof of useful analogical transfer or of a role-specific failure.",
            "Logit lens uses a supplied answer prefix and hand-picked token sets on five seeds from one model. It does not locate a causal failure layer or identify harmful neurons.",
            "GSM8K membership diagnostics do not certify newly constructed seed cards; rewriting and negative detection results do not establish non-membership.",
        ],
        "source_file_sha256": files,
        "decision": "REVISE AND CONTINUE FEASIBILITY ONLY. No main-paper go/freeze conclusion follows yet.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Existing pilot audit - 5 November 2026", "",
             "Saved files were checked. No model was run; no generated code was executed.", "",
             "| Model | Saved outputs | Seeds | Plain failures | Explicit failures | Old E4 rule met? |",
             "| --- | ---: | ---: | ---: | ---: | --- |"]
    for name, m in models.items():
        lines.append(f"| {name} | {m['saved_answers']} | {m['independent_seed_count']} | {m['plain_single_fail_n']}/{m['plain_single_n']} | {m['explicit_single_fail_n']}/{m['explicit_single_n']} | {m['old_E4_pass_rule_met']} |")
    lines += ["", "Rates reproduce the old scorer, whose gold/check validity needs revision. They are exploratory, not confirmed role-transfer failure rates.", "",
              "Confirmed mismatch: P5's prompt allows ten words, but the analogy transfer checker permits only eight.", "",
              "Handcheck files contain WildChat 10/45 positive labels (9 requirement, 1 analogy) and OASST2 12/40 (8 requirement, 2 analogy, 2 counter-example). Annotator identity and independent human verification remain unconfirmed. These files do not establish population prevalence.", "",
              "## Issues requiring revision", ""]
    lines.extend(f"- {issue}" for issue in report["additional_design_issues"])
    lines += ["", f"Decision: **{report['decision']}**", "",
              "Original files are preserved. File hashes and item-ID checks are in summary.json. Revised gates must be evaluated on new held-out seeds, never represented as pre-registered for these old results."]
    (OUT / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"audit": str(OUT), "models": models, "decision": report["decision"]}, indent=2))


if __name__ == "__main__":
    main()
