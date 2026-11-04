"""Lint v1 seed cards against the machine-checkable rules of docs/paper-protocol.md section 3.

Usage:
    python -I src/seed_lint_v1.py [DIR_OR_FILES ...] [--release] [--no-gold]

Default directory: data/seeds_v1_draft/. Exit code 1 if any ERROR is found.

Levels:
  ERROR    a rule is broken; the card cannot be used.
  WARN     probably a problem; a person should look.
  PENDING  a rule that only humans can settle (realism, scope agreement,
           adjudication of ambiguous implied checks). PENDING is allowed in
           draft mode and becomes ERROR with --release.

The full field list and the rule-to-field map are in docs/seed-spec-v1.md.
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checks as C  # noqa: E402
import checks_v1 as V  # noqa: E402

DRAFT_STATUS = "draft — needs two human annotators before use"
ROLES = ["analogy", "requirement", "counter"]
CUES = ["stated", "implied"]
FITS = ["full", "partial", "wrong"]
FAMILIES = ["decision", "code"]
SOURCE_TYPES = [
    "real_request_paraphrased",   # WildChat / OASST2
    "documented_case",            # business, engineering, science, policy
    "software_practice",          # documented real software practice or incident
    "supernatural_instructions",
    "analogy_dataset",            # AnaloBench, ParallelPARC, ARN
    "lost_in_conversation",
    "fresh_after_cutoff",
]
ROLE_IMPLICATIONS = {
    "analogy": {"relation_transfer", "source_specific_fact"},
    "requirement": {"named_part_transfer", "source_specific_fact"},
    "counter": {"avoid_flagged_feature", "source_specific_fact"},
}
# Phrases that state the role outright. Implied-cue text must contain none;
# stated-cue text must contain at least one phrase for its own role.
CUE_PHRASES = {
    "analogy": ["borrow the idea", "the idea", "the principle", "in the same spirit", "inspiration",
                "not the details", "not its details", "adapt"],
    "requirement": ["must use", "must follow", "must keep", "exactly", "the same", "follow the",
                    "keep the", "copy the", "use the same"],
    "counter": ["don't", "do not", "avoid", "not like this", "instead of"],
}
IMPLIED_BANNED = ["borrow the idea", "in the same spirit", "for inspiration", "don't do it like", "do not do it like",
                  "avoid", "take only", "do not copy", "don't copy", "must use the same", "follow it exactly",
                  "as an analogy", "as a requirement", "counter-example", "bad example", "what not to do"]
NUM_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
             "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
             "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
             "half": 0.5, "double": 2, "twice": 2}
HUMAN_FIELDS = ("realism", "scope_agreement")


# ---------------------------------------------------------------- helpers
def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def prose(text):
    """Source text without fenced code blocks."""
    return re.sub(r"```.*?```", " ", text, flags=re.S)


def count_sentences(text):
    parts = re.split(r"(?<=[.!?])[\"')\]]?\s+(?=[\"'(\[]?[A-Z0-9])", prose(text).strip())
    return sum(1 for p in parts if len(p.split()) >= 3)


def numbers_in(text):
    t = norm(text)
    found = {float(x.replace(",", "")) for x in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", t)}
    for w, n in NUM_WORDS.items():
        if re.search(r"\b" + w + r"\b", t):
            found.add(float(n))
    return found


def source_text(card, perturbed=False):
    t = card["source_example"]["text"]
    if perturbed:
        for d in card["source_example"]["incidental_details"]:
            c = d.get("control")
            if c:
                t = t.replace(c["from"], c["to"])
    return t


def rules_for(card, variant):
    return list(card["target"]["rules"]) + list(variant.get("rules_add", []) if variant else [])


def target_text(card, variant=None):
    return card["target"]["task"] + "\n" + " ".join(r["text"] for r in rules_for(card, variant))


def build_messages(card, variant, turns="single", perturbed=False):
    """Prompt for one variant. Multi-turn carries the same information as single-turn."""
    head = card["target"]["task"] + "\nRules: " + " ".join(r["text"] for r in rules_for(card, variant))
    fmt = card["target"]["format"]
    if variant is None:
        return [{"role": "user", "content": f"{head}\n\n{fmt}"}]
    ex = variant["text"].replace("{EX}", source_text(card, perturbed))
    if turns == "single":
        return [{"role": "user", "content": f"{head}\n\n{ex}\n\n{fmt}"}]
    return [
        {"role": "user", "content": f"{head}\n\n{fmt}"},
        {"role": "assistant", "content": "Understood. Is there anything else I should take into account before I give the final answer?"},
        {"role": "user", "content": f"{ex}\n\nNow give the final answer in the format I asked for."},
    ]


def prompt_text(card, variant, perturbed=False):
    return build_messages(card, variant, "single", perturbed)[0]["content"]


class Report:
    def __init__(self, sid):
        self.sid, self.items = sid, []

    def add(self, level, msg):
        self.items.append((level, msg))

    def count(self, level):
        return sum(1 for lv, _ in self.items if lv == level)


# ---------------------------------------------------------------- check-level lint
def lint_check(rep, card, variant, chk, where, rule=None):
    """Rule: every check matches something the prompt states or the role implies (pilot P5)."""
    cid = chk.get("id", "?")
    spec = chk.get("spec")
    if not isinstance(spec, list) or not spec:
        rep.add("ERROR", f"{where} {cid}: missing spec")
        return
    kind = spec[0]
    known = kind in V.NEW_KINDS or kind in KNOWN_PILOT_KINDS
    if not known:
        rep.add("ERROR", f"{where} {cid}: unknown check kind {kind}")
        return
    basis = chk.get("basis") or ({"type": "target_rule", "rule": rule["id"]} if rule else None)
    if not basis:
        rep.add("ERROR", f"{where} {cid}: no basis (stated / target_rule / role_implied)")
        return
    btype = basis.get("type")
    full_prompt = prompt_text(card, variant) if variant else target_text(card) + "\n" + card["source_example"]["text"]
    if btype == "stated":
        q = basis.get("quote", "")
        if not q or norm(q) not in norm(full_prompt):
            rep.add("ERROR", f"{where} {cid}: stated quote not found in the prompt: {q[:60]!r}")
        ref_text = q
    elif btype == "target_rule":
        rid = basis.get("rule") or (rule and rule["id"])
        rr = {r["id"]: r for r in rules_for(card, variant)}
        if rid not in rr:
            rep.add("ERROR", f"{where} {cid}: basis rule {rid} not in the target rules for this variant")
            return
        ref_text = rr[rid]["text"]
    elif btype == "role_implied":
        role = variant["role"] if variant else None
        imp = basis.get("implication")
        if role is None or imp not in ROLE_IMPLICATIONS.get(role, ()):
            rep.add("ERROR", f"{where} {cid}: implication {imp!r} is not allowed for role {role}")
        q = basis.get("quote")
        if q and norm(q) not in norm(full_prompt):
            rep.add("ERROR", f"{where} {cid}: role_implied quote not found in the prompt: {q[:60]!r}")
        if variant and variant["cue"] == "implied":
            amb = basis.get("ambiguity")
            if amb not in ("clear", "ambiguous"):
                rep.add("ERROR", f"{where} {cid}: implied-cue check needs ambiguity clear/ambiguous (pilot P1)")
            elif amb == "ambiguous":
                done = [a for a in card.get("human_review", {}).get("adjudications", [])
                        if a.get("variant") == variant["id"] and a.get("check") == cid and a.get("decision")]
                if not done:
                    rep.add("PENDING", f"{where} {cid}: ambiguous implied check needs two-annotator adjudication before scoring (pilot P1)")
        ref_text = q or ""
    else:
        rep.add("ERROR", f"{where} {cid}: unknown basis type {btype!r}")
        return

    # numeric bounds must come from the instruction text (P5: prompt said ten words, check allowed eight)
    if kind in V.BOUND_ARGS:
        have = numbers_in(ref_text)
        for i in V.BOUND_ARGS[kind]:
            if i >= len(spec):
                continue
            vals = spec[i] if isinstance(spec[i], list) else [spec[i]]
            for v in vals:
                if not C.is_num(v):
                    continue
                if kind == "json_len_between" and i == 2 and v <= 1:
                    continue  # a lower bound of 0 or 1 is not a tightening
                if float(v) not in have:
                    rep.add("ERROR", f"{where} {cid}: bound {v} in {kind} does not appear in its basis text "
                                     f"({btype}); check may be stricter than the instruction (pilot P5)")
    # banned / required words must be mentioned somewhere in the prompt
    if kind in V.TERM_ARGS:
        terms = spec[V.TERM_ARGS[kind]]
        missing = [t for t in terms if norm(t) not in norm(full_prompt)]
        if missing:
            rep.add("ERROR", f"{where} {cid}: terms never mentioned in the prompt: {missing[:5]} (hidden ban or requirement)")
    if kind in V.REGEX_ARGS:
        if not re.search(spec[V.REGEX_ARGS[kind]], full_prompt, re.I):
            rep.add("ERROR", f"{where} {cid}: regex matches nothing in the prompt (hidden ban or requirement)")
    if kind == "leak_absent":
        lint_leak(rep, card, variant, cid, spec[1], where)
    if kind == "py_test":
        if spec[1] not in card.get("tests", {}):
            rep.add("ERROR", f"{where} {cid}: test {spec[1]} not defined")


KNOWN_PILOT_KINDS = {
    "text_absent", "text_present", "regex_absent", "regex_present", "py_test", "json_len_between",
    "json_all_int", "json_all_num", "json_all_le", "json_increasing", "json_eq", "json_is_bool",
    "json_all_word", "json_any_word", "json_no_word", "json_count_in_lt", "json_all_words_le",
    "json_all_nonempty", "json_exists_item", "json_not_exists_item", "json_first_item_word",
}


def lint_leak(rep, card, variant, cid, did, where):
    """Leak terms must be source-specific: present in the source, absent from the target."""
    try:
        terms, rx = V.detail_terms(card, did)
    except KeyError:
        rep.add("ERROR", f"{where} {cid}: unknown incidental detail {did}")
        return
    src, tgt = card["source_example"]["text"], target_text(card, variant)
    if variant:  # the user's own words around the example count as target text too
        tgt += "\n" + variant["text"].replace("{EX}", " ")
    for t in terms:
        if not C.term_regex(t).search(src):
            rep.add("ERROR", f"{where} {cid}: leak term {t!r} of {did} is not in the source example")
        if C.term_regex(t).search(tgt):
            rep.add("ERROR", f"{where} {cid}: leak term {t!r} of {did} also appears in the target; banning it is stricter than the task")
    if rx:
        if not re.search(rx, src, re.I):
            rep.add("ERROR", f"{where} {cid}: leak regex of {did} matches nothing in the source example")
        if re.search(rx, tgt, re.I):
            rep.add("ERROR", f"{where} {cid}: leak regex of {did} matches the target text")


# ---------------------------------------------------------------- card-level lint
def lint_card(card, release=False, gold=True):
    rep = Report(card.get("id", "?"))
    req = ["id", "schema", "status", "author", "family", "provenance", "target", "source_example",
           "relation", "variants", "turns", "human_review", "reference_solutions", "copy_answers"]
    for f in req:
        if f not in card:
            rep.add("ERROR", f"missing field {f}")
    if rep.count("ERROR"):
        return rep
    if card["schema"] != "seed-card-v1":
        rep.add("ERROR", "schema must be seed-card-v1")
    if card["family"] not in FAMILIES:
        rep.add("ERROR", f"family must be one of {FAMILIES}")
    if release:
        if card["status"] == DRAFT_STATUS:
            rep.add("ERROR", "status is still draft")
    elif card["status"] != DRAFT_STATUS:
        rep.add("ERROR", f"draft cards must carry status {DRAFT_STATUS!r}")

    # provenance: real, citable source
    pv = card["provenance"]
    if pv.get("source_type") not in SOURCE_TYPES:
        rep.add("ERROR", f"provenance.source_type must be one of {SOURCE_TYPES}")
    refs = pv.get("references") or []
    if not refs or not all(r.get("citation") for r in refs) or not any(r.get("url") or r.get("doi") for r in refs):
        rep.add("ERROR", "provenance needs references with citations, at least one with a url/doi")
    if not pv.get("case"):
        rep.add("ERROR", "provenance.case (what real case this is) is empty")
    if not pv.get("provenance_group_id"):
        rep.add("ERROR", "provenance.provenance_group_id is empty (needed for split hygiene)")
    if not pv.get("urls_checked_by_human"):
        rep.add("PENDING", "reference URLs not yet opened and checked by a person")

    # source example length
    se = card["source_example"]
    n = count_sentences(se["text"])
    if n < 8:
        rep.add("ERROR", f"source example has {n} sentences; at least 8 required")
    if se.get("length") == "long" and n < 20:
        rep.add("ERROR", f"source marked long but has {n} sentences; at least 20 required")
    if se.get("length") not in ("standard", "long"):
        rep.add("ERROR", "source_example.length must be standard or long")

    # incidental details
    inc = se.get("incidental_details", [])
    if len(inc) < 3:
        rep.add("ERROR", f"{len(inc)} incidental details; at least 3 required")
    for d in inc:
        if not (d.get("leak_terms") or d.get("leak_regex")):
            rep.add("ERROR", f"incidental {d.get('id')}: no leak_terms / leak_regex, so no automatic check")
    controls = [d for d in inc if d.get("control")]
    if not controls:
        rep.add("ERROR", "no incidental-detail control (protocol axis: same role and relation, different details)")
    for d in controls:
        c = d["control"]
        if c["from"] not in se["text"]:
            rep.add("ERROR", f"control for {d['id']}: 'from' text not in source")
        if c["from"] == c["to"]:
            rep.add("ERROR", f"control for {d['id']}: 'to' equals 'from'")
        pt = source_text(card, perturbed=True)
        for t in c.get("leak_terms", []):
            if not C.term_regex(t).search(pt):
                rep.add("ERROR", f"control for {d['id']}: leak term {t!r} not in perturbed source")

    # target rules
    rules = card["target"]["rules"]
    if not rules:
        rep.add("ERROR", "no target rules")
    for r in rules:
        if not r.get("checks"):
            rep.add("ERROR", f"target rule {r['id']} has no automatic check")
        for c in r.get("checks", []):
            lint_check(rep, card, None, c, f"rule {r['id']}", rule=r)
    if card["family"] == "code" and not (card.get("func") and card.get("tests")):
        rep.add("ERROR", "code card needs func and tests")

    # variants
    variants = card["variants"]
    ids = [v["id"] for v in variants]
    if len(ids) != len(set(ids)):
        rep.add("ERROR", "duplicate variant ids")
    used_details = set()
    for v in variants:
        w = f"variant {v['id']}"
        if v.get("role") not in ROLES or v.get("cue") not in CUES or v.get("fit") not in FITS:
            rep.add("ERROR", f"{w}: role/cue/fit must be in {ROLES}/{CUES}/{FITS}")
            continue
        if "{EX}" not in v.get("text", ""):
            rep.add("ERROR", f"{w}: text must contain {{EX}} where the source example goes")
        if not v.get("must_transfer"):
            rep.add("ERROR", f"{w}: must_transfer is empty")
        if not v.get("must_not_transfer"):
            rep.add("ERROR", f"{w}: must_not_transfer is empty")
        if v["fit"] != "full" and not v.get("rules_add") and not v.get("fit_note"):
            rep.add("ERROR", f"{w}: non-full fit needs rules_add or fit_note saying what changes")
        own = norm(v["text"].replace("{EX}", " "))
        if v["cue"] == "implied":
            hits = [p for p in IMPLIED_BANNED if p in own]
            if hits:
                rep.add("ERROR", f"{w}: implied cue states the role outright: {hits}")
        else:
            if not any(p in own for p in CUE_PHRASES[v["role"]]):
                rep.add("WARN", f"{w}: stated cue has no recognised {v['role']} phrase")
        cids = [c["id"] for c in v.get("must_transfer", []) + v.get("must_not_transfer", [])]
        if len(cids) != len(set(cids)):
            rep.add("ERROR", f"{w}: duplicate check ids")
        for r in v.get("rules_add", []):
            for c in r.get("checks", []):
                lint_check(rep, card, v, c, f"{w} rule {r['id']}", rule=r)
        for c in v.get("must_transfer", []) + v.get("must_not_transfer", []):
            if not c.get("what"):
                rep.add("ERROR", f"{w} {c.get('id')}: missing 'what' (plain description of the scope item)")
            lint_check(rep, card, v, c, w)
            if c.get("spec", [None])[0] == "leak_absent":
                used_details.add(c["spec"][1])
    for d in inc:
        if d["id"] not in used_details:
            rep.add("ERROR", f"incidental {d['id']} is never checked by any variant")

    # cells: every role x fit is present for both cues, or marked not applicable
    na = card.get("cells_not_applicable", [])
    for role in ROLES:
        for fit in FITS:
            for cue in CUES:
                have = any(v["role"] == role and v["fit"] == fit and v["cue"] == cue for v in variants)
                skip = [x for x in na if x.get("role") == role and x.get("fit") == fit and x.get("cue") in (None, cue)]
                if have and skip:
                    rep.add("ERROR", f"cell {role}/{fit}/{cue} both present and marked not applicable")
                if not have and not skip:
                    rep.add("ERROR", f"cell {role}/{fit}/{cue} missing and not marked not applicable")
                if skip and not all(x.get("reason", "").strip() for x in skip):
                    rep.add("ERROR", f"cell {role}/{fit}: not-applicable without a reason")
    if not any(v["role"] == "counter" for v in variants):
        rep.add("WARN", "no counter-example variant")

    # counter-example surface similarity
    if any(v["role"] == "counter" for v in variants):
        feats = se.get("shared_surface_features", [])
        if len(feats) < 3:
            rep.add("ERROR", f"counter-example shares {len(feats)} listed surface features with the target; at least 3 required")
        tt = target_text(card)
        for f in feats:
            if norm(f.get("source_quote", "#")) not in norm(se["text"]):
                rep.add("ERROR", f"surface feature {f.get('feature')!r}: source_quote not in source")
            if norm(f.get("target_quote", "#")) not in norm(tt):
                rep.add("ERROR", f"surface feature {f.get('feature')!r}: target_quote not in target")

    # implied-cue share (protocol: half of all variants)
    if variants:
        share = sum(v["cue"] == "implied" for v in variants) / len(variants)
        rep.implied_share = share
        if share < 0.5:
            rep.add("ERROR", f"implied-cue share {share:.2f} < 0.50")
    if sorted(card["turns"]) != ["multi", "single"]:
        rep.add("ERROR", "turns must be ['single', 'multi']")

    # human fields
    hr = card["human_review"]
    for f in HUMAN_FIELDS:
        vals = hr.get(f, {})
        if set(vals) != {"annotator_1", "annotator_2"}:
            rep.add("ERROR", f"human_review.{f} needs annotator_1 and annotator_2 slots")
            continue
        if any(x is None for x in vals.values()):
            rep.add("PENDING", f"human_review.{f} not filled by two annotators")
        elif f == "realism" and not all(isinstance(x, int) and x >= 4 for x in vals.values()):
            rep.add("ERROR", f"realism {vals}: both annotators must rate 4 or 5")
        elif f == "scope_agreement" and not all(x is True for x in vals.values()):
            rep.add("ERROR", "annotators do not both agree on transfer scope; seed must be dropped or revised")

    if gold and not rep.count("ERROR"):
        lint_gold(rep, card)
    if release:
        rep.items = [("ERROR" if lv == "PENDING" else lv, m) for lv, m in rep.items]
    return rep


def lint_gold(rep, card):
    """Gold must pass; an example-copying answer must fail a transfer or leakage check."""
    refs, copies = card["reference_solutions"], card["copy_answers"]
    for v in card["variants"]:
        vid = v["id"]
        if vid not in refs:
            rep.add("ERROR", f"no reference solution for {vid}")
            continue
        r = V.score_v1(refs[vid], card, v)
        if not r["joint"]:
            bad = [x for k in ("constraints", "transfer", "leakage") for x in r["detail"][k] if not x[1]]
            rep.add("ERROR", f"reference for {vid} fails: {bad[:3]} format_ok={r['format_ok']}")
        # incidental-detail control: only leakage checks depend on the swapped details
        ans = V.parse_answer(refs[vid], card)
        for c in v["must_not_transfer"]:
            if c["spec"][0] == "leak_absent" and not V.run_check_v1(c["spec"], ans, card, perturbed=True)[0]:
                rep.add("ERROR", f"reference for {vid} fails {c['id']} on the incidental-detail control")
        if card.get("marker") and v["fit"] == "full":
            m = V.score_v1(refs[vid], card, v).get("marker")
            if v["role"] == "requirement" and m is not True:
                rep.add("WARN", f"reference for {vid} lacks the marker; requirement should copy it")
            if v["role"] == "counter" and m is not False:
                rep.add("WARN", f"reference for {vid} has the marker; counter should avoid it")
        if vid not in copies:
            rep.add("ERROR", f"no copy answer for {vid}")
            continue
        r = V.score_v1(copies[vid], card, v)
        if not r["format_ok"]:
            rep.add("ERROR", f"copy answer for {vid} is not even parseable; it tests nothing")
        elif r["transfer_ok"] and not r["leak"]:
            rep.add("ERROR", f"copy answer for {vid} passes transfer and leakage checks; checks do not catch copying")
    for alt in card.get("alternative_solutions", []):
        v = next((x for x in card["variants"] if x["id"] == alt["variant"]), None)
        if v and not V.score_v1(alt["answer"], card, v)["joint"]:
            rep.add("ERROR", f"valid alternative for {alt['variant']} fails; checks too strict")


def lint_set(cards, release=False):
    """Set-level rules (meaningful at full benchmark size)."""
    out = []
    if not cards:
        return out
    by = {}
    for c in cards:
        by.setdefault(c.get("provenance", {}).get("source_type"), []).append(c["id"])
    for st, ids in by.items():
        share = len(ids) / len(cards)
        if share > 0.40:
            out.append(("ERROR" if release else "WARN", f"source type {st} supplies {share:.0%} of seeds (> 40%)"))
    long_share = sum(c["source_example"].get("length") == "long" for c in cards) / len(cards)
    if long_share < 0.30:
        out.append(("ERROR", f"long source examples: {long_share:.0%} of seeds (< 30%)"))
    fams = {}
    for c in cards:
        fams[c["family"]] = fams.get(c["family"], 0) + 1
    for f in FAMILIES:
        if fams.get(f, 0) < 40:
            out.append(("ERROR" if release else "WARN", f"family {f}: {fams.get(f, 0)} seeds (< 40 required at full size)"))
    groups = {}
    for c in cards:
        groups.setdefault(c["provenance"].get("provenance_group_id"), []).append(c["id"])
    for g, ids in groups.items():
        if len(ids) > 1:
            out.append(("WARN", f"provenance group {g} shared by {ids}: keep in one split"))
    nv = sum(len(c["variants"]) for c in cards)
    ni = sum(v["cue"] == "implied" for c in cards for v in c["variants"])
    out.append(("INFO", f"{len(cards)} seeds, {nv} variants x 2 turns = {2 * nv} prompts (+ controls); implied share {ni / max(nv, 1):.2f}"))
    return out


def load(paths):
    files = []
    for p in paths:
        files += sorted(glob.glob(os.path.join(p, "*.json"))) if os.path.isdir(p) else [p]
    cards = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            cards.append(json.load(fh))
    return files, cards


def main(argv=None):
    ap = argparse.ArgumentParser()
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    ap.add_argument("paths", nargs="*", default=[os.path.join(root, "data", "seeds_v1_draft")])
    ap.add_argument("--release", action="store_true", help="treat PENDING human items as errors")
    ap.add_argument("--no-gold", action="store_true", help="skip running reference and copy answers")
    ap.add_argument("--quiet", action="store_true", help="only print the summary line per seed")
    a = ap.parse_args(argv)
    files, cards = load(a.paths)
    errors = 0
    for f, c in zip(files, cards):
        rep = lint_card(c, release=a.release, gold=not a.no_gold)
        ne, nw, npd = rep.count("ERROR"), rep.count("WARN"), rep.count("PENDING")
        errors += ne
        nvar = len(c.get("variants", []))
        share = getattr(rep, "implied_share", float("nan"))
        n = count_sentences(c["source_example"]["text"]) if "source_example" in c else 0
        print(f"{'FAIL' if ne else 'ok  '} {rep.sid:28s} variants={nvar:2d} implied={share:.2f} "
              f"sentences={n:2d} errors={ne} warnings={nw} pending_human={npd}")
        if not a.quiet:
            for lv, m in rep.items:
                if lv != "PENDING":
                    print(f"     {lv:7s} {m}")
            pend = [m for lv, m in rep.items if lv == "PENDING"]
            if pend:
                print(f"     PENDING {len(pend)} human item(s), e.g. {pend[0][:110]}")
    for lv, m in lint_set(cards, a.release):
        errors += lv == "ERROR"
        print(f"SET  {lv:7s} {m}")
    print(f"{len(cards)} card(s), {errors} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
