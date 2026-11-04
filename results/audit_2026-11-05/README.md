# Existing pilot audit - 5 November 2026

Saved files were checked. No model was run; no generated code was executed.

| Model | Saved outputs | Seeds | Plain failures | Explicit failures | Old E4 rule met? |
| --- | ---: | ---: | ---: | ---: | --- |
| llama3.1-8b-4bit | 130 | 10 | 14/30 | 8/30 | False |
| qwen2.5-3b | 130 | 10 | 14/30 | 10/30 | False |
| qwen2.5-7b-4bit | 130 | 10 | 12/30 | 9/30 | False |

Rates reproduce the old scorer, whose gold/check validity needs revision. They are exploratory, not confirmed role-transfer failure rates.

Confirmed mismatch: P5's prompt allows ten words, but the analogy transfer checker permits only eight.

Handcheck files contain WildChat 10/45 positive labels (9 requirement, 1 analogy) and OASST2 12/40 (8 requirement, 2 analogy, 2 counter-example). Annotator identity and independent human verification remain unconfirmed. These files do not establish population prevalence.

## Issues requiring revision

- Plain P1 asks for inspiration but its gold bans colour names; that prohibition is only explicit in the explicit variant. Human adjudication is required.
- checks.score marks invalid format as leakage. Report format failure separately from source-detail import.
- E5 requirement-minus-counter marker gap is a role-response sanity check, not proof of useful analogical transfer or of a role-specific failure.
- Logit lens uses a supplied answer prefix and hand-picked token sets on five seeds from one model. It does not locate a causal failure layer or identify harmful neurons.
- GSM8K membership diagnostics do not certify newly constructed seed cards; rewriting and negative detection results do not establish non-membership.

Decision: **REVISE AND CONTINUE FEASIBILITY ONLY. No main-paper go/freeze conclusion follows yet.**

Original files are preserved. File hashes and item-ID checks are in summary.json. Revised gates must be evaluated on new held-out seeds, never represented as pre-registered for these old results.
