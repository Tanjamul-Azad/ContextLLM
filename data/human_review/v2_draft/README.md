# Review pack v2 (draft)

Use reviewer_a_part1.md and reviewer_b_part1.md independently. Each reviewer sees 14 complete prompts
(2 cards), in a different order, with the units of the example in a different order. No author label,
note, check or answer is shown in Part 1. Hashes of the prompts are in the researcher-only manifest.

Part 1 gives, per prompt: the role, a realism rating from 1 to 5, and one label per unit (MUST, MAY, MUST_NOT or
UNCLEAR) with evidence. Part 2 (span review and the author-flagged items) is opened only after both Part 1 files are
submitted. Keep the manifest and the card JSON closed until then.

Start with a timed batch of 6 to 10 prompts. If instructions change after calibration, record the change and report
calibration separately from later agreement. The author of a card must not review it (lint rule H2).

Filled Part 1 files are read back into the cards' human_review slots with scripts/import_review_v2.py.
Report agreement before adjudication, then the adjudications, then the share of variants in the ambiguity set.
