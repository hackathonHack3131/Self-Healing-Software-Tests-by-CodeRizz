"""Comprehensive tests for controlled agent tools, safety invariants, and Deep Agent healer (Module 8)."""

import asyncio
import os
from pathlib import Path
import pytest
from deepagents import create_deep_agent
from engine.agent.fake import FakeAgent
from engine.agent.healer import (
    UNSAFE_BUILTIN_TOOLS,
    HealOutcome,
    configure_safe_harness_profile,
    heal_recipe,
    run_heal,
)
from engine.agent.recorded import RecordedAgent, load_trace, replay_trace, save_trace
from engine.agent.tools import HealingRunState, create_healing_tools
from engine.config import Settings
from engine.models import (
    ActionType,
    FailureContext,
    Intent,
    Recipe,
    RunResult,
    Status,
    Step,
    StepTarget,
    TargetBy,
    Triage,
    Verdict,
)
from engine.recipes import load_intent


@pytest.fixture
def intent() -> Intent:
    return load_intent("checkout")


@pytest.fixture
def v1_recipe(intent: Intent) -> Recipe:
    return Recipe(
        intent_id=intent.id,
        version=1,
        steps=[
            Step(action=ActionType.GOTO_START),
            Step(
                action=ActionType.FILL_FIELD,
                target=StepTarget(by=TargetBy.LABEL, name="Name"),
                field_key="full_name",
            ),
            Step(
                action=ActionType.CLICK_BUTTON,
                target=StepTarget(by=TargetBy.ROLE, role="button", name="Checkout"),
            ),
        ],
        intent_hash=intent.content_hash,
    )


