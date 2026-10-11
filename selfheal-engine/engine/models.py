"""Data models for immutable intents, versioned recipes, and test execution results."""

from enum import Enum
import hashlib
import json
import re
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


class Check(BaseModel):
    """Individual verification check result."""

    model_config = ConfigDict(extra="forbid")

    name: str
    passed: bool
    detail: str
    evidence: Any = None


class VerificationResult(BaseModel):
    """Aggregated deterministic verification result."""

    model_config = ConfigDict(extra="forbid")

    passed: bool
    checks: list[Check]


class RunResult(BaseModel):
    """Comprehensive result of an end-to-end recipe run."""

    model_config = ConfigDict(extra="forbid")

    status: Status
    steps: list[StepResult] = Field(default_factory=list)
    failed_step_index: int | None = None
    failure_type: FailureType | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    agent_explanation: str | None = None
    verification: VerificationResult | None = None


# -------------------------------------------------------------
# Module 6: UI Snapshot and Diff Models
# -------------------------------------------------------------

_CREDIT_CARD_REGEX = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


class UIElement(BaseModel):
    """Structural information of an interactive or key UI element.

    Strict privacy: Never contains input values, passwords, card details, cookies, or tokens.
    """

    model_config = ConfigDict(extra="forbid")

    role: str
    name: str
    label: str | None = None
    element_id: str | None = None
    tag_name: str
    element_type: str | None = None
    placeholder: str | None = None
    input_name: str | None = None
    heading: str | None = None
    page_path: str = "/"
    enabled: bool = True
    visible: bool = True

    @model_validator(mode="after")
    def verify_privacy_invariants(self) -> "UIElement":
        """Verify no sensitive data (card numbers, secrets) is captured in structural fields."""
        fields_to_check = [
            self.role,
            self.name,
            self.label or "",
            self.element_id or "",
            self.placeholder or "",
            self.heading or "",
        ]
        for field in fields_to_check:
            if _CREDIT_CARD_REGEX.search(field):
                raise ValueError("Privacy violation: UIElement contains credit card number")
        return self


class PageSnapshot(BaseModel):
    """Snapshot of structural UI information for a single page."""

    model_config = ConfigDict(extra="forbid")

    page_path: str
    title: str = ""
    headings: list[str] = Field(default_factory=list)
    elements: list[UIElement] = Field(default_factory=list)


class UIInventory(BaseModel):
    """Inventory of structural UI information across pages of a version / workflow."""

    model_config = ConfigDict(extra="forbid")

    intent_id: str
    app_version: str
    pages: list[PageSnapshot] = Field(default_factory=list)
    created_at: str | None = None

    @property
    def all_elements(self) -> list[UIElement]:
        """Aggregate all elements across all pages."""
        items: list[UIElement] = []
        for p in self.pages:
            items.extend(p.elements)
        return items

    @property
    def page_paths(self) -> list[str]:
        """Return list of distinct page paths in order."""
        return [p.page_path for p in self.pages]

    def get_page(self, path: str) -> PageSnapshot | None:
        """Find page snapshot by path."""
        for p in self.pages:
            if p.page_path == path:
                return p
        return None

    def find_elements(
        self, role: str | None = None, name: str | None = None
    ) -> list[UIElement]:
        """Filter elements across all pages by role and/or accessible name."""
        results = self.all_elements
        if role is not None:
            results = [e for e in results if e.role.lower() == role.lower()]
        if name is not None:
            results = [e for e in results if e.name.lower() == name.lower()]
        return results


class RenamedElement(BaseModel):
    """Mapping between a baseline element and a renamed element in the current UI."""

    model_config = ConfigDict(extra="forbid")

    old_element: UIElement
    new_element: UIElement
    old_name: str
    new_name: str
    confidence: float = 1.0


class AmbiguousElement(BaseModel):
    """Element matching multiple candidates or having duplicate accessible names."""

    model_config = ConfigDict(extra="forbid")

    element: UIElement
    matching_candidates: list[UIElement] = Field(default_factory=list)
    reason: str


class FlowDiff(BaseModel):
    """Comparison of page paths / navigation flow between baseline and current."""

    model_config = ConfigDict(extra="forbid")

    baseline_paths: list[str]
    current_paths: list[str]
    is_flow_changed: bool
    added_paths: list[str] = Field(default_factory=list)
    removed_paths: list[str] = Field(default_factory=list)


