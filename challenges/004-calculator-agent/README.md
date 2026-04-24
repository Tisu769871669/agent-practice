# Calculator Agent

## Task

Translate the arithmetic request into a calculation expression and return the numeric result. The goal is deterministic arithmetic, not estimation.

## Input Contract

Each case provides a `question` string containing a small arithmetic task.

## Output Contract

Return a JSON object with:

```json
{
  "expression": "(18 + 7) * 4",
  "result": 100
}
```

`expression` should represent the calculation used. `result` must be a JSON number.

## Scoring

The deterministic grader checks schema validity, expression text after whitespace normalization, and the numeric result with a tiny tolerance for floating-point values.

## Local Run Command

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 004 --submission path/to/submission --challenges-dir challenges
```

## Common Failure Modes

- Returning the answer as a string instead of a number.
- Skipping the expression field.
- Making an arithmetic slip on percent, division, or multi-step operations.
- Adding explanatory prose outside the JSON object.
