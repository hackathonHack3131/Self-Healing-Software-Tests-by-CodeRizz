"""Tests for agent tools, FakeAgent, recorded replay, and Deep Agent healer (Module 8)."""

import asyncio
from pathlib import Path
import pytest
from engine.agent.fake import FakeAgent
from engine.agent.healer import heal_recipe
from engine.agent.recorded import load_trace, replay_trace, save_trace
from engine.agent.tools import create_healing_tools
from engine.browser import BrowserSession
from engine.classifier import classify
from engine.config import Settings
from engine.context import build_failure_context
from engine.diff import diff_snapshots
from engine.executor import run_recipe
from engine.models import (
    ActionType,
    ExpectedOutcome,
    FailureContext,
    Intent,
    Recipe,
    RunResult,
    SnapshotDiff,
    Status,
    Step,
    StepTarget,
    TargetBy,
    Triage,
    UIInventory,
    Verdict,
)
from engine.snapshot import capture_page_snapshot, load_baseline_inventory


from engine.recipes import load_intent


@pytest.fixture
def checkout_intent() -> Intent:
    return load_intent("checkout")



@pytest.fixture
def sample_v1_recipe(checkout_intent: Intent) -> Recipe:
    return Recipe(
        intent_id=checkout_intent.id,
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
        intent_hash=checkout_intent.content_hash,
    )


