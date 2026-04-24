import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.loader import load_challenge  # noqa: E402
from agent_practice_runner.schemas import ChallengeConfig  # noqa: E402


CATALOG_PATH = ROOT / "challenges" / "catalog.yaml"
RUNNABLE_IDS = {"001", "002", "003", "004", "005", "006", "008", "010", "013", "017"}
FIRST_RUNNABLE_DIRS = [
    ROOT / "challenges" / "001-echo-agent",
    ROOT / "challenges" / "002-json-only",
]
REQUIRED_CHALLENGE_FILES = [
    "challenge.yaml",
    "README.md",
    "fixtures/public.jsonl",
    "schemas/input.schema.json",
    "schemas/output.schema.json",
    "grader.py",
]


def load_catalog() -> list[dict]:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    assert isinstance(data, dict)
    entries = data.get("challenges")
    assert isinstance(entries, list)
    return entries


def test_catalog_contains_30_entries() -> None:
    assert len(load_catalog()) == 30


def test_catalog_has_exactly_10_runnable_entries() -> None:
    runnable_entries = [
        entry for entry in load_catalog() if entry.get("status") == "runnable"
    ]

    assert len(runnable_entries) == 10


def test_catalog_challenge_ids_are_unique() -> None:
    ids = [entry.get("id") for entry in load_catalog()]

    assert len(ids) == len(set(ids))


def test_catalog_runnable_ids_match_launch_set() -> None:
    runnable_ids = {
        entry.get("id")
        for entry in load_catalog()
        if entry.get("status") == "runnable"
    }

    assert runnable_ids == RUNNABLE_IDS


def test_first_two_challenge_directories_have_required_files() -> None:
    for challenge_dir in FIRST_RUNNABLE_DIRS:
        assert challenge_dir.is_dir()
        for relative_path in REQUIRED_CHALLENGE_FILES:
            assert (challenge_dir / relative_path).is_file()


def test_first_two_challenge_configs_parse() -> None:
    for challenge_dir in FIRST_RUNNABLE_DIRS:
        challenge = load_challenge(challenge_dir)

        assert isinstance(challenge, ChallengeConfig)
