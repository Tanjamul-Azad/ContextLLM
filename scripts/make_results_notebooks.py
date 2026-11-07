"""Write and execute one results notebook per finished experiment.

The notebooks read the saved outputs in results/ (no GPU, no API calls), so every
model answer, score, table and figure from the pilot runs is visible inside the
notebook. They are executed here, so the outputs are stored in the .ipynb files and
show on GitHub and in Colab without running anything.

Also writes results/behaviour/answers/<model>.csv: one readable row per answer
(prompt, model answer, scores).

Usage: python -I scripts/make_results_notebooks.py [--no-exec]
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "results"
REPO = "https://github.com/Tanjamul-Azad/ContextLLM.git"
MODELS = ["qwen2.5-3b", "qwen2.5-7b-4bit", "llama3.1-8b-4bit", "gpt-4.1-mini", "gpt-5.4-mini", "gpt-5.4"]

SETUP = """# Works locally (run from the repo) and in Colab (clones the public repo; no GPU needed).
import os, json, subprocess
if not os.path.exists('results/behaviour'):
    if not os.path.exists('/content/ContextLLM'):
        subprocess.run(['git', 'clone', '-q', '%s', '/content/ContextLLM'], check=True)
    os.chdir('/content/ContextLLM')
import pandas as pd
pd.set_option('display.max_colwidth', 120); pd.set_option('display.width', 200)
from IPython.display import Image, Markdown, display
print('reading saved results from', os.path.abspath('results'))""" % REPO

TO_DRIVE = """# Optional, Colab only: copy these saved outputs into Google Drive (DL paper/03_Results/%s).
import shutil
try:
    from google.colab import drive
    drive.mount('/content/drive')
    for src in %r:
        dst = '/content/drive/MyDrive/DL paper/03_Results/%s/' + os.path.basename(src.rstrip('/'))
        shutil.copytree(src, dst, dirs_exist_ok=True); print('copied', src, '->', dst)
except ImportError:
    print('Not in Colab: skipped. The files are in the repo under', %r)"""


_n = [0]


def _id():
    _n[0] += 1
    return f"c{_n[0]:03d}"


def md(text):
    return {"cell_type": "markdown", "id": _id(), "metadata": {}, "source": text.strip("\n")}


def code(text):
    return {"cell_type": "code", "id": _id(), "metadata": {}, "execution_count": None, "outputs": [], "source": text.strip("\n")}


def notebook(cells):
    return {"nbformat": 4, "nbformat_minor": 5, "cells": cells,
            "metadata": {"colab": {"provenance": []},
                         "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                         "language_info": {"name": "python"}}}


def drive_cell(name, srcs):
    return code(TO_DRIVE % (name, srcs, name, srcs))


# ---------------------------------------------------------------- answers CSV
def export_answers():
    out_dir = ROOT / "results" / "behaviour" / "answers"
    out_dir.mkdir(exist_ok=True)
    cols = ["item", "seed", "role", "wording", "turns", "prompt", "answer",
            "format_ok", "constraint_ok", "transfer_ok", "leak", "joint", "copied_pattern"]
    for m in MODELS:
        base = ROOT / "results" / "behaviour" / m
        gens = {json.loads(l)["item"]: json.loads(l) for l in open(base / "generations.jsonl", encoding="utf-8")}
        with open(out_dir / f"{m}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for line in open(base / "scored.jsonl", encoding="utf-8"):
                s = json.loads(line)
                g = gens[s["item"]]
                prompt = "\n\n".join(f"[{x['role']}] {x['content']}" for x in g["messages"])
                w.writerow([s["item"], s["seed"], s["role"], s["wording"], s["turns"], prompt, g["output"],
                            s["format_ok"], s["constraint_ok"], s["transfer_ok"], s["leak"], s["joint"], s["marker"]])
    print("wrote answers CSVs to", out_dir)


# ---------------------------------------------------------------- notebooks
LOAD_BEHAVIOUR = """MODELS = %r
rows = []
for m in MODELS:
    gens = {json.loads(l)['item']: json.loads(l) for l in open(f'results/behaviour/{m}/generations.jsonl', encoding='utf-8')}
    for l in open(f'results/behaviour/{m}/scored.jsonl', encoding='utf-8'):
        s = json.loads(l); g = gens[s['item']]
        s['messages'] = g['messages']; s['answer'] = g['output']; rows.append(s)
