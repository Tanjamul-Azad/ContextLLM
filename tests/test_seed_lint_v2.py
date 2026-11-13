"""Tests for the v2 seed-card linter and scorer (docs/seed-spec-v2.md).

Run: python -I tests/test_seed_lint_v2.py      (or: python -m pytest tests/test_seed_lint_v2.py)

What is tested:
  * both reference cards pass with no ERROR, and the example card of spec Section 11 passes with only
    the accepted warning S14;
  * one mutation per ERROR rule: a copy of a reference card is changed in memory and exactly that rule
    must be the only ERROR rule raised (release-only rules are compared against an unmutated release run);
  * score_v2 joint equals score_v1 joint on every valid, invalid and copy answer of both cards
    (for the one variant with a reserved judge check, against score_v1 on a copy without the judge check);
  * licence helpers, scorer details, the CLI exit code, JSON output and determinism.
"""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import checks_v1 as V1  # noqa: E402
import checks_v2 as V2  # noqa: E402
import seed_lint_v2 as L  # noqa: E402

DRAFTS = os.path.join(ROOT, "data", "seeds_v2_draft")
_CACHE = {}


def load(name):
    if name not in _CACHE:
        with open(os.path.join(DRAFTS, name + ".json"), encoding="utf-8") as f:
            _CACHE[name] = json.load(f)
    return copy.deepcopy(_CACHE[name])


def spec_example():
    """The example card embedded in spec Section 11."""
    with open(os.path.join(ROOT, "docs", "seed-spec-v2.md"), encoding="utf-8") as f:
        sec = f.read().split("## 11. Example card", 1)[1].split("## 12.", 1)[0]
    return json.loads(re.search(r"```json\n(.*?)\n```", sec, re.S).group(1))


def d01():
    return load("D01_stockholm_parking")


def c01():
    return load("C01_calver_compare")


def var(card, vid):
    return next(v for v in card["variants"] if v["id"] == vid)


def levels(card, level="ERROR", **kw):
    return {it["rule"] for it in L.lint_card(card, **kw).items if it["level"] == level}


def messages(card, **kw):
    return [L.fmt(it) for it in L.lint_card(card, **kw).items if it["level"] == "ERROR"]


def only(card, rule, **kw):
    """The mutation raises exactly one ERROR rule and it is `rule`."""
    got = levels(card, **kw)
    assert got == {rule}, (rule, sorted(got), messages(card, **kw)[:4])


def new_in_release(mutated, base, rule):
    """For release-only rules: the mutated card raises `rule` and nothing that the unmutated card does not."""
    a, b = levels(mutated, release=True), levels(base, release=True)
    assert a - b == {rule}, (rule, sorted(a - b), messages(mutated, release=True)[:3])


# ================================================================= reference cards
def test_reference_cards_have_no_errors():
    for name in ("D01_stockholm_parking", "C01_calver_compare"):
        card = load(name)
        rep = L.lint_card(card, path=os.path.join(DRAFTS, name + ".json"))
        errs = [L.fmt(it) for it in rep.items if it["level"] == "ERROR"]
        assert errs == [], errs[:5]
        assert rep.skipped is None


def test_reference_cards_core_rates_match_spec():
    """Spec 14.10: 3 of 8 D01 variants and 1 of 6 C01 variants are core until adjudication."""
    r = L.lint_card(d01())
    assert (r.n_core, r.n_variants) == (3, 8)
    r = L.lint_card(c01())
    assert (r.n_core, r.n_variants) == (1, 6)


def test_spec_example_card_has_only_the_accepted_warning():
    rep = L.lint_card(spec_example())
    assert [it for it in rep.items if it["level"] == "ERROR"] == []
    assert sorted({it["rule"] for it in rep.items if it["level"] == "WARN"}) == ["S14"], [L.fmt(i) for i in rep.items]


def test_release_mode_blocks_drafts():
    got = levels(d01(), release=True, gold=False)
    for rule in ("M3", "P2", "H1", "H4", "K7r"):
        assert rule in got, (rule, sorted(got))
    assert "M6" not in got                       # D01 uses registered ids now that data/registry exists
    assert "C9" not in got and "K7" not in got   # draft-only rules do not run in release mode


