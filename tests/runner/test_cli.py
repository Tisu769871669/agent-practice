import json
import sys
from pathlib import Path

import yaml
from typer.testing import CliRunner


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.cli import app  # noqa: E402


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
        "metadata": {},
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def write_passing_challenge(challenges_dir: Path) -> Path:
    challenge_dir = challenges_dir / "001-echo-agent"
    challenge_dir.mkdir(parents=True)
    (challenge_dir / "challenge.yaml").write_text(
        yaml.safe_dump(minimal_challenge_config()),
        encoding="utf-8",
    )
    write_jsonl(
        challenge_dir / "fixtures" / "public.jsonl",
        [
            {
                "case_id": "public-001",
                "input": {"text": "hello"},
                "expected": {"answer": "HELLO"},
            },
            {
                "case_id": "public-002",
                "input": {"text": "world"},
                "expected": {"answer": "WORLD"},
            },
        ],
    )
    (challenge_dir / "grader.py").write_text(
        """
def grade(case_runs, transcript_path, challenge):
    cases = []
    for case in case_runs:
        passed = case.error is None and case.output == case.fixture["expected"]
        cases.append(
            {
                "case_id": case.case_id,
                "score": 50 if passed else 0,
                "max_score": 50,
                "passed": passed,
                "duration_ms": case.duration_ms,
                "error": case.error,
            }
        )
    score = sum(case["score"] for case in cases)
    return {
        "schema_version": "0.1",
        "challenge_id": challenge.id,
        "challenge_version": challenge.version,
        "runner_version": "0.1.0",
        "submission_id": "sample-submission",
        "template": "raw-python",
        "score": score,
        "max_score": challenge.scoring.max_score,
        "passed": score >= challenge.scoring.pass_score,
        "duration_ms": sum(case.duration_ms for case in case_runs),
        "metrics": [
            {
                "name": "task_success",
                "score": score,
                "max_score": challenge.scoring.max_score,
                "passed": score >= challenge.scoring.pass_score,
            }
        ],
        "cases": cases,
        "artifacts": {"transcript": "transcript.jsonl"},
    }
""".strip(),
        encoding="utf-8",
    )
    return challenge_dir


def write_passing_submission(submission_dir: Path) -> Path:
    package_dir = submission_dir / "solution"
    package_dir.mkdir(parents=True)
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "agent.py").write_text(
        """
def run(input, context):
    return {"answer": input["text"].upper()}
""".strip(),
        encoding="utf-8",
    )
    submission_path = submission_dir / "submission.yaml"
    submission_path.write_text(
        yaml.safe_dump(minimal_submission_config()),
        encoding="utf-8",
    )
    return submission_path


def test_run_command_exits_zero_for_passing_submission_and_writes_artifacts(
    tmp_path: Path,
) -> None:
    challenges_dir = tmp_path / "challenges"
    runs_dir = tmp_path / "runs"
    write_passing_challenge(challenges_dir)
    submission_path = write_passing_submission(tmp_path / "submission")
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "run",
            "001",
            "--submission",
            str(submission_path),
            "--challenges-dir",
            str(challenges_dir),
            "--runs-dir",
            str(runs_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ACCEPTED 001" in result.output
    run_dirs = list((runs_dir / "001").iterdir())
    assert len(run_dirs) == 1
    result_path = run_dirs[0] / "result.json"
    transcript_path = run_dirs[0] / "transcript.jsonl"
    assert result_path.exists()
    assert transcript_path.exists()
    assert transcript_path.read_text(encoding="utf-8").strip()

    report = json.loads(result_path.read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["verdict"] == "accepted"
    assert report["gates"]
    assert report["score"] == 100


def test_run_command_unknown_challenge_id_exits_nonzero_with_clear_message(
    tmp_path: Path,
) -> None:
    challenges_dir = tmp_path / "challenges"
    challenges_dir.mkdir()
    submission_path = write_passing_submission(tmp_path / "submission")
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "run",
            "999",
            "--submission",
            str(submission_path),
            "--challenges-dir",
            str(challenges_dir),
            "--runs-dir",
            str(tmp_path / "runs"),
        ],
    )

    assert result.exit_code != 0
    assert "Unknown challenge id '999'" in result.output
