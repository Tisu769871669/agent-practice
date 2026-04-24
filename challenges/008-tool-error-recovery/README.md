# Tool Error Recovery

## Task

Review prior simulated tool attempts and choose the correct recovery status and next action.

## Input Contract

Each case provides a `goal` and an `attempts` array. Attempts include a `tool`, `status`, optional `result`, optional `error_code`, and optional `error_message`.

## Output Contract

Return a JSON object with:

```json
{
  "final_status": "needs_retry",
  "action": "retry_with_broader_query"
}
```

`final_status` must be one of `recovered`, `needs_retry`, `needs_user`, or `failed`.

## Scoring

The deterministic grader checks schema validity, exact final status, and exact recovery action.

## Local Run Command

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 008 --submission path/to/submission --challenges-dir challenges
```

## Common Failure Modes

- Treating transient errors as permanent failures.
- Retrying invalid user input instead of asking the user for corrected data.
- Reporting success after an empty result set.
- Ignoring a successful retry that appears after an earlier failure.
