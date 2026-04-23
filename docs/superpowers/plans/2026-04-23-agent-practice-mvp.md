# Agent Practice MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first open-source Agent Practice MVP: a static challenge website plus a local Python runner/grader protocol.

**Architecture:** Challenge metadata in `challenges/` is the source of truth. The Python runner executes local submissions and writes reports. The Astro static site reads generated challenge metadata and renders the learning route, catalog, challenge pages, and contribution docs.

**Tech Stack:** Python 3.12, Pydantic, Typer, pytest, jsonschema, Node.js 24, Astro, TypeScript, plain CSS, npm scripts.

---

## File Structure

The implementation creates these major areas:

- `pyproject.toml`: Python package metadata, dependencies, pytest configuration.
- `package.json`: website scripts and Node dependencies.
- `schemas/`: JSON schema contracts for challenge, submission, result, and transcript.
- `runner/agent_practice_runner/`: local CLI, schema models, loader, executor, transcript writer, grader adapter, report writer.
- `tests/runner/`: pytest tests for runner behavior.
- `challenges/`: 30 challenge folders, with 10 runnable launch challenges.
- `templates/`: starter templates for raw Python, LangChain, and LangGraph.
- `apps/web/`: Astro static site.
- `docs/`: architecture, authoring, grading, and roadmap docs.

Implementation tasks are intentionally sequenced. Do not start website rendering before challenge metadata and generated catalog data exist.

## Task 1: Bootstrap Project Tooling

**Files:**

- Create: `pyproject.toml`
- Create: `package.json`
- Create: `CONTRIBUTING.md`
- Create: `LICENSE`
- Create: `docs/architecture.md`
- Create: `docs/grading-policy.md`
- Create: `docs/challenge-authoring.md`
- Create: `docs/roadmap.md`

- [ ] **Step 1: Add Python package configuration**

Create `pyproject.toml` with package name `agent-practice`, Python requirement `>=3.12`, dependencies `pydantic`, `typer`, `jsonschema`, `pyyaml`, and dev dependency `pytest`.

- [ ] **Step 2: Add Node package configuration**

Create `package.json` with scripts:

```json
{
  "scripts": {
    "web:dev": "astro dev --root apps/web",
    "web:build": "astro build --root apps/web",
    "test:py": "pytest",
    "test": "pytest && npm run web:build"
  }
}
```

- [ ] **Step 3: Add open-source docs**

Create `CONTRIBUTING.md`, `LICENSE`, and the four `docs/*.md` files. Each doc must describe the MVP contracts already approved in `docs/superpowers/specs/2026-04-23-agent-practice-design.md`.

- [ ] **Step 4: Verify baseline metadata**

Run:

```powershell
git status --short
```

Expected: new project files are visible, with no files outside `agent-practice/` modified by this task.

## Task 2: Define Shared Schemas

**Files:**

- Create: `schemas/challenge.schema.json`
- Create: `schemas/submission.schema.json`
- Create: `schemas/result.schema.json`
- Create: `schemas/transcript.schema.json`
- Create: `runner/agent_practice_runner/__init__.py`
- Create: `runner/agent_practice_runner/schemas.py`
- Create: `tests/runner/test_schemas.py`

- [ ] **Step 1: Write failing schema tests**

Create `tests/runner/test_schemas.py` with tests that validate:

- A minimal runnable challenge config parses successfully.
- A challenge config without `id` fails.
- A valid result report parses successfully.
- A transcript event with an unknown type fails.

Run:

```powershell
python -m pytest tests/runner/test_schemas.py -v
```

Expected: tests fail because schema models do not exist.

- [ ] **Step 2: Add JSON schema contracts**

Create the four JSON schema files. The challenge schema must require `id`, `slug`, `title`, `track`, `difficulty`, `status`, `version`, `summary`, `tags`, `entrypoint`, `fixtures`, `limits`, and `scoring`.

- [ ] **Step 3: Add Pydantic models**

Create `runner/agent_practice_runner/schemas.py` with Pydantic models:

- `ChallengeConfig`
- `EntrypointConfig`
- `FixtureConfig`
- `LimitsConfig`
- `ScoringConfig`
- `ScoringMetric`
- `SubmissionConfig`
- `GradeMetric`
- `GradeCase`
- `GradeReport`
- `TranscriptEvent`

