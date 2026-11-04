"""The v1 seed linter must pass good cards and catch bad ones.

Run: python -I tests/test_seed_lint_v1.py      (or: python -m pytest tests/test_seed_lint_v1.py)
"""
import copy
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
import checks_v1 as V  # noqa: E402
import seed_lint_v1 as L  # noqa: E402

DRAFTS = os.path.join(ROOT, "data", "seeds_v1_draft")


def load(name):
    with open(os.path.join(DRAFTS, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def errors(card, **kw):
    return [m for lv, m in L.lint_card(card, **kw).items if lv == "ERROR"]


def has(errs, text):
    return any(text in e for e in errs)


def test_good_cards_pass():
    for f in sorted(os.listdir(DRAFTS)):
        if f.endswith(".json"):
            card = load(f[:-5])
            assert errors(card) == [], (f, errors(card)[:3])


def test_release_mode_blocks_drafts():
    errs = errors(load("D02_social_norm_library"), release=True, gold=False)
    assert has(errs, "status is still draft")
    assert has(errs, "human_review.realism not filled")
    assert has(errs, "needs two-annotator adjudication")


def test_bad_card_is_caught():
    bad = load("D01_stockholm_parking")
    bad["provenance"]["references"] = []
    bad["source_example"]["text"] = "Stockholm charged drivers. Prices changed by hour. It worked."
    bad["source_example"]["incidental_details"] = bad["source_example"]["incidental_details"][:2]
    bad["cells_not_applicable"] = []
    v = bad["variants"][1]                                   # analogy-implied-full
    v["text"] = "Don't do it like this:\n\n{EX}"              # implied cue that states the role
    v["must_transfer"][0]["basis"].pop("ambiguity")           # P1: implied check without ambiguity flag
    bad["variants"][0]["must_transfer"][0]["basis"] = {"type": "stated", "quote": "words the prompt never says"}
    bad["copy_answers"]["counter-stated-full"] = bad["reference_solutions"]["counter-stated-full"]
    errs = errors(bad, gold=False)
    for text in ["references with citations", "sentences; at least 8", "2 incidental details", "missing and not marked",
                 "implied cue states the role", "needs ambiguity clear/ambiguous", "stated quote not found"]:
        assert has(errs, text), (text, errs)
    # gold run on a card that is otherwise valid: a copy answer equal to the gold must be flagged
    bad2 = load("D01_stockholm_parking")
    bad2["copy_answers"]["counter-stated-full"] = bad2["reference_solutions"]["counter-stated-full"]
    assert has(errors(bad2), "copy answer for counter-stated-full passes")


def test_pilot_p5_stricter_bound_is_caught():
    """Pilot P5: the prompt allowed ten words but the check allowed only eight."""
    card = load("D02_social_norm_library")
    card["target"]["rules"][2] = {"id": "R3", "text": "Each message text has at most ten words.",
                                  "checks": [{"id": "R3a", "spec": ["json_all_words_le", "messages[].text", 8]}]}
    assert has(errors(card, gold=False), "bound 8 in json_all_words_le does not appear")
    card["target"]["rules"][2]["checks"][0]["spec"][2] = 10
    assert not has(errors(card, gold=False), "does not appear in its basis text")


def test_hidden_ban_is_caught():
    """P1-style: banning a word that neither the prompt nor the source ever mentions."""
    card = load("D01_stockholm_parking")
    card["variants"][0]["must_not_transfer"].append(
        {"id": "L9", "what": "no colour names", "spec": ["text_absent", ["Red", "Amber"]], "basis": {"type": "stated", "quote": "not its details"}})
    assert has(errors(card, gold=False), "terms never mentioned in the prompt")


def test_leak_term_from_target_is_caught():
    card = load("D05_release_train_portal")
    card["source_example"]["incidental_details"][2]["leak_terms"].append("portal")
    assert has(errors(card, gold=False), "also appears in the target")


def test_checker_rejects_round_robin_for_hash_analogy():
    card = load("C04_grader_assignment")
    v = next(x for x in card["variants"] if x["id"] == "analogy-stated-full")
    rr = "```python\ndef assign(script_ids, graders):\n    return {s: graders[i % len(graders)] for i, s in enumerate(sorted(script_ids))}\n```"
    r = V.score_v1(rr, card, v)
    assert r["format_ok"] and r["constraint_ok"] and r["transfer_ok"] is False, r["detail"]


def test_format_failure_is_not_leakage():
    card = load("D03_group_lending_lab")
    r = V.score_v1("I would suggest groups of five.", card, card["variants"][0])
    assert r["format_ok"] is False and r["leak"] is None and r["transfer_ok"] is None


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except AssertionError as e:
                fails += 1
                print("FAIL", name, str(e)[:300])
    sys.exit(1 if fails else 0)
