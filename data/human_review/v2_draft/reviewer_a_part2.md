# Part 2: reviewer A

Open ONLY after BOTH reviewers have submitted Part 1. Work independently.
A. Segmentation. For each card, check that every span belongs to the unit it names. Mark 'mixes units' if a span
   carries two ideas or two surface items that could get different labels, and say how you would split it.

### C01_calver_compare

| Span | Kind | Unit | Text | OK / mixes units / wrong unit | Suggested split or unit |
| --- | --- | --- | --- | --- | --- |
| S01 | detail | I8 | Semantic Versioning 2.0.0 | | |
| S02 | context |  | , published at | | |
| S03 | detail | I3 | semver.org | | |
| S04 | context |  | , defines how version numbers like 1.4.2 are compared. | | |
| S05 | relation | U01 | A version has MAJOR, MINOR and PATCH numbers, and they are compared numerically from le... | | |
| S06 | relation | U02 | A version may carry a pre-release tag after a hyphen, such as 1.4.2-rc.1. | | |
| S07 | relation | U03 | A pre-release version has lower precedence than the normal version, so 1.4.2-rc.1 comes... | | |
| S08 | relation | U04 | Pre-release tags are compared part by part, numbers as numbers and words in ASCII order. | | |
| S09 | relation | U05 | Build metadata after a plus sign, such as 1.4.2+build.7, must be ignored when determini... | | |
| S10 | relation | U06 | Many teams also strip a leading v, as in v1.4.2, before parsing. | | |
| S11 | context |  | The functions below are the comparator our release tooling used for a library we publis... | | |
| S12 | detail | I1 | PyPI | | |
| S13 | context |  | . | | |
| S14 | relation | U07 | They raise ValueError for anything that does not look like a | | |
| S15 | detail | I4 | semantic version | | |
| S16 | context |  | . ```python | | |
| S17 | detail | I7 | import functools | | |
| S18 | context |  | import re | | |
| S19 | detail | I3 | SEMVER | | |
| S20 | context |  | = re.compile(r" | | |
| S21 | detail | I2 | ^v? | | |
| S22 | relation | U01 | (\d+)\.(\d+)\.(\d+) | | |
| S23 | relation | U02 | (?:-([0-9A-Za-z.-]+))? | | |
| S24 | relation | U05 | (?:\+[0-9A-Za-z.-]+)? | | |
| S25 | context |  | $") def _key(v): m = | | |
| S26 | detail | I3 | SEMVER | | |
| S27 | context |  | .match(v) | | |
| S28 | relation | U07 | if not m: raise ValueError(f" | | |
| S29 | detail | I4 | not a semantic version | | |
| S30 | relation | U07 | : {v}") | | |
| S31 | context |  | major, minor, patch, pre = m.groups() | | |
| S32 | relation | U01 | core = (int(major), int(minor), int(patch)) | | |
| S33 | relation | U03 | if pre is None: return core, (1,) # a release outranks any pre-release | | |
| S34 | relation | U04 | parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split(".")) | | |
| S35 | relation | U03 | return core, (0,) + parts | | |
| S36 | context |  | def | | |
| S37 | detail | I3 | compare_semver | | |
| S38 | relation | U01 | (a, b): ka, kb = _key(a), _key(b) return (ka > kb) - (ka < kb) | | |
| S39 | context |  | def | | |
| S40 | detail | I5 | sort_versions | | |
| S41 | relation | U08 | (versions): return sorted(versions, key= | | |
| S42 | detail | I7 | functools | | |
| S43 | context |  | . | | |
| S44 | detail | I5 | cmp_to_key | | |
| S45 | context |  | ( | | |
| S46 | detail | I3 | compare_semver | | |
| S47 | context |  | )) ``` | | |

### D01_stockholm_parking

