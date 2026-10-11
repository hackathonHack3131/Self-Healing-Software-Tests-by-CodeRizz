"""Tests for Module 7: rule-based failure triage classifier and compact failure context."""

import pytest
from engine.browser import BrowserSession
from engine.classifier import classify
from engine.context import build_failure_context, summarize_diff
from engine.diff import diff_snapshots
from engine.executor import run_recipe
from engine.models import (
    ActionType,
    Check,
    FailureContext,
    FailureType,
    Intent,
    PageSnapshot,
    Recipe,
    RecommendedAction,
    RenamedElement,
    RunResult,
    SnapshotDiff,
    Status,
    Step,
    StepResult,
    StepTarget,
    TargetBy,
    UIElement,
    UIInventory,
    Verdict,
    VerificationResult,
)
from engine.recipes import load_intent, load_recipe
from engine.snapshot import capture_page_snapshot, load_baseline_inventory
from engine.verifier import verify_outcome


@pytest.fixture
def checkout_intent():
    return load_intent("checkout")


@pytest.fixture
def recipe_v1(checkout_intent):
    return load_recipe("checkout", version=1, intent=checkout_intent)


def _make_step(action: ActionType, name: str | None = None, field_key: str | None = None) -> Step:
    target = StepTarget(by=TargetBy.LABEL, name=name) if name else None
    return Step(action=action, target=target, field_key=field_key)


def _make_run_result(
    failed_index: int | None = None,
    failure_type: FailureType | None = None,
    http_errors: list | None = None,
    alerts: list | None = None,
) -> RunResult:
    evidence = {
        "http_errors": http_errors or [],
        "alerts": alerts or [],
        "step_urls": ["/v/a/"],
    }
    status = Status.PASS_NO_HEAL if failed_index is None else Status.FAIL_FUNCTIONAL
    steps = [
        StepResult(
            step_index=0,
            step=_make_step(ActionType.GOTO_START),
            success=failed_index != 0,
            failure_type=failure_type if failed_index == 0 else None,
        )
    ]
    return RunResult(
        status=status,
        steps=steps,
        failed_step_index=failed_index,
        failure_type=failure_type,
        evidence=evidence,
    )


# -------------------------------------------------------------
# 1. Parametrized Rules Table Tests
# -------------------------------------------------------------