class SnapshotDiff(BaseModel):
    """Complete diff report comparing baseline UI to current UI."""

    model_config = ConfigDict(extra="forbid")

    unchanged: list[UIElement] = Field(default_factory=list)
    added: list[UIElement] = Field(default_factory=list)
    removed: list[UIElement] = Field(default_factory=list)
    renamed: list[RenamedElement] = Field(default_factory=list)
    ambiguous: list[AmbiguousElement] = Field(default_factory=list)
    flow: FlowDiff | None = None
    has_drift: bool = False

    def summary(self) -> dict[str, Any]:
        """Return dictionary summary of diff metrics."""
        return {
            "unchanged_count": len(self.unchanged),
            "added_count": len(self.added),
            "removed_count": len(self.removed),
            "renamed_count": len(self.renamed),
            "ambiguous_count": len(self.ambiguous),
            "has_drift": self.has_drift,
            "is_flow_changed": self.flow.is_flow_changed if self.flow else False,
        }

    def get_renamed_map(self) -> dict[str, str]:
        """Return a mapping of old accessible names to new accessible names."""
        return {r.old_name: r.new_name for r in self.renamed}


# -------------------------------------------------------------
# Module 7: Failure Classification and Context Models
# -------------------------------------------------------------

class Verdict(str, Enum):
    """Triage verdict categories."""

    UI_DRIFT = "UI_DRIFT"
    APP_BUG = "APP_BUG"
    FLAKY = "FLAKY"
    UNKNOWN = "UNKNOWN"


class RecommendedAction(str, Enum):
    """Next action recommended by the rule-based triage classifier."""

    HEAL = "HEAL"
    REPORT = "REPORT"
    RETRY = "RETRY"
    REVIEW = "REVIEW"


class Triage(BaseModel):
    """Deterministic failure triage decision with confidence and supporting evidence."""

    model_config = ConfigDict(extra="forbid")

    verdict: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    recommended: RecommendedAction
    rule_name: str | None = None


class FailureContext(BaseModel):
    """Compact failure context packaged for triage reporting and healing agents.

    Strict privacy: contains only field_keys (names), never actual test data values,
    card numbers, passwords, or tokens. Kept under ~6k tokens.
    """

    model_config = ConfigDict(extra="forbid")

    goal: str
    field_keys: list[str]
    failed_step_index: int | None = None
    failure_type: FailureType | None = None
    passed_steps: list[Step] = Field(default_factory=list)
    failed_step: Step | None = None
    current_inventory: UIInventory | PageSnapshot | None = None
    diff_summary: str = ""
    evidence: dict[str, Any] = Field(default_factory=dict)
    triage: Triage

    @model_validator(mode="after")
    def verify_privacy(self) -> "FailureContext":
        """Verify no credit card numbers or secret tokens are leaked in field keys or text."""
        for k in self.field_keys:
            if _CREDIT_CARD_REGEX.search(k):
                raise ValueError("Privacy violation: Credit card number found in field_keys")
        if _CREDIT_CARD_REGEX.search(self.diff_summary):
            raise ValueError("Privacy violation: Credit card number found in diff_summary")
        return self

    def estimated_tokens(self) -> int:
        """Estimate token count based on JSON serialized character count."""
        return max(1, len(self.model_dump_json()) // 4)


# -------------------------------------------------------------
# Module 8: Healing Result Model
# -------------------------------------------------------------

class HealResult(BaseModel):
    """Result of an automated self-healing attempt."""

    model_config = ConfigDict(extra="forbid")

    status: Status
    recipe: Recipe | None = None
    executed_steps: list[Step] = Field(default_factory=list)
    explanation: str = ""
    trace: list[dict[str, Any]] = Field(default_factory=list)
    clean_replay_result: RunResult | None = None
    is_recorded: bool = False


# -------------------------------------------------------------
# Module 10: Run Report Model
# -------------------------------------------------------------

class TimelineEvent(BaseModel):
    """Chronological event in the run timeline."""

    model_config = ConfigDict(extra="forbid")

    timestamp: str
    phase: str
    message: str
    level: str = "info"
    details: dict[str, Any] = Field(default_factory=dict)


class RunReport(BaseModel):
    """Comprehensive, self-explaining run report per Module 10 and AGENTS.md."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    timestamp: str
    status: Status
    headline: str
    app_version: str
    intent_id: str
    intent_goal: str
    initial_recipe_version: int
    new_recipe_version: int | None = None
    healed: bool = False
    mode: str = "NONE"  # "LIVE" | "RECORDED" | "NONE"
    provider: str = ""
    llm_calls: int = 0
    duration_ms: float = 0.0
    action_count: int = 0
    triage: Triage | None = None
    what_broke: str = ""
    what_changed: str = ""
    agent_explanation: str = ""
    verification: VerificationResult | None = None
    timeline: list[TimelineEvent] = Field(default_factory=list)
    initial_recipe_steps: list[dict[str, Any]] = Field(default_factory=list)
    final_recipe_steps: list[dict[str, Any]] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def verify_no_secrets(self) -> "RunReport":
        """Verify strict privacy: no credit card numbers or raw tokens in report fields."""
        fields_to_check = [
            self.headline,
            self.what_broke,
            self.what_changed,
            self.agent_explanation,
        ]
        for val in fields_to_check:
            if _CREDIT_CARD_REGEX.search(val):
                raise ValueError("Privacy violation: RunReport contains credit card number")
        return self


