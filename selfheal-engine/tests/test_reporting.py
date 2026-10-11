"""Unit tests for Module 10: Run Reporting and Artifact Generation (engine/reporting.py).

Tests:
1. Every RunReport status supported and formatted correctly.
2. Complete artifact creation in runs/<run_id>/ and copy to runs/latest/.
3. report.json schema validation against RunReport Pydantic model.
4. Static HTML parsing and content verification.
5. Correct honest headlines for FAIL_FUNCTIONAL (HTTP 500 and total mismatch, both healed and unhealed).
6. Prominent RECORDED mode labeling.
7. Strict secret & credit card redaction: fake GOOGLE_API_KEY and full card numbers must be 100% absent from runs/.
"""

import json
from pathlib import Path
import shutil
import pytest

from engine.models import (
    Check,
    FailureType,
    HealResult,
    Intent,
    PageSnapshot,
    Recipe,
    RunReport,
    RunResult,
    SnapshotDiff,
    Status,
    Step,
    StepResult,
    ActionType,
    StepTarget,
    TargetBy,
    Triage,
    Verdict,
    RecommendedAction,
    VerificationResult,
)
from engine.orchestrator import OrchestratorEvent, OrchestratorResult
from engine.recipes import load_intent
from engine.reporting import (
    build_headline,
    build_run_report,
    generate_run_artifacts,
    redact_data,
    redact_secrets,
    render_html_report,
    render_markdown_report,
)


@pytest.fixture
def checkout_intent():
    return load_intent("checkout")


def _make_dummy_orch_result(
    status: Status,
    healed: bool = False,
    app_version: str = "a",
    evidence: dict | None = None,
    triage: Triage | None = None,
    verification: VerificationResult | None = None,
    heal_result: HealResult | None = None,
) -> OrchestratorResult:
    ev = evidence or {}
    steps = [
        StepResult(
            step_index=0,
            step=Step(action=ActionType.GOTO_START),
            success=True,
            duration_ms=10.0,
        )
    ]
    init_res = RunResult(status=status, steps=steps, evidence=ev)

    ver = verification
    if ver is None:
        checks = [
            Check(name="order_id_present", passed="PASS" in status.value, detail="Order ID matched", evidence="QA-101"),
            Check(name="total_matches", passed="PASS" in status.value, detail="Total matched expected $36.50, actual $36.50", evidence="36.50"),
        ]
        ver = VerificationResult(passed="PASS" in status.value, checks=checks)

    events = [
        OrchestratorEvent(timestamp="2026-10-11T12:00:00Z", phase="INIT", message="Starting run", level="info"),
        OrchestratorEvent(timestamp="2026-10-11T12:00:01Z", phase="EXECUTE", message="Executed steps", level="info"),
    ]

    return OrchestratorResult(
        run_id=f"test_run_{status.value.lower()}",
        intent_id="checkout",
        target_url=f"http://127.0.0.1:5000/v/{app_version}/",
        status=status,
        status_label=f"Label for {status.value}",
        initial_recipe_version=1,
        new_recipe_version=2 if healed else 1,
        healed=healed,
        duration_ms=150.0,
        initial_run_result=init_res,
        verification=ver,
        triage=triage,
        heal_result=heal_result,
        events=events,
        evidence=ev,
    )


# -------------------------------------------------------------
# 1. Headline generation tests
# -------------------------------------------------------------

def test_headline_generation_all_cases():
    """Verify honest headline generation for every required scenario."""
    # PASS_NO_HEAL
    h = build_headline(Status.PASS_NO_HEAL, False, 1, None, None, {})
    assert "cleanly with zero healing" in h

    # PASS_AFTER_HEAL
    h = build_headline(Status.PASS_AFTER_HEAL, True, 2, None, None, {})
    assert "repaired: recipe updated to v2" in h

    # FAIL_FUNCTIONAL with HTTP 500 when healed
    h = build_headline(Status.FAIL_FUNCTIONAL, True, 2, None, None, {"http_errors": [{"status": 500}]})
    assert h == "UI repaired successfully, but the application failed: HTTP 500 on order submission"

    # FAIL_FUNCTIONAL with HTTP 500 unhealed
    h = build_headline(Status.FAIL_FUNCTIONAL, False, 1, None, None, {"http_errors": [{"status": 500}]})
    assert h == "Application defect detected: HTTP 500 on order submission (healing refused)"

    # FAIL_FUNCTIONAL with calculation invariant when healed
    ver_fail_total = VerificationResult(
        passed=False,
        checks=[Check(name="total_matches", passed=False, detail="Expected $36.50, got $32.50", evidence="32.50")],
    )
    h = build_headline(Status.FAIL_FUNCTIONAL, True, 2, None, ver_fail_total, {})
    assert "UI repaired successfully, but the application failed: total mismatch; expected $36.50, actual $32.50" in h

    # FAIL_FUNCTIONAL with calculation invariant unhealed
    h = build_headline(Status.FAIL_FUNCTIONAL, False, 1, None, ver_fail_total, {})
    assert "Application defect detected: total mismatch; expected $36.50, actual $32.50" in h

    # FAIL_HEALING
    h = build_headline(Status.FAIL_HEALING, False, 1, None, None, {})
    assert "Self-healing agent failed to discover" in h

    # BLOCKED_CONFIG
    h = build_headline(Status.BLOCKED_CONFIG, False, 1, None, None, {})
    assert "missing required model configuration" in h

    # BLOCKED_AGENT
    h = build_headline(Status.BLOCKED_AGENT, False, 1, None, None, {})
    assert "AI agent API call failed" in h


