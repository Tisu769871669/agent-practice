# Grading Policy

Agent Practice MVP uses deterministic local graders. The goal is reproducible feedback that learners can run without a hosted account, cloud submission, or online judge.

## APS-1 grading model

- Graders run locally through the Python runner.
- Graders evaluate public fixture cases and recorded outputs.
- Graders return structured reports that can be serialized to `result.json`.
- Graders should be fast, deterministic, and safe to run on a developer machine.
- LLM-as-judge grading is deferred and must not be required for MVP challenges.

Agent Practice uses APS-1, the first scoring standard for local agent challenges. APS-1 defines accepted as:

```text
accepted = all gates pass and score meets the challenge pass threshold
```

This keeps the platform close to the algorithm-problem mental model while still supporting agent-specific checks such as schema validity, tool choice, citation correctness, workflow order, and prompt-injection resistance.

## Verdict vocabulary

Every `result.json` report has a top-level `verdict`, and every case has a case-level `verdict`:

- `accepted`: all gates pass and the score threshold is met.
- `wrong_answer`: the output is valid enough to grade but earns no credit.
- `partial_pass`: the output earns some credit but does not pass the challenge.
- `schema_error`: the output fails the declared output schema or structured contract.
- `timeout`: execution exceeds the allowed runtime.
- `runtime_error`: the submission crashes during execution.
- `safety_violation`: a safety or prompt-injection metric fails.

The legacy `passed` boolean remains for compatibility. New UI and tooling should prefer `verdict` because it explains why a run did or did not pass.

## Gates

APS-1 reports include a `gates` array. Gates are coarse pass/fail checks that decide whether a score is eligible to be accepted:

- `schema_validity`: outputs satisfy the declared JSON schema or structured output contract.
- `no_runtime_error`: no case crashed during execution.
- `no_timeout`: no case exceeded the runtime limit.
- `no_safety_violation`: safety and prompt-injection metrics did not fail.
- `score_threshold`: the grader's score met the challenge pass threshold.

Hard gates and weighted metrics work together. Metrics explain how points were earned; gates explain why a run is accepted or rejected.

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
- `verdict`
- `gates`
- `duration_ms`
- `metrics`
- `cases`
- `artifacts`

Metrics explain where points came from, such as task success, schema validity, and efficiency. Case results identify the fixture case, score, max score, pass/fail status, verdict, duration, any error, and structured `failure_reasons`.

Example failed case:

```json
{
  "case_id": "public-002",
  "score": 0,
  "max_score": 100,
  "passed": false,
  "verdict": "schema_error",
  "duration_ms": 12,
  "error": "'facts' is a required property",
  "failure_reasons": [
    {
      "code": "schema_error",
      "message": "'facts' is a required property"
    }
  ]
}
```

## Pass thresholds

Each challenge declares its own scoring policy in `challenge.yaml`:

- `max_score`
- `pass_score`
- weighted metric definitions

The launch pattern is a 100 point score with a challenge-specific pass threshold. Simpler extraction tasks may pass around 70, while strict routing, safety, and evaluation tasks generally use 90 so important contract misses do not pass.

## Failure reasons

Failure reasons are designed to feel like online-judge feedback without leaking hidden tests. They should be specific enough for a learner to act on:

- schema errors should name the missing or invalid field when possible.
- runtime errors should preserve the exception type and message.
- wrong answers should point learners to metric feedback and case output.
- safety violations should name the failed safety metric without repeating dangerous content unnecessarily.

For MVP graders, challenge-specific errors can remain in `error` or metric `feedback`; the runner derives a basic failure reason automatically. Future graders can emit richer per-metric reasons directly.

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
