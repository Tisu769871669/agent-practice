# Agent Practice Design Spec

Date: 2026-04-23

## Product Promise

Agent Practice is a public open-source practice platform for developers who want to learn AI agent engineering the way algorithm learners use LeetCode: by solving progressively harder, graded problems.

The MVP is not an online judge. It is a static website plus a GitHub repository. Users browse the route and challenge statements online, clone the repository, implement solutions locally with their preferred framework, and run a local runner/grader.

## Target User

The first release serves self-learning developers.

Primary needs:

- Understand what to learn first when studying agents.
- Practice agent skills through real tasks rather than passive tutorials.
- Get local, reproducible feedback without paying for a hosted platform.
- Learn LangChain/LangGraph through official templates while remaining free to use another framework.

Secondary users:

- Contributors who want to add challenges, graders, or templates.
- Course authors who want to reuse the challenge format.

## MVP Decisions

- User experience: website for discovery, GitHub clone for execution.
- Website type: static site.
- First route: 30 challenges, 10 runnable at launch.
- Official path: LangChain and LangGraph.
- Challenge protocol: framework-neutral.
- Runner: local Python CLI.
- Grading: deterministic graders first; LLM-as-judge is deferred.
- Output artifacts: `result.json` and `transcript.jsonl`.
- Deferred features: accounts, online submissions, hosted sandbox, leaderboard, discussion forum, paid model pool.

## Homepage Information Architecture

The homepage leads with a learning route, then immediately shows runnable challenges.

Sections:

1. Hero: "Learn agents by solving real, graded challenges."
2. Primary calls to action: "Start the path" and "Clone on GitHub."
3. Route summary: 30 total challenges, 10 runnable, official LangChain/LangGraph path.
4. Stage overview: Foundations, Tools, RAG, Workflows, Safety, Evaluation, Capstone.
5. Runnable challenge preview: 10 launch challenges with difficulty, status, tags, and estimated time.
6. Local workflow: clone, implement, run, inspect feedback.
7. Open-source trust area: GitHub link, contribution guide, roadmap, latest release notes.
8. FAQ and project boundaries.

The homepage should feel like a learning product rather than a marketing splash page. Users should see the route and challenge cards in the first meaningful scroll.

## Core Pages

### Home

Purpose: establish the product and route.

Required data:

- Product promise.
- 30 challenge count.
- 10 runnable count.
- Official framework path.
- Route preview.
- Runnable challenge preview.
- GitHub clone command.
- Contribution entry.

### Learning Path

Purpose: tell learners what to do in what order.

Required data:

- Stages and learning goals.
- Challenge order.
- Difficulty.
- Status: planned, draft, runnable, deprecated.
- Prerequisites.
- Estimated time.
- Tags.

### Challenge Catalog

Purpose: let users find challenges by difficulty or skill.

Required data:

- Search.
- Difficulty filter.
- Status filter.
- Tag filter.
- Challenge title, summary, difficulty, status, tags, estimated time.
- Runnable indicator.

### Challenge Detail

Purpose: let users solve a specific task locally.

Required data:

- Task statement.
- Learning goals.
- Input and output contract.
- Available tools.
- Fixtures description.
- Local run command.
- Scoring rubric.
- Example input and output.
- Common failure modes.
- Links to starter templates.
- Link to the GitHub challenge folder.

### Contributing

Purpose: make external contribution practical.

Required data:

- Repository structure.
- Challenge authoring guide.
- Grader authoring guide.
- Template contribution guide.
- Pull request checklist.
- Labels: `good first issue`, `help wanted`, `runnable`, `planned`.

## User Journey

1. Learner opens homepage.
2. Learner chooses "Start the path."
3. Learner selects the first runnable challenge.
4. Learner clones the repository.
5. Learner copies a starter template or writes a solution with their own framework.
6. Learner runs the local CLI.
7. Runner records a transcript and calls the grader.
8. Learner reads `result.json` feedback and repeats.

## Repository Architecture

```text
agent-practice/
  README.md
  CONTRIBUTING.md
  LICENSE
  pyproject.toml
  package.json

  apps/
    web/
      astro.config.mjs
      src/
        pages/
        components/
        content/
        lib/
      public/

  challenges/
    001-echo-agent/
      challenge.yaml
      README.md
      starter/
        raw-python/
        langchain/
        langgraph/
      fixtures/
        public.jsonl
      schemas/
        input.schema.json
        output.schema.json
      grader.py

  runner/
    agent_practice_runner/
      cli.py
      schemas.py
      loader.py
      execution.py
      transcript.py
      grading.py
      reports.py

  templates/
    raw-python/
    langchain/
    langgraph/

  schemas/
    challenge.schema.json
    submission.schema.json
    result.schema.json
    transcript.schema.json

  docs/
    architecture.md
    challenge-authoring.md
    grading-policy.md
    roadmap.md
```

Boundaries:

- `apps/web` displays challenge data and documentation. It does not execute user code.
- `challenges` is the source of truth for challenge metadata, fixtures, graders, and starter files.
- `runner` loads user submissions, executes cases, records transcripts, calls graders, and writes reports.
- `templates` proves the protocol is framework-neutral while giving guided starting points.
- `schemas` defines stable contracts reused by the website, runner, and future cloud submissions.

