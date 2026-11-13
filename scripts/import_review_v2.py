"""Read a filled Part 1 review file back into the human_review slots of v2 cards.

Usage:
    python -I scripts/import_review_v2.py FILLED_part1.md --slot annotator_1 --reviewer-id NAME --date YYYY-MM-DD
           --manifest data/human_review/v2_draft/researcher_only_manifest.json
           [--cards DIR] [--out DIR | --in-place]

Writes one slot per variant: {reviewer_id, date, role, realism, licence} (spec 2.7). The cards are copied to
--out (default: a new directory next to the review file named imported_<slot>); the originals change only with
--in-place. Every item must have a role, a realism rating from 1 to 5, and a label for every unit; a missing or
invalid answer stops the import with the item code and the unit. Evidence quotes are not stored in the card.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import checks_v2 as V2  # noqa: E402

ROLE_WORDS = {"analogy": "analogy", "requirement": "requirement", "counter": "counter", "counter-example": "counter",
              "counterexample": "counter", "mixed": "mixed", "unclear": "unclear"}


def parse(text):
    """{code: {"role", "realism", "licence": {unit: label}}} from a filled Part 1 file; raises ValueError on a gap."""
    out = {}
    parts = re.split(r"^## (R\d{3})\s*$", text, flags=re.M)
    for code, body in zip(parts[1::2], parts[2::2]):
        role = re.search(r"^- Role \(.*?\):[ \t]*(.*)$", body, re.M)
        real = re.search(r"^- Realism of this complete prompt \(1-5\):[ \t]*(.*)$", body, re.M)
        w = ROLE_WORDS.get((role.group(1).strip().lower().split() or [""])[0].strip(".,;") if role else "")
        if not w:
            raise ValueError(f"{code}: role is missing or not one of {sorted(set(ROLE_WORDS.values()))}")
        m = re.match(r"\s*([1-5])\b", real.group(1) if real else "")
        if not m:
            raise ValueError(f"{code}: realism must start with a number from 1 to 5")
        lic = {}
        for u, rest in re.findall(r"^  - ((?:U\d{2})|(?:I\d+)):[ \t]*(.*)$", body, re.M):
            lab = rest.split(";")[0].strip().upper().replace(" ", "_").replace("-", "_")
            if lab not in V2.LABELS:
                raise ValueError(f"{code} unit {u}: label {rest[:30]!r} is not one of {V2.LABELS}")
            lic[u] = lab
        out[code] = {"role": w, "realism": int(m.group(1)), "licence": lic}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("review")
    ap.add_argument("--slot", required=True, choices=["annotator_1", "annotator_2"])
    ap.add_argument("--reviewer-id", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--cards", default=str(ROOT / "data/seeds_v2_draft"))
    ap.add_argument("--out")
    ap.add_argument("--in-place", action="store_true")
    a = ap.parse_args(argv)
    manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    try:
        filled = parse(Path(a.review).read_text(encoding="utf-8"))
    except ValueError as e:
        raise SystemExit(f"IMPORT ERROR: {e}")
    missing = sorted(set(manifest) - set(filled))
    if missing:
        raise SystemExit(f"IMPORT ERROR: items without a block: {missing[:5]}")
    cards = {}
    for p in sorted(Path(a.cards).glob("*.json")):
        c = json.loads(p.read_text(encoding="utf-8"))
        cards[c["id"]] = (p, c)
    for code, m in manifest.items():
        p, c = cards[m["card"]]
        v = next(x for x in c["variants"] if x["id"] == m["variant"])
        units = set(V2.unit_registry(c))
        got = filled[code]
        if set(got["licence"]) != units:
            raise SystemExit(f"IMPORT ERROR: {code} labels {sorted(units ^ set(got['licence']))} do not match the units of {c['id']}")
        slot = {"reviewer_id": a.reviewer_id, "date": a.date, **got}
        c["human_review"]["variants"][v["id"]][a.slot] = slot
        if a.reviewer_id not in [r if isinstance(r, str) else r.get("reviewer_id") for r in c["human_review"]["reviewers"]]:
            c["human_review"]["reviewers"].append(a.reviewer_id)
    out = None if a.in_place else Path(a.out or Path(a.review).parent / f"imported_{a.slot}")
    if out:
        out.mkdir(parents=True, exist_ok=True)
    for cid, (p, c) in cards.items():
        dest = p if a.in_place else out / p.name
        dest.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"imported {len(filled)} item(s) into slot {a.slot} for {len(cards)} card(s): {'in place' if a.in_place else out}")


if __name__ == "__main__":
    main()