def test_unknown_registry_id_is_flagged():
    card = d01()
    card["relation_family"] = "not_a_registered_family"
    assert "M6" in levels(card, release=False, gold=False)


def test_draft_mode_reports_pending_not_errors():
    rep = L.lint_card(d01())
    pend = {it["rule"] for it in rep.items if it["level"] == "PENDING"}
    assert {"C9", "H1", "K7", "P2"} <= pend, pend
    assert "M6" not in pend


# ================================================================= scorer
def test_score_v2_joint_equals_score_v1_on_every_answer():
    n = 0
    for card in (d01(), c01()):
        for v in card["variants"]:
            v1 = copy.deepcopy(v)   # score_v1 does not know the reserved judge kinds: compare without them
            v1["must_not_transfer"] = [c for c in v1["must_not_transfer"] if not V2.is_judge(c)]
            v1["must_transfer"] = [c for c in v1["must_transfer"] if not V2.is_judge(c)]
            for a in v["valid_answers"] + v["invalid_answers"]:
                r1 = V1.score_v1(a["text"], card, v1)
                r2 = V2.score_v2(a["text"], card, v)
                assert r1["joint"] == r2["joint"], (card["id"], v["id"], a["id"], r1["joint"], r2["joint"])
                assert r1["format_ok"] == r2["format_ok"]
                if "kind" not in a:
                    assert r2["joint"] is True
                n += 1
    assert n >= 80, n


def test_score_v2_joint_equals_score_v1_under_the_control():
    for card in (d01(), c01()):
        for v in card["variants"]:
            if not V2.control_applies(card, v):
                continue
            v1 = copy.deepcopy(v)
            v1["must_not_transfer"] = [c for c in v1["must_not_transfer"] if not V2.is_judge(c)]
            for a in v["valid_answers"]:
                assert V1.score_v1(a["text"], card, v1, perturbed=True)["joint"] == V2.score_v2(a["text"], card, v, perturbed=True)["joint"]


def test_score_v2_reports_judge_as_not_run():
    card = d01()
    v = var(card, "requirement-stated-full")
    r = V2.score_v2(v["valid_answers"][0]["text"], card, v)
    assert r["judge_pending"] is True and r["judge_checks"] == ["J1"] and r["joint"] is True
    assert V2.score_v2(v["valid_answers"][0]["text"], card, var(card, "analogy-stated-full"))["judge_pending"] is False


def test_score_v2_attribution():
    card = d01()
    v = var(card, "analogy-stated-full")
    x1 = next(a for a in v["invalid_answers"] if a["id"] == "X1")     # violates U01
    r = V2.score_v2(x1["text"], card, v)
    assert r["under_transfer"] is True and r["over_transfer"] is False and r["must_ok"] is False and r["joint"] is False
    x2 = next(a for a in v["invalid_answers"] if a["id"] == "X2")     # copies the currency (I1)
    r = V2.score_v2(x2["text"], card, v)
    assert r["over_transfer"] is True and "I1" in r["used_units"] and r["must_ok"] is True
    x3 = next(a for a in v["invalid_answers"] if a["id"] == "X3")     # breaks target rule R3
    r = V2.score_v2(x3["text"], card, v)
    assert r["constraint_ok"] is False and r["must_ok"] is True and r["mustnot_ok"] is True


def test_score_v2_format_failure_is_not_over_transfer():
    card = d01()
    v = var(card, "analogy-stated-full")
    r = V2.score_v2("I would charge more at the peak.", card, v)
    assert r["format_ok"] is False and r["joint"] is False
    assert r["must_ok"] is None and r["mustnot_ok"] is None and r["over_transfer"] is None and r["used_units"] == []


