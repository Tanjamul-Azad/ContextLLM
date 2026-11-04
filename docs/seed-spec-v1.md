# Seed card format v1

Date: 5 November 2026. Author: Tanjamul Azad. Status: DRAFT, follows `paper-protocol.md` section 3 (not yet frozen).

A seed card is one JSON file: one target task, one source example, a gold specification and its variants. Cards live in `data/seeds_v1_draft/` until two annotators have reviewed them. The linter is `src/seed_lint_v1.py`; new check kinds are in `src/checks_v1.py`; tests are in `tests/test_seed_lint_v1.py`.

```
python -I src/seed_lint_v1.py                 # draft mode: human items are PENDING
python -I src/seed_lint_v1.py --release       # benchmark mode: PENDING becomes ERROR
python -I tests/test_seed_lint_v1.py
```

## 1. Fields

| Field | Content |
| --- | --- |
| `id`, `schema` | Unique seed ID; `schema` is `seed-card-v1`. |
| `status` | `draft — needs two human annotators before use` until review is complete. |
| `author`, `created` | Who wrote the card, and the date. |
| `family` | `decision` (JSON answer) or `code` (Python function and unit tests). |
| `domain` | Free text, for example "transport policy". |
| `provenance` | `source_type` (one of the protocol's source rows), `case` (the real case), `references` (citations; at least one with a URL or DOI), `provenance_group_id` (all seeds from one case share it and stay in one split), `fresh_after_cutoff`, `urls_checked_by_human`. |
| `target` | `task`, `rules` and `format`. Each rule has an `id`, its `text` as shown to the model, and at least one automatic `check`. Code cards also have `func` and `tests`. |
| `source_example` | `text` (the example as shown), `length` (`standard` ≥ 8 sentences or `long` ≥ 20), `incidental_details` and `shared_surface_features`. |
| `incidental_details` | Each has `id`, `text`, `leak_terms` and/or `leak_regex`, and optionally a `control`: `from`, `to` and the control's own leak terms. The control is the incidental-detail axis: same role and relation, different detail. |
| `shared_surface_features` | For counter-examples: each feature quotes the source (`source_quote`) and the target (`target_quote`). |
| `relation` | One sentence: the idea that could transfer. |
| `marker` | The source's distinctive pattern, as a check. A requirement should copy it and a counter-example should avoid it. Used for the copy-rate gap (H2). |
| `turns` | Always `["single", "multi"]`. The multi-turn prompt carries the same information (built by `build_messages`). |
| `variants` | One per (role, cue, fit) cell. See section 2. |
| `cells_not_applicable` | `role`, `fit`, optional `cue`, and a `reason`, for every cell that is not built. |
| `reference_solutions` | One correct answer per variant (JSON text or a Python code block). |
| `copy_answers` | One example-copying answer per variant. It must fail a transfer or leakage check. |
| `alternative_solutions` | Optional other valid answers. They must pass, which guards against checks that are too strict. |
| `human_review` | `annotators`, `realism` and `scope_agreement` (slots `annotator_1`, `annotator_2`, both null in drafts), and `adjudications` (one entry per ambiguous implied check: `variant`, `check`, `decision`). |
| `contamination`, `split` | Filled by later pipeline steps. Drafts have `not run` and null. |
| `notes` | Known doubts, for the annotators. |

## 2. Variants and checks

A variant has `id`, `role` (`analogy`, `requirement`, `counter`), `cue` (`stated`, `implied`), `fit` (`full`, `partial`, `wrong`), `text` (the user's words, with `{EX}` where the source example goes), `must_transfer`, `must_not_transfer`, and, for partial or wrong fit, `rules_add` (extra target rules) and `fit_note`.

A check is `{"id", "what", "spec", "basis"}`. `spec` is `[kind, args...]`. `what` is the scope item in plain words. `basis` says why the check is allowed:

| Basis type | Meaning | Linter test |
| --- | --- | --- |
| `stated` | The prompt says it. `quote` is an exact substring of the full prompt. | Quote must be found. |
| `target_rule` | It is a target rule (`rule` gives the ID). | Rule must exist for this variant. |
| `role_implied` | The role implies it. `implication` is one of: `relation_transfer` (analogy), `named_part_transfer` (requirement), `avoid_flagged_feature` (counter), `source_specific_fact` (any role). Optional `quote`. On implied-cue variants, `ambiguity` is `clear` or `ambiguous`. | Implication must suit the role; an ambiguous check needs an adjudication record before scoring. |

Check kinds reused from `src/checks.py`: `text_absent`, `text_present`, `regex_absent`, `regex_present`, `py_test`, `json_len_between`, `json_all_int`, `json_all_le`, `json_increasing`, `json_eq`, `json_any_word`, `json_no_word`, `json_all_words_le`, and the rest of the pilot kinds. New kinds in `src/checks_v1.py`: `leak_absent` (by incidental-detail ID, so the control version swaps terms automatically), `json_all_ge`, `json_all_lt`, `json_eq_num`, `json_in`, `json_distinct_nonzero_lt/eq`, `json_levels_ratio`, `json_ranges_cover`, `json_range_value_cmp`, `json_map_in`, `json_monotone_map`, `json_map_rank_cmp`, `json_count_value_le`. `score_v1` reports format failure on its own; it is never counted as leakage.

## 3. Protocol rules and how each is enforced

| Protocol section 3 rule | Field | Machine check (`seed_lint_v1.py`) | Needs a person |
| --- | --- | --- | --- |
| Real, citable case, source recorded | `provenance` | source type in the allowed list; case named; citations present, at least one URL/DOI; group ID present | Open the URLs and confirm the facts in the source text (`urls_checked_by_human`) |
| Source ≥ 8 sentences; long variant ≥ 20 for 30% of seeds | `source_example.text`, `length` | sentence count on prose (code blocks excluded); set-level share of `long` ≥ 30% | No |
| ≥ 3 incidental details that must not transfer | `incidental_details` | at least 3; each has leak terms or regex; each is checked by at least one variant; leak terms must occur in the source and not in the target or the user's own words | Whether each detail is really incidental |
| Counter-example shares ≥ 3 surface features | `shared_surface_features` | at least 3; each quote found in source and in target | Whether the counter-example really looks applicable |
| Gold lists must / must not / target rules, each with an automatic check | `target.rules`, `must_transfer`, `must_not_transfer` | every rule has a check; every variant has both lists non-empty; every check has a known kind and a `what` | Whether the lists are complete |
| Gold is valid | `reference_solutions`, `copy_answers`, `alternative_solutions` | every reference passes (and passes the control); every copy answer fails a transfer or leakage check; every alternative passes; requirement reference has the marker, counter reference does not | Write more valid alternatives and wrong answers (dataset-construction step 8) |
| Realism 4 or 5 from both annotators | `human_review.realism` | PENDING while null; in `--release`, both must be ≥ 4 | Yes |
| Both annotators agree on transfer scope (kappa ≥ 0.6 overall) | `human_review.scope_agreement` | PENDING while null; in `--release`, both must be true | Yes; kappa is computed across seeds, not per card |
| Implied-cue variants are half of all variants | `variants[].cue` | implied share ≥ 0.5 per seed; implied text must not contain role-stating phrases; stated text should contain one | Whether an implied cue really lets a reader infer the role |
| No check stricter than the prompt or role (pilot P5) | `basis` | stated quote found; numeric bounds in bound-type checks must appear in the basis text (digits or number words); banned or required words must appear in the prompt; regex bans must match something in the prompt; leak terms must be source-only | Strictness of `py_test` thresholds and of word lists (the linter only proves the words come from the prompt) |
| Ambiguous implied details adjudicated before scoring (pilot P1) | `basis.ambiguity`, `adjudications` | implied-cue checks must carry `ambiguity`; ambiguous ones are PENDING until an adjudication exists | Yes |
| Every seed covers all meaningful cells | `variants`, `cells_not_applicable` | every role × fit × cue cell is present or marked not applicable with a reason; turns are single and multi; at least one incidental-detail control | Whether a "not applicable" reason is honest |
| No source supplies > 40% of seeds; ≥ 40 seeds per family | `provenance.source_type`, `family` | set-level; WARN in draft, ERROR in `--release` | No |
| Fresh seeds ≥ 1/3 of test; contamination checks; splits | `fresh_after_cutoff`, `contamination`, `split` | not checked here | Later pipeline steps |

## 4. Limits of the linter

- It proves that a check's numbers and words come from the prompt. It cannot prove a word list is complete, or that a threshold inside a unit test matches a vague instruction such as "don't let it drift".
- The role-cue phrase lists are heuristics. They catch an implied cue that says "don't do it like this"; they do not prove the role can be inferred.
- Passing references and failing copy answers show the checks separate two answers. They do not show the checks accept every valid answer.
