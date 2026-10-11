"""Deterministic step proposal validator for self-healing tests.

Enforces strict rules on agent-proposed actions before execution:
- Only fill_field and click_button actions are allowed.
- Target ref must exist in the latest inventory.
- Target element must be visible, enabled, and uniquely resolvable.
- fill_field must use a valid field_key from intent test_data and never literal values.
- click_button must target a button element and must not specify a field_key.
- The element must resolve to a unique semantic target (role & name or label).
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from engine.models import (
    ActionType,
    Intent,
    PageSnapshot,
    Step,
    StepTarget,
    TargetBy,
    UIElement,
    UIInventory,
)


class StepProposal(BaseModel):
    """An action proposal submitted by the healing agent."""

    model_config = ConfigDict(extra="forbid")

    action: ActionType | str
    ref: str
    field_key: str | None = None
    literal_value: str | None = None


class Decision(BaseModel):
    """Deterministic validation decision for a proposed step."""

    model_config = ConfigDict(extra="forbid")

    approved: bool
    reasons: list[str] = Field(default_factory=list)
    step: Step | None = None
    target: StepTarget | None = None


def resolve_inventory_ref(
    ref: str,
    inventory: Any,
) -> tuple[UIElement | None, list[UIElement]]:
    """Resolve a ref key to a UIElement and return (target_element, all_elements)."""
    if inventory is None:
        return None, []

    if isinstance(inventory, dict):
        all_elements = list(inventory.values())
        elem = inventory.get(ref)
        if elem is not None:
            return elem, all_elements
        # Also try matching by element_id or accessible name
        for el in all_elements:
            if getattr(el, "element_id", None) == ref or getattr(el, "name", None) == ref:
                return el, all_elements
        return None, all_elements

    if isinstance(inventory, PageSnapshot):
        all_elements = inventory.elements
    elif isinstance(inventory, UIInventory):
        all_elements = inventory.all_elements
    elif isinstance(inventory, (list, tuple)):
        all_elements = list(inventory)
    elif hasattr(inventory, "elements"):
        all_elements = list(inventory.elements)
    elif hasattr(inventory, "all_elements"):
        all_elements = list(inventory.all_elements)
    else:
        return None, []

    # Try 1-based or 0-based ref indexing e.g. ref_1, ref_2
    if ref.startswith("ref_"):
        try:
            num = int(ref.split("_")[1])
            # Check 1-indexed first (standard in tools)
            if 1 <= num <= len(all_elements):
                return all_elements[num - 1], all_elements
            # Check 0-indexed
            if 0 <= num < len(all_elements):
                return all_elements[num], all_elements
        except (ValueError, IndexError):
            pass

    # Try matching element_id, name, or label
    for el in all_elements:
        if getattr(el, "element_id", None) == ref:
            return el, all_elements
        if getattr(el, "name", None) == ref:
            return el, all_elements
        if getattr(el, "label", None) == ref:
            return el, all_elements

    return None, all_elements


def _find_unique_target(
    target_elem: UIElement,
    action_type: ActionType,
    all_elements: list[UIElement],
) -> StepTarget | None:
    """Find a unique StepTarget strategy that uniquely identifies target_elem in all_elements."""
    # Visible candidates only for resolution uniqueness
    visible_elements = [e for e in all_elements if getattr(e, "visible", True)]

    if action_type == ActionType.CLICK_BUTTON:
        # For buttons, prefer ROLE ("button", name) first
        if target_elem.name and target_elem.name.strip():
            matches = [
                e
                for e in visible_elements
                if (e.name or "").strip() == target_elem.name.strip()
                and e.role.lower() in ("button", "link")
            ]
            if len(matches) == 1:
                return StepTarget(
                    by=TargetBy.ROLE,
                    role="button",
                    name=target_elem.name.strip(),
                )

        # Fallback to label if role wasn't unique or available
        if target_elem.label and target_elem.label.strip():
            matches = [
                e
                for e in visible_elements
                if (e.label or "").strip() == target_elem.label.strip()
            ]
            if len(matches) == 1:
                return StepTarget(
                    by=TargetBy.LABEL,
                    name=target_elem.label.strip(),
                )

    elif action_type == ActionType.FILL_FIELD:
        # For inputs, prefer LABEL first (Playwright accessible standard)
        if target_elem.label and target_elem.label.strip():
            matches = [
                e
                for e in visible_elements
                if (e.label or "").strip() == target_elem.label.strip()
            ]
            if len(matches) == 1:
                return StepTarget(
                    by=TargetBy.LABEL,
                    name=target_elem.label.strip(),
                )

        # Fallback to ROLE (role, name)
        if target_elem.name and target_elem.name.strip():
            matches = [
                e
                for e in visible_elements
                if (e.name or "").strip() == target_elem.name.strip()
                and e.role.lower() == target_elem.role.lower()
            ]
            if len(matches) == 1:
                return StepTarget(
                    by=TargetBy.ROLE,
                    role=target_elem.role,
                    name=target_elem.name.strip(),
                )

        # Fallback to PLACEHOLDER
        if target_elem.placeholder and target_elem.placeholder.strip():
            matches = [
                e
                for e in visible_elements
                if (e.placeholder or "").strip() == target_elem.placeholder.strip()
            ]
            if len(matches) == 1:
                return StepTarget(
                    by=TargetBy.PLACEHOLDER,
                    name=target_elem.placeholder.strip(),
                )

    return None


def validate_step_proposal(
    proposal: StepProposal | dict[str, Any] | Step,
    intent: Intent,
    run_state: Any = None,
    inventory: Any = None,
) -> Decision:
    """Validate an agent step proposal deterministically.

    Rejection criteria (AGENTS.md & Module 8 spec):
    1. Action is not fill_field or click_button.
    2. The ref is not in the latest inventory.
    3. The ref does not resolve to exactly one visible, enabled element.
    4. fill_field has no valid field_key or specifies any literal value.
    5. click_button targets a non-button element or specifies a field_key.
    6. The element cannot be expressed as a unique exact semantic target.
    """
    reasons: list[str] = []

    # Normalize proposal
    if isinstance(proposal, dict):
        try:
            prop = StepProposal.model_validate(proposal)
        except Exception as exc:
            return Decision(approved=False, reasons=[f"Invalid proposal payload: {exc}"])
    elif isinstance(proposal, Step):
        ref_val = getattr(proposal, "ref", "") or (
            proposal.target.name if proposal.target else ""
        )
        prop = StepProposal(
            action=proposal.action,
            ref=ref_val,
            field_key=proposal.field_key,
        )
    elif isinstance(proposal, StepProposal):
        prop = proposal
    else:
        return Decision(
            approved=False,
            reasons=[f"Unsupported proposal type: {type(proposal).__name__}"],
        )

    # 1. Action validation
    action_val = prop.action.value if hasattr(prop.action, "value") else str(prop.action)
    action_str = action_val.lower()

    if action_str not in (ActionType.FILL_FIELD.value, ActionType.CLICK_BUTTON.value):
        reasons.append(
            f"Disallowed action '{prop.action}'. Only 'fill_field' and 'click_button' are allowed."
        )
        return Decision(approved=False, reasons=reasons)

    act_enum = ActionType(action_str)

    # Check run_state limits if available
    if run_state is not None:
        action_count = getattr(run_state, "action_count", 0)
        max_actions = getattr(run_state, "max_actions", 10)
        if action_count >= max_actions:
            reasons.append(f"Maximum agent action limit ({max_actions}) reached.")

    # 2. Ref resolution in inventory
    target_elem, all_elements = resolve_inventory_ref(prop.ref, inventory)
    if target_elem is None:
        reasons.append(f"Ref '{prop.ref}' was not found in the latest inventory.")
        return Decision(approved=False, reasons=reasons)

    # 3. Visibility and enabled check
    if not getattr(target_elem, "visible", True):
        reasons.append(f"Target element '{prop.ref}' is not visible.")
    if not getattr(target_elem, "enabled", True):
        reasons.append(f"Target element '{prop.ref}' is disabled.")

    # 4. fill_field specific rules
    if act_enum == ActionType.FILL_FIELD:
        role = (target_elem.role or "").lower()
        tag = (target_elem.tag_name or "").lower()
        elem_type = (target_elem.element_type or "").lower()
        is_input = (
            role in ("textbox", "combobox", "searchbox", "spinbutton")
            or tag in ("input", "textarea", "select")
            or elem_type in ("text", "email", "password", "tel", "number", "url", "search")
        )
        if not is_input:
            reasons.append(
                f"Target element '{prop.ref}' (role='{target_elem.role}', tag='{target_elem.tag_name}') "
                "is not an editable input field."
            )

        if prop.literal_value is not None:
            reasons.append("Literal values are forbidden. Values must come from intent test_data.")
        if not prop.field_key:
            reasons.append("fill_field requires a valid 'field_key'.")
        elif prop.field_key not in intent.test_data:
            reasons.append(
                f"field_key '{prop.field_key}' is not in intent test_data. "
                f"Valid keys: {list(intent.test_data.keys())}"
            )


    # 5. click_button specific rules
    elif act_enum == ActionType.CLICK_BUTTON:
        if prop.field_key is not None:
            reasons.append("click_button must not specify a field_key.")
        if prop.literal_value is not None:
            reasons.append("click_button must not specify a literal value.")

        role = (target_elem.role or "").lower()
        tag = (target_elem.tag_name or "").lower()
        elem_type = (target_elem.element_type or "").lower()
        is_button = (
            role in ("button", "link")
            or tag in ("button", "a")
            or elem_type in ("button", "submit", "reset")
        )
        if not is_button:
            reasons.append(
                f"Target element '{prop.ref}' (role='{target_elem.role}', tag='{target_elem.tag_name}') "
                "is not a button or clickable element."
            )

    # 6. Unique exact semantic target resolution
    target = _find_unique_target(target_elem, act_enum, all_elements)
    if target is None:
        reasons.append(
            f"Target element '{prop.ref}' cannot be expressed as a unique exact semantic target. "
            "It either lacks an accessible name/label or has duplicate ambiguous matches."
        )

    if reasons:
        return Decision(approved=False, reasons=reasons, step=None, target=target)

    # Construct validated Step
    validated_step = Step(
        action=act_enum,
        target=target,
        field_key=prop.field_key,
    )

    return Decision(
        approved=True,
        reasons=[],
        step=validated_step,
        target=target,
    )
