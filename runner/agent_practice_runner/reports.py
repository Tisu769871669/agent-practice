from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from agent_practice_runner.schemas import GradeReport


def write_result(report: GradeReport | Mapping[str, Any], path: str | Path) -> GradeReport:
    validated_report = _validate_report(report)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            validated_report.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return validated_report


def summarize_result(report: GradeReport | Mapping[str, Any]) -> str:
    validated_report = _validate_report(report)
    status = validated_report.verdict.upper()
    return (
        f"{status} {validated_report.challenge_id} "
        f"score={validated_report.score:g}/{validated_report.max_score:g} "
        f"duration_ms={validated_report.duration_ms}"
    )


def _validate_report(report: GradeReport | Mapping[str, Any]) -> GradeReport:
    if isinstance(report, GradeReport):
        return report
    return GradeReport.model_validate(dict(report))
