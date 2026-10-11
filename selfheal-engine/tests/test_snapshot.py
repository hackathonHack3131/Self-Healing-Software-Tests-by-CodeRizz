"""Tests for UI structural snapshot capture, privacy invariants, and baseline creation."""

from pathlib import Path
import pytest
from engine.browser import BrowserSession
from engine.models import (
    Intent,
    PageSnapshot,
    Recipe,
    UIElement,
    UIInventory,
)
from engine.recipes import get_project_root, load_intent, load_recipe
from engine.snapshot import (
    BaselineVerificationError,
    capture_page_snapshot,
    create_version_a_baseline,
    get_baseline_path,
    load_baseline_inventory,
    save_baseline_inventory,
)


@pytest.fixture
def checkout_intent():
    return load_intent("checkout")


@pytest.fixture
def recipe_v1(checkout_intent):
    return load_recipe("checkout", version=1, intent=checkout_intent)


# -------------------------------------------------------------
# Unit & Synthetic Page Snapshot Tests
# -------------------------------------------------------------

async def test_capture_page_snapshot_structure(browser_session):
    """Test capturing structural UI information (roles, names, labels, IDs, headings, paths)."""
    html = """
    <!DOCTYPE html>
    <html>
      <head><title>Test Checkout Form</title></head>
      <body>
        <h1>Checkout Section</h1>
        <h2>Billing Details</h2>
        <form action="/submit" method="post">
          <div>
            <label for="cust-name">Full Name</label>
            <input type="text" id="cust-name" name="customer_name" placeholder="John Doe">
          </div>
          <div>
            <label for="cust-email">Email Address</label>
            <input type="email" id="cust-email" name="customer_email">
          </div>
          <button type="submit" id="btn-pay">Pay Now</button>
          <a href="/cancel" id="link-cancel">Cancel</a>
        </form>
      </body>
    </html>
    """
    await browser_session.page.set_content(html)

    snapshot = await capture_page_snapshot(browser_session.page)

    assert isinstance(snapshot, PageSnapshot)
    assert snapshot.title == "Test Checkout Form"
    assert "Checkout Section" in snapshot.headings
    assert "Billing Details" in snapshot.headings

    # Verify captured elements
    name_el = next((e for e in snapshot.elements if e.element_id == "cust-name"), None)
    assert name_el is not None
    assert name_el.role == "textbox"
    assert name_el.name == "Full Name"
    assert name_el.label == "Full Name"
    assert name_el.placeholder == "John Doe"
    assert name_el.input_name == "customer_name"
    assert name_el.enabled is True
    assert name_el.visible is True

    btn_el = next((e for e in snapshot.elements if e.element_id == "btn-pay"), None)
    assert btn_el is not None
    assert btn_el.role == "button"
    assert btn_el.name == "Pay Now"

    link_el = next((e for e in snapshot.elements if e.element_id == "link-cancel"), None)
    assert link_el is not None
    assert link_el.role == "link"
    assert link_el.name == "Cancel"


# -------------------------------------------------------------
# Privacy Invariant Tests (Requirement 2)
# -------------------------------------------------------------

async def test_privacy_never_stores_input_values(browser_session):
    """Verify that entered input values are NEVER stored in UIElement or PageSnapshot."""
    html = """
    <!DOCTYPE html>
    <html>
      <body>
        <label for="username">Username</label>
        <input type="text" id="username" value="secret_user_value">
      </body>
    </html>
    """
    await browser_session.page.set_content(html)
    # Type user value
    await browser_session.page.fill("#username", "my_confidential_login")

    snapshot = await capture_page_snapshot(browser_session.page)

    assert len(snapshot.elements) >= 1
    elem = snapshot.elements[0]

    # Verify UIElement has no value attribute and serialized JSON does not contain entered value
    assert not hasattr(elem, "value")
    serialized = snapshot.model_dump_json()
    assert "secret_user_value" not in serialized
    assert "my_confidential_login" not in serialized


async def test_privacy_never_stores_passwords_or_card_numbers(browser_session):
    """Verify that sensitive password inputs and card numbers are never stored."""
    html = """
    <!DOCTYPE html>
    <html>
      <body>
        <label for="pwd">Password</label>
        <input type="password" id="pwd" value="SuperSecretPassword123!">
        <label for="cc">Card number</label>
        <input type="text" id="cc" value="4242424242424242">
      </body>
    </html>
    """
    await browser_session.page.set_content(html)

    snapshot = await capture_page_snapshot(browser_session.page)
    dumped = snapshot.model_dump_json()

    assert "SuperSecretPassword123!" not in dumped
    assert "4242424242424242" not in dumped