# -------------------------------------------------------------
# 2. Every status report generation & schema validation
# -------------------------------------------------------------

@pytest.mark.parametrize("status", list(Status))
def test_every_status_produces_valid_run_report(status, checkout_intent):
    """Every Status enum value must produce a schema-valid RunReport."""
    healed = status == Status.PASS_AFTER_HEAL
    orch_res = _make_dummy_orch_result(status=status, healed=healed)
    report = build_run_report(orch_res, intent=checkout_intent)

    assert isinstance(report, RunReport)
    assert report.status == status
    assert report.run_id == orch_res.run_id
    assert report.intent_id == "checkout"

    # Ensure JSON serializable and re-parseable
    dumped = report.model_dump_json()
    reloaded = RunReport.model_validate_json(dumped)
    assert reloaded.status == status


# -------------------------------------------------------------
# 3. Artifact generation in runs/<run_id>/ and runs/latest/
# -------------------------------------------------------------

def test_artifact_generation_and_latest_copy(tmp_path, checkout_intent):
    """Artifact bundle must generate all required files in run folder and sync to latest/."""
    orch_res = _make_dummy_orch_result(status=Status.PASS_NO_HEAL)
    report = build_run_report(orch_res, intent=checkout_intent)

    run_dir = generate_run_artifacts(report=report, output_dir=tmp_path)

    assert run_dir.exists()
    assert (run_dir / "report.json").exists()
    assert (run_dir / "report.md").exists()
    assert (run_dir / "report.html").exists()
    assert (run_dir / "snapshot_current.json").exists()
    assert (run_dir / "diff.json").exists()
    assert (run_dir / "agent_trace.json").exists()
    assert (run_dir / "screenshots").is_dir()

    # Validate report.json schema
    with open(run_dir / "report.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    loaded_report = RunReport.model_validate(data)
    assert loaded_report.run_id == report.run_id

    # Validate latest/ directory
    latest_dir = tmp_path / "latest"
    assert latest_dir.exists()
    assert (latest_dir / "report.json").exists()
    assert (latest_dir / "report.html").exists()

    # Check HTML contains essential elements
    html_text = (run_dir / "report.html").read_text(encoding="utf-8")
    assert report.headline in html_text
    assert report.status.value in html_text
    assert "SelfHeal" in html_text


# -------------------------------------------------------------
# 4. RECORDED mode label test
# -------------------------------------------------------------

def test_recorded_mode_prominently_labeled(checkout_intent):
    """Healed runs with recorded trace must be labeled RECORDED, never live AI."""
    heal_res = HealResult(
        status=Status.PASS_AFTER_HEAL,
        executed_steps=[Step(action=ActionType.GOTO_START)],
        explanation="RECORDED: Replayed trace",
        is_recorded=True,
    )
    orch_res = _make_dummy_orch_result(
        status=Status.PASS_AFTER_HEAL,
        healed=True,
        heal_result=heal_res,
    )
    report = build_run_report(orch_res, intent=checkout_intent)

    assert report.mode == "RECORDED"
    assert report.llm_calls == 0
    assert "Recorded" in report.provider

    html = render_html_report(report)
    assert "MODE: RECORDED" in html

    md = render_markdown_report(report)
    assert "**Mode**: `RECORDED`" in md


# -------------------------------------------------------------
# 5. Secret and Credit Card Redaction Test
# -------------------------------------------------------------

def test_secret_redaction_and_card_masking(tmp_path, checkout_intent):
    """Fake API key and real credit card numbers must NEVER appear in generated files."""
    fake_api_key = "AIzaSyD-FAKE-SECRET-KEY-ABC123456789"
    raw_card = "4242424242424242"

    orch_res = _make_dummy_orch_result(status=Status.PASS_NO_HEAL)
    orch_res.events.append(
        OrchestratorEvent(
            timestamp="2026-10-11T12:00:02Z",
            phase="DEBUG",
            message=f"Filled card {raw_card} using key {fake_api_key}",
            level="info",
        )
    )

    report = build_run_report(orch_res, intent=checkout_intent, custom_secrets=[fake_api_key])
    run_dir = generate_run_artifacts(report=report, output_dir=tmp_path, custom_secrets=[fake_api_key])

    # Scan every single file in the runs directory
    all_files = list(tmp_path.rglob("*"))
    for file_path in all_files:
        if file_path.is_file():
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            assert fake_api_key not in content, f"Secret leaked in {file_path.name}"
            assert raw_card not in content, f"Credit card leaked in {file_path.name}"
            if "••••" in content:
                assert "4242" in content  # Last 4 digits allowed masked
