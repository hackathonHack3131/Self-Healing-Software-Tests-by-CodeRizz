"""Agent tools for Deep Agent self-healing test repair.

Provides deterministic, privacy-preserving tools for the Deep Agent:
- observe(): captures UI inventory + diff, returns accessible element refs.
- propose_fill(ref, field_key): validates via validator, executes fill, records step.
- propose_click(ref): validates via validator, executes click, records step.
- get_failure_context(): returns the compact FailureContext.
- get_test_data_keys(): returns allowed field_keys without literal values.

Rule 5: The agent has NO tool that declares success.
Rule 2: Never pass literal values to propose_fill; use field_key only.
Rule 7: Enforces MAX_AGENT_ACTIONS limit (default 10).
"""

from dataclasses import dataclass, field
from typing import Any
from langchain_core.tools import BaseTool, tool
from engine.actions import execute_step
from engine.browser import BrowserSession
from engine.models import (
    ActionType,
    FailureContext,
    Intent,
    PageSnapshot,
    Step,
    UIElement,
    UIInventory,
)
from engine.snapshot import capture_page_snapshot
from engine.validator import StepProposal, validate_step_proposal
from engine.verifier import verify_outcome



@dataclass
class HealingRunState:
    """State tracking for a single healing session."""

    session: BrowserSession
    intent: Intent
    failure_context: FailureContext
    baseline: UIInventory | None = None
    passed_prefix: list[Step] = field(default_factory=list)
    max_actions: int = 10
    action_count: int = 0
    executed_steps: list[Step] = field(default_factory=list)
    current_page_snapshot: PageSnapshot | None = None
    current_ref_map: dict[str, UIElement] = field(default_factory=dict)
    trace_events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def new_steps(self) -> list[Step]:
        """Alias for executed_steps representing newly added healing steps."""
        return self.executed_steps



def format_inventory_refs(
    snapshot: PageSnapshot, ref_map: dict[str, UIElement]
) -> str:
    """Format accessible references for the LLM to inspect cleanly."""
    lines = [
        f"Page Path: {snapshot.page_path}",
        f"Page Title: {snapshot.title}",
    ]
    if snapshot.headings:
        lines.append(f"Headings: {', '.join(snapshot.headings)}")

    lines.append("\nAvailable Interactive Controls:")
    for ref, el in ref_map.items():
        role = el.role
        name = el.name
        label = el.label
        elem_type = el.element_type or ""
        vis = "visible" if el.visible else "hidden"
        en = "enabled" if el.enabled else "disabled"

        details = [f"role={role}"]
        if name:
            details.append(f'name="{name}"')
        if label and label != name:
            details.append(f'label="{label}"')
        if elem_type:
            details.append(f"type={elem_type}")
        details.append(vis)
        details.append(en)

        lines.append(f"  - {ref}: " + " | ".join(details))

    return "\n".join(lines)