def test_score_v2_probe_uses_and_may_units():
    card = c01()
    v = var(card, "analogy-implied-full")
    plain = next(a for a in v["valid_answers"] if not a.get("uses_may"))
    uses = next(a for a in v["valid_answers"] if a.get("uses_may"))
    assert V2.score_v2(plain["text"], card, v)["probe_uses"] == {"P1": False}
    r = V2.score_v2(uses["text"], card, v)
    assert r["probe_uses"] == {"P1": True} and r["joint"] is True and "I2" in r["used_units"]


def test_score_v2_subset_and_readings():
    card = d01()
    assert V2.score_v2(var(card, "analogy-stated-full")["valid_answers"][0]["text"], card, var(card, "analogy-stated-full"))["subset"] == "core"
    v = var(card, "analogy-implied-full")
    assert V2.variant_subset(card, v) == "ambiguity" and V2.unresolved_units(card, v)
    u = V2.unresolved_units(card, v)[0]
    lenient = V2.resolved_labels(card, v, "lenient")
    assert lenient[u] == "MAY"
    # an adjudication settles the unit and can move the variant to the core set
    for w in V2.unresolved_units(card, v):
        card["human_review"]["adjudications"].append({"variant": v["id"], "field": "licence", "unit": w, "value": "MAY",
                                                      "decided_by": "t", "date": "2026-11-14", "note": ""})
    assert V2.variant_subset(card, v) == "core"
    assert V2.final_label(card, v["id"], u) == "MAY"


def test_final_label_needs_agreement():
    card = d01()
    vid = "analogy-implied-full"
    slot = {"reviewer_id": "a", "date": "d", "role": "analogy", "realism": 5, "licence": {"I2": "MUST_NOT"}}
    card["human_review"]["variants"][vid]["annotator_1"] = slot
    assert V2.final_label(card, vid, "I2") is None
    card["human_review"]["variants"][vid]["annotator_2"] = dict(slot, reviewer_id="b")
    assert V2.final_label(card, vid, "I2") == "MUST_NOT"
    card["human_review"]["variants"][vid]["annotator_2"]["licence"] = {"I2": "MAY"}
    assert V2.final_label(card, vid, "I2") is None


def test_normalised_forms():
    card = d01()
    a = '```json\n{"b": 1, "a": 2}\n```'
    b = '{"a": 2,   "b": 1}'
    assert V2.normalise_answer(a, card) == V2.normalise_answer(b, card)
    code = c01()
    x = "```python\nimport re\n\n# comment\ndef is_newer(a,   b):\n    return a  > b  # trailing\n```"
    y = "```python\nimport re\ndef is_newer(a, b):\n    return a > b\n```"
    assert V2.normalise_answer(x, code) == V2.normalise_answer(y, code)


# ================================================================= mutations: metadata and provenance
def test_mut_M1():
    c = d01()
    del c["status_note"]
    only(c, "M1")


def test_mut_M2():
    c = d01()
    c["schema"] = "seed-card-v1"
    only(c, "M2")
    c = d01()
    got = {it["rule"] for it in L.lint_card(c, path="X99_other.json").items if it["level"] == "ERROR"}
    assert got == {"M2"}


def test_mut_M3():
    c = d01()
    c["status"] = "bogus"
    only(c, "M3")


def test_mut_M4():
    c = d01()
    c["model_assistance_log"]["model"] = ""
    only(c, "M4")
    c = d01()
    c["model_assistance"] = "robot"
    only(c, "M4")


def test_mut_M5():
    c = d01()
    c["author_id"] = "Bad Author"
    only(c, "M5")


def test_mut_M6():
    old = L.REGISTRY_DIR
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "domains.json"), "w") as f:
            json.dump(["other_domain"], f)
        with open(os.path.join(d, "relation_families.json"), "w") as f:
            json.dump({"ids": ["demand_responsive_pricing"]}, f)
        L.REGISTRY_DIR = d
        try:
            only(d01(), "M6")
            assert "M6" not in {it["rule"] for it in L.lint_card(d01()).items if it["level"] == "PENDING"}
            c = d01()
            c["domain"] = "other_domain"
            assert levels(c) == set()
        finally:
            L.REGISTRY_DIR = old


