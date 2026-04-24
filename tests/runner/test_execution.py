import json
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.execution import run_cases  # noqa: E402
from agent_practice_runner.grading import grade_cases, load_grader  # noqa: E402
from agent_practice_runner.schemas import (  # noqa: E402
    ChallengeConfig,
    GradeReport,
    SubmissionConfig,
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
            "metrics": [{"name": "task_success", "weight": 100}],
        },
    }


def minimal_submission_config() -> dict:
    return {
        "schema_version": "0.1",
        "submission_id": "sample-submission",
        "template": "raw-python",
        "entrypoint": {
            "module": "solution.agent",
            "callable": "run",
            "signature": "run(input: dict, context: AgentContext) -> dict",
        },
        "metadata": {"submission_name": "sample"},
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def write_submission_module(submission_dir: Path, source: str) -> Path:
    package_dir = submission_dir / "solution"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "agent.py").write_text(source, encoding="utf-8")
    (submission_dir / "submission.yaml").write_text(
        yaml.safe_dump(minimal_submission_config()),
        encoding="utf-8",
    )
    return submission_dir / "submission.yaml"


def test_run_cases_calls_submission_once_per_fixture_and_exposes_context(
    tmp_path: Path,
    monkeypatch,
) -> None:
    challenge_dir = tmp_path / "challenge"
    rows = [
        {
            "case_id": "public-001",
            "input": {"text": "hello"},
            "tools": {"lookup": {"answer": 42}},
            "metadata": {"fixture_tag": "alpha"},
        },
        {
            "case_id": "public-002",
            "input": {"text": "world"},
            "tools": {},
            "metadata": {"fixture_tag": "beta"},
        },
    ]
    write_jsonl(challenge_dir / "fixtures" / "public.jsonl", rows)

    calls_path = tmp_path / "calls.json"
    monkeypatch.setenv("CALLS_PATH", str(calls_path))
    submission_path = write_submission_module(
        tmp_path / "submission",
        """
import json
import os
from pathlib import Path


def run(input, context):
    calls_path = Path(os.environ["CALLS_PATH"])
    calls = json.loads(calls_path.read_text(encoding="utf-8")) if calls_path.exists() else []
    calls.append(
        {
            "input": input,
            "challenge_id": context.challenge_id,
            "case_id": context.case_id,
            "tools": context.tools,
            "metadata": context.metadata,
        }
    )
    calls_path.write_text(json.dumps(calls), encoding="utf-8")
    return {"echo": input["text"], "case_id": context.case_id}
""".strip(),
    )

    case_runs = run_cases(
        challenge_dir=challenge_dir,
        challenge=ChallengeConfig.model_validate(minimal_challenge_config()),
        submission=SubmissionConfig.model_validate(minimal_submission_config()),
        submission_path=submission_path,
        transcript_path=tmp_path / "transcript.jsonl",
    )

    calls = json.loads(calls_path.read_text(encoding="utf-8"))

    assert len(calls) == 2
    assert [call["input"] for call in calls] == [row["input"] for row in rows]
    assert calls[0]["challenge_id"] == "001"
    assert calls[0]["case_id"] == "public-001"
    assert calls[0]["tools"] == {"lookup": {"answer": 42}}
    assert calls[0]["metadata"] == {
        "submission_name": "sample",
        "fixture_tag": "alpha",
    }
    assert [case_run.output for case_run in case_runs] == [
        {"echo": "hello", "case_id": "public-001"},
        {"echo": "world", "case_id": "public-002"},
    ]


def test_run_cases_captures_case_exception_without_crashing(
    tmp_path: Path,
) -> None:
    challenge_dir = tmp_path / "challenge"
    write_jsonl(
        challenge_dir / "fixtures" / "public.jsonl",
        [
            {"case_id": "public-001", "input": {"text": "ok"}},
            {"case_id": "public-002", "input": {"text": "boom"}},
            {"case_id": "public-003", "input": {"text": "after"}},
        ],
    )
    submission_path = write_submission_module(
        tmp_path / "submission",
        """
def run(input, context):
    if input["text"] == "boom":
        raise RuntimeError("exploded on purpose")
    return {"echo": input["text"]}
""".strip(),
    )
    transcript_path = tmp_path / "transcript.jsonl"

    case_runs = run_cases(
        challenge_dir=challenge_dir,
        challenge=ChallengeConfig.model_validate(minimal_challenge_config()),
        submission=SubmissionConfig.model_validate(minimal_submission_config()),
        submission_path=submission_path,
        transcript_path=transcript_path,
    )

    assert [case_run.case_id for case_run in case_runs] == [
        "public-001",
        "public-002",
        "public-003",
    ]
    assert [case_run.passed for case_run in case_runs] == [True, False, True]
    assert "exploded on purpose" in (case_runs[1].error or "")
    transcript_events = [
        json.loads(line)
        for line in transcript_path.read_text(encoding="utf-8").splitlines()
    ]
    assert any(
        event["type"] == "error" and event["case_id"] == "public-002"
        for event in transcript_events
    )


def test_grade_cases_loads_challenge_grader_and_validates_report(
    tmp_path: Path,
) -> None:
    challenge_dir = tmp_path / "challenge"
    write_jsonl(
        challenge_dir / "fixtures" / "public.jsonl",
        [{"case_id": "public-001", "input": {"text": "hello"}}],
    )
    (challenge_dir / "grader.py").write_text(
        """
def grade(case_runs, transcript_path, challenge):
    return {
        "schema_version": "0.1",
        "challenge_id": challenge.id,
        "challenge_version": challenge.version,
        "runner_version": "0.1.0",
        "submission_id": "sample-submission",
        "template": "raw-python",
        "score": 100,
        "max_score": challenge.scoring.max_score,
        "passed": True,
        "duration_ms": sum(case.duration_ms for case in case_runs),
        "metrics": [
            {
                "name": "task_success",
                "score": 100,
                "max_score": 100,
                "passed": True,
            }
        ],
        "cases": [
            {
                "case_id": case.case_id,
                "score": 100,
                "max_score": 100,
                "passed": True,
                "duration_ms": case.duration_ms,
                "error": case.error,
            }
            for case in case_runs
        ],
        "artifacts": {"transcript": str(transcript_path)},
    }
""".strip(),
        encoding="utf-8",
    )
    submission_path = write_submission_module(
        tmp_path / "submission",
        """
def run(input, context):
    return {"echo": input["text"]}
""".strip(),
    )
    challenge = ChallengeConfig.model_validate(minimal_challenge_config())
    case_runs = run_cases(
        challenge_dir=challenge_dir,
        challenge=challenge,
        submission=SubmissionConfig.model_validate(minimal_submission_config()),
        submission_path=submission_path,
        transcript_path=tmp_path / "transcript.jsonl",
    )

    report = grade_cases(
        challenge_dir=challenge_dir,
        case_runs=case_runs,
        transcript_path=tmp_path / "transcript.jsonl",
        challenge=challenge,
    )

    assert isinstance(report, GradeReport)
    assert report.challenge_id == "001"
    assert report.passed is True


def test_load_grader_requires_callable_grade(tmp_path: Path) -> None:
    challenge_dir = tmp_path / "challenge"
    challenge_dir.mkdir()
    (challenge_dir / "grader.py").write_text(
        "not_grade = 'missing callable'\n",
        encoding="utf-8",
    )

    with pytest.raises(AttributeError, match="must expose callable grade"):
        load_grader(challenge_dir)
