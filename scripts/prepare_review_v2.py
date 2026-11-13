"""Export blind review packs for v2 seed cards (successor of prepare_review_v1_1.py).

Reviewers see the complete single-turn prompt of every variant and the licensed units of the card (ideas and
surface items, with quotes from the example), never the author's labels, notes or checks. Two reviewers get the
same items in a different order, and the units inside an item in a different order. Part 1 (role, realism, a
label for every unit) is done before Part 2 (span review and the author-flagged items). The manifest that maps
codes to cards stays with the researcher.

Usage:
    python -I scripts/prepare_review_v2.py [--cards DIR_OR_FILES ...] [--out DIR]

Default cards: data/seeds_v2_draft/. Default output: data/human_review/v2_draft/. Refuses to overwrite an
existing output directory (it may hold reviews). No model calls, no scoring, no card is changed.
The filled Part 1 files are read back into the cards' human_review slots by scripts/import_review_v2.py.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import checks_v2 as V2  # noqa: E402
import seed_lint_v1 as L1  # noqa: E402
import seed_lint_v2 as L  # noqa: E402

DEFAULT_OUT = ROOT / "data/human_review/v2_draft"


def clip(s, n=80):
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n - 3] + "..."


def unit_block(card, order_rng):
    """Lines that describe the units of a card without any label, in a reviewer-specific order."""
    reg = V2.unit_registry(card)
    quotes = {}
    for s in card["source_spans"]:
        if s["kind"] != "context":
            quotes.setdefault(s["unit"], [])
            if clip(s["text"], 70) not in quotes[s["unit"]]:
                quotes[s["unit"]].append(clip(s["text"], 70))
    ids = list(reg)
    order_rng.shuffle(ids)
    lines = []
    for u in ids:
        info = reg[u]
        kind = "idea" if info["kind"] == "relation" else "surface item"
        q = "; ".join(f'"{x}"' for x in quotes.get(u, [])[:3])
        lines.append((u, f"{u} ({kind}): {clip(info['text'], 140)}  | in the example: {q}"))
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cards", nargs="*", default=[str(ROOT / "data/seeds_v2_draft")])
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"Output directory {out} exists; refusing to overwrite reviews.")
    files, cards = L.load(a.cards)
    for f, c in zip(files, cards):
        if "__load_error__" in c:
            raise SystemExit(f"cannot read {f}: {c['__load_error__']}")
        errs = [it for it in L.lint_card(c, gold=False, path=f).items if it["level"] == "ERROR"]
        if errs:
            raise SystemExit(f"{c.get('id', f)} has lint errors; fix them before review. First: {L.fmt(errs[0])}")
    items = [(f"R{i:03d}", c, v) for i, (c, v) in enumerate(((c, v) for c in cards for v in c["variants"]), 1)]
    manifest, packs = {}, {}
    for reviewer in ("a", "b"):
        ordered = list(items)
        random.Random(f"v2-reviewer-{reviewer}").shuffle(ordered)
        lines = [f"# Independent review v2: reviewer {reviewer.upper()}", "",
                 "Do not open the other review, any seed JSON, Part 2 or the researcher manifest before both Part 1 reviews are submitted.",
                 "Each block is the COMPLETE single-turn model prompt, including variant-specific rules and output format.",
                 "Answer from this prompt only. A source detail being unnecessary does not automatically make it prohibited.",
                 "",
                 "Label every unit listed under the prompt with exactly one of:",
                 "- MUST: an answer that does not use this unit fails the user's request.",
                 "- MUST_NOT: an answer that uses this unit fails the user's request.",
                 "- MAY: using it or not using it never makes an answer wrong (permitted but optional).",
                 "- UNCLEAR: the prompt does not let you decide between two of these labels.",
                 "After the label write a semicolon, the shortest prompt phrase that carries the instruction (outside the example),",
                 "a semicolon, and DIRECT (an instruction or rule covers the unit) or INFERRED (you reasoned from the role).",
                 "Leave the evidence out for MAY when nothing in the prompt speaks to the unit. Do not invent a quotation.",
                 "Do not force a unique role when the prompt is genuinely ambiguous (write mixed or unclear).",
                 "Record any prior exposure. The author of a card cannot count as an independent blind reviewer of that card.",
                 "Related prompts can occur in this pack; judge each on its own. Repeated variants are not independent seeds.", ""]
        for code, c, v in ordered:
            prompt = L1.build_messages(c, v, "single")[0]["content"]
            manifest[code] = {"card": c["id"], "variant": v["id"], "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}
            ub = unit_block(c, random.Random(f"v2-{reviewer}-{code}"))
            lines += [f"## {code}", "", "<!-- BEGIN EXACT PROMPT -->", prompt, "<!-- END EXACT PROMPT -->", "",
                      "Units of the example (label each one below):", ""]
            lines += [f"- {text}" for _, text in ub]
            lines += ["", "- Prior exposure (none / authored / saw gold / other):",
                      "- Role (analogy / requirement / counter / mixed / unclear):",
                      "- Role evidence (quote + DIRECT/INFERRED + reason):",
                      "- Realism of this complete prompt (1-5):",
                      "- Realism reason:",
                      "- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):"]
            lines += [f"  - {u}:" for u, _ in ub]
            lines += ["- UNCLEAR / conflicting requirements:", "- Review time in minutes:", ""]
        packs[f"reviewer_{reviewer}_part1.md"] = "\n".join(lines)

    # Part 2: only after both Part 1 files are submitted. Segmentation, and what the author flagged.
    flagged = []
    for code, c, v in items:
        entries = V2.expand_licence(c, v)[0]
        for u, e in entries.items():
            if e.get("label") == "UNCLEAR" or (e.get("label") == "MAY" and e.get("note") and not e["_default"]):
                flagged.append((code, u, "author note", e.get("note", "")))
        for it in V2.iter_checks(c, v):
            if V2.is_judge(it["check"]):
                flagged.append((code, ", ".join(it["check"].get("units") or []), "judge question", it["check"].get("what", "")))
    for reviewer in ("a", "b"):
        lines = [f"# Part 2: reviewer {reviewer.upper()}", "",
                 "Open ONLY after BOTH reviewers have submitted Part 1. Work independently.",
                 "A. Segmentation. For each card, check that every span belongs to the unit it names. Mark 'mixes units' if a span",
                 "   carries two ideas or two surface items that could get different labels, and say how you would split it.", ""]
        for c in cards:
            lines += [f"### {c['id']}", "", "| Span | Kind | Unit | Text | OK / mixes units / wrong unit | Suggested split or unit |",
                      "| --- | --- | --- | --- | --- | --- |"]
            for s in c["source_spans"]:
                lines.append(f"| {s['id']} | {s['kind']} | {s.get('unit', '')} | {clip(s['text'], 90).replace('|', chr(92) + '|')} | | |")
            lines.append("")
        lines += ["B. Items the author flagged. These are author notes and questions, not accepted gold labels.",
                  "   Use the R-code to find the complete prompt in your Part 1. Do not change your Part 1 answers.", "",
                  "| Item | Unit(s) | Type | Author note or question | Decision (agree / disagree / unsure) | Reason |",
                  "| --- | --- | --- | --- | --- | --- |"]
        for code, u, kind, text in flagged:
            lines.append(f"| {code} | {u} | {kind} | {clip(text, 220).replace('|', chr(92) + '|')} | | |")
        packs[f"reviewer_{reviewer}_part2.md"] = "\n".join(lines) + "\n"

    # Verify every exported prompt against the model prompt builder, and that no label leaked into Part 1.
    for reviewer in ("a", "b"):
        content = packs[f"reviewer_{reviewer}_part1.md"]
        assert content.count("<!-- BEGIN EXACT PROMPT -->") == len(items)
        for code, c, v in items:
            block = content.split(f"## {code}\n", 1)[1].split("<!-- BEGIN EXACT PROMPT -->\n", 1)[1]
            assert block.split("\n<!-- END EXACT PROMPT -->", 1)[0] == L1.build_messages(c, v, "single")[0]["content"]
            tail = block.split("<!-- END EXACT PROMPT -->", 1)[1].split("## R", 1)[0]
            for u in V2.unit_registry(c):
                line = next(x for x in tail.split("\n") if x.startswith(f"  - {u}:"))
                assert line.strip() == f"- {u}:", line
    packs["README.md"] = f"""# Review pack v2 (draft)

