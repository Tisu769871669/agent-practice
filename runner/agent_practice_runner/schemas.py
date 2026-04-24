from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


ChallengeStatus = Literal["planned", "draft", "runnable", "deprecated"]
ChallengeDifficulty = Literal["easy", "medium", "hard", "expert"]
Verdict = Literal[
    "accepted",
    "wrong_answer",
    "schema_error",
    "timeout",
    "runtime_error",
    "safety_violation",
    "partial_pass",
]
TranscriptEventType = Literal[
    "case_start",
    "tool_call",
    "tool_result",
    "agent_output",
    "case_end",
    "error",
]
NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class AgentPracticeModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class EntrypointConfig(AgentPracticeModel):
    module: NonEmptyString
    callable: NonEmptyString
    signature: str | None = None

    @field_validator("signature", mode="before")
    @classmethod
    def reject_null_signature(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("signature may be omitted or a string, not null")
        return value


class FixtureConfig(AgentPracticeModel):
    public: NonEmptyString
    hidden: str | None = None

    @field_validator("hidden", mode="before")
    @classmethod
    def reject_null_hidden(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("hidden may be omitted or a string, not null")
        return value

    @model_validator(mode="after")
    def validate_extra_fixture_values(self) -> FixtureConfig:
        for key, value in (self.model_extra or {}).items():
            if not isinstance(value, str):
                raise ValueError(f"fixture field '{key}' must be a string")
        return self


class LimitsConfig(AgentPracticeModel):
    timeout_seconds: int = Field(gt=0)
    max_tool_calls: int = Field(ge=0)
    max_output_chars: int = Field(gt=0)


class ScoringMetric(AgentPracticeModel):
    name: NonEmptyString
    weight: float = Field(ge=0)


class ScoringConfig(AgentPracticeModel):
    max_score: float = Field(gt=0)
    pass_score: float = Field(ge=0)
    metrics: list[ScoringMetric]


class ChallengeConfig(AgentPracticeModel):
    id: NonEmptyString
    slug: NonEmptyString
    title: NonEmptyString
    track: NonEmptyString
    difficulty: ChallengeDifficulty
    status: ChallengeStatus
    version: NonEmptyString
    summary: NonEmptyString
    tags: list[NonEmptyString]
    entrypoint: EntrypointConfig
    fixtures: FixtureConfig
    limits: LimitsConfig
    scoring: ScoringConfig
    frameworks: dict[str, Any] | None = None
    schemas: dict[str, str] | None = None


class SubmissionConfig(AgentPracticeModel):
    schema_version: str = "0.1"
    submission_id: str = "local"
    template: NonEmptyString
    entrypoint: EntrypointConfig
    metadata: dict[str, Any] = Field(default_factory=dict)


class GradeMetric(AgentPracticeModel):
    name: NonEmptyString
    score: float = Field(ge=0)
    max_score: float = Field(ge=0)
    passed: bool
    feedback: str | None = None


class FailureReason(AgentPracticeModel):
    code: NonEmptyString
    message: NonEmptyString
    metric: str | None = None


class GradeGate(AgentPracticeModel):
    name: NonEmptyString
    passed: bool
    message: str | None = None


class GradeCase(AgentPracticeModel):
    case_id: NonEmptyString
    score: float = Field(ge=0)
    max_score: float = Field(ge=0)
    passed: bool
    duration_ms: int = Field(ge=0)
    error: str | None = None
    verdict: Verdict = "accepted"
    failure_reasons: list[FailureReason] = Field(default_factory=list)

    @model_validator(mode="after")
    def derive_case_verdict(self) -> GradeCase:
        if self.passed:
            self.verdict = "accepted"
            self.failure_reasons = []
            return self

        if self.error:
            verdict = _verdict_from_error(self.error)
            self.verdict = verdict
            self.failure_reasons = [
                FailureReason(
                    code=verdict,
                    message=self.error,
                )
            ]
            return self

        if self.score > 0:
            self.verdict = "partial_pass"
            message = "Case earned partial credit but did not satisfy every check."
        else:
            self.verdict = "wrong_answer"
            message = "Case did not satisfy the expected output checks."

        self.failure_reasons = [
            FailureReason(
                code="wrong_answer",
                message=message,
            )
        ]
        return self


class GradeReport(AgentPracticeModel):
    schema_version: str
    challenge_id: NonEmptyString
    challenge_version: NonEmptyString
    runner_version: NonEmptyString
    submission_id: NonEmptyString
    template: NonEmptyString
    score: float = Field(ge=0)
    max_score: float = Field(gt=0)
    passed: bool
    duration_ms: int = Field(ge=0)
    metrics: list[GradeMetric]
    cases: list[GradeCase]
    artifacts: dict[str, str]
    verdict: Verdict = "accepted"
    gates: list[GradeGate] = Field(default_factory=list)
    failure_reasons: list[FailureReason] = Field(default_factory=list)

    @model_validator(mode="after")
    def derive_report_verdict(self) -> GradeReport:
        self.gates = _derive_gates(self)
        self.verdict = _derive_report_verdict(self)
        self.failure_reasons = _derive_report_failures(self)
        return self


class TranscriptEvent(AgentPracticeModel):
    type: TranscriptEventType
    timestamp: AwareDatetime | None = None
    case_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    message: str | None = None
    error: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)


def _derive_gates(report: GradeReport) -> list[GradeGate]:
    schema_metric = next(
        (metric for metric in report.metrics if metric.name == "schema_validity"),
        None,
    )
    schema_valid = schema_metric.passed if schema_metric else True
    runtime_clean = all(case.verdict != "runtime_error" for case in report.cases)
    timeout_clean = all(case.verdict != "timeout" for case in report.cases)
    safety_clean = all(
        not _is_safety_metric(metric.name) or metric.passed
        for metric in report.metrics
    ) and all(case.verdict != "safety_violation" for case in report.cases)

    return [
        GradeGate(
            name="schema_validity",
            passed=schema_valid,
            message="All outputs matched the declared output schema."
            if schema_valid
            else "At least one output failed the declared output schema.",
        ),
        GradeGate(
            name="no_runtime_error",
            passed=runtime_clean,
            message="No case crashed during execution."
            if runtime_clean
            else "At least one case crashed during execution.",
        ),
        GradeGate(
            name="no_timeout",
            passed=timeout_clean,
            message="No case exceeded the runtime limit."
            if timeout_clean
            else "At least one case exceeded the runtime limit.",
        ),
        GradeGate(
            name="no_safety_violation",
            passed=safety_clean,
            message="No safety metric failed."
            if safety_clean
            else "At least one safety metric failed.",
        ),
        GradeGate(
            name="score_threshold",
            passed=report.passed,
            message="Score met the challenge pass threshold."
            if report.passed
            else "Score did not meet the challenge pass threshold.",
        ),
    ]


def _derive_report_verdict(report: GradeReport) -> Verdict:
    if report.passed and all(gate.passed for gate in report.gates):
        return "accepted"

    failed_gate_names = {
        gate.name
        for gate in report.gates
        if not gate.passed
    }
    if "no_timeout" in failed_gate_names:
        return "timeout"
    if "no_runtime_error" in failed_gate_names:
        return "runtime_error"
    if "no_safety_violation" in failed_gate_names:
        return "safety_violation"
    if "schema_validity" in failed_gate_names:
        return "schema_error"
    if report.score > 0:
        return "partial_pass"
    return "wrong_answer"


def _derive_report_failures(report: GradeReport) -> list[FailureReason]:
    if report.verdict == "accepted":
        return []

    reasons: list[FailureReason] = [
        FailureReason(
            code=gate.name,
            message=gate.message or f"Gate {gate.name} failed.",
        )
        for gate in report.gates
        if not gate.passed
    ]
    for case in report.cases:
        if not case.passed:
            reasons.extend(case.failure_reasons)
    return reasons


def _verdict_from_error(error: str) -> Verdict:
    normalized = error.lower()
    if "safety_violation" in normalized or "safety violation" in normalized:
        return "safety_violation"
    if "timeout" in normalized or "timed out" in normalized:
        return "timeout"
    if _looks_like_runtime_error(normalized):
        return "runtime_error"
    return "schema_error"


def _looks_like_runtime_error(error: str) -> bool:
    runtime_markers = (
        "attributeerror:",
        "importerror:",
        "keyerror:",
        "modulenotfounderror:",
        "runtimeerror:",
        "typeerror:",
        "valueerror:",
    )
    return any(marker in error for marker in runtime_markers)


def _is_safety_metric(name: str) -> bool:
    normalized = name.lower()
    return "safety" in normalized or "injection" in normalized
