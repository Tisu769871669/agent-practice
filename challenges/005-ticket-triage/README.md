# Ticket Triage

## Task

Classify a support ticket into one category and one severity label.

## Input Contract

Each case provides:

```json
{
  "ticket": {
    "subject": "Cannot sign in after password reset",
    "body": "The reset link worked, but now every login attempt says account locked."
  }
}
```

## Output Contract

Return a JSON object with:

```json
{
  "category": "account",
  "severity": "high"
}
```

`category` must be one of `account`, `billing`, `bug`, `feature`, or `security`. `severity` must be one of `low`, `medium`, `high`, or `critical`.

## Scoring

The deterministic grader awards points for schema validity, exact category label, and exact severity label.

## Local Run Command

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 005 --submission path/to/submission --challenges-dir challenges
```

## Common Failure Modes

- Inventing a category outside the allowed label set.
- Treating account lockouts as generic bugs instead of account issues.
- Underestimating security exposure as medium or high instead of critical.
- Returning explanations instead of only the two labels.
