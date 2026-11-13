# WP0.4 backbone competence screen

**Exploratory.** Development-stage results on unreviewed draft items (10 v1 draft cards, 10 pilot seeds). Not evidence for the paper; used only to choose backbones.

Gate: a model is eligible if it solves at least 80% of the 20 no-example tasks (joint success: parseable answer and every task constraint satisfied). Greedy decoding, max 1024 new tokens. Intervals are 95% percentile bootstrap intervals (10,000 resamples over tasks; oracle: over cards). Oracle = the 68 v1 variants with the gold take / do-not-take statement in the prompt; joint success needs constraints, required transfer and no leakage. Code answers are executed by the existing checker, which is not sandboxed.

| Model | HF repo @ revision | No-example success (overall) | Decision | Code | v1 cards | Pilot seeds | Format fail | Oracle joint | Eligible (80%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3-4b-2507-4bit | unsloth/Qwen3-4B-Instruct-2507-bnb-4bit @ f12db89c | 70% [50, 90] (14/20) | 82% [55, 100] (9/11) | 56% [22, 89] (5/9) | 40% [10, 70] (4/10) | 100% [100, 100] (10/10) | 5% | 56% [37, 76] (38/68) | no |
| phi4-mini-4bit | unsloth/Phi-4-mini-instruct-bnb-4bit @ cece1fd3 | 75% [55, 90] (15/20) | 82% [55, 100] (9/11) | 67% [33, 100] (6/9) | 50% [20, 80] (5/10) | 100% [100, 100] (10/10) | 0% | 24% [7, 43] (16/68) | no |
| gemma3-4b-4bit | unsloth/gemma-3-4b-it-bnb-4bit @ eb03c885 | 75% [55, 95] (15/20) | 82% [55, 100] (9/11) | 67% [33, 100] (6/9) | 50% [20, 80] (5/10) | 100% [100, 100] (10/10) | 0% | 22% [6, 41] (15/68) | no |
| llama3.2-3b-4bit | unsloth/Llama-3.2-3B-Instruct-bnb-4bit @ bb1d317a | 50% [30, 70] (10/20) | 64% [36, 91] (7/11) | 33% [0, 67] (3/9) | 20% [0, 50] (2/10) | 80% [50, 100] (8/10) | 5% | 10% [2, 19] (7/68) | no |
| qwen3-8b-4bit | unsloth/Qwen3-8B-bnb-4bit @ 1deaf68f | 75% [55, 90] (15/20) | 91% [73, 100] (10/11) | 56% [22, 89] (5/9) | 60% [30, 90] (6/10) | 90% [70, 100] (9/10) | 0% | 43% [21, 62] (29/68) | no |
| qwen2.5-3b | Qwen/Qwen2.5-3B-Instruct @ aa8e7253 | 55% [35, 75] (11/20) | 64% [36, 91] (7/11) | 44% [11, 78] (4/9) | 30% [10, 60] (3/10) | 80% [50, 100] (8/10) | 0% | 21% [9, 31] (14/68) | no |
| qwen2.5-7b-4bit | unsloth/Qwen2.5-7B-Instruct-bnb-4bit @ bdd40416 | 70% [50, 90] (14/20) | 91% [73, 100] (10/11) | 44% [11, 78] (4/9) | 50% [20, 80] (5/10) | 90% [70, 100] (9/10) | 0% | 40% [22, 55] (27/68) | no |
| llama3.1-8b-4bit | unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit @ f15c379f | 60% [40, 80] (12/20) | 73% [46, 100] (8/11) | 44% [11, 78] (4/9) | 40% [10, 70] (4/10) | 80% [50, 100] (8/10) | 0% | 41% [19, 61] (28/68) | no |

## Oracle joint success by role

| Model | Analogy | Requirement | Counter-example | Oracle format failure |
| --- | --- | --- | --- | --- |
| qwen3-4b-2507-4bit | 57% [35, 81] (16/28) | 55% [25, 85] (11/20) | 55% [30, 80] (11/20) | 2% |
| phi4-mini-4bit | 32% [8, 58] (9/28) | 20% [5, 40] (4/20) | 15% [0, 35] (3/20) | 7% |
| gemma3-4b-4bit | 29% [0, 54] (8/28) | 15% [0, 35] (3/20) | 20% [0, 50] (4/20) | 0% |
| llama3.2-3b-4bit | 11% [0, 19] (3/28) | 0% [0, 0] (0/20) | 20% [0, 45] (4/20) | 7% |
| qwen3-8b-4bit | 54% [29, 75] (15/28) | 15% [0, 35] (3/20) | 55% [25, 85] (11/20) | 2% |
| qwen2.5-3b | 21% [3, 41] (6/28) | 20% [0, 50] (4/20) | 20% [0, 50] (4/20) | 0% |
| qwen2.5-7b-4bit | 46% [27, 62] (13/28) | 20% [5, 40] (4/20) | 50% [20, 80] (10/20) | 0% |
| llama3.1-8b-4bit | 54% [23, 80] (15/28) | 30% [5, 55] (6/20) | 35% [10, 60] (7/20) | 2% |

## Sensitivity: gate without the flagged tasks (not the gate)

Excluded: `C02_typed_tsv_parser` (checker: the test header does 'import datetime' after the model code, which rebinds the name and breaks correct solutions that use 'from datetime import datetime'); `D03_group_lending_lab` (task: the format template shows the placeholder 'group, individual or lab' and weaker models echo it); `D05_release_train_portal` (task: the format template shows the placeholder 'ship_without_it or delay_release' and models echo it).

| Model | No-example success on the remaining 17 tasks | Would pass 80% |
| --- | --- | --- |
| qwen3-4b-2507-4bit | 76% [53, 94] (13/17) | no |
| phi4-mini-4bit | 88% [71, 100] (15/17) | yes |
| gemma3-4b-4bit | 82% [65, 100] (14/17) | yes |
| llama3.2-3b-4bit | 59% [35, 82] (10/17) | no |
| qwen3-8b-4bit | 71% [47, 88] (12/17) | no |
| qwen2.5-3b | 65% [41, 88] (11/17) | no |
| qwen2.5-7b-4bit | 76% [53, 94] (13/17) | no |
| llama3.1-8b-4bit | 65% [41, 88] (11/17) | no |

## Tasks failed with no example

No task was failed by every complete model.

Failed by all but one model: C01_calver_compare (7/8), C02_typed_tsv_parser (7/8), C03_index_truncation (7/8)

### qwen3-4b-2507-4bit

- `C02_typed_tsv_parser` (v1_cards, code): R1a: <module> r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmpc; R2a: <module> r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmpu; R3a: <module> r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmp_; R4a: <module> r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmph
- `C03_index_truncation` (v1_cards, code): R1a: mp\tmp55l74mda\t.py", line 25, in <module> assert len(r) == 2 and abs(
- `C04_grader_assignment` (v1_cards, code): unparseable answer (output cut off at the token limit)
- `C05_simpson_methods` (v1_cards, code): R2a: \Users\User\AppData\Local\Temp\tmph19gcdgy\t.py", line 69, in <module>
- `D01_stockholm_parking` (v1_cards, decision): R2c: [200, 50, 30, 10]
- `D05_release_train_portal` (v1_cards, decision): R2a: ['ship_without_it or delay_release']

### phi4-mini-4bit

- `C01_calver_compare` (v1_cards, code): R2a:  parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmp95ib900b\t; R3a:  parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmpvh01v9zl\t; R4a:  parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmpsp8nxczj\t; R4b:  parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmp8xbv22sf\t
- `C02_typed_tsv_parser` (v1_cards, code): R1a: r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmpdqhvkh2g\t; R2a: r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmp33951ygb\t; R3a: r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmp8owi5znt\t; R4a: r = parse_rows(T) File "C:\Users\User\AppData\Local\Temp\tmp_jhau5ag\t
- `C04_grader_assignment` (v1_cards, code): R1a: timeout; R2a: timeout; R3a: timeout
- `D03_group_lending_lab` (v1_cards, decision): R2a: ['group, individual or lab']
- `D05_release_train_portal` (v1_cards, decision): R2a: ['ship_without_it or delay_release']

### gemma3-4b-4bit

- `C01_calver_compare` (v1_cards, code): R2a:  and not items)) ^^^^^^^^^^^^^^^^^^^^^^^^^ File "F:\Python\Lib\re\_par; R4a:  and not items)) ^^^^^^^^^^^^^^^^^^^^^^^^^ File "F:\Python\Lib\re\_par; R4b:  and not items)) ^^^^^^^^^^^^^^^^^^^^^^^^^ File "F:\Python\Lib\re\_par
- `C02_typed_tsv_parser` (v1_cards, code): R1a: sers\User\AppData\Local\Temp\tmp_tz40i9d\t.py", line 42, in <module> r; R2a: sers\User\AppData\Local\Temp\tmpwgld0tat\t.py", line 42, in <module> r; R3a: sers\User\AppData\Local\Temp\tmpoj4z10ff\t.py", line 42, in <module> r; R4a: sers\User\AppData\Local\Temp\tmp1v8tf8q8\t.py", line 42, in <module> r
- `C03_index_truncation` (v1_cards, code): R1a: mp\tmpdl64srth\t.py", line 21, in <module> assert len(r) == 2 and abs(
- `D02_social_norm_library` (v1_cards, decision): R1a: 5
- `D03_group_lending_lab` (v1_cards, decision): R2a: ['group, individual']