async def test_privacy_never_stores_cookies_tokens_or_storage(browser_session):
    """Verify that cookies, tokens, and browser storage are completely excluded."""
    # Set cookies and storage on page
    await browser_session.goto_start()
    await browser_session.page.evaluate(
        """() => {
            document.cookie = "auth_token=super_secret_jwt_token_12345; path=/";
            localStorage.setItem("session_token", "secret_local_storage_val");
            sessionStorage.setItem("user_secret", "secret_session_val");
        }"""
    )

    snapshot = await capture_page_snapshot(browser_session.page)
    dumped = snapshot.model_dump_json()

    assert "super_secret_jwt_token_12345" not in dumped
    assert "secret_local_storage_val" not in dumped
    assert "secret_session_val" not in dumped
    assert "auth_token" not in dumped


def test_ui_element_rejects_card_numbers_via_validator():
    """Verify that attempting to create a UIElement with a raw credit card number raises ValueError."""
    with pytest.raises(ValueError, match="Privacy violation"):
        UIElement(
            role="textbox",
            name="4242424242424242",
            tag_name="input",
            page_path="/v/a/",
        )


# -------------------------------------------------------------
# Baseline Creation and Guard Tests (Requirements 4 & 5)
# -------------------------------------------------------------

async def test_create_version_a_baseline_passes_verifier_and_saves_inventory(
    make_settings, checkout_intent, recipe_v1
):
    """Create the Version A baseline only after real Version A passes the verifier (Requirement 4)."""
    settings, start_url = make_settings("/v/a/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        inventory = await create_version_a_baseline(session, recipe_v1, checkout_intent)

        assert inventory.app_version == "a"
        assert inventory.intent_id == "checkout"
        assert len(inventory.pages) == 2

        # Verify checkout page snapshot
        checkout_page = inventory.get_page("/v/a/")
        assert checkout_page is not None
        assert "Payment & Shipping Details" in checkout_page.headings
        input_names = [e.name for e in checkout_page.elements if e.role == "textbox"]
        assert "Name" in input_names
        assert "Email" in input_names
        assert "Address" in input_names
        assert "Card number" in input_names
        assert "Expiry" in input_names
        assert "CVC" in input_names

        # Verify confirmation page snapshot
        confirmation_page = inventory.get_page("/v/a/confirmation")
        assert confirmation_page is not None
        assert "Order confirmed" in confirmation_page.headings

    # Verify the baseline file exists on disk and is non-empty
    baseline_path = get_baseline_path()
    assert baseline_path.exists()
    assert baseline_path.stat().st_size > 0

    # Verify baseline can be loaded cleanly
    loaded = load_baseline_inventory()
    assert loaded.app_version == "a"
    assert len(loaded.pages) == 2


async def test_never_replace_baseline_with_version_b_c_d(
    make_settings, checkout_intent
):
    """Verify that Version B, C, or D can NEVER replace the trusted baseline (Requirement 5)."""
    settings, start_url = make_settings("/v/b/")

    fake_b_inventory = UIInventory(
        intent_id="checkout",
        app_version="b",
        pages=[PageSnapshot(page_path="/v/b/", title="Cart", headings=[], elements=[])],
    )

    # Directly saving with app_version='b' must raise ValueError
    with pytest.raises(ValueError, match="Only Version A is trusted"):
        save_baseline_inventory(fake_b_inventory)

    for invalid_version in ("c", "d"):
        invalid_inventory = UIInventory(
            intent_id="checkout",
            app_version=invalid_version,
            pages=[],
        )
        with pytest.raises(ValueError, match="Only Version A is trusted"):
            save_baseline_inventory(invalid_inventory)

    # Calling create_version_a_baseline with a non-Version A session must be refused immediately
    fake_recipe = Recipe(
        intent_id="checkout",
        version=1,
        steps=[],
        intent_hash=checkout_intent.content_hash,
    )
    async with BrowserSession(settings=settings, start_url=start_url) as session:
        with pytest.raises(ValueError, match="is not Version A"):
            await create_version_a_baseline(session, fake_recipe, checkout_intent)


async def test_create_baseline_refuses_when_verifier_fails(
    make_settings, checkout_intent, tmp_path
):
    """Verify that baseline creation is refused if deterministic verification fails (Requirement 4)."""
    settings, start_url = make_settings("/v/a/")

    # Create a broken recipe that skips all form filling and clicks immediately
    broken_recipe = Recipe(
        intent_id="checkout",
        version=1,
        steps=[],  # zero steps, won't complete checkout
        intent_hash=checkout_intent.content_hash,
    )

    output_baseline = tmp_path / "version_a_inventory.json"

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        with pytest.raises(BaselineVerificationError):
            await create_version_a_baseline(
                session, broken_recipe, checkout_intent, output_path=output_baseline
            )

    # Baseline file must NOT have been written
    assert not output_baseline.exists()
