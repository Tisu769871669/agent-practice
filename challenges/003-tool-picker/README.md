# Tool Picker

## Task

Choose the single best simulated tool for the user's request and return the exact arguments needed for that tool. Do not answer the user directly.

## Input Contract

Each case provides a `request` string and an `available_tools` array. Each tool has a `name`, `description`, and `arguments` list describing the expected argument keys.

## Output Contract

Return a JSON object with:

```json
{
  "tool_name": "get_weather",
  "arguments": {
    "location": "Boston",
    "date": "tomorrow"
  }
}
```

`tool_name` must be one of the available tool names. `arguments` must contain exactly the expected keys and values for the fixture.

## Scoring

The deterministic grader awards points for schema validity, exact tool selection, and exact argument matching. Extra or missing argument keys fail the argument check.

## Local Run Command

```powershell
$env:PYTHONPATH = "runner"
python -m agent_practice_runner.cli run 003 --submission path/to/submission --challenges-dir challenges
```

## Common Failure Modes

- Returning a natural-language answer instead of a tool selection.
- Choosing a broad search tool when a specialized tool is available.
- Including extra argument keys not requested by the tool contract.
- Normalizing values too aggressively, such as changing `tomorrow` to an invented date.
