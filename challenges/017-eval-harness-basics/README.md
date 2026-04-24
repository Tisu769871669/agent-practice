# Eval Harness Basics

## Task

Evaluate a candidate output against an expected answer and a small deterministic rubric. Return each check outcome, the overall pass flag, and a numeric score.

## Input Contract

Each case provides:

```json
{
  "candidate_output": {
    "answer": "Backups run nightly.",
    "citations": ["DOC-1"]
  },
  "expected": {
    "answer_keywords": ["nightly"],
    "citations": ["DOC-1"]
  },
  "rubric": [
    {
      "name": "answer_keywords",
      "description": "Answer contains every required keyword."
    }
  ]
}
```

## Output Contract

Return a JSON object with:

```json
{
  "checks": [
    {
      "name": "answer_keywords",
      "passed": true
    }
  ],
  "passed": true,
  "score": 100
}
```

The `checks` array must preserve the rubric check names and report the deterministic pass/fail result for each check. `score` is a number from 0 to 100.
Compute `score` as an integer percentage: `round(passed_checks / total_checks * 100)`. The public fixtures use whole-number percentages such as `67` for 2 of 3 checks passing.

## Scoring

The deterministic grader checks output schema validity, exact check results, exact overall `passed`, and exact integer score.

## Local Run Command

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 017 --submission path/to/submission --challenges-dir challenges
```

## Common Failure Modes

- Returning only a final score without individual check outcomes.
- Marking the overall result as passed when any check failed.
- Using a 0 to 1 score scale instead of 0 to 100.
- Changing rubric check names or order.
