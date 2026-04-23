import sys
from pathlib import Path

import pytest
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.schemas import (  # noqa: E402
    ChallengeConfig,
    GradeReport,
    SubmissionConfig,
    TranscriptEvent,
)


def minimal_challenge_config() -> dict:
    return {
        "id": "001",
        "slug": "echo-agent",
        "title": "Echo Agent",
        "track": "foundations",
        "difficulty": "easy",
        "status": "runnable",
        "version": "0.1.0",
        "summary": "Return important facts without adding new facts.",
        "tags": ["instruction-following", "structured-output"],
        "entrypoint": {
            "module": "solution.agent",
            "callable": "run",
            "signature": "run(input: dict, context: AgentContext) -> dict",
        },
        "fixtures": {
            "public": "fixtures/public.jsonl",
        },
        "limits": {
            "timeout_seconds": 60,
            "max_tool_calls": 12,
            "max_output_chars": 8000,
        },
        "scoring": {
            "max_score": 100,
            "pass_score": 70,
            "metrics": [
                {
                    "name": "task_success",
                    "weight": 60,
                },
                {
                    "name": "schema_validity",
                    "weight": 20,
                },
            ],
        },
    }


def minimal_submission_config() -> dict:
    return {
        "template": "raw-python",
        "entrypoint": {
            "module": "solution.agent",
            "callable": "run",
        },
    }


def minimal_grade_report() -> dict:
    return {
        "schema_version": "0.1",
        "challenge_id": "001",
        "challenge_version": "0.1.0",
        "runner_version": "0.1.0",
        "submission_id": "local",
        "template": "raw-python",
        "score": 86,
        "max_score": 100,
        "passed": True,
        "duration_ms": 8230,
        "metrics": [
            {
                "name": "task_success",
                "score": 55,
                "max_score": 60,
                "passed": True,
                "feedback": "Solved 11/12 cases.",
            }
        ],
        "cases": [
            {
                "case_id": "public-001",
                "score": 10,
                "max_score": 10,
                "passed": True,
                "duration_ms": 610,
                "error": None,
            }
        ],
        "artifacts": {
            "transcript": "transcript.jsonl",
            "stdout": "stdout.log",
            "stderr": "stderr.log",
        },
    }


def test_minimal_runnable_challenge_config_parses() -> None:
    challenge = ChallengeConfig(**minimal_challenge_config())

    assert challenge.id == "001"
    assert challenge.status == "runnable"
    assert challenge.entrypoint.module == "solution.agent"
    assert challenge.scoring.metrics[0].name == "task_success"


def test_challenge_config_without_id_fails() -> None:
    config = minimal_challenge_config()
    del config["id"]

    with pytest.raises(ValidationError):
        ChallengeConfig(**config)


def test_valid_grade_report_parses() -> None:
    report = GradeReport(**minimal_grade_report())

    assert report.passed is True
    assert report.metrics[0].max_score == 60
    assert report.cases[0].error is None


def test_unknown_transcript_event_type_fails() -> None:
    with pytest.raises(ValidationError):
        TranscriptEvent(
            type="not_a_real_event",
            case_id="public-001",
            timestamp="2026-04-23T00:00:00Z",
        )


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "id": "",
            },
        ),
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "slug": "",
            },
        ),
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "title": "",
            },
        ),
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "track": "",
            },
        ),
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "version": "",
            },
        ),
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "summary": "",
            },
        ),
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "entrypoint": {
                    **minimal_challenge_config()["entrypoint"],
                    "module": "",
                },
            },
        ),
        (
            ChallengeConfig,
            {
                **minimal_challenge_config(),
                "entrypoint": {
                    **minimal_challenge_config()["entrypoint"],
                    "callable": "",
                },
            },
        ),
        (
            SubmissionConfig,
            {
                **minimal_submission_config(),
                "template": "",
            },
        ),
        (
            GradeReport,
            {
                **minimal_grade_report(),
                "template": "",
            },
        ),
    ],
)
def test_empty_required_strings_fail(model: type, payload: dict) -> None:
    with pytest.raises(ValidationError):
        model(**payload)


def test_invalid_timestamp_format_fails() -> None:
    with pytest.raises(ValidationError):
        TranscriptEvent(
            type="case_start",
            case_id="public-001",
            timestamp="not-a-date",
        )


@pytest.mark.parametrize(
    "entrypoint_update",
    [
        {"signature": None},
        {"module": "solution.agent", "callable": "run", "signature": None},
    ],
)
def test_signature_null_fails_when_present(entrypoint_update: dict) -> None:
    config = minimal_submission_config()
    config["entrypoint"] = {
        **config["entrypoint"],
        **entrypoint_update,
    }

    with pytest.raises(ValidationError):
        SubmissionConfig(**config)


def test_hidden_null_fails_when_present() -> None:
    config = minimal_challenge_config()
    config["fixtures"] = {
        **config["fixtures"],
        "hidden": None,
    }

    with pytest.raises(ValidationError):
        ChallengeConfig(**config)


def test_extra_fixture_value_must_be_string() -> None:
    config = minimal_challenge_config()
    config["fixtures"] = {
        **config["fixtures"],
        "private": 123,
    }

    with pytest.raises(ValidationError):
        ChallengeConfig(**config)
