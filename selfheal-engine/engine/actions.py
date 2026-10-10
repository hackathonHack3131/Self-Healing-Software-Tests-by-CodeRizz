"""Deterministic action execution and accessible target resolution."""

import asyncio
import time
from playwright.async_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from engine.browser import BrowserSession
from engine.models import (
    ActionType,
    FailureType,
    Intent,
    Step,
    StepResult,
    StepTarget,
    TargetBy,
)

STEP_TIMEOUT_MS = 3000


async def resolve_target(
    page: Page, target: StepTarget
) -> tuple[int, bool, bool, Locator | None]:
    """Resolve a target using exact accessible name matching.

    Returns (count, visible, enabled, locator).
    """
    if target.by == TargetBy.LABEL:
        locator = page.get_by_label(target.name, exact=True)
    elif target.by == TargetBy.ROLE:
        role = target.role or "button"
        locator = page.get_by_role(role, name=target.name, exact=True, include_hidden=True)
    elif target.by == TargetBy.PLACEHOLDER:
        locator = page.get_by_placeholder(target.name, exact=True)
    else:
        raise ValueError(f"Unsupported locator strategy: {target.by}")

    count = await locator.count()
    if count == 0:
        return 0, False, False, locator
    elif count == 1:
        visible = await locator.is_visible()
        enabled = await locator.is_enabled()
        return 1, visible, enabled, locator
    else:
        # Multiple matches
        visible = False
        enabled = False
        try:
            visible = await locator.first.is_visible()
            enabled = await locator.first.is_enabled()
        except Exception:
            pass
        return count, visible, enabled, locator


async def execute_step(
    session: BrowserSession,
    step: Step,
    intent: Intent,
    step_index: int = 0,
) -> StepResult:
    """Execute a single deterministic recipe step with typed failure classifications."""
    start_time = time.perf_counter()

    try:
        if step.action == ActionType.GOTO_START:
            await session.goto_start(
                wait_until="domcontentloaded",
                timeout=STEP_TIMEOUT_MS,
            )
            await asyncio.sleep(0.1)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=True,
                duration_ms=elapsed_ms,
            )

        if not step.target:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=False,
                duration_ms=elapsed_ms,
                failure_type=FailureType.CONFIG,
                error_message="Step target is missing",
            )

        count, visible, enabled, locator = await resolve_target(
            session.page, step.target
        )

        if count == 0:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=False,
                duration_ms=elapsed_ms,
                failure_type=FailureType.ELEMENT_NOT_FOUND,
                error_message=f"Target '{step.target.name}' not found (count = 0)",
            )

        if count > 1:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=False,
                duration_ms=elapsed_ms,
                failure_type=FailureType.ELEMENT_AMBIGUOUS,
                error_message=f"Target '{step.target.name}' matched {count} elements (ambiguous)",
            )

        if not visible:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=False,
                duration_ms=elapsed_ms,
                failure_type=FailureType.ELEMENT_NOT_VISIBLE,
                error_message=f"Target '{step.target.name}' is not visible",
            )

        if not enabled:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=False,
                duration_ms=elapsed_ms,
                failure_type=FailureType.ELEMENT_NOT_VISIBLE,
                error_message=f"Target '{step.target.name}' is disabled",
            )

        assert locator is not None

        if step.action == ActionType.FILL_FIELD:
            if not step.field_key or step.field_key not in intent.test_data:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                return StepResult(
                    step_index=step_index,
                    step=step,
                    success=False,
                    duration_ms=elapsed_ms,
                    failure_type=FailureType.CONFIG,
                    error_message=f"field_key '{step.field_key}' missing from intent test_data",
                )

            value = intent.test_data[step.field_key]
            await locator.fill(value, timeout=STEP_TIMEOUT_MS)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=True,
                duration_ms=elapsed_ms,
            )

        elif step.action == ActionType.CLICK_BUTTON:
            await locator.click(timeout=STEP_TIMEOUT_MS)
            try:
                await session.page.wait_for_load_state(
                    "domcontentloaded", timeout=STEP_TIMEOUT_MS
                )
            except Exception:
                pass
            await asyncio.sleep(0.1)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_index=step_index,
                step=step,
                success=True,
                duration_ms=elapsed_ms,
            )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return StepResult(
            step_index=step_index,
            step=step,
            success=False,
            duration_ms=elapsed_ms,
            failure_type=FailureType.CONFIG,
            error_message=f"Unknown step action: {step.action}",
        )

    except PlaywrightTimeoutError as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return StepResult(
            step_index=step_index,
            step=step,
            success=False,
            duration_ms=elapsed_ms,
            failure_type=FailureType.TIMEOUT,
            error_message=f"Playwright timeout: {exc}",
        )
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return StepResult(
            step_index=step_index,
            step=step,
            success=False,
            duration_ms=elapsed_ms,
            failure_type=FailureType.UNKNOWN,
            error_message=str(exc),
        )