Allowed transcript event types are `case_start`, `tool_call`, `tool_result`, `agent_output`, `case_end`, and `error`.

- [ ] **Step 4: Verify schemas**

Run:

```powershell
python -m pytest tests/runner/test_schemas.py -v
```

Expected: all tests pass.

## Task 3: Build Loader, Transcript, and Report Primitives

**Files:**

- Create: `runner/agent_practice_runner/loader.py`
- Create: `runner/agent_practice_runner/transcript.py`
- Create: `runner/agent_practice_runner/reports.py`
- Create: `tests/runner/test_loader.py`
- Create: `tests/runner/test_transcript.py`
- Create: `tests/runner/test_reports.py`

- [ ] **Step 1: Write failing loader tests**

Tests must cover:

- `load_challenge(path)` reads `challenge.yaml` and returns `ChallengeConfig`.
- `load_jsonl(path)` returns a list of dictionaries.
- Missing challenge file raises `FileNotFoundError`.

Run:

```powershell
python -m pytest tests/runner/test_loader.py -v
```

Expected: fail because loader functions do not exist.

- [ ] **Step 2: Implement loader**

Implement `load_challenge`, `load_submission`, and `load_jsonl` using `yaml.safe_load`, `json.loads`, and Pydantic validation.

- [ ] **Step 3: Write failing transcript tests**

Tests must cover:

- `TranscriptWriter.write_event()` appends JSONL.
- `TranscriptWriter` rejects unknown event types through `TranscriptEvent`.
- Events include a timestamp field.

- [ ] **Step 4: Implement transcript writer**

Create a small class that writes one JSON object per line and validates each event with `TranscriptEvent`.

- [ ] **Step 5: Write failing report tests**

Tests must cover:

- `write_result(report, path)` writes valid JSON.
- `summarize_result(report)` includes score and pass/fail status.

- [ ] **Step 6: Implement report helpers**

Implement deterministic JSON writing with sorted keys and a concise CLI summary string.

- [ ] **Step 7: Verify primitives**

Run:

```powershell
python -m pytest tests/runner/test_loader.py tests/runner/test_transcript.py tests/runner/test_reports.py -v
```

Expected: all tests pass.

## Task 4: Build Runner Execution and CLI

**Files:**

- Create: `runner/agent_practice_runner/context.py`
- Create: `runner/agent_practice_runner/execution.py`
- Create: `runner/agent_practice_runner/grading.py`
- Create: `runner/agent_practice_runner/cli.py`
- Create: `tests/runner/test_execution.py`
- Create: `tests/runner/test_cli.py`

- [ ] **Step 1: Write failing execution tests**

Tests must create a temporary challenge and a temporary submission module. They must assert:

- The runner calls `run(input, context)` once per fixture case.
- The context exposes `challenge_id`, `case_id`, `tools`, and `metadata`.
- Execution errors are captured into a failed case instead of crashing the whole run.

- [ ] **Step 2: Implement execution core**

Implement:

- `AgentContext`
- `CaseRun`
- `run_cases(challenge, submission, fixtures, output_dir)`

The executor should import the configured module with `importlib`, call the configured callable, measure duration, and write transcript events.

- [ ] **Step 3: Write failing grading adapter tests**

Tests must assert:

- A challenge `grader.py` exposing `grade(case_runs, transcript_path, challenge)` is loaded.
- The returned dictionary is validated as `GradeReport`.
- Missing `grade` raises a clear error.

- [ ] **Step 4: Implement grader adapter**

Implement `load_grader(challenge_dir)` and `grade_cases(...)`.

- [ ] **Step 5: Write failing CLI tests**

Use Typer's test runner to assert:

- `agent-practice run 001 --submission path/to/submission.yaml` exits with code 0 on a passing sample.
- The command writes `result.json` and `transcript.jsonl`.
- Unknown challenge id exits with a non-zero code and a clear message.

- [ ] **Step 6: Implement CLI**

Expose `agent-practice run <challenge_id> --submission <path> --challenges-dir challenges --runs-dir runs`.

- [ ] **Step 7: Verify runner**

Run:

```powershell
python -m pytest tests/runner/test_execution.py tests/runner/test_cli.py -v
```

Expected: all tests pass.

## Task 5: Create Launch Challenge Metadata and First Two Runnable Challenges

**Files:**

