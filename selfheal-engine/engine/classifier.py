"""Rule-based failure triage classifier.

Separates harmless UI redesigns (UI_DRIFT) from application bugs (APP_BUG)
and infrastructure flakiness (FLAKY) before any LLM is invoked.
Deterministic code only.
"""

from typing import Any
from engine.models import (
    FailureType,
    RecommendedAction,
    RunResult,
    SnapshotDiff,
    Triage,
    Verdict,
    VerificationResult,
)


def classify(
    run_result: RunResult,
    verification: VerificationResult | None = None,
    evidence: dict[str, Any] | None = None,
    diff: SnapshotDiff | None = None,
    is_retry: bool = False,
    retry_count: int = 0,
) -> Triage:
    """Classify execution outcome into a deterministic Triage verdict with confidence.

    Rules in priority order:
    1. HTTP >= 500 or visible error alert after submit: APP_BUG, confidence 0.9, REPORT.
       Wins even if an element was also missing.
    2. Failure is ELEMENT_NOT_FOUND, ELEMENT_AMBIGUOUS or ELEMENT_NOT_VISIBLE and no 5xx/alerts:
       UI_DRIFT, base confidence 0.8 (+0.1 if diff has renamed, removed, or added controls), HEAL.
    3. All steps ran but verifier failed on total_matches or confirmation_visible (no error signals):
       APP_BUG, confidence 0.75, REPORT (silent bug).
    4. Only TIMEOUT with no other signal: FLAKY, RETRY once; if repeats, UNKNOWN and REVIEW.
    5. Anything else: UNKNOWN, REVIEW.
    """
    # Consolidate evidence sources
    eff_evidence: dict[str, Any] = dict(evidence or {})
    if run_result and run_result.evidence:
        for k, v in run_result.evidence.items():
            if k not in eff_evidence:
                eff_evidence[k] = v

    http_errors = eff_evidence.get("http_errors", [])
    alerts = eff_evidence.get("alerts", [])

    # Consolidate verification checks
    eff_verification = verification or (run_result.verification if run_result else None)
    ver_checks = eff_verification.checks if eff_verification else []

    # Detect 5xx errors from evidence or verification
    has_5xx = any(
        isinstance(e, dict) and e.get("status", 0) >= 500 for e in http_errors
    )
    if any(c.name == "no_server_errors" and not c.passed for c in ver_checks):
        has_5xx = True

    # Detect visible alerts from evidence or verification
    has_alerts = len(alerts) > 0
    if any(c.name == "no_error_alert" and not c.passed for c in ver_checks):
        has_alerts = True

    # -------------------------------------------------------------
    # Rule 1: HTTP >= 500 or visible error alert (Application Bug)
    # Highest priority: wins even if an element was also missing.
    # -------------------------------------------------------------
    if has_5xx or has_alerts:
        evidence_lines: list[str] = []
        if has_5xx:
            server_errs = [
                f"{e.get('method', 'REQ')} {e.get('url_path', '/')}: {e.get('status', 500)}"
                for e in http_errors
                if isinstance(e, dict) and e.get("status", 0) >= 500
            ]
            err_str = "; ".join(server_errs) if server_errs else "HTTP 5xx server error detected"
            evidence_lines.append(f"Server error: {err_str}")
        if has_alerts:
            alert_str = str(alerts[0]) if alerts else "Visible error banner on page"
            evidence_lines.append(f"Visible error alert: '{alert_str}'")

        if run_result and run_result.failure_type:
            evidence_lines.append(
                f"Step failure occurred: {run_result.failure_type.value} "
                f"(superseded by server error / alert)"
            )

        return Triage(
            verdict=Verdict.APP_BUG,
            confidence=0.9,
            evidence=evidence_lines,
            recommended=RecommendedAction.REPORT,
            rule_name="HTTP_OR_ALERT_ERROR",
        )

    # -------------------------------------------------------------
    # Rule 2: Locator failures without server errors (UI Drift)
    # -------------------------------------------------------------
    locator_failures = {
        FailureType.ELEMENT_NOT_FOUND,
        FailureType.ELEMENT_AMBIGUOUS,
        FailureType.ELEMENT_NOT_VISIBLE,
    }

    step_failure_type = run_result.failure_type if run_result else None

    if step_failure_type in locator_failures:
        base_confidence = 0.8
        diff_has_controls = False

        if diff is not None:
            if len(diff.renamed) > 0 or len(diff.removed) > 0 or len(diff.added) > 0:
                diff_has_controls = True

        confidence = 0.9 if diff_has_controls else base_confidence

        evidence_lines = [
            f"Step {run_result.failed_step_index} failed with {step_failure_type.value} "
            f"and zero server errors or alerts"
        ]
        if diff_has_controls:
            evidence_lines.append(
                f"Diff indicates UI drift: {len(diff.renamed)} renamed, "
                f"{len(diff.added)} added, {len(diff.removed)} removed controls"
            )

        return Triage(
            verdict=Verdict.UI_DRIFT,
            confidence=confidence,
            evidence=evidence_lines,
            recommended=RecommendedAction.HEAL,
            rule_name="LOCATOR_FAILURE_DRIFT",
        )

    # -------------------------------------------------------------
    # Rule 3: All steps ran but verifier failed on total or confirmation
    # Silent functional application bug
    # -------------------------------------------------------------
    all_steps_ran = run_result is not None and run_result.failed_step_index is None
    verifier_failed = eff_verification is not None and not eff_verification.passed

    if all_steps_ran and verifier_failed:
        failed_checks = [c.name for c in ver_checks if not c.passed]
        silent_bug_checks = {"total_matches", "confirmation_visible", "order_id_present"}

        if any(fc in silent_bug_checks for fc in failed_checks):
            return Triage(
                verdict=Verdict.APP_BUG,
                confidence=0.75,
                evidence=[
                    f"All recipe steps executed successfully but deterministic verification "
                    f"failed on: {', '.join(failed_checks)} (silent application bug)"
                ],
                recommended=RecommendedAction.REPORT,
                rule_name="SILENT_VERIFICATION_FAILURE",
            )

    # -------------------------------------------------------------
    # Rule 4: TIMEOUT with no other signal (Flaky infrastructure)
    # -------------------------------------------------------------
    if step_failure_type == FailureType.TIMEOUT:
        if not is_retry and retry_count == 0:
            return Triage(
                verdict=Verdict.FLAKY,
                confidence=0.8,
                evidence=[
                    f"Step {run_result.failed_step_index} timed out with zero server errors "
                    "or alerts (flaky candidate)"
                ],
                recommended=RecommendedAction.RETRY,
                rule_name="TIMEOUT_FLAKY",
            )
        else:
            return Triage(
                verdict=Verdict.UNKNOWN,
                confidence=0.5,
                evidence=[
                    f"Step {run_result.failed_step_index} timed out repeatedly across retries"
                ],
                recommended=RecommendedAction.REVIEW,
                rule_name="TIMEOUT_REPEATED",
            )

    # -------------------------------------------------------------
    # Rule 5: Fallback for unclassified failures
    # -------------------------------------------------------------
    fail_detail = (
        f"failure_type={step_failure_type.value}"
        if step_failure_type
        else "no step failure recorded"
    )
    return Triage(
        verdict=Verdict.UNKNOWN,
        confidence=0.5,
        evidence=[f"Unclassified failure condition: {fail_detail}"],
        recommended=RecommendedAction.REVIEW,
        rule_name="DEFAULT_FALLBACK",
    )
