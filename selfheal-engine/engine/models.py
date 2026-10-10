"""Data models for immutable intents, versioned recipes, and test execution results."""

from enum import Enum
import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Status(str, Enum):
    """Stable execution statuses used throughout the system (per AGENTS.md)."""

    PASS_NO_HEAL = "PASS_NO_HEAL"
    PASS_AFTER_HEAL = "PASS_AFTER_HEAL"
    FAIL_FUNCTIONAL = "FAIL_FUNCTIONAL"
    FAIL_HEALING = "FAIL_HEALING"
    FAIL_EXECUTION = "FAIL_EXECUTION"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED_CONFIG = "BLOCKED_CONFIG"
    BLOCKED_AGENT = "BLOCKED_AGENT"
    FAIL_BASELINE = "FAIL_BASELINE"


class FailureType(str, Enum):
    """Failure classifications for triage and diagnosis."""

    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"
    ELEMENT_AMBIGUOUS = "ELEMENT_AMBIGUOUS"
    ELEMENT_NOT_VISIBLE = "ELEMENT_NOT_VISIBLE"
    TIMEOUT = "TIMEOUT"
    HTTP_ERROR = "HTTP_ERROR"
    APP_ERROR_BANNER = "APP_ERROR_BANNER"
    ASSERTION_FAILED = "ASSERTION_FAILED"
    INVARIANT_FAILED = "INVARIANT_FAILED"
    CONFIG = "CONFIG"
    UNKNOWN = "UNKNOWN"


class ActionType(str, Enum):
    """Allowed deterministic step actions."""

    GOTO_START = "goto_start"
    FILL_FIELD = "fill_field"
    CLICK_BUTTON = "click_button"


class TargetBy(str, Enum):
    """Allowed locator strategies."""

    LABEL = "label"
    ROLE = "role"
    PLACEHOLDER = "placeholder"


class CreatedBy(str, Enum):
    """Creator tag for recipe versioning."""

    HUMAN = "human"
    AGENT = "agent"


class ExpectedOutcome(BaseModel):
    """Expected outcome invariants for deterministic verification."""

    model_config = ConfigDict(extra="forbid")

    confirmation_phrase: str
    order_id_pattern: str
    expected_total: float | str


class Intent(BaseModel):
    """Immutable intent specification."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: str
    goal: str
    test_data: dict[str, str]
    expected_outcome: ExpectedOutcome

    @property
    def content_hash(self) -> str:
        """Deterministic SHA-256 hash of the canonical JSON representation."""
        payload = {
            "id": self.id,
            "title": self.title,
            "goal": self.goal,
            "test_data": self.test_data,
            "expected_outcome": {
                "confirmation_phrase": self.expected_outcome.confirmation_phrase,
                "order_id_pattern": self.expected_outcome.order_id_pattern,
                "expected_total": str(self.expected_outcome.expected_total),
            },
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @property
    def intent_hash(self) -> str:
        """Alias for content_hash."""
        return self.content_hash


class StepTarget(BaseModel):
    """Target resolution descriptor for an element."""

    model_config = ConfigDict(extra="forbid")

    by: TargetBy
    name: str
    role: str | None = None


class Step(BaseModel):
    """A single deterministic workflow step."""

    model_config = ConfigDict(extra="forbid")

    action: ActionType
    target: StepTarget | None = None
    field_key: str | None = None

    @model_validator(mode="after")
    def validate_action_constraints(self) -> "Step":
        if self.action == ActionType.GOTO_START:
            if self.field_key is not None:
                raise ValueError("goto_start must not specify a field_key")
        elif self.action == ActionType.FILL_FIELD:
            if not self.field_key:
                raise ValueError("fill_field requires a field_key")
            if not self.target:
                raise ValueError("fill_field requires a target")
        elif self.action == ActionType.CLICK_BUTTON:
            if self.field_key is not None:
                raise ValueError("click_button must not specify a field_key")
            if not self.target:
                raise ValueError("click_button requires a target")
        return self

    def validate_against_intent(self, intent: Intent) -> None:
        """Verify that fill_field references an existing field_key in the intent test_data."""
        if self.action == ActionType.FILL_FIELD:
            if not self.field_key or self.field_key not in intent.test_data:
                raise ValueError(
                    f"field_key '{self.field_key}' is not defined in intent test_data. "
                    f"Valid keys: {list(intent.test_data.keys())}"
                )


class Recipe(BaseModel):
    """Versioned recipe consisting of deterministic steps."""

    model_config = ConfigDict(extra="forbid")

    intent_id: str
    version: int
    steps: list[Step]
    created_by: CreatedBy = CreatedBy.HUMAN
    parent_version: int | None = None
    intent_hash: str

    def validate_against_intent(self, intent: Intent) -> None:
        """Validate recipe against intent id, content hash, and step field keys."""
        if self.intent_id != intent.id:
            raise ValueError(
                f"Recipe intent_id '{self.intent_id}' does not match intent id '{intent.id}'"
            )
        if self.intent_hash != intent.content_hash:
            raise ValueError(
                f"Recipe intent_hash '{self.intent_hash}' does not match "
                f"intent content_hash '{intent.content_hash}'"
            )
        for step in self.steps:
            step.validate_against_intent(intent)


class StepResult(BaseModel):
    """Result of executing a single recipe step."""

    model_config = ConfigDict(extra="forbid")

    step_index: int
    step: Step
    success: bool
    duration_ms: float = 0.0
    error_message: str | None = None
    failure_type: FailureType | None = None


class RunResult(BaseModel):
    """Comprehensive result of an end-to-end recipe run."""

    model_config = ConfigDict(extra="forbid")

    status: Status
    steps: list[StepResult] = Field(default_factory=list)
    failed_step_index: int | None = None
    failure_type: FailureType | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    agent_explanation: str | None = None