@pytest.mark.asyncio
async def test_tool_inventory_and_refs(intent, session_b):
    """Test observe captures current UI inventory, accessible refs, and diff summary."""
    await session_b.goto_start()
    fc = FailureContext(
        goal=intent.goal,
        field_keys=list(intent.test_data.keys()),
        diff_summary="Renamed controls: 'Name' -> 'Full name'",
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

    tools, state = create_healing_tools(session=session_b, intent=intent, failure_context=fc)
    tools_by_name = {t.name: t for t in tools}

    obs = await tools_by_name["observe"].ainvoke({})
    assert "Page Path: /v/b/" in obs
    assert "Proceed to shipping" in obs
    assert "Baseline UI Diff Summary:" in obs
    assert len(state.current_ref_map) > 0


@pytest.mark.asyncio
async def test_privacy_of_tool_results(intent, session_b):
    """Rule 2 & 10: Tools and trace must never leak card numbers, secrets, or raw test-data values."""
    await session_b.goto_start()
    fc = FailureContext(
        goal=intent.goal,
        field_keys=list(intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

    tools, state = create_healing_tools(session=session_b, intent=intent, failure_context=fc)
    tools_by_name = {t.name: t for t in tools}

    # 1. get_test_data_keys must expose field names only
    keys_out = await tools_by_name["get_test_data_keys"].ainvoke({})
    assert "full_name" in keys_out
    assert "card_number" in keys_out
    # Card number must NOT appear in output
    assert intent.test_data["card_number"] not in keys_out
    assert intent.test_data["full_name"] not in keys_out

    # 2. get_failure_context must not leak secrets
    fc_out = await tools_by_name["get_failure_context"].ainvoke({})
    assert intent.test_data["card_number"] not in fc_out

    # 3. Trace events must never contain raw card values
    await tools_by_name["observe"].ainvoke({})
    btn_ref = next(r for r, el in state.current_ref_map.items() if el.name == "Proceed to shipping")
    await tools_by_name["propose_click"].ainvoke({"ref": btn_ref})
    # Next page
    await tools_by_name["observe"].ainvoke({})
    name_ref = next(r for r, el in state.current_ref_map.items() if el.name == "Full name")
    await tools_by_name["propose_fill"].ainvoke({"ref": name_ref, "field_key": "full_name"})

    for event in state.trace_events:
        event_str = str(event)
        assert intent.test_data["card_number"] not in event_str


@pytest.mark.asyncio
async def test_check_outcome_deterministic(intent, session_b):
    """Deterministic check_outcome reports business invariants without declaring test success."""
    await session_b.goto_start()
    fc = FailureContext(
        goal=intent.goal,
        field_keys=list(intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

    tools, state = create_healing_tools(session=session_b, intent=intent, failure_context=fc)
    tools_by_name = {t.name: t for t in tools}

    # On Cart page, confirmation is NOT yet reached
    outcome_cart = await tools_by_name["check_outcome"].ainvoke({})
    assert "NOT YET ACHIEVED" in outcome_cart
    assert "FAILED" in outcome_cart


@pytest.mark.asyncio
async def test_reset_to_failure_point(intent, session_b):
    """reset_to_failure_point replays the passing prefix and clears new_steps."""
    await session_b.goto_start()

    # Suppose step 0 (goto_start) and a click to cart passed
    passing_steps = [Step(action=ActionType.GOTO_START)]

    fc = FailureContext(
        goal=intent.goal,
        field_keys=list(intent.test_data.keys()),
        passed_steps=passing_steps,
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

    tools, state = create_healing_tools(session=session_b, intent=intent, failure_context=fc)
    tools_by_name = {t.name: t for t in tools}

    # Propose a step
    await tools_by_name["observe"].ainvoke({})
    btn_ref = next(r for r, el in state.current_ref_map.items() if el.name == "Proceed to shipping")
    await tools_by_name["propose_click"].ainvoke({"ref": btn_ref})
    assert len(state.new_steps) == 1
    assert "/v/b/shipping" in session_b.page.url

    # Now reset back to failure point
    reset_out = await tools_by_name["reset_to_failure_point"].ainvoke({})
    assert "Reset complete" in reset_out
    assert len(state.new_steps) == 0
    assert "/v/b/" in session_b.page.url


@pytest.mark.asyncio
async def test_action_limit_enforcement(intent, session_b):
    """Rule 7: Enforce MAX_AGENT_ACTIONS limit."""
    await session_b.goto_start()
    fc = FailureContext(
        goal=intent.goal,
        field_keys=list(intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

    # Set max_actions to 2
    tools, state = create_healing_tools(session=session_b, intent=intent, failure_context=fc, max_actions=2)
    tools_by_name = {t.name: t for t in tools}

    await tools_by_name["observe"].ainvoke({})
    btn_ref = next(r for r, el in state.current_ref_map.items() if el.name == "Proceed to shipping")

    # Action 1
    res1 = await tools_by_name["propose_click"].ainvoke({"ref": btn_ref})
    assert "success" in res1.lower()

    # Action 2: reset
    res2 = await tools_by_name["reset_to_failure_point"].ainvoke({})
    assert "Reset complete" in res2

    # Action 3: should be rejected due to action limit
    await tools_by_name["observe"].ainvoke({})
    btn_ref = next(r for r, el in state.current_ref_map.items() if el.name == "Proceed to shipping")
    res3 = await tools_by_name["propose_click"].ainvoke({"ref": btn_ref})
    assert "limit reached" in res3.lower()


@pytest.mark.asyncio
async def test_version_b_correct_sequence(intent, v1_recipe, session_b):
    """Test healing Version B with complete, valid multi-step sequence."""
    await session_b.goto_start()

    trace = [
        {"tool": "observe"},
        {"tool": "propose_click", "ref": "ref_6"},
        {"tool": "observe"},
        {"tool": "propose_fill", "ref": "ref_6", "field_key": "full_name"},
        {"tool": "propose_fill", "ref": "ref_7", "field_key": "email"},
        {"tool": "propose_fill", "ref": "ref_8", "field_key": "street_address"},
        {"tool": "propose_click", "ref": "ref_9"},
        {"tool": "observe"},
        {"tool": "propose_fill", "ref": "ref_6", "field_key": "card_number"},
        {"tool": "propose_fill", "ref": "ref_7", "field_key": "expiry"},
        {"tool": "propose_fill", "ref": "ref_8", "field_key": "cvc"},
        {"tool": "propose_click", "ref": "ref_9"},
        {"tool": "observe"},
        {"tool": "propose_click", "ref": "ref_6"},
        {"tool": "check_outcome"},
    ]

    agent = RecordedAgent(trace=trace)
    run_res = RunResult(status=Status.FAIL_FUNCTIONAL, failed_step_index=1)
    triage = Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL")

    heal_res = await heal_recipe(
        session=session_b,
        intent=intent,
        failed_recipe=v1_recipe,
        run_result=run_res,
        triage=triage,
        agent_override=agent,
    )

    assert heal_res.status == Status.PASS_AFTER_HEAL
    assert heal_res.recipe is not None
    assert len(heal_res.executed_steps) == 10
    assert heal_res.clean_replay_result.verification.passed is True


@pytest.mark.asyncio
async def test_version_b_incorrect_sequence(intent, v1_recipe, session_b):
    """Test that an incorrect action sequence fails validation or execution."""
    await session_b.goto_start()

    # Attempt to click non-existent buttons or fill invalid fields
    bad_trace = [
        {"tool": "observe"},
        {"tool": "propose_fill", "ref": "ref_6", "field_key": "card_number"},  # Filling button on Cart page!
    ]

    agent = RecordedAgent(trace=bad_trace)
    run_res = RunResult(status=Status.FAIL_FUNCTIONAL, failed_step_index=1)
    triage = Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL")

    heal_res = await heal_recipe(
        session=session_b,
        intent=intent,
        failed_recipe=v1_recipe,
        run_result=run_res,
        triage=triage,
        agent_override=agent,
    )

    assert heal_res.status == Status.FAIL_HEALING
    assert len(heal_res.executed_steps) == 0


def test_unsafe_builtin_tools_excluded():
    """Requirement 4: Exclude shell execution and filesystem tools using HarnessProfile."""
    configure_safe_harness_profile("google_genai")
    assert "execute" in UNSAFE_BUILTIN_TOOLS
    assert "read_file" in UNSAFE_BUILTIN_TOOLS
    assert "write_file" in UNSAFE_BUILTIN_TOOLS
    assert "edit_file" in UNSAFE_BUILTIN_TOOLS
    assert "ls" in UNSAFE_BUILTIN_TOOLS


@pytest.mark.asyncio
async def test_run_heal_blocked_config(intent, session_b):
    """Rule 12: Missing config gives BLOCKED_CONFIG."""
    settings_no_key = Settings(GOOGLE_API_KEY="")
    fc = FailureContext(
        goal=intent.goal,
        field_keys=list(intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )
    tools, state = create_healing_tools(session=session_b, intent=intent, failure_context=fc)

    outcome = await run_heal(
        settings=settings_no_key,
        tools=tools,
        run_state=state,
        context=fc,
    )

    assert outcome.status == "BLOCKED_CONFIG"
    assert "Missing GOOGLE_API_KEY" in outcome.report


@pytest.mark.asyncio
async def test_run_heal_timeout_handling(intent, session_b):
    """Test timeout handling in run_heal."""
    async def slow_coro(tools, inputs):
        await asyncio.sleep(5)
        return {"messages": []}

    fake_agent = FakeAgent(custom_coro=slow_coro)
    settings_fast_timeout = Settings(MAX_HEAL_SECONDS=1)

    fc = FailureContext(
        goal=intent.goal,
        field_keys=list(intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )
    tools, state = create_healing_tools(session=session_b, intent=intent, failure_context=fc)

    outcome = await run_heal(
        settings=settings_fast_timeout,
        tools=tools,
        run_state=state,
        context=fc,
        agent_override=fake_agent,
    )

    assert outcome.status == "FAIL_HEALING"
    assert "timed out" in outcome.report


@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="Opt-in: GOOGLE_API_KEY not set")
@pytest.mark.asyncio
async def test_live_gemini_model_healing(intent, v1_recipe, session_b):
    """Opt-in live Gemini model healing test (only runs if GOOGLE_API_KEY is configured)."""
    settings = Settings.from_env()
    run_res = RunResult(status=Status.FAIL_FUNCTIONAL, failed_step_index=1)
    triage = Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL")

    heal_res = await heal_recipe(
        session=session_b,
        intent=intent,
        failed_recipe=v1_recipe,
        run_result=run_res,
        triage=triage,
        settings=settings,
    )

    assert heal_res.status in (
        Status.PASS_AFTER_HEAL,
        Status.FAIL_HEALING,
        Status.BLOCKED_AGENT,
    )
