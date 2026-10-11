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
