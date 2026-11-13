"""Licence helpers and the v2 scorer for seed-card-v2 (docs/seed-spec-v2.md, Sections 5 to 7).

Usage (library):
    import checks_v2 as V2
    r = V2.score_v2(model_output, card, variant)                    # one answer, one variant
    r = V2.score_v2(model_output, card, variant, perturbed=True)    # incidental-detail control build
    r = V2.score_v2(model_output, card, variant, reading="lenient") # ambiguity set: UNCLEAR read as MAY

score_v2 returns format_ok, constraint_ok, must_ok, mustnot_ok, joint, over_transfer, under_transfer,
used_units, unit_used, probe_uses, judge_pending, subset, plus a v1-style "detail" block.
It reuses checks.py and checks_v1.py unchanged: every check is run by checks_v1.run_check_v1.
Judge checks (judge_absent, judge_present) are reserved: they are returned as "not run" and
excluded from joint success (spec 6.5).

Nothing here changes v1 behaviour.
"""
import io
import json
import os
import re
import sys
import tokenize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checks as C  # noqa: E402
import checks_v1 as V1  # noqa: E402

LABELS = ("MUST", "MAY", "MUST_NOT", "UNCLEAR")
BASES = ("DIRECT", "INFERRED", "DEFAULT")
JUDGE_KINDS = {"judge_absent", "judge_present"}
# Kinds in checks.run_check plus the kinds added by checks_v1 plus the reserved judge kinds.
PILOT_KINDS = {
    "text_absent", "text_present", "regex_absent", "regex_present", "py_test", "json_len_between",
    "json_all_int", "json_all_num", "json_all_le", "json_increasing", "json_eq", "json_is_bool",
    "json_all_word", "json_any_word", "json_no_word", "json_all_match", "json_none_match",
    "json_count_match_ge", "json_count_in_lt", "json_all_words_le", "json_all_nonempty",
    "json_exists_item", "json_not_exists_item", "json_first_item_regex", "json_first_item_word",
}
KNOWN_KINDS = PILOT_KINDS | set(V1.NEW_KINDS) | JUDGE_KINDS
# implication -> (label, roles, unit kinds)  (spec 5.4)
IMPLICATIONS = {
    "relation_transfer": ("MUST", {"analogy"}, {"relation"}),
    "named_part_transfer": ("MUST", {"requirement"}, {"relation", "detail"}),
    "avoid_flagged_feature": ("MUST_NOT", {"counter"}, {"relation", "detail"}),
    "source_specific_fact": ("MUST_NOT", {"analogy", "requirement", "counter"}, {"detail"}),
}
ROLE_ID = {"analogy": 0, "requirement": 1, "counter": 2}


# ---------------------------------------------------------------- unit registry
def unit_registry(card):
    """{unit_id: {"kind": "relation"|"detail", "main": bool, "text": str}} in card order (first definition wins)."""
    reg = {}
    for u in card.get("relation_units", []) or []:
        if isinstance(u, dict) and isinstance(u.get("id"), str):
            reg.setdefault(u["id"], {"kind": "relation", "main": bool(u.get("main")), "text": u.get("what", "")})
    for d in card.get("source_example", {}).get("incidental_details", []) or []:
        if isinstance(d, dict) and isinstance(d.get("id"), str):
            reg.setdefault(d["id"], {"kind": "detail", "main": False, "text": d.get("text", "")})
    return reg


def detail_ids_with_control(card):
    return [d["id"] for d in card["source_example"]["incidental_details"] if d.get("control")]