- Create: `challenges/001-echo-agent/**`
- Create: `challenges/002-json-only/**`
- Create: `challenges/catalog.yaml`
- Create: `tests/challenges/test_challenge_catalog.py`

- [ ] **Step 1: Write failing catalog tests**

Tests must assert:

- `challenges/catalog.yaml` contains 30 challenge entries.
- Exactly 10 entries have `status: runnable`.
- Challenge IDs are unique.
- The first two challenge folders contain `challenge.yaml`, `README.md`, `fixtures/public.jsonl`, `schemas/input.schema.json`, `schemas/output.schema.json`, and `grader.py`.

- [ ] **Step 2: Create 30-entry catalog**

Use the approved route:

1. Echo Agent
2. JSON Only
3. Tool Picker
4. Calculator Agent
5. Ticket Triage
6. Mini RAG
7. Context Window Diet
8. Tool Error Recovery
9. Personal Memory Lite
10. Two-Step Researcher
11. Prompt Router
12. Form Filler Agent
13. Injection Guard I
14. Unit Test Explainer
15. Email Assistant with Approval
16. Meeting Memory
17. Eval Harness Basics
18. ReAct Trace Auditor
19. Multi-Tool Planner
20. RAG with Conflicting Sources
21. Long-Running Workflow
22. Memory Conflict Resolver
23. Human Escalation Agent
24. Regression Eval Suite
25. Agent Judge Calibration
26. Injection Guard II
27. Multi-Agent Handoff
28. Budget-Aware Agent
29. Adversarial RAG Challenge
30. Capstone Support Agent

Mark challenges 1, 2, 3, 4, 5, 6, 8, 10, 13, and 17 as `runnable`; mark the rest as `planned`.

- [ ] **Step 3: Implement challenge 001**

Challenge 001 requires output containing:

```json
{
  "facts": ["..."],
  "added_facts": []
}
```

The grader scores schema validity, preservation of expected facts, and absence of added facts.

- [ ] **Step 4: Implement challenge 002**

Challenge 002 requires output matching a task object:

```json
{
  "title": "...",
  "priority": "low",
  "due_date": null
}
```

The grader scores JSON schema validity, field extraction, and null handling for missing dates.

- [ ] **Step 5: Verify challenge fixtures and graders**

Run:

```powershell
python -m pytest tests/challenges/test_challenge_catalog.py -v
```

Expected: all tests pass.

## Task 6: Add Starter Templates

**Files:**

- Create: `templates/raw-python/**`
- Create: `templates/langchain/**`
- Create: `templates/langgraph/**`
- Create: `tests/templates/test_templates.py`

- [ ] **Step 1: Write failing template tests**

Tests must assert every template contains:

- `submission.yaml`
- `solution/agent.py`
- `README.md`

Tests must import each `solution.agent` and assert a callable `run(input, context)` exists.

- [ ] **Step 2: Implement raw Python template**

The raw template should solve challenge 001 without external LLM calls, so users can verify the runner without API keys.

- [ ] **Step 3: Implement LangChain template**

The LangChain template should show the same `run(input, context)` interface and include comments where the user wires their model. It should not require a live API call during import.

- [ ] **Step 4: Implement LangGraph template**

The LangGraph template should show a minimal state graph wrapper around the same entrypoint. It should not require a live API call during import.

- [ ] **Step 5: Verify templates**

Run:

```powershell
python -m pytest tests/templates/test_templates.py -v
```

Expected: all tests pass.

## Task 7: Expand to 10 Runnable Challenge Folders

**Files:**

- Create: `challenges/003-tool-picker/**`
- Create: `challenges/004-calculator-agent/**`
- Create: `challenges/005-ticket-triage/**`
- Create: `challenges/006-mini-rag/**`
- Create: `challenges/008-tool-error-recovery/**`
- Create: `challenges/010-two-step-researcher/**`
- Create: `challenges/013-injection-guard-i/**`
- Create: `challenges/017-eval-harness-basics/**`
- Modify: `tests/challenges/test_challenge_catalog.py`

- [ ] **Step 1: Extend failing catalog test**

Add assertions that all 10 runnable entries have folders and required files.

- [ ] **Step 2: Add deterministic fixtures**

Each runnable challenge must have at least 3 public fixture cases.

- [ ] **Step 3: Add graders**

