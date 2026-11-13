"""Export v2 seed cards as training records and dataset statistics (docs/seed-spec-v2.md Section 9).

Usage:
    python -I src/export_v2.py [DIR_OR_FILES ...] [--pool NAME] [--records out.jsonl]
                               [--stats [--out-dir DIR]] [--check-tokens TOKENIZER [TOKENIZER ...]]

  --records FILE      one JSON line per variant x turns (single, multi) x control (orig, ctrl) (spec 9.1)
  --stats             cards.csv, variants.csv, units.csv, spans.csv and summary.json (spec 9.2) in
                      results/dataset_stats/<pool>/ or in --out-dir
  --check-tokens      load only the tokenizers (no model weights, no GPU, local cache only) and report, for every
                      record, token counts, spans without a token and tokens that straddle two spans
  --pool NAME         pool name for all cards (default: the card's `split`, or "unassigned")
  --no-lint           export cards even when the draft lint reports errors (default: refuse them)

Exports of a test pool (pool name starting with "test") are never written inside this repository (spec 9).

Library:
    records = export_card(card, path)              # list of dicts
    tl = token_labels(record, tokenizer)           # input_ids, token_labels, span_token_ranges, diagnostics
    tables = stats_tables(cards_with_paths)        # the four flat tables
    summary = stats_summary(tables)

Token labels follow spec 9.1: render the chat template, locate every message content in the rendered text
(an absent content raises, nothing is guessed), tokenize with offset mappings, and give each token the label of
the span it overlaps most (ties: the earlier span). Tokens outside the example, in context spans or in UNCLEAR
units get IGNORE (-100). Span offsets in a record are relative to the message content; the rendered offset of the
content is added at training time.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import checks_v2 as V2  # noqa: E402
import seed_lint_v1 as L1  # noqa: E402
import seed_lint_v2 as L  # noqa: E402

EXPORTER_VERSION = "0.1.0"
IGNORE = -100
LABEL_ID = {"MUST": 0, "MAY": 1, "MUST_NOT": 2}


class ExportError(RuntimeError):
    pass


def card_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def pool_of(card, override=None):
    return override or card.get("split") or "unassigned"


# ---------------------------------------------------------------- records (spec 9.1)
def _span_label(card, variant, entries, unit):
    """Final label if the reviewers or an adjudication settled it, else the author's label."""
    fl = V2.final_label(card, variant["id"], unit)
    return fl if fl is not None else entries[unit]["label"]


def _example_message(turns):
    return 0 if turns == "single" else 2


