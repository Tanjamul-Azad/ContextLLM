"""Check kinds for v1 seed cards (docs/seed-spec-v1.md).

Every check is automatic. Kinds already in checks.py are reused unchanged;
this file adds the kinds the v1 cards need and a scorer that keeps format
failure separate from leakage (pilot audit issue).

A check spec is a JSON list: [kind, arg1, arg2, ...].
"""
import re

import checks as C

# ---------------------------------------------------------------- new kinds
NEW_KINDS = {
    "leak_absent",                # [detail_id]: no leak term / leak regex of that incidental detail
    "json_all_ge",                # [path, n]
    "json_eq_num",                # [path, n]
    "json_distinct_nonzero_lt",   # [path, n]: fewer than n distinct non-zero values
    "json_distinct_nonzero_eq",   # [path, n]
    "json_levels_ratio",          # [path, [r1, r2, ...]]: distinct non-zero values proportional to ratios
    "json_ranges_cover",          # [list_path, start_f, end_f, lo, hi]: contiguous cover of [lo, hi)
    "json_range_value_cmp",       # [list_path, start_f, end_f, value_f, x1, op, x2]
    "json_map_in",                # [list_path, key_f, value_f, {key: [allowed, ...]}]
    "json_monotone_map",          # [list_path, key_f, value_f, [keys in order], [values in order]]
    "json_in",                    # [path, [allowed, ...]]
    "json_all_lt",                # [path, n]
    "json_count_value_le",        # [list_path, field, value, n]: at most n items with field == value
    "json_map_rank_cmp",          # [list_path, key_f, value_f, [values in order], key1, op, key2]
}

# Kinds whose numeric arguments are bounds taken from the instruction.
# Index list = positions in the spec (spec[0] is the kind) that hold bounds.
BOUND_ARGS = {
    "json_len_between": [2, 3],
    "json_all_le": [2],
    "json_all_ge": [2],
    "json_all_words_le": [2],
    "json_count_in_lt": [3],
    "json_eq_num": [2],
    "json_distinct_nonzero_lt": [2],
    "json_distinct_nonzero_eq": [2],
    "json_levels_ratio": [2],
    "json_ranges_cover": [4, 5],
    "json_all_lt": [2],
    "json_count_value_le": [4],
}

# Kinds whose argument is a list of words that are banned or required.
TERM_ARGS = {
    "text_absent": 1, "text_present": 1,
    "json_no_word": 2, "json_any_word": 2, "json_all_word": 2,
}
REGEX_ARGS = {"regex_absent": 1, "regex_present": 1}

OPS = {">": lambda a, b: a > b, "<": lambda a, b: a < b, ">=": lambda a, b: a >= b,
       "<=": lambda a, b: a <= b, "==": lambda a, b: a == b, "!=": lambda a, b: a != b}


def _norm(v):
    return str(v).strip().lower()


def _items(obj, path):
    vals = C.get_path(obj, path)
    return vals[0] if vals and isinstance(vals[0], list) else []


def _value_at(items, s, e, v, x):
    for it in items:
        if isinstance(it, dict) and C.is_num(it.get(s)) and C.is_num(it.get(e)) and it[s] <= x < it[e]:
            return it.get(v)
    return None


def detail_terms(card, detail_id, perturbed=False):
    """Leak terms and leak regex for one incidental detail (control version if perturbed)."""
    for d in card["source_example"]["incidental_details"]:
        if d["id"] == detail_id:
            src = d["control"] if perturbed and d.get("control") else d
            return src.get("leak_terms", []), src.get("leak_regex")
    raise KeyError(f"unknown incidental detail {detail_id}")