df = pd.DataFrame(rows)
df['failed'] = ~df['joint'].astype(bool)
print(len(df), 'answers:', df.groupby('model').size().to_dict())""" % MODELS

HEADLINE = """# E4: failure rate (not joint success) on single-turn prompts, averaged over the three roles.
ex = df[(df.role != 'none') & (df.turns == 'single')]
t = ex.pivot_table(index='model', columns='wording', values='failed', aggfunc='mean').reindex(MODELS)[['plain', 'explicit']] * 100
t = t.rename(columns={'plain': 'failure % (plain wording)', 'explicit': 'failure % (explicit wording)'}).round(0)
display(t)"""

BY_ROLE = """# Plain wording, single turn: joint success by role (%), and how often the answer copied the source pattern.
p = df[(df.wording == 'plain') & (df.turns == 'single')]
ROLES = ['analogy', 'requirement', 'counter']
print('Joint success % (plain, single turn)')
display((p.pivot_table(index='model', columns='role', values='joint', aggfunc='mean').reindex(MODELS)[ROLES] * 100).round(0))
print('Copied the source pattern % (should be high for requirement, low for counter)')
display((p.pivot_table(index='model', columns='role', values='marker', aggfunc='mean').reindex(MODELS)[ROLES] * 100).round(0))"""

WHY_FAIL = """# Why plain answers failed (share of plain single-turn answers with an example).
p = df[(df.role != 'none') & (df.wording == 'plain') & (df.turns == 'single')].copy()
why = pd.DataFrame({
    'leaked a detail %': p.groupby('model')['leak'].apply(lambda s: (s == True).mean() * 100),
    'missed needed transfer %': p.groupby('model')['transfer_ok'].apply(lambda s: (s == False).mean() * 100),
    'broke a target rule %': p.groupby('model')['constraint_ok'].apply(lambda s: (s == False).mean() * 100),
    'bad format %': p.groupby('model')['format_ok'].apply(lambda s: (s == False).mean() * 100),
}).reindex(MODELS).round(0)
display(why)"""

FIGS = """for f in ['joint_by_role.png', 'copy_rate_by_role.png']:
    display(Image(f'results/behaviour/figures/{f}'))"""

PER_SEED = """# Per seed, plain single-turn: did the answer succeed (1) or fail (0)? Rows = seed x role, columns = model.
p = df[(df.role != 'none') & (df.wording == 'plain') & (df.turns == 'single')]
display(p.pivot_table(index=['seed', 'role'], columns='model', values='joint', aggfunc='mean')[MODELS].astype(int))"""

SHOW_FN = """def verdict(r):
    if not r['format_ok']: return 'FAIL (bad format)'
    bits = []
    if r['constraint_ok'] is False: bits.append('broke a target rule')
    if r['transfer_ok'] is False: bits.append('missed needed transfer')
    if r['leak'] is True: bits.append('leaked a detail it should not copy')
    return 'PASS' if r['joint'] else 'FAIL (' + ', '.join(bits) + ')'

def show(seed, role, wording='plain', turns='single', models=MODELS):
    sub = df[(df.seed == seed) & (df.role == role) & (df.wording == wording) & (df.turns == turns)]
    first = sub.iloc[0]
    print('=' * 100); print(f'SEED {seed} | role = {role} | wording = {wording} | turns = {turns}'); print('=' * 100)
    for msg in first['messages']:
        print(f"--- {msg['role'].upper()} ---"); print(msg['content'])
    for m in models:
        r = sub[sub.model == m]
        if r.empty: continue
        r = r.iloc[0]
        print(f"\\n>>> {m}: {verdict(r)}"); print(r['answer'].strip())
    print()"""

MD_INTRO = """# R1 Behaviour test (E4 to E6): every model answer and its score

This notebook shows the **saved outputs** of the pilot behaviour runs. Nothing is re-generated here, so it needs no GPU and costs nothing. To re-run the models themselves, use `02_behaviour_open_models` (GPU) or `03_behaviour_openai_api` (OpenAI key).

**What was run (4 to 6 November 2026).** 10 seeds (6 planning tasks with a JSON answer, 4 code tasks with unit tests). Each seed appears with no example, and with the same source example in three roles: *analogy* (borrow the idea only), *requirement* (follow it exactly), *counter-example* (avoid it). Each role is written in plain wording (the role is implied, as real users write) and explicit wording (the role is stated), in a single turn or across two turns. That gives 130 prompts per model.

| Model | Where it ran |
| --- | --- |
| Qwen2.5-3B-Instruct (bf16) | local RTX 4060 8 GB, greedy decoding |
| Qwen2.5-7B-Instruct (4-bit) | local RTX 4060 8 GB, greedy decoding |
| Llama-3.1-8B-Instruct (4-bit) | local RTX 4060 8 GB, greedy decoding |
| gpt-4.1-mini-2025-04-14 | OpenAI API |
| gpt-5.4-mini-2026-03-17 | OpenAI API |
| gpt-5.4-2026-03-05 (reasoning effort low) | OpenAI API |