def build_record(card, path, variant, turns, perturbed, pool=None, sha=None):
    messages = L1.build_messages(card, variant, turns, perturbed)
    mi = _example_message(turns)
    ex = L1.source_text(card, perturbed)
    content = messages[mi]["content"]
    if content.count(ex) != 1:
        raise ExportError(f"{card['id']} {variant['id']}: the example occurs {content.count(ex)} times in message {mi}")
    base = content.index(ex)
    spans_src = V2.control_spans(card) if perturbed else card["source_spans"]
    entries = V2.expand_licence(card, variant)[0]
    spans, pos = [], 0
    for s in spans_src:
        unit = s.get("unit")
        spans.append({"span_id": s["id"], "kind": s["kind"], "unit": unit,
                      "label": None if s["kind"] == "context" else _span_label(card, variant, entries, unit),
                      "basis": None if s["kind"] == "context" else entries[unit].get("basis"),
                      "message_index": mi, "char_start": base + pos, "char_end": base + pos + len(s["text"])})
        pos += len(s["text"])
    if spans and spans[-1]["char_end"] != base + len(ex):
        raise ExportError(f"{card['id']} {variant['id']}: spans do not tile the example")
    licence, evidence = {}, []
    resolved = V2.resolved_labels(card, variant)
    for u, e in entries.items():
        licence[u] = {"label": e["label"], "basis": e.get("basis"), "implication": e.get("implication"),
                      "proposed": e.get("proposed"), "final": V2.final_label(card, variant["id"], u)}
        if e.get("basis") in ("DIRECT", "INFERRED"):
            q = e["evidence"]
            hit = None
            for k, m in enumerate(messages):
                c = m["content"]
                es = c.find(ex) if k == mi else -1
                for i in L.occurrences(c, q):
                    if es == -1 or i + len(q) <= es or i >= es + len(ex):
                        hit = (k, i)
                        break
                if hit:
                    break
            if hit is None:
                raise ExportError(f"{card['id']} {variant['id']} {u}: evidence {q[:50]!r} has no occurrence outside the example")
            evidence.append({"unit_id": u, "quote": q, "message_index": hit[0], "char_start": hit[1], "char_end": hit[1] + len(q)})
    checks = [{"id": it["check"]["id"], "list": it["list"], "kind": it["check"]["spec"][0], "units": list(it["check"].get("units") or [])}
              for it in V2.iter_checks(card, variant)]
    rec = {
        "record_id": f"{card['id']}::{variant['id']}::{turns}::{'ctrl' if perturbed else 'orig'}",
        "card_id": card["id"], "variant_id": variant["id"], "schema": card["schema"], "exporter_version": EXPORTER_VERSION,
        "card_sha256": sha or (card_sha256(path) if path else None),
        "pool": pool_of(card, pool), "split": card.get("split"), "subset": V2.variant_subset(card, variant),
        "family": card["family"], "domain": card["domain"], "relation_family": card["relation_family"],
        "template_group_id": card["template_group_id"], "provenance_group_id": card["provenance_group_id"],
        "source_type": card["provenance"]["source_type"], "model_assistance": card["model_assistance"],
        "role": variant["role"], "role_id": V2.ROLE_ID[variant["role"]], "cue": variant["cue"], "fit": variant["fit"],
        "turns": turns, "perturbed": perturbed, "messages": messages,
        "example_location": {"message_index": mi, "char_start": base, "char_end": base + len(ex)},
        "spans": spans, "licence": licence, "evidence": evidence, "checks": checks,
        "valid_answers": [{"id": a["id"], "text": a["text"]} for a in variant["valid_answers"]],
        "invalid_answers": [{"id": a["id"], "text": a["text"], "kind": a["kind"], "pair_of": a.get("pair_of"),
                             "violates": a.get("violates"), "fails": a["fails"]} for a in variant["invalid_answers"]],
        "siblings": siblings(card, variant, turns, perturbed),
    }
    del resolved
    return rec


def siblings(card, variant, turns, perturbed):
    """Other variants of the card (spec 9.1). `should_change` pairs feed RS; the control pair feeds INV."""
    out = []
    mine = V2.resolved_labels(card, variant)
    my_rules = {r["id"] for r in variant.get("rules_add", []) or []}
    my_prov = bool(V2.unresolved_units(card, variant))
    for w in card["variants"]:
        if w["id"] == variant["id"]:
            continue
        theirs = V2.resolved_labels(card, w)
        changed_units = sorted(u for u in mine if mine[u] != theirs.get(u))
        their_rules = {r["id"] for r in w.get("rules_add", []) or []}
        changed_rules = sorted(my_rules ^ their_rules)
        out.append({"variant_id": w["id"], "relation": "should_not_change" if not changed_units and not changed_rules else "should_change",
                    "changed_units": changed_units, "changed_rules": changed_rules,
                    "provisional": my_prov or bool(V2.unresolved_units(card, w))})
    if not perturbed and V2.control_applies(card, variant):
        out.append({"variant_id": variant["id"], "perturbed": True, "relation": "should_not_change", "changed_units": [], "changed_rules": []})
    return out


def export_card(card, path=None, pool=None):
    """All training records of one card, in a fixed order: variants, single before multi, orig before ctrl."""
    sha = card_sha256(path) if path else None
    out = []
    for v in card["variants"]:
        ctrl = V2.control_applies(card, v)
        for turns in ("single", "multi"):
            for perturbed in (False, True) if ctrl else (False,):
                out.append(build_record(card, path, v, turns, perturbed, pool, sha))
    return out


# ---------------------------------------------------------------- token labels (spec 9.1, steps 1 to 7)
def tokenizer_info(tok):
    return {"name": getattr(tok, "name_or_path", "?"), "revision": getattr(tok, "init_kwargs", {}).get("revision") or "local-cache"}


def locate_messages(rendered, messages):
    """Offset of every message content in the rendered chat text, searched in order. Raises if one is absent."""
    pos, offs = 0, []
    for i, m in enumerate(messages):
        j = rendered.find(m["content"], pos)
        if j == -1:
            raise ExportError(f"message {i} ({m['role']}) content is not found verbatim in the rendered chat template")
        offs.append(j)
        pos = j + len(m["content"])
    return offs


