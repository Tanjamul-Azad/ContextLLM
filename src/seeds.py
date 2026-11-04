"""Pilot seeds for the role-aware example-use study.

Each seed pairs a target task with a source example. The same example is given
in three roles (analogy, requirement, counter-example), with plain or explicit
wording. Every check is automatic, so no LLM judge is needed in the pilot.

Check kinds:
  format      the answer can be parsed (JSON object or a Python function)
  constraint  target rules that hold in every role
  transfer    what the role asks the model to take (or, for a counter-example, to avoid)
  leakage     incidental source details that must not appear
The "marker" is the example's distinctive pattern: a requirement must copy it,
a counter-example must not. It is used for the role-sensitivity measure (E5).
"""

COLOURS = ["Red", "Orange", "Yellow", "Green", "Blue"]
HOUR_WORDS = ["hour", "hours", "hourly", "per-hour"]
ANYONE = ["any", "anyone", "everyone", "all", "any member", "any developer", "any volunteer"]
STOP_WORDS = ["stop", "pause", "halt", "freeze", "block", "roll back", "rollback", "suspend"]
FAR_WORDS = ["back", "far", "farthest", "furthest", "last", "rear", "rows 2", "row 30", "rows 3"]
# v1.1: the word list missed "rows 25-30"; match any back-half row range instead.
FAR_REGEX = r"\b(back|far|farthest|furthest|last|rear)\b|\brows?\s*(1[6-9]|2\d|30)\b"
CAPS_BANG = r"^\s*[A-Z]{3,}!"
ZONE = r"^\s*zone\b"

JSON_FMT = "Reply with JSON only, in this shape: "
CODE_FMT = "Reply with one Python code block that contains only the function."

