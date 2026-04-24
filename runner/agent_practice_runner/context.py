from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    challenge_id: str
    case_id: str
    tools: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    deadline: float | None = None
    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("agent_practice_runner")
    )
