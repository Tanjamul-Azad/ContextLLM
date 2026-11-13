"""Print the expanded licence of v2 seed cards: units as rows, variants as columns (spec Section 10, step 8).

Usage:
    python -I scripts/licence_table.py [CARD.json | DIR ...] [--md] [--csv] [--evidence]

Default path: data/seeds_v2_draft/. One table per card. A cell is LABEL/BASIS with LABEL in MUST, MAY, NOT
(MUST_NOT) or ?X (UNCLEAR, X = the proposed label) and BASIS in D (DIRECT), I (INFERRED), - (DEFAULT).
A trailing * marks a licence that came from `defaults`. The last rows show the subset (core or ambiguity)
and the number of units per label. --md writes a Markdown table, --csv a CSV file, --evidence lists the
evidence quote and note of every entry below the table.
"""
import argparse
import csv
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
import checks_v2 as V2  # noqa: E402

SHORT = {"MUST": "MUST", "MAY": "MAY", "MUST_NOT": "NOT"}
BASIS = {"DIRECT": "D", "INFERRED": "I", "DEFAULT": "-"}


def cell(e):
    lab = e.get("label")
    txt = f"?{SHORT.get(e.get('proposed'), '?')}" if lab == "UNCLEAR" else SHORT.get(lab, str(lab))
    return f"{txt}/{BASIS.get(e.get('basis'), '?')}" + ("*" if e.get("_default") else "")


def table(card):
    """Return (header, rows, footer_rows, notes). Rows are lists of strings."""
    reg = V2.unit_registry(card)
    variants = card["variants"]
    header = ["unit", "kind", "what"] + [v["id"] for v in variants]
    expanded = {v["id"]: V2.expand_licence(card, v)[0] for v in variants}
    rows, notes = [], []
    for u, info in reg.items():
        what = info["text"] if len(info["text"]) <= 60 else info["text"][:57] + "..."
        rows.append([u, info["kind"], what] + [cell(expanded[v["id"]][u]) if u in expanded[v["id"]] else "(none)" for v in variants])
        for v in variants:
            e = expanded[v["id"]].get(u)
            if e and (e.get("evidence") or e.get("note")):
                notes.append(f"{u} in {v['id']}: " + (f"evidence {e['evidence']!r} " if e.get("evidence") else "")
                             + (f"[{e['implication']}] " if e.get("implication") else "") + (f"note: {e['note']}" if e.get("note") else ""))
    foot = [["subset", "", ""] + [V2.variant_subset(card, v) for v in variants]]
    for lab in ("MUST", "MAY", "MUST_NOT", "UNCLEAR"):
        foot.append([f"n {lab}", "", ""] + [str(sum(1 for e in expanded[v["id"]].values() if e.get("label") == lab)) for v in variants])
    return header, rows, foot, notes


def render_text(card, evidence):
    header, rows, foot, notes = table(card)
    allrows = [header] + rows + foot
    widths = [max(len(r[i]) for r in allrows) for i in range(len(header))]
    lines = [f"== {card['id']}  ({len(card['variants'])} variants, {len(rows)} units)"]
    for i, r in enumerate(allrows):
        lines.append("  ".join(x.ljust(w) for x, w in zip(r, widths)).rstrip())
        if i == 0 or i == len(rows):
            lines.append("  ".join("-" * w for w in widths))
    if evidence:
        lines += [""] + notes
    return "\n".join(lines)


def render_md(card, evidence):
    header, rows, foot, notes = table(card)
    esc = lambda x: x.replace("|", "\\|")
    lines = [f"### {card['id']}", "", "| " + " | ".join(esc(h) for h in header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(esc(x) for x in r) + " |" for r in rows + foot]
    if evidence:
        lines += [""] + [f"- {esc(n)}" for n in notes]
    return "\n".join(lines) + "\n"


def render_csv(card, evidence):
    header, rows, foot, _ = table(card)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["card"] + header)
    for r in rows + foot:
        w.writerow([card["id"]] + r)
    return buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", default=[os.path.join(ROOT, "data", "seeds_v2_draft")])
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--csv", action="store_true")
    ap.add_argument("--evidence", action="store_true")
    a = ap.parse_args(argv)
    files = []
    for p in a.paths:
        files += sorted(glob.glob(os.path.join(p, "*.json"))) if os.path.isdir(p) else [p]
    render = render_csv if a.csv else render_md if a.md else render_text
    for f in files:
        with open(f, encoding="utf-8") as fh:
            card = json.load(fh)
        print(render(card, a.evidence))
    return 0


if __name__ == "__main__":
    sys.exit(main())
