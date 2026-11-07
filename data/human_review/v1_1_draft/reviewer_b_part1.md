# Independent review v1.1: reviewer B

Do not open the other review, seed JSON, Part 2 or researcher manifest before both Part 1 reviews are submitted.
Each block is the COMPLETE single-turn model prompt, including variant-specific rules and output format.
Answer from this prompt only. A source detail being unnecessary does not automatically make it prohibited.
MAY USE means permitted but optional; UNCLEAR means the prompt does not determine the answer.
For each scope item, quote prompt evidence and mark DIRECT or INFERRED. Explain inferred mappings briefly.
For omitted details, do not invent a quotation or treat omission alone as a prohibition.
Write 'none' where appropriate. Do not force a unique role when the prompt is genuinely ambiguous.
Record any prior exposure. The author of a seed cannot count as an independent blind reviewer of that seed.
Related prompts can occur in this pack; judge each on its own. Repeated variants are not independent seeds.

## R031

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

When I read about Stockholm I wondered whether our car park could learn from it. Borrow the idea, not its details: our fees, periods and rules come from our own situation.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
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

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R014

<!-- BEGIN EXACT PROMPT -->
Our solar mini-grid cooperative in Sunamganj publishes a tariff index. It starts at a given value and changes by a percentage after every meter-reading batch, about 40 times a day. Write a Python function update_index(start, changes) that applies the percentage changes in order and returns the list of index values after each change.
Rules: A change of 1.0 means the index rises by 1 percent; return one value per change, in order. Each returned value has at most 3 decimal places.

The cooperative's founding bylaws copied their index rule word for word from the 1982 rule below, and the auditors check every published value against it.

In January 1982 the Vancouver Stock Exchange launched a new stock index with a starting value of 1000.000. The index was recalculated after every trade, about 3,000 times a day. Each time, the new value was cut to three decimal places instead of being rounded. Cutting off digits always pushes the value down, by about half of the last digit on average. The loss was tiny for one trade, but it added up over thousands of trades a day. By November 1983 the index stood near 524.811, although the market had not fallen anything like that much. Consultants traced the problem, and the exchange recalculated the index from the original prices. Overnight the corrected index stood at about 1098.892. The case is often cited in numerical-analysis teaching as a warning about repeated truncation. The code below reproduces the original update rule.

```python
import math


def next_index(index, pct_change):
    """Vancouver-style update: apply one change, then cut to 3 decimals."""
    raw = index * (1 + pct_change / 100)
    return math.floor(raw * 1000) / 1000


def run_day(index, changes):
    for c in changes:
        index = next_index(index, c)
    return index
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R045

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day. University data policy: reminder messages must not mention how other students behave.

A friend who works in public policy sent me this. Borrow the idea for our reminders, not its details; our numbers and wording must come from our own library.

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R018

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share.

Our web team showed me the function below when I asked how they spread work across machines:

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
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

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R048

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender.

Our department head keeps telling us this story whenever we discuss the kit losses:

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R047

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender.

Our department head suggested we learn from the microfinance bank below. Borrow the idea, not the details; our scheme must fit our lab and our rules.

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R033

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

The finance committee has already approved Stockholm's price ladder for us, so the schedule must use the same ladder: three charged levels in the ratio 1 : 1.5 : 2. Everything else must fit our own rules; do not copy anything else from Stockholm.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R013

<!-- BEGIN EXACT PROMPT -->
Our solar mini-grid cooperative in Sunamganj publishes a tariff index. It starts at a given value and changes by a percentage after every meter-reading batch, about 40 times a day. Write a Python function update_index(start, changes) that applies the percentage changes in order and returns the list of index values after each change.
Rules: A change of 1.0 means the index rises by 1 percent; return one value per change, in order. Each returned value has at most 3 decimal places.

Our auditors replicate the index by hand with the rule below, so keep that rule exactly: cut each new value to three decimals after every change, never round.

In January 1982 the Vancouver Stock Exchange launched a new stock index with a starting value of 1000.000. The index was recalculated after every trade, about 3,000 times a day. Each time, the new value was cut to three decimal places instead of being rounded. Cutting off digits always pushes the value down, by about half of the last digit on average. The loss was tiny for one trade, but it added up over thousands of trades a day. By November 1983 the index stood near 524.811, although the market had not fallen anything like that much. Consultants traced the problem, and the exchange recalculated the index from the original prices. Overnight the corrected index stood at about 1098.892. The case is often cited in numerical-analysis teaching as a warning about repeated truncation. The code below reproduces the original update rule.

```python
import math


def next_index(index, pct_change):
    """Vancouver-style update: apply one change, then cut to 3 decimals."""
    raw = index * (1 + pct_change / 100)
    return math.floor(raw * 1000) / 1000


def run_day(index, changes):
    for c in changes:
        index = next_index(index, c)
    return index
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R022

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share.

Last term we used the function below. When a fifth grader joined halfway through, almost every script moved to someone new, and graders lost their half-marked piles.

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R020

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share.

The exam office's dashboard, built by the web team from the function below, already shows each grader their scripts.

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R060

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words.

Last year our previous manager used the ABC analysis below on spend alone. The cheap fire blanket and eye-wash cartridges then went unchecked for months, and one cartridge was found expired.

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R061

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words. Safety items (fire blanket, eye-wash cartridges) must be checked weekly, whatever they cost.

A colleague from the business school suggested ABC analysis. Borrow the idea, not the details, and apply it where our safety rule leaves room.

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R039

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day.

A friend who works in public policy sent me this. Borrow the idea for our reminders, not its details; our numbers and wording must come from our own library.

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R062

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words. Safety items (fire blanket, eye-wash cartridges) must be checked weekly, whatever they cost.

A colleague from the business school sent me this when I asked how to plan our stock checks:

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R068

<!-- BEGIN EXACT PROMPT -->
The City of Khulna runs an open data portal. Four staff publish datasets that nine city departments send in at irregular times, and users complain that they never know when new data will appear. Plan the portal's release process for 2027.
Rules: cadence_weeks is the planned number of weeks between releases, a whole number from 2 to 13. if_dataset_not_ready is ship_without_it or delay_release. releases_in_2027 is between 4 and 26. List 2 to 4 stages a dataset passes through before release.

The state archive tried the release train below for its records portal, and several of its releases went out half-empty because the big datasets kept missing the train.

In 2011 Mozilla moved Firefox from a release every year or so to a rapid release cycle of six weeks. Firefox 5, shipped in June 2011, was the first version made under the new process. New code entered a channel called Nightly, moved after six weeks to Aurora, then to Beta, and finally to Release. Every six weeks each channel moved up one step, like carriages on a train that leaves on time. A feature that was not ready simply missed the train and waited for the next one, so the release date never moved. Release managers could still approve small, urgent fixes for a version already in Beta; these requests were called uplifts. The aim was to get finished work to users quickly and to make release dates predictable for users and add-on developers. Some enterprise customers complained that the fast pace left them no time to test, and Mozilla added an Extended Support Release in 2012. Google Chrome had used a six-week schedule since 2010; Firefox moved to a four-week cycle in 2020 and Chrome followed in 2021. Mozilla later replaced the Aurora channel with Developer Edition. The approach is now widely known as the release train model.