def token_labels(record, tokenizer, context_as_may=False, template_kw=None):
    """Token-level labels for one record and one tokenizer.

    Returns {input_ids, token_labels, span_token_ranges, tokenizer, diagnostics}. span_token_ranges[span_id] is
    [first, last + 1] over the tokens that overlap the span at all (empty list if none). diagnostics counts the
    tokens that overlap two or more spans (straddling), how many of those get a label different from one of
    the spans they touch, ties, and the licensed spans that received no label.
    """
    rendered = tokenizer.apply_chat_template(record["messages"], tokenize=False, add_generation_prompt=True, **(template_kw or {}))
    offs = locate_messages(rendered, record["messages"])
    enc = tokenizer(rendered, add_special_tokens=False, return_offsets_mapping=True)
    ids, mapping = enc["input_ids"], enc["offset_mapping"]
    abs_spans = []
    for s in record["spans"]:
        a = offs[s["message_index"]] + s["char_start"]
        abs_spans.append((a, a + (s["char_end"] - s["char_start"]), s))
    labels, ranges = [], {}
    diag = {"tokens": len(ids), "straddling": 0, "straddling_different_label": 0, "straddling_licensed_conflict": 0, "ties": 0, "straddling_example_edge": 0,
            "licensed_spans_without_overlapping_token": [], "licensed_spans_without_labelled_token": []}
    labelled = set()
    ex_a = offs[record["example_location"]["message_index"]] + record["example_location"]["char_start"]
    ex_b = ex_a + (record["example_location"]["char_end"] - record["example_location"]["char_start"])
    for t, (a, b) in enumerate(mapping):
        ov = []
        for k, (sa, sb, s) in enumerate(abs_spans):
            o = min(b, sb) - max(a, sa)
            if o > 0:
                ov.append((o, k))
        for o, k in ov:
            sid = abs_spans[k][2]["span_id"]
            lo, hi = ranges.get(sid, [t, t + 1])
            ranges[sid] = [min(lo, t), max(hi, t + 1)]
        if b > a and ((a < ex_a < b) or (a < ex_b < b)):
            diag["straddling_example_edge"] += 1
        if not ov:
            labels.append(IGNORE)
            continue
        best = max(o for o, _ in ov)
        winners = [k for o, k in ov if o == best]
        k = min(winners)
        if len(ov) > 1:
            diag["straddling"] += 1
            if len({abs_spans[x][2]["label"] for _, x in ov}) > 1:
                diag["straddling_different_label"] += 1
            if len({abs_spans[x][2]["label"] for _, x in ov if abs_spans[x][2]["kind"] != "context"}) > 1:
                diag["straddling_licensed_conflict"] += 1   # two licensed spans with different labels share this token
        if len(winners) > 1:
            diag["ties"] += 1
        s = abs_spans[k][2]
        if s["kind"] == "context":
            labels.append(LABEL_ID["MAY"] if context_as_may else IGNORE)
        elif s["label"] in LABEL_ID:
            labels.append(LABEL_ID[s["label"]])
            labelled.add(s["span_id"])
        else:
            labels.append(IGNORE)   # UNCLEAR
    for _, _, s in abs_spans:
        if s["kind"] != "context" and s["label"] in LABEL_ID:
            if s["span_id"] not in ranges:
                diag["licensed_spans_without_overlapping_token"].append(s["span_id"])
            if s["span_id"] not in labelled:
                diag["licensed_spans_without_labelled_token"].append(s["span_id"])
    return {"input_ids": ids, "token_labels": labels, "span_token_ranges": {k: v for k, v in ranges.items()},
            "tokenizer": tokenizer_info(tokenizer), "diagnostics": diag}


# ---------------------------------------------------------------- statistics (spec 9.2)
CARD_COLS = ["pool", "card_id", "family", "domain", "relation_family", "source_type", "model_assistance", "author_id",
             "template_group_id", "provenance_group_id", "split", "status", "length", "example_chars", "example_sentences",
             "n_variants", "n_spans", "n_relation_spans", "n_detail_spans", "n_context_spans", "n_relation_units",
             "n_detail_units", "has_control"]
VARIANT_COLS = ["pool", "card_id", "variant_id", "role", "cue", "fit", "family", "domain", "relation_family", "source_type",
                "subset", "n_must", "n_may", "n_must_not", "n_unclear", "n_direct", "n_inferred", "n_default", "n_rule_checks",
                "n_must_transfer", "n_must_not_transfer", "n_judge", "n_probes", "n_valid", "n_invalid_minimal", "n_copy",
                "prompt_chars_single", "control_applies"]
