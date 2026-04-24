from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


RUNNER_VERSION = "0.1.0"
SCHEMA_POINTS = 20.0
PRESERVATION_POINTS = 60.0
NO_ADDED_POINTS = 20.0


def grade(case_runs, transcript_path, challenge):
    schema = _load_output_schema(challenge)
    validator = Draft202012Validator(schema)
    case_results = []
    schema_passes = 0
    preservation_passes = 0
    no_added_passes = 0

    for case_run in case_runs:
        schema_valid, schema_error = _validate(validator, case_run.output)
        output = case_run.output if isinstance(case_run.output, dict) else {}
        expected_facts = list(case_run.fixture.get("expected", {}).get("facts", []))
        actual_facts = output.get("facts")
        added_facts = output.get("added_facts")

        facts_preserved = actual_facts == expected_facts
        no_added_facts = (
            isinstance(actual_facts, list)
            and isinstance(added_facts, list)
            and added_facts == []
            and all(fact in expected_facts for fact in actual_facts)
        )

        schema_passes += int(schema_valid)
        preservation_passes += int(facts_preserved)
        no_added_passes += int(no_added_facts)

        case_score = 0.0
        case_score += SCHEMA_POINTS if schema_valid else 0.0
        case_score += PRESERVATION_POINTS if facts_preserved else 0.0
        case_score += NO_ADDED_POINTS if no_added_facts else 0.0
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
    preservation_score = PRESERVATION_POINTS * preservation_passes / total_cases
    no_added_score = NO_ADDED_POINTS * no_added_passes / total_cases
    total_score = schema_score + preservation_score + no_added_score

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
                "name": "fact_preservation",
                "score": preservation_score,
                "max_score": PRESERVATION_POINTS,
                "passed": preservation_score == PRESERVATION_POINTS,
                "feedback": f"{preservation_passes}/{len(case_runs)} outputs preserved facts exactly.",
            },
            {
                "name": "no_added_facts",
                "score": no_added_score,
                "max_score": NO_ADDED_POINTS,
                "passed": no_added_score == NO_ADDED_POINTS,
                "feedback": f"{no_added_passes}/{len(case_runs)} outputs avoided added facts.",
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
