# What a best paper does that we do not yet do

8 November 2026. Comparison with the AACL 2026 best paper: Sakhawat, Raiyan et al., "LLM-Ideoplasticity: Measuring Ideological Plasticity in the Political Behavior of LLMs as a Context-Conditioned Distribution" (IUT Dhaka), AACL 2026 long, pages 3167–3209. Status: notes only. Nothing here has been added to the proposal or plan yet.

## What made the paper strong

| Aspect | What they did |
| --- | --- |
| One-line thesis | Ideology is a conditional distribution, not a point, written formally as p ~ P(· \| c). Memorable names: "Ideoplasticity", "algorithmic monoculture". |
| External grounding | Responses are projected onto a coordinate system built from validated political science data (VAA to CHES, bagged ElasticNet, R² 0.75–0.80). |
| Instrument audit first | Judge Bias Score: the LLM judge is tested under option-order permutation before any result (directional 1.43% against a 10% ceiling set in advance). |
| Metrics | Eight metrics, each isolating one contextual axis, with closed-form equations in an appendix. |
| Construct validity | Multi-trait multi-method correlation matrix, leave-one-model-out and bootstrap stability, PCA (3 factors, 83%), permutation tests. |
| Breadth | 9 models from 7 developers, 12 languages including Bengali, 3 election years. |
| Findings | Two counter-intuitive results: chain-of-thought often increases instability; all models occupy about one third of the human party spread. |
| Figures | 3D headline Figure 1, pipeline figure, colour-coded master table, per-item heatmaps with a concrete inset (English "Completely Disagree" vs Bengali "Completely Agree"). |
| Reproducibility | Exact provider identifiers, verbatim prompts, code, data and a project page, plus an appendix map. |
| Honesty | Specific limitations and ethics sections. |

Their weaknesses: 9 models, one judge, temperature 0 only, a European coordinate system, and no training method.

## What we lack

1. **A one-line formal claim and a name.** State the thesis in one sentence and formalise it (answer A for task, example, role; gold sets with MUST ⊆ A and MUST NOT ∩ A = ∅).
2. **External grounding and a human baseline.** Measure human performance on the same items; anchor gold where possible in human-written data (Super-NaturalInstructions positive and negative examples).
3. **Scorer audit on real model outputs.** Report agreement between automatic checks and human labels on a sample of model answers; audit any LLM judge the same way.
4. **Closed-form metric definitions** in an appendix.
5. **Construct validity** of our metrics (harmful vs missed transfer, role sensitivity, consistency).
6. **Model breadth:** 9–10 models from at least 6 developers, with reasoning and non-reasoning modes.
7. **One surprising finding**, for example whether reasoning helps or hurts role inference, or whether counter-examples increase copying.
8. **Figures:** a teaser Figure 1 (one example, three roles, real answers), a model × seed × role heatmap, per-item insets, a colour-coded master table.
9. **Statistics:** add permutation tests and leave-one-model-out to the planned bootstrap intervals.
10. **Reproducibility package:** verbatim prompt appendix, model identifier table, project page, appendix map.
11. **Optional Bangla subset** after the main benchmark is solid.
12. **Focus:** benchmark and rigorous behaviour analysis as the core, mechanism second, training third, so the paper stands even if training does not beat the baselines.

Where we can go further than they did: a causal mechanism study and a training method.
