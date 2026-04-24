import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.execution import CaseRun  # noqa: E402
from agent_practice_runner.grading import grade_cases  # noqa: E402
from agent_practice_runner.loader import load_challenge, load_jsonl  # noqa: E402
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


def test_echo_agent_has_fixture_that_requires_trusting_facts_over_message() -> None:
    fixtures = load_jsonl(ROOT / "challenges" / "001-echo-agent" / "fixtures" / "public.jsonl")

    assert any(
        any(fact not in fixture["input"]["message"] for fact in fixture["expected"]["facts"])
        for fixture in fixtures
    )


def test_json_only_rejects_wrong_dates_when_date_is_missing(tmp_path: Path) -> None:
    challenge_dir = ROOT / "challenges" / "002-json-only"
    challenge = load_challenge(challenge_dir)
    fixtures = load_jsonl(challenge_dir / "fixtures" / "public.jsonl")
    case_runs = []

    for fixture in fixtures:
        output = dict(fixture["expected"])
        if fixture["expected"]["due_date"] is None:
            output["due_date"] = "2026-01-01"
        case_runs.append(
            CaseRun(
                case_id=fixture["case_id"],
                input=fixture["input"],
                output=output,
                passed=True,
                duration_ms=0,
                fixture=fixture,
            )
        )

    report = grade_cases(
        challenge_dir=challenge_dir,
        case_runs=case_runs,
        transcript_path=tmp_path / "transcript.jsonl",
        challenge=challenge,
    )

    assert report.passed is False
    assert report.score < challenge.scoring.pass_score
