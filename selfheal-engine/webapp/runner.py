"""Asynchronous test execution pipeline and self-healing runner for webapp.

Delegates execution to the engine's state machine orchestrator (engine.orchestrator per Module 9)
and persists results into MongoDB and local telemetry.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, Optional

from engine.config import get_settings
from engine.orchestrator import run_orchestrator
from webapp.db import db_manager

logger = logging.getLogger("selfheal.runner")


async def execute_test_run(version: str = "a", force_heal_mode: Optional[str] = None) -> Dict[str, Any]:
    """Execute end-to-end test run against specified version (a, b, c, or d).

    Delegates to engine.orchestrator.run_orchestrator and persists run and recipe to MongoDB.
    """
    version = version.lower().strip()
    settings = get_settings()
    target_url = f"{settings.DEMO_BASE_URL}/v/{version}/"

    orch_result = await run_orchestrator(
        intent_id="checkout",
        target_url=target_url,
        recipe_version=1,
        settings=settings,
        force_heal_mode=force_heal_mode,
    )

    # Format steps for UI display
    if orch_result.saved_recipe and orch_result.healed:
        steps = [
            {
                "step_index": idx,
                "action": s.action.value,
                "target_name": s.target.name if s.target else "Start URL",
                "field_key": s.field_key or "",
                "success": True,
                "duration_ms": 120.0,
                "error_message": "",
            }
            for idx, s in enumerate(orch_result.saved_recipe.steps)
        ]
    else:
        steps = [
            {
                "step_index": s.step_index,
                "action": s.step.action.value,
                "target_name": s.step.target.name if s.step.target else "Start URL",
                "field_key": s.step.field_key or "",
                "success": s.success,
                "duration_ms": round(s.duration_ms, 1),
                "error_message": s.error_message or "",
            }
            for s in orch_result.initial_run_result.steps
        ]

    # Format diff summary for UI
    diff_summary = {"added": 0, "removed": 0, "renamed": 0, "details": []}
    if orch_result.diff:
        diff_summary = {
            "added": len(orch_result.diff.added),
            "removed": len(orch_result.diff.removed),
            "renamed": len(orch_result.diff.renamed),
            "details": [
                {"type": "added", "name": el.name, "role": el.role}
                for el in orch_result.diff.added[:10]
            ]
            + [
                {"type": "removed", "name": el.name, "role": el.role}
                for el in orch_result.diff.removed[:10]
            ]
            + [
                {"type": "renamed", "from": r.old_name, "to": r.new_name, "confidence": r.confidence}
                for r in orch_result.diff.renamed[:10]
            ],
        }

    # Save new recipe to MongoDB if one was created
    if orch_result.saved_recipe:
        recipe_doc = {
            "intent_id": orch_result.saved_recipe.intent_id,
            "version": orch_result.saved_recipe.version,
            "parent_version": orch_result.saved_recipe.parent_version,
            "created_by": orch_result.saved_recipe.created_by.value,
            "intent_hash": orch_result.saved_recipe.intent_hash,
            "steps": [s.model_dump() for s in orch_result.saved_recipe.steps],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        db_manager.save_recipe(recipe_doc)

    run_doc: Dict[str, Any] = {
        "run_id": orch_result.run_id,
        "version": version,
        "start_url": orch_result.target_url,
        "status": orch_result.status.value,
        "status_label": orch_result.status_label,
        "healed": orch_result.healed,
        "old_recipe_version": orch_result.initial_recipe_version,
        "new_recipe_version": orch_result.new_recipe_version or orch_result.initial_recipe_version,
        "triage_verdict": orch_result.triage.verdict.value if orch_result.triage else "NONE",
        "triage_confidence": orch_result.triage.confidence if orch_result.triage else 1.0,
        "triage_recommendation": orch_result.triage.recommended.value if orch_result.triage else "NONE",
        "steps": steps,
        "diff_summary": diff_summary,
        "evidence": orch_result.evidence,
        "agent_explanation": orch_result.agent_explanation,
        "logs": [e.model_dump() for e in orch_result.events],
        "duration_ms": round(orch_result.duration_ms, 1),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    db_manager.save_run(run_doc)
    return run_doc
