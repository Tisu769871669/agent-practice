from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


RUNNER_VERSION = "0.1.0"
SCHEMA_POINTS = 20.0
CATEGORY_POINTS = 40.0
SEVERITY_POINTS = 40.0


def grade(case_runs, transcript_path, challenge):
    schema = _load_output_schema(challenge)
    validator = Draft202012Validator(schema)
    case_results = []
    schema_passes = 0
    category_passes = 0
    severity_passes = 0

    for case_run in case_runs:
        schema_valid, schema_error = _validate(validator, case_run.output)
        output = case_run.output if isinstance(case_run.output, dict) else {}
        expected = case_run.fixture.get("expected", {})

        category_ok = output.get("category") == expected.get("category")
        severity_ok = output.get("severity") == expected.get("severity")

        schema_passes += int(schema_valid)
        category_passes += int(category_ok)
        severity_passes += int(severity_ok)

        case_score = 0.0
        case_score += SCHEMA_POINTS if schema_valid else 0.0
        case_score += CATEGORY_POINTS if category_ok else 0.0
        case_score += SEVERITY_POINTS if severity_ok else 0.0

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
    category_score = CATEGORY_POINTS * category_passes / total_cases
    severity_score = SEVERITY_POINTS * severity_passes / total_cases
    total_score = schema_score + category_score + severity_score

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
                "name": "category_label",
                "score": category_score,
                "max_score": CATEGORY_POINTS,
                "passed": category_score == CATEGORY_POINTS,
                "feedback": f"{category_passes}/{len(case_runs)} categories matched.",
            },
            {
                "name": "severity_label",
                "score": severity_score,
                "max_score": SEVERITY_POINTS,
                "passed": severity_score == SEVERITY_POINTS,
                "feedback": f"{severity_passes}/{len(case_runs)} severities matched.",
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
