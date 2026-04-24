from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


RUNNER_VERSION = "0.1.0"
SCHEMA_POINTS = 20.0
CHECK_POINTS = 40.0
PASSED_POINTS = 20.0
SCORE_POINTS = 20.0


def grade(case_runs, transcript_path, challenge):
    schema = _load_output_schema(challenge)
    validator = Draft202012Validator(schema)
    case_results = []
    schema_passes = 0
    check_passes = 0
    passed_flag_passes = 0
    score_passes = 0

    for case_run in case_runs:
        schema_valid, schema_error = _validate(validator, case_run.output)
        output = case_run.output if isinstance(case_run.output, dict) else {}
        expected = case_run.fixture.get("expected", {})

        checks_ok = output.get("checks") == expected.get("checks")
        passed_ok = output.get("passed") is expected.get("passed")
        score_ok = _integer_score_matches(
            output.get("score"),
            expected.get("score"),
        )

        schema_passes += int(schema_valid)
        check_passes += int(checks_ok)
        passed_flag_passes += int(passed_ok)
        score_passes += int(score_ok)

        case_score = 0.0
        case_score += SCHEMA_POINTS if schema_valid else 0.0
        case_score += CHECK_POINTS if checks_ok else 0.0
        case_score += PASSED_POINTS if passed_ok else 0.0
        case_score += SCORE_POINTS if score_ok else 0.0

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
    check_score = CHECK_POINTS * check_passes / total_cases
    passed_flag_score = PASSED_POINTS * passed_flag_passes / total_cases
    score_value_score = SCORE_POINTS * score_passes / total_cases
    total_score = schema_score + check_score + passed_flag_score + score_value_score

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
                "name": "check_results",
                "score": check_score,
                "max_score": CHECK_POINTS,
                "passed": check_score == CHECK_POINTS,
                "feedback": f"{check_passes}/{len(case_runs)} outputs matched check outcomes.",
            },
            {
                "name": "passed_flag",
                "score": passed_flag_score,
                "max_score": PASSED_POINTS,
                "passed": passed_flag_score == PASSED_POINTS,
                "feedback": f"{passed_flag_passes}/{len(case_runs)} outputs matched the overall pass flag.",
            },
            {
                "name": "score_value",
                "score": score_value_score,
                "max_score": SCORE_POINTS,
                "passed": score_value_score == SCORE_POINTS,
                "feedback": f"{score_passes}/{len(case_runs)} outputs matched the numeric score.",
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


def _integer_score_matches(actual: Any, expected: Any) -> bool:
    return type(actual) is int and type(expected) is int and actual == expected


def _validate(
    validator: Draft202012Validator,
    output: Any,
) -> tuple[bool, str | None]:
    errors = sorted(validator.iter_errors(output), key=lambda error: error.path)
    if not errors:
        return True, None
    return False, errors[0].message
