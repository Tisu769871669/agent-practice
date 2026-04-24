# Challenge Authoring

Agent Practice challenges teach agent engineering through small, runnable tasks with explicit contracts. The MVP route contains 30 challenges, with 10 launch runnable challenges.

The MVP remains local-first: contributors author files in the repository, learners run public fixtures locally, and graders produce local reports. Accounts, cloud submissions, hosted execution, and leaderboards are out of scope for MVP challenge authoring.

## Runnable challenge structure

Each runnable challenge uses this layout:

```text
challenges/001-echo-agent/
  challenge.yaml
  README.md
  fixtures/
    public.jsonl
  schemas/
    input.schema.json
    output.schema.json
  grader.py
```

`challenge.yaml` contains the metadata used by the website and runner. `README.md` explains the task, learning goals, input/output contract, fixtures, local run command, scoring, example input/output, common failure modes, and GitHub folder path. Reusable starter templates live in top-level `templates/`.

The public website also reads `challenges/details.yaml` for rich bilingual runnable challenge statements. When a planned challenge becomes runnable, add English and simplified Chinese detail entries with background, objective, input contract, output contract, scoring, sample input/output, common pitfalls, and a stretch goal.

## Required metadata

A runnable challenge should define:

```yaml
id: "001"
slug: "echo-agent"
title: "Echo Agent"
track: "foundations"
difficulty: "easy"
status: "runnable"
version: "0.1.0"
summary: "Return the important facts from a user message without adding new facts."
tags:
  - instruction-following
  - structured-output
frameworks:
  official:
    - raw-python
    - langchain
    - langgraph
  interface: "framework-neutral"
entrypoint:
  module: "solution.agent"
  callable: "run"
  signature: "run(input: dict, context: AgentContext) -> dict"
schemas:
  input: "schemas/input.schema.json"
  output: "schemas/output.schema.json"
fixtures:
  public: "fixtures/public.jsonl"
limits:
  timeout_seconds: 60
  max_tool_calls: 12
  max_output_chars: 8000
scoring:
  max_score: 100
  pass_score: 70
  metrics:
    - name: "task_success"
      weight: 60
    - name: "schema_validity"
      weight: 20
    - name: "efficiency"
      weight: 20
```

## Submission contract

Submissions are framework-neutral. The runner imports the configured module and calls:

```python
def run(input: dict, context: AgentContext) -> dict:
    ...
```

Official starters can demonstrate raw Python, LangChain, and LangGraph, but a valid solution only needs to satisfy the entrypoint and output schema.

## Fixture guidance

Public fixtures should be JSONL, deterministic, small enough for local execution, and representative of the target behavior. They should avoid secrets and should not depend on a live API. If a challenge uses tools, prefer simulated deterministic tools for the MVP.

## Grader guidance

`grader.py` should score local case runs deterministically and return the shared result report. It should validate schema compliance, core task behavior, and any documented efficiency or safety constraints. Do not add LLM-as-judge behavior for MVP runnable challenges.

Graders should follow APS-1 in `docs/grading-policy.md`: keep `passed` as the score-threshold boolean, and let the runner derive `verdict`, `gates`, and basic `failure_reasons`. If a grader can produce more specific feedback, put it in metric `feedback` or the case `error` field so learners can understand the failed check.

## Status vocabulary

- `planned`: visible on the route, not runnable yet.
- `runnable`: has complete metadata, fixtures, schemas, README, and grader.