Each grader must return the shared `GradeReport` shape and avoid LLM-as-judge.

- [ ] **Step 4: Add README files**

Each runnable challenge README must contain task, input contract, output contract, scoring, local run command, and common failure modes.

- [ ] **Step 5: Verify all runnable challenge folders**

Run:

```powershell
python -m pytest tests/challenges/test_challenge_catalog.py -v
```

Expected: all tests pass.

## Task 8: Build Static Website

**Files:**

- Create: `apps/web/astro.config.mjs`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/src/pages/index.astro`
- Create: `apps/web/src/pages/path.astro`
- Create: `apps/web/src/pages/challenges/index.astro`
- Create: `apps/web/src/pages/challenges/[slug].astro`
- Create: `apps/web/src/pages/contribute.astro`
- Create: `apps/web/src/components/Layout.astro`
- Create: `apps/web/src/components/ChallengeCard.astro`
- Create: `apps/web/src/components/RouteTimeline.astro`
- Create: `apps/web/src/lib/challenges.ts`
- Create: `apps/web/src/styles/global.css`

- [ ] **Step 1: Add Astro app skeleton**

Create a minimal Astro app in `apps/web`.

- [ ] **Step 2: Add challenge data loader**

`apps/web/src/lib/challenges.ts` must read `challenges/catalog.yaml` at build time and expose typed challenge records.

- [ ] **Step 3: Build homepage**

Homepage must show:

- Product promise.
- 30 challenge count.
- 10 runnable count.
- "Start the path" CTA.
- "Clone on GitHub" CTA.
- Route overview.
- Runnable challenge preview.
- Local workflow.

- [ ] **Step 4: Build route and catalog pages**

Path page must show stages and challenge order. Catalog page must show all challenges with difficulty, status, and tags.

- [ ] **Step 5: Build challenge detail pages**

Each challenge detail page must include learning goals, local run command, status, difficulty, tags, and GitHub folder path.

- [ ] **Step 6: Build contribution page**

Contribution page must explain challenge authoring, grader authoring, starter templates, and PR checklist.

- [ ] **Step 7: Apply visual direction**

Use the `frontend-design` guidance: serious engineering training lab, dense but readable, restrained palette with sharp runnable accent, no generic purple-gradient AI landing page, no nested cards, and responsive text that does not overflow.

- [ ] **Step 8: Verify website build**

Run:

```powershell
npm install
npm run web:build
```

Expected: Astro build exits with code 0.

## Task 9: End-to-End Verification and Release Polish

**Files:**

- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `docs/architecture.md`
- Modify: `docs/grading-policy.md`
- Modify: `docs/challenge-authoring.md`
- Modify: `docs/roadmap.md`

- [ ] **Step 1: Verify Python tests**

Run:

```powershell
python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: Verify website build**

Run:

```powershell
npm run web:build
```

Expected: build exits with code 0.

- [ ] **Step 3: Verify first local challenge run**

Run challenge 001 with the raw Python starter.

Expected artifacts:

```text
runs/001-echo-agent/<timestamp>/result.json
runs/001-echo-agent/<timestamp>/transcript.jsonl
```

- [ ] **Step 4: Review docs for launch clarity**

Docs must tell users:

- What Agent Practice is.
- How to clone and run a challenge.
- How to choose raw Python, LangChain, or LangGraph.
- How to add a challenge.
- What is deferred beyond MVP.

- [ ] **Step 5: Final review**

Run:

```powershell
git status --short
```

Expected: only intentional project files are modified.

## Execution Notes for Subagents

- Do not touch files outside `agent-practice/`.
- Do not edit files owned by another active implementer.
- Follow TDD for Python runner behavior.
- Use deterministic graders only.
- Do not add account systems, cloud execution, or leaderboard code.
- Keep official examples LangChain/LangGraph-friendly, but keep the runtime protocol framework-neutral.
- Commit after each completed task when running inside a git worktree.

## Plan Self-Review

- Spec coverage: product pages, challenge route, local runner, result artifacts, templates, and contribution docs are all mapped to tasks.
- Placeholder scan: no unresolved placeholder markers are present.
- Type consistency: all tasks use the same entrypoint `run(input, context) -> dict`, report artifact names, and status vocabulary.
- Scope control: cloud submissions and leaderboards are documented as future upgrades, not MVP implementation tasks.
