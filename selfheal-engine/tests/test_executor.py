"""Tests for browser session, actions resolution, and recipe executor."""

import time
import pytest
from engine.actions import execute_step
from engine.browser import BrowserSession, DisallowedOriginError
from engine.config import Settings
from engine.executor import run_recipe
from engine.models import (
    ActionType,
    FailureType,
    Intent,
    Recipe,
    Status,
    Step,
    StepTarget,
    TargetBy,
)
from engine.recipes import load_intent, load_recipe


@pytest.fixture
def checkout_intent():
    return load_intent("checkout")


@pytest.fixture
def recipe_v1(checkout_intent):
    return load_recipe("checkout", version=1, intent=checkout_intent)


async def test_version_a_completes_every_step_with_no_failure(
    make_settings, checkout_intent, recipe_v1
):
    """Verify Version A with recipe v1 completes every step with zero errors in < 15s."""
    settings, start_url = make_settings("/v/a/")

    start_time = time.perf_counter()
    async with BrowserSession(settings=settings, start_url=start_url) as session:
        result = await run_recipe(recipe_v1, checkout_intent, session)
    elapsed = time.perf_counter() - start_time

    assert result.status == Status.PASS_NO_HEAL
    assert result.failed_step_index is None
    assert result.failure_type is None
    assert len(result.steps) == len(recipe_v1.steps)
    for step_res in result.steps:
        assert step_res.success is True

    # Performance requirement: under 15 seconds
    assert elapsed < 15.0, f"Version A took {elapsed:.2f}s (must be < 15s)"


async def test_version_b_fails_at_first_fill_step_with_element_not_found(
    make_settings, checkout_intent, recipe_v1
):
    """Verify Version B fails at step 1 (fill Name) with ELEMENT_NOT_FOUND and no HTTP errors."""
    settings, start_url = make_settings("/v/b/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        result = await run_recipe(recipe_v1, checkout_intent, session)

    # Step 0 (goto_start) passed, step 1 (fill Name) failed
    assert result.failed_step_index == 1
    assert result.failure_type == FailureType.ELEMENT_NOT_FOUND
    assert result.steps[0].success is True
    assert result.steps[1].success is False

    # Evidence contains step URLs and no HTTP errors
    assert len(result.evidence.get("step_urls", [])) >= 2
    assert len(result.evidence.get("http_errors", [])) == 0


async def test_synthetic_pages_ambiguous_and_not_visible(
    make_settings, checkout_intent
):
    """Verify target resolution catches ambiguity and hidden/disabled visibility states."""
    settings, start_url = make_settings("/v/a/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        # Case 1: Two matching buttons -> ELEMENT_AMBIGUOUS
        await session.page.set_content(
            '<button>Checkout</button><button>Checkout</button>'
        )
        step_ambiguous = Step(
            action=ActionType.CLICK_BUTTON,
            target=StepTarget(by=TargetBy.ROLE, name="Checkout", role="button"),
        )
        res_ambiguous = await execute_step(session, step_ambiguous, checkout_intent)
        assert res_ambiguous.success is False
        assert res_ambiguous.failure_type == FailureType.ELEMENT_AMBIGUOUS

        # Case 2: Hidden button -> ELEMENT_NOT_VISIBLE
        await session.page.set_content(
            '<button style="display:none;">Checkout</button>'
        )
        step_hidden = Step(
            action=ActionType.CLICK_BUTTON,
            target=StepTarget(by=TargetBy.ROLE, name="Checkout", role="button"),
        )
        res_hidden = await execute_step(session, step_hidden, checkout_intent)
        assert res_hidden.success is False
        assert res_hidden.failure_type == FailureType.ELEMENT_NOT_VISIBLE

        # Case 3: Disabled button -> ELEMENT_NOT_VISIBLE
        await session.page.set_content(
            '<button disabled>Checkout</button>'
        )
        step_disabled = Step(
            action=ActionType.CLICK_BUTTON,
            target=StepTarget(by=TargetBy.ROLE, name="Checkout", role="button"),
        )
        res_disabled = await execute_step(session, step_disabled, checkout_intent)
        assert res_disabled.success is False
        assert res_disabled.failure_type == FailureType.ELEMENT_NOT_VISIBLE


async def test_off_origin_request_blocked(make_settings):
    """Verify off-origin goto is rejected and off-origin requests are aborted."""
    settings, start_url = make_settings("/v/a/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        # 1. Direct goto to off-origin raises DisallowedOriginError
        with pytest.raises(DisallowedOriginError):
            await session.goto("http://malicious.org")

        # 2. In-page fetch to off-origin origin is aborted by route guard
        await session.page.goto(start_url)
        fetch_result = await session.page.evaluate(
            """async () => {
                try {
                    await fetch('http://example.com/test-ssrf');
                    return 'passed';
                } catch (e) {
                    return 'blocked';
                }
            }"""
        )
        assert fetch_result == "blocked"
        assert len(session.monitor.failed_requests) > 0


async def test_browser_closed_even_when_step_raises(make_settings):
    """Verify browser and context resources are cleanly torn down on unexpected exceptions."""
    settings, start_url = make_settings("/v/a/")
    session_ref: BrowserSession | None = None

    with pytest.raises(RuntimeError, match="Simulated step crash"):
        async with BrowserSession(settings=settings, start_url=start_url) as session:
            session_ref = session
            raise RuntimeError("Simulated step crash")

    assert session_ref is not None
    assert session_ref.page is None
    assert session_ref.browser is None
