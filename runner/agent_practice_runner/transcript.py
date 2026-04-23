from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agent_practice_runner.schemas import TranscriptEvent


class TranscriptWriter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write_event(
        self, event: TranscriptEvent | Mapping[str, Any]
    ) -> TranscriptEvent:
        event_data: dict[str, Any]
        if isinstance(event, TranscriptEvent):
            event_data = event.model_dump(mode="python", exclude_none=False)
        else:
            event_data = dict(event)

        event_data.setdefault("timestamp", datetime.now(timezone.utc))
        if event_data["timestamp"] is None:
            event_data["timestamp"] = datetime.now(timezone.utc)

        validated_event = TranscriptEvent.model_validate(event_data)

        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(validated_event.model_dump_json(exclude_none=True))
            handle.write("\n")

        return validated_event
