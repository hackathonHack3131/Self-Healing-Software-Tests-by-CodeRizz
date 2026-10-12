"""Flask API blueprint for SelfHeal web application."""

import asyncio
import json
from pathlib import Path
from flask import Blueprint, jsonify, request
from engine.config import get_settings, llm_config_status
from engine.recipes import get_project_root, load_intent, load_recipe
from webapp.db import db_manager
from webapp.runner import execute_test_run

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/status", methods=["GET"])
def get_status():
    """Return system status including MongoDB connection, LLM config, and versions."""
    settings = get_settings()
    db_stat = db_manager.get_status()
    llm_stat = llm_config_status(settings)

    intent = load_intent("checkout")
    latest_recipe = load_recipe("checkout", version="latest", intent=intent)

    return jsonify({
        "status": "online",
        "demo_base_url": settings.DEMO_BASE_URL,
        "allowed_origins": list(settings.ALLOWED_ORIGINS),
        "db": db_stat,
        "llm": {
            "status": llm_stat,
            "model": settings.DEEPAGENT_MODEL,
            "mode": "Live Deep Agent" if llm_stat == "OK" else "Recorded Deterministic Healer",
        },
        "latest_recipe_version": latest_recipe.version,
    }), 200


@api_bp.route("/intents", methods=["GET"])
def get_intents():
    """Return immutable intent specifications with masked test-data values."""
    intent = load_intent("checkout")
    intent_data = intent.model_dump()

    # Mask test-data values (keep keys visible for inspection)
    masked_data = {}
    for k, v in intent_data.get("test_data", {}).items():
        if "card" in k:
            masked_data[k] = "•••• •••• •••• 4242"
        elif "cvc" in k:
            masked_data[k] = "•••"
        else:
            masked_data[k] = v
    intent_data["test_data_masked"] = masked_data

    return jsonify([intent_data]), 200


