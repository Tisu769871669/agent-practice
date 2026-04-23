import json
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.loader import load_challenge, load_jsonl  # noqa: E402
from agent_practice_runner.schemas import ChallengeConfig  # noqa: E402


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
            "metrics": [
                {
                    "name": "task_success",
                    "weight": 60,
                }
            ],
        },
    }


def test_load_challenge_reads_challenge_yaml(tmp_path: Path) -> None:
    challenge_dir = tmp_path / "001-echo-agent"
    challenge_dir.mkdir()
    (challenge_dir / "challenge.yaml").write_text(
        yaml.safe_dump(minimal_challenge_config()),
        encoding="utf-8",
    )

    challenge = load_challenge(challenge_dir)

    assert isinstance(challenge, ChallengeConfig)
    assert challenge.id == "001"
    assert challenge.slug == "echo-agent"


def test_load_jsonl_returns_list_of_dicts(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "public.jsonl"
    expected = [
        {"case_id": "public-001", "input": {"text": "hello"}},
        {"case_id": "public-002", "input": {"text": "world"}},
    ]
    jsonl_path.write_text(
        "\n".join(json.dumps(item) for item in expected) + "\n",
        encoding="utf-8",
    )

    rows = load_jsonl(jsonl_path)

    assert rows == expected


def test_load_challenge_missing_file_raises(tmp_path: Path) -> None:
    challenge_dir = tmp_path / "missing-challenge"
    challenge_dir.mkdir()

    with pytest.raises(FileNotFoundError):
        load_challenge(challenge_dir)
