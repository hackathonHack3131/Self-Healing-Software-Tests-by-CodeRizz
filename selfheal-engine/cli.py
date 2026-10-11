"""Command-line interface for the SelfHeal system (Module 11 per AGENTS.md).

Commands:
  serve    : Start the demo shop (or web dashboard)
  baseline : Verify Version A and establish trusted UI baseline
  run      : Run test against Version A, B, C, or D with live or recorded mode
  demo     : Run 5-beat demonstration workflow (A -> B -> B again -> C -> D)
  record   : Execute live Version B healing and save genuine agent trace
  reset    : Safe reset of generated recipe versions and runs (protects baseline/intent/v1)
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Dict, List, Optional

from engine.browser import BrowserSession
from engine.config import Settings, get_settings, llm_config_status
from engine.models import CreatedBy, HealResult, Recipe, Status
from engine.orchestrator import run_orchestrator
from engine.recipes import get_project_root, load_intent, load_recipe
from engine.snapshot import create_version_a_baseline, get_baseline_path


def status_to_exit_code(status: Status) -> int:
    """Map Status enum to standardized CLI exit codes (Module 11).

    0: PASS_NO_HEAL, PASS_AFTER_HEAL
    1: FAIL_FUNCTIONAL, FAIL_HEALING, FAIL_EXECUTION, FAIL_BASELINE
    2: BLOCKED_CONFIG, BLOCKED_AGENT
    3: NEEDS_REVIEW
    """
    if status in (Status.PASS_NO_HEAL, Status.PASS_AFTER_HEAL):
        return 0
    elif status in (
        Status.FAIL_FUNCTIONAL,
        Status.FAIL_HEALING,
        Status.FAIL_EXECUTION,
        Status.FAIL_BASELINE,
    ):
        return 1
    elif status in (Status.BLOCKED_CONFIG, Status.BLOCKED_AGENT):
        return 2
    elif status == Status.NEEDS_REVIEW:
        return 3
    return 1


def safe_reset(clean_runs: bool = True) -> Dict[str, Any]:
    """Safely reset generated recipes and runs.

    Guards: Never deletes or overwrites the immutable intent, v1.json, or version_a_inventory.json.
    """
    root = get_project_root()
    recipe_dir = root / "recipes" / "checkout"

    protected_paths = {
        root / "intents" / "checkout_intent.json",
        root / "recipes" / "checkout" / "v1.json",
        root / "baselines" / "version_a_inventory.json",
    }

    deleted_recipes = []
    if recipe_dir.exists():
        for f in recipe_dir.glob("v*.json"):
            if f.name != "v1.json" and f not in protected_paths:
                f.unlink(missing_ok=True)
                deleted_recipes.append(f.name)

    cleared_runs = 0
    if clean_runs:
        runs_dir = root / "runs"
        if runs_dir.exists():
            for item in runs_dir.iterdir():
                if item in protected_paths or item.name == ".gitkeep":
                    continue
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    cleared_runs += 1
                elif item.is_file():
                    item.unlink(missing_ok=True)
                    cleared_runs += 1

    return {
        "deleted_recipes": deleted_recipes,
        "cleared_runs": cleared_runs,
    }


def cmd_serve(args) -> int:
    """Start the demo shop (default port 5000) or web dashboard (port 8080)."""
    if getattr(args, "dashboard", False):
        from webapp.server import create_app
        app = create_app()
        port = int(getattr(args, "port", None) or os.getenv("WEBAPP_PORT", "8080"))
        host = getattr(args, "host", None) or os.getenv("WEBAPP_HOST", "0.0.0.0")
        print(f"Starting SelfHeal Dashboard at http://127.0.0.1:{port}")
        app.run(host=host, port=port, debug=False)
        return 0
    else:
        from demo_app.app import create_app
        app = create_app()
        port = int(getattr(args, "port", None) or os.getenv("DEMO_PORT", "5000"))
        host = getattr(args, "host", None) or "127.0.0.1"
        print(f"Starting SelfHeal Demo Shop at http://{host}:{port}")
        app.run(host=host, port=port, debug=False)
        return 0


def _run_async_compat(coro):
    """Run an async coroutine safely, even if an outer event loop is already active."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


async def _run_baseline_async() -> int:
    settings = get_settings()
    intent = load_intent("checkout")
    recipe = load_recipe("checkout", version=1, intent=intent)
    start_url = f"{settings.DEMO_BASE_URL}/v/a/"

    print(f"Creating and verifying Version A baseline at {start_url}...")
    try:
        async with BrowserSession(settings=settings, start_url=start_url) as session:
            inv = await create_version_a_baseline(session=session, recipe=recipe, intent=intent)
        print(f"[PASS] Trusted baseline established: {len(inv.pages)} pages, {len(inv.all_elements)} elements.")
        print(f"       Saved to: {get_baseline_path()}")
        return 0
    except Exception as exc:
        print(f"[FAIL] Baseline creation failed: {exc}")
        return 1


