"""Write one Colab notebook per experiment into notebooks/.

Each notebook clones the GitHub repo, installs packages, runs one experiment and
copies its outputs to Google Drive (DL paper/03_Results/<run date>/...).
Usage: python -I scripts/make_notebooks.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"
REPO = "https://github.com/Tanjamul-Azad/ContextLLM.git"

SETUP = [
    "# Setup: GPU runtime (Runtime > Change runtime type > T4 GPU), then run this cell.\n",
    "from google.colab import drive\n",
    "drive.mount('/content/drive')\n",
    "DRIVE = '/content/drive/MyDrive/DL paper'\n",
    f"!git clone -q {REPO} /content/ContextLLM || (cd /content/ContextLLM && git pull -q)\n",
    "%cd /content/ContextLLM\n",
    "!pip -q install -r requirements.txt\n",
    "!nvidia-smi --query-gpu=name,memory.total --format=csv\n",
]


def save_cell(src_dir, name):
    return [
        "# Copy outputs to Drive, in a folder named by date and time so runs never overwrite each other.\n",
        "import datetime, shutil, os\n",
        "stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')\n",
        f"dst = f'{{DRIVE}}/03_Results/{name}/{{stamp}}'\n",
        f"shutil.copytree('{src_dir}', dst, dirs_exist_ok=True)\n",
        "print('saved to', dst)\n",
    ]


def nb(title, intro, cells):
    md = {"cell_type": "markdown", "metadata": {}, "source": [f"# {title}\n", "\n", intro]}
    code = [{"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": c} for c in cells]
    return {"nbformat": 4, "nbformat_minor": 5, "cells": [md] + code,
            "metadata": {"accelerator": "GPU", "colab": {"provenance": []},
                         "kernelspec": {"name": "python3", "display_name": "Python 3"}}}


NOTEBOOKS = {
    "01_validate_checks.ipynb": nb(
        "01 Validate the automatic checks",
        "Shows that correct hand-written answers pass every check and copied answers are caught. Run this before any experiment.\n",
        [SETUP, ["!python -I tests/validate_checks.py\n", "!python -I -m pytest -q tests/test_seed_lint_v1.py\n"]]),
    "02_behaviour_open_models.ipynb": nb(
        "02 E4-E6 Behaviour test on open models",
        "Runs all 130 pilot prompts (10 seeds x 3 roles x 2 wordings x 2 turn types + baseline) on an open model and scores them. "
        "Choose MODEL: qwen2.5-3b, qwen2.5-7b-4bit or llama3.1-8b-4bit. Greedy decoding, so results repeat.\n",
        [SETUP, ["MODEL = 'qwen2.5-3b'\n", "!rm -rf results/behaviour/$MODEL\n", "!python -I src/run_behaviour.py $MODEL\n"],
         ["!python -I src/analyze.py\n", "print(open('results/behaviour/summary.md').read()[:4000])\n"],
         save_cell("results/behaviour", "behaviour")]),
    "03_behaviour_openai_api.ipynb": nb(
        "03 E4-E6 Behaviour test on OpenAI models",
        "Same prompts on pinned OpenAI snapshots. Add your key under Colab Secrets (key icon on the left) as OPENAI_API_KEY. "
        "Cost for all 130 prompts on one model was well under one US dollar.\n",
        [SETUP, ["from google.colab import userdata\n", "os_key = userdata.get('OPENAI_API_KEY')\n",
                 "import os; os.makedirs('local_only', exist_ok=True)\n",
                 "open('local_only/.env','w').write(f'OPENAI_API_KEY={os_key}\\n')\n"],
         ["MODEL = 'gpt-4.1-mini'  # or gpt-5.4-mini, gpt-5.4\n", "!rm -rf results/behaviour/$MODEL\n", "!python -I src/run_api.py $MODEL\n",
          "!python -I src/analyze.py\n"],
         save_cell("results/behaviour", "behaviour")]),
    "04_logit_lens.ipynb": nb(
        "04 E7 Logit-lens layer scan",
        "Reads every layer's guess at the token where the answer copies the example or not, for 5 probes and 3 roles. "
        "This is a read-out, not a causal test.\n",
        [SETUP, ["!python -I src/logit_lens.py qwen2.5-3b\n"],
         ["from IPython.display import Image, display\n", "import glob\n",
          "for p in sorted(glob.glob('results/logit_lens/qwen2.5-3b/*.png')): display(Image(p))\n"],
         save_cell("results/logit_lens", "logit_lens")]),
    "05_contamination.ipynb": nb(
        "05 E3 Contamination diagnostics",
        "Guided completion and Min-K% Prob on GSM8K, then on Super-NaturalInstructions, HumanEval, Spider and AnaloBench. "
        "These are diagnostics, not proof of clean data.\n",
        [SETUP, ["!python -I src/contamination.py qwen2.5-3b 60\n", "!python -I src/contamination_sources.py qwen2.5-3b 50\n",
                 "print(open('results/contamination/qwen2.5-3b/sources/README.md').read())\n"],
         save_cell("results/contamination", "contamination")]),
    "06_real_conversations.ipynb": nb(
        "06 E1 Example-giving turns in real conversations",
        "Samples WildChat-1M and OASST2 through the Hugging Face dataset viewer, filters candidate turns and labels them with a small model. "
        "Raw user text is written only to local_only/, which is never copied to Drive or GitHub. The model labels need a human check.\n",
        [SETUP, ["!python -I src/wildchat_mine.py 150 qwen2.5-3b wildchat\n", "!python -I src/wildchat_mine.py 150 qwen2.5-3b oasst\n"],
         ["import json\n", "for s in ['wildchat', 'oasst']: print(s, json.load(open(f'results/E1_{s}/summary.json'))['by_role'])\n"],
         save_cell("results/E1_wildchat", "E1_wildchat"), save_cell("results/E1_oasst", "E1_oasst")]),
    "07_kill_test_validation.ipynb": nb(
        "07 Kill test 1: does the failure survive validation?",
        "Runs the v1 seed cards under four conditions (no example, plain, scope-inference prompt, oracle) and prints the gate inputs. "
        "Only human-validated cards count; --dev runs on draft cards and is a pipeline check only. Rules: docs/goal-and-kill-tests.md section 2.\n",
        [SETUP, ["MODEL = 'qwen2.5-7b-4bit'  # open model; for API models add the key as in notebook 03\n",
                 "!python -I src/run_validation.py $MODEL --dev\n"],
         save_cell("results/validation_dev", "validation_dev")]),
    "08_kill_test_probe_patch.ipynb": nb(
        "08 Kill test 2: role probe and activation patching (development cards only)",
        "Collects last-token hidden states for every variant, trains a role probe on stated cues and tests it on implied cues "
        "(with a bag-of-words baseline), types each failure as inference or execution, then patches the stated-variant state into "
        "failing implied runs, with different-role and random-direction controls. Rules: docs/goal-and-kill-tests.md section 3.\n",
        [SETUP, ["!python -I src/role_probe_patch.py collect\n", "!python -I src/role_probe_patch.py probe\n"],
         ["!python -I src/role_probe_patch.py patch --layers 16,20,24,26,28\n", "!python -I src/role_probe_patch.py report\n"],
         save_cell("results/probe_patch_dev", "probe_patch_dev")]),
    "09_backbone_screen.ipynb": nb(
        "09 WP0.4 Backbone competence screen (development items, exploratory)",
        "Runs one candidate backbone on the 20 no-example items (10 v1 draft cards + 10 pilot seeds) and the 68 oracle variants, "
        "scores them, and rebuilds the summary table with 95% bootstrap intervals. A model is eligible as a method backbone if it "
        "solves at least 80% of the no-example tasks. Greedy decoding, max 1024 new tokens; resumable. "
        "Code answers are executed by the checker, which is not sandboxed. Pre-quantised 4-bit checkpoints.\n",
        [SETUP, ["# Candidates: qwen3-4b-2507-4bit, phi4-mini-4bit, gemma3-4b-4bit, llama3.2-3b-4bit, qwen3-8b-4bit,\n",
                 "# plus references qwen2.5-3b, qwen2.5-7b-4bit, llama3.1-8b-4bit\n",
                 "MODEL = 'qwen3-4b-2507-4bit'\n", "!python -I scripts/backbone_screen.py $MODEL\n"],
         ["!python -I scripts/backbone_screen_summary.py\n"],
         save_cell("results/backbone_screen", "backbone_screen")]),
}

OUT.mkdir(exist_ok=True)
for name, book in NOTEBOOKS.items():
    (OUT / name).write_text(json.dumps(book, indent=1), encoding="utf-8")
print(f"wrote {len(NOTEBOOKS)} notebooks to {OUT}")
