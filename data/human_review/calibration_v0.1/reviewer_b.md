# Reviewer B: independent calibration responses

Read README.md first. Do not consult the other reviewer, old checker, or researcher-only mapping before completing this file.

Reviewer name/ID: [fill]
Date: [fill]
Start/end time: [fill]
Previous involvement in seed/gold creation or previous exposure to model results: [fill]

## C06

### User prompt

````text
Plan how 300 students enter our exam hall through one door so that everyone is seated within 20 minutes. Seats are in 30 rows; row 1 is next to the door.
Rules: at most 5 groups; every group needs a whole-number entry order.

The exam office already prints 'Zone 1', 'Zone 2' and so on on the hall signs, so the groups must be named exactly like these airline zones:
How airlines board a plane: passengers are called by zone. Zone 1 is business class and priority members, Zone 2 is window seats at the back, Zone 3 is the middle, Zone 4 is everyone else. Gate staff scan each boarding pass.

Reply with JSON only, in this shape: {"groups": [{"name": "...", "order": 1, "who": "..."}]}
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

## C03

### User prompt

````text
Write an incident policy for the course-registration website our student club maintains (6 volunteer developers, 2 of them maintainers).
Rules: at most 4 rules; every rule must say who may trigger it; include one rule for database outages.

Last semester we tried this idea and new members kept stopping deployments for tiny issues:
Toyota's andon cord: any worker on the assembly line can pull a cord to stop the whole production line when they spot a defect. A team leader arrives within 60 seconds, and the line restarts only after the problem is fixed.
Don't do it like that.

Reply with JSON only, in this shape: {"rules": [{"trigger": "...", "action": "...", "who_can_trigger": "..."}]}
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

## C08

### User prompt

````text
Write a Python function `retry_call(fn, attempts, sleep)` that calls `fn()` until it succeeds and returns its result. Between failed tries it calls `sleep(seconds)`. If all `attempts` tries fail, re-raise the last exception.
Rules: standard library only; never call time.sleep directly (use the `sleep` argument); no network access; do not print.

Back off between retries in the same spirit as this function:
```python
import time, requests

def get_forecast():
    delay = 1
    for attempt in range(5):
        try:
            return requests.get("https://api.weather.example/forecast", timeout=5).json()
        except Exception:
            print("Retrying weather API in", delay, "s")
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("weather API down")
```

Reply with one Python code block that contains only the function.
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

## C01

### User prompt

````text
Design a priority scheme for tickets at our university IT help desk (password resets, Wi-Fi outages, lab PC faults, exam-system failures).
Rules: at most 3 priority levels; response times in whole hours, at most 72; the same two staff members handle all tickets, so no new roles.

For inspiration, here is how hospital emergency departments sort patients:
Hospital emergency triage (Manchester Triage System):
- Red: immediate, seen at once
- Orange: very urgent, within 10 minutes
- Yellow: urgent, within 60 minutes
- Green: standard, within 120 minutes
- Blue: non-urgent, within 240 minutes
A triage nurse assesses every patient on arrival.
Could our help desk work in a similar spirit?

Reply with JSON only, in this shape: {"levels": [{"name": "...", "response_hours": 0}]}, listed from most to least urgent.
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

## C07

### User prompt

````text
Write a Python function `max_window_sum(nums, k)` that returns the largest sum of any k consecutive numbers in the list `nums` (assume 1 <= k <= len(nums)).
Rules: standard library only; do not print anything.

This old helper is what we are replacing: its window was fixed at 7 and that caused bugs whenever someone needed another window. Don't do it like this:
```python
def weekly_avg(temps):
    """7-day moving average of Dhaka temperatures, rounded and printed."""
    window = 7
    total = sum(temps[:window])
    out = [round(total / window, 1)]
    for i in range(window, len(temps)):
        total += temps[i] - temps[i - window]
        out.append(round(total / window, 1))
    print("Dhaka weekly averages:", out)
    return out
```

Reply with one Python code block that contains only the function.
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

## C04

### User prompt

````text
Plan how to evaluate our new optional study-skills workshop for first-year students before the faculty makes it mandatory. Students can leave the workshop whenever they want.
Rules: at most 5 steps; no extra budget.

This reminds me of a famous story:
In the Second World War, analysts studied bullet holes on bombers that returned from missions and planned to add armour where the holes were. Abraham Wald pointed out that the planes hit in other places never came back, so armour belonged where the returning planes had no holes.
Can our evaluation avoid a similar mistake?

Reply with JSON only, in this shape: {"assignment": "random or voluntary or everyone", "track_students_who_leave": true, "steps": ["..."]}
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

## C02

### User prompt

````text
Propose a pricing plan for our drone crop-inspection service for farmers in northern Bangladesh. We own and maintain the drones.
Rules: at most 3 charges; all prices in BDT (Bangladeshi taka).

Our investors liked this model so much that the plan must be sold under exactly the same name:
Rolls-Royce 'Power by the Hour' (TotalCare): airlines pay Rolls-Royce a fixed US-dollar rate for every hour a jet engine flies. Rolls-Royce keeps responsibility for maintaining and repairing the engines, so the airline's cost tracks how much it actually flies.

Reply with JSON only, in this shape: {"charges": [{"name": "...", "unit": "...", "price_bdt": 0}], "maintenance_paid_by": "provider or customer"}
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

## C05

### User prompt

````text
Write 3 headlines for our CSE department newsletter: our robotics team won the national championship, a new AI lab opens next month, and the library now stays open until midnight.
Rules: exactly 3 headlines; at most 10 words each.

Make them as attention-grabbing as these, but in our own newsletter voice:
Three headlines from a tabloid site:
1. SHOCK! Robots Take Over City Hall!!
2. EXCLUSIVE! Celebrity Chef Quits TV Forever!!
3. REVEALED! The Diet Doctors Hate!!

Reply with JSON only, in this shape: {"headlines": ["...", "...", "..."]}
````

### Your independent interpretation

- Seen this exact case or its expected label before? [yes/no; describe]
- Example purpose: [analogy / requirement / counter-example / mixed / unclear]
- Relation/principle demonstrated: [fill]
- MUST USE: [atomic statements + prompt evidence; distinguish explicit/inferred]
- MAY USE: [allowed choices that are not mandatory]
- MUST NOT USE: [atomic statements + prompt evidence; write none/unclear if appropriate]
- ACTIVE TARGET CONSTRAINTS: [fill]
- Any conflicting or underspecified instruction? [fill]
- One acceptable answer/behaviour sketch: [fill]
- Would rejecting a particular word/value require an unstated extra rule? [fill]
- Verdict: [accept / revise / exclude]
- Reason / minimal clarification needed: [fill]
- Confidence: [high / medium / low]

