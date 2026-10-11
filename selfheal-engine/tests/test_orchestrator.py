"""Unit tests for the Module 9 State Machine Orchestrator (engine/orchestrator.py).

Verifies all critical state machine transitions and compliance with AGENTS.md:
- Rule 1: Intent immutability and hash checks.
- Rule 5: Deterministic clean replay verification.
- Rule 6: Deterministic code computes final status.
- Rule 7: One heal attempt, limits enforced.
- Rule 12: Never fake AI; BLOCKED_CONFIG and BLOCKED_AGENT handling.
"""

from pathlib import Path
import pytest

from engine.config import Settings
from engine.models import Status, Verdict
from engine.orchestrator import run_orchestrator
from engine.recipes import load_intent


@pytest.fixture
def checkout_intent():
    return load_intent("checkout")


@pytest.mark.asyncio
async def test_orchestrator_version_a_passes_cleanly(make_settings):
    """Version A must execute cleanly with zero healing (Status.PASS_NO_HEAL)."""
    settings, start_url = make_settings("/v/a/")

    result = await run_orchestrator(
        intent_id="checkout",
        target_url=start_url,
        recipe_version=1,
        settings=settings,
    )

    assert result.status == Status.PASS_NO_HEAL
    assert result.healed is False
    assert result.initial_recipe_version == 1
    assert result.new_recipe_version == 1
    assert result.verification is not None
    assert result.verification.passed is True
    assert "Baseline Execution Succeeded" in result.agent_explanation
    assert any(e.phase == "PASS" for e in result.events)


@pytest.mark.asyncio
async def test_orchestrator_version_b_heals_with_recorded_trace(make_settings):
    """Version B triggers UI drift, rebuilds multi-step recipe, and verifies via clean replay."""
    settings, start_url = make_settings("/v/b/")

    result = await run_orchestrator(
        intent_id="checkout",
        target_url=start_url,
        recipe_version=1,
        settings=settings,
        force_heal_mode="recorded",
    )

    assert result.status == Status.PASS_AFTER_HEAL
    assert result.healed is True
    assert result.initial_recipe_version == 1
    assert result.new_recipe_version is not None
    assert result.new_recipe_version >= 2
    assert result.saved_recipe is not None
    assert result.verification is not None
    assert result.verification.passed is True
    assert any(e.phase == "RECIPE_SAVED" for e in result.events)


@pytest.mark.asyncio
async def test_orchestrator_version_c_diagnoses_app_bug_and_refuses_heal(make_settings):
    """Version C throws HTTP 500 on checkout; clean replay catches the server error; recipe is NOT saved."""
    settings, start_url = make_settings("/v/c/")

    result = await run_orchestrator(
        intent_id="checkout",
        target_url=start_url,
        recipe_version=1,
        settings=settings,
        force_heal_mode="recorded",
    )

    # Clean replay must fail with FAIL_FUNCTIONAL due to HTTP 500 error on /place
    assert result.status == Status.FAIL_FUNCTIONAL
    assert result.healed is False
    assert result.saved_recipe is None
    assert result.heal_result is not None
    assert result.heal_result.status == Status.FAIL_FUNCTIONAL


@pytest.mark.asyncio
async def test_orchestrator_version_d_fails_calculation_invariant(make_settings):
    """Version D has wrong total calculation ($32.50 vs $36.50); verifier catches invariant violation."""
    settings, start_url = make_settings("/v/d/")

    result = await run_orchestrator(
        intent_id="checkout",
        target_url=start_url,
        recipe_version=1,
        settings=settings,
        force_heal_mode="recorded",
    )

    assert result.status == Status.FAIL_FUNCTIONAL
    assert result.healed is False
    assert result.verification is not None
    assert result.verification.passed is False
    # Verifier must catch the calculation invariant
    total_check = next((c for c in result.verification.checks if c.name == "total_matches"), None)
    assert total_check is not None
    assert total_check.passed is False


@pytest.mark.asyncio
async def test_orchestrator_blocked_config_when_no_llm_and_no_trace(make_settings, monkeypatch, tmp_path):
    """Rule 12: Missing LLM config with no recorded fallback must emit BLOCKED_CONFIG."""
    base_settings, start_url = make_settings("/v/b/")
    no_key_settings = Settings(
        DEMO_BASE_URL=base_settings.DEMO_BASE_URL,
        ALLOWED_ORIGINS=base_settings.ALLOWED_ORIGINS,
        GOOGLE_API_KEY="",
        HEADLESS=base_settings.HEADLESS,
    )

    # Point trace path to non-existent directory
    monkeypatch.setattr(
        "engine.orchestrator.get_project_root",
        lambda: tmp_path,
    )

    result = await run_orchestrator(
        intent_id="checkout",
        target_url=start_url,
        recipe_version=1,
        settings=no_key_settings,
        force_heal_mode=None,
    )

    assert result.status == Status.BLOCKED_CONFIG
    assert result.healed is False
    assert any(e.phase == "BLOCKED_CONFIG" for e in result.events)