Use reviewer_a_part1.md and reviewer_b_part1.md independently. Each reviewer sees {len(items)} complete prompts
({len(cards)} cards), in a different order, with the units of the example in a different order. No author label,
note, check or answer is shown in Part 1. Hashes of the prompts are in the researcher-only manifest.

Part 1 gives, per prompt: the role, a realism rating from 1 to 5, and one label per unit (MUST, MAY, MUST_NOT or
UNCLEAR) with evidence. Part 2 (span review and the author-flagged items) is opened only after both Part 1 files are
submitted. Keep the manifest and the card JSON closed until then.

Start with a timed batch of 6 to 10 prompts. If instructions change after calibration, record the change and report
calibration separately from later agreement. The author of a card must not review it (lint rule H2).

Filled Part 1 files are read back into the cards' human_review slots with scripts/import_review_v2.py.
Report agreement before adjudication, then the adjudications, then the share of variants in the ambiguity set.
"""
    packs["researcher_only_manifest.json"] = json.dumps(manifest, indent=2)
    out.mkdir(parents=True)
    for name, content in packs.items():
        (out / name).write_text(content, encoding="utf-8")
    print(f"Created {len(items)} complete prompts per reviewer ({len(cards)} cards); verified exact prompt equality and no labels in Part 1.")
    print(f"Part 2 flagged items: {len(flagged)}. Output: {out}")


if __name__ == "__main__":
    main()
