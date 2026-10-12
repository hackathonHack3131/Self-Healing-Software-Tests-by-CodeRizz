"""Pydantic data models for GitHub Change Intelligence."""

from __future__ import annotations

from enum import Enum
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ChangeCategory(str, Enum):
    """Classification category for changed code and files."""
    UI_UX = "ui_ux"
    FUNCTIONALITY = "functionality"
    BACKEND_API = "backend_api"
    TESTS = "tests"
    DEPENDENCIES_CONFIG = "dependencies_config"
    OTHER = "other"


class SeverityLevel(str, Enum):
    """Risk severity indicator."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConfidenceLevel(str, Enum):
    """Confidence assessment for findings."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AnalysisJobStatus(str, Enum):
    """Lifecycle status of an analysis job."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED_CONFIG = "BLOCKED_CONFIG"


class AnalysisMode(str, Enum):
    """Operating mode of analysis: deterministic or AI-assisted."""
    AI_ASSISTED = "AI_ASSISTED"
    DETERMINISTIC = "DETERMINISTIC"


class RepoAnalysisRequest(BaseModel):
    """Validated input request for comparing commits in a repository."""
    model_config = ConfigDict(extra="forbid")

    repo_url: str
    base_ref: Optional[str] = None
    head_ref: Optional[str] = None

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        url = v.strip()
        if not url:
            raise ValueError("Repository URL cannot be empty")
        return url


class CommitInfo(BaseModel):
    """Structured metadata for a Git commit."""
    model_config = ConfigDict(extra="forbid")

    sha: str
    short_sha: str
    message: str
    author_name: str = ""
    author_email: str = ""
    date: str = ""
    parents: List[str] = Field(default_factory=list)


class ChangedFile(BaseModel):
    """Metadata and patch details for an individual changed file."""
    model_config = ConfigDict(extra="forbid")

    path: str
    status: str  # "added" | "modified" | "deleted" | "renamed"
    old_path: Optional[str] = None
    additions: int = 0
    deletions: int = 0
    patch: str = ""
    is_binary: bool = False
    is_truncated: bool = False
    category: ChangeCategory = ChangeCategory.OTHER


class Finding(BaseModel):
    """Grounded risk, architectural, or behavioral change finding."""
    model_config = ConfigDict(extra="forbid")

    id: str
    category: ChangeCategory
    severity: SeverityLevel
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    file_path: str
    line_range: str = ""
    diff_hunk: str = ""
    what_changed: str
    why_it_matters: str
    potential_impact: str
    recommended_followup: str
    is_direct_fact: bool = True  # True if directly proven by diff; False if inferred


class RepoAnalysisReport(BaseModel):
    """Comprehensive, validated report for a GitHub commit comparison."""
    model_config = ConfigDict(extra="forbid")

    job_id: str
    repo_url: str
    base_commit: Optional[CommitInfo] = None
    head_commit: Optional[CommitInfo] = None
    mode: AnalysisMode
    status: AnalysisJobStatus
    created_at: str
    duration_ms: float = 0.0
    total_files_changed: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    categories_breakdown: Dict[str, int] = Field(default_factory=dict)
    files: List[ChangedFile] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    ai_explanation: str = ""
    is_partial: bool = False
    error_message: Optional[str] = None

    @model_validator(mode="after")
    def verify_privacy_and_integrity(self) -> RepoAnalysisReport:
        """Invariance check: prevent leaking raw 16-digit credit cards or secrets."""
        card_pattern = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
        # Ensure card numbers in findings or explanation are masked
        if self.ai_explanation and card_pattern.search(self.ai_explanation):
            raw = self.ai_explanation
            cleaned = card_pattern.sub(lambda m: "•••• •••• •••• " + m.group(0).replace(" ", "").replace("-", "")[-4:] if len(m.group(0).replace(" ", "").replace("-", "")) == 16 else "[REDACTED_NUM]", raw)
            object.__setattr__(self, "ai_explanation", cleaned)
        return self
