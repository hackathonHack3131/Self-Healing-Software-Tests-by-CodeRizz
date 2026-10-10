# Self-Healing E2E Test System (SelfHeal)

SelfHeal is a self-healing end-to-end test system where a test is an **immutable intent**, steps are a versioned recipe, a Deep Agent rebuilds steps when UI changes, and a deterministic verifier decides pass or fail.

## Quick Setup (PowerShell)

Run the following commands in PowerShell from the project root:

```powershell
# 1. Create and activate virtual environment
python -m venv .venv
./.venv/Scripts/Activate.ps1

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Install Chromium browser for Playwright
playwright install chromium

# 4. Configure environment
copy .env.example .env
```

Edit `.env` to supply your Google Gemini API key:
```env
DEEPAGENT_MODEL=google_genai:gemini-2.5-flash
GOOGLE_API_KEY=your_actual_api_key_here
```

## Check Commands

Verify configuration and dependencies:
```powershell
# Run configuration and origin allowlist unit tests
pytest tests/test_config.py

# Verify LLM connectivity and configuration status
python scripts/check_llm.py
```
Exit codes for `python scripts/check_llm.py`:
- `0`: Model check passed (`OK`)
- `2`: Missing or invalid configuration (`BLOCKED_CONFIG`)
- `3`: API / network / model failure (`BLOCKED_AGENT`)
