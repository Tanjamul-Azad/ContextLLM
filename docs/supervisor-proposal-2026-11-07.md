# “That Was Just an Example”

## Learning Role-Aware Selective Transfer in LLMs

**Supervisor discussion draft · 7 November 2026 · Tanjamul Azad**

Research area — NLP, instruction following, analogical transfer and mechanistic interpretability.

Target — ACL/EMNLP research track. Submission timing will follow validated results, available resources and official calls.

এই প্রস্তাবে dataset construction, model behaviour, causal analysis ও training method-এর পরিকল্পনা রয়েছে। Human annotation, causal experiment ও method improvement-এর ফল এখনও সংগ্রহ করতে হবে। Protocol freeze-এর আগে নিচের সিদ্ধান্তগুলো supervisor-এর সঙ্গে চূড়ান্ত করা হবে।

## সমস্যা ও সহজ উদাহরণ

একজন user LLM-কে কোনো কাজ বোঝাতে example দেন। Example কখনও একটি principle বোঝায়, কখনও তার নির্দিষ্ট অংশ অনুসরণ করতে বলে, আবার কখনও কী এড়াতে হবে তা দেখায়। আমরা পরীক্ষা করব model এই ভূমিকা বুঝে target task-এর জন্য প্রয়োজনীয় অংশ ব্যবহার করতে পারে কি না।

একটি fictional practice scenario-তে university help desk-এর ticket priority নির্ধারণ করতে hospital triage-এর example দেওয়া হলো। User স্পষ্টভাবে বললেন, বেশি জরুরি ticket আগে নিতে হবে, সর্বোচ্চ তিনটি priority থাকবে এবং hospital-এর colour label ব্যবহার করা যাবে না। এখানে urgency principle ও তিনটির সীমা মানতে হবে। Hospital-এর colour label ব্যবহার করলে নির্দিষ্ট নিষেধ ভাঙবে। অন্য একটি variant-এ user যদি ঠিক সেই label ব্যবহার করতে বলেন, তখন gold scope বদলাবে। তাই কোন detail সঠিক তা prompt অনুযায়ী নির্ধারণ করতে হবে।

## Research question ও সম্ভাব্য gap

**একই source example-এর ভূমিকা বদলালে LLM কি যথাযথভাবে transfer scope বদলায় এবং target constraints বজায় রাখে? এই আচরণের causal mechanism শনাক্ত করে training-এর মাধ্যমে উন্নতি করা যায় কি?**

কাছের গবেষণার সঙ্গে সম্পর্ক নিচে দেওয়া হলো। লিংক করা primary page-এর title, venue/status ও abstract 7 November 2026-এ যাচাই করা হয়েছে। বিস্তারিত overlap যাচাইয়ের জন্য full-text comparison ও বিস্তৃত literature search pilot-এর অংশ থাকবে।

| কাছের কাজ | প্রকাশিত কাজের focus | আমাদের প্রস্তাবের যে অংশ পরীক্ষা করতে হবে |
| --- | --- | --- |
| Mitigating Copy Bias in In-Context Learning through Neuron Pruning, EACL Findings 2026 | Demonstration থেকে copying bias, neuron identification ও pruning | User example-এর role অনুযায়ী কখন copy করা দরকার এবং কখন ক্ষতিকর, উভয় আচরণ একসঙ্গে মাপা |
| AnaloBench, EMNLP 2024 | Abstract ও long-context analogy identification/retrieval | Target task সম্পন্ন করার সময় scope অনুযায়ী relation ব্যবহার ও constraints ধরে রাখা |
| LLMs Get Lost In Multi-Turn Conversation, 2025 preprint | Single-turn ও multi-turn performance এবং unreliability | Single-turn-এই role-sensitive failure আছে কি না, পরে information-equivalent multi-turn control |

