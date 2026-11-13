"""Turn authoring markup into `source_spans` for a v2 seed card (docs/seed-spec-v2.md Section 10, step 3).

Markup: [[U01|text]] is a relation span of unit U01, [[I3|text]] is a detail span of detail I3, and everything
outside brackets is context. The first `|` separates the unit id from the text. Nesting is not allowed. If the
example itself contains `[[` or `]]`, write source_spans by hand.

Usage:
    python -I scripts/spans_from_markup.py MARKUP.txt --card CARD.json [-o spans.json] [--update-card] [--set-text]

  MARKUP.txt      the example with markup ('-' reads standard input)
  --card          a card JSON that already lists relation_units and source_example.incidental_details
                  (the detectors decide the detail spans, so choose them first)
  -o FILE         write the span list as JSON (default: print it)
  --update-card   write source_spans into the card file
  --set-text      also set source_example.text from the markup (otherwise the markup must reproduce the
                  card's existing text exactly, rule S1)

The tool prints one line per span and exits with 1 if S1, S2, S3, S4, S5, S6 or S7 break (the span rules of
seed_lint_v2, run on the new spans). Span ids are S01, S02, ... in order.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import seed_lint_v2 as L  # noqa: E402

TAG = re.compile(r"\[\[([UI]\d+)\|(.*?)\]\]", re.S)


def parse_markup(markup):
    """Return (spans, plain_text). Raises ValueError on stray or nested brackets."""
    spans, pos, plain = [], 0, []
    for m in TAG.finditer(markup):
        gap = markup[pos:m.start()]
        if gap:
            spans.append({"text": gap, "kind": "context"})
        uid, text = m.group(1), m.group(2)
        if "[[" in text:
            raise ValueError(f"nested markup inside [[{uid}|...]] at character {m.start()}")
        spans.append({"text": text, "kind": "relation" if uid.startswith("U") else "detail", "unit": uid})
        pos = m.end()
    tail = markup[pos:]
    if tail:
        spans.append({"text": tail, "kind": "context"})
    for s in spans:
        if s["kind"] == "context" and ("[[" in s["text"] or "]]" in s["text"]):
            raise ValueError(f"unmatched bracket markup in context text {s['text'][:40]!r} (a tag needs the form [[U01|text]])")
    out = []
    for i, s in enumerate(spans, 1):
        out.append({"id": f"S{i:02d}" if i < 100 else f"S{i}", "text": s["text"], "kind": s["kind"], **({"unit": s["unit"]} if "unit" in s else {})})
        plain.append(s["text"])
    return out, "".join(plain)


def check_spans(card, spans, text):
    """Run S1 to S7 (and the S9 warning) of seed_lint_v2 on a card stub that carries the new spans."""
    stub = {"source_example": dict(card["source_example"], text=text), "source_spans": spans,
            "relation_units": card["relation_units"], "variants": []}
    rep = L.Report(card.get("id", "?"))
    L.lint_spans(rep, stub, core_only=True)
    return [it for it in rep.items if it["rule"] in ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S9")]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("markup")
    ap.add_argument("--card", required=True)
    ap.add_argument("-o", "--out")
    ap.add_argument("--update-card", action="store_true")
    ap.add_argument("--set-text", action="store_true")
    a = ap.parse_args(argv)
    markup = sys.stdin.read() if a.markup == "-" else open(a.markup, encoding="utf-8").read()
    if markup.endswith("\n") and not a.set_text:
        # editors add a final newline that is not part of the example; keep it only if the card's text has it
        with open(a.card, encoding="utf-8") as f:
            existing = json.load(f).get("source_example", {}).get("text", "")
        if not existing.endswith("\n"):
            markup = markup.rstrip("\n")
    with open(a.card, encoding="utf-8") as f:
        card = json.load(f)
    try:
        spans, plain = parse_markup(markup)
    except ValueError as e:
        print(f"ERROR markup: {e}")
        return 1
    existing = card.get("source_example", {}).get("text")
    text = plain if (a.set_text or not existing) else existing
    for s in spans:
        print(f"{s['id']} {s['kind']:8s} {s.get('unit', ''):4s} {s['text']!r}")
    items = check_spans(card, spans, text)
    for it in items:
        print(L.fmt(it))
    bad = [it for it in items if it["level"] == "ERROR"]
    print(f"{len(spans)} span(s), {len(plain)} characters, {len(bad)} error(s)")
    if bad:
        return 1
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(spans, f, indent=1, ensure_ascii=False)
            f.write("\n")
    if a.update_card:
        card["source_spans"] = spans
        if a.set_text:
            card["source_example"]["text"] = plain
        with open(a.card, "w", encoding="utf-8") as f:
            json.dump(card, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"wrote source_spans to {a.card}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
