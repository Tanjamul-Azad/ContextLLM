# Independent review v2: reviewer A

Do not open the other review, any seed JSON, Part 2 or the researcher manifest before both Part 1 reviews are submitted.
Each block is the COMPLETE single-turn model prompt, including variant-specific rules and output format.
Answer from this prompt only. A source detail being unnecessary does not automatically make it prohibited.

Label every unit listed under the prompt with exactly one of:
- MUST: an answer that does not use this unit fails the user's request.
- MUST_NOT: an answer that uses this unit fails the user's request.
- MAY: using it or not using it never makes an answer wrong (permitted but optional).
- UNCLEAR: the prompt does not let you decide between two of these labels.
After the label write a semicolon, the shortest prompt phrase that carries the instruction (outside the example),
a semicolon, and DIRECT (an instruction or rule covers the unit) or INFERRED (you reasoned from the role).
Leave the evidence out for MAY when nothing in the prompt speaks to the unit. Do not invent a quotation.
Do not force a unique role when the prompt is genuinely ambiguous (write mixed or unclear).
Record any prior exposure. The author of a card cannot count as an independent blind reviewer of that card.
Related prompts can occur in this pack; judge each on its own. Repeated variants are not independent seeds.

## R013

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT. University policy (Board decision 2025/14) requires one flat fee per entry at all hours.

When I read about Stockholm I wondered whether our car park could learn from it. Borrow the idea, not its details: our fees, periods and rules come from our own situation.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"
- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"
- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U04:
  - U05:
  - I1:
  - U09:
  - U02:
  - I3:
  - I6:
  - U08:
  - U07:
  - I2:
  - I7:
  - U03:
  - I5:
  - U10:
  - U01:
  - U06:
  - I4:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R002

<!-- BEGIN EXACT PROMPT -->
Our field-survey app is versioned by date as YEAR.MONTH.PATCH, for example 2026.11.3. A hotfix is published as the base version plus -hotfixN, for example 2026.11.3-hotfix2. Our CI may append +ci.N to any version, for example 2026.11.3+ci.41. Write a Python function is_newer(a, b) that returns True if version a is newer than version b.
Rules: Use only the standard library; the only allowed import is re. A -hotfixN version is newer than its base version, and a higher N is newer. Equal versions are not newer than each other. is_newer must accept every version form described above, return True or False and never raise an error for them.

Our old library used the comparator below:

Semantic Versioning 2.0.0, published at semver.org, defines how version numbers like 1.4.2 are compared. A version has MAJOR, MINOR and PATCH numbers, and they are compared numerically from left to right, so 1.10.0 is newer than 1.9.0. A version may carry a pre-release tag after a hyphen, such as 1.4.2-rc.1. A pre-release version has lower precedence than the normal version, so 1.4.2-rc.1 comes before 1.4.2. Pre-release tags are compared part by part, numbers as numbers and words in ASCII order. Build metadata after a plus sign, such as 1.4.2+build.7, must be ignored when determining precedence. So 1.4.2+build.7 and 1.4.2+build.8 have the same precedence. Many teams also strip a leading v, as in v1.4.2, before parsing. The functions below are the comparator our release tooling used for a library we published on PyPI. They raise ValueError for anything that does not look like a semantic version.

```python
import functools
import re

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def _key(v):
    m = SEMVER.match(v)
    if not m:
        raise ValueError(f"not a semantic version: {v}")
    major, minor, patch, pre = m.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return core, (1,)  # a release outranks any pre-release
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core, (0,) + parts


def compare_semver(a, b):
    ka, kb = _key(a), _key(b)
    return (ka > kb) - (ka < kb)


def sort_versions(versions):
    return sorted(versions, key=functools.cmp_to_key(compare_semver))
```

