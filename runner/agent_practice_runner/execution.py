from __future__ import annotations

import importlib
import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agent_practice_runner.context import AgentContext
from agent_practice_runner.loader import load_jsonl
from agent_practice_runner.schemas import ChallengeConfig, SubmissionConfig
from agent_practice_runner.transcript import TranscriptWriter


_ISOLATED_MODULE_NAMES: set[str] = set()


@dataclass
class CaseRun:
    case_id: str
    input: dict[str, Any]
    output: Any
    passed: bool
    duration_ms: int
    error: str | None = None
    fixture: dict[str, Any] = field(default_factory=dict)


def run_cases(
    *,
    challenge_dir: str | Path,
    challenge: ChallengeConfig,
    submission: SubmissionConfig,
    submission_path: str | Path,
    transcript_path: str | Path,
) -> list[CaseRun]:
    challenge_root = Path(challenge_dir)
    fixture_path = challenge_root / challenge.fixtures.public
    fixture_rows = load_jsonl(fixture_path)
    writer = TranscriptWriter(transcript_path)
    run_callable = _load_entrypoint(
        module_name=submission.entrypoint.module,
        callable_name=submission.entrypoint.callable,
        import_root=_submission_import_root(submission_path),
    )

    case_runs: list[CaseRun] = []
    deadline = time.monotonic() + challenge.limits.timeout_seconds

    for index, fixture in enumerate(fixture_rows, start=1):
        case_id = str(fixture.get("case_id") or f"case-{index:03d}")
        input_payload = _dict_value(fixture.get("input"), "input", case_id)
        context = AgentContext(
            challenge_id=challenge.id,
            case_id=case_id,
            tools=_dict_value(fixture.get("tools", {}), "tools", case_id),
            metadata=_case_metadata(submission.metadata, fixture),
            deadline=deadline,
        )

        writer.write_event(
            {
                "type": "case_start",
                "case_id": case_id,
                "payload": {"input": input_payload},
            }
        )
        start = time.perf_counter()

        try:
            output = run_callable(input_payload, context)
            duration_ms = _elapsed_ms(start)
            writer.write_event(
                {
                    "type": "agent_output",
                    "case_id": case_id,
                    "payload": {"output": output},
                    "duration_ms": duration_ms,
                }
            )
            writer.write_event(
                {
                    "type": "case_end",
                    "case_id": case_id,
                    "duration_ms": duration_ms,
                }
            )
            case_runs.append(
                CaseRun(
                    case_id=case_id,
                    input=input_payload,
                    output=output,
                    passed=True,
                    duration_ms=duration_ms,
                    error=None,
                    fixture=fixture,
                )
            )
        except Exception as exc:  # noqa: BLE001 - runner isolates case failures.
            duration_ms = _elapsed_ms(start)
            case_runs.append(
                _record_case_failure(
                    writer=writer,
                    case_id=case_id,
                    input_payload=input_payload,
                    fixture=fixture,
                    duration_ms=duration_ms,
                    exc=exc,
                )
            )

    return case_runs


def _load_entrypoint(
    *,
    module_name: str,
    callable_name: str,
    import_root: Path,
) -> Callable[[dict[str, Any], AgentContext], Any]:
    _purge_isolated_modules()
    with _prepend_sys_path(import_root):
        importlib.invalidate_caches()
        _purge_module(module_name)
        before_import = set(sys.modules)
        module = importlib.import_module(module_name)
        _remember_modules_loaded_from(import_root, before_import)

    entrypoint = getattr(module, callable_name)
    if not callable(entrypoint):
        raise TypeError(f"{module_name}.{callable_name} is not callable")
    return entrypoint


def _submission_import_root(submission_path: str | Path) -> Path:
    path = Path(submission_path)
    if path.is_dir():
        return path
    return path.parent


def _case_metadata(
    submission_metadata: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    metadata = dict(submission_metadata)
    fixture_metadata = fixture.get("metadata", {})
    if isinstance(fixture_metadata, dict):
        metadata.update(fixture_metadata)
    return metadata


def _dict_value(value: Any, name: str, case_id: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"Fixture {case_id} field '{name}' must be an object")
    return value


def _elapsed_ms(start: float) -> int:
    return max(0, int((time.perf_counter() - start) * 1000))


def _record_case_failure(
    *,
    writer: TranscriptWriter,
    case_id: str,
    input_payload: dict[str, Any],
    fixture: dict[str, Any],
    duration_ms: int,
    exc: Exception,
) -> CaseRun:
    error = f"{type(exc).__name__}: {exc}"
    writer.write_event(
        {
            "type": "error",
            "case_id": case_id,
            "error": error,
            "duration_ms": duration_ms,
        }
    )
    writer.write_event(
        {
            "type": "case_end",
            "case_id": case_id,
            "error": error,
            "duration_ms": duration_ms,
        }
    )
    return CaseRun(
        case_id=case_id,
        input=input_payload,
        output=None,
        passed=False,
        duration_ms=duration_ms,
        error=error,
        fixture=fixture,
    )


def _purge_module(module_name: str) -> None:
    parts = module_name.split(".")
    for index in range(1, len(parts) + 1):
        sys.modules.pop(".".join(parts[:index]), None)
    for loaded_name in list(sys.modules):
        if loaded_name.startswith(f"{module_name}."):
            sys.modules.pop(loaded_name, None)


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
