"""Command-line interface for the SelfHeal system.

Commands (per AGENTS.md):
  baseline : Run Version A and establish trusted UI baseline
  run      : Run latest recipe against specified version
  demo     : Run end-to-end self-healing demonstration (Version A -> Version B)
  reset    : Reset recipes back to baseline v1
  serve    : Start the SelfHeal web application dashboard
"""

import argparse
import asyncio
import os
import sys

from engine.recipes import get_project_root, load_intent, load_recipe
from webapp.runner import execute_test_run


def cmd_serve(args):
    """Start the SelfHeal dashboard web application."""
    from webapp.server import create_app
    app = create_app()
    port = int(os.getenv("WEBAPP_PORT", args.port or "8080"))
    host = os.getenv("WEBAPP_HOST", args.host or "0.0.0.0")
    print(f"SelfHeal Studio starting at http://localhost:{port}")
    app.run(host=host, port=port, debug=False)


def cmd_run(args):
    """Run test recipe against a checkout version."""
    version = args.version or "a"
    print(f"Executing SelfHeal test against Version {version.upper()}...")
    res = asyncio.run(execute_test_run(version=version))
    print(f"Result Status : {res['status']}")
    print(f"Duration      : {res['duration_ms']}ms")
    print(f"Healed        : {res['healed']}")
    print(f"Explanation   :\n{res['agent_explanation']}")


def cmd_demo(args):
    """Run full demonstration workflow: Version A baseline then Version B self-heal."""
    print("=== Step 1: Running Baseline on Version A ===")
    res_a = asyncio.run(execute_test_run(version="a"))
    print(f"Version A Status: {res_a['status']} ({res_a['status_label']})\n")

    print("=== Step 2: Triggering UI Drift & Auto-Healing on Version B ===")
    res_b = asyncio.run(execute_test_run(version="b"))
    print(f"Version B Status: {res_b['status']} ({res_b['status_label']})")
    print(f"New Recipe Version: v{res_b['new_recipe_version']}")
    print(f"Explanation:\n{res_b['agent_explanation']}")


def cmd_reset(args):
    """Reset recipes to baseline v1."""
    root = get_project_root()
    recipe_dir = root / "recipes" / "checkout"
    count = 0
    if recipe_dir.exists():
        for f in recipe_dir.glob("v*.json"):
            if f.name != "v1.json":
                f.unlink(missing_ok=True)
                count += 1
    print(f"Reset complete. Removed {count} generated recipes. Current version is v1.")


def main():
    parser = argparse.ArgumentParser(description="SelfHeal E2E Autonomous Testing CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start web dashboard")
    serve_parser.add_argument("--port", default="8080", help="Port to listen on (default: 8080)")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")

    # run command
    run_parser = subparsers.add_parser("run", help="Run test against a version")
    run_parser.add_argument("--version", choices=["a", "b", "c", "d"], default="a", help="Version to test")

    # demo command
    subparsers.add_parser("demo", help="Run demo flow (A baseline then B heal)")

    # reset command
    subparsers.add_parser("reset", help="Reset recipes back to v1 baseline")

    args = parser.parse_args()
    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "demo":
        cmd_demo(args)
    elif args.command == "reset":
        cmd_reset(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
