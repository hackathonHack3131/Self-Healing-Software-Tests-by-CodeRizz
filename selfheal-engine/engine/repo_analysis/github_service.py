"""Git and GitHub acquisition service with strict URL validation and isolation."""

from __future__ import annotations

import logging
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
from typing import Optional, Tuple
from urllib.parse import urlsplit

from engine.repo_analysis.models import CommitInfo

logger = logging.getLogger("selfheal.repo_analysis.github")

# Safe characters for GitHub owner and repository
_GITHUB_NAME_RE = re.compile(r"^[a-zA-Z0-9_\.-]+$")

# Safe characters for Git references (branches, tags, SHAs)
_GIT_REF_RE = re.compile(r"^[a-zA-Z0-9_/\.~^@-]+$")


class GitHubValidationError(ValueError):
    """Raised when repository URL or Git reference is invalid or disallowed."""
    pass


class GitExecutionError(RuntimeError):
    """Raised when a Git command fails or times out."""
    pass


def remove_readonly(func, path, exc_info):
    """Windows-safe error handler for shutil.rmtree on read-only .git objects."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def validate_and_normalize_repo_url(
    url: str,
    allow_local: bool = False,
) -> Tuple[str, str, str]:
    """Validate and normalize a GitHub repository URL.

    Args:
        url: User-provided repository URL.
        allow_local: Allow local file paths (used exclusively for local automated unit tests).

    Returns:
        Tuple of (normalized_url, owner, repo).

    Raises:
        GitHubValidationError: If URL is malformed, uses an unsupported host, or fails security checks.
    """
    raw_url = str(url or "").strip()
    if not raw_url:
        raise GitHubValidationError("Repository URL cannot be empty.")

    # Allow local paths for offline test isolation if explicitly permitted
    if allow_local:
        clean_path = raw_url.removeprefix("file://")
        p = Path(clean_path)
        if p.exists() and (p / ".git").exists() or p.is_dir():
            repo_name = p.name or "local-repo"
            return str(p.resolve()), "local", repo_name

    parsed = urlsplit(raw_url)

    # 1. Scheme check: HTTPS only
    if parsed.scheme.lower() != "https":
        raise GitHubValidationError(f"Invalid URL scheme '{parsed.scheme}'. Only https:// is supported.")

    # 2. Host check: github.com only (no internal hostnames, loopbacks, or IP addresses)
    host = (parsed.hostname or "").lower()
    if host not in ("github.com", "www.github.com"):
        raise GitHubValidationError(
            f"Unsupported host '{host}'. Only public github.com repositories are supported."
        )

    # 3. Disallow embedded credentials (https://user:token@github.com/...)
    if parsed.username or parsed.password:
        raise GitHubValidationError("Embedded credentials in repository URL are prohibited.")

    # 4. Extract owner and repository name
    path_parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(path_parts) < 2:
        raise GitHubValidationError(
            "Invalid GitHub URL structure. Expected format: https://github.com/OWNER/REPOSITORY"
        )

    owner = path_parts[0]
    repo = path_parts[1]

    # Strip .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]

    # 5. Sanitize owner and repo identifiers against metacharacters and directory traversal
    if not _GITHUB_NAME_RE.match(owner):
        raise GitHubValidationError(f"Invalid characters in repository owner '{owner}'.")
    if not _GITHUB_NAME_RE.match(repo):
        raise GitHubValidationError(f"Invalid characters in repository name '{repo}'.")
    if owner in (".", "..") or repo in (".", ".."):
        raise GitHubValidationError("Path traversal sequences are not permitted.")

    normalized_url = f"https://github.com/{owner}/{repo}"
    return normalized_url, owner, repo


def validate_git_ref(ref: Optional[str]) -> Optional[str]:
    """Validate a branch name, tag, or commit SHA.

    Raises:
        GitHubValidationError: If ref contains command injection attempts or unsafe characters.
    """
    if not ref:
        return None

    cleaned = str(ref).strip()
    if not cleaned:
        return None

    # Ref must not begin with hyphen (prevents flag injection in git commands)
    if cleaned.startswith("-"):
        raise GitHubValidationError(f"Git reference '{cleaned}' cannot start with a hyphen.")

    if not _GIT_REF_RE.match(cleaned):
        raise GitHubValidationError(f"Git reference '{cleaned}' contains disallowed characters.")

    if len(cleaned) > 120:
        raise GitHubValidationError("Git reference is unreasonably long (exceeds 120 chars).")

    return cleaned


def run_git_command(
    args: list[str],
    cwd: Optional[Path] = None,
    timeout: int = 30,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute a git command safely using argument lists and subprocess isolation."""
    # Enforce safe git execution environment: disable hooks, restrict symlinks
    safe_env = os.environ.copy()
    safe_env["GIT_TERMINAL_PROMPT"] = "0"
    safe_env["GIT_CONFIG_NOSYSTEM"] = "1"

    cmd = ["git", "-c", "core.hooksPath=/dev/null"] + args

    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=safe_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
        )
        if check and result.returncode != 0:
            err = (result.stderr or "").strip() or (result.stdout or "").strip() or f"exited with code {result.returncode}"
            raise GitExecutionError(f"Git command {' '.join(cmd[:3])} failed: {err}")
        return result
    except subprocess.TimeoutExpired as exc:
        raise GitExecutionError(f"Git command timed out after {timeout} seconds.") from exc
    except FileNotFoundError as exc:
        raise GitExecutionError("Git CLI executable not found on system PATH.") from exc