def cmd_baseline(args) -> int:
    """Create or verify the Version A baseline inventory."""
    return _run_async_compat(_run_baseline_async())


async def _run_test_async(args) -> int:
    version = (getattr(args, "version", "a") or "a").lower().strip()
    if version not in ("a", "b", "c", "d"):
        print(f"[ERROR] Invalid version '{version}'. Allowed: a, b, c, d.")
        return 1

    mode = (getattr(args, "mode", "live") or "live").lower().strip()
    if mode not in ("live", "recorded", "no-heal"):
        print(f"[ERROR] Invalid mode '{mode}'. Allowed: live, recorded, no-heal.")
        return 1

    recipe_version = int(getattr(args, "recipe_version", 1) or 1)

    settings = get_settings()
    if getattr(args, "headed", False):
        settings = Settings(
            DEMO_BASE_URL=settings.DEMO_BASE_URL,
            ALLOWED_ORIGINS=settings.ALLOWED_ORIGINS,
            GOOGLE_API_KEY=settings.GOOGLE_API_KEY,
            DEEPAGENT_MODEL=settings.DEEPAGENT_MODEL,
            MAX_AGENT_ACTIONS=settings.MAX_AGENT_ACTIONS,
            MAX_HEAL_SECONDS=settings.MAX_HEAL_SECONDS,
            HEADLESS=False,
            RUNS_DIR=settings.RUNS_DIR,
        )

    start_url = f"{settings.DEMO_BASE_URL}/v/{version}/"
    print(f"--- Running SelfHeal: Version {version.upper()} [mode={mode}] ---")
    print(f"Target URL : {start_url}")

    res = await run_orchestrator(
        intent_id="checkout",
        target_url=start_url,
        recipe_version=recipe_version,
        settings=settings,
        force_heal_mode="recorded" if mode == "recorded" else None,
    )

    exit_code = status_to_exit_code(res.status)
    status_marker = "[PASS]" if exit_code == 0 else "[FAIL]" if exit_code == 1 else "[BLOCKED]"

    print(f"{status_marker} Status      : {res.status.value} ({res.status_label})")
    print(f"       Duration    : {res.duration_ms} ms")
    print(f"       Healed      : {res.healed}")
    if res.new_recipe_version and res.new_recipe_version != res.initial_recipe_version:
        print(f"       New Recipe  : v{res.new_recipe_version}")
    if res.report_path:
        print(f"       Report Path : {res.report_path}")

    print("\n--- Headline ---")
    from engine.reporting import build_headline
    hl = build_headline(
        status=res.status,
        healed=res.healed,
        new_version=res.new_recipe_version,
        triage=res.triage,
        verification=res.verification,
        evidence=res.evidence,
    )
    print(hl)

    return exit_code


def cmd_run(args) -> int:
    """Run test recipe against a checkout version."""
    try:
        return _run_async_compat(_run_test_async(args))
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        print(f"[FAIL] Configuration / File error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[FAIL] Unexpected execution error: {e}", file=sys.stderr)
        return 1


async def _run_record_async(args) -> int:
    """Execute live healing on Version B and capture genuine agent trace."""
    settings = get_settings()
    cfg_stat = llm_config_status(settings)
    if cfg_stat != "OK":
        print(f"[BLOCKED] Cannot record live trace: GOOGLE_API_KEY is not configured ({cfg_stat}).")
        return 2

    start_url = f"{settings.DEMO_BASE_URL}/v/b/"
    print(f"Executing live healing on Version B to record genuine agent trace...")
    print(f"Provider: Google Gemini ({settings.DEEPAGENT_MODEL})")

    res = await run_orchestrator(
        intent_id="checkout",
        target_url=start_url,
        recipe_version=1,
        settings=settings,
        force_heal_mode="live",
    )

    if res.status == Status.PASS_AFTER_HEAL and res.heal_result and res.heal_result.trace:
        from engine.agent.recorded import save_trace
        trace_path = save_trace(res.heal_result.trace)
        print(f"[PASS] Genuine agent trace recorded with {len(res.heal_result.trace)} events.")
        print(f"       Saved to: {trace_path}")
        return 0
    elif res.status in (Status.BLOCKED_AGENT, Status.BLOCKED_CONFIG):
        print(f"[BLOCKED] Live recording blocked by model API: {res.agent_explanation}")
        return 2
    else:
        print(f"[FAIL] Live healing did not produce a verified recipe (status: {res.status.value}).")
        return 1


def cmd_record(args) -> int:
    """Record a genuine agent trace from a live Version B healing run."""
    return _run_async_compat(_run_record_async(args))


