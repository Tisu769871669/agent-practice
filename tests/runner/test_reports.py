import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.reports import summarize_result, write_result  # noqa: E402
from agent_practice_runner.schemas import GradeReport  # noqa: E402


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


def test_write_result_writes_valid_json(tmp_path: Path) -> None:
    report = GradeReport(**minimal_grade_report())
    result_path = tmp_path / "result.json"

    write_result(report, result_path)

    written = json.loads(result_path.read_text(encoding="utf-8"))

    assert written["challenge_id"] == "001"
    assert written["score"] == 86
    assert written["passed"] is True


def test_summarize_result_includes_score_and_pass_fail() -> None:
    report = GradeReport(**minimal_grade_report())

    summary = summarize_result(report)

    assert "86" in summary
    assert "pass" in summary.lower()
