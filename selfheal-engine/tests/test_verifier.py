"""Tests for deterministic verifier checks and business invariants."""

import pytest
from engine.browser import BrowserSession
from engine.executor import run_recipe
from engine.models import Intent, Recipe
from engine.recipes import load_intent, load_recipe
from engine.verifier import verify_outcome


@pytest.fixture
def checkout_intent():
    return load_intent("checkout")


@pytest.fixture
def recipe_v1(checkout_intent):
    return load_recipe("checkout", version=1, intent=checkout_intent)


def get_check_map(checks):
    """Helper returning a dict of check_name -> Check."""
    return {c.name: c for c in checks}


# -------------------------------------------------------------
# Synthetic Page Fixture Tests
# -------------------------------------------------------------

async def test_good_confirmation_passes_all_five_checks(
    browser_session, checkout_intent
):
    """Verify that a compliant confirmation page passes all 5 verification checks."""
    good_html = """
    <!DOCTYPE html>
    <html>
      <body>
        <h1>Order confirmed</h1>
        <p>Your order number is <strong id="order-id">QA-1042</strong></p>
        <p>Total: <strong id="order-total">$36.50</strong></p>
      </body>
    </html>
    """
    await browser_session.page.set_content(good_html)

    result = await verify_outcome(
        browser_session.page,
        checkout_intent,
        browser_session.monitor,
    )

    assert result.passed is True
    assert len(result.checks) == 5
    for c in result.checks:
        assert c.passed is True, f"Check {c.name} unexpectedly failed: {c.detail}"


async def test_missing_phrase_fails_confirmation_visible(
    browser_session, checkout_intent
):
    """Verify that missing the confirmation phrase fails confirmation_visible."""
    missing_phrase_html = """
    <!DOCTYPE html>
    <html>
      <body>
        <h1>Checkout Finished</h1>
        <p>Your order number is <strong>QA-1042</strong></p>
        <p>Total: <strong>$36.50</strong></p>
      </body>
    </html>
    """
    await browser_session.page.set_content(missing_phrase_html)

    result = await verify_outcome(
        browser_session.page,
        checkout_intent,
        browser_session.monitor,
    )

    assert result.passed is False
    cmap = get_check_map(result.checks)
    assert cmap["confirmation_visible"].passed is False
    assert cmap["order_id_present"].passed is True
    assert cmap["total_matches"].passed is True
    assert cmap["no_server_errors"].passed is True
    assert cmap["no_error_alert"].passed is True


async def test_confirmation_with_total_32_50_fails_total_matches_only(
    browser_session, checkout_intent
):
    """Verify that wrong total (32.50 instead of 36.50) fails total_matches only."""
    wrong_total_html = """
    <!DOCTYPE html>
    <html>
      <body>
        <h1>Order confirmed</h1>
        <p>Order number: <strong>QA-1042</strong></p>
        <div class="summary-total-row">Total Charged: <strong>$32.50</strong></div>
      </body>
    </html>
    """
    await browser_session.page.set_content(wrong_total_html)

    result = await verify_outcome(
        browser_session.page,
        checkout_intent,
        browser_session.monitor,
    )

    assert result.passed is False
    cmap = get_check_map(result.checks)
    assert cmap["total_matches"].passed is False
    assert cmap["confirmation_visible"].passed is True
    assert cmap["order_id_present"].passed is True
    assert cmap["no_server_errors"].passed is True
    assert cmap["no_error_alert"].passed is True


async def test_alert_element_fails_no_error_alert(
    browser_session, checkout_intent
):
    """Verify that a visible role=alert element causes no_error_alert to fail."""
    alert_html = """
    <!DOCTYPE html>
    <html>
      <body>
        <h1>Order confirmed</h1>
        <p>Order number: QA-1042</p>
        <p>Total: $36.50</p>
        <div role="alert" class="alert-error">Payment service unavailable.</div>
      </body>
    </html>
    """
    await browser_session.page.set_content(alert_html)

    result = await verify_outcome(
        browser_session.page,
        checkout_intent,
        browser_session.monitor,
    )

    assert result.passed is False
    cmap = get_check_map(result.checks)
    assert cmap["no_error_alert"].passed is False
    assert cmap["confirmation_visible"].passed is True
    assert cmap["order_id_present"].passed is True
    assert cmap["total_matches"].passed is True


async def test_injected_500_evidence_fails_no_server_errors(
    browser_session, checkout_intent
):
    """Verify that an HTTP 500 error recorded by the monitor causes no_server_errors to fail."""
    good_html = """
    <!DOCTYPE html>
    <html>
      <body>
        <h1>Order confirmed</h1>
        <p>Order number: QA-1042</p>
        <p>Total: $36.50</p>
      </body>
    </html>
    """
    await browser_session.page.set_content(good_html)

    # Inject 500 error into monitor evidence
    browser_session.monitor.http_errors.append(
        {"method": "POST", "url_path": "/v/c/place", "status": 500}
    )

    result = await verify_outcome(
        browser_session.page,
        checkout_intent,
        browser_session.monitor,
    )

    assert result.passed is False
    cmap = get_check_map(result.checks)
    assert cmap["no_server_errors"].passed is False
    assert cmap["confirmation_visible"].passed is True
    assert cmap["order_id_present"].passed is True
    assert cmap["total_matches"].passed is True
    assert cmap["no_error_alert"].passed is True


# -------------------------------------------------------------
# Live Application Integration Tests
# -------------------------------------------------------------

async def test_integration_version_a_run_and_verify_passes(
    make_settings, checkout_intent, recipe_v1
):
    """Verify live Version A run completes recipe v1 and passes all verifier checks."""
    settings, start_url = make_settings("/v/a/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        run_res = await run_recipe(recipe_v1, checkout_intent, session)
        assert run_res.failed_step_index is None

        ver_res = await verify_outcome(session.page, checkout_intent, session.monitor)
        assert ver_res.passed is True
        assert all(c.passed for c in ver_res.checks)


async def test_integration_version_c_fails_alert_500_and_no_phrase(
    make_settings, checkout_intent
):
    """Verify Version C error page fails no_error_alert, no_server_errors, and confirmation_visible."""
    settings, start_url = make_settings("/v/c/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        # POST to place order in Version C returns HTTP 500
        resp = await session.page.request.post(f"{settings.DEMO_BASE_URL}/v/c/place")
        assert resp.status == 500
        content = await resp.text()

        # Render the returned error page in the session
        await session.page.set_content(content)
        session.monitor.http_errors.append(
            {"method": "POST", "url_path": "/v/c/place", "status": 500}
        )

        ver_res = await verify_outcome(session.page, checkout_intent, session.monitor)
        assert ver_res.passed is False

        cmap = get_check_map(ver_res.checks)
        assert cmap["no_server_errors"].passed is False
        assert cmap["no_error_alert"].passed is False
        assert cmap["confirmation_visible"].passed is False


async def test_integration_version_d_fails_only_total_check(
    make_settings, checkout_intent
):
    """Verify Version D confirmation page fails only total_matches check."""
    settings, start_url = make_settings("/v/d/confirmation")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        await session.goto_start()

        ver_res = await verify_outcome(session.page, checkout_intent, session.monitor)
        assert ver_res.passed is False

        cmap = get_check_map(ver_res.checks)
        assert cmap["total_matches"].passed is False
        assert cmap["confirmation_visible"].passed is True
        assert cmap["order_id_present"].passed is True
        assert cmap["no_server_errors"].passed is True
        assert cmap["no_error_alert"].passed is True