@pytest.mark.parametrize(
    "case_name, run_res, verification, diff, is_retry, retry_count, expected_verdict, expected_rec, expected_conf",
    [
        # Rule 1: HTTP 500 error alone -> APP_BUG, 0.9, REPORT
        (
            "rule1_http_500",
            _make_run_result(failed_index=0, failure_type=FailureType.UNKNOWN, http_errors=[{"status": 500}]),
            None,
            None,
            False,
            0,
            Verdict.APP_BUG,
            RecommendedAction.REPORT,
            0.9,
        ),
        # Rule 1: Visible error alert alone -> APP_BUG, 0.9, REPORT
        (
            "rule1_visible_alert",
            _make_run_result(failed_index=0, failure_type=FailureType.UNKNOWN, alerts=["Payment Gateway Unavailable"]),
            None,
            None,
            False,
            0,
            Verdict.APP_BUG,
            RecommendedAction.REPORT,
            0.9,
        ),
        # Rule 1 Conflict Case: ELEMENT_NOT_FOUND together with a 500 error gives APP_BUG (500 wins)
        (
            "rule1_conflict_missing_element_and_500",
            _make_run_result(
                failed_index=1,
                failure_type=FailureType.ELEMENT_NOT_FOUND,
                http_errors=[{"status": 502, "url_path": "/v/b/payment"}],
            ),
            None,
            None,
            False,
            0,
            Verdict.APP_BUG,
            RecommendedAction.REPORT,
            0.9,
        ),
        # Rule 1 Conflict Case: ELEMENT_NOT_FOUND together with visible alert gives APP_BUG (alert wins)
        (
            "rule1_conflict_missing_element_and_alert",
            _make_run_result(
                failed_index=1,
                failure_type=FailureType.ELEMENT_NOT_FOUND,
                alerts=["Internal error occurred"],
            ),
            None,
            None,
            False,
            0,
            Verdict.APP_BUG,
            RecommendedAction.REPORT,
            0.9,
        ),
        # Rule 2: ELEMENT_NOT_FOUND alone without diff -> UI_DRIFT, 0.8, HEAL
        (
            "rule2_element_not_found_no_diff",
            _make_run_result(failed_index=1, failure_type=FailureType.ELEMENT_NOT_FOUND),
            None,
            None,
            False,
            0,
            Verdict.UI_DRIFT,
            RecommendedAction.HEAL,
            0.8,
        ),
        # Rule 2: ELEMENT_AMBIGUOUS alone -> UI_DRIFT, 0.8, HEAL
        (
            "rule2_element_ambiguous",
            _make_run_result(failed_index=2, failure_type=FailureType.ELEMENT_AMBIGUOUS),
            None,
            None,
            False,
            0,
            Verdict.UI_DRIFT,
            RecommendedAction.HEAL,
            0.8,
        ),
        # Rule 2: ELEMENT_NOT_VISIBLE alone -> UI_DRIFT, 0.8, HEAL
        (
            "rule2_element_not_visible",
            _make_run_result(failed_index=3, failure_type=FailureType.ELEMENT_NOT_VISIBLE),
            None,
            None,
            False,
            0,
            Verdict.UI_DRIFT,
            RecommendedAction.HEAL,
            0.8,
        ),
        # Rule 2 Confidence Bump: ELEMENT_NOT_FOUND with diff showing renamed controls -> UI_DRIFT, 0.9, HEAL
        (
            "rule2_confidence_bump_renamed",
            _make_run_result(failed_index=1, failure_type=FailureType.ELEMENT_NOT_FOUND),
            None,
            SnapshotDiff(
                renamed=[
                    RenamedElement(
                        old_element=UIElement(role="textbox", name="Name", tag_name="input", page_path="/"),
                        new_element=UIElement(role="textbox", name="Full name", tag_name="input", page_path="/"),
                        old_name="Name",
                        new_name="Full name",
                    )
                ]
            ),
            False,
            0,
            Verdict.UI_DRIFT,
            RecommendedAction.HEAL,
            0.9,
        ),
        # Rule 2 Confidence Bump: ELEMENT_NOT_FOUND with diff showing added controls -> UI_DRIFT, 0.9, HEAL
        (
            "rule2_confidence_bump_added",
            _make_run_result(failed_index=1, failure_type=FailureType.ELEMENT_NOT_FOUND),
            None,
            SnapshotDiff(
                added=[UIElement(role="button", name="Continue to payment", tag_name="button", page_path="/")]
            ),
            False,
            0,
            Verdict.UI_DRIFT,
            RecommendedAction.HEAL,
            0.9,
        ),
        # Rule 3: All steps ran, verifier failed on total_matches (silent bug) -> APP_BUG, 0.75, REPORT
        (
            "rule3_silent_bug_total_matches",
            _make_run_result(failed_index=None),
            VerificationResult(
                passed=False,
                checks=[
                    Check(name="confirmation_visible", passed=True, detail="ok"),
                    Check(name="order_id_present", passed=True, detail="ok"),
                    Check(name="total_matches", passed=False, detail="32.50 != 36.50"),
                    Check(name="no_server_errors", passed=True, detail="ok"),
                    Check(name="no_error_alert", passed=True, detail="ok"),
                ],
            ),
            None,
            False,
            0,
            Verdict.APP_BUG,
            RecommendedAction.REPORT,
            0.75,
        ),
        # Rule 3: All steps ran, verifier failed on confirmation_visible -> APP_BUG, 0.75, REPORT
        (
            "rule3_silent_bug_confirmation_missing",
            _make_run_result(failed_index=None),
            VerificationResult(
                passed=False,
                checks=[
                    Check(name="confirmation_visible", passed=False, detail="missing phrase"),
                    Check(name="order_id_present", passed=True, detail="ok"),
                    Check(name="total_matches", passed=True, detail="ok"),
                    Check(name="no_server_errors", passed=True, detail="ok"),
                    Check(name="no_error_alert", passed=True, detail="ok"),
                ],
            ),
            None,
            False,
            0,
            Verdict.APP_BUG,
            RecommendedAction.REPORT,
            0.75,
        ),
        # Rule 4: TIMEOUT on first attempt -> FLAKY, 0.8, RETRY
        (
            "rule4_timeout_first_run",
            _make_run_result(failed_index=2, failure_type=FailureType.TIMEOUT),
            None,
            None,
            False,
            0,
            Verdict.FLAKY,
            RecommendedAction.RETRY,
            0.8,
        ),
        # Rule 4 Retry-then-REVIEW path: TIMEOUT repeated on retry -> UNKNOWN, 0.5, REVIEW
        (
            "rule4_timeout_repeated_retry",
            _make_run_result(failed_index=2, failure_type=FailureType.TIMEOUT),
            None,
            None,
            True,  # is_retry
            1,     # retry_count
            Verdict.UNKNOWN,
            RecommendedAction.REVIEW,
            0.5,
        ),
        # Rule 5: Fallback for unexpected CONFIG error -> UNKNOWN, 0.5, REVIEW
        (
            "rule5_fallback_config",
            _make_run_result(failed_index=0, failure_type=FailureType.CONFIG),
            None,
            None,
            False,
            0,
            Verdict.UNKNOWN,
            RecommendedAction.REVIEW,
            0.5,
        ),
    ],
)
def test_classifier_rules(
    case_name,
    run_res,
    verification,
    diff,
    is_retry,
    retry_count,
    expected_verdict,
    expected_rec,
    expected_conf,
):
    """Test every rule and priority edge case in the classifier decision matrix."""
    triage = classify(
        run_result=run_res,
        verification=verification,
        diff=diff,
        is_retry=is_retry,
        retry_count=retry_count,
    )
    assert triage.verdict == expected_verdict, f"Failed case {case_name}: verdict mismatch"
    assert triage.recommended == expected_rec, f"Failed case {case_name}: recommendation mismatch"
    assert triage.confidence == expected_conf, f"Failed case {case_name}: confidence mismatch"
    assert len(triage.evidence) > 0, f"Failed case {case_name}: evidence list empty"


