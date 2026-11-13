"""Lint seed-card-v2 cards against the rules of docs/seed-spec-v2.md Section 8.

Usage:
    python -I src/seed_lint_v2.py [DIR_OR_FILES ...] [--release] [--no-gold] [--quiet] [--json out.json]

Default directory: data/seeds_v2_draft/. Exit code 1 if any ERROR is found (card level or set level).

Levels:
  ERROR    a rule is broken; the card cannot be used.
  WARN     probably a problem; a person should look.
  PENDING  only humans (or a later work package) can settle it. Allowed in draft mode,
           becomes ERROR with --release.
  INFO     set-level counts.

Every finding is printed as   LEVEL RULE card | variant ..., unit ...: message   so that it can be grepped
by rule id. Rules marked "gold" (A3, A4, A7, A12, A13) run the answers and are skipped with --no-gold.
Each card gets one summary line: errors / warnings / pending / core rate (share of variants without an
unresolved UNCLEAR unit). The run is deterministic: same files, same output.

Rules that cannot be evaluated because an earlier structural rule failed (M1) are not run; the summary
line says so. An internal failure of a rule group is reported as ERROR INT, never swallowed.

Helpers of seed_lint_v1 (prompt building, cue phrase lists, sentence counting) are imported unchanged.
"""
import argparse
import difflib
import glob
import json
import os
import re
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import checks as C  # noqa: E402
import checks_v1 as V1  # noqa: E402
import checks_v2 as V2  # noqa: E402
import seed_lint_v1 as L1  # noqa: E402

REGISTRY_DIR = os.path.join(ROOT, "data", "registry")
JUDGE_STATUS = os.path.join(ROOT, "results", "judge_audit", "status.json")

STATUSES = ["draft", "in_review", "reviewed", "accepted", "rejected"]
ASSISTANCE = ["none", "edited", "drafted"]
SOURCE_TYPES = list(L1.SOURCE_TYPES) + ["original_scenario"]
ROLES, CUES, FITS = L1.ROLES, L1.CUES, L1.FITS
FAMILIES = L1.FAMILIES
LENGTHS = ["standard", "long"]
VALID_ORIGINS = ["v1_reference", "v1_alternative", "author", "model_drafted"]
INVALID_ORIGINS = VALID_ORIGINS + ["v1_copy"]
REVIEW_ROLES = ROLES + ["mixed", "unclear"]
ID_RE = re.compile(r"^[CDX]\d{2,3}_[a-z0-9_]+$")
AUTHOR_RE = re.compile(r"^[a-z][a-z0-9_]{1,31}$")
SNAKE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
GROUP_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{1,63}$")
SPAN_ID_RE = re.compile(r"^S\d{2,3}$")
REL_ID_RE = re.compile(r"^U\d{2}$")
DET_ID_RE = re.compile(r"^I\d+$")
POOLS = ["calibration", "development", "test_familiar", "test_heldout_relation", "test_heldout_domain",
         "natural", "training"]
LEVEL_ORDER = {"ERROR": 0, "WARN": 1, "PENDING": 2, "INFO": 3}


# ---------------------------------------------------------------- report
class Report:
    """Findings of one card. Each finding names the card, rule, and (when it applies) variant and unit."""

    def __init__(self, sid):
        self.sid, self.items = sid, []
        self.n_variants = self.n_core = 0
        self.skipped = None

    def add(self, level, rule, msg, variant=None, unit=None):
        self.items.append({"level": level, "rule": rule, "card": self.sid, "variant": variant, "unit": unit, "msg": msg})

    def count(self, level):
        return sum(1 for it in self.items if it["level"] == level)

    def rules(self, level="ERROR"):
        return sorted({it["rule"] for it in self.items if it["level"] == level})

    @property
    def core_rate(self):
        return self.n_core / self.n_variants if self.n_variants else float("nan")


def fmt(it):
    where = ", ".join(x for x in (f"variant {it['variant']}" if it["variant"] else "", f"unit {it['unit']}" if it["unit"] else "") if x)
    return f"{it['level']:7s} {it['rule']:5s} {it['card']}" + (f" | {where}" if where else "") + f": {it['msg']}"


# ---------------------------------------------------------------- small helpers
def is_type(v, t):
    if t == "str":
        return isinstance(v, str)
    if t == "int":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "bool":
        return isinstance(v, bool)
    if t == "list":
        return isinstance(v, list)
    if t == "obj":
        return isinstance(v, dict)
    if t == "null":
        return v is None
    raise ValueError(t)


def nonempty(v):
    return isinstance(v, str) and v.strip() != ""


def own_words(variant):
    """The user's own words of a variant: its text without the example."""
    return variant["text"].replace("{EX}", "\u0000")


def occurrences(hay, needle):
    out, i = [], hay.find(needle)
    while needle and i != -1:
        out.append(i)
        i = hay.find(needle, i + 1)
    return out


def detector_regexes(detail, control=False):
    """Compiled detectors of a detail: one per leak term (checks.term_regex) plus the leak regex."""
    src = detail["control"] if control and detail.get("control") else detail
    rx = [C.term_regex(t) for t in src.get("leak_terms", []) or []]
    if src.get("leak_regex"):
        rx.append(re.compile(src["leak_regex"], re.I))
    return rx


def span_offsets(spans):
    """[(start, end)] of each span in the concatenation (derived, never stored: spec 3.1)."""
    out, pos = [], 0
    for s in spans:
        out.append((pos, pos + len(s["text"])))
        pos += len(s["text"])
    return out


def example_in_message(content, example):
    """Start offset of the example inside a message, or -1."""
    return content.find(example)


class Ctx:
    """One card under lint with the derived data that several rules share."""

    def __init__(self, card, rep, release, gold, path):
        self.card, self.rep, self.release, self.gold, self.path = card, rep, release, gold, path
        self.reg = V2.unit_registry(card)
        self._ent, self._prompt, self._multi = {}, {}, {}

    def ent(self, v):
        if v["id"] not in self._ent:
            self._ent[v["id"]] = V2.expand_licence(self.card, v)
        return self._ent[v["id"]]

    def label(self, v, u):
        """Label of a unit as the author set it (UNCLEAR counts as its `proposed`)."""
        e = self.ent(v)[0].get(u)
        return V2.entry_label(e) if e else None

    def has_ex(self, v):
        return v["text"].count("{EX}") == 1

    def prompt(self, v):
        if v["id"] not in self._prompt:
            self._prompt[v["id"]] = L1.prompt_text(self.card, v)
        return self._prompt[v["id"]]

    def multi(self, v):
        if v["id"] not in self._multi:
            self._multi[v["id"]] = L1.build_messages(self.card, v, "multi")
        return self._multi[v["id"]]


# ---------------------------------------------------------------- M1: structure
def check_fields(rep, obj, spec, where, variant=None):
    """spec = [(key, type or 'a|b', required)]. Reports M1 for a missing key or a wrong type."""
    ok = True
    for key, types, req in spec:
        if key not in obj:
            if req:
                rep.add("ERROR", "M1", f"{where}: missing required field {key!r}", variant)
                ok = False
            continue
        if not any(is_type(obj[key], t) for t in types.split("|")):
            rep.add("ERROR", "M1", f"{where}: field {key!r} must be {types}, found {type(obj[key]).__name__}", variant)
            ok = False
    return ok


