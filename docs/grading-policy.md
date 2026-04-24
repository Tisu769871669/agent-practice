# Grading Policy

Agent Practice MVP uses deterministic local graders. The goal is reproducible feedback that learners can run without a hosted account, cloud submission, or online judge.

## MVP grading model

- Graders run locally through the Python runner.
- Graders evaluate public fixture cases and recorded outputs.
- Graders return structured reports that can be serialized to `result.json`.
- Graders should be fast, deterministic, and safe to run on a developer machine.
- LLM-as-judge grading is deferred and must not be required for MVP challenges.

## Score reports

Each grader returns a report with:

- `schema_version`
- `challenge_id`
- `challenge_version`
- `runner_version`
- `submission_id`
- `template`
- `score`
- `max_score`
- `passed`
- `duration_ms`
- `metrics`
- `cases`
- `artifacts`

Metrics explain where points came from, such as task success, schema validity, and efficiency. Case results identify the fixture case, score, max score, pass/fail status, duration, and any error.

## Pass thresholds

Each challenge declares its own scoring policy in `challenge.yaml`:

- `max_score`
- `pass_score`
- weighted metric definitions

The launch pattern is a 100 point score with a challenge-specific pass threshold. Simpler extraction tasks may pass around 70, while strict routing, safety, and evaluation tasks generally use 90 so important contract misses do not pass.

## Transcript policy

The runner records `transcript.jsonl` next to `result.json`. Transcript events support auditability and future evaluation work. MVP event types are:

- `case_start`
- `tool_call`
- `tool_result`
- `agent_output`
- `case_end`
- `error`

Graders may inspect transcripts, but they should not require external services.

## Deferred grading features

The MVP does not include:

- hidden hosted fixtures
- cloud execution
- online submissions
- account-linked results
- public leaderboards
- LLM-as-judge scoring

Future hosted submissions may reuse the local result format, but local results and future leaderboard results remain separate.
