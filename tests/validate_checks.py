"""Sanity test: hand-written correct answers must pass, copied answers must fail.

Run: python -I tests/validate_checks.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from checks import score  # noqa: E402
from seeds import SEEDS  # noqa: E402

J = json.dumps
P6_WHO = [("rows 21-30, farthest from the door", 1), ("rows 11-20", 2), ("rows 1-10", 3)]

GOLD = {
    "P1_helpdesk_triage": {
        "analogy": J({"levels": [{"name": "Critical", "response_hours": 2}, {"name": "High", "response_hours": 8}, {"name": "Normal", "response_hours": 48}]}),
        "requirement": J({"levels": [{"name": "Red", "response_hours": 2}, {"name": "Orange", "response_hours": 8}, {"name": "Green", "response_hours": 48}]}),
        "counter": J({"levels": [{"name": "Critical", "response_hours": 2}, {"name": "High", "response_hours": 8}, {"name": "Normal", "response_hours": 48}]}),
    },
    "P2_drone_pricing": {
        "analogy": J({"charges": [{"name": "Flight-time fee", "unit": "per flight hour", "price_bdt": 3000}], "maintenance_paid_by": "provider"}),
        "requirement": J({"charges": [{"name": "Power by the Hour plan", "unit": "per flight hour", "price_bdt": 3000}], "maintenance_paid_by": "provider"}),
        "counter": J({"charges": [{"name": "Season pass", "unit": "per acre per season", "price_bdt": 500}], "maintenance_paid_by": "provider"}),
    },
    "P3_incident_andon": {
        "analogy": J({"rules": [{"trigger": "Database outage", "action": "Pause deployments and restore the backup", "who_can_trigger": "Any developer"}]}),
        "requirement": J({"rules": [{"trigger": "Database outage (andon rule)", "action": "Pause deployments", "who_can_trigger": "Any developer"}]}),
        "counter": J({"rules": [{"trigger": "Database outage", "action": "Pause deployments and restore the backup", "who_can_trigger": "The two maintainers only"}]}),
    },
    "P4_workshop_survivorship": {
        "analogy": J({"assignment": "random", "track_students_who_leave": True, "steps": ["Offer seats at random", "Record who leaves and when", "Compare grades of everyone invited"]}),
        "requirement": J({"assignment": "random", "track_students_who_leave": True, "steps": ["Offer seats at random", "Record who leaves", "Credit: this follows Abraham Wald's reasoning"]}),
        "counter": J({"assignment": "random", "track_students_who_leave": False, "steps": ["Assign students at random", "Compare grades"]}),
    },
    "P5_newsletter_headlines": {
        "analogy": J({"headlines": ["Robotics Team Wins National Title", "New AI Lab Opens Next Month", "Library Now Open Until Midnight"]}),
        "requirement": J({"headlines": ["CHAMPIONS! Robotics Team Wins National Title", "COMING! New AI Lab Opens Next Month", "LATE! Library Now Open Until Midnight"]}),
        "counter": J({"headlines": ["Robotics Team Wins National Title", "New AI Lab Opens Next Month", "Library Now Open Until Midnight"]}),
    },
    "P6_exam_hall_boarding": {
        "analogy": J({"groups": [{"name": n, "order": o, "who": w} for n, (w, o) in zip(["Back rows", "Middle rows", "Front rows"], P6_WHO)]}),
        "requirement": J({"groups": [{"name": n, "order": o, "who": w} for n, (w, o) in zip(["Zone 1", "Zone 2", "Zone 3"], P6_WHO)]}),
        "counter": J({"groups": [{"name": n, "order": o, "who": w} for n, (w, o) in zip(["Back rows", "Middle rows", "Front rows"], P6_WHO)]}),
    },
}

WIN = """def max_window_sum(nums, k{d}):
    s = sum(nums[:k]); best = s
    for i in range(k, len(nums)):
        s += nums[i] - nums[i - k]
        best = max(best, s)
    return best
"""
RETRY = """def retry_call(fn, attempts, sleep):
    delay = {start}
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                raise
            sleep(delay)
            delay = delay {op}
"""
UNIQ = """def unique_usernames(names):
    seen, out = set(), []
    for n in names:
        k = n.lower(){extra}
        if k not in seen:
            seen.add(k)
            out.append(n)
    return out
"""
PAGE = """def fetch_all(get_page, page_size):
    out, n = [], 1
    while True:
        b = get_page(n)
        {stop}
        out.extend(b)
        n += 1
    return out
"""
SHORT = "if len(b) < page_size:\n            out.extend(b)\n            return out"
EMPTY = "if not b:\n            break"


def code(s):
    return "```python\n" + s + "```"


GOLD.update({
    "C1_window_sum": {"analogy": code(WIN.format(d="")), "requirement": code(WIN.format(d="=7")), "counter": code(WIN.format(d=""))},
    "C2_retry_backoff": {"analogy": code(RETRY.format(start=1, op="* 2")), "requirement": code(RETRY.format(start=1, op="* 2")),
                         "counter": code(RETRY.format(start=0.5, op="* 1"))},
    "C3_dedupe_usernames": {"analogy": code(UNIQ.format(extra="")), "requirement": code(UNIQ.format(extra='.replace(".", "")')),
                            "counter": code(UNIQ.format(extra=""))},
    "C4_pagination": {"analogy": code(PAGE.format(stop=SHORT)), "requirement": code(PAGE.format(stop=EMPTY)),
                      "counter": code(PAGE.format(stop=SHORT))},
})

# A "copier" answer for the counter role is the requirement answer: it follows the example it should reject.
bad = 0
for s in SEEDS:
    g = GOLD[s["id"]]
    for role in ("analogy", "requirement", "counter"):
        r = score(g[role], s, role)
        ok = r["joint"] and (role == "analogy" or r["marker"] == (role == "requirement"))
        if not ok:
            bad += 1
            print("GOLD FAIL", s["id"], role, json.dumps(r["detail"])[:400])
    copier = score(g["requirement"], s, "counter")
    if copier["joint"] or not copier["marker"]:
        bad += 1
        print("COPIER NOT CAUGHT", s["id"], json.dumps(copier["detail"])[:400])
    base = score(g["analogy"], s, None)
    if not base["joint"]:
        bad += 1
        print("BASELINE FAIL", s["id"], json.dumps(base["detail"])[:300])
print(f"{len(SEEDS)} seeds checked, {bad} problems")
sys.exit(1 if bad else 0)