@api_bp.route("/recipes", methods=["GET"])
def get_recipes():
    """Return all available versions of the checkout recipe."""
    root = get_project_root()
    recipe_dir = root / "recipes" / "checkout"
    recipes = []
    intent = load_intent("checkout")

    if recipe_dir.exists():
        for f in sorted(recipe_dir.glob("v*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                recipes.append(data)
            except Exception:
                pass

    return jsonify(recipes), 200


@api_bp.route("/runs", methods=["GET"])
def get_runs():
    """Return test execution history from MongoDB."""
    limit = int(request.args.get("limit", 50))
    runs = db_manager.get_runs(limit=limit)
    return jsonify(runs), 200


@api_bp.route("/runs/<run_id>", methods=["GET"])
def get_run(run_id: str):
    """Return full execution report for a specific run."""
    run = db_manager.get_run(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(run), 200


@api_bp.route("/run", methods=["POST"])
def run_test():
    """Trigger an end-to-end test execution against Version A, B, C, or D."""
    payload = request.get_json(silent=True) or {}
    version = payload.get("version", "a")
    force_mode = payload.get("force_mode")

    # Run asynchronous execution loop safely
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        run_doc = loop.run_until_complete(execute_test_run(version=version, force_heal_mode=force_mode))
    finally:
        loop.close()

    return jsonify(run_doc), 200


@api_bp.route("/reset", methods=["POST"])
def reset_state():
    """Reset recipes to baseline v1 and optionally clear runs."""
    root = get_project_root()
    recipe_dir = root / "recipes" / "checkout"

    # Remove v2+, keep only v1.json
    deleted_recipes = []
    if recipe_dir.exists():
        for f in recipe_dir.glob("v*.json"):
            if f.name != "v1.json":
                f.unlink(missing_ok=True)
                deleted_recipes.append(f.name)

    cleared_runs = db_manager.clear_runs()

    return jsonify({
        "status": "reset_complete",
        "deleted_recipes": deleted_recipes,
        "cleared_runs_count": cleared_runs,
        "current_recipe_version": 1,
    }), 200


@api_bp.route("/contact", methods=["POST"])
def submit_contact():
    """Handle contact and feedback form submissions, persisting to MongoDB."""
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    subject = str(data.get("subject", "General Inquiry")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not message:
        return jsonify({"error": "Name, email, and message are required fields."}), 400

    doc = {
        "name": name,
        "email": email,
        "subject": subject,
        "message": message,
    }
    contact_id = db_manager.save_contact(doc)
    return jsonify({
        "status": "success",
        "contact_id": contact_id,
        "message": "Thank you! Your inquiry has been recorded and submitted to the engineering team.",
    }), 200


# -------------------------------------------------------------
# GitHub Change Intelligence API Endpoints
# -------------------------------------------------------------

@api_bp.route("/github-analysis", methods=["POST"])
def submit_github_analysis():
    """Submit a GitHub repository commit comparison for asynchronous analysis."""
    import os
    from engine.repo_analysis.models import RepoAnalysisRequest
    from engine.repo_analysis.github_service import (
        GitHubValidationError,
        validate_and_normalize_repo_url,
        validate_git_ref,
    )
    from engine.repo_analysis.report_builder import job_manager

    payload = request.get_json(silent=True) or {}
    repo_url = payload.get("repo_url", "").strip()
    base_ref = payload.get("base_ref")
    head_ref = payload.get("head_ref")
    allow_local = bool(payload.get("allow_local", False)) and os.getenv("APP_ENV") != "production"

    if not repo_url:
        return jsonify({"error": "repo_url is a required field."}), 400

    try:
        norm_url, _, _ = validate_and_normalize_repo_url(repo_url, allow_local=allow_local)
        clean_base = validate_git_ref(base_ref)
        clean_head = validate_git_ref(head_ref)

        req_model = RepoAnalysisRequest(
            repo_url=norm_url,
            base_ref=clean_base,
            head_ref=clean_head,
        )
        job_id = job_manager.submit_job(req_model, allow_local=allow_local)

        return jsonify({
            "job_id": job_id,
            "status": "QUEUED",
            "message": "GitHub change intelligence job accepted and running in background.",
            "repo_url": norm_url,
        }), 202

    except GitHubValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Failed to submit analysis: {exc}"}), 500


@api_bp.route("/github-analysis/<job_id>", methods=["GET"])
def get_github_analysis_status(job_id: str):
    """Retrieve status, progress, and summary of a GitHub change intelligence job."""
    from engine.repo_analysis.report_builder import job_manager, validate_job_id

    try:
        clean_job_id = validate_job_id(job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    job = job_manager.get_job(clean_job_id)
    if not job:
        return jsonify({"error": f"Analysis job '{clean_job_id}' not found."}), 404

    # Return status and high-level progress
    return jsonify({
        "job_id": clean_job_id,
        "status": job.get("status"),
        "progress": job.get("progress"),
        "created_at": job.get("created_at"),
        "repo_url": job.get("repo_url"),
        "error": job.get("error"),
        "has_report": bool(job.get("report")),
    }), 200


@api_bp.route("/github-analysis/<job_id>/report", methods=["GET"])
def get_github_analysis_report(job_id: str):
    """Retrieve the completed, structured JSON report for an analysis job."""
    from engine.repo_analysis.report_builder import job_manager, validate_job_id

    try:
        clean_job_id = validate_job_id(job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    job = job_manager.get_job(clean_job_id)
    if not job:
        return jsonify({"error": f"Analysis job '{clean_job_id}' not found."}), 404

    if job.get("status") == "FAILED":
        return jsonify({
            "error": "Analysis failed",
            "detail": job.get("error", "Unknown error occurred during analysis"),
        }), 500

    if job.get("status") in ("QUEUED", "RUNNING"):
        return jsonify({
            "status": job.get("status"),
            "message": "Analysis is currently processing. Please poll status.",
        }), 202

    report = job.get("report")
    if not report:
        return jsonify({"error": "Report data not available."}), 404

    return jsonify(report), 200


@api_bp.route("/github-analysis/<job_id>/html", methods=["GET"])
def get_github_analysis_html(job_id: str):
    """Serve the standalone rendered HTML report for an analysis job."""
    from engine.repo_analysis.report_builder import job_manager, validate_job_id

    try:
        clean_job_id = validate_job_id(job_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    html = job_manager.get_html_report(clean_job_id)
    if not html:
        return jsonify({"error": f"HTML report for job '{clean_job_id}' not found or still generating."}), 404

    return html, 200, {"Content-Type": "text/html; charset=utf-8"}