SEEDS = [
    # ------------------------------------------------------------------ planning
    {
        "id": "P1_helpdesk_triage",
        "family": "planning",
        "basis": "Manchester Triage System (real hospital practice) mapped to a university IT help desk",
        "task": "Design a priority scheme for tickets at our university IT help desk (password resets, Wi-Fi outages, lab PC faults, exam-system failures).",
        "rules": "Rules: at most 3 priority levels; response times in whole hours, at most 72; the same two staff members handle all tickets, so no new roles.",
        "format": JSON_FMT + '{"levels": [{"name": "...", "response_hours": 0}]}, listed from most to least urgent.',
        "example": (
            "Hospital emergency triage (Manchester Triage System):\n"
            "- Red: immediate, seen at once\n"
            "- Orange: very urgent, within 10 minutes\n"
            "- Yellow: urgent, within 60 minutes\n"
            "- Green: standard, within 120 minutes\n"
            "- Blue: non-urgent, within 240 minutes\n"
            "A triage nurse assesses every patient on arrival."
        ),
        "roles": {
            "analogy": {
                "plain": "For inspiration, here is how hospital emergency departments sort patients:\n{EX}\nCould our help desk work in a similar spirit?",
                "explicit": "Take only the principle that more urgent tickets get a faster response. Do not reuse the colour names, minute-based times or clinical roles.",
                "checks": [
                    ("transfer", ("json_increasing", "levels[].response_hours")),
                    ("leakage", ("json_no_word", "levels[].name", COLOURS)),
                    ("leakage", ("text_absent", ["nurse", "patient", "patients", "minutes", "Manchester"])),
                    ("leakage", ("json_count_in_lt", "levels[].response_hours", [10, 60, 120, 240], 2)),
                ],
            },
            "requirement": {
                "plain": "Our faculty already uses these hospital colour codes on all its signs, so the levels must use the same colour names as this scheme:\n{EX}",
                "explicit": "Copy only the colour names for the level names. Do not copy the clinical roles or the minute-based times.",
                "checks": [
                    ("transfer", ("json_all_word", "levels[].name", COLOURS)),
                    ("leakage", ("text_absent", ["nurse", "patient", "patients", "minutes", "Manchester"])),
                    ("leakage", ("json_count_in_lt", "levels[].response_hours", [10, 60, 120, 240], 2)),
                ],
            },
            "counter": {
                "plain": "Last year a consultant copied the hospital scheme below for us, and staff found the colour codes confusing:\n{EX}\nPlease don't do it like that.",
                "explicit": "Do not use colour names or any clinical terms for the levels.",
                "checks": [
                    ("transfer", ("json_no_word", "levels[].name", COLOURS)),
                    ("leakage", ("text_absent", ["nurse", "patient", "patients", "minutes", "Manchester"])),
                    ("leakage", ("json_count_in_lt", "levels[].response_hours", [10, 60, 120, 240], 2)),
                ],
            },
        },
        "constraints": [
            ("json_len_between", "levels", 2, 3),
            ("json_all_int", "levels[].response_hours"),
            ("json_all_le", "levels[].response_hours", 72),
        ],
        "marker": ("json_any_word", "levels[].name", COLOURS),
    },
    {
        "id": "P2_drone_pricing",
        "family": "planning",
        "basis": "Rolls-Royce 'Power by the Hour' (real business model) mapped to drone crop inspection",
        "task": "Propose a pricing plan for our drone crop-inspection service for farmers in northern Bangladesh. We own and maintain the drones.",
        "rules": "Rules: at most 3 charges; all prices in BDT (Bangladeshi taka).",
        "format": JSON_FMT + '{"charges": [{"name": "...", "unit": "...", "price_bdt": 0}], "maintenance_paid_by": "provider or customer"}',
        "example": (
            "Rolls-Royce 'Power by the Hour' (TotalCare): airlines pay Rolls-Royce a fixed US-dollar rate for every hour "
            "a jet engine flies. Rolls-Royce keeps responsibility for maintaining and repairing the engines, so the "
            "airline's cost tracks how much it actually flies."
        ),
        "roles": {
            "analogy": {
                "plain": "I keep thinking about this model from aviation:\n{EX}\nCould something along those lines work for us?",
                "explicit": "Take only the idea of charging by hours of use while we keep maintenance. Do not reuse the name or any aviation terms, and do not price in dollars.",
                "checks": [
                    ("transfer", ("json_any_word", "charges[].unit", HOUR_WORDS)),
                    ("transfer", ("json_eq", "maintenance_paid_by", "provider")),
                    ("leakage", ("text_absent", ["engine", "engines", "jet", "airline", "airlines", "aircraft", "Rolls", "dollar", "USD", "TotalCare"])),
                    ("leakage", ("regex_absent", r"power[\s-]*by[\s-]*the[\s-]*hour")),
                ],
            },
            "requirement": {
                "plain": "Our investors liked this model so much that the plan must be sold under exactly the same name:\n{EX}",
                "explicit": "Copy only the name 'Power by the Hour' for the plan. Do not copy aviation terms or dollar prices.",
                "checks": [
                    ("transfer", ("regex_present", r"power[\s-]*by[\s-]*the[\s-]*hour")),
                    ("leakage", ("text_absent", ["engine", "engines", "jet", "airline", "airlines", "aircraft", "Rolls", "dollar", "USD", "TotalCare"])),
                ],
            },
            "counter": {
                "plain": "A competitor copied the model below, and farmers hated not knowing their bill until the season ended:\n{EX}\nPlease don't price it like that.",
                "explicit": "Do not charge by the hour and do not use the name 'Power by the Hour'.",
                "checks": [
                    ("transfer", ("json_no_word", "charges[].unit", HOUR_WORDS)),
                    ("transfer", ("regex_absent", r"power[\s-]*by[\s-]*the[\s-]*hour")),
                    ("leakage", ("text_absent", ["engine", "engines", "jet", "airline", "airlines", "aircraft", "Rolls", "dollar", "USD", "TotalCare"])),
                ],
            },
        },
        "constraints": [
            ("json_len_between", "charges", 1, 3),
            ("json_all_num", "charges[].price_bdt"),
        ],
        "marker": ("regex_present", r"power[\s-]*by[\s-]*the[\s-]*hour"),
    },
    {
        "id": "P3_incident_andon",
        "family": "planning",
        "basis": "Toyota andon cord (real manufacturing practice) mapped to a student-run website",
        "task": "Write an incident policy for the course-registration website our student club maintains (6 volunteer developers, 2 of them maintainers).",
        "rules": "Rules: at most 4 rules; every rule must say who may trigger it; include one rule for database outages.",
        "format": JSON_FMT + '{"rules": [{"trigger": "...", "action": "...", "who_can_trigger": "..."}]}',
        "example": (
            "Toyota's andon cord: any worker on the assembly line can pull a cord to stop the whole production line "
            "when they spot a defect. A team leader arrives within 60 seconds, and the line restarts only after the "
            "problem is fixed."
        ),
        "roles": {
            "analogy": {
                "plain": "I like how car factories deal with problems:\n{EX}\nCan our policy follow a similar idea?",
                "explicit": "Take only the idea that anyone on the team can stop a release when they see a problem. Do not reuse factory terms or the word 'andon'.",
                "checks": [
                    ("transfer", ("json_exists_item", "rules", {"who_can_trigger": ANYONE, "action": STOP_WORDS})),
                    ("leakage", ("text_absent", ["cord", "assembly", "production line", "Toyota", "worker", "workers", "60 seconds", "car"])),
                    ("leakage", ("text_absent", ["andon"])),
                ],
            },
            "requirement": {
                "plain": "Our club already calls this the 'andon' rule after Toyota, so the policy must use the word 'andon' for it:\n{EX}",
                "explicit": "Copy only the word 'andon' as the rule's name. Do not copy factory terms.",
                "checks": [
                    ("transfer", ("text_present", ["andon"])),
                    ("leakage", ("text_absent", ["cord", "assembly", "production line", "Toyota", "worker", "workers", "60 seconds", "car"])),
                ],
            },
            "counter": {
                "plain": "Last semester we tried this idea and new members kept stopping deployments for tiny issues:\n{EX}\nDon't do it like that.",
                "explicit": "Do not let everyone stop a release; only the two maintainers may do that. Do not use the word 'andon'.",
                "checks": [
                    ("transfer", ("json_not_exists_item", "rules", {"who_can_trigger": ANYONE, "action": STOP_WORDS})),
                    ("transfer", ("text_absent", ["andon"])),
                    ("leakage", ("text_absent", ["cord", "assembly", "production line", "Toyota", "worker", "workers", "60 seconds", "car"])),
                ],
            },
        },
        "constraints": [
            ("json_len_between", "rules", 1, 4),
            ("json_all_nonempty", "rules[].who_can_trigger"),
            ("json_any_word", "rules[].trigger", ["database", "DB"]),
        ],
        "marker": ("text_present", ["andon"]),
    },
    {
        "id": "P4_workshop_survivorship",
        "family": "planning",
        "basis": "Abraham Wald and WWII bomber survivorship bias (real case) mapped to an optional workshop",
        "task": "Plan how to evaluate our new optional study-skills workshop for first-year students before the faculty makes it mandatory. Students can leave the workshop whenever they want.",
        "rules": "Rules: at most 5 steps; no extra budget.",
        "format": JSON_FMT + '{"assignment": "random or voluntary or everyone", "track_students_who_leave": true, "steps": ["..."]}',
        "example": (
            "In the Second World War, analysts studied bullet holes on bombers that returned from missions and planned "
            "to add armour where the holes were. Abraham Wald pointed out that the planes hit in other places never came "
            "back, so armour belonged where the returning planes had no holes."
        ),
        "roles": {
            "analogy": {
                "plain": "This reminds me of a famous story:\n{EX}\nCan our evaluation avoid a similar mistake?",
                "explicit": "Take only the lesson that the people who drop out must be counted. Do not mention the war, planes or Wald.",
                "checks": [
                    ("transfer", ("json_eq", "track_students_who_leave", True)),
                    ("leakage", ("text_absent", ["bullet", "bullets", "bomber", "bombers", "plane", "planes", "aircraft", "armour", "armor", "war", "mission", "missions"])),
                    ("leakage", ("text_absent", ["Wald"])),
                ],
            },
            "requirement": {
                "plain": "Our dean loves this story and wants the plan to credit it by naming Abraham Wald:\n{EX}",
                "explicit": "Copy only Wald's name as the credit. Do not retell the war story.",
                "checks": [
                    ("transfer", ("text_present", ["Wald"])),
                    ("leakage", ("text_absent", ["bullet", "bullets", "bomber", "bombers", "plane", "planes", "aircraft", "armour", "armor", "war", "mission", "missions"])),
                ],
            },
            "counter": {
                "plain": "A colleague keeps citing this story, but it does not fit us because attendance is tracked and no student has left so far:\n{EX}\nDon't build the plan around that story.",
                "explicit": "Do not mention Wald, survivorship or the war story.",
                "checks": [
                    ("transfer", ("text_absent", ["Wald", "survivorship", "survivor", "survivors"])),
                    ("leakage", ("text_absent", ["bullet", "bullets", "bomber", "bombers", "plane", "planes", "aircraft", "armour", "armor", "war", "mission", "missions"])),
                ],
            },
        },
        "constraints": [
            ("json_len_between", "steps", 1, 5),
            ("json_is_bool", "track_students_who_leave"),
        ],
        "marker": ("text_present", ["Wald"]),
    },
    {
        "id": "P5_newsletter_headlines",
        "family": "planning",
        "basis": "Tabloid headline style (the most common real request type in WildChat: 'like this')",
        "task": "Write 3 headlines for our CSE department newsletter: our robotics team won the national championship, a new AI lab opens next month, and the library now stays open until midnight.",
        "rules": "Rules: exactly 3 headlines; at most 10 words each.",
        "format": JSON_FMT + '{"headlines": ["...", "...", "..."]}',
        "example": (
            "Three headlines from a tabloid site:\n"
            "1. SHOCK! Robots Take Over City Hall!!\n"
            "2. EXCLUSIVE! Celebrity Chef Quits TV Forever!!\n"
            "3. REVEALED! The Diet Doctors Hate!!"
        ),
        "roles": {
            "analogy": {
                "plain": "Make them as attention-grabbing as these, but in our own newsletter voice:\n{EX}",
                "explicit": "Take only the punchy, short style. Do not copy the ALL-CAPS opener, the double exclamation marks or any of their words.",
                "checks": [
                    # v1.1: removed an 8-word transfer check; the prompt allows 10 words (audit 2026-11-05).
                    ("leakage", ("json_none_match", "headlines[]", CAPS_BANG)),
                    ("leakage", ("text_absent", ["SHOCK", "EXCLUSIVE", "REVEALED", "Celebrity", "Take Over", "!!"])),
                ],
            },
            "requirement": {
                "plain": "Our editor wants exactly the same format as these, with one ALL-CAPS word and an exclamation mark first:\n{EX}",
                "explicit": "Copy only the format: one ALL-CAPS word with '!' and then the headline. Do not reuse their words or the double '!!'.",
                "checks": [
                    ("transfer", ("json_all_match", "headlines[]", CAPS_BANG)),
                    ("leakage", ("text_absent", ["SHOCK", "EXCLUSIVE", "REVEALED", "Celebrity", "Take Over", "!!"])),
                ],
            },
            "counter": {
                "plain": "Our readers complained when we wrote headlines like these tabloid ones:\n{EX}\nPlease don't.",
                "explicit": "Do not start with an ALL-CAPS word and do not use exclamation marks.",
                "checks": [
                    ("transfer", ("json_none_match", "headlines[]", CAPS_BANG)),
                    ("leakage", ("text_absent", ["SHOCK", "EXCLUSIVE", "REVEALED", "Celebrity", "Take Over", "!!"])),
                ],
            },
        },
        "constraints": [
            ("json_len_between", "headlines", 3, 3),
            ("json_all_words_le", "headlines[]", 10),
        ],
        "marker": ("json_count_match_ge", "headlines[]", CAPS_BANG, 2),
    },
    {
        "id": "P6_exam_hall_boarding",
        "family": "planning",
        "basis": "Airline boarding by zones (real practice) mapped to exam-hall entry",
        "task": "Plan how 300 students enter our exam hall through one door so that everyone is seated within 20 minutes. Seats are in 30 rows; row 1 is next to the door.",
        "rules": "Rules: at most 5 groups; every group needs a whole-number entry order.",
        "format": JSON_FMT + '{"groups": [{"name": "...", "order": 1, "who": "..."}]}',
        "example": (
            "How airlines board a plane: passengers are called by zone. Zone 1 is business class and priority members, "
            "Zone 2 is window seats at the back, Zone 3 is the middle, Zone 4 is everyone else. Gate staff scan each "
            "boarding pass."
        ),
        "roles": {
            "analogy": {
                "plain": "Something like how airlines board planes might help:\n{EX}",
                "explicit": "Take only the idea of letting the people seated farthest from the door enter first. Do not reuse zone names or airline terms.",
                "checks": [
                    ("transfer", ("json_first_item_regex", "groups", "order", "who", FAR_REGEX)),
                    ("leakage", ("json_none_match", "groups[].name", ZONE)),
                    ("leakage", ("text_absent", ["business class", "passenger", "passengers", "gate", "boarding pass", "flight", "priority members", "window seats"])),
                ],
            },
            "requirement": {
                "plain": "The exam office already prints 'Zone 1', 'Zone 2' and so on on the hall signs, so the groups must be named exactly like these airline zones:\n{EX}",
                "explicit": "Copy only the 'Zone N' names. Do not copy airline terms.",
                "checks": [
                    ("transfer", ("json_all_match", "groups[].name", ZONE)),
                    ("leakage", ("text_absent", ["business class", "passenger", "passengers", "gate", "boarding pass", "flight", "priority members", "window seats"])),
                ],
            },
            "counter": {
                "plain": "Someone suggested copying airline boarding, but our exam office finds the airline-zone idea confusing:\n{EX}\nDon't do it like that.",
                "explicit": "Do not name groups as zones and do not use airline terms.",
                "checks": [
                    ("transfer", ("json_none_match", "groups[].name", ZONE)),
                    ("leakage", ("text_absent", ["business class", "passenger", "passengers", "gate", "boarding pass", "flight", "priority members", "window seats"])),
                ],
            },
        },
        "constraints": [
            ("json_len_between", "groups", 1, 5),
            ("json_all_int", "groups[].order"),
        ],
        "marker": ("json_count_match_ge", "groups[].name", ZONE, 2),
    },
    # ---------------------------------------------------------------------- code
    {
        "id": "C1_window_sum",
        "family": "code",
        "basis": "A real-style moving-average helper with a hard-coded 7-day window",
        "task": "Write a Python function `max_window_sum(nums, k)` that returns the largest sum of any k consecutive numbers in the list `nums` (assume 1 <= k <= len(nums)).",
        "rules": "Rules: standard library only; do not print anything.",
        "format": CODE_FMT,
        "func": "max_window_sum",
        "example": (
            "```python\n"
            "def weekly_avg(temps):\n"
            '    """7-day moving average of Dhaka temperatures, rounded and printed."""\n'
            "    window = 7\n"
            "    total = sum(temps[:window])\n"
            "    out = [round(total / window, 1)]\n"
            "    for i in range(window, len(temps)):\n"
            "        total += temps[i] - temps[i - window]\n"
            "        out.append(round(total / window, 1))\n"
            '    print("Dhaka weekly averages:", out)\n'
            "    return out\n"
            "```"
        ),
        "roles": {
            "analogy": {
                "plain": "We already have this helper that uses a nice trick; write the new one in a similar way:\n{EX}",
                "explicit": "Take only the running-sum trick (add the new item, subtract the old one). Do not copy the fixed window of 7, the rounding or the Dhaka wording.",
                "checks": [
                    ("transfer", ("py_test", "FAST")),
                    ("leakage", ("py_test", "NO_DEFAULT_7")),
                    ("leakage", ("regex_absent", r"round\(|Dhaka|temps")),
                ],
            },
            "requirement": {
                "plain": "Our dashboards always use the same 7-day window as this helper, so k must default to 7 exactly like it:\n{EX}",
                "explicit": "Copy only the default window of 7 for k. Do not copy the rounding or the Dhaka wording.",
                "checks": [
                    ("transfer", ("py_test", "DEFAULT_7")),
                    ("leakage", ("regex_absent", r"round\(|Dhaka|temps")),
                ],
            },
            "counter": {
                "plain": "This old helper is what we are replacing: its window was fixed at 7 and that caused bugs whenever someone needed another window. Don't do it like this:\n{EX}",
                "explicit": "Do not give k a default of 7; the caller must always pass k.",
                "checks": [
                    ("transfer", ("py_test", "NO_DEFAULT_7")),
                    ("leakage", ("regex_absent", r"round\(|Dhaka|temps")),
                ],
            },
        },
        "constraints": [
            ("py_test", "BASIC"),
            ("regex_absent", r"\bprint\s*\("),
        ],
        "marker": ("py_test", "DEFAULT_7"),
        "tests": {
            "BASIC": (
                "assert max_window_sum([1, 2, 3, 4, 5], 2) == 9\n"
                "assert max_window_sum([5, -1, -2, 7], 1) == 7\n"
                "assert max_window_sum([3, 3, 3], 3) == 9\n"
                "assert max_window_sum([-5, -2, -9], 2) == -7\n"
            ),
            "FAST": (
                "import time, random\n"
                "random.seed(0)\n"
                "xs = [random.randint(-100, 100) for _ in range(200000)]\n"
                "t = time.time()\n"
                "max_window_sum(xs, 5000)\n"
                "assert time.time() - t < 2.0, 'too slow'\n"
            ),
            "DEFAULT_7": (
                "import inspect\n"
                "p = inspect.signature(max_window_sum).parameters['k']\n"
                "assert p.default == 7\n"
            ),
            "NO_DEFAULT_7": (
                "import inspect\n"
                "p = inspect.signature(max_window_sum).parameters['k']\n"
                "assert p.default != 7\n"
            ),
        },
    },
    {
        "id": "C2_retry_backoff",
        "family": "code",
        "basis": "A real-style API retry loop with doubling delays",
        "task": "Write a Python function `retry_call(fn, attempts, sleep)` that calls `fn()` until it succeeds and returns its result. Between failed tries it calls `sleep(seconds)`. If all `attempts` tries fail, re-raise the last exception.",
        "rules": "Rules: standard library only; never call time.sleep directly (use the `sleep` argument); no network access; do not print.",
        "format": CODE_FMT,
        "func": "retry_call",
        "example": (
            "```python\n"
            "import time, requests\n\n"
            "def get_forecast():\n"
            "    delay = 1\n"
            "    for attempt in range(5):\n"
            "        try:\n"
            '            return requests.get("https://api.weather.example/forecast", timeout=5).json()\n'
            "        except Exception:\n"
            '            print("Retrying weather API in", delay, "s")\n'
            "            time.sleep(delay)\n"
            "            delay *= 2\n"
            '    raise RuntimeError("weather API down")\n'
            "```"
        ),
        "roles": {
            "analogy": {
                "plain": "Back off between retries in the same spirit as this function:\n{EX}",
                "explicit": "Take only the idea of waiting longer after each failure. Do not copy the weather API, requests, printing or the RuntimeError message.",
                "checks": [
                    ("transfer", ("py_test", "INCREASING")),
                    ("leakage", ("regex_absent", r"weather|forecast|requests")),
                ],
            },
            "requirement": {
                "plain": "Our ops team tuned the delays in this function, so keep exactly the same delays:\n{EX}",
                "explicit": "Copy only the delays: start at 1 second and double after each failure. Do not copy the weather API, requests or printing.",
                "checks": [
                    ("transfer", ("py_test", "DOUBLING")),
                    ("leakage", ("regex_absent", r"weather|forecast|requests")),
                ],
            },
            "counter": {
                "plain": "Users complained that this function made them wait far too long because of how its delays grow. Don't do it like this:\n{EX}",
                "explicit": "Do not let the delay grow; use the same short fixed delay (for example 0.5 seconds) between tries.",
                "checks": [
                    ("transfer", ("py_test", "NOT_INCREASING")),
                    ("leakage", ("regex_absent", r"weather|forecast|requests")),
                ],
            },
        },
        "constraints": [
            ("py_test", "BASIC"),
            ("regex_absent", r"time\.sleep\s*\(|\bprint\s*\("),
        ],
        "marker": ("py_test", "DOUBLING"),
        "tests": {
            "BASIC": (
                "calls = {'n': 0}\n"
                "def flaky():\n"
                "    calls['n'] += 1\n"
                "    if calls['n'] < 3:\n"
                "        raise ValueError('boom')\n"
                "    return 42\n"
                "slept = []\n"
                "assert retry_call(flaky, 5, slept.append) == 42\n"
                "def bad():\n"
                "    raise KeyError('x')\n"
                "try:\n"
                "    retry_call(bad, 3, lambda s: None)\n"
                "    raise AssertionError('should re-raise')\n"
                "except KeyError:\n"
                "    pass\n"
            ),
            "_DELAYS": (
                "state = {'n': 0}\n"
                "def fail4():\n"
                "    state['n'] += 1\n"
                "    if state['n'] <= 4:\n"
                "        raise ValueError('boom')\n"
                "    return 'ok'\n"
                "d = []\n"
                "retry_call(fail4, 6, d.append)\n"
                "d = [float(x) for x in d][:4]\n"
                "assert len(d) == 4, d\n"
            ),
            "INCREASING": "{_DELAYS}assert all(b > a for a, b in zip(d, d[1:])), d\n",
            "NOT_INCREASING": "{_DELAYS}assert not all(b > a for a, b in zip(d, d[1:])), d\n",
            "DOUBLING": "{_DELAYS}assert d == [1.0, 2.0, 4.0, 8.0], d\n",
        },
    },
    {
        "id": "C3_dedupe_usernames",
        "family": "code",
        "basis": "Gmail dot-insensitive address cleaning (real Gmail rule) mapped to forum usernames",
        "task": "Write a Python function `unique_usernames(names)` that removes duplicate usernames from our course forum list and returns the remaining usernames as a list, keeping the order in which they first appear.",
        "rules": "Rules: standard library only.",
        "format": CODE_FMT,
        "func": "unique_usernames",
        "example": (
            "```python\n"
            "def clean_emails(emails):\n"
            '    """Merge duplicate Gmail addresses."""\n'
            "    seen, out = set(), []\n"
            "    for e in emails:\n"
            '        user, domain = e.lower().split("@")\n'
            '        if domain == "gmail.com":\n'
            '            user = user.replace(".", "")\n'
            '        key = user + "@" + domain\n'
            "        if key not in seen:\n"
            "            seen.add(key)\n"
            "            out.append(key)\n"
            "    return out\n"
            "```"
        ),
        "roles": {
            "analogy": {
                "plain": "Our email cleaner below handles duplicates well; do something similar for usernames:\n{EX}",
                "explicit": "Take only the idea of comparing names case-insensitively. Do not remove dots and do not copy anything about email domains.",
                "checks": [
                    ("transfer", ("py_test", "CASE_INSENSITIVE")),
                    ("leakage", ("py_test", "DOTS_KEPT")),
                    ("leakage", ("regex_absent", r"gmail|@")),
                ],
            },
            "requirement": {
                "plain": "Normalise names exactly the way this email cleaner does before comparing them:\n{EX}",
                "explicit": "Copy only the normalisation: lowercase and remove dots. Do not copy anything about email domains.",
                "checks": [
                    ("transfer", ("py_test", "DOTS_REMOVED")),
                    ("leakage", ("regex_absent", r"gmail|@")),
                ],
            },
            "counter": {
                "plain": "This email cleaner wrongly merged two different students because of how it normalises. Don't do it like this:\n{EX}",
                "explicit": "Do not remove dots: 'a.rahman' and 'arahman' are different students.",
                "checks": [
                    ("transfer", ("py_test", "DOTS_KEPT")),
                    ("leakage", ("regex_absent", r"gmail|@")),
                ],
            },
        },
        "constraints": [
            ("py_test", "BASIC"),
        ],
        "marker": ("py_test", "DOTS_REMOVED"),
        "tests": {
            "BASIC": (
                "r = unique_usernames(['amin', 'rafi', 'amin', 'nila'])\n"
                "assert isinstance(r, list)\n"
                "assert [x.lower() for x in r] == ['amin', 'rafi', 'nila'], r\n"
            ),
            "CASE_INSENSITIVE": "assert len(unique_usernames(['Amin', 'amin', 'Rafi'])) == 2\n",
            "DOTS_REMOVED": "assert len(unique_usernames(['a.rahman', 'arahman'])) == 1\n",
            "DOTS_KEPT": "assert len(unique_usernames(['a.rahman', 'arahman'])) == 2\n",
        },
    },
    {
        "id": "C4_pagination",
        "family": "code",
        "basis": "A real-style GitHub API pager that stops on an empty page",
        "task": "Write a Python function `fetch_all(get_page, page_size)` that collects every item from a paginated source. `get_page(n)` returns the list of items on page n (pages start at 1); every full page has `page_size` items.",
        "rules": "Rules: standard library only; no network access; return all items in order.",
        "format": CODE_FMT,
        "func": "fetch_all",
        "example": (
            "```python\n"
            "import requests\n\n"
            "def all_repos(user):\n"
            "    repos, page = [], 1\n"
            "    while True:\n"
            '        r = requests.get(f"https://api.github.com/users/{user}/repos",\n'
            '                         params={"page": page, "per_page": 100})\n'
            "        batch = r.json()\n"
            "        if not batch:\n"
            "            break\n"
            "        repos.extend(batch)\n"
            "        page += 1\n"
            "    return repos\n"
            "```"
        ),
        "roles": {
            "analogy": {
                "plain": "Our GitHub helper below pages through results; write the new one along the same lines:\n{EX}",
                "explicit": "Take only the idea of requesting page after page until the data runs out. Do not copy GitHub, requests or the page size of 100.",
                "checks": [
                    ("transfer", ("py_test", "SMALL_PAGES")),
                    ("leakage", ("regex_absent", r"github|requests|per_page|\b100\b")),
                ],
            },
            "requirement": {
                "plain": "Stop exactly the way this helper stops, so our request logs look the same:\n{EX}",
                "explicit": "Copy only the stopping rule: keep requesting until a page comes back empty. Do not copy GitHub or requests.",
                "checks": [
                    ("transfer", ("py_test", "STOPS_ON_EMPTY")),
                    ("leakage", ("regex_absent", r"github|requests|per_page|\b100\b")),
                ],
            },
            "counter": {
                "plain": "This helper wastes one request every time because of how it decides to stop, and our rate limit punishes that. Don't do it like this:\n{EX}",
                "explicit": "Do not request a page after a short page; stop as soon as a page has fewer than page_size items.",
                "checks": [
                    ("transfer", ("py_test", "STOPS_ON_SHORT")),
                    ("leakage", ("regex_absent", r"github|requests|per_page|\b100\b")),
                ],
            },
        },
        "constraints": [
            ("py_test", "BASIC"),
        ],
        "marker": ("py_test", "STOPS_ON_EMPTY"),
        "tests": {
            "_SRC": (
                "def make(items, size):\n"
                "    log = []\n"
                "    def get_page(n):\n"
                "        log.append(n)\n"
                "        if n > 1000:\n"
                "            raise RuntimeError('runaway loop')\n"
                "        return items[(n - 1) * size: n * size]\n"
                "    return get_page, log\n"
            ),
            "BASIC": "{_SRC}g, log = make(list(range(1, 8)), 3)\nassert fetch_all(g, 3) == list(range(1, 8))\n",
            "SMALL_PAGES": "{_SRC}g, log = make(list('abcde'), 2)\nassert fetch_all(g, 2) == list('abcde')\n",
            "STOPS_ON_EMPTY": "{_SRC}g, log = make(list(range(1, 8)), 3)\nfetch_all(g, 3)\nassert len(log) == 4, log\n",
            "STOPS_ON_SHORT": "{_SRC}g, log = make(list(range(1, 8)), 3)\nfetch_all(g, 3)\nassert len(log) == 3, log\n",
        },
    },
]