def create_healing_tools(
    session: BrowserSession,
    intent: Intent,
    failure_context: FailureContext,
    baseline: UIInventory | None = None,
    max_actions: int = 10,
    state: HealingRunState | None = None,
) -> tuple[list[BaseTool], HealingRunState]:
    """Factory that creates the 5 agent tools bound to the live session state."""
    run_state = state or HealingRunState(
        session=session,
        intent=intent,
        failure_context=failure_context,
        baseline=baseline,
        passed_prefix=list(failure_context.passed_steps) if failure_context and failure_context.passed_steps else [],
        max_actions=max_actions,
    )


    @tool
    async def observe() -> str:
        """Capture the current page's interactive elements and accessible refs.

        Call this tool first or after clicking navigation buttons to see the current page controls.
        """
        snapshot = await capture_page_snapshot(run_state.session.page)
        run_state.current_page_snapshot = snapshot
        run_state.current_ref_map.clear()

        # Index visible interactive elements first, then any other elements
        idx = 1
        for el in snapshot.elements:
            ref_id = f"ref_{idx}"
            run_state.current_ref_map[ref_id] = el
            idx += 1

        output = format_inventory_refs(snapshot, run_state.current_ref_map)

        if run_state.failure_context and run_state.failure_context.diff_summary:
            output += f"\n\nBaseline UI Diff Summary:\n{run_state.failure_context.diff_summary}"

        run_state.trace_events.append(
            {
                "tool": "observe",
                "page_path": snapshot.page_path,
                "elements_count": len(run_state.current_ref_map),
            }
        )
        return output

    @tool
    async def get_test_data_keys() -> str:
        """Get the list of allowed field_keys for form inputs.

        Never contains real user secrets or values. Only use keys from this list in propose_fill.
        """
        keys = list(run_state.intent.test_data.keys())
        msg = f"Allowed field_keys: {keys}\nDo NOT pass literal values. Always reference one of these field_keys."
        run_state.trace_events.append({"tool": "get_test_data_keys", "keys": keys})
        return msg

    @tool
    async def get_failure_context() -> str:
        """Get the triage summary and root cause diagnosis for why the prior test run failed."""
        fc = run_state.failure_context
        lines = [
            f"Goal: {fc.goal}",
            f"Failed Step Index: {fc.failed_step_index}",
            f"Failure Type: {fc.failure_type.value if fc.failure_type else 'None'}",
            f"Triage Verdict: {fc.triage.verdict.value} (Confidence: {fc.triage.confidence:.2f})",
            f"Recommended Action: {fc.triage.recommended.value}",
            f"Triage Evidence: {', '.join(fc.triage.evidence)}",
            f"Diff Summary: {fc.diff_summary}",
            f"Available Test Data Keys: {fc.field_keys}",
        ]
        if fc.failed_step:
            lines.append(f"Failed Step: action={fc.failed_step.action}, target={fc.failed_step.target}")

        msg = "\n".join(lines)
        run_state.trace_events.append({"tool": "get_failure_context"})
        return msg

    @tool
    async def propose_fill(ref: str, field_key: str) -> str:
        """Propose filling an input field identified by its ref (e.g. 'ref_1') using an allowed field_key.

        The action is validated and, if approved, executed on the live page.
        """
        if run_state.action_count >= run_state.max_actions:
            return f"Action limit reached: Maximum {run_state.max_actions} actions allowed."

        # Ensure we have fresh inventory
        if not run_state.current_ref_map:
            await observe.ainvoke({})

        proposal = StepProposal(
            action=ActionType.FILL_FIELD,
            ref=ref,
            field_key=field_key,
        )

        decision = validate_step_proposal(
            proposal=proposal,
            intent=run_state.intent,
            run_state=run_state,
            inventory=run_state.current_ref_map,
        )

        run_state.action_count += 1

        if not decision.approved:
            reason_str = "; ".join(decision.reasons)
            run_state.trace_events.append(
                {
                    "tool": "propose_fill",
                    "ref": ref,
                    "field_key": field_key,
                    "approved": False,
                    "reasons": decision.reasons,
                }
            )
            return f"Proposal rejected by validator: {reason_str}"

        assert decision.step is not None
        step_result = await execute_step(
            session=run_state.session,
            step=decision.step,
            intent=run_state.intent,
            step_index=len(run_state.executed_steps),
        )

        if step_result.success:
            run_state.executed_steps.append(decision.step)
            run_state.trace_events.append(
                {
                    "tool": "propose_fill",
                    "ref": ref,
                    "field_key": field_key,
                    "approved": True,
                    "executed": True,
                    "step": decision.step.model_dump(),
                }
            )
            return f"Success: Filled field '{field_key}' on target '{decision.target.name}'."
        else:
            run_state.trace_events.append(
                {
                    "tool": "propose_fill",
                    "ref": ref,
                    "field_key": field_key,
                    "approved": True,
                    "executed": False,
                    "error": step_result.error_message,
                }
            )
            return f"Execution failed on page: {step_result.error_message} (FailureType: {step_result.failure_type})"

    @tool
    async def propose_click(ref: str) -> str:
        """Propose clicking a button or link identified by its ref (e.g. 'ref_2').

        The action is validated and, if approved, clicked on the live page.
        """
        if run_state.action_count >= run_state.max_actions:
            return f"Action limit reached: Maximum {run_state.max_actions} actions allowed."

        # Ensure we have fresh inventory
        if not run_state.current_ref_map:
            await observe.ainvoke({})

        proposal = StepProposal(
            action=ActionType.CLICK_BUTTON,
            ref=ref,
        )

        decision = validate_step_proposal(
            proposal=proposal,
            intent=run_state.intent,
            run_state=run_state,
            inventory=run_state.current_ref_map,
        )

        run_state.action_count += 1

        if not decision.approved:
            reason_str = "; ".join(decision.reasons)
            run_state.trace_events.append(
                {
                    "tool": "propose_click",
                    "ref": ref,
                    "approved": False,
                    "reasons": decision.reasons,
                }
            )
            return f"Proposal rejected by validator: {reason_str}"

        assert decision.step is not None
        step_result = await execute_step(
            session=run_state.session,
            step=decision.step,
            intent=run_state.intent,
            step_index=len(run_state.executed_steps),
        )

        if step_result.success:
            run_state.executed_steps.append(decision.step)
            new_url = run_state.session.page.url

            # Automatically refresh inventory after navigation click
            try:
                new_snap = await capture_page_snapshot(run_state.session.page)
                run_state.current_page_snapshot = new_snap
                run_state.current_ref_map.clear()
                idx = 1
                for el in new_snap.elements:
                    run_state.current_ref_map[f"ref_{idx}"] = el
                    idx += 1
            except Exception:
                pass

            run_state.trace_events.append(
                {
                    "tool": "propose_click",
                    "ref": ref,
                    "approved": True,
                    "executed": True,
                    "new_url": new_url,
                    "step": decision.step.model_dump(),
                }
            )
            return f"Success: Clicked button '{decision.target.name}'. Current page URL is: {new_url}. Call observe() to see new controls."
        else:
            run_state.trace_events.append(
                {
                    "tool": "propose_click",
                    "ref": ref,
                    "approved": True,
                    "executed": False,
                    "error": step_result.error_message,
                }
            )
            return f"Execution failed on page: {step_result.error_message} (FailureType: {step_result.failure_type})"

    @tool
    async def check_outcome() -> str:
        """Deterministically check if expected business invariants (confirmation, total, order ID) pass on current page.

        Use during exploration to determine whether the target confirmation state has been reached.
        The official pass/fail status is determined by deterministic verification on clean replay.
        """
        ver = await verify_outcome(
            run_state.session.page,
            run_state.intent,
            run_state.session.monitor,
        )
        passed_names = [c.name for c in ver.checks if c.passed]
        failed_names = [c.name for c in ver.checks if not c.passed]
        run_state.trace_events.append(
            {
                "tool": "check_outcome",
                "passed": ver.passed,
                "passed_checks": passed_names,
                "failed_checks": failed_names,
            }
        )
        lines = [f"Deterministic Outcome Check: {'PASSED' if ver.passed else 'NOT YET ACHIEVED'}"]
        for c in ver.checks:
            mark = "PASSED" if c.passed else "FAILED"
            lines.append(f"  - {c.name}: {mark} ({c.detail})")
        return "\n".join(lines)

    @tool
    async def reset_to_failure_point() -> str:
        """Reset the browser to start, replay passing prefix steps, and clear newly proposed steps.

        Use this tool when an action sequence went down a dead end or caused an unwanted page state.
        """
        if run_state.action_count >= run_state.max_actions:
            return f"Action limit reached: Maximum {run_state.max_actions} actions allowed."

        run_state.executed_steps.clear()
        run_state.action_count += 1
        await run_state.session.goto_start()

        replayed_count = 0
        for step in run_state.passed_prefix:
            if step.action == ActionType.GOTO_START:
                continue
            step_res = await execute_step(
                session=run_state.session,
                step=step,
                intent=run_state.intent,
                step_index=replayed_count,
            )
            if not step_res.success:
                break
            replayed_count += 1

        # Re-observe current page
        snap = await capture_page_snapshot(run_state.session.page)
        run_state.current_page_snapshot = snap
        run_state.current_ref_map.clear()
        idx = 1
        for el in snap.elements:
            run_state.current_ref_map[f"ref_{idx}"] = el
            idx += 1

        run_state.trace_events.append(
            {
                "tool": "reset_to_failure_point",
                "replayed_count": replayed_count,
                "current_url": run_state.session.page.url,
            }
        )
        return (
            f"Reset complete. Cleared all new steps and replayed {replayed_count} prefix steps. "
            f"Current page URL: {run_state.session.page.url}. Call observe() to inspect controls."
        )

    tools_list: list[BaseTool] = [
        observe,
        get_test_data_keys,
        get_failure_context,
        propose_fill,
        propose_click,
        check_outcome,
        reset_to_failure_point,
    ]

    return tools_list, run_state

