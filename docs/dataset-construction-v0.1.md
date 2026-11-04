# Dataset construction and contamination controls

Date: 5 November 2026. Status: DRAFT FOR REVIEW, not a frozen main-paper protocol.

## What is being constructed

The experimental object is a target task, an example, the example's intended role, an allowed-transfer scope, and a verifiable answer contract. Public data supplies candidate material, not ready-made gold labels for this new task.

Use **controlled perturbation** for intentional changes to examples. Reserve **data contamination** for unwanted training/evaluation exposure. A deliberately misleading example is a test condition with a valid answer contract, not a mislabeled example.

## Source roles and limits

| Source | Extract | Do not assume | Initial use |
| --- | --- | --- | --- |
| WildChat-1M | User requests containing an actual supplied example, with enough preceding context to identify what it is for | Every `for example` hit is relevant; normal style imitation is cross-domain analogy; a public answer is the gold answer | Natural phrasing and ecological-validation subset |
| Super-NaturalInstructions | Task definitions and positive/negative examples with explanations | A negative task example is already a natural user counter-example; repository licence automatically covers every upstream item | Candidate task specifications and scope annotations, subject to source licence checks |
| AnaloBench / ParallelPARC | Relational mappings and plausible distractors | Analogical similarity provides a ready target solution; generated silver data is human data | Candidate source-target relations, after licence and utility screening |
| ARN / other unavailable sources | Nothing until data and reuse permission are verified | A paper licence licenses an absent dataset | Optional, never a sprint dependency |
| Newly authored scenarios | New source-target combinations with explicit valid-answer contracts | Newly written text or paraphrasing proves no model exposure to its underlying idea | Main controlled construction pool |

Access verified this review: WildChat card, NaturalInstructions repository and ParallelPARC paper. No new full source dataset was downloaded for this review. Per-source usable counts and item-level licence decisions remain pending.

## Operational inclusion test for real conversations

A candidate must contain (1) a target request, (2) a concrete example, (3) a recoverable connection between them, and (4) enough context to annotate role and scope. Exclude a document supplied only for translation/summarization, pasted prose that happens to say `for example`, and a requested example that the user has not actually supplied. Keep format/style imitation as its own subtype. Mark ambiguous scope explicitly; never invent a hidden prohibition.

Sample keyword hits AND a smaller random set of misses. Preserve conversation/turn IDs, dataset revision, page offsets, sampling seed, inclusion probabilities where available, fetch failures and dedup counts. Avoid truncating all turns to the same prefix for deduplication. Use full normalized text hashes, conversation ancestry, then near-duplicate review. Retain relevant surrounding context and redact identifiers in any export.

Report precision of the retrieval filter and its length/keyword selection restrictions. Inspect misses to learn what the filter omits. Without a representative sampling/weighting design, do not extrapolate a candidate-sample fraction into a corpus count, call it an unbiased prevalence estimate, or label it a lower bound when false positives remain.

## Merge procedure

1. Register each candidate's source, source ID/revision, licence status and annotation provenance.
2. Extract task, constraints, example and relational structure into a common seed card.
3. Decide if a target solution actually needs the source relation. Record a no-example control; reject trivial source-irrelevant seeds from the primary analogical-transfer subset.
4. Write three role variants: borrow a relation; follow a specified part; avoid a specified failure/pattern. Some seeds need fewer roles if a valid conversion is unnatural.
5. Annotate permitted and forbidden content per role. `partial` is a scope, not a fourth role. Mark fit as full, partial or misleading only when the intended relation makes this meaningful. Do not force the full Cartesian product.
6. Generate a controlled incidental-detail pair and, where valid, a structural-relation pair. Change one intended factor per pair. Recompute gold labels after any change.
7. Two independent humans inspect the task/scope contract and representative outputs before model evaluation. AI labels remain AI labels. Record exact agreement and adjudication; uncertain cards stay outside confirmatory evaluation.
8. Independently challenge verifiers with valid alternatives and wrong answers; a reference answer merely passing its own checker is insufficient.
9. Build connected provenance groups: same seed, conversation, original item, paraphrase, source story or shared template must not cross splits. A held-out-relation test additionally excludes relation families from training.
10. Write a versioned manifest, file hashes and split assignment. Keep a separate untouched evaluation holdout; log every evaluation and any API disclosure.

Do not balance roles by attaching arbitrary role labels to irrelevant conversations. Report each source's actual contributions and role/domain distribution. Natural conversation and constructed variants are distinct provenance categories even when stored in one schema.

## Required seed-card fields

