# Seed card format v2

Date: 13 November 2026. Status: DRAFT design for WP0.2 (MASTER-PLAN Section 4.1). It replaces `docs/seed-spec-v1.md` for new cards; v1 cards stay valid under the v1 linter until they are migrated. Nothing in this file changes the v1 schema, linter or checks.

Reference cards: `data/seeds_v2_draft/D01_stockholm_parking.json` and `data/seeds_v2_draft/C01_calver_compare.json` (hand-migrated from v1). To be implemented: `src/seed_lint_v2.py`, `src/checks_v2.py`, `src/export_v2.py`, `tests/test_seed_lint_v2.py` (Section 13).

```
python -I src/seed_lint_v2.py                    # draft mode: human items are PENDING
python -I src/seed_lint_v2.py --release          # release mode: PENDING becomes ERROR
python -I src/seed_lint_v2.py --no-gold          # skip running the answers
python -I tests/test_seed_lint_v2.py
```

## 1. Concepts

| Term | Meaning |
| --- | --- |
| Source example | `source_example.text`, shown to the model in place of `{EX}`. |
| Span | A contiguous piece of the example text. The spans of a card tile the example exactly, in order. Each span has a `kind`: `relation`, `detail` or `context`. |
| Unit | A licensed item. A relation unit (`U01`, `U02`, ...) is one idea and may own several spans anywhere in the example. A detail unit (`I1`, `I2`, ...) is one copyable surface item with one detector (leak terms or leak regex) and owns every span where the detector fires. Context spans belong to no unit. |
| Licence | Per variant, one label per unit: `MUST` (the answer must use it), `MAY` (free either way), `MUST_NOT` (the answer must not use it), or `UNCLEAR` (the author cannot decide; see 5.6). A span inherits the label of its unit. |
| Gold atom | One licence entry: (variant, unit, label, basis, evidence). MASTER-PLAN Section 4.1 uses both "licence" and "gold atoms"; in v2 they are the same object. There is no separate `gold_atoms` field. |
| use(a) | The set of units an answer `a` uses, decided by the checks that name each unit (Section 6.2). |
| Role | `analogy`, `requirement` or `counter`. The role is what the user intends the example for. The licence is what the answer may take from it. They are different: an analogy can permit a source name, a requirement can forbid every detail except the named part, a counter-example can forbid one pattern while every other detail stays MAY. The role does not fix the licence; the prompt does. |

## 2. Card fields

Types: `str`, `int`, `bool`, `list`, `obj`, `null`. "Req" is required (R), optional (O) or required for code cards (C).

### 2.1 Top level

| Field | Type | Req | Meaning |
| --- | --- | --- | --- |
| `schema` | str | R | Always `seed-card-v2`. |
| `id` | str | R | Unique card id, `^[CDX]\d{2,3}_[a-z0-9_]+$` (C = code, D = decision, X = documentation example or test fixture, never in a pool). Equals the file name without `.json`. |
| `status` | str | R | `draft`, `in_review`, `reviewed`, `accepted` or `rejected`. `draft` means every licence is the author's proposal and no blind review has started. |
| `status_note` | str | R | One sentence for people, for example "Licences are the author's draft, pending two blind reviewers." |
| `created`, `updated` | str | R | ISO dates. |
| `author_id` | str | R | Stable lowercase id of the human author, `^[a-z][a-z0-9_]{1,31}$`. Replaces v1 `author`. |
| `model_assistance` | str | R | `none`: no model output appears in the card. `edited`: a human wrote the card and a model edited parts or added parts that a human then checked line by line. `drafted`: a model wrote the first draft of the card or of any gold field (spans, licences, answers) and no human has yet rewritten it. |
| `model_assistance_log` | obj | R unless `none` | `model` (exact model id), `date`, `scope` (which fields the model wrote), `prompt_ref` (where the drafting prompt is stored), `human_edits` (what a human changed, or null); migrated cards add `v1_origin` (what is known about how the v1 text was written). Plan 4.3 requires this log. |
| `family` | str | R | `decision` (JSON answer) or `code` (Python function with unit tests). |
| `domain` | str | R | Snake-case domain id from the domain registry (Section 14, item 12), for example `transport`. Used for held-out-domain splits. |
| `domain_note` | str | O | Free-text domain description (the v1 `domain` value). |
| `relation_family` | str | R | Snake-case id of the abstract relation, for example `demand_responsive_pricing`. Used for held-out-relation splits; paraphrases of one relation share a family. |
| `template_group_id` | str | R | Cards drafted from one template or one drafting prompt share an id. A hand-written card uses `TG-` plus its id prefix, for example `TG-D01`. |
| `provenance_group_id` | str | R | Cards from one case, conversation or source item share an id and stay in one split. Moved from v1 `provenance.provenance_group_id`. |
| `provenance` | obj | R | Section 2.2. |
| `target` | obj | R | v1 `target`: `task`, `rules`, `format`. A rule check may carry `units` (Section 6.1). |
| `func`, `tests` | str, obj | C | v1 fields for code cards. |
| `source_example` | obj | R | Section 2.3. |
| `relation_units` | list | R | `[{id, what, main}]`. `id` matches `^U\d{2}$`; `what` is one plain sentence; `main` is true for units that state the card's central relation (at least one). |
| `source_spans` | list | R | `[{id, text, kind, unit}]`, Section 3. |
| `relation` | str | R | v1 one-sentence statement of the idea that could transfer. |
| `marker` | obj | O | v1 marker (`what`, `spec`) plus `units`: the units whose copying the marker measures. Descriptive only (H2 copy-rate gap), never scored. |
| `turns` | list | R | Always `["single", "multi"]`. |
| `variants` | list | R | Section 2.4. |
| `cells_not_applicable` | list | R | v1 field, unchanged. |
| `human_review` | obj | R | Section 2.7. |
| `contamination`, `split` | obj, str/null | R | v1 fields, filled by later steps. |
| `notes` | str | O | Known doubts, for reviewers. |
| `migration` | obj | O | For migrated cards: `from_schema`, `from_file`, `date`, `changes` (list of plain sentences). |

### 2.2 `provenance`

| Field | Type | Req | Meaning |
| --- | --- | --- | --- |
| `source_type` | str | R | One of the v1 list (`real_request_paraphrased`, `documented_case`, `software_practice`, `supernatural_instructions`, `analogy_dataset`, `lost_in_conversation`, `fresh_after_cutoff`) or the new `original_scenario`. |
| `case` | str | R | The real case or scenario in a few words. |
| `references` | list | R unless `original_scenario` | `[{citation, url or doi}]`, at least one with a URL or DOI. |
| `original_authoring` | str | R if `original_scenario` | The author's signed line: "Original scenario written by <author_id> on <date>; no source text was copied." |
| `fresh_after_cutoff` | bool | R | v1 meaning. |
| `urls_checked_by_human` | bool | R | v1 meaning. |

### 2.3 `source_example`

