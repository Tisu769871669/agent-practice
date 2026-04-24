import builtins
import importlib.util
import inspect
import json
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.execution import run_cases  # noqa: E402
from agent_practice_runner.grading import grade_cases  # noqa: E402
from agent_practice_runner.loader import load_challenge, load_submission  # noqa: E402


TEMPLATE_NAMES = ("raw-python", "langchain", "langgraph")


def template_dir(name: str) -> Path:
    return ROOT / "templates" / name


def load_template_agent(name: str):
    agent_path = template_dir(name) / "solution" / "agent.py"
    module_name = f"agent_practice_template_{name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, agent_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", TEMPLATE_NAMES)
def test_template_contains_required_files_and_submission_config(name: str) -> None:
    root = template_dir(name)

    assert (root / "submission.yaml").is_file()
    assert (root / "solution" / "agent.py").is_file()
    assert (root / "README.md").is_file()

    submission = yaml.safe_load((root / "submission.yaml").read_text(encoding="utf-8"))
    assert submission["template"] == name
    assert submission["entrypoint"] == {
        "module": "solution.agent",
        "callable": "run",
        "signature": "run(input: dict, context: AgentContext) -> dict",
    }


@pytest.mark.parametrize("name", TEMPLATE_NAMES)
def test_template_agent_exports_run_without_optional_dependencies(
    name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def block_optional_agent_frameworks(import_name, *args, **kwargs):
        if import_name.split(".", 1)[0] in {"langchain", "langgraph"}:
            raise ImportError(f"No module named {import_name!r}")
        return real_import(import_name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_optional_agent_frameworks)

    module = load_template_agent(name)

    assert callable(module.run)
    signature = inspect.signature(module.run)
    assert list(signature.parameters) == ["input", "context"]

    result = module.run(
        {
            "message": "Return only these facts.",
            "facts": ["The runner calls run(input, context)."],
        },
        context=None,
    )
    assert result == {
        "facts": ["The runner calls run(input, context)."],
        "added_facts": [],
    }


def test_raw_python_template_solves_challenge_001(tmp_path: Path) -> None:
    challenge_dir = ROOT / "challenges" / "001-echo-agent"
    submission_path = template_dir("raw-python") / "submission.yaml"

    case_runs = run_cases(
        challenge_dir=challenge_dir,
        challenge=load_challenge(challenge_dir),
        submission=load_submission(submission_path),
        submission_path=submission_path,
        transcript_path=tmp_path / "transcript.jsonl",
    )
    report = grade_cases(
        challenge_dir=challenge_dir,
        case_runs=case_runs,
        transcript_path=tmp_path / "transcript.jsonl",
        challenge=load_challenge(challenge_dir),
    )

    assert report.passed is True
    assert report.score == report.max_score


def test_raw_python_template_returns_input_facts_without_added_facts() -> None:
    module = load_template_agent("raw-python")
    fixtures = [
        json.loads(line)
        for line in (ROOT / "challenges" / "001-echo-agent" / "fixtures" / "public.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]

    for fixture in fixtures:
        assert module.run(fixture["input"], context=None) == {
            "facts": fixture["input"]["facts"],
            "added_facts": [],
        }
