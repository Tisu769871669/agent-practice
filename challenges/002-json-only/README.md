# JSON Only

Extract one task request into a strict JSON object. Return only data from the request.

## Input

Each case provides a `request` string.

```json
{
  "request": "Create a high priority task titled \"Patch staging database\" due on 2026-05-03."
}
```

## Output

Return JSON matching:

```json
{
  "title": "Patch staging database",
  "priority": "high",
  "due_date": "2026-05-03"
}
```

`priority` must be `low`, `medium`, or `high`. If the request has no due date, set `due_date` to `null`.

## Scoring

The deterministic grader checks output schema validity, exact field extraction, and null handling for missing dates.
