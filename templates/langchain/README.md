# LangChain Starter

Use this template when you want to solve Agent Practice challenges with a
LangChain-based agent while keeping the runner interface framework-neutral.

## Copy

Copy this directory to a working location, then edit `solution/agent.py`:

```powershell
New-Item -ItemType Directory -Force submissions
Copy-Item -Recurse templates/langchain submissions/my-langchain-agent
```

## Dependencies

Install and configure LangChain dependencies yourself before using real
LangChain models or tools. This starter imports LangChain only if it is
available, so the template can still be inspected and loaded without it.

## Run

Run the local runner against a challenge:

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 001 --submission submissions/my-langchain-agent
```

The runner imports `solution.agent` and calls `run(input, context)`.