| Span | Kind | Unit | Text | OK / mixes units / wrong unit | Suggested split or unit |
| --- | --- | --- | --- | --- | --- |
| S01 | relation | U08 | Stockholm ran congestion charges as a full-scale trial from | | |
| S02 | detail | I6 | 3 January | | |
| S03 | relation | U08 | to | | |
| S04 | detail | I6 | 31 July 2006 | | |
| S05 | context |  | . | | |
| S06 | relation | U08 | After a | | |
| S07 | detail | I5 | referendum | | |
| S08 | relation | U08 | in | | |
| S09 | detail | I6 | September 2006 | | |
| S10 | relation | U08 | , in which a majority of city voters said yes, the charges became permanent on | | |
| S11 | detail | I6 | 1 August 2007 | | |
| S12 | context |  | . | | |
| S13 | relation | U07 | The charge was collected at | | |
| S14 | detail | I4 | 18 control points | | |
| S15 | relation | U07 | on the roads into and out of the inner city. | | |
| S16 | relation | U07 | Cameras read each car's number plate, so drivers did not have to stop. | | |
| S17 | relation | U01 | The price depended on the time of day. | | |
| S18 | relation | U02 | A passage in the busiest half hours cost 20 | | |
| S19 | detail | I1 | Swedish kronor (SEK) | | |
| S20 | relation | U02 | , the shoulder periods around them cost 15 | | |
| S21 | detail | I1 | SEK | | |
| S22 | relation | U02 | , and the remaining daytime periods cost 10 | | |
| S23 | detail | I1 | SEK | | |
| S24 | context |  | . | | |
| S25 | relation | U03 | No charge applied in the evening, at night, at weekends or on public holidays. | | |
| S26 | relation | U04 | A driver paid at most 60 | | |
| S27 | detail | I1 | SEK | | |
| S28 | relation | U04 | in one day, however often they crossed the cordon. | | |
| S29 | relation | U05 | Traffic across the cordon fell by about | | |
| S30 | detail | I7 | 20 percent | | |
| S31 | relation | U05 | compared with the year before, and queues on the main approach roads became much shorter. | | |
| S32 | relation | U01 | Planners explained the result simply: drivers who could move their trip to a cheaper ha... | | |
| S33 | relation | U06 | The through route | | |
| S34 | detail | I2 | Essingeleden | | |
| S35 | relation | U06 | was exempt at first, because it was the main bypass around the centre. | | |
| S36 | relation | U06 | Residents of the island of | | |
| S37 | detail | I3 | Lidingö | | |
| S38 | relation | U06 | also had an exemption at the start, since their only road link to the mainland ran thro... | | |
| S39 | relation | U08 | Public support was low before the trial and rose after people saw the shorter queues. | | |
| S40 | relation | U09 | The revenue was earmarked for transport investment in the Stockholm region. | | |
| S41 | relation | U05 | Later evaluations found that the traffic reduction lasted for years after the charges b... | | |
| S42 | relation | U08 | The charges were raised in | | |
| S43 | detail | I6 | 2016 | | |
| S44 | relation | U08 | , and | | |
| S45 | detail | I2 | Essingeleden | | |
| S46 | relation | U08 | began to be charged at the same time. | | |
| S47 | relation | U01 | Researchers have used the case to argue that a price which follows the daily peak can m... | | |
| S48 | relation | U10 | Critics pointed to the cost of running the camera system and asked whether a simpler fl... | | |
| S49 | relation | U02 | The Stockholm design is a three-step price ladder in which the top price is double the ... | | |
| S50 | relation | U04 | It also shows that a daily cap protects people who must cross the cordon many times. | | |

B. Items the author flagged. These are author notes and questions, not accepted gold labels.
   Use the R-code to find the complete prompt in your Part 1. Do not change your Part 1 answers.