# -------------------------------------------------------------
# 2. FailureContext Structure & Privacy Invariants Tests
# -------------------------------------------------------------

def test_failure_context_privacy_and_structure(checkout_intent, recipe_v1):
    """Verify FailureContext contains field keys only, never sensitive values, cards or passwords."""
    run_res = _make_run_result(failed_index=1, failure_type=FailureType.ELEMENT_NOT_FOUND)
    triage = classify(run_res)

    context = build_failure_context(
        intent=checkout_intent,
        recipe=recipe_v1,
        run_result=run_res,
        triage=triage,
    )

    # Goal and field keys
    assert context.goal == checkout_intent.goal
    assert context.field_keys == ["full_name", "email", "street_address", "card_number", "expiry", "cvc"]
    assert context.failed_step_index == 1
    assert context.failure_type == FailureType.ELEMENT_NOT_FOUND
    assert len(context.passed_steps) == 1
    assert context.failed_step is not None
    assert context.failed_step.field_key == "full_name"

    # Strict Privacy Check on Serialized Content
    dumped = context.model_dump_json()
    # Actual test data values from checkout_intent
    for sensitive_val in ("4242424242424242", "Jane Doe", "jane@example.com", "123 Main St", "12/30", "123"):
        assert sensitive_val not in dumped, f"Sensitive value '{sensitive_val}' was leaked into FailureContext!"

    # Token estimate is well below budget
    assert context.estimated_tokens() < 6000


def test_failure_context_validator_rejects_card_leaks():
    """Verify FailureContext validator blocks attempts to leak card numbers."""
    run_res = _make_run_result(failed_index=0, failure_type=FailureType.UNKNOWN)
    triage = classify(run_res)

    with pytest.raises(ValueError, match="Privacy violation"):
        FailureContext(
            goal="Test",
            field_keys=["4242424242424242"],  # Accidental card number in keys
            triage=triage,
        )


# -------------------------------------------------------------
# 3. Live Integration Checks: Version B (UI_DRIFT), C (APP_BUG), D (APP_BUG)
# -------------------------------------------------------------