The app needs one too.

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U02 (idea): A suffix after a hyphen is parsed as a separate tag  | in the example: "A version may carry a pre-release tag after a hyphen, such as 1.4.2..."; "(?:-([0-9A-Za-z.-]+))?"
- U05 (idea): Build metadata after a plus sign is ignored for ordering  | in the example: "Build metadata after a plus sign, such as 1.4.2+build.7, must be ig..."; "(?:\+[0-9A-Za-z.-]+)?"
- I4 (surface item): The error message  | in the example: "semantic version"; "not a semantic version"
- I5 (surface item): Sorting helper with cmp_to_key  | in the example: "sort_versions"; "cmp_to_key"
- I8 (surface item): The name of the standard, Semantic Versioning  | in the example: "Semantic Versioning 2.0.0"
- I7 (surface item): The functools import  | in the example: "import functools"; "functools"
- U01 (idea): Split the version into numeric parts and compare them as numbers, left to right  | in the example: "A version has MAJOR, MINOR and PATCH numbers, and they are compared..."; "(\d+)\.(\d+)\.(\d+)"; "core = (int(major), int(minor), int(patch))"
- U08 (idea): A sorting helper built on the comparator  | in the example: "(versions): return sorted(versions, key="
- U04 (idea): Tag parts are compared one by one, numbers as numbers  | in the example: "Pre-release tags are compared part by part, numbers as numbers and ..."; "parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p i..."
- I1 (surface item): Published on PyPI  | in the example: "PyPI"
- U07 (idea): Input that does not match the format raises an error  | in the example: "They raise ValueError for anything that does not look like a"; "if not m: raise ValueError(f""; ": {v}")"
- U03 (idea): A version with a hyphen tag ranks below the plain version (pre-release precedence)  | in the example: "A pre-release version has lower precedence than the normal version,..."; "if pre is None: return core, (1,) # a release outranks any pre-release"; "return core, (0,) + parts"
- I3 (surface item): semver naming  | in the example: "semver.org"; "SEMVER"; "compare_semver"
- I2 (surface item): Leading v is stripped  | in the example: "^v?"
- U06 (idea): A leading v is accepted and stripped before parsing  | in the example: "Many teams also strip a leading v, as in v1.4.2, before parsing."

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U02:
  - U05:
  - I4:
  - I5:
  - I8:
  - I7:
  - U01:
  - U08:
  - U04:
  - I1:
  - U07:
  - U03:
  - I3:
  - I2:
  - U06:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R014

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT. University policy (Board decision 2025/14) requires one flat fee per entry at all hours.

I came across this while reading about how cities manage traffic, and I keep thinking about our car park:

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

What would make sense for us?

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."
- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U03:
  - U02:
  - I4:
  - U08:
  - I3:
  - I7:
  - U05:
  - U09:
  - U07:
  - U10:
  - U04:
  - I5:
  - I6:
  - I1:
  - U06:
  - I2:
  - U01:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R004

<!-- BEGIN EXACT PROMPT -->
Our field-survey app is versioned by date as YEAR.MONTH.PATCH, for example 2026.11.3. A hotfix is published as the base version plus -hotfixN, for example 2026.11.3-hotfix2. Our CI may append +ci.N to any version, for example 2026.11.3+ci.41. Write a Python function is_newer(a, b) that returns True if version a is newer than version b.
Rules: Use only the standard library; the only allowed import is re. A -hotfixN version is newer than its base version, and a higher N is newer. Equal versions are not newer than each other. is_newer must accept every version form described above, return True or False and never raise an error for them.

Our CI adds +ci.N as the build-metadata part of the spec below allows, and our update server already treats such builds the way the spec says.

Semantic Versioning 2.0.0, published at semver.org, defines how version numbers like 1.4.2 are compared. A version has MAJOR, MINOR and PATCH numbers, and they are compared numerically from left to right, so 1.10.0 is newer than 1.9.0. A version may carry a pre-release tag after a hyphen, such as 1.4.2-rc.1. A pre-release version has lower precedence than the normal version, so 1.4.2-rc.1 comes before 1.4.2. Pre-release tags are compared part by part, numbers as numbers and words in ASCII order. Build metadata after a plus sign, such as 1.4.2+build.7, must be ignored when determining precedence. So 1.4.2+build.7 and 1.4.2+build.8 have the same precedence. Many teams also strip a leading v, as in v1.4.2, before parsing. The functions below are the comparator our release tooling used for a library we published on PyPI. They raise ValueError for anything that does not look like a semantic version.