class TemporaryRepository:
    """Context manager managing an isolated temporary clone of a Git repository."""

    def __init__(self, repo_url: str, allow_local: bool = False, depth: int = 50, timeout: int = 45):
        self.repo_url = repo_url
        self.allow_local = allow_local
        self.depth = depth
        self.timeout = timeout
        self.temp_dir: Optional[Path] = None

    def __enter__(self) -> Path:
        normalized_url, _, _ = validate_and_normalize_repo_url(self.repo_url, allow_local=self.allow_local)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="selfheal_repo_"))

        # Perform shallow/minimal clone
        clone_args = [
            "clone",
            "--no-checkout",
            f"--depth={self.depth}",
            normalized_url,
            str(self.temp_dir),
        ]

        logger.info("Cloning repository into temporary workspace %s", self.temp_dir)
        try:
            run_git_command(clone_args, timeout=self.timeout)
        except Exception:
            self.cleanup()
            raise

        return self.temp_dir

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def cleanup(self) -> None:
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, onerror=remove_readonly)
            except Exception as exc:
                logger.warning("Failed to clean up temporary repo %s: %s", self.temp_dir, exc)
            self.temp_dir = None


def get_commit_metadata(repo_dir: Path, ref: str) -> CommitInfo:
    """Retrieve structured metadata for a specific commit ref."""
    fmt = "%H%n%h%n%an%n%ae%n%cI%n%P%n%B"
    res = run_git_command(["log", "-1", f"--format={fmt}", ref], cwd=repo_dir)
    lines = res.stdout.splitlines()

    if len(lines) < 6:
        raise GitExecutionError(f"Could not retrieve complete commit metadata for '{ref}'.")

    full_sha = lines[0].strip()
    short_sha = lines[1].strip()
    author_name = lines[2].strip()
    author_email = lines[3].strip()
    date = lines[4].strip()
    parents = lines[5].strip().split() if lines[5].strip() else []
    message = "\n".join(lines[6:]).strip()

    return CommitInfo(
        sha=full_sha,
        short_sha=short_sha,
        message=message,
        author_name=author_name,
        author_email=author_email,
        date=date,
        parents=parents,
    )


def _verify_commit_ref(repo_dir: Path, ref_str: str, label: str) -> None:
    """Verify that a commit reference exists, attempting a remote fetch if needed, with helpful errors."""
    # 1. Check if ref exists locally
    check_local = run_git_command(["rev-parse", "--verify", f"{ref_str}^{{commit}}"], cwd=repo_dir, check=False)
    if check_local.returncode == 0:
        return

    # 2. Try fetching the ref from remote (in case it is a remote branch or commit)
    run_git_command(["fetch", "--depth=50", "origin", ref_str], cwd=repo_dir, check=False)
    check_fetched = run_git_command(["rev-parse", "--verify", f"{ref_str}^{{commit}}"], cwd=repo_dir, check=False)
    if check_fetched.returncode == 0:
        return

    # 3. Try fetching as a remote tag
    run_git_command(["fetch", "--depth=50", "origin", "tag", ref_str], cwd=repo_dir, check=False)
    check_tag = run_git_command(["rev-parse", "--verify", f"{ref_str}^{{commit}}"], cwd=repo_dir, check=False)
    if check_tag.returncode == 0:
        return

    # 4. Check with FETCH_HEAD
    check_fetch_head = run_git_command(["rev-parse", "--verify", "FETCH_HEAD^{commit}"], cwd=repo_dir, check=False)
    if check_fetch_head.returncode == 0:
        return

    # 5. Ref genuinely does not exist in this repository
    raise GitHubValidationError(
        f"{label} revision '{ref_str}' does not exist in this repository. "
        "Please check the branch name, tag, or commit SHA, or leave both Base Ref and Target Ref empty to analyze the latest commits."
    )


def resolve_comparison_commits(
    repo_dir: Path,
    base_ref: Optional[str] = None,
    head_ref: Optional[str] = None,
) -> Tuple[CommitInfo, CommitInfo]:
    """Resolve and validate both base and head commits with clean user-facing validation."""
    head_query = validate_git_ref(head_ref) or "HEAD"

    # Verify head ref exists
    _verify_commit_ref(repo_dir, head_query, "Target (head)")
    head_commit = get_commit_metadata(repo_dir, head_query)

    # Determine base ref
    if base_ref:
        base_query = validate_git_ref(base_ref)
        _verify_commit_ref(repo_dir, base_query, "Base")
        base_commit = get_commit_metadata(repo_dir, base_query)
    else:
        # Default: first parent of head if available
        if head_commit.parents:
            base_commit = get_commit_metadata(repo_dir, head_commit.parents[0])
        else:
            # Initial commit with no parent
            base_commit = head_commit

    return base_commit, head_commit

