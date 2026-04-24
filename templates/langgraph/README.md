# LangGraph Starter

Use this template when you want to solve Agent Practice challenges with a
LangGraph workflow while preserving the standard `run(input, context)` entry
point.

## Copy

Copy this directory to a working location, then edit `solution/agent.py`:

```powershell
New-Item -ItemType Directory -Force submissions
Copy-Item -Recurse templates/langgraph submissions/my-langgraph-agent
```

## Dependencies

Install and configure LangGraph dependencies yourself before building real
graphs. This starter imports LangGraph only if it is available, so the template
can still be inspected and loaded without it.

## Run

Run the local runner against a challenge:

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 001 --submission submissions/my-langgraph-agent
```

The runner imports `solution.agent` and calls `run(input, context)`.
