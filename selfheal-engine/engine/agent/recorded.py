"""Trace recording and replay for deterministic healing and demos.

Follows AGENTS.md Rule 12:
- Never fakes AI.
- Replays must be explicitly labeled RECORDED in explanations and results.
- Every replayed action MUST still pass through the deterministic validator.
- Success is ONLY decided by the deterministic verifier on a clean replay.
"""

import json
import os
from pathlib import Path
from typing import Any
from engine.browser import BrowserSession
from engine.executor import run_recipe
from engine.models import (
    ActionType,
    CreatedBy,
    FailureContext,
    HealResult,
    Intent,
    Recipe,
    Status,
    Step,
    UIInventory,
)
from engine.recipes import get_project_root
from engine.verifier import verify_outcome
from engine.agent.tools import create_healing_tools


DEFAULT_TRACE_FILENAME = "b_heal_trace.json"


def get_default_trace_path() -> Path:
    """Return the default path to the Version B recorded trace."""
    return get_project_root() / "recorded" / DEFAULT_TRACE_FILENAME


def save_trace(trace: list[dict[str, Any]], path: Path | str | None = None) -> Path:
    """Save a recorded agent trace to disk atomically."""
    target_path = Path(path) if path else get_default_trace_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target_path.parent / f".tmp_{target_path.name}"

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(trace, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, target_path)
    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise

    return target_path


def load_trace(path: Path | str | None = None) -> list[dict[str, Any]]:
    """Load a recorded agent trace from disk."""
    target_path = Path(path) if path else get_default_trace_path()
    if not target_path.exists() or target_path.stat().st_size == 0:
        raise FileNotFoundError(f"Recorded trace not found or empty at {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


class RecordedAgent:
    """Agent that replays a recorded trace through the exact tool interface."""

    def __init__(
        self,
        trace: list[dict[str, Any]] | None = None,
        trace_path: Path | str | None = None,
    ):
        self.trace = trace if trace is not None else load_trace(trace_path)
        self.tools: dict[str, Any] = {}
        self.invoked = False
        self.inputs_received: list[dict[str, Any]] = []

    def set_tools(self, tools: list[Any]) -> None:
        """Register tools available for execution."""
        self.tools = {t.name: t for t in tools}

    async def ainvoke(self, inputs: dict[str, Any], config: Any = None) -> dict[str, Any]:
        """Execute recorded actions sequentially through the registered tools."""
        self.invoked = True
        self.inputs_received.append(inputs)
        results = []
        for action_record in self.trace:
            tool_name = action_record.get("tool")
            if not tool_name or tool_name not in self.tools:
                continue

            target_tool = self.tools[tool_name]
            if tool_name == "observe":
                res = await target_tool.ainvoke({})
            elif tool_name == "propose_fill":
                res = await target_tool.ainvoke({
                    "ref": action_record["ref"],
                    "field_key": action_record["field_key"],
                })
            elif tool_name == "propose_click":
                res = await target_tool.ainvoke({
                    "ref": action_record["ref"],
                })
            elif tool_name == "check_outcome":
                res = await target_tool.ainvoke({})
            elif tool_name == "reset_to_failure_point":
                res = await target_tool.ainvoke({})
            else:
                args = {k: v for k, v in action_record.items() if k != "tool"}
                res = await target_tool.ainvoke(args)

            results.append({"tool": tool_name, "output": str(res)})

        return {
            "messages": [
                {"role": "assistant", "content": "Recorded agent replayed trace."}
            ],
            "execution_log": results,
        }



async def replay_trace(
    session: BrowserSession,
    intent: Intent,
    failure_context: FailureContext,
    trace: list[dict[str, Any]] | None = None,
    trace_path: Path | str | None = None,
    baseline: UIInventory | None = None,
    parent_version: int = 1,
) -> HealResult:
    """Replay a recorded agent trace through the validator, then run clean verification.

    Per Rule 12: Every replayed action goes through the validator and live browser execution,
    and success is validated by deterministic verification on a fresh replay.
    """
    if trace is None:
        trace = load_trace(trace_path)

    tools_list, state = create_healing_tools(
        session=session,
        intent=intent,
        failure_context=failure_context,
        baseline=baseline,
        max_actions=len(trace) + 5,
    )
    tools_by_name = {t.name: t for t in tools_list}

    # Execute trace actions
    for action_record in trace:
        tool_name = action_record.get("tool")
        if not tool_name or tool_name not in tools_by_name:
            continue

        target_tool = tools_by_name[tool_name]

        if tool_name == "observe":
            await target_tool.ainvoke({})
        elif tool_name == "propose_fill":
            res = await target_tool.ainvoke({
                "ref": action_record["ref"],
                "field_key": action_record["field_key"],
            })
            if "rejected" in str(res).lower():
                return HealResult(
                    status=Status.FAIL_HEALING,
                    executed_steps=state.executed_steps,
                    explanation=f"RECORDED: Trace proposal rejected by validator: {res}",
                    trace=state.trace_events,
                    is_recorded=True,
                )
        elif tool_name == "propose_click":
            res = await target_tool.ainvoke({
                "ref": action_record["ref"],
            })
            if "rejected" in str(res).lower():
                return HealResult(
                    status=Status.FAIL_HEALING,
                    executed_steps=state.executed_steps,
                    explanation=f"RECORDED: Trace proposal rejected by validator: {res}",
                    trace=state.trace_events,
                    is_recorded=True,
                )

    if not state.executed_steps:
        return HealResult(
            status=Status.FAIL_HEALING,
            executed_steps=[],
            explanation="RECORDED: No steps were successfully executed from trace.",
            trace=state.trace_events,
            is_recorded=True,
        )

    # Reconstruct candidate Recipe
    recipe_steps = [Step(action=ActionType.GOTO_START)] + list(state.executed_steps)
    candidate_recipe = Recipe(
        intent_id=intent.id,
        version=parent_version + 1,
        created_by=CreatedBy.AGENT,
        parent_version=parent_version,
        intent_hash=intent.content_hash,
        steps=recipe_steps,
    )

    # Clean replay verification per Rule 5
    await session.goto_start()
    clean_run_res = await run_recipe(candidate_recipe, intent, session)

    if clean_run_res.failed_step_index is not None:
        return HealResult(
            status=Status.FAIL_HEALING,
            recipe=candidate_recipe,
            executed_steps=state.executed_steps,
            explanation=f"RECORDED: Clean replay failed at step {clean_run_res.failed_step_index}",
            trace=state.trace_events,
            clean_replay_result=clean_run_res,
            is_recorded=True,
        )

    ver_res = await verify_outcome(session.page, intent, session.monitor)
    clean_run_res.verification = ver_res

    if not ver_res.passed:
        failed_checks = [c.name for c in ver_res.checks if not c.passed]
        return HealResult(
            status=Status.FAIL_FUNCTIONAL,
            recipe=candidate_recipe,
            executed_steps=state.executed_steps,
            explanation=f"RECORDED: Clean replay failed verification checks: {failed_checks}",
            trace=state.trace_events,
            clean_replay_result=clean_run_res,
            is_recorded=True,
        )

    return HealResult(
        status=Status.PASS_AFTER_HEAL,
        recipe=candidate_recipe,
        executed_steps=state.executed_steps,
        explanation="RECORDED: Successfully healed and verified workflow via recorded trace.",
        trace=state.trace_events,
        clean_replay_result=clean_run_res,
        is_recorded=True,
    )