# ---------------------------------------------------------------- licence
def expand_licence(card, variant):
    """Expand `defaults` into one entry per unit (spec 2.5).

    Returns (entries, problems). entries = {unit_id: entry copy with "_kind" and "_default" added}.
    problems = list of (unit_id or None, text) for units without an entry or unknown keys.
    """
    reg = unit_registry(card)
    lic = variant.get("licence")
    problems, entries = [], {}
    if not isinstance(lic, dict):
        return entries, [(None, "licence is missing or not an object")]
    defaults = lic.get("defaults") or {}
    units = lic.get("units") or {}
    if not isinstance(defaults, dict) or not isinstance(units, dict):
        return entries, [(None, "licence.defaults and licence.units must be objects")]
    for k in defaults:
        if k not in ("relation", "detail"):
            problems.append((None, f"licence.defaults key {k!r} is not 'relation' or 'detail'"))
    for u in units:
        if u not in reg:
            problems.append((u, f"licence.units key {u!r} is not a unit id of this card"))
    for u, info in reg.items():
        if u in units:
            e, from_default = units[u], False
        elif info["kind"] in defaults:
            e, from_default = defaults[info["kind"]], True
        else:
            problems.append((u, f"no licence entry and no default for {info['kind']} units"))
            continue
        if not isinstance(e, dict):
            problems.append((u, "licence entry is not an object"))
            continue
        e = dict(e)
        e["_kind"], e["_default"] = info["kind"], from_default
        entries[u] = e
    return entries, problems


def entry_label(entry, reading="proposed"):
    """Label an entry stands for before review: UNCLEAR becomes its `proposed` (or MAY under 'lenient')."""
    lab = entry.get("label")
    if lab == "UNCLEAR":
        return entry.get("proposed") if reading == "proposed" else "MAY"
    return lab


def final_label(card, variant_id, unit):
    """Final label of a unit (spec 2.7): adjudicated value, else the label both reviewers gave, else None."""
    hr = card.get("human_review") or {}
    decided = None
    for a in hr.get("adjudications", []) or []:
        if isinstance(a, dict) and a.get("variant") == variant_id and a.get("field") == "licence" and a.get("unit") == unit:
            decided = a.get("value")
    if decided is not None:
        return decided
    slots = (hr.get("variants") or {}).get(variant_id) or {}
    labs = []
    for key in ("annotator_1", "annotator_2"):
        s = slots.get(key)
        labs.append(((s or {}).get("licence") or {}).get(unit) if isinstance(s, dict) else None)
    if labs[0] is not None and labs[0] == labs[1]:
        return labs[0]
    return None


def resolved_labels(card, variant, reading="proposed"):
    """{unit: MUST|MAY|MUST_NOT} used for scoring. Reviewed final labels settle UNCLEAR units."""
    entries, _ = expand_licence(card, variant)
    out = {}
    for u, e in entries.items():
        if e.get("label") == "UNCLEAR":
            fl = final_label(card, variant["id"], u)
            out[u] = fl if fl in ("MUST", "MAY", "MUST_NOT") else entry_label(e, reading)
        else:
            out[u] = e.get("label")
    return out


def unresolved_units(card, variant):
    """UNCLEAR units whose final label is unresolved or UNCLEAR: they put the variant in the ambiguity set."""
    entries, _ = expand_licence(card, variant)
    res = []
    for u, e in entries.items():
        if e.get("label") == "UNCLEAR" and final_label(card, variant["id"], u) in (None, "UNCLEAR"):
            res.append(u)
    return res


def variant_subset(card, variant):
    return "ambiguity" if unresolved_units(card, variant) else "core"


def control_applies(card, variant):
    """The control build exists when the card has a control and no controlled unit is MUST here (spec 3.5)."""
    ctrl = detail_ids_with_control(card)
    if not ctrl:
        return False
    labels = resolved_labels(card, variant)
    return all(labels.get(u) != "MUST" for u in ctrl)


def control_spans(card):
    """Source spans of the control build: replace `from` by `to` inside the spans of each controlled unit only."""
    spans = [dict(s) for s in card["source_spans"]]
    for d in card["source_example"]["incidental_details"]:
        c = d.get("control")
        if not c:
            continue
        for s in spans:
            if s.get("unit") == d["id"]:
                s["text"] = s["text"].replace(c["from"], c["to"])
    return spans


