# Architecture

Agent Practice MVP is a local-first, open-source practice platform for agent engineering. It is intentionally not an online judge. Learners discover challenges on a static website, clone the repository, implement a local solution, and run a Python runner/grader on their own machine.

The MVP does not include user accounts, online submissions, hosted sandboxes, paid model pools, discussion forums, or leaderboards.

## System boundaries

- `apps/web` renders the static website from challenge data and documentation. It does not execute user code.
- `challenges` is the source of truth for challenge metadata, statements, fixtures, schemas, and graders.
- `runner/agent_practice_runner` loads local submissions, executes fixture cases, records transcript events, calls graders, and writes reports.
- `templates` contains reusable raw Python, LangChain, and LangGraph starter templates.
- `schemas` defines shared JSON contracts for challenges, submissions, results, and transcripts.
- `docs` explains architecture, authoring, grading, and roadmap decisions.

## Local workflow

1. A learner browses the static site and chooses a runnable challenge.
2. The learner clones the GitHub repository.
3. The learner copies a starter template or writes a framework-neutral submission.
4. The local runner reads `challenge.yaml` and `submission.yaml`.
5. The runner loads the configured `run(input: dict, context: AgentContext) -> dict` entrypoint.
6. Each public fixture case runs locally.
7. The runner records transcript events.
8. The challenge grader returns a deterministic score report.
9. The runner writes `result.json` and `transcript.jsonl` under `runs/<challenge_id>/<timestamp>/`.

## Repository layout

```text
agent-practice/
  README.md
  CONTRIBUTING.md
  LICENSE
  pyproject.toml
  package.json

  apps/web/
  challenges/
  runner/agent_practice_runner/
  templates/
  schemas/
  docs/
```

## Challenge protocol

The runtime protocol is framework-neutral. A submission exposes:

```python
def run(input: dict, context: AgentContext) -> dict:
    ...
```

`AgentContext` provides the challenge id, case id, available tools, logger, deadline, and metadata. Official examples may use raw Python, LangChain, or LangGraph, but the runner only depends on the entrypoint contract.

## Artifacts

Every local run writes:

- `result.json`: score, pass/fail status, metrics, case results, duration, and artifact paths.
- `transcript.jsonl`: one JSON event per line for case starts, tool calls, tool results, agent outputs, case ends, and errors.

These artifacts are local files in the MVP. Hosted result storage and leaderboard aggregation are future-stage capabilities, not MVP features.