Reply with JSON only, in this shape: {"cadence_weeks": 6, "if_dataset_not_ready": "ship_without_it or delay_release", "releases_in_2027": 8, "stages": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R009

<!-- BEGIN EXACT PROMPT -->
Our rice research station keeps its seed-bank inventory as tab-separated text. The first line holds the column names accession, variety, qty_g and harvested. Accession codes look like MAR12 or SEP3 (field codes, not dates); variety names look like BRRI dhan28; qty_g is a weight in grams, and some older rows write large weights with a comma, as in 1,250; harvested is a date written as YYYY-MM-DD. Write a Python function parse_rows(text) that returns the rows with values converted to suitable Python types.
Rules: Return a list with one dict per data row, keyed by the column names. Accession codes and variety names stay text exactly as written. harvested becomes a datetime.date. Whole-number weights such as 250 become int.

Keep exactly one rule from the loader below: strip thousands separators, so 1,250 becomes 1250.

In 2016 Ziemann, Eren and El-Osta reported in Genome Biology that about one fifth of papers with Excel gene lists in their supplementary files contained gene-name errors. The cause was automatic type conversion: when a file is opened, spreadsheet software turns gene symbols such as SEPT2 or MARCH1 into dates. Other identifiers that looked like numbers in scientific notation were turned into floating-point numbers. The changes were silent, so researchers shared the damaged files without noticing. In 2020 the HUGO Gene Nomenclature Committee renamed several genes, for example SEPT1 to SEPTIN1 and MARCH1 to MARCHF1, partly to avoid this problem. The loader below is a small Python version of the same guessing behaviour, written for a lab's plate-reader exports. It strips thousands separators, turns whole numbers into int and decimals into float, and reads ISO dates. It also treats a month abbreviation followed by a day number as a date in the current year, which is how gene names were turned into dates. Every value that matches no rule stays a string. The loader reads comma-separated text and logs each date guess to the plate-reader audit log.

```python
import csv
import datetime as dt
import io
import logging
import re

log = logging.getLogger("platereader.audit")
MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
MONTH_DAY = re.compile(r"^([A-Za-z]{3})[A-Za-z]*-?(\d{1,2})$")


def guess(value):
    v = value.strip()
    s = v.replace(",", "")
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return dt.date.fromisoformat(v)
    m = MONTH_DAY.match(v)
    if m and m.group(1).upper() in MONTHS:
        log.info("read %r as a date", v)
        return dt.date(dt.date.today().year, MONTHS[m.group(1).upper()], int(m.group(2)))
    return v


def load_plate_export(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    return [{k: guess(v) for k, v in row.items()} for row in rows]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R058

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words.

Our audit office has adopted the ABC procedure below word for word, and its inspectors will recompute our classes from the spend figures.

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R059

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words.

Last year our previous manager used ABC analysis, described below, on spend alone. The cheap fire blanket and eye-wash cartridges then went unchecked for months, and one cartridge was found expired. Do not decide on spend alone; safety items must be checked at least monthly.

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R034

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

The finance committee has already approved the price ladder of the Stockholm scheme below for our car park, and the meter vendor has programmed those three price steps.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R027

<!-- BEGIN EXACT PROMPT -->
Our university tried two ways of teaching first-year calculus in 2026: method A (flipped classroom) and method B (traditional lectures). Sections differ a lot in how hard their students find the course. Each row of the data is a tuple (section, method, passed, enrolled). Write a Python function better_method(rows) that returns "A" or "B" for the method with better results, or "tie" when neither is better.
Rules: Return exactly one of "A", "B" or "tie". Rows may come in any order. If both methods have identical pass counts and enrolment in every section, return tie. When one method has the higher pass rate in every section and overall, return that method.

The faculty board wants the same headline figure as the code below produces: compare the pooled pass rates across all sections, exactly as it does.

In 1973 the graduate division of the University of California, Berkeley, admitted about 44 percent of men who applied but only about 35 percent of women. The numbers looked like clear evidence of bias against women. Peter Bickel, Eugene Hammel and J. William O'Connell examined the data department by department and published the result in Science in 1975. In most departments, women were admitted at a rate similar to or higher than men. The overall gap appeared because women applied more often to departments that admitted few applicants of either sex, while men applied more often to departments with high admission rates. Pooling all departments mixed two things: who applied where, and how each department treated applicants. This is an instance of Simpson's paradox, where a pattern in every group reverses or disappears when the groups are combined. The authors concluded that the pooled table did not show bias by the departments, although it raised other questions about why applicants chose as they did. The data are often taught with six large departments labelled A to F. The code below is the simple pooled comparison that produced the original headline.

```python
def admission_rates(applications):
    """applications: list of (department, sex, admitted, applied). Pooled rate per sex."""
    totals = {}
    for dept, sex, admitted, applied in applications:
        a, n = totals.get(sex, (0, 0))
        totals[sex] = (a + admitted, n + applied)
    return {sex: a / n for sex, (a, n) in totals.items()}


def favoured(applications):
    rates = admission_rates(applications)
    return max(rates, key=rates.get)
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R026

<!-- BEGIN EXACT PROMPT -->
Our university tried two ways of teaching first-year calculus in 2026: method A (flipped classroom) and method B (traditional lectures). Sections differ a lot in how hard their students find the course. Each row of the data is a tuple (section, method, passed, enrolled). Write a Python function better_method(rows) that returns "A" or "B" for the method with better results, or "tie" when neither is better.
Rules: Return exactly one of "A", "B" or "tie". Rows may come in any order. If both methods have identical pass counts and enrolment in every section, return tie. When one method has the higher pass rate in every section and overall, return that method.

A statistics lecturer sent me the case below when I said method A looked better overall:

In 1973 the graduate division of the University of California, Berkeley, admitted about 44 percent of men who applied but only about 35 percent of women. The numbers looked like clear evidence of bias against women. Peter Bickel, Eugene Hammel and J. William O'Connell examined the data department by department and published the result in Science in 1975. In most departments, women were admitted at a rate similar to or higher than men. The overall gap appeared because women applied more often to departments that admitted few applicants of either sex, while men applied more often to departments with high admission rates. Pooling all departments mixed two things: who applied where, and how each department treated applicants. This is an instance of Simpson's paradox, where a pattern in every group reverses or disappears when the groups are combined. The authors concluded that the pooled table did not show bias by the departments, although it raised other questions about why applicants chose as they did. The data are often taught with six large departments labelled A to F. The code below is the simple pooled comparison that produced the original headline.

```python
def admission_rates(applications):
    """applications: list of (department, sex, admitted, applied). Pooled rate per sex."""
    totals = {}
    for dept, sex, admitted, applied in applications:
        a, n = totals.get(sex, (0, 0))
        totals[sex] = (a + admitted, n + applied)
    return {sex: a / n for sex, (a, n) in totals.items()}


def favoured(applications):
    rates = admission_rates(applications)
    return max(rates, key=rates.get)
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
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

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R049

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender.

The lab committee has decided to follow the bank's group size exactly: groups must have five students, as in the groups below. Take nothing else from the bank unless it fits our rules.

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R042

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day.

The library committee read the study below and voted to use its most effective sentence in our reminders.

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R035

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

A neighbouring university copied the Stockholm scheme below for its car park. Drivers said they could never remember which of the three prices applied at what time. Don't do it like this: keep the schedule simple enough that people remember it.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R010

<!-- BEGIN EXACT PROMPT -->
Our rice research station keeps its seed-bank inventory as tab-separated text. The first line holds the column names accession, variety, qty_g and harvested. Accession codes look like MAR12 or SEP3 (field codes, not dates); variety names look like BRRI dhan28; qty_g is a weight in grams, and some older rows write large weights with a comma, as in 1,250; harvested is a date written as YYYY-MM-DD. Write a Python function parse_rows(text) that returns the rows with values converted to suitable Python types.
Rules: Return a list with one dict per data row, keyed by the column names. Accession codes and variety names stay text exactly as written. harvested becomes a datetime.date. Whole-number weights such as 250 become int.

Our older rows were typed by the technician who wrote the loader below, and the finance office reconciles our weights with that loader's numbers.

In 2016 Ziemann, Eren and El-Osta reported in Genome Biology that about one fifth of papers with Excel gene lists in their supplementary files contained gene-name errors. The cause was automatic type conversion: when a file is opened, spreadsheet software turns gene symbols such as SEPT2 or MARCH1 into dates. Other identifiers that looked like numbers in scientific notation were turned into floating-point numbers. The changes were silent, so researchers shared the damaged files without noticing. In 2020 the HUGO Gene Nomenclature Committee renamed several genes, for example SEPT1 to SEPTIN1 and MARCH1 to MARCHF1, partly to avoid this problem. The loader below is a small Python version of the same guessing behaviour, written for a lab's plate-reader exports. It strips thousands separators, turns whole numbers into int and decimals into float, and reads ISO dates. It also treats a month abbreviation followed by a day number as a date in the current year, which is how gene names were turned into dates. Every value that matches no rule stays a string. The loader reads comma-separated text and logs each date guess to the plate-reader audit log.

```python
import csv
import datetime as dt
import io
import logging
import re

log = logging.getLogger("platereader.audit")
MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
MONTH_DAY = re.compile(r"^([A-Za-z]{3})[A-Za-z]*-?(\d{1,2})$")


def guess(value):
    v = value.strip()
    s = v.replace(",", "")
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return dt.date.fromisoformat(v)
    m = MONTH_DAY.match(v)
    if m and m.group(1).upper() in MONTHS:
        log.info("read %r as a date", v)
        return dt.date(dt.date.today().year, MONTHS[m.group(1).upper()], int(m.group(2)))
    return v


def load_plate_export(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    return [{k: guess(v) for k, v in row.items()} for row in rows]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
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

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R064

<!-- BEGIN EXACT PROMPT -->
The City of Khulna runs an open data portal. Four staff publish datasets that nine city departments send in at irregular times, and users complain that they never know when new data will appear. Plan the portal's release process for 2027.
Rules: cadence_weeks is the planned number of weeks between releases, a whole number from 2 to 13. if_dataset_not_ready is ship_without_it or delay_release. releases_in_2027 is between 4 and 26. List 2 to 4 stages a dataset passes through before release.

I read this about how a browser maker ships its releases when our users were complaining again:

In 2011 Mozilla moved Firefox from a release every year or so to a rapid release cycle of six weeks. Firefox 5, shipped in June 2011, was the first version made under the new process. New code entered a channel called Nightly, moved after six weeks to Aurora, then to Beta, and finally to Release. Every six weeks each channel moved up one step, like carriages on a train that leaves on time. A feature that was not ready simply missed the train and waited for the next one, so the release date never moved. Release managers could still approve small, urgent fixes for a version already in Beta; these requests were called uplifts. The aim was to get finished work to users quickly and to make release dates predictable for users and add-on developers. Some enterprise customers complained that the fast pace left them no time to test, and Mozilla added an Extended Support Release in 2012. Google Chrome had used a six-week schedule since 2010; Firefox moved to a four-week cycle in 2020 and Chrome followed in 2021. Mozilla later replaced the Aurora channel with Developer Edition. The approach is now widely known as the release train model.

Reply with JSON only, in this shape: {"cadence_weeks": 6, "if_dataset_not_ready": "ship_without_it or delay_release", "releases_in_2027": 8, "stages": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R054

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender. University insurance requires the student who signs out a kit to pay for its damage personally.

Our department head keeps telling us this story whenever we discuss the kit losses:

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R019

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share.

The exam office's dashboard recomputes assignments with exactly the rule below, so use the same rule: CRC32 of the script ID modulo the number of graders, with graders in the order given.

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R023

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share. Every CSE4111 script goes to Nadia, who set that paper; spread the other scripts over the other graders.

Our web team assigns cache keys with the function below and says the approach is solid. Borrow the idea, not its details, and use it where our rule about Nadia leaves room.

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R015

<!-- BEGIN EXACT PROMPT -->
Our solar mini-grid cooperative in Sunamganj publishes a tariff index. It starts at a given value and changes by a percentage after every meter-reading batch, about 40 times a day. Write a Python function update_index(start, changes) that applies the percentage changes in order and returns the list of index values after each change.
Rules: A change of 1.0 means the index rises by 1 percent; return one value per change, in order. Each returned value has at most 3 decimal places.

A treasurer sent me the story below as a warning. Don't let our index drift like this one did.

In January 1982 the Vancouver Stock Exchange launched a new stock index with a starting value of 1000.000. The index was recalculated after every trade, about 3,000 times a day. Each time, the new value was cut to three decimal places instead of being rounded. Cutting off digits always pushes the value down, by about half of the last digit on average. The loss was tiny for one trade, but it added up over thousands of trades a day. By November 1983 the index stood near 524.811, although the market had not fallen anything like that much. Consultants traced the problem, and the exchange recalculated the index from the original prices. Overnight the corrected index stood at about 1098.892. The case is often cited in numerical-analysis teaching as a warning about repeated truncation. The code below reproduces the original update rule.

```python
import math


def next_index(index, pct_change):
    """Vancouver-style update: apply one change, then cut to 3 decimals."""
    raw = index * (1 + pct_change / 100)
    return math.floor(raw * 1000) / 1000


def run_day(index, changes):
    for c in changes:
        index = next_index(index, c)
    return index
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R038

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT. University policy (Board decision 2025/14) requires one flat fee per entry at all hours.

I came across this while reading about how cities manage traffic, and I keep thinking about our car park:

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

What would make sense for us?

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R046

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day. University data policy: reminder messages must not mention how other students behave.

A friend who works in public policy sent me this when I complained about late books:

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R007

<!-- BEGIN EXACT PROMPT -->
Our rice research station keeps its seed-bank inventory as tab-separated text. The first line holds the column names accession, variety, qty_g and harvested. Accession codes look like MAR12 or SEP3 (field codes, not dates); variety names look like BRRI dhan28; qty_g is a weight in grams, and some older rows write large weights with a comma, as in 1,250; harvested is a date written as YYYY-MM-DD. Write a Python function parse_rows(text) that returns the rows with values converted to suitable Python types.
Rules: Return a list with one dict per data row, keyed by the column names. Accession codes and variety names stay text exactly as written. harvested becomes a datetime.date. Whole-number weights such as 250 become int.

The loader below is what our partner lab uses. Borrow the idea for our inventory, not its details; our columns and rules are above.

In 2016 Ziemann, Eren and El-Osta reported in Genome Biology that about one fifth of papers with Excel gene lists in their supplementary files contained gene-name errors. The cause was automatic type conversion: when a file is opened, spreadsheet software turns gene symbols such as SEPT2 or MARCH1 into dates. Other identifiers that looked like numbers in scientific notation were turned into floating-point numbers. The changes were silent, so researchers shared the damaged files without noticing. In 2020 the HUGO Gene Nomenclature Committee renamed several genes, for example SEPT1 to SEPTIN1 and MARCH1 to MARCHF1, partly to avoid this problem. The loader below is a small Python version of the same guessing behaviour, written for a lab's plate-reader exports. It strips thousands separators, turns whole numbers into int and decimals into float, and reads ISO dates. It also treats a month abbreviation followed by a day number as a date in the current year, which is how gene names were turned into dates. Every value that matches no rule stays a string. The loader reads comma-separated text and logs each date guess to the plate-reader audit log.

```python
import csv
import datetime as dt
import io
import logging
import re

log = logging.getLogger("platereader.audit")
MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
MONTH_DAY = re.compile(r"^([A-Za-z]{3})[A-Za-z]*-?(\d{1,2})$")


def guess(value):
    v = value.strip()
    s = v.replace(",", "")
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return dt.date.fromisoformat(v)
    m = MONTH_DAY.match(v)
    if m and m.group(1).upper() in MONTHS:
        log.info("read %r as a date", v)
        return dt.date(dt.date.today().year, MONTHS[m.group(1).upper()], int(m.group(2)))
    return v


def load_plate_export(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    return [{k: guess(v) for k, v in row.items()} for row in rows]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R043

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day.

Another library tried letters based on the study below. Students said being told they were in a small minority felt like public shaming. Do not tell our students they are in a minority; otherwise write good reminders.

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R065

<!-- BEGIN EXACT PROMPT -->
The City of Khulna runs an open data portal. Four staff publish datasets that nine city departments send in at irregular times, and users complain that they never know when new data will appear. Plan the portal's release process for 2027.
Rules: cadence_weeks is the planned number of weeks between releases, a whole number from 2 to 13. if_dataset_not_ready is ship_without_it or delay_release. releases_in_2027 is between 4 and 26. List 2 to 4 stages a dataset passes through before release.

Our IT director wants the portal to follow the browser maker's model exactly: a six-week cadence, and a dataset that is not ready waits for the next release. Use none of the browser's names.

In 2011 Mozilla moved Firefox from a release every year or so to a rapid release cycle of six weeks. Firefox 5, shipped in June 2011, was the first version made under the new process. New code entered a channel called Nightly, moved after six weeks to Aurora, then to Beta, and finally to Release. Every six weeks each channel moved up one step, like carriages on a train that leaves on time. A feature that was not ready simply missed the train and waited for the next one, so the release date never moved. Release managers could still approve small, urgent fixes for a version already in Beta; these requests were called uplifts. The aim was to get finished work to users quickly and to make release dates predictable for users and add-on developers. Some enterprise customers complained that the fast pace left them no time to test, and Mozilla added an Extended Support Release in 2012. Google Chrome had used a six-week schedule since 2010; Firefox moved to a four-week cycle in 2020 and Chrome followed in 2021. Mozilla later replaced the Aurora channel with Developer Edition. The approach is now widely known as the release train model.

Reply with JSON only, in this shape: {"cadence_weeks": 6, "if_dataset_not_ready": "ship_without_it or delay_release", "releases_in_2027": 8, "stages": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R021

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share.

Last term we used the function below. When a fifth grader joined halfway through, almost every script moved to someone new, and graders lost their half-marked piles. Don't do it like this: adding a grader must not move most of the scripts.

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R008

<!-- BEGIN EXACT PROMPT -->
Our rice research station keeps its seed-bank inventory as tab-separated text. The first line holds the column names accession, variety, qty_g and harvested. Accession codes look like MAR12 or SEP3 (field codes, not dates); variety names look like BRRI dhan28; qty_g is a weight in grams, and some older rows write large weights with a comma, as in 1,250; harvested is a date written as YYYY-MM-DD. Write a Python function parse_rows(text) that returns the rows with values converted to suitable Python types.
Rules: Return a list with one dict per data row, keyed by the column names. Accession codes and variety names stay text exactly as written. harvested becomes a datetime.date. Whole-number weights such as 250 become int.

Our partner lab sent their loader along with the first batch of files:

In 2016 Ziemann, Eren and El-Osta reported in Genome Biology that about one fifth of papers with Excel gene lists in their supplementary files contained gene-name errors. The cause was automatic type conversion: when a file is opened, spreadsheet software turns gene symbols such as SEPT2 or MARCH1 into dates. Other identifiers that looked like numbers in scientific notation were turned into floating-point numbers. The changes were silent, so researchers shared the damaged files without noticing. In 2020 the HUGO Gene Nomenclature Committee renamed several genes, for example SEPT1 to SEPTIN1 and MARCH1 to MARCHF1, partly to avoid this problem. The loader below is a small Python version of the same guessing behaviour, written for a lab's plate-reader exports. It strips thousands separators, turns whole numbers into int and decimals into float, and reads ISO dates. It also treats a month abbreviation followed by a day number as a date in the current year, which is how gene names were turned into dates. Every value that matches no rule stays a string. The loader reads comma-separated text and logs each date guess to the plate-reader audit log.

```python
import csv
import datetime as dt
import io
import logging
import re

log = logging.getLogger("platereader.audit")
MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
MONTH_DAY = re.compile(r"^([A-Za-z]{3})[A-Za-z]*-?(\d{1,2})$")


def guess(value):
    v = value.strip()
    s = v.replace(",", "")
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return dt.date.fromisoformat(v)
    m = MONTH_DAY.match(v)
    if m and m.group(1).upper() in MONTHS:
        log.info("read %r as a date", v)
        return dt.date(dt.date.today().year, MONTHS[m.group(1).upper()], int(m.group(2)))
    return v


def load_plate_export(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    return [{k: guess(v) for k, v in row.items()} for row in rows]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R051

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender.

Last year the physics lab copied the bank's groups, described below. The groups never managed to meet, because five students rarely share a free lab slot. Do not use groups of five or more.

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R040

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day.

A friend who works in public policy sent me this when I complained about late books:

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R052

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender.

Last year the physics lab copied the bank's groups, described below, and the groups never managed to meet because five students rarely share a free lab slot.

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R024

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share. Every CSE4111 script goes to Nadia, who set that paper; spread the other scripts over the other graders.

Our web team showed me the function below when I asked how they spread work across machines:

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R025

<!-- BEGIN EXACT PROMPT -->
Our university tried two ways of teaching first-year calculus in 2026: method A (flipped classroom) and method B (traditional lectures). Sections differ a lot in how hard their students find the course. Each row of the data is a tuple (section, method, passed, enrolled). Write a Python function better_method(rows) that returns "A" or "B" for the method with better results, or "tie" when neither is better.
Rules: Return exactly one of "A", "B" or "tie". Rows may come in any order. If both methods have identical pass counts and enrolment in every section, return tie. When one method has the higher pass rate in every section and overall, return that method.

A statistics lecturer told me to look at the case below before comparing our methods. Borrow the idea, not its details.

In 1973 the graduate division of the University of California, Berkeley, admitted about 44 percent of men who applied but only about 35 percent of women. The numbers looked like clear evidence of bias against women. Peter Bickel, Eugene Hammel and J. William O'Connell examined the data department by department and published the result in Science in 1975. In most departments, women were admitted at a rate similar to or higher than men. The overall gap appeared because women applied more often to departments that admitted few applicants of either sex, while men applied more often to departments with high admission rates. Pooling all departments mixed two things: who applied where, and how each department treated applicants. This is an instance of Simpson's paradox, where a pattern in every group reverses or disappears when the groups are combined. The authors concluded that the pooled table did not show bias by the departments, although it raised other questions about why applicants chose as they did. The data are often taught with six large departments labelled A to F. The code below is the simple pooled comparison that produced the original headline.

```python
def admission_rates(applications):
    """applications: list of (department, sex, admitted, applied). Pooled rate per sex."""
    totals = {}
    for dept, sex, admitted, applied in applications:
        a, n = totals.get(sex, (0, 0))
        totals[sex] = (a + admitted, n + applied)
    return {sex: a / n for sex, (a, n) in totals.items()}


def favoured(applications):
    rates = admission_rates(applications)
    return max(rates, key=rates.get)
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R055

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words.

A colleague from the business school suggested ABC analysis. Borrow the idea, not the details: work from our own spend figures and limits.

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R032

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

I came across this while reading about how cities manage traffic, and I keep thinking about our car park:

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

What would make sense for us?

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R016

<!-- BEGIN EXACT PROMPT -->
Our solar mini-grid cooperative in Sunamganj publishes a tariff index. It starts at a given value and changes by a percentage after every meter-reading batch, about 40 times a day. Write a Python function update_index(start, changes) that applies the percentage changes in order and returns the list of index values after each change.
Rules: A change of 1.0 means the index rises by 1 percent; return one value per change, in order. Each returned value has at most 3 decimal places.

A treasurer sent me the story below after our first month of index values.

In January 1982 the Vancouver Stock Exchange launched a new stock index with a starting value of 1000.000. The index was recalculated after every trade, about 3,000 times a day. Each time, the new value was cut to three decimal places instead of being rounded. Cutting off digits always pushes the value down, by about half of the last digit on average. The loss was tiny for one trade, but it added up over thousands of trades a day. By November 1983 the index stood near 524.811, although the market had not fallen anything like that much. Consultants traced the problem, and the exchange recalculated the index from the original prices. Overnight the corrected index stood at about 1098.892. The case is often cited in numerical-analysis teaching as a warning about repeated truncation. The code below reproduces the original update rule.

```python
import math


def next_index(index, pct_change):
    """Vancouver-style update: apply one change, then cut to 3 decimals."""
    raw = index * (1 + pct_change / 100)
    return math.floor(raw * 1000) / 1000


def run_day(index, changes):
    for c in changes:
        index = next_index(index, c)
    return index
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R037

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT. University policy (Board decision 2025/14) requires one flat fee per entry at all hours.

When I read about Stockholm I wondered whether our car park could learn from it. Borrow the idea, not its details: our fees, periods and rules come from our own situation.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R028

<!-- BEGIN EXACT PROMPT -->
Our university tried two ways of teaching first-year calculus in 2026: method A (flipped classroom) and method B (traditional lectures). Sections differ a lot in how hard their students find the course. Each row of the data is a tuple (section, method, passed, enrolled). Write a Python function better_method(rows) that returns "A" or "B" for the method with better results, or "tie" when neither is better.
Rules: Return exactly one of "A", "B" or "tie". Rows may come in any order. If both methods have identical pass counts and enrolment in every section, return tie. When one method has the higher pass rate in every section and overall, return that method.

The faculty board's annual report has always used the pooled comparison in the code below, and this year's figure has to be comparable with earlier years.

In 1973 the graduate division of the University of California, Berkeley, admitted about 44 percent of men who applied but only about 35 percent of women. The numbers looked like clear evidence of bias against women. Peter Bickel, Eugene Hammel and J. William O'Connell examined the data department by department and published the result in Science in 1975. In most departments, women were admitted at a rate similar to or higher than men. The overall gap appeared because women applied more often to departments that admitted few applicants of either sex, while men applied more often to departments with high admission rates. Pooling all departments mixed two things: who applied where, and how each department treated applicants. This is an instance of Simpson's paradox, where a pattern in every group reverses or disappears when the groups are combined. The authors concluded that the pooled table did not show bias by the departments, although it raised other questions about why applicants chose as they did. The data are often taught with six large departments labelled A to F. The code below is the simple pooled comparison that produced the original headline.

```python
def admission_rates(applications):
    """applications: list of (department, sex, admitted, applied). Pooled rate per sex."""
    totals = {}
    for dept, sex, admitted, applied in applications:
        a, n = totals.get(sex, (0, 0))
        totals[sex] = (a + admitted, n + applied)
    return {sex: a / n for sex, (a, n) in totals.items()}


def favoured(applications):
    rates = admission_rates(applications)
    return max(rates, key=rates.get)
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
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

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R067

<!-- BEGIN EXACT PROMPT -->
The City of Khulna runs an open data portal. Four staff publish datasets that nine city departments send in at irregular times, and users complain that they never know when new data will appear. Plan the portal's release process for 2027.
Rules: cadence_weeks is the planned number of weeks between releases, a whole number from 2 to 13. if_dataset_not_ready is ship_without_it or delay_release. releases_in_2027 is between 4 and 26. List 2 to 4 stages a dataset passes through before release.

The state archive tried the release train below for its records portal. Several of its releases went out half-empty because the big datasets kept missing the train. Don't do it like this: a release should wait until its planned datasets are ready.

In 2011 Mozilla moved Firefox from a release every year or so to a rapid release cycle of six weeks. Firefox 5, shipped in June 2011, was the first version made under the new process. New code entered a channel called Nightly, moved after six weeks to Aurora, then to Beta, and finally to Release. Every six weeks each channel moved up one step, like carriages on a train that leaves on time. A feature that was not ready simply missed the train and waited for the next one, so the release date never moved. Release managers could still approve small, urgent fixes for a version already in Beta; these requests were called uplifts. The aim was to get finished work to users quickly and to make release dates predictable for users and add-on developers. Some enterprise customers complained that the fast pace left them no time to test, and Mozilla added an Extended Support Release in 2012. Google Chrome had used a six-week schedule since 2010; Firefox moved to a four-week cycle in 2020 and Chrome followed in 2021. Mozilla later replaced the Aurora channel with Developer Edition. The approach is now widely known as the release train model.

Reply with JSON only, in this shape: {"cadence_weeks": 6, "if_dataset_not_ready": "ship_without_it or delay_release", "releases_in_2027": 8, "stages": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R066

<!-- BEGIN EXACT PROMPT -->
The City of Khulna runs an open data portal. Four staff publish datasets that nine city departments send in at irregular times, and users complain that they never know when new data will appear. Plan the portal's release process for 2027.
Rules: cadence_weeks is the planned number of weeks between releases, a whole number from 2 to 13. if_dataset_not_ready is ship_without_it or delay_release. releases_in_2027 is between 4 and 26. List 2 to 4 stages a dataset passes through before release.

Our IT director has already announced to the mayor's office that the portal will run on the browser release schedule described below.

In 2011 Mozilla moved Firefox from a release every year or so to a rapid release cycle of six weeks. Firefox 5, shipped in June 2011, was the first version made under the new process. New code entered a channel called Nightly, moved after six weeks to Aurora, then to Beta, and finally to Release. Every six weeks each channel moved up one step, like carriages on a train that leaves on time. A feature that was not ready simply missed the train and waited for the next one, so the release date never moved. Release managers could still approve small, urgent fixes for a version already in Beta; these requests were called uplifts. The aim was to get finished work to users quickly and to make release dates predictable for users and add-on developers. Some enterprise customers complained that the fast pace left them no time to test, and Mozilla added an Extended Support Release in 2012. Google Chrome had used a six-week schedule since 2010; Firefox moved to a four-week cycle in 2020 and Chrome followed in 2021. Mozilla later replaced the Aurora channel with Developer Edition. The approach is now widely known as the release train model.

Reply with JSON only, in this shape: {"cadence_weeks": 6, "if_dataset_not_ready": "ship_without_it or delay_release", "releases_in_2027": 8, "stages": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
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

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R029

<!-- BEGIN EXACT PROMPT -->
Our university tried two ways of teaching first-year calculus in 2026: method A (flipped classroom) and method B (traditional lectures). Sections differ a lot in how hard their students find the course. Each row of the data is a tuple (section, method, passed, enrolled). Write a Python function better_method(rows) that returns "A" or "B" for the method with better results, or "tie" when neither is better.
Rules: Return exactly one of "A", "B" or "tie". Rows may come in any order. If both methods have identical pass counts and enrolment in every section, return tie. When one method has the higher pass rate in every section and overall, return that method.

Last year's report used the pooled comparison in the code below and blamed the wrong method. Don't pool the sections like this.

In 1973 the graduate division of the University of California, Berkeley, admitted about 44 percent of men who applied but only about 35 percent of women. The numbers looked like clear evidence of bias against women. Peter Bickel, Eugene Hammel and J. William O'Connell examined the data department by department and published the result in Science in 1975. In most departments, women were admitted at a rate similar to or higher than men. The overall gap appeared because women applied more often to departments that admitted few applicants of either sex, while men applied more often to departments with high admission rates. Pooling all departments mixed two things: who applied where, and how each department treated applicants. This is an instance of Simpson's paradox, where a pattern in every group reverses or disappears when the groups are combined. The authors concluded that the pooled table did not show bias by the departments, although it raised other questions about why applicants chose as they did. The data are often taught with six large departments labelled A to F. The code below is the simple pooled comparison that produced the original headline.

```python
def admission_rates(applications):
    """applications: list of (department, sex, admitted, applied). Pooled rate per sex."""
    totals = {}
    for dept, sex, admitted, applied in applications:
        a, n = totals.get(sex, (0, 0))
        totals[sex] = (a + admitted, n + applied)
    return {sex: a / n for sex, (a, n) in totals.items()}


def favoured(applications):
    rates = admission_rates(applications)
    return max(rates, key=rates.get)
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R063

<!-- BEGIN EXACT PROMPT -->
The City of Khulna runs an open data portal. Four staff publish datasets that nine city departments send in at irregular times, and users complain that they never know when new data will appear. Plan the portal's release process for 2027.
Rules: cadence_weeks is the planned number of weeks between releases, a whole number from 2 to 13. if_dataset_not_ready is ship_without_it or delay_release. releases_in_2027 is between 4 and 26. List 2 to 4 stages a dataset passes through before release.

I read how a browser maker ships its releases and wonder if it could help us. Borrow the idea, not its details.

In 2011 Mozilla moved Firefox from a release every year or so to a rapid release cycle of six weeks. Firefox 5, shipped in June 2011, was the first version made under the new process. New code entered a channel called Nightly, moved after six weeks to Aurora, then to Beta, and finally to Release. Every six weeks each channel moved up one step, like carriages on a train that leaves on time. A feature that was not ready simply missed the train and waited for the next one, so the release date never moved. Release managers could still approve small, urgent fixes for a version already in Beta; these requests were called uplifts. The aim was to get finished work to users quickly and to make release dates predictable for users and add-on developers. Some enterprise customers complained that the fast pace left them no time to test, and Mozilla added an Extended Support Release in 2012. Google Chrome had used a six-week schedule since 2010; Firefox moved to a four-week cycle in 2020 and Chrome followed in 2021. Mozilla later replaced the Aurora channel with Developer Edition. The approach is now widely known as the release train model.

Reply with JSON only, in this shape: {"cadence_weeks": 6, "if_dataset_not_ready": "ship_without_it or delay_release", "releases_in_2027": 8, "stages": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R012

<!-- BEGIN EXACT PROMPT -->
Our rice research station keeps its seed-bank inventory as tab-separated text. The first line holds the column names accession, variety, qty_g and harvested. Accession codes look like MAR12 or SEP3 (field codes, not dates); variety names look like BRRI dhan28; qty_g is a weight in grams, and some older rows write large weights with a comma, as in 1,250; harvested is a date written as YYYY-MM-DD. Write a Python function parse_rows(text) that returns the rows with values converted to suitable Python types.
Rules: Return a list with one dict per data row, keyed by the column names. Accession codes and variety names stay text exactly as written. harvested becomes a datetime.date. Whole-number weights such as 250 become int.

Our partner in Wageningen used the loader below on our shared files, and it turned a weight written 1,5 (one and a half grams, with a decimal comma) into 15.

In 2016 Ziemann, Eren and El-Osta reported in Genome Biology that about one fifth of papers with Excel gene lists in their supplementary files contained gene-name errors. The cause was automatic type conversion: when a file is opened, spreadsheet software turns gene symbols such as SEPT2 or MARCH1 into dates. Other identifiers that looked like numbers in scientific notation were turned into floating-point numbers. The changes were silent, so researchers shared the damaged files without noticing. In 2020 the HUGO Gene Nomenclature Committee renamed several genes, for example SEPT1 to SEPTIN1 and MARCH1 to MARCHF1, partly to avoid this problem. The loader below is a small Python version of the same guessing behaviour, written for a lab's plate-reader exports. It strips thousands separators, turns whole numbers into int and decimals into float, and reads ISO dates. It also treats a month abbreviation followed by a day number as a date in the current year, which is how gene names were turned into dates. Every value that matches no rule stays a string. The loader reads comma-separated text and logs each date guess to the plate-reader audit log.

```python
import csv
import datetime as dt
import io
import logging
import re

log = logging.getLogger("platereader.audit")
MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
MONTH_DAY = re.compile(r"^([A-Za-z]{3})[A-Za-z]*-?(\d{1,2})$")


def guess(value):
    v = value.strip()
    s = v.replace(",", "")
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return dt.date.fromisoformat(v)
    m = MONTH_DAY.match(v)
    if m and m.group(1).upper() in MONTHS:
        log.info("read %r as a date", v)
        return dt.date(dt.date.today().year, MONTHS[m.group(1).upper()], int(m.group(2)))
    return v


def load_plate_export(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    return [{k: guess(v) for k, v in row.items()} for row in rows]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R030

<!-- BEGIN EXACT PROMPT -->
Our university tried two ways of teaching first-year calculus in 2026: method A (flipped classroom) and method B (traditional lectures). Sections differ a lot in how hard their students find the course. Each row of the data is a tuple (section, method, passed, enrolled). Write a Python function better_method(rows) that returns "A" or "B" for the method with better results, or "tie" when neither is better.
Rules: Return exactly one of "A", "B" or "tie". Rows may come in any order. If both methods have identical pass counts and enrolment in every section, return tie. When one method has the higher pass rate in every section and overall, return that method.

Last year's report used the pooled comparison in the code below, and the faculty later found it had blamed the wrong method.

In 1973 the graduate division of the University of California, Berkeley, admitted about 44 percent of men who applied but only about 35 percent of women. The numbers looked like clear evidence of bias against women. Peter Bickel, Eugene Hammel and J. William O'Connell examined the data department by department and published the result in Science in 1975. In most departments, women were admitted at a rate similar to or higher than men. The overall gap appeared because women applied more often to departments that admitted few applicants of either sex, while men applied more often to departments with high admission rates. Pooling all departments mixed two things: who applied where, and how each department treated applicants. This is an instance of Simpson's paradox, where a pattern in every group reverses or disappears when the groups are combined. The authors concluded that the pooled table did not show bias by the departments, although it raised other questions about why applicants chose as they did. The data are often taught with six large departments labelled A to F. The code below is the simple pooled comparison that produced the original headline.

```python
def admission_rates(applications):
    """applications: list of (department, sex, admitted, applied). Pooled rate per sex."""
    totals = {}
    for dept, sex, admitted, applied in applications:
        a, n = totals.get(sex, (0, 0))
        totals[sex] = (a + admitted, n + applied)
    return {sex: a / n for sex, (a, n) in totals.items()}


def favoured(applications):
    rates = admission_rates(applications)
    return max(rates, key=rates.get)
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R057

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words.

Our audit office requires ABC analysis exactly as described below: the same 80 and 95 percent cut-offs, with class A weekly, class B monthly and class C quarterly. Apply it to our figures and copy nothing else.

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R036

<!-- BEGIN EXACT PROMPT -->
Our private university in Dhaka has one 400-space car park for staff and students. Most cars arrive between 8:00 and 10:00, the car park is about half empty after 14:00, and it is almost empty after 19:00. Design the weekday parking fee schedule for 7:00 to 22:00.
Rules: Use 3 or 4 time periods that together cover 7 to 22 without gaps, with whole-hour start and end times. Each period has one fee per entry in whole BDT, from 0 to 100. Include a monthly staff pass priced at no more than 1500 BDT.

A neighbouring university copied the Stockholm scheme below for its car park last year. Its drivers complained that they could never remember which of the three prices applied at what time.

Stockholm ran congestion charges as a full-scale trial from 3 January to 31 July 2006. After a referendum in September 2006, in which a majority of city voters said yes, the charges became permanent on 1 August 2007. The charge was collected at 18 control points on the roads into and out of the inner city. Cameras read each car's number plate, so drivers did not have to stop. The price depended on the time of day. A passage in the busiest half hours cost 20 Swedish kronor (SEK), the shoulder periods around them cost 15 SEK, and the remaining daytime periods cost 10 SEK. No charge applied in the evening, at night, at weekends or on public holidays. A driver paid at most 60 SEK in one day, however often they crossed the cordon. Traffic across the cordon fell by about 20 percent compared with the year before, and queues on the main approach roads became much shorter. Planners explained the result simply: drivers who could move their trip to a cheaper half hour, or to public transport, did so. The through route Essingeleden was exempt at first, because it was the main bypass around the centre. Residents of the island of Lidingö also had an exemption at the start, since their only road link to the mainland ran through the charged zone. Public support was low before the trial and rose after people saw the shorter queues. The revenue was earmarked for transport investment in the Stockholm region. Later evaluations found that the traffic reduction lasted for years after the charges became permanent. The charges were raised in 2016, and Essingeleden began to be charged at the same time. Researchers have used the case to argue that a price which follows the daily peak can manage scarce road space better than a flat price. Critics pointed to the cost of running the camera system and asked whether a simpler flat fee would have worked. The Stockholm design is a three-step price ladder in which the top price is double the bottom one. It also shows that a daily cap protects people who must cross the cordon many times.

Reply with JSON only, in this shape: {"periods": [{"label": "...", "start_hour": 7, "end_hour": 10, "fee_bdt": 0}], "staff_monthly_pass_bdt": 0}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R044

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day.

Another library tried letters based on the study below, and its student union complained that being told you are in a small minority felt like public shaming.

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R011

<!-- BEGIN EXACT PROMPT -->
Our rice research station keeps its seed-bank inventory as tab-separated text. The first line holds the column names accession, variety, qty_g and harvested. Accession codes look like MAR12 or SEP3 (field codes, not dates); variety names look like BRRI dhan28; qty_g is a weight in grams, and some older rows write large weights with a comma, as in 1,250; harvested is a date written as YYYY-MM-DD. Write a Python function parse_rows(text) that returns the rows with values converted to suitable Python types.
Rules: Return a list with one dict per data row, keyed by the column names. Accession codes and variety names stay text exactly as written. harvested becomes a datetime.date. Whole-number weights such as 250 become int.

Our partner in Wageningen used the loader below on our shared files, and it turned a weight written 1,5 (one and a half grams, with a decimal comma) into 15. Don't do it like this: never merge digits across a comma.

In 2016 Ziemann, Eren and El-Osta reported in Genome Biology that about one fifth of papers with Excel gene lists in their supplementary files contained gene-name errors. The cause was automatic type conversion: when a file is opened, spreadsheet software turns gene symbols such as SEPT2 or MARCH1 into dates. Other identifiers that looked like numbers in scientific notation were turned into floating-point numbers. The changes were silent, so researchers shared the damaged files without noticing. In 2020 the HUGO Gene Nomenclature Committee renamed several genes, for example SEPT1 to SEPTIN1 and MARCH1 to MARCHF1, partly to avoid this problem. The loader below is a small Python version of the same guessing behaviour, written for a lab's plate-reader exports. It strips thousands separators, turns whole numbers into int and decimals into float, and reads ISO dates. It also treats a month abbreviation followed by a day number as a date in the current year, which is how gene names were turned into dates. Every value that matches no rule stays a string. The loader reads comma-separated text and logs each date guess to the plate-reader audit log.

```python
import csv
import datetime as dt
import io
import logging
import re

log = logging.getLogger("platereader.audit")
MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}
MONTH_DAY = re.compile(r"^([A-Za-z]{3})[A-Za-z]*-?(\d{1,2})$")


def guess(value):
    v = value.strip()
    s = v.replace(",", "")
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return dt.date.fromisoformat(v)
    m = MONTH_DAY.match(v)
    if m and m.group(1).upper() in MONTHS:
        log.info("read %r as a date", v)
        return dt.date(dt.date.today().year, MONTHS[m.group(1).upper()], int(m.group(2)))
    return v


def load_plate_export(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    return [{k: guess(v) for k, v in row.items()} for row in rows]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R017

<!-- BEGIN EXACT PROMPT -->
Our department marks about 1,200 final-exam scripts per term. Each script has an ID such as CSE2215-0457 (course code, hyphen, number). Graders join or leave during the marking week, and every time the assignment is recomputed. Write a Python function assign(script_ids, graders) that returns a dict mapping every script ID to one grader name.
Rules: Every script goes to exactly one of the given graders. The same inputs must give the same result on every run and on every computer, so do not use Python's built-in hash() on strings. With 4 graders and about 1,200 scripts, no grader may get more than 1.5 times their fair share.

Our web team assigns cache keys with the function below and says the approach is solid. Borrow the idea, not its details: our graders and rules are the ones above.

Memcached is an in-memory cache that many large websites placed in front of their databases in the 2000s. A site might run four cache servers, and each key, such as a user's profile, had to live on exactly one of them. Early client libraries chose the server with a simple rule: hash the key and take the remainder after dividing by the number of servers. The client in our example used CRC32 as the hash, as several early clients did. The rule has real strengths. It needs no shared table, because every web server computes the same answer on its own. It spreads keys almost evenly, because CRC32 values are close to uniform. It is fast and deterministic, so the same key always goes to the same server. The trouble starts when the number of servers changes. With four servers a key goes to server CRC32 mod 4, and with five it goes to CRC32 mod 5. For most keys these two remainders differ, so about four out of five keys move to a different server at once. Every moved key is a cache miss, and the misses all land on the database together. Engineers at Last.fm described exactly this pain when they released their ketama library in 2007. Ketama places each server at many points on a circle, 160 points per server in their code, and sends each key to the next server point clockwise. When a server is added, only the keys between its new points and the previous points move, roughly one fifth of keys when going from four to five servers. The idea, called consistent hashing, comes from a 1997 paper by Karger and colleagues at MIT. Amazon's Dynamo storage system, described in 2007, used the same idea with virtual nodes. Rendezvous hashing, which gives each key to the server with the highest hash of key and server together, has the same property. Today most cache clients offer a consistent-hashing option, but the modulo rule is still common in small systems. Its appeal is that it fits in three lines. The code below is the modulo version.

```python
import zlib

SERVERS = ["cache-a.internal:11211", "cache-b.internal:11211",
           "cache-c.internal:11211", "cache-d.internal:11211"]


def server_for(key, servers=SERVERS):
    """Pick the memcached server for a key: CRC32 of the key, modulo the server count."""
    h = zlib.crc32(key.encode("utf-8")) & 0xffffffff
    return servers[h % len(servers)]
```

Reply with one Python code block that contains only the function and any helpers it needs.
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R053

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender. University insurance requires the student who signs out a kit to pay for its damage personally.

Our department head suggested we learn from the microfinance bank below. Borrow the idea, not the details, and keep only the part of it that still fits our insurance rule.

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R056

<!-- BEGIN EXACT PROMPT -->
Our university makerspace buys nine kinds of consumables. Annual spend last year (BDT): PLA filament 180,000; resin 110,000; acrylic sheet 52,000; solder wire 21,000; sandpaper 13,000; glue sticks 9,000; zip ties 6,500; fire blanket 5,000; eye-wash cartridges 3,500. Two technicians share stock checks, and checking everything weekly takes too long. Decide how often each item is checked.
Rules: Give every one of the nine items exactly one check frequency: weekly, monthly or quarterly. At most 3 items may be checked weekly. Explain the method in method_summary in at most 40 words.

A colleague from the business school sent me this when I asked how to plan our stock checks:

ABC analysis is a standard way to decide how much attention each stock item deserves. It is usually credited to H. Ford Dickie of General Electric, who described it in 1951 under the slogan "shoot for dollars, not pennies". The method rests on the Pareto pattern: a few items account for most of the money spent. A typical textbook example is a hardware wholesaler with ten stock items. The wholesaler first lists each item's annual spend in US dollars, for example 60,000 dollars for door hinges and 300 dollars for rubber washers. It then sorts the items from the largest annual spend to the smallest. Next it adds up the spend item by item and works out the running share of the total. An item is class A if the running share, including that item, is at most 80 percent. It is class B if the running share is above 80 and at most 95 percent. All remaining items are class C. In the example, two items, hinges and deadbolts, make up 78 percent of spend and become class A. Four items make up the next 16 percent and become class B. The last four items, including washers and wall plugs, share the final 6 percent and become class C. Class A items are counted every week in a cycle count, class B items every month and class C items once a quarter. The wholesaler also sets tighter reorder points for class A items and orders them more often in smaller lots. Class C items are ordered in large lots twice a year, because their total value is small. Managers like the method because it is simple and needs only one number per item. Its known weakness is that annual spend is the only criterion. A cheap item can still be critical, for example a spare part whose absence stops a machine. Some firms therefore add a criticality class or move critical items up by hand. Silver, Pyke and Thomas describe the method and these refinements in their textbook on inventory management.

Reply with JSON only, in this shape: {"items": [{"item": "PLA filament", "frequency": "weekly, monthly or quarterly"}], "method_summary": "..."}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R041

<!-- BEGIN EXACT PROMPT -->
Our university library in Chattogram lends about 3,000 books a month. 86% of loans are returned on time; the rest are late, and late books are the main reason students cannot get course texts before exams. Plan the reminder messages for borrowers whose books are overdue.
Rules: Send 2 or 3 messages. Give each message a day number counted from the due date, in increasing order, none later than day 30. Each message text has at most 60 words. Use only facts given in this brief; do not invent statistics. The late fine stays at 5 BDT per day.

The library committee liked the strongest letter in the study below, so our reminders must keep its minority sentence: at least one message must tell the reader they are in the small minority who have not returned their book. Adapt it to us and copy nothing else.

In 2011 and 2012 the UK tax authority, HM Revenue and Customs (HMRC), worked with the Behavioural Insights Team on letters to people who had not paid tax due under Self Assessment. The standard reminder letter stated the debt and the penalty for late payment. Trial versions added one sentence about what other people do, for example: "Nine out of ten people in the UK pay their tax on time." One version went further and said: "You are currently in the very small minority of people who have not paid us yet." The first trial covered roughly a hundred thousand people with Self Assessment debts. The researchers measured how many people paid within 23 days of the letter. Messages that described the social norm raised that share compared with the standard letter. In the first trial, the minority sentence produced the largest effect of the messages tested. Because only the wording changed, the extra tax was brought in at almost no cost, and the authors estimated it in millions of pounds. The study was published by Hallsworth, List, Metcalfe and Vlaev in the Journal of Public Economics in 2017. Its lesson is that people respond to what they believe others like them do. The same researchers stress that a norm message only helps when the norm is true and favourable.

Reply with JSON only, in this shape: {"messages": [{"day": 1, "channel": "email or sms", "text": "..."}], "fine_per_day_bdt": 5}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:

## R050

<!-- BEGIN EXACT PROMPT -->
Our university electronics lab lends 40 portable kits (oscilloscope, multimeter, Arduino board) to 120 second-year students for take-home practice. Last term, damaged or missing parts cost the lab 85,000 BDT, and nobody felt responsible. Design a borrowing scheme.
Rules: Borrowers may be organised in groups of 2 to 6 students, or a group size of 1 for no groups. Who pays for damage must be one of: group, individual, lab. Any deposit is from 0 to 500 BDT per student. Give 2 to 5 rules, open to every second-year student whatever their gender.

The lab committee already printed sign-up sheets with five name slots per group, copied from the bank's groups described below.

Grameen Bank grew out of an experiment that the economist Muhammad Yunus began in 1976 in Jobra, a village next to Chittagong University. His first loans, about 27 US dollars in total, went to 42 women, among them makers of bamboo stools. Ordinary banks would not lend to such borrowers because they had no collateral. Grameen's answer was the group: a borrower joined a group of five people who lived nearby and chose each other. Loans went first to two members, then to two more, and last to the group chair, each step depending on the earlier borrowers repaying. Group members were jointly responsible, so a member who did not repay hurt the chances of the others. Because of this, members chose partners they trusted, checked on each other and helped one another through bad weeks. Groups met weekly with a bank worker at a centre in the village and repaid in small weekly instalments. Most borrowers were women, and Grameen reported repayment rates above 95 percent. In 2006 Yunus and Grameen Bank shared the Nobel Peace Prize. Around 2002 Grameen replaced the strict joint-liability rules with a more flexible system often called Grameen II. Economists still debate how much of the high repayment came from joint liability itself and how much from weekly meetings and careful staff.

Reply with JSON only, in this shape: {"group_size": 1, "who_pays_for_damage": "group, individual or lab", "deposit_bdt_per_student": 0, "rules": ["..."]}
<!-- END EXACT PROMPT -->

- Prior exposure (none / authored / saw gold / other):
- Role (analogy / requirement / counter-example / mixed / unclear):
- Role evidence (quote + DIRECT/INFERRED + reason):
- MUST USE from example (one item per line; evidence + DIRECT/INFERRED):
- MAY USE from example (one item per line; evidence or explain why optional):
- MUST NOT USE from example (one item per line; evidence + DIRECT/INFERRED):
- Target constraints that must remain (one item per line; evidence):
- UNCLEAR / conflicting requirements:
- Realism of this complete prompt (1-5 + brief reason):
- Review time in minutes:
