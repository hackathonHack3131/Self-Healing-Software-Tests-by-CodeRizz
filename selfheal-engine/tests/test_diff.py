"""Tests for UI Diff engine: unchanged UI, renamed fields, added/removed elements, duplicates, and flow changes."""

import pytest
from engine.browser import BrowserSession
from engine.diff import diff_snapshots
from engine.models import PageSnapshot, UIElement, UIInventory
from engine.recipes import load_intent, load_recipe
from engine.snapshot import capture_page_snapshot, load_baseline_inventory


@pytest.fixture
def checkout_intent():
    return load_intent("checkout")


@pytest.fixture
def recipe_v1(checkout_intent):
    return load_recipe("checkout", version=1, intent=checkout_intent)


def _make_elem(
    name: str,
    role: str = "textbox",
    element_id: str | None = None,
    label: str | None = None,
    placeholder: str | None = None,
    input_name: str | None = None,
    page_path: str = "/v/a/",
) -> UIElement:
    return UIElement(
        role=role,
        name=name,
        label=label or name,
        element_id=element_id or name.lower().replace(" ", "-"),
        tag_name="button" if role == "button" else "input",
        element_type=None if role == "button" else "text",
        placeholder=placeholder,
        input_name=input_name,
        page_path=page_path,
        enabled=True,
        visible=True,
    )


# -------------------------------------------------------------
# 1. Unchanged UI Tests
# -------------------------------------------------------------

def test_diff_unchanged_ui():
    """Verify comparing identical snapshots reports all unchanged and zero drift."""
    elements = [
        _make_elem("Name", role="textbox"),
        _make_elem("Email", role="textbox"),
        _make_elem("Checkout", role="button"),
    ]

    snapshot1 = PageSnapshot(page_path="/v/a/", title="Checkout", elements=elements)
    snapshot2 = PageSnapshot(page_path="/v/a/", title="Checkout", elements=elements)

    diff = diff_snapshots(snapshot1, snapshot2)

    assert diff.has_drift is False
    assert len(diff.unchanged) == 3
    assert len(diff.added) == 0
    assert len(diff.removed) == 0
    assert len(diff.renamed) == 0
    assert len(diff.ambiguous) == 0


# -------------------------------------------------------------
# 2. Renamed Fields Tests
# -------------------------------------------------------------

def test_diff_renamed_fields():
    """Verify renamed fields between Version A and Version B are correctly reported."""
    baseline_elements = [
        _make_elem("Name", role="textbox", element_id="name", input_name="name"),
        _make_elem("Email", role="textbox", element_id="email", input_name="email"),
        _make_elem("Address", role="textbox", element_id="address", input_name="address"),
        _make_elem("Card number", role="textbox", element_id="card_number", input_name="card_number"),
        _make_elem("Expiry", role="textbox", element_id="expiry", placeholder="MM/YY", input_name="expiry"),
        _make_elem("CVC", role="textbox", element_id="cvc", input_name="cvc"),
        _make_elem("Checkout", role="button", element_id="checkout-btn"),
    ]

    current_elements = [
        _make_elem("Full name", role="textbox", element_id="b-shipping-name", input_name="full_name"),
        _make_elem("Email address", role="textbox", element_id="b-shipping-email", input_name="email_address"),
        _make_elem("Street address", role="textbox", element_id="b-shipping-address", input_name="street_address"),
        _make_elem("Credit card #", role="textbox", element_id="b-payment-card", input_name="card_number"),
        _make_elem("Valid thru (MM/YY)", role="textbox", element_id="b-payment-expiry", placeholder="MM/YY", input_name="expiry"),
        _make_elem("Security code", role="textbox", element_id="b-payment-cvc", input_name="cvc"),
        _make_elem("Continue to payment", role="button", element_id="continue-btn"),
    ]

    diff = diff_snapshots(baseline_elements, current_elements)

    assert diff.has_drift is True
    assert len(diff.renamed) >= 6

    renamed_map = diff.get_renamed_map()
    assert renamed_map.get("Name") == "Full name"
    assert renamed_map.get("Email") == "Email address"
    assert renamed_map.get("Address") == "Street address"
    assert renamed_map.get("Card number") == "Credit card #"
    assert renamed_map.get("Expiry") == "Valid thru (MM/YY)"
    assert renamed_map.get("CVC") == "Security code"
    assert renamed_map.get("Checkout") == "Continue to payment"


# -------------------------------------------------------------
# 3. Added and Removed Elements Tests
# -------------------------------------------------------------

def test_diff_added_elements():
    """Verify newly introduced elements are classified as added."""
    baseline = [
        _make_elem("Name", role="textbox"),
        _make_elem("Checkout", role="button"),
    ]
    current = [
        _make_elem("Name", role="textbox"),
        _make_elem("Checkout", role="button"),
        _make_elem("Coupon code", role="textbox", element_id="promo-code"),
        _make_elem("Apply Coupon", role="button", element_id="btn-coupon"),
    ]

    diff = diff_snapshots(baseline, current)

    assert diff.has_drift is True
    assert len(diff.unchanged) == 2
    assert len(diff.added) == 2
    added_names = {e.name for e in diff.added}
    assert "Coupon code" in added_names
    assert "Apply Coupon" in added_names


