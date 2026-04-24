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
    assert written["verdict"] == "accepted"
    assert written["cases"][0]["verdict"] == "accepted"
    assert written["cases"][0]["failure_reasons"] == []


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

    assert summary == "ACCEPTED 001 score=86/100 duration_ms=8230"


def test_grade_report_derives_schema_error_verdict_and_case_failure_reason() -> None:
    payload = minimal_grade_report()
    payload["score"] = 0
    payload["passed"] = False
    payload["metrics"][0] = {
        "name": "schema_validity",
        "score": 0,
        "max_score": 20,
        "passed": False,
        "feedback": "0/1 outputs matched the schema.",
    }
    payload["cases"][0] = {
        "case_id": "public-001",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "duration_ms": 610,
        "error": "'facts' is a required property",
    }

    report = GradeReport(**payload)

    assert report.verdict == "schema_error"
    assert report.gates[0].name == "schema_validity"
    assert report.gates[0].passed is False
    assert report.cases[0].verdict == "schema_error"
    assert report.cases[0].failure_reasons[0].code == "schema_error"
    assert "facts" in report.cases[0].failure_reasons[0].message


def test_grade_report_derives_partial_pass_for_scored_wrong_answer() -> None:
    payload = minimal_grade_report()
    payload["score"] = 50
    payload["passed"] = False
    payload["cases"][0] = {
        "case_id": "public-001",
        "score": 5,
        "max_score": 10,
        "passed": False,
        "duration_ms": 610,
        "error": None,
    }

    report = GradeReport(**payload)

    assert report.verdict == "partial_pass"
    assert report.cases[0].verdict == "partial_pass"
    assert report.cases[0].failure_reasons[0].code == "wrong_answer"


def test_grade_report_derives_wrong_answer_when_no_credit_is_earned() -> None:
    payload = minimal_grade_report()
    payload["score"] = 0
    payload["passed"] = False
    payload["cases"][0] = {
        "case_id": "public-001",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "duration_ms": 610,
        "error": None,
    }

    report = GradeReport(**payload)

    assert report.verdict == "wrong_answer"
    assert report.cases[0].verdict == "wrong_answer"


def test_grade_report_derives_runtime_error_from_case_exception() -> None:
    payload = minimal_grade_report()
    payload["score"] = 0
    payload["passed"] = False
    payload["cases"][0] = {
        "case_id": "public-001",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "duration_ms": 610,
        "error": "TypeError: unsupported operand type",
    }

    report = GradeReport(**payload)

    assert report.verdict == "runtime_error"
    assert report.cases[0].verdict == "runtime_error"


def test_grade_report_derives_timeout_from_case_timeout_error() -> None:
    payload = minimal_grade_report()
    payload["score"] = 0
    payload["passed"] = False
    payload["cases"][0] = {
        "case_id": "public-001",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "duration_ms": 60001,
        "error": "TimeoutError: case exceeded 60 seconds",
    }

    report = GradeReport(**payload)

    assert report.verdict == "timeout"
    assert report.cases[0].verdict == "timeout"


def test_grade_report_derives_safety_violation_from_case_error() -> None:
    payload = minimal_grade_report()
    payload["score"] = 0
    payload["passed"] = False
    payload["cases"][0] = {
        "case_id": "public-001",
        "score": 0,
        "max_score": 10,
        "passed": False,
        "duration_ms": 610,
        "error": "safety_violation: injected instruction was followed",
    }

    report = GradeReport(**payload)

    assert report.verdict == "safety_violation"
    assert report.cases[0].verdict == "safety_violation"


def test_result_json_schema_declares_aps1_fields() -> None:
    schema = json.loads((ROOT / "schemas" / "result.schema.json").read_text(encoding="utf-8"))

    assert {"verdict", "gates", "failure_reasons"} <= set(schema["required"])
    assert "verdict" in schema["properties"]
    assert "gate" in schema["$defs"]
    assert "failure_reason" in schema["$defs"]
    assert {"verdict", "failure_reasons"} <= set(schema["$defs"]["case"]["properties"])