Sources — [Copy bias and neuron pruning](https://aclanthology.org/2026.findings-eacl.13/), [AnaloBench](https://aclanthology.org/2024.emnlp-main.725/), [Multi-turn conversation](https://arxiv.org/abs/2505.06120).

**Proposed novelty** হলো prompt-grounded role ও transfer-scope benchmark, useful ও harmful transfer-এর causal comparison এবং scope-consistency training। এই সমন্বয়ের distinctness literature comparison ও pilot দিয়ে প্রতিষ্ঠা করতে হবে। বিশেষ করে neuron pruning একাই novelty হিসেবে দাবি করা যাবে না।

## প্রত্যাশিত contribution

1. Evidence-grounded dataset যেখানে একই পরিস্থিতির meaningful role ও detail variants থাকবে। প্রতিটি gold item prompt-এর quote বা স্পষ্ট inference দিয়ে সমর্থিত হবে।
2. Model-এর role sensitivity ও failure mechanism-এর analysis, matched controls ও held-out evaluation সহ।
3. একটি scope-consistency training objective যার উন্নতি strong prompting, ordinary SFT এবং সমান parameter budget-এর LoRA-এর সঙ্গে তুলনা করা হবে।

## Dataset design

প্রথমে দুটি task family নেওয়ার প্রস্তাব করছি, constraint-based planning/decision এবং code/data transformation। Structured output ও unit test যেখানে উপযুক্ত সেখানে ব্যবহার করব।

একটি independent seed-এ থাকবে target task, source example, candidate relation, target constraints, provenance এবং evidence-grounded gold scope। Role flip, paraphrase বা incidental-detail substitution ওই seed-এর variant হিসেবে থাকবে।

| Annotation field | অর্থ |
| --- | --- |
| Role | analogy, requirement, counter-example, mixed বা unclear |
| MUST USE | যে relation বা detail ব্যবহার করা বাধ্যতামূলক |
| MAY USE | ব্যবহার করা অনুমোদিত, তবে optional |
| MUST NOT USE | ব্যবহার করলে prompt-এর নিষেধ বা target constraint ভাঙবে |
| Evidence | Prompt-এর quote, DIRECT/INFERRED label এবং প্রয়োজন হলে সংক্ষিপ্ত inference |
| Target constraints | মূল task-এর কার্যকর শর্ত |
| Uncertainty ও realism | অস্পষ্টতা, বিরোধ এবং বাস্তবসম্মত হওয়ার rating |

Role, fit এবং cue আলাদা axis। Fit full/partial/wrong হতে পারে। Cue explicit বা inferable হতে পারে। অর্থপূর্ণ combination তৈরি করব এবং অপ্রযোজ্য combination-এর কারণ লিখব। দীর্ঘ context ও multi-turn variant পরে diagnostic subset-এ যোগ হবে।

### বর্তমান প্রস্তুতি ও সংগ্রহের প্রস্তাব

- 10টি draft seed ও 68টি variant আছে। Gold ও references-এর independent validation বাকি।
- সংশোধিত v1.1 review pack-এ model-এর সম্পূর্ণ prompt রয়েছে। Export-এর সময় দুই reviewer-এর প্রতিটি prompt actual prompt builder-এর output-এর সঙ্গে মিলিয়ে দেখা হয়েছে।
- শুরুতে দুই reviewer একই ছয়টি item স্বাধীনভাবে করবেন, সময় ও prior exposure লিখবেন।
- Feasibility-তে সম্ভব হলে মোট 20–30টি reviewed development seed সংগ্রহ করব। এরপর 20টি করে batch-এ প্রাথমিক benchmark target 120–200 accepted seed। Final size pilot variance ও resource দিয়ে নির্ধারিত হবে।
- DL training-এর জন্য আলাদা pool ও learning curve লাগবে। 200–500 training seed group একটি প্রাথমিক planning range, যা collection capacity ও training smoke test দেখে সংশোধিত হবে।

প্রত্যেকে প্রথমে 10টি candidate জমা দেবেন। Drafting time, review time ও acceptance rate মেপে পরের batch দেব। 100টি করে candidate সংগ্রহে source ও relation diversity রাখতে হবে। Authors এবং independent reviewers-এর ভূমিকা ও আগের exposure লিখে রাখতে হবে। Author নিজের seed-এর independent blind reviewer হিসেবে গণ্য হবেন না।

### Source, merging ও contamination

Original human scenario, verified real request, documented-case adaptation এবং AI-assisted draft-এর provenance আলাদাভাবে লিখব। Factual claim-এর exact supporting excerpt, license/consent এবং adaptation record রাখব। Fictional scenario হলে সেটি fictional হিসেবে চিহ্নিত থাকবে।

সমস্ত source common seed schema-তে আনা হবে। Source/story/template ও near-duplicate group শনাক্ত করার পরে split হবে। Related variant একই split-এ থাকবে। Unseen-relation claim-এর জন্য relation holdout লাগবে। Held-out material দিয়ে training data বা prompt tuning করা যাবে না।

Controlled role/detail perturbation এবং unwanted train/test contamination আলাদাভাবে log হবে। Recall ও membership diagnostics-এর ফল uncertainty সহ প্রকাশ করব। Rewriting-এর পরে contamination আছে কি না, তারও সীমাবদ্ধতা থাকবে। Benchmark mitigation-এর সীমা নিয়ে ICML 2025-এর systematic study প্রাসঙ্গিক। [Contamination mitigation study](https://proceedings.mlr.press/v267/sun25t.html)

## Methodology ও deep learning method

**Behavioural evaluation**-এ no-example, original example, practical scope-inference prompting এবং scope-explicit oracle condition তুলনা করব। Oracle-তে gold scope দেওয়া হয় বলে সেটি model-এর available information বদলায়। Single-turn হবে প্রাথমিক evaluation।

**Mechanistic analysis**-এ dev data-তে layer scan ও lexical-control probe চালাব। তারপর token-aligned matched pair-এ activation patching এবং selected head/neuron ablation করব। Random এবং same-layer controls থাকবে। Layer early, middle, late বা distributed হতে পারে। Component নির্বাচন dev-তে করে held-out data-তে যাচাই করব। Patching metric ও intervention choice-এর sensitivity পরীক্ষা করতে হবে। [Activation patching methodology](https://proceedings.iclr.cc/paper_files/paper/2024/hash/06a52a54c8ee03cd86771136bc91eb1f-Abstract-Conference.html)

**Proposed training objective**-এ তিনটি অংশ থাকবে।

- Task supervision দিয়ে valid target answer শেখানো।
- Scope supervision দিয়ে required, optional ও prohibited transfer শেখানো।
- Paired consistency দিয়ে incidental detail বদলালে relevant answer properties স্থির রাখা এবং role/scope বদলালে সংশ্লিষ্ট properties বদলানো।

শুধু wording এক রাখাকে consistency ধরা হবে না। Gold-নির্ধারিত semantic properties-এর consistency মাপব। Training-এ gold scope ব্যবহার করা গেলেও মূল test-এ model-কে scope মূল prompt থেকে বুঝতে হবে।

প্রথমে ছোট open model-এ LoRA/QLoRA smoke test হবে। Targeted layers-এর causal evidence ও resource support পেলে targeted LoRA পরীক্ষা করব। তুলনায় strong prompting, same-data SFT এবং সমান parameter budget-এর random/all-layer LoRA থাকবে। Scope loss ও consistency loss বাদ দিয়ে ablation হবে। DPO/GRPO যোগ করার প্রয়োজন claim ও budget অনুযায়ী নির্ধারণ করা হবে।

## Evaluation ও validity

Primary metric হবে joint success, যেখানে required transfer ও target constraints পূরণ হয় এবং prohibited transfer ঘটে না। Secondary metrics হবে appropriate transfer, harmful detail transfer, constraint retention এবং role sensitivity। Format failure আলাদাভাবে রিপোর্ট করব। Optional detail-এর উপস্থিতি failure হিসেবে গণ্য হবে না।

Checkers-এ multiple valid answers, paraphrased errors এবং negated mention দিয়ে পরীক্ষা করব। Human-validated semantic audit sample থাকবে। Scope agreement-এর জন্য atomic item ও coding rule ঠিক করতে হবে। Categorical role agreement ও pre-adjudication scope agreement আলাদাভাবে রিপোর্ট করব। [Annotation agreement](https://aclanthology.org/J08-4004/)

Paired comparison ও seed/group-level uncertainty ব্যবহার করব, কারণ variants পরস্পর সম্পর্কিত। Ablation-এর পরে useful transfer ও general capability ধরে থাকছে কি না যাচাই করব। Requirement-counter copying gap একা failure প্রমাণ করবে না।

## 7–12 November feasibility plan

| সময় | কাজ | Reviewable output |
| --- | --- | --- |
| 7–8 Nov | Timed independent calibration, references ও prompt/gold audit | দুই reviewer-এর উত্তর, সময়, ambiguity ও rejection log |
| 8–9 Nov | Guide সংশোধন প্রয়োজন হলে version করা, নতুন seed সংগ্রহ ও checker validation | সম্ভব হলে 20–30 reviewed development seed, provenance ও checker examples |
| 10 Nov | একটি local ও একটি capable API model-এ validated prompt এবং prompting controls | Saved outputs, manual error audit, seed-level uncertainty ও token usage |
| 11 Nov | Dev-only patching prototype ও controls, memory/time measurement, সম্ভব হলে training smoke test | Causal intervention feasibility ও compute record |
| 12 Nov | Supervisor review | GO / REVISE / NO-GO এবং পরবর্তী scope |

এই সময়সূচি resource ও annotation progress অনুযায়ী review করতে হবে। প্রতিটি API run-এর আগে spending cap স্থির হবে। Confirmatory feasibility subset model run-এর আগে আলাদা করা হবে।

### Topic চালিয়ে যাওয়ার সিদ্ধান্ত

GO-এর পক্ষে চারটি evidence লাগবে।

1. মানুষের কাছে role ও gold scope যথেষ্ট পরিষ্কার এবং annotation workload সামলানো যায়।
2. Validated prompt-এ reproducible error থাকে, target-task inability বা checker mistake দিয়ে সেটি ব্যাখ্যা হয়ে যায় না। Practical prompting-এর পরও meaningful residual problem থাকে।
3. Closest prior work-এর তুলনায় contribution-এর স্পষ্ট পার্থক্য থাকে।
4. Small-model intervention ও training pipeline-এর resource feasibility দেখা যায়।

Supervisor-এর সঙ্গে ফল দেখার আগে numerical threshold, primary test ও exclusion rule ঠিক করতে হবে। Evidence অসম্পূর্ণ থাকলে REVISE হবে। Gold অনির্ধারিত থাকলে, distinct gap না পেলে বা প্রয়োজনীয় experiment চালানো অসম্ভব হলে scope change বা pivot বিবেচনা করব।

## Meeting-এ সিদ্ধান্তের তালিকা

- Dataset task families, source policy ও independent reviewer arrangement।
- Pilot pass marks, held-out families/relations এবং primary comparison।
- Small open model, API budget ও main training resource।
- Training contribution-এর minimum viable scope এবং baseline budget।
- Protocol amendment ও freeze করার শর্ত।

Freeze-এর সময় research questions, data rules, split, analysis ও stopping criteria লিখিতভাবে স্থির করব। পরের পরিবর্তন dated deviation log-এ যাবে। ইতিমধ্যে দেখা data-এর ব্যবহার development evidence হিসেবে নথিবদ্ধ থাকবে।

## Supporting documents

- [Dataset audit ও সংশোধনের বিস্তারিত](review-audit-and-dataset-plan-2026-11-06.md)
- [Dataset construction workflow](dataset-construction-v0.1.md)
- [সংশোধিত human-review pack](../data/human_review/v1_1_draft/README.md)
- [পুরোনো detailed protocol draft, amendment review প্রয়োজন](paper-protocol.md)

এই meeting draft-এ audited dataset ও method corrections একত্র করা হয়েছে। Detailed protocol-এর claims, thresholds ও contamination section এই সিদ্ধান্তের সঙ্গে সমন্বয় করে freeze করতে হবে।
