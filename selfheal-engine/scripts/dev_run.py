"""Developer utility script to run recipes against demo shop checkout versions."""

import argparse
import asyncio
from dataclasses import replace
import os
import sys

# Ensure project root is in sys.path before engine imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.browser import BrowserSession
from engine.config import get_settings
from engine.executor import run_recipe
from engine.recipes import load_intent, load_recipe


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run latest recipe against demo app.")
    parser.add_argument(
        "--version",
        choices=["a", "b", "c", "d"],
        default="a",
        help="Demo shop checkout version (default: a)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode (visible window)",
    )
    parser.add_argument(
        "--intent",
        default="checkout",
        help="Intent ID to execute (default: checkout)",
    )

    args = parser.parse_args()

    settings = get_settings()
    if args.headed:
        settings = replace(settings, HEADLESS=False)

    intent = load_intent(args.intent)
    recipe = load_recipe(args.intent, version="latest", intent=intent)

    start_url = f"{settings.DEMO_BASE_URL}/v/{args.version}/"
    print(f"=== Running recipe v{recipe.version} against Version {args.version.upper()} ===")
    print(f"Start URL: {start_url}")
    print(f"Steps count: {len(recipe.steps)}")

    async with BrowserSession(settings=settings, start_url=start_url) as session:
        result = await run_recipe(recipe, intent, session)

    print("\n=== Run Result ===")
    print(f"Status: {result.status.value}")
    if result.failed_step_index is not None:
        print(f"Failed Step Index: {result.failed_step_index}")
        print(f"Failure Type: {result.failure_type.value if result.failure_type else 'None'}")
        failed_step = result.steps[result.failed_step_index]
        print(f"Error Message: {failed_step.error_message}")
    else:
        print("All recipe steps executed successfully!")

    print(f"\nExecuted Steps ({len(result.steps)}):")
    for s in result.steps:
        target_name = s.step.target.name if s.step.target else ""
        outcome = "PASS" if s.success else "FAIL"
        print(f"  [{s.step_index}] {s.step.action.value} {target_name} ({s.duration_ms:.1f}ms) -> {outcome}")

    if result.evidence.get("http_errors"):
        print(f"\nHTTP Errors: {result.evidence['http_errors']}")
    if result.evidence.get("alerts"):
        print(f"Alerts: {result.evidence['alerts']}")
    if result.evidence.get("failure_screenshot"):
        print(f"Failure Screenshot: {result.evidence['failure_screenshot']}")

    return 0 if result.failed_step_index is None else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