@pytest.mark.asyncio
async def test_tools_factory_and_invariants(checkout_intent, sample_v1_recipe, session_b):
    await session_b.goto_start()
    fc = FailureContext(
        goal=checkout_intent.goal,
        field_keys=list(checkout_intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

    tools, state = create_healing_tools(
        session=session_b,
        intent=checkout_intent,
        failure_context=fc,
        max_actions=10,
    )

    assert len(tools) == 7
    tool_names = {t.name for t in tools}
    assert tool_names == {
        "observe",
        "get_test_data_keys",
        "get_failure_context",
        "propose_fill",
        "propose_click",
        "check_outcome",
        "reset_to_failure_point",
    }


    # 1. Test get_test_data_keys (Rule 2: contains keys, never literal values)
    keys_tool = next(t for t in tools if t.name == "get_test_data_keys")
    keys_out = await keys_tool.ainvoke({})
    assert "full_name" in keys_out
    assert "4111111111111111" not in keys_out

    # 2. Test get_failure_context
    fc_tool = next(t for t in tools if t.name == "get_failure_context")
    fc_out = await fc_tool.ainvoke({})
    assert "UI_DRIFT" in fc_out
    assert checkout_intent.goal in fc_out

    # 3. Test observe on Cart page
    obs_tool = next(t for t in tools if t.name == "observe")
    obs_out = await obs_tool.ainvoke({})
    assert "Page Path: /v/b/" in obs_out
    assert "Proceed to shipping" in obs_out
    assert state.current_page_snapshot is not None
    assert len(state.current_ref_map) > 0


@pytest.mark.asyncio
async def test_propose_fill_and_click_validation_on_live_page(checkout_intent, session_b):
    await session_b.goto_start()
    fc = FailureContext(
        goal=checkout_intent.goal,
        field_keys=list(checkout_intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

    tools, state = create_healing_tools(session=session_b, intent=checkout_intent, failure_context=fc)
    tools_by_name = {t.name: t for t in tools}

    # Observe to populate ref_map
    await tools_by_name["observe"].ainvoke({})

    # Attempt to fill on a button ref should be rejected by validator
    # Find ref for "Proceed to shipping"
    btn_ref = next(r for r, el in state.current_ref_map.items() if el.name == "Proceed to shipping")
    res_rejected = await tools_by_name["propose_fill"].ainvoke({"ref": btn_ref, "field_key": "full_name"})
    assert "rejected" in res_rejected.lower()

    # Click the button successfully
    res_click = await tools_by_name["propose_click"].ainvoke({"ref": btn_ref})
    assert "success" in res_click.lower()
    assert len(state.executed_steps) == 1
    assert "/v/b/shipping" in session_b.page.url


@pytest.mark.asyncio
async def test_heal_recipe_with_fake_agent(checkout_intent, sample_v1_recipe, session_b):
    """Test full self-healing workflow on Version B using FakeAgent."""
    await session_b.goto_start()

    # Pre-scripted actions to solve Version B
    async def scripted_solve(tools_map, inputs):
        # 1. Cart: observe & click 'Proceed to shipping'
        await tools_map["observe"].ainvoke({})
        await tools_map["propose_click"].ainvoke({"ref": "ref_6"})  # Proceed to shipping

        # 2. Shipping: observe & fill inputs & click 'Continue to payment'
        await tools_map["observe"].ainvoke({})
        await tools_map["propose_fill"].ainvoke({"ref": "ref_6", "field_key": "full_name"})
        await tools_map["propose_fill"].ainvoke({"ref": "ref_7", "field_key": "email"})
        await tools_map["propose_fill"].ainvoke({"ref": "ref_8", "field_key": "street_address"})
        await tools_map["propose_click"].ainvoke({"ref": "ref_9"})  # Continue to payment

        # 3. Payment: observe & fill card details & click 'Review order'
        await tools_map["observe"].ainvoke({})
        await tools_map["propose_fill"].ainvoke({"ref": "ref_6", "field_key": "card_number"})
        await tools_map["propose_fill"].ainvoke({"ref": "ref_7", "field_key": "expiry"})
        await tools_map["propose_fill"].ainvoke({"ref": "ref_8", "field_key": "cvc"})
        await tools_map["propose_click"].ainvoke({"ref": "ref_9"})  # Review order

        # 4. Review: observe & click 'Place order securely'
        await tools_map["observe"].ainvoke({})
        await tools_map["propose_click"].ainvoke({"ref": "ref_6"})  # Place order securely

        return {"messages": [{"role": "assistant", "content": "Healing complete"}]}

    fake_agent = FakeAgent(custom_coro=scripted_solve)

    # Fake triage and run result for Version B failure
    run_res = RunResult(
        status=Status.FAIL_FUNCTIONAL,
        failed_step_index=1,
    )
    triage = Triage(
        verdict=Verdict.UI_DRIFT,
        confidence=0.9,
        recommended="HEAL",
        evidence=["Single-page form converted to multi-step wizard"],
    )

    heal_res = await heal_recipe(
        session=session_b,
        intent=checkout_intent,
        failed_recipe=sample_v1_recipe,
        run_result=run_res,
        triage=triage,
        agent_override=fake_agent,
    )

    assert heal_res.status == Status.PASS_AFTER_HEAL
    assert heal_res.recipe is not None
    assert heal_res.recipe.version == 2
    assert len(heal_res.executed_steps) == 10
    assert heal_res.clean_replay_result is not None
    assert heal_res.clean_replay_result.verification.passed is True


@pytest.mark.asyncio
async def test_blocked_config_when_api_key_missing(checkout_intent, sample_v1_recipe, session_b):
    """Rule 12: Missing config gives BLOCKED_CONFIG."""
    settings_no_key = Settings(GOOGLE_API_KEY="")
    run_res = RunResult(status=Status.FAIL_FUNCTIONAL, failed_step_index=1)
    triage = Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL")

    heal_res = await heal_recipe(
        session=session_b,
        intent=checkout_intent,
        failed_recipe=sample_v1_recipe,
        run_result=run_res,
        triage=triage,
        settings=settings_no_key,
    )

    assert heal_res.status == Status.BLOCKED_CONFIG
    assert "Missing GOOGLE_API_KEY" in heal_res.explanation


@pytest.mark.asyncio
async def test_recorded_trace_save_and_replay(checkout_intent, session_b, tmp_path):
    """Test saving and replaying a recorded trace (Rule 12)."""
    await session_b.goto_start()

    fc = FailureContext(
        goal=checkout_intent.goal,
        field_keys=list(checkout_intent.test_data.keys()),
        triage=Triage(verdict=Verdict.UI_DRIFT, confidence=0.9, recommended="HEAL"),
    )

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
    ]

    trace_file = tmp_path / "test_trace.json"
    save_trace(trace, trace_file)

    loaded = load_trace(trace_file)
    assert len(loaded) == len(trace)

    # Replay trace
    heal_res = await replay_trace(
        session=session_b,
        intent=checkout_intent,
        failure_context=fc,
        trace=loaded,
        parent_version=1,
    )

    assert heal_res.status == Status.PASS_AFTER_HEAL
    assert heal_res.is_recorded is True
    assert "RECORDED" in heal_res.explanation
    assert heal_res.clean_replay_result.verification.passed is True