# ---------------------------------------------------------------- checks of a variant
def iter_checks(card, variant):
    """Every check of one variant as dicts: list (rule | must_transfer | must_not_transfer | probe),
    scope (card | variant | None), rule (rule id or None), check."""
    out = []
    for r in card["target"]["rules"]:
        for c in r.get("checks", []):
            out.append({"list": "rule", "scope": "card", "rule": r["id"], "rule_text": r.get("text", ""), "check": c})
    for r in variant.get("rules_add", []) or []:
        for c in r.get("checks", []):
            out.append({"list": "rule", "scope": "variant", "rule": r["id"], "rule_text": r.get("text", ""), "check": c})
    for name in ("must_transfer", "must_not_transfer", "probes"):
        for c in variant.get(name, []) or []:
            out.append({"list": "probe" if name == "probes" else name, "scope": None, "rule": None, "rule_text": None, "check": c})
    return out


def is_judge(check):
    spec = check.get("spec")
    return isinstance(spec, list) and bool(spec) and spec[0] in JUDGE_KINDS


# ---------------------------------------------------------------- running checks
_PY_CACHE = {}


def run_check_v2(spec, ans, card, perturbed=False):
    """checks_v1.run_check_v1 with a cache for py_test (each py_test starts a Python process)."""
    if spec[0] == "py_test":
        if ans.get("code") is None:
            return False, "no code"
        key = (ans["code"], C.expand(card["tests"], spec[1]))
        if key not in _PY_CACHE:
            _PY_CACHE[key] = C.run_py_test(*key)
        return _PY_CACHE[key]
    return V1.run_check_v1(spec, ans, card, perturbed)


def warm_cache(card, variant, outputs, workers=8):
    """Run the py_test checks of one variant on several answers in parallel threads and cache the results,
    so that a card with many answers does not start its test processes one after the other."""
    if card["family"] != "code":
        return
    jobs = set()
    for out in outputs:
        code = parse_answer(out, card)["code"]
        if code is None:
            continue
        for it in iter_checks(card, variant):
            spec = it["check"].get("spec") or []
            if spec[:1] == ["py_test"] and len(spec) > 1 and spec[1] in (card.get("tests") or {}) and not is_judge(it["check"]):
                key = (code, C.expand(card["tests"], spec[1]))
                if key not in _PY_CACHE:
                    jobs.add(key)
    if len(jobs) > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=workers) as ex:
            for key, res in zip(sorted(jobs), ex.map(lambda k: C.run_py_test(*k), sorted(jobs))):
                _PY_CACHE[key] = res


def parse_answer(output, card):
    return V1.parse_answer(output, card)


