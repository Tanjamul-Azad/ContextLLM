"""Build independent prompt-only review packs for OLD pilot calibration.

No model outputs, expected role labels, or checker rules are exported to reviewers.
This is calibration/design review, not new held-out data or completed annotation.
"""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "human_review" / "calibration_v0.1"
SELECTION = [
    ("C01", "P1_helpdesk_triage", "analogy"),
    ("C02", "P2_drone_pricing", "requirement"),
    ("C03", "P3_incident_andon", "counter"),
    ("C04", "P4_workshop_survivorship", "analogy"),
    ("C05", "P5_newsletter_headlines", "analogy"),
    ("C06", "P6_exam_hall_boarding", "requirement"),
    ("C07", "C1_window_sum", "counter"),
    ("C08", "C2_retry_backoff", "analogy"),
]


def write_new(path, text):
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite a review response: {path}")
    path.write_text(text, encoding="utf-8")


def main():
    seeds = json.loads((ROOT / "data" / "seeds.json").read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in seeds}
    cards = {}
    mapping = []
    for card_id, seed_id, role in SELECTION:
        seed = by_id[seed_id]
        role_prompt = seed["roles"][role]["plain"].replace("{EX}", seed["example"])
        prompt = f"{seed['task']}\n{seed['rules']}\n\n{role_prompt}\n\n{seed['format']}"
        cards[card_id] = prompt
        mapping.append({"card_id": card_id, "legacy_seed_id": seed_id,
                        "construction_role_NOT_human_gold": role, "wording": "plain",
                        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()})
    OUT.mkdir(parents=True, exist_ok=True)
    guide = """# Human review: প্রথম calibration round

Status: READY FOR INDEPENDENT REVIEW. Human responses: NOT COLLECTED.

এই pack-এ পুরোনো pilot-এর আটটি prompt আছে। উদ্দেশ্য হলো prompt থেকে কী চাওয়া হয়েছে এবং gold-check কী হওয়া উচিত তা স্বাধীনভাবে বোঝা। এগুলো নতুন held-out benchmark নয়। Model-এর output বা আমাদের checker-এর প্রত্যাশা দেওয়া হয়নি।

## কীভাবে কাজ করবেন

1. Reviewer A ও B নিজের নিজের file আলাদাভাবে পূরণ করবেন। প্রথম round শেষ হওয়ার আগে উত্তর আলোচনা করবেন না এবং পুরোনো gold/checker/result দেখবেন না।
2. কোনো case আগে দেখে থাকলে prior exposure লিখবেন। ইতিমধ্যে জানা label ভুলে যাওয়ার ভান করার প্রয়োজন নেই; এই কারণে সম্পূর্ণ blind study দাবি করা হবে না।
3. প্রতিটি prompt পড়ে purpose লিখবেন: analogy / requirement / counter-example / mixed / unclear। কোনো example প্রাসঙ্গিক না হলে সেটিও লিখবেন।
4. MUST USE, MAY USE, MUST NOT USE আলাদা করুন। প্রতিটি বাধ্যবাধকতা বা নিষেধাজ্ঞার পক্ষে prompt-এর একটি ছোট quote দিন। স্পষ্ট নির্দেশ, reasonable inference ও uncertain interpretation আলাদা করে লিখুন।
5. Prompt-এ নিষেধ না থাকলে নিজের পছন্দকে gold prohibition করবেন না। একটি negative example-এর সব বৈশিষ্ট্যই নিষিদ্ধ ধরে নেবেন না।
6. মূল task-এর কোন শর্ত বজায় থাকবে, conflict আছে কি না এবং গ্রহণযোগ্য একাধিক উত্তর সম্ভব কি না লিখুন। সময় লাগলে পূর্ণ code লিখতে হবে না; গ্রহণযোগ্য behaviour বা ছোট output sketch যথেষ্ট।
7. Accept / revise / exclude verdict দিন। সংশোধন প্রয়োজন হলে কী স্পষ্ট করতে হবে লিখুন; original prompt বদলে নিজের interpretation বসাবেন না।

প্রথম round-এ প্রায় ৩০–৪৫ মিনিট রাখুন; প্রকৃত সময় record করুন। বেশি সময় লাগলে সেটিও data-construction cost হিসেবে গুরুত্বপূর্ণ।

## Round শেষে

দুই file জমা হওয়ার পরে researcher-only mapping খুলে adjudication.md-তে মতভেদ লিখবেন। আগে দেওয়া উত্তর অপরিবর্তিত রেখে পাশে final decision যোগ করবেন। Free-text উত্তর থেকে স্বয়ংক্রিয় exact agreement হিসাব করা হবে না; প্রথমে atomic scope/constraint statements align করতে হবে। Raw disagreement, exclusion/revision এবং final labels আলাদা থাকবে। আটটি case থেকে স্থিতিশীল population agreement বা final dataset quality দাবি করা যাবে না।

এই calibration-এর পরে guide সংশোধন করে নতুন seed-এ independent annotation শুরু হবে। Human availability নিশ্চিত; annotation completion এবং agreement এখনও pending।
"""
    write_new(OUT / "README.md", guide)
    for reviewer, order in (("A", list(cards)), ("B", ["C06", "C03", "C08", "C01", "C07", "C04", "C02", "C05"])):
        lines = [f"# Reviewer {reviewer}: independent calibration responses", "",
                 "Read README.md first. Do not consult the other reviewer, old checker, or researcher-only mapping before completing this file.", "",
                 "Reviewer name/ID: [fill]", "Date: [fill]", "Start/end time: [fill]",
                 "Previous involvement in seed/gold creation or previous exposure to model results: [fill]", ""]
        for card_id in order:
            lines += [f"## {card_id}", "", "### User prompt", "", "````text", cards[card_id], "````", "",
                      "### Your independent interpretation", "",
                      "- Seen this exact case or its expected label before? [yes/no; describe]",
                      "- Example purpose: [analogy / requirement / counter-example / mixed / unclear]",
                      "- Relation/principle demonstrated: [fill]",
                      "- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]",
                      "- MAY USE: [allowed choices that are not mandatory]",
                      "- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]",
                      "- ACTIVE TARGET CONSTRAINTS: [fill]",
                      "- Any conflicting or underspecified instruction? [fill]",
                      "- One acceptable answer/behaviour sketch: [fill]",
                      "- Would rejecting a particular word/value require an unstated extra rule? [fill]",
                      "- Verdict: [accept / revise / exclude]",
                      "- Reason / minimal clarification needed: [fill]",
                      "- Confidence: [high / medium / low]", ""]
        write_new(OUT / f"reviewer_{reviewer.lower()}.md", "\n".join(lines) + "\n")
    lines = ["# Adjudication - use only AFTER both independent files are complete", "",
             "Status: NOT STARTED. Preserve initial responses. A discussion result is not independent agreement.", "",
             "| Card | Role: A / B | Shared atomic obligations | Disputed obligation / prohibition | Prompt evidence | Final decision | Action / version |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    lines.extend(f"| {card_id} | [fill] | [fill] | [fill] | [fill] | [accept/revise/exclude] | [fill] |" for card_id in cards)
    lines += ["", "Record any important missing constraint or accepted alternative answer. The two people should first align the unit being judged; do not compute kappa over eight arbitrary free-text rows. Track role agreement, atomic scope agreement and acceptability decisions separately. With this tiny calibration set, use descriptive counts and examples rather than a quality-certification claim."]
    write_new(OUT / "adjudication.md", "\n".join(lines) + "\n")
    manifest = {"version": "calibration_v0.1", "created": "2026-11-05",
                "purpose": "Legacy prompt/gold design calibration; not confirmatory evaluation",
                "human_annotation_completed": False, "cards": mapping}
    write_new(OUT / "researcher_only_manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(OUT), "cards_per_reviewer": len(cards),
                      "human_annotation_completed": False, "reviewer_ids": ["A", "B"]}, indent=2))


if __name__ == "__main__":
    main()