### llama3.2-3b-4bit

- `C01_calver_compare` (v1_cards, code): R2a: is True ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "C:\Users\User; R3a: 11.3') is False ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^ File "C:\Users\User; R4a: ert is_newer(a, b) in (True, False) ~~~~~~~~^^^^^^ File "C:\Users\User; R4b: .11.2') is True ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^ File "C:\Users\User
- `C02_typed_tsv_parser` (v1_cards, code): R1a: ocal\Temp\tmp828wdq4o\t.py", line 22, in parse_rows parsed_row['harves; R2a: ocal\Temp\tmp9r17fm2y\t.py", line 22, in parse_rows parsed_row['harves; R3a: ocal\Temp\tmpcr91_q9p\t.py", line 22, in parse_rows parsed_row['harves; R4a: ocal\Temp\tmpehn31xsj\t.py", line 22, in parse_rows parsed_row['harves
- `C03_index_truncation` (v1_cards, code): R1a: \Users\User\AppData\Local\Temp\tmp7th1_5yc\t.py", line 26, in <module>
- `C04_grader_assignment` (v1_cards, code): R1a: \Users\User\AppData\Local\Temp\tmpgpgwt0d2\t.py", line 45, in <module>; R2a: \Users\User\AppData\Local\Temp\tmpiwxt6gu6\t.py", line 44, in <module>
- `C05_simpson_methods` (v1_cards, code): R4a: \Users\User\AppData\Local\Temp\tmpwszec_fx\t.py", line 65, in <module>
- `D02_social_norm_library` (v1_cards, decision): R1a: missing; R2a: []; R2b: []; R2c: []; R3a: []; R5a: []
- `D03_group_lending_lab` (v1_cards, decision): unparseable answer
- `D05_release_train_portal` (v1_cards, decision): R2a: ['ship_without_it or delay_release']
- `P1_helpdesk_triage` (pilot_seeds, decision): json_len_between#0: missing; json_all_int#1: []; json_all_le#2: []
- `C2_retry_backoff` (pilot_seeds, code): py_test#0: .append) == 42 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ AssertionError; regex_absent#1: time.sleep(

### qwen3-8b-4bit

- `C01_calver_compare` (v1_cards, code): R2a: = parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmpvgjn97a0\; R3a: = parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmpw3hjut_s\; R4a: = parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmpgxa8bymf\; R4b: = parse_version(a) File "C:\Users\User\AppData\Local\Temp\tmpmz69b8av\
- `C03_index_truncation` (v1_cards, code): R1a: cal\Temp\tmpa7obgy9a\t.py", line 24, in <module> assert len(r) == 2 an
- `C04_grader_assignment` (v1_cards, code): R1a:  = assign(IDS, G4) File "C:\Users\User\AppData\Local\Temp\tmp974mn5eg\; R2a: )) ~~~~~~^^^^^^^^^ File "C:\Users\User\AppData\Local\Temp\tmp4lhgn0gd\; R3a:  = assign(IDS, G4) File "C:\Users\User\AppData\Local\Temp\tmp4k7jhuep\
- `D01_stockholm_parking` (v1_cards, decision): R2c: [500, 200, 100]
- `C2_retry_backoff` (pilot_seeds, code): py_test#0: builtin_function_or_method' object cannot be interpreted as an integer; regex_absent#1: time.sleep(

### qwen2.5-3b

- `C01_calver_compare` (v1_cards, code): R2a: \Users\User\AppData\Local\Temp\tmpzqymcgwj\t.py", line 49, in <module>; R4b: \Users\User\AppData\Local\Temp\tmpt9ntuhp4\t.py", line 51, in <module>
- `C02_typed_tsv_parser` (v1_cards, code): R1a: "C:\Users\User\AppData\Local\Temp\tmp34srmi9x\t.py", line 18, in parse; R2a: "C:\Users\User\AppData\Local\Temp\tmp5w8qbd02\t.py", line 18, in parse; R3a: "C:\Users\User\AppData\Local\Temp\tmpcixr5jud\t.py", line 18, in parse; R4a: "C:\Users\User\AppData\Local\Temp\tmpgx8pco6q\t.py", line 18, in parse
- `C03_index_truncation` (v1_cards, code): R1a: mp\tmp6bbikcro\t.py", line 23, in <module> assert len(r) == 2 and abs(
- `D02_social_norm_library` (v1_cards, decision): R1a: 1; R2b: [1]
- `D03_group_lending_lab` (v1_cards, decision): R2a: ['group, individual or lab']
- `D04_abc_makerspace` (v1_cards, decision): R1b: r wire,sandpaper,glue sticks,zip ties,fire blanket,eye-wash cartridges
- `D05_release_train_portal` (v1_cards, decision): R2a: ['ship_without_it or delay_release']
- `C2_retry_backoff` (pilot_seeds, code): py_test#0: builtin_function_or_method' object cannot be interpreted as an integer; regex_absent#1: print(
- `C4_pagination` (pilot_seeds, code): py_test#0:  list(range(1, 8)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ AssertionError

### qwen2.5-7b-4bit

- `C01_calver_compare` (v1_cards, code): R2a: ersion(a) ~~~~~~~~~~~~~^^^ File "C:\Users\User\AppData\Local\Temp\tmp1; R3a: ersion(a) ~~~~~~~~~~~~~^^^ File "C:\Users\User\AppData\Local\Temp\tmp4; R4a: ersion(a) ~~~~~~~~~~~~~^^^ File "C:\Users\User\AppData\Local\Temp\tmp1; R4b: ersion(a) ~~~~~~~~~~~~~^^^ File "C:\Users\User\AppData\Local\Temp\tmp7
- `C02_typed_tsv_parser` (v1_cards, code): R1a: _rows(T) File "C:\Users\User\AppData\Local\Temp\tmp6mz7c9cm\t.py", lin; R2a: _rows(T) File "C:\Users\User\AppData\Local\Temp\tmpnpun4ptn\t.py", lin; R3a: _rows(T) File "C:\Users\User\AppData\Local\Temp\tmpoo8d1fs7\t.py", lin; R4a: _rows(T) File "C:\Users\User\AppData\Local\Temp\tmprrj_w5y9\t.py", lin
- `C03_index_truncation` (v1_cards, code): R1a: mp\tmp983xaf8m\t.py", line 10, in <module> assert len(r) == 2 and abs(
- `C04_grader_assignment` (v1_cards, code): R1a: ndex]) >= (min_scripts_per_grader + (grader_index < num_graders - 1)):; R2a: ndex]) >= (min_scripts_per_grader + (grader_index < num_graders - 1)):; R3a: ndex]) >= (min_scripts_per_grader + (grader_index < num_graders - 1)):
- `D03_group_lending_lab` (v1_cards, decision): R2a: ['group, individual or lab']
- `C2_retry_backoff` (pilot_seeds, code): py_test#0: builtin_function_or_method' object cannot be interpreted as an integer; regex_absent#1: time.sleep(

