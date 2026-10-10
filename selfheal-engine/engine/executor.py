"""Deterministic recipe runner executing steps sequentially and gathering evidence."""

from pathlib import Path
import uuid
from engine.actions import execute_step
from engine.browser import BrowserSession
from engine.models import (
    FailureType,
    Intent,
    Recipe,
    RunResult,
    Status,
    StepResult,
)


async def run_recipe(
    recipe: Recipe,
    intent: Intent,
    session: BrowserSession,
    run_id: str | None = None,
) -> RunResult:
    """Run steps of a recipe against a BrowserSession and compile execution evidence.

    Stops execution at the first failing step and records screenshots and diagnostics.
    """
    executed_steps: list[StepResult] = []
    step_urls: list[str] = []
    failed_step_index: int | None = None
    failure_type: FailureType | None = None

    effective_run_id = run_id or f"run_{uuid.uuid4().hex[:8]}"

    for idx, step in enumerate(recipe.steps):
        step_result = await execute_step(
            session=session,
            step=step,
            intent=intent,
            step_index=idx,
        )
        executed_steps.append(step_result)

        current_url = session.page.url if session.page else ""
        step_urls.append(current_url)

        if not step_result.success:
            failed_step_index = idx
            failure_type = step_result.failure_type
            break

    # Gather diagnostics from monitor
    evidence: dict[str, list] = {}
    if session.monitor:
        evidence = session.monitor.get_evidence()
        visible_alerts = await session.monitor.visible_alerts(session.page)
        evidence["alerts"] = visible_alerts
    evidence["step_urls"] = step_urls

    # Capture failure screenshot if a step failed
    if failed_step_index is not None and session.page:
        runs_dir = Path(session.settings.RUNS_DIR) / effective_run_id
        runs_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = runs_dir / f"failure_step_{failed_step_index}.png"
        try:
            await session.page.screenshot(path=str(screenshot_path))
            evidence["failure_screenshot"] = str(screenshot_path)
        except Exception:
            pass

    # Triage preliminary status (final verification is handled by the verifier in Module 5)
    if failed_step_index is None:
        status = Status.PASS_NO_HEAL
    else:
        http_errors = evidence.get("http_errors", [])
        has_5xx = any(err.get("status", 0) >= 500 for err in http_errors)
        alerts = evidence.get("alerts", [])

        if has_5xx or len(alerts) > 0:
            status = Status.FAIL_FUNCTIONAL
        elif failure_type == FailureType.TIMEOUT:
            status = Status.FAIL_EXECUTION
        else:
            status = Status.FAIL_HEALING

    return RunResult(
        status=status,
        steps=executed_steps,
        failed_step_index=failed_step_index,
        failure_type=failure_type,
        evidence=evidence,
    )
