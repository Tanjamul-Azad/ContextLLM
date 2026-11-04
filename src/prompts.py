"""Build the prompt for every (seed, role, wording, turns) condition."""
from seeds import SEEDS

ROLES = ["analogy", "requirement", "counter"]
WORDINGS = ["plain", "explicit"]
TURNS = ["single", "multi"]
ACK = "Understood. Is there anything else I should take into account before I give the final answer?"
FINAL = "Now give the final answer in the format I asked for."


def role_text(seed, role, wording):
    r = seed["roles"][role]
    txt = r["plain"].replace("{EX}", seed["example"])
    if wording == "explicit":
        txt += "\n" + r["explicit"]
    return txt


def build(seed, role, wording, turns):
    head = f"{seed['task']}\n{seed['rules']}"
    if role is None:
        return [{"role": "user", "content": f"{head}\n\n{seed['format']}"}]
    ex = role_text(seed, role, wording)
    if turns == "single":
        return [{"role": "user", "content": f"{head}\n\n{ex}\n\n{seed['format']}"}]
    return [
        {"role": "user", "content": f"{head}\n\n{seed['format']}"},
        {"role": "assistant", "content": ACK},
        {"role": "user", "content": f"{ex}\n\n{FINAL}"},
    ]


def all_conditions():
    """Yield (item_id, seed, role, wording, turns, messages)."""
    for s in SEEDS:
        yield f"{s['id']}|none|-|single", s, None, "-", "single", build(s, None, "-", "single")
        for role in ROLES:
            for w in WORDINGS:
                for t in TURNS:
                    yield f"{s['id']}|{role}|{w}|{t}", s, role, w, t, build(s, role, w, t)
