import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))

from agent_practice_runner.transcript import TranscriptWriter  # noqa: E402


def test_write_event_appends_jsonl(tmp_path: Path) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    writer = TranscriptWriter(transcript_path)

    writer.write_event({"type": "case_start", "case_id": "public-001"})
    writer.write_event(
        {
            "type": "agent_output",
            "case_id": "public-001",
            "payload": {"output": {"answer": "hello"}},
        }
    )

    lines = transcript_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0])["type"] == "case_start"
    assert json.loads(lines[1])["type"] == "agent_output"


def test_transcript_writer_rejects_unknown_event_type(tmp_path: Path) -> None:
    writer = TranscriptWriter(tmp_path / "transcript.jsonl")

    with pytest.raises(ValidationError):
        writer.write_event({"type": "not_a_real_event", "case_id": "public-001"})


def test_write_event_adds_timestamp_when_missing(tmp_path: Path) -> None:
    transcript_path = tmp_path / "transcript.jsonl"
    writer = TranscriptWriter(transcript_path)

    writer.write_event({"type": "case_start", "case_id": "public-001"})

    event = json.loads(transcript_path.read_text(encoding="utf-8").splitlines()[0])
    timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))

    assert "timestamp" in event
    assert timestamp.tzinfo is not None
    assert timestamp.utcoffset() == timezone.utc.utcoffset(timestamp)