`seed_id`, `provenance_group_id`, `source_records`, `author_or_generator`, `creation_date`, `domain`, `relation_family`, `target_task`, `active_constraints`, `source_example`, `example_components`, `role`, `permitted_transfer`, `forbidden_import`, `target_fit`, `role_wording`, `perturbation_type`, `changed_components`, `valid_answer_contract`, `verifier_version`, `human_review`, `split`, `data_version`.

No gold-only scope annotations are supplied at test time except in a separately named oracle control. Annotation evidence states where each required/prohibited property comes from in the actual user prompt.

## Worked example: one seed, three roles

This is a newly authored CONTROLLED CONSTRUCTION EXAMPLE, not mined from WildChat and not yet human-validated.

**Target:** Design exactly three university IT response tiers, ordered most to least urgent. Respond as JSON with `tiers[{name,response_hours}]` and `assignments{exam_system,wifi,printing}`. Times must be nonnegative integers, strictly increasing and at most 72 hours. Example names and times are local to its source organisation. The university has two existing staff; no extra staffing is available.

**Source:** A fictional equipment depot handles complete shutdowns first, degraded service next, cosmetic faults last. Its tiers are `Cobalt` (5 minutes), `Amber` (30 minutes), `Pearl` (120 minutes), staffed by six depot inspectors. The example demonstrates ordering by disruption severity.

| Variant | User instruction | Gold scope |
| --- | --- | --- |
| Analogy | Apply the severity-ordering principle to the university; choose university-specific tier names and hours. Source names, minute deadlines and inspector staffing are not requirements. | Exam-system failure before Wi-Fi degradation before cosmetic printing fault; preserve target time/staff limits; do not transfer source names, minute units or extra inspectors as target properties |
| Requirement | Use exactly `Cobalt`, `Amber`, `Pearl` as tier names in that order; adapt deadlines to the university's hour/staff limits. | Name copying is correct; copying source minute deadlines or staffing is not. No earlier hard constraint is silently overridden |
| Counter-example | Avoid the depot's named colour labels, which confused our students; keep severity-based ordering and our hour/staff limits. | Avoid the specified label choice, retain the explicitly useful ordering; do not infer that every property in a negative example is forbidden |

**Incidental-detail perturbation:** Replace depot staffing six -> nine. The university allocation must remain unchanged in all three variants. Source-label replacement is NOT incidental for the requirement variant: its gold target names must change. Replace the source relational rule only in a separately defined pair, updating target expectations accordingly.

**Misleading-fit example:** A depot orders by cosmetic appearance, but the university's explicit priority is service disruption. Either reject that ordering and follow the explicit university rule or request clarification when the instruction is genuinely contradictory. Do not score an impossible instruction as model incompetence. Keep ambiguous conflicts outside the primary subset.

Use additional minimally explicit paraphrases only after humans agree what they permit/prohibit. Inference from `inspiration` alone must not create a hidden ban on a harmless word.

## Three exposure questions

| Question | Control | What can be concluded |
| --- | --- | --- |
| Did our fine-tuning/dev pipeline see the test family? | Provenance-group split, exact/near-duplicate audit, no test-driven selection, immutable manifests | Our controlled exposure policy and observed overlap audit |
| Could the pretrained model have seen a public source? | Source/model exposure matrix; fresh source-target constructions; counterfactual pairs; optional calibrated completion/MIA diagnostics | Exposure risk and sensitivity results, not blanket absence of contamination |
| Will evaluation/release expose hidden items? | Local open-weight execution where possible; provider data-handling review if APIs are used; access log; release version/canary outside model prompts | Managed disclosure history, not guaranteed protection from future training |

Rewriting names/numbers does not erase structural familiarity. A model preferring a paraphrase it generated itself is not evidence that the original was unseen. Min-K% Prob and guided completion are diagnostic tools with assumptions; failure to detect membership is not a clean certificate. Do not use the old arbitrary 5% or 70% rules as published universal thresholds.

## Primary references

- WildChat dataset/card and licence: https://huggingface.co/datasets/allenai/WildChat-1M
- Super-NaturalInstructions task examples: https://github.com/allenai/natural-instructions
- ParallelPARC gold and silver analogy construction: https://aclanthology.org/2024.naacl-long.329/
- Guided completion: https://arxiv.org/abs/2308.08493
- Min-K% Prob: https://arxiv.org/abs/2310.16789
- MIA distribution-confound evaluation: https://arxiv.org/abs/2402.07841
- Contamination-detection assumptions: https://aclanthology.org/2025.findings-naacl.291/
- A newer dataset-level non-membership method, not implemented in this sprint: https://aclanthology.org/2026.eacl-long.251/
