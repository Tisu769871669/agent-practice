# Contributing to Agent Practice

Agent Practice is an open-source practice platform for learning agent engineering through runnable, locally graded challenges. The MVP is a static website plus a GitHub repository and a local Python runner. It does not include accounts, cloud submissions, hosted execution, discussion forums, or leaderboards.

## Challenge authoring

Runnable challenges live under `challenges/<id>-<slug>/` and are the source of truth for both the website and the local runner. Each runnable challenge must include:

- `challenge.yaml`
- `README.md`
- `fixtures/public.jsonl`
- `schemas/input.schema.json`
- `schemas/output.schema.json`
- `grader.py`

Challenge metadata should use the MVP status vocabulary: `planned` or `runnable`. The initial launch route contains 30 challenges, with 10 marked runnable for the MVP. Keep challenge statements framework-neutral: submissions expose `run(input: dict, context: AgentContext) -> dict`, while reusable starters live in top-level `templates/raw-python`, `templates/langchain`, and `templates/langgraph`.

## Grader contract

MVP graders are deterministic Python graders. They should not call an LLM, depend on hosted services, or require private fixtures. A grader must evaluate the recorded case outputs and return the stable result shape used by the runner:

- challenge and runner metadata
- score and max score
- pass/fail status
- metric-level scores and feedback
- case-level scores, duration, and errors
- artifact paths such as `transcript.jsonl`

The local runner writes `runs/<challenge_id>/<timestamp>/result.json` and `runs/<challenge_id>/<timestamp>/transcript.jsonl`. Future hosted submissions and leaderboard scoring may use the same contracts, but they are not part of the MVP.

## Starter templates

Starter templates should help learners begin without locking them to one framework. The MVP supports:

- `raw-python`
- `langchain`
- `langgraph`

Each template should include a `submission.yaml`, a `solution/agent.py` file exposing `run(input, context)`, and a short README. Templates must import without making live API calls. Raw Python examples should work without API keys when possible so new users can verify the local runner quickly.

## Pull request checklist

Before opening a pull request, confirm:

- The change stays inside the local MVP scope unless the roadmap explicitly says otherwise.
- New or changed challenges preserve the `run(input, context) -> dict` protocol.
- Graders are deterministic and do not use LLM-as-judge behavior.
- Public fixtures are reproducible and safe to run locally.
- Documentation explains local setup, scoring, and expected artifacts.
- Relevant Python tests pass with `pytest`.
- Website changes build with `npm run web:build` once the Astro app exists.
- No account system, cloud submission flow, hosted sandbox, or leaderboard code has been added for the MVP.
