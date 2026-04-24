from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


RUNNER_VERSION = "0.1.0"
SCHEMA_POINTS = 20.0
TOOL_POINTS = 40.0
ARGUMENT_POINTS = 40.0


def grade(case_runs, transcript_path, challenge):
    schema = _load_output_schema(challenge)
    validator = Draft202012Validator(schema)
    case_results = []
    schema_passes = 0
    tool_passes = 0
    argument_passes = 0

    for case_run in case_runs:
        schema_valid, schema_error = _validate(validator, case_run.output)
        output = case_run.output if isinstance(case_run.output, dict) else {}
        expected = case_run.fixture.get("expected", {})

        tool_ok = output.get("tool_name") == expected.get("tool_name")
        arguments_ok = output.get("arguments") == expected.get("arguments")

        schema_passes += int(schema_valid)
        tool_passes += int(tool_ok)
        argument_passes += int(arguments_ok)

        case_score = 0.0
        case_score += SCHEMA_POINTS if schema_valid else 0.0
        case_score += TOOL_POINTS if tool_ok else 0.0
        case_score += ARGUMENT_POINTS if arguments_ok else 0.0

        case_results.append(
            {
                "case_id": case_run.case_id,
                "score": case_score,
                "max_score": challenge.scoring.max_score,
                "passed": case_score == challenge.scoring.max_score,
                "duration_ms": case_run.duration_ms,
                "error": case_run.error or schema_error,
            }
        )

    total_cases = max(1, len(case_runs))
    schema_score = SCHEMA_POINTS * schema_passes / total_cases
    tool_score = TOOL_POINTS * tool_passes / total_cases
    argument_score = ARGUMENT_POINTS * argument_passes / total_cases
    total_score = schema_score + tool_score + argument_score

    return {
        "schema_version": "0.1",
        "challenge_id": challenge.id,
        "challenge_version": challenge.version,
        "runner_version": RUNNER_VERSION,
        "submission_id": "local",
        "template": "unknown",
        "score": total_score,
        "max_score": challenge.scoring.max_score,
        "passed": total_score >= challenge.scoring.pass_score,
        "duration_ms": sum(case.duration_ms for case in case_runs),
        "metrics": [
            {
                "name": "schema_validity",
                "score": schema_score,
                "max_score": SCHEMA_POINTS,
                "passed": schema_score == SCHEMA_POINTS,
                "feedback": f"{schema_passes}/{len(case_runs)} outputs matched the schema.",
            },
            {
                "name": "tool_selection",
                "score": tool_score,
                "max_score": TOOL_POINTS,
                "passed": tool_score == TOOL_POINTS,
                "feedback": f"{tool_passes}/{len(case_runs)} outputs selected the expected tool.",
            },
            {
                "name": "argument_exactness",
                "score": argument_score,
                "max_score": ARGUMENT_POINTS,
                "passed": argument_score == ARGUMENT_POINTS,
                "feedback": f"{argument_passes}/{len(case_runs)} outputs matched arguments exactly.",
            },
        ],
        "cases": case_results,
        "artifacts": {"transcript": str(transcript_path)},
    }


def _load_output_schema(challenge: Any) -> dict[str, Any]:
    schema_path = Path(__file__).parent / (challenge.schemas or {}).get(
        "output",
        "schemas/output.schema.json",
    )
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _validate(
    validator: Draft202012Validator,
    output: Any,
) -> tuple[bool, str | None]:
    errors = sorted(validator.iter_errors(output), key=lambda error: error.path)
    if not errors:
        return True, None
    return False, errors[0].message
