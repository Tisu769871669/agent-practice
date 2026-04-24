# Two-Step Researcher

## Task

Show a two-step workflow: retrieve relevant evidence before answering, then answer with citations from the retrieved evidence.

## Input Contract

Each case provides a `question` and a small `docs` array. Each document has an `id`, `title`, and `text`.

## Output Contract

Return a JSON object with:

```json
{
  "steps": [
    {
      "type": "retrieve",
      "description": "Retrieved REL-2 because it mentions audit log export."
    },
    {
      "type": "answer",
      "description": "Answered from REL-2."
    }
  ],
  "answer": "Release 2.4 added audit log export.",
  "citations": ["REL-2"]
}
```

The `retrieve` step must appear before the `answer` step.

## Scoring

The deterministic grader checks schema validity, retrieve-before-answer ordering, required answer keywords, and exact citation ids in order.

## Local Run Command

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 010 --submission path/to/submission --challenges-dir challenges
```

## Common Failure Modes

- Answering without a `retrieve` step.
- Listing `answer` before `retrieve`.
- Citing the wrong document id.
- Using general knowledge instead of the documents.
