"""Export complete, prompt-identical review packs without overwriting v1 drafts.

No model calls, scoring, human answers or seed mutations. Run from any directory.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from seed_lint_v1 import build_messages

OUT = ROOT / "data/human_review/v1_1_draft"


def main():
    if OUT.exists():
        raise SystemExit("Output directory exists; refusing to overwrite reviews.")
    cards = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted((ROOT / "data/seeds_v1_draft").glob("*.json"))]
    items = [(f"R{i:03d}", c, v) for i, (c, v) in enumerate(
        ((c, v) for c in cards for v in c["variants"]), 1)]
    manifest = {}
    packs = {}
    for reviewer in ("a", "b"):
        ordered = list(items)
        random.Random(f"v1.1-reviewer-{reviewer}").shuffle(ordered)
        lines = [f"# Independent review v1.1: reviewer {reviewer.upper()}", "",
                 "Do not open the other review, seed JSON, Part 2 or researcher manifest before both Part 1 reviews are submitted.",
                 "Each block is the COMPLETE single-turn model prompt, including variant-specific rules and output format.",
                 "Answer from this prompt only. A source detail being unnecessary does not automatically make it prohibited.",
                 "MAY USE means permitted but optional; UNCLEAR means the prompt does not determine the answer.",
                 "For each scope item, quote prompt evidence and mark DIRECT or INFERRED. Explain inferred mappings briefly.",
                 "For omitted details, do not invent a quotation or treat omission alone as a prohibition.",
                 "Write 'none' where appropriate. Do not force a unique role when the prompt is genuinely ambiguous.",
                 "Record any prior exposure. The author of a seed cannot count as an independent blind reviewer of that seed.",
                 "Related prompts can occur in this pack; judge each on its own. Repeated variants are not independent seeds.", ""]
        for code, c, v in ordered:
            prompt = build_messages(c, v, "single")[0]["content"]
            digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            manifest[code] = {"seed": c["id"], "variant": v["id"], "prompt_sha256": digest}
            lines += [f"## {code}", "", "<!-- BEGIN EXACT PROMPT -->", prompt,
                      "<!-- END EXACT PROMPT -->", "",
                      "- Prior exposure (none / authored / saw gold / other):",
                      "- Role (analogy / requirement / counter-example / mixed / unclear):",
                      "- Role evidence (quote + DIRECT/INFERRED + reason):",
                      "- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):",
                      "- MAY USE from example (one item per line; evidence or explain why optional):",
                      "- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):",
                      "- Target constraints that must remain (one item per line; evidence):",
                      "- UNCLEAR / conflicting requirements:",
                      "- Realism of this complete prompt (1-5 + brief reason):",
                      "- Review time in minutes:", ""]
        packs[f"reviewer_{reviewer}_part1.md"] = "\n".join(lines)

    # Separate files: one reviewer never sees the other's decisions.
    for reviewer in ("a", "b"):
        lines = [f"# Part 2: reviewer {reviewer.upper()}", "",
                 "Open ONLY after BOTH reviewers have submitted Part 1. Work independently.",
                 "These are author-flagged ambiguous draft checks, not accepted gold labels.",
                 "Use the corresponding R-code in your Part 1 for the complete prompt.",
                 "This list does not replace auditing the remaining checks. A clear-labelled check can also be wrong.", "",
                 "| Item | Draft check | Proposed condition | Decision: keep/drop/reword | Prompt evidence and reason |",
                 "| --- | --- | --- | --- | --- |"]
        for code, c, v in items:
            for kind in ("must_transfer", "must_not_transfer"):
                for ch in v.get(kind, []):
                    if ch.get("basis", {}).get("ambiguity") == "ambiguous":
                        what = ch["what"].replace("|", "\\|").replace("\n", " ")
                        lines.append(f"| {code} | {ch['id']} | {what} | | |")
        packs[f"reviewer_{reviewer}_part2.md"] = "\n".join(lines) + "\n"

    # Verify every exported prompt against the actual model prompt builder.
    for reviewer in ("a", "b"):
        content = packs[f"reviewer_{reviewer}_part1.md"]
        assert content.count("<!-- BEGIN EXACT PROMPT -->") == len(items)
        for code, c, v in items:
            block = content.split(f"## {code}\n", 1)[1].split("<!-- BEGIN EXACT PROMPT -->\n", 1)[1]
            rendered = block.split("\n<!-- END EXACT PROMPT -->", 1)[0]
            assert rendered == build_messages(c, v, "single")[0]["content"]
    packs["README.md"] = """# Review pack v1.1 — 6 November 2026

Use reviewer_a_part1.md and reviewer_b_part1.md independently.
This corrects v1's omission of variant-specific target rules and output format.
All 68 full prompts per reviewer were checked against build_messages; hashes
are in the researcher-only manifest. No model outputs or draft gold are shown
in Part 1. Keep the manifest and seed JSON closed until both Part 1 submissions.

Start with a timed batch of 6–10 prompts. If instructions change after calibration,
record the change and report calibration separately from subsequent agreement.
Prior v1 answers, if any exist elsewhere, are not interchangeable with v1.1 answers.
Items with changed information require fresh review and exposure disclosure.

Each reviewer uses their OWN Part 2 file only after BOTH Part 1 submissions.
Part 2 contains 95 author-flagged checks; every other gold check also needs a
prompt-evidence audit before release. The old reference checklist still needs
verification; no citations were verified by this export.

Role categories support categorical agreement statistics. Free-text scope answers
do NOT directly produce Cohen's kappa. Preserve independent original answers;
define aligned atomic propositions and labels before calculating scope agreement.
Report pre-adjudication agreement, uncertainty and rejection/ambiguity rates.
These 10 development seeds are not a final held-out benchmark.
"""
    packs["researcher_only_manifest.json"] = json.dumps(manifest, indent=2)
    OUT.mkdir(parents=True)
    for name, content in packs.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"Created {len(items)} complete prompts per reviewer; verified exact prompt equality.")
    print(f"Created separate Part 2 files. Output: {OUT}")


if __name__ == "__main__":
    main()
