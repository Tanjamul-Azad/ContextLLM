"""Tests for src/export_v2.py (docs/seed-spec-v2.md Section 9) on the two reference cards.

Run: python -I tests/test_export_v2.py      (or: python -m pytest tests/test_export_v2.py)

Tokenizer tests load only tokenizers from the local Hugging Face cache (no model weights, no GPU) and are
skipped, with a printed note, when a tokenizer is not cached.
"""
import copy
import csv
import json
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import checks_v2 as V2  # noqa: E402
import export_v2 as E  # noqa: E402

DRAFTS = os.path.join(ROOT, "data", "seeds_v2_draft")
TOKENIZERS = ["Qwen/Qwen2.5-3B-Instruct", "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"]
NAMES = ["D01_stockholm_parking", "C01_calver_compare"]
_C = {}


def load(name):
    p = os.path.join(DRAFTS, name + ".json")
    if p not in _C:
        with open(p, encoding="utf-8") as f:
            _C[p] = json.load(f)
    return copy.deepcopy(_C[p]), p


def records(name):
    c, p = load(name)
    return c, E.export_card(c, p)


def tokenizer(name):
    try:
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(name, local_files_only=True)
    except Exception as e:   # noqa: BLE001
        print(f"     (tokenizer {name} not available: {type(e).__name__}; test skipped)")
        return None


# ---------------------------------------------------------------- records
def test_record_counts_and_ids():
    total = 0
    for n in NAMES:
        c, recs = records(n)
        want = sum(2 * (2 if V2.control_applies(c, v) else 1) for v in c["variants"])
        assert len(recs) == want
        ids = [r["record_id"] for r in recs]
        assert len(ids) == len(set(ids))
        assert recs[0]["record_id"] == f"{c['id']}::{c['variants'][0]['id']}::single::orig"
        total += len(recs)
    assert total == 56, total


def test_span_offsets_reproduce_span_texts_from_messages():
    for n in NAMES:
        c, recs = records(n)
        for r in recs:
            spans = V2.control_spans(c) if r["perturbed"] else c["source_spans"]
            assert [s["span_id"] for s in r["spans"]] == [s["id"] for s in spans]
            for rs, s in zip(r["spans"], spans):
                content = r["messages"][rs["message_index"]]["content"]
                assert content[rs["char_start"]:rs["char_end"]] == s["text"], (r["record_id"], s["id"])
            loc = r["example_location"]
            ex = r["messages"][loc["message_index"]]["content"][loc["char_start"]:loc["char_end"]]
            assert ex == "".join(s["text"] for s in spans)
            assert loc["message_index"] == (0 if r["turns"] == "single" else 2)
            assert r["spans"][0]["char_start"] == loc["char_start"] and r["spans"][-1]["char_end"] == loc["char_end"]
            for a, b in zip(r["spans"], r["spans"][1:]):
                assert a["char_end"] == b["char_start"]


def test_evidence_offsets_and_licence_block():
    for n in NAMES:
        c, recs = records(n)
        for r in recs:
            loc = r["example_location"]
            for e in r["evidence"]:
                msg = r["messages"][e["message_index"]]["content"]
                assert msg[e["char_start"]:e["char_end"]] == e["quote"]
                inside = e["message_index"] == loc["message_index"] and e["char_start"] < loc["char_end"] and e["char_end"] > loc["char_start"]
                assert not inside, (r["record_id"], e["unit_id"])
            v = next(x for x in c["variants"] if x["id"] == r["variant_id"])
            assert set(r["licence"]) == set(V2.unit_registry(c))
            assert {e["unit_id"] for e in r["evidence"]} == {u for u, x in V2.expand_licence(c, v)[0].items() if x.get("basis") in ("DIRECT", "INFERRED")}


