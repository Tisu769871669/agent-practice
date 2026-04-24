# Agent Practice

Agent Practice is an open-source practice platform for learning AI agent engineering through graded, local challenges.

Think of it as a LeetCode-style training lab for agents: browse the route on a static website, clone the repo, solve challenges locally with any framework, and get deterministic feedback from a Python runner.

## What is included

- Static Astro website with a learning path, catalog, and 30 generated challenge detail pages.
- 30-challenge roadmap from foundations to capstone agent systems.
- 10 runnable launch challenges with fixtures, JSON schemas, deterministic graders, and READMEs.
- Local Python runner that writes `result.json` and `transcript.jsonl`.
- Starter templates for raw Python, LangChain, and LangGraph.
- Framework-neutral submission contract: `run(input: dict, context: AgentContext) -> dict`.

The MVP does not include accounts, hosted submissions, cloud execution, hidden hosted tests, forums, or leaderboards.

## Quick start

Install dependencies:

```powershell
python -m pip install -e ".[dev]"
npm install
```

Run the website:

```powershell
npm run web:dev -- --host 127.0.0.1 --port 4321
```

Open `http://127.0.0.1:4321/`.

Run the first challenge with the raw Python starter:

```powershell
New-Item -ItemType Directory -Force submissions
Copy-Item -Recurse templates/raw-python submissions/my-agent
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 001 --submission submissions/my-agent
```

Run verification:

```powershell
python -m pytest -q
npm run web:build
```

## Repository layout

```text
apps/web/                 Static Astro website
challenges/catalog.yaml   Source of truth for catalog metadata
challenges/<id>-<slug>/   Runnable challenge contracts, fixtures, schemas, graders
runner/                   Local runner package
templates/                Raw Python, LangChain, and LangGraph starters
docs/                     Architecture, authoring, grading, and roadmap notes
schemas/                  Shared JSON schemas
tests/                    Runner, template, and challenge tests
```

## Launch runnable set

The first release includes these runnable challenges:

- `001` Echo Agent
- `002` JSON Only
- `003` Tool Picker
- `004` Calculator Agent
- `005` Ticket Triage
- `006` Mini RAG
- `008` Tool Error Recovery
- `010` Two-Step Researcher
- `013` Injection Guard I
- `017` Eval Harness Basics

The other 20 catalog entries are planned so contributors can see the route ahead.
