"""Check LLM connectivity and configuration."""

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.config import get_settings, llm_config_status


def main() -> int:
    settings = get_settings()

    # Step 1: Check configuration
    status = llm_config_status(settings)
    if status != "OK":
        print(status)
        print("Fix: Copy .env.example to .env and provide a valid GOOGLE_API_KEY and DEEPAGENT_MODEL.")
        return 2

    # Step 2: Ensure API key is set in os.environ for underlying clients
    if settings.GOOGLE_API_KEY:
        os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API_KEY

    # Step 3: Initialize model and make a tiny connectivity test call
    try:
        from langchain.chat_models import init_chat_model
        from langchain_core.messages import HumanMessage

        start_time = time.perf_counter()
        model = init_chat_model(settings.DEEPAGENT_MODEL)
        _ = model.invoke([HumanMessage(content="Respond with 'pong'")])
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        print(f"OK ({latency_ms:.1f}ms)")
        return 0

    except Exception as exc:
        err_msg = str(exc)
        # Classify if config-related or agent/API-related
        if "API_KEY" in err_msg.upper() or "MODEL" in err_msg.upper() and "NOT FOUND" in err_msg.upper():
            print(f"BLOCKED_CONFIG: {err_msg}")
            print("Fix: Verify your GOOGLE_API_KEY and DEEPAGENT_MODEL in .env.")
            return 2
        else:
            print(f"BLOCKED_AGENT: {err_msg}")
            print("Fix: Check network connectivity, quota, or Gemini API permissions.")
            return 3


if __name__ == "__main__":
    sys.exit(main())
