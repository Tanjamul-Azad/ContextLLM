"""Build blind review packs for the 10 v1 draft seed cards (two independent annotators).

Part 1 is blind: reviewers see the task, rules, source example and each user message,
but not the role, cue, fit or gold checks. Part 2 (opened only after Part 1 is finished)
asks for decisions on checks the author marked ambiguous. Part 3 is for one person:
open every reference and confirm it supports the case.

Usage: python -I scripts/prepare_review_v1.py
Writes data/human_review/v1_draft/{reviewer_a,reviewer_b}_part1.md, part2.md, part3_references.md
and _key_open_after_review.json. Refuses to overwrite existing files.
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = sorted((ROOT / "data" / "seeds_v1_draft").glob("*.json"))
OUT = ROOT / "data" / "human_review" / "v1_draft"


def write_new(path, text):
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.write_text(text, encoding="utf-8")


def part1(cards, reviewer, key):
    L = [f"# Seed review v1, Part 1 (blind) - reviewer {reviewer.upper()}", "",
         "Do this alone. Do not look at the other reviewer's file, the seed JSON files or Part 2 until you finish.", "",
         "For every message below, answer three questions from the user's point of view:", "",
         "1. **Role:** is the example meant as `analogy` (borrow the idea, not the details), `requirement` "
         "(follow a specified part exactly), `counter-example` (avoid what it does), or `unclear`?",
         "2. **Must carry over:** what from the example must the answer use? Write `nothing` if nothing.",
         "3. **Must NOT carry over:** which details from the example must stay out of the answer?", "",
         "At the end of each seed, rate how realistic the whole situation is: 1 (artificial) to 5 (could happen at work tomorrow).", ""]
    for c in cards:
        L += ["---", "", f"## Seed {c['id']}", "", f"**Task.** {c['target']['task']}", "", "**Rules.**"]
        L += [f"- {r['text']}" for r in c["target"]["rules"]]
        L += ["", "**Source example** (inserted where a message says {EX}):", "", "> " + c["source_example"]["text"].replace("\n", "\n> "), ""]
        variants = list(c["variants"])
        random.Random(f"{c['id']}-order").shuffle(variants)
        for i, v in enumerate(variants, 1):
            code = f"{c['id']}-{i:02d}"
            key[code] = {"seed": c["id"], "variant": v["id"], "role": v["role"], "cue": v["cue"], "fit": v["fit"]}
            msg = v["text"].replace("{EX}", "[source example above]")
            L += [f"### {code}", "", "> " + msg.replace("\n", "\n> "), "",
                  "- Role: ", "- Must carry over: ", "- Must NOT carry over: ", ""]
        L += [f"**Realism of seed {c['id']} (1-5):** ", "", "**Notes:** ", ""]
    return "\n".join(L)


def part2(cards):
    L = ["# Seed review v1, Part 2 - open only after Part 1 is finished", "",
         "The author marked these checks as ambiguous: the message only implies them. For each, decide whether a careful reader "
         "would agree the answer must meet it. Write `keep`, `drop` or `reword: ...`. Both reviewers fill this independently.", ""]
    for c in cards:
        rows = []
        for v in c["variants"]:
            for kind in ("must_transfer", "must_not_transfer"):
                for ch in v.get(kind, []):
                    if (ch.get("basis") or {}).get("ambiguity") == "ambiguous":
                        rows.append((v["id"], kind, ch["id"], ch["what"]))
        if not rows:
            continue
        L += [f"## {c['id']}", "", "| Variant | Kind | Check | What it requires | Reviewer A | Reviewer B |", "| --- | --- | --- | --- | --- | --- |"]
        L += [f"| {v} | {k.replace('_', ' ')} | {i} | {w} | | |" for v, k, i, w in rows]
        L.append("")
    return "\n".join(L)


def part3(cards):
    L = ["# Seed review v1, Part 3 - reference check (one person)", "",
         "Open every reference. Mark `ok` if it exists and supports the facts used in the source example, otherwise write what is wrong.", "",
         "| Seed | Case | Reference | Link | Check |", "| --- | --- | --- | --- | --- |"]
    for c in cards:
        p = c["provenance"]
        for r in p.get("references", []):
            link = r.get("url") or (f"https://doi.org/{r['doi']}" if r.get("doi") else "")
            L.append(f"| {c['id']} | {p.get('case', '')} | {r.get('citation', '')} | {link} | |")
    return "\n".join(L) + "\n"


def main():
    cards = [json.loads(p.read_text(encoding="utf-8")) for p in CARDS]
    OUT.mkdir(parents=True, exist_ok=True)
    key = {}
    a = part1(cards, "a", key)
    write_new(OUT / "reviewer_a_part1.md", a)
    write_new(OUT / "reviewer_b_part1.md", part1(cards, "b", {}))
    write_new(OUT / "part2_ambiguous_checks.md", part2(cards))
    write_new(OUT / "part3_references.md", part3(cards))
    write_new(OUT / "_key_open_after_review.json", json.dumps(key, indent=1))
    print(f"{len(cards)} seeds, {len(key)} messages per reviewer -> {OUT}")


if __name__ == "__main__":
    main()