def test_span_labels_context_and_unclear():
    c, recs = records("D01_stockholm_parking")
    r = next(x for x in recs if x["record_id"].endswith("analogy-implied-full::single::orig"))
    assert all(s["label"] is None for s in r["spans"] if s["kind"] == "context")
    assert any(s["label"] == "UNCLEAR" for s in r["spans"]) and r["subset"] == "ambiguity"
    assert all(s["label"] in ("MUST", "MAY", "MUST_NOT", "UNCLEAR") for s in r["spans"] if s["kind"] != "context")


def test_control_records_only_where_the_unit_is_not_must():
    c, recs = records("C01_calver_compare")
    ctrl = [r for r in recs if r["perturbed"]]
    assert ctrl and all(r["perturbed"] and r["record_id"].endswith("::ctrl") for r in ctrl)
    assert "bad semantic version string" in ctrl[0]["messages"][ctrl[0]["example_location"]["message_index"]]["content"]
    assert len({(r["variant_id"], r["turns"]) for r in ctrl}) == len(ctrl)


def test_siblings():
    c, recs = records("D01_stockholm_parking")
    r = next(x for x in recs if x["record_id"] == "D01_stockholm_parking::analogy-stated-full::single::orig")
    by = {s["variant_id"]: s for s in r["siblings"] if not s.get("perturbed")}
    assert set(by) == {v["id"] for v in c["variants"]} - {"analogy-stated-full"}
    assert by["analogy-implied-full"]["relation"] == "should_not_change" and by["analogy-implied-full"]["provisional"] is True
    assert by["requirement-stated-full"]["relation"] == "should_change" and by["requirement-stated-full"]["provisional"] is False
    assert by["requirement-stated-full"]["changed_units"][:2] == ["U01", "U02"]
    assert by["analogy-stated-wrong"]["changed_rules"] == ["R4"]
    ctrl = [s for s in r["siblings"] if s.get("perturbed")]
    assert ctrl == [{"variant_id": "analogy-stated-full", "perturbed": True, "relation": "should_not_change", "changed_units": [], "changed_rules": []}]
    rc = next(x for x in recs if x["record_id"] == "D01_stockholm_parking::analogy-stated-full::single::ctrl")
    assert not [s for s in rc["siblings"] if s.get("perturbed")]


def test_records_are_json_and_deterministic():
    a = [json.dumps(r, sort_keys=True) for n in NAMES for r in records(n)[1]]
    b = [json.dumps(r, sort_keys=True) for n in NAMES for r in records(n)[1]]
    assert a == b


def test_test_pool_is_never_written_inside_the_repo():
    try:
        E.guard_private("test_familiar", os.path.join(ROOT, "results", "dataset_stats", "test_familiar"))
    except E.ExportError:
        pass
    else:
        raise AssertionError("test pool inside the repository was allowed")
    with tempfile.TemporaryDirectory() as d:
        E.guard_private("test_familiar", d)   # outside the repository: allowed
    E.guard_private("development", os.path.join(ROOT, "results"))