## Challenge Model

Every runnable challenge contains:

```text
challenge.yaml
README.md
starter/
fixtures/public.jsonl
schemas/input.schema.json
schemas/output.schema.json
grader.py
```

Minimal `challenge.yaml` fields:

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

## Runner Protocol

User submissions expose:

```python
def run(input: dict, context: AgentContext) -> dict:
    ...
```

`AgentContext` provides:

- `challenge_id`
- `case_id`
- `tools`
- `logger`
- `deadline`
- `metadata`

Runner flow:

1. Read `challenge.yaml`.
2. Read `submission.yaml`.
3. Load the user entrypoint.
4. Run each fixture case.
5. Record transcript events.
6. Call `grader.py`.
7. Write CLI summary.
8. Write `runs/<challenge_id>/<timestamp>/result.json`.
9. Write `runs/<challenge_id>/<timestamp>/transcript.jsonl`.

## Result Format

The runner writes a stable `result.json`:

```json
{
  "schema_version": "0.1",
  "challenge_id": "001",
  "challenge_version": "0.1.0",
  "runner_version": "0.1.0",
  "submission_id": "local",
  "template": "raw-python",
  "score": 86,
  "max_score": 100,
  "passed": true,
  "duration_ms": 8230,
  "metrics": [
    {
      "name": "task_success",
      "score": 55,
      "max_score": 60,
      "passed": true,
      "feedback": "Solved 11/12 cases."
    }
  ],
  "cases": [
    {
      "case_id": "public-001",
      "score": 10,
      "max_score": 10,
      "passed": true,
      "duration_ms": 610,
      "error": null
    }
  ],
  "artifacts": {
    "transcript": "transcript.jsonl",
    "stdout": "stdout.log",
    "stderr": "stderr.log"
  }
}
```

## Launch Challenge Route

The launch route contains 30 challenges. The first 10 runnable challenges are:

1. Echo Agent: stable fact-preserving responses.
2. JSON Only: structured output and schema validity.
3. Tool Picker: choose the correct simulated tool.
4. Calculator Agent: call a deterministic tool instead of guessing.
5. Ticket Triage: classify support tickets.
6. Mini RAG: answer from a small document set with citations.
7. Tool Error Recovery: recover from tool errors and empty results.
8. Two-Step Researcher: retrieve first, answer second.
9. Injection Guard I: treat malicious retrieved text as data, not instruction.
10. Eval Harness Basics: write or inspect a simple deterministic grader.

The remaining 20 planned challenges cover context compression, memory, routing, form filling, human approval, trace audit, conflicting sources, long-running workflows, memory conflict resolution, escalation, regression evaluation, LLM judge calibration, tool-result injection defense, multi-agent handoff, budget-aware routing, adversarial RAG, and a capstone support agent.

## Visual Direction

The site should feel like a serious engineering training lab, not a generic AI landing page.

Design principles:

- Dense and scannable, like a technical console or developer dashboard.
- Learning route visible early.
- Challenge cards use status, difficulty, and tags as primary affordances.
- Avoid purple-gradient AI aesthetics.
- Use restrained colors with a sharp accent for runnable challenges.
- Prefer real product UI over marketing sections.
- Keep the first screen useful: route status, challenge counts, and calls to action.

## Open-Source Strategy

The first release should make contribution obvious:

- Every challenge page links to its GitHub folder.
- Planned challenges are visible so contributors know what to build.
- `CONTRIBUTING.md` explains challenge and grader contracts.
- Issues should be labeled by skill area and difficulty.
- Local results and future leaderboard results remain separate.

## Upgrade Path

Stage 1: local MVP.

- Static website.
- Local runner.
- Deterministic graders.
- GitHub repo as source of truth.

Stage 2: GitHub Actions validation.

- Public graders run on forks or PRs.
- Results can be displayed as badges.

Stage 3: hosted submissions.

- Cloud API accepts submissions.
- Worker runs the same runner inside an isolated container.
- Hidden fixtures live only in the hosted environment.

Stage 4: leaderboard.

- Leaderboard uses only hosted results.
- Entries are tied to challenge version and runner version.
- Metrics include score, duration, tool calls, estimated cost, and template.

## Acceptance Criteria

The MVP is ready to publish when:

- The static site builds successfully.
- The homepage, path page, catalog page, challenge page, and contribution page exist.
- The 30-challenge roadmap appears on the website.
- The first 10 challenges are marked runnable and have folders in `challenges/`.
- At least the first two challenges run end-to-end through the local runner.
- The runner writes `result.json` and `transcript.jsonl`.
- The repository includes raw Python, LangChain, and LangGraph starter templates.
- Documentation explains local setup and challenge contribution.

## Spec Self-Review

- Placeholder scan: no unresolved placeholder markers are present.
- Scope check: online accounts, cloud execution, leaderboards, forums, and hosted model pools are explicitly deferred.
- Consistency check: the website reads challenge metadata; the runner executes challenge folders; schemas are shared by both.
- Ambiguity check: "framework-neutral" means the user only needs to expose the `run(input, context)` entrypoint, while official examples may use LangChain/LangGraph.
