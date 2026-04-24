from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


RUNNER_VERSION = "0.1.0"
SCHEMA_POINTS = 20.0
EXPRESSION_POINTS = 20.0
RESULT_POINTS = 60.0
TOLERANCE = 1e-9


def grade(case_runs, transcript_path, challenge):
    schema = _load_output_schema(challenge)
    validator = Draft202012Validator(schema)
    case_results = []
    schema_passes = 0
    expression_passes = 0
    result_passes = 0

    for case_run in case_runs:
        schema_valid, schema_error = _validate(validator, case_run.output)
        output = case_run.output if isinstance(case_run.output, dict) else {}
        expected = case_run.fixture.get("expected", {})

        expression_ok = _normalize_expression(output.get("expression")) == _normalize_expression(
            expected.get("expression")
        )
        result_ok = _numbers_equal(output.get("result"), expected.get("result"))

        schema_passes += int(schema_valid)
        expression_passes += int(expression_ok)
        result_passes += int(result_ok)

        case_score = 0.0
        case_score += SCHEMA_POINTS if schema_valid else 0.0
        case_score += EXPRESSION_POINTS if expression_ok else 0.0
        case_score += RESULT_POINTS if result_ok else 0.0

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
    expression_score = EXPRESSION_POINTS * expression_passes / total_cases
    result_score = RESULT_POINTS * result_passes / total_cases
    total_score = schema_score + expression_score + result_score

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
                "name": "expression_match",
                "score": expression_score,
                "max_score": EXPRESSION_POINTS,
                "passed": expression_score == EXPRESSION_POINTS,
                "feedback": f"{expression_passes}/{len(case_runs)} expressions matched after whitespace normalization.",
            },
            {
                "name": "numeric_result",
                "score": result_score,
                "max_score": RESULT_POINTS,
                "passed": result_score == RESULT_POINTS,
                "feedback": f"{result_passes}/{len(case_runs)} numeric results matched.",
            },
        ],
        "cases": case_results,
        "artifacts": {"transcript": str(transcript_path)},
    }


def _normalize_expression(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return "".join(value.split())


def _numbers_equal(actual: Any, expected: Any) -> bool:
    if not isinstance(actual, int | float) or not isinstance(expected, int | float):
        return False
    return abs(float(actual) - float(expected)) <= TOLERANCE


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