def test_mut_P1():
    c = d01()
    c["provenance"]["case"] = ""
    only(c, "P1")
    c = d01()
    c["provenance"]["references"] = [{"citation": "A. N. Author, a paper"}]
    only(c, "P1")
    c = d01()
    c["provenance"]["source_type"] = "original_scenario"
    del c["provenance"]["references"]
    c["provenance"]["original_authoring"] = ""
    only(c, "P1")


# ================================================================= mutations: spans
def test_mut_S1():
    c = d01()
    c["source_spans"][0]["text"] += "x"
    only(c, "S1")


def test_mut_S2():
    c = d01()
    c["source_spans"][1]["id"] = c["source_spans"][0]["id"]
    only(c, "S2")


def test_mut_S3():
    c = d01()
    c["source_spans"].append({"id": "S99", "text": "", "kind": "context"})
    only(c, "S3")


def test_mut_S4():
    c = d01()
    counts = {}
    for s in c["source_spans"]:
        counts[s.get("unit")] = counts.get(s.get("unit"), 0) + 1
    s = next(s for s in c["source_spans"] if s["kind"] == "relation" and counts[s["unit"]] > 1)
    s["unit"] = "U99"
    only(c, "S4")


def test_mut_S5():
    c = d01()
    owner = {}
    for s in c["source_spans"]:
        owner.setdefault(s.get("unit"), []).append(s)
    unit = next(u for u, ss in owner.items() if u and u.startswith("U") and len(ss) == 1)
    owner[unit][0]["kind"] = "context"
    del owner[unit][0]["unit"]
    only(c, "S5")
    c = d01()   # one unit id defined twice
    c["relation_units"].append({"id": "U01", "what": "clash", "main": False})
    assert "S5" in levels(c, gold=False)


def test_mut_S6():
    c = d01()
    i = next(i for i, s in enumerate(c["source_spans"]) if s["kind"] == "context" and len(s["text"]) >= 2)
    s = c["source_spans"][i]
    c["source_spans"][i:i + 1] = [{"id": "S97", "text": s["text"][:-1], "kind": "context"},
                                  {"id": "S98", "text": s["text"][-1], "kind": "detail", "unit": "I1"}]
    only(c, "S6")


def test_mut_S7():
    c = d01()
    firsts = [s for s in c["source_spans"] if s["kind"] == "detail" and s["unit"] == "I1"]
    firsts[-1]["kind"], firsts[-1]["unit"] = "relation", "U02"
    only(c, "S7")


def test_mut_S8():
    c = d01()
    next(d for d in c["source_example"]["incidental_details"] if d["id"] == "I2")["leak_terms"].append("Zzyzx")
    only(c, "S8")


def test_mut_S10():
    c = d01()
    d = next(d for d in c["source_example"]["incidental_details"] if d["id"] == "I3")
    d["control"] = {"from": "Lidingö", "to": "Lidingö", "leak_terms": ["Lidingö"]}
    only(c, "S10")


def test_mut_S11():
    c = d01()
    for u in c["relation_units"]:
        u["main"] = False
    only(c, "S11")


def test_mut_S14():
    c = spec_example()
    c["source_example"]["incidental_details"] = [d for d in c["source_example"]["incidental_details"] if d["id"] != "I3"]
    for s in c["source_spans"]:
        if s.get("unit") == "I3":
            s["kind"] = "context"
            del s["unit"]
    for v in c["variants"]:
        for a in v["valid_answers"]:
            a["uses_may"] = [u for u in a.get("uses_may", []) if u != "I3"]
    only(c, "S14")


def test_mut_S16():
    c = d01()
    c["source_example"]["shared_surface_features"] = c["source_example"]["shared_surface_features"][:2]
    only(c, "S16")


def test_mut_S17():
    c = d01()
    c["target"]["format"] += "\n" + c["source_example"]["text"]
    only(c, "S17")


# ================================================================= mutations: licence
def first_entry(card, vid, pred):
    v = var(card, vid)
    ents, _ = V2.expand_licence(card, v)
    for u, e in ents.items():
        if pred(e):
            return v, u, e
    raise AssertionError("no matching licence entry")


