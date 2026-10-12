"""Deterministic Git diff analyzer and grounded change classifier."""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

from engine.repo_analysis.github_service import run_git_command
from engine.repo_analysis.models import (
    ChangeCategory,
    ChangedFile,
    ConfidenceLevel,
    Finding,
    SeverityLevel,
)

logger = logging.getLogger("selfheal.repo_analysis.analyzer")

# Patterns for secret redaction in diffs and commit messages
_SECRET_PATTERNS = [
    (re.compile(r"(?i)(api[_-]?key|secret|token|password|auth[_-]?key)\s*[:=]\s*['\"]([^'\"]{6,})['\"]"), r"\1='[REDACTED_SECRET]'"),
    (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "[REDACTED_GOOGLE_KEY]"),
    (re.compile(r"ghp_[0-9A-Za-z]{36}"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----.*?-----END [A-Z ]+ PRIVATE KEY-----", re.DOTALL), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), lambda m: "•••• •••• •••• " + m.group(0).replace(" ", "").replace("-", "")[-4:] if len(m.group(0).replace(" ", "").replace("-", "")) == 16 else "[REDACTED_CARD]"),
]


def redact_text(text: str) -> str:
    """Safely redact credentials, API keys, and full payment cards from text."""
    if not text:
        return ""
    res = text
    for pattern, repl in _SECRET_PATTERNS:
        if callable(repl):
            res = pattern.sub(repl, res)
        else:
            res = pattern.sub(repl, res)
    return res


def categorize_file(path: str) -> ChangeCategory:
    """Classify a file into one of the standard change categories based on path and extension."""
    norm = path.lower().replace("\\", "/")
    filename = norm.split("/")[-1]

    # 1. Tests
    if (
        "/tests/" in norm
        or "/test/" in norm
        or "/spec/" in norm
        or filename.startswith("test_")
        or filename.endswith("_test.py")
        or filename.endswith(".spec.js")
        or filename.endswith(".test.js")
        or filename.endswith(".spec.ts")
        or filename.endswith(".test.ts")
    ):
        return ChangeCategory.TESTS

    # 2. UI / UX
    ui_exts = (".html", ".htm", ".jinja", ".jinja2", ".j2", ".css", ".scss", ".sass", ".less", ".vue", ".jsx", ".tsx", ".svg")
    ui_paths = ("/templates/", "/static/", "/styles/", "/components/", "/views/", "/ui/", "/assets/")
    if filename.endswith(ui_exts) or any(p in norm for p in ui_paths):
        return ChangeCategory.UI_UX

    # 3. Dependencies and Configuration
    dep_filenames = {
        "requirements.txt",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env.example",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "pytest.ini",
        ".gitignore",
    }
    if filename in dep_filenames or "/.github/" in norm or "/migrations/" in norm:
        return ChangeCategory.DEPENDENCIES_CONFIG

    # 4. Backend / API
    backend_indicators = (
        "routes",
        "server.py",
        "api.py",
        "endpoints",
        "controller",
        "models.py",
        "database.py",
        "db.py",
        "schema.py",
        "views.py",
    )
    if any(ind in norm for ind in backend_indicators) or "/api/" in norm or "/backend/" in norm:
        return ChangeCategory.BACKEND_API

    # 5. Core Functionality (code files)
    code_exts = (".py", ".js", ".ts", ".go", ".java", ".rb", ".rs", ".php", ".c", ".cpp")
    if filename.endswith(code_exts):
        return ChangeCategory.FUNCTIONALITY

    return ChangeCategory.OTHER


def parse_raw_diff(
    repo_dir: Path,
    base_sha: str,
    head_sha: str,
    max_total_lines: int = 5000,
    max_file_patch_lines: int = 600,
) -> Tuple[List[ChangedFile], bool]:
    """Extract and parse changed files and patches between two commits."""
    # 1. Query numstat: additions, deletions, path
    numstat_res = run_git_command(["diff", "-M", "--numstat", base_sha, head_sha], cwd=repo_dir)
    file_stats: Dict[str, Tuple[int, int, bool]] = {}

    for line in (numstat_res.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(maxsplit=2)
        if len(parts) < 3:
            continue
        adds_str, dels_str, file_path = parts
        is_bin = (adds_str == "-" and dels_str == "-")
        adds = int(adds_str) if not is_bin else 0
        dels = int(dels_str) if not is_bin else 0
        file_stats[file_path] = (adds, dels, is_bin)

    # 2. Query name-status to detect added/deleted/renamed
    status_res = run_git_command(["diff", "-M", "--name-status", base_sha, head_sha], cwd=repo_dir)
    file_statuses: Dict[str, Tuple[str, Optional[str]]] = {}

    for line in (status_res.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        cols = line.split("\t")
        st_code = cols[0][0].upper()
        if st_code == "A":
            file_statuses[cols[1]] = ("added", None)
        elif st_code == "D":
            file_statuses[cols[1]] = ("deleted", None)
        elif st_code == "R":
            old_p = cols[1]
            new_p = cols[2] if len(cols) > 2 else old_p
            file_statuses[new_p] = ("renamed", old_p)
        else:
            target_path = cols[1] if len(cols) > 1 else ""
            if target_path:
                file_statuses[target_path] = ("modified", None)

    # 3. Query actual patch
    patch_res = run_git_command(["diff", "-M", "--patch", "-U3", base_sha, head_sha], cwd=repo_dir)
    raw_patches = patch_res.stdout or ""

    # Split patch by file diff headers
    diff_hunks_by_file: Dict[str, str] = {}
    current_file: Optional[str] = None
    current_hunk_lines: List[str] = []

    for line in raw_patches.splitlines():
        if line.startswith("diff --git "):
            if current_file and current_hunk_lines:
                diff_hunks_by_file[current_file] = "\n".join(current_hunk_lines)
            current_hunk_lines = [line]
            match = re.search(r"b/(.+)$", line)
            current_file = match.group(1) if match else None
        else:
            if current_file:
                current_hunk_lines.append(line)

    if current_file and current_hunk_lines:
        diff_hunks_by_file[current_file] = "\n".join(current_hunk_lines)

    # Assemble ChangedFile list
    changed_files: List[ChangedFile] = []
    total_lines_accumulated = 0
    is_overall_truncated = False

    # Collect all known file paths
    all_paths = list(file_statuses.keys())
    for p in file_stats.keys():
        if p not in all_paths and "=>" not in p:
            all_paths.append(p)

    for path in all_paths:
        status, old_path = file_statuses.get(path, ("modified", None))
        adds, dels, is_bin = file_stats.get(path, (0, 0, False))

        raw_patch = diff_hunks_by_file.get(path, "")
        patch_lines = raw_patch.splitlines()

        is_file_truncated = False
        if len(patch_lines) > max_file_patch_lines:
            patch_lines = patch_lines[:max_file_patch_lines]
            patch_lines.append(f"... [Truncated: diff for {path} exceeds {max_file_patch_lines} lines]")
            is_file_truncated = True

        total_lines_accumulated += len(patch_lines)
        if total_lines_accumulated > max_total_lines:
            is_overall_truncated = True

        sanitized_patch = redact_text("\n".join(patch_lines))
        category = categorize_file(path)

        changed_files.append(
            ChangedFile(
                path=path,
                status=status,
                old_path=old_path,
                additions=adds,
                deletions=dels,
                patch=sanitized_patch,
                is_binary=is_bin,
                is_truncated=is_file_truncated,
                category=category,
            )
        )

    return changed_files, is_overall_truncated


def generate_grounded_findings(files: List[ChangedFile]) -> List[Finding]:
    """Perform deterministic analysis of code changes to produce grounded findings."""
    findings: List[Finding] = []
    finding_counter = 1

    for f in files:
        if f.is_binary or not f.patch:
            continue

        lines = f.patch.splitlines()
        for idx, line in enumerate(lines):
            # 1. Detection: Removed assertions or validation
            if (
                line.startswith("-")
                and not line.startswith("---")
                and ("assert " in line or "raise " in line or "validate_" in line or "abort(4" in line)
            ):
                hunk = "\n".join(lines[max(0, idx - 2): min(len(lines), idx + 3)])
                findings.append(
                    Finding(
                        id=f"FIND-{finding_counter:03d}",
                        category=f.category,
                        severity=SeverityLevel.HIGH,
                        confidence=ConfidenceLevel.HIGH,
                        file_path=f.path,
                        line_range=f"Near patch line {idx + 1}",
                        diff_hunk=hunk,
                        what_changed=f"Removed validation or assertion statement: `{line[1:].strip()}`",
                        why_it_matters="Removing validation constraints or assertions may permit invalid inputs or bypass domain safety rules.",
                        potential_impact="Potential regression: this change may bypass validation or suppress error detection.",
                        recommended_followup=f"Verify if validation in `{f.path}` was intentionally relaxed or relocated to a different handler.",
                        is_direct_fact=True,
                    )
                )
                finding_counter += 1

            # 2. Detection: Authentication & access control changes
            if (
                line.startswith("-")
                and not line.startswith("---")
                and any(kw in line.lower() for kw in ("@login_required", "check_permission", "is_authenticated", "current_user", "verify_token"))
            ):
                hunk = "\n".join(lines[max(0, idx - 2): min(len(lines), idx + 3)])
                findings.append(
                    Finding(
                        id=f"FIND-{finding_counter:03d}",
                        category=ChangeCategory.BACKEND_API,
                        severity=SeverityLevel.CRITICAL,
                        confidence=ConfidenceLevel.HIGH,
                        file_path=f.path,
                        line_range=f"Near patch line {idx + 1}",
                        diff_hunk=hunk,
                        what_changed=f"Modified or removed authorization check: `{line[1:].strip()}`",
                        why_it_matters="Authorization decorators and permission checks prevent unauthorized access to sensitive endpoints.",
                        potential_impact="Security vulnerability: unauthenticated or unauthorized users may gain access to this route.",
                        recommended_followup="Audit endpoint authorization requirements and execute access-control tests.",
                        is_direct_fact=True,
                    )
                )
                finding_counter += 1

            # 3. Detection: UI / Form & E2E Locators Drift
            if f.category == ChangeCategory.UI_UX and (
                line.startswith("+") or line.startswith("-")
            ) and not line.startswith("+++") and not line.startswith("---"):
                if any(tag in line for tag in ("<button", "<input", "<form", "id=", "name=", "class=", "data-testid=")):
                    # Only record one locator drift finding per UI file to avoid clutter
                    if not any(fd.file_path == f.path and "UI locator or form control" in fd.what_changed for fd in findings):
                        hunk = "\n".join(lines[max(0, idx - 2): min(len(lines), idx + 3)])
                        findings.append(
                            Finding(
                                id=f"FIND-{finding_counter:03d}",
                                category=ChangeCategory.UI_UX,
                                severity=SeverityLevel.MEDIUM,
                                confidence=ConfidenceLevel.HIGH,
                                file_path=f.path,
                                line_range=f"Near patch line {idx + 1}",
                                diff_hunk=hunk,
                                what_changed=f"UI locator or form control changed in template: `{line[1:].strip()[:80]}`",
                                why_it_matters="Altering form field names, IDs, button labels, or element hierarchy causes traditional E2E tests to fail.",
                                potential_impact="Existing end-to-end test recipes targeting this interface will break due to locator mismatch (UI drift).",
                                recommended_followup="Trigger autonomous SelfHeal recipe rebuild or update automated test locators.",
                                is_direct_fact=True,
                            )
                        )
                        finding_counter += 1

            # 4. Detection: Modified financial or business calculations
            if (
                line.startswith("+") or line.startswith("-")
            ) and not line.startswith("+++") and not line.startswith("---") and (
                "total" in line.lower() or "price" in line.lower() or "tax" in line.lower() or "discount" in line.lower()
            ) and any(op in line for op in ("*", "/", "+", "-")):
                if not any(fd.file_path == f.path and "Calculation logic modified" in fd.what_changed for fd in findings):
                    hunk = "\n".join(lines[max(0, idx - 2): min(len(lines), idx + 3)])
                    findings.append(
                        Finding(
                            id=f"FIND-{finding_counter:03d}",
                            category=ChangeCategory.FUNCTIONALITY,
                            severity=SeverityLevel.HIGH,
                            confidence=ConfidenceLevel.HIGH,
                            file_path=f.path,
                            line_range=f"Near patch line {idx + 1}",
                            diff_hunk=hunk,
                            what_changed=f"Calculation logic modified: `{line[1:].strip()[:80]}`",
                            why_it_matters="Financial, tax, or totals calculations are business invariants that must remain strictly deterministic.",
                            potential_impact="Risk of calculation invariant violation (e.g. incorrect order total, unexpected tax calculation).",
                            recommended_followup="Verify financial calculation with automated invariant regression tests.",
                            is_direct_fact=True,
                        )
                    )
                    finding_counter += 1

        # 5. Detection: Deleted tests
        if f.category == ChangeCategory.TESTS and f.status == "deleted":
            findings.append(
                Finding(
                    id=f"FIND-{finding_counter:03d}",
                    category=ChangeCategory.TESTS,
                    severity=SeverityLevel.HIGH,
                    confidence=ConfidenceLevel.HIGH,
                    file_path=f.path,
                    line_range="Entire file",
                    diff_hunk="",
                    what_changed=f"Test file deleted: `{f.path}`",
                    why_it_matters="Deleting automated tests reduces regression coverage and may hide existing defects.",
                    potential_impact="Decreased test coverage; regressions in covered components will not be caught.",
                    recommended_followup=f"Review why `{f.path}` was removed and ensure relevant coverage is maintained.",
                    is_direct_fact=True,
                )
            )
            finding_counter += 1

        # 6. Detection: Dependency manifest additions/removals
        if f.category == ChangeCategory.DEPENDENCIES_CONFIG and ("requirements.txt" in f.path or "package.json" in f.path):
            findings.append(
                Finding(
                    id=f"FIND-{finding_counter:03d}",
                    category=ChangeCategory.DEPENDENCIES_CONFIG,
                    severity=SeverityLevel.MEDIUM,
                    confidence=ConfidenceLevel.HIGH,
                    file_path=f.path,
                    line_range="Manifest diff",
                    diff_hunk=f.patch[:400] if f.patch else "",
                    what_changed=f"Project dependency manifest modified in `{f.path}` (+{f.additions}/-{f.deletions})",
                    why_it_matters="Dependency changes can introduce supply-chain vulnerabilities, breaking transitive changes, or environment mismatches.",
                    potential_impact="Possible runtime behavior changes or security vulnerabilities from updated third-party packages.",
                    recommended_followup=f"Run dependency vulnerability scans and smoke tests on the updated dependencies.",
                    is_direct_fact=True,
                )
            )
            finding_counter += 1

    return findings