def lint_m1(rep, card):
    """M1: every required field of Section 2 is present with the stated type. Returns True when the structure is sound."""
    n0 = rep.count("ERROR")
    top = [("schema", "str", 1), ("id", "str", 1), ("status", "str", 1), ("status_note", "str", 1), ("created", "str", 1),
           ("updated", "str", 1), ("author_id", "str", 1), ("model_assistance", "str", 1), ("family", "str", 1),
           ("domain", "str", 1), ("domain_note", "str", 0), ("relation_family", "str", 1), ("template_group_id", "str", 1),
           ("provenance_group_id", "str", 1), ("provenance", "obj", 1), ("target", "obj", 1), ("source_example", "obj", 1),
           ("relation_units", "list", 1), ("source_spans", "list", 1), ("relation", "str", 1), ("marker", "obj", 0),
           ("turns", "list", 1), ("variants", "list", 1), ("cells_not_applicable", "list", 1), ("human_review", "obj", 1),
           ("contamination", "obj", 1), ("split", "str|null", 1), ("notes", "str", 0), ("migration", "obj", 0)]
    check_fields(rep, card, top, "card")
    if card.get("model_assistance") in ("edited", "drafted"):
        check_fields(rep, card, [("model_assistance_log", "obj", 1)], "card")
    elif "model_assistance_log" in card:
        check_fields(rep, card, [("model_assistance_log", "obj|null", 0)], "card")
    if card.get("family") == "code":
        check_fields(rep, card, [("func", "str", 1), ("tests", "obj", 1)], "card (code family)")
    if card.get("family") not in FAMILIES and isinstance(card.get("family"), str):
        rep.add("ERROR", "M1", f"family {card['family']!r} must be one of {FAMILIES}")
    containers = [("provenance", dict), ("target", dict), ("source_example", dict), ("variants", list),
                  ("relation_units", list), ("source_spans", list), ("human_review", dict), ("turns", list)]
    if not all(isinstance(card.get(k), t) for k, t in containers):
        return False
    pv = card["provenance"]
    check_fields(rep, pv, [("source_type", "str", 1), ("case", "str", 1), ("references", "list", pv.get("source_type") != "original_scenario"),
                           ("original_authoring", "str", pv.get("source_type") == "original_scenario"),
                           ("fresh_after_cutoff", "bool", 1), ("urls_checked_by_human", "bool", 1)], "provenance")
    for i, r in enumerate(pv.get("references") or []):
        if not isinstance(r, dict):
            rep.add("ERROR", "M1", f"provenance.references[{i}] must be an object")
    t = card["target"]
    check_fields(rep, t, [("task", "str", 1), ("rules", "list", 1), ("format", "str", 1)], "target")
    for r in t.get("rules", []) if isinstance(t.get("rules"), list) else []:
        if not isinstance(r, dict):
            rep.add("ERROR", "M1", "target.rules entry must be an object")
            continue
        check_fields(rep, r, [("id", "str", 1), ("text", "str", 1), ("checks", "list", 1)], f"target rule {r.get('id', '?')}")
        for c in r.get("checks", []) if isinstance(r.get("checks"), list) else []:
            lint_check_shape(rep, c, f"rule {r.get('id', '?')}", None, "rule")
    se = card["source_example"]
    check_fields(rep, se, [("text", "str", 1), ("length", "str", 1), ("incidental_details", "list", 1),
                           ("shared_surface_features", "list", 0)], "source_example")
    if isinstance(se.get("length"), str) and se["length"] not in LENGTHS:
        rep.add("ERROR", "M1", f"source_example.length {se['length']!r} must be one of {LENGTHS}")
    for d in se.get("incidental_details", []) if isinstance(se.get("incidental_details"), list) else []:
        if not isinstance(d, dict):
            rep.add("ERROR", "M1", "incidental_details entry must be an object")
            continue
        w = f"incidental detail {d.get('id', '?')}"
        check_fields(rep, d, [("id", "str", 1), ("text", "str", 1), ("leak_terms", "list", 0), ("leak_regex", "str", 0),
                              ("control", "obj", 0)], w)
        if isinstance(d.get("id"), str) and not DET_ID_RE.match(d["id"]):
            rep.add("ERROR", "M1", f"{w}: id must match {DET_ID_RE.pattern}")
        if not (d.get("leak_terms") or d.get("leak_regex")):
            rep.add("ERROR", "M1", f"{w}: needs leak_terms and/or leak_regex (the detector)")
        for who, src in (("detail", d), ("control", d.get("control") or {})):
            if not isinstance(src, dict):
                continue
            if not all(isinstance(x, str) for x in src.get("leak_terms", []) if isinstance(src.get("leak_terms"), list)):
                rep.add("ERROR", "M1", f"{w}: {who} leak_terms must be strings")
            if isinstance(src.get("leak_regex"), str):
                try:
                    re.compile(src["leak_regex"])
                except re.error as e:
                    rep.add("ERROR", "M1", f"{w}: {who} leak_regex does not compile: {e}")
        if isinstance(d.get("control"), dict):
            check_fields(rep, d["control"], [("from", "str", 1), ("to", "str", 1)], f"{w} control")
    for u in card["relation_units"]:
        if not isinstance(u, dict):
            rep.add("ERROR", "M1", "relation_units entry must be an object")
            continue
        w = f"relation unit {u.get('id', '?')}"
        check_fields(rep, u, [("id", "str", 1), ("what", "str", 1), ("main", "bool", 1)], w)
        if isinstance(u.get("id"), str) and not REL_ID_RE.match(u["id"]):
            rep.add("ERROR", "M1", f"{w}: id must match {REL_ID_RE.pattern}")
    for s in card["source_spans"]:
        if not isinstance(s, dict):
            rep.add("ERROR", "M1", "source_spans entry must be an object")
            continue
        check_fields(rep, s, [("id", "str", 1), ("text", "str", 1), ("kind", "str", 1), ("unit", "str", 0)], f"span {s.get('id', '?')}")
    vids = []
    for v in card["variants"]:
        if not isinstance(v, dict):
            rep.add("ERROR", "M1", "variants entry must be an object")
            continue
        vids.append(v.get("id"))
        lint_m1_variant(rep, card, v)
    lint_m1_review(rep, card, vids)
    return rep.count("ERROR") == n0


def lint_check_shape(rep, c, where, variant, lst):
    if not isinstance(c, dict):
        rep.add("ERROR", "M1", f"{where}: check must be an object", variant)
        return
    spec = [("id", "str", 1), ("spec", "list", 1), ("what", "str", 0), ("basis", "obj", 0), ("units", "list", 0)]
    if lst == "probe":
        spec += [("use_when", "str", 1), ("v1_id", "str", 0)]
    check_fields(rep, c, spec, f"{where} check {c.get('id', '?')}", variant)
    if lst == "probe" and c.get("use_when") not in (None, "fail", "pass"):
        rep.add("ERROR", "M1", f"{where} check {c.get('id', '?')}: use_when must be 'fail' or 'pass'", variant)
    if isinstance(c.get("units"), list) and not all(isinstance(u, str) for u in c["units"]):
        rep.add("ERROR", "M1", f"{where} check {c.get('id', '?')}: units must be strings", variant)
    if isinstance(c.get("spec"), list) and c["spec"] and not isinstance(c["spec"][0], str):
        rep.add("ERROR", "M1", f"{where} check {c.get('id', '?')}: spec[0] must be the check kind (a string)", variant)


def lint_m1_variant(rep, card, v):
    vid = v.get("id")
    w = f"variant {vid}"
    check_fields(rep, v, [("id", "str", 1), ("role", "str", 1), ("cue", "str", 1), ("fit", "str", 1), ("text", "str", 1),
                          ("rules_add", "list", 0), ("fit_note", "str", 0), ("licence", "obj", 1), ("must_transfer", "list", 1),
                          ("must_not_transfer", "list", 1), ("probes", "list", 1), ("valid_answers", "list", 1),
                          ("invalid_answers", "list", 1)], w, vid)
    for name, lst in (("must_transfer", "must_transfer"), ("must_not_transfer", "must_not_transfer"), ("probes", "probe")):
        for c in v.get(name, []) if isinstance(v.get(name), list) else []:
            lint_check_shape(rep, c, f"{w} {name}", vid, lst)
    for r in v.get("rules_add", []) if isinstance(v.get("rules_add"), list) else []:
        if not isinstance(r, dict):
            rep.add("ERROR", "M1", f"{w}: rules_add entry must be an object", vid)
            continue
        check_fields(rep, r, [("id", "str", 1), ("text", "str", 1), ("checks", "list", 1)], f"{w} rules_add {r.get('id', '?')}", vid)
        for c in r.get("checks", []) if isinstance(r.get("checks"), list) else []:
            lint_check_shape(rep, c, f"{w} rules_add {r.get('id', '?')}", vid, "rule")
    seen = set()
    for a in v.get("valid_answers", []) if isinstance(v.get("valid_answers"), list) else []:
        if not isinstance(a, dict):
            rep.add("ERROR", "M1", f"{w}: valid_answers entry must be an object", vid)
            continue
        check_fields(rep, a, [("id", "str", 1), ("text", "str", 1), ("origin", "str", 1), ("uses_may", "list", 0), ("note", "str", 0)],
                     f"{w} valid answer {a.get('id', '?')}", vid)
        if isinstance(a.get("id"), str):
            if not re.match(r"^V\d+$", a["id"]):
                rep.add("ERROR", "M1", f"{w}: valid answer id {a['id']!r} must match V<n>", vid)
            if a["id"] in seen:
                rep.add("ERROR", "M1", f"{w}: duplicate answer id {a['id']}", vid)
            seen.add(a["id"])
        if a.get("origin") not in VALID_ORIGINS and isinstance(a.get("origin"), str):
            rep.add("ERROR", "M1", f"{w} valid answer {a.get('id')}: origin {a['origin']!r} not in {VALID_ORIGINS}", vid)
    for a in v.get("invalid_answers", []) if isinstance(v.get("invalid_answers"), list) else []:
        if not isinstance(a, dict):
            rep.add("ERROR", "M1", f"{w}: invalid_answers entry must be an object", vid)
            continue
        minimal = a.get("kind") == "minimal"
        check_fields(rep, a, [("id", "str", 1), ("text", "str", 1), ("kind", "str", 1), ("pair_of", "str", minimal),
                              ("violates", "str", minimal), ("fails", "list", 1), ("origin", "str", 1), ("note", "str", 0)],
                     f"{w} invalid answer {a.get('id', '?')}", vid)
        if isinstance(a.get("kind"), str) and a["kind"] not in ("minimal", "copy"):
            rep.add("ERROR", "M1", f"{w} invalid answer {a.get('id')}: kind must be minimal or copy", vid)
        if isinstance(a.get("id"), str):
            if not re.match(r"^X\d+$" if minimal else r"^C\d+$", a["id"]):
                rep.add("ERROR", "M1", f"{w}: invalid answer id {a['id']!r} must be X<n> (minimal) or C<n> (copy)", vid)
            if a["id"] in seen:
                rep.add("ERROR", "M1", f"{w}: duplicate answer id {a['id']}", vid)
            seen.add(a["id"])
        if isinstance(a.get("origin"), str) and a["origin"] not in INVALID_ORIGINS:
            rep.add("ERROR", "M1", f"{w} invalid answer {a.get('id')}: origin {a['origin']!r} not in {INVALID_ORIGINS}", vid)


