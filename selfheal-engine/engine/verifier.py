"""Deterministic verifier for checkout business outcomes and invariants."""

from decimal import Decimal, InvalidOperation
import re
from typing import Any
from playwright.async_api import Page
from engine.models import Check, Intent, VerificationResult
from engine.monitor import Monitor


def _parse_currency_candidates(page_text: str) -> list[Decimal]:
    """Extract candidate currency amounts from page text using Decimal."""
    candidates: list[Decimal] = []

    # Priority 1: Lines explicitly referencing total / paid / charged / amount
    for line in page_text.splitlines():
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ("total", "paid", "charged", "amount")):
            matches = re.findall(r"\$?\s*(\d+(?:\.\d{2})?)", line)
            for m in matches:
                try:
                    val = Decimal(m)
                    if val not in candidates:
                        candidates.append(val)
                except InvalidOperation:
                    continue

    # Priority 2: Any explicit currency formatted values ($X.XX)
    all_currency_matches = re.findall(r"\$\s*(\d+(?:\.\d{2})?)", page_text)
    for m in all_currency_matches:
        try:
            val = Decimal(m)
            if val not in candidates:
                candidates.append(val)
        except InvalidOperation:
            continue

    return candidates


async def verify_outcome(
    page: Page,
    intent: Intent,
    monitor: Monitor | None = None,
    since_mark: Any = None,
) -> VerificationResult:
    """Verify outcome and business invariants. Returns VerificationResult with 5 checks."""
    checks: list[Check] = []

    # Get body text for fast text-based invariant evaluation
    try:
        page_text = (await page.inner_text("body")).strip()
    except Exception:
        page_text = ""

    # Check 1: confirmation_visible
    phrase = intent.expected_outcome.confirmation_phrase
    phrase_visible = False
    try:
        locator = page.get_by_text(phrase, exact=False)
        if await locator.count() > 0 and await locator.first.is_visible():
            phrase_visible = True
    except Exception:
        pass

    if not phrase_visible and phrase.lower() in page_text.lower():
        phrase_visible = True

    if phrase_visible:
        checks.append(
            Check(
                name="confirmation_visible",
                passed=True,
                detail=f"Confirmation phrase '{phrase}' is visible on page",
                evidence=phrase,
            )
        )
    else:
        checks.append(
            Check(
                name="confirmation_visible",
                passed=False,
                detail=f"Confirmation phrase '{phrase}' is not visible on page",
                evidence=None,
            )
        )

    # Check 2: order_id_present
    pattern = intent.expected_outcome.order_id_pattern
    order_id_match = re.search(pattern, page_text)
    if order_id_match:
        matched_id = order_id_match.group(0)
        checks.append(
            Check(
                name="order_id_present",
                passed=True,
                detail=f"Order ID '{matched_id}' matches pattern '{pattern}'",
                evidence=matched_id,
            )
        )
    else:
        checks.append(
            Check(
                name="order_id_present",
                passed=False,
                detail=f"Order ID matching pattern '{pattern}' not found",
                evidence=None,
            )
        )

    # Check 3: total_matches
    expected_total = Decimal(str(intent.expected_outcome.expected_total))

    # Also inspect dedicated total elements if present
    element_totals: list[Decimal] = []
    try:
        total_locators = await page.locator(
            "#order-total, #b-total-charged, .summary-total, .total"
        ).all()
        for el in total_locators:
            if await el.is_visible():
                txt = await el.inner_text()
                matches = re.findall(r"\d+(?:\.\d{2})?", txt)
                for m in matches:
                    try:
                        element_totals.append(Decimal(m))
                    except InvalidOperation:
                        pass
    except Exception:
        pass

    candidates = element_totals + _parse_currency_candidates(page_text)

    # If any specific total element matches, or any candidate equals expected total
    total_matched = False
    observed_total: Decimal | None = None

    if element_totals:
        observed_total = element_totals[0]
        total_matched = any(et == expected_total for et in element_totals)
    elif candidates:
        observed_total = candidates[0]
        total_matched = any(c == expected_total for c in candidates)

    if total_matched:
        checks.append(
            Check(
                name="total_matches",
                passed=True,
                detail=f"Confirmed total matches expected total of {expected_total}",
                evidence=str(expected_total),
            )
        )
    else:
        checks.append(
            Check(
                name="total_matches",
                passed=False,
                detail=(
                    f"Observed total '{observed_total}' does not match "
                    f"expected total '{expected_total}'"
                ),
                evidence=str(observed_total) if observed_total else None,
            )
        )

    # Check 4: no_server_errors
    http_errors: list[dict[str, Any]] = []
    if monitor is not None:
        if since_mark is not None:
            http_errors = monitor.since(since_mark).get("http_errors", [])
        else:
            http_errors = monitor.http_errors

    server_errors = [e for e in http_errors if e.get("status", 0) >= 500]
    if len(server_errors) == 0:
        checks.append(
            Check(
                name="no_server_errors",
                passed=True,
                detail="Zero HTTP 5xx errors recorded",
                evidence=[],
            )
        )
    else:
        checks.append(
            Check(
                name="no_server_errors",
                passed=False,
                detail=f"Recorded {len(server_errors)} HTTP 5xx error(s)",
                evidence=server_errors,
            )
        )

    # Check 5: no_error_alert
    alerts: list[str] = []
    if monitor is not None:
        alerts = await monitor.visible_alerts(page)
    else:
        try:
            elements = await page.locator(
                '[role="alert"], .alert, .error, .alert-error'
            ).all()
            for el in elements:
                if await el.is_visible():
                    txt = (await el.inner_text()).strip()
                    if txt and txt not in alerts:
                        alerts.append(txt)
        except Exception:
            pass

    if len(alerts) == 0:
        checks.append(
            Check(
                name="no_error_alert",
                passed=True,
                detail="Zero visible error or alert elements found",
                evidence=[],
            )
        )
    else:
        checks.append(
            Check(
                name="no_error_alert",
                passed=False,
                detail=f"Found visible error alert: '{alerts[0]}'",
                evidence=alerts,
            )
        )

    all_passed = all(c.passed for c in checks)
    return VerificationResult(passed=all_passed, checks=checks)