```python
import functools
import re

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def _key(v):
    m = SEMVER.match(v)
    if not m:
        raise ValueError(f"not a semantic version: {v}")
    major, minor, patch, pre = m.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return core, (1,)  # a release outranks any pre-release
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core, (0,) + parts


def compare_semver(a, b):
    ka, kb = _key(a), _key(b)
    return (ka > kb) - (ka < kb)


def sort_versions(versions):
    return sorted(versions, key=functools.cmp_to_key(compare_semver))
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U01 (idea): Split the version into numeric parts and compare them as numbers, left to right  | in the example: "A version has MAJOR, MINOR and PATCH numbers, and they are compared..."; "(\d+)\.(\d+)\.(\d+)"; "core = (int(major), int(minor), int(patch))"
- U03 (idea): A version with a hyphen tag ranks below the plain version (pre-release precedence)  | in the example: "A pre-release version has lower precedence than the normal version,..."; "if pre is None: return core, (1,) # a release outranks any pre-release"; "return core, (0,) + parts"
- U07 (idea): Input that does not match the format raises an error  | in the example: "They raise ValueError for anything that does not look like a"; "if not m: raise ValueError(f""; ": {v}")"
- I5 (surface item): Sorting helper with cmp_to_key  | in the example: "sort_versions"; "cmp_to_key"
- U08 (idea): A sorting helper built on the comparator  | in the example: "(versions): return sorted(versions, key="
- U05 (idea): Build metadata after a plus sign is ignored for ordering  | in the example: "Build metadata after a plus sign, such as 1.4.2+build.7, must be ig..."; "(?:\+[0-9A-Za-z.-]+)?"
- I4 (surface item): The error message  | in the example: "semantic version"; "not a semantic version"
- I3 (surface item): semver naming  | in the example: "semver.org"; "SEMVER"; "compare_semver"
- U02 (idea): A suffix after a hyphen is parsed as a separate tag  | in the example: "A version may carry a pre-release tag after a hyphen, such as 1.4.2..."; "(?:-([0-9A-Za-z.-]+))?"
- I7 (surface item): The functools import  | in the example: "import functools"; "functools"
- U04 (idea): Tag parts are compared one by one, numbers as numbers  | in the example: "Pre-release tags are compared part by part, numbers as numbers and ..."; "parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p i..."
- I8 (surface item): The name of the standard, Semantic Versioning  | in the example: "Semantic Versioning 2.0.0"
- I1 (surface item): Published on PyPI  | in the example: "PyPI"
- U06 (idea): A leading v is accepted and stripped before parsing  | in the example: "Many teams also strip a leading v, as in v1.4.2, before parsing."
- I2 (surface item): Leading v is stripped  | in the example: "^v?"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U01:
  - U03:
  - U07:
  - I5:
  - U08:
  - U05:
  - I4:
  - I3:
  - U02:
  - I7:
  - U04:
  - I8:
  - I1:
  - U06:
  - I2:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R012

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

A neighbouring university copied the Stockholm scheme below for its car park last year. Its drivers complained that they could never remember which of the three prices applied at what time.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."
- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."
- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U10:
  - U05:
  - U08:
  - I6:
  - U07:
  - I4:
  - I7:
  - I2:
  - U02:
  - U09:
  - U06:
  - I3:
  - U03:
  - I5:
  - U04:
  - U01:
  - I1:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R005

<!-- BEGIN EXACT PROMPT -->
Our field-survey app is versioned by date as YEAR.MONTH.PATCH, for example 2026.11.3. A hotfix is published as the base version plus -hotfixN, for example 2026.11.3-hotfix2. Our CI may append +ci.N to any version, for example 2026.11.3+ci.41. Write a Python function is_newer(a, b) that returns True if version a is newer than version b.
Rules: Use only the standard library; the only allowed import is re. A -hotfixN version is newer than its base version, and a higher N is newer. Equal versions are not newer than each other. is_newer must accept every version form described above, return True or False and never raise an error for them.

Our first updater used the comparator below and ignored the +ci.N part, so devices never installed rebuilt versions. Don't do it like this: a higher ci number must count as newer.

Semantic Versioning 2.0.0, published at semver.org, defines how version numbers like 1.4.2 are compared. A version has MAJOR, MINOR and PATCH numbers, and they are compared numerically from left to right, so 1.10.0 is newer than 1.9.0. A version may carry a pre-release tag after a hyphen, such as 1.4.2-rc.1. A pre-release version has lower precedence than the normal version, so 1.4.2-rc.1 comes before 1.4.2. Pre-release tags are compared part by part, numbers as numbers and words in ASCII order. Build metadata after a plus sign, such as 1.4.2+build.7, must be ignored when determining precedence. So 1.4.2+build.7 and 1.4.2+build.8 have the same precedence. Many teams also strip a leading v, as in v1.4.2, before parsing. The functions below are the comparator our release tooling used for a library we published on PyPI. They raise ValueError for anything that does not look like a semantic version.

```python
import functools
import re

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def _key(v):
    m = SEMVER.match(v)
    if not m:
        raise ValueError(f"not a semantic version: {v}")
    major, minor, patch, pre = m.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return core, (1,)  # a release outranks any pre-release
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core, (0,) + parts