UNIT_COLS = ["pool", "card_id", "variant_id", "unit_id", "unit_kind", "main", "n_spans", "chars", "label", "basis", "implication",
             "proposed", "final_label", "n_checks", "role", "cue", "fit", "family", "subset"]
SPAN_COLS = ["pool", "card_id", "span_id", "position", "kind", "unit", "chars", "words", "in_code"]


def stats_tables(cards, pool=None):
    """cards = list of (path, card). Returns {"cards": rows, "variants": rows, "units": rows, "spans": rows} (lists of dicts)."""
    T = {"cards": [], "variants": [], "units": [], "spans": []}
    for _, c in cards:
        pl = pool_of(c, pool)
        se = c["source_example"]
        spans = c["source_spans"]
        reg = V2.unit_registry(c)
        kinds = [s["kind"] for s in spans]
        T["cards"].append({
            "pool": pl, "card_id": c["id"], "family": c["family"], "domain": c["domain"], "relation_family": c["relation_family"],
            "source_type": c["provenance"]["source_type"], "model_assistance": c["model_assistance"], "author_id": c["author_id"],
            "template_group_id": c["template_group_id"], "provenance_group_id": c["provenance_group_id"], "split": c.get("split") or "",
            "status": c["status"], "length": se["length"], "example_chars": len(se["text"]),
            "example_sentences": L1.count_sentences(se["text"]), "n_variants": len(c["variants"]), "n_spans": len(spans),
            "n_relation_spans": kinds.count("relation"), "n_detail_spans": kinds.count("detail"), "n_context_spans": kinds.count("context"),
            "n_relation_units": sum(1 for i in reg.values() if i["kind"] == "relation"),
            "n_detail_units": sum(1 for i in reg.values() if i["kind"] == "detail"),
            "has_control": any(d.get("control") for d in se["incidental_details"])})
        pos = 0
        for i, s in enumerate(spans):
            before = se["text"][:pos]
            in_code = before.count("```") % 2 == 1   # the span starts inside a fenced code block
            T["spans"].append({"pool": pl, "card_id": c["id"], "span_id": s["id"], "position": i, "kind": s["kind"],
                               "unit": s.get("unit") or "", "chars": len(s["text"]), "words": len(s["text"].split()), "in_code": in_code})
            pos += len(s["text"])
        for v in c["variants"]:
            entries = V2.expand_licence(c, v)[0]
            items = V2.iter_checks(c, v)
            lab = lambda x: sum(1 for e in entries.values() if e.get("label") == x)
            bas = lambda x: sum(1 for e in entries.values() if e.get("basis") == x)
            T["variants"].append({
                "pool": pl, "card_id": c["id"], "variant_id": v["id"], "role": v["role"], "cue": v["cue"], "fit": v["fit"],
                "family": c["family"], "domain": c["domain"], "relation_family": c["relation_family"],
                "source_type": c["provenance"]["source_type"], "subset": V2.variant_subset(c, v),
                "n_must": lab("MUST"), "n_may": lab("MAY"), "n_must_not": lab("MUST_NOT"), "n_unclear": lab("UNCLEAR"),
                "n_direct": bas("DIRECT"), "n_inferred": bas("INFERRED"), "n_default": bas("DEFAULT"),
                "n_rule_checks": sum(1 for it in items if it["list"] == "rule"),
                "n_must_transfer": sum(1 for it in items if it["list"] == "must_transfer"),
                "n_must_not_transfer": sum(1 for it in items if it["list"] == "must_not_transfer"),
                "n_judge": sum(1 for it in items if V2.is_judge(it["check"])),
                "n_probes": sum(1 for it in items if it["list"] == "probe"),
                "n_valid": len(v["valid_answers"]),
                "n_invalid_minimal": sum(1 for a in v["invalid_answers"] if a["kind"] == "minimal"),
                "n_copy": sum(1 for a in v["invalid_answers"] if a["kind"] == "copy"),
                "prompt_chars_single": len(L1.prompt_text(c, v)), "control_applies": V2.control_applies(c, v)})
            for u, info in reg.items():
                e = entries.get(u, {})
                mine = [s for s in spans if s.get("unit") == u]
                T["units"].append({
                    "pool": pl, "card_id": c["id"], "variant_id": v["id"], "unit_id": u, "unit_kind": info["kind"],
                    "main": info["main"], "n_spans": len(mine), "chars": sum(len(s["text"]) for s in mine),
                    "label": e.get("label", ""), "basis": e.get("basis", ""), "implication": e.get("implication") or "",
                    "proposed": e.get("proposed") or "", "final_label": V2.final_label(c, v["id"], u) or "",
                    "n_checks": sum(1 for it in items if u in (it["check"].get("units") or [])),
                    "role": v["role"], "cue": v["cue"], "fit": v["fit"], "family": c["family"], "subset": V2.variant_subset(c, v)})
    return T


