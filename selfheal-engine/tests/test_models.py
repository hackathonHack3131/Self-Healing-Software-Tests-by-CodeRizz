"""Tests for Pydantic v2 data models and strict contracts."""

import pytest
from pydantic import ValidationError
from engine.models import (
    ActionType,
    CreatedBy,
    ExpectedOutcome,
    FailureType,
    Intent,
    Recipe,
    RunResult,
    Status,
    Step,
    StepResult,
    StepTarget,
    TargetBy,
)


@pytest.fixture
def sample_intent():
    """Sample valid Intent instance."""
    return Intent(
        id="checkout",
        title="Complete Checkout",
        goal="Complete checkout with a valid credit card",
        test_data={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "street_address": "123 Main St",
        },
        expected_outcome=ExpectedOutcome(
            confirmation_phrase="Order confirmed",
            order_id_pattern="QA-[0-9]+",
            expected_total=36.50,
        ),
    )


def test_extra_fields_rejected():
    """Verify that extra fields are rejected on all models (extra='forbid')."""
    with pytest.raises(ValidationError):
        Step(action=ActionType.GOTO_START, extra_field="forbidden")  # type: ignore[call-arg]

    with pytest.raises(ValidationError):
        StepTarget(by=TargetBy.LABEL, name="Name", unexpected="forbidden")  # type: ignore[call-arg]


def test_step_carrying_literal_value_rejected():
    """Verify that steps have no value field and reject literal values."""
    with pytest.raises(ValidationError):
        Step(
            action=ActionType.FILL_FIELD,
            target=StepTarget(by=TargetBy.LABEL, name="Name"),
            field_key="full_name",
            value="Literal Value",  # type: ignore[call-arg]
        )


def test_click_button_with_field_key_rejected():
    """Verify click_button cannot have a field_key."""
    with pytest.raises(ValidationError):
        Step(
            action=ActionType.CLICK_BUTTON,
            target=StepTarget(by=TargetBy.ROLE, name="Submit"),
            field_key="full_name",
        )


def test_goto_start_with_field_key_rejected():
    """Verify goto_start cannot have a field_key."""
    with pytest.raises(ValidationError):
        Step(action=ActionType.GOTO_START, field_key="any_key")


def test_fill_field_without_field_key_rejected():
    """Verify fill_field requires a field_key."""
    with pytest.raises(ValidationError):
        Step(
            action=ActionType.FILL_FIELD,
            target=StepTarget(by=TargetBy.LABEL, name="Name"),
        )


def test_fill_field_with_unknown_field_key_rejected(sample_intent):
    """Verify fill_field referencing a field_key not in intent.test_data is rejected."""
    step = Step(
        action=ActionType.FILL_FIELD,
        target=StepTarget(by=TargetBy.LABEL, name="Unknown"),
        field_key="non_existent_field",
    )
    with pytest.raises(ValueError, match="not defined in intent test_data"):
        step.validate_against_intent(sample_intent)


def test_intent_is_frozen(sample_intent):
    """Verify that Intent is immutable and attribute mutation raises ValidationError."""
    with pytest.raises(ValidationError):
        sample_intent.goal = "Changed goal"  # type: ignore[misc]

    with pytest.raises(ValidationError):
        sample_intent.test_data = {"tampered": "value"}  # type: ignore[misc]

    with pytest.raises(ValidationError):
        sample_intent.id = "tampered_id"  # type: ignore[misc]


def test_intent_content_hash_is_deterministic(sample_intent):
    """Verify intent content_hash is consistent and changes with any field update."""
    h1 = sample_intent.content_hash
    assert len(h1) == 64
    assert sample_intent.content_hash == h1

    # Slightly different intent
    modified = Intent(
        id=sample_intent.id,
        title=sample_intent.title,
        goal=sample_intent.goal + ".",  # mutated by 1 dot
        test_data=sample_intent.test_data,
        expected_outcome=sample_intent.expected_outcome,
    )
    assert modified.content_hash != h1


def test_run_result_and_step_result_creation():
    """Verify StepResult and RunResult can be constructed with enums."""
    step = Step(action=ActionType.GOTO_START)
    sr = StepResult(
        step_index=0,
        step=step,
        success=True,
        duration_ms=120.5,
    )
    run_result = RunResult(
        status=Status.PASS_NO_HEAL,
        steps=[sr],
        evidence={"nav": "ok"},
    )
    assert run_result.status == Status.PASS_NO_HEAL
    assert len(run_result.steps) == 1
