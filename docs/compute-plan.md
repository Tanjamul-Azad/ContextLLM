# Compute plan (estimates, 2026-11-03)

Numbers are rough. Fix them after the pilot, when benchmark size and model count are known.

## Total need

| Work | Hardware | Estimate |
| --- | --- | --- |
| Pilot and behavioural study (inference only) | one 24GB GPU, or 8GB with 4-bit models; API for frontier models and judge | 10–30 GPU-hours; API about $50–200 |
| Method training (QLoRA 7–8B; SFT, DPO, ours, ablations, 3 seeds, 2 models) | 16GB+ GPU; 40–80GB is easier | 30–40 runs, about 150–300 A100-hours |
| Optional probing / patching | 24GB GPU | small |

## Available hardware

| GPU | Owner | Use |
| --- | --- | --- |
| RTX 4060, 8GB | Tanjamul | Pilot inference, data building, 3–4B experiments, 4-bit 7–8B inference. Not 8B paired training. |
| RTX 5070 Ti, 16GB | friend | Main 8B QLoRA runs (SFT, DPO, ours), batch 1–2 with gradient checkpointing. Needs PyTorch 2.7+ / CUDA 12.8 and recent bitsandbytes / Unsloth (Blackwell). |
| Kaggle, 2×T4, about 30 h/week free | free | Extra evaluation runs. No bf16 on T4. |
| GCP free trial, $300 | free | Final 8B runs on spot A100 (about $1–1.5/h). |

## Split of work

1. Ablations and seeds on 3–4B models, on both local GPUs in parallel.
2. Core 8B runs (baselines and ours, 3 seeds) on the 5070 Ti.
3. No self-hosted 70B models. Use an API if needed.
4. Final big runs on GCP spot A100 if time is short. Save checkpoints often.

Time is the bottleneck on a 5070 Ti, not memory. Expect 1.5–2x the A100 time.

## GCP credit caveats

- Free-trial accounts have no GPU quota. Upgrade to a paid account first; the remaining credit stays.
- Request GPU quota early. New accounts are sometimes slow or rejected.
- Credit expires 90 days after the account is opened. Open it for the training phase (about Feb–Mar 2027), not now.
- A card is required. Set a budget alert and delete VMs after use, since charges start when credit runs out.
- Also ask sir about Google Cloud research credits for academics.
- Modal gives monthly free credit (about $30 last known) with A100/H100. Good for small jobs.

## Risks

- Friend's GPU availability during the training weeks. Agree on overnight use or remote access (SSH / Tailscale) beforehand.
- Verify current GPU prices and free-credit terms before relying on them.
