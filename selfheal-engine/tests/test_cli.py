"""Unit tests for Module 11: CLI, demo workflow, and recorded fallback (cli.py).

Tests:
1. Exit codes mapping for all status categories:
   - 0: PASS_NO_HEAL, PASS_AFTER_HEAL
   - 1: FAIL_FUNCTIONAL, FAIL_HEALING, FAIL_EXECUTION, FAIL_BASELINE
   - 2: BLOCKED_CONFIG, BLOCKED_AGENT
   - 3: NEEDS_REVIEW
2. Clean rejection of invalid versions and modes.
3. Protected files guard in safe_reset (intent, v1 recipe, baseline file).
4. CLI baseline, run, and reset commands.
"""

from pathlib import Path
import pytest

import cli
from engine.models import Status
from engine.recipes import get_project_root


# -------------------------------------------------------------
# 1. Exit code mapping test
# -------------------------------------------------------------

def test_status_to_exit_code_mapping():
    """Verify exact status code mappings per Module 11 specification."""
    # 0 for passes
    assert cli.status_to_exit_code(Status.PASS_NO_HEAL) == 0
    assert cli.status_to_exit_code(Status.PASS_AFTER_HEAL) == 0

    # 1 for failures
    assert cli.status_to_exit_code(Status.FAIL_FUNCTIONAL) == 1
    assert cli.status_to_exit_code(Status.FAIL_HEALING) == 1
    assert cli.status_to_exit_code(Status.FAIL_EXECUTION) == 1
    assert cli.status_to_exit_code(Status.FAIL_BASELINE) == 1

    # 2 for blocked
    assert cli.status_to_exit_code(Status.BLOCKED_CONFIG) == 2
    assert cli.status_to_exit_code(Status.BLOCKED_AGENT) == 2

    # 3 for review
    assert cli.status_to_exit_code(Status.NEEDS_REVIEW) == 3


# -------------------------------------------------------------
# 2. Rejection of invalid arguments
# -------------------------------------------------------------

def test_cli_rejects_invalid_version():
    """CLI must reject invalid version with non-zero exit code."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["run", "--version", "z"])
    assert exc.value.code != 0


def test_cli_rejects_invalid_mode():
    """CLI must reject invalid mode with non-zero exit code."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["run", "--mode", "unsupported_mode"])
    assert exc.value.code != 0


# -------------------------------------------------------------
# 3. Protected files guard in reset
# -------------------------------------------------------------

def test_safe_reset_protects_immutable_files(tmp_path, monkeypatch):
    """Safe reset must refuse to delete intent, recipe v1, or baseline inventory."""
    root = get_project_root()
    intent_path = root / "intents" / "checkout_intent.json"
    recipe_v1_path = root / "recipes" / "checkout" / "v1.json"
    baseline_path = root / "baselines" / "version_a_inventory.json"

    assert intent_path.exists(), "Intent file must exist before reset"
    assert recipe_v1_path.exists(), "Recipe v1 must exist before reset"
    assert baseline_path.exists(), "Baseline file must exist before reset"

    # Create dummy v2.json to simulate generated recipe
    dummy_v2 = root / "recipes" / "checkout" / "v2.json"
    dummy_v2.write_text('{"dummy": true}', encoding="utf-8")

    # Run safe reset
    result = cli.safe_reset(clean_runs=False)

    # Verify protected files still exist untouched
    assert intent_path.exists(), "Intent file was deleted!"
    assert recipe_v1_path.exists(), "Recipe v1 was deleted!"
    assert baseline_path.exists(), "Baseline inventory was deleted!"

    # Verify generated v2.json was cleaned up
    assert not dummy_v2.exists(), "Generated recipe v2 was not removed!"
    assert "v2.json" in result["deleted_recipes"]


# -------------------------------------------------------------
# 4. CLI command execution integration
# -------------------------------------------------------------

def test_cli_reset_command():
    """CLI reset command must return 0."""
    code = cli.main(["reset"])
    assert code == 0


def test_cli_run_version_a_baseline(make_settings, monkeypatch):
    """CLI run against Version A baseline must return 0."""
    settings, start_url = make_settings("/v/a/")
    monkeypatch.setattr(cli, "get_settings", lambda: settings)

    code = cli.main(["run", "--version", "a"])
    assert code == 0