def compare_semver(a, b):
    ka, kb = _key(a), _key(b)
    return (ka > kb) - (ka < kb)


def sort_versions(versions):
    return sorted(versions, key=functools.cmp_to_key(compare_semver))
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U06 (idea): A leading v is accepted and stripped before parsing  | in the example: "Many teams also strip a leading v, as in v1.4.2, before parsing."
- U01 (idea): Split the version into numeric parts and compare them as numbers, left to right  | in the example: "A version has MAJOR, MINOR and PATCH numbers, and they are compared..."; "(\d+)\.(\d+)\.(\d+)"; "core = (int(major), int(minor), int(patch))"
- I2 (surface item): Leading v is stripped  | in the example: "^v?"
- I8 (surface item): The name of the standard, Semantic Versioning  | in the example: "Semantic Versioning 2.0.0"
- U02 (idea): A suffix after a hyphen is parsed as a separate tag  | in the example: "A version may carry a pre-release tag after a hyphen, such as 1.4.2..."; "(?:-([0-9A-Za-z.-]+))?"
- I5 (surface item): Sorting helper with cmp_to_key  | in the example: "sort_versions"; "cmp_to_key"
- U08 (idea): A sorting helper built on the comparator  | in the example: "(versions): return sorted(versions, key="
- U05 (idea): Build metadata after a plus sign is ignored for ordering  | in the example: "Build metadata after a plus sign, such as 1.4.2+build.7, must be ig..."; "(?:\+[0-9A-Za-z.-]+)?"
- I4 (surface item): The error message  | in the example: "semantic version"; "not a semantic version"
- U03 (idea): A version with a hyphen tag ranks below the plain version (pre-release precedence)  | in the example: "A pre-release version has lower precedence than the normal version,..."; "if pre is None: return core, (1,) # a release outranks any pre-release"; "return core, (0,) + parts"
- I1 (surface item): Published on PyPI  | in the example: "PyPI"
- U04 (idea): Tag parts are compared one by one, numbers as numbers  | in the example: "Pre-release tags are compared part by part, numbers as numbers and ..."; "parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p i..."
- I7 (surface item): The functools import  | in the example: "import functools"; "functools"
- I3 (surface item): semver naming  | in the example: "semver.org"; "SEMVER"; "compare_semver"
- U07 (idea): Input that does not match the format raises an error  | in the example: "They raise ValueError for anything that does not look like a"; "if not m: raise ValueError(f""; ": {v}")"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U06:
  - U01:
  - I2:
  - I8:
  - U02:
  - I5:
  - U08:
  - U05:
  - I4:
  - U03:
  - I1:
  - U04:
  - I7:
  - I3:
  - U07:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R006

<!-- BEGIN EXACT PROMPT -->
Our field-survey app is versioned by date as YEAR.MONTH.PATCH, for example 2026.11.3. A hotfix is published as the base version plus -hotfixN, for example 2026.11.3-hotfix2. Our CI may append +ci.N to any version, for example 2026.11.3+ci.41. Write a Python function is_newer(a, b) that returns True if version a is newer than version b.
Rules: Use only the standard library; the only allowed import is re. A -hotfixN version is newer than its base version, and a higher N is newer. Equal versions are not newer than each other. is_newer must accept every version form described above, return True or False and never raise an error for them.

Our first updater used the comparator below, and because of how it treated the +ci.N part, devices never installed rebuilt versions.

Semantic Versioning 2.0.0, published at semver.org, defines how version numbers like 1.4.2 are compared. A version has MAJOR, MINOR and PATCH numbers, and they are compared numerically from left to right, so 1.10.0 is newer than 1.9.0. A version may carry a pre-release tag after a hyphen, such as 1.4.2-rc.1. A pre-release version has lower precedence than the normal version, so 1.4.2-rc.1 comes before 1.4.2. Pre-release tags are compared part by part, numbers as numbers and words in ASCII order. Build metadata after a plus sign, such as 1.4.2+build.7, must be ignored when determining precedence. So 1.4.2+build.7 and 1.4.2+build.8 have the same precedence. Many teams also strip a leading v, as in v1.4.2, before parsing. The functions below are the comparator our release tooling used for a library we published on PyPI. They raise ValueError for anything that does not look like a semantic version.

