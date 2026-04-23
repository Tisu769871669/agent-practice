from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ChallengeStatus = Literal["planned", "draft", "runnable", "deprecated"]
ChallengeDifficulty = Literal["easy", "medium", "hard", "expert"]
TranscriptEventType = Literal[
    "case_start",
    "tool_call",
    "tool_result",
    "agent_output",
    "case_end",
    "error",
]


class AgentPracticeModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class EntrypointConfig(AgentPracticeModel):
    module: str
    callable: str
    signature: str | None = None


class FixtureConfig(AgentPracticeModel):
    public: str
    hidden: str | None = None


class LimitsConfig(AgentPracticeModel):
    timeout_seconds: int = Field(gt=0)
    max_tool_calls: int = Field(ge=0)
    max_output_chars: int = Field(gt=0)


class ScoringMetric(AgentPracticeModel):
    name: str
    weight: float = Field(ge=0)


class ScoringConfig(AgentPracticeModel):
    max_score: float = Field(gt=0)
    pass_score: float = Field(ge=0)
    metrics: list[ScoringMetric]


class ChallengeConfig(AgentPracticeModel):
    id: str
    slug: str
    title: str
    track: str
    difficulty: ChallengeDifficulty
    status: ChallengeStatus
    version: str
    summary: str
    tags: list[str]
    entrypoint: EntrypointConfig
    fixtures: FixtureConfig
    limits: LimitsConfig
    scoring: ScoringConfig
    frameworks: dict[str, Any] | None = None
    schemas: dict[str, str] | None = None


class SubmissionConfig(AgentPracticeModel):
    schema_version: str = "0.1"
    submission_id: str = "local"
    template: str
    entrypoint: EntrypointConfig
    metadata: dict[str, Any] = Field(default_factory=dict)


class GradeMetric(AgentPracticeModel):
    name: str
    score: float = Field(ge=0)
    max_score: float = Field(ge=0)
    passed: bool
    feedback: str | None = None


class GradeCase(AgentPracticeModel):
    case_id: str
    score: float = Field(ge=0)
    max_score: float = Field(ge=0)
    passed: bool
    duration_ms: int = Field(ge=0)
    error: str | None = None


class GradeReport(AgentPracticeModel):
    schema_version: str
    challenge_id: str
    challenge_version: str
    runner_version: str
    submission_id: str
    template: str
    score: float = Field(ge=0)
    max_score: float = Field(gt=0)
    passed: bool
    duration_ms: int = Field(ge=0)
    metrics: list[GradeMetric]
    cases: list[GradeCase]
    artifacts: dict[str, str]


class TranscriptEvent(AgentPracticeModel):
    type: TranscriptEventType
    timestamp: str | None = None
    case_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    message: str | None = None
    error: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