| Item | Unit(s) | Type | Author note or question | Decision (agree / disagree / unsure) | Reason |
| --- | --- | --- | --- | --- | --- |
| R001 | U05 | author note | The target is silent on +ci.N ordering; ignoring it and ordering by it are both allowed. | | |
| R002 | I1 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R002 | I2 | author note | v1 banned this as a source-specific fact, but accepting a leading v is a behaviour, not a fact about the source world, and nothing in this prompt forbids it. MAY; the v1 check L2 is kept as a probe. | | |
| R002 | I3 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R002 | I4 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R002 | I8 | author note | Added in v2 (no v1 check). Same doubt as the v1 identifier checks. | | |
| R003 | U01 | author note | Any correct comparator for YEAR.MONTH.PATCH compares numerically; motivated by the target, so the blanket rule does not cover it. | | |
| R003 | I1 | author note | v1 recorded no ambiguity on stated cues, but this cue does not speak about names, so the same doubt as in the implied variants applies. | | |
| R003 | I3 | author note | v1 recorded no ambiguity on stated cues, but this cue does not speak about names, so the same doubt as in the implied variants applies. | | |
| R003 | I4 | author note | v1 recorded no ambiguity on stated cues, but this cue does not speak about names, so the same doubt as in the implied variants applies. | | |
| R003 | I8 | author note | Added in v2 (no v1 check). Same doubt as the v1 identifier checks. | | |
| R004 | I1 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R004 | I2 | author note | v1 banned this as a source-specific fact, but accepting a leading v is a behaviour, not a fact about the source world, and nothing in this prompt forbids it. MAY; the v1 check L2 is kept as a probe. | | |
| R004 | I3 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R004 | I4 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R004 | I8 | author note | Added in v2 (no v1 check). Same doubt as the v1 identifier checks. | | |
| R005 | I1 | author note | v1 recorded no ambiguity on stated cues, but this cue does not speak about names, so the same doubt as in the implied variants applies. | | |
| R005 | I2 | author note | v1 banned this as a source-specific fact, but accepting a leading v is a behaviour, not a fact about the source world, and nothing in this prompt forbids it. MAY; the v1 check L2 is kept as a probe. | | |
| R005 | I3 | author note | v1 recorded no ambiguity on stated cues, but this cue does not speak about names, so the same doubt as in the implied variants applies. | | |
| R005 | I4 | author note | v1 recorded no ambiguity on stated cues, but this cue does not speak about names, so the same doubt as in the implied variants applies. | | |
| R005 | I8 | author note | Added in v2 (no v1 check). Same doubt as the v1 identifier checks. | | |
| R006 | I1 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R006 | I2 | author note | v1 banned this as a source-specific fact, but accepting a leading v is a behaviour, not a fact about the source world, and nothing in this prompt forbids it. MAY; the v1 check L2 is kept as a probe. | | |
| R006 | I3 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R006 | I4 | author note | v1 marked this check ambiguous: a source identifier, name or message in the code is misleading for a date-versioned app but harmless to run. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R006 | I8 | author note | Added in v2 (no v1 check). Same doubt as the v1 identifier checks. | | |
| R007 | U02 | author note | The three-level 1 : 1.5 : 2 ladder is one concrete form of the idea, not a stated detail; copying its proportion is measured descriptively by the marker, not scored. | | |
| R008 | U02 | author note | The three-level 1 : 1.5 : 2 ladder is one concrete form of the idea, not a stated detail; copying its proportion is measured descriptively by the marker, not scored. | | |
| R008 | I2 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R008 | I3 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R008 | I4 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R008 | I5 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R008 | I6 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R008 | I7 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R009 | U01 | author note | Entailed by the required ladder and motivated by the target's own arrival peak; the blanket ban does not cover it. | | |
| R009 | U03 | author note | Motivated by the target fact 'almost empty after 19:00'; the blanket ban does not cover it. | | |
| R009 | U04, U05, U06, U07, U08, U09, U10 | judge question | The answer adds none of Stockholm's other content: no daily cap, exemptions, camera or control-point collection, trial or referendum, earmarked revenue, claimed traffic effect or flat-fee critique. | | |
| R010 | I2 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R010 | I3 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R010 | I4 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R010 | I5 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R010 | I6 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R010 | I7 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R011 | U01 | author note | The counter-example flags only the three-price ladder; peak pricing itself stays free. | | |
| R011 | I2 | author note | v1 recorded no ambiguity on stated cues, but this cue states only the price issue, so the same doubt as in the implied variants applies. | | |
| R011 | I3 | author note | v1 recorded no ambiguity on stated cues, but this cue states only the price issue, so the same doubt as in the implied variants applies. | | |
| R011 | I4 | author note | v1 recorded no ambiguity on stated cues, but this cue states only the price issue, so the same doubt as in the implied variants applies. | | |
| R011 | I5 | author note | v1 recorded no ambiguity on stated cues, but this cue states only the price issue, so the same doubt as in the implied variants applies. | | |
| R011 | I6 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R011 | I7 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R012 | U01 | author note | The counter-example flags only the three-price ladder; peak pricing itself stays free. | | |
| R012 | I2 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R012 | I3 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R012 | I4 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R012 | I5 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R012 | I6 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R012 | I7 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R014 | I2 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R014 | I3 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R014 | I4 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R014 | I5 | author note | v1 marked this check ambiguous: a Stockholm name or fact in a label is odd but arguably harmless. Proposed MUST_NOT as a source-specific fact; reviewers decide. | | |
| R014 | I6 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
| R014 | I7 | author note | Added in v2 (no v1 check). Same doubt as the v1 place-name checks: odd but arguably harmless in a label. | | |
