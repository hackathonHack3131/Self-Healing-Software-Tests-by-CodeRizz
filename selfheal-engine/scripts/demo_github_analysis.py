import os
import sys
from pathlib import Path
import shutil
import subprocess
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.repo_analysis.github_service import remove_readonly
from engine.repo_analysis.models import RepoAnalysisRequest
from engine.repo_analysis.report_builder import analyze_repository_commits, get_reports_dir


def main():
    print("================================================================")
    print("      SELFHEAL GITHUB CHANGE INTELLIGENCE DEMONSTRATION         ")
    print("================================================================\n")

    # 1. Create a real temporary Git repository with 2 commits
    temp_dir = Path(tempfile.mkdtemp(prefix="selfheal_demo_repo_"))
    print(f"Creating isolated Git repository at: {temp_dir}")

    try:
        subprocess.run(["git", "init"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Demo Engineer"], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "demo@coderizz.test"], cwd=str(temp_dir), check=True, capture_output=True)

        # Commit 1: Add a page and simple functionality
        (temp_dir / "templates").mkdir()
        (temp_dir / "templates" / "checkout.html").write_text(
            "<!DOCTYPE html>\n<html>\n<body>\n  <form action='/pay'>\n    <button id='checkout-button'>Pay Now</button>\n  </form>\n</body>\n</html>\n",
            encoding="utf-8",
        )
        (temp_dir / "pricing.py").write_text(
            "def calculate_total(subtotal: float) -> float:\n    # base calculation\n    return subtotal * 1.05\n",
            encoding="utf-8",
        )

        subprocess.run(["git", "add", "."], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Commit 1: Add checkout template and initial pricing logic"], cwd=str(temp_dir), check=True, capture_output=True)
        c1_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(temp_dir), check=True, capture_output=True, text=True).stdout.strip()
        print(f"Created Commit 1: {c1_sha[:7]} - 'Add checkout template and initial pricing logic'")

        # Commit 2: Change style / locators, alter calculation, and add test
        (temp_dir / "templates" / "checkout.html").write_text(
            "<!DOCTYPE html>\n<html>\n<head><style>.btn { color: blue; }</style></head>\n<body>\n  <form action='/pay'>\n    <button id='submit-order-button' class='btn'>Complete Order</button>\n  </form>\n</body>\n</html>\n",
            encoding="utf-8",
        )
        (temp_dir / "pricing.py").write_text(
            "def calculate_total(subtotal: float) -> float:\n    # revised pricing formula\n    total = subtotal * 1.10\n    return total\n",
            encoding="utf-8",
        )
        (temp_dir / "tests").mkdir()
        (temp_dir / "tests" / "test_pricing.py").write_text(
            "from pricing import calculate_total\n\ndef test_total():\n    assert calculate_total(100.0) == 110.0\n",
            encoding="utf-8",
        )

        subprocess.run(["git", "add", "."], cwd=str(temp_dir), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Commit 2: Redesign checkout button, update tax formula, add pricing unit test"], cwd=str(temp_dir), check=True, capture_output=True)
        c2_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(temp_dir), check=True, capture_output=True, text=True).stdout.strip()
        print(f"Created Commit 2: {c2_sha[:7]} - 'Redesign checkout button, update tax formula, add pricing unit test'\n")

        # 2. Run backend analysis engine against the two real commits
        print("Running backend analysis between Commit 1 and Commit 2...")
        req = RepoAnalysisRequest(repo_url=str(temp_dir), base_ref=c1_sha, head_ref=c2_sha)
        report = analyze_repository_commits(req, allow_local=True)

        print("\n--- ANALYSIS SUMMARY ---")
        print(f"Status           : {report.status.value}")
        print(f"Mode             : {report.mode.value}")
        print(f"Duration         : {report.duration_ms} ms")
        print(f"Base Commit      : {report.base_commit.short_sha} ({report.base_commit.message})")
        print(f"Head Commit      : {report.head_commit.short_sha} ({report.head_commit.message})")
        print(f"Files Changed    : {report.total_files_changed} (+{report.total_additions} / -{report.total_deletions})")
        print(f"Categories       : {report.categories_breakdown}")
        print(f"Risk Findings    : {len(report.findings)}")

        print("\n--- GROUNDED FINDINGS ---")
        for f in report.findings:
            print(f"- [{f.severity.value}] {f.what_changed}")
            print(f"  File   : {f.file_path} ({f.line_range})")
            print(f"  Impact : {f.potential_impact}")
            print(f"  Advice : {f.recommended_followup}\n")

        print("--- EXECUTIVE AI EXPLANATION ---")
        print(report.ai_explanation[:350] + "...\n")

        report_dir = get_reports_dir() / report.job_id
        print("--- GENERATED REPORT ARTIFACTS ---")
        print(f"HTML Report : {report_dir / 'report.html'}")
        print(f"JSON Report : {report_dir / 'report.json'}")
        print(f"Markdown    : {report_dir / 'report.md'}")
        print("================================================================")

    finally:
        shutil.rmtree(temp_dir, onerror=remove_readonly)
        print("Cleaned up temporary demonstration repository.")


if __name__ == "__main__":
    main()
