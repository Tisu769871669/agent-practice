from __future__ import annotations

import importlib.util
import sys
import uuid
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from agent_practice_runner.execution import CaseRun
from agent_practice_runner.schemas import ChallengeConfig, GradeReport


Grader = Callable[[list[CaseRun], Path, ChallengeConfig], GradeReport | dict[str, Any]]


def load_grader(challenge_dir: str | Path) -> Grader:
    challenge_root = Path(challenge_dir)
    grader_path = challenge_root / "grader.py"
    if not grader_path.exists():
        raise FileNotFoundError(grader_path)

    module_name = f"agent_practice_grader_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, grader_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load grader from {grader_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    with _prepend_sys_path(challenge_root):
        spec.loader.exec_module(module)

    grade = getattr(module, "grade", None)
    if not callable(grade):
        raise AttributeError(f"{grader_path} must expose callable grade")
    return grade


def grade_cases(
    *,
    challenge_dir: str | Path,
    case_runs: list[CaseRun],
    transcript_path: str | Path,
    challenge: ChallengeConfig,
) -> GradeReport:
    challenge_root = Path(challenge_dir)
    grade = load_grader(challenge_root)
    with _prepend_sys_path(challenge_root):
        report = grade(case_runs, Path(transcript_path), challenge)

    if isinstance(report, GradeReport):
        return report
    return GradeReport.model_validate(report)


@contextmanager
def _prepend_sys_path(path: str | Path) -> Iterator[None]:
    resolved = str(Path(path).resolve())
    sys.path.insert(0, resolved)
    try:
        yield
    finally:
        try:
            sys.path.remove(resolved)
        except ValueError:
            pass
