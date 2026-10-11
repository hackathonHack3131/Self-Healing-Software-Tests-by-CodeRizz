"""Comprehensive tests for deterministic step proposal validator (Module 8)."""

import pytest
from engine.models import (
    ActionType,
    ExpectedOutcome,
    Intent,
    Step,
    StepTarget,
    TargetBy,
    UIElement,
)
from engine.validator import Decision, StepProposal, validate_step_proposal


@pytest.fixture
def checkout_intent() -> Intent:
    return Intent(
        id="checkout",
        title="Complete checkout",
        goal="Complete checkout with valid test details",
        test_data={
            "full_name": "Alex Tester",
            "email": "alex@example.com",
            "street_address": "123 Market St",
            "card_number": "4111111111111111",
            "expiry": "12/28",
            "cvc": "123",
        },
        expected_outcome=ExpectedOutcome(
            confirmation_phrase="Thank you for your order",
            order_id_pattern=r"ORD-\d+",
            expected_total="36.50",
        ),
    )


@pytest.fixture
def sample_inventory() -> dict[str, UIElement]:
    return {
        "ref_1": UIElement(
            role="button",
            name="Proceed to Checkout",
            tag_name="button",
            visible=True,
            enabled=True,
        ),
        "ref_2": UIElement(
            role="textbox",
            name="Full name",
            label="Full name",
            tag_name="input",
            element_type="text",
            visible=True,
            enabled=True,
        ),
        "ref_3": UIElement(
            role="textbox",
            name="Email address",
            label="Email address",
            tag_name="input",
            element_type="email",
            visible=True,
            enabled=True,
        ),
        "ref_hidden": UIElement(
            role="textbox",
            name="Hidden Input",
            tag_name="input",
            visible=False,
            enabled=True,
        ),
        "ref_disabled": UIElement(
            role="button",
            name="Disabled Button",
            tag_name="button",
            visible=True,
            enabled=False,
        ),
        "ref_non_button": UIElement(
            role="heading",
            name="Cart Summary",
            tag_name="h1",
            visible=True,
            enabled=True,
        ),
        "ref_ambiguous_1": UIElement(
            role="button",
            name="Submit",
            tag_name="button",
            visible=True,
            enabled=True,
        ),
        "ref_ambiguous_2": UIElement(
            role="button",
            name="Submit",
            tag_name="button",
            visible=True,
            enabled=True,
        ),
    }


def test_validator_approves_valid_fill_field(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.FILL_FIELD,
        ref="ref_2",
        field_key="full_name",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is True
    assert decision.step is not None
    assert decision.step.action == ActionType.FILL_FIELD
    assert decision.step.field_key == "full_name"
    assert decision.target.name == "Full name"
    assert decision.target.by == TargetBy.LABEL


def test_validator_approves_valid_click_button(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.CLICK_BUTTON,
        ref="ref_1",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is True
    assert decision.step is not None
    assert decision.step.action == ActionType.CLICK_BUTTON
    assert decision.step.field_key is None
    assert decision.target.name == "Proceed to Checkout"
    assert decision.target.by == TargetBy.ROLE


def test_validator_rejects_disallowed_actions(checkout_intent, sample_inventory):
    # goto_start is forbidden for agent proposals
    prop = StepProposal(action="goto_start", ref="ref_1")
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("Disallowed action" in r for r in decision.reasons)

    # random action
    prop_bad = {"action": "delete_all", "ref": "ref_1"}
    decision = validate_step_proposal(prop_bad, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False


def test_validator_rejects_missing_ref(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.FILL_FIELD,
        ref="ref_unknown_999",
        field_key="full_name",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("was not found in the latest inventory" in r for r in decision.reasons)


def test_validator_rejects_hidden_element(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.FILL_FIELD,
        ref="ref_hidden",
        field_key="full_name",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("not visible" in r for r in decision.reasons)


def test_validator_rejects_disabled_element(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.CLICK_BUTTON,
        ref="ref_disabled",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("disabled" in r for r in decision.reasons)


def test_validator_rejects_literal_value(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.FILL_FIELD,
        ref="ref_2",
        field_key="full_name",
        literal_value="Alex Tester Literal",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("Literal values are forbidden" in r for r in decision.reasons)


def test_validator_rejects_invalid_field_key(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.FILL_FIELD,
        ref="ref_2",
        field_key="non_existent_key",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("not in intent test_data" in r for r in decision.reasons)


def test_validator_rejects_click_on_non_button(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.CLICK_BUTTON,
        ref="ref_non_button",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("not a button" in r for r in decision.reasons)


def test_validator_rejects_click_with_field_key(checkout_intent, sample_inventory):
    prop = StepProposal(
        action=ActionType.CLICK_BUTTON,
        ref="ref_1",
        field_key="full_name",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("click_button must not specify a field_key" in r for r in decision.reasons)


def test_validator_rejects_ambiguous_element(checkout_intent, sample_inventory):
    # Both ref_ambiguous_1 and ref_ambiguous_2 have name="Submit" and role="button"
    prop = StepProposal(
        action=ActionType.CLICK_BUTTON,
        ref="ref_ambiguous_1",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("cannot be expressed as a unique exact semantic target" in r for r in decision.reasons)


def test_validator_rejects_fill_on_non_input(checkout_intent, sample_inventory):
    # ref_1 is a button, not an editable input
    prop = StepProposal(
        action=ActionType.FILL_FIELD,
        ref="ref_1",
        field_key="full_name",
    )
    decision = validate_step_proposal(prop, checkout_intent, inventory=sample_inventory)
    assert decision.approved is False
    assert any("not an editable input field" in r for r in decision.reasons)


def test_validator_rejects_when_action_limit_reached(checkout_intent, sample_inventory):
    from types import SimpleNamespace
    run_state = SimpleNamespace(action_count=10, max_actions=10)
    prop = StepProposal(
        action=ActionType.CLICK_BUTTON,
        ref="ref_1",
    )
    decision = validate_step_proposal(
        prop, checkout_intent, run_state=run_state, inventory=sample_inventory
    )
    assert decision.approved is False
    assert any("action limit (10) reached" in r for r in decision.reasons)


