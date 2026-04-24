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


def test_write_result_accepts_plain_dict_and_writes_trailing_newline(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"

    write_result(minimal_grade_report(), result_path)

    text = result_path.read_text(encoding="utf-8")
    written = json.loads(text)

    assert text.endswith("\n")
    assert written["challenge_id"] == "001"
    assert written["score"] == 86


def test_write_result_uses_stable_sorted_serialization(tmp_path: Path) -> None:
    result_path = tmp_path / "result.json"

    write_result(minimal_grade_report(), result_path)

    first_key = next(
        line.strip()
        for line in result_path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith('"')
    )

    assert first_key == '"artifacts": {'


def test_summarize_result_uses_exact_current_format() -> None:
    report = GradeReport(**minimal_grade_report())

    summary = summarize_result(report)

    assert summary == "PASS 001 score=86/100 duration_ms=8230"