```python
import functools
import re

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def _key(v):
    m = SEMVER.match(v)
    if not m:
        raise ValueError(f"not a semantic version: {v}")
    major, minor, patch, pre = m.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return core, (1,)  # a release outranks any pre-release
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core, (0,) + parts


def compare_semver(a, b):
    ka, kb = _key(a), _key(b)
    return (ka > kb) - (ka < kb)


def sort_versions(versions):
    return sorted(versions, key=functools.cmp_to_key(compare_semver))
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- I7 (surface item): The functools import  | in the example: "import functools"; "functools"
- U08 (idea): A sorting helper built on the comparator  | in the example: "(versions): return sorted(versions, key="
- I2 (surface item): Leading v is stripped  | in the example: "^v?"
- U01 (idea): Split the version into numeric parts and compare them as numbers, left to right  | in the example: "A version has MAJOR, MINOR and PATCH numbers, and they are compared..."; "(\d+)\.(\d+)\.(\d+)"; "core = (int(major), int(minor), int(patch))"
- U06 (idea): A leading v is accepted and stripped before parsing  | in the example: "Many teams also strip a leading v, as in v1.4.2, before parsing."
- I4 (surface item): The error message  | in the example: "semantic version"; "not a semantic version"
- I5 (surface item): Sorting helper with cmp_to_key  | in the example: "sort_versions"; "cmp_to_key"
- I1 (surface item): Published on PyPI  | in the example: "PyPI"
- U03 (idea): A version with a hyphen tag ranks below the plain version (pre-release precedence)  | in the example: "A pre-release version has lower precedence than the normal version,..."; "if pre is None: return core, (1,) # a release outranks any pre-release"; "return core, (0,) + parts"
- U05 (idea): Build metadata after a plus sign is ignored for ordering  | in the example: "Build metadata after a plus sign, such as 1.4.2+build.7, must be ig..."; "(?:\+[0-9A-Za-z.-]+)?"
- I8 (surface item): The name of the standard, Semantic Versioning  | in the example: "Semantic Versioning 2.0.0"
- U07 (idea): Input that does not match the format raises an error  | in the example: "They raise ValueError for anything that does not look like a"; "if not m: raise ValueError(f""; ": {v}")"
- U02 (idea): A suffix after a hyphen is parsed as a separate tag  | in the example: "A version may carry a pre-release tag after a hyphen, such as 1.4.2..."; "(?:-([0-9A-Za-z.-]+))?"
- I3 (surface item): semver naming  | in the example: "semver.org"; "SEMVER"; "compare_semver"
- U04 (idea): Tag parts are compared one by one, numbers as numbers  | in the example: "Pre-release tags are compared part by part, numbers as numbers and ..."; "parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p i..."

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - I7:
  - U08:
  - I2:
  - U01:
  - U06:
  - I4:
  - I5:
  - I1:
  - U03:
  - U05:
  - I8:
  - U07:
  - U02:
  - I3:
  - U04:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R003

<!-- BEGIN EXACT PROMPT -->
Our field-survey app is versioned by date as YEAR.MONTH.PATCH, for example 2026.11.3. A hotfix is published as the base version plus -hotfixN, for example 2026.11.3-hotfix2. Our CI may append +ci.N to any version, for example 2026.11.3+ci.41. Write a Python function is_newer(a, b) that returns True if version a is newer than version b.
Rules: Use only the standard library; the only allowed import is re. A -hotfixN version is newer than its base version, and a higher N is newer. Equal versions are not newer than each other. is_newer must accept every version form described above, return True or False and never raise an error for them.

Keep exactly one rule from the comparator below: build metadata after a plus sign is ignored, so 2026.11.3+ci.41 and 2026.11.3+ci.42 are equally new. Everything else follows our rules above.

Semantic Versioning 2.0.0, published at semver.org, defines how version numbers like 1.4.2 are compared. A version has MAJOR, MINOR and PATCH numbers, and they are compared numerically from left to right, so 1.10.0 is newer than 1.9.0. A version may carry a pre-release tag after a hyphen, such as 1.4.2-rc.1. A pre-release version has lower precedence than the normal version, so 1.4.2-rc.1 comes before 1.4.2. Pre-release tags are compared part by part, numbers as numbers and words in ASCII order. Build metadata after a plus sign, such as 1.4.2+build.7, must be ignored when determining precedence. So 1.4.2+build.7 and 1.4.2+build.8 have the same precedence. Many teams also strip a leading v, as in v1.4.2, before parsing. The functions below are the comparator our release tooling used for a library we published on PyPI. They raise ValueError for anything that does not look like a semantic version.

```python
import functools
import re

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def _key(v):
    m = SEMVER.match(v)
    if not m:
        raise ValueError(f"not a semantic version: {v}")
    major, minor, patch, pre = m.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return core, (1,)  # a release outranks any pre-release
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core, (0,) + parts


