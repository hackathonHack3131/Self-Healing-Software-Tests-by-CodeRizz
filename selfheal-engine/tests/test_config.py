"""Unit tests for application configuration and origin guard."""

import pytest
from engine.config import Settings, get_settings, is_origin_allowed, llm_config_status


def test_default_settings_without_dotenv(monkeypatch):
    """Verify default settings load cleanly without needing a .env file."""
    # Ensure environment does not override defaults
    monkeypatch.delenv("DEMO_BASE_URL", raising=False)
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    monkeypatch.delenv("MAX_AGENT_ACTIONS", raising=False)
    monkeypatch.delenv("MAX_HEAL_SECONDS", raising=False)
    monkeypatch.delenv("HEADLESS", raising=False)
    monkeypatch.delenv("RUNS_DIR", raising=False)

    settings = get_settings()
    assert settings.DEMO_BASE_URL == "http://127.0.0.1:5000"
    assert settings.ALLOWED_ORIGINS == ("http://127.0.0.1:5000",)
    assert settings.MAX_AGENT_ACTIONS == 10
    assert settings.MAX_HEAL_SECONDS == 120
    assert settings.HEADLESS is True
    assert settings.RUNS_DIR == "runs"


def test_missing_key_gives_blocked_config():
    """Verify missing API key or unconfigured model results in BLOCKED_CONFIG."""
    # Empty API key
    s_no_key = Settings(GOOGLE_API_KEY="", DEEPAGENT_MODEL="google_genai:gemini-2.5-flash")
    status = llm_config_status(s_no_key)
    assert "BLOCKED_CONFIG" in status
    assert "GOOGLE_API_KEY" in status

    # Placeholder model
    s_placeholder = Settings(
        GOOGLE_API_KEY="valid_key",
        DEEPAGENT_MODEL="google_genai:REPLACE_WITH_VERIFIED_MODEL_ID"
    )
    status_placeholder = llm_config_status(s_placeholder)
    assert "BLOCKED_CONFIG" in status_placeholder

    # Valid config
    s_valid = Settings(
        GOOGLE_API_KEY="valid_key",
        DEEPAGENT_MODEL="google_genai:gemini-2.5-flash"
    )
    assert llm_config_status(s_valid) == "OK"


def test_origin_allowlist_helper():
    """Verify helper accepts allowlisted origins and rejects outside origins."""
    settings = Settings(ALLOWED_ORIGINS=("http://127.0.0.1:5000",))

    # Allowed origins and paths
    assert is_origin_allowed("http://127.0.0.1:5000", settings) is True
    assert is_origin_allowed("http://127.0.0.1:5000/", settings) is True
    assert is_origin_allowed("http://127.0.0.1:5000/cart", settings) is True
    assert is_origin_allowed("http://127.0.0.1:5000/checkout?user=1", settings) is True

    # Rejected origins
    assert is_origin_allowed("http://malicious.org", settings) is False
    assert is_origin_allowed("https://google.com", settings) is False
    assert is_origin_allowed("http://127.0.0.1:8080", settings) is False
    assert is_origin_allowed("http://localhost:5000", settings) is False


def test_secrets_never_appear_in_repr():
    """Verify API keys and sensitive secrets never appear in repr or str."""
    secret = "AIzaSySecretApiKey123456789"
    settings = Settings(GOOGLE_API_KEY=secret)

    rep = repr(settings)
    assert secret not in rep
    assert "***" in rep

    s = str(settings)
    assert secret not in s
    assert "***" in s