def test_mut_C1():
    c = d01()
    var(c, "analogy-stated-full")["licence"]["units"]["U99"] = {"label": "MAY", "basis": "DEFAULT"}
    only(c, "C1")
    c = d01()
    del var(c, "analogy-stated-full")["licence"]["defaults"]["relation"]
    assert "C1" in levels(c)


def test_mut_C2():
    c = d01()
    var(c, "analogy-stated-full")["licence"]["units"]["U02"] = {"label": "MAY", "basis": "GUESS"}
    only(c, "C2")
    c = d01()
    var(c, "analogy-stated-full")["licence"]["units"]["U02"] = {"label": "MUST", "basis": "DEFAULT"}
    assert "C2" in levels(c, gold=False)


def test_mut_C3():
    c = d01()
    var(c, "analogy-stated-full")["licence"]["defaults"]["detail"]["evidence"] = "not the details at all"
    only(c, "C3")
    c = d01()   # evidence that occurs only inside the example does not count
    v = var(c, "analogy-stated-full")
    v["licence"]["defaults"]["detail"]["evidence"] = "Stockholm ran congestion charges"
    only(c, "C3")


def test_mut_C4():
    c = d01()
    v, u, e = first_entry(c, "analogy-implied-full", lambda e: e.get("basis") == "INFERRED")
    v["licence"]["units"] = dict(v["licence"].get("units", {}))
    v["licence"]["units"][u] = dict(e)
    for k in ("_kind", "_default"):
        v["licence"]["units"][u].pop(k, None)
    v["licence"]["units"][u]["implication"] = "bogus"
    only(c, "C4")


def test_mut_C5():
    c = d01()
    v, u, e = first_entry(c, "analogy-implied-full", lambda e: e.get("label") == "UNCLEAR" and not e["_default"])
    del v["licence"]["units"][u]["note"]
    only(c, "C5")


# ================================================================= mutations: checks
def test_mut_K1():
    c = d01()
    var(c, "analogy-stated-full")["must_transfer"][0]["units"].append("U99")
    only(c, "K1")


def test_mut_K2():
    c = d01()
    var(c, "analogy-stated-full")["must_transfer"][0]["units"].append("I1")
    only(c, "K2")


def test_mut_K3():
    c = d01()
    v = var(c, "analogy-stated-full")
    v["must_not_transfer"] = [x for x in v["must_not_transfer"] if x["id"] != "L3"]
    only(c, "K3")


def test_mut_K4():
    c = d01()
    var(c, "analogy-stated-full")["must_transfer"][0]["units"].append("U02")
    only(c, "K4")


def test_mut_K5():
    c = d01()
    var(c, "analogy-stated-full")["probes"].append({"id": "P1", "what": "x", "spec": ["leak_absent", "I2"], "units": ["U02"], "use_when": "fail"})
    only(c, "K5")


def test_mut_K6():
    c = d01()
    var(c, "analogy-stated-full")["must_not_transfer"][0]["spec"] = ["bogus_kind", "I1"]
    only(c, "K6")
    c = d01()   # a bound that the instruction does not state (pilot P5)
    c["target"]["rules"][2]["checks"][1]["spec"][2] = 1400
    only(c, "K6")
    c = c01()   # a py_test that is not defined
    c["target"]["rules"][2]["checks"][0]["spec"][1] = "NOPE"
    assert levels(c, gold=False) == {"K6"}


def test_mut_K7r():
    old = L.JUDGE_STATUS
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "status.json")
        L.JUDGE_STATUS = p
        try:
            base = d01()
            with open(p, "w") as f:
                json.dump({"passed": True}, f)
            assert "K7r" not in levels(base, release=True)
            with open(p, "w") as f:
                json.dump({"passed": False}, f)
            a = levels(base, release=True)
            assert "K7r" in a
            # a card without judge checks never raises K7r
            assert "K7r" not in levels(c01(), release=True)
        finally:
            L.JUDGE_STATUS = old


def test_mut_K8():
    c = d01()
    c["marker"]["units"] = []
    only(c, "K8")