def run_check_v1(spec, ans, card, perturbed=False):
    """Returns (passed, note). Falls back to checks.run_check for pilot kinds."""
    kind = spec[0]
    if kind not in NEW_KINDS:
        return C.run_check(tuple(spec), ans, card)
    obj, text = ans["obj"], ans["text"]

    if kind == "leak_absent":
        terms, rx = detail_terms(card, spec[1], perturbed)
        hits = [t for t in terms if C.term_regex(t).search(text)]
        if rx:
            m = re.search(rx, text, re.I)
            if m:
                hits.append(m.group(0))
        return not hits, ",".join(hits)

    if obj is None:
        return False, "no json"
    vals = C.get_path(obj, spec[1])

    if kind == "json_all_ge":
        return bool(vals) and all(C.is_num(v) and v >= spec[2] for v in vals), str(vals)[:80]
    if kind == "json_eq_num":
        return len(vals) == 1 and C.is_num(vals[0]) and vals[0] == spec[2], str(vals)[:80]
    if kind == "json_all_lt":
        return bool(vals) and all(C.is_num(v) and v < spec[2] for v in vals), str(vals)[:80]
    if kind == "json_in":
        return len(vals) == 1 and _norm(vals[0]) in {_norm(a) for a in spec[2]}, str(vals)[:80]
    if kind in ("json_distinct_nonzero_lt", "json_distinct_nonzero_eq", "json_levels_ratio"):
        if not vals or not all(C.is_num(v) for v in vals):
            return False, str(vals)[:80]
        levels = sorted({v for v in vals if v != 0})
        if kind == "json_distinct_nonzero_lt":
            return len(levels) < spec[2], str(levels)
        if kind == "json_distinct_nonzero_eq":
            return len(levels) == spec[2], str(levels)
        ratios = spec[2]
        if len(levels) != len(ratios):
            return False, str(levels)
        base = levels[0] / ratios[0]
        return all(abs(l - r * base) < 1e-9 * max(1, l) for l, r in zip(levels, ratios)), str(levels)

    items = _items(obj, spec[1])
    if kind == "json_ranges_cover":
        _, _, s, e, lo, hi = spec
        rs = sorted(((it.get(s), it.get(e)) for it in items if isinstance(it, dict)), key=lambda t: (t[0] is None, t[0]))
        ok = bool(rs) and all(C.is_num(a) and C.is_num(b) and a < b for a, b in rs)
        ok = ok and rs[0][0] == lo and rs[-1][1] == hi and all(rs[i][1] == rs[i + 1][0] for i in range(len(rs) - 1))
        return ok, str(rs)[:80]
    if kind == "json_range_value_cmp":
        _, _, s, e, v, x1, op, x2 = spec
        a, b = _value_at(items, s, e, v, x1), _value_at(items, s, e, v, x2)
        ok = C.is_num(a) and C.is_num(b) and OPS[op](a, b)
        return ok, f"{a} {op} {b}"
    if kind == "json_map_in":
        _, _, kf, vf, want = spec
        got = {_norm(it.get(kf)): _norm(it.get(vf)) for it in items if isinstance(it, dict)}
        bad = [k for k, allowed in want.items() if got.get(_norm(k)) not in {_norm(a) for a in allowed}]
        return not bad, ",".join(bad)
    if kind == "json_monotone_map":
        _, _, kf, vf, keys, order = spec
        got = {_norm(it.get(kf)): _norm(it.get(vf)) for it in items if isinstance(it, dict)}
        rank = {_norm(o): i for i, o in enumerate(order)}
        rs = [rank.get(got.get(_norm(k)), None) for k in keys]
        ok = None not in rs and all(b >= a for a, b in zip(rs, rs[1:]))
        return ok, str(rs)
    if kind == "json_count_value_le":
        _, _, f, val, n = spec
        k = sum(1 for it in items if isinstance(it, dict) and _norm(it.get(f)) == _norm(val))
        return k <= n, str(k)
    if kind == "json_map_rank_cmp":
        _, _, kf, vf, order, k1, op, k2 = spec
        got = {_norm(it.get(kf)): _norm(it.get(vf)) for it in items if isinstance(it, dict)}
        rank = {_norm(o): i for i, o in enumerate(order)}
        a, b = rank.get(got.get(_norm(k1))), rank.get(got.get(_norm(k2)))
        return a is not None and b is not None and OPS[op](a, b), f"{a} {op} {b}"
    raise ValueError(f"unknown check {kind}")


# ---------------------------------------------------------------- scoring
def parse_answer(output, card):
    return C.parse_answer(output, card)


def score_v1(output, card, variant, perturbed=False):
    """Score one answer for one variant.

    Format failure is reported on its own: when the answer cannot be parsed,
    transfer and leakage are None, never counted as leakage.
    """
    ans = parse_answer(output, card)
    res = {"format_ok": ans["format_ok"], "detail": {}}
    rules = list(card["target"]["rules"]) + list(variant.get("rules_add", []))
    cons = [(c["id"],) + run_check_v1(c["spec"], ans, card, perturbed) for r in rules for c in r["checks"]]
    trans = [(c["id"],) + run_check_v1(c["spec"], ans, card, perturbed) for c in variant["must_transfer"]]
    leaks = [(c["id"],) + run_check_v1(c["spec"], ans, card, perturbed) for c in variant["must_not_transfer"]]
    res["detail"] = {"constraints": cons, "transfer": trans, "leakage": leaks}
    if not ans["format_ok"]:
        res.update({"constraint_ok": False, "transfer_ok": None, "leak": None, "joint": False})
        return res
    res["constraint_ok"] = all(p for _, p, _ in cons)
    res["transfer_ok"] = all(p for _, p, _ in trans)
    res["leak"] = any(not p for _, p, _ in leaks)
    res["joint"] = res["constraint_ok"] and res["transfer_ok"] and not res["leak"]
    if card.get("marker"):
        res["marker"] = run_check_v1(card["marker"]["spec"], ans, card, perturbed)[0]
    return res