def compare_semver(a, b):
    ka, kb = _key(a), _key(b)
    return (ka > kb) - (ka < kb)


def sort_versions(versions):
    return sorted(versions, key=functools.cmp_to_key(compare_semver))
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- I8 (surface item): The name of the standard, Semantic Versioning  | in the example: "Semantic Versioning 2.0.0"
- U01 (idea): Split the version into numeric parts and compare them as numbers, left to right  | in the example: "A version has MAJOR, MINOR and PATCH numbers, and they are compared..."; "(\d+)\.(\d+)\.(\d+)"; "core = (int(major), int(minor), int(patch))"
- U03 (idea): A version with a hyphen tag ranks below the plain version (pre-release precedence)  | in the example: "A pre-release version has lower precedence than the normal version,..."; "if pre is None: return core, (1,) # a release outranks any pre-release"; "return core, (0,) + parts"
- U08 (idea): A sorting helper built on the comparator  | in the example: "(versions): return sorted(versions, key="
- I1 (surface item): Published on PyPI  | in the example: "PyPI"
- I3 (surface item): semver naming  | in the example: "semver.org"; "SEMVER"; "compare_semver"
- I2 (surface item): Leading v is stripped  | in the example: "^v?"
- U07 (idea): Input that does not match the format raises an error  | in the example: "They raise ValueError for anything that does not look like a"; "if not m: raise ValueError(f""; ": {v}")"
- I7 (surface item): The functools import  | in the example: "import functools"; "functools"
- U06 (idea): A leading v is accepted and stripped before parsing  | in the example: "Many teams also strip a leading v, as in v1.4.2, before parsing."
- U05 (idea): Build metadata after a plus sign is ignored for ordering  | in the example: "Build metadata after a plus sign, such as 1.4.2+build.7, must be ig..."; "(?:\+[0-9A-Za-z.-]+)?"
- I5 (surface item): Sorting helper with cmp_to_key  | in the example: "sort_versions"; "cmp_to_key"
- U02 (idea): A suffix after a hyphen is parsed as a separate tag  | in the example: "A version may carry a pre-release tag after a hyphen, such as 1.4.2..."; "(?:-([0-9A-Za-z.-]+))?"
- U04 (idea): Tag parts are compared one by one, numbers as numbers  | in the example: "Pre-release tags are compared part by part, numbers as numbers and ..."; "parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p i..."
- I4 (surface item): The error message  | in the example: "semantic version"; "not a semantic version"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - I8:
  - U01:
  - U03:
  - U08:
  - I1:
  - I3:
  - I2:
  - U07:
  - I7:
  - U06:
  - U05:
  - I5:
  - U02:
  - U04:
  - I4:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R007

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

When I read about Stockholm I wondered whether our car park could learn from it. Borrow the idea, not its details: our fees, periods and rules come from our own situation.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."
- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U01:
  - U07:
  - I3:
  - I5:
  - U10:
  - U05:
  - U06:
  - U09:
  - U02:
  - U03:
  - U04:
  - I7:
  - I2:
  - I4:
  - I6:
  - I1:
  - U08:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R011

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

A neighbouring university copied the Stockholm scheme below for its car park. Drivers said they could never remember which of the three prices applied at what time. Don't do it like this: keep the schedule simple enough that people remember it.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."
- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"
- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"
- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U09:
  - I7:
  - I4:
  - U06:
  - U01:
  - U10:
  - U03:
  - I2:
  - I3:
  - U05:
  - U07:
  - I5:
  - I6:
  - U02:
  - U08:
  - I1:
  - U04:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R009

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

