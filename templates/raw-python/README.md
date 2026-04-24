# Raw Python Starter

Use this template when you want the smallest possible submission: one Python
function with no agent framework dependency.

## Copy

Copy this directory to a working location, then edit `solution/agent.py`:

```powershell
New-Item -ItemType Directory -Force submissions
Copy-Item -Recurse templates/raw-python submissions/my-raw-python-agent
```

## Run

Run the local runner against a challenge:

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 001 --submission submissions/my-raw-python-agent
```

The runner imports `solution.agent` and calls `run(input, context)`.