def score_v2(output, card, variant, perturbed=False, reading="proposed"):
    """Score one answer for one variant (spec 6.3). Judge checks are not run."""
    ans = parse_answer(output, card)
    labels = resolved_labels(card, variant, reading)
    runs = []
    for it in iter_checks(card, variant):
        c = it["check"]
        if is_judge(c):
            passed, note = None, "not run (reserved judge check)"
        else:
            passed, note = run_check_v2(c["spec"], ans, card, perturbed)
        runs.append({**it, "id": c["id"], "units": list(c.get("units") or []), "passed": passed, "note": note,
                     "judge": is_judge(c), "use_when": c.get("use_when", "fail")})
    judge_ids = [r["id"] for r in runs if r["judge"]]
    res = {"format_ok": ans["format_ok"], "subset": variant_subset(card, variant), "judge_pending": bool(judge_ids),
           "judge_checks": judge_ids}
    lists = {"constraints": "rule", "transfer": "must_transfer", "leakage": "must_not_transfer", "probes": "probe"}
    res["detail"] = {k: [(r["id"], r["passed"], r["note"]) for r in runs if r["list"] == v] for k, v in lists.items()}
    if card.get("marker"):
        res["marker"] = run_check_v2(card["marker"]["spec"], ans, card, perturbed)[0] if ans["format_ok"] else None
    if not ans["format_ok"]:
        res.update({"constraint_ok": None, "must_ok": None, "mustnot_ok": None, "joint": False,
                    "over_transfer": None, "under_transfer": None, "used_units": [], "unit_used": {}, "probe_uses": {}})
        return res
    scoring = [r for r in runs if r["list"] != "probe" and not r["judge"]]
    res["constraint_ok"] = all(r["passed"] for r in scoring if r["list"] == "rule")
    unit_used = {}
    for u, lab in labels.items():
        named = [r for r in scoring if u in r["units"]]
        probes = [r for r in runs if r["list"] == "probe" and u in r["units"]]
        if lab == "MUST":
            unit_used[u] = all(r["passed"] for r in named) if named else None
        elif lab == "MUST_NOT":
            unit_used[u] = any(not r["passed"] for r in named) if named else None
        else:  # MAY: descriptive only
            hit = [(not r["passed"]) if r["use_when"] == "fail" else bool(r["passed"]) for r in probes]
            if hit:
                unit_used[u] = any(hit)
            elif unit_kind(card, u) == "detail":
                unit_used[u] = not run_check_v2(["leak_absent", u], ans, card, perturbed)[0]
            else:
                unit_used[u] = None
    res["must_ok"] = all(unit_used[u] for u, lab in labels.items() if lab == "MUST" and unit_used[u] is not None)
    res["mustnot_ok"] = not any(unit_used[u] for u, lab in labels.items() if lab == "MUST_NOT" and unit_used[u] is not None)
    res["joint"] = bool(res["format_ok"] and res["constraint_ok"] and res["must_ok"] and res["mustnot_ok"])
    res["over_transfer"] = not res["mustnot_ok"]
    res["under_transfer"] = not res["must_ok"]
    res["unit_used"] = unit_used
    res["used_units"] = sorted(u for u, used in unit_used.items() if used)
    res["probe_uses"] = {r["id"]: ((not r["passed"]) if r["use_when"] == "fail" else bool(r["passed"]))
                         for r in runs if r["list"] == "probe"}
    return res


def unit_kind(card, unit):
    return unit_registry(card).get(unit, {}).get("kind")


# ---------------------------------------------------------------- answers
def failing_checks(output, card, variant, perturbed=False):
    """Ids of non-judge scoring checks (rules, must_transfer, must_not_transfer) that fail. Probes never fail."""
    ans = parse_answer(output, card)
    out = []
    for it in iter_checks(card, variant):
        c = it["check"]
        if it["list"] == "probe" or is_judge(c):
            continue
        if not run_check_v2(c["spec"], ans, card, perturbed)[0]:
            out.append(c["id"])
    return out


def _strip_comments(code):
    lines = code.split("\n")
    cuts = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(code).readline):
            if tok.type == tokenize.COMMENT:
                cuts[tok.start[0]] = tok.start[1]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return "\n".join(re.sub(r"\s#.*$", "", ln) for ln in lines)
    return "\n".join(ln[:cuts[i + 1]] if (i + 1) in cuts else ln for i, ln in enumerate(lines))


def normalise_answer(output, card):
    """Normalised form of an answer (spec 7): sorted-key JSON for decision cards; code without comments,
    blank lines and repeated whitespace for code cards."""
    if card["family"] == "code":
        code = C.extract_code(output, card["func"])
        if code is None:
            return " ".join(output.split())
        out = []
        for ln in _strip_comments(code).split("\n"):
            if ln.strip():
                indent = re.match(r"\s*", ln).group(0)
                out.append(indent + re.sub(r"[ \t]+", " ", ln.strip()))
        return "\n".join(out)
    obj = C.extract_json(output)
    return json.dumps(obj, sort_keys=True, ensure_ascii=False) if obj is not None else " ".join(output.split())