# ================================================================= mutations: answers
V = "analogy-stated-full"


def test_mut_A1():
    c = d01()
    v = var(c, V)
    del v["valid_answers"][1]
    for a in v["invalid_answers"]:
        if a.get("pair_of") == "V2":
            a["pair_of"] = "V1"
    only(c, "A1")


def test_mut_A2():
    c = d01()
    v = var(c, V)
    v["valid_answers"][1]["text"] = v["valid_answers"][0]["text"]
    for a in v["invalid_answers"]:
        if a.get("pair_of") == "V2":
            a["pair_of"] = "V1"
    only(c, "A2")


def test_mut_A3():
    c = d01()
    v = var(c, V)
    v["valid_answers"][0]["text"] = v["valid_answers"][0]["text"].replace('"label": "', '"label": "SEK ', 1)
    only(c, "A3")


def test_mut_A4():
    c = d01()
    var(c, V)["valid_answers"][0]["uses_may"] = ["I1"]
    only(c, "A4")


def test_mut_A6():
    c = d01()
    v = var(c, V)
    v["invalid_answers"] = [a for a in v["invalid_answers"] if a["id"] not in ("X2", "X3")]
    only(c, "A6")


def test_mut_A7():
    c = d01()
    x3 = next(a for a in var(c, V)["invalid_answers"] if a["id"] == "X3")
    x3["fails"] = ["R3b", "R3a"]
    only(c, "A7")


def test_mut_A8():
    c = d01()
    next(a for a in var(c, V)["invalid_answers"] if a["id"] == "X2")["pair_of"] = "V9"
    only(c, "A8")
    c = d01()   # a failing check that does not test the violated item
    next(a for a in var(c, V)["invalid_answers"] if a["id"] == "X2")["violates"] = "I2"
    assert "A8" in levels(c)


def test_mut_A10():
    c = d01()
    v = var(c, V)
    x3 = next(a for a in v["invalid_answers"] if a["id"] == "X3")
    clone = dict(x3, id="X4")
    v["invalid_answers"] = [a for a in v["invalid_answers"] if a["id"] not in ("X1", "X2", "X3")] + [x3, clone]
    only(c, "A10")


def test_mut_A12():
    c = d01()
    v = var(c, V)
    cp = next(a for a in v["invalid_answers"] if a["kind"] == "copy")
    cp["text"] = v["valid_answers"][0]["text"]
    cp["fails"] = []
    only(c, "A12")


# ================================================================= mutations: variants and cells
def test_mut_Q1():
    c = d01()
    v = var(c, V)
    v["text"] = v["text"].replace("{EX}", "")
    only(c, "Q1")
    c = d01()   # duplicate variant id
    old = c["variants"][1]["id"]
    c["variants"][1]["id"] = c["variants"][0]["id"]
    del c["human_review"]["variants"][old]
    assert "Q1" in levels(c, gold=False)


def test_mut_Q2():
    c = d01()
    var(c, "analogy-implied-full")["text"] += " We should avoid mistakes."
    only(c, "Q2")


def test_mut_Q4():
    c = d01()
    v = var(c, V)
    v["fit"] = "wrong"
    c["cells_not_applicable"].append({"role": "analogy", "fit": "full", "cue": "stated", "reason": "moved in this test"})
    only(c, "Q4")


def test_mut_Q5():
    c = d01()
    c["cells_not_applicable"].pop()
    only(c, "Q5")


def test_mut_Q7():
    c = d01()
    c["turns"] = ["multi", "single"]
    only(c, "Q7")


# ================================================================= mutations: human review
def fill_review(card):
    """Both annotators agree with the author on role and every unit label (UNCLEAR stays UNCLEAR)."""
    for v in card["variants"]:
        ents = V2.expand_licence(card, v)[0]
        mk = lambda rid: {"reviewer_id": rid, "date": "2026-11-14", "role": v["role"], "realism": 5,
                          "licence": {u: e["label"] for u, e in ents.items()}}
        card["human_review"]["variants"][v["id"]] = {"annotator_1": mk("rev_a"), "annotator_2": mk("rev_b")}
    card["human_review"]["reviewers"] = ["rev_a", "rev_b"]
    return card