def lint_m1_review(rep, card, vids):
    hr = card["human_review"]
    check_fields(rep, hr, [("reviewers", "list", 1), ("variants", "obj", 1), ("adjudications", "list", 1)], "human_review")
    vs = hr.get("variants")
    if isinstance(vs, dict):
        for vid in vids:
            if vid not in vs:
                rep.add("ERROR", "M1", f"human_review.variants has no key for variant {vid}", vid)
                continue
            if not isinstance(vs[vid], dict) or set(vs[vid]) != {"annotator_1", "annotator_2"}:
                rep.add("ERROR", "M1", "human_review slot needs exactly annotator_1 and annotator_2", vid)
                continue
            for k in ("annotator_1", "annotator_2"):
                s = vs[vid][k]
                if s is None:
                    continue
                if not isinstance(s, dict):
                    rep.add("ERROR", "M1", f"{k} slot must be null or an object", vid)
                    continue
                check_fields(rep, s, [("reviewer_id", "str", 1), ("date", "str", 1), ("role", "str", 1), ("realism", "int", 1),
                                      ("licence", "obj", 1)], f"{k} slot", vid)
                if isinstance(s.get("role"), str) and s["role"] not in REVIEW_ROLES:
                    rep.add("ERROR", "M1", f"{k} slot: role {s['role']!r} not in {REVIEW_ROLES}", vid)
                if isinstance(s.get("realism"), int) and not isinstance(s.get("realism"), bool) and not 1 <= s["realism"] <= 5:
                    rep.add("ERROR", "M1", f"{k} slot: realism must be 1 to 5", vid)
                for u, lab in (s.get("licence") or {}).items() if isinstance(s.get("licence"), dict) else []:
                    if lab not in V2.LABELS:
                        rep.add("ERROR", "M1", f"{k} slot: label {lab!r} for {u} not in {V2.LABELS}", vid, u)
        for vid in vs:
            if vid not in vids:
                rep.add("ERROR", "M1", f"human_review.variants has a key for unknown variant {vid}")
    for a in hr.get("adjudications", []) if isinstance(hr.get("adjudications"), list) else []:
        if not isinstance(a, dict):
            rep.add("ERROR", "M1", "adjudications entry must be an object")
            continue
        check_fields(rep, a, [("variant", "str", 1), ("field", "str", 1), ("unit", "str", a.get("field") == "licence"),
                              ("value", "str", 1), ("decided_by", "str", 1), ("date", "str", 1), ("note", "str", 0)],
                     "adjudication")
        if a.get("field") not in (None, "role", "licence"):
            rep.add("ERROR", "M1", f"adjudication field {a.get('field')!r} must be role or licence", a.get("variant"))
        if a.get("field") == "licence" and isinstance(a.get("value"), str) and a["value"] not in V2.LABELS:
            rep.add("ERROR", "M1", f"adjudication value {a['value']!r} not in {V2.LABELS}", a.get("variant"), a.get("unit"))
        if a.get("field") == "role" and isinstance(a.get("value"), str) and a["value"] not in REVIEW_ROLES:
            rep.add("ERROR", "M1", f"adjudication role value {a['value']!r} not in {REVIEW_ROLES}", a.get("variant"))


