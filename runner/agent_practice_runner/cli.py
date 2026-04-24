from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import typer

from agent_practice_runner.execution import run_cases
from agent_practice_runner.grading import grade_cases
from agent_practice_runner.loader import load_challenge, load_submission
from agent_practice_runner.reports import summarize_result, write_result


app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Run local Agent Practice challenges."""


@app.command("run")
def run_command(
    challenge_id: str,
    submission: Path = typer.Option(..., "--submission"),
    challenges_dir: Path = typer.Option(Path("challenges"), "--challenges-dir"),
    runs_dir: Path = typer.Option(Path("runs"), "--runs-dir"),
) -> None:
    challenge_dir = find_challenge_dir(challenges_dir, challenge_id)
    if challenge_dir is None:
        typer.echo(
            f"Unknown challenge id '{challenge_id}' in {challenges_dir}",
            err=True,
        )
        raise typer.Exit(1)

    challenge = load_challenge(challenge_dir)
    submission_config = load_submission(submission)
    run_dir = _create_run_dir(runs_dir, challenge.id)
    transcript_path = run_dir / "transcript.jsonl"

    case_runs = run_cases(
        challenge_dir=challenge_dir,
        challenge=challenge,
        submission=submission_config,
        submission_path=submission,
        transcript_path=transcript_path,
    )
    report = grade_cases(
        challenge_dir=challenge_dir,
        case_runs=case_runs,
        transcript_path=transcript_path,
        challenge=challenge,
    )
    write_result(report, run_dir / "result.json")
    typer.echo(summarize_result(report))

    if not report.passed:
        raise typer.Exit(1)


def find_challenge_dir(
    challenges_dir: str | Path,
    challenge_id: str,
) -> Path | None:
    root = Path(challenges_dir)
    if not root.exists():
        return None

    candidates: list[Path] = []
    if (root / "challenge.yaml").exists():
        candidates.append(root)

    candidates.extend(
        child
        for child in sorted(root.iterdir())
        if child.is_dir() and (child / "challenge.yaml").exists()
    )

    for candidate in candidates:
        challenge = load_challenge(candidate)
        if challenge.id == challenge_id:
            return candidate

    return None


def _create_run_dir(runs_dir: str | Path, challenge_id: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = Path(runs_dir) / challenge_id
    run_dir = root / timestamp
    suffix = 1

    while run_dir.exists():
        run_dir = root / f"{timestamp}-{suffix}"
        suffix += 1

    run_dir.mkdir(parents=True)
    return run_dir


if __name__ == "__main__":
    app()