### llama3.1-8b-4bit

- `C01_calver_compare` (v1_cards, code): R2a: \Users\User\AppData\Local\Temp\tmpd8l17yp_\t.py", line 49, in <module>
- `C02_typed_tsv_parser` (v1_cards, code): R1a: ~~~~~~~~^^^^^^^^^^^ File "C:\Users\User\AppData\Local\Temp\tmp89pup96t; R2a: ~~~~~~~~^^^^^^^^^^^ File "C:\Users\User\AppData\Local\Temp\tmpcw7xf2tp; R3a: ~~~~~~~~^^^^^^^^^^^ File "C:\Users\User\AppData\Local\Temp\tmpa0wkr6iw; R4a: ~~~~~~~~^^^^^^^^^^^ File "C:\Users\User\AppData\Local\Temp\tmpeekls99d
- `C03_index_truncation` (v1_cards, code): R1a: mp\tmpcbf4yla8\t.py", line 23, in <module> assert len(r) == 2 and abs(
- `C05_simpson_methods` (v1_cards, code): R1a: fk2gnv\t.py", line 17, in <genexpr> pass_rate_a = sum(passed for _, pa; R2a: 6zxhbn\t.py", line 17, in <genexpr> pass_rate_a = sum(passed for _, pa; R3a: 2395k1\t.py", line 17, in <genexpr> pass_rate_a = sum(passed for _, pa; R4a: gbqufm\t.py", line 17, in <genexpr> pass_rate_a = sum(passed for _, pa
- `D01_stockholm_parking` (v1_cards, decision): R1b: [(7, 10), (8, 14), (14, 19), (19, 22)]
- `D05_release_train_portal` (v1_cards, decision): R2a: ['ship_without_it or delay_release']
- `P6_exam_hall_boarding` (pilot_seeds, decision): json_len_between#0: 10
- `C2_retry_backoff` (pilot_seeds, code): py_test#0: nnot access local variable 'e' where it is not associated with a value