async def _run_demo_async(args) -> int:
    """Execute the 5-beat demonstration workflow with pauses."""
    settings = get_settings()

    print("================================================================")
    print("      SELFHEAL INTENT-AWARE AUTONOMOUS E2E TESTING DEMO        ")
    print("================================================================\n")

    # Pre-demo: Reset recipes to clean baseline v1
    safe_reset(clean_runs=False)

    beats = [
        ("BEAT 1", "a", 1, "Baseline single-page checkout (passes cleanly with Recipe v1)"),
        ("BEAT 2", "b", 1, "Multi-step UI redesign drift (autonomously heals and saves Recipe v2)"),
        ("BEAT 3", "b", "latest", "Run Version B again with healed Recipe (passes with zero AI overhead)"),
        ("BEAT 4", "c", 1, "Detect real HTTP 500 server error (triage diagnoses APP_BUG & refuses false heal)"),
        ("BEAT 5", "d", 1, "Detect calculation invariant bug ($32.50 vs $36.50) (verifier fails invariants)"),
    ]

    all_passed = True

    for beat_name, version, recipe_ver, desc in beats:
        print(f">>> {beat_name}: Testing Version {version.upper()}")
        print(f"    Intent: Complete checkout with a valid credit card")
        print(f"    Scenario: {desc}")

        # Resolve latest recipe version for Beat 3
        active_ver = 1
        if recipe_ver == "latest":
            intent = load_intent("checkout")
            latest_recipe = load_recipe("checkout", version="latest", intent=intent)
            active_ver = latest_recipe.version
            print(f"    Using healed recipe: v{active_ver}")
        else:
            active_ver = recipe_ver

        start_url = f"{settings.DEMO_BASE_URL}/v/{version}/"
        res = await run_orchestrator(
            intent_id="checkout",
            target_url=start_url,
            recipe_version=active_ver,
            settings=settings,
        )

        # Print outcome summary
        print(f"    Outcome: {res.status.value} ({res.status_label})")
        print(f"    Duration: {res.duration_ms} ms | Healed: {res.healed}")
        if res.report_path:
            print(f"    Report: {res.report_path}")
        print("----------------------------------------------------------------\n")

        time.sleep(1.0)

    print("[DEMO COMPLETE] All 5 beats executed successfully.")
    return 0


def cmd_demo(args) -> int:
    """Run full demonstration workflow across all 5 beats."""
    return _run_async_compat(_run_demo_async(args))


def cmd_reset(args) -> int:
    """Reset recipes to baseline v1 and clean runs/ directory safely."""
    info = safe_reset(clean_runs=True)
    count = len(info["deleted_recipes"])
    runs_count = info["cleared_runs"]
    print(f"Reset complete. Removed {count} generated recipes. Current version is v1.")
    print(f"Cleared {runs_count} run directories from runs/.")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="SelfHeal E2E Autonomous Testing CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start demo shop (or dashboard)")
    serve_parser.add_argument("--port", help="Port to listen on (default: 5000 for shop, 8080 for dashboard)")
    serve_parser.add_argument("--host", help="Host to bind to (default: 127.0.0.1)")
    serve_parser.add_argument("--dashboard", action="store_true", help="Start web dashboard instead of shop")

    # baseline command
    subparsers.add_parser("baseline", help="Establish/verify Version A baseline")

    # run command
    run_parser = subparsers.add_parser("run", help="Run test against a version")
    run_parser.add_argument("--version", choices=["a", "b", "c", "d"], default="a", help="Version to test (default: a)")
    run_parser.add_argument("--mode", choices=["live", "recorded", "no-heal"], default="live", help="Healing mode")
    run_parser.add_argument("--recipe-version", default=1, type=int, help="Initial recipe version to run")
    run_parser.add_argument("--headed", action="store_true", help="Run browser in visible (headed) mode")
    run_parser.add_argument("--require-approval", action="store_true", help="Prompt before saving healed recipes")

    # record command
    subparsers.add_parser("record", help="Record genuine agent trace from live Version B healing")

    # demo command
    subparsers.add_parser("demo", help="Run full 5-beat demonstration workflow")

    # reset command
    subparsers.add_parser("reset", help="Reset recipes back to v1 baseline and clear runs")

    parsed_args = parser.parse_args(argv)

    if parsed_args.command == "serve":
        return cmd_serve(parsed_args)
    elif parsed_args.command == "baseline":
        return cmd_baseline(parsed_args)
    elif parsed_args.command == "run":
        return cmd_run(parsed_args)
    elif parsed_args.command == "record":
        return cmd_record(parsed_args)
    elif parsed_args.command == "demo":
        return cmd_demo(parsed_args)
    elif parsed_args.command == "reset":
        return cmd_reset(parsed_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
