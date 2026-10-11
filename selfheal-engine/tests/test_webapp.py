"""Unit tests for SelfHeal web application backend and MongoDB persistence."""

import json
import pytest
from webapp.db import DatabaseManager
from webapp.server import create_app


@pytest.fixture
def test_client():
    """Flask test client fixture."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_webapp_db_status_and_in_memory_fallback():
    """Verify DatabaseManager reports connectivity and handles run persistence."""
    dm = DatabaseManager()
    status = dm.get_status()
    assert "connected" in status
    assert "backend" in status
    assert "runs_count" in status

    # Test saving and retrieving a run
    run_doc = {
        "run_id": "test_run_123",
        "version": "a",
        "status": "PASS_NO_HEAL",
        "duration_ms": 120.0,
    }
    saved_id = dm.save_run(run_doc)
    assert saved_id == "test_run_123"

    fetched = dm.get_run("test_run_123")
    assert fetched is not None
    assert fetched["status"] == "PASS_NO_HEAL"


def test_api_status_endpoint(test_client):
    """Verify /api/status returns 200 with db and llm details."""
    res = test_client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "online"
    assert "db" in data
    assert "llm" in data
    assert "latest_recipe_version" in data


def test_api_intents_endpoint_masks_sensitive_data(test_client):
    """Verify /api/intents returns masked card and cvc data."""
    res = test_client.get("/api/intents")
    assert res.status_code == 200
    intents = res.get_json()
    assert len(intents) >= 1
    intent = intents[0]
    assert intent["id"] == "checkout"
    masked = intent.get("test_data_masked", {})
    if "card_number" in masked:
        assert "4242" in masked["card_number"]
        assert "••••" in masked["card_number"]


def test_api_recipes_endpoint(test_client):
    """Verify /api/recipes returns valid recipe versions."""
    res = test_client.get("/api/recipes")
    assert res.status_code == 200
    recipes = res.get_json()
    assert len(recipes) >= 1
    assert recipes[0]["version"] == 1


def test_api_runs_endpoint(test_client):
    """Verify /api/runs returns a list of historical runs."""
    res = test_client.get("/api/runs")
    assert res.status_code == 200
    runs = res.get_json()
    assert isinstance(runs, list)


def test_index_html_renders(test_client):
    """Verify GET / serves the Home landing page."""
    res = test_client.get("/")
    assert res.status_code == 200
    assert b"SelfHeal Studio" in res.data
    assert b"Intent-Aware E2E Testing" in res.data


def test_demo_page_renders(test_client):
    """Verify GET /demo serves the Interactive Studio."""
    res = test_client.get("/demo")
    assert res.status_code == 200
    assert b"Interactive Testing Studio" in res.data
    assert b"PASS_NO_HEAL" in res.data


def test_about_page_renders(test_client):
    """Verify GET /about serves the Architecture & Rules page."""
    res = test_client.get("/about")
    assert res.status_code == 200
    assert b"Architecture &amp; Global System Rules" in res.data or b"Architecture & Global System Rules" in res.data
    assert b"Immutable Intent" in res.data


def test_contact_page_renders(test_client):
    """Verify GET /contact serves the Contact & Inquiries page."""
    res = test_client.get("/contact")
    assert res.status_code == 200
    assert b"Get in Touch with Team CodeRizz" in res.data
    assert b"Submit to MongoDB" in res.data


def test_contact_api_submission(test_client):
    """Verify POST /api/contact validates input and records to MongoDB."""
    # Invalid empty payload
    bad_res = test_client.post("/api/contact", json={})
    assert bad_res.status_code == 400

    # Valid submission
    payload = {
        "name": "Alex Evaluation",
        "email": "alex@evaluator.org",
        "subject": "Hackathon Evaluation",
        "message": "Excellent multi-page architecture and clean intent verifier implementation.",
    }
    good_res = test_client.post("/api/contact", json=payload)
    assert good_res.status_code == 200
    data = good_res.get_json()
    assert data["status"] == "success"
    assert "contact_id" in data
