from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


RUNNER_VERSION = "0.1.0"
SCHEMA_POINTS = 20.0
KEYWORD_POINTS = 40.0
CITATION_POINTS = 40.0


def grade(case_runs, transcript_path, challenge):
    schema = _load_output_schema(challenge)
    validator = Draft202012Validator(schema)
    case_results = []
    schema_passes = 0
    keyword_ratios = []
    citation_passes = 0

    for case_run in case_runs:
        schema_valid, schema_error = _validate(validator, case_run.output)
        output = case_run.output if isinstance(case_run.output, dict) else {}
        expected = case_run.fixture.get("expected", {})

        keywords = expected.get("answer_keywords", [])
        keyword_ratio = _keyword_ratio(output.get("answer"), keywords)
        citations_ok = output.get("citations") == expected.get("citations")

        schema_passes += int(schema_valid)
        keyword_ratios.append(keyword_ratio)
        citation_passes += int(citations_ok)

        case_score = 0.0
        case_score += SCHEMA_POINTS if schema_valid else 0.0
        case_score += KEYWORD_POINTS * keyword_ratio
        case_score += CITATION_POINTS if citations_ok else 0.0

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
    keyword_score = KEYWORD_POINTS * sum(keyword_ratios) / total_cases
    citation_score = CITATION_POINTS * citation_passes / total_cases
    total_score = schema_score + keyword_score + citation_score

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
                "name": "answer_keywords",
                "score": keyword_score,
                "max_score": KEYWORD_POINTS,
                "passed": keyword_score == KEYWORD_POINTS,
                "feedback": "Answer score is the average required-keyword coverage.",
            },
            {
                "name": "citation_ids",
                "score": citation_score,
                "max_score": CITATION_POINTS,
                "passed": citation_score == CITATION_POINTS,
                "feedback": f"{citation_passes}/{len(case_runs)} outputs cited the exact expected ids.",
            },
        ],
        "cases": case_results,
        "artifacts": {"transcript": str(transcript_path)},
    }


def _keyword_ratio(answer: Any, keywords: list[str]) -> float:
    if not isinstance(answer, str) or not keywords:
        return 0.0
    normalized_answer = answer.casefold()
    matches = sum(1 for keyword in keywords if str(keyword).casefold() in normalized_answer)
    return matches / len(keywords)


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