# ---------------------------------------------------------------- statistics: independent manual counts
def test_statistics_match_a_manual_count():
    cards = [load(n) for n in NAMES]
    T = E.stats_tables([(p, c) for c, p in cards])
    assert len(T["cards"]) == 2 and len(T["variants"]) == 14 and len(T["spans"]) == 97
    for c, _ in cards:
        row = next(r for r in T["cards"] if r["card_id"] == c["id"])
        kinds = [s["kind"] for s in c["source_spans"]]
        assert row["n_spans"] == len(c["source_spans"]) == sum(1 for r in T["spans"] if r["card_id"] == c["id"])
        assert (row["n_relation_spans"], row["n_detail_spans"], row["n_context_spans"]) == (kinds.count("relation"), kinds.count("detail"), kinds.count("context"))
        assert row["n_relation_units"] == len(c["relation_units"]) and row["n_detail_units"] == len(c["source_example"]["incidental_details"])
        assert row["n_variants"] == len(c["variants"])
        assert row["example_chars"] == len(c["source_example"]["text"])
        n_units = len(c["relation_units"]) + len(c["source_example"]["incidental_details"])
        assert sum(1 for r in T["units"] if r["card_id"] == c["id"]) == n_units * len(c["variants"])
        for v in c["variants"]:
            vr = next(r for r in T["variants"] if r["card_id"] == c["id"] and r["variant_id"] == v["id"])
            assert vr["n_valid"] == len(v["valid_answers"])
            assert vr["n_invalid_minimal"] == sum(1 for a in v["invalid_answers"] if a["kind"] == "minimal")
            assert vr["n_copy"] == sum(1 for a in v["invalid_answers"] if a["kind"] == "copy")
            assert vr["n_must_transfer"] == len(v["must_transfer"]) and vr["n_probes"] == len(v["probes"])
            assert vr["n_must_not_transfer"] == len(v["must_not_transfer"])
            assert vr["n_rule_checks"] == sum(len(r["checks"]) for r in c["target"]["rules"]) + sum(len(r["checks"]) for r in v.get("rules_add", []))
            assert vr["n_must"] + vr["n_may"] + vr["n_must_not"] + vr["n_unclear"] == n_units
            assert vr["n_direct"] + vr["n_inferred"] + vr["n_default"] == n_units
            assert vr["n_judge"] == sum(1 for x in v["must_transfer"] + v["must_not_transfer"] if x["spec"][0].startswith("judge_"))
    d01 = next(r for r in T["cards"] if r["card_id"] == "D01_stockholm_parking")
    c01 = next(r for r in T["cards"] if r["card_id"] == "C01_calver_compare")
    assert (d01["n_spans"], d01["n_relation_units"], d01["n_detail_units"]) == (50, 10, 7)
    assert (c01["n_spans"], c01["n_relation_units"], c01["n_detail_units"]) == (47, 8, 7)
    # unit rows of one variant: spans and characters of a unit
    u = next(r for r in T["units"] if r["card_id"] == "D01_stockholm_parking" and r["unit_id"] == "I1")
    c, _ = cards[0]
    assert u["n_spans"] == sum(1 for s in c["source_spans"] if s.get("unit") == "I1")
    assert u["chars"] == sum(len(s["text"]) for s in c["source_spans"] if s.get("unit") == "I1")
    S = E.stats_summary(T)
    assert sum(r["n_variants"] for r in S["by_role"]) == 14 and abs(sum(r["share"] for r in S["by_role"]) - 1) < 1e-3
    assert {r["subset"]: r["n_variants"] for r in S["by_subset"]} == {"core": 4, "ambiguity": 10}
    assert {r["model_assistance"]: r["n_variants"] for r in S["by_model_assistance"]} == {"drafted": 14}
    assert sum(r["n_units"] for r in S["licence_label_by_role_kind"]) == len(T["units"])


