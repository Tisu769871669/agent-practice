# Mini RAG

## Task

Answer the question using only the supplied documents and cite the document ids that support the answer.

## Input Contract

Each case provides a `question` and a `docs` array. Each document has an `id`, `title`, and `text`.

## Output Contract

Return a JSON object with:

```json
{
  "answer": "Employees may use 16 paid volunteer hours per calendar year.",
  "citations": ["HR-1"]
}
```

`citations` must contain document ids from the input docs.

## Scoring

The deterministic grader checks schema validity, required answer keywords, and exact citation ids in order.

## Local Run Command

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 006 --submission path/to/submission --challenges-dir challenges
```

## Common Failure Modes

- Answering from general knowledge instead of the provided documents.
- Omitting a required keyword from the answer.
- Citing every document rather than the document that supports the answer.
- Returning citation titles instead of document ids.
