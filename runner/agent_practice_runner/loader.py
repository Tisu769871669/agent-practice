from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from agent_practice_runner.schemas import ChallengeConfig, SubmissionConfig


def load_challenge(path: str | Path) -> ChallengeConfig:
    config_path = _resolve_config_path(path, "challenge.yaml")
    data = _load_yaml(config_path)
    return ChallengeConfig.model_validate(data)


def load_submission(path: str | Path) -> SubmissionConfig:
    config_path = _resolve_config_path(path, "submission.yaml")
    data = _load_yaml(config_path)
    return SubmissionConfig.model_validate(data)


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    jsonl_path = Path(path)
    rows: list[dict[str, Any]] = []

    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue

            row = json.loads(stripped)
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object in {jsonl_path}")
            rows.append(row)

    return rows


def _resolve_config_path(path: str | Path, filename: str) -> Path:
    resolved_path = Path(path)
    if resolved_path.is_dir():
        resolved_path = resolved_path / filename

    if not resolved_path.exists():
        raise FileNotFoundError(resolved_path)

    return resolved_path


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