def test_diff_removed_elements():
    """Verify missing elements from baseline are classified as removed."""
    baseline = [
        _make_elem("Name", role="textbox"),
        _make_elem("Fax number", role="textbox", element_id="fax"),
        _make_elem("Checkout", role="button"),
    ]
    current = [
        _make_elem("Name", role="textbox"),
        _make_elem("Checkout", role="button"),
    ]

    diff = diff_snapshots(baseline, current)

    assert diff.has_drift is True
    assert len(diff.unchanged) == 2
    assert len(diff.removed) == 1
    assert diff.removed[0].name == "Fax number"


# -------------------------------------------------------------
# 4. Duplicate Matches / Ambiguity Tests
# -------------------------------------------------------------

def test_diff_duplicate_matches_ambiguous():
    """Verify duplicate accessible names on current page are classified as ambiguous."""
    baseline = [
        _make_elem("Submit", role="button"),
    ]
    current = [
        _make_elem("Submit", role="button", element_id="btn-submit-1"),
        _make_elem("Submit", role="button", element_id="btn-submit-2"),
    ]

    diff = diff_snapshots(baseline, current)

    assert diff.has_drift is True
    assert len(diff.ambiguous) >= 2
    assert any("Multiple elements" in amb.reason for amb in diff.ambiguous)
    for amb in diff.ambiguous:
        assert "Submit" in amb.element.name or "Submit" in amb.reason
        assert "Multiple elements" in amb.reason or "equally confident" in amb.reason


# -------------------------------------------------------------
# 5. Flow Changes Tests
# -------------------------------------------------------------

def test_diff_flow_changes_detected():
    """Verify multi-step workflow changes are reported in flow diff."""
    baseline_inv = UIInventory(
        intent_id="checkout",
        app_version="a",
        pages=[
            PageSnapshot(page_path="/v/a/", title="Checkout", elements=[]),
            PageSnapshot(page_path="/v/a/confirmation", title="Confirmed", elements=[]),
        ],
    )

    current_inv = UIInventory(
        intent_id="checkout",
        app_version="b",
        pages=[
            PageSnapshot(page_path="/v/b/", title="Cart", elements=[]),
            PageSnapshot(page_path="/v/b/shipping", title="Shipping", elements=[]),
            PageSnapshot(page_path="/v/b/payment", title="Payment", elements=[]),
            PageSnapshot(page_path="/v/b/review", title="Review", elements=[]),
            PageSnapshot(page_path="/v/b/confirmation", title="Confirmed", elements=[]),
        ],
    )

    diff = diff_snapshots(baseline_inv, current_inv)

    assert diff.has_drift is True
    assert diff.flow is not None
    assert diff.flow.is_flow_changed is True
    assert "/v/b/shipping" in diff.flow.added_paths
    assert "/v/b/payment" in diff.flow.added_paths
    assert "/v/b/review" in diff.flow.added_paths
    assert "/v/a/" in diff.flow.removed_paths


def test_diff_flow_unchanged():
    """Verify unchanged navigation paths report is_flow_changed = False."""
    pages = [
        PageSnapshot(page_path="/v/a/", title="Checkout", elements=[]),
        PageSnapshot(page_path="/v/a/confirmation", title="Confirmed", elements=[]),
    ]
    inv1 = UIInventory(intent_id="checkout", app_version="a", pages=pages)
    inv2 = UIInventory(intent_id="checkout", app_version="a", pages=pages)

    diff = diff_snapshots(inv1, inv2)

    assert diff.flow is not None
    assert diff.flow.is_flow_changed is False
    assert len(diff.flow.added_paths) == 0
    assert len(diff.flow.removed_paths) == 0


# -------------------------------------------------------------
# 6. Live Version A vs Version B Integration Test
# -------------------------------------------------------------

async def test_diff_live_version_a_vs_version_b_integration(make_settings):
    """Verify comparing live Version A baseline against Version B detects drift and renames."""
    # Ensure baseline exists (or load it)
    try:
        baseline = load_baseline_inventory()
    except FileNotFoundError:
        pytest.skip("Version A baseline not yet created")

    settings, start_url = make_settings("/v/b/shipping")

    # Visit Version B shipping page and capture snapshot
    async with BrowserSession(settings=settings, start_url=start_url) as session:
        await session.goto_start()
        b_shipping_snapshot = await capture_page_snapshot(session.page)

    diff = diff_snapshots(baseline, b_shipping_snapshot)

    assert diff.has_drift is True
    # The fields on shipping page should be recognized as renames of baseline fields
    renamed_map = diff.get_renamed_map()
    assert "Name" in renamed_map
    assert renamed_map["Name"] == "Full name"
    assert "Email" in renamed_map
    assert renamed_map["Email"] == "Email address"
    assert "Address" in renamed_map
    assert renamed_map["Address"] == "Street address"