**How each answer is scored** (scorer v1.1, `src/checks.py`): *format ok* (valid JSON or code that runs), *rules kept* (the user's own constraints hold), *transfer right* (what the role requires was carried over), *leaked* (a source detail the role forbids appears), *joint* = all of these at once. An answer **fails** if joint is false. *Copied pattern* marks whether the source's surface pattern appears; it should be high for requirement and low for counter-example.

**Caveat.** These are pilot numbers on 10 seeds. The seeds have not yet been checked by independent annotators, so treat the rates as provisional."""


def behaviour_nb():
    cells = [md(MD_INTRO), code(SETUP), code(LOAD_BEHAVIOUR),
             md("## 1. Headline: how often each model fails\nPlain wording is the realistic case. Explicit wording tells the model the role, so it works as an upper bound."),
             code(HEADLINE), code(BY_ROLE),
             md("## 2. Why the plain answers failed"), code(WHY_FAIL),
             md("## 3. Figures"), code(FIGS),
             md("## 4. Per seed\nThis shows which seeds are hard for every model and which only for small ones."), code(PER_SEED),
             md("## 5. The actual prompts and answers\nFor every seed and role (plain wording, single turn), the full prompt is printed once, then each model's answer with its verdict. "
                "Use `show(seed, role, wording, turns)` in a new cell to see any other condition, for example `show('C1_window_sum', 'counter', 'explicit', 'multi')`."),
             code(SHOW_FN)]
    all_seeds = sorted({json.loads(l)["seed"] for l in open(ROOT / "results/behaviour/qwen2.5-3b/scored.jsonl", encoding="utf-8")},
                       key=lambda s: (s[0] != "P", s))
    for s in all_seeds:
        cells.append(md(f"### {s}"))
        cells.append(code("\n".join(f"show('{s}', '{r}')" for r in ["analogy", "requirement", "counter"])))
    cells += [md("## 6. Every answer as a table\nOne CSV per model with the prompt, the answer and all scores: `results/behaviour/answers/<model>.csv`. They open in Excel or Google Sheets."),
              code("for m in MODELS:\n    a = pd.read_csv(f'results/behaviour/answers/{m}.csv')\n    print(m, a.shape, 'failed:', int((~a.joint.astype(bool) & (a.role != 'none')).sum()))\n"
                   "display(pd.read_csv('results/behaviour/answers/gpt-5.4.csv')[['item', 'answer', 'joint']].head(8))"),
              drive_cell("behaviour", ["results/behaviour"])]
    return notebook(cells)


def logit_nb():
    intro = """# R2 Logit-lens layer scan (E7) on Qwen2.5-3B: saved outputs

For five probe prompts, the same example is given in each of the three roles. At the first answer token where a copied answer and a non-copied answer differ, we read each layer's guess through the model's output head (the *logit lens*). `diff` = log-prob of the copied token minus the alternative: above 0 means the layer leans towards copying.

**What it shows.** The three roles start to separate around layers 23 to 28 of 36. **What it does not show.** This is a read-out, not a causal test. Causal tests (activation patching, ablation with random controls) are planned for the main study."""
    cells = [md(intro), code(SETUP),
             code("s = json.load(open('results/logit_lens/qwen2.5-3b/summary.json'))\n"
                  "rows = [{'probe': k, 'separation layer': v['separation_layer'], 'layers': v['n_layers'],\n"
                  "         **{f'final diff ({r})': v['final_diff'][r] for r in v['final_diff']},\n"
                  "         **{f'top token ({r})': v['final_top_token'][r] for r in v['final_top_token']},\n"
                  "         'role-correct at output': v['role_correct_at_output']} for k, v in s['probes'].items()]\n"
                  "display(pd.DataFrame(rows))"),
             code("scan = pd.read_csv('results/logit_lens/qwen2.5-3b/layer_scan.csv')\n"
                  "display(scan.pivot_table(index='layer', columns=['seed', 'role'], values='diff').round(2).tail(14))"),
             md("## Figures, one per probe")]
    cells.append(code("import glob\nfor p in sorted(glob.glob('results/logit_lens/qwen2.5-3b/*.png')):\n    print(os.path.basename(p)); display(Image(p))"))
    cells.append(drive_cell("logit_lens", ["results/logit_lens"]))
    return notebook(cells)


def contamination_nb():
    intro = """# R3 Contamination diagnostics (E3) on Qwen2.5-3B: saved outputs

Before reusing a public dataset, we test whether the model may have seen it in training. Two checks: **guided completion** (give the first half of an item and the dataset name; does the model reproduce the rest nearly word for word?) and **Min-K% Prob** (does the original text look less surprising to the model than a paraphrase of it?). A source is flagged if more than 5% of items come back near verbatim, or originals beat paraphrases in more than 70% of pairs.

These are diagnostics. A clean result does not prove the data was never seen."""
    cells = [md(intro), code(SETUP),
             md("## GSM8K (first run, 60 questions)"),
             code("print(json.dumps(json.load(open('results/contamination/qwen2.5-3b/summary.json')), indent=1))"),
             code("g = pd.read_csv('results/contamination/qwen2.5-3b/items.csv')\ndisplay(g.describe().round(3))"),
             md("## Candidate training sources (50 items each)"),
             code("display(Markdown(open('results/contamination/qwen2.5-3b/sources/README.md', encoding='utf-8').read()))"),
             code("import glob\nfor f in sorted(glob.glob('results/contamination/qwen2.5-3b/sources/*/items.csv')):\n"
                  "    d = pd.read_csv(f); print(f.split(os.sep)[-2] if os.sep in f else f, d.shape); display(d.head(5))"),
             drive_cell("contamination", ["results/contamination"])]
    return notebook(cells)


def e1_nb():
    intro = """# R4 Example-giving in real conversations (E1): saved outputs

Question: do real users give examples, and in which role? We sampled WildChat-1M (15,000 conversations) and OASST2 through the Hugging Face dataset viewer, kept English user turns, filtered candidates with keywords, and labelled them with a small model. A random sample was then checked by hand.

**Privacy.** Only hashes, lengths and labels are stored here. The raw user text stays on the local machine (`local_only/`) and is never uploaded.

**Caveat.** The 3B labeller agreed with the hand labels only 42% of the time, so the hand-checked numbers are the ones to trust."""
    cells = [md(intro), code(SETUP)]
    for s in ["wildchat", "oasst"]:
        cells += [md(f"## {'WildChat-1M' if s == 'wildchat' else 'OASST2'}"),
                  code(f"print(json.dumps(json.load(open('results/E1_{s}/summary.json')), indent=1))\n"
                       f"print(json.dumps(json.load(open('results/E1_{s}/handcheck_summary.json')), indent=1))"),
                  code(f"lab = pd.read_csv('results/E1_{s}/labels.csv'); hc = pd.read_csv('results/E1_{s}/handcheck_sample.csv')\n"
                       "print('model labels by role:'); display(lab.role.value_counts())\n"
                       "print('hand labels by role (checked sample):'); display(hc.hand_role.value_counts())\n"
                       "print('model vs hand label:'); display(pd.crosstab(hc.model_role, hc.hand_role))")]
    cells.append(drive_cell("E1_real_conversations", ["results/E1_wildchat", "results/E1_oasst"]))
    return notebook(cells)


def checks_nb():
    intro = """# R0 Scorer validation: saved outputs

Before trusting any score, we check the automatic checks themselves. `tests/validate_checks.py` feeds hand-written correct answers (which must pass) and deliberately copied answers (which must be caught) through every seed's checks. `tests/test_seed_lint_v1.py` tests the linter for the new v1 seed format. `scripts/recheck_identical.py` (run earlier on the GPU) confirmed that all three open models reproduce 16 of 16 saved answers exactly, so the open-model runs are repeatable."""
    cells = [md(intro), code(SETUP),
             code("import sys\nr = subprocess.run([sys.executable, '-I', 'tests/validate_checks.py'], capture_output=True, text=True)\nprint(r.stdout[-6000:], r.stderr[-2000:])"),
             code("r = subprocess.run([sys.executable, '-I', '-m', 'pytest', '-q', '--color=no', '-p', 'no:cacheprovider', 'tests/test_seed_lint_v1.py'], capture_output=True, text=True)\nprint(r.stdout[-3000:], r.stderr[-1000:])")]
    return notebook(cells)


NOTEBOOKS = {
    "R0_scorer_validation.ipynb": checks_nb,
    "R1_behaviour_answers.ipynb": behaviour_nb,
    "R2_logit_lens.ipynb": logit_nb,
    "R3_contamination.ipynb": contamination_nb,
    "R4_real_conversations.ipynb": e1_nb,
}


def main():
    export_answers()
    OUT.mkdir(parents=True, exist_ok=True)
    import nbformat
    for name, build in NOTEBOOKS.items():
        nb = nbformat.from_dict(build())
        if "--no-exec" not in sys.argv:
            from nbclient import NotebookClient
            NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
        nbformat.write(nb, OUT / name)
        print("wrote", OUT / name, f"{(OUT / name).stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