The finance committee has already approved Stockholm's price ladder for us, so the schedule must use the same ladder: three charged levels in the ratio 1 : 1.5 : 2. Everything else must fit our own rules; do not copy anything else from Stockholm.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"
- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."
- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U09:
  - U05:
  - U01:
  - U02:
  - I3:
  - I4:
  - I6:
  - I1:
  - U03:
  - I5:
  - I2:
  - U06:
  - I7:
  - U04:
  - U10:
  - U07:
  - U08:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R008

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

I came across this while reading about how cities manage traffic, and I keep thinking about our car park:

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

What would make sense for us?

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"
- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."
- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"
- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - U07:
  - I6:
  - I2:
  - I3:
  - U08:
  - U09:
  - U02:
  - U03:
  - I5:
  - U01:
  - I1:
  - U04:
  - U05:
  - I7:
  - U06:
  - U10:
  - I4:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R001

<!-- BEGIN EXACT PROMPT -->
Our field-survey app is versioned by date as YEAR.MONTH.PATCH, for example 2026.11.3. A hotfix is published as the base version plus -hotfixN, for example 2026.11.3-hotfix2. Our CI may append +ci.N to any version, for example 2026.11.3+ci.41. Write a Python function is_newer(a, b) that returns True if version a is newer than version b.
Rules: Use only the standard library; the only allowed import is re. A -hotfixN version is newer than its base version, and a higher N is newer. Equal versions are not newer than each other. is_newer must accept every version form described above, return True or False and never raise an error for them.

Our old library used the comparator below. Borrow the idea for the app, not its details; our version rules are the ones above.

Semantic Versioning 2.0.0, published at semver.org, defines how version numbers like 1.4.2 are compared. A version has MAJOR, MINOR and PATCH numbers, and they are compared numerically from left to right, so 1.10.0 is newer than 1.9.0. A version may carry a pre-release tag after a hyphen, such as 1.4.2-rc.1. A pre-release version has lower precedence than the normal version, so 1.4.2-rc.1 comes before 1.4.2. Pre-release tags are compared part by part, numbers as numbers and words in ASCII order. Build metadata after a plus sign, such as 1.4.2+build.7, must be ignored when determining precedence. So 1.4.2+build.7 and 1.4.2+build.8 have the same precedence. Many teams also strip a leading v, as in v1.4.2, before parsing. The functions below are the comparator our release tooling used for a library we published on PyPI. They raise ValueError for anything that does not look like a semantic version.