# ---------------------------------------------------------------- M2 to M6, P1, P2
def load_registry(name):
    """List of ids of data/registry/<name>.json, or None when the file does not exist."""
    p = os.path.join(REGISTRY_DIR, name + ".json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        for k in ("ids", name):
            if isinstance(data.get(k), list):
                data = data[k]
                break
        else:
            return list(data)
    return [x["id"] if isinstance(x, dict) else x for x in data]


def lint_meta(ctx):
    rep, card, release = ctx.rep, ctx.card, ctx.release
    cid = card.get("id")
    if card.get("schema") != "seed-card-v2":
        rep.add("ERROR", "M2", f"schema must be 'seed-card-v2', found {card.get('schema')!r}")
    if not isinstance(cid, str) or not ID_RE.match(cid):
        rep.add("ERROR", "M2", f"id {cid!r} must match {ID_RE.pattern}")
    elif ctx.path:
        stem = os.path.splitext(os.path.basename(ctx.path))[0]
        if stem != cid:
            rep.add("ERROR", "M2", f"id {cid!r} differs from the file name {stem!r}")
    st = card.get("status")
    if st not in STATUSES:
        rep.add("ERROR", "M3", f"status {st!r} must be one of {STATUSES}")
    elif release and st != "accepted":
        rep.add("ERROR", "M3", f"release mode needs status 'accepted', found {st!r}")
    ma = card.get("model_assistance")
    if ma not in ASSISTANCE:
        rep.add("ERROR", "M4", f"model_assistance {ma!r} must be one of {ASSISTANCE}")
    elif ma != "none":
        log = card.get("model_assistance_log")
        if not isinstance(log, dict):
            rep.add("ERROR", "M4", "model_assistance_log is missing")
        else:
            for k in ("model", "date", "scope", "prompt_ref"):
                if not nonempty(log.get(k)):
                    rep.add("ERROR", "M4", f"model_assistance_log.{k} is empty")
    for k, rx in (("author_id", AUTHOR_RE), ("domain", SNAKE_RE), ("relation_family", SNAKE_RE),
                  ("template_group_id", GROUP_RE), ("provenance_group_id", GROUP_RE)):
        if not isinstance(card.get(k), str) or not rx.match(card[k]):
            rep.add("ERROR", "M5", f"{k} {card.get(k)!r} must match {rx.pattern}")
    for k, name in (("domain", "domains"), ("relation_family", "relation_families")):
        try:
            ids = load_registry(name)
        except (OSError, ValueError, KeyError, TypeError) as e:
            rep.add("ERROR", "M6", f"registry data/registry/{name}.json is unreadable: {e}")
            continue
        if ids is None:
            rep.add("PENDING", "M6", f"registry data/registry/{name}.json does not exist yet; {k} {card.get(k)!r} not verified")
        elif card.get(k) not in ids:
            rep.add("ERROR", "M6", f"{k} {card.get(k)!r} is not in data/registry/{name}.json")
    pv = card.get("provenance")
    if isinstance(pv, dict):
        st = pv.get("source_type")
        if st not in SOURCE_TYPES:
            rep.add("ERROR", "P1", f"provenance.source_type {st!r} must be one of {SOURCE_TYPES}")
        if not nonempty(pv.get("case")):
            rep.add("ERROR", "P1", "provenance.case is empty")
        if st == "original_scenario":
            if not nonempty(pv.get("original_authoring")):
                rep.add("ERROR", "P1", "original_scenario needs provenance.original_authoring (the author's signed line)")
        else:
            refs = pv.get("references") or []
            if not refs or not all(isinstance(r, dict) and nonempty(r.get("citation")) for r in refs) \
                    or not any(isinstance(r, dict) and (r.get("url") or r.get("doi")) for r in refs):
                rep.add("ERROR", "P1", "provenance needs references with citations, at least one with a url or doi")
        if pv.get("urls_checked_by_human") is not True:
            rep.add("PENDING", "P2", "reference URLs not yet opened and checked by a person")


# ---------------------------------------------------------------- S: source example and spans
def target_pieces(card):
    """Texts a leak detector must not match: the target and the user's own words, per variant (v1 rule)."""
    pieces = [("target", L1.target_text(card))]
    for v in card["variants"]:
        pieces.append((f"variant {v['id']} target", L1.target_text(card, v)))
        pieces.append((f"variant {v['id']} own words", v["text"].replace("{EX}", " ")))
    return pieces


def lint_spans(rep, card, core_only=False):
    """S1 to S13, S15 and S16: everything that depends only on the example, its spans and its details.
    core_only=True stops after S7 (the part that needs only the example, details and spans; used by
    scripts/spans_from_markup.py)."""
    se = card["source_example"]
    text = se["text"]
    spans = card["source_spans"]
    details = {d["id"]: d for d in se["incidental_details"]}
    rel_ids = [u["id"] for u in card["relation_units"]]
    det_ids = [d["id"] for d in se["incidental_details"]]

    joined = "".join(s["text"] for s in spans)
    tiles = joined == text
    if not tiles:
        k = next((i for i, (a, b) in enumerate(zip(joined, text)) if a != b), min(len(joined), len(text)))
        rep.add("ERROR", "S1", f"span texts do not concatenate to source_example.text (lengths {len(joined)} vs {len(text)}; "
                               f"first difference at offset {k}: spans {joined[k:k + 25]!r} vs example {text[k:k + 25]!r})")
    seen = set()
    for s in spans:
        sid = s["id"]
        if not SPAN_ID_RE.match(sid):
            rep.add("ERROR", "S2", f"span id {sid!r} must match {SPAN_ID_RE.pattern}")
        if sid in seen:
            rep.add("ERROR", "S2", f"duplicate span id {sid}")
        seen.add(sid)
        if s["text"] == "":
            rep.add("ERROR", "S3", f"span {sid} has empty text")
        kind, unit = s["kind"], s.get("unit")
        if kind not in ("relation", "detail", "context"):
            rep.add("ERROR", "S4", f"span {sid}: kind {kind!r} must be relation, detail or context", unit=unit)
        elif kind == "relation" and unit not in rel_ids:
            rep.add("ERROR", "S4", f"span {sid}: relation span names unit {unit!r}, not in relation_units", unit=unit)
        elif kind == "detail" and unit not in det_ids:
            rep.add("ERROR", "S4", f"span {sid}: detail span names unit {unit!r}, not in incidental_details", unit=unit)
        elif kind == "context" and unit:
            rep.add("ERROR", "S4", f"span {sid}: context span must not name a unit (found {unit})", unit=unit)
        if kind in ("relation", "detail") and s["text"] and not any(ch.isalnum() for ch in s["text"]):
            rep.add("WARN", "S9", f"span {sid} ({kind}, unit {unit}) has no letter or digit and should be kind context: {s['text']!r}", unit=unit)
    all_ids = rel_ids + det_ids
    for u in sorted({x for x in all_ids if all_ids.count(x) > 1}):
        rep.add("ERROR", "S5", f"unit id {u} is defined more than once across relation_units and incidental_details", unit=u)
    owned = {s.get("unit") for s in spans if s["kind"] != "context"}
    for u in all_ids:
        if u not in owned:
            rep.add("ERROR", "S5", f"unit {u} owns no span", unit=u)

    # S6, S7: detectors and spans
    offs = span_offsets(spans)
    matches = []   # (start, end, unit, matched text)
    for did, d in details.items():
        for rx in detector_regexes(d):
            for m in rx.finditer(text):
                if m.end() > m.start():
                    matches.append((m.start(), m.end(), did, m.group(0)))
        for s in spans:
            if s["kind"] == "detail" and s.get("unit") == did and not any(rx.search(s["text"]) for rx in detector_regexes(d)):
                rep.add("ERROR", "S6", f"detail span {s['id']} {s['text']!r} contains no match of the detector of {did}", unit=did)
    if tiles:
        for a, b, did, mt in sorted(matches):
            inside = any(s["kind"] == "detail" and s.get("unit") == did and o[0] <= a and b <= o[1] for s, o in zip(spans, offs))
            if not inside:
                where = [s["id"] for s, o in zip(spans, offs) if o[0] < b and a < o[1]]
                rep.add("ERROR", "S7", f"detector of {did} matches {mt!r} at offset {a}, which does not lie inside one {did} span "
                                       f"(it touches spans {where})", unit=did)
        by_pos = sorted(matches)
        for i, (a, b, did, mt) in enumerate(by_pos):
            for a2, b2, did2, mt2 in by_pos[i + 1:]:
                if a2 >= b:
                    break
                if did2 != did:
                    rep.add("ERROR", "S7", f"detectors of {did} ({mt!r}) and {did2} ({mt2!r}) match overlapping characters at offset {a2}", unit=did)

    if core_only:
        return
    # S8: detectors match the example, never the target or the user's own words
    pieces = target_pieces(card)
    ctext = L1.source_text(card, perturbed=True)
    for did, d in details.items():
        for who, src, ex in (("", d, text), ("control ", d.get("control") or {}, ctext)):
            if who and not src:
                continue
            terms = [(t, C.term_regex(t)) for t in src.get("leak_terms", []) or []]
            if src.get("leak_regex"):
                terms.append((src["leak_regex"], re.compile(src["leak_regex"], re.I)))
            for t, rx in terms:
                if not rx.search(ex):
                    rep.add("ERROR", "S8", f"{who}detector {t!r} of {did} matches nothing in the {who}example", unit=did)
                for label, tt in pieces:
                    if rx.search(tt):
                        rep.add("ERROR", "S8", f"{who}detector {t!r} of {did} also matches the {label}; banning it is stricter than the task", unit=did)
                        break

    # S10: controls
    for did, d in details.items():
        c = d.get("control")
        if not c:
            continue
        frm, to = c["from"], c["to"]
        if frm == to:
            rep.add("ERROR", "S10", f"control of {did}: 'to' equals 'from'", unit=did)
        if not frm or frm not in text:
            rep.add("ERROR", "S10", f"control of {did}: 'from' {frm!r} does not occur in the example", unit=did)
        elif tiles:
            total = text.count(frm)
            inside = sum(s["text"].count(frm) for s in spans if s.get("unit") == did)
            if inside != total:
                rep.add("ERROR", "S10", f"control of {did}: {total - inside} of {total} occurrence(s) of {frm!r} lie outside the spans of {did}", unit=did)
        if not (c.get("leak_terms") or c.get("leak_regex")):
            rep.add("ERROR", "S10", f"control of {did} has no leak_terms/leak_regex, so the control build would never detect the detail", unit=did)
    if tiles and any(d.get("control") for d in details.values()):
        if "".join(s["text"] for s in V2.control_spans(card)) != ctext:
            rep.add("ERROR", "S10", "control spans do not tile the control example (seed_lint_v1.source_text(perturbed=True))")

    if not any(u.get("main") for u in card["relation_units"]):
        rep.add("ERROR", "S11", "no relation unit has main: true")
    for a, b in zip(spans, spans[1:]):
        if a["text"] and b["text"] and a["text"][-1].isalnum() and b["text"][0].isalnum():
            rep.add("WARN", "S12", f"span boundary between {a['id']} and {b['id']} falls inside a word ({a['text'][-12:]!r}|{b['text'][:12]!r})")
    for s in spans:
        if s["kind"] == "context" and len(s["text"]) > 160:
            sents = [x for x in re.split(r"(?<=[.!?])\s+", s["text"]) if len(x.split()) >= 8]
            if sents:
                rep.add("WARN", "S13", f"context span {s['id']} has {len(s['text'])} characters and a sentence of {len(sents[0].split())} words; "
                                       f"probably an unlabelled relation: {s['text'][:60]!r}")
    n = L1.count_sentences(text)
    need = 20 if se["length"] == "long" else 8
    if n < need:
        rep.add("WARN", "S15", f"source example has {n} prose sentences; at least {need} expected for length {se['length']!r}")

    # S16
    feats = se.get("shared_surface_features") or []
    if any(v["role"] == "counter" for v in card["variants"]) and len(feats) < 3:
        rep.add("ERROR", "S16", f"card has a counter variant but only {len(feats)} shared_surface_features (at least 3 required)")
    tt = L1.target_text(card)
    for f in feats:
        if not isinstance(f, dict):
            rep.add("ERROR", "S16", "shared_surface_features entry must be an object")
            continue
        if L1.norm(f.get("source_quote", "#")) not in L1.norm(text):
            rep.add("ERROR", "S16", f"surface feature {f.get('feature')!r}: source_quote not in the example")
        if L1.norm(f.get("target_quote", "#")) not in L1.norm(tt):
            rep.add("ERROR", "S16", f"surface feature {f.get('feature')!r}: target_quote not in the target")


def lint_s14(ctx):
    """S14: at least 3 detail units (ERROR); at least 3 MUST_NOT in at least one variant (WARN)."""
    n = len(ctx.card["source_example"]["incidental_details"])
    if n < 3:
        ctx.rep.add("ERROR", "S14", f"{n} detail unit(s); at least 3 required")
        return
    best = 0
    for v in ctx.card["variants"]:
        best = max(best, sum(1 for u, i in ctx.reg.items() if i["kind"] == "detail" and ctx.label(v, u) == "MUST_NOT"))
    if best < 3:
        ctx.rep.add("WARN", "S14", f"at most {best} detail unit(s) are MUST_NOT in any one variant; at least 3 expected in some variant")


def lint_s17(ctx):
    """S17: the example occurs exactly once in the built prompt of every variant (single turn, and message 2 of multi turn)."""
    ex = ctx.card["source_example"]["text"]
    for v in ctx.card["variants"]:
        if not ctx.has_ex(v):
            continue   # Q1 reports it
        n = ctx.prompt(v).count(ex)
        m = ctx.multi(v)
        total = sum(x["content"].count(ex) for x in m)
        if n != 1 or m[2]["content"].count(ex) != 1 or total != 1:
            ctx.rep.add("ERROR", "S17", f"the example occurs {n} time(s) in the single-turn prompt and {total} time(s) in the "
                                        f"multi-turn messages (message 2: {m[2]['content'].count(ex)}); it must occur exactly once", v["id"])


# ---------------------------------------------------------------- C: licence
def evidence_problem(ctx, v, q):
    """None when the quote satisfies C3, else the reason it does not."""
    ex = ctx.card["source_example"]["text"]
    prompt = ctx.prompt(v)
    occ = occurrences(prompt, q)
    if not occ:
        return "not an exact, case-sensitive substring of the single-turn prompt"
    s = prompt.find(ex)
    e = s + len(ex)
    if s != -1 and not any(i + len(q) <= s or i >= e for i in occ):
        return "occurs only inside the source example (the example cannot license its own transfer)"
    for m in ctx.multi(v):
        c = m["content"]
        es = c.find(ex)
        if any(es == -1 or i + len(q) <= es or i >= es + len(ex) for i in occurrences(c, q)):
            return None
    return "does not lie inside one message of the multi-turn build (it straddles the target and the example turn)"


def lint_licence(ctx):
    rep, card = ctx.rep, ctx.card
    controlled = V2.detail_ids_with_control(card)
    for v in card["variants"]:
        vid = v["id"]
        entries, problems = ctx.ent(v)
        for u, txt in problems:
            rep.add("ERROR", "C1", txt, vid, u)
        for u, e in entries.items():
            lab, basis = e.get("label"), e.get("basis")
            kind = e["_kind"]
            tag = " (from licence.defaults)" if e["_default"] else ""
            eff = lab
            if lab not in V2.LABELS:
                rep.add("ERROR", "C2", f"label {lab!r} must be one of {V2.LABELS}{tag}", vid, u)
                continue
            if basis not in V2.BASES:
                rep.add("ERROR", "C2", f"basis {basis!r} must be one of {V2.BASES}{tag}", vid, u)
                continue
            if lab == "UNCLEAR":
                eff = e.get("proposed")
                if eff not in ("MUST", "MAY", "MUST_NOT"):
                    rep.add("ERROR", "C5", f"UNCLEAR entry needs proposed in MUST, MAY, MUST_NOT; found {eff!r}{tag}", vid, u)
                    eff = None
                if not nonempty(e.get("note")):
                    rep.add("ERROR", "C5", f"UNCLEAR entry needs a non-empty note for reviewers{tag}", vid, u)
            if eff in ("MUST", "MUST_NOT") and basis == "DEFAULT":
                rep.add("ERROR", "C2", f"{lab}{' (proposed ' + eff + ')' if lab == 'UNCLEAR' else ''} cannot have basis DEFAULT: "
                                       f"no MUST or MUST_NOT without evidence{tag}", vid, u)
            if eff == "MAY" and basis == "INFERRED":
                rep.add("ERROR", "C2", f"MAY cannot have basis INFERRED (MAY is DEFAULT or a stated permission, DIRECT){tag}", vid, u)
            if basis in ("DIRECT", "INFERRED"):
                q = e.get("evidence")
                if not nonempty(q):
                    rep.add("ERROR", "C3", f"{basis} entry needs evidence (an exact substring of the prompt){tag}", vid, u)
                elif ctx.has_ex(v):
                    why = evidence_problem(ctx, v, q)
                    if why:
                        rep.add("ERROR", "C3", f"evidence {q[:70]!r}: {why}{tag}", vid, u)
            if basis == "INFERRED":
                imp = e.get("implication")
                if imp not in V2.IMPLICATIONS:
                    rep.add("ERROR", "C4", f"INFERRED entry needs implication from {sorted(V2.IMPLICATIONS)}; found {imp!r}{tag}", vid, u)
                else:
                    want, roles, kinds = V2.IMPLICATIONS[imp]
                    if eff != want:
                        rep.add("ERROR", "C4", f"implication {imp} gives {want}, but the entry is {eff}{tag}", vid, u)
                    if v["role"] not in roles:
                        rep.add("ERROR", "C4", f"implication {imp} is not allowed for role {v['role']} (allowed: {sorted(roles)}){tag}", vid, u)
                    if kind not in kinds:
                        rep.add("ERROR", "C4", f"implication {imp} is not allowed for {kind} units (allowed: {sorted(kinds)}){tag}", vid, u)
                    if imp == "relation_transfer" and not ctx.reg[u]["main"]:
                        rep.add("WARN", "C4", f"relation_transfer on {u}, which is not a main relation unit{tag}", vid, u)
            if u in controlled and eff == "MUST":
                rep.add("WARN", "C8", f"{u} has an incidental-detail control but is MUST here; this variant gets no control prompt", vid, u)
        if v["cue"] == "stated" and not any(e.get("basis") == "DIRECT" for e in entries.values()):
            rep.add("WARN", "C6", "stated-cue variant has no DIRECT licence entry", vid)
        if ctx.has_ex(v):
            pieces = own_words(v).split("\u0000")
            shaped = [u for u, e in entries.items() if V2.entry_label(e) in ("MUST", "MUST_NOT") and nonempty(e.get("evidence"))
                      and e.get("basis") in ("DIRECT", "INFERRED") and any(e["evidence"] in p for p in pieces)]
            if not shaped:
                rep.add("WARN", "C7", "no MUST or MUST_NOT entry takes its evidence from the variant's own words; "
                                      "the role and cue do not shape the licence (expected only where a target rule decides)", vid)
        left = V2.unresolved_units(card, v)
        if left and not ctx.release:
            rep.add("PENDING", "C9", f"{len(left)} UNCLEAR unit(s) without a final label ({', '.join(left)}); variant is in the ambiguity set", vid)


# ---------------------------------------------------------------- K: checks
def named_units(item):
    return list(item["check"].get("units") or [])


def lint_k6(ctx, v, item, where):
    """K6: the v1 check lint. v is None for a card-level rule check."""
    rep, card = ctx.rep, ctx.card
    c = item["check"]
    cid, spec = c["id"], c["spec"]
    vid = v["id"] if v else None
    if not spec:
        rep.add("ERROR", "K6", f"{where} {cid}: empty spec", vid)
        return
    kind = spec[0]
    if kind not in V2.KNOWN_KINDS:
        rep.add("ERROR", "K6", f"{where} {cid}: unknown check kind {kind!r}", vid)
        return
    if kind in V2.JUDGE_KINDS:
        return
    if v is not None and not ctx.has_ex(v):
        return   # Q1 reports it; the prompt cannot be built
    prompt = ctx.prompt(v) if v else L1.target_text(card) + "\n" + card["source_example"]["text"]
    basis = c.get("basis")
    ref = ""
    if basis:
        btype = basis.get("type")
        if btype == "stated":
            q = basis.get("quote", "")
            if not q or L1.norm(q) not in L1.norm(prompt):
                rep.add("ERROR", "K6", f"{where} {cid}: stated quote not found in the prompt: {q[:60]!r}", vid)
            ref = q
        elif btype == "target_rule":
            rr = {r["id"]: r for r in L1.rules_for(card, v)}
            rid = basis.get("rule") or item["rule"]
            if rid not in rr:
                rep.add("ERROR", "K6", f"{where} {cid}: basis rule {rid} is not among the target rules of this variant", vid)
            else:
                ref = rr[rid]["text"]
        elif btype == "role_implied":
            q = basis.get("quote")
            if q and L1.norm(q) not in L1.norm(prompt):
                rep.add("ERROR", "K6", f"{where} {cid}: role_implied quote not found in the prompt: {q[:60]!r}", vid)
            ref = q or ""
        else:
            rep.add("ERROR", "K6", f"{where} {cid}: unknown basis type {btype!r}", vid)
            return
    elif item["list"] == "rule":
        ref = item["rule_text"] or ""
    elif v is not None:
        ents = ctx.ent(v)[0]
        ref = " ".join(ents[u]["evidence"] for u in named_units(item) if u in ents and isinstance(ents[u].get("evidence"), str))
    if kind in V1.BOUND_ARGS:
        have = L1.numbers_in(ref)
        for i in V1.BOUND_ARGS[kind]:
            if i >= len(spec):
                continue
            for x in spec[i] if isinstance(spec[i], list) else [spec[i]]:
                if not C.is_num(x):
                    continue
                if kind == "json_len_between" and i == 2 and x <= 1:
                    continue   # a lower bound of 0 or 1 is not a tightening
                if float(x) not in have:
                    rep.add("ERROR", "K6", f"{where} {cid}: bound {x} in {kind} does not appear in its basis text "
                                           f"({ref[:60]!r}); the check may be stricter than the instruction", vid)
    if kind in V1.TERM_ARGS:
        missing = [t for t in spec[V1.TERM_ARGS[kind]] if L1.norm(t) not in L1.norm(prompt)]
        if missing:
            rep.add("ERROR", "K6", f"{where} {cid}: terms never mentioned in the prompt: {missing[:5]} (hidden ban or requirement)", vid)
    if kind in V1.REGEX_ARGS:
        try:
            found = re.search(spec[V1.REGEX_ARGS[kind]], prompt, re.I)
        except re.error as e:
            rep.add("ERROR", "K6", f"{where} {cid}: regex does not compile: {e}", vid)
            found = True
        if not found:
            rep.add("ERROR", "K6", f"{where} {cid}: regex matches nothing in the prompt (hidden ban or requirement)", vid)
    if kind == "leak_absent" and (len(spec) < 2 or ctx.reg.get(spec[1], {}).get("kind") != "detail"):
        rep.add("ERROR", "K6", f"{where} {cid}: leak_absent names {spec[1:2]}, which is not an incidental detail of this card", vid)
    if kind == "py_test" and (len(spec) < 2 or spec[1] not in (card.get("tests") or {})):
        rep.add("ERROR", "K6", f"{where} {cid}: test {spec[1:2]} is not defined in tests", vid)


def lint_checks(ctx):
    rep, card = ctx.rep, ctx.card
    variants = card["variants"]
    # card-level rule checks, once
    card_items = [it for it in V2.iter_checks(card, variants[0]) if it["scope"] == "card"] if variants else []
    ids = [it["check"]["id"] for it in card_items]
    for x in sorted({i for i in ids if ids.count(i) > 1}):
        rep.add("ERROR", "K1", f"card-level rule check id {x} is used more than once")
    for it in card_items:
        c = it["check"]
        for u in named_units(it):
            if u not in ctx.reg:
                rep.add("ERROR", "K1", f"rule check {c['id']} names unknown unit {u}", unit=u)
                continue
            labs = {}
            for v in variants:
                lab = ctx.label(v, u)
                if lab is not None:
                    labs.setdefault(lab, []).append(v["id"])
            if len(labs) > 1:
                rep.add("ERROR", "K2", f"card-level rule check {c['id']} names {u}, whose label differs across variants {labs}", unit=u)
            elif labs:
                lab = next(iter(labs))
                if lab == "MAY":
                    rep.add("ERROR", "K4", f"card-level rule check {c['id']} names {u}, which is MAY", unit=u)
                elif lab not in ("MUST", "MUST_NOT"):
                    rep.add("ERROR", "K2", f"card-level rule check {c['id']} names {u}, whose label is {lab}", unit=u)
        if c["spec"][:1] == ["leak_absent"] and len(c["spec"]) > 1 and c["spec"][1] not in named_units(it):
            rep.add("ERROR", "K5", f"rule check {c['id']} is leak_absent on {c['spec'][1]} but does not list it in units", unit=c["spec"][1])
        lint_k6(ctx, None, it, "rule check")
    # per variant
    for v in variants:
        vid = v["id"]
        items = V2.iter_checks(card, v)
        seen = {}
        for it in items:
            c = it["check"]
            if it["scope"] != "card":
                seen.setdefault(c["id"], 0)
                seen[c["id"]] += 1
        card_ids = set(ids)
        for x, n in sorted(seen.items()):
            if n > 1 or x in card_ids:
                rep.add("ERROR", "K1", f"check id {x} is not unique within the variant (rule checks included)", vid)
        named = set()
        for it in items:
            c, lst = it["check"], it["list"]
            units = named_units(it)
            if lst in ("must_transfer", "must_not_transfer", "probe") and not units:
                rep.add("ERROR", "K1", f"{lst} check {c['id']} has no units", vid)
            for u in units:
                if u not in ctx.reg:
                    rep.add("ERROR", "K1", f"check {c['id']} names unknown unit {u}", vid, u)
                    continue
                if it["scope"] == "card":
                    named.add(u)
                    continue   # K2 and K4 were reported once above
                lab = ctx.label(v, u)
                if lst != "probe":
                    named.add(u)
                if lab is None:
                    continue
                if lab == "MAY" and lst != "probe":
                    rep.add("ERROR", "K4", f"{lst} check {c['id']} names {u}, which is MAY", vid, u)
                elif (lst == "must_transfer" and lab != "MUST") or (lst == "must_not_transfer" and lab != "MUST_NOT") \
                        or (lst == "rule" and lab not in ("MUST", "MUST_NOT")) or (lst == "probe" and lab != "MAY"):
                    rep.add("ERROR", "K2", f"{lst} check {c['id']} names {u}, whose label is {lab}", vid, u)
            if c["spec"][:1] == ["leak_absent"] and len(c["spec"]) > 1 and c["spec"][1] not in units:
                if it["scope"] != "card":
                    rep.add("ERROR", "K5", f"check {c['id']} is leak_absent on {c['spec'][1]} but does not list it in units", vid, c["spec"][1])
            if it["scope"] != "card":
                lint_k6(ctx, v, it, f"{lst} check" if lst != "rule" else f"rules_add {it['rule']} check")
        for u in ctx.reg:
            if ctx.label(v, u) in ("MUST", "MUST_NOT") and u not in named:
                rep.add("ERROR", "K3", f"{ctx.label(v, u)} unit is named by no check of this variant", vid, u)
    # K7, K7r
    judges = [(v["id"], it["check"]["id"]) for v in variants for it in V2.iter_checks(card, v) if V2.is_judge(it["check"])]
    judges = sorted(set(judges))
    if judges:
        if not ctx.release:
            for vid, cid in judges:
                q = next((it["check"].get("what", "") for it in V2.iter_checks(card, next(x for x in variants if x["id"] == vid))
                          if it["check"]["id"] == cid), "")
                rep.add("PENDING", "K7", f"judge check {cid} is not run until the judge passes its audit: {q[:90]}", vid)
        elif not judge_passed():
            rep.add("ERROR", "K7r", f"card has {len(judges)} judge check(s) and {display_path(JUDGE_STATUS)} does not mark the judge as passed")
    m = card.get("marker")
    if m is not None:
        mu = m.get("units")
        if not isinstance(mu, list) or not mu:
            rep.add("ERROR", "K8", "marker.units is missing or empty")
        else:
            for u in mu:
                if u not in ctx.reg:
                    rep.add("ERROR", "K8", f"marker.units names unknown unit {u}", unit=u)


def display_path(p):
    p = os.path.abspath(p)
    return os.path.relpath(p, ROOT) if p.startswith(ROOT) else p


def judge_passed():
    try:
        with open(JUDGE_STATUS, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return False
    return d.get("passed") is True or d.get("status") == "passed"


# ---------------------------------------------------------------- A: answers
def rule_ids(card, v):
    return {r["id"] for r in L1.rules_for(card, v)}


def lint_answers(ctx):
    rep, card = ctx.rep, ctx.card
    if ctx.gold and rep.count("ERROR"):
        ctx.gold = False   # as in v1: answers are run only on a card whose rules hold, otherwise the failures are noise
        rep.skipped = "gold answers (A3, A4, A7, A12, A13) were not run because of earlier errors"
    for v in card["variants"]:
        vid = v["id"]
        entries = ctx.ent(v)[0]
        valid, invalid = v["valid_answers"], v["invalid_answers"]
        items = V2.iter_checks(card, v)
        by_id = {it["check"]["id"]: it for it in items if it["list"] != "probe"}
        judge_ids = {it["check"]["id"] for it in items if V2.is_judge(it["check"])}
        scoring = [it for it in items if it["list"] != "probe" and not V2.is_judge(it["check"])]
        # A1, A2
        if len(valid) < 2:
            rep.add("ERROR", "A1", f"{len(valid)} valid answer(s); at least 2 required", vid)
        forms = {}
        for a in valid:
            forms.setdefault(V2.normalise_answer(a["text"], card), []).append(a["id"])
        for ids_ in forms.values():
            if len(ids_) > 1:
                rep.add("ERROR", "A2", f"valid answers {ids_} have the same normalised form", vid)
        # A5
        may_det = [u for u, i in ctx.reg.items() if i["kind"] == "detail" and ctx.label(v, u) == "MAY"]
        if may_det and not any(set(a.get("uses_may") or []) & set(may_det) for a in valid):
            rep.add("WARN", "A5", f"MAY detail unit(s) {may_det} exist but no valid answer lists one in uses_may; "
                                  f"nothing proves that no check bans them", vid)
        # A3, A4 (gold)
        if ctx.gold:
            V2.warm_cache(card, v, [a["text"] for a in valid + invalid])
            control = V2.control_applies(card, v)
            for a in valid:
                for pert in (False, True) if control else (False,):
                    r = V2.score_v2(a["text"], card, v, perturbed=pert)
                    if not r["joint"]:
                        bad = V2.failing_checks(a["text"], card, v, perturbed=pert)
                        rep.add("ERROR", "A3", f"valid answer {a['id']} is not joint-valid{' under the control' if pert else ''}: "
                                               f"format_ok={r['format_ok']} failing checks {bad}", vid)
                for u in a.get("uses_may") or []:
                    lab = ctx.label(v, u)
                    if u not in ctx.reg:
                        rep.add("ERROR", "A4", f"valid answer {a['id']}: uses_may names unknown unit {u}", vid, u)
                    elif lab != "MAY":
                        rep.add("ERROR", "A4", f"valid answer {a['id']}: uses_may lists {u}, whose label is {lab}, not MAY", vid, u)
                    elif ctx.reg[u]["kind"] == "detail":
                        ans = V2.parse_answer(a["text"], card)
                        if ans["format_ok"] and V2.run_check_v2(["leak_absent", u], ans, card)[0]:
                            rep.add("ERROR", "A4", f"valid answer {a['id']}: uses_may lists {u} but its detector does not fire on the answer", vid, u)
        # A6, A7, A8, A9, A10, A11, A12
        minimal = [a for a in invalid if a["kind"] == "minimal"]
        if len(minimal) < 2:
            rep.add("ERROR", "A6", f"{len(minimal)} minimal invalid answer(s); at least 2 required", vid)
        vtext = {a["id"]: a["text"] for a in valid}
        rids = rule_ids(card, v)
        violated_units = set()
        for a in invalid:
            for f in a["fails"]:
                for u in named_units(by_id[f]) if f in by_id else []:
                    violated_units.add(u)
            if ctx.gold:
                ans = V2.parse_answer(a["text"], card)
                if not ans["format_ok"]:
                    rep.add("ERROR", "A7", f"invalid answer {a['id']} is not parseable (format failure is not a licence violation)", vid)
                else:
                    failing = set(V2.failing_checks(a["text"], card, v))
                    want = set(a["fails"]) - judge_ids
                    if failing != want:
                        rep.add("ERROR", "A7", f"invalid answer {a['id']}: failing checks {sorted(failing)} differ from fails {sorted(a['fails'])}"
                                               f" (missing {sorted(want - failing)}, unexpected {sorted(failing - want)})", vid)
                    if a["kind"] == "copy" and not (failing & {it["check"]["id"] for it in scoring if it["list"] in ("must_transfer", "must_not_transfer")}):
                        rep.add("ERROR", "A12", f"copy answer {a['id']} fails no must_transfer or must_not_transfer check; the checks do not catch copying", vid)
        for a in minimal:
            aid, viol = a["id"], a["violates"]
            if a["pair_of"] not in vtext:
                rep.add("ERROR", "A8", f"minimal answer {aid}: pair_of {a['pair_of']!r} is not a valid answer of this variant", vid)
            if viol in ctx.reg:
                raw = entries.get(viol, {}).get("label")
                if raw not in ("MUST", "MUST_NOT"):
                    rep.add("ERROR", "A8", f"minimal answer {aid}: violates {viol}, whose label is {raw}; only MUST or MUST_NOT units can be violated", vid, viol)
                elif not any(viol in named_units(it) for it in scoring):
                    rep.add("ERROR", "A8", f"minimal answer {aid}: {viol} is tested only by judge checks (or by none)", vid, viol)
            elif viol not in rids:
                rep.add("ERROR", "A8", f"minimal answer {aid}: violates {viol!r} is neither a unit nor a target rule id of this variant", vid)
            if not a["fails"]:
                rep.add("ERROR", "A8", f"minimal answer {aid}: fails is empty", vid)
            for f in a["fails"]:
                it = by_id.get(f)
                if f in judge_ids:
                    rep.add("ERROR", "A8", f"minimal answer {aid}: fails lists the judge check {f}; judge checks are never run", vid)
                elif it is None:
                    rep.add("ERROR", "A8", f"minimal answer {aid}: fails lists {f}, which is not a check of this variant", vid)
                elif not (viol in named_units(it) or it["rule"] == viol):
                    rep.add("ERROR", "A8", f"minimal answer {aid}: failing check {f} does not test {viol} (it names {named_units(it)}"
                                           f"{', rule ' + it['rule'] if it['rule'] else ''})", vid)
            if a["pair_of"] in vtext:
                ratio = difflib.SequenceMatcher(None, vtext[a["pair_of"]], a["text"]).ratio()
                if ratio < 0.7:
                    rep.add("WARN", "A9", f"minimal answer {aid} is not one edit from {a['pair_of']} (similarity {ratio:.2f} < 0.70)", vid)
        if minimal and not any(a["violates"] in ctx.reg for a in minimal):
            rep.add("ERROR", "A10", "no minimal invalid answer violates a licence unit (all violate target rules)", vid)
        for u in ctx.reg:
            if ctx.label(v, u) == "MUST" and u not in violated_units:
                rep.add("WARN", "A11", f"MUST unit {u} is violated by no invalid answer", vid, u)
        # A13 (gold)
        if ctx.gold and card.get("marker") and v["fit"] == "full" and v["role"] in ("requirement", "counter"):
            for a in valid:
                ans = V2.parse_answer(a["text"], card)
                if not ans["format_ok"]:
                    continue
                m = V2.run_check_v2(card["marker"]["spec"], ans, card)[0]
                if v["role"] == "requirement" and m is not True:
                    rep.add("WARN", "A13", f"valid answer {a['id']} lacks the marker; a full-fit requirement should copy it", vid)
                if v["role"] == "counter" and m is not False:
                    rep.add("WARN", "A13", f"valid answer {a['id']} carries the marker; a full-fit counter-example should avoid it", vid)


# ---------------------------------------------------------------- Q: variants, cues and cells
def lint_variants(ctx):
    rep, card = ctx.rep, ctx.card
    variants = card["variants"]
    ids = [v["id"] for v in variants]
    for x in sorted({i for i in ids if ids.count(i) > 1}):
        rep.add("ERROR", "Q1", f"duplicate variant id {x}", x)
    for v in variants:
        vid = v["id"]
        if v["role"] not in ROLES or v["cue"] not in CUES or v["fit"] not in FITS:
            rep.add("ERROR", "Q1", f"role/cue/fit must be in {ROLES}/{CUES}/{FITS}; found {v['role']}/{v['cue']}/{v['fit']}", vid)
            continue
        n = v["text"].count("{EX}")
        if n != 1:
            rep.add("ERROR", "Q1", f"text must contain {{EX}} exactly once, found {n}", vid)
        own = L1.norm(v["text"].replace("{EX}", " "))
        if v["cue"] == "implied":
            hits = [p for p in L1.IMPLIED_BANNED if p in own]
            if hits:
                rep.add("ERROR", "Q2", f"implied cue states the role outright: {hits}", vid)
        elif not any(p in own for p in L1.CUE_PHRASES[v["role"]]):
            rep.add("WARN", "Q3", f"stated cue has no recognised {v['role']} phrase", vid)
        if v["fit"] != "full" and not v.get("rules_add") and not v.get("fit_note"):
            rep.add("ERROR", "Q4", "non-full fit needs rules_add or fit_note saying what changes", vid)
    na = card["cells_not_applicable"]
    for role in ROLES:
        for fit in FITS:
            for cue in CUES:
                have = any(v["role"] == role and v["fit"] == fit and v["cue"] == cue for v in variants)
                skip = [x for x in na if isinstance(x, dict) and x.get("role") == role and x.get("fit") == fit and x.get("cue") in (None, cue)]
                if have and skip:
                    rep.add("ERROR", "Q5", f"cell {role}/{fit}/{cue} is both present and listed in cells_not_applicable")
                if not have and not skip:
                    rep.add("ERROR", "Q5", f"cell {role}/{fit}/{cue} is missing and not listed in cells_not_applicable")
                if skip and not all(nonempty(x.get("reason")) for x in skip):
                    rep.add("ERROR", "Q5", f"cell {role}/{fit}/{cue} is not applicable but has no reason")
    if variants:
        share = sum(v["cue"] == "implied" for v in variants) / len(variants)
        if share < 0.5:
            rep.add("WARN", "Q6", f"implied-cue share {share:.2f} < 0.50")
    if card["turns"] != ["single", "multi"]:
        rep.add("ERROR", "Q7", f"turns must be ['single', 'multi'], found {card['turns']}")


# ---------------------------------------------------------------- H: human review
def reviewer_ids(card):
    hr = card["human_review"]
    ids = set()
    for r in hr.get("reviewers", []):
        ids.add(r.get("reviewer_id") or r.get("id") if isinstance(r, dict) else r)
    for slots in hr.get("variants", {}).values():
        for s in slots.values():
            if isinstance(s, dict):
                ids.add(s.get("reviewer_id"))
    return ids


def lint_review(ctx):
    rep, card, release = ctx.rep, ctx.card, ctx.release
    hr = card["human_review"]
    if card["author_id"] in reviewer_ids(card):
        rep.add("ERROR", "H2", f"author {card['author_id']} is among the reviewers of their own card")
    for v in card["variants"]:
        vid = v["id"]
        slots = hr["variants"].get(vid, {})
        units = list(ctx.reg)
        empty = [k for k in ("annotator_1", "annotator_2") if slots.get(k) is None]
        partial = []
        for k in ("annotator_1", "annotator_2"):
            s = slots.get(k)
            if s is not None and not (set(units) <= set(s.get("licence", {}))):
                partial.append(f"{k} lacks labels for {sorted(set(units) - set(s.get('licence', {})))}")
        if empty or partial:
            rep.add("PENDING", "H1", f"annotator slot(s) not complete: empty {empty}{'; ' + '; '.join(partial) if partial else ''}", vid)
        if not release:
            continue
        for k in ("annotator_1", "annotator_2"):
            s = slots.get(k)
            if s is None:
                continue
            if s["realism"] < 4:
                rep.add("ERROR", "H3", f"{k} rated realism {s['realism']} (< 4)", vid)
            if s["role"] != v["role"] and not any(a.get("variant") == vid and a.get("field") == "role" for a in hr["adjudications"]):
                rep.add("ERROR", "H5", f"{k} labelled the role {s['role']!r}, the variant is {v['role']!r}, and no role adjudication exists", vid)
        entries = ctx.ent(v)[0]
        for u, e in entries.items():
            fl = V2.final_label(card, vid, u)
            if fl is None:
                rep.add("ERROR", "H4", "no final label (reviewers disagree or are missing, and no adjudication)", vid, u)
            elif e.get("label") != fl:
                rep.add("ERROR", "H4", f"card licence label {e.get('label')} differs from the final label {fl}", vid, u)


# ---------------------------------------------------------------- card driver
STAGES = [("spans", lambda c: lint_spans(c.rep, c.card)), ("S14", lint_s14), ("S17", lint_s17), ("licence", lint_licence),
          ("checks", lint_checks), ("variants", lint_variants), ("answers", lint_answers), ("review", lint_review)]


def guard(ctx, name, fn):
    try:
        fn(ctx)
    except Exception as e:   # a crash in one rule group must never look like a pass
        tb = traceback.extract_tb(e.__traceback__)[-1]
        ctx.rep.add("ERROR", "INT", f"internal failure in rule group {name}: {type(e).__name__}: {e} (seed_lint_v2.py line {tb.lineno})")


def lint_card(card, release=False, gold=True, path=None):
    rep = Report(card.get("id", "?") if isinstance(card, dict) else "?")
    if not isinstance(card, dict):
        rep.add("ERROR", "M1", "card is not a JSON object")
        return rep
    ctx = Ctx(card, rep, release, gold, path)
    sound = lint_m1(rep, card)
    lint_meta(ctx)
    if not sound:
        rep.skipped = "rules after M1 were not evaluated because the structure is not sound"
        return finish(rep, card, release)
    for name, fn in STAGES:
        guard(ctx, name, fn)
    rep.n_variants = len(card["variants"])
    rep.n_core = sum(1 for v in card["variants"] if not V2.unresolved_units(card, v))
    return finish(rep, card, release)


def finish(rep, card, release):
    if release:
        for it in rep.items:
            if it["level"] == "PENDING":
                it["level"], it["msg"] = "ERROR", it["msg"] + " (PENDING in draft mode)"
    if not rep.n_variants and isinstance(card.get("variants"), list):
        rep.n_variants = len(card["variants"])
        rep.n_core = rep.n_variants
    return rep


# ---------------------------------------------------------------- set level
def pool_of(card):
    return card.get("split") or "(unassigned)"


def lint_set(cards, release=False):
    """Set-level rules T1 to T7. cards = list of (path, card). Returns findings as dicts (card = '*')."""
    out = []

    def add(level, rule, msg):
        out.append({"level": level, "rule": rule, "card": "*", "variant": None, "unit": None, "msg": msg})

    cards = [(p, c) for p, c in cards if isinstance(c, dict) and isinstance(c.get("variants"), list) and "provenance" in c]
    if not cards:
        return out
    dlevel = "ERROR" if release else "WARN"
    pools = {}
    for _, c in cards:
        pools.setdefault(pool_of(c), []).append(c)
    for pool, cs in sorted(pools.items()):
        counts = {}
        for c in cs:
            counts.setdefault(c["provenance"].get("source_type"), []).append(c["id"])
        for st, ids in sorted(counts.items(), key=lambda kv: str(kv[0])):
            if len(ids) / len(cs) > 0.40:
                add(dlevel, "T1", f"pool {pool}: source type {st} supplies {len(ids)} of {len(cs)} cards ({len(ids) / len(cs):.0%} > 40%)")
    test_cards = [c for c in (c for _, c in cards) if str(c.get("split") or "").startswith("test")]
    if test_cards or release:
        for fam in FAMILIES:
            n = sum(1 for c in test_cards if c.get("family") == fam)
            if n < 40:
                add(dlevel, "T2", f"family {fam}: {n} test seed(s), at least 40 required")
        tv = [v for c in test_cards for v in c["variants"]]
        share = sum(v.get("cue") == "implied" for v in tv) / len(tv) if tv else 0.0
        if share < 0.30:
            add(dlevel, "T3", f"implied-cue share of test variants is {share:.0%} (< 30%)")
    for key in ("provenance_group_id", "template_group_id"):
        groups = {}
        for _, c in cards:
            groups.setdefault(c.get(key), []).append(c)
        for g, cs in sorted(groups.items(), key=lambda kv: str(kv[0])):
            splits = {c.get("split") for c in cs}
            if len(cs) > 1 and len(splits) > 1:
                add("ERROR", "T4", f"cards {[c['id'] for c in cs]} share {key} {g} but have different splits {sorted(map(str, splits))}")
    held = {c.get("relation_family") for _, c in cards if c.get("split") == "test_heldout_relation"}
    for _, c in cards:
        if c.get("split") in ("training", "development") and c.get("relation_family") in held:
            add("ERROR", "T5", f"card {c['id']} ({c['split']}) has relation_family {c['relation_family']}, which is in the held-out-relation pool")
    ids = [c["id"] for _, c in cards]
    for x in sorted({i for i in ids if ids.count(i) > 1}):
        add("ERROR", "T6", f"card id {x} occurs more than once in the set")
    for _, c in cards:
        if c["id"].startswith("X") and c.get("split"):
            add("ERROR", "T6", f"card {c['id']} is an X card (documentation or fixture) but is in pool {c['split']}")
    nv = sum(len(c["variants"]) for _, c in cards)
    nctrl = sum(1 for _, c in cards for v in c["variants"] if V2.control_applies(c, v))
    n_amb = sum(1 for _, c in cards for v in c["variants"] if V2.unresolved_units(c, v))
    dist = {}
    for _, c in cards:
        for v in c["variants"]:
            for e in V2.expand_licence(c, v)[0].values():
                dist[e.get("label")] = dist.get(e.get("label"), 0) + 1
    add("INFO", "T7", f"{len(cards)} cards, {nv} variants, {2 * nv + nctrl} prompts ({nv} variants x 2 turns + {nctrl} controls), "
                      f"core {nv - n_amb}, ambiguity {n_amb}, licence labels {dict(sorted(dist.items(), key=lambda kv: str(kv[0])))}, "
                      f"pools {sorted((k, len(v)) for k, v in pools.items())}")
    return out


# ---------------------------------------------------------------- CLI
def load(paths):
    files = []
    for p in paths:
        files += sorted(glob.glob(os.path.join(p, "*.json"))) if os.path.isdir(p) else [p]
    cards = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                cards.append(json.load(fh))
        except (OSError, ValueError) as e:
            cards.append({"__load_error__": f"{type(e).__name__}: {e}"})
    return files, cards


def summary_line(rep):
    ne, nw, npd = rep.count("ERROR"), rep.count("WARN"), rep.count("PENDING")
    core = f"{rep.n_core}/{rep.n_variants} = {rep.core_rate:.2f}" if rep.n_variants else "n/a"
    return (f"{'FAIL' if ne else 'ok  '} {rep.sid:30s} variants={rep.n_variants:2d} errors={ne} warnings={nw} pending={npd} core={core}"
            + (f"  [{rep.skipped}]" if rep.skipped else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", default=[os.path.join(ROOT, "data", "seeds_v2_draft")])
    ap.add_argument("--release", action="store_true", help="PENDING becomes ERROR; release-only rules run")
    ap.add_argument("--no-gold", action="store_true", help="skip running the answers (A3, A4, A7, A12, A13)")
    ap.add_argument("--quiet", action="store_true", help="only the summary line per card")
    ap.add_argument("--json", metavar="FILE", help="write every finding as JSON")
    a = ap.parse_args(argv)
    files, cards = load(a.paths)
    reports, errors = [], 0
    for f, c in zip(files, cards):
        if "__load_error__" in c:
            rep = Report(os.path.splitext(os.path.basename(f))[0])
            rep.add("ERROR", "M1", f"cannot read {f}: {c['__load_error__']}")
        else:
            rep = lint_card(c, release=a.release, gold=not a.no_gold, path=f)
        reports.append((f, rep))
        errors += rep.count("ERROR")
        print(summary_line(rep))
        if not a.quiet:
            groups = {}
            for it in rep.items:
                if it["level"] == "PENDING":
                    groups.setdefault(it["rule"], []).append(it)
                else:
                    print("     " + fmt(it))
            for rule, its in sorted(groups.items()):
                print(f"     PENDING {rule:5s} {rep.sid}: {len(its)} item(s), e.g. {its[0]['msg']}"[:240])
    set_items = lint_set([(f, c) for f, c in zip(files, cards) if "__load_error__" not in c], a.release)
    for it in set_items:
        errors += it["level"] == "ERROR"
        print(f"SET  {fmt(it)}")
    print(f"{len(cards)} card(s), {errors} error(s)")
    if a.json:
        doc = {"mode": "release" if a.release else "draft", "gold": not a.no_gold, "errors": errors,
               "cards": [{"file": display_path(f), "id": r.sid,
                          "errors": r.count("ERROR"), "warnings": r.count("WARN"), "pending": r.count("PENDING"),
                          "variants": r.n_variants, "core_variants": r.n_core,
                          "core_rate": None if not r.n_variants else r.core_rate, "skipped": r.skipped, "findings": r.items}
                         for f, r in reports],
               "set": set_items}
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
