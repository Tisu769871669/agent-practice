# Roadmap

Agent Practice starts as a static website plus a GitHub repository and local Python runner. The roadmap keeps local learning useful first, then adds automation and hosted features later.

## Stage 1: Local MVP

Stage 1 is the current MVP scope.

- Static Astro website for discovery.
- 30 challenge learning route.
- 10 launch runnable challenges.
- Local Python runner.
- Deterministic graders.
- Raw Python, LangChain, and LangGraph starter templates.
- `result.json` and `transcript.jsonl` artifacts.
- Documentation for local setup and contribution.

Stage 1 explicitly does not include accounts, online submissions, cloud execution, hosted sandboxes, discussion forums, paid model pools, or leaderboards.

## Stage 2: GitHub Actions validation

Public graders can run on forks or pull requests. Results may appear as repository checks or badges. The repository remains the source of truth, and users can still run everything locally.

## Stage 3: Hosted submissions

A cloud API may accept submissions and execute the same runner in an isolated container. Hidden fixtures can live only in the hosted environment. This is the first stage where online submission accounts may become relevant.

## Stage 4: Leaderboard

Leaderboards are only meaningful after hosted submissions exist. Entries should be tied to challenge version and runner version, and metrics may include score, duration, tool calls, estimated cost, and starter template.

## Launch challenge route

The 10 launch runnable challenges are:

1. 001 Echo Agent
2. 002 JSON Only
3. 003 Tool Picker
4. 004 Calculator Agent
5. 005 Ticket Triage
6. 006 Mini RAG
7. 008 Tool Error Recovery
8. 010 Two-Step Researcher
9. 013 Injection Guard I
10. 017 Eval Harness Basics

Runnable IDs: 001, 002, 003, 004, 005, 006, 008, 010, 013, 017.

The remaining 20 planned challenges cover context compression, memory, routing, form filling, human approval, trace audit, conflicting sources, long-running workflows, memory conflict resolution, escalation, regression evaluation, LLM judge calibration, tool-result injection defense, multi-agent handoff, budget-aware routing, adversarial RAG, and a capstone support agent.