```python
import functools
import re

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$")


def _key(v):
    m = SEMVER.match(v)
    if not m:
        raise ValueError(f"not a semantic version: {v}")
    major, minor, patch, pre = m.groups()
    core = (int(major), int(minor), int(patch))
    if pre is None:
        return core, (1,)  # a release outranks any pre-release
    parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
    return core, (0,) + parts


def compare_semver(a, b):
    ka, kb = _key(a), _key(b)
    return (ka > kb) - (ka < kb)


def sort_versions(versions):
    return sorted(versions, key=functools.cmp_to_key(compare_semver))
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- I2 (surface item): Leading v is stripped  | in the example: "^v?"
- I3 (surface item): semver naming  | in the example: "semver.org"; "SEMVER"; "compare_semver"
- I8 (surface item): The name of the standard, Semantic Versioning  | in the example: "Semantic Versioning 2.0.0"
- U04 (idea): Tag parts are compared one by one, numbers as numbers  | in the example: "Pre-release tags are compared part by part, numbers as numbers and ..."; "parts = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p i..."
- U01 (idea): Split the version into numeric parts and compare them as numbers, left to right  | in the example: "A version has MAJOR, MINOR and PATCH numbers, and they are compared..."; "(\d+)\.(\d+)\.(\d+)"; "core = (int(major), int(minor), int(patch))"
- I7 (surface item): The functools import  | in the example: "import functools"; "functools"
- U05 (idea): Build metadata after a plus sign is ignored for ordering  | in the example: "Build metadata after a plus sign, such as 1.4.2+build.7, must be ig..."; "(?:\+[0-9A-Za-z.-]+)?"
- U08 (idea): A sorting helper built on the comparator  | in the example: "(versions): return sorted(versions, key="
- U06 (idea): A leading v is accepted and stripped before parsing  | in the example: "Many teams also strip a leading v, as in v1.4.2, before parsing."
- I4 (surface item): The error message  | in the example: "semantic version"; "not a semantic version"
- U07 (idea): Input that does not match the format raises an error  | in the example: "They raise ValueError for anything that does not look like a"; "if not m: raise ValueError(f""; ": {v}")"
- I1 (surface item): Published on PyPI  | in the example: "PyPI"
- I5 (surface item): Sorting helper with cmp_to_key  | in the example: "sort_versions"; "cmp_to_key"
- U02 (idea): A suffix after a hyphen is parsed as a separate tag  | in the example: "A version may carry a pre-release tag after a hyphen, such as 1.4.2..."; "(?:-([0-9A-Za-z.-]+))?"
- U03 (idea): A version with a hyphen tag ranks below the plain version (pre-release precedence)  | in the example: "A pre-release version has lower precedence than the normal version,..."; "if pre is None: return core, (1,) # a release outranks any pre-release"; "return core, (0,) + parts"

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - I2:
  - I3:
  - I8:
  - U04:
  - U01:
  - I7:
  - U05:
  - U08:
  - U06:
  - I4:
  - U07:
  - I1:
  - I5:
  - U02:
  - U03:
- UNCLEAR / conflicting requirements:
- Review time in minutes:

## R010

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

The finance committee has already approved the price ladder of the Stockholm scheme below for our car park, and the meter vendor has programmed those three price steps.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

Units of the example (label each one below):

- I1 (surface item): Prices in Swedish kronor (SEK)  | in the example: "Swedish kronor (SEK)"; "SEK"
- U10 (idea): Criticism: running cost of the cameras; would a flat fee have done  | in the example: "Critics pointed to the cost of running the camera system and asked ..."
- U02 (idea): Three charged levels (busiest, shoulder, rest) in proportion 10 : 15 : 20, top price double the bottom  | in the example: "A passage in the busiest half hours cost 20"; ", the shoulder periods around them cost 15"; ", and the remaining daytime periods cost 10"
- U06 (idea): Exemptions for a through route and for residents with no other road link  | in the example: "The through route"; "was exempt at first, because it was the main bypass around the centre."; "Residents of the island of"
- U05 (idea): Reported effect: traffic and queues fell, and the fall lasted  | in the example: "Traffic across the cordon fell by about"; "compared with the year before, and queues on the main approach road..."; "Later evaluations found that the traffic reduction lasted for years..."
- U01 (idea): Price follows demand: charge more at the peak and less when demand is low, so people shift their timing  | in the example: "The price depended on the time of day."; "Planners explained the result simply: drivers who could move their ..."; "Researchers have used the case to argue that a price which follows ..."
- U07 (idea): Automatic collection at control points with number-plate cameras  | in the example: "The charge was collected at"; "on the roads into and out of the inner city."; "Cameras read each car's number plate, so drivers did not have to stop."
- I3 (surface item): Lidingö residents' exemption  | in the example: "Lidingö"
- I5 (surface item): The 2006 referendum  | in the example: "referendum"
- I2 (surface item): Essingeleden bypass exemption  | in the example: "Essingeleden"
- U04 (idea): A daily cap on what one driver pays  | in the example: "A driver paid at most 60"; "in one day, however often they crossed the cordon."; "It also shows that a daily cap protects people who must cross the c..."
- I7 (surface item): Measured traffic reduction of about 20 percent  | in the example: "20 percent"
- I4 (surface item): 18 control points with number-plate cameras  | in the example: "18 control points"
- U03 (idea): No charge in the evening, at night, at weekends and on holidays  | in the example: "No charge applied in the evening, at night, at weekends or on publi..."
- U08 (idea): Staged introduction: trial, referendum, permanent scheme, support rising after the trial, later price rise  | in the example: "Stockholm ran congestion charges as a full-scale trial from"; "to"; "After a"
- I6 (surface item): Trial, referendum and price-change dates  | in the example: "3 January"; "31 July 2006"; "September 2006"
- U09 (idea): Revenue earmarked for transport investment  | in the example: "The revenue was earmarked for transport investment in the Stockholm..."

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- Realism of this complete prompt (1-5):
- Realism reason:
- Licence (one line per unit: LABEL ; evidence quote ; DIRECT or INFERRED):
  - I1:
  - U10:
  - U02:
  - U06:
  - U05:
  - U01:
  - U07:
  - I3:
  - I5:
  - I2:
  - U04:
  - I7:
  - I4:
  - U03:
  - U08:
  - I6:
  - U09:
- UNCLEAR / conflicting requirements:
- Review time in minutes:
