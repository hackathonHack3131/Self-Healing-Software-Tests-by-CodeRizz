"""Unit and integration tests for GitHub Change Intelligence (Modules 1-8 of Feature)."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import pytest

from engine.repo_analysis.diff_analyzer import (
    categorize_file,
    generate_grounded_findings,
    parse_raw_diff,
    redact_text,
)
from engine.repo_analysis.github_service import (
    GitHubValidationError,
    GitExecutionError,
    TemporaryRepository,
    get_commit_metadata,
    remove_readonly,
    resolve_comparison_commits,
    run_git_command,
    validate_and_normalize_repo_url,
    validate_git_ref,
)
from engine.repo_analysis.models import (
    AnalysisJobStatus,
    AnalysisMode,
    ChangeCategory,
    ChangedFile,
    CommitInfo,
    Finding,
    RepoAnalysisReport,
    RepoAnalysisRequest,
    SeverityLevel,
)
from engine.repo_analysis.report_builder import (
    AnalysisJobManager,
    analyze_repository_commits,
    get_reports_dir,
    persist_report_bundle,
    render_github_html_report,
    render_github_markdown_report,
    validate_job_id,
)
from webapp.server import create_app


@pytest.fixture
def local_git_repo():
    """Create an isolated, temporary local git repository with multiple commits."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_git_repo_"))
    try:
        # 1. Initialize repo
        subprocess.run(["git", "init"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test Committer"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "committer@example.com"], cwd=str(temp_dir), check=True, capture_output=True)

        # 2. Commit 1: Initial files
        (temp_dir / "app.py").write_text("def run():\n    return 'hello'\n", encoding="utf-8")
        (temp_dir / "old_name.py").write_text("print('to be renamed')\n", encoding="utf-8")
        (temp_dir / "delete_me.py").write_text("print('to be deleted')\n", encoding="utf-8")
        (temp_dir / "templates").mkdir()
        (temp_dir / "templates" / "index.html").write_text("<div><button id='checkout-btn'>Pay</button></div>\n", encoding="utf-8")
        (temp_dir / "tests").mkdir()
        (temp_dir / "tests" / "test_app.py").write_text("def test_run(): assert True\n", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit 1"], cwd=str(temp_dir), check=True, capture_output=True)
        c1_res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(temp_dir), check=True, capture_output=True, text=True)
        c1_sha = c1_res.stdout.strip()

        # 3. Commit 2: Changes (Modify app.py, add new_file.py, delete delete_me.py, rename old_name.py, change template)
        (temp_dir / "app.py").write_text("def run():\n    # assert valid\n    total = 100 * 0.9\n    return 'hello world'\n", encoding="utf-8")
        (temp_dir / "new_feature.py").write_text("def feature(): return True\n", encoding="utf-8")
        (temp_dir / "delete_me.py").unlink()
        subprocess.run(["git", "mv", "old_name.py", "renamed_name.py"], cwd=str(temp_dir), check=True, capture_output=True)
        (temp_dir / "templates" / "index.html").write_text("<div><button id='submit-order-button'>Submit Order</button></div>\n", encoding="utf-8")

        subprocess.run(["git", "add", "."], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Commit 2: Feature additions and UI updates"], cwd=str(temp_dir), check=True, capture_output=True)
        c2_res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(temp_dir), check=True, capture_output=True, text=True)
        c2_sha = c2_res.stdout.strip()

        yield temp_dir, c1_sha, c2_sha
    finally:
        shutil.rmtree(temp_dir, onerror=remove_readonly)


@pytest.fixture
def test_client():
    """Create Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# =========================================================================
# 1. URL and Ref Validation Tests
# =========================================================================

def test_url_validation_success():
    url, owner, repo = validate_and_normalize_repo_url("https://github.com/torvalds/linux")
    assert url == "https://github.com/torvalds/linux"
    assert owner == "torvalds"
    assert repo == "linux"

    url, owner, repo = validate_and_normalize_repo_url("https://github.com/pallets/flask.git")
    assert url == "https://github.com/pallets/flask"
    assert repo == "flask"


def test_url_validation_rejection():
    # Reject non-https
    with pytest.raises(GitHubValidationError, match="Only https:// is supported"):
        validate_and_normalize_repo_url("http://github.com/owner/repo")

    # Reject non-github host
    with pytest.raises(GitHubValidationError, match="Only public github.com repositories are supported"):
        validate_and_normalize_repo_url("https://gitlab.com/owner/repo")

    # Reject localhost / SSRF
    with pytest.raises(GitHubValidationError):
        validate_and_normalize_repo_url("https://127.0.0.1/owner/repo")

    # Reject embedded credentials
    with pytest.raises(GitHubValidationError, match="Embedded credentials"):
        validate_and_normalize_repo_url("https://user:token@github.com/owner/repo")

    # Reject path traversal
    with pytest.raises(GitHubValidationError):
        validate_and_normalize_repo_url("https://github.com/../etc/passwd")


def test_ref_validation():
    assert validate_git_ref("main") == "main"
    assert validate_git_ref("v1.2.3") == "v1.2.3"
    assert validate_git_ref("HEAD~1") == "HEAD~1"
    assert validate_git_ref(None) is None

    # Reject flags starting with hyphen (command injection defense)
    with pytest.raises(GitHubValidationError, match="cannot start with a hyphen"):
        validate_git_ref("--upload-pack=evil")


# =========================================================================
# 2. Diff Extraction & Categorization Tests
# =========================================================================

def test_diff_extraction_and_categorization(local_git_repo):
    repo_dir, c1_sha, c2_sha = local_git_repo

    changed_files, is_truncated = parse_raw_diff(repo_dir, c1_sha, c2_sha)
    assert not is_truncated
    assert len(changed_files) >= 4

    # Verify statuses
    paths = {f.path: f for f in changed_files}
    assert "new_feature.py" in paths
    assert paths["new_feature.py"].status == "added"

    assert "delete_me.py" in paths
    assert paths["delete_me.py"].status == "deleted"

    assert "renamed_name.py" in paths
    assert paths["renamed_name.py"].status == "renamed"
    assert paths["renamed_name.py"].old_path == "old_name.py"

    assert "app.py" in paths
    assert paths["app.py"].status == "modified"

    # Category checks
    assert categorize_file("templates/index.html") == ChangeCategory.UI_UX
    assert categorize_file("tests/test_run.py") == ChangeCategory.TESTS
    assert categorize_file("requirements.txt") == ChangeCategory.DEPENDENCIES_CONFIG
    assert categorize_file("webapp/api.py") == ChangeCategory.BACKEND_API
    assert categorize_file("engine/service.py") == ChangeCategory.FUNCTIONALITY


def test_grounded_risk_findings(local_git_repo):
    repo_dir, c1_sha, c2_sha = local_git_repo
    changed_files, _ = parse_raw_diff(repo_dir, c1_sha, c2_sha)
    findings = generate_grounded_findings(changed_files)

    assert len(findings) > 0
    # Must have detected UI locator drift from button change
    ui_findings = [f for f in findings if f.category == ChangeCategory.UI_UX]
    assert len(ui_findings) > 0
    assert "UI locator or form control changed" in ui_findings[0].what_changed
    assert ui_findings[0].severity == SeverityLevel.MEDIUM


def test_empty_diff(local_git_repo):
    repo_dir, _, c2_sha = local_git_repo
    changed_files, is_truncated = parse_raw_diff(repo_dir, c2_sha, c2_sha)
    assert len(changed_files) == 0
    assert not is_truncated
    findings = generate_grounded_findings(changed_files)
    assert len(findings) == 0


# =========================================================================
# 3. Secret Redaction Tests
# =========================================================================

def test_secret_redaction():
    raw_patch = (
        "+ api_key = 'AIzaSyA1234567890123456789012345678901'\n"
        "+ test_card = '4242424242424242'\n"
        "+ token = 'ghp_123456789012345678901234567890123456'\n"
    )
    cleaned = redact_text(raw_patch)
    assert "AIza" not in cleaned
    assert "4242424242424242" not in cleaned
    assert "•••• •••• •••• 4242" in cleaned
    assert "ghp_" not in cleaned


# =========================================================================
# 4. End-to-End Local Analysis & Report Generation
# =========================================================================

def test_analyze_repository_commits(local_git_repo):
    repo_dir, c1_sha, c2_sha = local_git_repo
    req = RepoAnalysisRequest(
        repo_url=str(repo_dir),
        base_ref=c1_sha,
        head_ref=c2_sha,
    )

    report = analyze_repository_commits(req, allow_local=True)
    assert report.status == AnalysisJobStatus.COMPLETED
    assert report.total_files_changed >= 4
    assert report.total_additions > 0
    assert report.base_commit.short_sha == c1_sha[:7]
    assert report.head_commit.short_sha == c2_sha[:7]

    # Verify generated bundle
    report_dir = get_reports_dir() / report.job_id
    assert (report_dir / "report.json").exists()
    assert (report_dir / "report.md").exists()
    assert (report_dir / "report.html").exists()

    # Verify HTML template render
    html_content = (report_dir / "report.html").read_text(encoding="utf-8")
    assert "SelfHeal Change Intelligence" in html_content
    assert report.job_id in html_content

    # Clean up test report directory
    shutil.rmtree(report_dir, onerror=remove_readonly)


# =========================================================================
# 5. Path Traversal & Security Validation
# =========================================================================

def test_validate_job_id_security():
    assert validate_job_id("gh_20261011_123456") == "gh_20261011_123456"

    with pytest.raises(ValueError, match="Directory traversal"):
        validate_job_id("../../../etc/passwd")

    with pytest.raises(ValueError, match="disallowed characters"):
        validate_job_id("job;rm-rf")


# =========================================================================
# 6. Web API Endpoints Tests
# =========================================================================

def test_api_submit_validation(test_client):
    # Missing repo_url
    res = test_client.post("/api/github-analysis", json={})
    assert res.status_code == 400

    # Disallowed host
    res = test_client.post("/api/github-analysis", json={"repo_url": "https://attacker.com/repo"})
    assert res.status_code == 400
    assert "Only public github.com" in res.get_json()["error"]

    # Valid submission
    res = test_client.post(
        "/api/github-analysis",
        json={"repo_url": "https://github.com/pallets/flask", "base_ref": "3.1.2", "head_ref": "3.1.3"},
    )
    assert res.status_code == 202
    data = res.get_json()
    assert "job_id" in data
    assert data["status"] == "QUEUED"


def test_api_get_job_status_and_report(test_client, local_git_repo, monkeypatch):
    repo_dir, c1_sha, c2_sha = local_git_repo

    # Mock external LLM call so API test is deterministic and does not rely on external network latency
    import engine.repo_analysis.report_builder
    monkeypatch.setattr(
        engine.repo_analysis.report_builder,
        "run_ai_explanation",
        lambda *args, **kwargs: ("Fast deterministic test explanation.", True),
    )

    # Submit job with allow_local enabled in test environment
    os.environ["APP_ENV"] = "local"
    res = test_client.post(
        "/api/github-analysis",
        json={
            "repo_url": str(repo_dir),
            "base_ref": c1_sha,
            "head_ref": c2_sha,
            "allow_local": True,
        },
    )
    assert res.status_code == 202
    job_id = res.get_json()["job_id"]

    # Wait for thread execution (accommodates local git diff extraction and synthesis)
    import time
    for _ in range(40):
        stat_res = test_client.get(f"/api/github-analysis/{job_id}")
        assert stat_res.status_code == 200
        stat_data = stat_res.get_json()
        if stat_data["status"] in ("COMPLETED", "FAILED"):
            break
        time.sleep(0.5)

    assert stat_data["status"] == "COMPLETED"

    # Fetch report
    rpt_res = test_client.get(f"/api/github-analysis/{job_id}/report")
    assert rpt_res.status_code == 200
    rpt_data = rpt_res.get_json()
    assert rpt_data["total_files_changed"] >= 4

    # Fetch HTML
    html_res = test_client.get(f"/api/github-analysis/{job_id}/html")
    assert html_res.status_code == 200
    assert "SelfHeal Change Intelligence" in html_res.get_data(as_text=True)

    # Clean up test artifacts
    job_dir = get_reports_dir() / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir, onerror=remove_readonly)


def test_api_invalid_job_id_traversal(test_client):
    res = test_client.get("/api/github-analysis/..%2F..%2Fetc%2Fpasswd")
    assert res.status_code in (400, 404)


# =========================================================================
# 7. Additional Edge Case & Reliability Tests
# =========================================================================

def test_invalid_commit_sha(local_git_repo):
    repo_dir, c1_sha, _ = local_git_repo
    with pytest.raises((GitHubValidationError, GitExecutionError)):
        resolve_comparison_commits(repo_dir, base_ref="invalid_sha_000000000", head_ref=c1_sha)


def test_missing_branch_ref(local_git_repo):
    repo_dir, c1_sha, _ = local_git_repo
    with pytest.raises((GitHubValidationError, GitExecutionError)):
        resolve_comparison_commits(repo_dir, base_ref="non_existent_branch_xyz", head_ref=c1_sha)



def test_ai_unavailable_fallback(local_git_repo, monkeypatch):
    repo_dir, c1_sha, c2_sha = local_git_repo
    # Force llm_config_status to report unconfigured
    monkeypatch.setattr(
        "engine.repo_analysis.report_builder.llm_config_status",
        lambda settings: "BLOCKED_CONFIG",
    )
    req = RepoAnalysisRequest(repo_url=str(repo_dir), base_ref=c1_sha, head_ref=c2_sha)
    report = analyze_repository_commits(req, allow_local=True)
    assert report.mode == AnalysisMode.DETERMINISTIC
    assert "LLM integration is not configured" in report.ai_explanation
    # Clean up generated test report
    report_dir = get_reports_dir() / report.job_id
    if report_dir.exists():
        shutil.rmtree(report_dir, onerror=remove_readonly)


def test_large_diff_truncation(local_git_repo):
    repo_dir, c1_sha, c2_sha = local_git_repo
    # Parse with very low max_file_patch_lines to verify truncation logic
    changed_files, is_truncated = parse_raw_diff(
        repo_dir,
        base_sha=c1_sha,
        head_sha=c2_sha,
        max_total_lines=5,
        max_file_patch_lines=2,
    )
    assert is_truncated
    assert any(f.is_truncated for f in changed_files)


def test_temporary_repo_cleanup(local_git_repo):
    repo_dir, _, _ = local_git_repo
    temp_holder = TemporaryRepository(str(repo_dir), allow_local=True)
    with temp_holder as active_dir:
        assert active_dir.exists()
        captured_path = active_dir
    # Context manager exit must have safely cleaned up
    assert not captured_path.exists()


def test_concurrent_analysis_isolation(local_git_repo, monkeypatch):
    repo_dir, c1_sha, c2_sha = local_git_repo
    monkeypatch.setattr(
        "engine.repo_analysis.report_builder.run_ai_explanation",
        lambda *args, **kwargs: ("Fast deterministic test explanation.", True),
    )
    mgr = AnalysisJobManager()
    req1 = RepoAnalysisRequest(repo_url=str(repo_dir), base_ref=c1_sha, head_ref=c2_sha)
    req2 = RepoAnalysisRequest(repo_url=str(repo_dir), base_ref=c1_sha, head_ref=c2_sha)

    job1 = mgr.submit_job(req1, allow_local=True)
    job2 = mgr.submit_job(req2, allow_local=True)
    assert job1 != job2

    import time
    for _ in range(30):
        j1_stat = mgr.get_job(job1)
        j2_stat = mgr.get_job(job2)
        if j1_stat and j1_stat.get("status") == "COMPLETED" and j2_stat and j2_stat.get("status") == "COMPLETED":
            break
        time.sleep(0.3)

    assert mgr.get_job(job1)["status"] == "COMPLETED"
    assert mgr.get_job(job2)["status"] == "COMPLETED"

    # Clean up generated artifacts
    for j_id in (job1, job2):
        p = get_reports_dir() / j_id
        if p.exists():
            shutil.rmtree(p, onerror=remove_readonly)
