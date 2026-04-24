from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


RUNNER_VERSION = "0.1.0"
SCHEMA_POINTS = 20.0
FIELD_POINTS = 60.0
NULL_DATE_POINTS = 20.0


def grade(case_runs, transcript_path, challenge):
    schema = _load_output_schema(challenge)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    case_results = []
    schema_passes = 0
    field_ratios = []
    null_date_passes = 0
    null_date_cases = 0

    for case_run in case_runs:
        schema_valid, schema_error = _validate(validator, case_run.output)
        output = case_run.output if isinstance(case_run.output, dict) else {}
        expected = case_run.fixture.get("expected", {})

        field_checks = [
            output.get("title") == expected.get("title"),
            output.get("priority") == expected.get("priority"),
            output.get("due_date") == expected.get("due_date"),
        ]

        field_ratio = sum(field_checks) / len(field_checks)
        expects_null_date = expected.get("due_date") is None
        null_date_ok = output.get("due_date") is None if expects_null_date else True

        schema_passes += int(schema_valid)
        field_ratios.append(field_ratio)
        if expects_null_date:
            null_date_cases += 1
            null_date_passes += int(null_date_ok)

        case_score = 0.0
        case_score += SCHEMA_POINTS if schema_valid else 0.0
        case_score += FIELD_POINTS * field_ratio
        case_score += NULL_DATE_POINTS if null_date_ok else 0.0
        error = case_run.error or schema_error

        case_results.append(
            {
                "case_id": case_run.case_id,
                "score": case_score,
                "max_score": challenge.scoring.max_score,
                "passed": case_score == challenge.scoring.max_score,
                "duration_ms": case_run.duration_ms,
                "error": error,
            }
        )

    total_cases = max(1, len(case_runs))
    schema_score = SCHEMA_POINTS * schema_passes / total_cases
    field_score = FIELD_POINTS * sum(field_ratios) / total_cases
    null_date_score = (
        NULL_DATE_POINTS
        if null_date_cases == 0
        else NULL_DATE_POINTS * null_date_passes / null_date_cases
    )
    total_score = schema_score + field_score + null_date_score

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
                "name": "field_extraction",
                "score": field_score,
                "max_score": FIELD_POINTS,
                "passed": field_score == FIELD_POINTS,
                "feedback": "Title, priority, and due_date are scored exactly.",
            },
            {
                "name": "null_date_handling",
                "score": null_date_score,
                "max_score": NULL_DATE_POINTS,
                "passed": null_date_score == NULL_DATE_POINTS,
                "feedback": f"{null_date_passes}/{null_date_cases} missing dates returned null.",
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