async def test_live_version_b_recipe_v1_classified_ui_drift_and_heal(
    make_settings, checkout_intent, recipe_v1
):
    """Live check: running Recipe v1 against Version B fails with UI_DRIFT and HEAL.

    Confirms FailureContext contains field keys but no card numbers, and is under 6k tokens.
    """
    settings, start_url = make_settings("/v/b/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        # Run recipe v1 against Version B
        run_res = await run_recipe(recipe_v1, checkout_intent, session)

        # Step 1 should fail because "Name" does not exist on Version B cart page
        assert run_res.failed_step_index == 1
        assert run_res.failure_type == FailureType.ELEMENT_NOT_FOUND

        # Capture current page snapshot on Version B
        current_snapshot = await capture_page_snapshot(session.page)

        # Load trusted Version A baseline
        baseline = load_baseline_inventory()

        # Compute diff between baseline and current Version B snapshot
        diff = diff_snapshots(baseline, current_snapshot)

        # Classify the outcome
        triage = classify(run_res, diff=diff)

        # Verification: must be UI_DRIFT with HEAL recommendation
        assert triage.verdict == Verdict.UI_DRIFT
        assert triage.recommended == RecommendedAction.HEAL
        assert triage.confidence >= 0.8
        assert len(triage.evidence) >= 1

        # Build FailureContext
        context = build_failure_context(
            intent=checkout_intent,
            recipe=recipe_v1,
            run_result=run_res,
            triage=triage,
            current_inventory=current_snapshot,
            diff=diff,
        )

        # Print FailureContext representation for inspection
        print("\n=== LIVE VERSION B FAILURE CONTEXT ===")
        print(f"Goal: {context.goal}")
        print(f"Field Keys (names only): {context.field_keys}")
        print(f"Failed Step Index: {context.failed_step_index} ({context.failure_type})")
        print(f"Triage Verdict: {context.triage.verdict} ({context.triage.recommended})")
        print(f"Diff Summary:\n{context.diff_summary}")
        print(f"Estimated tokens: {context.estimated_tokens()}")

        # Verify no card number in serialized context
        dumped_json = context.model_dump_json()
        assert "4242424242424242" not in dumped_json
        assert "Jane Doe" not in dumped_json
        assert "123 Main St" not in dumped_json

        # Token budget check (< 6k tokens)
        assert context.estimated_tokens() < 6000


async def test_live_version_c_classified_app_bug(make_settings, checkout_intent):
    """Live check: Version C server error (HTTP 500) is classified as APP_BUG and REPORT."""
    settings, start_url = make_settings("/v/c/")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        # Trigger HTTP 500 via POST to /v/c/place
        resp = await session.page.request.post(f"{settings.DEMO_BASE_URL}/v/c/place")
        assert resp.status == 500
        content = await resp.text()
        await session.page.set_content(content)
        session.monitor.http_errors.append(
            {"method": "POST", "url_path": "/v/c/place", "status": 500}
        )

        run_res = RunResult(
            status=Status.FAIL_FUNCTIONAL,
            failed_step_index=0,
            failure_type=FailureType.HTTP_ERROR,
            evidence=session.monitor.get_evidence(),
        )

        triage = classify(run_res)
        assert triage.verdict == Verdict.APP_BUG
        assert triage.recommended == RecommendedAction.REPORT
        assert triage.confidence == 0.9
        assert any("500" in e for e in triage.evidence)


async def test_live_version_d_classified_app_bug(make_settings, checkout_intent):
    """Live check: Version D wrong total ($32.50) is classified as APP_BUG and REPORT (silent bug)."""
    settings, start_url = make_settings("/v/d/confirmation")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        await session.goto_start()
        ver_res = await verify_outcome(session.page, checkout_intent, session.monitor)
        assert ver_res.passed is False

        # All steps ran successfully
        run_res = RunResult(
            status=Status.FAIL_FUNCTIONAL,
            failed_step_index=None,
            verification=ver_res,
            evidence=session.monitor.get_evidence(),
        )

        triage = classify(run_res, verification=ver_res)
        assert triage.verdict == Verdict.APP_BUG
        assert triage.recommended == RecommendedAction.REPORT
        assert triage.confidence == 0.75
        assert any("total_matches" in e for e in triage.evidence)