def test_mut_H2():
    c = d01()
    c["human_review"]["reviewers"] = [c["author_id"]]
    only(c, "H2")


def test_filled_review_clears_h1():
    base = fill_review(d01())
    assert "H1" not in {it["rule"] for it in L.lint_card(base).items if it["level"] == "PENDING"}
    assert {"H3", "H4", "H5"} & levels(base, release=True) == set()


def test_mut_H3():
    base = fill_review(d01())
    m = copy.deepcopy(base)
    m["human_review"]["variants"][V]["annotator_2"]["realism"] = 3
    new_in_release(m, base, "H3")


def test_mut_H4():
    base = fill_review(d01())
    m = copy.deepcopy(base)
    for k in ("annotator_1", "annotator_2"):   # both reviewers agree on a label the card does not carry
        m["human_review"]["variants"][V]["licence" if False else k]["licence"]["I2"] = "MAY"
    new_in_release(m, base, "H4")
    m = copy.deepcopy(base)   # the reviewers disagree and nothing adjudicates
    m["human_review"]["variants"][V]["annotator_1"]["licence"]["I2"] = "MAY"
    new_in_release(m, base, "H4")


def test_mut_H5():
    base = fill_review(d01())
    m = copy.deepcopy(base)
    m["human_review"]["variants"][V]["annotator_1"]["role"] = "counter"
    new_in_release(m, base, "H5")
    m["human_review"]["adjudications"].append({"variant": V, "field": "role", "value": "analogy", "decided_by": "t", "date": "d", "note": ""})
    assert "H5" not in levels(m, release=True) - levels(base, release=True)


# ================================================================= set level
def _pair():
    a, b = d01(), copy.deepcopy(d01())
    b["id"] = "D98_copy"
    b["provenance_group_id"], b["template_group_id"] = "PG-other", "TG-other"
    return a, b


def set_errors(cards, release=False):
    return {it["rule"] for it in L.lint_set([(None, c) for c in cards], release) if it["level"] == "ERROR"}


def test_mut_T4():
    a, b = _pair()
    b["provenance_group_id"] = a["provenance_group_id"]
    a["split"], b["split"] = "development", "training"
    assert set_errors([a, b]) == {"T4"}
    b["split"] = "development"
    assert set_errors([a, b]) == set()


def test_mut_T5():
    a, b = _pair()
    a["split"], b["split"] = "test_heldout_relation", "training"
    assert set_errors([a, b]) == {"T5"}
    b["relation_family"] = "something_else"
    assert set_errors([a, b]) == set()


def test_mut_T6():
    a, b = _pair()
    b["id"] = a["id"]
    assert set_errors([a, b]) == {"T6"}
    a, b = _pair()
    a["id"] = "X01_fixture_in_pool"
    a["split"] = "development"
    b["split"] = "development"
    assert set_errors([a, b]) == {"T6"}


def test_set_rules_draft_warn_release_error():
    a, b = _pair()
    a["split"] = b["split"] = "test_familiar"
    draft = {(it["level"], it["rule"]) for it in L.lint_set([(None, a), (None, b)], False)}
    rel = {(it["level"], it["rule"]) for it in L.lint_set([(None, a), (None, b)], True)}
    for v in a["variants"] + b["variants"]:
        v["cue"] = "stated"   # no implied cue at all: T3
    draft = {(it["level"], it["rule"]) for it in L.lint_set([(None, a), (None, b)], False)}
    rel = {(it["level"], it["rule"]) for it in L.lint_set([(None, a), (None, b)], True)}
    assert ("WARN", "T1") in draft and ("WARN", "T2") in draft and ("WARN", "T3") in draft, draft
    assert ("ERROR", "T1") in rel and ("ERROR", "T2") in rel and ("ERROR", "T3") in rel, rel
    assert any(r == "T7" for _, r in draft)


# ================================================================= CLI and robustness
def run_cli(*args):
    p = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "src", "seed_lint_v2.py"), *args], capture_output=True, text=True)
    return p.returncode, p.stdout