| Field | Type | Req | Meaning |
| --- | --- | --- | --- |
| `text` | str | R | The example exactly as shown to the model. |
| `length` | str | R | `standard` or `long` (v1). |
| `incidental_details` | list | R | The registry of detail units. The v1 name is kept so that `checks_v1.leak_absent` and `score_v1` keep working; in v2 a "detail" is incidental only relative to a role (a requirement may make a detail MUST). Each entry: `id` (`^I\d+$`), `text` (short description), `leak_terms` and/or `leak_regex` (the detector), optional `control` (`from`, `to`, and the control's own `leak_terms`/`leak_regex`). |
| `shared_surface_features` | list | R if any counter variant | v1 field, unchanged. |

### 2.4 Variant

| Field | Type | Req | Meaning |
| --- | --- | --- | --- |
| `id` | str | R | `<role>-<cue>-<fit>`, plus a suffix if one cell has two variants. |
| `role`, `cue`, `fit` | str | R | v1 values. |
| `text` | str | R | The user's words with `{EX}` exactly once. |
| `rules_add`, `fit_note` | list, str | O | v1 fields for partial and wrong fit. |
| `licence` | obj | R | Section 2.5. |
| `must_transfer` | list | R | Checks that test MUST units. May be empty when no unit is MUST (common for counter-examples). |
| `must_not_transfer` | list | R | Checks that test MUST_NOT units. |
| `probes` | list | R | Descriptive checks on MAY units. Never scored (Section 6.4). May be empty. |
| `valid_answers` | list | R | Section 2.6. At least two. |
| `invalid_answers` | list | R | Section 2.6. At least two of kind `minimal`. |

A check is v1 `{id, what, spec, basis}` plus `units`: a non-empty list of unit ids it tests. `basis` is optional in v2 and is kept on migrated checks for traceability; the licence entry of each named unit is the authoritative basis. A probe is `{id, what, spec, units, use_when}`, where `use_when` is `fail` (the unit counts as used when the probe fails, as for `leak_absent`) or `pass`; a probe migrated from a v1 check keeps the old id in `v1_id`.

### 2.5 `licence`

```json
"licence": {
  "defaults": {
    "relation": {"label": "MAY", "basis": "DEFAULT"},
    "detail": {"label": "MUST_NOT", "basis": "DIRECT", "evidence": "not its details"}
  },
  "units": {
    "U01": {"label": "MUST", "basis": "DIRECT", "evidence": "Borrow the idea"},
    "U02": {"label": "MAY", "basis": "DEFAULT", "note": "One concrete form of the idea; not a stated detail."}
  }
}
```

- `defaults` is optional and may hold `relation` and/or `detail`. `units` maps unit ids to entries.
- Expansion: the entry for unit `u` is `units[u]` if present, else `defaults[kind of u]`. After expansion every relation and detail unit must have exactly one entry. Context spans have no entry; they are not licensed.
- Entry fields:

| Field | Type | Req | Meaning |
| --- | --- | --- | --- |
| `label` | str | R | `MUST`, `MAY`, `MUST_NOT`, `UNCLEAR`. |
| `basis` | str | R | `DIRECT`, `INFERRED` or `DEFAULT` (Section 5.2). For `UNCLEAR`, the basis of the proposed reading. |
| `evidence` | str | R unless `DEFAULT` | An exact, case-sensitive substring of the built prompt (Section 5.3). |
| `implication` | str | R if `INFERRED` | One value from the closed list in Section 5.4. |
| `proposed` | str | R if `UNCLEAR` | `MUST`, `MAY` or `MUST_NOT`: the author's lean. |
| `note` | str | R if `UNCLEAR`; expected on every deviation from the role default (Section 5.5) and on every MAY under a blanket ban | One or two sentences for reviewers. The linter checks only the UNCLEAR case. |

### 2.6 Answers

Valid answer: `{id, text, origin, uses_may, note}`.

| Field | Type | Req | Meaning |
| --- | --- | --- | --- |
| `id` | str | R | `V1`, `V2`, ... unique in the variant. |
| `text` | str | R | The full answer as a model would write it (JSON text, or a Python code block). |
| `origin` | str | R | `v1_reference`, `v1_alternative`, `author`, `model_drafted`. |
| `uses_may` | list | O | Units this answer deliberately uses although they are MAY. For detail units the linter confirms the detector fires (A4). This is the guard against hidden bans. |
| `note` | str | O | Why it is valid. |

Invalid answer: `{id, text, kind, pair_of, violates, fails, origin, note}`.

| Field | Type | Req | Meaning |
| --- | --- | --- | --- |
| `id` | str | R | `X1`, `X2`, ... for `minimal`; `C1`, ... for `copy`. |
| `text` | str | R | A parseable answer (real runnable code for code cards). Format failure is not a licence violation and is never used here. |
| `kind` | str | R | `minimal`: one edit away from a valid answer and violating exactly one item. `copy`: an example-copying answer (v1 `copy_answers`); it may violate several items and does not count toward the minimum of two. |
| `pair_of` | str | R if `minimal` | The valid answer it was derived from. |
| `violates` | str | R if `minimal` | Exactly one item: a unit id whose label in this variant is MUST or MUST_NOT, or a target rule id (`R1`, ...) of this variant. Never a MAY or UNCLEAR unit. |
| `fails` | list | R | The exact set of check ids that must fail. For `minimal`, every listed check must test `violates` (it names that unit, or belongs to that rule). Usually one check; more only when several checks test the same item (D01 wrong fit: `T1` and `R4a` both test U01). |
| `origin` | str | R | As for valid answers, plus `v1_copy`. |

### 2.7 `human_review`

```json
"human_review": {
  "reviewers": [],
  "variants": {"analogy-stated-full": {"annotator_1": null, "annotator_2": null}},
  "adjudications": []
}
```

- `variants` has one key per variant. A filled annotator slot is `{reviewer_id, date, role, realism, licence}` where `role` is the reviewer's blind role label, `realism` is 1 to 5 for the full prompt, and `licence` maps every unit id to the reviewer's label (`MUST`, `MAY`, `MUST_NOT`, `UNCLEAR`). Reviewers see the expanded licence units, never the author's labels.
- `adjudications`: `[{variant, field, unit, value, decided_by, date, note}]` with `field` `role` or `licence` (`unit` only for `licence`).
- Final label of a unit: the adjudicated value if one exists, else the reviewers' label if both agree, else unresolved.
- v1 `annotators`, per-card `realism` and `scope_agreement` are replaced by this block.

## 3. Span segmentation

### 3.1 Storage and offsets

- `source_spans` is a list of `{id, text, kind, unit}`. `id` matches `^S\d{2,3}$` and is unique. `unit` is required for `relation` and `detail` spans and absent for `context` spans.
- The rule: `"".join(s["text"] for s in source_spans) == source_example["text"]`, exactly, including whitespace, newlines and code fences. Offsets are derived, never stored: span `j` starts at the sum of `len(text)` of spans before it (Python string length, Unicode code points) and ends at its start plus its own length.
- In the prompt, the example appears exactly once in the message that carries `{EX}` (message 0 single-turn, message 2 multi-turn); prompt offset = position of the example in that message + span offset.
- Span ids carry no meaning. Licences and checks reference units, never span ids, so spans can be split or merged without touching variants.

### 3.2 Kinds

| Kind | What goes in it | Unit |
| --- | --- | --- |
| `relation` | Text that states an idea that could transfer: a rule, a mechanism, an ordering, a structure, including the numbers that parameterise it (see 3.3, rule 3) and the code lines that implement it. | A relation unit `U..` |
| `detail` | The smallest copyable surface item: a name, a place, a number that is a fact about the source world together with its unit, a currency, a label, a code identifier, an error message, a distinctive phrase. | A detail unit `I..` whose detector fires inside the span |
| `context` | Framing, connectives, generic code syntax, blank lines, and any fragment with no letter or digit. | none |

### 3.3 Rules

1. **One idea per relation unit.** A unit may own several sentences and code lines (in C01, U01 owns a prose sentence, a regex fragment and three code lines). Two sentences stating the same idea share a unit.
2. **Smallest copyable detail.** A detail span is the smallest unit that could be copied on its own. Split further whenever two parts could get different labels in any variant of the card (licence-boundary rule). Example: in D01 "20 Swedish kronor (SEK)" the requirement variants need the price level and forbid the currency, so `20` and `Swedish kronor (SEK)` are separate spans.
3. **Numbers.** A number that parameterises a relation stated in the same clause (a price level of the ladder, a threshold, an example version such as 1.10.0 that illustrates the comparison rule) stays inside the relation span. A number that is a fact about the source world (a date, a count of control points, a measured effect) is a detail span with its unit word (`18 control points`, `20 percent`, `31 July 2006`).
4. **Not a detail.** Generic words and identifiers that an independent answer would plausibly contain (`ValueError`, `_key`, `int`, "peak") and names that also occur in the user's own words or the target (`Stockholm` in D01) are not details. They stay in the surrounding relation or context span. Reason: their presence in an answer is not evidence of transfer.
5. **Mixed sentences.** Carve the detail spans out. The remaining fragments keep the sentence's relation unit (the same `unit` value on every fragment). Fragments with no letter or digit become context.
6. **Detectors decide detail spans.** Every detail span contains at least one match of its unit's detector, and every detector match in the example lies inside a span of that unit. Matches of two detectors never overlap. In practice: choose leak terms first, then cut spans around their matches.
7. **Whitespace.** Whitespace after a sentence or a code line belongs to the span that ends there. A span boundary never falls between two letters or digits.
8. **Code.** Segment by line. Split a line only when it mixes units (C01 regex line below). Indentation stays with its line.

### 3.4 Worked examples

D01, sentence with three prices (rules 2, 3, 5):

```
S18 relation U02  "A passage in the busiest half hours cost 20 "
S19 detail   I1   "Swedish kronor (SEK)"
S20 relation U02  ", the shoulder periods around them cost 15 "
S21 detail   I1   "SEK"
S22 relation U02  ", and the remaining daytime periods cost 10 "
S23 detail   I1   "SEK"
S24 context       ". "
```

The levels 20, 15 and 10 parameterise the ladder (U02), so they stay in its spans; the currency is detail I1 in every occurrence because one detector (`SEK`, `kronor`) covers all of them.

D01, a background sentence with dates (rule 3):

```
S01 relation U08  "Stockholm ran congestion charges as a full-scale trial from "
S02 detail   I6   "3 January"
S03 relation U08  " to "
S04 detail   I6   "31 July 2006"
S05 context       ". "
```

C01, one regex line that mixes four units (rule 8):

```
S19 detail   I3   "SEMVER"
S20 context       " = re.compile(r\""
S21 detail   I2   "^v?"
S22 relation U01  "(\d+)\.(\d+)\.(\d+)"
S23 relation U02  "(?:-([0-9A-Za-z.-]+))?"
S24 relation U05  "(?:\+[0-9A-Za-z.-]+)?"
```

C01, the detector of I3 (`semver`) also fires inside `compare_semver`, so that identifier is an I3 detail span wherever it occurs (rule 6).

### 3.5 The incidental-detail control

- A `control` swaps one detail for another of the same type (v1 axis: same role and relation, different detail). Every occurrence of `control.from` in the example must lie inside spans of the control's detail unit.
- Control spans: apply `text.replace(from, to)` inside each span of that unit only. Ids, kinds, units and labels are unchanged, and the control spans tile the control example (`seed_lint_v1.source_text(card, perturbed=True)`).
- Under the control, the unit's detector is the control's `leak_terms`/`leak_regex`; all other detectors are unchanged.
- The control is built only for variants where the controlled unit is not MUST. If the unit is MUST, changing it changes the gold, so it is not incidental (dataset-construction-v0.1, worked example). The exporter skips the control for such variants.

## 4. Changes from v1

| Change | v1 | v2 |
| --- | --- | --- |
| Added | | `source_spans`, `relation_units`, `variants[].licence`, `units` on every check, `variants[].probes`, `variants[].valid_answers`, `variants[].invalid_answers`, `marker.units`, `relation_family`, `domain` (as an id), `domain_note`, `template_group_id`, `author_id`, `model_assistance`, `model_assistance_log`, `status_note`, `updated`, `migration`, `provenance.original_authoring`, source type `original_scenario`, check kinds `judge_absent` and `judge_present` (reserved, Section 6.5) |
| Renamed or moved | `author` | `author_id` |
| | `provenance.provenance_group_id` | top-level `provenance_group_id` |
| | `domain` (free text) | `domain_note`; `domain` becomes a registry id |
| | `status` (one fixed sentence) | `status` enum plus `status_note` |
| Removed | `reference_solutions`, `alternative_solutions`, `copy_answers` | moved into the variants (mapping below) |
| | `human_review.annotators`, `.realism`, `.scope_agreement` | `human_review.reviewers` and per-variant slots |
| | check `basis` as the authority | the licence entry is the authority; `basis` optional |
| Kept unchanged | `target`, `func`, `tests`, `source_example.text`, `length`, `incidental_details` (plus new entries), `shared_surface_features`, `relation`, `marker.spec`, `turns`, `cells_not_applicable`, `contamination`, `split`, variant `id`, `role`, `cue`, `fit`, `text`, `rules_add`, `fit_note`, every check `id` and `spec` | |

Prompt building is unchanged: `seed_lint_v1.build_messages(card, variant, turns, perturbed)` builds identical prompts from a v1 card and its v2 migration (checked for D01 and C01).

### 4.1 Migration mapping

| v1 item | v2 item |
| --- | --- |
| `reference_solutions[v]` | `variants[v].valid_answers` entry, `origin: v1_reference` |
| `alternative_solutions[i]` with `variant: v` | `variants[v].valid_answers` entry, `origin: v1_alternative`, `why` becomes `note` |
| `copy_answers[v]` | `variants[v].invalid_answers` entry, `kind: copy`, `origin: v1_copy`, `fails` = the checks it fails today |
| check `basis.type: stated` | licence `DIRECT`, `evidence` = the quote |
| check `basis.type: target_rule` | licence `DIRECT`, `evidence` = the rule text or its decisive phrase |
| check `basis.type: role_implied` | licence `INFERRED`, same `implication`, `evidence` from the user's words or the target |
| check `basis.ambiguity: ambiguous` | licence `UNCLEAR` with `proposed` = the label the check implied |
| counter-example check in `must_transfer` that passes when the flagged pattern is avoided | moved to `must_not_transfer`, id kept, `units` = the flagged unit |
| wrong-fit check in `must_transfer` that repeats a `rules_add` rule against the relation | moved to `must_not_transfer`, id kept, `units` = the relation units the rule forbids |
| check on a unit whose v2 label is MAY (no basis in the prompt) | moved to `probes`, new id `P..`, old id in `v1_id` |

The extra answers needed to reach two valid and two minimal invalid answers per variant are written during migration.

## 5. Licence rules

### 5.1 Labels

- `MUST`: the answer fails if it does not use the unit.
- `MUST_NOT`: the answer fails if it uses the unit.
- `MAY`: using or not using the unit never fails the answer. MAY is not a failure (pilot audit). Target rules still apply: a MAY unit does not excuse a rule violation.
- `UNCLEAR`: Section 5.6.

### 5.2 Basis

| Basis | Definition | Allowed labels |
| --- | --- | --- |
| `DIRECT` | The evidence is an instruction or rule in the user's words or the target whose wording covers the unit. | MUST, MUST_NOT, MAY (a stated permission such as "you may keep the colour names") |
| `INFERRED` | No instruction covers the unit; the label follows from the role through one implication of the closed list (5.4). | MUST, MUST_NOT |
| `DEFAULT` | No evidence. | MAY only |

Reading guide for DIRECT (closed; anything else is INFERRED or DEFAULT):

| Prompt wording | Units covered |
| --- | --- |
| "borrow the idea", "take the principle", "the same idea" | MUST on the main relation units |
| "not its details", "not the numbers", "not the names" | MUST_NOT on every detail unit of the named type (all detail units for "details"); relation units are not details |
| "use the same X", "keep X", "follow X exactly" | MUST on the units that state X |
| "do not copy anything else", "everything else follows our rules" (blanket ban) | MUST_NOT on every other unit, except units entailed by a MUST unit or motivated by the target's own facts or rules, which are MAY with a `note` |
| "don't do it like this: <property>" | MUST_NOT on the units that realise the flagged property |
| a target rule (card or `rules_add`) or the format instruction that forbids what a unit states | MUST_NOT; evidence is the rule or format text (wrong fit, lures, an unneeded helper under "only the function and any helpers it needs") |
| a target rule that already requires what a unit states | MAY: the rule, not the example, is the reason; the rule's own checks test it |
| "you may keep X", "X is fine" | MAY on the units that state X |

### 5.3 Evidence

- `evidence` is an exact, case-sensitive substring of the single-turn prompt `seed_lint_v1.prompt_text(card, variant)` built without the control.
- At least one occurrence lies outside the source example. The example cannot license its own transfer; the user or the target must.
- The quote lies inside one message in the multi-turn build too (so it may not straddle the target and the user's example turn).
- Keep it short: the smallest phrase that carries the instruction (for example "not its details", not the whole sentence). The exporter records its prompt offsets (Section 9.1).

### 5.4 Closed list of implications (INFERRED)

| `implication` | Label | Roles | Unit kinds | Use when |
| --- | --- | --- | --- | --- |
| `relation_transfer` | MUST | analogy | relation | The relation the analogy is about. WARN if the unit is not `main`. |
| `named_part_transfer` | MUST | requirement | relation, detail | The part the user's words point to, when the requirement is implied. |
| `avoid_flagged_feature` | MUST_NOT | counter | relation, detail | The pattern the user's words blame, when the counter-example is implied. |
| `source_specific_fact` | MUST_NOT | all | detail | A fact about the source world that would be false in the target answer: the wrong currency, place, count or date for the target. If copying would only be odd (a source name in a label, a source identifier in code) and not false, the label is MAY, or UNCLEAR when the author expects reviewers to disagree. |

**Rule against hidden bans.** A unit is MUST_NOT only with DIRECT evidence or an INFERRED implication from this list. Otherwise it is MAY. Not needed does not mean banned. The same holds for MUST: no MUST without evidence.

### 5.5 Default patterns per role

Start from the column of the variant's role, then apply the prompt's wording. Any entry that departs from the default needs a `note`.

| Unit | Analogy | Requirement | Counter-example |
| --- | --- | --- | --- |
| Main relation units | MUST (DIRECT if stated, else `relation_transfer`) | MAY, unless it is the named part | MAY, unless it is the flagged pattern |
| The named part | | MUST (DIRECT if stated, else `named_part_transfer`) | |
| The flagged pattern | | | MUST_NOT (DIRECT if stated, else `avoid_flagged_feature`) |
| Other relation units | MAY | MAY; MUST_NOT under a blanket ban | MAY |
| Detail units | MUST_NOT if the prompt bans details (DIRECT) or the detail is a false-for-target fact (`source_specific_fact`); else MAY or UNCLEAR | same | same |
| Units that contradict a target rule | MUST_NOT (DIRECT, rule text) | same | same |

Common deviations:

- An analogy that permits a source name: "you may keep the colour names" makes that detail MAY (DIRECT). See the example card, Section 11.
- A counter-example that forbids one pattern: only the flagged units are MUST_NOT; the main relation and the other details stay as the default says (D01 counter: the three-price ladder is MUST_NOT, peak pricing is MAY).
- A requirement that names a detail: "use exactly the tier names Cobalt, Amber, Pearl" makes those detail units MUST.
- Wrong fit: a `rules_add` rule that forbids the relation makes the main relation MUST_NOT (D01 `analogy-*-wrong`).
- Partial fit: some relation units MUST, others MUST_NOT through `rules_add`.
- A lure: a relation that looks applicable but contradicts a card-level target rule is MUST_NOT in every variant (C01 U03, pre-release precedence against rule R2).

### 5.6 UNCLEAR

- Use UNCLEAR when the author cannot decide between two labels and expects reviewers to disagree. Give `proposed`, the basis and evidence of the proposed reading, and a `note`.
- If `proposed` is MUST or MUST_NOT, the unit still needs a check (so adjudication can settle it without re-authoring).
- A variant with at least one UNCLEAR unit whose final label (Section 2.7) is unresolved or UNCLEAR belongs to the ambiguity set, not the core benchmark. The core set and all confirmatory numbers use core variants only. The ambiguity set is reported separately under two readings: proposed (UNCLEAR as `proposed`) and lenient (UNCLEAR as MAY).
- Valid answers must be valid under every resolution: they pass every check, including checks on UNCLEAR units. Minimal invalid answers never target an UNCLEAR unit.
- Training exports mask UNCLEAR tokens (Section 9.1).

## 6. Licence and checks

### 6.1 Which checks may name which units

| Check list | Names units with label | When the check fails |
| --- | --- | --- |
| `target.rules[].checks`, `rules_add[].checks` (`units` optional) | MUST or MUST_NOT; a card-level rule check may name a unit only if that unit has the same label in every variant | Constraint failure; also counts as use of a named MUST_NOT unit, or non-use of a named MUST unit |
| `must_transfer` (`units` required) | MUST, or UNCLEAR with `proposed: MUST` | The named MUST units are not used |
| `must_not_transfer` (`units` required) | MUST_NOT, or UNCLEAR with `proposed: MUST_NOT` | The named MUST_NOT units are used |
| `probes` (`units` required) | MAY, or UNCLEAR with `proposed: MAY` | Never fails the answer |

Coverage: every MUST and MUST_NOT unit (and every UNCLEAR unit proposed MUST or MUST_NOT) is named by at least one check of that variant. No scoring check names a MAY unit. A `leak_absent` check on detail `I` names `I`. A check may name several units when one test covers them jointly (C01 L2 names I2 and U06); a failure then counts as use of all of them. Attribution through a rule check is coarse: any failure of the check counts as use of its named unit (C01 R2a fails for a hotfix bug of any cause). The scorer audit of plan 4.4 measures how often such attribution is wrong.

### 6.2 How use(a) is decided

The scored text is the v1 one: for decision cards the JSON string and number values of the parsed answer (`checks.json_strings`; keys are not scanned), for code cards the extracted code.

| Unit label | used(u) is true when |
| --- | --- |
| MUST | every check naming u passes |
| MUST_NOT | at least one check naming u fails |
| MAY | descriptive only: a probe naming u signals use (`use_when`), or, for a detail unit, its detector fires on the scored text |
| UNCLEAR | as its `proposed` label, in the ambiguity set only |

For detail units the check is normally `leak_absent` on the unit, so used(u) is "the detector fires". For relation units it is whatever kind the author chose (`py_test`, `json_*`, `regex_*`). The existing kinds of `checks.py` and `checks_v1.py` are all allowed.

### 6.3 Scoring

For one answer to one variant, after removing judge checks that have not been run:

- `format_ok` as in v1. If false, everything else is null and the answer counts only as a format failure, never as over-transfer.
- `constraint_ok`: every rule check passes.
- `must_ok`: every MUST unit is used.
- `mustnot_ok`: no MUST_NOT unit is used.
- `joint` (J) = `format_ok and constraint_ok and must_ok and mustnot_ok`.
- Over-transfer OT: `mustnot_ok` is false. Under-transfer UT: `must_ok` is false.

For a variant without judge checks, `joint` equals `checks_v1.score_v1(answer, card, variant)["joint"]` (for an ambiguity-set variant, under the proposed reading), because `score_v1` ignores `units`, `probes` and `licence`. This is how the reference cards were verified, and the v2 test suite must assert it.

### 6.4 Probes and the marker

Probes keep the copy rate of MAY units measurable (for example, how often a model reuses a source identifier it was allowed to reuse). They never enter J, OT or UT. The v1 marker is a card-level probe with `units`.

### 6.5 Reserved judge checks

Some licences are honest but no word list or test can decide them (D01 requirement-stated: "do not copy anything else from Stockholm" bans copying the daily cap or the exemptions, which a fee schedule can only mention in a label or an extra key). Such a unit gets a check of kind `judge_absent` (or `judge_present` for a MUST unit), `spec: ["judge_absent"]`, with `what` written as the yes/no question for the semantic judge of plan Section 4.4. Until that judge passes its audit:

- the linter reports each judge check as PENDING in draft mode and ERROR in release mode;
- the linter does not run judge checks on answers, and `fails` never lists them;
- the scorer returns them as not run, computes J without them, and sets `judge_pending: true` on the result.

A minimal invalid answer may not target a unit tested only by judge checks.

## 7. Answers

- At least two valid answers per variant, differently worded: their normalised forms differ (decision: the parsed object serialised with sorted keys; code: the extracted code with comments, blank lines and repeated whitespace removed).
- Every valid answer passes every non-judge check of the variant (`joint` true), and again under the incidental-detail control when the control applies to that variant.
- If the variant has a MAY detail unit, at least one valid answer should use it and list it in `uses_may` (WARN otherwise). This proves no check bans it.
- At least two `minimal` invalid answers per variant, each one edit away from its `pair_of` answer, each violating exactly one item; at least one of them violates a licence unit rather than a target rule. Prefer one answer per kind of failure: a missing MUST unit, a used MUST_NOT unit, a broken target rule.
- For code cards an invalid answer is real, runnable code (it parses and defines `func`) whose only fault is the one it declares.
- `copy` answers keep the v1 role: an answer that copies the example. Each must fail at least one `must_transfer` or `must_not_transfer` check.

## 8. Linter rules (`src/seed_lint_v2.py`)

Each statement is a condition that must hold; the linter reports the rule ID when it does not. Severity: ERROR (card unusable), WARN (a person should look), PENDING (only humans or a later work package can settle it; becomes ERROR with `--release`). Mode: D = draft, R = release, B = both. Rules marked "gold" run only without `--no-gold`.

### 8.1 Metadata and provenance

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| M1 | Every field marked R in Section 2 is present with the stated type; code cards have `func` and `tests`. | ERROR | B |
| M2 | `schema == "seed-card-v2"`; `id` matches its pattern and the file name. | ERROR | B |
| M3 | `status` is in the enum. In release mode `status == "accepted"`. | ERROR | B |
| M4 | `model_assistance` is `none`, `drafted` or `edited`; if not `none`, `model_assistance_log` has non-empty `model`, `date`, `scope`, `prompt_ref`. | ERROR | B |
| M5 | `author_id`, `domain`, `relation_family`, `template_group_id`, `provenance_group_id` match their patterns. | ERROR | B |
| M6 | `domain` and `relation_family` are in their registries (`data/registry/domains.json`, `data/registry/relation_families.json`). If a registry file does not exist yet, PENDING. | ERROR | B |
| P1 | `source_type` is in the list; `case` is non-empty; references as in v1 unless `original_scenario`, which needs `original_authoring`. | ERROR | B |
| P2 | `urls_checked_by_human` is true. | PENDING | B |

### 8.2 Source example and spans

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| S1 | The span texts concatenate exactly to `source_example.text`. | ERROR | B |
| S2 | Span ids are unique and match `^S\d{2,3}$`. | ERROR | B |
| S3 | No span text is empty. | ERROR | B |
| S4 | `kind` is `relation`, `detail` or `context`; relation spans name a unit in `relation_units`; detail spans name a unit in `incidental_details`; context spans have no `unit`. | ERROR | B |
| S5 | Every relation unit and every detail unit owns at least one span; unit ids are unique across both registries. | ERROR | B |
| S6 | Every detail span contains at least one match of its unit's detector (`checks.term_regex` per leak term, `re.search(leak_regex, ..., re.I)`). | ERROR | B |
| S7 | Every detector match in the example lies inside one span of that unit; no two detectors match overlapping characters. | ERROR | B |
| S8 | Leak terms and leak regex match the example and match neither the target text (task, rules of every variant) nor the user's own words of any variant (v1 rule). | ERROR | B |
| S9 | A span with no letter or digit has kind `context`. | WARN | B |
| S10 | Every occurrence of a control's `from` lies inside spans of its unit, `from != to`, and the control spans tile the control example. | ERROR | B |
| S11 | At least one relation unit has `main: true`. | ERROR | B |
| S12 | No span boundary falls between two letters or digits. | WARN | B |
| S13 | No context span is longer than 160 characters while containing a sentence of at least 8 words (such a span is likely an unlabelled relation). | WARN | B |
| S14 | The card has at least 3 detail units (ERROR), and at least 3 of them are MUST_NOT in at least one variant (WARN). | ERROR / WARN | B |
| S15 | Sentence count on prose (v1 `count_sentences`) is at least 8 for `standard` and at least 20 for `long`. | WARN | B |
| S16 | `shared_surface_features`: at least 3 when the card has a counter variant; each `source_quote` is in the example and each `target_quote` in the target (v1). | ERROR | B |
| S17 | The example text occurs exactly once in the built prompt of every variant. | ERROR | B |

### 8.3 Licence

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| C1 | Every variant has `licence`; every key of `licence.units` is a unit id; after expansion every relation and detail unit has exactly one entry. | ERROR | B |
| C2 | `label` and `basis` are in their enums and compatible: MUST and MUST_NOT need DIRECT or INFERRED; MAY needs DEFAULT or DIRECT; INFERRED is never used for MAY; for UNCLEAR the rule applies to `proposed`. | ERROR | B |
| C3 | Every DIRECT or INFERRED entry has `evidence` that is an exact substring of the single-turn prompt, has at least one occurrence outside the source example, and lies inside one message of the multi-turn build. | ERROR | B |
| C4 | Every INFERRED entry has an `implication` from the closed list that allows its label, the variant's role and the unit's kind (Section 5.4). `relation_transfer` on a non-main unit is WARN. | ERROR | B |
| C5 | Every UNCLEAR entry has `proposed` in {MUST, MAY, MUST_NOT} and a non-empty `note`. | ERROR | B |
| C6 | A stated-cue variant has at least one DIRECT entry. | WARN | B |
| C7 | At least one MUST or MUST_NOT entry of the variant takes its evidence from the variant's own words (text without `{EX}`); otherwise the role and cue do not shape the licence. Expected to fail for some wrong-fit variants, where a target rule decides (D01 `analogy-implied-wrong`). | WARN | B |
| C8 | No unit that has a control is MUST in any variant (if it is, that variant gets no control prompt). | WARN | B |
| C9 | Every UNCLEAR unit has a final label (Section 2.7). Until then its variant is in the ambiguity set; the linter reports the count. In release mode a final UNCLEAR is allowed (H4). | PENDING | D |

### 8.4 Checks

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| K1 | Every check in `must_transfer`, `must_not_transfer` and `probes` has non-empty `units`, all valid ids; rule checks may have `units`; check ids are unique within a variant (rule checks included). | ERROR | B |
| K2 | List and label agree (Section 6.1): `must_transfer` names MUST units, `must_not_transfer` names MUST_NOT units, rule checks name MUST or MUST_NOT units (card-level rule checks: in every variant), probes name MAY units; UNCLEAR counts as its `proposed`. | ERROR | B |
| K3 | Every MUST and MUST_NOT unit (and UNCLEAR proposed MUST or MUST_NOT) is named by at least one check of the variant. | ERROR | B |
| K4 | No rule, `must_transfer` or `must_not_transfer` check names a MAY unit. | ERROR | B |
| K5 | A `leak_absent` check on detail `I` lists `I` in `units`. | ERROR | B |
| K6 | The v1 check lint holds for every check and probe: known kind; `py_test` names a defined test; stated quotes found; numeric bounds of bound kinds appear in the basis text; banned or required terms appear in the prompt; regex bans match the prompt. Basis text = the check's own `basis` quote or rule text if present, else the evidence of its named units joined. | ERROR | B |
| K7 | The card has no `judge_absent` or `judge_present` check. | PENDING | D |
| K7r | The card has no judge check, or the judge audit file `results/judge_audit/status.json` marks the judge as passed. | ERROR | R |
| K8 | `marker.units` is non-empty and names existing relation or detail units. | ERROR | B |

### 8.5 Answers (gold)

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| A1 | Each variant has at least two valid answers. | ERROR | B |
| A2 | The valid answers of a variant have pairwise different normalised forms (Section 7). | ERROR | B |
| A3 | Every valid answer gives `joint` true on all non-judge checks, and again with `perturbed=True` when the control applies to the variant. | ERROR | B, gold |
| A4 | Every unit in `uses_may` is MAY (final or proposed) in the variant; for a detail unit its detector fires on the answer's scored text. | ERROR | B, gold |
| A5 | If the variant has a MAY detail unit, at least one valid answer lists a MAY detail unit in `uses_may`. | WARN | B |
| A6 | Each variant has at least two `minimal` invalid answers. | ERROR | B |
| A7 | Every invalid answer is parseable (`format_ok`), and the set of failing non-judge checks equals `fails` exactly. | ERROR | B, gold |
| A8 | For a `minimal` answer: `pair_of` names a valid answer of the variant; `violates` is a MUST or MUST_NOT unit (not UNCLEAR, not judge-only) or a rule id of the variant; every check in `fails` tests `violates`. | ERROR | B |
| A9 | Every `minimal` answer has `difflib.SequenceMatcher(None, pair.text, answer.text).ratio() >= 0.7` against its `pair_of`. | WARN | B |
| A10 | At least one `minimal` answer per variant violates a licence unit. | ERROR | B |
| A11 | Every MUST unit of the variant is violated by at least one invalid answer. | WARN | B |
| A12 | Every `copy` answer fails at least one `must_transfer` or `must_not_transfer` check. | ERROR | B, gold |
| A13 | v1 marker warnings: a full-fit requirement's valid answers carry the marker; a full-fit counter's valid answers do not. | WARN | B, gold |

### 8.6 Variants, cues and cells

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| Q1 | Variant ids are unique; role, cue, fit are in their enums; `text` contains `{EX}` exactly once. | ERROR | B |
| Q2 | An implied-cue variant's own words (text without `{EX}`) contain no phrase of `seed_lint_v1.IMPLIED_BANNED`. | ERROR | B |
| Q3 | A stated-cue variant's own words contain a `seed_lint_v1.CUE_PHRASES` phrase for its role. | WARN | B |
| Q4 | A non-full fit has `rules_add` or `fit_note`. | ERROR | B |
| Q5 | Every role x fit x cue cell is present or listed in `cells_not_applicable` with a reason, never both (v1). | ERROR | B |
| Q6 | The implied-cue share of the card's variants is at least 0.5. | WARN | B |
| Q7 | `turns == ["single", "multi"]`. | ERROR | B |

### 8.7 Human review

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| H1 | Every variant has both annotator slots filled with `role`, `realism` and a label for every unit. | PENDING | B |
| H2 | `author_id` is not among the reviewers of its own card. | ERROR | B |
| H3 | Both annotators rate realism at least 4 for every variant kept in the card. | ERROR | R |
| H4 | Every unit of every variant has a final label (agreement or adjudication), the card's `licence` label equals it, and a final UNCLEAR places the variant in the ambiguity set. | ERROR | R |
| H5 | Each annotator's role equals the variant's role, or a `role` adjudication exists. | ERROR | R |

### 8.8 Set level (`lint_set`)

| ID | Testable statement | Sev | Mode |
| --- | --- | --- | --- |
| T1 | No `source_type` supplies more than 40% of the cards of a pool. | WARN / ERROR | D / R |
| T2 | Each family has at least 40 test seeds (test pool only). | WARN / ERROR | D / R |
| T3 | At least 30% of test variants have an implied cue. | WARN / ERROR | D / R |
| T4 | Cards that share a `provenance_group_id` or `template_group_id` have the same `split`. | ERROR | B |
| T5 | No `relation_family` of the held-out-relation pool appears in training or development cards. | ERROR | B |
| T6 | Card ids are unique across the set, and no `X` card is in a pool. | ERROR | B |
| T7 | Not a rule: an INFO line with cards, variants, prompts (variants x 2 turns, plus controls), core and ambiguity counts, label distribution. | INFO | B |

## 9. Export definitions (`src/export_v2.py`, not yet implemented)

Exports of the hidden test pool are written only to the private test location (WP1.7), never into the public repository.

### 9.1 Training record (one JSON line per variant x turns x control)

| Field | Type | Meaning |
| --- | --- | --- |
| `record_id` | str | `<card_id>::<variant_id>::<single or multi>::<orig or ctrl>` |
| `card_id`, `variant_id` | str | |
| `schema`, `exporter_version`, `card_sha256` | str | Card schema, exporter version, hash of the card file |
| `pool`, `split` | str | Pool name (calibration, development, test_familiar, test_heldout_relation, test_heldout_domain, natural, training) and split |
| `subset` | str | `core` or `ambiguity` |
| `family`, `domain`, `relation_family`, `template_group_id`, `provenance_group_id`, `source_type`, `model_assistance` | str | Copied from the card |
| `role`, `role_id` | str, int | `analogy` 0, `requirement` 1, `counter` 2 |
| `cue`, `fit` | str | |
| `turns` | str | `single` or `multi` |
| `perturbed` | bool | True for the control build |
| `messages` | list | `seed_lint_v1.build_messages(card, variant, turns, perturbed)` |
| `example_location` | obj | `{message_index, char_start, char_end}` of the example inside that message's content |
| `spans` | list | One per span: `{span_id, kind, unit, label, basis, message_index, char_start, char_end}`; `label` is the final label, else the author's; context spans have `label: null` |
| `licence` | obj | The expanded licence: `{unit_id: {label, basis, implication, proposed, final}}` |
| `evidence` | list | One per DIRECT or INFERRED entry: `{unit_id, quote, message_index, char_start, char_end}` (first occurrence outside the example) |
| `checks` | list | `{id, list (rule, must_transfer, must_not_transfer, probe), kind, units}` |
| `valid_answers` | list | `{id, text}` |
| `invalid_answers` | list | `{id, text, kind, pair_of, violates, fails}` (ready for preference pairs) |
| `siblings` | list | Defined below |

Token labels are computed at training time for each tokenizer, from the character offsets above:

1. `rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)`.
2. Locate each message's content in `rendered` in order (search from the end of the previous match). If a content string is not found verbatim, the exporter raises; it never guesses.
3. Absolute span offsets = content offset of `example_location.message_index` + `example_location.char_start` + span offsets.
4. `enc = tokenizer(rendered, add_special_tokens=False, return_offsets_mapping=True)`.
5. Each token takes the label of the span it overlaps most (ties: the earlier span). Tokens outside the example, tokens of context spans and tokens of UNCLEAR units get IGNORE.
6. Ids: `MUST` 0, `MAY` 1, `MUST_NOT` 2, IGNORE -100. A flag `context_as_may` (default false) labels context tokens MAY instead.
7. Stored per tokenizer: `input_ids`, `token_labels` (same length), `span_token_ranges` (`{span_id: [first, last + 1]}`), `tokenizer` (name and revision).

Span boundaries come from the card and are given identically to every method (plan 4.1).

Siblings (within one card; all variants of a card share a split):

- For every other variant `w`: `{variant_id: w, relation, changed_units, changed_rules, provisional}`. `relation` is `should_not_change` when every unit has the same label in both variants and the rule sets (card rules plus `rules_add` ids) are equal, else `should_change`. `changed_units` lists units whose labels differ; `changed_rules` lists rule ids present in only one. `provisional` is true when either variant has an unresolved UNCLEAR (labels compared as `proposed`).
- For the control build of the same variant, when the control applies: `{variant_id: same, perturbed: true, relation: "should_not_change", changed_units: [], changed_rules: []}`.

RS uses `should_change` pairs; INV uses the control pairs.

### 9.2 Dataset statistics

`export_v2.py --stats` writes, per pool, four flat tables and one summary to `results/dataset_stats/<pool>/` (test pool: private location only).

`cards.csv`: `pool, card_id, family, domain, relation_family, source_type, model_assistance, author_id, template_group_id, provenance_group_id, split, status, length, example_chars, example_sentences, n_variants, n_spans, n_relation_spans, n_detail_spans, n_context_spans, n_relation_units, n_detail_units, has_control`.

`variants.csv`: `pool, card_id, variant_id, role, cue, fit, family, domain, relation_family, source_type, subset, n_must, n_may, n_must_not, n_unclear, n_direct, n_inferred, n_default, n_rule_checks, n_must_transfer, n_must_not_transfer, n_judge, n_probes, n_valid, n_invalid_minimal, n_copy, prompt_chars_single, control_applies`.

`units.csv`: `pool, card_id, variant_id, unit_id, unit_kind, main, n_spans, chars, label, basis, implication, proposed, final_label, n_checks, role, cue, fit, family, subset`.

`spans.csv`: `pool, card_id, span_id, position, kind, unit, chars, words, in_code`.

`summary.json`: one key per table below, each a list of rows `{group values..., n_cards, n_variants, share}`:

| Key | Group by | Source |
| --- | --- | --- |
| `by_family`, `by_role`, `by_cue`, `by_fit`, `by_source_type`, `by_domain`, `by_relation_family`, `by_model_assistance`, `by_subset` | the named column | variants.csv |
| `role_x_cue_x_fit` | role, cue, fit | variants.csv |
| `licence_label_by_role_kind` | role, unit_kind, label (counts and shares of unit entries) | units.csv |
| `basis_by_label` | label, basis | units.csv |
| `unclear_rate` | role, cue | units.csv |
| `spans_per_card` | kind; mean, median, min, max | spans.csv |
| `span_chars` | kind; mean, median, p90, max | spans.csv |
| `units_per_card` | unit kind; mean, median, min, max | cards.csv |
| `checks_per_variant` | check list; mean, median | variants.csv |
| `answers_per_variant` | answer kind; mean, min | variants.csv |
| `example_length` | length; chars and sentences, mean, median | cards.csv |

Token counts per tokenizer are added by the training pipeline, not by this export.

## 10. Authoring workflow (fast path)

1. Write `target` (task, rules with checks, format) and the example.
2. Choose the detail units and their detectors first (leak terms that occur in the example and nowhere in the target or the user's words).
3. Mark spans in authoring markup and convert them with `scripts/spans_from_markup.py` (to be written). Markup: `[[U01|text]]` for a relation span of unit U01, `[[I3|text]]` for a detail span of I3, everything outside brackets is context. The first `|` separates the id; nesting is not allowed. If the example itself contains `[[` or `]]`, write `source_spans` by hand. The tool prints the spans and fails if S1, S6 or S7 break.
4. List `relation_units` with one-sentence `what` and the `main` flags.
5. Per variant: write `licence` as `defaults` plus the units that differ, using the role table (5.5) and reading guide (5.2). Write a `note` on every deviation.
6. Attach checks with `units`; reuse v1 kinds; for each detail unit that is MUST_NOT anywhere, one `leak_absent`.
7. Write one valid answer, then a second one worded differently, then derive each minimal invalid answer by one edit of a valid one.
8. Run the linter until it shows no ERROR. Review the expanded licence table (`scripts/licence_table.py`, to be written: units as rows, variants as columns).

Drafting agents follow the same steps, fill `model_assistance: drafted` and the log, and never see test-pool material.

## 11. Example card (abridged scenario, complete fields)

Verified with the WP0.2 prototype checks: spans tile the example, every evidence quote is a prompt substring outside the example, every valid answer passes `score_v1` (and the control), every invalid answer fails exactly its `fails`. The only finding is the accepted WARN S14 (two detail units are MUST_NOT anywhere, not three). It is a documentation example with two variants, not a benchmark card; its reference was not checked by a person.

```json
{
  "schema": "seed-card-v2",
  "id": "X01_triage_helpdesk",
  "status": "draft",
  "status_note": "Specification example only. Licences are the author's proposal, pending two blind reviewers.",
  "created": "2026-11-13",
  "updated": "2026-11-13",
  "author_id": "example_author",
  "model_assistance": "drafted",
  "model_assistance_log": {
    "model": "claude-opus-5-5",
    "date": "2026-11-13",
    "scope": "whole card",
    "prompt_ref": "WP0.2 specification example",
    "human_edits": null
  },
  "family": "decision",
  "domain": "it_operations",
  "domain_note": "university IT support",
  "relation_family": "urgency_ordered_service_levels",
  "template_group_id": "TG-X01",
  "provenance_group_id": "PG-manchester-triage",
  "provenance": {
    "source_type": "documented_case",
    "case": "Manchester Triage System colour categories",
    "references": [
      {
        "citation": "Mackway-Jones, K., Marsden, J., Windle, J. (eds.) Emergency Triage: Manchester Triage Group. 3rd ed. Wiley-Blackwell, 2014.",
        "doi": "10.1002/9781118299029"
      }
    ],
    "fresh_after_cutoff": false,
    "urls_checked_by_human": false
  },
  "target": {
    "task": "Our university IT helpdesk receives about 300 tickets a week, from network outages to requests for a new mouse. Set up exactly three priority levels for tickets, listed from most urgent to least urgent, and give each a target response time.",
    "rules": [
      {
        "id": "R1",
        "text": "Use exactly three levels.",
        "checks": [{"id": "R1a", "spec": ["json_len_between", "levels", 3, 3]}]
      },
      {
        "id": "R2",
        "text": "Response times are whole hours from 1 to 72.",
        "checks": [
          {"id": "R2a", "spec": ["json_all_int", "levels[].response_hours"]},
          {"id": "R2b", "spec": ["json_all_ge", "levels[].response_hours", 1]},
          {"id": "R2c", "spec": ["json_all_le", "levels[].response_hours", 72]}
        ]
      }
    ],
    "format": "Reply with JSON only, in this shape: {\"levels\": [{\"name\": \"...\", \"response_hours\": 1}]}"
  },
  "source_example": {
    "text": "Many hospital emergency departments sort arriving patients with a triage system. A nurse assesses each patient within a few minutes of arrival. The nurse gives the patient one of five colours. Red means immediate treatment. Orange means treatment within 10 minutes. Yellow means within 60 minutes, green within 120 minutes and blue within 240 minutes. The most dangerous conditions always get the shortest waiting time. The system is now used in hospitals in many countries.",
    "length": "standard",
    "incidental_details": [
      {"id": "I1", "text": "Colour names of the levels", "leak_terms": ["Red", "Orange", "Yellow", "Green", "Blue"]},
      {
        "id": "I2",
        "text": "Waiting times in minutes",
        "leak_regex": "\\b(?:10|60|120|240) minutes\\b",
        "control": {"from": "10 minutes", "to": "15 minutes", "leak_regex": "\\b(?:15|60|120|240) minutes\\b"}
      },
      {"id": "I3", "text": "The word 'immediate' for the top level", "leak_terms": ["immediate"]}
    ],
    "shared_surface_features": [
      {
        "feature": "named urgency levels",
        "source_quote": "one of five colours",
        "target_quote": "three priority levels"
      },
      {
        "feature": "a time limit per level",
        "source_quote": "treatment within 10 minutes",
        "target_quote": "target response time"
      },
      {
        "feature": "incoming cases sorted on arrival",
        "source_quote": "sort arriving patients",
        "target_quote": "receives about 300 tickets a week"
      }
    ]
  },
  "relation_units": [
    {"id": "U01", "what": "The more urgent the case, the shorter the allowed waiting time", "main": true},
    {"id": "U02", "what": "A quick first assessment of every case", "main": false},
    {"id": "U03", "what": "Every case gets exactly one named level", "main": false}
  ],
  "source_spans": [
    {
      "id": "S01",
      "text": "Many hospital emergency departments sort arriving patients with a triage system. ",
      "kind": "context"
    },
    {
      "id": "S02",
      "text": "A nurse assesses each patient within a few minutes of arrival. ",
      "kind": "relation",
      "unit": "U02"
    },
    {"id": "S03", "text": "The nurse gives the patient one of five colours. ", "kind": "relation", "unit": "U03"},
    {"id": "S04", "text": "Red", "kind": "detail", "unit": "I1"},
    {"id": "S05", "text": " means ", "kind": "relation", "unit": "U01"},
    {"id": "S06", "text": "immediate", "kind": "detail", "unit": "I3"},
    {"id": "S07", "text": " treatment. ", "kind": "relation", "unit": "U01"},
    {"id": "S08", "text": "Orange", "kind": "detail", "unit": "I1"},
    {"id": "S09", "text": " means treatment within ", "kind": "relation", "unit": "U01"},
    {"id": "S10", "text": "10 minutes", "kind": "detail", "unit": "I2"},
    {"id": "S11", "text": ". ", "kind": "context"},
    {"id": "S12", "text": "Yellow", "kind": "detail", "unit": "I1"},
    {"id": "S13", "text": " means within ", "kind": "relation", "unit": "U01"},
    {"id": "S14", "text": "60 minutes", "kind": "detail", "unit": "I2"},
    {"id": "S15", "text": ", ", "kind": "context"},
    {"id": "S16", "text": "green", "kind": "detail", "unit": "I1"},
    {"id": "S17", "text": " within ", "kind": "relation", "unit": "U01"},
    {"id": "S18", "text": "120 minutes", "kind": "detail", "unit": "I2"},
    {"id": "S19", "text": " and ", "kind": "context"},
    {"id": "S20", "text": "blue", "kind": "detail", "unit": "I1"},
    {"id": "S21", "text": " within ", "kind": "relation", "unit": "U01"},
    {"id": "S22", "text": "240 minutes", "kind": "detail", "unit": "I2"},
    {"id": "S23", "text": ". ", "kind": "context"},
    {
      "id": "S24",
      "text": "The most dangerous conditions always get the shortest waiting time. ",
      "kind": "relation",
      "unit": "U01"
    },
    {"id": "S25", "text": "The system is now used in hospitals in many countries.", "kind": "context"}
  ],
  "relation": "The more urgent a case, the shorter the time allowed before it is handled.",
  "turns": ["single", "multi"],
  "variants": [
    {
      "id": "analogy-stated-full",
      "role": "analogy",
      "cue": "stated",
      "fit": "full",
      "text": "Our helpdesk could work like the hospital system below. Borrow the idea, not the numbers: our response times must suit IT work. You may keep the colour names if they help.\n\n{EX}",
      "licence": {
        "defaults": {"relation": {"label": "MAY", "basis": "DEFAULT"}, "detail": {"label": "MAY", "basis": "DEFAULT"}},
        "units": {
          "U01": {"label": "MUST", "basis": "DIRECT", "evidence": "Borrow the idea"},
          "I1": {"label": "MAY", "basis": "DIRECT", "evidence": "You may keep the colour names"},
          "I2": {"label": "MUST_NOT", "basis": "DIRECT", "evidence": "not the numbers"}
        }
      },
      "must_transfer": [
        {
          "id": "T1",
          "what": "Response times increase from the most to the least urgent level",
          "spec": ["json_increasing", "levels[].response_hours"],
          "units": ["U01"]
        }
      ],
      "must_not_transfer": [{"id": "L1", "what": "No minute deadlines from the hospital", "spec": ["leak_absent", "I2"], "units": ["I2"]}],
      "probes": [
        {
          "id": "P1",
          "what": "Colour names reused",
          "spec": ["leak_absent", "I1"],
          "units": ["I1"],
          "use_when": "fail"
        }
      ],
      "valid_answers": [
        {
          "id": "V1",
          "text": "{\"levels\": [{\"name\": \"Red\", \"response_hours\": 2}, {\"name\": \"Orange\", \"response_hours\": 8}, {\"name\": \"Yellow\", \"response_hours\": 48}]}",
          "origin": "author",
          "uses_may": ["I1"]
        },
        {
          "id": "V2",
          "text": "{\"levels\": [{\"name\": \"Immediate\", \"response_hours\": 1}, {\"name\": \"Same day\", \"response_hours\": 8}, {\"name\": \"This week\", \"response_hours\": 72}]}",
          "origin": "author",
          "uses_may": ["I3"]
        }
      ],
      "invalid_answers": [
        {
          "id": "X1",
          "text": "{\"levels\": [{\"name\": \"Immediate\", \"response_hours\": 72}, {\"name\": \"Same day\", \"response_hours\": 8}, {\"name\": \"This week\", \"response_hours\": 1}]}",
          "kind": "minimal",
          "pair_of": "V2",
          "violates": "U01",
          "fails": ["T1"],
          "origin": "author"
        },
        {
          "id": "X2",
          "text": "{\"levels\": [{\"name\": \"Red (10 minutes)\", \"response_hours\": 2}, {\"name\": \"Orange\", \"response_hours\": 8}, {\"name\": \"Yellow\", \"response_hours\": 48}]}",
          "kind": "minimal",
          "pair_of": "V1",
          "violates": "I2",
          "fails": ["L1"],
          "origin": "author"
        }
      ]
    },
    {
      "id": "counter-implied-full",
      "role": "counter",
      "cue": "implied",
      "fit": "full",
      "text": "Last term we copied the hospital system below for the helpdesk. Students kept asking what the colours meant, and most of them picked the wrong one when they filed a ticket.\n\n{EX}",
      "licence": {
        "defaults": {"relation": {"label": "MAY", "basis": "DEFAULT"}, "detail": {"label": "MAY", "basis": "DEFAULT"}},
        "units": {
          "I1": {
            "label": "MUST_NOT",
            "basis": "INFERRED",
            "evidence": "Students kept asking what the colours meant",
            "implication": "avoid_flagged_feature"
          },
          "I2": {"label": "MUST_NOT", "basis": "DIRECT", "evidence": "Response times are whole hours"},
          "U01": {
            "label": "MAY",
            "basis": "DEFAULT",
            "note": "Only the colour names are flagged; ordering by urgency stays free."
          }
        }
      },
      "must_transfer": [],
      "must_not_transfer": [
        {"id": "L1", "what": "No colour names", "spec": ["leak_absent", "I1"], "units": ["I1"]},
        {"id": "L2", "what": "No minute deadlines", "spec": ["leak_absent", "I2"], "units": ["I2"]}
      ],
      "probes": [],
      "valid_answers": [
        {
          "id": "V1",
          "text": "{\"levels\": [{\"name\": \"Immediate\", \"response_hours\": 1}, {\"name\": \"Today\", \"response_hours\": 8}, {\"name\": \"This week\", \"response_hours\": 72}]}",
          "origin": "author",
          "uses_may": ["I3"]
        },
        {
          "id": "V2",
          "text": "{\"levels\": [{\"name\": \"P1 Outage\", \"response_hours\": 4}, {\"name\": \"P2 Degraded\", \"response_hours\": 24}, {\"name\": \"P3 Request\", \"response_hours\": 72}]}",
          "origin": "author"
        }
      ],
      "invalid_answers": [
        {
          "id": "X1",
          "text": "{\"levels\": [{\"name\": \"Immediate\", \"response_hours\": 1}, {\"name\": \"Orange\", \"response_hours\": 8}, {\"name\": \"This week\", \"response_hours\": 72}]}",
          "kind": "minimal",
          "pair_of": "V1",
          "violates": "I1",
          "fails": ["L1"],
          "origin": "author"
        },
        {
          "id": "X2",
          "text": "{\"levels\": [{\"name\": \"P1 Outage\", \"response_hours\": 0}, {\"name\": \"P2 Degraded\", \"response_hours\": 24}, {\"name\": \"P3 Request\", \"response_hours\": 72}]}",
          "kind": "minimal",
          "pair_of": "V2",
          "violates": "R2",
          "fails": ["R2b"],
          "origin": "author"
        }
      ]
    }
  ],
  "cells_not_applicable": [
    {"role": "analogy", "fit": "full", "cue": "implied", "reason": "Not built in this specification example."},
    {"role": "analogy", "fit": "partial", "reason": "Not built in this specification example."},
    {"role": "analogy", "fit": "wrong", "reason": "Not built in this specification example."},
    {"role": "requirement", "fit": "full", "reason": "Not built in this specification example."},
    {"role": "requirement", "fit": "partial", "reason": "Not built in this specification example."},
    {"role": "requirement", "fit": "wrong", "reason": "Not built in this specification example."},
    {"role": "counter", "fit": "full", "cue": "stated", "reason": "Not built in this specification example."},
    {"role": "counter", "fit": "partial", "reason": "Not built in this specification example."},
    {"role": "counter", "fit": "wrong", "reason": "Not built in this specification example."}
  ],
  "human_review": {
    "reviewers": [],
    "variants": {
      "analogy-stated-full": {"annotator_1": null, "annotator_2": null},
      "counter-implied-full": {"annotator_1": null, "annotator_2": null}
    },
    "adjudications": []
  },
  "contamination": {"status": "not run"},
  "split": null,
  "notes": "Specification example. Shows an analogy that permits a source name (I1), a counter-example that forbids one pattern while the main relation stays MAY, a MAY detail used by valid answers (I3), and a probe."
}
```

What it shows: in `analogy-stated-full` the colour names (I1) are a source detail the user explicitly allows (MAY, DIRECT) while the minute deadlines (I2) are banned (MUST_NOT, DIRECT); in `counter-implied-full` only the flagged colour names are MUST_NOT by inference, the main relation U01 stays MAY, and the harmless detail I3 (`immediate`) is used by valid answers in both variants (`uses_may`). Probe P1 measures how often models reuse the allowed colour names.

## 12. What is still decided by humans

- Every licence in a draft card is the author's proposal. It becomes gold only when two blind reviewers label every unit of every variant and agree, or an adjudication settles the difference (H1, H4). Reviewers see the prompt and the units, not the author's labels.
- Reviewers also decide: the role of each prompt (kappa on roles), realism 1 to 5 per prompt, every UNCLEAR unit, whether a "target-motivated" or "entailed" MAY note under a blanket ban is honest, and whether a `source_specific_fact` really is false for the target.
- The linter proves that labels, evidence, checks and answers are consistent with each other. It does not prove that the segmentation is the best one, that a word list catches every paraphrase, or that a `py_test` threshold matches a vague instruction. The scorer audit (plan 4.4) measures that on real outputs.
- Span boundaries and unit groupings are reviewed with the licences: a reviewer who thinks a span mixes two units marks it, and the author splits it.
- The domain and relation-family registries and the assignment of cards to pools are decided by the owner (with Opus), not by the author of a card.

## 13. Implementation tasks

1. `src/checks_v2.py`: `score_v2` (Section 6.3) on top of `checks_v1.run_check_v1`, returning `format_ok, constraint_ok, must_ok, mustnot_ok, joint, used_units, probe_uses, judge_pending, subset`; reserved judge kinds return "not run".
2. `src/seed_lint_v2.py`: every rule in Section 8 with its ID in the message, draft and release modes, `--no-gold`, `--quiet`; import helpers from `seed_lint_v1` without changing it.
3. `tests/test_seed_lint_v2.py`: the two reference cards pass with no ERROR; one mutation test per ERROR rule (each mutation must raise exactly that rule); `score_v2` joint equals `score_v1` joint on every valid and invalid answer of the reference cards.
4. `scripts/spans_from_markup.py` and `scripts/licence_table.py` (Section 10).
5. `src/export_v2.py`: Section 9, with a test that span offsets reproduce the span texts from `messages` and that token labels cover every non-context span with at least one token for one Qwen and one Llama tokenizer.
6. A v2 review-pack generator (successor of `scripts/prepare_review_v1_1.py`) that shows units, not labels, and writes the `human_review` slots back.
7. Migrate the other eight v1 cards by hand following Section 4.1 and the two reference cards.

## 14. Open design questions

Each item states the conflict, what this spec does now, and the recommended answer. Items 1 to 4 differ from the wording of MASTER-PLAN Section 4.1 and need a dated entry in its Section 13 if accepted.

1. **A third span kind.** The plan names two kinds (`relation | detail`) that tile the example. Tiling then forces framing text, connectives and code syntax into one of them, where no label makes sense and no check can test it. This spec adds `context` (unlicensed; IGNORE in training). Recommended: accept. Fallback if rejected: context spans become `detail` spans with a fixed MAY label, which inflates MAY counts.
2. **Licence keyed by unit, not by span.** The plan writes `licence: {span_id: label}`. Keying by unit keeps fragments of one idea and all occurrences of one detail consistent by construction and shortens cards; the export gives the plan's span-level map exactly. Recommended: accept.
3. **`gold_atoms` merged into the licence.** The plan lists both. Two stores of the same label would drift. Recommended: accept; "gold atom" names a licence entry.
4. **Check field `units` (a list) instead of `span`.** One check often tests several spans or units (all statements of the main relation; I2 and U06 in C01). Recommended: accept.
5. **"Every MUST and MUST_NOT span has a check" versus honest bans no check can test.** This spec reserves `judge_absent` and `judge_present` (Section 6.5) so the licence can stay honest; J excludes them until the plan 4.4 judge passes its audit. Alternative: label such units UNCLEAR. Recommended: judge checks, because UNCLEAR would push clear prompts into the ambiguity set.
6. **"Fails exactly the intended check."** When two checks test one item (D01 wrong fit: `T1` repeats rule `R4a`), a correct minimal answer fails both. This spec requires exactly one violated item and lets `fails` list every check of that item. Recommended: accept, and in new cards avoid duplicating a rule as a transfer check.
7. **"Violates exactly one licence item" (plan) versus "one licence item or target rule" (WP0.2 brief).** This spec allows either but requires at least one minimal answer per variant to violate a licence unit (A10). Recommended: accept.
8. **v1 copy answers fail several checks.** They cannot satisfy the minimal rule, so they are kept as `kind: copy` and do not count toward the minimum. Recommended: accept.
9. **Counter and wrong-fit checks change lists.** In v1 a counter-example's "avoid the flagged pattern" check sat in `must_transfer`, so copying the pattern counted as under-transfer. In v2 it counts as over-transfer. Pilot UT and OT for counter variants are not comparable with v2 numbers. Recommended: accept and say so in the paper's pilot note.
10. **Tighter hidden-ban rule shrinks the core set until review.** Applying Section 5.4 strictly, v1 inferred bans on names and identifiers become UNCLEAR (copying them is odd, not false), and a v1 ban on a behaviour with no prompt evidence (C01 leading `v` in four variants) becomes MAY with a probe. In the migrated cards only 3 of 8 D01 variants and 1 of 6 C01 variants are core until adjudication. Recommended: accept; reviewers settle UNCLEAR units in their first pass, and authors of new cards should state the bans they intend in the user's words when the scenario allows.
11. **Leak scanning skips JSON keys.** `checks.json_strings` scans values only, so a copied detail placed in a key (`"daily_cap_sek": 60`) is not seen. Changing it would change v1 scores. Recommended: keep v1 behaviour in `score_v2` for comparability, add keys to the semantic judge's input, and report this limit.
12. **Registries do not exist yet.** Held-out-relation and held-out-domain pools need closed lists of `relation_family` and `domain`. M6 is PENDING until `data/registry/` exists. Recommended: Opus defines both registries before batch drafting starts (WP1.x), from the relation, not the surface domain.
13. **Per-seed implied share.** v1 makes an implied share below 0.5 per seed an ERROR; plan 4.2 asks for implied cues "where natural" and 4.3 for at least 30% of test variants. This spec makes the per-seed rule a WARN (Q6) and the 30% set rule an ERROR in release (T3). Recommended: accept.
14. **Length rules.** v1 requires at least 8 sentences and 30% `long` seeds; plan 4.2 moves long sources to diagnostic subsets and the 6 November audit asks not to impose fixed lengths. This spec keeps the sentence minimum as WARN (S15) and drops the 30% long share. Recommended: accept.
15. **Three must-not details.** v1 requires at least 3 incidental details, all checked. This spec requires 3 detail units (ERROR) and warns when fewer than 3 are MUST_NOT anywhere (S14), so a card may keep harmless details MAY. Recommended: accept.
16. **Realism per prompt or per seed.** Plan 4.4 accepts a seed when both reviewers rate realism 4 or above; the v1.1 review pack rates each full prompt. This spec stores realism per variant and drops a variant (not the seed) that fails. Recommended: accept, and report variant and seed acceptance rates.
17. **Exceptions to a blanket ban.** "Do not copy anything else" does not cover units entailed by the required part or motivated by the target's own facts (D01 requirement-stated: U01 and U03 are MAY). This is a judgement the linter cannot test; it requires a `note` and reviewer confirmation. Recommended: accept.
18. **Model assistance of migrated cards.** The v1 cards recorded no model assistance. The migrated cards are marked `drafted` because their spans, licences and new answers were written by a model; the author should record whether v1 text was model-assisted. Recommended: the author fills `model_assistance_log.v1_origin` before review.