def _r(x):
    return round(x, 4) if isinstance(x, float) else x


def _p90(xs):
    xs = sorted(xs)
    return xs[max(0, -(-9 * len(xs) // 10) - 1)] if xs else 0   # nearest rank


def _num(xs, with_p90=False, with_minmax=True):
    out = {"mean": _r(statistics.fmean(xs)) if xs else 0, "median": _r(statistics.median(xs)) if xs else 0}
    if with_minmax:
        out.update({"min": min(xs) if xs else 0, "max": max(xs) if xs else 0})
    if with_p90:
        out = {"mean": out["mean"], "median": out["median"], "p90": _p90(xs), "max": max(xs) if xs else 0}
    return out


def stats_summary(T):
    """summary.json of spec 9.2 from the four tables."""
    V, U, S, Cd = T["variants"], T["units"], T["spans"], T["cards"]
    total = len(V) or 1

    card_row = {c["card_id"]: c for c in Cd}

    def by(cols):
        # variants.csv has no model_assistance column (spec 9.2 lists it as a source anyway): take it from cards.csv
        groups = {}
        for r in V:
            groups.setdefault(tuple(r[c] if c in r else card_row[r["card_id"]][c] for c in cols), []).append(r)
        return [dict(zip(cols, k), n_cards=len({r["card_id"] for r in rs}), n_variants=len(rs), share=_r(len(rs) / total))
                for k, rs in sorted(groups.items(), key=lambda kv: tuple(str(x) for x in kv[0]))]

    out = {f"by_{c}": by([c]) for c in ("family", "role", "cue", "fit", "source_type", "domain", "relation_family", "model_assistance", "subset")}
    out["role_x_cue_x_fit"] = by(["role", "cue", "fit"])

    def count_share(rows, keys, within):
        groups, base = {}, {}
        for r in rows:
            groups[tuple(r[k] for k in keys)] = groups.get(tuple(r[k] for k in keys), 0) + 1
            base[tuple(r[k] for k in within)] = base.get(tuple(r[k] for k in within), 0) + 1
        return [dict(zip(keys, k), n_units=n, share=_r(n / base[tuple(dict(zip(keys, k))[w] for w in within)]))
                for k, n in sorted(groups.items(), key=lambda kv: tuple(str(x) for x in kv[0]))]

    out["licence_label_by_role_kind"] = count_share(U, ["role", "unit_kind", "label"], ["role", "unit_kind"])
    out["basis_by_label"] = count_share(U, ["label", "basis"], ["label"])
    ur = {}
    for r in U:
        k = (r["role"], r["cue"])
        a, b = ur.get(k, (0, 0))
        ur[k] = (a + 1, b + (r["label"] == "UNCLEAR"))
    out["unclear_rate"] = [{"role": k[0], "cue": k[1], "n_units": n, "n_unclear": m, "rate": _r(m / n)} for k, (n, m) in sorted(ur.items())]
    out["spans_per_card"] = []
    out["span_chars"] = []
    for kind in ("relation", "detail", "context"):
        per_card = [sum(1 for s in S if s["card_id"] == c["card_id"] and s["kind"] == kind) for c in Cd]
        out["spans_per_card"].append({"kind": kind, **_num(per_card)})
        out["span_chars"].append({"kind": kind, **_num([s["chars"] for s in S if s["kind"] == kind], with_p90=True)})
    out["units_per_card"] = [{"unit_kind": "relation", **_num([c["n_relation_units"] for c in Cd])},
                             {"unit_kind": "detail", **_num([c["n_detail_units"] for c in Cd])}]
    out["checks_per_variant"] = [{"check_list": name, **_num([r[col] for r in V], with_minmax=False)} for name, col in
                                 (("rule", "n_rule_checks"), ("must_transfer", "n_must_transfer"),
                                  ("must_not_transfer", "n_must_not_transfer"), ("probe", "n_probes"), ("judge", "n_judge"))]
    out["answers_per_variant"] = [{"answer_kind": name, "mean": _r(statistics.fmean([r[col] for r in V])) if V else 0,
                                   "min": min([r[col] for r in V]) if V else 0}
                                  for name, col in (("valid", "n_valid"), ("invalid_minimal", "n_invalid_minimal"), ("copy", "n_copy"))]
    out["example_length"] = []
    for ln in sorted({c["length"] for c in Cd}):
        cs = [c for c in Cd if c["length"] == ln]
        out["example_length"].append({"length": ln, "n_cards": len(cs),
                                      "chars_mean": _r(statistics.fmean([c["example_chars"] for c in cs])),
                                      "chars_median": _r(statistics.median([c["example_chars"] for c in cs])),
                                      "sentences_mean": _r(statistics.fmean([c["example_sentences"] for c in cs])),
                                      "sentences_median": _r(statistics.median([c["example_sentences"] for c in cs]))})
    return out


def write_stats(T, summary, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, cols in (("cards", CARD_COLS), ("variants", VARIANT_COLS), ("units", UNIT_COLS), ("spans", SPAN_COLS)):
        with open(os.path.join(out_dir, name + ".csv"), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            w.writerows(T[name])
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------- CLI
def inside_repo(path):
    p = os.path.abspath(path)
    return p == ROOT or p.startswith(ROOT + os.sep)


def guard_private(pool, path):
    if str(pool).startswith("test") and inside_repo(path):
        raise ExportError(f"pool {pool!r} is a test pool: its export must not be written inside the public repository ({path})")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", default=[os.path.join(ROOT, "data", "seeds_v2_draft")])
    ap.add_argument("--pool")
    ap.add_argument("--records")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--out-dir")
    ap.add_argument("--check-tokens", nargs="+", metavar="TOKENIZER")
    ap.add_argument("--no-lint", action="store_true")
    a = ap.parse_args(argv)
    files, cards = L.load(a.paths)
    good = []
    for f, c in zip(files, cards):
        if "__load_error__" in c:
            print(f"SKIP {f}: {c['__load_error__']}")
            return 1
        if not a.no_lint:
            rep = L.lint_card(c, gold=False, path=f)
            if rep.count("ERROR"):
                print(f"REFUSED {c.get('id', f)}: {rep.count('ERROR')} lint error(s); first: {L.fmt([i for i in rep.items if i['level'] == 'ERROR'][0])}")
                return 1
        good.append((f, c))
    pools = sorted({pool_of(c, a.pool) for _, c in good})
    records = [r for f, c in good for r in export_card(c, f, a.pool)]
    print(f"{len(good)} card(s), {len(records)} record(s), pools {pools}")
    if a.records:
        for p in pools:
            guard_private(p, a.records)
        with open(a.records, "w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
        print(f"wrote {a.records}")
    if a.stats:
        for p in pools:
            cs = [(f, c) for f, c in good if pool_of(c, a.pool) == p]
            out = a.out_dir or os.path.join(ROOT, "results", "dataset_stats", p)
            guard_private(p, out)
            T = stats_tables(cs, a.pool)
            write_stats(T, stats_summary(T), out)
            print(f"wrote statistics for pool {p}: {out} ({len(T['cards'])} cards, {len(T['variants'])} variants, "
                  f"{len(T['units'])} unit rows, {len(T['spans'])} span rows)")
    if a.check_tokens:
        from transformers import AutoTokenizer
        for name in a.check_tokens:
            tok = AutoTokenizer.from_pretrained(name, local_files_only=True)
            tot = {"records": 0, "tokens": 0, "straddling": 0, "straddling_different_label": 0, "straddling_licensed_conflict": 0, "ties": 0, "no_overlap": 0, "no_label": 0}
            for r in records:
                d = token_labels(r, tok)["diagnostics"]
                tot["records"] += 1
                tot["tokens"] += d["tokens"]
                for k in ("straddling", "straddling_different_label", "straddling_licensed_conflict", "ties"):
                    tot[k] += d[k]
                tot["no_overlap"] += len(d["licensed_spans_without_overlapping_token"])
                tot["no_label"] += len(d["licensed_spans_without_labelled_token"])
            print(f"{name}: {tot}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ExportError as e:
        print(f"EXPORT ERROR: {e}")
        sys.exit(1)