def test_statistics_files_have_the_specified_columns():
    cards = [load(n) for n in NAMES]
    T = E.stats_tables([(p, c) for c, p in cards])
    with tempfile.TemporaryDirectory() as d:
        E.write_stats(T, E.stats_summary(T), d)
        for name, cols in (("cards", E.CARD_COLS), ("variants", E.VARIANT_COLS), ("units", E.UNIT_COLS), ("spans", E.SPAN_COLS)):
            with open(os.path.join(d, name + ".csv"), encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            assert list(rows[0].keys()) == cols and len(rows) == len(T[name])
        s = json.load(open(os.path.join(d, "summary.json"), encoding="utf-8"))
        for k in ("by_family", "by_role", "by_cue", "by_fit", "by_source_type", "by_domain", "by_relation_family", "by_model_assistance",
                  "by_subset", "role_x_cue_x_fit", "licence_label_by_role_kind", "basis_by_label", "unclear_rate", "spans_per_card",
                  "span_chars", "units_per_card", "checks_per_variant", "answers_per_variant", "example_length"):
            assert k in s, k


# ---------------------------------------------------------------- tokenizers
def test_token_labels_cover_every_licensed_span():
    for name in TOKENIZERS:
        tok = tokenizer(name)
        if tok is None:
            continue
        for n in NAMES:
            for r in records(n)[1]:
                out = E.token_labels(r, tok)
                d = out["diagnostics"]
                assert len(out["input_ids"]) == len(out["token_labels"])
                assert d["licensed_spans_without_overlapping_token"] == [], (name, r["record_id"], d)
                assert d["licensed_spans_without_labelled_token"] == [], (name, r["record_id"], d)
                for s in r["spans"]:
                    if s["kind"] != "context" and s["label"] in E.LABEL_ID:
                        lo, hi = out["span_token_ranges"][s["span_id"]]
                        assert hi > lo
                        assert any(l == E.LABEL_ID[s["label"]] for l in out["token_labels"][lo:hi])


def test_token_labels_ignore_outside_context_and_unclear():
    for name in TOKENIZERS:
        tok = tokenizer(name)
        if tok is None:
            continue
        c, recs = records("D01_stockholm_parking")
        r = next(x for x in recs if x["record_id"].endswith("analogy-implied-full::single::orig"))
        out = E.token_labels(r, tok)
        lab = out["token_labels"]
        lo = min(v[0] for v in out["span_token_ranges"].values())
        hi = max(v[1] for v in out["span_token_ranges"].values())
        assert all(x == E.IGNORE for x in lab[:lo - 1]) and all(x == E.IGNORE for x in lab[hi + 1:])
        unclear = [s for s in r["spans"] if s["label"] == "UNCLEAR"]
        assert unclear
        for s in unclear:   # a token that overlaps an UNCLEAR span most is IGNORE
            a, b = out["span_token_ranges"][s["span_id"]]
            assert E.IGNORE in lab[a:b]
        may = E.token_labels(r, tok, context_as_may=True)["token_labels"]
        assert sum(1 for x in may if x == E.LABEL_ID["MAY"]) > sum(1 for x in lab if x == E.LABEL_ID["MAY"])


def test_missing_message_content_raises():
    try:
        E.locate_messages("hello world", [{"role": "user", "content": "goodbye"}])
    except E.ExportError:
        return
    raise AssertionError("an absent content must raise")


def test_token_labels_match_a_character_level_reference():
    """Independent check: label every character by its span, then vote per token."""
    tok = tokenizer(TOKENIZERS[0])
    if tok is None:
        return
    c, recs = records("C01_calver_compare")
    r = recs[0]
    out = E.token_labels(r, tok)
    rendered = tok.apply_chat_template(r["messages"], tokenize=False, add_generation_prompt=True)
    offs = E.locate_messages(rendered, r["messages"])
    char = [None] * len(rendered)
    for k, s in enumerate(r["spans"]):
        a = offs[s["message_index"]] + s["char_start"]
        for i in range(a, a + s["char_end"] - s["char_start"]):
            char[i] = k
    enc = tok(rendered, add_special_tokens=False, return_offsets_mapping=True)
    for t, (a, b) in enumerate(enc["offset_mapping"]):
        votes = {}
        for i in range(a, b):
            if char[i] is not None:
                votes[char[i]] = votes.get(char[i], 0) + 1
        if not votes:
            assert out["token_labels"][t] == E.IGNORE
            continue
        k = min(votes, key=lambda x: (-votes[x], x))
        s = r["spans"][k]
        want = E.LABEL_ID.get(s["label"], E.IGNORE) if s["kind"] != "context" else E.IGNORE
        assert out["token_labels"][t] == want, (t, rendered[a:b], s["span_id"])


if __name__ == "__main__":
    fails = passed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
                print("ok  ", name)
            except Exception as e:   # noqa: BLE001
                fails += 1
                print("FAIL", name, type(e).__name__, str(e)[:400])
    print(f"{passed} passed, {fails} failed")
    sys.exit(1 if fails else 0)