def test_cli_exit_code_json_and_determinism():
    rc, out1 = run_cli("--quiet")
    assert rc == 0 and "0 error(s)" in out1
    rc2, out2 = run_cli("--quiet")
    assert out1 == out2
    with tempfile.TemporaryDirectory() as d:
        bad = d01()
        bad["status"] = "bogus"
        p = os.path.join(d, "D01_stockholm_parking.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(bad, f)
        j = os.path.join(d, "out.json")
        rc, out = run_cli(p, "--no-gold", "--json", j)
        assert rc == 1 and "M3" in out and "D01_stockholm_parking" in out
        doc = json.load(open(j, encoding="utf-8"))
        assert doc["errors"] == 1 and doc["cards"][0]["findings"][0]["rule"] == "M3"
        rc, out = run_cli(os.path.join(d, "missing.json"))
        assert rc == 1 and "cannot read" in out


def test_no_gold_skips_answer_runs():
    c = d01()
    v = var(c, V)
    v["valid_answers"][0]["text"] = v["valid_answers"][0]["text"].replace('"label": "', '"label": "SEK ', 1)
    assert "A3" in levels(c) and "A3" not in levels(c, gold=False)


def test_gold_is_skipped_after_structural_errors():
    c = d01()
    c["author_id"] = "Bad Author"
    rep = L.lint_card(c)
    assert rep.skipped and "gold" in rep.skipped


def test_m1_failure_stops_later_rules_and_says_so():
    c = d01()
    del c["variants"]
    rep = L.lint_card(c)
    assert rep.skipped and "M1" in rep.skipped and rep.rules() == ["M1"]


def test_messages_name_card_variant_unit_and_rule():
    c = d01()
    var(c, V)["licence"]["defaults"]["detail"]["evidence"] = "not the details at all"
    msg = messages(c)[0]
    assert "C3" in msg and "D01_stockholm_parking" in msg and V in msg and "unit I" in msg


def test_internal_failure_is_reported_not_swallowed():
    c = d01()
    c["target"]["rules"][0]["checks"][0]["spec"] = ["json_len_between", "periods"]    # too short: crashes the check runner
    rep = L.lint_card(c, gold=True)
    assert rep.count("ERROR") >= 1


# ================================================================= scripts
def test_spans_from_markup_roundtrip_and_failures():
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import spans_from_markup as S
    import licence_table as LT
    for card in (d01(), c01()):
        markup = "".join(s["text"] if s["kind"] == "context" else f"[[{s['unit']}|{s['text']}]]" for s in card["source_spans"])
        spans, plain = S.parse_markup(markup)
        assert plain == card["source_example"]["text"]
        assert spans == card["source_spans"] or "".join(x["text"] for x in spans) == plain
        assert S.check_spans(card, spans, plain) == []
        # a detail left outside brackets breaks S5 and S7
        bad, _ = S.parse_markup(markup.replace("[[I2|Essingeleden]]", "Essingeleden")) if card["id"].startswith("D01") else (None, None)
        if bad:
            assert {it["rule"] for it in S.check_spans(card, bad, plain)} >= {"S5", "S7"}
    for broken in ("a [[U01|b [[U02|c]] d]]", "a ]] b", "a [[U01|b"):
        try:
            S.parse_markup(broken)
        except ValueError:
            continue
        raise AssertionError(broken)
    text = LT.render_text(d01(), True)
    assert "analogy-stated-full" in text and "U01" in text and "MUST/D" in text
    assert LT.render_md(c01(), False).count(chr(10)) > 10 and LT.render_csv(c01(), False).startswith("card,unit")


# ================================================================= runner
if __name__ == "__main__":
    fails = passed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
                print("ok  ", name)
            except AssertionError as e:
                fails += 1
                print("FAIL", name, str(e)[:400])
            except Exception as e:   # noqa: BLE001
                fails += 1
                print("ERR ", name, type(e).__name__, str(e)[:400])
    print(f"{passed} passed, {fails} failed")
    sys.exit(1 if fails else 0)
