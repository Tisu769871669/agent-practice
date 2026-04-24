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
_ISOLATED_MODULE_NAMES: set[str] = set()


def load_grader(challenge_dir: str | Path) -> Grader:
    challenge_root = Path(challenge_dir)
    grader_path = challenge_root / "grader.py"
    if not grader_path.exists():
        raise FileNotFoundError(grader_path)

    module_name = f"agent_practice_grader_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, grader_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load grader from {grader_path}")

    _purge_isolated_modules()
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    with _prepend_sys_path(challenge_root):
        before_import = set(sys.modules)
        spec.loader.exec_module(module)
        _remember_modules_loaded_from(challenge_root, before_import)

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
        before_call = set(sys.modules)
        report = grade(case_runs, Path(transcript_path), challenge)
        _remember_modules_loaded_from(challenge_root, before_call)

    if isinstance(report, GradeReport):
        return report
    return GradeReport.model_validate(report)


def _purge_isolated_modules() -> None:
    for module_name in list(_ISOLATED_MODULE_NAMES):
        sys.modules.pop(module_name, None)


def _remember_modules_loaded_from(import_root: str | Path, before_import: set[str]) -> None:
    root = Path(import_root).resolve()
    for module_name, module in list(sys.modules.items()):
        if module_name in before_import:
            continue
        module_file = getattr(module, "__file__", None)
        if module_file and _is_relative_to(Path(module_file), root):
            _ISOLATED_MODULE_NAMES.add(module_name)
            sys.modules.pop(module_name, None)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False


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
