"""Draw the study framework figure: docs/figures/framework.png

Usage: python -I scripts/make_framework_figure.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "docs" / "figures" / "framework.png"
LANES = [
    ("Dataset", "#e7f1fb", "#2f6db3"),
    ("1  Behaviour", "#e5f4e4", "#2e7d32"),
    ("2  Mechanism", "#f9eeda", "#a86b00"),
    ("3  Correction", "#efedff", "#5b4bb7"),
]
BOXES = [
    # lane 0: dataset
    [("Sources", "fresh seeds and adapted real cases (test)\npublic sets: Super-NI, AnaloBench,\nARN, Lost in Conversation (train)\nWildChat / OASST2 for realism"),
     ("Seed card", "target task + source example\nrelation + user constraints\ngold scope: MUST / MAY / MUST NOT"),
     ("Variants", "role: analogy / requirement /\ncounter-example\nfit (full, partial, wrong)\ncue (stated, implied), turns"),
     ("Review and split", "two blind reviewers, agreement\ntrain / dev / hidden test\nheld-out task families\ncontamination checks")],
    # lane 1: behaviour
    [("Models", "open 3B to 8B (local GPU)\nfrontier GPT (pinned API\nsnapshots, no-training policy\nfor the hidden test)"),
     ("Conditions", "no example\nplain (realistic)\nscope-inference prompt\nexplicit scope (oracle)"),
     ("Automatic scorer", "format, user rules kept,\nrequired transfer done,\nforbidden detail leaked\n-> joint success"),
     ("Behaviour result", "failure rate per role\nharmful vs missed transfer\nseed-level bootstrap CIs")],
    # lane 2: mechanism
    [("Matched pairs", "dev prompts that differ\nonly in the example's role"),
     ("Locate", "logit lens and probes\nwith lexical controls\n(read-out only)"),
     ("Test causally", "activation patching by layer\nand head on held-out data"),
     ("Intervene", "ablate selected components\nvs random ablations of same size\ngeneral-ability check")],
    # lane 3: correction
    [("Training data", "train split only (public-derived)\ngold scope used in training,\nnever at test time"),
     ("LoRA objective", "answer loss\n+ scope prediction loss\n+ paired consistency loss"),
     ("Where to train", "layers found in stage 2\nvs all layers, random layers"),
     ("Evaluation", "vs prompting, SFT, LoRA baselines\nheld-out task families\nGSM8K / MMLU drift, 3 seeds")],
]

W, H = 16, 11.8
fig, ax = plt.subplots(figsize=(W, H), dpi=150)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

lane_h, gap, top = 2.45, 0.25, H - 0.75
label_w, x0, bw, bgap = 1.7, 2.0, 3.15, 0.35
centers = {}
for li, ((name, fill, edge), boxes) in enumerate(zip(LANES, BOXES)):
    y = top - (li + 1) * lane_h - li * gap
    ax.add_patch(FancyBboxPatch((0.15, y), W - 0.3, lane_h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc=fill, ec="none", alpha=0.65))
    ax.text(0.25 + label_w / 2, y + lane_h / 2, name, ha="center", va="center", fontsize=13, weight="bold", color=edge)
    for bi, (title, body) in enumerate(boxes):
        bx = x0 + bi * (bw + bgap)
        by, bh = y + 0.18, lane_h - 0.36
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.02,rounding_size=0.1",
                                    fc="white", ec=edge, lw=1.4))
        ax.text(bx + bw / 2, by + bh - 0.28, title, ha="center", va="center", fontsize=11, weight="bold", color=edge)
        ax.text(bx + bw / 2, by + (bh - 0.5) / 2, body, ha="center", va="center", fontsize=8.6, color="#222", linespacing=1.35)
        centers[(li, bi)] = (bx, by, bw, bh)
        if bi:
            px, py, pw, ph = centers[(li, bi - 1)]
            ax.add_patch(FancyArrowPatch((px + pw + 0.03, py + ph / 2), (bx - 0.03, by + bh / 2),
                                         arrowstyle="-|>", mutation_scale=14, color=edge, lw=1.4))


def down(a, b, color, text=None, dx=0.0):
    ax_, ay, aw, ah = centers[a]
    bx_, by_, bw_, bh_ = centers[b]
    start = (ax_ + aw / 2 + dx, ay - 0.02)
    end = (bx_ + bw_ / 2 + dx, by_ + bh_ + 0.02)
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14, color=color, lw=1.6,
                                 connectionstyle="arc3,rad=0"))
    if text:
        ax.text((start[0] + end[0]) / 2 + 0.1, (start[1] + end[1]) / 2, text, fontsize=8.5, color=color,
                ha="left", va="center", style="italic")


down((0, 3), (1, 1), "#2f6db3", "validated test items")
down((1, 3), (2, 0), "#2e7d32", "failing cases")
down((2, 2), (3, 2), "#a86b00", "selected layers")
ax.text(W / 2, H - 0.35, "Study framework: Role-Aware Selective Transfer in LLMs", ha="center", va="center",
        fontsize=15, weight="bold", color="#222")
ax.text(W / 2, 0.25, "Main question: when a user gives an example, does the model use it according to its intended role? "
        "If not, why, and can training fix it?", ha="center", va="center", fontsize=10, color="#444")
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, bbox_inches="tight", facecolor="white")
print("wrote", OUT)
