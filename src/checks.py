"""Automatic checks for model answers. No LLM judge is used."""
import ast
import json
import os
import re
import subprocess
import sys
import tempfile

# Generated code is run only if it avoids these calls.
UNSAFE = re.compile(r"\b(subprocess|shutil|os\.remove|os\.unlink|os\.system|os\.rmdir|socket|ctypes)\b")


# ---------------------------------------------------------------- extraction
def extract_json(text):
    """Return the first JSON object in the answer, or None."""
    t = re.sub(r"```(?:json)?", "", text)
    dec = json.JSONDecoder()
    for i, ch in enumerate(t):
        if ch == "{":
            try:
                obj, _ = dec.raw_decode(t[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return None


def extract_code(text, func):
    """Return the Python code that defines `func`, or None."""
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    candidates = blocks + [text]
    for code in candidates:
        if f"def {func}" not in code:
            continue
        try:
            ast.parse(code)
            return code
        except SyntaxError:
            continue
    return None


def json_strings(obj):
    """All string values (and keys of nested items are skipped), joined."""
    out = []

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, (str, int, float)) and not isinstance(o, bool):
            out.append(str(o))

    walk(obj)
    return "\n".join(out)


# ---------------------------------------------------------------- helpers
def get_path(obj, path):
    """'levels[].name' -> list of values."""
    cur = [obj]
    for tok in path.split("."):
        nxt = []
        many = tok.endswith("[]")
        key = tok[:-2] if many else tok
        for o in cur:
            if not isinstance(o, dict) or key not in o:
                continue
            v = o[key]
            if many:
                if isinstance(v, list):
                    nxt.extend(v)
            else:
                nxt.append(v)
        cur = nxt
    return cur


def term_regex(term):
    pre = r"(?<![A-Za-z0-9])" if term[:1].isalnum() else ""
    post = r"(?![A-Za-z0-9])" if term[-1:].isalnum() else ""
    return re.compile(pre + re.escape(term) + post, re.I)


def has_word(value, words):
    s = str(value)
    return any(term_regex(w).search(s) for w in words)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def expand(tests, key):
    src = tests[key]
    for name, body in tests.items():
        if name.startswith("_"):
            src = src.replace("{" + name + "}", body)
    return src


def run_py_test(code, test_src, timeout=30):
    if UNSAFE.search(code):
        return False, "unsafe code not run"
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "t.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(code + "\n\n" + test_src)
        try:
            r = subprocess.run([sys.executable, "-I", path], cwd=d, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "timeout"
        return r.returncode == 0, (r.stderr or "")[-300:]


# ---------------------------------------------------------------- one check
def run_check(spec, ans, seed):
    """ans = {'obj': dict|None, 'text': str, 'code': str|None}. Returns (passed, note)."""
    kind = spec[0]
    obj, text, code = ans["obj"], ans["text"], ans["code"]

    if kind == "text_absent":
        hits = [t for t in spec[1] if term_regex(t).search(text)]
        return not hits, ",".join(hits)
    if kind == "text_present":
        return any(term_regex(t).search(text) for t in spec[1]), ""
    if kind == "regex_absent":
        m = re.search(spec[1], text, re.I)
        return m is None, m.group(0) if m else ""
    if kind == "regex_present":
        return re.search(spec[1], text, re.I) is not None, ""

    if kind == "py_test":
        if code is None:
            return False, "no code"
        return run_py_test(code, expand(seed["tests"], spec[1]))

    if obj is None:
        return False, "no json"
    vals = get_path(obj, spec[1])

    if kind == "json_len_between":
        ok = len(vals) == 1 and isinstance(vals[0], list) and spec[2] <= len(vals[0]) <= spec[3]
        return ok, str(len(vals[0])) if vals and isinstance(vals[0], list) else "missing"
    if kind == "json_all_int":
        return bool(vals) and all(isinstance(v, int) and not isinstance(v, bool) for v in vals), str(vals)[:80]
    if kind == "json_all_num":
        return bool(vals) and all(is_num(v) for v in vals), str(vals)[:80]
    if kind == "json_all_le":
        return bool(vals) and all(is_num(v) and v <= spec[2] for v in vals), str(vals)[:80]
    if kind == "json_increasing":
        ok = len(vals) >= 2 and all(is_num(v) for v in vals) and all(b > a for a, b in zip(vals, vals[1:]))
        return ok, str(vals)[:80]
    if kind == "json_eq":
        ok = bool(vals) and str(vals[0]).strip().lower() == str(spec[2]).strip().lower()
        return ok, str(vals)[:80]
    if kind == "json_is_bool":
        return bool(vals) and isinstance(vals[0], bool), str(vals)[:80]
    if kind == "json_all_word":
        return bool(vals) and all(has_word(v, spec[2]) for v in vals), str(vals)[:80]
    if kind == "json_any_word":
        return any(has_word(v, spec[2]) for v in vals), str(vals)[:80]
    if kind == "json_no_word":
        return bool(vals) and not any(has_word(v, spec[2]) for v in vals), str(vals)[:80]
    if kind == "json_all_match":
        return bool(vals) and all(re.search(spec[2], str(v), re.I if spec[2] == r"^\s*zone\b" else 0) for v in vals), str(vals)[:80]
    if kind == "json_none_match":
        flags = re.I if spec[2] == r"^\s*zone\b" else 0
        return bool(vals) and not any(re.search(spec[2], str(v), flags) for v in vals), str(vals)[:80]
    if kind == "json_count_match_ge":
        flags = re.I if spec[2] == r"^\s*zone\b" else 0
        return sum(bool(re.search(spec[2], str(v), flags)) for v in vals) >= spec[3], str(vals)[:80]
    if kind == "json_count_in_lt":
        return sum(1 for v in vals if v in spec[2]) < spec[3], str(vals)[:80]
    if kind == "json_all_words_le":
        return bool(vals) and all(len(str(v).split()) <= spec[2] for v in vals), str(vals)[:80]
    if kind == "json_all_nonempty":
        return bool(vals) and all(str(v).strip() for v in vals), ""
    if kind in ("json_exists_item", "json_not_exists_item"):
        items = vals[0] if vals and isinstance(vals[0], list) else []
        found = any(isinstance(it, dict) and all(has_word(it.get(f, ""), ws) for f, ws in spec[2].items()) for it in items)
        return (found if kind == "json_exists_item" else (bool(items) and not found)), ""
    if kind == "json_first_item_word":
        items = vals[0] if vals and isinstance(vals[0], list) else []
        items = [it for it in items if isinstance(it, dict) and is_num(it.get(spec[2]))]
        if not items:
            return False, "no ordered items"
        first = min(items, key=lambda it: it[spec[2]])
        return has_word(first.get(spec[3], ""), spec[4]), str(first.get(spec[3], ""))[:80]
    raise ValueError(f"unknown check {kind}")


# ---------------------------------------------------------------- scoring
def parse_answer(output, seed):
    if seed["family"] == "code":
        code = extract_code(output, seed["func"])
        return {"obj": None, "code": code, "text": code or "", "format_ok": code is not None}
    obj = extract_json(output)
    return {"obj": obj, "code": None, "text": json_strings(obj) if obj else "", "format_ok": obj is not None}


def score(output, seed, role):
    """Score one answer. role=None means the no-example baseline."""
    ans = parse_answer(output, seed)
    detail = {}
    cons = [run_check(c, ans, seed) for c in seed["constraints"]]
    detail["constraints"] = [list(map(str, c)) for c in cons]
    res = {"format_ok": ans["format_ok"], "constraint_ok": ans["format_ok"] and all(p for p, _ in cons)}
    if role is None:
        res.update({"transfer_ok": None, "leak": None, "joint": res["constraint_ok"], "marker": None})
        res["detail"] = detail
        return res
    trans, leaks = [], []
    for kind, spec in seed["roles"][role]["checks"]:
        r = run_check(spec, ans, seed)
        (trans if kind == "transfer" else leaks).append(r)
    marker = run_check(seed["marker"], ans, seed)[0] if ans["format_ok"] else False
    res["transfer_ok"] = ans["format_ok"] and all(p for p, _ in trans)
    res["leak"] = (not ans["format_ok"]) or any(not p for p, _ in leaks)
    res["joint"] = res["constraint_ok"] and res["transfer_ok"] and not res["leak"]
    res["marker"] = marker
    detail["transfer"] = [list(map(str, t)) for t in trans]
    detail["leakage"] = [list(map(str, x)) for x in leaks]
    res["detail"] = detail
    return res
